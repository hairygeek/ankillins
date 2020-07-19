import typing as ty
import io
import dataclasses

import requests as rq
import jsonschema
import yarl
from lxml import etree, html

from .errors import WrongResponse, NotFound


@dataclasses.dataclass()
class WordUsageExample:
    text: str
    pronounce: str = None


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
    pronounce: str
    definitions: ty.Sequence[WordDefinition]


# Collins Dictionary hasn't respond to my request for API access, so I have to scrape it :(

class Collins:
    _SEARCH_API_URL = 'https://www.collinsdictionary.com/autocomplete/'
    _SEARCH_VALIDATE_SCHEMA = {'type': 'array', 'items': {'type': 'string'}}
    _DICT_WORD_URL = 'https://www.collinsdictionary.com/dictionary/english/'
    _DICT_CLASSES = ['dictionary Cob_Adv_Brit dictentry',
                     'dictionary Cob_Adv_Brit',
                     'dictionaries dictionary dictionary Collins_Eng_Dict',
                     'dictionaries dictionary dictionary Cob_Adv_Brit',
                     'dictionary Collins_Eng_Dict dictentry',
                     ]

    def __init__(self):
        self._session = rq.Session()
        self._session.headers.update({
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        })

    def _get_word(self, word: str):
        if ' ' in word:
            word = word.replace(' ', '-')
        url = yarl.URL(self._DICT_WORD_URL) / word
        r = self._session.get(str(url))
        r.raise_for_status()
        parsed_page: etree._Element = etree.parse(io.StringIO(r.text), parser=etree.HTMLParser())
        if parsed_page.xpath('//div[@class="suggested_words"]/ul/li/a'):
            raw_suggestions = parsed_page.xpath('//div[@class="suggested_words"]/ul/li/a')
            suggestions = [tag.text for tag in raw_suggestions]
            raise NotFound(word, suggestions)
        return self._parse_word(r.text)

    def _parse_word(self, word_page: str):
        # todo: scrape other dictionaries
        parsed_page: etree._Element = html.fromstring(word_page)
        word: etree._Element = parsed_page.xpath(
            f'.//div[contains(@class,"dictionary")]/div[contains(@class,"dictlink")]/div'
        )[0]
        frequency = word.find('.//span[@class="word-frequency-img"]')
        if frequency is not None:
            frequency = frequency.get('data-band')
        pronounce = word.find('.//a[@class="hwd_sound sound audio_play_button icon-volume-up ptr"]')
        if pronounce is not None:
            pronounce = pronounce.get('data-src-mp3')
        word_text = word.find('.//h2[@class="h2_entry"]/span[@class="orth"]').text
        # definitions = word.find('./div[@class="content definitions cobuild br "]') or word.find(
        #     './div[@class="content definitions ced"]')
        definitions = word.xpath('./div[contains(@class,"content definitions")]')[0]
        if not definitions:
            # todo: scrape peace of speech
            word_def = word.find('.//div[@class="hom sense"]/div[@class="def"]').text
            print(word_def)
            sense = Sense(word_def)
            word_definition = WordDefinition([sense])
            return Word(word_text, frequency, [word_definition])

        parsed_definitions = []
        for definition in definitions.xpath('.//div[@class="hom"]'):
            definition: etree._Element
            part_of_speech = definition.find('./span[@class="gramGrp pos"]')
            if part_of_speech is None:
                part_of_speech = definition.find('./span[@class="gramGrp"]/span[@class="pos"]')
                if part_of_speech is not None:
                    part_of_speech = part_of_speech.text
            else:
                part_of_speech = part_of_speech.text
            senses = []
            for sense in definition.xpath('./div[@class="sense"]'):
                def_text = ''.join(sense.find('./div[@class="def"]').itertext()).replace('\n', '')
                examples = []
                for example in sense.xpath('./div[@class="cit type-example"]'):
                    text = example.find('./span[@class="quote"]').text.replace('\n', ' ')
                    audio_url = None
                    audio = example.find('./span[@class="ptr exa_sound type-exa_sound"]/a')
                    if audio is not None:
                        audio_url = audio.get('data-src-mp3')
                    examples.append(WordUsageExample(text, audio_url))
                senses.append(Sense(def_text, examples))
            parsed_definitions.append(WordDefinition(senses, part_of_speech))
        return Word(word_text, frequency, pronounce, parsed_definitions)

    def get_words(self, words: ty.Sequence[str]):
        ...

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

    def search(self, word: str, attempts: int = 3):
        params = {
            'dictCode': 'english',
            'q': word,
        }
        response = self._session.get('https://www.collinsdictionary.com/autocomplete/', params=params)
        try:
            self._validate_response(response, self._SEARCH_VALIDATE_SCHEMA, allow_error_codes=False)
        except jsonschema.ValidationError:
            if attempts:
                return self.search(word, attempts - 1)
            else:
                raise WrongResponse
        return response.json()
