#!/usr/bin/env python3
"""Validate the catalog, lab, and browser script before producing deployable files."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fontawesome-assets-url', help='Existing licensed icon asset origin; no fonts are added to Git')
    args = parser.parse_args()
    commands = [
        [sys.executable, 'scripts/validate.py'],
        [sys.executable, 'scripts/verify_evidence.py', '--fixture-only'],
        ['node', '--test', 'labs/electron-notes/app/csv.test.cjs'],
        ['node', '--check', 'site/app.js'],
    ]
    build = [sys.executable, 'scripts/build_site.py']
    if args.fontawesome_assets_url:
        build.extend(['--fontawesome-assets-url', args.fontawesome_assets_url])
    commands.append(build)
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            print('Production build stopped because a required check failed.', file=sys.stderr)
            return result.returncode
    print('Production checks passed; deployable files are in dist/.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
