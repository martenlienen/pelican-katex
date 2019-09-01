# LaTeX Pre-rendering for Pelican

This plugin hooks itself directly into docutils' reStructuredText parser to
render math roles and blocks with [KaTeX](https://github.com/KaTeX/KaTeX) while
building your blog. Therefore, you do not need to ship the KaTeX javascript
implementation with your website anymore and improve the accessibility as well
as the load time of your internet presence.

For a demo visit this [blog
post](https://martenlienen.com/sampling-k-partite-graph-edges/). Notice how all
the formulas are just there. There is no loading and the website does not even
serve the javascript part of KaTeX.

## Installation

First of all, you need to install `nodejs` so that `pelican-katex` can run
KaTeX. Then run `pip install pelican-katex` and add `"pelican_katex"` to the
`PlUGINS` setting in your configuration file. Finally, remove the `katex.js`
`<script>` tag from your template and enjoy a lighter website and instant
formulas.

## Configuration

The plugin offers several configuration options that you can set in your
`pelicanconf.py`.

```python
# nodejs binary path or command to run KaTeX with.
# KATEX_NODEJS_BINARY = "node"

# Path to the katex file to use. This project comes with version `0.10` of
# katex but if you want to use a different one you can overwrite the path
# here. To use a katex npm installation, set this to `"katex"`.
# KATEX_PATH = "/path/to/katex.js"

# By default, this plugin will redefine reStructuredText's `math` role and
# directive. However, if you prefer to have leave the docutil's defaults
# alone, you can use this to define a `katex` role for example.
# KATEX_DIRECTIVE = "katex"

# How long to wait for the initial startup of the rendering server. You can
# increasing it but if startup takes longer than one second, something is
# probably seriously broken.
# KATEX_STARTUP_TIMEOUT = 1.0

# Time budget in seconds per call to the rendering engine. 1 second should
# be plenty since most renderings take less than 50ms.
# KATEX_RENDER_TIMEOUT = 1.0

# Here you can pass a dictionary of default options that you want to run
# KaTeX with. All possible options are listed on KaTeX's options page,
# https://katex.org/docs/options.html.
# KATEX = {
#     # Abort the build instead of coloring broken math in red
#     "throwOnError": True
# }
```
