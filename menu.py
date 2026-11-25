"""Menus e telas em modo texto. As classes levantam ValueError; as telas mostram."""

from datetime import datetime
from capacidade import CentroTrabalho
from custos import relatorio_custo
from itens import Item
import relatorios
from utils import (
    formatar_fixo, formatar_numero, ler_codigo, ler_float, ler_inteiro, ler_texto,
)

LARGURA = 50


def executar(tela, sistema):
    """Roda uma tela e mostra a mensagem se uma regra de negócio for violada."""
    try:
        tela(sistema)
    except ValueError as erro:
        print(f"ERRO: {erro}")


def executar_menu(titulo, opcoes, sistema, rotulo_saida="Voltar"):
    """Mostra um menu numerado e repete até o usuário escolher 0."""
    while True:
        print()
        print("=" * LARGURA)
        print(titulo.center(LARGURA))
        print("=" * LARGURA)
        for numero, (texto, _) in enumerate(opcoes, start=1):
            print(f" {numero}. {texto}")
        print(f" 0. {rotulo_saida}")
        print("-" * LARGURA)
        escolha = ler_inteiro(" Escolha uma opcao: ", 0)
        if escolha == 0:
            return
        if escolha > len(opcoes):
            print("ERRO: opção inexistente.")
            continue
        executar(opcoes[escolha - 1][1], sistema)
        sistema.salvar()


# ---------------------------------------------------------------- cadastros

def tela_listar_itens(sistema):
    """Lista todos os itens cadastrados."""
    itens = sistema.itens.listar()
    if not itens:
        print("Nenhum item cadastrado.")
        return
    print(f"{'Codigo':<8}{'Descricao':<28}{'Un':<4}{'Custo':>9}"
          f"{'LT':>4}{'ES':>8}{'Lote':>8}")
    for item in itens:
        print(f"{item.codigo:<8}{item.descricao:<28}{item.unidade:<4}"
              f"{formatar_fixo(item.custo_unitario):>9}{item.lead_time:>4}"
              f"{formatar_numero(item.estoque_seguranca):>8}"
              f"{formatar_numero(item.lote_minimo):>8}")


def tela_cadastrar_item(sistema):
    """RF02: lê os dados de um item novo e o cadastra."""
    codigo = ler_codigo(">> Codigo (ex.: PA-001): ")
    descricao = ler_texto(">> Descricao: ")
    unidade = ler_texto(">> Unidade de medida: ")
    custo = ler_float(">> Custo unitario (R$): ")
    lead_time = ler_inteiro(">> Lead time (semanas): ")
    seguranca = ler_float(">> Estoque de seguranca: ")
    lote = ler_float(">> Lote minimo: ", 0.001)
    item = Item(codigo, descricao, unidade, custo, lead_time, seguranca, lote)
    sistema.itens.cadastrar(item)
    print(f"Item {item.codigo} cadastrado como {item.tipo}.")


def tela_alterar_item(sistema):
    """RF02: altera um campo de um item existente."""
    codigo = ler_codigo(">> Codigo do item: ")
    item = sistema.itens.obter(codigo)
    print(f"Alterando {item.codigo} - {item.descricao}")
    print(" 1. Descricao  2. Unidade  3. Custo  4. Lead time"
          "  5. Estoque de seguranca  6. Lote minimo")
    campo = ler_inteiro(">> Campo a alterar: ", 1)
    if campo == 1:
        sistema.itens.alterar(codigo, descricao=ler_texto(">> Nova descricao: "))
    elif campo == 2:
        sistema.itens.alterar(codigo, unidade=ler_texto(">> Nova unidade: "))
    elif campo == 3:
        sistema.itens.alterar(codigo, custo_unitario=ler_float(">> Novo custo: "))
    elif campo == 4:
        sistema.itens.alterar(codigo, lead_time=ler_inteiro(">> Novo lead time: "))
    elif campo == 5:
        sistema.itens.alterar(
            codigo, estoque_seguranca=ler_float(">> Novo estoque de seguranca: "))
    elif campo == 6:
        sistema.itens.alterar(
            codigo, lote_minimo=ler_float(">> Novo lote minimo: ", 0.001))
    else:
        raise ValueError("campo inexistente.")
    print("Item alterado.")


