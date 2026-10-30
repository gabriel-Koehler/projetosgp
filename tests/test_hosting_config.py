import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app

class HostingCookieTests(unittest.TestCase):
    def test_https_cookie_configuration(self):
        for setting, expected in [('true', True), ('false', False)]:
            with patch.dict(os.environ, {'SESSION_HTTPS_ONLY': setting}):
                with TestClient(app, base_url='https://testserver') as client:
                    response = client.post('/api/auth/login', json={'email': 'professor@avaliasystem.com', 'password': '123456'})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual('Secure' in response.headers['set-cookie'], expected)
