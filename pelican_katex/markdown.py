from xml.etree import ElementTree

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import AtomicString

from .rendering import push_preamble, render_latex


def revert_xmlns_resolution(root):
    """Revert the xmlns resolution that ElementTree performs upon parsing

    ElementTree resolves each tag into its universal name during parsing, see
    [1]. The nice solution would be to wrap each such element tag and attribute
    name into a ElementTree.QName which the Markdown package supports properly
    in its serialization. However, at other points the Markdown package makes
    use of the contract of ElementTree.Element that says that its tag and
    attribute names are always either strings or bytes and calls for example
    .lower() on it. Therefore, we revert this "universalization" manually.

    [1] http://effbot.org/zone/element-namespaces.htm
    """

    candidates = [(root, None)]
    while len(candidates) > 0:
        node, namespace = candidates.pop()

        if node.tag.startswith("{") and "}" in node.tag:
            this_namespace, node.tag = node.tag[1:].split("}", maxsplit=1)

            # The xmlns is inherited so only set it when the namespace changes
            if this_namespace != namespace:
                node.attrib["xmlns"] = this_namespace
                namespace = this_namespace

        candidates.extend((child, namespace) for child in node)


PATTERN = (
    r"(?P<preceding>\s?)"
    r"(?P<delimiter>\$\$?)"
    r"(?P<latex>[\S\n].*?)"
    # Only accept closing delimiters that are not followed by word characters
    # (alpha-numeric or underscore) or at the end of the string.
    r"(?P=delimiter)(?=\W|\Z)"
)


class KatexPattern(InlineProcessor):
    def __init__(self, md=None):
        super().__init__(pattern=PATTERN, md=md)

    def handleMatch(self, m, data):
        preceding = m.group("preceding")
        delimiter = m.group("delimiter")
        latex = m.group("latex")

        # If we matched a $ that was not preceded by whitespace or at the
        # beginning of a block, continue but consume exactly one character. If
        # we consume no characters, the parser goes into an infinite loop and if
        # we return None, None, None, the parser consumes the whole pattern
        # match including the matched "closing" delimiter which could actually
        # be the start of a true match.
        if len(preceding) == 0 and m.start() > 0:
            return None, m.start() + 1, m.start() + 1

        # Leave any preceding whitespace that we matched on untouched
        match_start = m.start() + len(preceding)
        match_end = m.end()

        # If a math block starts with an @, it is a preamble block and does not
        # produce any output
        if len(delimiter) == 2 and len(latex) > 0 and latex[0] == "@":
            push_preamble(latex[1:])
            return "", match_start, match_end

        display_mode = True if delimiter == "$$" else False
        rendered = render_latex(latex, {"displayMode": display_mode})
        node = ElementTree.fromstring(rendered)

        # Side-step the whole xmlns and QName problem
        revert_xmlns_resolution(node)

        # Mark any text in the rendered output as atomic so that it is not
        # recursively parsed as markdown
        for elem in node.iter():
            if elem.text is not None:
                elem.text = AtomicString(elem.text)

        return node, match_start, match_end


ESCAPE_PATTERN = r"\\(?P<delimiter>\$\$?)"


class DollarEscapePattern(InlineProcessor):
    """Allow escaping dollar delimiters with backslash."""

    def __init__(self, md=None):
        super().__init__(pattern=ESCAPE_PATTERN, md=md)

    def handleMatch(self, m, data):
        delimiter = m.group("delimiter")

        return delimiter, m.start(), m.end()


class KatexExtension(Extension):
    def extendMarkdown(self, md):
        # render_math uses priority 186 as well because apparently it needs to be
        # higher than 180 which some "escape" extension uses.
        md.inlinePatterns.register(KatexPattern(md), "katex", 186)
        md.inlinePatterns.register(DollarEscapePattern(md), "katex-dollar-escape", 185)
