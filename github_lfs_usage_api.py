import json
import os
import re
import sys
import urllib.request

from bs4 import BeautifulSoup


def get_usage(org: str, user_session: str) -> dict[str, str]:
    req = urllib.request.Request(f'https://github.com/organizations/{org}/settings/billing/lfs_bandwidth')
    req.add_header('Cookie', f'user_session={user_session}')
    with urllib.request.urlopen(req) as res:
        body = res.read().decode('utf-8')
    soup = BeautifulSoup(body, 'html.parser')
    usages = {}
    for li in soup.find_all('li'):
        (org_parsed, repo) = li.find('a').text.split('/')
        assert org == org_parsed
        usage = li.find('div', class_='text-small').text
        usages[repo] = float(re.search(r'^([\d.]+) GB', usage).group(1))
    return usages


def main(argv: list[str]) -> int:
    org = argv[1]
    user_session = os.environ.get('GITHUB_USER_SESSION_COOKIE', None)
    if user_session is None:
        raise RuntimeError('GITHUB_USER_SESSION_COOKIE is not set')
    print(json.dumps(get_usage(org, user_session), indent=2))
    return 0


if __name__ == '__main__':
    exit(main(sys.argv))
