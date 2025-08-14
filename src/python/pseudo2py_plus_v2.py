import re
import sys

INDENT = "    "


def to_snake(s: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"[^\w]+", "_", s)
    return s.strip("_").lower()


def parse_requires_type(line: str):
    m = re.match(
        r"^REQUIRES\s+TYPE:\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_\|][A-Za-z0-9_\|\[\]]*)$",
        line,
        re.I,
    )
    if not m:
        return None
    var, types = m.groups()
    types_tuple = ",".join(t.strip() for t in types.split("|"))
    return var, types_tuple


def parse_retry(line: str):
    m = re.match(r"^RETRY:\s*(\d+)(?:\s+backoff=(\d+(?:\.\d+)?))?$", line, re.I)
    if not m:
        return None
    n, b = m.groups()
    return int(n), (float(b) if b else 1.5)


def compile_line(code: str):
    # FUNCTION name(args) RETURNS Type
    m = re.match(
        r"^FUNCTION\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*RETURNS\s*([A-Za-z_][\w\[\], ]*)$",
        code,
        re.I,
    )
    if m:
        name, args, ret = m.groups()
        return f"def {to_snake(name)}({args}) -> {ret}:"

    # END FUNCTION
    if re.match(r"^END\s*FUNCTION$", code, re.I):
        return None

    # SET X = expr
    m = re.match(r"^SET\s+([A-Za-z_]\w*)\s*=\s*(.+)$", code, re.I)
    if m:
        var, expr = m.groups()
        return f"{to_snake(var)} = {expr}"

    # IF / ELSE / ENDIF
    m = re.match(r"^IF\s+(.+?)\s+THEN$", code, re.I)
    if m:
        return f"if {m.group(1)}:"
    if re.match(r"^ELSE$", code, re.I):
        return "else:"
    if re.match(r"^ENDIF$", code, re.I):
        return None

    # FOR EACH var IN iterable
    m = re.match(r"^FOR\s+EACH\s+([A-Za-z_]\w*)\s+IN\s+(.+)$", code, re.I)
    if m:
        var, it = m.groups()
        return f"for {to_snake(var)} in {it}:"
    if re.match(r"^ENDFOR$", code, re.I):
        return None

    # PARALLEL FOR EACH var IN iterable
    m = re.match(r"^PARALLEL\s+FOR\s+EACH\s+([A-Za-z_]\w*)\s+IN\s+(.+)$", code, re.I)
    if m:
        var, it = m.groups()
        return (
            f"# PARALLEL FOR EACH {to_snake(var)} IN {it}\n"
            f"with ThreadPoolExecutor() as __exec:\n"
            f"{INDENT}list(__exec.map(lambda __item: __parallel_body(__item), {it}))"
        )
    if re.match(r"^ENDPARALLEL$", code, re.I):
        return None

    # WHILE ... DO / ENDWHILE
    m = re.match(r"^WHILE\s+(.+?)\s+DO$", code, re.I)
    if m:
        return f"while {m.group(1)}:"
    if re.match(r"^ENDWHILE$", code, re.I):
        return None

    # TRY / CATCH X / ENDTRY
    if re.match(r"^TRY$", code, re.I):
        return "try:"
    m = re.match(r"^CATCH\s+([A-Za-z_][A-Za-z0-9_]*)$", code, re.I)
    if m:
        return f"except {m.group(1)}:"
    if re.match(r"^ENDTRY$", code, re.I):
        return None

    # RETURN / CONTINUE
    m = re.match(r"^RETURN\s+(.+)$", code, re.I)
    if m:
        return f"return {m.group(1)}"
    if re.match(r"^CONTINUE$", code, re.I):
        return "continue"

    # default passthrough (or comment)
    return code


def main():
    if len(sys.argv) < 2:
        print("Usage: pseudo2py_plus_v2.py <input.pseudo> [output.py]")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()

    py_lines = []
    for raw in lines:
        code = raw.rstrip("\r\n")
        compiled = compile_line(code)
        if compiled is None:
            continue
        py_lines.append(compiled)

    py = "\n".join(py_lines)
    if out:
        with open(out, "w", encoding="utf-8") as g:
            g.write(py + "\n")
    else:
        print(py)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
