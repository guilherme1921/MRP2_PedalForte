"""Cadastro de itens (PA, SA e MP) - RF02, RN01."""

from persistencia import carregar_json, salvar_json
from utils import (codigo_valido, formatar_moeda, ler_float, ler_inteiro,
                   ler_texto)

ARQUIVO = "itens.json"
CAMPOS_ALTERAVEIS = {
    "1": ("descricao", "Descrição"),
    "2": ("unidade", "Unidade de medida"),
    "3": ("custo_unitario", "Custo unitário"),
    "4": ("lead_time", "Lead time (semanas)"),
    "5": ("estoque_seguranca", "Estoque de segurança"),
    "6": ("lote_minimo", "Lote mínimo"),
}


class Item:
    """Representa um item: produto acabado, semiacabado ou matéria-prima."""

    def __init__(self, codigo, descricao, unidade, custo_unitario,
                 lead_time, estoque_seguranca, lote_minimo):
        self.codigo = codigo
        self.descricao = descricao
        self.unidade = unidade
        self.custo_unitario = custo_unitario
        self.lead_time = lead_time
        self.estoque_seguranca = estoque_seguranca
        self.lote_minimo = lote_minimo

    @property
    def tipo(self):
        """O tipo (PA, SA ou MP) vem do prefixo do código."""
        return self.codigo[:2]

    @property
    def fabricado(self):
        """PA e SA são fabricados; MP é comprada."""
        return self.tipo in ("PA", "SA")

    def to_dict(self):
        return {
            "codigo": self.codigo,
            "descricao": self.descricao,
            "unidade": self.unidade,
            "custo_unitario": self.custo_unitario,
            "lead_time": self.lead_time,
            "estoque_seguranca": self.estoque_seguranca,
            "lote_minimo": self.lote_minimo,
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(**dados)


class CadastroItens:
    """Guarda todos os itens em um dicionário {código: Item} e persiste em JSON."""

    def __init__(self):
        self.itens = {}
        self.carregar()

    def carregar(self):
        dados = carregar_json(ARQUIVO)
        self.itens = {cod: Item.from_dict(d) for cod, d in dados.items()}

    def salvar(self):
        salvar_json(ARQUIVO, {c: i.to_dict() for c, i in self.itens.items()})

    def cadastrar(self, item):
        if not codigo_valido(item.codigo):
            raise ValueError("código inválido; use o formato Tipo-Número (ex.: PA-001)")
        if item.codigo in self.itens:
            raise ValueError(f"o código {item.codigo} já está cadastrado")
        self.itens[item.codigo] = item
        self.salvar()

    def buscar(self, codigo):
        return self.itens.get(codigo)

    def listar(self):
        return [self.itens[c] for c in sorted(self.itens)]

    def alterar(self, codigo, campo, valor):
        item = self.buscar(codigo)
        if item is None:
            raise ValueError(f"item {codigo} não encontrado")
        setattr(item, campo, valor)
        self.salvar()


def tela_cadastrar(cadastro):
    codigo = ler_texto("Código (ex.: PA-001): ").upper()
    if not codigo_valido(codigo):
        print("ERRO: use o formato Tipo-Número (PA-001, SA-020, MP-201).")
        return
    if cadastro.buscar(codigo):
        print(f"ERRO: o código {codigo} já existe.")
        return
    item = Item(
        codigo=codigo,
        descricao=ler_texto("Descrição: "),
        unidade=ler_texto("Unidade de medida (un, m, L...): "),
        custo_unitario=ler_float("Custo unitário: "),
        lead_time=ler_inteiro("Lead time (semanas): "),
        estoque_seguranca=ler_float("Estoque de segurança: "),
        lote_minimo=ler_float("Lote mínimo: "),
    )
    cadastro.cadastrar(item)
    print(f"Item {codigo} cadastrado ({item.tipo}).")


def tela_listar(cadastro):
    itens = cadastro.listar()
    if not itens:
        print("Nenhum item cadastrado.")
        return
    print(f"{'Código':<8} {'Descrição':<28} {'Un':<4} {'Custo':>12} "
          f"{'LT':>3} {'ES':>6} {'Lote':>6}")
    for i in itens:
        print(f"{i.codigo:<8} {i.descricao:<28} {i.unidade:<4} "
              f"{formatar_moeda(i.custo_unitario):>12} {i.lead_time:>3} "
              f"{i.estoque_seguranca:>6g} {i.lote_minimo:>6g}")


def tela_alterar(cadastro):
    codigo = ler_texto("Código do item a alterar: ").upper()
    if cadastro.buscar(codigo) is None:
        print(f"ERRO: item {codigo} não encontrado.")
        return
    for chave, (_, rotulo) in CAMPOS_ALTERAVEIS.items():
        print(f"  {chave}. {rotulo}")
    escolha = ler_texto("Campo a alterar: ")
    if escolha not in CAMPOS_ALTERAVEIS:
        print("ERRO: opção inválida.")
        return
    campo, rotulo = CAMPOS_ALTERAVEIS[escolha]
    if campo in ("descricao", "unidade"):
        valor = ler_texto(f"Novo valor de {rotulo}: ")
    elif campo == "lead_time":
        valor = ler_inteiro(f"Novo valor de {rotulo}: ")
    else:
        valor = ler_float(f"Novo valor de {rotulo}: ")
    cadastro.alterar(codigo, campo, valor)
    print("Item alterado.")


def menu_itens(cadastro):
    """Submenu de itens, que será chamado pelo menu principal."""
    while True:
        print("\n--- ITENS ---")
        print("1. Cadastrar  2. Listar  3. Alterar  0. Voltar")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            tela_cadastrar(cadastro)
        elif opcao == "2":
            tela_listar(cadastro)
        elif opcao == "3":
            tela_alterar(cadastro)
        elif opcao == "0":
            return
        else:
            print("ERRO: opção inválida.")


if __name__ == "__main__":
    menu_itens(CadastroItens())