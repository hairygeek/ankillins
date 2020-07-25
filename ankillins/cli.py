import typing as ty
import sys

import click
import colorama
from colorama import Fore, Style
import requests.exceptions

from .client import Collins
from .main import process_words
from .errors import WrongResponse, NotFound


def exit_with_error(error_text: str):
    print(f'[{Fore.RED + "Error" + Style.RESET_ALL}] {error_text}')
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
            exit_with_error('Cannot connect to Collins. Check your Ethernet connection and try again.')


@click.group()
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
    parsed = []
    for w in words:
        parsed.append(client.get_word(w))
    process_words(words, result_path or './result.csv')


def main():
    ankillins(obj={})


if __name__ == '__main__':
    main()
