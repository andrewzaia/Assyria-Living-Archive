"""Wait for GitHub's branch-based Pages deployment before publishing our built site."""
import json
import os
import time
from urllib.parse import urlencode
import urllib.request

def wait_for_publisher(fetch_runs, sleep=time.sleep, clock=time.monotonic, timeout=300, quiet_period=20):
    started = clock()
    while clock() - started < timeout:
        # A failed API request raises rather than silently permitting a race.
        runs = fetch_runs()
        publishers = [run for run in runs if run.get('path') == 'dynamic/pages/pages-build-deployment']
        pending = [run for run in publishers if run['status'] != 'completed']
        if publishers and not pending:
            print('Branch-based Pages publisher finished. The generated website can now deploy.', flush=True)
            return
        if not publishers and clock() - started >= quiet_period:
            print('No branch-based Pages publisher detected. The generated website can now deploy.', flush=True)
            return
        if pending:
            print('Waiting for branch-based Pages publisher: ' + ', '.join(str(run['id']) for run in pending), flush=True)
        sleep(5)
    raise TimeoutError('Branch-based Pages deployment did not finish; refusing to race its publication')

def main():
    repository = os.environ['GITHUB_REPOSITORY']
    commit = os.environ['GITHUB_SHA']
    token = os.environ['GH_TOKEN']
    endpoint = os.environ.get('GITHUB_API_URL', 'https://api.github.com')
    url = f'{endpoint}/repos/{repository}/actions/runs?' + urlencode({'head_sha': commit, 'per_page': 100})

    def fetch_runs():
        request = urllib.request.Request(url, headers={
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'AssyriaLivingArchive-deployment-order',
        })
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)['workflow_runs']

    wait_for_publisher(fetch_runs)

if __name__ == '__main__':
    main()