def tela_adicionar_componente(sistema):
    """RF03: adiciona um componente à estrutura de um item pai."""
    pai = ler_codigo(">> Codigo do item pai: ")
    filho = ler_codigo(">> Codigo do componente: ")
    quantidade = ler_float(">> Quantidade por unidade do pai: ")
    sistema.estrutura.adicionar_componente(pai, filho, quantidade)
    print("Componente registrado na estrutura.")


def tela_remover_componente(sistema):
    """Remove um componente da estrutura de um item pai."""
    pai = ler_codigo(">> Codigo do item pai: ")
    filho = ler_codigo(">> Codigo do componente: ")
    sistema.estrutura.remover_componente(pai, filho)
    print("Componente removido.")


def tela_exibir_estrutura(sistema):
    """RF03: mostra a estrutura de um item de forma indentada, com os níveis."""
    codigo = ler_codigo(">> Codigo do produto: ")
    sistema.itens.obter(codigo)
    print()
    print(sistema.estrutura.formatar_arvore(codigo))


def tela_cadastrar_centro(sistema):
    """RF06: cadastra um centro de trabalho."""
    codigo = ler_texto(">> Codigo do centro (ex.: CT-01): ").upper()
    descricao = ler_texto(">> Descricao: ")
    capacidade = ler_float(">> Capacidade (h/semana): ", 0.1)
    custo_hora = ler_float(">> Custo-hora (R$): ")
    centro = CentroTrabalho(codigo, descricao, capacidade, custo_hora)
    sistema.capacidade.cadastrar_centro(centro)
    print(f"Centro {centro.codigo} cadastrado.")


def tela_listar_centros(sistema):
    """Lista os centros de trabalho e os roteiros cadastrados."""
    for centro in sistema.capacidade.listar_centros():
        print(f"{centro.codigo}  {centro.descricao:<24}"
              f"{formatar_fixo(centro.capacidade_horas, 1):>7} h/sem"
              f"   R$ {formatar_fixo(centro.custo_hora)}/h")
    print("\nRoteiros (item -> centro, h/un):")
    for codigo, roteiro in sorted(sistema.capacidade.roteiros.items()):
        print(f"  {codigo} -> {roteiro['centro']}, "
              f"{formatar_numero(roteiro['tempo'])} h/un")


def tela_definir_roteiro(sistema):
    """RF06: define o centro e o tempo por unidade de um item fabricado."""
    codigo = ler_codigo(">> Codigo do item fabricado: ")
    centro = ler_texto(">> Codigo do centro de trabalho: ").upper()
    tempo = ler_float(">> Tempo por unidade (h): ", 0.001)
    sistema.capacidade.definir_roteiro(codigo, centro, tempo)
    print("Roteiro registrado.")


def menu_cadastros(sistema):
    """Submenu de cadastros (RF02, RF03, RF06)."""
    opcoes = [
        ("Listar itens", tela_listar_itens),
        ("Cadastrar item", tela_cadastrar_item),
        ("Alterar item", tela_alterar_item),
        ("Adicionar componente a estrutura", tela_adicionar_componente),
        ("Remover componente da estrutura", tela_remover_componente),
        ("Exibir estrutura (arvore indentada)", tela_exibir_estrutura),
        ("Cadastrar centro de trabalho", tela_cadastrar_centro),
        ("Listar centros e roteiros", tela_listar_centros),
        ("Definir roteiro de um item", tela_definir_roteiro),
    ]
    executar_menu("CADASTROS", opcoes, sistema)


# ------------------------------------------------------------------ estoque

