#!/usr/bin/env python3
"""Detects violations of the personal code style rules in source files.

The checker scans Rust, PHP, TypeScript, JavaScript and Python files. It reports
inline comments, string interpolation and concatenation, collection merging
with ``+``, forbidden operators, weak types and missing doc-comments. The
process exits with status 1 when at least one violation is found.

Usage:
    python3 check_style.py src tests
    python3 check_style.py app/Services/CouponService.php --json
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from collections import Counter
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final, TypedDict


class Language(Enum):
    """Source languages understood by the checker."""

    RUST = 'rust'
    PHP = 'php'
    TYPESCRIPT = 'typescript'
    JAVASCRIPT = 'javascript'
    PYTHON = 'python'


class Rule(Enum):
    """Rule groups that a violation can belong to."""

    COMMENTS = 'comments'
    STRINGS = 'string-building'
    MERGING = 'merging'
    OPERATORS = 'operators'
    TYPES = 'typing'
    DOCS = 'doc-comments'


@dataclass(frozen=True, slots=True)
class Violation:
    """A single rule violation found in a source file.

    Attributes:
        rule: Rule group the violation belongs to.
        path: Path of the offending file.
        line: 1-based line number of the violation.
        message: Human readable description of the violation.
    """

    rule: Rule
    path: Path
    line: int
    message: str


@dataclass(frozen=True, slots=True)
class Comment:
    """A comment found while masking a C-like source file.

    Attributes:
        start_line: 1-based line where the comment starts.
        end_line: 1-based line where the comment ends.
        text: Raw comment text including its delimiters.
        is_doc: Whether the comment is a doc-comment such as ``/** ... */`` or ``///``.
    """

    start_line: int
    end_line: int
    text: str
    is_doc: bool


@dataclass(frozen=True, slots=True)
class MaskedSource:
    """C-like source code with string contents and comments blanked out.

    Attributes:
        code: Source of the same shape where comments and string contents are spaces.
        comments: Comments in the order they appear.
        interpolated_lines: Lines that contain an interpolated string literal.
    """

    code: str
    comments: tuple[Comment, ...]
    interpolated_lines: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class LinePattern:
    """A regular expression that marks a masked line as violating a rule.

    Attributes:
        rule: Rule group reported on a match.
        pattern: Expression searched for in the masked line.
        message: Message reported on a match.
    """

    rule: Rule
    pattern: re.Pattern[str]
    message: str


@dataclass(frozen=True, slots=True)
class Declaration:
    """A declaration that requires a doc-comment.

    Attributes:
        line_index: 0-based index of the line holding the declaration.
        signature_column: Column of the opening parenthesis of a function
            signature, or ``None`` when the declaration is not a function.
        requires_return_type: Whether the function must declare a return type.
    """

    line_index: int
    signature_column: int | None
    requires_return_type: bool


@dataclass(slots=True)
class SourceMasker:
    """Replaces comments and string contents of C-like code with spaces.

    The masker is used as a ``re.sub`` callback and records every comment and
    interpolated string it meets on the way.

    Attributes:
        source: The original source text.
        language: Language that decides how string interpolation looks.
        comments: Comments collected so far.
        interpolated_lines: Lines with interpolated strings collected so far.
    """

    source: str
    language: Language
    comments: list[Comment] = field(default_factory=list)
    interpolated_lines: list[int] = field(default_factory=list)

    def replace(self, match: re.Match[str]) -> str:
        """Returns the masked replacement for a comment or string literal.

        Args:
            match: Match produced by the language token pattern.

        Returns:
            Text of the same shape with comment or string contents blanked out.
        """
        text = match.group(0)
        kind = match.lastgroup

        if kind in COMMENT_GROUPS:
            self.comments.append(
                Comment(
                    start_line=line_at(self.source, match.start()),
                    end_line=line_at(self.source, match.end() - 1),
                    text=text,
                    is_doc=kind in DOC_GROUPS,
                ),
            )

            return blank(text)

        if is_interpolated(text, self.language):
            self.interpolated_lines.append(line_at(self.source, match.start()))

        return '{}{}{}'.format(text[0], blank(text[1:-1]), text[-1])


class ViolationRecord(TypedDict):
    """JSON representation of a violation."""

    rule: str
    path: str
    line: int
    message: str


class Report(TypedDict):
    """JSON representation of a full checker run."""

    files_checked: int
    violation_count: int
    counts: dict[str, int]
    violations: list[ViolationRecord]


EXTENSIONS: Final[dict[str, Language]] = {
    '.rs': Language.RUST,
    '.php': Language.PHP,
    '.ts': Language.TYPESCRIPT,
    '.tsx': Language.TYPESCRIPT,
    '.mts': Language.TYPESCRIPT,
    '.cts': Language.TYPESCRIPT,
    '.js': Language.JAVASCRIPT,
    '.jsx': Language.JAVASCRIPT,
    '.mjs': Language.JAVASCRIPT,
    '.cjs': Language.JAVASCRIPT,
    '.py': Language.PYTHON,
}

IGNORED_DIRECTORIES: Final[frozenset[str]] = frozenset(
    {
        '.git',
        '.mypy_cache',
        '.pytest_cache',
        '.ruff_cache',
        '.venv',
        '__pycache__',
        'build',
        'coverage',
        'dist',
        'node_modules',
        'storage',
        'target',
        'vendor',
        'venv',
    },
)

COMMENT_GROUPS: Final[frozenset[str]] = frozenset({'doc', 'doc_line', 'block', 'line', 'hash'})

DOC_GROUPS: Final[frozenset[str]] = frozenset({'doc', 'doc_line'})

INNER_DOC_PREFIXES: Final[tuple[str, ...]] = ('//!', '/*!')

STRING_PATTERNS: Final[str] = r"""
    (?P<single>'(?:\\.|[^'\\])*'?)
    | (?P<double>"(?:\\.|[^"\\])*"?)
