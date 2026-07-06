"""Enforcement test: hand-authored source must standardize Latin
transliteration of Hebrew het ("h with dot below") on NFC, i.e. the
precomposed U+1E25 / U+1E24 forms, never the decomposed "h"/"H" + COMBINING
DOT BELOW (U+0323) sequence. Comments must not use either Unicode form at
all -- plain ASCII "x"/"X" is used instead, since comments don't flow to
output.

Scope note: this test deliberately does NOT assert whole-file NFC
(unicodedata.normalize("NFC", text) == text). A blanket NFC pass also
reorders unrelated Hebrew combining marks (shin dot, sin dot, dagesh,
rafeh) according to Unicode canonical combining class, conflicting with the
deliberate non-Unicode-standard Hebrew mark order used across these repos.
So this test checks only the specific h-with-dot-below sequence, which has
no such ambiguity: composing "h"/"H" + U+0323 to U+1E25/U+1E24 is a simple,
unambiguous Latin-script composition.

Scope for THIS repo (phonetic-hbo):
  - gh-pages/ is entirely GENERATED phonetic-transcription output
    (per-chapter Bible HTML, testsuite HTML, CSS/font/image assets). It is
    full of het by design and is NOT hand-authored; its het self-corrects
    when the upstream generator (out of scope for this repo) emits NFC. It
    is excluded from this guard, both as a directory and via its binary
    assets.
  - binary files (by extension) are excluded.

Only two hand-authored text files exist in this repo (LICENSE.md and the
GitHub Pages workflow), plus this test tree; the sanity floor below is set
accordingly low.
"""
import subprocess
import unicodedata
import unittest
from pathlib import Path


def _discover_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return Path(result.stdout.strip())


REPO_ROOT = _discover_repo_root()

_COMBINING_DOT_BELOW = chr(0x0323)
_H_WITH_DOT_BELOW = chr(0x1E25)
_H_CAP_WITH_DOT_BELOW = chr(0x1E24)

_BINARY_EXTENSIONS = {
    ".png",
    ".woff2",
    ".woff",
    ".svg",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".ttf",
    ".otf",
    ".eot",
    ".zip",
    ".gz",
    ".pyc",
    ".exe",
    ".dll",
}

# Generated / non-hand-authored directory prefixes. gh-pages/ is the
# phonetic-transcription generator's GitHub Pages output.
_EXCLUDE_DIR_PREFIXES = (
    "gh-pages/",
)

_EXCLUDE_FILES: frozenset = frozenset()

_COMMENT_GLYPH_ALLOWLIST = frozenset()


def _is_binary(path: Path) -> bool:
    return path.suffix.lower() in _BINARY_EXTENSIONS


def _is_excluded(posix_rel: str) -> bool:
    if posix_rel in _EXCLUDE_FILES:
        return True
    return any(posix_rel.startswith(prefix) for prefix in _EXCLUDE_DIR_PREFIXES)


def _tracked_files_in_scope():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    in_scope = []
    for line in result.stdout.splitlines():
        rel = line.strip()
        if not rel:
            continue
        posix_rel = rel.replace("\\", "/")
        if _is_excluded(posix_rel):
            continue
        full = REPO_ROOT / rel
        if not full.is_file():
            continue
        if _is_binary(full):
            continue
        in_scope.append(posix_rel)
    return in_scope


