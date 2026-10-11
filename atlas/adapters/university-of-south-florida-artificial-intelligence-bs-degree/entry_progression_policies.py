"""Bounded public USF entry/allocation observations; manual policy reviews stay separate."""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import rule
PID = "university-of-south-florida-artificial-intelligence-bs-degree"
REVIEWS = json.loads(Path(__file__).with_suffix(".json").read_text())
def observe(html, review):
    soup = BeautifulSoup(html, "html.parser")
    if soup.find(string=lambda s: s and any(x in s.lower() for x in ("access denied", "verify you are human"))):
        raise ValueError("USF policy access/interstitial response")
    text = " ".join((soup.select_one("main") or soup).get_text(" ", strip=True).split())
    if hashlib.sha256(text.encode()).hexdigest() != review["normalized_sha256"]:
        raise ValueError("USF public policy changed; human scope review required")
    return {"id": PID, "requirements": [rule(review["source_id"] + "-" + r["key"], r["title"], review["source_id"], kind="note", summary=r["summary"]) for r in review["rules"]]}
PARSERS = {r["url"]: (lambda html, r=r: observe(html, r)) for r in REVIEWS}
