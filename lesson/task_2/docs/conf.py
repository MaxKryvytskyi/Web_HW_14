import sys
import os

sys.path.append(os.path.abspath('..'))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'task_2' # Rest API
copyright = '2024, max' 
author = 'max'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'UA'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme ='nature'# 'readthedocs' mkdocs? alabaster classic sphinxdoc scrolls agogo traditional haiku pyramid bizstyle
# https://www.sphinx-doc.org/en/master/usage/theming.html 
html_static_path = ['_static']
