"""Tests for the personal code style checker."""

import json
from pathlib import Path
from textwrap import dedent

import pytest

from check_style import Rule, Violation, check_file, main

CLEAN_SOURCES: list[tuple[str, str]] = [
    (
        'report.rs',
        '''
        //! Builds language reports.

        use std::collections::BTreeMap;

        /// Label used for repositories without a language.
        pub const UNKNOWN_LANGUAGE: &str = "Unknown";

        /// Errors returned while building a report.
        #[derive(Debug, thiserror::Error)]
        pub enum ReportError {
            /// The language code is not known.
            #[error("unknown language code {0}")]
            UnknownLanguage(String),
        }

        /// A repository with its primary language.
        pub struct Repository {
            /// Name of the repository.
            pub name: String,
            /// Primary language of the repository.
            pub language: Option<String>,
        }

        /// Returns the language of a repository or the unknown label.
        pub fn language_of(repository: &Repository) -> String {
            repository.language.clone().unwrap_or_else(|| UNKNOWN_LANGUAGE.to_owned())
        }

        /// Formats a report line.
        pub fn line(language: &str, count: usize) -> String {
            format!("{}: {}", language, count)
        }

        /// Builds the path of the report file.
        pub fn report_path(base: &std::path::Path) -> std::path::PathBuf {
            base.join("reports")
        }

        /// Unit tests for the report.
        #[cfg(test)]
        mod tests {
            use super::*;

            /// Ensures the line contains the language and the count.
            #[test]
            fn formats_line() {
                let text = line("Rust", 2);

                assert_eq!(text, "Rust: 2".to_owned());
                assert!(BTreeMap::<String, String>::new().is_empty());
                assert_eq!(Some(1).unwrap(), 1);
            }
        }
        ''',
    ),
    (
        'CouponService.php',
        '''
        <?php

        declare(strict_types=1);

        namespace App\\Billing;

        use Illuminate\\Support\\Arr;

        /**
         * Describes applied coupons.
         */
        final class CouponService
        {
            /**
             * Builds a summary of the coupon codes.
             *
             * @param list<string> $codes Applied coupon codes.
             */
            #[Pure]
            public function summary(array $codes): string
            {
                if (count($codes) === 0 or $codes === ['']) {
                    return 'No coupons';
                }

                return sprintf('Coupons: %s', Arr::join($codes, ', '));
            }
        }
        ''',
    ),
    (
        'language-report.ts',
        '''
        import { format } from 'node:util';
        import path from 'node:path';

        /**
         * Repositories that share a language.
         */
        export interface LanguageGroup {
            /** Language name. */
            readonly language: string;
            /** Repository names. */
            readonly repositories: readonly string[];
        }

        /**
         * Formats one line per group.
         *
         * @param groups - Groups to format.
         * @returns Report lines.
         */
        export function reportLines(groups: readonly LanguageGroup[]): readonly string[] {
            const list = new Intl.ListFormat('en', { style: 'short', type: 'unit' });

            return groups.map((group) => format('%s: %s', group.language, list.format(group.repositories)));
        }

        /**
         * Resolves the report directory.
         *
         * @param base - Base directory.
         * @returns The report directory.
         */
        export function reportDirectory(base: string): string {
            return path.join(base, 'reports');
        }
        ''',
    ),
    (
        'reports.py',
        '''
        #!/usr/bin/env python3
        """Department reports."""

        from collections.abc import Sequence


        def report_lines(names: Sequence[str]) -> list[str]:
            """Formats one line per name.

            Args:
                names: Names to format.

            Returns:
                The formatted lines.
            """
            label = names[0] or 'Unknown'
            lines = ['{}: {}'.format(label, name) for name in names]
            lines.extend(['End of report'])

            return lines
        ''',
    ),
]

