import uuid
import datetime 
import config 
from utils import obter_input_validado, confirmar_acao, registrar_erro, formatar_data_br 
import database 

# Importa cx_Oracle do config para checagem de tipo de erro
cx_Oracle = config.cx_Oracle 

# --- Produtor ---
def cadastrar_produtor(conexao):
    """Cadastra um novo produtor no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Cadastro de Novo Produtor ---")
    while True:
        id_produtor = obter_input_validado("ID único para o produtor (ex: CPF/CNPJ ou código)")
        if not id_produtor: continue
        cursor = None; existe = False
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT 1 FROM PRODUTORES WHERE id_produtor = :1", (id_produtor,))
            if cursor.fetchone(): existe = True
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao verificar ID produtor: {e}")
        except Exception as e: registrar_erro(f"Erro inesperado ao verificar ID: {e}")
        finally:
            if cursor: cursor.close()
        if existe: print("Erro: ID de produtor já existe no Oracle. Tente novamente.")
        else: break
    nome = obter_input_validado("Nome do Produtor/Propriedade: ")
    localizacao = obter_input_validado("Localização (Município/Estado): ")
    contato = obter_input_validado("Contato (Telefone/Email): ", obrigatorio=False)
    associacao = obter_input_validado("Associação (se houver): ", obrigatorio=False)
    certificacao_inicial = {"certificado": False, "etapas": {"Documentação": False, "Inspeção": False, "Aprovação": False}}
    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql_produtor = "INSERT INTO PRODUTORES (id_produtor, nome, localizacao, contato, associacao) VALUES (:1, :2, :3, :4, :5)"
        cursor.execute(sql_produtor, (id_produtor, nome, localizacao, contato, associacao))
        sql_cert = "INSERT INTO STATUS_CERTIFICACAO (id_produtor, certificado, etapa_documentacao, etapa_inspecao, etapa_aprovacao) VALUES (:1, :2, :3, :4, :5)"
        etapas = certificacao_inicial["etapas"]
        cursor.execute(sql_cert, (id_produtor, 0, 0, 0, 0))
        conexao.commit()
        print(f"Produtor '{nome}' cadastrado com sucesso no Oracle com ID '{id_produtor}'.")
        sucesso = True
    except cx_Oracle.IntegrityError as e: registrar_erro(f"Erro de Integridade Oracle (ID duplicado?): {e}"); conexao.rollback()
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao cadastrar produtor: {e}"); conexao.rollback()
    except Exception as e: registrar_erro(f"Erro inesperado ao cadastrar produtor Oracle: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def selecionar_produtor(conexao):
    """Lista produtores do Oracle e permite selecionar um pelo ID."""
    produtores_para_listar = database.carregar_produtores_talhoes(conexao)
    if not produtores_para_listar: print("Nenhum produtor cadastrado."); return None
    print("\n--- Produtores Cadastrados ---")
    lista_ordenada = sorted(produtores_para_listar.items(), key=lambda item: item[1].get('nome', ''))
    for id_p, dados_p in lista_ordenada: print(f"ID: {id_p} - Nome: {dados_p.get('nome', 'N/A')}")
    while True:
        id_selecionado = input("Digite o ID do produtor desejado (ou 0 para cancelar): ").strip()
        if id_selecionado == '0': return None
        if id_selecionado in produtores_para_listar: return id_selecionado
        else: print("ID inválido. Tente novamente.")

def editar_produtor(conexao):
    """Edita os dados de um produtor existente no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Editar Produtor ---")
    id_produtor = selecionar_produtor(conexao)
    if not id_produtor: return False

    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, localizacao, contato, associacao FROM PRODUTORES WHERE id_produtor = :1", (id_produtor,))
        row = cursor.fetchone()
        if not row: print("Erro: Produtor não encontrado no Oracle."); return False
        dados_atuais = {"nome": row[0], "localizacao": row[1], "contato": row[2], "associacao": row[3]}
        print("Digite os novos dados (ou pressione Enter para manter o atual):")
        nome = obter_input_validado("Nome", valor_padrao=dados_atuais["nome"])
        localizacao = obter_input_validado("Localização", valor_padrao=dados_atuais["localizacao"])
        contato = obter_input_validado("Contato", valor_padrao=dados_atuais["contato"], obrigatorio=False)
        associacao = obter_input_validado("Associação", valor_padrao=dados_atuais["associacao"], obrigatorio=False)
        sql_update = "UPDATE PRODUTORES SET nome = :1, localizacao = :2, contato = :3, associacao = :4 WHERE id_produtor = :5"
        cursor.execute(sql_update, (nome, localizacao, contato, associacao, id_produtor))
        conexao.commit(); print("Dados do produtor atualizados (Oracle)."); sucesso = True
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao editar produtor: {e}"); conexao.rollback()
    except Exception as e: registrar_erro(f"Erro inesperado Oracle: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def excluir_produtor(conexao):
    """Exclui um produtor do Oracle (ON DELETE CASCADE cuidará das dependências)."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Excluir Produtor ---")
    id_produtor = selecionar_produtor(conexao)
    if not id_produtor: return False

    print(f"[AVISO] Excluir o produtor '{id_produtor}' também excluirá seus talhões, plantios e insumos associados devido ao ON DELETE CASCADE.")
    if confirmar_acao(f"Excluir produtor '{id_produtor}' e TODOS os seus dados? (Irreversível)"):
        cursor = None; sucesso = False
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM PRODUTORES WHERE id_produtor = :1", (id_produtor,))
            if cursor.rowcount > 0: conexao.commit(); print(f"Produtor '{id_produtor}' e dados associados excluídos (Oracle)."); sucesso = True
            else: print("Produtor não encontrado (Oracle)."); conexao.rollback()
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao excluir produtor: {e}"); conexao.rollback()
        finally:
            if cursor: cursor.close()
        return sucesso
    return False

# --- Talhão ---
def cadastrar_talhao(conexao, id_produtor):
    """Cadastra um novo talhão para um produtor específico no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print(f"\n--- Cadastro de Novo Talhão para Produtor ID: {id_produtor} ---")
    while True:
        id_talhao_produtor = obter_input_validado("ID do talhão para o produtor (ex: T01, AreaNorte): ")
        if not id_talhao_produtor: continue
        cursor = None; existe = False
        try:
            cursor = conexao.cursor()
            sql = "SELECT 1 FROM TALHOES WHERE id_produtor = :1 AND id_talhao_produtor = :2"
            cursor.execute(sql, (id_produtor, id_talhao_produtor))
            if cursor.fetchone(): existe = True
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao verificar talhão: {e}")
        finally:
            if cursor: cursor.close()
        if existe: print("Erro: ID de talhão já existe para este produtor. Tente novamente.")
        else: break
    tamanho_ha = obter_input_validado("Tamanho do talhão (hectares): ", float)
    tipo_solo = obter_input_validado("Tipo de solo (opcional): ", obrigatorio=False)
    id_talhao_unico = str(uuid.uuid4())
    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql = "INSERT INTO TALHOES (id_talhao_unico, id_produtor, id_talhao_produtor, tamanho_ha, tipo_solo) VALUES (:1, :2, :3, :4, :5)"
        cursor.execute(sql, (id_talhao_unico, id_produtor, id_talhao_produtor, tamanho_ha, tipo_solo))
        conexao.commit(); print(f"Talhão '{id_talhao_produtor}' cadastrado (Oracle)."); sucesso = True
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao cadastrar talhão: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def selecionar_talhao(conexao, id_produtor):
    """Lista talhões de um produtor do Oracle e permite selecionar um."""
    produtores = database.carregar_produtores_talhoes(conexao)
    if id_produtor not in produtores or not produtores[id_produtor].get("talhoes"):
        print("Nenhum talhão cadastrado para este produtor.")
        return None, None
    talhoes_produtor = produtores[id_produtor]["talhoes"]
    print(f"\n--- Talhões do Produtor ID: {id_produtor} ---")
    lista_ordenada = sorted(talhoes_produtor.items())
    for id_t_prod, dados_t in lista_ordenada: print(f"ID: {id_t_prod} - Tamanho: {dados_t.get('tamanho_ha', 'N/A')} ha")
    while True:
        id_selecionado_produtor = input("Digite o ID do talhão desejado (ou 0 para cancelar): ").strip()
        if id_selecionado_produtor == '0': return None, None
        if id_selecionado_produtor in talhoes_produtor:
            id_talhao_unico = talhoes_produtor[id_selecionado_produtor].get("id_talhao_unico")
            return id_selecionado_produtor, id_talhao_unico
        else: print("ID inválido.")

def editar_talhao(conexao, id_produtor):
    """Edita os dados de um talhão existente no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Editar Talhão ---")
    id_talhao_produtor, id_talhao_unico = selecionar_talhao(conexao, id_produtor)
    if not id_talhao_unico: return False

    produtores_db = database.carregar_produtores_talhoes(conexao)
    dados_atuais = produtores_db.get(id_produtor, {}).get("talhoes", {}).get(id_talhao_produtor)
    if not dados_atuais: print("Erro: Dados do talhão não encontrados."); return False

    print("Digite os novos dados (ou pressione Enter para manter o atual):")
    tamanho_ha = obter_input_validado("Tamanho (ha)", float, valor_padrao=dados_atuais.get("tamanho_ha"))
    tipo_solo = obter_input_validado("Tipo de solo", str, valor_padrao=dados_atuais.get("tipo_solo"), obrigatorio=False)

    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql_update = "UPDATE TALHOES SET tamanho_ha = :1, tipo_solo = :2 WHERE id_talhao_unico = :3"
        cursor.execute(sql_update, (tamanho_ha, tipo_solo, id_talhao_unico))
        conexao.commit(); print(f"Dados do talhão '{id_talhao_produtor}' atualizados (Oracle)."); sucesso = True
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao editar talhão: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def excluir_talhao(conexao, id_produtor):
    """Exclui um talhão do Oracle (ON DELETE CASCADE cuidará das dependências)."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Excluir Talhão ---")
    id_talhao_produtor, id_talhao_unico = selecionar_talhao(conexao, id_produtor)
    if not id_talhao_unico: return False

    print(f"[AVISO] Excluir o talhão '{id_talhao_produtor}' também excluirá seus plantios e insumos (ON DELETE CASCADE).")
    if confirmar_acao(f"Excluir talhão '{id_talhao_produtor}' e dados associados?"):
        cursor = None; sucesso = False
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM TALHOES WHERE id_talhao_unico = :1", (id_talhao_unico,))
            if cursor.rowcount > 0: conexao.commit(); print(f"Talhão '{id_talhao_produtor}' excluído (Oracle)."); sucesso = True
            else: print("Talhão não encontrado (Oracle)."); conexao.rollback()
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao excluir talhão: {e}"); conexao.rollback()
        finally:
            if cursor: cursor.close()
        return sucesso
    return False

