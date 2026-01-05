import ast
import sys
from typing import Tuple, Optional

class CodeLinter:
    """
    Static analysis tool to prevent syntax and indentation errors 
    before code enters the runtime.
    """
    
    @staticmethod
    def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """
        Parses code string to check for syntax errors.
        Returns (is_valid, error_message).
        """
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            error_msg = f"SyntaxError on line {e.lineno}: {e.msg}\n{e.text}"
            return False, error_msg
        except Exception as e:
            return False, f"Linter Error: {str(e)}"

    @staticmethod
    def check_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Reads and checks a file from disk.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return CodeLinter.check_syntax(content)
        except Exception as e:
            return False, f"File Read Error: {str(e)}"
