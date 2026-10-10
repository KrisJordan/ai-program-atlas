"""CourseLeaf table observations with explicit bundles, alternatives and provenance.

Used by source-specific degree adapters; this helper never asserts completeness.
"""
import re
from urllib.parse import urljoin
from atlas.adapters.national_curriculum_common import clean,course,rule


def slug(text):return re.sub(r'[^a-z0-9]+','-',text.casefold()).strip('-')


class Tables:
    def __init__(self,prefix,sid,url,unit='unknown'):
        self.prefix,self.sid,self.url,self.unit=prefix,sid,url,unit
        self.courses={};self.rules=[];self.serial=0

    def group(self,title,**kwargs):
        self.serial+=1
        node=rule(f'{self.prefix}-r{self.serial}',title,self.sid,unit=self.unit,**kwargs)
        self.rules.append(node);return node

    def row(self,row,topic=None):
        cells=row.find_all('td',recursive=False)
        codecell=row.find('td',class_='codecol')
        if codecell is None or len(cells)<2:return None
        links=codecell.find_all('a',class_='code')
        if not links:return None
        nameparts=[clean(x) for x in cells[1].stripped_strings]
        names=[]
        for name in nameparts:
            if name.startswith('and '):name=name[4:]
            if name and name not in ('and','or'):names.append(name)
        if len(names)!=len(links):
            if len(links)==1:names=[clean(cells[1].get_text(' ',strip=True))]
            elif len(names)==1 and '/' in clean(codecell.get_text(' ',strip=True)):names=names*len(links)
            else:raise ValueError('Unrecognized bundled course-title structure')
        hours=row.find('td',class_='hourscol');value=clean(hours.get_text()) if hours else ''
        credit=float(value) if re.fullmatch(r'\d+(?:\.\d+)?',value) and len(links)==1 else None
        ids=[];topic_name=topic
        for a,name in zip(links,names):
            code=clean(a.get_text(' ',strip=True))
            special=bool(re.search(r'Special Topics|Selected Topics|Special Projects',name,re.I))
            if special and '(' in name:topic_name=name
            if special and topic_name and '(' not in name:name+=' — approved topic: '+topic_name
            category='mathematics' if code.startswith(('MATH ','STAT ','CMOR ')) else 'human_context' if code.startswith(('PHIL ','HUMN ','COMM_ST ')) else 'ai_ml' if any(w in name.lower() for w in ['artificial intelligence','machine learning','robot','vision','neural','language model','deep learning']) else 'other'
            c=course(self.prefix,code,name,self.sid,urljoin(self.url,a['href']),credits=credit,unit=self.unit,category=category,topic=topic_name if special else None)
            prior=self.courses.get(c['id'])
            if prior and c['credits'] is None:c['credits']=prior['credits']
            self.courses[c['id']]=c;ids.append(c['id'])
        bundle='&' in clean(codecell.get_text(' ',strip=True))
        return dict(ids=ids,title=' + '.join(names),topic=topic_name,indented=bool(codecell.find(class_='blockindent')),bundle=bundle)

    def table(self,table,title,*,parent=None,kind='all',count=None,category='other',interpret_choices=True):
        root=self.group(title,parent=parent,kind=kind,count=count,category=category)
        scope=root;choice=None;last=None
        for row in table.find_all('tr'):
            cells=row.find_all('td',recursive=False)
            if not cells:continue
            classes=row.get('class',[])
            if 'listsum' in classes:continue
            parsed=self.row(row,last.get('topic') if last and 'orclass' in classes else None)
            if parsed is None:
                text=clean(cells[0].get_text(' ',strip=True))
                m=re.match(r'(?:Choose|Select) (one|three|six|1)\b',text)
                if interpret_choices and m and 'or two' not in text:
                    n={'one':1,'three':3,'six':6,'1':1}[m[1]]
                    choice=self.group('Choose '+str(n)+' course option'+('s' if n>1 else ''),parent=root['id'],kind='alternative' if n==1 else 'choose_courses',count=n if n>1 else None,summary='Select '+str(n)+' listed option'+('s.' if n>1 else '. A bundled row requires every course in that option.'))
                    scope=choice;last=None
                continue
            if choice and not parsed['indented'] and 'orclass' not in classes:
                scope=root;choice=None
            if 'orclass' in classes:
                if not last:raise ValueError('Alternative row without prior course slot')
                previous=last['node']
                if not last.get('alternative'):
                    alt=self.group('Choose an alternative for '+previous['title'],parent=previous['parent_id'],kind='alternative',summary='Complete one listed course or course bundle for this slot.')
                    previous['parent_id']=alt['id'];last['alternative']=alt
                entry=self.group(parsed['title'],parent=last['alternative']['id'],ids=parsed['ids'])
            else:
                entry=self.group(parsed['title'],parent=scope['id'],ids=parsed['ids'])
                last=dict(node=entry,topic=parsed['topic'])
        return root
