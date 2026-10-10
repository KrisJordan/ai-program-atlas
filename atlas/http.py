"""Bounded, robots-aware HTTP transport. Raw bodies stay in ignored local cache."""

from __future__ import annotations

import hashlib
import json
import ipaddress
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

USER_AGENT = "AIProgramAtlas/0.1 (+https://github.com/KrisJordan/ai-program-atlas)"


class FetchError(RuntimeError):
    pass


def validate_public_url(url):
    parsed = urlparse(url)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise FetchError("Unsafe URL: only public HTTP(S) URLs without credentials are supported")
    host = (parsed.hostname or "").lower().rstrip(".")
    if (
        host == "localhost"
        or host.endswith((".localhost", ".local", ".internal"))
        or "." not in host
        and ":" not in host
    ):
        raise FetchError("Unsafe local or private host")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return
    if not address.is_global:
        raise FetchError("Unsafe non-public IP address")


@dataclass(frozen=True)
class FetchResult:
    url: str
    text: str
    content_hash: str
    fetched_at: str
    status: int
    cached: bool


class Fetcher:
    def __init__(
        self,
        cache_dir=".cache/http",
        *,
        ttl=86400,
        delay=1.5,
        retries=2,
        max_bytes=5_000_000,
        client=None,
        sleep=time.sleep,
        clock=time.time,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl, self.delay, self.retries = ttl, max(0, delay), min(3, max(0, retries))
        self.max_bytes, self.sleep, self.clock = max_bytes, sleep, clock
        self.client = client or httpx.Client(
            headers={"User-Agent": USER_AGENT}, timeout=25, follow_redirects=False
        )
        self.owns_client = client is None
        self.last_request = {}
        self.robots = {}
        self.crawl_delays = {}

    def close(self):
        if self.owns_client:
            self.client.close()

    def _get(self, url):
        validate_public_url(url)
        host = urlparse(url).netloc
        for attempt in range(self.retries + 1):
            wait = max(self.delay, self.crawl_delays.get(host, 0)) - (
                self.clock() - self.last_request.get(host, float("-inf"))
            )
            if wait > 0:
                self.sleep(wait)
            self.last_request[host] = self.clock()
            try:
                with self.client.stream("GET", url) as response:
                    body = bytearray()
                    for chunk in response.iter_bytes():
                        body.extend(chunk)
                        if len(body) > self.max_bytes:
                            raise FetchError(f"Response exceeds {self.max_bytes} bytes: {url}")
                    headers = dict(response.headers)
                    # iter_bytes already decoded Content-Encoding; do not decode a second time.
                    headers.pop("content-encoding", None)
                    headers.pop("content-length", None)
                    result = httpx.Response(
                        response.status_code,
                        headers=headers,
                        content=bytes(body),
                        request=response.request,
                    )
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt == self.retries:
                    raise FetchError(f"Transport failure: {url}: {type(exc).__name__}") from exc
                self.sleep(min(2**attempt, 8))
                continue
            if result.status_code not in (429, 500, 502, 503, 504):
                return result
            if attempt == self.retries:
                return result
            retry_after = result.headers.get("Retry-After", "")
            pause = float(retry_after) if retry_after.isdigit() else 0
            if retry_after and not retry_after.isdigit():
                try:
                    pause = max(0, parsedate_to_datetime(retry_after).timestamp() - self.clock())
                except (ValueError, TypeError, OverflowError):
                    pause = 0
            if pause > 60:
                raise FetchError(
                    f"Server requests retry after {pause:g}s; defer this source to a later run: {url}"
                )
            self.sleep(max(2**attempt, pause))
        raise FetchError(f"Exhausted retries: {url}")

    def _check_robots(self, url):
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self.robots:
            robots_url = origin + "/robots.txt"
            response = self._get(robots_url)
            # Follow only same-origin robots redirects, bounded and without attempting protected access.
            for _ in range(3):
                if response.status_code not in (301, 302, 303, 307, 308):
                    break
                target = urljoin(robots_url, response.headers.get("location", ""))
                if (
                    urlparse(target).netloc != parsed.netloc
                    or urlparse(target).scheme != parsed.scheme
                    or urlparse(target).username is not None
                ):
                    raise FetchError(f"Cross-origin robots redirect requires review: {robots_url}")
                robots_url = target
                response = self._get(robots_url)
            robot = RobotFileParser(origin + "/robots.txt")
            if response.status_code == 404:
                robot.parse(["User-agent: *", "Allow: /"])
            elif response.status_code == 200:
                if "<html" in response.text[:500].lower():
                    raise FetchError(f"Robots response is HTML; policy unavailable: {origin}")
                robot.parse(response.text.splitlines())
            else:
                raise FetchError(f"Robots unavailable ({response.status_code}); not fetching {url}")
            crawl_delay = robot.crawl_delay(USER_AGENT) or robot.crawl_delay("*") or 0
            if crawl_delay > 60:
                raise FetchError(
                    f"Robots crawl delay {crawl_delay}s requires separate scheduling: {origin}"
                )
            self.robots[origin] = robot
            self.crawl_delays[parsed.netloc] = crawl_delay
        if not self.robots[origin].can_fetch(USER_AGENT, url):
            raise FetchError(f"Robots disallows fetch: {url}")

    def fetch(self, url, *, force=False):
        from .db import now

        validate_public_url(url)
        key = hashlib.sha256(url.encode()).hexdigest()
        meta_path, body_path = self.cache_dir / (key + ".json"), self.cache_dir / (key + ".body")
        if not force and meta_path.exists() and body_path.exists():
            meta = json.loads(meta_path.read_text())
            body = body_path.read_bytes()
            if (
                self.clock() - meta["cached_at"] < self.ttl
                and hashlib.sha256(body).hexdigest() == meta["content_hash"]
            ):
                return FetchResult(
                    url,
                    body.decode("utf-8"),
                    meta["content_hash"],
                    meta["fetched_at"],
                    meta["status"],
                    True,
                )
        current = url
        for _ in range(5):
            validate_public_url(current)
            self._check_robots(current)
            response = self._get(current)
            if response.status_code in (301, 302, 303, 307, 308):
                current = urljoin(current, response.headers.get("location", ""))
                if urlparse(current).scheme not in ("http", "https"):
                    raise FetchError("Unsafe redirect")
                continue
            if response.status_code != 200:
                raise FetchError(
                    f"HTTP {response.status_code}: {current}; no access bypass attempted"
                )
            if "text/" not in response.headers.get(
                "content-type", "text/html"
            ) and "json" not in response.headers.get("content-type", ""):
                raise FetchError(f"Non-text source requires a reviewed format adapter: {current}")
            body = response.text.encode("utf-8")
            fingerprint = hashlib.sha256(body).hexdigest()
            fetched_at = now()
            meta = {
                "url": url,
                "resolved_url": current,
                "cached_at": self.clock(),
                "content_hash": fingerprint,
                "fetched_at": fetched_at,
                "status": response.status_code,
            }
            body_path.write_bytes(body)
            meta_path.write_text(json.dumps(meta, indent=2))
            return FetchResult(
                url, response.text, fingerprint, fetched_at, response.status_code, False
            )
        raise FetchError(f"Too many redirects: {url}")
