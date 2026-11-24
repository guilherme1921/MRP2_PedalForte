"""Cálculo do Planejamento das Necessidades de Materiais (MRP)."""
import math

class MRP:
    """Calcula necessidades brutas, saldos projetados e necessidades líquidas por semana."""
    def __init__(self, cadastro_itens, estrutura, estoque, mps):
        """Inicializa o MRP com as dependências principais do sistema."""
        self.cadastro_itens = cadastro_itens
        self.estrutura = estrutura
        self.estoque = estoque
        self.mps = mps