def tela_movimentar_estoque(sistema):
    """RF04: registra entrada, saída ou ajuste de estoque."""
    codigo = ler_codigo(">> Codigo do item: ")
    sistema.itens.obter(codigo)
    tipos = {"E": "ENTRADA", "S": "SAIDA", "A": "AJUSTE"}
    while True:
        letra = ler_texto(">> Tipo [E]ntrada [S]aida [A]juste: ").upper()[:1]
        if letra in tipos:
            break
        print("ERRO: digite E, S ou A.")
    if letra == "A":
        quantidade = ler_float(">> Quantidade (negativa para reduzir): ", -1e12)
    else:
        quantidade = ler_float(">> Quantidade: ")
    documento = ler_texto(">> Documento/motivo: ")
    movimento = sistema.estoque.movimentar(codigo, tipos[letra], quantidade, documento)
    print(f"Movimento registrado. Saldo atual: "
          f"{formatar_numero(movimento['saldo'])}")


def tela_kardex(sistema):
    """RF05: mostra o saldo e o kardex de um item, com alerta de segurança."""
    codigo = ler_codigo(">> Codigo do item: ")
    item = sistema.itens.obter(codigo)
    kardex = sistema.estoque.kardex(codigo)
    print(f"\nKARDEX - {item.codigo} {item.descricao} ({item.unidade})")
    print(f"{'Data':<12}{'Tipo':<9}{'Qtde':>8}{'Saldo':>8}  Documento")
    for mov in kardex["movimentos"]:
        print(f"{mov['data']:<12}{mov['tipo']:<9}"
              f"{mov['quantidade']:>+8g}{mov['saldo']:>8g}  {mov['documento']}")
    print(f"\nSaldo atual: {formatar_numero(kardex['saldo'])} {item.unidade}")
    if kardex["alerta_seguranca"]:
        print(f"ALERTA: saldo ({formatar_numero(kardex['saldo'])} {item.unidade}) "
              f"abaixo do estoque de seguranca "
              f"({formatar_numero(kardex['estoque_seguranca'])} {item.unidade}).")


def tela_posicao_estoque(sistema):
    """Mostra o saldo de todos os itens e sinaliza os abaixo da segurança."""
    print(f"{'Codigo':<8}{'Descricao':<28}{'Saldo':>10}{'Seguranca':>11}")
    for item in sistema.itens.listar():
        saldo = sistema.estoque.saldo(item.codigo)
        alerta = "  ALERTA" if saldo < item.estoque_seguranca else ""
        print(f"{item.codigo:<8}{item.descricao:<28}"
              f"{formatar_numero(saldo):>10}"
              f"{formatar_numero(item.estoque_seguranca):>11}{alerta}")


def menu_estoque(sistema):
    """Submenu de estoque (RF04, RF05)."""
    opcoes = [
        ("Movimentar (entrada, saida, ajuste)", tela_movimentar_estoque),
        ("Saldo e kardex de um item", tela_kardex),
        ("Posicao de estoque de todos os itens", tela_posicao_estoque),
    ]
    executar_menu("ESTOQUE", opcoes, sistema)


# ---------------------------------------------------------------------- MPS

def tela_exibir_mps(sistema):
    """Mostra a demanda semanal de cada PA no horizonte do MPS."""
    semanas = sistema.mps.semanas
    print(f"MPS - horizonte de {semanas} semanas")
    print(f"{'Item':<8}" + "".join(f"{'S' + str(s):>6}" for s in range(1, semanas + 1)))
    for item in sistema.itens.listar("PA"):
        demandas = [sistema.mps.obter_demanda(item.codigo, s)
                    for s in range(1, semanas + 1)]
        print(f"{item.codigo:<8}"
              + "".join(f"{formatar_numero(d):>6}" for d in demandas))


def tela_definir_demanda(sistema):
    """RF07: lança ou altera a demanda de um PA em uma semana."""
    codigo = ler_codigo(">> Codigo do PA: ")
    semana = ler_inteiro(f">> Semana (1 a {sistema.mps.semanas}): ", 1)
    quantidade = ler_float(">> Demanda (unidades): ")
    sistema.mps.definir_demanda(codigo, semana, quantidade)
    print("Demanda registrada.")


