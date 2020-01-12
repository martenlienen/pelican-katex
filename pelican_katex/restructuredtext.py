import re

import docutils
from docutils.parsers.rst import Directive, directives, roles

from .rendering import KaTeXError, render_latex


class KatexBlock(Directive):
    """A docutils block that renders its content with KaTeX."""

    has_content = True

    def run(self):
        """Adapted from the original MathBlock directive."""
        self.assert_has_content()

        # Join lines, separate blocks
        content = "\n".join(self.content).split("\n\n")

        try:
            nodes = []
            for block in content:
                if not block or len(block) == 0:
                    continue

                html = render_latex(block, {"displayMode": True})
                node = docutils.nodes.raw(self.block_text, html, format="html")
                node.line = self.content_offset + 1

                self.add_name(node)
                nodes.append(node)

            return nodes
        except KaTeXError as e:
            raise self.error(str(e))


# To avoid having to escape all backslashes (which you usually have quite a bit
# of in LaTeX), we re-parse the role content from the raw text.
ROLE_TEXT_RE = re.compile("\A:.+:`((?s:.)+)`\Z")


def katex_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    match = ROLE_TEXT_RE.match(rawtext)
    if not match:
        return [], ["Could not extract raw text from role"]

    latex = match.group(1)
    html = render_latex(latex, {"displayMode": False})
    node = docutils.nodes.raw(rawtext, html, format="html")

    return [node], []
