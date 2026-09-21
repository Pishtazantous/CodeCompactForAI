#!/usr/bin/env python3
"""
codemerge.py — Manifest / Fetch / Diff / Search for LLM-friendly project bundling.

Commands
--------
manifest    Build a compact map of the project (paths + symbols + imports).
fetch       Given a list of file paths, emit their full contents.
diff        Emit only files that changed since the previous run.
search      Search a symbol across the project.
langs       List supported languages.

Ignore support
--------------
A gitignore-style file named ``.codemergeignore`` in the project root is
applied to every command. It also works in non-Git mode, and it can be
overridden or disabled from the CLI:

    --ignore-file PATH    use a custom ignore file
    --no-ignore-file      disable ignore-file support

Working directory
-----------------
By default, codemerge operates on the current working directory. To work
on a different directory without changing your shell, use ``-C`` / ``--cd``:

    python codemerge.py -C /path/to/project manifest -o .ai/manifest.md
    python codemerge.py manifest --cd /path/to/project -o .ai/manifest.md

This changes the process working directory before any command runs, so
all relative paths (input, output, ignore file, state file) are resolved
against the new directory, and Git detection uses that directory too.

Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

DEFAULT_MANIFEST_OUT = "manifest.txt"
DEFAULT_BUNDLE_OUT = "project_source.txt"
DEFAULT_STATE_NAME = "codemerge.state.json"
DEFAULT_IGNORE_FILE = ".codemergeignore"
DEFAULT_MAX_SIZE_MB = 100.0
STATE_VERSION = 1

EXCLUDE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
    "dist", "build", "target", "out", ".idea", ".vscode", ".next",
    ".nuxt", "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "vendor", "obj", "Debug", "Release", ".cache", ".tox",
    ".eggs", "site-packages", ".sass-cache", ".parcel-cache",
    ".turbo", ".gradle", ".mvn", ".codemerge_cache",
}

EXCLUDE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "Pipfile.lock", "Cargo.lock", "composer.lock", "Gemfile.lock",
    "go.sum", "bun.lockb",
}

EXCLUDE_GLOBS = {"*.min.js", "*.min.css", "*.map"}

COMMON_EXTS = { ".markdown", ".rst", ".txt", ".adoc"}
COMMON_GLOBS = {
    "readme*", "license*", "licence*", "changelog*", "contributing*",
    "authors*", "notice*",
    "dockerfile*", "docker-compose*", "compose*.yml", "compose*.yaml",
    "makefile", "gnumakefile",
    ".gitignore", ".gitattributes", ".editorconfig", ".dockerignore",
    ".env.example", ".env.sample", ".env.template", ".env.dist",
}

SENSITIVE_NAMES = {
    ".env", ".netrc", ".pypirc", ".htpasswd", ".pgpass",
    "credentials.json", "secrets.json", "service-account.json",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
}
SENSITIVE_GLOBS = {
    "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore",
    "*.ppk", "*.secret", "*.secrets", "*.crt",
}
SAFE_ENV_NAMES = {".env.example", ".env.sample", ".env.template", ".env.dist"}

SOURCE_EXTS: dict[str, set[str]] = {
    "python": {".py", ".pyi", ".pyx", ".pyw"},
    "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx"},
    "vue": {".vue"},
    "svelte": {".svelte"},
    "web": {".html", ".htm", ".css", ".scss", ".sass", ".less"},
    "c": {".c", ".h"},
    "cpp": {".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx", ".inl", ".ipp"},
    "csharp": {".cs"},
    "java": {".java"},
    "kotlin": {".kt", ".kts"},
    "go": {".go"},
    "rust": {".rs"},
    "ruby": {".rb", ".rake"},
    "php": {".php"},
    "swift": {".swift"},
    "dart": {".dart"},
    "scala": {".scala", ".sc"},
    "shell": {".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd"},
    "sql": {".sql"},
    "yaml": {".yaml", ".yml"},
    "json": {".json"},
    "xml": {".xml"},
    "toml": {".toml"},
    "ini": {".ini", ".cfg", ".conf", ".properties"},
    "markdown": {".md", ".markdown", ".rst", ".adoc"},
    "protobuf": {".proto"},
    "graphql": {".graphql", ".gql"},
    "terraform": {".tf", ".tfvars", ".hcl"},
    "lua": {".lua"},
    "perl": {".pl", ".pm"},
    "r": {".r", ".rmd"},
    "haskell": {".hs", ".lhs"},
    "clojure": {".clj", ".cljs", ".cljc", ".edn"},
    "elixir": {".ex", ".exs"},
    "erlang": {".erl", ".hrl"},
    "ocaml": {".ml", ".mli"},
    "fsharp": {".fs", ".fsx", ".fsi"},
    "jupyter": {".ipynb"},
}

EXT_TO_LANG: dict[str, str] = {}
for _lang, _exts in SOURCE_EXTS.items():
    for _e in _exts:
        EXT_TO_LANG.setdefault(_e, _lang)

OPAQUE_LANGS = {
    "markdown", "json", "yaml", "xml", "toml", "ini", "sql",
    "graphql", "protobuf", "jupyter",
}

# ============================================================
# Basic helpers
# ============================================================

def is_sensitive(name: str) -> bool:
    lower = name.lower()
    if lower in SAFE_ENV_NAMES:
        return False
    if lower in SENSITIVE_NAMES:
        return True
    for pat in SENSITIVE_GLOBS:
        if fnmatch.fnmatch(lower, pat):
            return True
    if lower.startswith(".env."):
        suffix = lower[5:]
        return suffix not in {"example", "sample", "template", "dist"}
    return False


def find_git_root(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def should_skip_dir(name: str) -> bool:
    if name in EXCLUDE_DIRS:
        return True
    if name.startswith("cmake-build-"):
        return True
    if name.endswith(".egg-info"):
        return True
    return False


def should_skip_path(rel: Path) -> bool:
    for part in rel.parts[:-1]:
        if should_skip_dir(part):
            return True
    return False


def should_skip_file(name: str) -> bool:
    if name in EXCLUDE_FILES:
        return True
    lower = name.lower()
    for pat in EXCLUDE_GLOBS:
        if fnmatch.fnmatch(lower, pat):
            return True
    return False


def is_binary(p: Path, sample_size: int = 8192) -> bool:
    try:
        with p.open("rb") as f:
            chunk = f.read(sample_size)
    except OSError:
        return True
    if not chunk:
        return False
    return b"\x00" in chunk


def file_sha(p: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def estimate_tokens(text: str) -> int:
    try:
        import tiktoken  # type: ignore
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def human_size(n: int) -> str:
    for unit in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}{unit}"
        n /= 1024  # type: ignore
    return f"{n:.1f}T"


# ============================================================
# Ignore file support (.codemergeignore)
# ============================================================

def _translate_gitignore_pattern(pattern: str) -> str:
    i, n = 0, len(pattern)
    out: list[str] = []
    while i < n:
        c = pattern[i]
        i += 1
        if c == "*":
            if i < n and pattern[i] == "*":
                i += 1
                if i < n and pattern[i] == "/":
                    i += 1
                    out.append("(?:.*/)?")
                else:
                    out.append(".*")
            else:
                out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "[":
            j = i
            if j < n and pattern[j] in "!^":
                j += 1
            if j < n and pattern[j] == "]":
                j += 1
            while j < n and pattern[j] != "]":
                j += 1
            if j >= n:
                out.append(r"\[")
            else:
                inner = pattern[i:j]
                i = j + 1
                if inner.startswith("!"):
                    inner = "^" + inner[1:]
                out.append("[" + inner.replace("\\", "\\\\") + "]")
        else:
            out.append(re.escape(c))
    return "".join(out)


class IgnoreMatcher:
    """Apply gitignore-style patterns to project-relative paths."""

    def __init__(self, patterns: list[str]) -> None:
        self._rules: list[tuple[re.Pattern, bool, bool]] = []
        for raw in patterns:
            line = raw.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            negate = False
            if line.startswith("!"):
                negate = True
                line = line[1:]
            elif line.startswith("\\!"):
                line = line[1:]
            dir_only = line.endswith("/")
            if dir_only:
                line = line[:-1]
            anchored = line.startswith("/")
            if anchored:
                line = line[1:]
            if not line:
                continue
            has_slash = "/" in line
            prefix = "^" if (has_slash or anchored) else "(?:^|.*/)"
            regex = prefix + _translate_gitignore_pattern(line) + "$"
            try:
                rx = re.compile(regex)
            except re.error:
                continue
            self._rules.append((rx, negate, dir_only))

    @classmethod
    def from_text(cls, text: str) -> "IgnoreMatcher":
        return cls(text.splitlines())

    @classmethod
    def from_file(cls, path: Path) -> "IgnoreMatcher":
        try:
            return cls(path.read_text(encoding="utf-8").splitlines())
        except OSError:
            return cls([])

    @classmethod
    def merge(cls, *matchers: "IgnoreMatcher | None") -> "IgnoreMatcher":
        m = cls([])
        for other in matchers:
            if other is not None:
                m._rules.extend(other._rules)
        return m

    @property
    def is_empty(self) -> bool:
        return not self._rules

    def match(self, rel_posix: str, is_dir: bool) -> bool:
        if not self._rules:
            return False
        ignored = False
        for rx, negate, dir_only in self._rules:
            if self._matches(rx, dir_only, rel_posix, is_dir):
                ignored = not negate
        return ignored

    @staticmethod
    def _matches(rx: re.Pattern, dir_only: bool,
                 rel_posix: str, is_dir: bool) -> bool:
        if not (dir_only and not is_dir):
            if rx.match(rel_posix):
                return True
        parts = rel_posix.split("/")
        for i in range(1, len(parts)):
            ancestor = "/".join(parts[:i])
            if rx.match(ancestor):
                return True
        return False


def load_ignore_matcher(
    root: Path,
    ignore_file_arg: str | None,
    no_ignore_file: bool,
) -> tuple[IgnoreMatcher, Path | None]:
    matchers: list[IgnoreMatcher] = []
    user_path: Path | None = None

    if not no_ignore_file:
        builtin = root / DEFAULT_IGNORE_FILE
        if builtin.is_file():
            matchers.append(IgnoreMatcher.from_file(builtin))

    if ignore_file_arg:
        p = Path(ignore_file_arg).expanduser()
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.is_file():
            matchers.append(IgnoreMatcher.from_file(p))
            user_path = p
        else:
            print(f"Warning: --ignore-file not found: {p}",
                  file=sys.stderr)

    return IgnoreMatcher.merge(*matchers), user_path


# ============================================================
# Language matcher
# ============================================================

class LangMatcher:
    def __init__(self, langs: list[str]) -> None:
        self.langs = [l.lower() for l in (langs or ["all"])]
        self.include_all = "all" in self.langs or "any" in self.langs
        self.exts: set[str] = set(COMMON_EXTS)
        self.globs: set[str] = set(COMMON_GLOBS)
        if not self.include_all:
            for lang in self.langs:
                if lang not in SOURCE_EXTS and lang != "docker":
                    raise ValueError(f"Unknown language: {lang!r}")
                if lang == "docker":
                    self.globs |= {
                        "dockerfile*", "docker-compose*",
                        "compose*.yml", "compose*.yaml", ".dockerignore",
                    }
                    continue
                self.exts |= SOURCE_EXTS[lang]
                if lang == "python":
                    self.globs |= {
                        "pyproject.toml", "setup.py", "setup.cfg",
                        "tox.ini", "pipfile", ".python-version",
                        "requirements*.txt",
                    }
                elif lang == "javascript":
                    self.globs |= {
                        "package.json", "jsconfig.json", ".babelrc",
                        ".browserslistrc", ".npmrc", ".nvmrc",
                        "vite.config.*", "webpack.config.*",
                        "rollup.config.*", "babel.config.*",
                        ".eslintrc*", ".prettierrc*",
                    }
                elif lang == "typescript":
                    self.globs |= {"tsconfig*.json"}
                elif lang == "go":
                    self.globs |= {"go.mod", "go.work"}
                elif lang == "rust":
                    self.globs |= {"cargo.toml", "rust-toolchain"}

    def matches(self, name: str, ext: str) -> bool:
        if self.include_all:
            return True
        if ext in self.exts:
            return True
        lower = name.lower()
        for pat in self.globs:
            if fnmatch.fnmatch(lower, pat):
                return True
        return False


# ============================================================
# File discovery
# ============================================================

def get_git_files(root: Path) -> list[Path] | None:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "-co",
             "--exclude-standard", "-z"],
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    files: list[Path] = []
    for raw in output.split(b"\0"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8", errors="surrogateescape"))
        p = root / rel
        try:
            if p.is_file():
                files.append(p)
        except OSError:
            continue
    return files


def get_walk_files(
    root: Path,
    ignore: IgnoreMatcher | None = None,
) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        kept: list[str] = []
        for d in dirnames:
            if should_skip_dir(d):
                continue
            if ignore is not None and not ignore.is_empty:
                rel = (Path(dirpath) / d).relative_to(root).as_posix()
                if ignore.match(rel, is_dir=True):
                    continue
            kept.append(d)
        dirnames[:] = kept
        for name in filenames:
            files.append(Path(dirpath) / name)
    return files


def discover(
    root: Path,
    matcher: LangMatcher | None,
    max_size: int,
    extra_includes: list[str],
    extra_excludes: list[str],
    allow_sensitive: bool,
    skip_paths: set[Path],
    use_git: bool,
    strict_lang: bool = True,
    ignore: IgnoreMatcher | None = None,
) -> list[Path]:
    raw = get_git_files(root) if use_git else None
    if raw is None:
        raw = get_walk_files(root, ignore=ignore)

    result: list[Path] = []
    for p in raw:
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        try:
            resolved = p.resolve()
        except OSError:
            continue
        if resolved in skip_paths:
            continue
        if should_skip_path(rel):
            continue

        rel_posix = rel.as_posix()

        if ignore is not None and not ignore.is_empty:
            if ignore.match(rel_posix, is_dir=False):
                continue

        name = rel.name
        if should_skip_file(name):
            continue

        if any(fnmatch.fnmatch(rel_posix, pat)
               or fnmatch.fnmatch(name, pat)
               for pat in extra_excludes):
            continue

        forced = any(fnmatch.fnmatch(rel_posix, pat)
                     or fnmatch.fnmatch(name, pat)
                     for pat in extra_includes)

        if not forced:
            if not allow_sensitive and is_sensitive(name):
                continue
            if strict_lang and matcher is not None:
                if not matcher.matches(name, p.suffix.lower()):
                    continue

        if is_binary(p):
            continue

        try:
            if p.stat().st_size > max_size:
                continue
        except OSError:
            continue

        result.append(p)

    result.sort(key=lambda p: p.relative_to(root).as_posix().lower())
    return result


# ============================================================
# Symbol extraction — data model
# ============================================================

@dataclass
class Symbol:
    kind: str
    name: str
    signature: str = ""
    line: int = 0
    doc: str = ""
    children: list["Symbol"] = field(default_factory=list)


@dataclass
class FileInfo:
    path: str
    lang: str
    size: int
    lines: int
    sha: str
    doc: str = ""
    imports: list[str] = field(default_factory=list)
    symbols: list[Symbol] = field(default_factory=list)


def detect_lang(p: Path) -> str:
    name = p.name.lower()
    ext = p.suffix.lower()
    if name == "dockerfile" or name.startswith("dockerfile."):
        return "docker"
    if name in {"makefile", "gnumakefile"}:
        return "make"
    return EXT_TO_LANG.get(ext, "text")


# ============================================================
# Python — real AST parsing
# ============================================================

def _py_doc(node: ast.AST) -> str:
    d = ast.get_docstring(node) or ""
    return d.split("\n", 1)[0].strip()


def _py_sig(node) -> str:
    parts: list[str] = []
    a = node.args
    posonly = getattr(a, "posonlyargs", [])
    all_args = [*posonly, *a.args]
    for arg in all_args:
        parts.append(arg.arg)
    if a.vararg:
        parts.append("*" + a.vararg.arg)
    elif a.kwonlyargs:
        parts.append("*")
    for arg in a.kwonlyargs:
        parts.append(arg.arg)
    if a.kwarg:
        parts.append("**" + a.kwarg.arg)
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({', '.join(parts)})"


def _py_bases(node: ast.ClassDef) -> list[str]:
    out: list[str] = []
    for b in node.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out


def extract_python(source: str) -> tuple[list[str], list[Symbol], str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], [], ""

    imports: list[str] = []
    symbols: list[Symbol] = []
    module_doc = (ast.get_docstring(tree) or "").split("\n", 1)[0].strip()

    for node in tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for a in node.names:
                imports.append(f"{mod}.{a.name}" if mod else a.name)
        elif isinstance(node, ast.ClassDef):
            methods: list[Symbol] = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(Symbol(
                        kind="method",
                        name=item.name,
                        signature=_py_sig(item),
                        line=item.lineno,
                        doc=_py_doc(item),
                    ))
            bases = _py_bases(node)
            sig = f"class {node.name}"
            if bases:
                sig += f"({', '.join(bases)})"
            symbols.append(Symbol(
                kind="class",
                name=node.name,
                signature=sig,
                line=node.lineno,
                doc=_py_doc(node),
                children=methods,
            ))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(Symbol(
                kind="function",
                name=node.name,
                signature=_py_sig(node),
                line=node.lineno,
                doc=_py_doc(node),
            ))

    return imports, symbols, module_doc


# ============================================================
# Generic extraction — shared helpers
# ============================================================

KEYWORDS = frozenset({
    "if", "elif", "else", "for", "while", "do", "switch", "case",
    "default", "try", "catch", "except", "finally", "with", "as",
    "return", "yield", "throw", "raise", "new", "delete", "typeof",
    "instanceof", "in", "of", "await", "break", "continue", "pass",
    "goto", "assert", "import", "export", "from", "using", "namespace",
    "package", "module", "public", "private", "protected", "internal",
    "static", "final", "abstract", "sealed", "open", "override",
    "virtual", "synchronized", "native", "volatile", "transient",
    "const", "let", "var", "function", "func", "fn", "def", "sub",
    "proc", "method", "class", "interface", "struct", "enum", "trait",
    "record", "union", "typedef", "type", "impl", "extends",
    "implements", "where", "select", "insert", "update", "delete",
    "create", "drop", "alter", "and", "or", "not", "is", "null",
    "nil", "none", "true", "false", "self", "this", "super", "base",
    "void", "int", "float", "double", "char", "bool", "boolean",
    "string", "long", "short", "unsigned", "signed", "auto", "sizeof",
})

LANG_FAMILY: dict[str, str] = {
    "javascript": "js", "typescript": "js", "vue": "js",
    "svelte": "js", "web": "js",
    "java": "c", "csharp": "c", "kotlin": "c", "scala": "c",
    "dart": "c", "swift": "c", "c": "c", "cpp": "c",
    "go": "go",
    "rust": "rust",
    "ruby": "ruby",
    "php": "php",
    "shell": "shell",
}


def _brace_depths(lines: list[str]) -> list[int]:
    depths = [0] * len(lines)
    depth = 0
    for i, line in enumerate(lines):
        depths[i] = depth
        depth += line.count("{") - line.count("}")
    return depths


def _collect_imports_generic(text: str) -> list[str]:
    patterns = [
        re.compile(r'^\s*import\s+[^"\']*["\']([^"\']+)["\']', re.M),
        re.compile(r'^\s*from\s+([\w\.\-/]+)\s+import', re.M),
        re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]', re.M),
        re.compile(r'^\s*use\s+([\w\:]+)', re.M),
        re.compile(r'require\s*\(\s*["\']([^"\']+)["\']', re.M),
        re.compile(r'^\s*import\s+([\w\.\-/]+)\s*;', re.M),
        re.compile(r'^\s*require\s+["\']([^"\']+)["\']', re.M),
    ]
    seen: set[str] = set()
    out: list[str] = []
    for pat in patterns:
        for m in pat.finditer(text):
            name = m.group(1)
            if name not in seen:
                seen.add(name)
                out.append(name)
                if len(out) >= 40:
                    return out
    return out


# --- Regex building blocks ---------------------------------

# Balanced-paren fragment tolerating one level of nesting.
_PAREN_INNER = r"[^()]|\([^()]*\)"
_PAREN = rf"\(((?:{_PAREN_INNER})*)\)"

# Type parameters up to three levels of nesting.
_TPARAM = (
    r"<[^<>]*"
    r"(?:<[^<>]*(?:<[^<>]*>[^<>]*)*>[^<>]*)*"
    r">"
)

# Return type: simple or single-level object literal.
_RETURN = r"(?:[A-Za-z_$\[\]\(\)\.\w\s\|&<>,?:]+|\{[^{}]*\})"


def _shorten_params(params: str, max_len: int = 90) -> str:
    """Collapse a possibly multi-line parameter list to one line."""
    joined = " ".join(params.split())
    if len(joined) > max_len:
        joined = joined[: max_len - 1] + "…"
    return joined


# ============================================================
# JS / TS / Vue / Svelte
# ============================================================

JS_CLASS = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?"
    r"(class|interface)\s+(\w+)"
    r"(?:\s+extends\s+([\w\.]+))?"
)
JS_ENUM = re.compile(r"^\s*(?:export\s+)?(?:const\s+)?enum\s+(\w+)")
JS_TYPE = re.compile(r"^\s*(?:export\s+)?type\s+(\w+)")

JS_FUNCTION = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?"
    r"function\s*\*?\s*(\w+)\s*"
    r"(" + _TPARAM + r")?\s*" + _PAREN +
    r"(?:\s*:\s*(" + _RETURN + r"))?\s*\{"
)

JS_ARROW = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*"
    r"(?::\s*[^=]+?)?\s*=\s*"
    r"(?:async\s+)?"
    r"(" + _TPARAM + r"\s*)?"
    r"(?:" + _PAREN + r"|(\w+))"
    r"(?:\s*:\s*(" + _RETURN + r"))?\s*=>"
)

JS_OBJECT = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*"
    r"(?::\s*[^=]+?)?\s*=\s*\{\s*$",
    re.M,
)

JS_OBJECT_METHOD = re.compile(
    r"^\s*(?:async\s+)?(\w+)\s*:\s*(?:async\s+)?"
    r"(?:" + _TPARAM + r"\s*)?"
    r"(?:" + _PAREN + r"|(\w+))"
    r"(?:\s*:\s*(" + _RETURN + r"))?\s*=>"
)

JS_METHOD = re.compile(
    r"^\s*(?:(?:public|private|protected|static|async|readonly|"
    r"abstract|override|get|set)\s+)*"
    r"(\w+)\s*" + _PAREN +
    r"(?:\s*:\s*(" + _RETURN + r"))?\s*\{"
)


def _extract_js(text: str) -> tuple[list[str], list[Symbol], str]:
    """Extract JS / TS / Vue / Svelte symbols."""
    imports = _collect_imports_generic(text)
    lines = text.splitlines()
    symbols: list[Symbol] = []
    scope_stack: list[tuple[int, Symbol]] = []

    WINDOW = 40
    depth = 0
    i = 0
    n = len(lines)

    while i < n:
        while scope_stack and scope_stack[-1][0] >= depth:
            scope_stack.pop()

        line = lines[i]
        stripped = line.strip()

        if (not stripped
                or stripped.startswith("//")
                or stripped.startswith("*")
                or stripped.startswith("/*")):
            depth += line.count("{") - line.count("}")
            i += 1
            continue

        window = "\n".join(lines[i:min(i + WINDOW, n)])
        in_object = bool(scope_stack
                         and scope_stack[-1][1].kind == "object")

        sym: Symbol | None = None
        consumed = 0
        opens_body = False

        # 1) class / interface
        m = JS_CLASS.match(window)
        if m:
            kind, name = m.group(1), m.group(2)
            sig = f"{kind} {name}"
            if m.group(3):
                sig += f" extends {m.group(3)}"
            sym = Symbol(kind=kind, name=name, signature=sig, line=i + 1)
            consumed = m.group(0).count("\n") + 1
            opens_body = True

        # 2) enum
        if sym is None:
            m = JS_ENUM.match(window)
            if m:
                sym = Symbol(kind="enum", name=m.group(1),
                             signature=f"enum {m.group(1)}", line=i + 1)
                consumed = m.group(0).count("\n") + 1
                opens_body = "{" in m.group(0)

        # 3) type alias
        if sym is None:
            m = JS_TYPE.match(window)
            if m:
                sym = Symbol(kind="type", name=m.group(1),
                             signature=f"type {m.group(1)}", line=i + 1)
                consumed = m.group(0).count("\n") + 1

        # 4) object literal (top-level only)
        if sym is None and not scope_stack:
            m = JS_OBJECT.match(window)
            if m:
                name = m.group(1)
                sym = Symbol(kind="object", name=name,
                             signature=f"object {name}",
                             line=i + 1)
                consumed = m.group(0).count("\n") + 1
                opens_body = True

        # 5) function declaration
        if sym is None:
            m = JS_FUNCTION.match(window)
            if m and m.group(1) not in KEYWORDS:
                name = m.group(1)
                tparam = (m.group(2) or "").strip()
                params = m.group(3)
                ret = m.group(4)
                sig = f"function {name}{tparam}({_shorten_params(params)})"
                if ret:
                    sig += f": {_shorten_params(ret, max_len=60)}"
                sym = Symbol(kind="function", name=name,
                             signature=sig, line=i + 1)
                consumed = m.group(0).count("\n") + 1
                opens_body = True

        # 6) object method
        if sym is None and in_object:
            m = JS_OBJECT_METHOD.match(window)
            if m and m.group(1) not in KEYWORDS:
                name = m.group(1)
                params = m.group(2) or m.group(3) or ""
                ret = m.group(4)
                sig = f"{name}({_shorten_params(params)})"
                if ret:
                    sig += f": {_shorten_params(ret, max_len=60)}"
                sym = Symbol(kind="method", name=name,
                             signature=sig, line=i + 1)
                consumed = m.group(0).count("\n") + 1
                after_arrow = window[m.end():].lstrip()
                opens_body = after_arrow.startswith("{")

        # 7) arrow function
        if sym is None:
            m = JS_ARROW.match(window)
            if m and m.group(1) not in KEYWORDS:
                name = m.group(1)
                tparam = (m.group(2) or "").strip()
                params = m.group(3) or m.group(4) or ""
                ret = m.group(5)
                sig = f"function {name}{tparam}({_shorten_params(params)})"
                if ret:
                    sig += f": {_shorten_params(ret, max_len=60)}"
                sym = Symbol(kind="function", name=name,
                             signature=sig, line=i + 1)
                consumed = m.group(0).count("\n") + 1
                after_arrow = window[m.end():].lstrip()
                opens_body = after_arrow.startswith("{")

        # 8) method inside class / interface
        if sym is None and scope_stack:
            if scope_stack[-1][1].kind in ("class", "interface"):
                m = JS_METHOD.match(window)
                if m and m.group(1) not in KEYWORDS:
                    name = m.group(1)
                    params = m.group(2)
                    ret = m.group(3)
                    sig = f"{name}({_shorten_params(params)})"
                    if ret:
                        sig += f": {_shorten_params(ret, max_len=60)}"
                    sym = Symbol(kind="method", name=name,
                                 signature=sig, line=i + 1)
                    consumed = m.group(0).count("\n") + 1
                    opens_body = True

        if sym is not None:
            parent = scope_stack[-1][1] if scope_stack else None
            (parent.children if parent else symbols).append(sym)
            if opens_body:
                scope_stack.append((depth, sym))
            for k in range(i, min(i + consumed, n)):
                depth += lines[k].count("{") - lines[k].count("}")
            i += consumed
            continue

        depth += line.count("{") - line.count("}")
        i += 1

    return imports, symbols, ""


# ============================================================
# C-family
# ============================================================

C_CLASS = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|final|"
    r"abstract|sealed|open|data|partial|export|inline)\s+)*"
    r"(class|interface|enum|struct|record|trait|object)\s+(\w+)"
)
C_METHOD = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|final|"
    r"abstract|sealed|open|override|virtual|async|synchronized|"
    r"native|constexpr|inline|extern|export|readonly|unsafe)\s+)*"
    r"(?:[\w:<>,\[\]\*&\?\.]+\s+)*"
    r"(\w+)\s*" + _PAREN + r"\s*"
    r"(?:const\s*)?(?::\s*[^;{]+?)?\s*"
    r"(?:\{|;|=>)"
)


def _extract_c_family(text: str) -> tuple[list[str], list[Symbol], str]:
    imports = _collect_imports_generic(text)
    lines = text.splitlines()
    depths = _brace_depths(lines)
    symbols: list[Symbol] = []
    class_stack: list[tuple[int, Symbol]] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if (not stripped or stripped.startswith("//")
                or stripped.startswith("*") or stripped.startswith("#")):
            continue

        depth = depths[i]
        while class_stack and class_stack[-1][0] > depth:
            class_stack.pop()

        m = C_CLASS.match(line)
        if m:
            kind, name = m.group(1), m.group(2)
            sym = Symbol(kind=kind, name=name,
                         signature=f"{kind} {name}", line=i + 1)
            symbols.append(sym)
            class_stack.append((depth, sym))
            continue

        m = C_METHOD.match(line)
        if m and m.group(1) not in KEYWORDS:
            name, params = m.group(1), m.group(2)
            sym = Symbol(kind="method" if class_stack else "function",
                         name=name,
                         signature=f"{name}({_shorten_params(params)})",
                         line=i + 1)
            (class_stack[-1][1].children if class_stack
             else symbols).append(sym)
            continue

    return imports, symbols, ""


# ============================================================
# Go
# ============================================================

GO_TYPE = re.compile(r"^\s*type\s+(\w+)\s+(struct|interface)\b")
GO_ALIAS = re.compile(r"^\s*type\s+(\w+)\s*=")
GO_METHOD = re.compile(
    r"^\s*func\s+\(\s*\w+\s+\*?(\w+)\s*\)\s*(\w+)\s*" + _PAREN
)
GO_FUNC = re.compile(r"^\s*func\s+(\w+)\s*" + _PAREN)


def _extract_go(text: str) -> tuple[list[str], list[Symbol], str]:
    imports = _collect_imports_generic(text)
    lines = text.splitlines()
    depths = _brace_depths(lines)
    symbols: list[Symbol] = []
    struct_by_name: dict[str, Symbol] = {}
    struct_stack: list[tuple[int, Symbol]] = []

    for i, line in enumerate(lines):
        depth = depths[i]
        while struct_stack and struct_stack[-1][0] > depth:
            struct_stack.pop()

        m = GO_TYPE.match(line)
        if m:
            name, kind = m.group(1), m.group(2)
            sym = Symbol(kind=kind, name=name,
                         signature=f"{kind} {name}", line=i + 1)
            symbols.append(sym)
            struct_by_name[name] = sym
            struct_stack.append((depth, sym))
            continue

        m = GO_ALIAS.match(line)
        if m:
            symbols.append(Symbol(kind="type", name=m.group(1),
                                  signature=f"type {m.group(1)}",
                                  line=i + 1))
            continue

        m = GO_METHOD.match(line)
        if m:
            recv_type, name, params = m.group(1), m.group(2), m.group(3)
            sym = Symbol(kind="method", name=name,
                         signature=f"{name}({_shorten_params(params)})",
                         line=i + 1)
            target = struct_by_name.get(recv_type)
            if target is not None:
                target.children.append(sym)
            else:
                symbols.append(sym)
            continue

        m = GO_FUNC.match(line)
        if m:
            name, params = m.group(1), m.group(2)
            symbols.append(Symbol(
                kind="function", name=name,
                signature=f"{name}({_shorten_params(params)})",
                line=i + 1,
            ))
            continue

    return imports, symbols, ""


# ============================================================
# Rust
# ============================================================

RUST_TYPE = re.compile(
    r"^\s*(?:pub(?:\([^)]*\))?\s+)?"
    r"(struct|enum|trait|union)\s+(\w+)"
)
RUST_IMPL = re.compile(r"^\s*impl(?:<[^>]*>)?\s+(\w+)")
RUST_FN = re.compile(
    r"^\s*(?:pub(?:\([^)]*\))?\s+)?"
    r"(?:async\s+)?(?:unsafe\s+)?(?:const\s+)?"
    r"fn\s+(\w+)\s*" + _PAREN +
    r"(?:\s*->\s*([^{;]+?))?\s*(?:\{|;)"
)


def _extract_rust(text: str) -> tuple[list[str], list[Symbol], str]:
    imports = _collect_imports_generic(text)
    lines = text.splitlines()
    depths = _brace_depths(lines)
    symbols: list[Symbol] = []
    impl_stack: list[tuple[int, Symbol]] = []
    type_by_name: dict[str, Symbol] = {}

    for i, line in enumerate(lines):
        depth = depths[i]
        while impl_stack and impl_stack[-1][0] > depth:
            impl_stack.pop()

        m = RUST_TYPE.match(line)
        if m:
            kind, name = m.group(1), m.group(2)
            sym = Symbol(kind=kind, name=name,
                         signature=f"{kind} {name}", line=i + 1)
            symbols.append(sym)
            type_by_name[name] = sym
            continue

        m = RUST_IMPL.match(line)
        if m:
            target = type_by_name.get(m.group(1))
            if target is None:
                target = Symbol(kind="impl", name=m.group(1),
                                signature=f"impl {m.group(1)}",
                                line=i + 1)
                symbols.append(target)
            impl_stack.append((depth, target))
            continue

        m = RUST_FN.match(line)
        if m:
            name, params, ret = m.group(1), m.group(2), m.group(3)
            sig = f"{name}({_shorten_params(params)})"
            if ret:
                sig += f" -> {ret.strip()}"
            sym = Symbol(kind="function", name=name,
                         signature=sig, line=i + 1)
            (impl_stack[-1][1].children if impl_stack
             else symbols).append(sym)
            continue

    return imports, symbols, ""


# ============================================================
# Ruby
# ============================================================

RUBY_CLASS = re.compile(r"^\s*(?:class|module)\s+(\w+)")
RUBY_DEF = re.compile(r"^\s*def\s+(\w+[?!]?)\s*(?:" + _PAREN + r")?")


def _extract_ruby(text: str) -> tuple[list[str], list[Symbol], str]:
    imports = _collect_imports_generic(text)
    lines = text.splitlines()
    symbols: list[Symbol] = []
    class_stack: list[tuple[int, Symbol]] = []

    for i, line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        while class_stack and class_stack[-1][0] >= indent:
            class_stack.pop()

        m = RUBY_CLASS.match(line)
        if m:
            name = m.group(1)
            sym = Symbol(kind="class", name=name,
                         signature=f"class {name}", line=i + 1)
            symbols.append(sym)
            class_stack.append((indent, sym))
            continue

        m = RUBY_DEF.match(line)
        if m:
            name = m.group(1)
            params = m.group(2) or ""
            sym = Symbol(kind="method" if class_stack else "function",
                         name=name,
                         signature=f"{name}({_shorten_params(params)})",
                         line=i + 1)
            (class_stack[-1][1].children if class_stack
             else symbols).append(sym)
            continue

    return imports, symbols, ""


# ============================================================
# PHP
# ============================================================

PHP_CLASS = re.compile(
    r"^\s*(?:abstract\s+|final\s+)?(class|interface|trait|enum)\s+(\w+)"
)
PHP_FUNC = re.compile(
    r"^\s*(?:(?:public|private|protected|static|final|abstract)\s+)*"
    r"function\s+(\w+)\s*" + _PAREN
)


def _extract_php(text: str) -> tuple[list[str], list[Symbol], str]:
    imports = _collect_imports_generic(text)
    lines = text.splitlines()
    depths = _brace_depths(lines)
    symbols: list[Symbol] = []
    class_stack: list[tuple[int, Symbol]] = []

    for i, line in enumerate(lines):
        depth = depths[i]
        while class_stack and class_stack[-1][0] > depth:
            class_stack.pop()

        m = PHP_CLASS.match(line)
        if m:
            kind, name = m.group(1), m.group(2)
            sym = Symbol(kind=kind, name=name,
                         signature=f"{kind} {name}", line=i + 1)
            symbols.append(sym)
            class_stack.append((depth, sym))
            continue

        m = PHP_FUNC.match(line)
        if m:
            name, params = m.group(1), m.group(2)
            sym = Symbol(kind="method" if class_stack else "function",
                         name=name,
                         signature=f"{name}({_shorten_params(params)})",
                         line=i + 1)
            (class_stack[-1][1].children if class_stack
             else symbols).append(sym)
            continue

    return imports, symbols, ""


# ============================================================
# Dispatcher
# ============================================================

def extract_generic(text: str, lang: str) -> tuple[list[str], list[Symbol], str]:
    family = LANG_FAMILY.get(lang)
    if family == "js":
        return _extract_js(text)
    if family == "c":
        return _extract_c_family(text)
    if family == "go":
        return _extract_go(text)
    if family == "rust":
        return _extract_rust(text)
    if family == "ruby":
        return _extract_ruby(text)
    if family == "php":
        return _extract_php(text)
    return _collect_imports_generic(text), [], ""


def extract_file_info(root: Path, p: Path) -> FileInfo | None:
    try:
        raw = p.read_bytes()
    except OSError:
        return None

    text = raw.decode("utf-8", errors="replace")
    rel = p.relative_to(root).as_posix()
    lang = detect_lang(p)
    sha = hashlib.sha1(raw).hexdigest()[:8]
    lines = text.count("\n") + 1

    if lang == "python":
        imports, symbols, doc = extract_python(text)
    elif lang in OPAQUE_LANGS or lang in {"docker", "make", "text"}:
        imports, symbols, doc = [], [], ""
    else:
        imports, symbols, doc = extract_generic(text, lang)

    return FileInfo(
        path=rel, lang=lang, size=len(raw), lines=lines, sha=sha,
        doc=doc, imports=imports, symbols=symbols,
    )


# ============================================================
# Manifest formatting
# ============================================================

def _symbol_to_text(s: Symbol, indent: str = "  ") -> list[str]:
    out: list[str] = []
    doc = f"  # {s.doc}" if s.doc else ""
    if s.children:
        head = s.signature or f"{s.kind} {s.name}"
        out.append(f"{indent}{head}{doc}")
        for c in s.children:
            csig = c.signature or c.name
            cdoc = f"  # {c.doc}" if c.doc else ""
            out.append(f"{indent}  . {csig}{cdoc}")
    else:
        sig = s.signature or f"{s.kind} {s.name}"
        out.append(f"{indent}{sig}{doc}")
    return out


def manifest_text(
    root: Path,
    infos: list[FileInfo],
    langs: list[str],
    show_symbols: bool = True,
    show_imports: bool = True,
) -> str:
    lines: list[str] = [
        "# Project Manifest",
        f"# Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"# Root: {root}",
        f"# Languages: {', '.join(langs)}",
        f"# Files: {len(infos)}",
        "# " + "-" * 60,
        "",
    ]
    for fi in infos:
        header = (
            f"=== {fi.path}  "
            f"[{fi.lang} {fi.lines}L {human_size(fi.size)} sha={fi.sha}] ==="
        )
        lines.append(header)
        if fi.doc:
            lines.append(f"  doc: {fi.doc}")
        if show_imports and fi.imports:
            imp = ", ".join(fi.imports[:20])
            if len(fi.imports) > 20:
                imp += f", …(+{len(fi.imports)-20})"
            lines.append(f"  imports: {imp}")
        if show_symbols and fi.symbols:
            for s in fi.symbols:
                lines.extend(_symbol_to_text(s))
        lines.append("")
    return "\n".join(lines)


def manifest_md(
    root: Path,
    infos: list[FileInfo],
    langs: list[str],
    show_symbols: bool = True,
    show_imports: bool = True,
) -> str:
    out: list[str] = [
        "# Project Manifest",
        "",
        f"- **Root:** `{root}`",
        f"- **Languages:** {', '.join(langs)}",
        f"- **Files:** {len(infos)}",
        f"- **Generated:** {datetime.now().isoformat(timespec='seconds')}",
        "",
        "---",
        "",
    ]
    for fi in infos:
        out.append(f"### `{fi.path}`")
        out.append(
            f"*{fi.lang} — {fi.lines} lines, {human_size(fi.size)}, "
            f"sha=`{fi.sha}`*"
        )
        if fi.doc:
            out.append(f"> {fi.doc}")
        if show_imports and fi.imports:
            out.append("")
            out.append("**Imports:** " +
                       ", ".join(f"`{i}`" for i in fi.imports[:30]))
        if show_symbols and fi.symbols:
            out.append("")
            out.append("**Symbols:**")
            for s in fi.symbols:
                if s.children:
                    sig = s.signature or f"{s.kind} {s.name}"
                    out.append(f"- `{sig}`")
                    for c in s.children:
                        out.append(f"  - `{c.signature or c.name}`")
                else:
                    out.append(f"- `{s.signature or s.name}`")
        out.append("")
    return "\n".join(out)


def manifest_json(
    root: Path,
    infos: list[FileInfo],
    langs: list[str],
    show_symbols: bool = True,
    show_imports: bool = True,
) -> str:
    def sym_to_dict(s: Symbol) -> dict:
        d = {"kind": s.kind, "name": s.name, "line": s.line}
        if s.signature:
            d["signature"] = s.signature
        if s.doc:
            d["doc"] = s.doc
        if s.children:
            d["children"] = [sym_to_dict(c) for c in s.children]
        return d

    data = {
        "root": str(root),
        "generated": datetime.now().isoformat(timespec="seconds"),
        "languages": langs,
        "file_count": len(infos),
        "files": [],
    }
    for fi in infos:
        entry: dict = {
            "path": fi.path,
            "lang": fi.lang,
            "lines": fi.lines,
            "size": fi.size,
            "sha": fi.sha,
        }
        if fi.doc:
            entry["doc"] = fi.doc
        if show_imports and fi.imports:
            entry["imports"] = fi.imports
        if show_symbols and fi.symbols:
            entry["symbols"] = [sym_to_dict(s) for s in fi.symbols]
        data["files"].append(entry)
    return json.dumps(data, ensure_ascii=False, indent=2)


# ============================================================
# State (diff mode)
# ============================================================

def _ignore_signature(root: Path) -> str:
    p = root / DEFAULT_IGNORE_FILE
    if not p.is_file():
        return ""
    try:
        return hashlib.sha1(p.read_bytes()).hexdigest()[:12]
    except OSError:
        return ""


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict) or data.get("version") != STATE_VERSION:
        return {}
    if not isinstance(data.get("files"), dict):
        return {}
    return data


def save_state(path: Path, root: Path, files: dict) -> None:
    data = {
        "version": STATE_VERSION,
        "updated": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "ignore_sig": _ignore_signature(root),
        "files": files,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8", newline="\n",
        )
        tmp.replace(path)
    except OSError as e:
        print(f"Warning: could not save state to {path}: {e}",
              file=sys.stderr)


def compute_delta(
    root: Path,
    files: list[Path],
    old_files: dict,
) -> tuple[list[Path], dict, list[str]]:
    changed: list[Path] = []
    new_map: dict[str, dict] = {}
    current_rels: set[str] = set()

    for p in files:
        rel = p.relative_to(root).as_posix()
        current_rels.add(rel)
        try:
            st = p.stat()
        except OSError:
            continue

        prev = old_files.get(rel)
        if (prev
                and prev.get("size") == st.st_size
                and abs(float(prev.get("mtime", 0.0)) - st.st_mtime) < 1e-6):
            new_map[rel] = prev
            continue

        try:
            h = file_sha(p)
        except OSError:
            continue

        new_map[rel] = {"hash": h, "size": st.st_size, "mtime": st.st_mtime}
        if prev is None or prev.get("hash") != h:
            changed.append(p)

    deleted: list[str] = []
    for rel, entry in old_files.items():
        if rel in current_rels:
            continue
        if (root / rel).exists():
            new_map[rel] = entry
        else:
            deleted.append(rel)

    deleted.sort()
    return changed, new_map, deleted


# ============================================================
# Bundle writer (fetch + diff)
# ============================================================

def write_bundle(
    out_path: Path,
    root: Path,
    files: list[Path],
    langs: list[str],
    mode: str,
    deleted: list[str] | None = None,
    no_header: bool = False,
) -> tuple[int, int]:
    written = 0
    total_bytes = 0

    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        if not no_header:
            lines = [
                "# Project Source Bundle",
                f"# Mode: {mode}",
                f"# Generated: {datetime.now().isoformat(timespec='seconds')}",
                f"# Root: {root}",
                f"# Languages: {', '.join(langs)}",
                f"# Files: {len(files)}",
            ]
            if deleted:
                lines.append(f"# Deleted: {len(deleted)}")
                for rel in deleted:
                    lines.append(f"#   - {rel}")
            lines += ["# " + "-" * 60, "", ""]
            header = "\n".join(lines)
            out.write(header)
            total_bytes += len(header.encode("utf-8"))
        elif deleted:
            mini = "# deleted: " + ", ".join(deleted) + "\n\n"
            out.write(mini)
            total_bytes += len(mini.encode("utf-8"))

        for p in files:
            try:
                rel = p.relative_to(root).as_posix()
            except ValueError:
                rel = p.as_posix()
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                print(f"  ! skip {rel}: {e}", file=sys.stderr)
                continue
            block = f"=== {rel} ===\n{text}\n\n"
            out.write(block)
            total_bytes += len(block.encode("utf-8"))
            written += 1

    return written, total_bytes


# ============================================================
# Resolve root / paths / langs / ignore
# ============================================================

def resolve_root(args) -> tuple[Path, bool]:
    cwd = Path.cwd()
    if args.root:
        root = Path(args.root).expanduser().resolve()
        if not root.is_dir():
            raise SystemExit(f"Error: --root is not a directory: {root}")
        use_git = (not args.no_git) and (root / ".git").exists()
        return root, use_git
    git_root = find_git_root(cwd)
    root = git_root or cwd
    use_git = (git_root is not None) and not args.no_git
    return root, use_git


def resolve_output(arg_output: str | None, default_name: str) -> Path:
    cwd = Path.cwd()
    p = Path(arg_output).expanduser() if arg_output else Path(default_name)
    if not p.is_absolute():
        p = cwd / p
    return p


def normalize_langs(raw: list[str] | None) -> list[str]:
    if not raw:
        return ["all"]
    out: list[str] = []
    for item in raw:
        for part in item.replace(",", " ").split():
            part = part.strip().lower()
            if part:
                out.append(part)
    if not out or "all" in out or "any" in out:
        return ["all"]
    seen: set[str] = set()
    unique: list[str] = []
    for l in out:
        if l not in seen:
            seen.add(l)
            unique.append(l)
    return unique


def make_matcher(langs_raw: list[str] | None) -> LangMatcher:
    langs = normalize_langs(langs_raw)
    return LangMatcher(langs)


def _setup_ignore_and_skip(
    root: Path,
    args,
    base_skip: set[Path],
) -> tuple[IgnoreMatcher, set[Path], Path | None]:
    ignore, user_ignore_path = load_ignore_matcher(
        root, args.ignore_file, args.no_ignore_file,
    )
    skip = set(base_skip)
    skip.add((root / DEFAULT_IGNORE_FILE).resolve())
    if user_ignore_path:
        skip.add(user_ignore_path.resolve())
    return ignore, skip, user_ignore_path


# ============================================================
# Commands
# ============================================================

def cmd_manifest(args) -> int:
    root, use_git = resolve_root(args)
    matcher = make_matcher(args.lang)

    out_path = resolve_output(args.output, DEFAULT_MANIFEST_OUT)
    self_path = Path(__file__).resolve()

    ignore, skip, _ = _setup_ignore_and_skip(
        root, args, base_skip={self_path, out_path.resolve()},
    )

    files = discover(
        root=root,
        matcher=matcher,
        max_size=int(args.max_size * 1024 * 1024),
        extra_includes=args.include or [],
        extra_excludes=args.exclude or [],
        allow_sensitive=args.allow_sensitive,
        skip_paths=skip,
        use_git=use_git,
        strict_lang=not args.all_files,
        ignore=ignore,
    )

    if not files:
        print("No source files found.", file=sys.stderr)
        return 1

    infos: list[FileInfo] = []
    for p in files:
        info = extract_file_info(root, p)
        if info is not None:
            infos.append(info)

    fmt = args.format
    if fmt == "json":
        text = manifest_json(root, infos, matcher.langs,
                             not args.no_symbols, not args.no_imports)
    elif fmt == "md":
        text = manifest_md(root, infos, matcher.langs,
                           not args.no_symbols, not args.no_imports)
    else:
        text = manifest_text(root, infos, matcher.langs,
                             not args.no_symbols, not args.no_imports)

    tokens = estimate_tokens(text)
    if args.max_tokens and tokens > args.max_tokens and not args.no_symbols:
        if fmt == "json":
            text = manifest_json(root, infos, matcher.langs, False, True)
        elif fmt == "md":
            text = manifest_md(root, infos, matcher.langs, False, True)
        else:
            text = manifest_text(root, infos, matcher.langs, False, True)
        tokens = estimate_tokens(text)
        if not args.quiet:
            print("Note: symbols dropped to fit --max-tokens.",
                  file=sys.stderr)

    if args.max_tokens and tokens > args.max_tokens and not args.quiet:
        print(f"Warning: manifest is ~{tokens} tokens, "
              f"over budget {args.max_tokens}.", file=sys.stderr)

    out_path.write_text(text, encoding="utf-8", newline="\n")

    if not args.quiet:
        print(f"Wrote manifest of {len(infos)} file(s) to {out_path} "
              f"(~{tokens} tokens, {human_size(len(text.encode('utf-8')))})")
    return 0


def cmd_fetch(args) -> int:
    root, use_git = resolve_root(args)
    matcher = make_matcher(args.lang)

    out_path = resolve_output(args.output, DEFAULT_BUNDLE_OUT)
    self_path = Path(__file__).resolve()

    _, skip, _ = _setup_ignore_and_skip(
        root, args, base_skip={self_path, out_path.resolve()},
    )

    requested: list[str] = list(args.files or [])

    if args.files_from:
        try:
            for line in Path(args.files_from).read_text(
                encoding="utf-8"
            ).splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    requested.append(line)
        except OSError as e:
            print(f"Error reading --files-from: {e}", file=sys.stderr)
            return 2

    if args.from_stdin:
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):
                requested.append(line)

    seen: set[str] = set()
    requested = [r for r in requested if not (r in seen or seen.add(r))]

    if not requested:
        print("No files requested. Pass paths, --files-from, or --from-stdin.",
              file=sys.stderr)
        return 2

    selected: list[Path] = []
    missing: list[str] = []
    skipped_binary: list[str] = []
    skipped_self: list[str] = []

    for raw in requested:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = root / p
        try:
            rp = p.resolve()
        except OSError:
            missing.append(raw)
            continue
        if rp in skip:
            skipped_self.append(raw)
            continue
        if not p.is_file():
            missing.append(raw)
            continue
        if is_binary(p):
            skipped_binary.append(raw)
            continue
        selected.append(p)

    if not selected:
        print("No valid files to merge.", file=sys.stderr)
        if missing:
            print(f"Missing: {', '.join(missing[:10])}", file=sys.stderr)
        return 1

    if not args.quiet:
        for m in missing:
            print(f"  ! missing: {m}", file=sys.stderr)
        for m in skipped_binary:
            print(f"  ! binary skipped: {m}", file=sys.stderr)
        for m in skipped_self:
            print(f"  ! skipped (self/output): {m}", file=sys.stderr)

    try:
        written, total_bytes = write_bundle(
            out_path=out_path,
            root=root,
            files=selected,
            langs=matcher.langs,
            mode="fetch",
            no_header=args.no_header,
        )
    except OSError as e:
        print(f"Error writing {out_path}: {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"[fetch] Wrote {written} file(s) "
              f"({human_size(total_bytes)}) to {out_path}")
    return 0


def cmd_diff(args) -> int:
    root, use_git = resolve_root(args)
    matcher = make_matcher(args.lang)

    out_path = resolve_output(args.output, DEFAULT_BUNDLE_OUT)
    state_path = (
        Path(args.state_file).expanduser() if args.state_file
        else out_path.with_suffix(".state.json")
    )
    if not state_path.is_absolute():
        state_path = Path.cwd() / state_path

    if args.reset_state and state_path.exists():
        try:
            state_path.unlink()
            if not args.quiet:
                print(f"Reset state: {state_path}")
        except OSError as e:
            print(f"Warning: could not delete state: {e}",
                  file=sys.stderr)

    self_path = Path(__file__).resolve()

    ignore, skip, _ = _setup_ignore_and_skip(
        root, args,
        base_skip={self_path, out_path.resolve(), state_path.resolve()},
    )

    files = discover(
        root=root,
        matcher=matcher,
        max_size=int(args.max_size * 1024 * 1024),
        extra_includes=args.include or [],
        extra_excludes=args.exclude or [],
        allow_sensitive=args.allow_sensitive,
        skip_paths=skip,
        use_git=use_git,
        strict_lang=not args.all_files,
        ignore=ignore,
    )

    if not files:
        print("No source files found.", file=sys.stderr)
        return 1

    old_state = {} if args.full else load_state(state_path)
    old_files = old_state.get("files", {}) if old_state else {}

    if old_state.get("root") and old_state["root"] != str(root):
        if not args.quiet:
            print(f"Warning: root changed "
                  f"({old_state['root']} -> {root}); starting fresh.",
                  file=sys.stderr)
        old_files = {}

    if (old_state.get("ignore_sig")
            and old_state["ignore_sig"] != _ignore_signature(root)):
        if not args.quiet:
            print("Ignore file changed; forcing full merge.",
                  file=sys.stderr)
        old_files = {}

    changed, new_map, deleted = compute_delta(root, files, old_files)
    mode = "full" if not old_files else "delta"

    if args.dry_run:
        label = "Would merge" if mode == "full" else "Would merge (changes)"
        print(f"[{mode}] {label} {len(changed)} file(s) into {out_path}:")
        total = 0
        for p in changed:
            try:
                size = p.stat().st_size
            except OSError:
                size = 0
            total += size
            print(f"  {p.relative_to(root).as_posix()}  ({size:,} bytes)")
        if deleted:
            print(f"Deleted since last run: {len(deleted)}")
            for rel in deleted:
                print(f"  - {rel}")
        print(f"Total changed size: {total:,} bytes")
        return 0

    if mode == "delta" and not changed and not deleted:
        if not args.quiet:
            print("No changes since last run.")
        save_state(state_path, root, new_map)
        return 0

    try:
        written, total_bytes = write_bundle(
            out_path=out_path,
            root=root,
            files=changed,
            langs=matcher.langs,
            mode=mode,
            deleted=deleted,
            no_header=args.no_header,
        )
    except OSError as e:
        print(f"Error writing {out_path}: {e}", file=sys.stderr)
        return 1

    save_state(state_path, root, new_map)

    if not args.quiet:
        print(f"[{mode}] Wrote {written} file(s) "
              f"({human_size(total_bytes)}) to {out_path}")
        if deleted:
            print(f"       Deleted: {len(deleted)} file(s)")
        print(f"       State:   {state_path}")
    return 0


def cmd_search(args) -> int:
    root, use_git = resolve_root(args)
    matcher = make_matcher(args.lang)

    self_path = Path(__file__).resolve()

    ignore, skip, _ = _setup_ignore_and_skip(
        root, args, base_skip={self_path},
    )

    files = discover(
        root=root,
        matcher=matcher,
        max_size=int(args.max_size * 1024 * 1024),
        extra_includes=args.include or [],
        extra_excludes=args.exclude or [],
        allow_sensitive=args.allow_sensitive,
        skip_paths=skip,
        use_git=use_git,
        strict_lang=not args.all_files,
        ignore=ignore,
    )

    pattern = args.symbol
    try:
        rx = re.compile(pattern)
    except re.error:
        rx = re.compile(re.escape(pattern))

    hits = 0
    out_lines: list[str] = []
    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = p.relative_to(root).as_posix()
        for i, line in enumerate(text.splitlines(), start=1):
            if rx.search(line):
                hits += 1
                out_lines.append(f"{rel}:{i}: {line.strip()}")
                if hits >= args.max_hits:
                    break
        if hits >= args.max_hits:
            break

    if args.output:
        Path(args.output).write_text(
            "\n".join(out_lines) + "\n", encoding="utf-8", newline="\n",
        )
        if not args.quiet:
            print(f"Wrote {hits} hit(s) to {args.output}")
    else:
        for line in out_lines:
            print(line)
        if not args.quiet:
            print(f"--- {hits} hit(s) ---", file=sys.stderr)

    return 0


def cmd_langs(_args) -> int:
    print("Supported languages:")
    for name in sorted(SOURCE_EXTS):
        print(f"  {name}")
    print("  docker  (Dockerfile, docker-compose.yml, ...)")
    print("  all     (everything)")
    return 0


# ============================================================
# CLI
# ============================================================

def add_common(parser: argparse.ArgumentParser, *, output_default: str) -> None:
    # --cd must come first so users see it prominently in --help.
    parser.add_argument(
        "-C", "--cd",
        default=None,
        metavar="DIR",
        help="Change working directory to DIR before running. "
             "All input, output, ignore, and state paths are resolved "
             "against DIR, and Git detection uses DIR as the starting "
             "point. Useful when running codemerge.py from a different "
             "location than the project (like `git -C`).",
    )
    parser.add_argument("-l", "--lang", nargs="+", action="extend",
                        default=None, metavar="LANG",
                        help="Language(s). Default: all.")
    parser.add_argument("-o", "--output", default=None,
                        help=f"Output file (default: {output_default}).")
    parser.add_argument("-r", "--root", default=None,
                        help="Project root (default: cwd or Git root).")
    parser.add_argument("--max-size", type=float,
                        default=DEFAULT_MAX_SIZE_MB, metavar="MB",
                        help=f"Max size per file in MB "
                             f"(default: {DEFAULT_MAX_SIZE_MB}).")
    parser.add_argument("--no-git", action="store_true",
                        help="Ignore Git and walk the filesystem.")
    parser.add_argument("--include", nargs="+", action="extend",
                        default=None, metavar="PATTERN",
                        help="Extra glob patterns to force-include.")
    parser.add_argument("--exclude", nargs="+", action="extend",
                        default=None, metavar="PATTERN",
                        help="Extra glob patterns to exclude.")
    parser.add_argument("--allow-sensitive", action="store_true",
                        help="Include .env, keys, certificates, etc.")
    parser.add_argument("--all-files", action="store_true",
                        help="Ignore the language filter and include every "
                             "text file.")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress the final summary.")
    parser.add_argument("--no-header", action="store_true",
                        help="Do not add the metadata header.")
    parser.add_argument("--ignore-file", default=None, metavar="PATH",
                        help=f"Custom ignore file with gitignore-style "
                             f"patterns (default: {DEFAULT_IGNORE_FILE} "
                             f"in project root, if present).")
    parser.add_argument("--no-ignore-file", action="store_true",
                        help="Do not read any ignore file "
                             "(.codemergeignore or --ignore-file).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codemerge.py",
        description="Manifest / Fetch / Diff / Search for LLM-friendly "
                    "project bundling.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # --- manifest ---
    p_man = sub.add_parser("manifest",
                           help="Build a compact map of the project.")
    add_common(p_man, output_default=DEFAULT_MANIFEST_OUT)
    p_man.add_argument("--format", choices=("text", "md", "json"),
                       default="text",
                       help="Output format (default: text).")
    p_man.add_argument("--no-symbols", action="store_true",
                       help="Only list files, no functions/classes.")
    p_man.add_argument("--no-imports", action="store_true",
                       help="Do not list imports.")
    p_man.add_argument("--max-tokens", type=int, default=None, metavar="N",
                       help="Soft limit on manifest token count.")
    p_man.set_defaults(func=cmd_manifest)

    # --- fetch ---
    p_fetch = sub.add_parser(
        "fetch", help="Emit full contents of the listed files.")
    add_common(p_fetch, output_default=DEFAULT_BUNDLE_OUT)
    p_fetch.add_argument("files", nargs="*",
                         help="Paths of files to include "
                              "(relative to root).")
    p_fetch.add_argument("--files-from", default=None, metavar="FILE",
                         help="Read a newline-separated list of paths.")
    p_fetch.add_argument("--from-stdin", action="store_true",
                         help="Read paths from stdin.")
    p_fetch.set_defaults(func=cmd_fetch)

    # --- diff ---
    p_diff = sub.add_parser(
        "diff", help="Emit only files changed since the last run.")
    add_common(p_diff, output_default=DEFAULT_BUNDLE_OUT)
    p_diff.add_argument("--state-file", default=None, metavar="PATH",
                        help="Custom state file path.")
    p_diff.add_argument("--full", action="store_true",
                        help="Force a full merge (still updates state).")
    p_diff.add_argument("--reset-state", action="store_true",
                        help="Delete the state file before running.")
    p_diff.add_argument("--dry-run", action="store_true",
                        help="Only list changed files, write nothing.")
    p_diff.set_defaults(func=cmd_diff)

    # --- search ---
    p_search = sub.add_parser("search",
                              help="Search a symbol across the project.")
    add_common(p_search, output_default="")
    p_search.add_argument("symbol",
                          help="Regex or literal to search for.")
    p_search.add_argument("--max-hits", type=int, default=500, metavar="N",
                          help="Stop after N hits (default: 500).")
    p_search.set_defaults(func=cmd_search)

    # --- langs ---
    p_langs = sub.add_parser("langs", help="List supported languages.")
    p_langs.set_defaults(func=cmd_langs)

    return parser


def _apply_cd(args) -> int | None:
    """Change working directory if --cd/-C was given.

    Returns an exit code on failure, or None on success.
    Safe to call even if the subcommand did not define --cd.
    """
    cd_dir = getattr(args, "cd", None)
    if not cd_dir:
        return None

    target = Path(cd_dir).expanduser()
    if not target.is_absolute():
        target = Path.cwd() / target
    try:
        target = target.resolve()
    except OSError as e:
        print(f"Error: cannot resolve --cd {cd_dir}: {e}", file=sys.stderr)
        return 2

    if not target.is_dir():
        print(f"Error: --cd is not a directory: {target}", file=sys.stderr)
        return 2

    try:
        os.chdir(target)
    except OSError as e:
        print(f"Error: cannot change directory to {target}: {e}",
              file=sys.stderr)
        return 2

    if not getattr(args, "quiet", False):
        print(f"cd: {target}", file=sys.stderr)
    return None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Handle --cd/-C before dispatching to any command so that
    # every path in the run resolves against the new directory.
    rc = _apply_cd(args)
    if rc is not None:
        return rc

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())