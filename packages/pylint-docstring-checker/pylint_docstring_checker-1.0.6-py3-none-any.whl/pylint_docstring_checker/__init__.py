from pylint.lint import PyLinter
from .function_docstring_checker import FunctionDocstringChecker
from .class_docstring_checker import ClassDocstringChecker

def register(linter: PyLinter):
    linter.register_checker(FunctionDocstringChecker(linter))
    linter.register_checker(ClassDocstringChecker(linter))
