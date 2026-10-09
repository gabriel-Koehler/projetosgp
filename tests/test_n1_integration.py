from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings
from app.repositories.avaliacao_repository import AvaliacaoRepository, get_avaliacao_repository
from test_avaliacoes_qrcode import payload, ler_qrcode


def test_mounted_backend_preserves_mvp_and_public_qr_contract(settings):
    backend = next(route.app for route in app.routes if getattr(route, 'path', None) == '/n1')
    previous = backend.dependency_overrides.copy()
    backend.dependency_overrides[get_settings] = lambda: settings
    backend.dependency_overrides[get_avaliacao_repository] = lambda: store
    store = AvaliacaoRepository()
    try:
        with TestClient(app) as client:
            assert client.get('/n1/api/painel').status_code == 401
            assert client.post('/api/auth/login', json={'email':'professor','password':'123456'}).status_code == 200
            assert client.get('/api/questoes').status_code == 200
            assert client.get('/n1/api/painel').status_code == 401
            assert client.post('/n1/api/auth/login', json={'username':'professor','password':'senha-teste'}).status_code == 200
            response = client.post('/n1/api/avaliacoes', json=payload())
            assert response.status_code == 201
            evaluation = response.json()
            version = evaluation['versoes'][0]
            assert version['url_qrcode'].startswith('/n1/api/avaliacoes/')
            assert version['url_aluno'].startswith('http://testserver/n1/student/gabarito/')
            assert ler_qrcode(client.get(version['url_qrcode']).content) == version['url_aluno']
            with TestClient(app) as anonymous:
                assert anonymous.get(version['url_aluno']).status_code == 403
                assert client.patch('/n1/api/avaliacoes/'+str(evaluation['id'])+'/gabarito', json={'liberado':True}).status_code == 200
                assert set(anonymous.get(version['url_aluno']).json()) == {'avaliacao','versao','gabarito'}
            assert client.post('/n1/api/auth/logout').status_code == 204
            assert client.get('/n1/api/painel').status_code == 401
            assert client.get('/api/questoes').status_code == 200
    finally:
        backend.dependency_overrides = previous
