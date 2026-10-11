"""Synthetic program-family contracts: scoped inheritance without degree merging.

These examples are invented. They preserve local course/source identities while
sharing reviewed requirement facts, and deliberately use different awards.
"""
from copy import deepcopy
import pytest
from atlas.families import resolve_program, validate_family


def source(sid):
    return dict(id=sid,url=f'https://example.edu/catalog/{sid}',title='Synthetic catalog evidence',
                fetched_at='2026-10-10',source_date=None,catalog_year='2026–2027',
                locator='Invented test section',confidence='high')


def requirement(rid, sid, *, parent=None, courses=(), kind='all', count=None, **extra):
    return dict(id=rid,parent_id=parent,title='Synthetic requirement',kind=kind,count=count,
                credits=None,credit_unit='unknown',category='other',source_id=sid,
                source_text=None,summary='An invented requirement for testing.',
                course_ids=list(courses),**extra)


def synthetic_family():
    shared=requirement('shared-foundations','family-catalog',component='ai_core')
    shared.pop('course_ids');shared['course_codes']=['AI 101','CS 102']
    return dict(id='synthetic-ai-combined',institution_id='synthetic-university',
                name='Synthetic combined AI programs',classification_kind='analyst_classified',
                sources=[source('family-catalog')],shared_requirements=[shared])


def synthetic_variant(partner='biology',award='BS'):
    pid=f'ai-{partner}';sid=pid+'-catalog'
    courses=[]
    for suffix,code in [('ai','AI 101'),('cs','CS 102'),('domain',partner.upper()+' 201')]:
        courses.append(dict(id=pid+'-'+suffix,code=code,name='Synthetic '+code,description=None,
                            prerequisites=None,credits=None,credit_unit='unknown',category='other',
                            source_id=sid,url=source(sid)['url'],public_site=None,syllabus=None))
    return dict(id=pid,institution=dict(id='synthetic-university',name='Synthetic University',
                aliases=[],calendar='unknown',website='https://example.edu'),title='AI and '+partner.title(),
                award_level=award,program_kind='degree',hosting_unit='Synthetic School',
                status='unknown',first_offered=None,overview='Invented combined program.',
                catalog_year='2026–2027',verification_status='partial',last_verified='2026-10-10',
                curriculum_status='partial',links=[],sources=[source(sid)],outcomes=[],courses=courses,
                requirements=[requirement(pid+'-domain',sid,courses=[pid+'-domain'])],notes=[],
                family=dict(id='synthetic-ai-combined',variant_label=partner.title(),
                    disciplines=[partner.title()],relationship='integrated',
                    classification_kind='analyst_classified',source_ids=[sid],
                    hosting_units=[dict(name='Synthetic School',source_id=sid)],
                    requirement_bindings=[dict(shared_id='shared-foundations',id=pid+'-foundations',
                        parent_id=None,course_ids=[pid+'-ai',pid+'-cs'],source_id=sid)],
                    requirement_overrides=[],components=[dict(kind='domain',
                        classification_kind='analyst_classified',source_ids=[sid],
                        requirement_ids=[pid+'-domain'])]))


def nodes(program):return {node['id']:node for node in program['requirements']}


def test_two_variants_resolve_one_core_with_local_ids_sources_and_distinct_awards():
    family=synthetic_family();biology=synthetic_variant();philosophy=synthetic_variant('philosophy','BA')
    snapshots=deepcopy((family,biology,philosophy))
    for variant in (biology,philosophy):
        result=resolve_program(variant,family);pid=variant['id'];shared=nodes(result)[pid+'-foundations']
        assert result['id']==pid and result['award_level']==variant['award_level']
        assert result['title']==variant['title'] and result['curriculum_status']=='partial'
        assert shared['course_ids']==[pid+'-ai',pid+'-cs']
        assert shared['source_id']==pid+'-catalog'
        assert shared['family_source_id']=='family-catalog'
        assert shared['family_requirement_id']=='shared-foundations'
        assert shared['origin']=='family' and shared['component']=='ai_core'
        assert 'course_codes' not in shared
        assert nodes(result)[pid+'-domain']['origin']=='variant'
        assert nodes(result)[pid+'-domain']['component']=='domain'
        assert nodes(result)[pid+'-domain']['component_classification']=='analyst_classified'
    assert (family,biology,philosophy)==snapshots


