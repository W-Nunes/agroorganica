# Importa as funções de operações e relatórios
import crud_operations as crud
import reports
from utils import registrar_erro 
def menu_principal():
    """Exibe o menu principal e retorna a escolha do usuário."""
    print("\n--- Agrorgânica Soluções Sustentáveis ---") 
    print("1. Gestão de Produtores")
    print("2. Gestão de Talhões")
    print("3. Gestão de Plantios e Colheitas")
    print("4. Gestão de Práticas Sustentáveis")
    print("5. Gestão de Demandas")
    print("6. Mercado") 
    print("7. Outras Consultas e Relatórios") 
    print("0. Sair")
    print("-" * 40) 
    return input("Escolha uma opção: ").strip()

def menu_gestao_produtores(conexao):
    """Menu para gerenciar produtores."""
    while True:
        print("\n--- Gestão de Produtores ---")
        print("1. Cadastrar Novo Produtor"); print("2. Listar Produtores")
        print("3. Editar Produtor"); print("4. Excluir Produtor")
        print("0. Voltar ao Menu Principal"); print("-" * 28)
        opcao = input("Escolha: ").strip()
        try:
            if opcao == '1': crud.cadastrar_produtor(conexao)
            elif opcao == '2': crud.selecionar_produtor(conexao); input("Pressione Enter para continuar...")
            elif opcao == '3': crud.editar_produtor(conexao)
            elif opcao == '4': crud.excluir_produtor(conexao)
            elif opcao == '0': break
            else: print("Opção inválida.")
            if opcao != '0': input("\nPressione Enter para continuar...")
        except Exception as e:
            registrar_erro(f"Erro inesperado no menu de produtores (opção {opcao}): {e}")
            input("Ocorreu um erro inesperado. Pressione Enter para continuar...")


def menu_gestao_talhoes(conexao):
    """Menu para gerenciar talhões."""
    id_produtor = crud.selecionar_produtor(conexao)
    if not id_produtor: print("Nenhum produtor selecionado."); return
    while True:
        print(f"\n--- Gestão de Talhões (Produtor: {id_produtor}) ---")
        print("1. Cadastrar Novo Talhão"); print("2. Listar Talhões")
        print("3. Editar Talhão"); print("4. Excluir Talhão")
        print("5. Histórico de Rotação"); print("0. Voltar"); print("-" * 45)
        opcao = input("Escolha: ").strip()
        try:
            if opcao == '1': crud.cadastrar_talhao(conexao, id_produtor)
            elif opcao == '2': crud.selecionar_talhao(conexao, id_produtor); input("Pressione Enter para continuar...")
            elif opcao == '3': crud.editar_talhao(conexao, id_produtor)
            elif opcao == '4': crud.excluir_talhao(conexao, id_produtor)
            elif opcao == '5': reports.visualizar_historico_rotacao(conexao, id_produtor)
            elif opcao == '0': break
            else: print("Opção inválida.")
            if opcao != '0': input("\nPressione Enter para continuar...")
        except Exception as e:
            registrar_erro(f"Erro inesperado no menu de talhões (opção {opcao}): {e}")
            input("Ocorreu um erro inesperado. Pressione Enter para continuar...")

def menu_gestao_plantios(conexao):
    """Menu para gerenciar plantios e colheitas."""
    id_produtor = crud.selecionar_produtor(conexao)
    if not id_produtor: print("Nenhum produtor selecionado."); return
    while True:
        print(f"\n--- Gestão de Plantios/Colheitas (Produtor: {id_produtor}) ---")
        print("1. Registrar Novo Plantio"); print("2. Confirmar Colheita")
        print("3. Editar Plantio/Produto"); print("4. Excluir Plantio/Produto")
        print("0. Voltar"); print("-" * 50)
        opcao = input("Escolha: ").strip()
        try:
            if opcao == '1':
                id_talhao_produtor, id_talhao_unico = crud.selecionar_talhao(conexao, id_produtor)
                if id_talhao_unico: crud.registrar_plantio(conexao, id_produtor, id_talhao_produtor, id_talhao_unico)
            elif opcao == '2': crud.confirmar_colheita(conexao, id_produtor)
            elif opcao == '3': crud.editar_plantio(conexao, id_produtor)
            elif opcao == '4': crud.excluir_plantio(conexao, id_produtor)
            elif opcao == '0': break
            else: print("Opção inválida.")
            if opcao != '0': input("\nPressione Enter para continuar...")
        except Exception as e:
            registrar_erro(f"Erro inesperado no menu de plantios (opção {opcao}): {e}")
            input("Ocorreu um erro inesperado. Pressione Enter para continuar...")