"""

PHP_TOKENS: Final[re.Pattern[str]] = re.compile(
    r"""
    (?P<doc>/\*\*(?!/).*?(?:\*/|\Z))
    | (?P<block>/\*.*?(?:\*/|\Z))
    | (?P<line>//[^\n]*)
    | (?P<hash>\#(?!\[)[^\n]*)
    | """ '{}'.format(STRING_PATTERNS),
    re.DOTALL | re.VERBOSE,
)

SCRIPT_TOKENS: Final[re.Pattern[str]] = re.compile(
    r"""
    (?P<doc>/\*\*(?!/).*?(?:\*/|\Z))
    | (?P<block>/\*.*?(?:\*/|\Z))
    | (?P<line>//[^\n]*)
    | (?P<backtick>`(?:\\.|[^`\\])*`?)
    | """ '{}'.format(STRING_PATTERNS),
    re.DOTALL | re.VERBOSE,
)

RUST_TOKENS: Final[re.Pattern[str]] = re.compile(
    r"""
    (?P<doc>/\*[*!](?![*/]).*?(?:\*/|\Z))
    | (?P<block>/\*.*?(?:\*/|\Z))
    | (?P<doc_line>//[/!](?!/)[^\n]*)
    | (?P<line>//[^\n]*)
    | (?P<raw>b?r(?P<hashes>\#*)".*?"(?P=hashes))
    | (?P<char>'(?:\\u\{[0-9a-fA-F]{1,6}\}|\\.|[^'\\\n])')
    | (?P<double>"(?:\\.|[^"\\])*"?)
    """,
    re.DOTALL | re.VERBOSE,
)

TOKENS: Final[dict[Language, re.Pattern[str]]] = {
    Language.RUST: RUST_TOKENS,
    Language.PHP: PHP_TOKENS,
    Language.TYPESCRIPT: SCRIPT_TOKENS,
    Language.JAVASCRIPT: SCRIPT_TOKENS,
}

PHP_INTERPOLATION: Final[re.Pattern[str]] = re.compile(r'(?<!\\)\$[A-Za-z_{]|\{\$')

RUST_CAPTURED_ARGUMENT: Final[re.Pattern[str]] = re.compile(r'\{[A-Za-z_]\w*(?::[^}]*)?\}')

RUST_FORMAT_MACRO: Final[re.Pattern[str]] = re.compile(
    r'\b(?:format|print|println|eprint|eprintln|write|writeln|panic|format_args|unreachable|todo|assert|'
    r'assert_eq|assert_ne|debug_assert|info|warn|error|debug|trace|bail|ensure)!\s*\(',
)

RUST_SEPARATOR_JOIN: Final[re.Pattern[str]] = re.compile(r'\.join\s*\(\s*"[^"\w]*"\s*\)')

RUST_PANIC: Final[re.Pattern[str]] = re.compile(
    r'\.unwrap\s*\(\s*\)|\.expect\s*\(|\b(?:panic|unreachable|todo|unimplemented)!',
)

RUST_VISIBILITY: Final[str] = r'(?:pub(?:\([^)]*\))?\s+)?'

RUST_ITEM: Final[re.Pattern[str]] = re.compile(
    r'^\s*{}(?:(?:const|async|unsafe|default|extern\s+"[^"]*")\s+)*'
    r'(?:fn|struct|enum|trait|type|const|static|union|mod)\s+\w+'
    r'|^\s*macro_rules!\s*\w+'.format(RUST_VISIBILITY),
)

RUST_MODULE_FILE: Final[re.Pattern[str]] = re.compile(r'^\s*{}mod\s+\w+\s*;'.format(RUST_VISIBILITY))

RUST_CONTAINER: Final[re.Pattern[str]] = re.compile(r'^\s*{}(?:struct|enum|union)\s+\w+'.format(RUST_VISIBILITY))

RUST_FIELD: Final[re.Pattern[str]] = re.compile(r'^\s*{}[a-z_]\w*\s*:(?!:)'.format(RUST_VISIBILITY))

RUST_VARIANT: Final[re.Pattern[str]] = re.compile(r'^\s*[A-Z]\w*\s*(?:[({,=]|$)')

RUST_ATTRIBUTE: Final[re.Pattern[str]] = re.compile(r'^\s*#!?\[')

RUST_LINE_PATTERNS: Final[tuple[LinePattern, ...]] = (
    LinePattern(
        Rule.OPERATORS,
        re.compile(r'(?:[)\]?]|\b(?!move\b)\w+)\s*\|\|'),
        'Logical `||` is not allowed; use `matches!`, `contains()`, `any()` or early returns.',
    ),
    LinePattern(Rule.STRINGS, re.compile(r'\+\s*[&"]|\+=\s*[&"]'), 'String concatenation with `+` is not allowed.'),
    LinePattern(Rule.STRINGS, re.compile(r'\.push_str\s*\('), 'Building strings with `push_str()` is not allowed.'),
    LinePattern(Rule.STRINGS, re.compile(r'\bitertools::join\b'), '`itertools::join()` is not allowed; use `.format()`.'),
    LinePattern(Rule.MERGING, re.compile(r'\.concat\s*\(\s*\)'), '`concat()` is not allowed; use `extend()` or `chain()`.'),
    LinePattern(Rule.TYPES, re.compile(r'\bdyn\s+(?:(?:std|core)::any::)?Any\b'), '`dyn Any` is not allowed.'),
    LinePattern(
        Rule.TYPES,
        re.compile(r'\bserde_json::Value\b'),
        '`serde_json::Value` is not allowed; deserialize into a typed struct.',
    ),
    LinePattern(
        Rule.TYPES,
        re.compile(r'\bBox<dyn\s+(?:std::error::)?Error\b|\banyhow::'),
        'Type-erased errors are not allowed; use a `thiserror` enum.',
    ),
    LinePattern(Rule.TYPES, re.compile(r'\bunsafe\b'), '`unsafe` code is not allowed.'),
    LinePattern(
        Rule.TYPES,
        re.compile(r'\bas\s+(?:u8|u16|u32|u64|u128|usize|i8|i16|i32|i64|i128|isize|f32|f64)\b'),
        'Numeric `as` casts are not allowed; use `From` or `TryFrom`.',
    ),
)

TYPE_SUPPRESSION: Final[re.Pattern[str]] = re.compile(
    r'@ts-(?:ignore|expect-error|nocheck)|@phpstan-ignore|@psalm-suppress|type:\s*ignore',
)

TOOL_DIRECTIVE: Final[re.Pattern[str]] = re.compile(
    r'eslint-(?:disable|enable)|prettier-ignore|phpcs:|@codeCoverageIgnore|noqa|'
    r'(?:istanbul|c8|v8) ignore|^///\s*<reference',
)

STRICT_TYPES: Final[re.Pattern[str]] = re.compile(r'declare\s*\(\s*strict_types\s*=\s*1\s*\)')

PHP_LINE_PATTERNS: Final[tuple[LinePattern, ...]] = (
    LinePattern(Rule.OPERATORS, re.compile(r'\?\?'), 'Null-coalescing operator `??` is not allowed.'),
    LinePattern(Rule.OPERATORS, re.compile(r'\?->'), 'Nullsafe operator `?->` is not allowed.'),
    LinePattern(Rule.OPERATORS, re.compile(r'\?\s*:'), 'Short ternary `?:` is not allowed.'),
    LinePattern(Rule.OPERATORS, re.compile(r'\s\?\s'), 'Ternary operator is not allowed.'),
    LinePattern(Rule.OPERATORS, re.compile(r'\|\|'), 'Logical `||` is not allowed; use `or`.'),
    LinePattern(
        Rule.STRINGS,
        re.compile(r'\s\.\s|\.=|[\'"]\s*\.(?![.\d])|(?<![.\d])\.\s*[\'"]|\w\.\$'),
        'String concatenation with `.` is not allowed.',
    ),
    LinePattern(
        Rule.STRINGS,
        re.compile(r'\bimplode\s*\(|(?<![:>])\bjoin\s*\('),
        'Raw `implode()` or `join()` is not allowed; use `Arr::join()` or Symfony String.',
    ),
    LinePattern(
        Rule.MERGING,
        re.compile(r'\]\s*\+(?![+=])|(?<![+])\+\s*\[|\+=\s*\['),
        'Arrays must not be merged with `+`.',
    ),
    LinePattern(Rule.TYPES, re.compile(r'\bmixed\b'), 'The `mixed` type is not allowed.'),
)

PHP_UNTYPED_PROPERTY: Final[re.Pattern[str]] = re.compile(r'^\s*(?:public|protected|private|var)(?:\s+static)?\s+\$\w+')

SCRIPT_LINE_PATTERNS: Final[tuple[LinePattern, ...]] = (
    LinePattern(Rule.OPERATORS, re.compile(r'\?\?'), 'Null-coalescing operator `??` is not allowed.'),
    LinePattern(Rule.OPERATORS, re.compile(r'\?\.(?!\d)'), 'Optional chaining `?.` is not allowed.'),
    LinePattern(Rule.OPERATORS, re.compile(r'\s\?\s'), 'Ternary operator is not allowed.'),
    LinePattern(Rule.OPERATORS, re.compile(r'\|\|'), 'Logical `||` is not allowed.'),
    LinePattern(
        Rule.STRINGS,
        re.compile(r'(?<!path)(?<!posix)(?<!win32)\.join\s*\('),
        'Raw `join()` is not allowed; use `Intl.ListFormat` or return separate lines.',
    ),
    LinePattern(
        Rule.STRINGS,
        re.compile(r'[\'"`]\s*\+(?![+=])|(?<![+])\+\s*[\'"`]|\+=\s*[\'"`]'),
        'String concatenation with `+` is not allowed.',
    ),
    LinePattern(Rule.MERGING, re.compile(r'\.concat\s*\('), '`concat()` is not allowed; use spread syntax.'),
)

