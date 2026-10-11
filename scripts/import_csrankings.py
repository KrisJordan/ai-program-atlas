#!/usr/bin/env python3
"""Rebuild small computed artifacts from verified, ignored pinned upstream inputs."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atlas.csrankings import build_artifact


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=Path('.cache/csrankings'))
    parser.add_argument('--download', action='store_true', help='Fetch exact pinned official GitHub inputs before verifying hashes')
    parser.add_argument('--crosswalk', type=Path, default=Path('data/csrankings-crosswalk.json'))
    parser.add_argument('--cohort', type=Path, default=Path('data/cohort.json'))
    parser.add_argument('--output', type=Path, default=Path('data/csrankings.json'))
    args = parser.parse_args()
    if args.download:
        import httpx
        sources = json.loads(args.crosswalk.read_text())['sources']
        args.source_dir.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=45, follow_redirects=False) as client:
            for source in sources:
                if not source['url'].startswith('https://raw.githubusercontent.com/emeryberger/CSrankings/'):
                    raise ValueError('Only pinned official upstream raw URLs are permitted')
                with client.stream('GET', source['url']) as response:
                    response.raise_for_status()
                    body = bytearray()
                    for chunk in response.iter_bytes():
                        body.extend(chunk)
                        if len(body) > 100_000_000:
                            raise ValueError('Source exceeds bounded download size')
                import hashlib
                if hashlib.sha256(body).hexdigest() != source['sha256']:
                    raise ValueError('Downloaded source does not match pinned hash')
                (args.source_dir / source['filename']).write_bytes(body)
    artifact = build_artifact(args.source_dir, args.crosswalk, args.cohort)
    args.output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(artifact['population'], indent=2))


if __name__ == '__main__':
    main()