def menu_gestao_sustentabilidade(conexao):
    """Menu para registrar insumos e gerenciar certificação."""
    id_produtor = crud.selecionar_produtor(conexao)
    if not id_produtor: print("Nenhum produtor selecionado."); return
    while True:
        print(f"\n--- Gestão de Práticas Sustentáveis (Produtor: {id_produtor}) ---")
        print("1. Registrar Aplicação de Insumo"); print("2. Excluir Registro de Insumo")
        print("3. Gerenciar Certificação"); print("0. Voltar"); print("-" * 55)
        opcao = input("Escolha: ").strip()
        try:
            if opcao == '1':
                id_talhao_produtor, id_talhao_unico = crud.selecionar_talhao(conexao, id_produtor)
                if id_talhao_unico: crud.registrar_insumo(conexao, id_produtor, id_talhao_produtor, id_talhao_unico)
            elif opcao == '2': crud.excluir_insumo(conexao, id_produtor)
            elif opcao == '3': crud.gerenciar_certificacao(conexao, id_produtor)
            elif opcao == '0': break
            else: print("Opção inválida.")
            if opcao != '0': input("\nPressione Enter para continuar...")
        except Exception as e:
            registrar_erro(f"Erro inesperado no menu de sustentabilidade (opção {opcao}): {e}")
            input("Ocorreu um erro inesperado. Pressione Enter para continuar...")

# --- NOVO MENU ---
def menu_gestao_demandas(conexao):
    """Menu para gerenciar demandas."""
    while True:
        print("\n--- Gestão de Demandas ---")
        print("1. Registrar Nova Demanda")
        print("2. Listar Demandas") # Adicionado para visualização
        print("3. Excluir Demanda")
        print("0. Voltar ao Menu Principal")
        print("-" * 28)
        opcao = input("Escolha: ").strip()
        try:
            if opcao == '1': crud.registrar_demanda(conexao)
            elif opcao == '2': reports.listar_demandas(conexao) # Chama a nova função de listagem
            elif opcao == '3': crud.excluir_demanda(conexao)
            elif opcao == '0': break
            else: print("Opção inválida.")
            if opcao != '0': input("\nPressione Enter para continuar...")
        except Exception as e:
            registrar_erro(f"Erro inesperado no menu de demandas (opção {opcao}): {e}")
            input("Ocorreu um erro inesperado. Pressione Enter para continuar...")

def menu_consultas_relatorios(conexao):
    """Menu para visualizações e relatórios (sem Mercado)."""
    while True:
        print("\n--- Outras Consultas e Relatórios ---")
        print("1. Gerar Relatório de Rastreabilidade")
        print("2. Calendário de Colheitas Previstas")
        print("0. Voltar ao Menu Principal")
        print("-" * 38)
        opcao = input("Escolha: ").strip()
        try:
            if opcao == '1': reports.gerar_relatorio_rastreabilidade(conexao)
            elif opcao == '2': reports.visualizar_calendario_colheitas(conexao)
            elif opcao == '0': break
            else: print("Opção inválida.")
            if opcao in ['1', '2']: input("\nPressione Enter para continuar...")
        except Exception as e:
            registrar_erro(f"Erro inesperado no menu de consultas (opção {opcao}): {e}")
            input("Ocorreu um erro inesperado. Pressione Enter para continuar...")