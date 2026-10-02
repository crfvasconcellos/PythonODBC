-- ==============================================================================
-- ATIVIDADE 1 - PARTE 2: CRIAÇÃO DAS TABELAS E RESTRIÇÕES (PK, FK, NOT NULL)
-- Modelo Físico: biblioteca -> edificacoes -> pisos -> espacos & tipos_de_espaco -> estantes -> livros
-- SGBD: PostgreSQL
-- ==============================================================================

SET search_path TO biblioteca, public;

-- 1. Limpeza previa de tabelas do modelo atual (ordem reversa de dependencia)
DROP TABLE IF EXISTS livros CASCADE;
DROP TABLE IF EXISTS estantes CASCADE;
DROP TABLE IF EXISTS espacos CASCADE;
DROP TABLE IF EXISTS tipos_de_espaco CASCADE;
DROP TABLE IF EXISTS pisos CASCADE;
DROP TABLE IF EXISTS edificacoes CASCADE;
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
-- CRIAÇÃO DAS TABELAS (EXATAMENTE COMO NO NOVO DIAGRAMA FÍSICO)
-- ==============================================================================

-- 1. Tabela Biblioteca
CREATE TABLE biblioteca (
    id_biblioteca SERIAL PRIMARY KEY,
    numero_edificacoes INT,
    diretoria VARCHAR(150)
);

-- 2. Tabela Edificações
CREATE TABLE edificacoes (
    id_endereco SERIAL PRIMARY KEY,
    endereco VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    id_biblioteca INT NOT NULL REFERENCES biblioteca(id_biblioteca) ON DELETE CASCADE
);

-- 3. Tabela Pisos
CREATE TABLE pisos (
    id_pisos SERIAL PRIMARY KEY,
    capacidade_maxima INT,
    numero_de_espacos INT,
    id_endereco INT NOT NULL REFERENCES edificacoes(id_endereco) ON DELETE CASCADE
);

-- 4. Tabela Tipos de Espaço
CREATE TABLE tipos_de_espaco (
    tipo VARCHAR(50) PRIMARY KEY,
    numero_maximo_de_estantes INT,
    eh_privado BOOLEAN
);

-- 5. Tabela Espaços
CREATE TABLE espacos (
    id_espaco SERIAL PRIMARY KEY,
    numero_de_espacos INT,
    id_pisos INT NOT NULL REFERENCES pisos(id_pisos) ON DELETE CASCADE
);

-- 6. Tabela Estantes
CREATE TABLE estantes (
    id_estante SERIAL PRIMARY KEY,
    dominio_lado_1 VARCHAR(100),
    dominio_lado_2 VARCHAR(100),
    numero_de_livros INT,
    id_espaco INT NOT NULL REFERENCES espacos(id_espaco) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL REFERENCES tipos_de_espaco(tipo) ON DELETE CASCADE
);

-- 7. Tabela Livros
CREATE TABLE livros (
    id_livro SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    numero_de_exemplares INT,
    pode_ser_emprestado BOOLEAN,
    autor VARCHAR(255),
    genero VARCHAR(100),
    id_estante INT NOT NULL REFERENCES estantes(id_estante) ON DELETE CASCADE
);
