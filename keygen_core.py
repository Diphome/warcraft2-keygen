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


# ---------------------------------------------------------------------------
# Constructive generation (no brute force)
# ---------------------------------------------------------------------------
#
# The validation is separable, which lets us build a valid key directly:
#
#   * ``principal_key_score`` is an 8-bit mask: bit i is set iff pair i carries
#     (i.e. ``b + 24*a >= 256``). Each bit depends only on its own pair.
#   * ``key_score`` depends only on the 16 nibbles of the derived key, in order.
#
# So we can fix the first 7 pairs (locking bits 0..6 of the score and the
# running key_score state), then enumerate the 576 possibilities of the last
# pair and keep the first one for which key_score == principal_key_score.

# Each authorized character maps to a value in 0..23; several characters can
# share the same value (e.g. 'B' and 'b'). Map every distinct value to the
# characters that produce it so the constructed key can still vary.
_VALUE_TO_CHARS: dict = {}
for _ch in AUTHORIZED_CHARS:
    _VALUE_TO_CHARS.setdefault(LOOKUP_TABLE[ord(_ch)], []).append(_ch)
_DISTINCT_VALUES: Tuple[int, ...] = tuple(sorted(_VALUE_TO_CHARS))


def _pair_carry_and_nibbles(a: int, b: int) -> Tuple[int, int, int]:
    """For a pair of values, return (carry, high_nibble, low_nibble)."""
    v5 = b + 24 * a
    carry = 0
    if v5 >= 256:
        v5 -= 256
        carry = 1
    return carry, (v5 >> 4) & 15, v5 & 15


def _key_score_step(v4: int, nibble: int) -> int:
    return v4 + (2 * v4 ^ nibble)


def construct_valid_key(rng: random.Random = random) -> str:
    """Build a valid key directly, without brute-forcing candidates.

    Runs in roughly constant time: one random 7-pair prefix plus at most 576
    constant-time checks of the final pair (a matching prefix is found on the
    first try in the overwhelming majority of cases).
    """
    while True:
        prefix = [(rng.choice(_DISTINCT_VALUES), rng.choice(_DISTINCT_VALUES))
                  for _ in range(7)]

        # Score mask and running key_score state after the first 7 pairs.
        partial_score = 0
        v4 = 3
        for i, (a, b) in enumerate(prefix):
            carry, hi, lo = _pair_carry_and_nibbles(a, b)
            if carry:
                partial_score |= 1 << i
            v4 = _key_score_step(v4, hi)
            v4 = _key_score_step(v4, lo)

        # Enumerate the last pair; keep the first that balances the scores.
        for a in _DISTINCT_VALUES:
            for b in _DISTINCT_VALUES:
                carry, hi, lo = _pair_carry_and_nibbles(a, b)
                full_score = partial_score | (carry << 7)
                v4_final = _key_score_step(v4, hi)
                v4_final = _key_score_step(v4_final, lo)
                if (v4_final & 255) == full_score:
                    pairs = prefix + [(a, b)]
                    return ''.join(
                        rng.choice(_VALUE_TO_CHARS[value])
                        for pair in pairs for value in pair
                    )
