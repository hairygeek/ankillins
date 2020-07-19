import pytest
from ankillins.main import generate_page


@pytest.fixture(params=reversed([
    'if i were you', 'sort of', 'gonna', 'for now', 'in-that-which-case', 'besides', 'believe', 'turn out',
    'as soon as', 'hell of a', 'elected', 'unless', 'case', 'face', 'gone towards', 'shin guards', 'lean towards',
    'and-so-on', 'get to', 'mean', 'rest', 'further', 'previously', 'accountable', 'in the middle of nowhere'
]))
def word(request):
    return request.param


class TestCollinsClient:

    def test_search(self, collins_client):
        s = collins_client.search('bar')
        assert s

    def test_get_word(self, collins_client, word):
        s = collins_client._get_word(word)
        assert s


def test_generate_page(collins_client, word):
    word = collins_client._get_word(word)
    page = generate_page(word)
    assert page

