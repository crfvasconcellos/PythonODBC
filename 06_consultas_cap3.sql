-- ==============================================================================
-- ATIVIDADE: IMPLEMENTAÇÃO DOS CONCEITOS FALTANTES DO CAPÍTULO 3
-- SGBD: PostgreSQL (pgAdmin4)
-- Banco de Dados: Biblioteca
-- ==============================================================================

SET search_path TO biblioteca, public;

-- ==============================================================================
-- 1. DDL BÁSICA E MODIFICAÇÃO (ALTER TABLE, TIPOS DE DADOS E MODIFICAÇÃO AVANÇADA)
-- ==============================================================================

-- Adicionando colunas com os tipos solicitados (CHAR, SMALLINT, REAL, DOUBLE PRECISION, NUMERIC, FLOAT)
ALTER TABLE livros ADD COLUMN IF NOT EXISTS codigo_isbn CHAR(13);
ALTER TABLE livros ADD COLUMN IF NOT EXISTS edicao SMALLINT;
ALTER TABLE livros ADD COLUMN IF NOT EXISTS peso_kg REAL;
ALTER TABLE livros ADD COLUMN IF NOT EXISTS avaliacao DOUBLE PRECISION;
ALTER TABLE livros ADD COLUMN IF NOT EXISTS valor_seguro NUMERIC(10,2);
ALTER TABLE livros ADD COLUMN IF NOT EXISTS taxa_uso FLOAT;

-- Removendo coluna específica (DROP)
ALTER TABLE livros DROP COLUMN IF EXISTS taxa_uso;

-- Modificação avançada: INSERT INTO ... SELECT ...
-- Cria uma cópia da estante 1, adicionando um prefixo ao domínio
INSERT INTO estantes (dominio_lado_1, dominio_lado_2, numero_de_livros, id_espaco, tipo)
SELECT 'Cópia ' || dominio_lado_1, dominio_lado_2, 0, id_espaco, tipo
FROM estantes 
WHERE id_estante = 1;

-- Modificação avançada: UPDATE ... SET coluna = (SELECT ...)
-- Atualiza o valor do seguro do livro de ID 1 com base na média de livros das estantes
UPDATE livros 
SET valor_seguro = (SELECT AVG(numero_de_livros) * 10 FROM estantes)
WHERE id_livro = 1;

-- (Opcional) Inserindo um livro com caractere especial para testar o ESCAPE mais abaixo
INSERT INTO livros (nome, autor, numero_de_exemplares, pode_ser_emprestado, id_estante)
VALUES ('Projeto 100% Aprovado', 'Equipe de BD', 5, TRUE, 1);

-- ==============================================================================
-- 2. DML, OPERADORES, VALORES NULOS E PREDICADOS
-- ==============================================================================

-- SELECT ALL, Aritmética (+, *, /), Comparação (<, <=, >, >=, <>), Lógica (AND, OR, NOT), BETWEEN e IS NOT NULL
CREATE OR REPLACE VIEW vw_cap3_dml_operadores AS
SELECT ALL 
    nome, 
    numero_de_exemplares,
    (numero_de_exemplares + 2) * 4 / 2 AS calculo_aritmetico
FROM livros
WHERE numero_de_exemplares IS NOT NULL 
  AND numero_de_exemplares BETWEEN 5 AND 50
  AND (numero_de_exemplares > 2 OR numero_de_exemplares <= 15)
  AND numero_de_exemplares <> 3
  AND NOT (genero = 'Terror')
  AND (numero_de_exemplares + 2) * 4 / 2 >= 10;

-- Comparação de Tuplas
CREATE OR REPLACE VIEW vw_cap3_comparacao_tuplas AS
SELECT nome, autor, genero, pode_ser_emprestado
FROM livros
WHERE (pode_ser_emprestado, genero) = (TRUE, 'Ficção Científica');

-- ==============================================================================
-- 3. STRINGS E ORDENAÇÃO
-- ==============================================================================

