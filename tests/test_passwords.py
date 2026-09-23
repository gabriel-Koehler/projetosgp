from app.core import passwords


def test_hash_confere_com_a_senha_certa():
    hash_ = passwords.gerar_hash("segredo", iteracoes=1000)
    assert passwords.verificar("segredo", hash_)
    assert not passwords.verificar("errado", hash_)


def test_hashes_diferentes_para_a_mesma_senha():
    assert passwords.gerar_hash("x", iteracoes=1000) != passwords.gerar_hash("x", iteracoes=1000)


def test_hash_invalido_nao_confere():
    assert not passwords.verificar("x", "lixo")
    assert not passwords.verificar("x", "md5$1$a$b")
