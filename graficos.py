"""Gráficos de gestão com matplotlib (exibidos na tela e salvos em PNG)."""

import matplotlib.pyplot as plt
from persistencia import caminho_arquivo


def _finalizar(figura, nome_arquivo, mostrar):
    """Salva a figura em data/, mostra na tela (se pedido) e a fecha."""
    caminho = caminho_arquivo(nome_arquivo)
    figura.savefig(caminho, dpi=120, bbox_inches="tight")
    if mostrar:
        plt.show()
    plt.close(figura)
    return caminho


def grafico_posicao_estoque(cadastro_itens, estoque, mostrar=True):
    """Barras: saldo atual x estoque de segurança de cada item."""
    itens = cadastro_itens.listar()
    posicoes = range(len(itens))
    largura = 0.4

    figura, eixo = plt.subplots(figsize=(11, 5))
    eixo.bar(
        [p - largura / 2 for p in posicoes],
        [estoque.saldo(i.codigo) for i in itens],
        largura, label="Saldo atual",
    )
    eixo.bar(
        [p + largura / 2 for p in posicoes],
        [i.estoque_seguranca for i in itens],
        largura, label="Estoque de segurança",
    )
    eixo.set_xticks(list(posicoes))
    eixo.set_xticklabels([i.codigo for i in itens], rotation=60)
    eixo.set_ylabel("Quantidade")
    eixo.set_title("Posição de estoque: saldo x estoque de segurança")
    eixo.legend()
    return _finalizar(figura, "grafico_posicao_estoque.png", mostrar)


def grafico_estoque_projetado(registro, estoque_seguranca, mostrar=True):
    """Linha: estoque projetado do item nas semanas do MRP."""
    semanas = list(range(1, len(registro["estoque_projetado"]) + 1))

    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.plot(semanas, registro["estoque_projetado"], marker="o",
              label="Estoque projetado")
    eixo.axhline(estoque_seguranca, color="red", linestyle="--",
                 label="Estoque de segurança")
    eixo.set_xlabel("Semana")
    eixo.set_ylabel("Quantidade")
    eixo.set_title(f"Estoque projetado - {registro['codigo']}")
    eixo.legend()
    nome = f"grafico_estoque_projetado_{registro['codigo']}.png"
    return _finalizar(figura, nome, mostrar)


def grafico_ordens_por_semana(gerenciador_ordens, semanas, mostrar=True):
    """Barras empilhadas: OP e OC por semana de entrega."""
    producao = [0] * semanas
    compra = [0] * semanas
    for ordem in gerenciador_ordens.ordens:
        if ordem.status == "ENCERRADA":
            continue
        if 1 <= ordem.semana_entrega <= semanas:
            lista = producao if ordem.tipo == "OP" else compra
            lista[ordem.semana_entrega - 1] += 1

    eixo_x = list(range(1, semanas + 1))
    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.bar(eixo_x, producao, label="Ordens de produção (OP)")
    eixo.bar(eixo_x, compra, bottom=producao, label="Ordens de compra (OC)")
    eixo.set_xlabel("Semana de entrega")
    eixo.set_ylabel("Número de ordens")
    eixo.set_title("Ordens por semana de entrega")
    eixo.legend()
    return _finalizar(figura, "grafico_ordens_por_semana.png", mostrar)


def grafico_carga_capacidade(centro, carga, mostrar=True):
    """Barras: carga x capacidade do centro, destacando as sobrecargas."""
    semanas = list(range(1, len(carga) + 1))
    cores = [
        "red" if horas > centro.capacidade_horas else "steelblue"
        for horas in carga
    ]

    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.bar(semanas, carga, color=cores, label="Carga (h)")
    eixo.axhline(centro.capacidade_horas, color="black", linestyle="--",
                 label="Capacidade (h/semana)")
    eixo.set_xlabel("Semana")
    eixo.set_ylabel("Horas")
    eixo.set_title(f"Carga x capacidade - {centro.codigo} {centro.descricao}")
    eixo.legend()
    nome = f"grafico_carga_{centro.codigo}.png"
    return _finalizar(figura, nome, mostrar)
