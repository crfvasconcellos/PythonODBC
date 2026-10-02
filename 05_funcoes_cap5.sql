-- Function e procedure do capítulo 5 (funções/procedures armazenadas)
-- Usadas pelo main.py nas opções 5 e 6 do menu.
-- Rodar esse script no banco antes de testar essas opções, senão dá
-- erro de função inexistente.
--
-- Obs: trabalham em cima da tabela "livros" simples que o main.py cria
-- sozinho (schema public). Não tem relação com a tabela "livros" do
-- schema biblioteca usada nas atividades 1 e 2.

-- conta quantos livros um autor tem cadastrado
CREATE OR REPLACE FUNCTION fn_contar_livros_por_autor(p_autor VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total
    FROM livros
    WHERE autor = p_autor;

    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- uso: SELECT * FROM fn_contar_livros_por_autor('Machado de Assis');


-- insere um livro novo (mesma coisa que o INSERT do cadastrar_livro,
-- só que rodando dentro do banco em vez de vir do Python)
CREATE OR REPLACE PROCEDURE sp_cadastrar_livro(
    p_titulo VARCHAR,
    p_autor  VARCHAR,
    p_ano    INT,
    p_preco  NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO livros (titulo, autor, ano, preco)
    VALUES (p_titulo, p_autor, p_ano, p_preco);
END;
$$;

-- uso: CALL sp_cadastrar_livro('O Alienista', 'Machado de Assis', 1882, 29.90);
