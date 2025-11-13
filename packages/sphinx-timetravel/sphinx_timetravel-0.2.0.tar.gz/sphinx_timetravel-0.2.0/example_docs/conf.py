"""
Sphinx configuration for TimeTravel plugin examples
"""

import os
import sys

# Add parent directory to path to import the plugin
sys.path.insert(0, os.path.abspath('..'))

project = 'Sphinx TimeTravel Examples'
copyright = '2024'
author = 'Your Name'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_timetravel',
]

templates_path = ['_templates']
exclude_patterns = ['_build']

html_theme = 'alabaster'
html_static_path = ['_static']

# Copy CSS from plugin to static directory
def copy_css_files(app, exception):
    """Copy CSS files from plugin to build output."""
    import shutil
    src = os.path.join(os.path.dirname(__file__), '..', 'sphinx_timetravel', '_static', 'timeline.css')
    dst = os.path.join(app.outdir, '_static', 'timeline.css')
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

def setup(app):
    app.connect('build-finished', copy_css_files)