def tela_remover_demanda(sistema):
    """Remove o lançamento de demanda de um PA em uma semana."""
    codigo = ler_codigo(">> Codigo do PA: ")
    semana = ler_inteiro(">> Semana: ", 1)
    sistema.mps.remover_demanda(codigo, semana)
    print("Demanda removida.")


def menu_mps(sistema):
    """Submenu do Plano Mestre de Produção (RF07)."""
    opcoes = [
        ("Exibir plano", tela_exibir_mps),
        ("Lancar ou alterar demanda", tela_definir_demanda),
        ("Remover demanda", tela_remover_demanda),
    ]
    executar_menu("PLANO MESTRE DE PRODUCAO (MPS)", opcoes, sistema)


# ---------------------------------------------------------------- MRP/ordens

def imprimir_ordens(ordens):
    """Imprime a tabela de ordens (tela 6.5)."""
    print(f"{'Ordem':<9}{'Tipo':<5}{'Item':<8}{'Qtde':>7}  "
          f"{'Liberar':<8}{'Entregar':<9}Status")
    for ordem in ordens:
        print(f"{ordem.id:<9}{ordem.tipo:<5}{ordem.codigo_item:<8}"
              f"{formatar_numero(ordem.quantidade):>7}  "
              f"{'S' + str(ordem.semana_liberacao):<8}"
              f"{'S' + str(ordem.semana_entrega):<9}{ordem.status}")


def tela_executar_mrp(sistema):
    """RF08 e RF09: executa o MRP, gera as ordens e mostra registros de itens."""
    registros = sistema.mrp.calcular()
    criadas = sistema.ordens.gerar_do_mrp(registros)
    hoje = datetime.now().strftime("%d/%m/%Y")
    print(f"\nORDENS PLANEJADAS - execucao do MRP em {hoje}")
    imprimir_ordens(criadas)
    excecoes = sistema.ordens.mensagens_excecao()
    print(f"\n{len(criadas)} ordens geradas, {len(excecoes)} mensagens de excecao.")
    for mensagem in excecoes:
        print(f"  ! {mensagem}")

    while True:
        codigo = input("\nCodigo do item para ver o registro MRP "
                       "(ENTER para voltar): ").strip().upper()
        if not codigo:
            return
        if codigo not in registros:
            print("ERRO: item sem registro MRP.")
            continue
        print()
        print(sistema.mrp.formatar_registro(registros[codigo]))


def tela_ordens(sistema):
    """RF10 e RF11: lista as ordens e permite firmar, liberar e apontar."""
    acoes = {
        "F": sistema.ordens.firmar,
        "L": sistema.ordens.liberar,
        "A": sistema.ordens.apontar_producao,
        "R": sistema.ordens.receber_compra,
    }
    mostrar_todas = False
    while True:
        ordens = sistema.ordens.listar()
        if not mostrar_todas:
            ordens = [o for o in ordens if o.status != "ENCERRADA"]
        print()
        imprimir_ordens(ordens)
        for mensagem in sistema.ordens.mensagens_excecao():
            print(f"  ! {mensagem}")
        letra = ler_texto("[F] Firmar [L] Liberar [A] Apontar producao "
                          "[R] Receber compra\n[T] Alternar encerradas "
                          "[V] Voltar: ").upper()[:1]
        if letra == "V":
            return
        if letra == "T":
            mostrar_todas = not mostrar_todas
            continue
        if letra not in acoes:
            print("ERRO: opção inválida.")
            continue
        try:
            ordem = acoes[letra](ler_texto(">> Numero da ordem: "))
            print(f"OK: {ordem.id} agora esta {ordem.status}.")
            sistema.salvar()
        except ValueError as erro:
            print(f"ERRO: {erro}")


# ------------------------------------------------------------ CRP e custos

def tela_crp(sistema):
    """RF12: mostra a carga x capacidade de cada centro de trabalho."""
    for centro in sistema.capacidade.listar_centros():
        print()
        print(sistema.capacidade.formatar_crp(
            centro.codigo, sistema.ordens, sistema.mps.semanas))


