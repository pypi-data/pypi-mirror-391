import re
from pylint.lint import PyLinter
from .docstring_checker_base import DocstringCheckerBase


class FunctionDocstringChecker(DocstringCheckerBase):
    """
    Checker for verifying function-level docstrings follow Google Python Style Guide.
    """

    name = "function-docstring-checker"
    priority = -1

    msgs = {
        "E9001": (
            "Function '%s' has more than %d lines and no docstring",
            "missing-docstring-for-long-function",
            "Used when a long function has more than N lines but no docstring.",
        ),
        "E9002": (
            "Function '%s' has a docstring written in Vietnamese",
            "vietnamese-docstring-detected",
            "Used when a docstring contains Vietnamese characters.",
        ),
        "E9003": (
            "Function '%s' docstring missing Args section (Google Style)",
            "missing-args-section",
            "Used when a function with parameters is missing an Args section.",
        ),
        "E9004": (
            "Function '%s' docstring missing Returns section (Google Style)",
            "missing-returns-section",
            "Used when a function that returns a value is missing a Returns section.",
        ),
        "E9005": (
            "Function '%s' docstring missing Raises section (Google Style)",
            "missing-raises-section",
            "Used when a function that raises exceptions is missing a Raises section.",
        ),
        "E9006": (
            "Function '%s' docstring missing summary line (Google Style)",
            "missing-summary-line",
            "Google Style: missing short description at the start of docstring.",
        ),
    }

    options = (
        (
            "function-min-lines",
            {
                "default": 0,
                "type": "int",
                "help": "Minimum number of lines in a function to require a docstring",
            },
        ),
    )

    ARGS_SECTION = re.compile(
        r"Args:\n(?:\s{2,}\w+(?: *\([^)]*\))?: .+(?:\n|$))+",
        re.MULTILINE,
    )

    RETURNS_SECTION = re.compile(
        r"Returns:\s*\n\s{2,}.+",
        re.MULTILINE,
    )

    RAISES_SECTION = re.compile(
        r"Raises:\n(?:\s{2,}[\w.]+: .+(?:\n|$))+",
        re.MULTILINE,
    )

    def __init__(self, linter: PyLinter):
        super().__init__(linter, "Function Docstring Summary Report", "functions")

    def visit_functiondef(self, node):
        """Visit each function definition."""
        self.total_items += 1
        docstring = node.doc_node.value if node.doc_node else None
        num_lines = node.tolineno - node.fromlineno
        if num_lines < self.linter.config.function_min_lines:
            self.skipped_items += 1
            return

        if not docstring:
            self.without_docstring += 1
            self.add_message(
                "missing-docstring-for-long-function",
                node=node,
                args=(node.name, self.linter.config.function_min_lines),
            )
        else:
            self.with_docstring += 1
            # Check Vietnamese docstring
            if self.detect_vietnamese_docstring(node, docstring, "vietnamese-docstring-detected"):
                return

            # Check Google Style
            if self._check_google_style(node, docstring):
                self.google_style_compliant += 1
            

    def _check_google_style(self, node, docstring: str) -> bool:
        """Check compliance with Google Python Style Guide."""
        compliant = True

        # Summary line
        lines = [l.strip() for l in docstring.strip().splitlines() if l.strip()]
        if not lines or not re.match(r"^[A-Z].*\.$", lines[0]):
            self.add_message("missing-summary-line", node=node, args=(node.name,))
            compliant = False

        # Args section
        # For methods, exclude 'self' parameter
        args = node.args.args
        if args and args[0].name == "self":
            args = args[1:]
        
        has_params = bool(args)
        if has_params and not self.ARGS_SECTION.search(docstring):
            self.add_message("missing-args-section", node=node, args=(node.name,))
            compliant = False

        # Returns section
        has_return = any(
            getattr(stmt, "value", None) is not None
            and stmt.__class__.__name__ == "Return"
            for stmt in node.body
        )
        if has_return and not self.RETURNS_SECTION.search(docstring):
            self.add_message("missing-returns-section", node=node, args=(node.name,))
            compliant = False

        # Raises section
        has_raise = any(stmt.__class__.__name__ == "Raise" for stmt in node.body)
        if has_raise and not self.RAISES_SECTION.search(docstring):
            self.add_message("missing-raises-section", node=node, args=(node.name,))
            compliant = False

        return compliant


def register(linter: PyLinter):
    linter.register_checker(FunctionDocstringChecker(linter))
