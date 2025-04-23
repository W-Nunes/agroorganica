import datetime 
import config 
from utils import registrar_erro 

# Importa cx_Oracle do config 
cx_Oracle = config.cx_Oracle # Já definido globalmente

# --- Funções de Banco de Dados Oracle ---

def criar_tabelas_se_nao_existir(conexao):
    """Cria as tabelas necessárias no banco de dados Oracle se elas não existirem."""
    if not conexao or cx_Oracle is None:
        registrar_erro("Tentativa de criar tabelas sem conexão Oracle válida.")
        return

    cursor = None
    try:
        cursor = conexao.cursor()
        tabelas_necessarias = {
            "PRODUTORES": """
                CREATE TABLE PRODUTORES (
                    id_produtor VARCHAR2(50) PRIMARY KEY, nome VARCHAR2(200) NOT NULL,
                    localizacao VARCHAR2(200), contato VARCHAR2(100), associacao VARCHAR2(100) )
            """,
            "TALHOES": """
                CREATE TABLE TALHOES (
                    id_talhao_unico VARCHAR2(40) PRIMARY KEY,
                    id_produtor VARCHAR2(50) NOT NULL REFERENCES PRODUTORES(id_produtor) ON DELETE CASCADE,
                    id_talhao_produtor VARCHAR2(50) NOT NULL, tamanho_ha NUMBER, tipo_solo VARCHAR2(100),
                    CONSTRAINT uk_produtor_talhao UNIQUE (id_produtor, id_talhao_produtor) )
            """,
            "PLANTIOS_PRODUTOS": """
                CREATE TABLE PLANTIOS_PRODUTOS (
                    id_plantio VARCHAR2(40) PRIMARY KEY,
                    id_produtor VARCHAR2(50) NOT NULL REFERENCES PRODUTORES(id_produtor) ON DELETE CASCADE,
                    id_talhao_unico VARCHAR2(40) NOT NULL REFERENCES TALHOES(id_talhao_unico) ON DELETE CASCADE,
                    cultura VARCHAR2(100) NOT NULL, data_plantio DATE, data_prevista_colheita DATE, data_colheita_real DATE,
                    quantidade_colhida NUMBER, unidade_medida VARCHAR2(20),
                    status VARCHAR2(20) CHECK (status IN ('Planejado', 'Disponível', 'Vendido', 'Cancelado')),
                    observacoes CLOB, cultura_anterior VARCHAR2(100) )
            """,
             "REGISTROS_INSUMOS": """
                CREATE TABLE REGISTROS_INSUMOS (
                    id_registro VARCHAR2(40) PRIMARY KEY,
                    id_produtor VARCHAR2(50) NOT NULL REFERENCES PRODUTORES(id_produtor) ON DELETE CASCADE,
                    id_talhao_unico VARCHAR2(40) NOT NULL REFERENCES TALHOES(id_talhao_unico) ON DELETE CASCADE,
                    data_aplicacao DATE, tipo_insumo VARCHAR2(100), quantidade VARCHAR2(50), observacoes CLOB )
            """,
            "STATUS_CERTIFICACAO": """
                CREATE TABLE STATUS_CERTIFICACAO (
                    id_produtor VARCHAR2(50) PRIMARY KEY REFERENCES PRODUTORES(id_produtor) ON DELETE CASCADE,
                    certificado NUMBER(1) DEFAULT 0 NOT NULL CHECK (certificado IN (0, 1)),
                    etapa_documentacao NUMBER(1) DEFAULT 0 NOT NULL CHECK (etapa_documentacao IN (0, 1)),
                    etapa_inspecao NUMBER(1) DEFAULT 0 NOT NULL CHECK (etapa_inspecao IN (0, 1)),
                    etapa_aprovacao NUMBER(1) DEFAULT 0 NOT NULL CHECK (etapa_aprovacao IN (0, 1)) )
            """,
           
            "DEMANDAS": """
                CREATE TABLE DEMANDAS (
                    id_demanda VARCHAR2(40) PRIMARY KEY,
                    cultura VARCHAR2(100) NOT NULL,
                    quantidade NUMBER NOT NULL,
                    unidade_medida VARCHAR2(20) NOT NULL,
                    data_necessidade DATE NOT NULL,
                    observacoes CLOB,
                    registrado_em DATE DEFAULT SYSDATE
                )
            """
        }
        cursor.execute("SELECT table_name FROM user_tables")
        tabelas_existentes = {row[0] for row in cursor.fetchall()}
        print(f"[DB INFO] Tabelas existentes: {tabelas_existentes}")
        for nome_tabela, sql_create in tabelas_necessarias.items():
            if nome_tabela.upper() not in tabelas_existentes:
                print(f"[DB INFO] Criando tabela {nome_tabela.upper()}...")
                cursor.execute(sql_create)
                print(f"[DB INFO] Tabela {nome_tabela.upper()} criada.")
            else: print(f"[DB INFO] Tabela {nome_tabela.upper()} já existe.")
        conexao.commit(); print("[DB INFO] Verificação/Criação de tabelas concluída.")
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao verificar/criar tabelas: {e}"); conexao.rollback()
    except Exception as e: registrar_erro(f"Erro inesperado ao criar tabelas: {e}"); conexao.rollback()
    finally:
        if cursor: cursor.close()

