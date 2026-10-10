-- Bucket proposto para fotos de correção; backend deve confirmar o nome.
-- Não cria acesso público nem altera buckets existentes.
BEGIN;
INSERT INTO storage.buckets(id,name,public)
VALUES ('correcoes','correcoes',false)
ON CONFLICT (id) DO NOTHING;
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM storage.buckets WHERE id='correcoes' AND public) THEN
  RAISE EXCEPTION 'Bucket correcoes precisa ser privado; revisar configuração existente';
 END IF;
END $$;
COMMIT;
