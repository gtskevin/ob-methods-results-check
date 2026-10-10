#!/usr/bin/env python3
"""Read-only release check. Sends no manuscript, local path, or credentials."""
import json
import os
from pathlib import Path
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

REPO_URL = 'https://github.com/gtskevin/ob-methods-results-check'
VERSION_URL = ('https://api.github.com/repos/gtskevin/ob-methods-results-check/'
               'contents/skills/ob-methods-results-check/VERSION?ref=main')
VERSION_FILE = Path(__file__).resolve().parents[1] / 'VERSION'


def parse_version(value):
    text = value.strip()
    if not re.fullmatch(r'(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8})', text):
        raise ValueError('Invalid release version')
    return tuple(map(int, text.split('.'))), text


def check_update(version_file=VERSION_FILE):
    if os.environ.get('OB_METHODS_SKIP_UPDATE_CHECK') == '1':
        return {'status': 'skipped', 'reason': 'disabled'}
    result = {'status': 'unavailable', 'update_url': REPO_URL}
    try:
        local_tuple, local = parse_version(Path(version_file).read_text(encoding='utf-8'))
        result['local_version'] = local
    except (OSError, UnicodeError, ValueError):
        return {**result, 'reason': 'invalid_local_version'}
    try:
        request = Request(VERSION_URL, headers={
            'User-Agent': 'ob-methods-results-check-update-check',
            'Accept': 'application/vnd.github.raw+json', 'Cache-Control': 'no-cache',
        })
        with urlopen(request, timeout=3) as response:
            data = response.read(129)
        if len(data) > 128:
            raise ValueError('Oversized response')
        remote_tuple, remote = parse_version(data.decode('ascii'))
    except (OSError, URLError, UnicodeError, ValueError):
        return {**result, 'reason': 'remote_check_failed'}
    status = ('update_available' if remote_tuple > local_tuple else
              'up_to_date' if remote_tuple == local_tuple else 'local_ahead')
    return {**result, 'status': status, 'latest_version': remote}


if __name__ == '__main__':
    print(json.dumps(check_update()))
