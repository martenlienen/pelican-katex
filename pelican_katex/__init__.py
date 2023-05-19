"""LaTeX pre-rendering for pelican with katex.js"""

__version__ = "1.6.1"

# Expose the register hook for pelican
from .plugin import register