TYPESCRIPT_LINE_PATTERNS: Final[tuple[LinePattern, ...]] = (
    LinePattern(Rule.TYPES, re.compile(r'\bany\b'), 'The `any` type is not allowed.'),
    LinePattern(Rule.TYPES, re.compile(r'\bunknown\b'), 'The `unknown` type is not allowed.'),
    LinePattern(Rule.TYPES, re.compile(r':\s*(?:object|Function)\b'), 'Loose `object` or `Function` type is not allowed.'),
    LinePattern(Rule.TYPES, re.compile(r'[\w)\]]!(?=[.\[),;])'), 'Non-null assertion `!` is not allowed.'),
)

PHP_FUNCTION: Final[re.Pattern[str]] = re.compile(
    r'^\s*(?:(?:abstract|final|public|protected|private|static)\s+)*function\s+&?(?P<name>\w+)\s*\(',
)

PHP_OTHER_DECLARATIONS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r'^\s*(?:(?:abstract|final|readonly)\s+)*(?:class|interface|trait|enum)\s+\w+'),
    re.compile(r'^\s*(?:public|protected|private)(?:\s+(?:static|readonly))*\s+[?\w\\|&]+\s+\$\w+'),
    re.compile(r'^\s*(?:(?:public|protected|private|final)\s+)*const\s+\w+'),
)

PHP_WITHOUT_RETURN_TYPE: Final[frozenset[str]] = frozenset({'__construct', '__destruct'})

PHP_TYPED_PARAMETER: Final[re.Pattern[str]] = re.compile(
    r'^(?:\#\[.*?\]\s*)*(?:(?:public|protected|private|readonly)\s+)*[?\w\\|&()]+\s+&?(?:\.\.\.)?\$\w+',
    re.DOTALL,
)

PHP_ATTRIBUTE: Final[re.Pattern[str]] = re.compile(r'^\s*#\[')

SCRIPT_CONTAINER: Final[re.Pattern[str]] = re.compile(
    r'^\s*(?:export\s+)?(?:default\s+)?(?:declare\s+)?(?:abstract\s+)?(?P<kind>class|interface|enum)\s+\w+',
)

SCRIPT_FUNCTION: Final[re.Pattern[str]] = re.compile(
    r'^\s*(?:export\s+)?(?:default\s+)?(?:declare\s+)?(?:async\s+)?function\s*\*?\s*\w+\s*(?:<[^(]*>)?\s*\(',
)

SCRIPT_TYPE_ALIAS: Final[re.Pattern[str]] = re.compile(r'^\s*(?:export\s+)?(?:declare\s+)?type\s+\w+')

SCRIPT_TOP_LEVEL_CONSTANT: Final[re.Pattern[str]] = re.compile(r'^(?:export\s+)?const\s+\w+')

SCRIPT_METHOD: Final[re.Pattern[str]] = re.compile(
    r'^\s*(?P<modifiers>(?:(?:public|private|protected|static|async|readonly|override|abstract|get|set|declare)\s+)*)'
    r'#?\*?(?P<name>\w+)\s*\??\s*(?:<[^(]*>)?\s*\(',
)

SCRIPT_PROPERTY: Final[re.Pattern[str]] = re.compile(
    r'^\s*(?:(?:public|private|protected|static|readonly|declare|override|abstract)\s+)*#?\w+[?!]?\s*[:=;]',
)