def test_no_family_is_a_deep_copy_and_never_adds_relationship_or_audit():
    original=synthetic_variant();original.pop('family')
    result=resolve_program(original)
    assert result==original and result is not original
    result['courses'][0]['name']='Changed'
    assert original['courses'][0]['name']!='Changed'
    assert 'curriculum_audit' not in result and 'family' not in result


def test_unknown_relationship_remains_unknown_without_inference_from_title():
    variant=synthetic_variant();variant['title']='Biology with AI'
    variant['family'].update(relationship='unknown',classification_kind='unknown')
    result=resolve_program(variant,synthetic_family())
    assert result['family']['relationship']=='unknown'
    assert result['family']['classification_kind']=='unknown'


def test_explicit_exclusion_works_without_binding_and_keeps_local_additions():
    variant=synthetic_variant();variant['family']['requirement_bindings']=[]
    variant['family']['requirement_overrides']=[dict(shared_id='shared-foundations',
        operation='exclude',reason='Reviewed synthetic catalog does not require this core.',source_id='ai-biology-catalog')]
    result=resolve_program(variant,synthetic_family())
    assert set(nodes(result))=={'ai-biology-domain'}


def test_explicit_replacement_retains_bound_id_and_its_own_requirements():
    variant=synthetic_variant();variant['requirements'].append(requirement('ai-biology-foundations',
        'ai-biology-catalog',courses=['ai-biology-ai'],kind='choose_courses',count=1))
    variant['family']['requirement_overrides']=[dict(shared_id='shared-foundations',operation='replace',
        reason='Reviewed alternative core for this invented variant.',source_id='ai-biology-catalog')]
    result=nodes(resolve_program(variant,synthetic_family()))['ai-biology-foundations']
    assert result['origin']=='replacement' and result['family_requirement_id']=='shared-foundations'
    assert result['kind']=='choose_courses' and result['count']==1
    assert result['course_ids']==['ai-biology-ai']


@pytest.mark.parametrize('change',[
    lambda f,v:v['family'].update(id='other-family'),
    lambda f,v:v['institution'].update(id='other-university'),
    lambda f,v:v['family'].update(variant_label=''),
    lambda f,v:v['family'].update(relationship='dominant_ai'),
    lambda f,v:v['family'].update(classification_kind='unknown'),
    lambda f,v:v['family'].update(disciplines=[]),
    lambda f,v:v['family'].update(source_ids=['unregistered']),
    lambda f,v:v['family']['hosting_units'][0].update(source_id='unregistered'),
    lambda f,v:v['family']['components'][0].update(source_ids=['unregistered']),
    lambda f,v:v['family']['components'][0].update(requirement_ids=['absent']),
    lambda f,v:v['family']['components'][0].update(classification_kind='unknown'),
    lambda f,v:v['family'].update(requirement_bindings=[]),
    lambda f,v:v['family']['requirement_bindings'][0].update(shared_id='unregistered'),
    lambda f,v:v['family']['requirement_bindings'][0].update(source_id='unregistered'),
    lambda f,v:v['family']['requirement_bindings'][0].update(course_ids=['absent']),
    lambda f,v:v['family']['requirement_bindings'][0].update(course_ids=['ai-biology-domain']),
    lambda f,v:v['family']['requirement_bindings'][0].update(parent_id='absent'),
    lambda f,v:v['family']['requirement_bindings'][0].update(parent_id='ai-biology-foundations'),
    lambda f,v:v['requirements'].append(requirement('ai-biology-foundations','ai-biology-catalog')),
    lambda f,v:v['requirements'].append(deepcopy(v['requirements'][0])),
    lambda f,v:v['family']['requirement_bindings'].append(deepcopy(v['family']['requirement_bindings'][0])),
])
def test_invalid_membership_binding_component_or_silent_collision_rejected(change):
    family=synthetic_family();variant=synthetic_variant();change(family,variant)
    with pytest.raises(ValueError):resolve_program(variant,family)


