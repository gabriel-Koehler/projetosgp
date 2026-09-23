"""Banco de questões sobre o PostgreSQL (precisa de TEST_DATABASE_URL)."""

QUESTAO = {
    "enunciado": "Qual linguagem define a estrutura de uma página?",
    "alternativas": ["HTML", "CSS", "JavaScript", "SQL"],
    "correta": "a",
    "disciplina": "Web",
    "categoria": "Fundamentos",
    "dificuldade": "facil",
}


def criar(api, **mudancas):
    resposta = api.post("/api/questoes", json={**QUESTAO, **mudancas})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_cadastro_manual(api):
    questao = criar(api)
    assert questao["correta"] == "A"
    assert questao["alternativas"] == ["HTML", "CSS", "JavaScript", "SQL"]
    assert api.get(f"/api/questoes/{questao['id']}").json() == questao


def test_cinco_alternativas(api):
    assert criar(api, alternativas=["a", "b", "c", "d", "e"], correta="E")["correta"] == "E"


def test_gabarito_fora_das_alternativas(api):
    resposta = api.post("/api/questoes", json={**QUESTAO, "correta": "E"})
    assert resposta.status_code == 422
    assert "não corresponde" in resposta.json()["detail"]


def test_alternativas_repetidas(api):
    resposta = api.post("/api/questoes", json={**QUESTAO, "alternativas": ["a", "b", "A", "d"]})
    assert resposta.status_code == 422


def test_edicao(api):
    questao = criar(api)
    editada = api.put(
        f"/api/questoes/{questao['id']}", json={**QUESTAO, "alternativas": ["1", "2", "3", "4"], "correta": "D"}
    ).json()
    assert editada["alternativas"] == ["1", "2", "3", "4"]
    assert editada["correta"] == "D"
    assert editada["atualizado_em"] > questao["atualizado_em"]


def test_busca_e_filtros(api):
    criar(api)
    criar(api, enunciado="O que é CSS?", disciplina="Web", categoria="Estilo", dificuldade="media")
    criar(api, enunciado="O que é um SGBD?", alternativas=["x", "y", "z", "PostgreSQL"], disciplina="Banco de Dados")

    def ids(**params):
        return [q["enunciado"] for q in api.get("/api/questoes", params=params).json()["itens"]]

    assert len(ids()) == 3
    assert ids(busca="é css") == ["O que é CSS?"]
    assert len(ids(busca="css")) == 2  # a primeira tem "CSS" como alternativa
    assert ids(busca="postgres") == ["O que é um SGBD?"]  # busca também nas alternativas
    assert len(ids(disciplina="Web")) == 2
    assert ids(dificuldade="media") == ["O que é CSS?"]
    assert api.get("/api/questoes/filtros").json() == {
        "disciplina": ["Banco de Dados", "Web"],
        "categoria": ["Estilo", "Fundamentos"],
    }


def test_paginacao(api):
    for i in range(5):
        criar(api, enunciado=f"Questão {i}")
    pagina = api.get("/api/questoes", params={"pagina": 2, "por_pagina": 2}).json()
    assert pagina["total"] == 5
    assert [q["enunciado"] for q in pagina["itens"]] == ["Questão 2", "Questão 1"]


def test_exclusao_de_questao_nao_usada(api):
    questao = criar(api)
    resposta = api.delete(f"/api/questoes/{questao['id']}").json()
    assert resposta["excluida"] is True
    assert api.get(f"/api/questoes/{questao['id']}").status_code == 404


def test_exclusao_de_questao_usada_arquiva(api, banco):
    questao = criar(api)
    banco.execute("INSERT INTO avaliacao (professor_id, nome, configuracao) VALUES (1, 'N1', '{}')")
    banco.execute("INSERT INTO avaliacao_questao VALUES (1, %s, 1, 'A')", (questao["id"],))

    resposta = api.delete(f"/api/questoes/{questao['id']}").json()
    assert resposta == {
        "excluida": False,
        "arquivada": True,
        "mensagem": "A questão já foi usada em avaliações: ela saiu do banco, mas o histórico foi mantido.",
    }
    assert api.get("/api/questoes").json()["total"] == 0
    assert banco.execute("SELECT count(*) AS n FROM questao").fetchone()["n"] == 1


def test_importacao_de_questoes(api):
    criar(api)  # já existe no banco
    planilha = (
        "enunciado;alternativa_a;alternativa_b;alternativa_c;alternativa_d;gabarito;dificuldade\n"
        "Qual linguagem define a estrutura de uma página?;a;b;c;d;A;\n"
        "O que é CSS?;Estilo;Banco;Rede;Script;A;Fácil\n"
        "Sem gabarito;a;b;c;d;;\n"
    ).encode()

    previa = api.post("/api/questoes/importar", files={"arquivo": ("q.csv", planilha)}).json()
    assert previa["total_linhas"] == 3
    assert [v["linha"] for v in previa["validas"]] == [3]
    assert {e["linha"] for e in previa["erros"]} == {2, 4}
    assert api.get("/api/questoes").json()["total"] == 1

    confirmado = api.post(
        "/api/questoes/importar", params={"confirmar": True}, files={"arquivo": ("q.csv", planilha)}
    ).json()
    assert confirmado["importados"] == 1
    importada = api.get("/api/questoes", params={"busca": "CSS"}).json()["itens"][0]
    assert importada["dificuldade"] == "facil"
    assert importada["alternativas"] == ["Estilo", "Banco", "Rede", "Script"]


def test_importacao_com_arquivo_invalido(api):
    resposta = api.post("/api/questoes/importar", files={"arquivo": ("q.pdf", b"%PDF")})
    assert resposta.status_code == 422
    assert ".xlsx ou .csv" in resposta.json()["detail"]


def test_modelo_xlsx(api):
    resposta = api.get("/api/questoes/modelo.xlsx")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("application/vnd.openxmlformats")
    reimportado = api.post("/api/questoes/importar", files={"arquivo": ("modelo.xlsx", resposta.content)}).json()
    assert reimportado["erros"] == [] and len(reimportado["validas"]) == 1
