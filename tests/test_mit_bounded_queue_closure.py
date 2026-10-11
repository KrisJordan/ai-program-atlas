"""Evidence-ledger reconciliation, without certifying missing course content."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'atlas/adapters/mit-ai-decision-making-bs'

def read(path):return json.loads(path.read_text())

def test_every_snapshot_gap_has_one_explicit_disposition():
    closure=read(ROOT/'research/degree-audit/mit-hass-bounded-closure.json')
    queue=read(ROOT/closure['input_queue']['path'])
    assert hashlib.sha256((ROOT/closure['input_queue']['path']).read_bytes()).hexdigest()==closure['input_queue']['sha256']
    assert {r['id']for r in closure['records']}=={r['id']for r in queue['records']}
    assert len(closure['records'])==len({r['id']for r in closure['records']})==361
    assert 484+len(closure['records'])==845
    assert all(r['next_action'] and r['listed_source_url'] for r in closure['records'])
    assert not any(r['state']=='delegated_architecture_remainder'for r in closure['records'])

def test_architecture_remainder_is_exact_difference_not_new_assignment():
    closure=read(ROOT/'research/degree-audit/mit-hass-bounded-closure.json')
    original=read(BASE/'reviewed_architecture_remainder.json')['courses']
    observed=read(BASE/'reviewed_architecture_ocw.json')['sources']
    enriched={key for source in observed.values()for key in source['courses']}
    remaining=set(original)-enriched
    assert len(original)==58 and len(enriched)==6 and len(remaining)==52
    assert set(closure['architecture_reconciliation']['remaining_exact_record_ids'])==remaining
    assert {r['id']for r in closure['records']if r['state']=='architecture_reviewed_source_gap'}==remaining

def test_access_failure_is_not_reported_as_a_publisher_denial():
    closure=read(ROOT/'research/degree-audit/mit-hass-bounded-closure.json')
    checks={r['url']:r for r in closure['supplemental_policy_checks']}
    assert checks['http://mitgsl.mit.edu/robots.txt']['location']=='https://languages.mit.edu'
    assert 'homepage' in checks['http://mitgsl.mit.edu/robots.txt']['finding']
    assert checks['https://languages.mit.edu/robots.txt']['status']=='200'
    assert 'ConnectError' in checks['https://cmsw.mit.edu/robots.txt']['finding']
    assert 'ERR_BLOCKED_BY_CLIENT' in checks['https://cmsw.mit.edu/robots.txt']['finding']
    assert closure['counts']['identified_unrestricted_unread_exact_pages']==0

def test_bounded_closure_preserves_full_audit_blockers_and_manual_roles():
    path=ROOT/'research/degree-audit/mit-hass-bounded-closure.json'
    audit=read(ROOT/'research/degree-audit/mit.json')['programs'][0]
    assert audit['status']=='blocked' and audit['blockers']
    assert audit['bounded_source_queue_review']['full_audit_certified'] is False
    assert audit['bounded_source_queue_review']['sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    assert {k:len(v)for k,v in audit['expected_course_ids'].items()}=={'required':3,'options':275,'unresolved':904}