@pytest.mark.parametrize('override',[
    dict(shared_id='unknown',operation='exclude',reason='Reviewed',source_id='ai-biology-catalog'),
    dict(shared_id='shared-foundations',operation='ignore',reason='Reviewed',source_id='ai-biology-catalog'),
    dict(shared_id='shared-foundations',operation='exclude',reason='',source_id='ai-biology-catalog'),
    dict(shared_id='shared-foundations',operation='exclude',reason='Reviewed',source_id='unknown'),
    dict(shared_id='shared-foundations',operation='replace',reason='Reviewed',source_id='ai-biology-catalog'),
])
def test_invalid_or_missing_replacement_override_rejected(override):
    variant=synthetic_variant();variant['family']['requirement_overrides']=[override]
    with pytest.raises(ValueError):resolve_program(variant,synthetic_family())


def test_exclusion_cannot_leave_its_local_replacement_or_dangling_children():
    variant=synthetic_variant();variant['family']['requirement_overrides']=[dict(shared_id='shared-foundations',operation='exclude',reason='Reviewed',source_id='ai-biology-catalog')]
    variant['requirements'].append(requirement('ai-biology-foundations','ai-biology-catalog'))
    with pytest.raises(ValueError):resolve_program(variant,synthetic_family())
    variant['requirements'].pop();variant['requirements'][0]['parent_id']='ai-biology-foundations'
    with pytest.raises(ValueError):resolve_program(variant,synthetic_family())


def test_cross_boundary_requirement_cycle_rejected():
    variant=synthetic_variant();variant['requirements'][0]['parent_id']='ai-biology-foundations'
    variant['family']['requirement_bindings'][0]['parent_id']='ai-biology-domain'
    with pytest.raises(ValueError,match='cycle'):resolve_program(variant,synthetic_family())


@pytest.mark.parametrize('change',[
    lambda f:f.update(id='../unsafe'),lambda f:f.update(institution_id=''),
    lambda f:f.update(classification_kind='unknown'),lambda f:f.update(shared_requirements=[]),
    lambda f:f.update(sources=[]),lambda f:f['sources'].append(deepcopy(f['sources'][0])),
    lambda f:f['sources'][0].update(url='file:///private/source'),
    lambda f:f['shared_requirements'][0].update(source_id='unknown'),
    lambda f:f['shared_requirements'][0].update(component='unreviewed_component'),
    lambda f:f['shared_requirements'][0].update(course_codes=[None]),
    lambda f:f['shared_requirements'][0].update(parent_id='missing'),
    lambda f:f['shared_requirements'][0].update(parent_id='shared-foundations'),
    lambda f:f['shared_requirements'].append(deepcopy(f['shared_requirements'][0])),
])
def test_invalid_shared_definition_rejected(change):
    family=synthetic_family();change(family)
    with pytest.raises(ValueError):validate_family(family)


def nested_family_and_variant():
    family=synthetic_family();variant=synthetic_variant()
    shared=requirement('shared-choice','family-catalog',kind='alternative',component='ai_core')
    shared.pop('course_ids');shared['course_codes']=[]
    family['shared_requirements'].insert(0,shared)
    family['shared_requirements'][1]['parent_id']='shared-choice'
    variant['family']['requirement_bindings'].insert(0,dict(shared_id='shared-choice',
        id='ai-biology-choice',parent_id=None,course_ids=[],source_id='ai-biology-catalog'))
    variant['family']['requirement_bindings'][1]['parent_id']='ai-biology-choice'
    return family,variant


def test_nested_shared_choice_preserves_variant_tree():
    family,variant=nested_family_and_variant()
    result=nodes(resolve_program(variant,family))
    assert result['ai-biology-choice']['kind']=='alternative'
    assert result['ai-biology-foundations']['parent_id']=='ai-biology-choice'


def test_shared_parent_cannot_be_silently_flattened_without_override():
    family,variant=nested_family_and_variant()
    variant['family']['requirement_bindings'][1]['parent_id']=None
    with pytest.raises(ValueError):resolve_program(variant,family)


def test_domain_replacement_does_not_inherit_ai_component_without_evidence():
    variant=synthetic_variant();variant['requirements'].append(requirement('ai-biology-foundations',
        'ai-biology-catalog',courses=['ai-biology-domain']))
    variant['family']['requirement_overrides']=[dict(shared_id='shared-foundations',operation='replace',
        reason='The local catalog replaces this group with a domain requirement.',source_id='ai-biology-catalog')]
    node=nodes(resolve_program(variant,synthetic_family()))['ai-biology-foundations']
    assert node.get('component','other')=='other'


