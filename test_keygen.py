"""Tests for the Warcraft II keygen core logic."""

import random

import keygen_core


def test_generated_key_has_expected_length_and_charset():
    rng = random.Random(1234)
    key = keygen_core.generate_random_key(rng)
    assert len(key) == keygen_core.KEY_LENGTH
    assert keygen_core.has_only_authorized_chars(key)


def test_found_key_is_valid():
    rng = random.Random(1234)
    key, failures = keygen_core.find_valid_key(rng)
    assert failures >= 0
    assert keygen_core.is_valid_key(key)


def test_find_valid_key_is_reproducible_with_seed():
    key_a, _ = keygen_core.find_valid_key(random.Random(42))
    key_b, _ = keygen_core.find_valid_key(random.Random(42))
    assert key_a == key_b


def test_known_valid_key():
    # Regression value captured from the original implementation.
    assert keygen_core.is_valid_key('greMmeCJBG262Kr9')


def test_has_only_authorized_chars_rejects_unknown_char():
    assert not keygen_core.has_only_authorized_chars('AAAAAAAAAAAAAAAA')


def test_derive_key_matches_reference():
    generated, principal, key_score = keygen_core.derive_key('greMmeCJBG262Kr9')
    assert generated == '1AE771B59B020EB5'
    assert principal == key_score == 133


if __name__ == '__main__':
    import sys
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print(f'PASS {name}')
            except AssertionError as exc:
                failures += 1
                print(f'FAIL {name}: {exc}')
    sys.exit(1 if failures else 0)
