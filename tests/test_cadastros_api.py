"""CRUDs de semestres, turmas e alunos sobre o PostgreSQL (precisa de TEST_DATABASE_URL)."""

from dataclasses import replace

from fastapi.testclient import TestClient

from app.core import passwords
from app.main import create_app


def criar_semestre(api, nome="2026/2", **extra):
    resposta = api.post("/api/semestres", json={"nome": nome, **extra})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_turma(api, semestre_id, nome="ES-01"):
    resposta = api.post("/api/turmas", json={"semestre_id": semestre_id, "nome": nome, "disciplina": "Eng. Software"})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


# --- Login com o banco ------------------------------------------------------------


def test_login_usa_a_tabela_professor(api):
    assert api.get("/api/auth/me").json() == {"username": "professor", "nome": "Prof. Teste"}


def test_login_errado_com_banco(banco, banco_url, settings):
    with TestClient(create_app(replace(settings, database_url=banco_url))) as cliente:
        resposta = cliente.post("/api/auth/login", json={"username": "professor", "password": "errada"})
        assert resposta.status_code == 401
        resposta = cliente.post("/api/auth/login", json={"username": "ninguem", "password": "senha-teste"})
        assert resposta.status_code == 401


def test_rotas_exigem_login(banco, banco_url, settings):
    with TestClient(create_app(replace(settings, database_url=banco_url))) as cliente:
        for url in ("/api/semestres", "/api/turmas", "/api/questoes", "/api/alunos/1"):
            assert cliente.get(url).status_code == 401


# --- Semestres (RF02) -------------------------------------------------------------


def test_crud_de_semestre(api):
    semestre = criar_semestre(api, data_inicio="2026-08-01", data_fim="2026-12-15")
    assert semestre["ativo"] is True

    alterado = api.put(f"/api/semestres/{semestre['id']}", json={"nome": "2026/2 - Noturno"}).json()
    assert alterado["nome"] == "2026/2 - Noturno"
    assert alterado["data_inicio"] is None

    desativado = api.patch(f"/api/semestres/{semestre['id']}/ativo", json={"ativo": False}).json()
    assert desativado["ativo"] is False
    assert api.get("/api/semestres", params={"ativo": True}).json() == []
    assert len(api.get("/api/semestres").json()) == 1


def test_semestre_com_nome_repetido(api):
    criar_semestre(api)
    resposta = api.post("/api/semestres", json={"nome": "2026/2"})
    assert resposta.status_code == 409
    assert "Já existe" in resposta.json()["detail"]


def test_semestre_com_datas_invertidas(api):
    resposta = api.post("/api/semestres", json={"nome": "X", "data_inicio": "2026-12-01", "data_fim": "2026-01-01"})
    assert resposta.status_code == 422


def test_semestre_inexistente(api):
    assert api.get("/api/semestres/999").status_code == 404


# --- Turmas (RF03) ----------------------------------------------------------------


def test_crud_de_turma(api):
    s1, s2 = criar_semestre(api, "2026/1"), criar_semestre(api, "2026/2")
    turma = criar_turma(api, s1["id"])
    assert turma["semestre_nome"] == "2026/1"

    movida = api.put(f"/api/turmas/{turma['id']}", json={"semestre_id": s2["id"], "nome": "ES-02"}).json()
    assert movida["semestre_id"] == s2["id"] and movida["nome"] == "ES-02"
    assert api.get("/api/turmas", params={"semestre_id": s1["id"]}).json() == []

    assert api.delete(f"/api/turmas/{turma['id']}").status_code == 204
    assert api.get(f"/api/turmas/{turma['id']}").status_code == 404


def test_turma_em_semestre_inexistente(api):
    assert api.post("/api/turmas", json={"semestre_id": 999, "nome": "X"}).status_code == 404


def test_turma_com_alunos_nao_pode_ser_excluida(api):
    turma = criar_turma(api, criar_semestre(api)["id"])
    api.post(f"/api/turmas/{turma['id']}/alunos", json={"nome": "Ana", "matricula": "1"})
    resposta = api.delete(f"/api/turmas/{turma['id']}")
    assert resposta.status_code == 409


