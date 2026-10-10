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
