from fastapi.testclient import TestClient
from app.core.config import Settings
from app.persistent import create_app


def test_real_api_never_falls_back_to_demo_credentials():
    with TestClient(create_app(Settings(secret_key='test'))) as client:
        assert client.post('/api/auth/login', json={'username':'professor','password':'123456'}).status_code == 503
        assert client.get('/api/health').status_code == 503
        assert client.get('/api/auth/me').status_code == 401
        assert client.get('/api/semestres').status_code in (401, 503)


def test_infrastructure_failure_does_not_leak_connection_details():
    import psycopg
    from app.core import security
    from unittest.mock import patch
    class FailedPool:
        def connection(self):
            raise psycopg.OperationalError('postgresql://private-user:secret@host/db')
    application = create_app(Settings(secret_key='test'))
    with TestClient(application) as client:
        application.state.pool = FailedPool()
        try:
            response = client.post('/api/auth/login', json={'username':'professor','password':'123456'})
            assert response.status_code == 503
            assert 'secret' not in response.text and 'postgresql' not in response.text
        finally:
            application.state.pool = None