# --- Plantio/Produto ---
def obter_cultura_anterior(conexao, id_talhao_unico):
    """Busca a última cultura plantada para um talhão no Oracle."""
    if not conexao or cx_Oracle is None: return "Erro de conexão"
    cursor = None; cultura = "Nenhuma registrada"
    try:
        cursor = conexao.cursor()
        sql = """SELECT cultura FROM PLANTIOS_PRODUTOS WHERE id_talhao_unico = :1 ORDER BY data_plantio DESC FETCH FIRST 1 ROW ONLY"""
        cursor.execute(sql, (id_talhao_unico,))
        row = cursor.fetchone()
        if row: cultura = row[0]
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao buscar cultura anterior: {e}")
    finally:
        if cursor: cursor.close()
    return cultura

def registrar_plantio(conexao, id_produtor, id_talhao_produtor, id_talhao_unico):
    """Registra um novo plantio no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print(f"\n--- Registrar Novo Plantio (Produtor: {id_produtor}, Talhão: {id_talhao_produtor}) ---")
    cultura_anterior = obter_cultura_anterior(conexao, id_talhao_unico)
    print(f"Última cultura registrada neste talhão: {cultura_anterior}")
    cultura_atual = obter_input_validado("Cultura a ser plantada")
    if not cultura_atual: return False

    if cultura_atual.lower() == cultura_anterior.lower() and cultura_anterior != "Nenhuma registrada":
        print(f"[AVISO] Plantando '{cultura_atual}' novamente em sequência.")
        if not confirmar_acao("Continuar?"): return False

    while True: # Loop para validar data de plantio
        data_plantio = obter_input_validado("Data do Plantio", tipo_dado=datetime.date)
        if not data_plantio: return False # Cancelou
        # Validação: Data não pode ser mais antiga que 2 dias atrás
        data_minima = datetime.date.today() - datetime.timedelta(days=2)
        if data_plantio < data_minima:
            print(f"Erro: A data de plantio não pode ser anterior a {formatar_data_br(data_minima)}.")
        elif data_plantio > datetime.date.today():
             print(f"Erro: A data de plantio não pode ser futura.")
        else:
            break # Data válida

    data_prevista_colheita = obter_input_validado("Data PREVISTA da Colheita", tipo_dado=datetime.date)
    observacoes = obter_input_validado("Observações (opcional)", obrigatorio=False)

    if not data_prevista_colheita: print("Erro: Data prevista é obrigatória."); return False
    if data_prevista_colheita <= data_plantio: print("Erro: Data prevista inválida."); return False

    id_plantio = str(uuid.uuid4())
    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql = """INSERT INTO PLANTIOS_PRODUTOS (id_plantio, id_produtor, id_talhao_unico, cultura, data_plantio,
                   data_prevista_colheita, status, observacoes, cultura_anterior)
                   VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)"""
        cursor.execute(sql, (id_plantio, id_produtor, id_talhao_unico, cultura_atual, data_plantio,
                   data_prevista_colheita, "Planejado", observacoes, cultura_anterior))
        conexao.commit()
        print(f"Plantio de '{cultura_atual}' registrado (Oracle). Prev: {formatar_data_br(data_prevista_colheita)}")
        sucesso = True
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao registrar plantio: {e}"); conexao.rollback()
    except Exception as e: registrar_erro(f"Erro inesperado Oracle: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def selecionar_plantio(conexao, id_produtor, status_permitidos=None):
    """Lista plantios/produtos de um produtor do Oracle e permite selecionar um."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return None
    if status_permitidos is None: status_permitidos = ['Planejado', 'Disponível']
    print(f"\n--- Selecionar Plantio/Produto (Produtor: {id_produtor}) ---")
    plantios_produtor = []
    cursor = None
    try:
        cursor = conexao.cursor()
        status_placeholders = ','.join([f':{i+2}' for i in range(len(status_permitidos))])
        sql = f"""SELECT p.id_plantio, p.cultura, t.id_talhao_produtor, p.status,
                   CASE p.status WHEN 'Disponível' THEN p.data_colheita_real ELSE p.data_prevista_colheita END AS data_ref
                   FROM PLANTIOS_PRODUTOS p JOIN TALHOES t ON p.id_talhao_unico = t.id_talhao_unico
                   WHERE p.id_produtor = :1 AND p.status IN ({status_placeholders}) ORDER BY data_ref DESC NULLS LAST"""
        params = [id_produtor] + status_permitidos
        cursor.execute(sql, params)
        for row in cursor.fetchall():
             data_ref_obj = row[4] if isinstance(row[4], datetime.date) else (row[4].date() if isinstance(row[4], datetime.datetime) else datetime.date.min)
             plantios_produtor.append({
                 "id_plantio": row[0], "cultura": row[1], "id_talhao_produtor": row[2],
                 "status": row[3], "data_ref_obj": data_ref_obj,
                 "data_ref_str": formatar_data_br(data_ref_obj) })
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao listar plantios: {e}")
    finally:
        if cursor: cursor.close()

    if not plantios_produtor: print(f"Nenhum registro encontrado com status: {', '.join(status_permitidos)}"); return None

    print("Registros encontrados:")
    for i, p in enumerate(plantios_produtor):
        # Mostra o ID completo
        print(f"{i+1}. ID: {p['id_plantio']} - Cultura: {p['cultura']} ({p['status']}) - Talhão: {p['id_talhao_produtor']} - Data Ref: {p['data_ref_str']}")

    while True:
        try:
            escolha_str = input(f"Digite o número (1-{len(plantios_produtor)}) ou 0 para cancelar: ").strip()
            if not escolha_str: continue
            escolha = int(escolha_str)
            if escolha == 0: return None
            if 1 <= escolha <= len(plantios_produtor): return plantios_produtor[escolha-1]['id_plantio']
            else: print("Número inválido.")
        except ValueError: print("Entrada inválida.")

