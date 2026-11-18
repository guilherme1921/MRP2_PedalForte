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

    def kardex(self, codigo):
        """Lista os movimentos de um item, em ordem de registro."""
        return [m for m in self.movimentos if m["codigo"] == codigo]

    def abaixo_da_seguranca(self, codigo):
        """True se o saldo está abaixo do estoque de segurança (RF05)."""
        item = self.cadastro.buscar(codigo)
        return self.saldo(codigo) < item.estoque_seguranca

def imprimir_kardex(estoque, codigo):
    item = estoque.cadastro.buscar(codigo)
    print(f"\nKARDEX - {codigo} {item.descricao} ({item.unidade})")
    print(f"{'Data':<12} {'Tipo':<8} {'Qtde':>8} {'Saldo':>8}  Documento")
    for m in estoque.kardex(codigo):
        qtd = float(m["quantidade"])
        print(f"{m['data']:<12} {m['tipo']:<8} {qtd:>+8g} "
              f"{float(m['saldo']):>8g}  {m['documento']}")
    saldo = estoque.saldo(codigo)
    print(f"\nSaldo atual: {saldo:g} {item.unidade}")
    if estoque.abaixo_da_seguranca(codigo):
        print(f"ALERTA: saldo ({saldo:g} {item.unidade}) abaixo do estoque "
              f"de segurança ({item.estoque_seguranca:g} {item.unidade}).")

def tela_movimentar(estoque):
    from utils import ler_float, ler_texto
    codigo = ler_texto("Código do item: ").upper()
    if estoque.cadastro.buscar(codigo) is None:
        print(f"ERRO: item {codigo} não encontrado.")
        return
    letra = ler_texto("Tipo [E]ntrada [S]aída [A]juste: ").upper()
    tipos = {"E": "ENTRADA", "S": "SAIDA", "A": "AJUSTE"}
    if letra not in tipos:
        print("ERRO: tipo inválido.")
        return
    tipo = tipos[letra]
    if tipo == "AJUSTE":
        quantidade = ler_float("Quantidade (negativa para reduzir): ",
                               minimo=-1e12)
    else:
        quantidade = ler_float("Quantidade: ", minimo=0.0001)
    documento = ler_texto("Documento/motivo: ")
    try:
        estoque.movimentar(codigo, tipo, quantidade, documento)
        print(f"Movimento registrado. Saldo atual: {estoque.saldo(codigo):g}")
    except ValueError as erro:
        print(f"ERRO: {erro}. Operação cancelada.")


def tela_kardex(estoque):
    from utils import ler_texto
    codigo = ler_texto("Código do item: ").upper()
    if estoque.cadastro.buscar(codigo) is None:
        print(f"ERRO: item {codigo} não encontrado.")
        return
    imprimir_kardex(estoque, codigo)


def menu_estoque(estoque):
    """Submenu de estoque, chamado pelo menu principal."""
    while True:
        print("\n--- ESTOQUE ---")
        print("1. Movimentar  2. Saldo e kardex  0. Voltar")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            tela_movimentar(estoque)
        elif opcao == "2":
            tela_kardex(estoque)
        elif opcao == "0":
            return
        else:
            print("ERRO: opção inválida.")


if __name__ == "__main__":
    from itens import CadastroItens
    menu_estoque(Estoque(CadastroItens()))