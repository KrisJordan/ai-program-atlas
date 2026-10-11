"""Subject evidence for the two fixed foundation identities in 6-4_2025."""
import hashlib
SPECS={
 '6.1010':('Fundamentals of Programming',('fundamental concepts of programming','software design')),
 '6.1210':('Introduction to Algorithms',('algorithmic paradigms','data structures')),
}

def classify_annotation(course,annotation):
    expected=SPECS.get(course['code'])
    if expected is None:return None
    value=annotation.casefold()
    course['category']='foundations' if course['name']==expected[0] and all(m in value for m in expected[1]) else 'other'
    return hashlib.sha256(annotation.encode()).hexdigest()
