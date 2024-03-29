import sys
import os
import re
import sphinx_rtd_theme

# Add autodoc extension
extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_toolbox.confval',
    'sphinx_copybutton',
]

pygments_style = 'sphinx'
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# Set up paths to include your project's Python modules
sys.path.insert(0, os.path.abspath('../src/'))

# Project information
project = 'DOLOST'
slug = re.sub(r'\W+', '-', project.lower())
version = "1.0"
release = "1.0"
language = 'en'
author = 'BASE4 Security'
copyright = author

# Theme options
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    'logo_only': True,
    'navigation_depth': 3,
    'style_nav_header_background': 'black',
    'display_version': False,
}
html_logo = "images/logo.png"
html_show_sourcelink = True
html_show_copyright = True