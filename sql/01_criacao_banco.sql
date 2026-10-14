-- ==============================================================================
-- ATIVIDADE 1 - PARTE 1: CRIAÇÃO DO ESQUEMA / BANCO DE DADOS
-- Modelo Físico: Biblioteca, Edificações, Pisos, Espaços, Tipos de Espaço, Estantes e Livros
-- SGBD: PostgreSQL
-- ==============================================================================

-- Criacao do esquema 'biblioteca'
CREATE SCHEMA IF NOT EXISTS biblioteca;

-- Definindo o esquema padrao para a sessao
SET search_path TO biblioteca, public;