def conectar_banco():
    """Conecta ao banco de dados Oracle."""
    if cx_Oracle is None:
        registrar_erro("Biblioteca cx_Oracle não está disponível. Impossível conectar ao Oracle.")
        return None

    if "SEU_" in config.ORACLE_USER or "SEU_" in config.ORACLE_PASSWORD or "SEU_" in config.ORACLE_DSN:
         print("\n" + "!"*68)
         print("!!! ATENÇÃO: Credenciais/DSN Oracle não parecem configurados. !!!")
         print("!!!          Verifique as constantes em config.py ou variáveis de ambiente. !!!")
         print("!"*68 + "\n")

    print(f"[INFO] Tentando conectar ao Oracle DSN: {config.ORACLE_DSN} com usuário: {config.ORACLE_USER}...")
    try:
        conexao = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
        print("[INFO] Conexão Oracle estabelecida com sucesso.")
        criar_tabelas_se_nao_existir(conexao)
        return conexao
    except cx_Oracle.DatabaseError as e:
        registrar_erro(f"Erro ao conectar ao Oracle: {e}")
        print("!!! FALHA NA CONEXÃO ORACLE. Verifique DSN, usuário, senha e Oracle Client.")
        return None
    except Exception as e:
        registrar_erro(f"Erro inesperado ao conectar ao Oracle: {e}")
        return None

def desconectar_banco(conexao):
    """Fecha a conexão com o banco de dados Oracle."""
    if conexao and hasattr(conexao, 'close') and cx_Oracle:
        print("[INFO] Desconectando do Banco de Dados Oracle...")
        try: conexao.close(); print("[INFO] Conexão Oracle fechada.")
        except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro ao fechar conexão Oracle: {e}")


# --- Funções de Carregamento de Dados ---

def carregar_produtores_talhoes(conexao):
    """Carrega dados de produtores e talhões do Oracle."""
    if not conexao or cx_Oracle is None: return {}
    produtores = {}
    cursor = None
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id_produtor, nome, localizacao, contato, associacao FROM PRODUTORES")
        prod_rows = cursor.fetchall()
        cols_prod = [desc[0].lower() for desc in cursor.description]
        for row in prod_rows: produtores[row[0]] = dict(zip(cols_prod, row)); produtores[row[0]]['talhoes'] = {}
        cursor.execute("SELECT id_talhao_unico, id_produtor, id_talhao_produtor, tamanho_ha, tipo_solo FROM TALHOES")
        tal_rows = cursor.fetchall()
        cols_tal = [desc[0].lower() for desc in cursor.description]
        for row in tal_rows:
             id_prod = row[1]
             if id_prod in produtores:
                 id_talhao_prod = row[2]
                 talhao_data = dict(zip(cols_tal, row))
                 del talhao_data['id_produtor']
                 produtores[id_prod]["talhoes"][id_talhao_prod] = talhao_data
        return produtores
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao carregar produtores/talhões: {e}"); return {}
    finally:
        if cursor: cursor.close()

