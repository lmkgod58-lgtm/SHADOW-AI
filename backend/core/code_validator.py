import ast
import py_compile
import io
import re
from typing import Dict

class CodeValidator:
    """
    Extracts code blocks from AI responses, validates syntax,
    auto-fixes common errors, and replaces them in the text.
    """

    def validate_code_blocks(self, text: str) -> str:
        pattern = r"```python\s*(.*?)\s*```"

        def replace_block(match):
            code = match.group(1)
            validated = self._validate_and_fix(code)
            return f"```python\n{validated['code']}\n```"

        return re.sub(pattern, replace_block, text, flags=re.DOTALL)

    def _validate_and_fix(self, code: str) -> Dict:
        errors = []

        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax line {e.lineno}: {e.msg}")
            code = self._fix_common_syntax(code, e)
            try:
                ast.parse(code)
                errors.append(f"  -> Auto-patched line {e.lineno}")
            except SyntaxError as e2:
                errors.append(f"  -> Patch failed: {e2.msg}")

        try:
            with io.BytesIO(code.encode("utf-8")) as f:
                py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as e:
            if not any(str(e) in err for err in errors):
                errors.append(f"Compile: {e}")

        try:
            import black
            code = black.format_str(code, mode=black.Mode())
        except:
            pass

        if errors:
            comment = "\n# [GHOSTFRAME VALIDATOR]\n"
            for err in errors:
                comment += f"# ! {err}\n"
            code = comment + code

        return {"code": code, "errors": errors, "valid": len(errors) == 0}

    def _fix_common_syntax(self, code: str, exc: SyntaxError) -> str:
        lines = code.split("\n")
        line_no = exc.lineno - 1
        if line_no < 0 or line_no >= len(lines):
            return code

        line = lines[line_no]
        stripped = line.strip()

        control_kws = ["if ", "for ", "while ", "def ", "class ", "elif ", "else", "try", "except", "finally"]
        if any(stripped.startswith(kw) for kw in control_kws):
            if not line.rstrip().endswith(":") and not line.rstrip().endswith('"'):
                lines[line_no] = line.rstrip() + ":"

        if "EOF" in exc.msg or "unexpected EOF" in exc.msg:
            open_p = line.count("(") - line.count(")")
            open_b = line.count("[") - line.count("]")
            open_c = line.count("{") - line.count("}")
            lines[line_no] = line + ")" * max(0, open_p) + "]" * max(0, open_b) + "}" * max(0, open_c)

        if "EOL while scanning string literal" in exc.msg:
            if line.count("'") % 2 != 0:
                lines[line_no] = line + "'"
            elif line.count('"') % 2 != 0:
                lines[line_no] = line + '"'

        if "unexpected indent" in exc.msg:
            lines[line_no] = line.lstrip()

        return "\n".join(lines)
