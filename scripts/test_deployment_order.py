"""Regression checks for the two-publisher deployment race."""
import unittest
from wait_for_pages_publisher import wait_for_publisher

class DeploymentOrderingTests(unittest.TestCase):
    def clock(self):
        state = [0]
        def sleep(seconds):
            state[0] += seconds
        return state, sleep, lambda: state[0]

    def test_publication_waits_until_branch_publisher_finishes(self):
        elapsed, sleep, clock = self.clock()
        responses = iter([
            [{'id': 1, 'path': 'dynamic/pages/pages-build-deployment', 'status': 'queued'}],
            [{'id': 1, 'path': 'dynamic/pages/pages-build-deployment', 'status': 'in_progress'}],
            [{'id': 1, 'path': 'dynamic/pages/pages-build-deployment', 'status': 'completed'}],
        ])
        wait_for_publisher(lambda: next(responses), sleep=sleep, clock=clock)
        self.assertEqual(elapsed[0], 10)

    def test_late_branch_publisher_is_detected(self):
        elapsed, sleep, clock = self.clock()
        responses = iter([
            [],
            [{'id': 1, 'path': 'dynamic/pages/pages-build-deployment', 'status': 'in_progress'}],
            [{'id': 1, 'path': 'dynamic/pages/pages-build-deployment', 'status': 'completed'}],
        ])
        wait_for_publisher(lambda: next(responses), sleep=sleep, clock=clock)
        self.assertEqual(elapsed[0], 10)

    def test_actions_only_hosting_does_not_wait_for_its_own_workflow(self):
        elapsed, sleep, clock = self.clock()
        runs = [{'id': 2, 'path': '.github/workflows/pages.yml', 'status': 'in_progress'}]
        wait_for_publisher(lambda: runs, sleep=sleep, clock=clock)
        self.assertEqual(elapsed[0], 20)

    def test_api_errors_and_timeout_do_not_allow_publication(self):
        _, sleep, clock = self.clock()
        def failed_request():
            raise OSError('API unavailable')
        with self.assertRaises(OSError):
            wait_for_publisher(failed_request, sleep=sleep, clock=clock)
        runs = [{'id': 1, 'path': 'dynamic/pages/pages-build-deployment', 'status': 'queued'}]
        with self.assertRaises(TimeoutError):
            wait_for_publisher(lambda: runs, sleep=sleep, clock=clock, timeout=10)

if __name__ == '__main__':
    unittest.main()
