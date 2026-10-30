from datetime import date

from fastapi.testclient import TestClient

from app.backend import create_app as legacy_app
from app.persistent import create_app
from app.services.errors import ErroDeNegocio


def test_all_business_routes_available_in_persistent_mode(settings):
    real = create_app(settings).openapi()['paths']
    legacy = legacy_app(settings).openapi()['paths']
    assert set(real) == set(legacy)
    assert '/api/correcoes/leitura' in real
    assert '/api/correcoes/manual' in real
    assert '/api/avaliacoes/{avaliacao_id}/resultados.xlsx' in real
    assert '/api/avaliacoes/{avaliacao_id}/estatisticas' in real


def test_production_does_not_accept_development_credentials(settings):
    with TestClient(create_app(settings)) as client:
        assert client.post('/api/auth/login', json={
            'username': settings.professor_username,
            'password': settings.professor_password,
        }).status_code == 503
        assert client.get('/api/health').status_code == 503


def test_business_error_keeps_omr_details(settings):
    app = create_app(settings)

    @app.get('/test-error')
    def fail():
        raise ErroDeNegocio('Confira as respostas', 'leitura_duvidosa', {
            'ilegiveis': [2], 'respostas': {1: 'A'}, 'data': date(2026, 10, 11),
        })

    with TestClient(app) as client:
        response = client.get('/test-error')
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'Confira as respostas', 'codigo': 'leitura_duvidosa',
        'ilegiveis': [2], 'respostas': {'1': 'A'}, 'data': '2026-10-11',
    }
