"""Keep the locked HTML parser usable for source-specific university adapters."""
import pytest
from bs4 import BeautifulSoup

@pytest.mark.parametrize('selector', ['a', 'a.course', '[data-course-code]', 'div a', '.course', '#course'])
def test_public_catalog_selectors(selector):
    soup = BeautifulSoup('<div><a id="course" class="course" data-course-code="CS101">Synthetic course</a></div>', 'html.parser')
    assert [node.get_text() for node in soup.select(selector)] == ['Synthetic course']
