"""Transport regressions for publisher rules, independently of policy line order."""

import httpx
import pytest
from atlas.http import Fetcher, FetchError


@pytest.mark.parametrize(
    "rules,allowed,blocked",
    [
        (
            "Disallow: /\nAllow: /v/\nDisallow: /v/private/",
            ["/v/public-checklist"],
            ["/", "/account", "/v/private/checklist"],
        ),
        (
            "Allow: /v/\nDisallow: /v/private/\nDisallow: /",
            ["/v/public-checklist"],
            ["/", "/account", "/v/private/checklist"],
        ),
        ("Disallow: /same\nAllow: /same", ["/same"], []),
        (
            "Disallow: /*.pdf$\nAllow: /public/",
            ["/public/notes.html", "/notes.pdf?view=1"],
            ["/notes.pdf"],
        ),
        ("Disallow: /a%2Fb\nDisallow: /caf%C3%A9", ["/a/b"], ["/a%2fb", "/café"]),
    ],
)
def test_policy_precedence_paths_and_anchors(tmp_path, rules, allowed, blocked):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(
            200,
            text="User-agent: *\n" + rules
            if request.url.path == "/robots.txt"
            else "public content",
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        f = Fetcher(tmp_path, client=client, delay=0)
        for path in allowed:
            assert f.fetch("https://catalog.example.edu" + path).text == "public content"
        before = len(calls)
        for path in blocked:
            with pytest.raises(FetchError, match="Robots disallows"):
                f.fetch("https://catalog.example.edu" + path)
        assert len(calls) == before


def test_specific_agent_groups_merge_without_wildcard_allow(tmp_path):
    policy = "User-agent: *\nAllow: /\n\nUser-agent: aiprogramatlas\nDisallow: /\n\nUser-agent: AIProgramAtlas\nAllow: /reviewed/"
    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(
            200, text=policy if request.url.path == "/robots.txt" else "public content"
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        f = Fetcher(tmp_path, client=client, delay=0)
        assert f.fetch("https://catalog.example.edu/reviewed/checklist").status == 200
        with pytest.raises(FetchError, match="Robots disallows"):
            f.fetch("https://catalog.example.edu/other")
        assert calls == ["/robots.txt", "/reviewed/checklist"]


def test_request_rate_adds_required_pacing(tmp_path):
    clock = [1000.0]
    calls = []

    def sleep(seconds):
        clock[0] += seconds

    def handler(request):
        calls.append((request.url.path, clock[0]))
        return httpx.Response(
            200,
            text="User-agent: *\nAllow: /\nCrawl-delay: 2\nRequest-rate: 2/1m"
            if request.url.path == "/robots.txt"
            else "public content",
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        f = Fetcher(tmp_path, client=client, delay=0, sleep=sleep, clock=lambda: clock[0])
        f.fetch("https://catalog.example.edu/one")
        f.fetch("https://catalog.example.edu/two")
    assert calls == [("/robots.txt", 1000), ("/one", 1030), ("/two", 1060)]


def test_visit_window_defers_request_instead_of_ignoring_policy(tmp_path):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(200, text="User-agent: *\nAllow: /\nVisit-time: 0200-0300")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        f = Fetcher(tmp_path, client=client, delay=0)
        with pytest.raises(FetchError, match="visit window"):
            f.fetch("https://catalog.example.edu/one")
    assert calls == ["/robots.txt"]