SCRIPT_KEYWORDS: Final[frozenset[str]] = frozenset(
    {'if', 'for', 'while', 'switch', 'catch', 'return', 'await', 'new', 'super', 'function', 'throw', 'typeof'},
)

SCRIPT_DECORATOR: Final[re.Pattern[str]] = re.compile(r'^\s*@\w+')

TYPED_SCRIPT_LANGUAGES: Final[frozenset[Language]] = frozenset({Language.TYPESCRIPT})

BARE_GENERICS: Final[frozenset[str]] = frozenset(
    {'dict', 'list', 'set', 'frozenset', 'tuple', 'Dict', 'List', 'Set', 'FrozenSet', 'Tuple'},
)

FSTRING_START: Final[int] = getattr(tokenize, 'FSTRING_START', -1)

TSTRING_START: Final[int] = getattr(tokenize, 'TSTRING_START', -1)


def blank(text: str) -> str:
    """Replaces every character except line breaks with a space.

    Args:
        text: The text to blank out.

    Returns:
        A string of the same length that keeps only the line breaks.
    """
    return re.sub(r'[^\n]', ' ', text)


def line_at(source: str, offset: int) -> int:
    """Returns the 1-based line number of a character offset.

    Args:
        source: The full source text.
        offset: Character offset inside the source.

    Returns:
        The line number that contains the offset.
    """
    return source.count('\n', 0, offset) + 1


def is_interpolated(literal: str, language: Language) -> bool:
    """Tells whether a string literal interpolates values.

    Args:
        literal: The literal including its quotes.
        language: Language the literal was written in.

    Returns:
        True for PHP double-quoted strings with variables, for template
        literals that contain ``${`` and for Rust literals with inline
        captured format arguments such as ``{name}``.
    """
    if language is Language.RUST:
        unescaped = literal.replace('{{', '').replace('}}', '')

        return RUST_CAPTURED_ARGUMENT.search(unescaped) is not None

    if language is Language.PHP:
        return literal.startswith('"') and PHP_INTERPOLATION.search(literal) is not None

    return literal.startswith('`') and '${' in literal


def mask_source(source: str, language: Language) -> MaskedSource:
    """Blanks out comments and string contents of Rust, PHP or script source.

    Args:
        source: The original source text.
        language: Language of the source.

    Returns:
        The masked source together with the comments and interpolated lines found.
    """
    masker = SourceMasker(source=source, language=language)
    code = TOKENS[language].sub(masker.replace, source)

    return MaskedSource(
        code=code,
        comments=tuple(masker.comments),
        interpolated_lines=tuple(masker.interpolated_lines),
    )


def comment_violations(path: Path, masked: MaskedSource) -> Iterator[Violation]:
    """Reports inline comments and type-checking suppressions.

    Args:
        path: Path of the checked file.
        masked: Masked source of the file.

    Yields:
        One violation per offending comment.
    """
    for comment in masked.comments:
        if TYPE_SUPPRESSION.search(comment.text) is not None:
            yield Violation(Rule.TYPES, path, comment.start_line, 'Type checking is suppressed by a directive.')
            continue

        if comment.is_doc:
            continue

        if TOOL_DIRECTIVE.search(comment.text) is not None:
            continue

        yield Violation(Rule.COMMENTS, path, comment.start_line, 'Inline comment found; only doc-comments are allowed.')


def line_violations(
    path: Path,
    masked_lines: Sequence[str],
    patterns: Sequence[LinePattern],
) -> Iterator[Violation]:
    """Reports every masked line that matches a forbidden pattern.

    Args:
        path: Path of the checked file.
        masked_lines: Lines of the masked source.
        patterns: Patterns to search for.

    Yields:
        One violation per matching pattern and line.
    """
    for number, line in enumerate(masked_lines, start=1):
        for item in patterns:
            if item.pattern.search(line) is not None:
                yield Violation(item.rule, path, number, item.message)


def interpolation_violations(path: Path, masked: MaskedSource) -> Iterator[Violation]:
    """Reports interpolated string literals.

    Args:
        path: Path of the checked file.
        masked: Masked source of the file.

    Yields:
        One violation per interpolated literal.
    """
    for number in masked.interpolated_lines:
        yield Violation(Rule.STRINGS, path, number, 'String interpolation is not allowed.')


def previous_code_line(source_lines: Sequence[str], index: int, attribute: re.Pattern[str]) -> int:
    """Finds the nearest line above that is neither blank nor an attribute.

    Args:
        source_lines: Lines of the original source.
        index: 0-based index of the declaration line.
        attribute: Pattern of attribute or decorator lines to skip.

    Returns:
        The 1-based number of that line, or 0 when there is none.
    """
    cursor = index - 1

    while cursor >= 0:
        line = source_lines[cursor]

        if line.strip() == '' or attribute.match(line) is not None:
            cursor -= 1
            continue

        return cursor + 1

    return 0


def doc_violations(
    path: Path,
    source_lines: Sequence[str],
    masked: MaskedSource,
    declarations: Sequence[Declaration],
    attribute: re.Pattern[str],
) -> Iterator[Violation]:
    """Reports declarations that are not preceded by a doc-comment.

    Args:
        path: Path of the checked file.
        source_lines: Lines of the original source.
        masked: Masked source of the file.
        declarations: Declarations found in the file.
        attribute: Pattern of attribute or decorator lines between the doc-comment and the declaration.

    Yields:
        One violation per undocumented declaration.
    """
    doc_end_lines = frozenset(
        comment.end_line
        for comment in masked.comments
        if comment.is_doc and not comment.text.startswith(INNER_DOC_PREFIXES)
    )

    for declaration in declarations:
        previous = previous_code_line(source_lines, declaration.line_index, attribute)

        if previous not in doc_end_lines:
            yield Violation(Rule.DOCS, path, declaration.line_index + 1, 'Declaration has no doc-comment.')


def line_offsets(lines: Sequence[str]) -> list[int]:
    """Computes the character offset at which each line starts.

    Args:
        lines: Lines of a text split on ``\\n``.

    Returns:
        Offsets in the same order as the lines.
    """
    offsets: list[int] = []
    position = 0

    for line in lines:
        offsets.append(position)
        position += len(line) + 1

    return offsets


