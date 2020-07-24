import pytest


@pytest.fixture(params=reversed([
    'if i were you', 'sort of', 'gonna', 'for now', 'in-that-which-case', 'besides', 'believe', 'turn out',
    'as soon as', 'hell of a', 'elected', 'unless', 'case', 'face', 'gone towards', 'shin guards', 'lean towards',
    'and-so-on', 'get to', 'mean', 'rest', 'further', 'previously', 'accountable', 'in the middle of nowhere',
    'further', "that's it ",
]))
def word(request):
    return request.param


class TestCollinsClient:
    # todo: mock responses

    def test_search(self, collins_client):
        s = collins_client.search('bar')
        assert s

    def test_get_word(self, collins_client, word):
        s = collins_client._get_word(word)
        assert s


# def test_generate_page(collins_client, word):
#     # words = ['since', 'during', 'so', 'way', 'rest', 'further']
#     words = ['so']
#     parsed = [collins_client._get_word(w) for w in words]
#     page = generate_pages(parsed)
#     assert page
