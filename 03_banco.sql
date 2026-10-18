-- =====================================================================
-- Projeto Aplicado I - UniSENAI Santa Catarina
-- Tema 02: Modelagem e Implementacao de Banco de Dados
-- Empresa parceira: Schulz S.A.
-- Grupo: Otavio Modolon Neto, Thiago Neves Gomes, Lucas Antonio Severino
--
-- Script DDL de criacao das tabelas - SQLite
-- Banco: certificados.db
-- Execucao: sqlite3 certificados.db < 03_banco.sql
-- =====================================================================

-- O SQLite nao aplica chave estrangeira por padrao; a verificacao
-- precisa ser ligada em toda conexao, inclusive na do script Python.
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS medicao;
DROP TABLE IF EXISTS equipamento;
DROP TABLE IF EXISTS tecnico;

-- ---------------------------------------------------------------------
-- Tabela 1: tecnico
-- Pessoas e setores que participam da calibracao: o metrologista que
-- executa, o setor que solicita e o signatario que aprova.
-- A matricula e a chave de identificacao, nao o nome.
-- ---------------------------------------------------------------------
CREATE TABLE tecnico (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula     TEXT UNIQUE,
    nome          TEXT    NOT NULL,
    setor         TEXT,
    funcao        TEXT    NOT NULL
                  CHECK (funcao IN ('executante', 'solicitante', 'signatario')),
    pode_assinar  INTEGER NOT NULL DEFAULT 0
                  CHECK (pode_assinar IN (0, 1))
);

-- ---------------------------------------------------------------------
-- Tabela 2: equipamento
-- Instrumento calibrado e padrao de calibracao, separados pela coluna
-- tipo. As datas de calibracao do padrao sustentam a verificacao de
-- vigencia na data da medicao.
-- ---------------------------------------------------------------------
CREATE TABLE equipamento (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo                  TEXT NOT NULL UNIQUE,
    tag                     TEXT UNIQUE,
    denominacao             TEXT NOT NULL,
    tipo                    TEXT NOT NULL
                            CHECK (tipo IN ('instrumento', 'padrao')),
    fabricante              TEXT,
    modelo                  TEXT,
    num_serie               TEXT,
    resolucao_mm            REAL,
    num_certificado_padrao  TEXT,
    data_ult_calibracao     TEXT,
    data_prox_calibracao    TEXT
);

-- ---------------------------------------------------------------------
-- Tabela 3: medicao
-- Uma linha por caracteristica e por execucao da medicao, o que remove o
-- limite de 35 caracteristicas e de duas repeticoes da planilha atual.
-- As chaves estrangeiras ligam a medicao ao instrumento, ao padrao,
-- ao tecnico executante e ao setor solicitante.
-- ---------------------------------------------------------------------
CREATE TABLE medicao (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    equipamento_id   INTEGER NOT NULL,
    padrao_id        INTEGER NOT NULL,
    tecnico_id       INTEGER NOT NULL,
    solicitante_id   INTEGER,
    num_certificado  TEXT,
    data_execucao    TEXT    NOT NULL,
    temperatura_c    REAL,
    caracteristica     TEXT    NOT NULL,
    sequencia_medicao  INTEGER NOT NULL CHECK (sequencia_medicao >= 1),
    valor_nominal    REAL    NOT NULL,
    tol_superior     REAL    NOT NULL,
    tol_inferior     REAL    NOT NULL,
    valor_medido     REAL    NOT NULL,
    erro             REAL,
    status           TEXT    CHECK (status IN ('conforme', 'nao conforme')),

    -- Impede gravar duas vezes a mesma caracteristica da mesma execucao,
    -- situacao que a colagem manual na planilha permitia.
    UNIQUE (equipamento_id, data_execucao, caracteristica, sequencia_medicao),

    FOREIGN KEY (equipamento_id) REFERENCES equipamento (id),
    FOREIGN KEY (padrao_id)      REFERENCES equipamento (id),
    FOREIGN KEY (tecnico_id)     REFERENCES tecnico (id),
    FOREIGN KEY (solicitante_id) REFERENCES tecnico (id)
);