def test_shared_root_can_mount_under_reviewed_local_group():
    family=synthetic_family();variant=synthetic_variant()
    variant['requirements'].append(requirement('ai-biology-major-core','ai-biology-catalog'))
    variant['family']['requirement_bindings'][0]['parent_id']='ai-biology-major-core'
    result=nodes(resolve_program(variant,family))
    assert result['ai-biology-foundations']['parent_id']=='ai-biology-major-core'
    assert result['ai-biology-foundations']['component_classification']=='analyst_classified'


def test_explicit_replacement_can_change_shared_parent_and_get_reviewed_component():
    family,variant=nested_family_and_variant()
    variant['requirements'].append(requirement('ai-biology-foundations','ai-biology-catalog',
        courses=['ai-biology-domain']))
    variant['family']['requirement_overrides']=[dict(shared_id='shared-foundations',operation='replace',
        reason='Reviewed replacement moved outside the former alternative group.',source_id='ai-biology-catalog')]
    variant['family']['components'][0]['requirement_ids'].append('ai-biology-foundations')
    result=nodes(resolve_program(variant,family))['ai-biology-foundations']
    assert result['parent_id'] is None
    assert result['component']=='domain' and result['component_classification']=='analyst_classified'
    assert result['origin']=='replacement'


def test_excluding_shared_parent_requires_explicit_handling_of_its_children():
    family,variant=nested_family_and_variant()
    variant['family']['requirement_overrides']=[dict(shared_id='shared-choice',operation='exclude',
        reason='Reviewed',source_id='ai-biology-catalog')]
    with pytest.raises(ValueError):resolve_program(variant,family)


def test_duplicate_override_and_local_binding_ids_rejected():
    family,variant=nested_family_and_variant()
    row=dict(shared_id='shared-choice',operation='exclude',reason='Reviewed',source_id='ai-biology-catalog')
    variant['family']['requirement_overrides']=[row,deepcopy(row)]
    with pytest.raises(ValueError,match='Duplicate'):resolve_program(variant,family)
    variant['family']['requirement_overrides']=[]
    variant['family']['requirement_bindings'][1]['id']=variant['family']['requirement_bindings'][0]['id']
    with pytest.raises(ValueError,match='same program node'):resolve_program(variant,family)


def test_family_update_with_different_course_scope_invalidates_dependent_binding():
    family=synthetic_family();variant=synthetic_variant()
    resolve_program(variant,family)
    family['shared_requirements'][0]['course_codes'].append('AI 299')
    with pytest.raises(ValueError,match='course identities'):resolve_program(variant,family)


def test_resolution_is_idempotent_for_program_without_family():
    variant=synthetic_variant();variant.pop('family')
    assert resolve_program(resolve_program(variant))==variant


def test_local_requirements_cannot_spoof_family_origin_or_unreviewed_component():
    variant=synthetic_variant();variant['family']['components']=[]
    variant['requirements'][0].update(origin='family',family_requirement_id='invented-shared',
        family_source_id='invented-source',component='ai_core',component_classification='source_stated')
    node=nodes(resolve_program(variant,synthetic_family()))['ai-biology-domain']
    assert node['origin']=='variant'
    assert node.get('component','other')=='other'
    assert 'family_requirement_id' not in node and 'family_source_id' not in node
    assert node.get('component_classification','unknown')!='source_stated'


@pytest.fixture
def family_database(tmp_path):
    from atlas import db
    from atlas.family_store import ingest_family
    conn=db.connect(tmp_path/'families.sqlite');db.migrate(conn)
    family=synthetic_family();variant=synthetic_variant()
    with conn:db.upsert_institution(conn,variant['institution'])
    ingest_family(conn,family)
    yield conn,family
    conn.close()


