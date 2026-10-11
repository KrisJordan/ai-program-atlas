"""Read the official UI's downloaded XLSX; no hidden endpoints or source redistribution.

Rerun: python -m atlas.adapters.university-of-south-florida-artificial-intelligence-bs-degree.ge_export '/path/Course Inventory.xlsx'
Outputs factual attribute rows for review; never updates the database or audit.
"""
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
HEADERS=['College','Department','Prefix','Number','Title','Credits','Course Attributes(s)']
GE={'SGEC','SGEH','SGEM','SGEN','SGES','UGEC','UGEH','UGEM','UGEN','UGES'}

def read_export(path):
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist())>20_000_000:raise ValueError('Unexpectedly large course export')
        shared=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        rows=[]
        for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:row',NS):
            values={}
            for cell in row.findall('s:c',NS):
                col=''.join(c for c in cell.get('r','') if c.isalpha());v=cell.find('s:v',NS);value=v.text if v is not None else ''
                values[col]=shared[int(value)] if cell.get('t')=='s' else value
            rows.append([values.get(c,'') for c in 'ABCDEFG'])
    if rows[:2]!=[HEADERS,['','','','','','','One USF']]:raise ValueError('USF export headers/scope changed')
    result=[];seen=set()
    for row in rows[2:]:
        code=row[2]+' '+row[3];attrs=[v.strip() for v in row[6].split(',') if v.strip()]
        if code in seen or not row[2] or not row[3] or not GE.intersection(attrs):raise ValueError('Unexpected or duplicate GE course')
        seen.add(code);result.append(dict(code=code,name=row[4],credits=float(row[5]),attributes=attrs))
    if not result:raise ValueError('Empty pool is not a deletion instruction')
    return result
if __name__=='__main__':print(json.dumps(read_export(sys.argv[1]),indent=2,ensure_ascii=False))
