import typing as ty


class WrongResponse(RuntimeError):
    _default_message = 'Server sent wrong response'


class NoResponse(RuntimeError):
    _default_message = 'Server does not respond'


class Forbidden(WrongResponse):
    _default_message = 'Forbidden error. Please check your access token and limits'


class NotFound(RuntimeError):
    def __init__(self, word: str, suggestions: ty.Sequence[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.word = word
        self.suggestions = suggestions

    def __str__(self):
        return f'No rersults. Suggestions: {" ".join(self.suggestions)}'
