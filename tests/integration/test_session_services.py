"""Regression for the observed Type=dbus startup loop in slow Plasma sessions."""
import importlib.util
from pathlib import Path
import unittest

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts/testing'
spec = importlib.util.spec_from_file_location('session_checks', SCRIPTS / 'installed_smoke.py')
session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)


class SessionServiceTests(unittest.TestCase):
    def healthy(self):
        # Same systemctl show fields and duration format captured in the live A/B diagnostic.
        identities = [('plasma-polkit-agent.service', 'org.kde.polkit-kde-authentication-agent-1'),
                      ('plasma-powerdevil.service', 'org.kde.Solid.PowerManagement'),
                      ('plasma-kscreen.service', 'org.kde.KScreen')]
        return {'units': {'returncode': 0, 'stdout': '\n\n'.join(
            'Type=dbus\nTimeoutStartUSec=1min\nBusName=' + bus
            + '\nResult=success\nNRestarts=0\nId=' + name
            + '\nActiveState=active\nSubState=running' for name, bus in identities)}}

    def test_all_three_agents_must_be_active_without_a_restart_loop(self):
        result = self.healthy()
        self.assertTrue(session.session_services_ready(result))
        result['units']['stdout'] = result['units']['stdout'].replace('NRestarts=0', 'NRestarts=17', 1)
        self.assertFalse(session.session_services_ready(result))

    def test_missing_bus_readiness_cannot_be_hidden_by_changing_unit_type(self):
        result = self.healthy()
        result['units']['stdout'] = result['units']['stdout'].replace('Type=dbus', 'Type=simple', 1)
        self.assertFalse(session.session_services_ready(result))
        self.assertFalse(session.session_services_ready({'units': {'returncode': 1, 'stdout': ''}}))
