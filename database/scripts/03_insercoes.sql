-- ==============================================================================
-- ATIVIDADE 1 - PARTE 3: INSERÇÃO DE DADOS DE EXEMPLO
-- SGBD: PostgreSQL
-- ==============================================================================

SET search_path TO biblioteca, public;

-- 1. Inserindo Bibliotecas
INSERT INTO biblioteca (numero_edificacoes, diretoria) VALUES
(3, 'Diretoria Central de Acervos'),
(2, 'Diretoria de Pesquisa Acadêmica'),
(1, 'Diretoria de Tecnologia e Cultura');

-- 2. Inserindo Bibliotecários (chaves candidatas UNIQUE: email e cpf)
INSERT INTO bibliotecarios (nome, email, cpf, status) VALUES
('Ana Paula Mendes', 'ana.mendes@biblioteca.edu.br', '11122233344', 'Ativo'),
('Carlos Eduardo Lima', 'carlos.lima@biblioteca.edu.br', '55566677788', 'Ativo'),
('Mariana Souza', 'mariana.souza@biblioteca.edu.br', '99988877766', 'Ferias');

-- 3. Inserindo Edificações (com responsável vinculado via ON DELETE SET NULL)
INSERT INTO edificacoes (endereco, telefone, id_biblioteca, id_responsavel) VALUES
('Av. Paulista, 1000 - Bela Vista, São Paulo/SP', '(11) 3222-1000', 1, 1),
('Rua da Consolação, 500 - Centro, São Paulo/SP', '(11) 3100-2000', 1, 2),
('Av. Afonso Pena, 1500 - Centro, Belo Horizonte/MG', '(31) 3400-5000', 2, 1),
('Rua XV de Novembro, 800 - Centro, Curitiba/PR', '(41) 3300-8000', 3, 3);

-- 4. Inserindo Fichas Técnicas das Edificações (Relacionamento 1:1)
INSERT INTO ficha_tecnica_edificacao (id_endereco, ano_construcao, area_m2, possui_acessibilidade) VALUES
(1, 1985, 3200.50, TRUE),
(2, 1972, 1850.00, TRUE),
(3, 1998, 2400.75, TRUE),
(4, 2005, 1950.25, FALSE);

-- 5. Inserindo Pisos
INSERT INTO pisos (capacidade_maxima, numero_de_espacos, id_endereco) VALUES
(500, 4, 1),
(800, 6, 1),
(300, 3, 2),
(600, 5, 3),
(400, 4, 4);

-- 6. Inserindo Tipos de Espaço
INSERT INTO tipos_de_espaco (tipo, numero_maximo_de_estantes, eh_privado) VALUES
('Sala de Leitura Geral', 20, FALSE),
('Acervo Geral de Livros', 50, FALSE),
('Sala de Estudos Individuais', 5, TRUE),
('Laboratório de Coleções Raras', 10, TRUE),
('Auditório e Arquivo', 15, FALSE);

-- 7. Inserindo Espaços
INSERT INTO espacos (numero_de_espacos, id_pisos) VALUES
(4, 1),
(6, 2),
(3, 3),
(5, 4),
(4, 5);

-- 8. Inserindo Estantes (Vinculadas ao espaco e ao tipo_de_espaco)
INSERT INTO estantes (dominio_lado_1, dominio_lado_2, numero_de_livros, id_espaco, tipo) VALUES
('Ficção Científica', 'Romance Clássico', 120, 1, 'Acervo Geral de Livros'),
('História Universal', 'Biografia', 85, 1, 'Sala de Leitura Geral'),
('Literatura Brasileira', 'Poesia', 150, 2, 'Acervo Geral de Livros'),
('Obras Raras Séc. XIX', 'Manuscritos', 45, 2, 'Laboratório de Coleções Raras'),
('Filosofia e Sociologia', 'Psicologia', 90, 4, 'Sala de Estudos Individuais'),
('Tecnologia e Informática', 'Engenharia', 200, 5, 'Auditório e Arquivo');

-- 9. Inserindo Categorias do Acervo (ID 1 é o padrão usado no ON DELETE SET DEFAULT)
INSERT INTO categorias_acervo (id_categoria, nome) VALUES
(1, 'Geral'),
(2, 'Clássicos Literários'),
(3, 'Ciências e Tecnologia'),
(4, 'Raridades Históricas');

-- 10. Inserindo Livros
INSERT INTO livros (nome, numero_de_exemplares, pode_ser_emprestado, autor, genero, id_estante, id_categoria, codigo_patrimonio, status_conservacao) VALUES
('Dom Casmurro', 15, TRUE, 'Machado de Assis', 'Romance Clássico', 3, 2, 'PAT-0001', 'Bom'),
('Memórias Póstumas de Brás Cubas', 10, TRUE, 'Machado de Assis', 'Romance Clássico', 3, 2, 'PAT-0002', 'Novo'),
('1984', 25, TRUE, 'George Orwell', 'Ficção Científica', 1, 2, 'PAT-0003', 'Bom'),
('A Revolução dos Bichos', 20, TRUE, 'George Orwell', 'Ficção Científica', 1, 2, 'PAT-0004', 'Bom'),
('O Capital no Século XXI', 8, TRUE, 'Thomas Piketty', 'Filosofia e Sociologia', 5, 1, 'PAT-0005', 'Novo'),
('Primeira Edição Carta de Pero Vaz de Caminha', 1, FALSE, 'Pero Vaz de Caminha', 'Obras Raras Séc. XIX', 4, 4, 'PAT-0006', 'Regular'),
('Manuscrito Histórico Imperial', 2, FALSE, 'D. Pedro II', 'Manuscritos', 4, 4, 'PAT-0007', 'Danificado'),
('Clean Code', 12, TRUE, 'Robert C. Martin', 'Tecnologia e Informática', 6, 3, 'PAT-0008', 'Novo'),
('Design Patterns', 10, TRUE, 'Erich Gamma et al.', 'Tecnologia e Informática', 6, 3, 'PAT-0009', 'Bom'),
('Cem Anos de Solidão', 18, TRUE, 'Gabriel García Márquez', 'Literatura Brasileira', 3, 2, 'PAT-0010', 'Bom');

-- 11. Inserindo Tags e Associação N:M (Chave Primária Composta em livro_tag)
INSERT INTO tags (nome) VALUES
('Leitura Obrigatória'),
('Clássico Mundial'),
('Acervo Histórico'),
('Engenharia de Software');

INSERT INTO livro_tag (id_livro, id_tag) VALUES
(1, 1),
(1, 2),
(3, 2),
(6, 3),
(8, 4),
(9, 4);