def test_family_database_stores_shared_facts_once_and_exports_concrete_variants(family_database):
    import json
    from atlas import db
    from atlas.family_store import load_family
    conn,family=family_database
    for variant in [synthetic_variant(),synthetic_variant('philosophy','BA')]:db.ingest_program(conn,variant)
    loaded=load_family(conn,family['id'])
    assert loaded['shared_requirements'][0]['course_codes']==['AI 101','CS 102']
    assert conn.execute('SELECT count(*) FROM family_requirement_groups').fetchone()[0]==1
    assert conn.execute('SELECT count(*) FROM requirement_groups').fetchone()[0]==2
    assert conn.execute('SELECT count(*) FROM family_requirement_bindings').fetchone()[0]==2
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    for row in conn.execute('SELECT record_zlib,content_hash FROM programs'):
        raw=db.program_record(row);assert len(raw['requirements'])==1
        assert all(n['id'].endswith('-domain') for n in raw['requirements'])
    data=db.export_data(conn)
    assert len(data['families'])==1 and len(data['programs'])==2
    assert data['meta']['coverage_summary']['programs']==2
    assert {p['award_level'] for p in data['programs']}=={'BS','BA'}
    for p in data['programs']:
        assert len(p['requirements'])==2
        assert nodes(p)[p['id']+'-foundations']['source_id']==p['id']+'-catalog'
        assert p['curriculum_status']=='partial'


def test_family_migration_keeps_old_full_program_revision(family_database):
    import json
    from atlas import db
    conn,family=family_database
    variant=synthetic_variant();old=deepcopy(variant);old.pop('family')
    old['requirements'].append(requirement('ai-biology-foundations','ai-biology-catalog',
        courses=['ai-biology-ai','ai-biology-cs']))
    db.ingest_program(conn,old);db.ingest_program(conn,variant)
    revisions=[db.revision_record(row) for row in conn.execute('SELECT * FROM program_revisions ORDER BY id')]
    assert len(revisions)==2 and revisions[0]==old and revisions[1]==variant
    assert conn.execute('SELECT count(*) FROM requirement_groups').fetchone()[0]==1
    assert len(db.export_data(conn)['programs'][0]['requirements'])==2


def test_invalid_family_revision_rolls_back_all_shared_rows(family_database):
    from atlas import db
    from atlas.family_store import ingest_family,load_family
    conn,family=family_database;db.ingest_program(conn,synthetic_variant())
    before=load_family(conn,family['id']);revisions=conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]
    changed=deepcopy(family);changed['shared_requirements'][0]['course_codes'].append('AI 299')
    with pytest.raises(ValueError):ingest_family(conn,changed)
    assert load_family(conn,family['id'])==before
    assert conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]==revisions
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]


def complete_variant(family):
    from atlas import db
    variant=synthetic_variant();variant['curriculum_status']='complete'
    variant['curriculum_audit']=dict(scope='degree',reviewed_at='2026-10-10',
        source_ids=['ai-biology-catalog'],sections=['Synthetic complete test scope'],
        unresolved_requirements=[],metadata_gaps=['Synthetic course descriptions are unknown.'],
        family_content_hash=db.digest(family))
    return variant


def test_complete_family_record_requires_current_family_review_hash(family_database):
    from atlas import db
    conn,family=family_database;variant=complete_variant(family)
    stale=deepcopy(variant);stale['curriculum_audit']['family_content_hash']='old-review'
    with pytest.raises(ValueError):db.ingest_program(conn,stale)
    missing=deepcopy(variant);missing['curriculum_audit'].pop('family_content_hash')
    with pytest.raises(ValueError):db.ingest_program(conn,missing)
    assert conn.execute('SELECT count(*) FROM programs').fetchone()[0]==0
    db.ingest_program(conn,variant)
    assert db.export_data(conn)['programs'][0]['curriculum_status']=='complete'


def test_material_family_edit_needs_reaudited_dependent_and_updates_atomically(family_database):
    from atlas import db
    from atlas.family_store import ingest_family,load_family
    conn,family=family_database;variant=complete_variant(family);db.ingest_program(conn,variant)
    changed=deepcopy(family);changed['shared_requirements'][0]['summary']='A reviewed change in the shared requirement.'
    with pytest.raises(ValueError):ingest_family(conn,changed)
    assert load_family(conn,family['id'])['shared_requirements'][0]['summary']!=changed['shared_requirements'][0]['summary']
    reviewed=deepcopy(variant);reviewed['curriculum_audit']['family_content_hash']=db.digest(changed)
    ingest_family(conn,changed,program_updates={reviewed['id']:reviewed})
    exported=db.export_data(conn)['programs'][0]
    assert exported['curriculum_audit']['family_content_hash']==db.digest(changed)
    assert nodes(exported)['ai-biology-foundations']['summary']==changed['shared_requirements'][0]['summary']
    assert exported['curriculum_status']=='complete'
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]