def matching_parenthesis(code: str, open_index: int) -> int:
    """Finds the parenthesis that closes the one at ``open_index``.

    Args:
        code: Masked source code.
        open_index: Offset of an opening parenthesis.

    Returns:
        Offset of the closing parenthesis, or -1 when it is missing.
    """
    depth = 0

    for index in range(open_index, len(code)):
        character = code[index]

        if character == '(':
            depth += 1

        if character == ')':
            depth -= 1

            if depth == 0:
                return index

    return -1


def split_parameters(text: str) -> list[str]:
    """Splits a parameter list on commas that are not nested in brackets.

    Args:
        text: Text between the parentheses of a signature.

    Returns:
        Non-empty parameters with surrounding whitespace removed.
    """
    parameters: list[str] = []
    depth = 0
    start = 0

    for index, character in enumerate(text):
        if character in '([{<':
            depth += 1

        if character in ')]}' or (character == '>' and text[index - 1] != '='):
            depth -= 1

        if character == ',' and depth == 0:
            parameters.append(text[start:index].strip())
            start = index + 1

    parameters.append(text[start:].strip())

    return [parameter for parameter in parameters if parameter != '']


def has_top_level_colon(text: str) -> bool:
    """Tells whether a parameter has a type annotation outside of nested brackets.

    Args:
        text: A single parameter of a TypeScript signature.

    Returns:
        True when a ``:`` appears at nesting depth zero.
    """
    depth = 0

    for character in text:
        if character in '([{':
            depth += 1

        if character in ')]}':
            depth -= 1

        if character == ':' and depth == 0:
            return True

    return False


def has_return_type(code: str, close_index: int) -> bool:
    """Tells whether a signature declares a return type after its parameters.

    Args:
        code: Masked source code.
        close_index: Offset of the parenthesis that closes the parameters.

    Returns:
        True when the next non-space character is ``:``.
    """
    rest = code[close_index + 1:].lstrip()

    return rest.startswith(':')


def parameter_is_typed(parameter: str, language: Language) -> bool:
    """Tells whether a single parameter declares an explicit type.

    Args:
        parameter: The parameter text.
        language: Language of the signature.

    Returns:
        True when the parameter has a type.
    """
    if language is Language.PHP:
        return PHP_TYPED_PARAMETER.match(parameter) is not None

    return has_top_level_colon(parameter)


def compact(text: str) -> str:
    """Collapses runs of whitespace into single spaces.

    Args:
        text: Text to compact.

    Returns:
        The compacted text.
    """
    return re.sub(r'\s+', ' ', text).strip()


def signature_violations(
    path: Path,
    masked_lines: Sequence[str],
    code: str,
    declarations: Sequence[Declaration],
    language: Language,
) -> Iterator[Violation]:
    """Reports untyped parameters and missing return types.

    Args:
        path: Path of the checked file.
        masked_lines: Lines of the masked source.
        code: The masked source.
        declarations: Declarations found in the file.
        language: Language of the file.

    Yields:
        One violation per untyped parameter or missing return type.
    """
    offsets = line_offsets(masked_lines)

    for declaration in declarations:
        if declaration.signature_column is None:
            continue

        open_index = offsets[declaration.line_index] + declaration.signature_column
        close_index = matching_parenthesis(code, open_index)
        line = declaration.line_index + 1

        if close_index == -1:
            continue

        for parameter in split_parameters(code[open_index + 1:close_index]):
            if not parameter_is_typed(parameter, language):
                yield Violation(Rule.TYPES, path, line, 'Parameter `{}` has no explicit type.'.format(compact(parameter)))

        if declaration.requires_return_type and not has_return_type(code, close_index):
            yield Violation(Rule.TYPES, path, line, 'Function has no explicit return type.')


def php_declarations(masked_lines: Sequence[str]) -> Iterator[Declaration]:
    """Finds PHP declarations that require a doc-comment.

    Args:
        masked_lines: Lines of the masked source.

    Yields:
        Classes, functions, methods, properties and constants.
    """
    for index, line in enumerate(masked_lines):
        function = PHP_FUNCTION.match(line)

        if function is not None:
            yield Declaration(
                line_index=index,
                signature_column=function.end() - 1,
                requires_return_type=function.group('name') not in PHP_WITHOUT_RETURN_TYPE,
            )
            continue

        if any(pattern.match(line) is not None for pattern in PHP_OTHER_DECLARATIONS):
            yield Declaration(line_index=index, signature_column=None, requires_return_type=False)


def script_declaration(line: str, index: int, in_member_scope: bool) -> Declaration | None:
    """Recognises a TypeScript or JavaScript declaration on a single line.

    Args:
        line: The masked line.
        index: 0-based index of the line.
        in_member_scope: Whether the line sits directly inside a class or interface body.

    Returns:
        The declaration, or ``None`` when the line declares nothing that needs documentation.
    """
    function = SCRIPT_FUNCTION.match(line)

    if function is not None:
        return Declaration(line_index=index, signature_column=function.end() - 1, requires_return_type=True)

    if SCRIPT_CONTAINER.match(line) is not None:
        return Declaration(line_index=index, signature_column=None, requires_return_type=False)

    if SCRIPT_TYPE_ALIAS.match(line) is not None:
        return Declaration(line_index=index, signature_column=None, requires_return_type=False)

    if SCRIPT_TOP_LEVEL_CONSTANT.match(line) is not None:
        return Declaration(line_index=index, signature_column=None, requires_return_type=False)

    if not in_member_scope:
        return None

    method = SCRIPT_METHOD.match(line)

    if method is not None and method.group('name') not in SCRIPT_KEYWORDS:
        name = method.group('name')
        is_setter = 'set ' in method.group('modifiers')

        return Declaration(
            line_index=index,
            signature_column=method.end() - 1,
            requires_return_type=name != 'constructor' and not is_setter,
        )

    if SCRIPT_PROPERTY.match(line) is not None:
        return Declaration(line_index=index, signature_column=None, requires_return_type=False)

    return None


def script_declarations(masked_lines: Sequence[str]) -> Iterator[Declaration]:
    """Finds TypeScript or JavaScript declarations that require a doc-comment.

    Class and interface members are recognised by tracking brace and
    parenthesis depth, so statements inside method bodies are not mistaken
    for members.

    Args:
        masked_lines: Lines of the masked source.

    Yields:
        Functions, classes, interfaces, members, type aliases and top-level constants.
    """
    brace_depth = 0
    parenthesis_depth = 0
    member_depths: list[int] = []

    for index, line in enumerate(masked_lines):
        in_member_scope = len(member_depths) > 0 and brace_depth == member_depths[-1] and parenthesis_depth == 0
        declaration = script_declaration(line, index, in_member_scope)

        if declaration is not None:
            yield declaration

        container = SCRIPT_CONTAINER.match(line)

        if container is not None and container.group('kind') != 'enum':
            member_depths.append(brace_depth + 1)

        brace_depth += line.count('{') - line.count('}')
        parenthesis_depth += line.count('(') - line.count(')')

        while len(member_depths) > 0 and brace_depth < member_depths[-1]:
            member_depths.pop()


