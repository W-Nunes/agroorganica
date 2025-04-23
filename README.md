# Agrorgânica Soluções Sustentáveis

## 1. A Nossa Missão

O agronegócio brasileiro é vasto e diversificado, mas os **pequenos produtores**, especialmente aqueles focados em **práticas orgânicas e sustentáveis**, muitas vezes enfrentam desafios significativos para ganhar visibilidade e acessar mercados. A falta de conexão direta com compradores e a dificuldade em planejar a produção com base na demanda real podem limitar o potencial de crescimento e a rentabilidade desses agricultores.

A **Agrorgânica Soluções Sustentáveis** nasce com a missão de ser uma ponte pioneira, conectando diretamente o pequeno produtor rural focado em sustentabilidade ao comerciante ou consumidor final. Acreditamos que, ao dar **visibilidade** à produção orgânica e facilitar o **acesso** a quem busca esses produtos, podemos fortalecer a agricultura familiar e promover um sistema alimentar mais saudável e justo.

Entendemos que, com menos terra, o diferencial do pequeno produtor está na **qualidade** e na **sustentabilidade**. Por isso, nossa ferramenta não só ajuda na gestão da produção, mas também permite que o produtor conheça a **demanda** antes mesmo de plantar, otimizando seus recursos e aumentando suas chances de sucesso e lucro. Queremos valorizar quem produz com respeito ao meio ambiente e à saúde, evitando os malefícios dos fertilizantes sintéticos e agrotóxicos.

## 2. Como a Agrorgânica Funciona?

A Agrorgânica Soluções Sustentáveis é uma aplicação de linha de comando (CLI) desenvolvida em Python, utilizando um banco de dados. Ela oferece um conjunto de ferramentas para:

* **Gestão Simplificada para o Produtor:**
    * Cadastro de produtores e suas áreas de cultivo (talhões).
    * Registro detalhado dos plantios, incluindo cultura, datas (com validação para plantio recente), previsão de colheita e **histórico da cultura anterior** para auxiliar na rotação de culturas, o que ajuda na qualidade do solo e afasta pragas.
    * Acompanhamento da colheita, atualizando o status do produto para "Disponível".
    * Registro de práticas sustentáveis, como aplicação de insumos orgânicos.
    * Gerenciamento simplificado do status da certificação orgânica.
    * Edição e exclusão de registros para manter os dados atualizados.

* **Conexão com o Mercado:**
    * **Registro de Demandas:** Comerciantes ou consumidores podem registrar suas necessidades futuras de produtos orgânicos (cultura, quantidade, data), permitindo que os produtores visualizem o que o mercado procura.
    * **Vitrine de Ofertas ("Mercado"):** Uma consulta que mostra aos interessados quais produtos estão disponíveis para compra imediata e quais estão planejados para colheita futura, incluindo detalhes sobre o produtor e sua certificação.
    * **Rastreabilidade:** Geração de um relatório simples que traça a origem de um lote específico, desde o produtor e talhão até as práticas recentes, agregando valor e confiança.

## 3. Principais Funcionalidades (Menus)

* **Gestão de Produtores:** Cadastrar, listar, editar e excluir produtores.
* **Gestão de Talhões:** Cadastrar, listar, editar, excluir talhões e visualizar histórico de rotação por talhão.
* **Gestão de Plantios e Colheitas:** Registrar plantios, confirmar colheitas, editar e excluir registros.
* **Gestão de Práticas Sustentáveis:** Registrar e excluir aplicações de insumos, gerenciar status de certificação.
* **Gestão de Demandas:** Registrar, listar e excluir demandas de mercado.
* **Mercado (Visão Comprador):** Visualizar a oferta atual e futura dos produtores cadastrados.
* **Outras Consultas e Relatórios:** Gerar relatório de rastreabilidade e visualizar calendário de colheitas.

## 4. Tecnologia Utilizada

* **Linguagem:** Python 3
* **Banco de Dados:** Oracle (requer `cx_Oracle` e Oracle Client configurados)
* **Interface:** Linha de Comando (CLI)

## 5. Como Executar

1.  **Pré-requisitos:** Python 3, `cx_Oracle` instalado (`pip install cx_Oracle`), Oracle Client configurado e acesso a um banco Oracle.
2.  **Configurar Credenciais:** Edite o arquivo `config.py` com seu usuário, senha e DSN do Oracle, ou (recomendado) configure as variáveis de ambiente `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`.
3.  **Executar:** No terminal, na pasta do projeto, rode `python main.py`.
4.  **Interagir:** Siga as opções do menu.

## 6. Nosso Objetivo

A Agrorgânica Soluções Sustentáveis é mais que um software; é uma iniciativa para fortalecer a agricultura familiar sustentável, promover a alimentação saudável e criar um mercado mais transparente e conectado.
Let's Rock