def editar_plantio(conexao, id_produtor):
    """Edita dados de um plantio/produto existente no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Editar Plantio/Produto ---")
    id_plantio = selecionar_plantio(conexao, id_produtor, status_permitidos=['Planejado', 'Disponível'])
    if not id_plantio: return False

    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql_select = """SELECT cultura, data_plantio, data_prevista_colheita, data_colheita_real, quantidade_colhida,
                           unidade_medida, status, observacoes, cultura_anterior
                           FROM PLANTIOS_PRODUTOS WHERE id_plantio = :1"""
        cursor.execute(sql_select, (id_plantio,))
        row = cursor.fetchone()
        if not row: print("Erro: Plantio não encontrado no Oracle."); return False
        cols = [desc[0].lower() for desc in cursor.description]
        dados_atuais = dict(zip(cols, row))
        for key in ['data_plantio', 'data_prevista_colheita', 'data_colheita_real']:
             if isinstance(dados_atuais.get(key), datetime.datetime): dados_atuais[key] = dados_atuais[key].date()

        print("Digite os novos dados (ou pressione Enter para manter o atual):")
        cultura = obter_input_validado("Cultura", str, valor_padrao=dados_atuais.get("cultura"))
        # Validação da data de plantio na edição também
        while True:
            data_plantio = obter_input_validado("Data Plantio", datetime.date, valor_padrao=dados_atuais.get("data_plantio"))
            if not data_plantio: break # Permite manter a data atual
            data_minima = datetime.date.today() - datetime.timedelta(days=2)
            if data_plantio < data_minima: print(f"Erro: Data de plantio não pode ser anterior a {formatar_data_br(data_minima)}.")
            elif data_plantio > datetime.date.today(): print(f"Erro: Data de plantio não pode ser futura.")
            else: break

        data_prevista_colheita = obter_input_validado("Data Prev. Colheita", datetime.date, valor_padrao=dados_atuais.get("data_prevista_colheita"))
        cultura_anterior = obter_input_validado("Cultura Anterior", str, valor_padrao=dados_atuais.get("cultura_anterior"), obrigatorio=False)
        observacoes = obter_input_validado("Observações", str, valor_padrao=dados_atuais.get("observacoes"), obrigatorio=False)

        data_colheita_real = dados_atuais.get("data_colheita_real")
        quantidade_colhida = dados_atuais.get("quantidade_colhida")
        unidade_medida = dados_atuais.get("unidade_medida")
        if dados_atuais.get("status") == 'Disponível':
            print("--- Editar Dados da Colheita ---")
            data_colheita_real = obter_input_validado("Data Real Colheita", datetime.date, valor_padrao=data_colheita_real)
            quantidade_colhida = obter_input_validado("Quantidade Colhida", float, valor_padrao=quantidade_colhida)
            unidade_medida = obter_input_validado("Unidade Medida", str, valor_padrao=unidade_medida)

        # Verifica consistência das datas
        if data_prevista_colheita and data_plantio and data_prevista_colheita <= data_plantio:
             print("Erro: Data prevista da colheita deve ser posterior à data de plantio."); return False
        if data_colheita_real and data_plantio and data_colheita_real < data_plantio:
             print("Erro: Data real da colheita não pode ser anterior à data de plantio."); return False


        sql_update = """UPDATE PLANTIOS_PRODUTOS SET cultura = :1, data_plantio = :2, data_prevista_colheita = :3,
                           data_colheita_real = :4, quantidade_colhida = :5, unidade_medida = :6,
                           observacoes = :7, cultura_anterior = :8 WHERE id_plantio = :9"""
        cursor.execute(sql_update, (cultura, data_plantio, data_prevista_colheita, data_colheita_real, quantidade_colhida,
                                     unidade_medida, observacoes, cultura_anterior, id_plantio))
        conexao.commit(); print("Dados atualizados (Oracle)."); sucesso = True
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao editar plantio: {e}"); conexao.rollback()
    except Exception as e: registrar_erro(f"Erro inesperado Oracle: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def excluir_plantio(conexao, id_produtor):
    """Exclui um registro de plantio/produto do Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Excluir Plantio/Produto ---")
    id_plantio = selecionar_plantio(conexao, id_produtor, status_permitidos=['Planejado', 'Disponível', 'Cancelado'])
    if not id_plantio: return False

    if confirmar_acao(f"Excluir registro ID {id_plantio}?"): # Mostra ID completo na confirmação
        cursor = None; sucesso = False
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM PLANTIOS_PRODUTOS WHERE id_plantio = :1", (id_plantio,))
            if cursor.rowcount > 0: conexao.commit(); print("Registro excluído (Oracle)."); sucesso = True
            else: print("Registro não encontrado (Oracle)."); conexao.rollback()
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao excluir plantio: {e}"); conexao.rollback()
        finally:
            if cursor: cursor.close()
        return sucesso
    return False

