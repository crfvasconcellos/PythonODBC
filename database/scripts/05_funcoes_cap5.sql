-- ==============================================================================
-- CAPÍTULO 5: FUNCTIONS (Escalar e Table Function), PROCEDURE e TRIGGERS (BEFORE e AFTER)
-- Schema: biblioteca | SGBD: PostgreSQL
-- ==============================================================================

SET search_path TO biblioteca, public;

-- 1. FUNÇÃO ESCALAR: conta quantos livros de um autor existem em biblioteca.livros
CREATE OR REPLACE FUNCTION public.fn_contar_livros_por_autor(p_autor VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total
    FROM biblioteca.livros
    WHERE autor ILIKE '%' || p_autor || '%';

    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- 2. TABLE FUNCTION (RETURNS TABLE): retorna conjunto estruturado de livros por gênero
CREATE OR REPLACE FUNCTION biblioteca.fn_listar_livros_por_genero(p_genero VARCHAR)
RETURNS TABLE (
    id_livro INT,
    nome VARCHAR,
    autor VARCHAR,
    numero_de_exemplares INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT l.id_livro, l.nome, l.autor, l.numero_de_exemplares
    FROM biblioteca.livros l
    WHERE l.genero ILIKE '%' || p_genero || '%'
    ORDER BY l.numero_de_exemplares DESC, l.nome ASC;
END;
$$ LANGUAGE plpgsql;

-- 3. STORED PROCEDURE (CALL): cadastra livro em biblioteca.livros
DROP PROCEDURE IF EXISTS public.sp_cadastrar_livro(VARCHAR, VARCHAR, INT, NUMERIC);
CREATE OR REPLACE PROCEDURE public.sp_cadastrar_livro(
    p_nome VARCHAR,
    p_autor VARCHAR,
    p_genero VARCHAR,
    p_exemplares INT,
    p_emprestavel BOOLEAN,
    p_id_estante INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO biblioteca.livros
        (nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante)
    VALUES
        (p_nome, p_autor, p_genero, p_exemplares, p_emprestavel, p_id_estante);
END;
$$;

-- 4. TRIGGER BEFORE (variável NEW): padroniza texto/patrimônio e barra nome em branco antes de gravar
CREATE OR REPLACE FUNCTION biblioteca.fn_padronizar_livro_before()
RETURNS TRIGGER AS $$
BEGIN
    NEW.nome := BTRIM(NEW.nome);
    IF NEW.nome = '' THEN
        RAISE EXCEPTION 'O título do livro não pode conter apenas espaços.';
    END IF;

    IF NEW.codigo_patrimonio IS NOT NULL THEN
        NEW.codigo_patrimonio := UPPER(BTRIM(NEW.codigo_patrimonio));
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_padronizar_livro_before ON biblioteca.livros;
CREATE TRIGGER trg_padronizar_livro_before
BEFORE INSERT OR UPDATE ON biblioteca.livros
FOR EACH ROW
EXECUTE FUNCTION biblioteca.fn_padronizar_livro_before();

-- 5. TRIGGER AFTER (variável OLD): registra auditoria automática após DELETE
CREATE OR REPLACE FUNCTION biblioteca.fn_auditar_exclusao_livro()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO biblioteca.auditoria_livros_excluidos
        (id_livro_apagado, nome_livro, autor)
    VALUES
        (OLD.id_livro, OLD.nome, OLD.autor);

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auditoria_exclusao ON biblioteca.livros;
CREATE TRIGGER trg_auditoria_exclusao
AFTER DELETE ON biblioteca.livros
FOR EACH ROW
EXECUTE FUNCTION biblioteca.fn_auditar_exclusao_livro();
