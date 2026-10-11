"""Independent catalog context, without importing major/minor rules into HASS."""
from functools import partial
from atlas.adapters.national_curriculum_common import content,require_phrases,rule,clean
PID='mit-ai-decision-making-bs'
CATALOGS={
 'cmsw':('https://catalog.mit.edu/schools/humanities-arts-social-sciences/comparative-media-studies-writing/','Comparative Media Studies/Writing',['Bachelor of Science in Comparative Media Studies (CMS)','Bachelor of Science in Writing (Course 21W)','Minor in Education']),
 'mta':('https://catalog.mit.edu/schools/humanities-arts-social-sciences/music-theater-arts/','Music and Theater Arts',['concentrations, minors, or majors in either Music or Theater Arts','Bachelor of Science in Music (Course 21M)','Minor in Theater Arts']),
}


def parse_catalog(key,html):
    url,title,markers=CATALOGS[key];root=content(html,title);require_phrases(root,markers)
    if any('concentration' in clean(h.get_text(' ',strip=True)).lower() for h in root.find_all(['h2','h3','h4'])):
        raise ValueError('New concentration-specific catalog section requires review')
    sid=PID+'-hass-'+key+'-catalog-context'
    return dict(id=PID,requirements=[rule('mit-ai-hass-'+key+'-catalog-context','Independent '+title+' catalog context',sid,kind='note',summary='This independently accessible catalog page was reviewed for the registrar-listed HASS fields. Its undergraduate sections describe majors/minors, not the missing field-specific concentration selection rules. Those other programs’ course counts and pools are not substituted for HASS concentration requirements. This is a scoped page observation, not a finding that no concentration exists.')])


SOURCE_PARSERS={v[0]:partial(parse_catalog,k) for k,v in CATALOGS.items()}