def confirmar_colheita(conexao, id_produtor):
    """Permite ao produtor confirmar a colheita de um plantio planejado no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Confirmar Colheita ---")
    id_plantio = selecionar_plantio(conexao, id_produtor, status_permitidos=['Planejado'])
    if not id_plantio: print("Nenhum plantio planejado selecionado."); return False

    data_colheita_real = obter_input_validado("Data REAL da Colheita", tipo_dado=datetime.date)
    quantidade_colhida = obter_input_validado("Quantidade Colhida (número)", tipo_dado=float)
    unidade_medida = obter_input_validado("Unidade de Medida (kg, ton, caixa, etc.)")
    if not data_colheita_real or quantidade_colhida is None or not unidade_medida:
        print("Erro: Todos os dados da colheita são obrigatórios."); return False

    # Validação extra: data da colheita não pode ser anterior ao plantio
    cursor = None
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT data_plantio FROM PLANTIOS_PRODUTOS WHERE id_plantio = :1", (id_plantio,))
        row = cursor.fetchone()
        if row and row[0] and isinstance(row[0], datetime.datetime) and data_colheita_real < row[0].date():
             print(f"Erro: Data da colheita ({formatar_data_br(data_colheita_real)}) não pode ser anterior à data de plantio ({formatar_data_br(row[0].date())}).")
             return False
    except cx_Oracle.DatabaseError as e:
        registrar_erro(f"Erro Oracle ao buscar data de plantio para validação: {e}")
        # Decide se continua ou não, por segurança vamos impedir
        return False
    finally:
        if cursor: cursor.close()


    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql = """UPDATE PLANTIOS_PRODUTOS SET status = 'Disponível', data_colheita_real = :1,
                   quantidade_colhida = :2, unidade_medida = :3 WHERE id_plantio = :4"""
        cursor.execute(sql, (data_colheita_real, quantidade_colhida, unidade_medida, id_plantio))
        if cursor.rowcount > 0: conexao.commit(); print(f"\nColheita confirmada (Oracle)."); sucesso = True
        else: print(f"Erro: Plantio {id_plantio} não encontrado (Oracle)."); conexao.rollback()
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

# --- Insumo ---
def registrar_insumo(conexao, id_produtor, id_talhao_produtor, id_talhao_unico):
    """Registra a aplicação de um insumo orgânico no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print(f"\n--- Registrar Aplicação de Insumo (Produtor: {id_produtor}, Talhão: {id_talhao_produtor}) ---")
    data_aplicacao = obter_input_validado("Data da Aplicação", tipo_dado=datetime.date)
    tipo_insumo = obter_input_validado("Tipo de Insumo (Composto, Adubo Verde, etc.)")
    quantidade = obter_input_validado("Quantidade Aplicada (ex: kg, L, m³)", obrigatorio=False)
    observacoes = obter_input_validado("Observações (opcional)", obrigatorio=False)
    if not data_aplicacao or not tipo_insumo: print("Erro: Data e Tipo de Insumo são obrigatórios."); return False
    id_registro = str(uuid.uuid4())

    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql = """INSERT INTO REGISTROS_INSUMOS (id_registro, id_produtor, id_talhao_unico, data_aplicacao, tipo_insumo, quantidade, observacoes)
                   VALUES (:1, :2, :3, :4, :5, :6, :7)"""
        cursor.execute(sql, (id_registro, id_produtor, id_talhao_unico, data_aplicacao, tipo_insumo, quantidade, observacoes))
        conexao.commit(); print(f"Registro de '{tipo_insumo}' salvo (Oracle)."); sucesso = True
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def selecionar_insumo(conexao, id_produtor):
    """Lista registros de insumo de um produtor do Oracle e permite selecionar um."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return None
    print(f"\n--- Selecionar Registro de Insumo (Produtor: {id_produtor}) ---")
    registros_produtor = []
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = """SELECT r.id_registro, r.data_aplicacao, r.tipo_insumo, t.id_talhao_produtor
                   FROM REGISTROS_INSUMOS r JOIN TALHOES t ON r.id_talhao_unico = t.id_talhao_unico
                   WHERE r.id_produtor = :1 ORDER BY r.data_aplicacao DESC"""
        cursor.execute(sql, (id_produtor,))
        for row in cursor.fetchall():
             data_app_obj = row[1].date() if isinstance(row[1], datetime.datetime) else row[1]
             registros_produtor.append({
                 "id_registro": row[0], "data_aplicacao_obj": data_app_obj,
                 "data_aplicacao_br": formatar_data_br(data_app_obj), # Usa formatar_data_br
                 "tipo_insumo": row[2], "id_talhao_produtor": row[3] })
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao listar insumos: {e}")
    finally:
        if cursor: cursor.close()

    if not registros_produtor: print("Nenhum registro de insumo encontrado."); return None

    print("Registros encontrados:")
    for i, r in enumerate(registros_produtor):
        # Mostra ID completo para facilitar a exclusão
        print(f"{i+1}. ID: {r['id_registro']} - Data: {r['data_aplicacao_br']} - Tipo: {r['tipo_insumo']} - Talhão: {r['id_talhao_produtor']}")

    while True:
        try:
            escolha_str = input(f"Digite o número (1-{len(registros_produtor)}) ou 0 para cancelar: ").strip()
            if not escolha_str: continue
            escolha = int(escolha_str)
            if escolha == 0: return None
            if 1 <= escolha <= len(registros_produtor): return registros_produtor[escolha-1]['id_registro']
            else: print("Número inválido.")
        except ValueError: print("Entrada inválida.");

def excluir_insumo(conexao, id_produtor):
    """Exclui um registro de aplicação de insumo do Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Excluir Registro de Insumo ---")
    id_registro = selecionar_insumo(conexao, id_produtor) # Chama a função corrigida
    if not id_registro: return False

    if confirmar_acao(f"Excluir registro de insumo ID {id_registro[:8]}...?"): # Mostra ID truncado na confirmação
        cursor = None; sucesso = False
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM REGISTROS_INSUMOS WHERE id_registro = :1", (id_registro,))
            if cursor.rowcount > 0: conexao.commit(); print("Registro excluído (Oracle)."); sucesso = True
            else: print("Registro não encontrado (Oracle)."); conexao.rollback()
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao excluir insumo: {e}"); conexao.rollback()
        finally:
            if cursor: cursor.close()
        return sucesso
    return False

