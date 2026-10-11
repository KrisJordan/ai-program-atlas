"""Independent original-upstream execution, not a second copy of importer logic."""
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_review_pins_final_artifact_and_source_hashes():
    review = json.loads((ROOT / 'research/csrankings-peer-review.json').read_text())
    for field, filename in [('computed_artifact_sha256', 'data/csrankings.json'),
                            ('crosswalk_sha256', 'data/csrankings-crosswalk.json')]:
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == review[field]
    assert review['comparison']['exact_display_score_and_rank_mismatches'] == 0
    assert review['comparison']['observed_rows_compared'] == 961


def test_complete_population_against_original_pinned_javascript(tmp_path):
    node = shutil.which('node')
    source = ROOT / '.cache/csrankings/csrankings.js'
    if not node or not source.is_file():
        pytest.skip('Original pinned private cache and Node needed for independent review replay')
    review = json.loads((ROOT / 'research/csrankings-peer-review.json').read_text())
    for capture in review['sources']:
        assert hashlib.sha256((source.parent / capture['filename']).read_bytes()).hexdigest() == capture['sha256']
    result = tmp_path / 'original-upstream.json'
    subprocess.run([node, str(ROOT / 'scripts/csrankings_peer_upstream.js'), str(result)], cwd=ROOT, check=True, capture_output=True)
    assert hashlib.sha256(result.read_bytes()).hexdigest() == review['independent_upstream_result_sha256']
    views = json.loads(result.read_text())['views']
    actual = json.loads((ROOT / 'data/csrankings.json').read_text())
    for row in actual['full_us_results']:
        view = views['ai_aggregate' if row['field'] == 'aggregate' else row['field']]
        upstream = next((r for r in view if r['institution'] == row['upstream_institution']), None)
        if upstream is None:
            assert row['missingness'] == 'no_selected_output'
            assert row['value'] is None and row['rank'] is None
            continue
        assert (row['value'], row['rank']) == (upstream['score'], upstream['rank'])
        assert math.isclose(row['unrounded_score'], upstream['raw_score'], rel_tol=1e-12, abs_tol=1e-12)
        for field, count in upstream['field_adjusted_counts'].items():
            imported = row['component_counts'][field] if row['field'] == 'aggregate' else row['adjusted_count']
            assert math.isclose(imported, count, rel_tol=1e-12, abs_tol=1e-12)
