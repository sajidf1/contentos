from contentos.core import Request, context_for, demo_draft, score_text, handoff

def request():
    return Request('A sample title', 'Blog post', 'Enterprise expansion', 'Consideration', 'Keep it practical', ['Ad copy'])

def test_context():
    assert context_for(request())['persona'] == 'VP of Data & Analytics'

def test_demo_and_score():
    draft = demo_draft(request())
    result = score_text(draft, request())
    assert 0 <= result['score'] <= 100
    assert result['passed'] == (result['score'] > 80)

def test_handoff():
    assert handoff(request(), 88)['ticket']['id'].startswith('DEMO-')
