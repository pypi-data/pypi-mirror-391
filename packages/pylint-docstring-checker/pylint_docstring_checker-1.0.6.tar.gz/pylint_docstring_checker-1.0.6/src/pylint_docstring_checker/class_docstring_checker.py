import re
from pylint.lint import PyLinter
from .docstring_checker_base import DocstringCheckerBase


class ClassDocstringChecker(DocstringCheckerBase):
    """
    Checker for verifying class-level docstrings follow Google Python Style Guide.
    """

    name = "class-docstring-checker"
    priority = -1
    msgs = {
        "E9101": (
            "Class '%s' is missing a docstring",
            "missing-google-class-docstring",
            "Used when a public class has no docstring.",
        ),
        "E9102": (
            "Class '%s' docstring missing summary line (Google Style)",
            "missing-google-class-summary-line",
            "Google Style: missing short description at the start of class docstring.",
        ),
        "E9103": (
            "Class '%s' docstring missing Attributes section (Google Style)",
            "missing-google-attributes-section",
            "Used when a class defines attributes but lacks an Attributes section in docstring.",
        ),
        "E9104": (
            "Class '%s' has a docstring written in Vietnamese",
            "class-vietnamese-docstring-detected",
            "Used when a class docstring contains Vietnamese characters.",
        ),
    }

    options = (
        (
            "class-min-lines",
            {
                "default": 0,
                "type": "int",
                "help": "Minimum number of lines in a class to require a docstring",
            },
        ),
    )


    ATTRIBUTES_SECTION = re.compile(
        r"Attributes:\n(?:\s{2,}\w+(?: *\([^)]*\))?: .+(?:\n|$))+",
        re.MULTILINE,
    )

    def __init__(self, linter: PyLinter):
        super().__init__(linter, "Class Docstring Summary Report", "classes")

    def visit_classdef(self, node):
        """Visit each class definition."""
        self.total_items += 1
        docstring = node.doc_node.value if node.doc_node else None
        num_lines = node.tolineno - node.fromlineno
        if num_lines < self.linter.config.class_min_lines:
            self.skipped_items += 1
            return

        if not docstring:
            self.without_docstring += 1
            self.add_message("missing-google-class-docstring", node=node, args=(node.name,))
            return

        self.with_docstring += 1

        # Check Vietnamese docstring
        if self.detect_vietnamese_docstring(node, docstring, "class-vietnamese-docstring-detected"):
            return

        # Check summary line
        lines = [l.strip() for l in docstring.strip().splitlines() if l.strip()]
        if not lines or not re.match(r"^[A-Z].*\.$", lines[0]):
            self.add_message("missing-google-class-summary-line", node=node, args=(node.name,))
            return

        # Detect attributes (self.xxx or xxx = ...)
        attributes = set()
        for stmt in node.body:
            # class-level variables
            if hasattr(stmt, "targets"):
                for target in stmt.targets:
                    if getattr(target, "attrname", None):
                        attributes.add(target.attrname)

            # instance variables inside methods
            if hasattr(stmt, "body"):
                for inner in getattr(stmt, "body", []):
                    try:
                        if hasattr(inner, "targets"):
                            for target in inner.targets:
                                if getattr(target, "attrname", None):
                                    attributes.add(target.attrname)
                    except Exception:
                        continue

        # Check Attributes section
        if attributes and not self.ATTRIBUTES_SECTION.search(docstring):
            attr_list = ", ".join(sorted(attributes))
            self.add_message(
                "missing-google-attributes-section",
                node=node,
                args=(f"{node.name} ({attr_list})",),
            )
            return

        # If all checks passed
        self.google_style_compliant += 1


def register(linter: PyLinter):
    linter.register_checker(ClassDocstringChecker(linter))
