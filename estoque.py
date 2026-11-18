"""Movimentações de estoque, saldo e kardex - RF04, RF05, RN02, RN10."""

from persistencia import carregar_csv, salvar_csv
from utils import data_hoje

ARQUIVO = "movimentos.csv"
CAMPOS = ["data", "codigo", "tipo", "quantidade", "saldo", "documento"]
TIPOS = ("ENTRADA", "SAIDA", "AJUSTE")


class Estoque:
    """Guarda o kardex (lista de movimentos). O saldo é sempre o do último
    movimento do item. Movimentos nunca são excluídos (RN10)."""

    def __init__(self, cadastro_itens):
        self.cadastro = cadastro_itens
        self.movimentos = []
        self.carregar()

    def carregar(self):
        self.movimentos = carregar_csv(ARQUIVO)

    def salvar(self):
        salvar_csv(ARQUIVO, self.movimentos, CAMPOS)

    def saldo(self, codigo):
        """Saldo atual do item: o saldo do último movimento dele."""
        for mov in reversed(self.movimentos):
            if mov["codigo"] == codigo:
                return float(mov["saldo"])
        return 0.0

    def movimentar(self, codigo, tipo, quantidade, documento, data=None):
        """Registra um movimento e atualiza o saldo.
        ENTRADA soma, SAIDA subtrai, AJUSTE aceita valor positivo ou negativo."""
        if self.cadastro.buscar(codigo) is None:
            raise ValueError(f"item {codigo} não encontrado")
        if tipo not in TIPOS:
            raise ValueError("tipo inválido (use ENTRADA, SAIDA ou AJUSTE)")
        if quantidade == 0:
            raise ValueError("a quantidade não pode ser zero")
        if tipo != "AJUSTE" and quantidade < 0:
            raise ValueError("a quantidade deve ser positiva")

        saldo_atual = self.saldo(codigo)
        if tipo == "ENTRADA":
            variacao = quantidade
        elif tipo == "SAIDA":
            variacao = -quantidade
        else:
            variacao = quantidade

        novo_saldo = saldo_atual + variacao
        if novo_saldo < 0:  # RN02
            raise ValueError(
                f"saldo insuficiente (saldo atual: {saldo_atual:g})"
            )

        self.movimentos.append({
            "data": data or data_hoje(),
            "codigo": codigo,
            "tipo": tipo,
            "quantidade": f"{variacao:g}",
            "saldo": f"{novo_saldo:g}",
            "documento": documento,
        })
        self.salvar()