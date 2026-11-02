"""
Projeto Aplicado I - UniSENAI Santa Catarina
AV 03: Construção do MVP (Parte 1)
Empresa parceira: Schulz S.A.
Grupo: Otávio Modolon Neto, Thiago Neves Gomes, Lucas Antunes Severino

Classes de domínio e de persistência do sistema de emissão de certificados
de calibração. O banco é o SQLite modelado na AV 02 (03_banco.sql), com as
tabelas tecnico, equipamento e medicao.

Classes:
    Tecnico      - pessoa ou setor que participa da calibração
    Equipamento  - instrumento calibrado ou padrão de calibração
    Medicao      - resultado de uma característica, com a validação de status
    BancoDados   - conexão sqlite3 e comandos INSERT, SELECT e UPDATE
"""

import sqlite3
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------
# Exceções do sistema
# ---------------------------------------------------------------------

class ErroValidacao(Exception):
    """Dado recusado pelas regras de negócio, antes de chegar ao banco."""


class ErroBanco(Exception):
    """Comando recusado pelo SQLite (chave, domínio ou conexão)."""


def _data_iso(texto, campo, obrigatoria=True):
    """Confere se a data está no formato AAAA-MM-DD (com ou sem hora)."""
    if texto is None or str(texto).strip() == "":
        if obrigatoria:
            raise ErroValidacao(f"{campo} é obrigatório")
        return None
    texto = str(texto).strip()
    try:
        date.fromisoformat(texto[:10])
    except ValueError:
        raise ErroValidacao(f"{campo} fora do formato AAAA-MM-DD: {texto}") from None
    return texto


def _texto_opcional(valor):
    """Texto vazio vira None. É a única forma de ausência aceita (A01)."""
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor or None


# ---------------------------------------------------------------------
# Classe Tecnico
# ---------------------------------------------------------------------

class Tecnico:
    """Profissional calibrador, setor solicitante ou signatário."""

    FUNCOES = ("executante", "solicitante", "signatario")

    def __init__(self, nome, funcao, matricula=None, setor=None,
                 pode_assinar=False, id_tecnico=None):
        self.id_tecnico = id_tecnico
        self.nome = nome
        self.funcao = funcao
        self.matricula = matricula
        self.setor = setor
        self.pode_assinar = pode_assinar

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        valor = _texto_opcional(valor)
        if valor is None:
            raise ErroValidacao("nome do técnico é obrigatório")
        self._nome = valor

    @property
    def funcao(self):
        return self._funcao

    @funcao.setter
    def funcao(self, valor):
        valor = str(valor).strip().lower()
        if valor not in self.FUNCOES:
            raise ErroValidacao(f"função inválida: {valor}. Use {', '.join(self.FUNCOES)}")
        self._funcao = valor

    @property
    def matricula(self):
        return self._matricula

    @matricula.setter
    def matricula(self, valor):
        self._matricula = _texto_opcional(valor)

    @property
    def setor(self):
        return self._setor

    @setor.setter
    def setor(self, valor):
        self._setor = _texto_opcional(valor)

    @property
    def pode_assinar(self):
        return self._pode_assinar

    @pode_assinar.setter
    def pode_assinar(self, valor):
        self._pode_assinar = bool(valor)

    @classmethod
    def de_linha(cls, linha):
        """Monta o objeto a partir de uma linha lida do banco."""
        return cls(nome=linha["nome"], funcao=linha["funcao"],
                   matricula=linha["matricula"], setor=linha["setor"],
                   pode_assinar=linha["pode_assinar"], id_tecnico=linha["id"])

    def __str__(self):
        return f"{self.nome} ({self.funcao}, matrícula {self.matricula or '-'})"


# ---------------------------------------------------------------------
# Classe Equipamento
# ---------------------------------------------------------------------

