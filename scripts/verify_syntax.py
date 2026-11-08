"""
SDNFlowGuard Python Syntax & Bytecode Compilation Validator
Validates in-memory compilation of all Python source files in the project without
creating any __pycache__ directories or .pyc bytecode files on disk.
"""
import pathlib
import sys

def verify_syntax(root_path: pathlib.Path) -> int:
    err_count = 0
    file_count = 0
    for file_path in sorted(root_path.rglob("*.py")):
        # Skip virtualenvs, node_modules, git, and scratch folders
        if any(part in ("venv", ".venv", "node_modules", ".git", "scratch") for part in file_path.parts):
            continue
        file_count += 1
        try:
            # compile in-memory without inheriting compiler flags or writing bytecode
            compile(file_path.read_bytes(), str(file_path), "exec", dont_inherit=True)
        except SyntaxError as exc:
            print(f"[SYNTAX ERROR] {file_path}:{exc.lineno}: {exc.msg}", file=sys.stderr)
            err_count += 1
        except Exception as exc:
            print(f"[READ ERROR] {file_path}: {exc}", file=sys.stderr)
            err_count += 1

    if err_count > 0:
        print(f"FAILED: {err_count} syntax error(s) found across {file_count} Python files.", file=sys.stderr)
        return 1

    print(f"PASS: Verified in-memory syntax of {file_count} Python files with zero syntax errors and zero bytecode artifacts written.")
    return 0

if __name__ == "__main__":
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("backend")
    sys.exit(verify_syntax(target))