def test_bad_dependent_update_cannot_partially_replace_family(family_database):
    from atlas import db
    from atlas.family_store import ingest_family,load_family
    conn,family=family_database;variant=synthetic_variant();db.ingest_program(conn,variant)
    original=load_family(conn,family['id']);changed=deepcopy(family);changed['name']='Changed synthetic family'
    bad=deepcopy(variant);bad['family']['requirement_bindings'][0]['course_ids']=['not-a-course']
    with pytest.raises(ValueError):ingest_family(conn,changed,program_updates={bad['id']:bad})
    assert load_family(conn,family['id'])==original
    assert db.export_data(conn)['programs'][0]['title']==variant['title']


def test_ingest_all_rolls_back_family_and_programs_if_later_program_fails(tmp_path):
    import json
    from atlas import db
    from atlas.cli import ingest_all
    conn=db.connect(tmp_path/'rollback.sqlite');db.migrate(conn)
    family=synthetic_family();variant=synthetic_variant()
    with conn:db.upsert_institution(conn,variant['institution'])
    data=tmp_path/'input';(data/'families').mkdir(parents=True);(data/'programs').mkdir()
    (data/'families'/'family.json').write_text(json.dumps(family))
    (data/'programs'/'a-valid.json').write_text(json.dumps(variant))
    bad=synthetic_variant('philosophy');bad['requirements'][0]['source_id']='missing-source'
    (data/'programs'/'z-invalid.json').write_text(json.dumps(bad))
    with pytest.raises(ValueError,match="Unknown source missing-source"):ingest_all(conn,data)
    assert conn.execute('SELECT count(*) FROM program_families').fetchone()[0]==0
    assert conn.execute('SELECT count(*) FROM programs').fetchone()[0]==0
    assert conn.execute('SELECT count(*) FROM program_revisions').fetchone()[0]==0
    assert conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]==0
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    conn.close()


def test_unknown_family_load_fails_and_repeat_ingestion_is_idempotent(family_database):
    from atlas import db
    from atlas.family_store import ingest_family,load_family
    conn,family=family_database;variant=synthetic_variant()
    with pytest.raises(ValueError,match='Unknown program family'):load_family(conn,'missing-family')
    db.ingest_program(conn,variant)
    ingest_family(conn,family);db.ingest_program(conn,variant)
    assert conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]==1
    assert conn.execute('SELECT count(*) FROM program_revisions').fetchone()[0]==1
    assert conn.execute('SELECT count(*) FROM family_binding_courses').fetchone()[0]==2


def test_ingest_all_existing_family_and_variants_roll_back_on_later_failure(family_database,tmp_path):
    import json
    from atlas import db
    from atlas.cli import ingest_all
    from atlas.family_store import load_family
    conn,family=family_database;variant=synthetic_variant();db.ingest_program(conn,variant)
    family_before=load_family(conn,family['id'])
    raw_before=conn.execute('SELECT record_zlib FROM programs WHERE id=?',(variant['id'],)).fetchone()[0]
    data=tmp_path/'existing-input';(data/'families').mkdir(parents=True);(data/'programs').mkdir()
    changed=deepcopy(family);changed['name']='A new reviewed family label'
    (data/'families'/'family.json').write_text(json.dumps(changed))
    updated=deepcopy(variant);updated['overview']='A changed program description'
    (data/'programs'/'a-updated.json').write_text(json.dumps(updated))
    bad=synthetic_variant('philosophy');bad['requirements'][0]['source_id']='missing-source'
    (data/'programs'/'z-invalid.json').write_text(json.dumps(bad))
    with pytest.raises(ValueError,match='Unknown source missing-source'):ingest_all(conn,data)
    assert load_family(conn,family['id'])==family_before
    assert conn.execute('SELECT record_zlib FROM programs WHERE id=?',(variant['id'],)).fetchone()[0]==raw_before
    assert conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]==1
    assert conn.execute('SELECT count(*) FROM program_revisions').fetchone()[0]==1