class Equipamento:
    """Instrumento de medição calibrado ou padrão usado na calibração."""

    TIPOS = ("instrumento", "padrao")

    def __init__(self, codigo, denominacao, tipo, tag=None, fabricante=None,
                 modelo=None, num_serie=None, resolucao_mm=None,
                 num_certificado_padrao=None, data_ult_calibracao=None,
                 data_prox_calibracao=None, id_equipamento=None):
        self.id_equipamento = id_equipamento
        self.codigo = codigo
        self.denominacao = denominacao
        self.tipo = tipo
        self.tag = tag
        self.fabricante = _texto_opcional(fabricante)
        self.modelo = _texto_opcional(modelo)
        self.num_serie = _texto_opcional(num_serie)
        self.resolucao_mm = resolucao_mm
        self.num_certificado_padrao = _texto_opcional(num_certificado_padrao)
        self.data_ult_calibracao = data_ult_calibracao
        self.data_prox_calibracao = data_prox_calibracao

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        # O mesmo equipamento aparecia como 500.011 e 500011 (A13).
        # O código é gravado só com dígitos.
        valor = "".join(c for c in str(valor) if c.isdigit())
        if not valor:
            raise ErroValidacao("código do equipamento é obrigatório e numérico")
        self._codigo = valor

    @property
    def denominacao(self):
        return self._denominacao

    @denominacao.setter
    def denominacao(self, valor):
        valor = _texto_opcional(valor)
        if valor is None:
            raise ErroValidacao("denominação do equipamento é obrigatória")
        self._denominacao = valor

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        valor = str(valor).strip().lower()
        if valor not in self.TIPOS:
            raise ErroValidacao(f"tipo inválido: {valor}. Use instrumento ou padrao")
        self._tipo = valor

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, valor):
        self._tag = _texto_opcional(valor)

    @property
    def resolucao_mm(self):
        return self._resolucao_mm

    @resolucao_mm.setter
    def resolucao_mm(self, valor):
        if valor is None:
            self._resolucao_mm = None
            return
        valor = float(valor)
        if valor <= 0:
            raise ErroValidacao("resolução deve ser maior que zero")
        self._resolucao_mm = valor

    @property
    def data_ult_calibracao(self):
        return self._data_ult_calibracao

    @data_ult_calibracao.setter
    def data_ult_calibracao(self, valor):
        self._data_ult_calibracao = _data_iso(valor, "data_ult_calibracao", False)

    @property
    def data_prox_calibracao(self):
        return self._data_prox_calibracao

    @data_prox_calibracao.setter
    def data_prox_calibracao(self, valor):
        self._data_prox_calibracao = _data_iso(valor, "data_prox_calibracao", False)

    def esta_vigente(self, data_referencia):
        """Indica se a calibração do padrão vale na data informada."""
        if self.data_prox_calibracao is None:
            return False
        return self.data_prox_calibracao[:10] >= str(data_referencia)[:10]

    @classmethod
    def de_linha(cls, linha):
        return cls(codigo=linha["codigo"], denominacao=linha["denominacao"],
                   tipo=linha["tipo"], tag=linha["tag"],
                   fabricante=linha["fabricante"], modelo=linha["modelo"],
                   num_serie=linha["num_serie"],
                   resolucao_mm=linha["resolucao_mm"],
                   num_certificado_padrao=linha["num_certificado_padrao"],
                   data_ult_calibracao=linha["data_ult_calibracao"],
                   data_prox_calibracao=linha["data_prox_calibracao"],
                   id_equipamento=linha["id"])

    def __str__(self):
        return f"{self.denominacao} (código {self.codigo}, TAG {self.tag or '-'})"


# ---------------------------------------------------------------------
# Classe Medicao
# ---------------------------------------------------------------------

