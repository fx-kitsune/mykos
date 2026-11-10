"""A running process alone does not establish a responsive desktop session."""
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts/testing'
spec = importlib.util.spec_from_file_location('session_checks', SCRIPTS / 'installed_smoke.py')
session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)

class SessionServiceTests(unittest.TestCase):
    def healthy(self):
        return {'agents': {name: {'returncode': 0} for name in ['openbox', 'lxpolkit', 'dunst']},
                'bus': {'returncode': 0},
                'shell_reply': {'returncode': 0, 'stdout': json.dumps({'desktop':'MyKOS','panel':True,'ticks':2})}}

    def test_all_agents_and_event_loop_must_be_responsive(self):
        result = self.healthy()
        self.assertTrue(session.session_services_ready(result))
        result['agents']['lxpolkit']['returncode'] = 1
        self.assertFalse(session.session_services_ready(result))
        self.assertFalse(session.session_services_ready({}))

    def test_unresponsive_shell_or_missing_bus_cannot_pass(self):
        result = self.healthy()
        result['shell_reply']['stdout'] = '{}'
        self.assertFalse(session.session_services_ready(result))
        result = self.healthy()
        result['bus']['returncode'] = 1
        self.assertFalse(session.session_services_ready(result))