# --- Alunos (RF04) ----------------------------------------------------------------


def test_crud_de_aluno(api):
    turma = criar_turma(api, criar_semestre(api)["id"])
    aluno = api.post(
        f"/api/turmas/{turma['id']}/alunos", json={"nome": "Ana", "matricula": "2026001", "email": "ana@x.com"}
    ).json()

    assert api.get(f"/api/turmas/{turma['id']}/alunos").json() == [aluno]
    alterado = api.put(f"/api/alunos/{aluno['id']}", json={"nome": "Ana Souza", "matricula": "2026001"}).json()
    assert alterado["nome"] == "Ana Souza" and alterado["email"] is None
    assert api.delete(f"/api/alunos/{aluno['id']}").status_code == 204
    assert api.get(f"/api/turmas/{turma['id']}/alunos").json() == []


def test_matricula_repetida_na_turma(api):
    turma = criar_turma(api, criar_semestre(api)["id"])
    api.post(f"/api/turmas/{turma['id']}/alunos", json={"nome": "Ana", "matricula": "1"})
    resposta = api.post(f"/api/turmas/{turma['id']}/alunos", json={"nome": "Bia", "matricula": "1"})
    assert resposta.status_code == 409


def test_email_invalido(api):
    turma = criar_turma(api, criar_semestre(api)["id"])
    resposta = api.post(f"/api/turmas/{turma['id']}/alunos", json={"nome": "Ana", "matricula": "1", "email": "x"})
    assert resposta.status_code == 422


# --- Importação de alunos (RF05) --------------------------------------------------


def test_importacao_de_alunos_com_previa_e_confirmacao(api):
    turma = criar_turma(api, criar_semestre(api)["id"])
    api.post(f"/api/turmas/{turma['id']}/alunos", json={"nome": "Já existe", "matricula": "9"})
    planilha = "nome;matricula;email\nAna;1;ana@x.com\nBia;2;\nCaio;9;\n".encode()
    url = f"/api/turmas/{turma['id']}/alunos/importar"

    previa = api.post(url, files={"arquivo": ("alunos.csv", planilha)}).json()
    assert previa["confirmado"] is False and previa["importados"] == 0
    assert [v["linha"] for v in previa["validas"]] == [2, 3]
    assert previa["erros"] == [{"linha": 4, "mensagens": ["Matrícula já cadastrada nesta turma."]}]
    assert len(api.get(f"/api/turmas/{turma['id']}/alunos").json()) == 1  # prévia não grava

    confirmado = api.post(url, params={"confirmar": True}, files={"arquivo": ("alunos.csv", planilha)}).json()
    assert confirmado["importados"] == 2
    assert len(api.get(f"/api/turmas/{turma['id']}/alunos").json()) == 3


def test_modelo_de_alunos(api):
    resposta = api.get("/api/alunos/modelo.csv")
    assert resposta.status_code == 200
    assert "modelo_alunos.csv" in resposta.headers["content-disposition"]
    assert resposta.content.decode("utf-8-sig").startswith("nome;matricula;email")


# --- Isolamento entre professores -------------------------------------------------


def test_professor_nao_ve_dados_de_outro(api, banco, banco_url, settings):
    turma = criar_turma(api, criar_semestre(api)["id"])
    banco.execute(
        "INSERT INTO professor (username, nome, senha_hash) VALUES ('outro', 'Outro', %s)",
        (passwords.gerar_hash("x", iteracoes=1000),),
    )
    with TestClient(create_app(replace(settings, database_url=banco_url))) as outro:
        outro.post("/api/auth/login", json={"username": "outro", "password": "x"})
        assert outro.get("/api/semestres").json() == []
        assert outro.get(f"/api/turmas/{turma['id']}").status_code == 404
        assert outro.post("/api/turmas", json={"semestre_id": turma["semestre_id"], "nome": "X"}).status_code == 404
