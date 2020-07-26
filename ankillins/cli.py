import typing as ty
import sys
import csv

import click
import colorama
from colorama import Fore, Style
import requests.exceptions

from .client import Collins
from .constants import CANNOT_CONNECT_TEXT, CANNOT_GENERATE_CARD
from .main import generate_page_card
from .errors import WrongResponse, NotFound


def _generate_error_message(error_text: str) -> str:
    return f'[{Fore.RED + "Error" + Style.RESET_ALL}] {error_text}'


def exit_with_error(error_text: str):
    print(_generate_error_message(error_text))
    sys.exit(1)


class ErrorHandlingGroup(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except NotFound as e:
            exit_with_error(str(e) + f'Similar words: {", ".join(e.suggestions)}')
        except WrongResponse as e:
            exit_with_error(str(e) + ' Try again later.')
        except requests.exceptions.ConnectionError:
            exit_with_error(CANNOT_CONNECT_TEXT)


@click.group(cls=ErrorHandlingGroup)
@click.pass_context
def ankillins(ctx: click.Context):
    colorama.init()
    ctx.obj['client'] = Collins()


@ankillins.command()
@click.argument('word')
@click.pass_context
def search(ctx: click.Context, word: str):
    client: Collins = ctx.obj['client']
    search_hints = client.search(word)
    click.echo(', '.join(search_hints))


@ankillins.command('gen-cards')
@click.argument('words', nargs=-1)
@click.option('--result_path', '-r', type=click.Path(writable=True))
@click.pass_context
def gen_cards(ctx: click.Context, words: ty.Sequence[str], result_path: str = None):
    client: Collins = ctx.obj['client']
    with open(result_path or './ankillins-result.csv', 'w', newline='') as fp:
        writer = csv.writer(fp, delimiter='~', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for word_str in words:
            try:
                parsed = client.get_word(word_str)
            except NotFound as e:
                print(_generate_error_message(str(e) + f'\nSimilar words: {", ".join(e.suggestions)}'))
                continue
            except requests.exceptions.ConnectionError:
                print(_generate_error_message(CANNOT_GENERATE_CARD.format(word_str, CANNOT_CONNECT_TEXT)))
                continue
            except Exception:
                print(_generate_error_message(CANNOT_GENERATE_CARD.format(word_str, 'Unknown error')))
                continue
            for word in parsed:
                writer.writerow((generate_page_card(word),))
            print(f'Word "{word_str}" processed {Fore.GREEN + "successfully" + Style.RESET_ALL}')


def main():
    ankillins(obj={})


if __name__ == '__main__':
    main()
