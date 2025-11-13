import re
from pylint.checkers import BaseChecker
from pylint.reporters.text import TextReporter


class DocstringCheckerBase(BaseChecker):
    """
    Base class for all docstring-related checkers.
    Provides shared logic such as detecting Vietnamese docstrings and printing summary.
    """

    VIETNAMESE_REGEX = re.compile(
        r"[ăâđêôơưàáạảãèéẹẻẽìíịỉĩòóọỏõùúụủũỳýỵỷỹ"
        r"ĂÂĐÊÔƠƯÀÁẠẢÃÈÉẸẺẼÌÍỊỈĨÒÓỌỎÕÙÚỤỦŨỲÝỴỶỸ]"
    )

    def __init__(self, linter, report_title: str, entity_name: str):
        super().__init__(linter)
        self.report_title = report_title
        self.entity_name = entity_name

        # Shared statistics
        self.total_items = 0
        self.skipped_items = 0
        self.with_docstring = 0
        self.without_docstring = 0
        self.vietnamese_docstring = 0
        self.english_or_japanese_docstring = 0
        self.google_style_compliant = 0

    def detect_vietnamese_docstring(self, node, docstring: str, msg_id: str) -> bool:
        """
        Detect Vietnamese text in a docstring and report message if found.

        Args:
            node: The AST node representing the class/function.
            docstring (str): The docstring text.
            msg_id (str): The message ID to use when reporting.

        Returns:
            bool: True if Vietnamese text was detected, False otherwise.
        """
        if not docstring:
            return False

        if self.VIETNAMESE_REGEX.search(docstring):
            self.vietnamese_docstring += 1
            self.add_message(msg_id, node=node, args=(node.name,))
            return True

        self.english_or_japanese_docstring += 1
        return False

    def close(self):
        """Print summary report at the end."""
        if not isinstance(self.linter.reporter, TextReporter):
            return

        total = self.total_items
        with_doc = self.with_docstring
        skipped = self.skipped_items
        percent_doc = ((with_doc + skipped) / total * 100) if total > 0 else 0.0

        google_style = self.google_style_compliant
        google_percent = (
            ((google_style + skipped) / total * 100)
            if total > 0
            else 0.0
        )

        self.linter.reporter.writeln(f"\n📘 {self.report_title}:")
        self.print_stat(f"- Total {self.entity_name}:", total)
        self.print_stat(f"- Skipped {self.entity_name}:", self.skipped_items)
        self.print_stat("- With docstring:", self.with_docstring)
        self.print_stat("- Without docstring:", self.without_docstring)
        self.print_stat("- Vietnamese docstrings:", self.vietnamese_docstring)
        self.print_stat("- English/Japanese docstrings:", self.english_or_japanese_docstring)
        self.print_stat("- Google-style compliant:", self.google_style_compliant)
        self.print_stat("- Docstring Coverage:", f"{percent_doc:.2f}%")
        self.print_stat("- Google Style Coverage:", f"{google_percent:.2f}%")

    def print_stat(self, label: str, value: str | int | float):
        self.linter.reporter.writeln(f"{label:<40}{value}")