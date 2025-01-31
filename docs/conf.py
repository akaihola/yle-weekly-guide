# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'YLE Weekly Guide'
copyright = '2024, Antti Kaihola'
author = 'Antti Kaihola'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

# Furo theme options
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2e7d32",  # Match the green color from the app
        "color-brand-content": "#4caf50",
        "color-background-secondary": "#f8f8f8",  # Match the marked program background
        "color-foreground-primary": "#000000",  # Black text like in the app
        "font-stack": "Arial, sans-serif",  # Match the app's font
    }
}
