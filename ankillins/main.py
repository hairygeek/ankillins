from ankillins.client import Word
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('ankillins', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def generate_page(word: Word):
    template = env.get_template('index.html')
    t = template.render(word=word)
    with open('/home/hairygeek/PycharmProjects/ankillins/ankillins/templates/res.html', 'w') as fp:
        fp.write(t)
    return t
