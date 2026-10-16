#!/usr/bin/env python3
"""Review catalog PRs with trusted base-branch code; never execute PR code."""
import base64
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from validate import validate_benchmarks, validate_resources, public_https_error

ROOT = Path(__file__).resolve().parents[1]
MARKER = '<!-- awesome-rea-automated-review -->'
CATALOGS = ('data/rea-resources.json', 'data/tool-resources.json')
SENSITIVE = re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
LOCAL_PATH = re.compile(r'/Users/[^/\s]+/|/home/[^/\s]+/')
MAX_FILE_BYTES = 8 * 1024 * 1024


def api(repository, endpoint, token, method='GET', payload=None, raw=False):
    url = f'https://api.github.com/repos/{repository}/{endpoint}'
    headers = {'Accept': 'application/vnd.github.raw+json' if raw else 'application/vnd.github+json',
               'Authorization': f'Bearer {token}', 'X-GitHub-Api-Version': '2022-11-28',
               'User-Agent': 'awesome-rea-catalog-review'}
    body = json.dumps(payload).encode() if payload is not None else None
    if body is not None:
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError('API response exceeds the review size limit')
    return data.decode('utf-8') if raw else json.loads(data)


def content_at(repository, filename, sha, token):
    path = urllib.parse.quote(filename, safe='/')
    return api(repository, f'contents/{path}?ref={sha}', token, raw=True)


def scan_index_errors(document):
    errors = []
    if not isinstance(document, dict) or not isinstance(document.get('resources'), list):
        return ['Source index must contain a resources array.']
    seen = set()
    for index, record in enumerate(document['resources']):
        if not isinstance(record, dict):
            errors.append(f'Source index entry {index} must be an object.')
            continue
        identifier = record.get('id')
        if not isinstance(identifier, str) or identifier in seen:
            errors.append(f'Source index entry {index} has a missing or duplicate ID.')
        else:
            seen.add(identifier)
        if record.get('scan_status') != 'readme-scanned':
            errors.append(f'Source index entry {index} must preserve its automated scan status.')
        for field in ('url', 'readme_url'):
            if public_https_error(record.get(field)):
                errors.append(f'Source index entry {index} has an invalid public {field}.')
        if not re.fullmatch(r'[0-9a-f]{64}', str(record.get('readme_sha256', ''))):
            errors.append(f'Source index entry {index} needs a README SHA-256.')
    return errors


def review_data(contents, changed):
    errors, reviewed = [], []
    if set(CATALOGS) & changed:
        records = []
        for filename in CATALOGS:
            data = json.loads(contents[filename])
            if not isinstance(data, list):
                errors.append(f'{filename}: expected a JSON array.')
            else:
                records.extend(data)
        validate_resources(records, errors)
        reviewed.append(f'{len(records)} curated records checked together for schema, duplicate IDs/URLs, provenance, targets, dates, and review labels.')
    if 'data/benchmarks.json' in changed:
        data = json.loads(contents['data/benchmarks.json'])
        if not isinstance(data, list):
            errors.append('Benchmarks must be an array.')
        else:
            validate_benchmarks(data, errors)
            reviewed.append(f'{len(data)} benchmark records checked for timestamp, count, and source consistency.')
    if 'data/source-index.json' in changed:
        data = json.loads(contents['data/source-index.json'])
        errors.extend(scan_index_errors(data))
        reviewed.append('Automated source-index records checked separately from curated resources.')
    return errors, reviewed


def safe_text(value):
    value = SENSITIVE.sub('[redacted credential-like value]', str(value))
    value = LOCAL_PATH.sub('[redacted local path]/', value)
    value = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', value)
    return value.replace('`', "'").replace('@', '@\u200b')[:500]


def main():
    token = os.environ['GITHUB_TOKEN']
    repository = os.environ['GITHUB_REPOSITORY']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid repository name')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    number = int(event['pull_request']['number'])
    pull = api(repository, f'pulls/{number}', token)
    sha = pull['head']['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Unexpected head SHA')
    reviews = api(repository, f'pulls/{number}/reviews?per_page=100', token)
    if any(MARKER in review.get('body', '') and review.get('commit_id') == sha for review in reviews):
        print('This commit already has an automated review.')
        return
    files = []
    for page in range(1, 4):
        batch = api(repository, f'pulls/{number}/files?per_page=100&page={page}', token)
        files.extend(batch)
        if len(batch) < 100:
            break
    changed = {entry['filename'] for entry in files}
    errors, reviewed = [], []
    if pull.get('changed_files', len(files)) > 300:
        errors.append('This PR exceeds the 300-file automatic review limit; split it for a complete review.')
    for entry in files:
        path = entry['filename']
        patch = entry.get('patch', '')
        added = '\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
        if SENSITIVE.search(added) or LOCAL_PATH.search(added):
            errors.append(f'{path}: added text contains a credential-like value or personal absolute path; inspect locally. The value is omitted here.')
        if re.search(r'(^|/)(\.env(?:\..*)?|secrets\.json|credentials[^/]*\.json)$', path) and not path.endswith('.env.example'):
            errors.append(f'{path}: private configuration should not be committed.')
        if path.startswith(('.cache/', '.wrangler/', 'dist/')) or '/output/' in path or path.endswith(('.woff', '.woff2')):
            errors.append(f'{path}: generated, raw, or licensed production assets do not belong in this public source repository.')
    relevant = set(CATALOGS) | {'data/benchmarks.json', 'data/source-index.json'}
    contents = {filename: (ROOT / filename).read_text() for filename in CATALOGS}
    for filename in sorted(changed & relevant):
        if any(entry['filename'] == filename and entry['status'] == 'removed' for entry in files):
            errors.append(f'{filename}: removing a catalog requires maintainer review.')
            continue
        try:
            contents[filename] = content_at(repository, filename, sha, token)
        except (urllib.error.HTTPError, UnicodeError, ValueError):
            errors.append(f'{filename}: could not safely retrieve text for this commit.')
    try:
        findings, checked = review_data(contents, changed & set(contents))
        errors.extend(findings)
        reviewed.extend(checked)
    except (ValueError, TypeError, KeyError):
        errors.append('Changed catalog JSON could not be parsed or validated. Check its shape locally.')
    manual = any(path.startswith(('scripts/', '.github/', 'site/')) for path in changed)
    body = [MARKER, '### Automated catalog review', '', f'Commit: `{sha[:12]}`.', '',
            '**Changes need attention.**' if errors else '**No issues found by these automatic checks.**', '']
    body.extend('- ' + safe_text(item) for item in reviewed)
    if errors:
        body.extend(['', 'Findings:'])
        body.extend('- ' + safe_text(item) for item in errors[:30])
        if len(errors) > 30:
            body.append(f'- {len(errors) - 30} additional findings; run the local validator for the complete list.')
    if manual:
        body.extend(['', 'Code, automation, or site changes require a maintainer to review behavior and permissions.'])
    body.extend(['', 'This is a rule-based review, not a runtime compatibility test or an approval. PR code is never executed by this review job. CI checks and maintainer review remain separate.'])
    # Ensure an obsolete run does not comment against a newly pushed commit.
    if api(repository, f'pulls/{number}', token)['head']['sha'] != sha:
        print('PR head changed; the next run will review the new commit.')
        return
    api(repository, f'pulls/{number}/reviews', token, method='POST',
        payload={'commit_id': sha, 'event': 'COMMENT', 'body': '\n'.join(body)})
    print(f'Posted a rule-based review: {len(errors)} finding(s); no PR code executed.')
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
