#!/usr/bin/env python3
"""Collect and report statistics about Warcraft II CD-key generation."""

import argparse
import random
import time

from keygen_core import find_valid_key


def collect_stats(duration: float, rng: random.Random):
    """Generate keys for ``duration`` seconds.

    Returns ``(times, failures)`` two parallel lists, one entry per key found.
    """
    times = []
    failures = []
    start_time = time.time()
    while (time.time() - start_time) < duration:
        start_process_time = time.time()
        _, failure_count = find_valid_key(rng)
        times.append(time.time() - start_process_time)
        failures.append(failure_count)
    return times, failures


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def print_report(duration: float, times, failures) -> None:
    print('--- Statistical report ---')
    print(f'Process has been generating keys for {duration} seconds.')
    print(f'Valid keys generated: {len(times)}')
    print('Failure statistics :')
    print(f'  Average failures before a valid key : {_mean(failures):.2f}')
    print(f'  Maximum failures before a valid key : {max(failures)}')
    print(f'  Minimum failures before a valid key : {min(failures)}')
    print('Time statistics :')
    print(f'  Average time to find a valid key : {_mean(times):.6f} s')
    print(f'  Maximum time to find a valid key : {max(times):.6f} s')
    print(f'  Minimum time to find a valid key : {min(times):.6f} s')


def plot(times, failures, output=None) -> None:
    """Plot failures against elapsed time. Requires matplotlib."""
    try:
        import matplotlib
        if output:
            matplotlib.use('Agg')  # Headless backend for file output.
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib is not installed; skipping the plot. '
              'Install it with "pip install -r requirements.txt".')
        return

    plt.plot(times, failures)
    plt.title('Warcraft II keygen stats')
    plt.xlabel('Time elapsed before getting a valid key')
    plt.ylabel('Failures made before getting a valid key')
    if output:
        plt.savefig(output)
        print(f'Plot saved to {output}')
    else:
        plt.show()


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-d', '--duration', type=float, default=15.0,
        help='how many seconds to run the benchmark (default: 15)',
    )
    parser.add_argument(
        '-s', '--seed', type=int, default=None,
        help='seed the random generator for reproducible runs',
    )
    parser.add_argument(
        '--no-plot', action='store_true',
        help='skip the matplotlib graph',
    )
    parser.add_argument(
        '-o', '--output', default=None,
        help='save the plot to this file instead of displaying it',
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    if args.duration <= 0:
        raise SystemExit('--duration must be positive')

    rng = random.Random(args.seed)
    times, failures = collect_stats(args.duration, rng)
    print_report(args.duration, times, failures)

    if not args.no_plot:
        plot(times, failures, args.output)


if __name__ == '__main__':
    main()