def tela_custo(sistema):
    """RF13: mostra o custo padrão de um item fabricado."""
    codigo = ler_codigo(">> Codigo do item fabricado: ")
    print()
    print(relatorio_custo(codigo, sistema.itens, sistema.estrutura,
                          sistema.capacidade))


# ---------------------------------------------------- relatórios e gráficos

def _importar_graficos():
    """Importa o módulo de gráficos só quando necessário."""
    try:
        import graficos
    except ImportError:
        raise ValueError("matplotlib não instalado. Rode: pip install matplotlib")
    return graficos


def tela_exportar_estoque(sistema):
    """RF14: exporta a posição de estoque em CSV."""
    total = relatorios.exportar_posicao_estoque(sistema.itens, sistema.estoque)
    print(f"{total} itens exportados para data/posicao_estoque.csv")


def tela_exportar_ordens(sistema):
    """RF14: exporta a lista de ordens em CSV."""
    total = relatorios.exportar_ordens(sistema.ordens)
    print(f"{total} ordens exportadas para data/ordens.csv")


def tela_grafico_estoque(sistema):
    """RF16: gráfico de saldo x estoque de segurança."""
    graficos = _importar_graficos()
    caminho = graficos.grafico_posicao_estoque(sistema.itens, sistema.estoque)
    print(f"Gráfico salvo em {caminho}")


def tela_grafico_projetado(sistema):
    """RF16: gráfico do estoque projetado de um item."""
    graficos = _importar_graficos()
    codigo = ler_codigo(">> Codigo do item: ")
    item = sistema.itens.obter(codigo)
    registros = sistema.mrp.calcular()
    caminho = graficos.grafico_estoque_projetado(
        registros[codigo], item.estoque_seguranca)
    print(f"Gráfico salvo em {caminho}")


def tela_grafico_ordens(sistema):
    """RF16: gráfico de OP e OC por semana de entrega."""
    graficos = _importar_graficos()
    caminho = graficos.grafico_ordens_por_semana(
        sistema.ordens, sistema.mps.semanas)
    print(f"Gráfico salvo em {caminho}")


def tela_grafico_carga(sistema):
    """RF16: gráfico de carga x capacidade de um centro."""
    graficos = _importar_graficos()
    codigo = ler_texto(">> Codigo do centro (ex.: CT-03): ").upper()
    centro = sistema.capacidade.obter_centro(codigo)
    carga = sistema.capacidade.calcular_carga(
        sistema.ordens, sistema.mps.semanas)[centro.codigo]
    caminho = graficos.grafico_carga_capacidade(centro, carga)
    print(f"Gráfico salvo em {caminho}")


def menu_relatorios(sistema):
    """Submenu de relatórios CSV e gráficos (RF14, RF16)."""
    opcoes = [
        ("Exportar posicao de estoque (CSV)", tela_exportar_estoque),
        ("Exportar ordens (CSV)", tela_exportar_ordens),
        ("Grafico: saldo x estoque de seguranca", tela_grafico_estoque),
        ("Grafico: estoque projetado de um item", tela_grafico_projetado),
        ("Grafico: ordens por semana de entrega", tela_grafico_ordens),
        ("Grafico: carga x capacidade de um centro", tela_grafico_carga),
    ]
    executar_menu("RELATORIOS E GRAFICOS", opcoes, sistema)


def menu_principal(sistema):
    """RF01: menu principal do sistema."""
    opcoes = [
        ("Cadastros (itens, estrutura, centros, roteiros)", menu_cadastros),
        ("Estoque (movimentar, saldo, kardex)", menu_estoque),
        ("Plano Mestre de Producao (MPS)", menu_mps),
        ("Executar MRP", tela_executar_mrp),
        ("Ordens de producao e de compra", tela_ordens),
        ("Carga x capacidade (CRP)", tela_crp),
        ("Custo padrao dos produtos", tela_custo),
        ("Relatorios (exportar CSV) e graficos", menu_relatorios),
    ]
    executar_menu("MRP II - PEDAL FORTE BICICLETAS", opcoes, sistema, "Sair")
