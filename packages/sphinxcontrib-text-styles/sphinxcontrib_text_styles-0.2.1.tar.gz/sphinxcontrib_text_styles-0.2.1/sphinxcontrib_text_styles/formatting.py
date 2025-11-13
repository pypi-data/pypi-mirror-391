import sphinx
import os
from docutils import nodes
from sphinx.util.docutils import SphinxRole
from sphinx.writers.latex import LaTeXTranslator
from typing import Dict, Any, List

class FormattingRole(SphinxRole):
    """
    Customizable text formatting role with support for aliases
    """
    def __init__(self, style_classes: List[str]):
        super().__init__()
        self.style_classes = style_classes

    def __call__(self, name: str, rawtext: str, text: str, lineno: int, 
                 inliner, options: Dict[str, Any] = None, content: List[str] = None):
        options = options or {}
        node = nodes.inline(rawtext, text, classes=self.style_classes)
        return [node], []

def create_role_mapping(app, config):
    """
    Create role mappings based on configuration
    """

    # These are colours with names understood by both CSS and Latex. They may
    # not render exactly the same in both.
    colours = [
        'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'black', 'gray',
        'white', 'darkgray', 'lightgray', 'brown', 'lime', 'olive', 'orange',
        'pink', 'purple', 'teal', 'violet' ]

    # Roles
    role_mapping = {
        'text-strike'    : ['text-strike'],
        'text-mono'      : ['text-mono'],
        'text-underline' : ['text-underline'],
        'text-bold'      : ['text-bold'],
        'text-italic'    : ['text-italic'],
    }

    # Implementation of styles in CSS
    css_styles = {
        'text-strike'    : f"text-decoration: line-through;",
        'text-mono'      : f"font-family: monospace;",
        'text-underline' : f"text-decoration: underline;",
        'text-bold'      : f"font-weight: bold;",
        'text-italic'    : f"font-style: italic;",
    }

    # Implementation of styles in Latex markup
    latex_styles = {
        'text-strike'    : r'\sout{',
        'text-mono'      : r'\texttt{',
        'text-underline' : r'\underline{',
        'text-bold'      : r'\textbf{',
        'text-italic'    : r'\textit{',
    }

    # Add colours
    for c in colours:
        role_mapping[f"text-{c}"] = [f"text-{c}"]
        role_mapping[f"bg-{c}"]   = [f"bg-{c}"]
        latex_styles[f"text-{c}"] = f"\\textcolor{{{c}}}{{"
        latex_styles[f"bg-{c}"]   = f"\\colorbox{{{c}!20}}{{"
        css_styles  [f"text-{c}"] = f"color: {c};"
        css_styles  [f"bg-{c}"]   = f"background-color: {c}; opacity: 0.5;"

    # Some colours look poor when faded
    latex_styles["bg-black"] = r'\colorbox{black}{'
    css_styles["bg-black"]   = "background-color: black;"

    # Allow users to override or add new styles
    user_styles = config.text_styles_styles or {}
    for style,(css,latex) in user_styles.items():
        role_mapping[style] = [style]
        css_styles[style] = css
        latex_styles[style] = latex

    # Allow users to override or add new roles
    user_roles = config.text_styles_roles or {}
    for role,styles in user_roles.items():
        for s in styles:
            if s not in css_styles:
                print("Error: custom role {role} references non-existant style {s}")
    role_mapping.update(user_roles)

    # Store the mapping for use in translator
    app.config.text_styles = role_mapping
    app.config.latex_styles = latex_styles
    app.config.css_styles = css_styles

    return role_mapping


def create_css(app, execution):
    if app.builder.name != "html":
        return

    path = os.path.join(app.builder.outdir, '_static', 'text_styles.css')

    with open(path, "w") as fh:
        for style,css in app.config.css_styles.items():
            fh.write(f".{style} {{ {css} }}\n")


# ==============================================================================
# Latex bits
# ==============================================================================

def add_packages(app, filename):
    """
    Add LaTeX packages to support inline formatting
    """
    packages = [
        'color',
        'soul',         # for background colours
        'ulem',         # for strikethrough
        'listings',     # for monospace
    ]
    for package in packages:
        # If the package is already added and we add it again, Sphinx will warn.
        if not app.registry.has_latex_package(package):
            app.add_latex_package(package)

class CustomLaTeXTranslator(LaTeXTranslator):

    def visit_inline(self, node):
        # Retrieve the latex style mapping
        text_styles = self.builder.config.text_styles
        latex_styles = self.builder.config.latex_styles

        # Get classes and find matching LaTeX commands
        classes = node.get('classes', [])

        # Track opened environments to ensure proper closing
        self._opened_environments = []

        for cls in classes:
            if cls in latex_styles:
                latex_style = latex_styles[cls]
                print(f"{cls} -> {latex_style}")
                self.body.append(latex_style)
                self._opened_environments.append(cls)

        super().visit_inline(node)

    def depart_inline(self, node):
        super().depart_inline(node)

        # Close any opened environments in reverse order
        while self._opened_environments:
            self.body.append('}')
            self._opened_environments.pop()

# ==============================================================================
# Setup and role registration
# ==============================================================================

def process_formatting_roles(app, config):
    """
    Process and register formatting roles dynamically
    """
    # Create role mapping
    role_mapping = create_role_mapping(app, config)

    # Dynamically add roles
    for role_name, style_classes in role_mapping.items():
        app.add_role(role_name, FormattingRole(style_classes))

def setup(app):
    """
    Set up the Sphinx extension with custom roles and configuration
    """
    # Add configuration value for custom roles
    app.add_config_value('text_styles_roles', {}, 'env')
    app.add_config_value('text_styles_styles', {}, 'env')

    # Connect to configuration processing
    app.connect('config-inited', add_packages)
    app.connect('config-inited', process_formatting_roles)

    # Add CSS for HTML output
    app.add_css_file('text_styles.css')
    app.connect('build-finished', create_css)

    # Use custom translator for Latex
    app.set_translator('latex', CustomLaTeXTranslator, override=True)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