def rust_line_declares(line: str, in_member_scope: bool) -> bool:
    """Tells whether a masked Rust line declares an element that needs a doc-comment.

    Args:
        line: The masked line.
        in_member_scope: Whether the line sits directly inside a struct, enum or union body.

    Returns:
        True for items, struct fields and enum variants. Out-of-line ``mod name;``
        declarations are documented inside their own file and are skipped.
    """
    if RUST_MODULE_FILE.match(line) is not None:
        return False

    if RUST_ITEM.match(line) is not None:
        return True

    if not in_member_scope:
        return False

    return RUST_FIELD.match(line) is not None or RUST_VARIANT.match(line) is not None


def rust_declarations(masked_lines: Sequence[str]) -> Iterator[Declaration]:
    """Finds Rust items, struct fields and enum variants that require a doc-comment.

    Args:
        masked_lines: Lines of the masked source.

    Yields:
        One declaration per documented element.
    """
    brace_depth = 0
    parenthesis_depth = 0
    member_depths: list[int] = []

    for index, line in enumerate(masked_lines):
        in_member_scope = len(member_depths) > 0 and brace_depth == member_depths[-1] and parenthesis_depth == 0

        if rust_line_declares(line, in_member_scope):
            yield Declaration(line_index=index, signature_column=None, requires_return_type=False)

        if RUST_CONTAINER.match(line) is not None and '{' in line:
            member_depths.append(brace_depth + 1)

        brace_depth += line.count('{') - line.count('}')
        parenthesis_depth += line.count('(') - line.count(')')

        while len(member_depths) > 0 and brace_depth < member_depths[-1]:
            member_depths.pop()


def starts_with_module_doc(source_lines: Sequence[str]) -> bool:
    """Tells whether a Rust file opens with a ``//!`` module doc-comment.

    Args:
        source_lines: Lines of the original source.

    Returns:
        True when the first non-blank line is an inner doc-comment.
    """
    for line in source_lines:
        stripped = line.strip()

        if stripped == '':
            continue

        return stripped.startswith('//!') or stripped.startswith('/*!')

    return False


def test_section_start(source_lines: Sequence[str]) -> int:
    """Finds the first line of the ``#[cfg(test)]`` section of a Rust file.

    Args:
        source_lines: Lines of the original source.

    Returns:
        The 1-based line of the first ``#[cfg(test)]`` attribute, or a number past
        the end of the file when there is none.
    """
    for number, line in enumerate(source_lines, start=1):
        if line.strip().startswith('#[cfg(test)]'):
            return number

    return len(source_lines) + 1


def check_rust(path: Path, source: str) -> list[Violation]:
    """Checks a Rust file.

    Panicking calls are allowed in integration tests under ``tests/`` and in
    the ``#[cfg(test)]`` section that closes a source file.

    Args:
        path: Path of the file.
        source: Contents of the file.

    Returns:
        Every violation found in the file.
    """
    masked = mask_source(source, Language.RUST)
    masked_lines = masked.code.split('\n')
    source_lines = source.split('\n')
    declarations = list(rust_declarations(masked_lines))
    violations = [
        *comment_violations(path, masked),
        *line_violations(path, masked_lines, RUST_LINE_PATTERNS),
        *doc_violations(path, source_lines, masked, declarations, RUST_ATTRIBUTE),
    ]

    for number in masked.interpolated_lines:
        if RUST_FORMAT_MACRO.search(source_lines[number - 1]) is not None:
            violations.append(
                Violation(Rule.STRINGS, path, number, 'Inline captured format arguments are not allowed; pass them positionally.'),
            )

    for number, line in enumerate(source_lines, start=1):
        if RUST_SEPARATOR_JOIN.search(line) is not None:
            violations.append(Violation(Rule.STRINGS, path, number, 'Raw `join()` is not allowed; use `.format()` from itertools.'))

    if 'tests' not in path.parts:
        test_start = test_section_start(source_lines)

        for number, line in enumerate(masked_lines, start=1):
            if number < test_start and RUST_PANIC.search(line) is not None:
                violations.append(Violation(Rule.TYPES, path, number, 'Panicking call outside tests; return a `Result` instead.'))

    if not starts_with_module_doc(source_lines):
        violations.append(Violation(Rule.DOCS, path, 1, 'File has no `//!` module doc-comment.'))

    return violations


def untyped_property_violations(
    path: Path,
    source_lines: Sequence[str],
    masked: MaskedSource,
    masked_lines: Sequence[str],
) -> Iterator[Violation]:
    """Reports PHP properties without a native type.

    A property that overrides an untyped parent property, such as Eloquent's
    ``$fillable``, cannot declare a native type. Such a property is accepted
    when its doc-comment declares the type with ``@var``.

    Args:
        path: Path of the checked file.
        source_lines: Lines of the original source.
        masked: Masked source of the file.
        masked_lines: Lines of the masked source.

    Yields:
        One violation per untyped property without an ``@var`` type.
    """
    typed_doc_lines = frozenset(
        comment.end_line for comment in masked.comments if comment.is_doc and '@var' in comment.text
    )

    for index, line in enumerate(masked_lines):
        if PHP_UNTYPED_PROPERTY.match(line) is None:
            continue

        if previous_code_line(source_lines, index, PHP_ATTRIBUTE) in typed_doc_lines:
            continue

        yield Violation(Rule.TYPES, path, index + 1, 'Property has no native type and no `@var` type.')


