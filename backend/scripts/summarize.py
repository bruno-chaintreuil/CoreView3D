#!/usr/bin/env python3

import os
import sys
import ast
import json
import argparse
import time
from pathlib import Path

SKIP_DIRS = {".git", "venv", "env", "__pycache__", "node_modules", ".venv"}

def read_file(path):
    # Essaie plusieurs encodages courants
    encs = ("utf-8", "latin-1", "utf-8-sig")
    for enc in encs:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read(), enc
        except Exception as e:
            last_exc = e
    raise last_exc

def summarize_file(path, verbose=False):
    debug = []
    try:
        source, used_enc = read_file(path)
        if verbose:
            debug.append(f"[OK] Lue: {path} (enc={used_enc}, bytes={len(source.encode(used_enc))})")
    except Exception as e:
        debug.append(f"[ERR] Lecture échouée: {path} -> {type(e).__name__}: {e}")
        return {"path": str(path), "error": f"read_error: {e}", "debug": debug}

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        msg = f"SyntaxError: {e.msg} (lineno={e.lineno}, offset={e.offset})"
        debug.append(f"[ERR] Parse AST échoué: {path} -> {msg}")
        return {"path": str(path), "error": msg, "debug": debug}
    except Exception as e:
        debug.append(f"[ERR] Parse AST exception: {path} -> {type(e).__name__}: {e}")
        return {"path": str(path), "error": f"parse_error: {e}", "debug": debug}

    classes, funcs, imports = [], [], []
    try:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # collecte méthodes courtes pour debug éventuel
                method_names = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({"name": node.name, "methods": method_names})
            elif isinstance(node, ast.FunctionDef):
                funcs.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                funcs.append(node.name + " (async)")
            elif isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for n in node.names:
                    imports.append(f"{mod}.{n.name}" if mod else n.name)
    except Exception as e:
        debug.append(f"[ERR] AST walk exception: {path} -> {type(e).__name__}: {e}")
        return {"path": str(path), "error": f"ast_walk_error: {e}", "debug": debug}

    return {
        "path": str(path),
        "classes": classes,
        "functions": funcs,
        "imports": sorted(set(imports)),
        "debug": debug
    }

def summarize_repo(root_dir, verbose=False, max_files=None, include_patterns=None):
    root = Path(root_dir)
    if not root.exists():
        raise FileNotFoundError(root_dir)

    all_results = []
    errors = []
    total_files = 0
    start = time.time()

    # calcul approximatif du nombre de fichiers .py pour le progrès
    estimated = sum(1 for _ in root.rglob("*.py"))
    print(f"[INFO] Dossier racine: {root.resolve()}  fichiers_py estimés: {estimated}", file=sys.stderr)

    for i, path in enumerate(root.rglob("*.py"), 1):
        # skip directories
        if any(part in SKIP_DIRS for part in path.parts):
            if verbose:
                print(f"[SKIP] {path} (répertoire ignoré)", file=sys.stderr)
            continue

        if include_patterns:
            if not any(p in str(path) for p in include_patterns):
                if verbose:
                    print(f"[SKIP] {path} (pattern mismatch)", file=sys.stderr)
                continue

        if max_files and total_files >= max_files:
            if verbose:
                print(f"[STOP] Atteint max_files={max_files}", file=sys.stderr)
            break

        if verbose:
            print(f"[PROG] Analyse {i}/{estimated} -> {path}", file=sys.stderr)

        total_files += 1
        info = summarize_file(path, verbose=verbose)
        if info.get("error"):
            errors.append(info)
        all_results.append(info)

    elapsed = time.time() - start
    footer = {
        "root": str(root.resolve()),
        "files_processed": total_files,
        "elapsed_seconds": round(elapsed, 2),
        "errors_count": len(errors)
    }
    if verbose:
        print(f"[DONE] files={total_files} errors={len(errors)} elapsed={footer['elapsed_seconds']}s", file=sys.stderr)

    return {"summary": all_results, "meta": footer, "errors": errors}

def pretty_text_output(result):
    out = []
    out.append(f"Repository: {result['meta']['root']}")
    out.append(f"Fichiers analysés: {result['meta']['files_processed']}")
    out.append(f"Erreurs: {result['meta']['errors_count']}")
    out.append("")
    for item in result["summary"]:
        out.append(f"--- {item.get('path')}")
        if item.get("error"):
            out.append(f"ERROR: {item['error']}")
            out.extend(item.get("debug", []))
            out.append("")
            continue
        if item.get("imports"):
            out.append("Imports: " + ", ".join(item["imports"]))
        if item.get("classes"):
            cls_lines = []
            for c in item["classes"]:
                m = f" (methods: {', '.join(c['methods'])})" if c.get("methods") else ""
                cls_lines.append(f"{c['name']}{m}")
            out.append("Classes: " + ", ".join(cls_lines))
        if item.get("functions"):
            out.append("Functions: " + ", ".join(item["functions"]))
        if item.get("debug"):
            out.extend(item["debug"])
        out.append("")
    return "\n".join(out)

def parse_args():
    p = argparse.ArgumentParser(description="Summarize Python repo with debug prints")
    p.add_argument("root", nargs="?", default=".", help="Chemin du dépôt (défaut=.)")
    p.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux (prints sur stderr)")
    p.add_argument("--max-files", type=int, help="Nombre max de fichiers à analyser")
    p.add_argument("--json", action="store_true", help="Sortie JSON (sinon texte lisible)")
    p.add_argument("--include", nargs="*", help="Inclure seulement les fichiers contenant ces sous-chaînes dans leur chemin")
    return p.parse_args()

def main():
    args = parse_args()
    try:
        result = summarize_repo(args.root, verbose=args.verbose, max_files=args.max_files, include_patterns=args.include)
    except Exception as e:
        print(f"[FATAL] Exception: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(pretty_text_output(result))

if __name__ == "__main__":
    main()
