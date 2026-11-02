"""
Projeto Aplicado I - UniSENAI Santa Catarina
AV 03: Construção do MVP (Parte 1)
Empresa parceira: Schulz S.A.
Grupo: Otávio Modolon Neto, Thiago Neves Gomes, Lucas Antunes Severino

Script de demonstração do MVP. Cria o banco certificados.db a partir do
03_banco.sql, cadastra técnicos e equipamentos, grava as medições de uma
calibração de teste, consulta com JOIN e exibe o relatório no terminal.

Os dados de teste seguem o caso do certificado nº 00091/2026 levantado na
Entrega 01. Matrículas, código do instrumento e valores medidos são
fictícios.

Execução, na pasta do repositório:
    python 05_main.py
"""

import importlib
import sys

# O nome do arquivo começa com número (04_classes.py), o que impede
# "import 04_classes". O importlib carrega o módulo pelo nome em texto.
classes = importlib.import_module("04_classes")

Tecnico = classes.Tecnico
Equipamento = classes.Equipamento
Medicao = classes.Medicao
BancoDados = classes.BancoDados
ErroValidacao = classes.ErroValidacao
ErroBanco = classes.ErroBanco

ARQUIVO_BANCO = "certificados.db"
DATA_EXECUCAO = "2026-08-13 10:15:00"

# (característica, nominal, tol. superior, tol. inferior, 1ª execução, 2ª execução)
RESULTADOS_TESTE = [
    ("PLANICIDADE_REF",  0.000, 0.020,  0.000,  0.01240,  0.01310),
    ("POSICAO_FURO_1",   0.000, 0.100,  0.000,  0.08730,  0.08910),
    ("POSICAO_FURO_2",   0.000, 0.100,  0.000,  0.11460,  0.11390),
    ("DIAMETRO_FURO_1", 12.000, 0.018,  0.000, 12.00920, 12.00880),
    ("DISTANCIA_A_B",   45.000, 0.050, -0.050, 44.96120, 44.96050),
]


def titulo(texto):
    print()
    print("=" * 78)
    print(texto)
    print("=" * 78)


def cadastrar(banco):
    titulo("1. CADASTRO DE TÉCNICOS E EQUIPAMENTOS (INSERT)")

    executante = Tecnico(nome="José Alcides Rosa Junior", funcao="executante",
                         matricula="10234", setor="Metrologia")
    solicitante = Tecnico(nome="Usinagem I", funcao="solicitante",
                          setor="Usinagem I")
    for tecnico in (executante, solicitante):
        banco.inserir_tecnico(tecnico)
        print(f"  Técnico gravado, id {tecnico.id_tecnico}: {tecnico}")

    instrumento = Equipamento(codigo="7031208", tag="703.1208",
                              denominacao="Dispositivo de controle",
                              tipo="instrumento", resolucao_mm=0.001)
    # Código informado com ponto, como no certificado; a classe grava 500011.
    padrao = Equipamento(codigo="500.011", denominacao="Máquina de medição por coordenadas",
                         tipo="padrao", fabricante="Carl Zeiss", modelo="Contura G2",
                         num_serie="502390", num_certificado_padrao="241120502390",
                         data_ult_calibracao="2025-08-31",
                         data_prox_calibracao="2026-08-31")
    padrao_vencido = Equipamento(codigo="500.020", denominacao="Bloco padrão de teste",
                                 tipo="padrao", data_ult_calibracao="2025-06-30",
                                 data_prox_calibracao="2026-06-30")
    for equipamento in (instrumento, padrao, padrao_vencido):
        banco.inserir_equipamento(equipamento)
        print(f"  Equipamento gravado, id {equipamento.id_equipamento}: {equipamento}")

    return executante, solicitante, instrumento, padrao, padrao_vencido


def gravar_medicoes(banco, executante, solicitante, instrumento, padrao):
    titulo("2. GRAVAÇÃO DAS MEDIÇÕES COM VALIDAÇÃO DE TOLERÂNCIA (INSERT)")
    print(f"  Instrumento {instrumento.tag}, executado em {DATA_EXECUCAO}")
    print(f"  Padrão {padrao.codigo}, válido até {padrao.data_prox_calibracao}: "
          f"{'vigente' if padrao.esta_vigente(DATA_EXECUCAO) else 'VENCIDO'}")
    print()

    total = 0
    for caracteristica, nominal, tol_sup, tol_inf, *execucoes in RESULTADOS_TESTE:
        for sequencia, valor in enumerate(execucoes, start=1):
            medicao = Medicao(equipamento_id=instrumento.id_equipamento,
                              padrao_id=padrao.id_equipamento,
                              tecnico_id=executante.id_tecnico,
                              solicitante_id=solicitante.id_tecnico,
                              data_execucao=DATA_EXECUCAO,
                              temperatura_c="20,4°",  # texto da planilha (A25)
                              caracteristica=caracteristica,
                              sequencia_medicao=sequencia,
                              valor_nominal=nominal, tol_superior=tol_sup,
                              tol_inferior=tol_inf, valor_medido=valor)
            banco.inserir_medicao(medicao)
            total += 1
            print(f"  {medicao}")
    print(f"\n  {total} medições gravadas.")