class TestHDotBelowNfc(unittest.TestCase):
    """Hand-authored source must use precomposed h-with-dot-below, never
    the decomposed sequence, and must never use either Unicode form in a
    '#'-led comment (plain ASCII "x"/"X" instead)."""

    @classmethod
    def setUpClass(cls):
        cls.in_scope_files = _tracked_files_in_scope()
        # Sanity floor: this repo has only a couple of hand-authored text
        # files (LICENSE.md, the Pages workflow, this test tree), so the
        # floor is intentionally low. It still catches an exclusion filter
        # that accidentally drops everything.
        assert len(cls.in_scope_files) >= 2, (
            f"Only {len(cls.in_scope_files)} files in scope -- exclusion "
            "filters may be too broad."
        )

    def test_no_decomposed_h_dot_below_in_hand_authored_files(self):
        offenders = []
        for posix_rel in self.in_scope_files:
            full = REPO_ROOT / posix_rel
            text = full.read_text(encoding="utf-8")
            for i, ch in enumerate(text):
                if (
                    ch in ("h", "H")
                    and i + 1 < len(text)
                    and text[i + 1] == _COMBINING_DOT_BELOW
                ):
                    line_no = text.count("\n", 0, i) + 1
                    offenders.append(f"{posix_rel}:{line_no}")
                    break
        self.assertEqual(
            offenders,
            [],
            "Found decomposed h-with-dot-below (h/H + COMBINING DOT BELOW) "
            "in hand-authored files; run the NFC migration or fix by hand: "
            f"{offenders}",
        )

    @staticmethod
    def _comment_has_h_dot_below(comment: str) -> bool:
        """True if `comment` contains h-with-dot-below specifically (either
        decomposed "h"/"H" + U+0323, or precomposed U+1E25/U+1E24) -- NOT
        just any U+0323, since U+0323 also legitimately appears on other
        base letters (e.g. "S" in "Sere", "t" in "qetannah"), which is a
        different character combination and out of scope for this issue."""
        if _H_WITH_DOT_BELOW in comment or _H_CAP_WITH_DOT_BELOW in comment:
            return True
        for i, ch in enumerate(comment):
            if (
                ch in ("h", "H")
                and i + 1 < len(comment)
                and comment[i + 1] == _COMBINING_DOT_BELOW
            ):
                return True
        return False

    def test_comments_use_ascii_not_h_dot_below(self):
        offenders = []
        for posix_rel in self.in_scope_files:
            if not posix_rel.endswith(".py"):
                continue
            if posix_rel in _COMMENT_GLYPH_ALLOWLIST:
                continue
            full = REPO_ROOT / posix_rel
            text = full.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.split("\n"), start=1):
                hash_idx = line.find("#")
                if hash_idx == -1:
                    continue
                comment = line[hash_idx:]
                if self._comment_has_h_dot_below(comment):
                    offenders.append(f"{posix_rel}:{line_no}")
        self.assertEqual(
            offenders,
            [],
            "Found h-with-dot-below (either Unicode form) in a '#' comment; "
            f"use plain ASCII x/X instead: {offenders}",
        )

    def test_h_dot_below_composition_is_canonically_lossless(self):
        """Spot-check unicodedata agrees h/H + U+0323 composes to
        U+1E25/U+1E24, guarding the core assumption behind this test."""
        self.assertEqual(
            unicodedata.normalize("NFC", "h" + _COMBINING_DOT_BELOW),
            _H_WITH_DOT_BELOW,
        )
        self.assertEqual(
            unicodedata.normalize("NFC", "H" + _COMBINING_DOT_BELOW),
            _H_CAP_WITH_DOT_BELOW,
        )

    def test_comment_detector_flags_decomposed_and_precomposed_h_dot_below(self):
        self.assertTrue(
            self._comment_has_h_dot_below("# guttural / h" + _COMBINING_DOT_BELOW + " slot")
        )
        self.assertTrue(
            self._comment_has_h_dot_below("# guttural / " + _H_WITH_DOT_BELOW + " slot")
        )
        self.assertTrue(
            self._comment_has_h_dot_below("# Capital H" + _COMBINING_DOT_BELOW + "olam")
        )
        self.assertTrue(
            self._comment_has_h_dot_below("# Capital " + _H_CAP_WITH_DOT_BELOW + "olam")
        )

    def test_comment_detector_ignores_dot_below_on_other_base_letters(self):
        # U+0323 legitimately appears on letters other than h/H (e.g. "S" in
        # "Sere", "t" in "qetannah"); that is a different character
        # combination and must NOT be flagged by this check.
        self.assertFalse(
            self._comment_has_h_dot_below("# Closed, S" + _COMBINING_DOT_BELOW + "ere-vowelled")
        )
        self.assertFalse(
            self._comment_has_h_dot_below("# shalshelet qet" + _COMBINING_DOT_BELOW + "annah")
        )


if __name__ == "__main__":
    unittest.main()
