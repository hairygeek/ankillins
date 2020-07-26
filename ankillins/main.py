import time
from os import path
import csv
import typing as ty

from jinja2 import Environment, PackageLoader, select_autoescape
import requests as rq
from colorama import Fore, Style

from .constants import ANKI_MEDIA_DIR, USER_AGENT
from ankillins.client import Word, Collins

env = Environment(
    loader=PackageLoader('ankillins', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def generate_page_card(word: Word):
    card_template = env.get_template('back.html')
    _download_audio_files_to_anki_dir_and_update_word(word)
    back = card_template.render(word=word)
    return back


def process_words(words: ty.Sequence[str], file_path: str):
    client = Collins()
    with open(file_path, 'w', newline='') as fp:
        writer = csv.writer(fp, delimiter='~', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for word_str in words:
            words = client.get_word(word_str)
            for word in words:
                writer.writerow((generate_page_card(word),))
            print(f'Word "{word_str}" processed {Fore.GREEN + "successfully" + Style.RESET_ALL}')


def _download_file_by_url(url: str, path: str):
    headers = {
        'user-agent': USER_AGENT
    }
    r = rq.get(url, headers=headers)
    r.raise_for_status()
    open(path, 'wb').write(r.content)


def _download_audio_files_to_anki_dir_and_update_word(word: Word):
    timestamp = int(time.time())
    if word.pronounce_url:
        file_name = '%s_%s.mp3' % (_text_to_filename(word.word), timestamp)
        file_path = path.join(ANKI_MEDIA_DIR, file_name)
        _download_file_by_url(word.pronounce_url, file_path)
        word.pronounce_filename = file_name
    for d in word.definitions:
        for s in d.senses:
            for ex in s.examples:
                if not ...:
                    # temporary lock the feature
                    file_name = '%s_%s.mp3' % (_text_to_filename(ex.text), timestamp)
                    file_path = path.join(ANKI_MEDIA_DIR, file_name)
                    _download_file_by_url(ex.pronounce_url, file_path)
                    ex.pronounce_path = file_name


def _text_to_filename(string: str):
    return ''.join(s for s in string.replace(' ', '_') if s.isalpha() or s.isnumeric() or s == '_')
