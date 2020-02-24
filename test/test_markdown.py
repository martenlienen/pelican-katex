import markdown

from html_template import HTMLTemplate
from pelican_katex.markdown import KatexExtension


def test_renders_standalone_inline_math():
    input = "Hello $x^2$ world!"
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate('<p>Hello <span class="katex">...</span> world!</p>')
    assert template == output


def test_renders_inline_math_at_beginning():
    input = "$x^2$ world!"
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate('<p><span class="katex">...</span> world!</p>')
    assert template == output


def test_renders_inline_math_in_front_of_punctuation():
    input = "Hello $x^2$!"
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate('<p>Hello <span class="katex">...</span>!</p>')
    assert template == output


def test_leaves_currencies_alone():
    input = "I have 10$."
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate("<p>I have 10$.</p>")
    assert template == output


def test_double_dollar_renders_inline_math():
    input = "$$x^2$$"
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate('<p><span class="katex-display">...</span></p>')
    assert template == output


def test_preamble_block_does_not_show_up():
    input = "$$@\def\pelican{x^2}$$\nUse it\n$$\pelican = 1$$"
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate('<p>\nUse it\n<span class="katex-display">...</span></p>')
    assert template == output
