import sys 
import config 
import database 
import ui 
import reports 
from utils import registrar_erro 

def main_loop():
    """Função principal que executa o loop do menu."""
    if config.cx_Oracle is None:
        print("\nERRO CRÍTICO: Biblioteca cx_Oracle não encontrada."); sys.exit(1)

    conexao_bd = database.conectar_banco()
    if not conexao_bd:
        print("\nERRO CRÍTICO: Falha ao conectar ao Oracle."); sys.exit(1)

    while True:
        try:
            opcao = ui.menu_principal()

            if opcao == '1': ui.menu_gestao_produtores(conexao_bd)
            elif opcao == '2': ui.menu_gestao_talhoes(conexao_bd)
            elif opcao == '3': ui.menu_gestao_plantios(conexao_bd)
            elif opcao == '4': ui.menu_gestao_sustentabilidade(conexao_bd)
            elif opcao == '5': ui.menu_gestao_demandas(conexao_bd) 
            elif opcao == '6': reports.buscar_produtos_mercado(conexao_bd) 
            elif opcao == '7': ui.menu_consultas_relatorios(conexao_bd) 
            elif opcao == '0': print("Saindo..."); break
            else:
                print("Opção inválida.")
                input("\nPressione Enter...")

        except KeyboardInterrupt: print("\nSaindo..."); break
        except Exception as e:
             registrar_erro(f"Erro inesperado no loop principal: {e}")
             print("Erro inesperado. Verifique o log."); input("Enter...")

    database.desconectar_banco(conexao_bd)

# --- Ponto de EntradAa ---
if __name__ == "__main__":
    print("Iniciando Agrorgânica Soluções Sustentáveis...") 
    main_loop()
    print("Aplicação encerrada.")