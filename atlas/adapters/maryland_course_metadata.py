"""Selected official Maryland course blocks; no topic or permission inference."""
import re
from functools import partial
from atlas.adapters.national_curriculum_common import content,clean,require_phrases
from atlas.adapters.cmu_bs.common import course

BASE='https://academiccatalog.umd.edu/undergraduate/approved-courses/'
HEADINGS={'math':'MATH - Mathematics','cmsc':'CMSC - Computer Science','inst':'INST - Information Studies'}
# Reviewed paraphrases: markers must still be present in the exact course block.
DESCRIPTIONS={
 'MATH115':('Elementary functions and graphs','Precalculus preparation develops algebra and graphical reasoning with polynomial, rational, exponential, logarithmic and trigonometric functions.'),
 'CMSC131':('Programming done in Java','Introduces Java programming through object-oriented design, implementation and testing using development tools.'),
 'CMSC132':('medium -size software systems','Builds object-oriented software-engineering skills through designing, testing and debugging medium-sized Java systems and using APIs.'),
 'CMSC250':('permutations, combinations, graphs','Develops discrete mathematical tools for computing, including sets, relations, logic, counting, graphs and trees.'),
 'CMSC320':('end-to-end process','Surveys the data-science workflow from messy data to useful conclusions, including analysis, learning methods, data systems and visualization.'),
 'CMSC351':('recurrences and summations','Uses mathematical analysis to study algorithmic complexity in sorting, graphs, trees and combinatorics.'),
 'CMSC422':('adaptive systems','Introduces learning representations and algorithms, emphasizing practical machine learning and data mining.'),
 'INST204':('algorithmic bias','Examines how values built into automated decisions produce unequal outcomes, drawing on technical, legal and social approaches to algorithmic bias.'),
 'INST326':('object-oriented techniques','Introduces object-oriented programming through application design, implementation and testing.'),
}


def parse(html,*,pid,prefix,codes):
    root=content(html,HEADINGS[prefix])
    wanted=set(codes);found={}
    for block in root.find_all(class_='courseblock'):
        title=block.find(class_='courseblocktitle')
        if title is None:continue
        match=re.fullmatch(r'([A-Z]+\d+[A-Z]?) (.+) \(([^()]+) Credits?\)',clean(title.get_text(' ',strip=True)))
        if not match or match[1] not in wanted:continue
        code,name,amount=match.groups()
        if code in found:raise ValueError('Duplicate selected Maryland course block')
        c=course(code,name,pid+'-courses-'+prefix,BASE+prefix+'/',institution='umd',unit='semester_hours',credits=int(amount) if amount.isdigit() else None)
        fields=[]
        for extra in block.find_all(class_='courseblockextra'):
            label=extra.find('strong')
            if label and clean(label.get_text()).rstrip(':') in {'Prerequisite','Corequisite','Restriction','Credit Only Granted for'}:
                fields.append(clean(extra.get_text(' ',strip=True)))
        c['prerequisites']=' '.join(fields) or None
        if code in DESCRIPTIONS:
            marker,summary=DESCRIPTIONS[code]
            desc=block.find(class_='courseblockdesc')
            if desc is None:raise ValueError('Selected description missing: '+code)
            require_phrases(desc,[marker]);c['description']=summary
        found[code]=c
    if not found:raise ValueError('No reviewed Maryland course blocks found')
    return dict(id=pid,courses=list(found.values()))


# These code selections are reviewed adapter configuration, never read from seeds at runtime.
TARGETS = {'university-of-maryland-college-park-human-centered-ai-ba-degree': {'math': ['MATH115'],
                                                                     'inst': ['INST204',
                                                                              'INST366',
                                                                              'INST430',
                                                                              'INST431',
                                                                              'INST432',
                                                                              'INST433',
                                                                              'INST436',
                                                                              'INST480']},
 'university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree': {'math': ['MATH140',
                                                                                                                              'MATH141',
                                                                                                                              'MATH240',
                                                                                                                              'MATH243',
                                                                                                                              'MATH340',
                                                                                                                              'MATH341',
                                                                                                                              'MATH461'],
                                                                                                                     'cmsc': ['CMSC131',
                                                                                                                              'CMSC132',
                                                                                                                              'CMSC141',
                                                                                                                              'CMSC142',
                                                                                                                              'CMSC250',
                                                                                                                              'CMSC320',
                                                                                                                              'CMSC351',
                                                                                                                              'CMSC401',
                                                                                                                              'CMSC421',
                                                                                                                              'CMSC422',
                                                                                                                              'CMSC425',
                                                                                                                              'CMSC426',
                                                                                                                              'CMSC427',
                                                                                                                              'CMSC434',
                                                                                                                              'CMSC436',
                                                                                                                              'CMSC454',
                                                                                                                              'CMSC470',
                                                                                                                              'CMSC471',
                                                                                                                              'CMSC472',
                                                                                                                              'CMSC474',
                                                                                                                              'CMSC477'],
                                                                                                                     'inst': ['INST204',
                                                                                                                              'INST326',
                                                                                                                              'INST362',
                                                                                                                              'INST366',
                                                                                                                              'INST401',
                                                                                                                              'INST402',
                                                                                                                              'INST414',
                                                                                                                              'INST436',
                                                                                                                              'INST461']}}


def parsers(pid):
    return {BASE+prefix+'/':partial(parse,pid=pid,prefix=prefix,codes=codes) for prefix,codes in TARGETS[pid].items()}
