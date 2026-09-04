import re

_DEVANAGARI_PATTERN = re.compile(r"[ऀ-ॿ]")
_LATIN_PATTERN = re.compile(r"[A-Za-z]")

_DEVANAGARI_LANGUAGES = {"hindi", "marathi"}
_LATIN_LANGUAGES = {"english"}


def detect_script(text: str) -> str | None:
    """
    Coarse script detection based on Unicode ranges.

    Returns "devanagari", "latin", or None if `text` has no
    script-identifying characters (empty, numeric-only, etc.).
    """

    devanagari_count = len(_DEVANAGARI_PATTERN.findall(text))
    latin_count = len(_LATIN_PATTERN.findall(text))

    if devanagari_count == 0 and latin_count == 0:
        return None

    return "devanagari" if devanagari_count > latin_count else "latin"


def expected_script(language: str) -> str | None:
    """
    Expected script for a requested output language.

    Returns None for languages this check doesn't cover.
    Hindi and Marathi both use Devanagari and can't be told
    apart by script alone, so a mismatch between the two is
    not detectable this way.
    """

    normalized = language.strip().lower()

    if normalized in _LATIN_LANGUAGES:
        return "latin"

    if normalized in _DEVANAGARI_LANGUAGES:
        return "devanagari"

    return None


def matches_expected_language(text: str, language: str) -> bool:
    """
    True if `text` appears to be written in the script expected
    for `language`. Always True for languages or text this
    coarse check can't confidently judge, so it never blocks on
    a false positive.
    """

    expected = expected_script(language)

    if expected is None:
        return True

    actual = detect_script(text)

    if actual is None:
        return True

    return actual == expected
