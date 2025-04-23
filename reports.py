import datetime 
from collections import defaultdict
import config 
import database 
from utils import registrar_erro, formatar_data_br 
from crud_operations import selecionar_plantio 


cx_Oracle = config.cx_Oracle

def visualizar_historico_rotacao(conexao, id_produtor):
    """Mostra o histórico de culturas plantadas em um talhão (lendo do Oracle)."""
    from crud_operations import selecionar_talhao # Import local para evitar ciclo
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return
    print("\n--- Histórico de Rotação de Culturas ---")
    id_talhao_produtor, id_talhao_unico = selecionar_talhao(conexao, id_produtor)
    if not id_talhao_unico: return

    plantios = database.carregar_plantios_produtos(conexao) # Carrega do Oracle
    historico = [p for p in plantios if p.get("id_talhao_unico") == id_talhao_unico and p.get("data_plantio")]
    historico.sort(key=lambda x: x.get("data_plantio", datetime.date.min), reverse=True)

    if not historico: print(f"Nenhum histórico encontrado para o talhão '{id_talhao_produtor}'."); return

    print(f"\nHistórico para Talhão '{id_talhao_produtor}':")
    print("-" * 65)
    print(f"{'Data Plantio':<15} {'Cultura Plantada':<20} {'Cultura Anterior':<20} {'Status'}")
    print("-" * 65)
    for item in historico:
        print(f"{formatar_data_br(item.get('data_plantio')):<15} {item.get('cultura','N/A'):<20} {item.get('cultura_anterior', 'N/A'):<20} {item.get('status','N/A')}")
    print("-" * 65)

def visualizar_calendario_colheitas(conexao):
    """Mostra um calendário simples de colheitas previstas (lendo do Oracle)."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return
    print("\n--- Calendário de Colheitas Previstas ---")
    plantios = database.carregar_plantios_produtos(conexao) # Carrega do Oracle
    produtores = database.carregar_produtores_talhoes(conexao)
    plantios_planejados = []
    for p in plantios:
        if p.get("status") == 'Planejado' and isinstance(p.get("data_prevista_colheita"), datetime.date):
             id_prod = p.get("id_produtor")
             nome_prod = produtores.get(id_prod, {}).get("nome", "Desconhecido")
             plantios_planejados.append({
                 "data": p["data_prevista_colheita"],
                 "cultura": p.get("cultura"),
                 "produtor": nome_prod })
    plantios_planejados.sort(key=lambda x: x["data"]) # Ordena por data

    if not plantios_planejados: print("Nenhuma colheita prevista encontrada."); return

    colheitas_por_mes = defaultdict(list)
    for p in plantios_planejados: colheitas_por_mes[p["data"].strftime("%Y-%m")].append(p)

    print("\nColheitas Planejadas por Mês:")
    for mes_ano in sorted(colheitas_por_mes.keys()):
        try: nome_mes_ano = datetime.datetime.strptime(mes_ano, "%Y-%m").strftime("%B/%Y") # Tenta formatar mês
        except ValueError: nome_mes_ano = mes_ano # Fallback
        print(f"\n--- {nome_mes_ano.capitalize()} ---")
        colheitas_por_mes[mes_ano].sort(key=lambda x: x["data"]) # Ordena dentro do mês
        for item in colheitas_por_mes[mes_ano]:
            print(f"  - {item['data'].strftime('%d/%m')}: {item['cultura']} (Produtor: {item['produtor']})")
    print("\n" + "-"*35)

def buscar_produtos_mercado(conexao):
    """Simula a visão de um comprador buscando produtos (lendo do Oracle)."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return
    print("\n--- Mercado Agrorgânica (Oferta Disponível/Prevista) ---") # Nome atualizado
    resultados = []
    plantios_db = database.carregar_plantios_produtos(conexao)
    produtores_db = database.carregar_produtores_talhoes(conexao)
    cert_db = database.carregar_status_certificacao(conexao)

    for p in plantios_db:
        if p.get('status') in ['Disponível', 'Planejado']:
            id_produtor = p.get('id_produtor')
            nome_produtor = produtores_db.get(id_produtor, {}).get('nome', 'Desconhecido')
            certificado = cert_db.get(id_produtor, {}).get('certificado', False)
            data_ref = p.get('data_colheita_real') if p.get('status') == 'Disponível' else p.get('data_prevista_colheita')
            data_ref_str = formatar_data_br(data_ref)
            # Correção Quantidade: Mostrar '---' se Planejado, ou a qtd/N/A se Disponível
            qtd_val = p.get('quantidade_colhida')
            qtd_str = '---' if p.get('status') == 'Planejado' else (str(qtd_val) if qtd_val is not None else 'N/A')
            unid_str = p.get('unidade_medida', '') if p.get('status') == 'Disponível' and qtd_val is not None else ''


            resultados.append({
                "id_plantio": p.get('id_plantio', 'N/A'), "cultura": p.get('cultura', 'N/A'),
                "status": p.get('status', 'N/A'), "data_ref": data_ref_str, "qtd": qtd_str, "unid": unid_str,
                "nome_produtor": nome_produtor, "certificado": certificado })

    if not resultados: print("Nenhum produto disponível ou plantio previsto encontrado."); input("..."); return

    print("Ofertas Disponíveis e Plantios Futuros:")
    id_width = 37 # Largura para UUID
    other_widths = [15, 12, 15, 10, 5, 20, 12]
    header_format = f"{{:<{id_width}}} {{:<{other_widths[0]}}} {{:<{other_widths[1]}}} {{:<{other_widths[2]}}} {{:<{other_widths[3]}}} {{:<{other_widths[4]}}} {{:<{other_widths[5]}}} {{:<{other_widths[6]}}}"
    total_width = id_width + sum(other_widths) + (len(other_widths))

    print("-" * total_width)
    print(header_format.format('ID Lote/Plantio', 'Cultura', 'Status', 'Prev./Real Colh', 'Qtd.', 'Unid.', 'Produtor', 'Certificado?'))
    print("-" * total_width)

    resultados.sort(key=lambda x: datetime.datetime.strptime(x["data_ref"], '%d/%m/%Y') if x["data_ref"] != 'N/A' else datetime.datetime.min)
    for r in resultados:
        status_cert_str = "Sim" if r["certificado"] else "Não"
        print(header_format.format(
            r['id_plantio'], r['cultura'], r['status'], r['data_ref'],
            r['qtd'], r['unid'], r['nome_produtor'], status_cert_str
        ))
    print("-" * total_width); input("\nPressione Enter para voltar...")

