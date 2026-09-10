#!/usr/bin/env python3
"""Generate valid Warcraft II CD-keys by brute force."""

import argparse
import random
import time

from keygen_core import derive_key, find_valid_key


def _report_key(cdkey: str) -> None:
    """Print the derivation details for a single valid key."""
    generated_key, principal_key_score, key_score = derive_key(cdkey)
    print(f'Using given key         : {cdkey}')
    print(f'Generated key is        : {generated_key}')
    print(f'CD-key score            : {principal_key_score}')
    print(f'Generated key score     : {key_score}')


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-n', '--count', type=int, default=1,
        help='number of valid keys to generate (default: 1)',
    )
    parser.add_argument(
        '-s', '--seed', type=int, default=None,
        help='seed the random generator for reproducible output',
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='print only the valid keys, one per line',
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    if args.count < 1:
        raise SystemExit('--count must be a positive integer')

    rng = random.Random(args.seed)
    start_time = time.time()
    total_failures = 0

    for _ in range(args.count):
        cdkey, failures = find_valid_key(rng)
        total_failures += failures
        if args.quiet:
            print(cdkey)
        else:
            _report_key(cdkey)
            print(f'Valid key: {cdkey} (after {failures} failures)')
            print('-' * 40)

    if not args.quiet:
        elapsed = time.time() - start_time
        print(
            f'Generated {args.count} valid key(s) in {elapsed:.4f} seconds '
            f'after {total_failures} total failures.'
        )


if __name__ == '__main__':
    main()
