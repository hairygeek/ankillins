import typing as ty


class WrongResponse(RuntimeError):
    def __str__(self):
        return 'Server sent wrong response.'


class NotFound(RuntimeError):
    def __init__(self, word: str, suggestions: ty.Sequence[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.word = word
        self.suggestions = suggestions

    def __str__(self):
        return f"Word {self.word} not found"
