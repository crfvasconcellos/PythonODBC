-- ==============================================================================
-- ATIVIDADE 1 - PARTE 2: CRIAÇÃO DAS TABELAS E RESTRIÇÕES DE INTEGRIDADE
-- Cobertura Completa de DDL (Cap. 1, 2, 3 e 4 - Silberschatz):
--   * PK Simples e PK Composta (N:M)
--   * FK com relacionamentos 1:1, 1:N e N:M
--   * Ações referenciais: ON DELETE CASCADE, ON UPDATE CASCADE,
--     ON DELETE SET NULL e ON DELETE SET DEFAULT
--   * UNIQUE, NOT NULL, CHECK (faixa e IN), DEFAULT, DROP TABLE e ALTER TABLE
-- SGBD: PostgreSQL
-- ==============================================================================

SET search_path TO biblioteca, public;

-- 1. Limpeza prévia de tabelas (DROP TABLE em ordem reversa de dependência)
DROP TABLE IF EXISTS livro_tag CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS auditoria_livros_excluidos CASCADE;
DROP TABLE IF EXISTS livros CASCADE;
DROP TABLE IF EXISTS categorias_acervo CASCADE;
DROP TABLE IF EXISTS estantes CASCADE;
DROP TABLE IF EXISTS espacos CASCADE;
DROP TABLE IF EXISTS tipos_de_espaco CASCADE;
DROP TABLE IF EXISTS pisos CASCADE;
DROP TABLE IF EXISTS ficha_tecnica_edificacao CASCADE;
DROP TABLE IF EXISTS edificacoes CASCADE;
DROP TABLE IF EXISTS bibliotecarios CASCADE;
DROP TABLE IF EXISTS biblioteca CASCADE;

-- 2. Limpeza de tabelas descontinuadas do modelo antigo
DROP TABLE IF EXISTS livro_promocao CASCADE;
DROP TABLE IF EXISTS promocoes CASCADE;
DROP TABLE IF EXISTS avaliacoes CASCADE;
DROP TABLE IF EXISTS itens_pedido CASCADE;
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS funcionarios CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;
DROP TABLE IF EXISTS editoras CASCADE;
DROP TABLE IF EXISTS autores CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS cidades CASCADE;

-- ==============================================================================
-- CRIAÇÃO DAS TABELAS E RESTRIÇÕES DE INTEGRIDADE
-- ==============================================================================

-- 1. Tabela Biblioteca (PK simples + CHECK de faixa)
CREATE TABLE biblioteca (
    id_biblioteca SERIAL PRIMARY KEY,
    numero_edificacoes INT DEFAULT 1 CHECK (numero_edificacoes >= 0),
    diretoria VARCHAR(150) NOT NULL
);

-- 2. Tabela Bibliotecários (UNIQUE em chaves candidatas + CHECK com IN + DEFAULT)
CREATE TABLE bibliotecarios (
    id_bibliotecario SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    cpf CHAR(11) NOT NULL UNIQUE CHECK (LENGTH(cpf) = 11),
    status VARCHAR(20) NOT NULL DEFAULT 'Ativo'
        CHECK (status IN ('Ativo', 'Inativo', 'Ferias'))
);

-- 3. Tabela Edificações (1:N com biblioteca + ON DELETE SET NULL com bibliotecarios)
CREATE TABLE edificacoes (
    id_endereco SERIAL PRIMARY KEY,
    endereco VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) UNIQUE,
    id_biblioteca INT NOT NULL
        REFERENCES biblioteca(id_biblioteca) ON DELETE CASCADE ON UPDATE CASCADE,
    id_responsavel INT
        REFERENCES bibliotecarios(id_bibliotecario) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 4. Tabela Ficha Técnica da Edificação (Relacionamento 1:1 via FK + UNIQUE + CHECK de faixa)