VIOLATING_SOURCES: list[tuple[str, str, Rule]] = [
    ('comment.rs', '//! Module.\n\n// explains the next line\n', Rule.COMMENTS),
    ('captured.rs', '//! Module.\n\n/// Greets.\nfn greet(name: &str) -> String {\n    format!("Hello {name}")\n}\n', Rule.STRINGS),
    ('plus.rs', '//! Module.\n\n/// Joins.\nfn both(a: String, b: &str) -> String {\n    a + &b\n}\n', Rule.STRINGS),
    ('join.rs', '//! Module.\n\n/// Lists.\nfn list(names: &[String]) -> String {\n    names.join(", ")\n}\n', Rule.STRINGS),
    ('concat.rs', '//! Module.\n\n/// Merges.\nfn merge(a: &[u8], b: &[u8]) -> Vec<u8> {\n    [a, b].concat()\n}\n', Rule.MERGING),
    ('or.rs', '//! Module.\n\n/// Checks.\nfn check(a: bool, b: bool) -> bool {\n    a || b\n}\n', Rule.OPERATORS),
    ('unwrap.rs', '//! Module.\n\n/// Parses.\nfn parse(text: &str) -> u32 {\n    text.parse().unwrap()\n}\n', Rule.TYPES),
    ('cast.rs', '//! Module.\n\n/// Narrows.\nfn narrow(value: u64) -> u32 {\n    value as u32\n}\n', Rule.TYPES),
    ('value.rs', '//! Module.\n\n/// Reads.\nfn read(value: serde_json::Value) {}\n', Rule.TYPES),
    ('undocumented.rs', '//! Module.\n\npub fn run() {}\n', Rule.DOCS),
    ('field.rs', '//! Module.\n\n/// User.\npub struct User {\n    pub name: String,\n}\n', Rule.DOCS),
    ('module.rs', '/// Runs.\npub fn run() {}\n', Rule.DOCS),
    ('ternary.php', '<?php\n\ndeclare(strict_types=1);\n\n$label = $isAdmin ? \'Admin\' : \'User\';\n', Rule.OPERATORS),
    ('coalesce.php', '<?php\n\ndeclare(strict_types=1);\n\n$limit = $input ?? 10;\n', Rule.OPERATORS),
    ('nullsafe.php', '<?php\n\ndeclare(strict_types=1);\n\n$city = $user?->profile;\n', Rule.OPERATORS),
    ('concat.php', '<?php\n\ndeclare(strict_types=1);\n\n$text = \'Hello \' . $name;\n', Rule.STRINGS),
    ('interpolation.php', '<?php\n\ndeclare(strict_types=1);\n\n$text = "Hello $name";\n', Rule.STRINGS),
    ('implode.php', '<?php\n\ndeclare(strict_types=1);\n\n$text = implode(\', \', $names);\n', Rule.STRINGS),
    ('strict.php', '<?php\n\n$value = 1;\n', Rule.TYPES),
    ('mixed.php', '<?php\n\ndeclare(strict_types=1);\n\n/**\n * Runs.\n */\nfunction run(mixed $value): void\n{\n}\n', Rule.TYPES),
    ('untyped.php', '<?php\n\ndeclare(strict_types=1);\n\n/**\n * Runs.\n */\nfunction run($value)\n{\n}\n', Rule.TYPES),
    ('template.ts', 'const greeting = `Hello ${name}`;\n', Rule.STRINGS),
    ('any.ts', '/**\n * Runs.\n */\nexport function run(value: any): void {}\n', Rule.TYPES),
    ('chain.ts', 'const city = user?.profile;\n', Rule.OPERATORS),
    ('suppress.ts', '// @ts-ignore\nrun();\n', Rule.TYPES),
    ('member.ts', '/**\n * User.\n */\nclass User {\n    name: string;\n}\n', Rule.DOCS),
    ('fstring.py', 'greeting = f"Hello {name}"\n', Rule.STRINGS),
    ('ifexp.py', 'label = "Admin" if is_admin else "User"\n', Rule.OPERATORS),
    ('strjoin.py', 'text = ", ".join(names)\n', Rule.STRINGS),
    ('listplus.py', 'items = [1] + more\n', Rule.MERGING),
    ('anytype.py', 'from typing import Any\n', Rule.TYPES),
    ('nodoc.py', 'def run() -> None:\n    pass\n', Rule.DOCS),
    ('noannotation.py', 'def run(value):\n    """Runs."""\n', Rule.TYPES),
]