# --- Certificação ---
def gerenciar_certificacao(conexao, id_produtor):
    """Permite visualizar e atualizar o status da certificação orgânica no Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return
    print(f"\n--- Status da Certificação Orgânica (Produtor: {id_produtor}) ---")
    etapas_map = {"etapa_documentacao": "Documentação", "etapa_inspecao": "Inspeção", "etapa_aprovacao": "Aprovação"}
    dados_produtor = database.carregar_status_certificacao(conexao).get(id_produtor) # Carrega do Oracle

    if not dados_produtor:
        print(f"Status não encontrado para produtor {id_produtor}. Verifique cadastro."); return

    # Exibe status
    print(f"Status Geral: {'CERTIFICADO' if dados_produtor.get('certificado', False) else 'NÃO CERTIFICADO'}")
    print("Etapas:")
    etapas_atuais = dados_produtor.get("etapas", {})
    etapas_nomes = list(etapas_map.values())
    for i, nome_etapa in enumerate(etapas_nomes): print(f"{i+1}. {nome_etapa}: {'[X]' if etapas_atuais.get(nome_etapa, False) else '[ ]'}")

    # Opções
    print("\nOpções: M - Marcar/Desmarcar | C - Alterar status geral | V - Voltar")
    while True:
        opcao = input("Escolha: ").strip().upper()
        if opcao == 'V': break
        elif opcao == 'C':
            novo_status_bool = confirmar_acao("Marcar como CERTIFICADO?")
            cursor = None
            try:
                cursor = conexao.cursor()
                sql = "UPDATE STATUS_CERTIFICACAO SET certificado = :1 WHERE id_produtor = :2"
                cursor.execute(sql, (1 if novo_status_bool else 0, id_produtor)); conexao.commit()
                print(f"Status geral alterado (Oracle).")
                dados_produtor['certificado'] = novo_status_bool # Atualiza memória
            except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle: {e}"); conexao.rollback()
            finally:
                if cursor: cursor.close()
            break
        elif opcao == 'M':
            while True:
                try:
                    num_etapa = int(input(f"Número da etapa (1-{len(etapas_nomes)}): "))
                    if 1 <= num_etapa <= len(etapas_nomes):
                        nome_etapa = etapas_nomes[num_etapa-1]
                        db_key = list(etapas_map.keys())[num_etapa-1]
                        novo_status_etapa = not dados_produtor['etapas'][nome_etapa]
                        cursor = None
                        try:
                            cursor = conexao.cursor()
                            sql = f"UPDATE STATUS_CERTIFICACAO SET {db_key} = :1 WHERE id_produtor = :2"
                            cursor.execute(sql, (1 if novo_status_etapa else 0, id_produtor)); conexao.commit()
                            print(f"Status '{nome_etapa}' alterado (Oracle).")
                            dados_produtor['etapas'][nome_etapa] = novo_status_etapa # Atualiza memória
                        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle: {e}"); conexao.rollback()
                        finally:
                            if cursor: cursor.close()
                        break # Sai do loop de marcar etapa
                    else: print("Número inválido.")
                except ValueError: print("Entrada inválida.")
            break # Sai após alterar etapa
        else: print("Opção inválida.")

# --- Demanda ---
def registrar_demanda(conexao):
    """Registra uma nova demanda de produto."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Registrar Nova Demanda ---")

    cultura = obter_input_validado("Cultura desejada")
    quantidade = obter_input_validado("Quantidade necessária", float)
    unidade_medida = obter_input_validado("Unidade de Medida (kg, ton, caixa, etc.)")
    while True: # Loop para validar data da demanda
        data_necessidade = obter_input_validado("Data para quando precisa do produto", datetime.date)
        if not data_necessidade: return False # Cancelou
        if data_necessidade < datetime.date.today():
            print("Erro: A data de necessidade não pode ser uma data passada.")
        else:
            break # Data válida
    observacoes = obter_input_validado("Observações (opcional)", obrigatorio=False)

    if not cultura or quantidade is None or not unidade_medida:
         print("Erro: Cultura, Quantidade e Unidade são obrigatórios.")
         return False

    id_demanda = str(uuid.uuid4())
    cursor = None; sucesso = False
    try:
        cursor = conexao.cursor()
        sql = """INSERT INTO DEMANDAS (id_demanda, cultura, quantidade, unidade_medida, data_necessidade, observacoes)
                   VALUES (:1, :2, :3, :4, :5, :6)"""
        cursor.execute(sql, (id_demanda, cultura, quantidade, unidade_medida, data_necessidade, observacoes))
        conexao.commit()
        print(f"Demanda por '{cultura}' registrada com sucesso (ID: {id_demanda[:8]}...).")
        sucesso = True
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao registrar demanda: {e}"); conexao.rollback()
    except Exception as e: registrar_erro(f"Erro inesperado Oracle: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()
    return sucesso

def selecionar_demanda(conexao):
    """Lista demandas registradas e permite selecionar uma."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return None
    print("\n--- Selecionar Demanda Registrada ---")
    demandas = database.carregar_demandas(conexao) # Carrega do Oracle
    if not demandas: print("Nenhuma demanda registrada."); return None

    print("Demandas Registradas:")
    for i, d in enumerate(demandas):
        print(f"{i+1}. ID: {d['id_demanda'][:8]}... - Cultura: {d['cultura']} - Qtd: {d['quantidade']} {d['unidade_medida']} - Precisa em: {formatar_data_br(d.get('data_necessidade'))}")

    while True:
        try:
            escolha_str = input(f"Digite o número (1-{len(demandas)}) ou 0 para cancelar: ").strip()
            if not escolha_str: continue
            escolha = int(escolha_str)
            if escolha == 0: return None
            if 1 <= escolha <= len(demandas): return demandas[escolha-1]['id_demanda']
            else: print("Número inválido.")
        except ValueError: print("Entrada inválida.")

def excluir_demanda(conexao):
    """Exclui um registro de demanda do Oracle."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return False
    print("\n--- Excluir Demanda ---")
    id_demanda = selecionar_demanda(conexao)
    if not id_demanda: return False

    if confirmar_acao(f"Excluir registro de demanda ID {id_demanda[:8]}...?"):
        cursor = None; sucesso = False
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM DEMANDAS WHERE id_demanda = :1", (id_demanda,))
            if cursor.rowcount > 0: conexao.commit(); print("Registro de demanda excluído (Oracle)."); sucesso = True
            else: print("Registro de demanda não encontrado (Oracle)."); conexao.rollback()
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao excluir demanda: {e}"); conexao.rollback()
        finally:
            if cursor: cursor.close()
        return sucesso
    return False