def test_candidate_review_compares_against_resolved_shared_requirements(family_database,capsys):
    from types import SimpleNamespace
    from atlas import db
    from atlas.cli import main
    from atlas.scrape import scrape_one
    from atlas.http import FetchResult
    conn,family=family_database;variant=synthetic_variant();db.ingest_program(conn,variant)
    resolved=resolve_program(variant,family)
    payload=dict(id=variant['id'],requirements=resolved['requirements'],courses=variant['courses'])
    nodes(payload)['ai-biology-foundations']['summary']='A newly observed shared rule.'
    module=SimpleNamespace(SOURCES=['https://example.edu/observed'],parse=lambda html:payload)
    class Fetch:
        def fetch(self,url,**kwargs):return FetchResult(url,'synthetic body','body-hash','2026-10-10',200,False)
    result=scrape_one(conn,variant['id'],module,Fetch())
    assert result['status']=='success' and result['new_candidates']==1
    cid=conn.execute('SELECT id FROM extraction_candidates').fetchone()[0]
    path=conn.execute('PRAGMA database_list').fetchone()[2]
    assert main(['--db',path,'review',str(cid)])==0
    output=capsys.readouterr().out
    assert any(line.startswith('-') and 'An invented requirement for testing.' in line for line in output.splitlines())
    assert any(line.startswith('+') and 'A newly observed shared rule.' in line for line in output.splitlines())
    assert 'No data was changed' in output
    assert db.export_data(conn)['programs'][0]['curriculum_status']=='partial'


def test_family_update_mapping_cannot_substitute_another_dependent_identity(family_database):
    from atlas import db
    from atlas.family_store import ingest_family,load_family
    conn,family=family_database;variant=complete_variant(family);db.ingest_program(conn,variant)
    changed=deepcopy(family);changed['name']='Changed family awaiting review'
    impostor=synthetic_variant('philosophy','BA')
    before=load_family(conn,family['id'])
    with pytest.raises(ValueError):
        ingest_family(conn,changed,program_updates={variant['id']:impostor})
    assert load_family(conn,family['id'])==before
    assert conn.execute('SELECT count(*) FROM programs').fetchone()[0]==1


def test_program_updates_are_applied_even_when_family_definition_is_unchanged(family_database):
    from atlas import db
    from atlas.family_store import ingest_family
    conn,family=family_database;variant=synthetic_variant();db.ingest_program(conn,variant)
    updated=deepcopy(variant);updated['overview']='Newly reviewed variant description.'
    ingest_family(conn,family,program_updates={updated['id']:updated})
    assert db.export_data(conn)['programs'][0]['overview']==updated['overview']
    assert conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]==1
    assert conn.execute('SELECT count(*) FROM program_revisions').fetchone()[0]==2