def write_source(directory: Path, name: str, source: str) -> Path:
    """Writes a dedented source file into a directory.

    Args:
        directory: Directory to write into.
        name: File name, whose extension selects the language.
        source: File contents, dedented and stripped of the leading blank line.

    Returns:
        Path of the written file.
    """
    path = directory / name
    path.write_text(dedent(source).lstrip('\n'), encoding='utf-8')

    return path


def rules_of(violations: list[Violation]) -> set[Rule]:
    """Collects the rule groups of the given violations.

    Args:
        violations: Violations to inspect.

    Returns:
        The distinct rule groups.
    """
    return {violation.rule for violation in violations}


@pytest.mark.parametrize(('name', 'source'), CLEAN_SOURCES)
def test_clean_source_has_no_violations(tmp_path: Path, name: str, source: str) -> None:
    """Ensures code that follows every rule is reported as clean."""
    path = write_source(tmp_path, name, source)

    violations = check_file(path)

    assert violations == []


@pytest.mark.parametrize(('name', 'source', 'rule'), VIOLATING_SOURCES)
def test_violating_source_is_reported(tmp_path: Path, name: str, source: str, rule: Rule) -> None:
    """Ensures each forbidden construct is reported under its rule group."""
    path = write_source(tmp_path, name, source)

    violations = check_file(path)

    assert rule in rules_of(violations)


def test_inherited_untyped_php_property_with_var_doc_is_allowed(tmp_path: Path) -> None:
    """Ensures an Eloquent-style untyped property documented with `@var` is accepted."""
    source = '<?php\n\ndeclare(strict_types=1);\n\n/**\n * Coupon.\n */\nclass Coupon\n{\n    /**\n     * Mass assignable attributes.\n     *\n     * @var list<string>\n     */\n    protected $fillable = [];\n}\n'
    path = write_source(tmp_path, 'Coupon.php', source)

    violations = check_file(path)

    assert violations == []


def test_untyped_php_property_without_var_doc_is_reported(tmp_path: Path) -> None:
    """Ensures an untyped property without an `@var` type is reported."""
    source = '<?php\n\ndeclare(strict_types=1);\n\n/**\n * Coupon.\n */\nclass Coupon\n{\n    /**\n     * Mass assignable attributes.\n     */\n    protected $fillable = [];\n}\n'
    path = write_source(tmp_path, 'Coupon.php', source)

    violations = check_file(path)

    assert rules_of(violations) == {Rule.TYPES}


def test_rust_unwrap_is_allowed_in_integration_tests(tmp_path: Path) -> None:
    """Ensures panicking calls are accepted in files under the tests directory."""
    directory = tmp_path / 'tests'
    directory.mkdir()
    path = write_source(directory, 'cli.rs', '//! CLI tests.\n\n/// Runs.\n#[test]\nfn runs() {\n    run().unwrap();\n}\n')

    violations = check_file(path)

    assert violations == []


def test_violation_points_to_offending_line(tmp_path: Path) -> None:
    """Ensures the reported line number matches the offending line."""
    path = write_source(tmp_path, 'line.py', '"""Module."""\n\nvalue = 1\nlabel = "a" if value else "b"\n')

    violations = check_file(path)

    assert [violation.line for violation in violations] == [4]


def test_main_returns_zero_for_clean_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Ensures the command exits successfully when no violation is found."""
    write_source(tmp_path, 'clean.py', '"""Module."""\n')

    status = main([str(tmp_path)])

    assert status == 0
    assert 'found 0 violation(s)' in capsys.readouterr().out


def test_main_prints_json_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Ensures the JSON report lists violations and per-rule counts."""
    write_source(tmp_path, 'dirty.py', '# note\n')

    status = main([str(tmp_path), '--json'])
    report = json.loads(capsys.readouterr().out)

    assert status == 1
    assert report['violation_count'] == 1
    assert report['counts']['comments'] == 1


def test_main_skips_dependency_directories(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Ensures vendored and built files are not checked."""
    vendor = tmp_path / 'vendor'
    vendor.mkdir()
    write_source(vendor, 'dirty.php', '<?php\n// vendored\n')

    status = main([str(tmp_path)])

    assert status == 0
    assert 'Checked 0 file(s)' in capsys.readouterr().out