def check_php(path: Path, source: str) -> list[Violation]:
    """Checks a PHP file.

    Args:
        path: Path of the file.
        source: Contents of the file.

    Returns:
        Every violation found in the file.
    """
    masked = mask_source(source, Language.PHP)
    masked_lines = masked.code.split('\n')
    source_lines = source.split('\n')
    declarations = list(php_declarations(masked_lines))
    violations = [
        *comment_violations(path, masked),
        *interpolation_violations(path, masked),
        *line_violations(path, masked_lines, PHP_LINE_PATTERNS),
        *doc_violations(path, source_lines, masked, declarations, PHP_ATTRIBUTE),
        *signature_violations(path, masked_lines, masked.code, declarations, Language.PHP),
        *untyped_property_violations(path, source_lines, masked, masked_lines),
    ]

    for comment in masked.comments:
        if comment.is_doc and re.search(r'\bmixed\b', comment.text) is not None:
            violations.append(Violation(Rule.TYPES, path, comment.start_line, 'The `mixed` type is not allowed.'))

    if STRICT_TYPES.search(masked.code) is None:
        violations.append(Violation(Rule.TYPES, path, 1, 'File does not declare `strict_types=1`.'))

    return violations


def check_script(path: Path, source: str, language: Language) -> list[Violation]:
    """Checks a TypeScript or JavaScript file.

    Args:
        path: Path of the file.
        source: Contents of the file.
        language: Either TypeScript or JavaScript.

    Returns:
        Every violation found in the file.
    """
    masked = mask_source(source, language)
    masked_lines = masked.code.split('\n')
    source_lines = source.split('\n')
    declarations = list(script_declarations(masked_lines))
    violations = [
        *comment_violations(path, masked),
        *interpolation_violations(path, masked),
        *line_violations(path, masked_lines, SCRIPT_LINE_PATTERNS),
        *doc_violations(path, source_lines, masked, declarations, SCRIPT_DECORATOR),
    ]

    if language in TYPED_SCRIPT_LANGUAGES:
        violations.extend(line_violations(path, masked_lines, TYPESCRIPT_LINE_PATTERNS))
        violations.extend(signature_violations(path, masked_lines, masked.code, declarations, language))

    return violations


def is_f_string_literal(literal: str) -> bool:
    """Tells whether a Python string token is an f-string.

    Args:
        literal: The token text including its prefix.

    Returns:
        True when the prefix contains ``f``.
    """
    prefix = re.match(r'[A-Za-z]*', literal)

    return prefix is not None and 'f' in prefix.group(0).lower()


def python_token_violations(path: Path, source: str) -> Iterator[Violation]:
    """Reports Python comments and interpolated strings.

    Args:
        path: Path of the checked file.
        source: Contents of the file.

    Yields:
        One violation per comment or interpolated string.
    """
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        line = token.start[0]

        if token.type == tokenize.COMMENT:
            if line == 1 and token.string.startswith('#!'):
                continue

            if TYPE_SUPPRESSION.search(token.string) is not None:
                yield Violation(Rule.TYPES, path, line, 'Type checking is suppressed by a directive.')
                continue

            if TOOL_DIRECTIVE.search(token.string) is not None:
                continue

            yield Violation(Rule.COMMENTS, path, line, 'Inline comment found; only docstrings are allowed.')
            continue

        if token.type in (FSTRING_START, TSTRING_START):
            yield Violation(Rule.STRINGS, path, line, 'String interpolation is not allowed.')
            continue

        if token.type == tokenize.STRING and is_f_string_literal(token.string):
            yield Violation(Rule.STRINGS, path, line, 'String interpolation is not allowed.')


def is_string_node(node: ast.expr) -> bool:
    """Tells whether an expression is a string literal or an f-string.

    Args:
        node: Expression to inspect.

    Returns:
        True for string constants and f-strings.
    """
    if isinstance(node, ast.JoinedStr):
        return True

    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def is_collection_node(node: ast.expr) -> bool:
    """Tells whether an expression is a list or tuple literal.

    Args:
        node: Expression to inspect.

    Returns:
        True for list, tuple and list comprehension literals.
    """
    return isinstance(node, (ast.List, ast.Tuple, ast.ListComp))


def addition_violations(path: Path, node: ast.BinOp | ast.AugAssign) -> Iterator[Violation]:
    """Reports ``+`` and ``+=`` applied to strings or collections.

    Args:
        path: Path of the checked file.
        node: Addition node to inspect.

    Yields:
        A violation when a string or collection literal takes part in the addition.
    """
    if isinstance(node, ast.BinOp):
        operands = [node.left, node.right]
    else:
        operands = [node.value]

    if any(is_string_node(operand) for operand in operands):
        yield Violation(Rule.STRINGS, path, node.lineno, 'String concatenation with `+` is not allowed.')
        return

    if any(is_collection_node(operand) for operand in operands):
        yield Violation(Rule.MERGING, path, node.lineno, 'Collections must not be merged with `+`.')


def call_violations(path: Path, node: ast.Call) -> Iterator[Violation]:
    """Reports ``str.join()`` and ``typing.cast()`` calls.

    Args:
        path: Path of the checked file.
        node: Call node to inspect.

    Yields:
        A violation for a forbidden call.
    """
    function = node.func

    if isinstance(function, ast.Name) and function.id == 'cast':
        yield Violation(Rule.TYPES, path, node.lineno, '`cast()` is not allowed.')
        return

    if not isinstance(function, ast.Attribute):
        return

    if function.attr == 'cast' and isinstance(function.value, ast.Name) and function.value.id == 'typing':
        yield Violation(Rule.TYPES, path, node.lineno, '`cast()` is not allowed.')
        return

    receiver = function.value
    is_string_receiver = is_string_node(receiver) or (isinstance(receiver, ast.Name) and receiver.id == 'str')

    if function.attr == 'join' and is_string_receiver:
        yield Violation(Rule.STRINGS, path, node.lineno, '`str.join()` is not allowed.')


def annotation_violation(path: Path, annotation: ast.expr | None, line: int, subject: str) -> Iterator[Violation]:
    """Reports a missing or bare generic annotation.

    Args:
        path: Path of the checked file.
        annotation: The annotation, or ``None`` when it is missing.
        line: Line to report.
        subject: Description of the annotated element.

    Yields:
        A violation when the annotation is missing or unparameterised.
    """
    if annotation is None:
        yield Violation(Rule.TYPES, path, line, '{} has no type annotation.'.format(subject))
        return

    if isinstance(annotation, ast.Name) and annotation.id in BARE_GENERICS:
        yield Violation(Rule.TYPES, path, line, '{} uses a bare `{}` without type parameters.'.format(subject, annotation.id))


