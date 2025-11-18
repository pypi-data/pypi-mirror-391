"""Command-line interface for mkdocs-quiz."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def convert_quiz_block(quiz_content: str) -> str:
    """Convert old quiz syntax to new markdown-style syntax.

    Args:
        quiz_content: The content inside <?quiz?> tags in old format.

    Returns:
        The converted quiz content in new format.
    """
    lines = quiz_content.strip().split("\n")

    question = None
    answers: list[tuple[str, str]] = []  # (type, text)
    content_lines: list[str] = []
    options: list[str] = []
    in_content = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Parse question
        if line.startswith("question:"):
            question = line.split("question:", 1)[1].strip()
        # Parse options that should be preserved
        elif line.startswith(("show-correct:", "auto-submit:", "disable-after-submit:")):
            options.append(line)
        # Parse content separator
        elif line == "content:":
            in_content = True
        # Parse answers
        elif line.startswith("answer-correct:"):
            answer_text = line.split("answer-correct:", 1)[1].strip()
            answers.append(("correct", answer_text))
        elif line.startswith("answer:"):
            answer_text = line.split("answer:", 1)[1].strip()
            answers.append(("incorrect", answer_text))
        # Content section
        elif in_content:
            content_lines.append(line)

    # Build new quiz format
    result = ["<quiz>"]

    # Add question
    if question:
        result.append(question)

    # Add options
    for opt in options:
        result.append(opt)

    # Add answers in new format
    for answer_type, answer_text in answers:
        if answer_type == "correct":
            result.append(f"- [x] {answer_text}")
        else:
            result.append(f"- [ ] {answer_text}")

    # Add content if present
    if content_lines:
        result.append("")  # Empty line before content
        result.extend(content_lines)

    result.append("</quiz>")

    return "\n".join(result)


def migrate_file(file_path: Path, dry_run: bool = False) -> tuple[int, bool]:
    """Migrate quiz blocks in a single file.

    Args:
        file_path: Path to the markdown file.
        dry_run: If True, don't write changes to disk.

    Returns:
        Tuple of (number of quizzes converted, whether file was modified).
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        return 0, False

    # Pattern to match quiz blocks
    quiz_pattern = r"<\?quiz\?>(.*?)<\?/quiz\?>"

    def replace_quiz(match: re.Match[str]) -> str:
        return convert_quiz_block(match.group(1))

    # Count how many quizzes will be converted
    quiz_count = len(re.findall(quiz_pattern, content, re.DOTALL))

    if quiz_count == 0:
        return 0, False

    # Replace all quiz blocks
    new_content = re.sub(quiz_pattern, replace_quiz, content, flags=re.DOTALL)

    if new_content == content:
        return 0, False

    if not dry_run:
        # Write new content
        file_path.write_text(new_content, encoding="utf-8")

    return quiz_count, True


def migrate(directory: str, dry_run: bool = False) -> None:
    """Migrate quiz blocks from old syntax to new markdown-style syntax.

    Converts old question:/answer:/content: syntax to the new cleaner
    markdown checkbox syntax (- [x] / - [ ]).

    Args:
        directory: Directory to search for markdown files.
        dry_run: Show what would be changed without modifying files.
    """
    # Convert string to Path and validate
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)

    if not dir_path.is_dir():
        print(f"Error: '{directory}' is not a directory")
        sys.exit(1)

    print("MkDocs Quiz Syntax Migration")
    print(f"Searching for quiz blocks in: {dir_path}")
    if dry_run:
        print("DRY RUN MODE - No files will be modified")
    print()

    # Find all markdown files
    md_files = list(dir_path.rglob("*.md"))

    if not md_files:
        print("No markdown files found")
        sys.exit(0)

    total_files_modified = 0
    total_quizzes = 0

    for file_path in md_files:
        quiz_count, modified = migrate_file(file_path, dry_run=dry_run)

        if modified:
            total_files_modified += 1
            total_quizzes += quiz_count
            quiz_text = "quiz" if quiz_count == 1 else "quizzes"
            if dry_run:
                print(
                    f"  Would convert {quiz_count} {quiz_text} in: {file_path.relative_to(dir_path)}"
                )
            else:
                print(f"  Converted {quiz_count} {quiz_text} in: {file_path.relative_to(dir_path)}")

    print()
    if total_files_modified == 0:
        print("No quiz blocks found to migrate")
    else:
        print("Migration complete!")
        action = "would be" if dry_run else "were"
        print(f"  Files {action} modified: {total_files_modified}")
        print(f"  Quizzes {action} converted: {total_quizzes}")

        if dry_run:
            print()
            print("Run without --dry-run to apply changes")


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="mkdocs-quiz",
        description="MkDocs Quiz CLI - Migrate quiz blocks from old syntax to new markdown-style syntax",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Migrate subcommand
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Migrate quiz blocks from old syntax to new markdown-style syntax",
    )
    migrate_parser.add_argument(
        "directory",
        nargs="?",
        default="docs",
        help="Directory to search for markdown files (default: docs)",
    )
    migrate_parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    if args.command == "migrate":
        migrate(args.directory, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
