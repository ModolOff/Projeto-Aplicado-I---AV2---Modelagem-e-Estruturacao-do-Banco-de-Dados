# Projeto Aplicado I — AV2: Modelagem e Estruturação do Banco de Dados

Banco de dados relacional em SQLite para a automação da emissão de certificados de calibração do laboratório de metrologia da **Schulz S.A.**, desenvolvido na unidade curricular Projeto Aplicado I do Centro Universitário UniSENAI Santa Catarina.

**Grupo:** Otávio Modolon Neto, Thiago Neves Gomes, Lucas Antunes Severino
**Professor:** MSc. Hugo Menezes Barra

## O problema

O laboratório executa entre 600 e 700 calibrações por mês. A máquina de medição grava o resultado em TXT, o cadastro do instrumento fica no software de gestão, e a ponte entre as duas fontes é uma planilha de onze abas preenchida à mão por um segundo metrologista.

O levantamento da Entrega 01 catalogou 34 anomalias nesse processo, 18 delas de severidade alta, concentradas em três frentes: a forma de representar dado ausente, a divergência de identificadores entre as fontes e as fórmulas incorretas dentro da planilha. Este banco substitui a planilha como lugar de guardar o dado.

## Estrutura do banco

Três tabelas, conforme o roteiro da entrega:

| Tabela | O que guarda |
|---|---|
| `tecnico` | Pessoas e setores que participam da calibração — executante, solicitante e signatário, distinguidos pela coluna `funcao`. Identificação pela matrícula, não pelo nome. |
| `equipamento` | Instrumento calibrado e padrão de calibração, separados pela coluna `tipo`. O padrão guarda as próprias datas de calibração, o que permite verificar a vigência por consulta. |
| `medicao` | Uma linha por característica e por execução, com valor nominal, tolerâncias, valor medido, erro e status. Quatro chaves estrangeiras ligam a medição ao instrumento, ao padrão, ao executante e ao solicitante. |

Gravar o resultado como linha, e não como coluna, remove dois limites da planilha atual: o de 35 características por calibração e o de duas execuções por característica.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `01_estrutura.md` | Organização dos dados e justificativa da não duplicação |
| `02_dicionario.md` | Dicionário de dados com 34 campos nas três tabelas |
| `03_banco.sql` | Script DDL executável em SQLite |
| `Entrega_02_PA_I.pdf` | Documento explicativo do projeto |

## Como executar

Com o SQLite instalado, na pasta do repositório:

```bash
sqlite3 certificados.db < 03_banco.sql
```

Para conferir as tabelas criadas:

```bash
sqlite3 certificados.db ".tables"
```

O script começa com `PRAGMA foreign_keys = ON`, necessário porque o SQLite não aplica chave estrangeira por padrão. Esse comando vale por conexão, então a aplicação que for usar o banco precisa executá-lo também.

Os comandos `DROP TABLE IF EXISTS` no início permitem reexecutar o script sobre um banco já criado. **Isso apaga os dados existentes.**

## Verificação

O script foi executado e o banco submetido a seis testes:

| Nº | Teste | Resultado |
|---|---|---|
| T01 | Executar o script em banco vazio | Três tabelas criadas |
| T02 | Medição apontando para equipamento e técnico inexistentes | Recusada |
| T03 | Mesma característica duas vezes na mesma execução | Recusada |
| T04 | Status fora da lista prevista | Recusado |
| T05 | Equipamento com código já existente | Recusado |
| T06 | Terceira execução da mesma característica | Aceita |

## Limitações

Com três tabelas, o número do certificado, a data de execução e a temperatura são dados do evento da calibração, mas ficam repetidos em todas as linhas da mesma calibração. No modelo relacional completo esses campos pertencem a uma entidade `CALIBRACAO` própria, e a separação está prevista para a implementação final do sistema.

O dicionário foi levantado a partir das evidências da Entrega 01. Quando a rotina de carga em Python estiver escrita, os nomes dos campos devem ser conferidos contra ela.