def function_violations(path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterator[Violation]:
    """Reports a missing docstring and missing annotations of a function.

    Args:
        path: Path of the checked file.
        node: Function definition to inspect.

    Yields:
        One violation per missing docstring or annotation.
    """
    if ast.get_docstring(node) is None:
        yield Violation(Rule.DOCS, path, node.lineno, 'Function `{}` has no docstring.'.format(node.name))

    yield from annotation_violation(path, node.returns, node.lineno, 'Return value of `{}`'.format(node.name))

    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]

    if node.args.vararg is not None:
        arguments.append(node.args.vararg)

    if node.args.kwarg is not None:
        arguments.append(node.args.kwarg)

    for position, argument in enumerate(arguments):
        if position == 0 and argument.arg in ('self', 'cls'):
            continue

        yield from annotation_violation(path, argument.annotation, node.lineno, 'Parameter `{}`'.format(argument.arg))


def python_ast_violations(path: Path, tree: ast.Module) -> Iterator[Violation]:
    """Reports violations that are visible in the Python syntax tree.

    Args:
        path: Path of the checked file.
        tree: Parsed module.

    Yields:
        Every syntax-level violation in the module.
    """
    for node in ast.walk(tree):
        match node:
            case ast.IfExp():
                yield Violation(Rule.OPERATORS, path, node.lineno, 'Conditional expression (ternary) is not allowed.')
            case ast.BinOp(op=ast.Add()) | ast.AugAssign(op=ast.Add()):
                yield from addition_violations(path, node)
            case ast.Call():
                yield from call_violations(path, node)
            case ast.Name(id='Any') | ast.Attribute(attr='Any') | ast.alias(name='Any'):
                yield Violation(Rule.TYPES, path, node.lineno, 'The `Any` type is not allowed.')
            case ast.FunctionDef() | ast.AsyncFunctionDef():
                yield from function_violations(path, node)
            case ast.ClassDef():
                if ast.get_docstring(node) is None:
                    yield Violation(Rule.DOCS, path, node.lineno, 'Class `{}` has no docstring.'.format(node.name))


def check_python(path: Path, source: str) -> list[Violation]:
    """Checks a Python file.

    Args:
        path: Path of the file.
        source: Contents of the file.

    Returns:
        Every violation found in the file.
    """
    try:
        tree = ast.parse(source)
        violations = list(python_token_violations(path, source))
    except (SyntaxError, tokenize.TokenError) as error:
        return [Violation(Rule.TYPES, path, 1, 'File could not be parsed: {}'.format(error))]

    violations.extend(python_ast_violations(path, tree))

    return violations


def check_file(path: Path) -> list[Violation]:
    """Checks a single supported source file.

    Args:
        path: Path of the file.

    Returns:
        Every violation found in the file, sorted by line.
    """
    language = EXTENSIONS[path.suffix]
    source = path.read_text(encoding='utf-8', errors='replace')

    match language:
        case Language.RUST:
            violations = check_rust(path, source)
        case Language.PYTHON:
            violations = check_python(path, source)
        case Language.PHP:
            violations = check_php(path, source)
        case Language.TYPESCRIPT | Language.JAVASCRIPT:
            violations = check_script(path, source, language)

    return sorted(violations, key=lambda violation: violation.line)


def is_supported(path: Path) -> bool:
    """Tells whether the checker understands a file.

    Args:
        path: Path of the file.

    Returns:
        True for supported source files, excluding Blade templates and declaration files.
    """
    if path.name.endswith('.blade.php') or path.name.endswith('.d.ts'):
        return False

    return path.suffix in EXTENSIONS


def is_ignored(candidate: Path, root: Path) -> bool:
    """Tells whether a file lives in a dependency, cache or build directory.

    Args:
        candidate: File found while walking ``root``.
        root: Directory that was walked.

    Returns:
        True when any directory between ``root`` and the file is ignored.
    """
    return any(part in IGNORED_DIRECTORIES for part in candidate.relative_to(root).parts)


def collect_files(paths: Sequence[Path]) -> list[Path]:
    """Expands files and directories into the list of files to check.

    Args:
        paths: Files and directories given on the command line.

    Returns:
        Supported files in a stable order.
    """
    files: list[Path] = []

    for path in paths:
        if path.is_file():
            if is_supported(path):
                files.append(path)

            continue

        for candidate in sorted(path.rglob('*')):
            if candidate.is_file() and is_supported(candidate) and not is_ignored(candidate, path):
                files.append(candidate)

    return files


def build_report(files: Sequence[Path], violations: Sequence[Violation]) -> Report:
    """Builds the JSON report of a checker run.

    Args:
        files: Files that were checked.
        violations: Violations that were found.

    Returns:
        The report ready to be serialised.
    """
    counts: Counter[str] = Counter(violation.rule.value for violation in violations)

    return Report(
        files_checked=len(files),
        violation_count=len(violations),
        counts={rule.value: counts[rule.value] for rule in Rule},
        violations=[
            ViolationRecord(
                rule=violation.rule.value,
                path=str(violation.path),
                line=violation.line,
                message=violation.message,
            )
            for violation in violations
        ],
    )


def print_text_report(files: Sequence[Path], violations: Sequence[Violation]) -> None:
    """Prints the violations and a per-rule summary for humans.

    Args:
        files: Files that were checked.
        violations: Violations that were found.
    """
    report = build_report(files, violations)

    for record in report['violations']:
        print('{}:{}: [{}] {}'.format(record['path'], record['line'], record['rule'], record['message']))

    print()
    print('Checked {} file(s), found {} violation(s).'.format(report['files_checked'], report['violation_count']))

    for rule, count in report['counts'].items():
        print('  {}: {}'.format(rule, count))


def main(argv: Sequence[str] | None = None) -> int:
    """Runs the checker from the command line.

    Args:
        argv: Command line arguments without the program name. Defaults to ``sys.argv``.

    Returns:
        Process exit status: 0 when the code is clean, 1 when violations were found.
    """
    parser = argparse.ArgumentParser(description='Checks source files against the personal code style rules.')
    parser.add_argument('paths', nargs='+', type=Path, help='Files or directories to check.')
    parser.add_argument('--json', action='store_true', help='Print the report as JSON.')
    arguments = parser.parse_args(argv)
    paths: list[Path] = arguments.paths

    for path in paths:
        if not path.exists():
            parser.error('Path does not exist: {}'.format(path))

    files = collect_files(paths)
    violations: list[Violation] = []

    for path in files:
        violations.extend(check_file(path))

    if arguments.json:
        print(json.dumps(build_report(files, violations), indent=2))
    else:
        print_text_report(files, violations)

    if len(violations) > 0:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