def gerar_relatorio_rastreabilidade(conexao):
    """Gera um relatório de rastreabilidade simple (lendo do Oracle)."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return
    print("\n--- Gerar Relatório de Rastreabilidade ---")

    # Pede produtor primeiro para filtrar a lista de plantios
    from crud_operations import selecionar_produtor
    id_produtor_selecionado = selecionar_produtor(conexao)
    if not id_produtor_selecionado: print("Nenhum produtor selecionado."); return

    # Permite selecionar qualquer plantio do produtor para o relatório
    id_plantio_selecionado = selecionar_plantio(conexao, id_produtor_selecionado, status_permitidos=['Planejado', 'Disponível', 'Vendido', 'Cancelado'])
    if not id_plantio_selecionado: print("Nenhum plantio selecionado."); return

    # Carrega dados necessários
    plantios_db = database.carregar_plantios_produtos(conexao)
    produtores_db = database.carregar_produtores_talhoes(conexao)
    insumos_db = database.carregar_registros_insumos(conexao)
    cert_db = database.carregar_status_certificacao(conexao)

    plantio_encontrado = next((p for p in plantios_db if p.get('id_plantio') == id_plantio_selecionado), None)
    if not plantio_encontrado: print(f"ID '{id_plantio_selecionado}' não encontrado (erro interno)."); return

    id_produtor = plantio_encontrado.get('id_produtor') # Confirma o ID do produtor do plantio
    id_talhao_unico = plantio_encontrado.get('id_talhao_unico')
    dados_produtor = produtores_db.get(id_produtor, {})
    dados_cert = cert_db.get(id_produtor, {})
    id_talhao_produtor = 'N/A'; dados_talhao = {}
    for id_t_prod, dados_t in dados_produtor.get('talhoes', {}).items():
        if dados_t.get('id_talhao_unico') == id_talhao_unico:
            dados_talhao = dados_t; id_talhao_produtor = id_t_prod; break

    # Filtra insumos relevantes
    insumos_relevantes = []
    data_limite = plantio_encontrado.get('data_colheita_real') or datetime.date.today()
    insumos_talhao = [i for i in insumos_db if i.get('id_talhao_unico') == id_talhao_unico]
    for insumo in insumos_talhao:
        data_app = insumo.get('data_aplicacao')
        if isinstance(data_app, datetime.date) and data_app <= data_limite:
            insumo_copy = insumo.copy()
            insumo_copy['data_aplicacao_br'] = formatar_data_br(data_app)
            insumos_relevantes.append(insumo_copy)
    insumos_relevantes.sort(key=lambda x: x.get('data_aplicacao', datetime.date.min), reverse=True)

    # Monta o relatório
    nome_arquivo_relatorio = f"rastreabilidade_{id_plantio_selecionado[:8]}.txt"
    try:
        with open(nome_arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write("--- Relatório de Rastreabilidade Simplificado ---\n\n")
            f.write(f"ID Lote/Plantio: {plantio_encontrado.get('id_plantio')}\n")
            f.write(f"Cultura: {plantio_encontrado.get('cultura', 'N/A')}\n")
            f.write(f"Status Atual: {plantio_encontrado.get('status', 'N/A')}\n")
            if plantio_encontrado.get('status') == 'Disponível':
                f.write(f"Data da Colheita: {formatar_data_br(plantio_encontrado.get('data_colheita_real'))}\n")
                f.write(f"Quantidade Colhida: {plantio_encontrado.get('quantidade_colhida', 'N/A')} {plantio_encontrado.get('unidade_medida', '')}\n")
            else: f.write(f"Data Prev. Colheita: {formatar_data_br(plantio_encontrado.get('data_prevista_colheita'))}\n")
            f.write(f"Data do Plantio: {formatar_data_br(plantio_encontrado.get('data_plantio'))}\n")
            f.write("-" * 30 + "\nDados do Produtor:\n")
            f.write(f"  ID: {id_produtor}\n  Nome: {dados_produtor.get('nome', 'N/A')}\n")
            f.write(f"  Localização: {dados_produtor.get('localizacao', 'N/A')}\n  Associação: {dados_produtor.get('associacao', 'Nenhuma')}\n")
            f.write(f"  Certificado Orgânico: {'Sim' if dados_cert.get('certificado', False) else 'Não'}\n")
            f.write("-" * 30 + "\nDados do Talhão de Origem:\n")
            f.write(f"  ID Talhão (Produtor): {id_talhao_produtor}\n  ID Único (Sistema): {id_talhao_unico}\n")
            f.write(f"  Tamanho: {dados_talhao.get('tamanho_ha', 'N/A')} ha\n  Tipo de Solo: {dados_talhao.get('tipo_solo', 'N/A')}\n")
            f.write("-" * 30 + "\nHistórico Recente de Insumos Orgânicos (Neste Talhão):\n")
            if insumos_relevantes:
                for insumo in insumos_relevantes[:5]:
                    f.write(f"  - {insumo['data_aplicacao_br']}: {insumo.get('tipo_insumo')} ({insumo.get('quantidade', 'N/A')})\n")
            else: f.write("  Nenhum registro de insumo encontrado.\n")
            f.write("-" * 30 + "\nObservações do Plantio: {plantio_encontrado.get('observacoes', 'Nenhuma')}\n\n")
            f.write(f"Relatório gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        print(f"Relatório salvo em '{nome_arquivo_relatorio}'.")
    except IOError as e: registrar_erro(f"Erro ao gerar relatório: {e}")
    except Exception as e: registrar_erro(f"Erro inesperado no relatório: {e}")

# --- NOVA FUNÇÃO ---
def listar_demandas(conexao):
    """Lista as demandas registradas."""
    if not conexao or cx_Oracle is None: registrar_erro("Conexão Oracle inválida."); return
    print("\n--- Demandas Registradas ---")
    demandas = database.carregar_demandas(conexao) # Carrega do Oracle
    if not demandas: print("Nenhuma demanda registrada."); return

    print("-" * 80)
    print(f"{'ID Demanda':<12} {'Cultura':<20} {'Qtd.':<10} {'Unid.':<10} {'Necessidade':<15} {'Registrado em':<15}")
    print("-" * 80)
    for d in demandas:
        print(f"{d['id_demanda'][:8]:<12} {d['cultura']:<20} {d['quantidade']:<10} {d['unidade_medida']:<10} {formatar_data_br(d.get('data_necessidade')):<15} {formatar_data_br(d.get('registrado_em')):<15}")
    print("-" * 80)