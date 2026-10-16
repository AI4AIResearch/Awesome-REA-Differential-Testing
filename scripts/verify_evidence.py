#!/usr/bin/env python3
"""Check the observable structure of REA 6.5.0 output for the Notes fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'labs/electron-notes/app'
RECEIPT = ROOT / 'labs/electron-notes/verification.json'


def check_fixture():
    receipt = json.loads(RECEIPT.read_text())
    expected = receipt['fixture_files_sha256']
    actual = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(FIXTURE.iterdir()) if path.is_file()}
    if actual != expected:
        raise ValueError('Fixture files differ from the recorded run; repeat the lab and review its receipt.')
    return actual


def check_evidence(evidence):
    if evidence.get('operation') != 'analyze_javascript_application':
        raise ValueError('Expected REA analyze_javascript_application Evidence.')
    result = evidence['normalized_result']
    checks = {
        'relevant_files': (result['statistics']['relevant_files'], 7),
        'parsed_javascript_files': (result['statistics']['parsed_javascript_files'], 5),
        'parse_failures': (result['statistics']['parse_failures'], 0),
        'browser_windows': (result['summary']['browser_windows'], 1),
        'preload_entrypoints': (result['summary']['preload_entrypoints'], 1),
        'context_bridge_apis': (result['summary']['context_bridge_apis'], 1),
        'ipc_literal_channels': (result['summary']['ipc']['literal_channels'], 1),
        'ipc_paired_transmissions': (result['summary']['ipc']['paired_renderer_transmissions'], 1),
        'integrity_contradictions': (len(result['integrity_contradictions']), 0),
    }
    observations = [observation for node in result['graph']['nodes']
                    for observation in node.get('observations', [])]
    for operation, source in [('invoke', 'preload.cjs'), ('handle', 'main.cjs')]:
        found = any(observation.get('properties', {}).get('channel') == 'notes:export'
                    and observation.get('properties', {}).get('operation') == operation
                    and observation.get('evidence', {}).get('location', {}).get('value', {}).get('source') == source
                    for observation in observations)
        checks[f'{operation}_source_location'] = (found, True)
    failed = {key: {'observed': actual, 'expected': expected}
              for key, (actual, expected) in checks.items() if actual != expected}
    if failed:
        raise ValueError(json.dumps(failed, indent=2))
    return {key: actual for key, (actual, _) in checks.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', nargs='?', type=Path)
    parser.add_argument('--fixture-only', action='store_true', help='Check fixture hashes against the published receipt')
    args = parser.parse_args()
    try:
        check_fixture()
        if args.fixture_only:
            print('PASS: fixture matches all 7 recorded file hashes.')
            return
        if args.evidence is None:
            parser.error('Supply an Evidence JSON file or --fixture-only.')
        checks = check_evidence(json.loads(args.evidence.read_text()))
        print(json.dumps({'status': 'pass', 'checks': checks}, indent=2))
        print('Static structure verified. Electron runtime behavior and full semantic recovery are not asserted.')
    except (KeyError, ValueError, OSError, TypeError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
