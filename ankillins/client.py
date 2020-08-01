import typing as ty
import io
import dataclasses

import requests as rq
import jsonschema
import yarl
from lxml import etree, html
import tenacity as tnc

from .errors import WrongResponse, NotFound
from .constants import USER_AGENT


@dataclasses.dataclass()
class WordUsageExample:
    text: str
    pronounce_url: str = None
    pronounce_path: str = None


@dataclasses.dataclass()
class Sense:
    text: str
    examples: ty.Sequence[WordUsageExample] = None


@dataclasses.dataclass()
class WordDefinition:
    senses: ty.Sequence[Sense]
    peace_of_speech: str = None


@dataclasses.dataclass()
class Word:
    word: str
    frequency: int
    pronounce_url: str
    definitions: ty.Sequence[WordDefinition]
    pronounce_filename: str = None


# Collins Dictionary hasn't respond to my request for API access, so I have to scrape it :(

class Collins:
    _SEARCH_API_URL = 'https://www.collinsdictionary.com/autocomplete/'
    _SEARCH_HINTS_URL = 'https://www.collinsdictionary.com/autocomplete/'
    _SEARCH_VALIDATE_SCHEMA = {'type': 'array', 'items': {'type': 'string'}}
    _DICT_WORD_URL = 'https://www.collinsdictionary.com/dictionary/english/'

    def __init__(self):
        self._session = rq.Session()
        self._session.headers.update({
            'user-agent': USER_AGENT,
        })

    def get_word(self, word: str):
        if ' ' in word:
            word = word.replace(' ', '-')
        url = yarl.URL(self._DICT_WORD_URL) / word
        r = self._session.get(str(url))
        r.raise_for_status()
        parsed_page: etree._Element = html.fromstring(r.text)
        if parsed_page.xpath('//p[@class="suggest_new_word"]'):
            suggestions = []
            if parsed_page.xpath('//div[@class="suggested_words"]/ul/li/a'):
                raw_suggestions = parsed_page.xpath('//div[@class="suggested_words"]/ul/li/a')
                suggestions = [tag.text for tag in raw_suggestions]
            raise NotFound(word, suggestions)
        dictionary = (
                parsed_page.xpath(f'.//div[contains(@class, "dictionaries")]/div[contains(@class,"dictionary")]')
                or parsed_page.xpath(f'.//div[contains(@class, "dictionaries")]')
        )[0]
        words = dictionary.xpath('./div[contains(@class,"dictlink")]')
        out = []
        for w in words:
            out.append(self._parse_word(w.find('./div')))
        return out

    def _parse_word(self, word: etree._Element) -> Word:
        frequency = word.find('.//span[@class="word-frequency-img"]')
        if frequency is not None:
            frequency = int(frequency.get('data-band'))
        pronounce = word.find(
            './/span[@class="pron type-"]//a[@class="hwd_sound sound audio_play_button icon-volume-up ptr"]')
        if pronounce is not None:
            pronounce = pronounce.get('data-src-mp3')
        word_text = word.find('.//h2[@class="h2_entry"]/span[@class="orth"]').text
        definitions = word.xpath('./div[contains(@class,"content definitions")]')[0]
        parsed_definitions = []
        for definition in definitions.xpath('.//div[contains(@class,"hom")]'):
            definition: etree._Element
            if (x := definition.find('./span[@class="gramGrp pos"]')) is not None:
                part_of_speech = x.text
            elif (x := definition.find('./span[@class="gramGrp"]/span[@class="pos"]')) is not None:
                part_of_speech = x.text
            elif (x := definition.find('./div[@class="def"]')) is not None:
                def_text = ''.join(x.itertext()).replace('\n', '')
                return Word(word_text, frequency, pronounce, [WordDefinition([Sense(def_text)])])
            else:
                continue
            senses = []
            for sense in definition.xpath('./div[@class="sense"]'):
                def_text = ''.join(sense.find('./div[@class="def"]').itertext()).replace('\n', '')
                examples = []
                for example in (sense.xpath('./div[@class="cit type-example"]/span[@class="quote"]') +
                                sense.xpath('./div[@class="cit type-example quote"]')
                ):
                    # text = example.find('./span[@class="quote"]').text.replace('\n', ' ')
                    text = example.text.replace('\n', ' ')
                    audio_url = None
                    audio = example.find('..//span[@class="ptr exa_sound type-exa_sound"]/a')
                    if audio is not None:
                        audio_url = audio.get('data-src-mp3')
                    examples.append(WordUsageExample(text, audio_url))
                senses.append(Sense(def_text, examples))
            parsed_definitions.append(WordDefinition(senses, part_of_speech))
        return Word(word_text, frequency, pronounce, parsed_definitions)

    def _validate_response(self,
                           r: rq.Response,
                           validate_schema: dict,
                           allow_error_codes: bool = True
                           ):
        if not allow_error_codes:
            r.raise_for_status()
        try:
            json_resp = r.json()
        except ValueError:
            raise WrongResponse
        jsonschema.validate(instance=json_resp, schema=validate_schema)

    @tnc.retry(stop=tnc.stop_after_attempt(3))
    def search(self, word: str):
        params = {
            'dictCode': 'english',
            'q': word,
        }
        response = self._session.get(self._SEARCH_HINTS_URL, params=params)
        self._validate_response(response, self._SEARCH_VALIDATE_SCHEMA, allow_error_codes=False)
        return response.json()
