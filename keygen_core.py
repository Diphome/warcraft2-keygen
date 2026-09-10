"""Core logic for the Warcraft II CD-key generator.

This module holds the reverse-engineered key validation algorithm and the
random key generator. It is intentionally free of any I/O (no prints, no
argument parsing) so that it can be reused by the CLI scripts and covered by
tests.

The validation algorithm is a faithful reimplementation of the routine found
in the game and must not be altered: generated keys are only useful if they
match the game's own check bit for bit.
"""

import random
from typing import List, Tuple

# Lookup table indexed by the ASCII code of a CD-key character. Positions that
# do not correspond to an authorized character hold the sentinel value 255.
LOOKUP_TABLE: List[int] = [
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 0, 255, 1, 255, 2, 3, 4, 5, 255, 255, 255, 255, 255,
    255, 255, 255, 6, 7, 8, 9, 10, 11, 12, 255, 13, 14, 255, 15, 16, 255,
    17, 255, 18, 255, 19, 255, 20, 21, 22, 255, 23, 255, 255, 255, 255,
    255, 255, 255, 6, 7, 8, 9, 10, 11, 12, 255, 13, 14, 255, 15, 16, 255,
    17, 255, 18, 255, 19, 255, 20, 21, 22, 255, 23, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
]

# Characters allowed to appear in a CD-key.
AUTHORIZED_CHARS: Tuple[str, ...] = (
    '2', '4', '6', '7', '8', '9',
    'B', 'C', 'D', 'E', 'F', 'G', 'H',
    'J', 'K', 'M', 'N', 'P', 'R', 'T',
    'V', 'W', 'X', 'Z', 'b', 'c', 'd',
    'e', 'f', 'g', 'h', 'j', 'k', 'm',
    'n', 'p', 'r', 't', 'v', 'w', 'x',
    'z',
)

_AUTHORIZED_SET = frozenset(AUTHORIZED_CHARS)

KEY_LENGTH = 16


def has_only_authorized_chars(key: str) -> bool:
    """Return True if every character of ``key`` is an authorized character."""
    return all(c in _AUTHORIZED_SET for c in key)


def _decode_char(letter: str) -> int:
    """Map a CD-key character to its numeric value (game's ``calculus_01``)."""
    v1 = letter.lower()  # A maj letter is normalised to lowercase.
    if ord(v1) < 97:
        return ord(v1) - 48  # It's a digit: subtract '0'.
    return ord(v1) - 87  # It's a letter: subtract ('a' - 10).


def _encode_nibble(value: int) -> int:
    """Map a 4-bit value to its hex-char ASCII code (game's ``calculus_02``)."""
    v1 = value & 15
    if v1 < 10:
        return v1 + 48  # 0-9
    return v1 + 55  # A-F


def derive_key(cdkey: str) -> Tuple[str, int, int]:
    """Run the game's derivation on ``cdkey``.

    Returns a tuple ``(generated_key, principal_key_score, key_score)``.
    The key is valid when the two scores are equal.
    """
    new_key_decimal: List[int] = []
    counter = 0
    v2 = 1
    principal_key_score = 0

    # First pass: derive a new key and accumulate the principal score.
    for _ in range(KEY_LENGTH // 2):
        v4 = 3 * LOOKUP_TABLE[ord(cdkey[counter])]
        v5 = LOOKUP_TABLE[ord(cdkey[counter + 1])] + 8 * v4

        if v5 >= 256:
            v5 -= 256
            # Inclusive OR, preserving the reverse-engineered expression.
            principal_key_score = principal_key_score | v2 + principal_key_score

        new_key_decimal.append(_encode_nibble(v5 >> 4))
        new_key_decimal.append(_encode_nibble(v5 & 15))
        counter += 2
        v2 *= 2

    generated_key = ''.join(chr(c) for c in new_key_decimal)

    # Second pass: compute the score of the derived key.
    v4 = 3
    counter = 0
    for _ in cdkey:
        v6 = chr(new_key_decimal[counter])
        # Each character of the derived key must be ascii 0-9, a-z or A-Z.
        if not (('0' <= v6 <= '9') or ('a' <= v6 <= 'z') or ('A' <= v6 <= 'Z')):
            break
        v4 = v4 + (2 * v4 ^ _decode_char(v6))
        counter += 1
    key_score = v4 & 255

    return generated_key, principal_key_score, key_score


def is_valid_key(cdkey: str) -> bool:
    """Return True if ``cdkey`` is a valid Warcraft II CD-key."""
    _, principal_key_score, key_score = derive_key(cdkey)
    return principal_key_score == key_score


def generate_random_key(rng: random.Random = random) -> str:
    """Generate a random candidate key made of authorized characters."""
    return ''.join(rng.choices(AUTHORIZED_CHARS, k=KEY_LENGTH))


def find_valid_key(rng: random.Random = random) -> Tuple[str, int]:
    """Brute-force a valid key.

    Returns ``(valid_key, failures)`` where ``failures`` is the number of
    rejected candidates tried before a valid one was found.
    """
    failures = 0
    candidate = generate_random_key(rng)
    while not is_valid_key(candidate):
        failures += 1
        candidate = generate_random_key(rng)
    return candidate, failures
