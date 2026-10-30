-- Validação transacional: dados de exemplo não permanecem no projeto.
BEGIN;
-- Somente desenvolvimento; conta sem login válido. Execute schema.sql primeiro.

INSERT INTO professor (username, nome, senha_hash) VALUES ('diego-local-seed', 'Professor de desenvolvimento', '!conta-seed-sem-login!') ON CONFLICT (username) DO NOTHING;
INSERT INTO semestre (professor_id, nome, ativo) SELECT id, '2026.2', TRUE FROM professor WHERE username = 'diego-local-seed' ON CONFLICT (professor_id, nome) DO NOTHING;
INSERT INTO turma (semestre_id, nome, disciplina)
SELECT s.id, 'ADS - Desenvolvimento', 'Projeto e Arquitetura de Software' FROM semestre s JOIN professor p ON p.id = s.professor_id WHERE p.username = 'diego-local-seed' AND s.nome = '2026.2' ON CONFLICT (semestre_id, nome) DO NOTHING;
INSERT INTO aluno (turma_id, nome, matricula)
SELECT t.id, a.nome, a.matricula FROM turma t JOIN semestre s ON s.id = t.semestre_id JOIN professor p ON p.id = s.professor_id CROSS JOIN (VALUES ('Ana Exemplo', '0001'), ('Bruno Exemplo', '0002')) a(nome, matricula) WHERE p.username = 'diego-local-seed' AND t.nome = 'ADS - Desenvolvimento' ON CONFLICT (turma_id, matricula) DO NOTHING;
INSERT INTO questao (professor_id, enunciado, correta, disciplina, dificuldade)
SELECT p.id, 'Qual linguagem estrutura páginas web?', 'A', 'Tecnologia', 'facil' FROM professor p WHERE p.username = 'diego-local-seed' AND NOT EXISTS (SELECT 1 FROM questao q WHERE q.professor_id = p.id AND q.enunciado = 'Qual linguagem estrutura páginas web?');
INSERT INTO alternativa (questao_id, letra, texto)
SELECT q.id, a.letra, a.texto FROM questao q JOIN professor p ON p.id = q.professor_id CROSS JOIN (VALUES ('A', 'HTML'), ('B', 'CSS'), ('C', 'SQL'), ('D', 'Python')) a(letra, texto) WHERE p.username = 'diego-local-seed' AND q.enunciado = 'Qual linguagem estrutura páginas web?' ON CONFLICT (questao_id, letra) DO NOTHING;


-- Somente desenvolvimento; conta sem login válido. Execute schema.sql primeiro.

INSERT INTO professor (username, nome, senha_hash) VALUES ('diego-local-seed', 'Professor de desenvolvimento', '!conta-seed-sem-login!') ON CONFLICT (username) DO NOTHING;
INSERT INTO semestre (professor_id, nome, ativo) SELECT id, '2026.2', TRUE FROM professor WHERE username = 'diego-local-seed' ON CONFLICT (professor_id, nome) DO NOTHING;
INSERT INTO turma (semestre_id, nome, disciplina)
SELECT s.id, 'ADS - Desenvolvimento', 'Projeto e Arquitetura de Software' FROM semestre s JOIN professor p ON p.id = s.professor_id WHERE p.username = 'diego-local-seed' AND s.nome = '2026.2' ON CONFLICT (semestre_id, nome) DO NOTHING;
INSERT INTO aluno (turma_id, nome, matricula)
SELECT t.id, a.nome, a.matricula FROM turma t JOIN semestre s ON s.id = t.semestre_id JOIN professor p ON p.id = s.professor_id CROSS JOIN (VALUES ('Ana Exemplo', '0001'), ('Bruno Exemplo', '0002')) a(nome, matricula) WHERE p.username = 'diego-local-seed' AND t.nome = 'ADS - Desenvolvimento' ON CONFLICT (turma_id, matricula) DO NOTHING;
INSERT INTO questao (professor_id, enunciado, correta, disciplina, dificuldade)
SELECT p.id, 'Qual linguagem estrutura páginas web?', 'A', 'Tecnologia', 'facil' FROM professor p WHERE p.username = 'diego-local-seed' AND NOT EXISTS (SELECT 1 FROM questao q WHERE q.professor_id = p.id AND q.enunciado = 'Qual linguagem estrutura páginas web?');
INSERT INTO alternativa (questao_id, letra, texto)
SELECT q.id, a.letra, a.texto FROM questao q JOIN professor p ON p.id = q.professor_id CROSS JOIN (VALUES ('A', 'HTML'), ('B', 'CSS'), ('C', 'SQL'), ('D', 'Python')) a(letra, texto) WHERE p.username = 'diego-local-seed' AND q.enunciado = 'Qual linguagem estrutura páginas web?' ON CONFLICT (questao_id, letra) DO NOTHING;



DO $$
DECLARE n int;
BEGIN
 SELECT count(*) INTO n FROM professor WHERE username='diego-local-seed';
 IF n<>1 THEN RAISE EXCEPTION 'seed professor duplicated'; END IF;
 SELECT count(*) INTO n FROM aluno a JOIN turma t ON t.id=a.turma_id JOIN semestre s ON s.id=t.semestre_id JOIN professor p ON p.id=s.professor_id WHERE p.username='diego-local-seed';
 IF n<>2 THEN RAISE EXCEPTION 'seed aluno duplicated'; END IF;
 BEGIN
 INSERT INTO semestre(professor_id,nome,data_inicio,data_fim) SELECT id,'invalid-dates','2026-10-05','2026-10-04' FROM professor WHERE username='diego-local-seed';
 RAISE EXCEPTION 'date constraint missing';
 EXCEPTION WHEN check_violation THEN NULL; END;
 BEGIN
 INSERT INTO aluno(turma_id,nome,matricula) VALUES(-1,'invalid','invalid');
 RAISE EXCEPTION 'foreign key missing';
 EXCEPTION WHEN foreign_key_violation THEN NULL; END;
END $$;
SET LOCAL ROLE anon;
DO $$ DECLARE n int; BEGIN SELECT count(*) INTO n FROM public.professor; IF n<>0 THEN RAISE EXCEPTION 'anon can access professor'; END IF; EXCEPTION WHEN insufficient_privilege THEN NULL; END $$;
RESET ROLE;
SET LOCAL ROLE authenticated;
DO $$ DECLARE n int; BEGIN SELECT count(*) INTO n FROM public.professor; IF n<>0 THEN RAISE EXCEPTION 'authenticated can access professor'; END IF; EXCEPTION WHEN insufficient_privilege THEN NULL; END $$;
RESET ROLE;
ROLLBACK;
