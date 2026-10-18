# Organização dos Dados

**Unidade curricular:** Projeto Aplicado I — Centro Universitário UniSENAI Santa Catarina
**Tema 02:** Modelagem e Implementação de Banco de Dados
**Empresa parceira:** Schulz S.A.
**Grupo:** Otávio Modolon Neto, Thiago Neves Gomes, Lucas Antonio Severino

## 1. O que o banco resolve

Na Entrega 01 mapeamos o caminho que um certificado percorre hoje. A máquina de medição grava o resultado em TXT, o cadastro do instrumento fica no software de gestão e a ponte entre as duas fontes é uma planilha de onze abas, preenchida à mão por um segundo metrologista. O banco desta entrega substitui essa planilha como lugar de guardar o dado: o script Python lê o relatório da máquina e, em vez de colar o bloco de resultados em uma aba, grava cada valor em uma tabela, com chave própria, tipo definido e histórico.

A estrutura foi dividida em três entidades principais, conforme o roteiro: Técnico/Solicitante, Equipamento e Medição. As duas primeiras guardam cadastro, que muda pouco e se repete em muitos certificados. A terceira guarda o evento, que nasce a cada calibração.

## 2. Técnico/Solicitante

Reúne as pessoas e os setores que participam da calibração: o metrologista que executa a medição na máquina, o setor que pediu o serviço e o signatário que aprova o certificado. Cada um é cadastrado uma vez só, identificado pela matrícula quando é pessoa da Schulz, e recebe uma função que indica o papel exercido.

A matrícula é a chave de identificação, e não o nome. A Entrega 01 mostrou o mesmo metrologista registrado como José A. Rosa Jr em uma planilha e como Jose Alcides Rosa Junior em outra (anomalia A15). Com o cadastro único, a grafia do nome deixa de ser o que liga o dado à pessoa.

## 3. Equipamento

Guarda tanto o instrumento que foi calibrado quanto o padrão usado na calibração, separados por uma coluna de tipo. Os dois têm os mesmos atributos — código, denominação, fabricante, modelo, número de série e resolução — e o padrão usa também as datas da própria calibração, que o sistema precisa consultar para saber se ele estava vigente no dia da medição.

O certificado nº 00091/2026 mostra por que esse cadastro precisa existir fora da planilha. O padrão Contura G2 da Carl Zeiss, série 502390, tem validade até 31/08/2026 e foi usado em uma calibração de 26/08/2026, com cinco dias de margem. Guardada a data de validade na tabela, essa verificação passa a ser consulta ao banco, e não conferência visual.

## 4. Medição

Grava uma linha por característica e por execução da medição. O relatório do Calypso traz cada característica duas vezes, uma por execução, e a planilha atual resolvia isso com duas colunas lado a lado, o que limitava o registro a duas repetições e a 35 características por certificado (anomalias A06 e A32). Como linha, não há limite: uma calibração com cinquenta características gera cinquenta linhas, e uma terceira execução gera uma linha a mais.

Cada linha carrega o valor nominal, as duas tolerâncias com sinal, o valor medido, o erro calculado e o status de conformidade, além das chaves que apontam para o instrumento, o padrão, o executante e o solicitante.

## 5. Por que evitar dados duplicados

Os problemas que a Entrega 01 catalogou nas planilhas vêm, na maioria, de dado repetido em lugares diferentes sem nada que o mantenha igual.

O nome do metrologista era digitado em cada planilha e apareceu com duas grafias. O código do mesmo equipamento aparecia como 500008 em uma fonte e 500.011 em outra (A13). A aba BANCO DE DADOS mantinha quatro listas de tamanhos diferentes lado a lado, sem chave que as ligasse (A29). A ausência de dado era escrita de seis maneiras: `---`, `------`, `00/00/0000`, Não consta, Não informado e Não se aplica (A01). E o mesmo evento tinha três datas distintas em três arquivos (A12).

Guardando cada informação em um lugar só e referenciando-a por chave estrangeira, essas divergências deixam de ser possíveis. O setor Usinagem I existe como um registro; se o nome dele mudar, muda em um lugar e todos os certificados passam a exibir o nome novo. O padrão 500.011 tem uma data de validade, e não uma por planilha. O banco também passa a recusar o que a planilha aceitava: uma medição sem instrumento, um técnico que não existe no cadastro ou um status fora da lista de valores previstos.

Há ganho de espaço, mas não é o principal. O que importa é a integridade: um dado que existe uma vez não entra em contradição consigo mesmo, e é isso que uma auditoria verifica no registro da qualidade.

## 6. Limitação registrada

O modelo completo da Entrega 01 separava o evento da calibração das características medidas, em tabelas distintas. Como esta entrega pede três tabelas, o número do certificado, a data de execução e a temperatura ficam repetidos em todas as linhas da mesma calibração. A separação da entidade Calibração fica prevista para a implementação final do sistema.
