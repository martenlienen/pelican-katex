from .rendering_katex  import render_latex_katex


# Default KaTeX options.
KATEX_DEFAULT_OPTIONS = {
    # Prefer KaTeX's debug coloring by default
    "throwOnError": False
}

# Path to the KaTeX program to run
KATEX_PATH = None

# How long to wait for the render server to start in seconds
KATEX_STARTUP_TIMEOUT = 1.0

# Timeout per rendering request in seconds
KATEX_RENDER_TIMEOUT = 1.0

# nodejs binary to run javascript
KATEX_NODEJS_BINARY = "node"

# Preamble to prepend to any rendered LaTeX
KATEX_PREAMBLE = None

# If latex2mathml should be used instead of Katex
KATEX_MATHML = False

# A list of file-local additions to the preamble
LOCAL_PREAMBLES = []


def push_preamble(preamble):
    LOCAL_PREAMBLES.append(preamble)


def reset_preamble():
    LOCAL_PREAMBLES.clear()


def get_preamble():
    preamble = KATEX_PREAMBLE

    if len(LOCAL_PREAMBLES) > 0:
        local_preamble = "\n".join(LOCAL_PREAMBLES)
        if preamble is None:
            preamble = local_preamble
        else:
            preamble += "\n" + local_preamble

    return preamble


class KaTeXError(Exception):
    pass


def render_latex(latex, options=None):
    """Render some LaTeX to an HTML suitable format.

    Parameters
    ----------
    latex : str
        LaTeX to render
    options : optional dict
        KaTeX-style options such as displayMode
    """

    return render_latex_katex(latex, options)
