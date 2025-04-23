import datetime
import os
import config # Garante que config seja importado aqui para acessar ARQUIVO_LOG_ERROS

# --- Funções de Log e Validação ---

def registrar_erro(mensagem):
    """Registra uma mensagem de erro no arquivo de log."""
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_mensagem = f"[{agora}] ERRO: {mensagem}\n"
    print("\n" + "="*10 + " ERRO " + "="*10)
    print(mensagem)
    print("="*26 + "\n")
    try:
        with open(config.ARQUIVO_LOG_ERROS, 'a', encoding='utf-8') as f:
            f.write(log_mensagem)
    except NameError:
         print(f"[{agora}] ERRO CRÍTICO: Falha ao acessar config.ARQUIVO_LOG_ERROS para logar.")
    except IOError as e:
        print(f"[{agora}] ERRO CRÍTICO: Não foi possível escrever no log {config.ARQUIVO_LOG_ERROS}: {e}")
    except Exception as e:
         print(f"[{agora}] ERRO CRÍTICO INESPERADO ao tentar logar: {e}")


def validar_data_br(data_str):
    """Valida se a string está no formato DD/MM/YYYY."""
    try:
        datetime.datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def obter_input_validado(prompt, tipo_dado=str, validacao_extra=None, obrigatorio=True, valor_padrao=None):
    """Solicita input do usuário, valida, e permite valor padrão para edição."""
    while True:
        prompt_completo = prompt
        if tipo_dado == datetime.date:
            prompt_completo += "(DD/MM/AAAA)"
        if valor_padrao is not None:
             valor_padrao_str = valor_padrao
             if isinstance(valor_padrao, datetime.date):
                 valor_padrao_str = valor_padrao.strftime('%d/%m/%Y')
             prompt_completo += f" [{valor_padrao_str}]"

        prompt_completo += ": "
        try:
            valor_str = input(prompt_completo).strip()
        except EOFError:
             registrar_erro("Entrada de dados interrompida (EOFError).")
             return None

        if not valor_str:
            if valor_padrao is not None: return valor_padrao
            elif not obrigatorio: return None
            else: print("Erro: Este campo é obrigatório."); continue

        try:
            if tipo_dado == int: valor = int(valor_str)
            elif tipo_dado == float: valor = float(valor_str)
            elif tipo_dado == datetime.date:
                 if not validar_data_br(valor_str): raise ValueError("Formato de data inválido.")
                 valor = datetime.datetime.strptime(valor_str, '%d/%m/%Y').date()
            else: valor = valor_str

            if validacao_extra and not validacao_extra(valor): continue
            return valor

        except ValueError as e:
            erro_msg = f"Entrada inválida ({e})."
            if tipo_dado == datetime.date: erro_msg += " Use o formato DD/MM/AAAA."
            elif tipo_dado in [int, float]: erro_msg += f" Esperado um número ({tipo_dado.__name__})."
            print(f"Erro: {erro_msg} Tente novamente.")
        except Exception as e:
             registrar_erro(f"Erro inesperado durante obtenção de input para '{prompt}': {e}")
             print("Ocorreu um erro inesperado ao processar sua entrada. Tente novamente.")


def confirmar_acao(mensagem="Você tem certeza?"):
    """Pede confirmação do usuário (S/N)."""
    while True:
        try:
            resposta = input(f"{mensagem} (S/N): ").strip().upper()
            if resposta in ['S', 'N']: return resposta == 'S'
            else: print("Resposta inválida. Digite S ou N.")
        except EOFError:
            registrar_erro("Entrada de dados interrompida (EOFError) na confirmação.")
            return False

def formatar_data_br(data_obj):
    """Formata um objeto date ou datetime para DD/MM/YYYY ou retorna 'N/A'."""
    if isinstance(data_obj, (datetime.date, datetime.datetime)):
        return data_obj.strftime('%d/%m/%Y')
    return 'N/A'