-- UPPER, LOWER, LENGTH, SUBSTRING, Concatenação (||), LIKE, NOT LIKE, Coringas (%, _) e ESCAPE
CREATE OR REPLACE VIEW vw_cap3_strings_ordenacao AS
SELECT 
    UPPER(nome) AS nome_maiusculo,
    LOWER(autor) AS autor_minusculo,
    LENGTH(genero) AS tamanho_genero,
    SUBSTRING(nome FROM 1 FOR 5) AS prefixo_nome,
    nome || ' - Escrito por: ' || autor AS concatenacao_livro_autor
FROM livros
WHERE (nome LIKE '%a%' OR autor NOT LIKE '_eorge%')
   OR nome LIKE '%100!%%' ESCAPE '!'
ORDER BY autor ASC, numero_de_exemplares DESC;

-- ==============================================================================
-- 4. OPERAÇÕES DE CONJUNTO
-- ==============================================================================

-- UNION (Sem duplicatas) e UNION ALL (Com duplicatas)
CREATE OR REPLACE VIEW vw_cap3_conjuntos_union AS
SELECT genero AS classificacao FROM livros WHERE genero IS NOT NULL
UNION ALL
SELECT tipo AS classificacao FROM tipos_de_espaco;

-- INTERSECT e INTERSECT ALL (Interseção entre quantidades de livros e capacidades de pisos)
CREATE OR REPLACE VIEW vw_cap3_conjuntos_intersect AS
SELECT numero_de_exemplares AS numero_comum FROM livros
INTERSECT
SELECT numero_de_espacos FROM espacos;

-- EXCEPT e EXCEPT ALL (Diferença)
CREATE OR REPLACE VIEW vw_cap3_conjuntos_except AS
SELECT id_estante FROM estantes
EXCEPT ALL
SELECT id_estante FROM livros;

-- ==============================================================================
-- 5. AGREGAÇÃO E AGRUPAMENTO
-- ==============================================================================

-- AVG, MIN, MAX e HAVING
CREATE OR REPLACE VIEW vw_cap3_agregacao_having AS
SELECT 
    genero, 
    AVG(numero_de_exemplares) AS media_exemplares,
    MIN(numero_de_exemplares) AS minimo_exemplares,
    MAX(numero_de_exemplares) AS maximo_exemplares
FROM livros
WHERE genero IS NOT NULL
GROUP BY genero
HAVING AVG(numero_de_exemplares) > 5;

-- ==============================================================================
-- 6. SUBCONSULTAS ANINHADAS (IN, ANY/SOME, ALL, EXISTS, FROM, CTEs e ESCALARES)
-- ==============================================================================

-- CTE (WITH), IN, NOT IN, SOME, ALL, EXISTS, NOT EXISTS, Subconsulta no FROM e Escalar no SELECT/WHERE
CREATE OR REPLACE VIEW vw_cap3_subconsultas_avancadas AS
WITH CTE_Estantes_Ficcao AS (
    SELECT id_estante FROM estantes WHERE dominio_lado_1 = 'Ficção Científica'
)
SELECT 
    sub.nome, 
    sub.numero_de_exemplares,
    (SELECT capacidade_maxima FROM pisos LIMIT 1) AS subconsulta_escalar
FROM (SELECT id_livro, nome, numero_de_exemplares, id_estante, genero FROM livros) AS sub -- Subconsulta no FROM
WHERE sub.id_estante IN (SELECT id_estante FROM CTE_Estantes_Ficcao)
  AND sub.id_estante NOT IN (SELECT id_estante FROM estantes WHERE tipo = 'Sala de Estudos Individuais')
  AND sub.numero_de_exemplares > SOME (SELECT numero_de_exemplares FROM livros WHERE genero = 'Romance Clássico')
  AND sub.numero_de_exemplares < ALL (SELECT capacidade_maxima FROM pisos)
  AND EXISTS (SELECT 1 FROM estantes e WHERE e.id_estante = sub.id_estante)
  AND NOT EXISTS (SELECT 1 FROM tipos_de_espaco te WHERE te.tipo = 'Inexistente');