def carregar_plantios_produtos(conexao):
    """Carrega dados de plantios e produtos do Oracle."""
    if not conexao or cx_Oracle is None: return []
    plantios = []
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = """SELECT id_plantio, id_produtor, id_talhao_unico, cultura, data_plantio, data_prevista_colheita,
                   data_colheita_real, quantidade_colhida, unidade_medida, status, observacoes, cultura_anterior
                   FROM PLANTIOS_PRODUTOS"""
        cursor.execute(sql)
        cols = [desc[0].lower() for desc in cursor.description]
        for row in cursor.fetchall():
            row_dict = dict(zip(cols, row))
            for key in ['data_plantio', 'data_prevista_colheita', 'data_colheita_real']:
                if isinstance(row_dict.get(key), datetime.datetime): row_dict[key] = row_dict[key].date()
            plantios.append(row_dict)
        return plantios
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao carregar plantios: {e}"); return []
    finally:
        if cursor: cursor.close()

def carregar_registros_insumos(conexao):
    """Carrega registros de insumos do Oracle."""
    if not conexao or cx_Oracle is None: return []
    insumos = []
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = """SELECT id_registro, id_produtor, id_talhao_unico, data_aplicacao, tipo_insumo, quantidade, observacoes
                   FROM REGISTROS_INSUMOS"""
        cursor.execute(sql)
        cols = [desc[0].lower() for desc in cursor.description]
        for row in cursor.fetchall():
             row_dict = dict(zip(cols, row))
             if isinstance(row_dict.get('data_aplicacao'), datetime.datetime): row_dict['data_aplicacao'] = row_dict['data_aplicacao'].date()
             insumos.append(row_dict)
        return insumos
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao carregar insumos: {e}"); return []
    finally:
        if cursor: cursor.close()

def carregar_status_certificacao(conexao):
    """Carrega status de certificação do Oracle."""
    if not conexao or cx_Oracle is None: return {}
    status = {}
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = "SELECT id_produtor, certificado, etapa_documentacao, etapa_inspecao, etapa_aprovacao FROM STATUS_CERTIFICACAO"
        cursor.execute(sql)
        for row in cursor.fetchall():
            status[row[0]] = {"certificado": bool(row[1]), "etapas": {"Documentação": bool(row[2]), "Inspeção": bool(row[3]), "Aprovação": bool(row[4])}}
        return status
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao carregar certificação: {e}"); return {}
    finally:
        if cursor: cursor.close()

def carregar_demandas(conexao):
    """Carrega dados de demandas do Oracle."""
    if not conexao or cx_Oracle is None: return []
    demandas = []
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = """SELECT id_demanda, cultura, quantidade, unidade_medida, data_necessidade, observacoes, registrado_em
                   FROM DEMANDAS ORDER BY data_necessidade"""
        cursor.execute(sql)
        cols = [desc[0].lower() for desc in cursor.description]
        for row in cursor.fetchall():
            row_dict = dict(zip(cols, row))
            
            # Converte datas Oracle para date objects
            for key in ['data_necessidade', 'registrado_em']:
                if isinstance(row_dict.get(key), datetime.datetime):
                    row_dict[key] = row_dict[key].date()
            demandas.append(row_dict)
        return demandas
    except cx_Oracle.DatabaseError as e: registrar_erro(f"Erro Oracle ao carregar demandas: {e}"); return []
    finally:
        if cursor: cursor.close()