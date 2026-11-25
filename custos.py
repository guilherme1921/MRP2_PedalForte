"""Custo padrão dos itens fabricados: materiais + mão de obra."""

from utils import formatar_fixo, formatar_moeda, formatar_numero


def custo_mao_de_obra(codigo, capacidade):
    """Devolve tempo x custo-hora do roteiro do item (0 se não houver roteiro)."""
    roteiro = capacidade.obter_roteiro(codigo)
    if roteiro is None:
        return 0.0
    centro = capacidade.obter_centro(roteiro["centro"])
    return roteiro["tempo"] * centro.custo_hora


def custo_padrao(codigo, cadastro_itens, estrutura, capacidade):
    """RF13: custo padrão do item, percorrendo a estrutura de forma recursiva."""
    item = cadastro_itens.obter(codigo)
    if item.tipo == "MP":
        return item.custo_unitario

    materiais = 0.0
    for filho, quantidade in estrutura.obter_componentes(item.codigo).items():
        custo_filho = custo_padrao(filho, cadastro_itens, estrutura, capacidade)
        materiais += quantidade * custo_filho
    return materiais + custo_mao_de_obra(item.codigo, capacidade)


def relatorio_custo(codigo, cadastro_itens, estrutura, capacidade):
    """Gera o texto do custo padrão de um item fabricado (tela 6.7)."""
    item = cadastro_itens.obter(codigo)
    if item.tipo == "MP":
        raise ValueError("Matéria-prima não tem custo padrão: use o custo unitário.")

    linhas = [
        f"CUSTO PADRAO - {item.codigo} {item.descricao}",
        f"{'Item':<8}{'Descricao':<30}{'Qtde':>8}{'Custo un.':>12}{'Total':>12}",
    ]
    total = 0.0
    for filho, quantidade in estrutura.obter_componentes(item.codigo).items():
        custo_filho = custo_padrao(filho, cadastro_itens, estrutura, capacidade)
        subtotal = quantidade * custo_filho
        total += subtotal
        descricao = cadastro_itens.obter(filho).descricao
        linhas.append(
            f"{filho:<8}{descricao:<30}{formatar_numero(quantidade):>8}"
            f"{formatar_fixo(custo_filho):>12}{formatar_fixo(subtotal):>12}"
        )

    roteiro = capacidade.obter_roteiro(item.codigo)
    if roteiro is not None:
        centro = capacidade.obter_centro(roteiro["centro"])
        mao_de_obra = custo_mao_de_obra(item.codigo, capacidade)
        total += mao_de_obra
        linhas.append(
            f"{'':<8}{'Mao de obra ' + centro.codigo:<30}"
            f"{formatar_numero(roteiro['tempo']) + ' h':>8}"
            f"{formatar_fixo(centro.custo_hora):>12}"
            f"{formatar_fixo(mao_de_obra):>12}"
        )

    linhas.append("-" * 70)
    linhas.append(f"{'CUSTO PADRAO TOTAL':<58}{formatar_moeda(total):>12}")
    return "\n".join(linhas)
