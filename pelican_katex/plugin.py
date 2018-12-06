import json
import os
import re
import shlex
from subprocess import Popen, PIPE, TimeoutExpired

import docutils
from docutils.parsers.rst import Directive, directives, roles
from pelican import signals, generators


# Global KaTeX options. Configurable via KATEX in the user conf.
KATEX_OPTIONS = {
    # Prefer KaTeX's debug coloring by default
    "throwOnError": False
}
def get_katex_options():
    return KATEX_OPTIONS.copy()


# Path to the KaTeX program to run
KATEX_PATH = None


class KaTeXError(Exception):
    pass


def render_latex(latex, options=None, timeout=1):
    """Call our KaTeX CLI to compile some LaTeX.

    Parameters
    ----------
    latex : str
        LaTeX to compile
    options : optional dict
        KaTeX options such as displayMode
    timeout : optional int
        Kill the compiler after this many seconds
    """
    global KATEX_PATH

    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compile-katex.js")
    cmd = "node {}".format(script_path)
    if options:
        cmd = "{} --options {}".format(cmd, shlex.quote(json.dumps(options)))

    if KATEX_PATH:
        cmd = "{} --katex {}".format(cmd, KATEX_PATH)

    proc = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE)

    try:
        out, err = proc.communicate(latex.encode("utf-8"), timeout=timeout)
        html = out.decode("utf-8")

        if proc.returncode == 0:
            return html
        else:
            raise KaTeXError(err)
    except TimeoutExpired:
        proc.kill()

        msg = "Compiling took longer than {} seconds".format(timeout)
        raise KaTeXError(msg)


class KatexBlock(Directive):
    """A docutils block that renders its content with KaTeX."""

    has_content = True

    def run(self):
        """Adapted from the original MathBlock directive."""
        self.assert_has_content()

        katex_options = get_katex_options()
        katex_options["displayMode"] = True

        # Join lines, separate blocks
        content = "\n".join(self.content).split("\n\n")

        try:
            nodes = []
            for block in content:
                if not block or len(block) == 0:
                    continue

                html = render_latex(block, katex_options)
                node = docutils.nodes.raw(self.block_text, html, format="html")
                node.line = self.content_offset + 1

                self.add_name(node)
                nodes.append(node)

            return nodes
        except KaTeXError as e:
            raise self.error(str(e))


# To avoid having to escape all backslashes (which you usually have quite a bit
# of in LaTeX), we re-parse the role content from the raw text.
ROLE_TEXT_RE = re.compile(":.+:`(.+)`")

def katex_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    katex_options = get_katex_options()
    katex_options["displayMode"] = False

    match = ROLE_TEXT_RE.match(rawtext)
    if not match:
        return [], ["Could not extract raw text from role"]

    try:
        latex = match.group(1)
        html = render_latex(latex, katex_options)
        node = docutils.nodes.raw(rawtext, html, format="html")

        return [node], []
    except KaTeXError as e:
        return [], [str(e)]


def configure_pelican(plc):
    global KATEX_OPTIONS, KATEX_PATH
    if "KATEX" in plc.settings and isinstance(plc.settings["KATEX"], dict):
        KATEX_OPTIONS.update(plc.settings["KATEX"])

    if "KATEX_PATH" in plc.settings:
        KATEX_PATH = plc.settings["KATEX_PATH"]

    if "KATEX_DIRECTIVE" in plc.settings:
        rst_name = str(plc.settings["KATEX_DIRECTIVE"])
    else:
        rst_name = "math"

    directives.register_directive(rst_name, KatexBlock)
    roles.register_canonical_role(rst_name, katex_role)


def register():
    signals.initialized.connect(configure_pelican)
