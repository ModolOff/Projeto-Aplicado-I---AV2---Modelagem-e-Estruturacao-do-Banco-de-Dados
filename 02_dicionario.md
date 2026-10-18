# Dicionário de Dados do Sistema

**Unidade curricular:** Projeto Aplicado I — Centro Universitário UniSENAI Santa Catarina
**Tema 02:** Modelagem e Implementação de Banco de Dados
**Empresa parceira:** Schulz S.A.
**Grupo:** Otávio Modolon Neto, Thiago Neves Gomes, Lucas Antonio Severino

Os campos abaixo são os que o script Python extrai do relatório da máquina de medição e das planilhas do laboratório, já convertidos para os tipos do SQLite. A coluna Tipo traz a classificação pedida no roteiro (Texto, Real ou Inteiro) e a coluna Tipo SQLite, a declaração usada no script `03_banco.sql`. A origem indica de onde o dado vem no processo atual.

## Tabela `tecnico` — Técnico/Solicitante

| Campo | Tipo | Tipo SQLite | Obrigatório | Origem | Descrição |
|---|---|---|---|---|---|
| id | Inteiro | INTEGER | Sim (PK) | Gerado pelo banco | Chave primária do registro |
| matricula | Texto | TEXT | Não | Aba Complemento, campo matrícula | Matrícula da Schulz, única; é a chave de identificação da pessoa, não o nome |
| nome | Texto | TEXT | Sim | Relatório da MMC e aba Registro | Nome da pessoa ou denominação do setor solicitante |
| setor | Texto | TEXT | Não | Aba BANCO DE DADOS, lista de 31 setores | Setor ao qual a pessoa pertence |
| funcao | Texto | TEXT | Sim | Definido no cadastro | Papel exercido: executante, solicitante ou signatario |
| pode_assinar | Inteiro | INTEGER | Sim | Aba Protocolo, lista de signatários | Indica se o registro pode aprovar certificado: 0 para não, 1 para sim |

## Tabela `equipamento` — Instrumento calibrado e padrão

| Campo | Tipo | Tipo SQLite | Obrigatório | Origem | Descrição |
|---|---|---|---|---|---|
| id | Inteiro | INTEGER | Sim (PK) | Gerado pelo banco | Chave primária do registro |
| codigo | Texto | TEXT | Sim | Relatório da MMC e aba Padrões | Código do equipamento, único, gravado só com dígitos |
| tag | Texto | TEXT | Não | Aba Complemento, campo TAG | TAG do instrumento calibrado, como 703.1208; é a chave de busca do usuário |
| denominacao | Texto | TEXT | Sim | Aba Registro, denominação | Nome do equipamento, como Dispositivo de controle |
| tipo | Texto | TEXT | Sim | Definido no cadastro | Separa instrumento calibrado de padrão de calibração |
| fabricante | Texto | TEXT | Não | Aba Complemento e aba Padrões | Fabricante, como Carl Zeiss |
| modelo | Texto | TEXT | Não | Aba Complemento e aba Padrões | Modelo, como Contura G2 |
| num_serie | Texto | TEXT | Não | Aba Complemento e aba Padrões | Número de série, como 502390 |
| resolucao_mm | Real | REAL | Não | Aba Complemento, resolução | Resolução em milímetro, como 0,001 |
| num_certificado_padrao | Texto | TEXT | Não | Aba Padrões | Certificado de calibração do padrão, como 241120502390 |
| data_ult_calibracao | Texto | TEXT | Não | Aba Padrões | Data da última calibração do padrão, no formato AAAA-MM-DD |
| data_prox_calibracao | Texto | TEXT | Não | Aba Padrões | Validade do padrão; usada para bloquear emissão com padrão vencido |

## Tabela `medicao` — Resultado por característica

| Campo | Tipo | Tipo SQLite | Obrigatório | Origem | Descrição |
|---|---|---|---|---|---|
| id | Inteiro | INTEGER | Sim (PK) | Gerado pelo banco | Chave primária do registro |
| equipamento_id | Inteiro | INTEGER | Sim (FK) | Vínculo pela TAG | Instrumento que foi calibrado |
| padrao_id | Inteiro | INTEGER | Sim (FK) | Aba Registro, padrão utilizado | Padrão usado na medição |
| tecnico_id | Inteiro | INTEGER | Sim (FK) | Relatório da MMC, metrologista | Técnico que executou a calibração |
| solicitante_id | Inteiro | INTEGER | Não (FK) | Aba Registro, solicitante | Setor que pediu a calibração, como Usinagem I |
| num_certificado | Texto | TEXT | Não | Aba Complemento, certificado | Número do certificado no formato 00091/2026; fica vazio até a emissão |
| data_execucao | Texto | TEXT | Sim | Cabeçalho do relatório, Date e Time | Data e hora da medição na máquina, no formato AAAA-MM-DD HH:MM:SS |
| temperatura_c | Real | REAL | Não | Aba Registro, temperatura | Temperatura ambiente em grau Celsius, gravada como número |
| caracteristica | Texto | TEXT | Sim | Relatório da MMC, Characteristic | Nome da característica medida, como PLANICIDADE_REF |
| sequencia_medicao | Inteiro | INTEGER | Sim | Ordem do bloco no relatório | Número da execução da medição: 1 para a primeira, 2 para a segunda |
| valor_nominal | Real | REAL | Sim | Relatório da MMC, Nominal | Valor de projeto da característica |
| tol_superior | Real | REAL | Sim | Relatório da MMC, Upper Tol | Tolerância superior, gravada com sinal |
| tol_inferior | Real | REAL | Sim | Relatório da MMC, Lower Tol | Tolerância inferior, gravada com sinal, negativa quando for o caso |
| valor_medido | Real | REAL | Sim | Relatório da MMC, Actual | Valor medido pela máquina, em precisão plena |
| erro | Real | REAL | Não | Calculado pelo sistema | Valor obtido menos valor nominal; não é importado do relatório |
| status | Texto | TEXT | Não | Calculado pelo sistema | Conformidade da característica: conforme ou nao conforme |

São 34 campos mapeados, acima do mínimo de 12 pedido no roteiro. Três observações sobre os tipos escolhidos:

1. As datas são gravadas como Texto no padrão AAAA-MM-DD, porque o SQLite não tem tipo próprio de data e esse formato permite ordenar e comparar como texto.
2. Os valores dimensionais são Real em milímetro e em precisão plena. O arredondamento para três casas continua existindo, mas só na hora de gerar o certificado.
3. O campo `pode_assinar` é Inteiro porque o SQLite não tem tipo booleano: o valor 0 significa não e o valor 1 significa sim.
