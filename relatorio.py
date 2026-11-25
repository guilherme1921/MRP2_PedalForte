"""Exportação de relatórios em CSV (posição de estoque e ordens)."""

from persistencia import salvar_csv
from utils import formatar_numero

CAMPOS_ESTOQUE = [
    "codigo", "descricao", "tipo", "unidade",
    "saldo", "estoque_seguranca", "situacao",
]
CAMPOS_ORDENS = [
    "ordem", "tipo", "item", "quantidade",
    "semana_liberacao", "semana_entrega", "status",
]


def exportar_posicao_estoque(cadastro_itens, estoque, arquivo="posicao_estoque.csv"):
    """RF14: grava o saldo de cada item e se está abaixo do estoque de segurança."""
    linhas = []
    for item in cadastro_itens.listar():
        saldo = estoque.saldo(item.codigo)
        abaixo = saldo < item.estoque_seguranca
        linhas.append(
            {
                "codigo": item.codigo,
                "descricao": item.descricao,
                "tipo": item.tipo,
                "unidade": item.unidade,
                "saldo": formatar_numero(saldo),
                "estoque_seguranca": formatar_numero(item.estoque_seguranca),
                "situacao": "ABAIXO DO ESTOQUE DE SEGURANCA" if abaixo else "OK",
            }
        )
    salvar_csv(arquivo, CAMPOS_ESTOQUE, linhas)
    return len(linhas)


def exportar_ordens(gerenciador_ordens, arquivo="ordens.csv"):
    """RF14: grava a lista de ordens em CSV."""
    linhas = []
    for ordem in gerenciador_ordens.listar():
        linhas.append(
            {
                "ordem": ordem.id,
                "tipo": ordem.tipo,
                "item": ordem.codigo_item,
                "quantidade": formatar_numero(ordem.quantidade),
                "semana_liberacao": ordem.semana_liberacao,
                "semana_entrega": ordem.semana_entrega,
                "status": ordem.status,
            }
        )
    salvar_csv(arquivo, CAMPOS_ORDENS, linhas)
    return len(linhas)
