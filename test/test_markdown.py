import markdown
from pelican_katex.markdown import KatexExtension

from html_template import HTMLTemplate


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
    input = "I have 10$ and 20$."
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate("<p>I have 10$ and 20$.</p>")
    assert template == output


def test_ignores_dollar_followed_by_alnum_character():
    input = "A coin is $1 and stored in $A register."
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate("<p>A coin is $1 and stored in $A register.</p>")
    assert template == output


def test_double_dollar_renders_display_math():
    input = "$$x^2$$"
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate('<p><span class="katex-display">...</span></p>')
    assert template == output


def test_preamble_block_does_not_show_up():
    input = "$$@\\def\\pelican{x^2}$$\nUse it\n$$\\pelican = 1$$"
    output = markdown.markdown(input, extensions=[KatexExtension()])

    template = HTMLTemplate('<p>\nUse it\n<span class="katex-display">...</span></p>')
    assert template == output


def test_backslash_escapes_dollar_delimiter():
    input = r"My bank account has \$1 and my wallet \$0."
    output = markdown.markdown(input, extensions=[KatexExtension()])

    target = input.replace("\\", "")
    template = HTMLTemplate(f"<p>{target}</p>")
    assert template == output


def test_backslash_escapes_double_dollar_delimiter():
    input = r"A is \$$1 and B is \$$10."
    output = markdown.markdown(input, extensions=[KatexExtension()])

    target = input.replace("\\", "")
    template = HTMLTemplate(f"<p>{target}</p>")
    assert template == output
