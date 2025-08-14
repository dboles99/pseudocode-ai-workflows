#!/usr/bin/env python3
"""
pseudo2py_plus_v2.py
Enhancements over pseudo2py_plus.py:
  - REQUIRES TYPE: var: Type[|Type2...]   -> asserts isinstance(var, (Type,...))
  - REQUIRES: <expr>                      -> assert <expr>
  - ENSURES: <expr>                       -> assert <expr> at end of FUNCTION
  - TIMEOUT: <seconds>s                   -> applies @with_timeout(seconds) to NEXT FUNCTION
  - RETRY: <n> [backoff=<float>]          -> applies @with_retry(n, backoff) to NEXT FUNCTION
  - TRY / CATCH <Exception> / ENDTRY
  - PARALLEL FOR EACH var IN iterable / ENDPARALLEL (ThreadPoolExecutor)
  - Existing: FUNCTION/END FUNCTION, SET, IF/ELSE/ENDIF, FOR EACH/ENDFOR, WHILE/ENDWHILE, RETURN/CONTINUE
"""
import re, sys, time, functools
from concurrent.futures import ThreadPoolExecutor

INDENT = "    "

def to_snake(name: str) -> str:
    s = re.sub(r'[^0-9a-zA-Z]+', '_', name).strip('_')
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()
    return s

# Decorators for TIMEOUT/RETRY
def with_timeout(seconds):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.time()
            result_container = {}
            exc_container = {}
            done = False
            import threading
            def run():
                try:
                    result_container['r'] = fn(*args, **kwargs)
                except Exception as e:
                    exc_container['e'] = e
                finally:
                    nonlocal done
                    done = True
            t = threading.Thread(target=run, daemon=True)
            t.start()
            t.join(timeout=seconds)
            if not done:
                raise TimeoutError(f"Function timed out after {seconds}s")
            if 'e' in exc_container:
                raise exc_container['e']
            return result_container.get('r')
        return wrapper
    return deco