def test_family_schema_upgrade_preserves_existing_requirement_rows(tmp_path):
    from pathlib import Path
    from atlas import db
    conn=db.connect(tmp_path/'pre-family.sqlite')
    conn.execute('CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)')
    migrations=Path(db.__file__).parent/'migrations'
    for path in sorted(migrations.glob('*.sql')):
        version=int(path.name.split('_')[0])
        if version>=5:continue
        conn.executescript(path.read_text())
        conn.execute('INSERT INTO schema_migrations VALUES (?,?)',(version,'2026-10-10'))
        conn.commit()
    program=synthetic_variant();program.pop('family');pid=program['id'];sid=pid+'-catalog'
    with conn:
        db.upsert_institution(conn,program['institution'])
        conn.execute('''INSERT INTO programs(id,institution_id,title,award_level,program_kind,status,
            overview,catalog_year,verification_status,curriculum_status,last_verified,content_hash,record_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',(pid,'synthetic-university',program['title'],'BS','degree',
            'unknown',program['overview'],'2026–2027','partial','partial','2026-10-10',db.digest(program),db.canonical(program)))
        conn.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?)',(pid,sid,'https://example.edu/catalog','Synthetic',None,None,None,None,'high'))
        conn.execute('INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(pid,pid+'-domain','BIOLOGY 201','Synthetic',None,None,None,'unknown','other',sid,None,None,None))
        conn.execute('INSERT INTO requirement_groups VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(pid,pid+'-domain',None,'Local domain','all',None,None,'unknown','other',sid,None,'Local requirement.'))
        conn.execute('INSERT INTO requirement_courses VALUES (?,?,?)',(pid,pid+'-domain',pid+'-domain'))
    before=[tuple(row) for row in conn.execute('SELECT * FROM requirement_groups')]
    membership=[tuple(row) for row in conn.execute('SELECT * FROM requirement_courses')]
    db.migrate(conn)
    assert [tuple(row) for row in conn.execute('SELECT * FROM requirement_groups')]==before
    assert [tuple(row) for row in conn.execute('SELECT * FROM requirement_courses')]==membership
    assert db.program_record(conn.execute('SELECT record_zlib,content_hash FROM programs').fetchone())==program
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    conn.close()


def test_reviewed_shared_id_and_course_scope_change_updates_two_variants_atomically(family_database):
    from atlas import db
    from atlas.family_store import ingest_family,load_family
    conn,family=family_database;variants=[synthetic_variant(),synthetic_variant('philosophy','BA')]
    for variant in variants:db.ingest_program(conn,variant)
    changed=deepcopy(family);shared=changed['shared_requirements'][0]
    shared['id']='shared-expanded-core';shared['course_codes'].append('AI 299')
    updates={}
    for variant in variants:
        updated=deepcopy(variant);pid=updated['id'];course=deepcopy(updated['courses'][0])
        course.update(id=pid+'-advanced',code='AI 299',name='Synthetic advanced AI')
        updated['courses'].append(course)
        binding=updated['family']['requirement_bindings'][0]
        binding['shared_id']='shared-expanded-core';binding['course_ids'].append(course['id'])
        updates[pid]=updated
    ingest_family(conn,changed,program_updates=updates)
    assert load_family(conn,family['id'])==changed
    for program in db.export_data(conn)['programs']:
        inherited=nodes(program)[program['id']+'-foundations']
        assert inherited['family_requirement_id']=='shared-expanded-core'
        assert len(inherited['course_ids'])==3
    assert conn.execute('SELECT count(*) FROM family_requirement_groups').fetchone()[0]==1
    assert conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]==2
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]


def test_optional_family_shape_and_annotations_round_trip_without_hash_drift(tmp_path):
    from atlas import db
    from atlas.family_store import ingest_family,load_family
    conn=db.connect(tmp_path/'shape.sqlite');db.migrate(conn)
    family=synthetic_family();shared=family['shared_requirements'][0]
    shared.pop('source_text');shared.pop('component')
    shared['review_note']='An explicit synthetic reviewer annotation.'
    family['sources'][0].pop('source_date')
    with conn:db.upsert_institution(conn,synthetic_variant()['institution'])
    ingest_family(conn,family)
    loaded=load_family(conn,family['id'])
    assert loaded==family and db.digest(loaded)==db.digest(family)
    db.ingest_program(conn,complete_variant(family))
    assert db.export_data(conn)['programs'][0]['curriculum_status']=='complete'
    conn.close()


def test_standalone_family_import_without_cohort_creates_institution_first(tmp_path):
    import json
    from atlas import db
    from atlas.cli import ingest_all
    conn=db.connect(tmp_path/'standalone.sqlite');db.migrate(conn)
    data=tmp_path/'standalone-input';(data/'families').mkdir(parents=True);(data/'programs').mkdir()
    (data/'families'/'family.json').write_text(json.dumps(synthetic_family()))
    for variant in [synthetic_variant(),synthetic_variant('philosophy','BA')]:
        (data/'programs'/(variant['id']+'.json')).write_text(json.dumps(variant))
    assert ingest_all(conn,data)==2
    exported=db.export_data(conn)
    assert len(exported['families'])==1 and len(exported['programs'])==2
    assert len(exported['institutions'])==1
    assert exported['institutions'][0]['id']=='synthetic-university'
    assert ingest_all(conn,data)==0
    assert conn.execute('SELECT count(*) FROM family_revisions').fetchone()[0]==1
    assert conn.execute('SELECT count(*) FROM program_revisions').fetchone()[0]==2
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    conn.close()