def exibir_relatorio(banco, tag):
    titulo("3. RELATÓRIO DE CALIBRAÇÃO (SELECT COM JOIN)")
    linhas = banco.relatorio_calibracao(tag, DATA_EXECUCAO)
    if not linhas:
        print("  Nenhuma medição encontrada.")
        return

    cab = linhas[0]
    print(f"  Certificado nº ...: {cab['num_certificado'] or '(não emitido)'}")
    print(f"  Instrumento ......: {cab['instrumento']}, TAG {cab['tag']}, "
          f"código {cab['codigo_instrumento']}")
    print(f"  Padrão ...........: {cab['padrao']} {cab['fabricante_padrao']}, "
          f"código {cab['codigo_padrao']}, série {cab['serie_padrao']}")
    print(f"  Certificado padrão: {cab['certificado_padrao']}, "
          f"válido até {cab['validade_padrao']}")
    print(f"  Executante .......: {cab['executante']} "
          f"(matrícula {cab['matricula_executante']})")
    print(f"  Solicitante ......: {cab['solicitante']}")
    print(f"  Data de execução .: {cab['data_execucao']}")
    print(f"  Temperatura ......: {cab['temperatura_c']:.1f} °C")
    print()

    # Os valores ficam em precisão plena no banco; o arredondamento para
    # três casas acontece só aqui, na exibição (RH20).
    print(f"  {'Característica':<16} {'Seq':>3} {'Nominal':>9} {'Lim. inf.':>9} "
          f"{'Lim. sup.':>9} {'Medido':>9} {'Erro':>8}  Status")
    print("  " + "-" * 76)
    reprovadas = 0
    for l in linhas:
        lim_inf = l["valor_nominal"] + l["tol_inferior"]
        lim_sup = l["valor_nominal"] + l["tol_superior"]
        print(f"  {l['caracteristica']:<16} {l['sequencia_medicao']:>3} "
              f"{l['valor_nominal']:>9.3f} {lim_inf:>9.3f} {lim_sup:>9.3f} "
              f"{l['valor_medido']:>9.3f} {l['erro']:>8.3f}  {l['status']}")
        if l["status"] == Medicao.REPROVADO:
            reprovadas += 1
    print("  " + "-" * 76)
    resultado = Medicao.REPROVADO if reprovadas else Medicao.APROVADO
    print(f"  Medições: {len(linhas)} | aprovadas: {len(linhas) - reprovadas} | "
          f"reprovadas: {reprovadas} | resultado da calibração: {resultado}")


def emitir_certificado(banco, instrumento):
    titulo("4. REGISTRO DO NÚMERO DO CERTIFICADO (UPDATE)")
    alteradas = banco.registrar_certificado(instrumento.id_equipamento,
                                            DATA_EXECUCAO, "00091/2026")
    print(f"  Certificado 00091/2026 gravado em {alteradas} linhas da calibração.")
    gravadas = banco.listar_medicoes(instrumento.id_equipamento, DATA_EXECUCAO)
    numeros = {m.num_certificado for m in gravadas}
    print(f"  Conferência pelo SELECT: {len(gravadas)} linhas, certificado(s) {sorted(numeros)}")


def demonstrar_erros(banco, executante, instrumento, padrao_vencido, padrao):
    titulo("5. TRATAMENTO DE ERROS (REGISTROS QUE DEVEM SER RECUSADOS)")

    def tentar(descricao, acao):
        try:
            acao()
            print(f"  [FALHOU] {descricao}: o registro foi aceito")
        except (ErroValidacao, ErroBanco) as erro:
            print(f"  [OK] {descricao}")
            print(f"       {type(erro).__name__}: {erro}")

    base = dict(equipamento_id=instrumento.id_equipamento,
                padrao_id=padrao.id_equipamento,
                tecnico_id=executante.id_tecnico,
                data_execucao=DATA_EXECUCAO, caracteristica="PLANICIDADE_REF",
                sequencia_medicao=3, valor_nominal=0, tol_superior=0.02,
                tol_inferior=0, valor_medido=0.0128)

    tentar("Medição com padrão vencido",
           lambda: banco.inserir_medicao(Medicao(**{**base, "padrao_id":
                                                    padrao_vencido.id_equipamento})))
    tentar("Mesma característica gravada duas vezes na mesma execução",
           lambda: banco.inserir_medicao(Medicao(**{**base, "sequencia_medicao": 1})))
    tentar("Medição apontando para técnico inexistente",
           lambda: banco.inserir_medicao(Medicao(**{**base, "tecnico_id": 999})))
    tentar("Equipamento com código já cadastrado",
           lambda: banco.inserir_equipamento(
               Equipamento(codigo="500011", denominacao="Duplicado", tipo="padrao")))
    tentar("Técnico com função fora da lista",
           lambda: Tecnico(nome="Teste", funcao="estagiario"))
    tentar("Tolerância inferior maior que a superior",
           lambda: Medicao(**{**base, "tol_superior": -0.01, "tol_inferior": 0.01}))
    tentar("Data fora do formato AAAA-MM-DD",
           lambda: Medicao(**{**base, "data_execucao": "13/08/2026"}))


def conferir_totais(banco):
    titulo("6. CONFERÊNCIA FINAL")
    for tabela in ("tecnico", "equipamento", "medicao"):
        total = banco.conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        print(f"  {tabela:<12} {total:>3} registros")
    print(f"\n  Banco gravado em {ARQUIVO_BANCO}.")


def main():
    print("MVP - Emissão de certificados de calibração | Schulz S.A.")
    try:
        with BancoDados(ARQUIVO_BANCO) as banco:
            banco.criar_estrutura()
            executante, solicitante, instrumento, padrao, padrao_vencido = cadastrar(banco)
            gravar_medicoes(banco, executante, solicitante, instrumento, padrao)
            exibir_relatorio(banco, instrumento.tag)
            emitir_certificado(banco, instrumento)
            demonstrar_erros(banco, executante, instrumento, padrao_vencido, padrao)
            conferir_totais(banco)
    except (ErroBanco, ErroValidacao) as erro:
        print(f"\nExecução interrompida: {erro}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
