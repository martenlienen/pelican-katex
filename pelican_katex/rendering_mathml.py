#from .rendering import KaTeXError
import pelican_katex.rendering as rendering
try:
    import latex2mathml.converter
    has_mathml = True
except ImportError:
    has_mathml = False

def render_latex_mathml(latex, options=None):
    """Render some LaTeX to MathML

    Parameters
    ----------
    latex : str
        LaTeX-Math string to render
    options : optional dict
        KaTeX-style options such as displayMode
        Only options.displayMode is currently being used
    """

    if not has_mathml:
        raise rendering.KaTeXError("latex2mathml could not be imported!")

    if options is None:
        display = "inline"
    else:
        display= "block" if options["displayMode"] else "inline"

    return latex2mathml.converter.convert(latex, display=display)