class Medicao:
    """Resultado de uma característica em uma execução da calibração.

    O erro e o status não são informados: são calculados a partir do valor
    nominal, das tolerâncias e do valor medido, e por isso não têm setter.
    """

    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"

    # Folga para a comparação entre números reais. Sem ela, um valor que
    # cai exatamente no limite pode ser reprovado por resíduo de ponto
    # flutuante (por exemplo, 45 + (-0.05) = 44.949999...).
    _FOLGA = 1e-9

    def __init__(self, equipamento_id, padrao_id, tecnico_id, data_execucao,
                 caracteristica, valor_nominal, tol_superior, tol_inferior,
                 valor_medido, sequencia_medicao=1, solicitante_id=None,
                 temperatura_c=None, num_certificado=None, id_medicao=None):
        self.id_medicao = id_medicao
        self.equipamento_id = equipamento_id
        self.padrao_id = padrao_id
        self.tecnico_id = tecnico_id
        self.solicitante_id = solicitante_id
        self.num_certificado = _texto_opcional(num_certificado)
        self.data_execucao = data_execucao
        self.temperatura_c = temperatura_c
        self.caracteristica = caracteristica
        self.sequencia_medicao = sequencia_medicao
        self.valor_nominal = valor_nominal
        self._definir_tolerancias(tol_superior, tol_inferior)
        self.valor_medido = valor_medido

    # --- atributos validados -----------------------------------------

    @property
    def data_execucao(self):
        return self._data_execucao

    @data_execucao.setter
    def data_execucao(self, valor):
        self._data_execucao = _data_iso(valor, "data_execucao")

    @property
    def temperatura_c(self):
        return self._temperatura_c

    @temperatura_c.setter
    def temperatura_c(self, valor):
        # A planilha guardava a temperatura como o texto 20,4° (A25).
        # Aqui ela é aceita nesse formato, mas vira número.
        if valor is None or str(valor).strip() == "":
            self._temperatura_c = None
            return
        texto = str(valor).replace("°", "").replace("C", "").replace(",", ".").strip()
        try:
            self._temperatura_c = float(texto)
        except ValueError:
            raise ErroValidacao(f"temperatura inválida: {valor}") from None

    @property
    def caracteristica(self):
        return self._caracteristica

    @caracteristica.setter
    def caracteristica(self, valor):
        valor = _texto_opcional(valor)
        if valor is None:
            raise ErroValidacao("característica é obrigatória")
        self._caracteristica = valor.upper()

    @property
    def sequencia_medicao(self):
        return self._sequencia_medicao

    @sequencia_medicao.setter
    def sequencia_medicao(self, valor):
        valor = int(valor)
        if valor < 1:
            raise ErroValidacao("sequência da medição começa em 1")
        self._sequencia_medicao = valor

    @property
    def valor_nominal(self):
        return self._valor_nominal

    @valor_nominal.setter
    def valor_nominal(self, valor):
        self._valor_nominal = float(valor)

    @property
    def valor_medido(self):
        return self._valor_medido

    @valor_medido.setter
    def valor_medido(self, valor):
        # Precisão plena; o arredondamento fica para o certificado.
        self._valor_medido = float(valor)

    @property
    def tol_superior(self):
        return self._tol_superior

    @property
    def tol_inferior(self):
        return self._tol_inferior

    def _definir_tolerancias(self, tol_superior, tol_inferior):
        superior, inferior = float(tol_superior), float(tol_inferior)
        if inferior > superior:
            raise ErroValidacao(
                f"tolerância inferior ({inferior}) maior que a superior ({superior})")
        self._tol_superior = superior
        self._tol_inferior = inferior

    # --- regras metrológicas -----------------------------------------

    @property
    def limite_inferior(self):
        # A tolerância inferior já vem com sinal. O limite é nominal + tol,
        # e não nominal - tol, que era a fórmula invertida da planilha.
        return self.valor_nominal + self.tol_inferior

    @property
    def limite_superior(self):
        return self.valor_nominal + self.tol_superior

    @property
    def erro(self):
        """Valor medido menos valor nominal."""
        return self.valor_medido - self.valor_nominal

    @property
    def status(self):
        """APROVADO se o valor medido estiver dentro dos limites."""
        dentro = (self.limite_inferior - self._FOLGA
                  <= self.valor_medido
                  <= self.limite_superior + self._FOLGA)
        return self.APROVADO if dentro else self.REPROVADO

    def verificar_padrao(self, padrao):
        """Bloqueia a medição se o padrão não servir para a data executada."""
        if padrao is None:
            raise ErroValidacao(f"padrão {self.padrao_id} não está cadastrado")
        if padrao.tipo != "padrao":
            raise ErroValidacao(f"{padrao.denominacao} não é um padrão de calibração")
        if not padrao.esta_vigente(self.data_execucao):
            raise ErroValidacao(
                f"padrão {padrao.codigo} vencido em {padrao.data_prox_calibracao}; "
                f"medição de {self.data_execucao[:10]} bloqueada")

    @classmethod
    def de_linha(cls, linha):
        return cls(equipamento_id=linha["equipamento_id"],
                   padrao_id=linha["padrao_id"],
                   tecnico_id=linha["tecnico_id"],
                   solicitante_id=linha["solicitante_id"],
                   num_certificado=linha["num_certificado"],
                   data_execucao=linha["data_execucao"],
                   temperatura_c=linha["temperatura_c"],
                   caracteristica=linha["caracteristica"],
                   sequencia_medicao=linha["sequencia_medicao"],
                   valor_nominal=linha["valor_nominal"],
                   tol_superior=linha["tol_superior"],
                   tol_inferior=linha["tol_inferior"],
                   valor_medido=linha["valor_medido"],
                   id_medicao=linha["id"])

    def __str__(self):
        return (f"{self.caracteristica} #{self.sequencia_medicao}: "
                f"{self.valor_medido:.4f} [{self.limite_inferior:.3f} a "
                f"{self.limite_superior:.3f}] {self.status}")


