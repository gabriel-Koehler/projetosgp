from app.repositories.cadastros_repository import ProfessorRepository


def test_register_persists_and_accepts_email_login(api):
    data = {"name": "Ana", "email": "Ana@example.com", "password": "senha-forte"}

    assert api.post("/api/auth/register", json=data).status_code == 201
    assert api.post("/api/auth/logout").status_code == 204
    login = api.post("/api/auth/login", json={
        "username": "ANA@example.com", "password": data["password"],
    })
    assert login.json() == {"username": "ana@example.com", "nome": "Ana"}
    assert api.post("/api/auth/register", json=data).status_code == 409
    assert api.get("/api/semestres").json() == []


def test_google_subject_reuses_professor_and_preserves_local_account(banco):
    repo = ProfessorRepository(banco)
    local = repo.cadastrar("ana@example.com", "Ana", "hash")
    google = repo.autenticar_google("subject-123", "Ana")

    assert local["id"] != google["id"]
    assert repo.autenticar_google("subject-123", "Nome atualizado")["id"] == google["id"]
    assert repo.obter_por_username(google["username"]).senha_hash is None
