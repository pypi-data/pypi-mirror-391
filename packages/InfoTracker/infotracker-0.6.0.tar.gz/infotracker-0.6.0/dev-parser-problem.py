#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Porównanie dev_parser.py vs parser.py + parser_modules/*

Wynik: raport Markdown z różnicami funkcji (sygnatury, ciała, wywołania, regexy).
Python 3.10+ (bez zewnętrznych zależności).

Użycie:
  python compare_parsers.py dev_parser.py parser.py parser_modules/ --out parser_diff_report.md

Jeśli nie podasz --out, raport trafi do parser_diff_report.md w bieżącym katalogu.
"""

from __future__ import annotations
import ast
import argparse
import difflib
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# -------------------------- zbieranie informacji --------------------------

@dataclass
class FnInfo:
    qualname: str           # np. "Class.method" lub "function"
    name: str               # sama nazwa, np. "method" / "function"
    file: Path              # ścieżka pliku
    lineno: int             # linia startu definicji
    signature: str          # uproszczona sygnatura
    source: str             # surowe źródło funkcji
    ast_dump_hash: str      # hash struktury AST ciała (bez lineno/col)
    calls: Set[str]         # nazwy wywoływanych funkcji (heurystycznie)
    regexes: Set[str]       # zebrane literały wzorców regex (re.compile/search/...)
    node_hist: Dict[str, int]  # histogram typów węzłów AST (prosty „odcisk palca”)

class _SrcGetter(ast.NodeVisitor):
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines(keepends=True)

    def get_src(self, node: ast.AST) -> str:
        try:
            # Py>=3.8: end_lineno/end_col_offset dostępne po parsowaniu z TypeComments
            start = (node.lineno - 1, getattr(node, "col_offset", 0))
            end = (getattr(node, "end_lineno", node.lineno) - 1,
                   getattr(node, "end_col_offset", 0))
        except Exception:
            return ""
        if start[0] == end[0]:
            seg = self.lines[start[0]][start[1]:end[1]]
        else:
            seg = self.lines[start[0]][start[1]:]
            for i in range(start[0]+1, end[0]):
                seg += self.lines[i]
            seg += self.lines[end[0]][:end[1]]
        return seg

def _fn_signature(fn: ast.FunctionDef) -> str:
    a = fn.args
    parts: List[str] = []
    def argn(x: ast.arg) -> str: return x.arg
    for x in a.posonlyargs + a.args: parts.append(argn(x))
    if a.vararg: parts.append("*" + a.vararg.arg)
    if a.kwonlyargs:
        parts.append("*")
        for x in a.kwonlyargs: parts.append(argn(x))
    if a.kwarg: parts.append("**" + a.kwarg.arg)
    return f"{fn.name}({', '.join(parts)})"

def _collect_calls(fn: ast.FunctionDef) -> Set[str]:
    calls: Set[str] = set()
    class V(ast.NodeVisitor):
        def visit_Call(self, n: ast.Call):
            name: Optional[str] = None
            if isinstance(n.func, ast.Name):
                name = n.func.id
            elif isinstance(n.func, ast.Attribute):
                name = n.func.attr
            if name: calls.add(name)
            self.generic_visit(n)
    V().visit(fn)
    return calls

_RE_FUNCS = {"compile", "search", "match", "fullmatch", "findall", "finditer", "sub", "subn"}

def _collect_regexes(fn: ast.FunctionDef) -> Set[str]:
    pats: Set[str] = set()
    class V(ast.NodeVisitor):
        def visit_Call(self, n: ast.Call):
            tgt = None
            if isinstance(n.func, ast.Attribute) and n.func.attr in _RE_FUNCS:
                tgt = n
            if tgt and n.args:
                a0 = n.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    pats.add(a0.value)
            self.generic_visit(n)
    V().visit(fn)
    return pats

def _histogram(node: ast.AST) -> Dict[str, int]:
    hist: Dict[str, int] = {}
    class V(ast.NodeVisitor):
        def generic_visit(self, n: ast.AST):
            name = type(n).__name__
            hist[name] = hist.get(name, 0) + 1
            super().generic_visit(n)
    V().visit(node)
    return hist

def _body_hash(fn: ast.FunctionDef) -> str:
    # Hash strukturalny: ast.dump bez atrybutów
    dump = ast.dump(fn, include_attributes=False)
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()

def _walk_functions(tree: ast.AST, src: str, file: Path, cls_prefix: Optional[str]=None) -> Dict[str, FnInfo]:
    out: Dict[str, FnInfo] = {}
    getter = _SrcGetter(src)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
            qual = name if not cls_prefix else f"{cls_prefix}.{name}"
            src_seg = getter.get_src(node)
            out[qual] = FnInfo(
                qualname=qual,
                name=name,
                file=file,
                lineno=node.lineno,
                signature=_fn_signature(node),
                source=src_seg,
                ast_dump_hash=_body_hash(node),
                calls=_collect_calls(node),
                regexes=_collect_regexes(node),
                node_hist=_histogram(node),
            )
        elif isinstance(node, ast.ClassDef):
            # klasy: zbierz metody jako Class.method
            getter_cls = _SrcGetter(src)
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    name = sub.name
                    qual = f"{node.name}.{name}"
                    src_seg = getter_cls.get_src(sub)
                    out[qual] = FnInfo(
                        qualname=qual,
                        name=name,
                        file=file,
                        lineno=sub.lineno,
                        signature=_fn_signature(sub),
                        source=src_seg,
                        ast_dump_hash=_body_hash(sub),
                        calls=_collect_calls(sub),
                        regexes=_collect_regexes(sub),
                        node_hist=_histogram(sub),
                    )
    return out

def _parse_file(p: Path) -> Tuple[ast.AST, str]:
    txt = p.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(txt, filename=str(p))
    return tree, txt

def collect_fninfo_from_files(files: List[Path]) -> Dict[str, FnInfo]:
    result: Dict[str, FnInfo] = {}
    for f in files:
        try:
            tree, src = _parse_file(f)
        except Exception as e:
            print(f"[WARN] Nie mogę sparsować {f}: {e}")
            continue
        chunk = _walk_functions(tree, src, f)
        # w przypadku konfliktów nadpisujemy ostatnim wystąpieniem (zapisz listę, jeśli wolisz)
        result.update(chunk)
    return result

# -------------------------- dopasowanie i porównanie --------------------------

def _best_matches(missing: Set[str], pool: Dict[str, FnInfo], src_side: Dict[str, FnInfo], topk: int=3) -> Dict[str, List[Tuple[str, float]]]:
    """
    Dla funkcji, których nie ma po drugiej stronie, znajdź kandydatów wg podobieństwa:
    - porównanie histogramów AST (kosinusowe podobieństwo),
    - diff ratio na źródle (SequenceMatcher).
    """
    def cos_sim(h1: Dict[str, int], h2: Dict[str, int]) -> float:
        if not h1 or not h2: return 0.0
        keys = set(h1) | set(h2)
        dot = sum(h1.get(k, 0)*h2.get(k, 0) for k in keys)
        n1 = sum(v*v for v in h1.values()) ** 0.5
        n2 = sum(v*v for v in h2.values()) ** 0.5
        if n1 == 0 or n2 == 0: return 0.0
        return dot/(n1*n2)

    out: Dict[str, List[Tuple[str, float]]] = {}
    for qual in missing:
        src_f = src_side.get(qual)
        if not src_f: 
            continue
        scores: List[Tuple[str, float]] = []
        for cand_qual, cand in pool.items():
            # podobieństwo łączone: 70% kosinus histogramu AST + 30% SequenceMatcher tekstu
            sm = difflib.SequenceMatcher(a=src_f.source, b=cand.source)
            ratio = sm.quick_ratio() * 0.3 + cos_sim(src_f.node_hist, cand.node_hist) * 0.7
            scores.append((cand_qual, ratio))
        scores.sort(key=lambda x: x[1], reverse=True)
        out[qual] = scores[:topk]
    return out

def unified_diff(a: str, b: str, fromfile: str, tofile: str, n: int=6) -> str:
    alines = a.splitlines()
    blines = b.splitlines()
    diff = difflib.unified_diff(alines, blines, fromfile=fromfile, tofile=tofile, n=n, lineterm="")
    return "\n".join(diff)

# -------------------------- raport --------------------------

def make_report(dev: Dict[str, FnInfo], new: Dict[str, FnInfo], out_path: Path, max_diffs: int=40, ctx_lines: int=6):
    dev_keys = set(dev.keys())
    new_keys = set(new.keys())

    missing_in_new = sorted(dev_keys - new_keys)
    added_in_new   = sorted(new_keys - dev_keys)
    common         = sorted(dev_keys & new_keys)

    with out_path.open("w", encoding="utf-8") as out:
        out.write("# Parser functions diff report\n\n")

        out.write("## Summary\n")
        out.write(f"- Functions in DEV: **{len(dev_keys)}**\n")
        out.write(f"- Functions in NEW: **{len(new_keys)}**\n")
        out.write(f"- Common: **{len(common)}** | Missing in NEW: **{len(missing_in_new)}** | Added in NEW: **{len(added_in_new)}**\n\n")

        out.write("## Missing in NEW (present in DEV)\n")
        if missing_in_new:
            for q in missing_in_new:
                f = dev[q]
                out.write(f"- `{q}` — {f.signature}  *(at {f.file.name}:{f.lineno})*\n")
        else:
            out.write("- (none)\n")
        out.write("\n")

        out.write("## Added in NEW (absent in DEV)\n")
        if added_in_new:
            for q in added_in_new:
                f = new[q]
                out.write(f"- `{q}` — {f.signature}  *(at {f.file.name}:{f.lineno})*\n")
        else:
            out.write("- (none)\n")
        out.write("\n")

        # Heurystyczne dopasowania dla brakujących
        if missing_in_new:
            out.write("## Rename/move suggestions (for missing in NEW)\n")
            candidates = _best_matches(set(missing_in_new), new, dev, topk=3)
            for q, cands in candidates.items():
                out.write(f"- `{q}` → candidates: ")
                if not cands:
                    out.write("(none)\n")
                else:
                    out.write(", ".join([f"`{cand}` (sim={score:.2f})" for cand, score in cands]) + "\n")
            out.write("\n")

        out.write("## Changed bodies / signatures (common functions)\n")
        changed = 0
        for q in common:
            d = dev[q]; n = new[q]
            sig_changed = d.signature != n.signature
            body_changed = d.ast_dump_hash != n.ast_dump_hash
            calls_added = sorted(n.calls - d.calls)
            calls_removed = sorted(d.calls - n.calls)
            rx_added = sorted(n.regexes - d.regexes)
            rx_removed = sorted(d.regexes - n.regexes)

            if not (sig_changed or body_changed or calls_added or calls_removed or rx_added or rx_removed):
                continue

            changed += 1
            out.write(f"\n### {q}\n")
            out.write(f"- DEV: `{d.signature}` *(at {d.file.name}:{d.lineno})*\n")
            out.write(f"- NEW: `{n.signature}` *(at {n.file.name}:{n.lineno})*\n")
            if sig_changed:
                out.write(f"- **Signature changed**\n")
            if body_changed:
                out.write(f"- **Body changed** (AST-hash)\n")
            if calls_added or calls_removed:
                if calls_added:  out.write(f"- Calls added: {calls_added}\n")
                if calls_removed: out.write(f"- Calls removed: {calls_removed}\n")
            if rx_added or rx_removed:
                if rx_added:   out.write(f"- Regex added: {rx_added}\n")
                if rx_removed: out.write(f"- Regex removed: {rx_removed}\n")

            # tekstowy diff (limitowane)
            diff_text = unified_diff(
                d.source, n.source,
                fromfile=f"DEV/{d.file.name}:{d.lineno}",
                tofile=f"NEW/{n.file.name}:{n.lineno}",
                n=ctx_lines
            )
            if diff_text.strip():
                out.write("\n```diff\n")
                # ogranicz rozmiar w raporcie
                lines = diff_text.splitlines()
                if len(lines) > 2000:
                    lines = lines[:2000] + ["... (diff truncated)"]
                out.write("\n".join(lines))
                out.write("\n```\n")

            if changed >= max_diffs:
                out.write("\n_(diff limit reached — increase with --max-diffs)_\n")
                break

        if changed == 0:
            out.write("- (no changed common functions)\n")

# -------------------------- main --------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dev_parser", type=Path, help="Ścieżka do dev_parser.py")
    ap.add_argument("parser_py", type=Path, help="Ścieżka do nowego parser.py")
    ap.add_argument("modules_dir", type=Path, help="Katalog parser_modules/")
    ap.add_argument("--out", type=Path, default=Path("parser_diff_report.md"), help="Plik wyjściowy z raportem")
    ap.add_argument("--max-diffs", type=int, default=40, help="Max funkcji z pełnym diffem w raporcie")
    ap.add_argument("--ctx-lines", type=int, default=6, help="Ilość linii kontekstu w unified diff")
    args = ap.parse_args()

    dev_parser = args.dev_parser.resolve()
    parser_py = args.parser_py.resolve()
    modules_dir = args.modules_dir.resolve()

    assert dev_parser.exists(), f"Nie znaleziono: {dev_parser}"
    assert parser_py.exists(), f"Nie znaleziono: {parser_py}"
    assert modules_dir.exists() and modules_dir.is_dir(), f"Nie znaleziono katalogu: {modules_dir}"

    # Zbierz funkcje z dev
    dev_funcs = collect_fninfo_from_files([dev_parser])

    # Zbierz funkcje z nowego parsera i wszystkich modułów
    new_files = [parser_py] + sorted(modules_dir.glob("*.py"))
    new_funcs = collect_fninfo_from_files(new_files)

    make_report(dev_funcs, new_funcs, args.out, max_diffs=args.max_diffs, ctx_lines=args.ctx_lines)
    print(f"[OK] Raport zapisany do: {args.out}")

if __name__ == "__main__":
    main()
