#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import sys
import urllib.request

from bs4 import BeautifulSoup


UNITS = {
    'Bytes': 1,
    'KB': 2**10,
    'MB': 2**20,
    'GB': 2**30,
    'TB': 2**40,
    'PB': 2**50,
}


def _get_lfs_stats(org: str, user_session: str, endpoint: str) -> dict[str, float]:
    req = urllib.request.Request(f'https://github.com/organizations/{org}/settings/billing/{endpoint}')
    req.add_header('Cookie', f'user_session={user_session}')
    with urllib.request.urlopen(req) as res:
        body = res.read().decode('utf-8')
    soup = BeautifulSoup(body, 'html.parser')
    usages = {}
    for li in soup.find_all('li'):
        (org_parsed, repo) = li.find('a').text.split('/')
        assert org == org_parsed
        usage = li.find('div', class_='text-small').text
        (size, unit) = re.search(r'^([\d.]+) (.+)', usage).groups()
        usages[repo] = float(size) * UNITS[unit]
    return usages


def get_bandwidth_usage(org: str, user_session: str) -> dict[str, float]:
    return _get_lfs_stats(org, user_session, 'lfs_bandwidth')


def get_storage_usage(org: str, user_session: str) -> dict[str, float]:
    return _get_lfs_stats(org, user_session, 'lfs_storage')


def get_usage(org: str, user_session: str) -> dict[str, float]:
    """Deprecated."""
    return get_bandwidth_usage(org, user_session)


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Get GitHub LFS usage')
    parser.add_argument('org', help='GitHub organization')
    parser.add_argument('-s', '--statistics', choices=['bandwidth', 'storage'], default='bandwidth')
    return parser.parse_args()


def main(argv: list[str]) -> int:
    options = parse_args(argv[1:])
    user_session = os.environ.get('GITHUB_USER_SESSION_COOKIE', None)
    if user_session is None:
        raise RuntimeError('GITHUB_USER_SESSION_COOKIE is not set')

    if options.statistics == 'bandwidth':
        print(json.dumps(get_bandwidth_usage(options.org, user_session), indent=2))
    elif options.statistics == 'storage':
        print(json.dumps(get_storage_usage(options.org, user_session), indent=2))
    else:
        assert False
    return 0


if __name__ == '__main__':
    exit(main(sys.argv))