CREATE TABLE ficha_tecnica_edificacao (
    id_ficha SERIAL PRIMARY KEY,
    id_endereco INT NOT NULL UNIQUE
        REFERENCES edificacoes(id_endereco) ON DELETE CASCADE ON UPDATE CASCADE,
    ano_construcao INT NOT NULL CHECK (ano_construcao >= 1800 AND ano_construcao <= 2100),
    area_m2 NUMERIC(10, 2) NOT NULL CHECK (area_m2 > 0),
    possui_acessibilidade BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Tabela Pisos (1:N com edificacoes + CHECK de faixa)
CREATE TABLE pisos (
    id_pisos SERIAL PRIMARY KEY,
    capacidade_maxima INT NOT NULL CHECK (capacidade_maxima > 0),
    numero_de_espacos INT NOT NULL DEFAULT 1 CHECK (numero_de_espacos >= 0),
    id_endereco INT NOT NULL
        REFERENCES edificacoes(id_endereco) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 6. Tabela Tipos de Espaço (PK natural VARCHAR + CHECK de faixa + DEFAULT)
CREATE TABLE tipos_de_espaco (
    tipo VARCHAR(50) PRIMARY KEY,
    numero_maximo_de_estantes INT NOT NULL CHECK (numero_maximo_de_estantes > 0),
    eh_privado BOOLEAN NOT NULL DEFAULT FALSE
);

-- 7. Tabela Espaços (1:N com pisos)
CREATE TABLE espacos (
    id_espaco SERIAL PRIMARY KEY,
    numero_de_espacos INT NOT NULL CHECK (numero_de_espacos >= 0),
    id_pisos INT NOT NULL
        REFERENCES pisos(id_pisos) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8. Tabela Estantes (ON DELETE CASCADE e ON UPDATE CASCADE em tipos_de_espaco)
CREATE TABLE estantes (
    id_estante SERIAL PRIMARY KEY,
    dominio_lado_1 VARCHAR(100),
    dominio_lado_2 VARCHAR(100),
    numero_de_livros INT DEFAULT 0 CHECK (numero_de_livros >= 0),
    id_espaco INT NOT NULL
        REFERENCES espacos(id_espaco) ON DELETE CASCADE ON UPDATE CASCADE,
    tipo VARCHAR(50) NOT NULL
        REFERENCES tipos_de_espaco(tipo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 9. Tabela Categorias do Acervo (suporte ao ON DELETE SET DEFAULT em livros)
CREATE TABLE categorias_acervo (
    id_categoria INT PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE
);

-- 10. Tabela Livros (NOT NULL, UNIQUE, CHECK faixa + IN, DEFAULT, ON DELETE CASCADE e SET DEFAULT)
CREATE TABLE livros (
    id_livro SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    numero_de_exemplares INT NOT NULL DEFAULT 1 CHECK (numero_de_exemplares >= 0),
    pode_ser_emprestado BOOLEAN NOT NULL DEFAULT TRUE,
    autor VARCHAR(255),
    genero VARCHAR(100),
    codigo_patrimonio VARCHAR(30) UNIQUE,
    status_conservacao VARCHAR(20) NOT NULL DEFAULT 'Bom'
        CHECK (status_conservacao IN ('Novo', 'Bom', 'Regular', 'Danificado')),
    data_cadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_estante INT NOT NULL
        REFERENCES estantes(id_estante) ON DELETE CASCADE ON UPDATE CASCADE,
    id_categoria INT DEFAULT 1
        REFERENCES categorias_acervo(id_categoria) ON DELETE SET DEFAULT ON UPDATE CASCADE
);

-- 11. Tabela Tags (para relacionamento N:M com livros)
CREATE TABLE tags (
    id_tag SERIAL PRIMARY KEY,
    nome VARCHAR(60) NOT NULL UNIQUE
);

-- 12. Tabela Associativa Livro_Tag (Relacionamento N:M + Chave Primária Composta)
CREATE TABLE livro_tag (
    id_livro INT NOT NULL
        REFERENCES livros(id_livro) ON DELETE CASCADE ON UPDATE CASCADE,
    id_tag INT NOT NULL
        REFERENCES tags(id_tag) ON DELETE CASCADE ON UPDATE CASCADE,
    data_associacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_livro, id_tag)
);

-- 13. Tabela de Auditoria de Livros Excluídos (DEFAULT CURRENT_TIMESTAMP e CURRENT_USER)
CREATE TABLE biblioteca.auditoria_livros_excluidos (
    id_auditoria SERIAL PRIMARY KEY,
    id_livro_apagado INT,
    nome_livro VARCHAR(255),
    autor VARCHAR(255),
    data_exclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_banco VARCHAR(50) DEFAULT CURRENT_USER
);

-- ==============================================================================
-- MODIFICAÇÃO DE ESQUEMA (ALTER TABLE ADD COLUMN / DROP COLUMN)
-- ==============================================================================
ALTER TABLE livros ADD COLUMN observacao_temporaria VARCHAR(100);
ALTER TABLE livros DROP COLUMN observacao_temporaria;
