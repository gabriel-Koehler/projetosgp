from dataclasses import replace

import cv2
import numpy as np
import psycopg
import pytest
from fastapi.testclient import TestClient

from app.persistent import create_app


def payload(api, **changes):
    semester = api.post('/api/semestres', json={'nome': '2026.2'}).json()
    room = api.post('/api/turmas', json={'nome': 'ADS', 'semestre_id': semester['id']}).json()
    questions = []
    for n in range(3):
        response = api.post('/api/questoes', json={
            'enunciado': f'Pergunta {n}', 'alternativas': ['a', 'b', 'c', 'd', 'e'], 'correta': 'E',
        })
        assert response.status_code == 201, response.text
        questions.append(response.json()['id'])
    return {
        'nome': 'Avaliação persistente', 'turma_id': room['id'], 'questao_ids': questions,
        'configuracao': {'quantidade': 2, 'nomenclatura': 'personalizada',
                         'nomes_personalizados': ['Azul 1', 'Verde_2'],
                         'embaralhar_questoes': True, 'embaralhar_alternativas': True},
        **changes,
    }


def create(api, data):
    response = api.post('/api/avaliacoes', json=data)
    assert response.status_code == 201, response.text
    return response.json()


def test_versions_survive_restart_and_bank_edits(api, banco_url, settings):
    data = payload(api)
    saved = create(api, data)
    for version in saved['versoes']:
        for question in version['questoes']:
            assert question['alternativas'][ord(question['correta']) - 65] == 'e'
            assert version['gabarito'][str(question['numero'])] == question['correta']
    api.put(f"/api/questoes/{data['questao_ids'][0]}", json={
        'enunciado': 'Alterada depois', 'alternativas': ['novo', 'b', 'c', 'd'], 'correta': 'A',
    })
    assert api.delete(f"/api/questoes/{data['questao_ids'][1]}").json()['arquivada']
    with TestClient(create_app(replace(settings, database_url=banco_url))) as restarted:
        assert restarted.post('/api/auth/login', json={'username': 'professor', 'password': 'senha-teste'}).status_code == 200
        assert restarted.get(f"/api/avaliacoes/{saved['id']}").json() == saved
        summaries = restarted.get('/api/avaliacoes').json()
        assert summaries[0]['quantidade_versoes'] == 2
        assert summaries[0]['quantidade_questoes'] == 3
        assert restarted.get(f"/api/avaliacoes?turma_id={data['turma_id']}").json() == summaries
        assert restarted.get('/api/avaliacoes?turma_id=-1').json() == []


def test_answer_override_only_changes_evaluation(api):
    data = payload(api)
    data['gabaritos'] = {str(data['questao_ids'][0]): 'B'}
    saved = create(api, data)
    for version in saved['versoes']:
        question = next(q for q in version['questoes'] if q['questao_id'] == str(data['questao_ids'][0]))
        assert question['alternativas'][ord(question['correta']) - 65] == 'b'
    assert api.get(f"/api/questoes/{data['questao_ids'][0]}").json()['correta'] == 'E'


def test_different_sets_and_custom_grade(api):
    data = payload(api, nota_maxima=20)
    data['configuracao'].update(mesmas_questoes=False, questoes_por_versao=1)
    saved = create(api, data)
    assert saved['nota_maxima'] == 20
    assert all(len(v['questoes']) == 1 for v in saved['versoes'])
    assert len({v['questoes'][0]['questao_id'] for v in saved['versoes']}) == 2


def test_foreign_professor_cannot_read_or_modify(api, banco):
    data = payload(api)
    saved = create(api, data)
    banco.execute("INSERT INTO professor(username,nome,senha_hash) SELECT 'outro','Outro',senha_hash FROM professor WHERE id=1")
    api.post('/api/auth/logout')
    api.post('/api/auth/login', json={'username':'outro','password':'senha-teste'})
    assert api.get('/api/avaliacoes').json() == []
    for path, method, body in [
        (f"/api/avaliacoes/{saved['id']}", 'get', None),
        (f"/api/avaliacoes/{saved['id']}", 'delete', None),
        (f"/api/avaliacoes/{saved['id']}/gabarito", 'patch', {'liberado':True}),
        (saved['versoes'][0]['url_qrcode'], 'get', None),
    ]:
        assert getattr(api, method)(path, **({'json':body} if body else {})).status_code == 404
    assert api.post('/api/avaliacoes', json=data).status_code == 404
    data['turma_id'] = None
    assert api.post('/api/avaliacoes', json=data).status_code == 404


def test_qr_public_gate_and_revocation(api):
    saved = create(api, payload(api))
    version = saved['versoes'][0]
    png = api.get(version['url_qrcode'], headers={'x-forwarded-host':'localhost:3000'})
    assert png.status_code == 200 and png.headers['content-type'] == 'image/png'
    image = cv2.imdecode(np.frombuffer(png.content, np.uint8), cv2.IMREAD_GRAYSCALE)
    url, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    assert url == f"http://localhost:3000/student?token={version['codigo']}"
    public_path = f"/api/public/gabaritos/{version['codigo']}"
    anonymous = TestClient(api.app)
    assert anonymous.get(public_path).status_code == 403
    assert api.patch(f"/api/avaliacoes/{saved['id']}/gabarito", json={'liberado':True}).status_code == 200
    public = anonymous.get(public_path).json()
    assert set(public) == {'avaliacao','versao','gabarito'}
    assert all(set(item) == {'questao','alternativa'} for item in public['gabarito'])
    api.patch(f"/api/avaliacoes/{saved['id']}/gabarito", json={'liberado':False})
    assert anonymous.get(public_path).status_code == 403
    assert anonymous.get(version['url_qrcode']).status_code == 401


@pytest.mark.parametrize('change,status', [
    ({'nome':'   '},422), ({'questao_ids':[]},422), ({'nota_maxima':0},422),
    ({'configuracao':{'quantidade':2,'nomenclatura':'personalizada','nomes_personalizados':['Azul','azul']}},422),
    ({'configuracao':{'quantidade':1,'nomenclatura':'personalizada','nomes_personalizados':['<script>']}},422),
])
def test_invalid_creation_has_no_partial_rows(api, banco, change, status):
    data = payload(api, **change)
    assert api.post('/api/avaliacoes',json=data).status_code == status
    assert banco.execute('SELECT count(*) AS n FROM avaliacao').fetchone()['n'] == 0


def test_creation_rolls_back_all_rows_on_midway_failure(api, banco):
    data = payload(api)
    banco.execute("CREATE FUNCTION fail_version() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.ordem=2 THEN RAISE EXCEPTION 'test failure'; END IF; RETURN NEW; END $$")
    banco.execute('CREATE TRIGGER fail_version BEFORE INSERT ON versao_avaliacao FOR EACH ROW EXECUTE FUNCTION fail_version()')
    try:
        with pytest.raises(psycopg.errors.RaiseException):
            api.post('/api/avaliacoes', json=data)
        for table in ('avaliacao','avaliacao_questao','versao_avaliacao','questao_versao','gabarito_versao'):
            assert banco.execute(f'SELECT count(*) AS n FROM {table}').fetchone()['n'] == 0
    finally:
        banco.execute('DROP TRIGGER fail_version ON versao_avaliacao')
        banco.execute('DROP FUNCTION fail_version()')
