"""Course-specific restrictions must survive storage and reach the static detail."""
import json
from pathlib import Path

from bs4 import BeautifulSoup

from atlas import db
from atlas.site import build, course_notes_markup
from tests.test_site import site_data  # noqa: F401


def test_course_note_disclosure_escapes_evidence_and_omits_empty_lists(tmp_path, site_data):
    c=site_data['programs'][0]['courses'][0]
    c['notes']=['A <script>alert("not executable")</script> condition & exception.', 'Historical Spring 2020 observation.']
    for duplicate in site_data['programs'][0]['courses']:
        duplicate['notes']=list(c['notes'])
    build(site_data,tmp_path)
    html=(tmp_path/'programs/test-ai-0/index.html').read_text()
    row=BeautifulSoup(html,'html.parser').find(id='course-course-0')
    notes=row.find('details',class_='course-notes')
    assert not notes.has_attr('open')
    assert notes.find('summary').get_text()=='Course notes (2) for AI 001'
    assert [n.get_text() for n in notes.find_all('li')]==c['notes']
    assert notes.find('script') is None
    assert notes.previous_sibling['class']==['course-description']
    assert course_notes_markup({'code':'EMPTY','notes':[]})==''
    assert course_notes_markup({'code':'MISSING'})==''
    assert 'course-notes' not in (tmp_path/'programs/test-ai-1/index.html').read_text()


def test_real_mit_conditional_and_version_notes_roundtrip_to_static_detail(tmp_path):
    root=Path(__file__).resolve().parents[1]
    seed=json.loads((root/'data/programs/mit-ai-decision-making-bs.json').read_text())
    ids=['mit-ai-6-3720','mit-ai-6-3900']
    source={c['id']:c for c in seed['courses'] if c['id'] in ids}
    assert '18.06 is recommended preparation, separate from the formal prerequisite expression.' in source[ids[0]]['notes']
    assert any('does not supersede the unversioned degree context' in n for n in source[ids[1]]['notes'])
    connection=db.connect(tmp_path/'atlas.sqlite');db.migrate(connection)
    db.ingest_program(connection,seed);connection.commit()
    data=db.export_data(connection);connection.close()
    exported={c['id']:c for c in data['programs'][0]['courses']}
    build(data,tmp_path/'site')
    soup=BeautifulSoup((tmp_path/'site/programs/mit-ai-decision-making-bs/index.html').read_text(),'html.parser')
    for cid in ids:
        assert exported[cid]['notes']==source[cid]['notes']
        notes=soup.find(id='course-'+cid).find('details',class_='course-notes')
        assert [item.get_text() for item in notes.find_all('li')]==source[cid]['notes']