def with_retry(retries, backoff=1.5):
    retries = int(retries)
    backoff = float(backoff)
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            delay = 0.0
            last_exc = None
            for attempt in range(retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt == retries:
                        raise
                    delay = delay * backoff if delay > 0 else 0.2
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return deco

def parse_requires_type(line: str):
    m = re.match(r'^REQUIRES\s+TYPE:\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_\|][A-Za-z0-9_\|\[\]]*)$', line, re.I)
    if not m: return None
    var, types = m.groups()
    types_tuple = ','.join([t.strip() for t in types.split('|')])
    return var, types_tuple

def parse_requires(line: str):
    m = re.match(r'^REQUIRES:\s*(.+)$', line, re.I)
    return m.group(1) if m else None

def parse_ensures(line: str):
    m = re.match(r'^ENSURES:\s*(.+)$', line, re.I)
    return m.group(1) if m else None

def parse_timeout(line: str):
    m = re.match(r'^TIMEOUT:\s*(\d+)s$', line, re.I)
    return int(m.group(1)) if m else None

def parse_retry(line: str):
    m = re.match(r'^RETRY:\s*(\d+)(?:\s+backoff=(\d+(?:\.\d+)?))?$', line, re.I)
    if not m: return None
    n, b = m.groups()
    return int(n), (float(b) if b else 1.5)

def translate_line(line: str):
    code = line.rstrip()

    # FUNCTION
    m = re.match(r'^FUNCTION\s+([A-Za-z0-9_]+)\((.*?)\)\s*->\s*(.*)$', code, re.I)
    if m:
        name, args, ret = m.groups()
        name = to_snake(name)
        args_py = ', '.join([to_snake(a.strip()) for a in args.split(',') if a.strip()])
        header = f"def {name}({args_py}):"
        return header

    # END FUNCTION
    if re.match(r'^END\s*FUNCTION$', code, re.I):
        return None

    # SET
    m = re.match(r'^SET\s+([A-Za-z0-9_]+)\s*:=\s*(.+)$', code, re.I)
    if m:
        var, expr = m.groups()
        return f"{to_snake(var)} = {expr}"

    # IF/ELSE/ENDIF
    m = re.match(r'^IF\s+(.+?)\s+THEN$', code, re.I)
    if m: return f"if {m.group(1)}:"
    if re.match(r'^ELSE$', code, re.I): return "else:"
    if re.match(r'^ENDIF$', code, re.I): return None

    # FOR EACH
    m = re.match(r'^FOR\s+EACH\s+([A-Za-z0-9_]+)\s+IN\s+(.+)$', code, re.I)
    if m:
        var, it = m.groups()
        return f"for {to_snake(var)} in {it}:"
    if re.match(r'^ENDFOR$', code, re.I): return None

    # PARALLEL FOR EACH
    m = re.match(r'^PARALLEL\s+FOR\s+EACH\s+([A-Za-z0-9_]+)\s+IN\s+(.+)$', code, re.I)
    if m:
        var, it = m.groups()
        # We require the user to write the body as if inside a function __parallel_body(__item)
        return f"# PARALLEL FOR EACH {to_snake(var)} IN {it}\nwith ThreadPoolExecutor() as __exec:\n{INDENT}list(__exec.map(lambda __item: __parallel_body(__item), {it}))"
    if re.match(r'^ENDPARALLEL$', code, re.I): return None

    # WHILE
    m = re.match(r'^WHILE\s+(.+?)\s+DO$', code, re.I)
    if m: return f"while {m.group(1)}:"
    if re.match(r'^ENDWHILE$', code, re.I): return None

    # TRY/CATCH/ENDTRY
    if re.match(r'^TRY$', code, re.I): return "try:"
    m = re.match(r'^CATCH\s+([A-Za-z_][A-Za-z0-9_]*)$', code, re.I)
    if m: return f"except {m.group(1)}:"
    if re.match(r'^ENDTRY$', code, re.I): return None

    # RETURN/CONTINUE
    m = re.match(r'^RETURN\s+(.+)$', code, re.I)
    if m: return f"return {m.group(1)}"
    if re.match(r'^CONTINUE$', code, re.I): return "continue"

    # default: passthrough
    return code

def convert(lines):
    py = []
    indent_stack = []
    ensures = []
    pending_timeout = None
    pending_retry = None
    in_function = False

    def append(line: str):
        py.append(INDENT * len(indent_stack) + line)

    for raw in lines:
        line = raw.rstrip()

        # TIMEOUT / RETRY directives apply to NEXT FUNCTION
        t = parse_timeout(line)
        if t is not None:
            pending_timeout = t
            continue
        r = parse_retry(line)
        if r is not None:
            pending_retry = r
            continue

        # REQUIRES TYPE
        rt = parse_requires_type(line)
        if rt:
            var, types_tuple = rt
            append(f"assert isinstance({to_snake(var)}, ({types_tuple},)), 'TYPE check failed for {var}: expected {types_tuple}'")
            continue

        # REQUIRES
        req = parse_requires(line)
        if req:
            append(f"assert {req}, 'REQUIRES failed: {req}'")
            continue

        # ENSURES (buffer to end of function)
        ens = parse_ensures(line)
        if ens:
            ensures.append(ens)
            continue

        # FUNCTION open: apply decorators if pending
        if re.match(r'^FUNCTION\b', line.strip(), re.I):
            if pending_timeout is not None:
                append(f"@with_timeout({pending_timeout})")
                pending_timeout = None
            if pending_retry is not None:
                n, b = pending_retry
                append(f"@with_retry({n}, {b})")
                pending_retry = None
            translated = translate_line(line.strip())
            append(translated)
            indent_stack.append('BLOCK')
            in_function = True
            continue

        # Block opens
        opens = [r'^(IF\b.*THEN)$', r'^(FOR\b\s+EACH\b.*)$', r'^(WHILE\b.*DO)$', r'^TRY$', r'^PARALLEL\b\s+FOR\b\s+EACH\b.*$']
        closes = [r'^(ENDIF|ENDFOR|ENDWHILE|ENDTRY|ENDPARALLEL)$']

        import re as _re
        if any(_re.match(p, line.strip(), _re.I) for p in opens):
            translated = translate_line(line.strip())
            append(translated)
            indent_stack.append('BLOCK')
            continue

        if _re.match(r'^END\s*FUNCTION$', line.strip(), _re.I):
            # close function
            if ensures:
                for e in ensures:
                    append(f"assert {e}, 'ENSURES failed: {e}'")
                ensures.clear()
            if indent_stack:
                indent_stack.pop()
            in_function = False
            continue

        if any(_re.match(p, line.strip(), _re.I) for p in closes):
            if indent_stack:
                indent_stack.pop()
            continue

        translated = translate_line(line.strip())
        if translated is None:
            continue
        append(translated)

    return "\n".join(py) + "\n"

def main():
    try:
    if len(sys.argv) < 2:
            print("Usage: pseudo2py_plus_v2.py <input.pseudo> [output.py]")
            sys.exit(1)
    src = sys.argv[1]
            out = sys.argv[2] if len(sys.argv) > 2 else None
            with open(src, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            py = convert(lines)
            if out:
                with open(out, 'w', encoding='utf-8') as f:
                    f.write(py)
            else:
                print(py)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR [converter]: {e}")
        sys.exit(1)
