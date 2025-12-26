import sys, os

# General

project = u'NestedText'
copyright = u'2020-2025, Ken and Kale Kundert'
release = '3.8'
version = '.'.join(release.split('.'))

master_doc = 'index'
source_suffix = '.rst'
templates_path = ['.templates']
exclude_patterns = ['.build']

# Extensions

extensions = '''\
    sphinx.ext.autodoc
    sphinx.ext.autosummary
    sphinx.ext.coverage
    sphinx.ext.doctest
    sphinx.ext.napoleon
    sphinx.ext.viewcode
    sphinx_rtd_theme
    sphinx_toolbox.collapse
'''.split()

autosummary_generate = True
html_theme = 'sphinx_rtd_theme'
pygments_style = 'sphinx'
html_static_path = ['.static']

def setup(app):
    import os
    if os.path.exists('.static/css/custom.css'):
        app.add_css_file('css/custom.css')

# The following are needed by the ReadTheDocs website.  KSK 240726

# Define the canonical URL if you are using a custom domain on Read the Docs
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")

# Tell Jinja2 templates the build is running on Read the Docs
if os.environ.get("READTHEDOCS", "") == "True":
    if "html_context" not in globals():
        html_context = {}
    html_context["READTHEDOCS"] = True
