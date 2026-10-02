-- ==============================================================================
-- ATIVIDADE 1 - SCRIPT CONSOLIDADO DO BANCO DE DADOS (SCHEMA, TABELAS E INSERÇÕES)
-- Modelo Físico: Biblioteca, Edificações, Pisos, Espaços, Tipos de Espaço, Estantes e Livros
-- SGBD: PostgreSQL
-- ==============================================================================

-- 1. CRIAÇÃO DO BANCO / ESQUEMA
CREATE SCHEMA IF NOT EXISTS biblioteca;
SET search_path TO biblioteca, public;

-- 2. CRIAÇÃO DAS TABELAS E RESTRIÇÕES
DROP TABLE IF EXISTS livros CASCADE;
DROP TABLE IF EXISTS estantes CASCADE;
DROP TABLE IF EXISTS espacos CASCADE;
DROP TABLE IF EXISTS tipos_de_espaco CASCADE;
DROP TABLE IF EXISTS pisos CASCADE;
DROP TABLE IF EXISTS edificacoes CASCADE;
DROP TABLE IF EXISTS biblioteca CASCADE;

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

CREATE TABLE biblioteca (
    id_biblioteca SERIAL PRIMARY KEY,
    numero_edificacoes INT,
    diretoria VARCHAR(150)
);

CREATE TABLE edificacoes (
    id_endereco SERIAL PRIMARY KEY,
    endereco VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    id_biblioteca INT NOT NULL REFERENCES biblioteca(id_biblioteca) ON DELETE CASCADE
);

CREATE TABLE pisos (
    id_pisos SERIAL PRIMARY KEY,
    capacidade_maxima INT,
    numero_de_espacos INT,
    id_endereco INT NOT NULL REFERENCES edificacoes(id_endereco) ON DELETE CASCADE
);

CREATE TABLE tipos_de_espaco (
    tipo VARCHAR(50) PRIMARY KEY,
    numero_maximo_de_estantes INT,
    eh_privado BOOLEAN
);

CREATE TABLE espacos (
    id_espaco SERIAL PRIMARY KEY,
    numero_de_espacos INT,
    id_pisos INT NOT NULL REFERENCES pisos(id_pisos) ON DELETE CASCADE
);

CREATE TABLE estantes (
    id_estante SERIAL PRIMARY KEY,
    dominio_lado_1 VARCHAR(100),
    dominio_lado_2 VARCHAR(100),
    numero_de_livros INT,
    id_espaco INT NOT NULL REFERENCES espacos(id_espaco) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL REFERENCES tipos_de_espaco(tipo) ON DELETE CASCADE
);

CREATE TABLE livros (
    id_livro SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    numero_de_exemplares INT,
    pode_ser_emprestado BOOLEAN,
    autor VARCHAR(255),
    genero VARCHAR(100),
    id_estante INT NOT NULL REFERENCES estantes(id_estante) ON DELETE CASCADE
);

-- 3. INSERÇÃO DOS DADOS DE EXEMPLO
INSERT INTO biblioteca (numero_edificacoes, diretoria) VALUES
(3, 'Diretoria Central de Acervos'),
(2, 'Diretoria de Pesquisa Acadêmica'),
(1, 'Diretoria de Tecnologia e Cultura');

INSERT INTO edificacoes (endereco, telefone, id_biblioteca) VALUES
('Av. Paulista, 1000 - Bela Vista, São Paulo/SP', '(11) 3222-1000', 1),
('Rua da Consolação, 500 - Centro, São Paulo/SP', '(11) 3100-2000', 1),
('Av. Afonso Pena, 1500 - Centro, Belo Horizonte/MG', '(31) 3400-5000', 2),
('Rua XV de Novembro, 800 - Centro, Curitiba/PR', '(41) 3300-8000', 3);

INSERT INTO pisos (capacidade_maxima, numero_de_espacos, id_endereco) VALUES
(500, 4, 1),
(800, 6, 1),
(300, 3, 2),
(600, 5, 3),
(400, 4, 4);

INSERT INTO tipos_de_espaco (tipo, numero_maximo_de_estantes, eh_privado) VALUES
('Sala de Leitura Geral', 20, FALSE),
('Acervo Geral de Livros', 50, FALSE),
('Sala de Estudos Individuais', 5, TRUE),
('Laboratório de Coleções Raras', 10, TRUE),
('Auditório e Arquivo', 15, FALSE);

INSERT INTO espacos (numero_de_espacos, id_pisos) VALUES
(4, 1),
(6, 2),
(3, 3),
(5, 4),
(4, 5);

INSERT INTO estantes (dominio_lado_1, dominio_lado_2, numero_de_livros, id_espaco, tipo) VALUES
('Ficção Científica', 'Romance Clássico', 120, 1, 'Acervo Geral de Livros'),
('História Universal', 'Biografia', 85, 1, 'Sala de Leitura Geral'),
('Literatura Brasileira', 'Poesia', 150, 2, 'Acervo Geral de Livros'),
('Obras Raras Séc. XIX', 'Manuscritos', 45, 2, 'Laboratório de Coleções Raras'),
('Filosofia e Sociologia', 'Psicologia', 90, 4, 'Sala de Estudos Individuais'),
('Tecnologia e Informática', 'Engenharia', 200, 5, 'Auditório e Arquivo');

INSERT INTO livros (nome, numero_de_exemplares, pode_ser_emprestado, autor, genero, id_estante) VALUES
('Dom Casmurro', 15, TRUE, 'Machado de Assis', 'Romance Clássico', 3),
('Memórias Póstumas de Brás Cubas', 10, TRUE, 'Machado de Assis', 'Romance Clássico', 3),
('1984', 25, TRUE, 'George Orwell', 'Ficção Científica', 1),
('A Revolução dos Bichos', 20, TRUE, 'George Orwell', 'Ficção Científica', 1),
('O Capital no Século XXI', 8, TRUE, 'Thomas Piketty', 'Filosofia e Sociologia', 5),
('Primeira Edição Carta de Pero Vaz de Caminha', 1, FALSE, 'Pero Vaz de Caminha', 'Obras Raras Séc. XIX', 4),
('Manuscrito Histórico Imperial', 2, FALSE, 'D. Pedro II', 'Manuscritos', 4),
('Clean Code', 12, TRUE, 'Robert C. Martin', 'Tecnologia e Informática', 6),
('Design Patterns', 10, TRUE, 'Erich Gamma et al.', 'Tecnologia e Informática', 6),
('Cem Anos de Solidão', 18, TRUE, 'Gabriel García Márquez', 'Literatura Brasileira', 3);
