import os
import sys

# Tenta importar cx_Oracle
try:
    import cx_Oracle
    print("[Config INFO] Biblioteca cx_Oracle carregada.")
except ImportError:
    cx_Oracle = None
    print("[ERRO] Biblioteca cx_Oracle não encontrada. A aplicação não funcionará sem ela.")
    print("       Instale com 'pip install cx_Oracle' e configure o Oracle Client.")
    # sys.exit("Erro crítico: cx_Oracle não encontrado.")

# --- Constantes ---
ARQUIVO_LOG_ERROS = "erros_agrorgânica.log" # Atualiza nome do log

# --- Configurações Oracle ---
# !!! IMPORTANTE: Use variáveis de ambiente ou um método seguro para gerenciar credenciais !!!
ORACLE_USER = os.environ.get("ORACLE_USER", "RM562839")
ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "120296")
ORACLE_DSN = os.environ.get("ORACLE_DSN", "oracle.fiap.com.br:1521/ORCL")

# Assume-se que Oracle é necessário se cx_Oracle foi importado.

print(f"[Config INFO] Configurado para usar Oracle.")
if "SEU_" in ORACLE_USER or "SEU_" in ORACLE_PASSWORD or "SEU_" in ORACLE_DSN:
    print("[AVISO] Placeholders de credenciais/DSN Oracle detectados em config.py.")