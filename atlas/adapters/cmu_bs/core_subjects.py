"""Exact BS core subjects, separate from their Computer Science table grouping."""
IDENTITIES = {
    '99-101': ('Core@CMU', 'human_context'),
    '15-122': ('Principles of Imperative Computation', 'foundations'),
    '15-150': ('Principles of Functional Programming', 'foundations'),
    '15-210': ('Parallel and Sequential Data Structures and Algorithms', 'foundations'),
    '15-213': ('Introduction to Computer Systems', 'systems'),
    '15-251': ('Great Ideas in Theoretical Computer Science', 'foundations'),
    '07-280': ('Artificial Intelligence and Machine Learning I', 'ai_ml'),
    '07-380': ('Artificial Intelligence and Machine Learning II', 'ai_ml'),
}


def classify_observed(observation):
    for c in observation.get('courses', []):
        expected = IDENTITIES.get(c['code'])
        if expected:
            # A renamed code is a review candidate, not a stale reviewed category.
            c['category'] = expected[1] if c['name'] == expected[0] else 'other'
    from .reviewed_scs import classify_titles
    from .reviewed_quantitative import classify_titles as classify_quantitative
    from .reviewed_departments import classify_titles as classify_department_titles
    return classify_department_titles(classify_quantitative(classify_titles(observation)))
