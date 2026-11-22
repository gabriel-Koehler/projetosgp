from app.repositories.cadastros_repository import ProfessorRepository


def test_register_without_email_persists_and_accepts_username_login(api, banco):
    data = {
        "name": "Ana", "username": "prof.ana",
        "password": "senha-forte", "passwordConfirmation": "senha-forte",
    }

    assert api.post("/api/auth/register", json=data).status_code == 201
    assert api.post("/api/auth/logout").status_code == 204
    assert banco.execute("SELECT email FROM professor WHERE username = %s", ("prof.ana",)).fetchone()["email"] is None
    login = api.post("/api/auth/login", json={"username": "Prof.Ana", "password": data["password"]})
    assert login.json() == {"username": "prof.ana", "nome": "Ana"}
    assert api.post("/api/auth/register", json=data).status_code == 409
    assert api.get("/api/semestres").json() == []


def test_google_subject_reuses_professor_and_preserves_local_account(banco):
    repo = ProfessorRepository(banco)
    local = repo.cadastrar("prof.ana", "Ana", "hash")
    google = repo.autenticar_google("subject-123", "Ana")

    assert local["id"] != google["id"]
    assert repo.autenticar_google("subject-123", "Nome atualizado")["id"] == google["id"]
    assert repo.obter_por_username(google["username"]).senha_hash is None
