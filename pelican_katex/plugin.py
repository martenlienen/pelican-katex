from docutils.parsers.rst import Directive, directives, roles
from pelican import signals

import pelican_katex.rendering as rendering

from .restructuredtext import KatexBlock, katex_role

try:
    from .markdown import KatexExtension

    markdown_available = True
except ImportError as e:
    markdown_available = False


def configure_pelican(plc):
    if "KATEX" in plc.settings and isinstance(plc.settings["KATEX"], dict):
        rendering.KATEX_DEFAULT_OPTIONS.update(plc.settings["KATEX"])

    if "KATEX_PATH" in plc.settings:
        rendering.KATEX_PATH = plc.settings["KATEX_PATH"]

    if "KATEX_DIRECTIVE" in plc.settings:
        rst_name = str(plc.settings["KATEX_DIRECTIVE"])
    else:
        rst_name = "math"

    if "KATEX_RENDER_TIMEOUT" in plc.settings:
        rendering.KATEX_RENDER_TIMEOUT = float(plc.settings["KATEX_RENDER_TIMEOUT"])

    if "KATEX_STARTUP_TIMEOUT" in plc.settings:
        rendering.KATEX_STARTUP_TIMEOUT = float(plc.settings["KATEX_STARTUP_TIMEOUT"])

    if "KATEX_NODEJS_BINARY" in plc.settings:
        rendering.KATEX_NODEJS_BINARY = plc.settings["KATEX_NODEJS_BINARY"]

    if "KATEX_PREAMBLE" in plc.settings:
        rendering.KATEX_PREAMBLE = plc.settings["KATEX_PREAMBLE"]

    # Integrate into reStructuredText
    directives.register_directive(rst_name, KatexBlock)
    roles.register_canonical_role(rst_name, katex_role)

    # Integrate into markdown
    if markdown_available:
        plc.settings["MARKDOWN"].setdefault("extensions", []).append(KatexExtension())


def reset_preamble(*args, **kwargs):
    """Reset the file-local preamble after every file"""
    rendering.reset_preamble()


def register():
    signals.initialized.connect(configure_pelican)
    signals.article_writer_finalized.connect(reset_preamble)
    signals.page_writer_finalized.connect(reset_preamble)
    signals.static_generator_finalized.connect(reset_preamble)
