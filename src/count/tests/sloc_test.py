import unittest
from contextlib import redirect_stdout
from pathlib import Path

from count.sloc import LineCounter, elide_comment_span, get_source_files, main

_REPOS = Path("/tmp/repos")

SOURCES = [
    _REPOS / "llama.cpp",
    _REPOS / "docker-php-tutorial",
]

INITIAL_SOURCES = get_source_files(SOURCES[0])[:3]


class SlocTest(unittest.TestCase):

    def test_main(self) -> None:
        with redirect_stdout(None):
            main(SOURCES[0])

    def test_count_lines(self) -> None:
        for folder in SOURCES:
            assert folder.is_dir(), "Please run: $ make count"

        self.assertEqual(
            [
                "/tmp/repos/llama.cpp/tests/test-arg-parser.cpp",
                "/tmp/repos/llama.cpp/tests/test-llama-grammar.cpp",
                "/tmp/repos/llama.cpp/tests/test-rope.cpp",
            ],
            list(map(str, INITIAL_SOURCES)),
        )

        cnt = LineCounter(INITIAL_SOURCES[0])
        self.assertEqual(
            {"blank": 26, "comment": 8, "code": 97},
            cnt.__dict__,
        )

        cnt = LineCounter(_REPOS / "llama.cpp/src/llama-vocab.cpp")
        self.assertEqual(
            {"blank": 287, "comment": 197, "code": 1500},
            cnt.__dict__,
        )

    def test_expand_comments(self) -> None:
        cnt = LineCounter(Path("/dev/null"))
        lines = [
            "zero /* comment */ calories",
            "/* one",
            " * two",
            " * three",
            " */ four",
            "five",
        ]
        self.assertEqual(
            [
                "zero  calories",
                "// // /* one",
                "//  * two",
                "//  * three",
                "//  four",
                "five",
            ],
            list(cnt.expand_comments(lines)),
        )

    def test_regex(self) -> None:
        self.assertEqual("", elide_comment_span("/* hello */"))
        self.assertEqual("", elide_comment_span("/* a */ b /* c */"))
        self.assertEqual("d  h", elide_comment_span("d /* e */ f /* g */ h"))
