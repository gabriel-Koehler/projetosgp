def test_health_e_publico(client):
    assert client.get("/api/health").status_code == 200


def test_login_com_credenciais_validas(client):
    resposta = client.post("/api/auth/login", json={"username": "professor", "password": "senha-teste"})

    assert resposta.status_code == 200
    assert resposta.json() == {"username": "professor", "nome": "Prof. Teste"}
    assert "sessao_professor" in resposta.cookies


def test_login_com_senha_errada(client):
    resposta = client.post("/api/auth/login", json={"username": "professor", "password": "errada"})

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Usuário ou senha inválidos."
    assert "sessao_professor" not in resposta.cookies


def test_login_com_usuario_errado(client):
    resposta = client.post("/api/auth/login", json={"username": "aluno", "password": "senha-teste"})
    assert resposta.status_code == 401


def test_login_sem_campos(client):
    assert client.post("/api/auth/login", json={}).status_code == 422


def test_rota_administrativa_bloqueada_sem_login(client):
    assert client.get("/api/painel").status_code == 401
    assert client.get("/api/auth/me").status_code == 401


def test_rota_administrativa_liberada_com_login(client_logado):
    assert client_logado.get("/api/painel").status_code == 200
    assert client_logado.get("/api/auth/me").json()["nome"] == "Prof. Teste"


def test_logout_encerra_sessao(client_logado):
    assert client_logado.post("/api/auth/logout").status_code == 204
    assert client_logado.get("/api/painel").status_code == 401


def test_cookie_adulterado_nao_autentica(client):
    client.cookies.set("sessao_professor", "valor-forjado")
    assert client.get("/api/painel").status_code == 401