# ---------------------------------------------------------------------
# Classe de conexão e persistência
# ---------------------------------------------------------------------

class BancoDados:
    """Conexão com o SQLite e comandos SQL das três tabelas.

    Pode ser usada com 'with', que fecha a conexão ao final:
        with BancoDados("certificados.db") as banco:
            banco.inserir_tecnico(...)
    """

    SCRIPT_DDL = Path(__file__).with_name("03_banco.sql")

    def __init__(self, caminho_banco="certificados.db"):
        self.caminho_banco = caminho_banco
        self._conexao = None

    # --- conexão -----------------------------------------------------

    def conectar(self):
        try:
            self._conexao = sqlite3.connect(self.caminho_banco)
        except sqlite3.Error as erro:
            raise ErroBanco(f"não foi possível abrir {self.caminho_banco}: {erro}") from erro
        self._conexao.row_factory = sqlite3.Row
        # O SQLite não aplica chave estrangeira por padrão, e o comando
        # vale por conexão. Sem ele, as FKs do 03_banco.sql não funcionam.
        self._conexao.execute("PRAGMA foreign_keys = ON")
        return self

    def fechar(self):
        if self._conexao is not None:
            self._conexao.close()
            self._conexao = None

    def __enter__(self):
        return self.conectar()

    def __exit__(self, tipo, valor, rastro):
        self.fechar()
        return False

    @property
    def conexao(self):
        if self._conexao is None:
            raise ErroBanco("banco não conectado; chame conectar() antes")
        return self._conexao

    def criar_estrutura(self, caminho_script=None):
        """Executa o DDL da AV 02. Atenção: o script apaga as tabelas."""
        caminho = Path(caminho_script or self.SCRIPT_DDL)
        try:
            script = caminho.read_text(encoding="utf-8")
        except OSError as erro:
            raise ErroBanco(f"script {caminho} não encontrado") from erro
        try:
            self.conexao.executescript(script)
        except sqlite3.Error as erro:
            raise ErroBanco(f"falha ao executar {caminho.name}: {erro}") from erro
        self.conexao.execute("PRAGMA foreign_keys = ON")

    # --- execução e tratamento de erros ------------------------------

    @staticmethod
    def _traduzir(erro):
        """Transforma a mensagem do SQLite em uma explicação de negócio."""
        texto = str(erro)
        if "FOREIGN KEY" in texto:
            return "registro relacionado não existe no cadastro (chave estrangeira)"
        if "UNIQUE" in texto:
            campos = texto.split(":", 1)[-1].strip()
            return f"registro duplicado em {campos}"
        if "CHECK" in texto:
            return "valor fora do domínio permitido pela tabela"
        if "NOT NULL" in texto:
            campo = texto.split(":", 1)[-1].strip()
            return f"campo obrigatório sem valor: {campo}"
        return texto

    def _executar(self, sql, parametros=()):
        """Executa um comando de escrita dentro de uma transação.

        Se o comando falhar, a transação é desfeita (rollback) e o erro
        sobe como ErroBanco, com a mensagem traduzida.
        """
        try:
            with self.conexao:
                return self.conexao.execute(sql, parametros)
        except sqlite3.IntegrityError as erro:
            raise ErroBanco(self._traduzir(erro)) from erro
        except sqlite3.Error as erro:
            raise ErroBanco(f"erro de SQL: {erro}") from erro

    def _consultar(self, sql, parametros=()):
        try:
            return self.conexao.execute(sql, parametros).fetchall()
        except sqlite3.Error as erro:
            raise ErroBanco(f"erro de consulta: {erro}") from erro

    # --- INSERT ------------------------------------------------------

    def inserir_tecnico(self, tecnico):
        cursor = self._executar(
            """INSERT INTO tecnico (matricula, nome, setor, funcao, pode_assinar)
               VALUES (?, ?, ?, ?, ?)""",
            (tecnico.matricula, tecnico.nome, tecnico.setor,
             tecnico.funcao, int(tecnico.pode_assinar)))
        tecnico.id_tecnico = cursor.lastrowid
        return tecnico.id_tecnico

    def inserir_equipamento(self, equipamento):
        cursor = self._executar(
            """INSERT INTO equipamento (codigo, tag, denominacao, tipo, fabricante,
                   modelo, num_serie, resolucao_mm, num_certificado_padrao,
                   data_ult_calibracao, data_prox_calibracao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (equipamento.codigo, equipamento.tag, equipamento.denominacao,
             equipamento.tipo, equipamento.fabricante, equipamento.modelo,
             equipamento.num_serie, equipamento.resolucao_mm,
             equipamento.num_certificado_padrao,
             equipamento.data_ult_calibracao, equipamento.data_prox_calibracao))
        equipamento.id_equipamento = cursor.lastrowid
        return equipamento.id_equipamento

    def inserir_medicao(self, medicao):
        """Grava a medição depois de conferir a vigência do padrão.

        O erro e o status vão para o banco já calculados pela classe
        Medicao; não são digitados.
        """
        padrao = self.buscar_equipamento_por_id(medicao.padrao_id)
        medicao.verificar_padrao(padrao)
        cursor = self._executar(
            """INSERT INTO medicao (equipamento_id, padrao_id, tecnico_id,
                   solicitante_id, num_certificado, data_execucao, temperatura_c,
                   caracteristica, sequencia_medicao, valor_nominal,
                   tol_superior, tol_inferior, valor_medido, erro, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (medicao.equipamento_id, medicao.padrao_id, medicao.tecnico_id,
             medicao.solicitante_id, medicao.num_certificado,
             medicao.data_execucao, medicao.temperatura_c,
             medicao.caracteristica, medicao.sequencia_medicao,
             medicao.valor_nominal, medicao.tol_superior, medicao.tol_inferior,
             medicao.valor_medido, medicao.erro, medicao.status))
        medicao.id_medicao = cursor.lastrowid
        return medicao.id_medicao

    # --- SELECT ------------------------------------------------------

    def buscar_tecnico_por_matricula(self, matricula):
        linhas = self._consultar("SELECT * FROM tecnico WHERE matricula = ?",
                                 (str(matricula),))
        return Tecnico.de_linha(linhas[0]) if linhas else None

    def buscar_equipamento_por_id(self, id_equipamento):
        linhas = self._consultar("SELECT * FROM equipamento WHERE id = ?",
                                 (id_equipamento,))
        return Equipamento.de_linha(linhas[0]) if linhas else None

    def buscar_equipamento_por_tag(self, tag):
        linhas = self._consultar("SELECT * FROM equipamento WHERE tag = ?", (tag,))
        return Equipamento.de_linha(linhas[0]) if linhas else None

    def listar_medicoes(self, equipamento_id, data_execucao=None):
        sql = "SELECT * FROM medicao WHERE equipamento_id = ?"
        parametros = [equipamento_id]
        if data_execucao:
            sql += " AND data_execucao = ?"
            parametros.append(data_execucao)
        sql += " ORDER BY caracteristica, sequencia_medicao"
        return [Medicao.de_linha(l) for l in self._consultar(sql, parametros)]

    def relatorio_calibracao(self, tag, data_execucao=None):
        """Consulta com JOIN entre as três tabelas para montar o relatório.

        A tabela equipamento entra duas vezes (instrumento e padrão) e a
        tabela tecnico também (executante e solicitante).
        """
        sql = """
            SELECT inst.tag              AS tag,
                   inst.codigo           AS codigo_instrumento,
                   inst.denominacao      AS instrumento,
                   pad.codigo            AS codigo_padrao,
                   pad.denominacao       AS padrao,
                   pad.fabricante        AS fabricante_padrao,
                   pad.num_serie         AS serie_padrao,
                   pad.num_certificado_padrao AS certificado_padrao,
                   pad.data_prox_calibracao   AS validade_padrao,
                   exe.nome              AS executante,
                   exe.matricula         AS matricula_executante,
                   sol.nome              AS solicitante,
                   m.num_certificado, m.data_execucao, m.temperatura_c,
                   m.caracteristica, m.sequencia_medicao, m.valor_nominal,
                   m.tol_inferior, m.tol_superior, m.valor_medido,
                   m.erro, m.status
              FROM medicao m
              JOIN equipamento inst ON inst.id = m.equipamento_id
              JOIN equipamento pad  ON pad.id  = m.padrao_id
              JOIN tecnico exe      ON exe.id  = m.tecnico_id
         LEFT JOIN tecnico sol      ON sol.id  = m.solicitante_id
             WHERE inst.tag = ?"""
        parametros = [tag]
        if data_execucao:
            sql += " AND m.data_execucao = ?"
            parametros.append(data_execucao)
        sql += " ORDER BY m.caracteristica, m.sequencia_medicao"
        return self._consultar(sql, parametros)

    # --- UPDATE ------------------------------------------------------

    def atualizar_tecnico(self, tecnico):
        if tecnico.id_tecnico is None:
            raise ErroBanco("técnico sem id; grave-o antes de atualizar")
        cursor = self._executar(
            """UPDATE tecnico
                  SET matricula = ?, nome = ?, setor = ?, funcao = ?, pode_assinar = ?
                WHERE id = ?""",
            (tecnico.matricula, tecnico.nome, tecnico.setor, tecnico.funcao,
             int(tecnico.pode_assinar), tecnico.id_tecnico))
        return cursor.rowcount

    def atualizar_equipamento(self, equipamento):
        if equipamento.id_equipamento is None:
            raise ErroBanco("equipamento sem id; grave-o antes de atualizar")
        cursor = self._executar(
            """UPDATE equipamento
                  SET codigo = ?, tag = ?, denominacao = ?, tipo = ?, fabricante = ?,
                      modelo = ?, num_serie = ?, resolucao_mm = ?,
                      num_certificado_padrao = ?, data_ult_calibracao = ?,
                      data_prox_calibracao = ?
                WHERE id = ?""",
            (equipamento.codigo, equipamento.tag, equipamento.denominacao,
             equipamento.tipo, equipamento.fabricante, equipamento.modelo,
             equipamento.num_serie, equipamento.resolucao_mm,
             equipamento.num_certificado_padrao, equipamento.data_ult_calibracao,
             equipamento.data_prox_calibracao, equipamento.id_equipamento))
        return cursor.rowcount

    def registrar_certificado(self, equipamento_id, data_execucao, num_certificado):
        """Grava o número do certificado em todas as linhas da calibração."""
        num_certificado = _texto_opcional(num_certificado)
        if num_certificado is None:
            raise ErroValidacao("número do certificado é obrigatório")
        cursor = self._executar(
            """UPDATE medicao SET num_certificado = ?
                WHERE equipamento_id = ? AND data_execucao = ?""",
            (num_certificado, equipamento_id, data_execucao))
        if cursor.rowcount == 0:
            raise ErroBanco("nenhuma medição encontrada para essa calibração")
        return cursor.rowcount
