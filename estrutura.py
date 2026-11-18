"""Estrutura de produto (BOM) em até 3 níveis - RF03, RN03."""

from persistencia import carregar_json, salvar_json

ARQUIVO = "estrutura.json"

# Regra RN03: quais tipos de componente cada tipo de pai pode ter.
COMPONENTES_PERMITIDOS = {
    "PA": ("SA", "MP"),
    "SA": ("MP",),
    "MP": (),
}


class Estrutura:
    """Guarda a BOM em um dicionário {pai: {filho: quantidade}}."""

    def __init__(self, cadastro_itens):
        self.cadastro = cadastro_itens
        self.bom = {}
        self.carregar()

    def carregar(self):
        self.bom = carregar_json(ARQUIVO)

    def salvar(self):
        salvar_json(ARQUIVO, self.bom)

    def adicionar_componente(self, pai, filho, quantidade):
        """Adiciona (ou atualiza) um componente no item pai, validando RN03."""
        item_pai = self.cadastro.buscar(pai)
        item_filho = self.cadastro.buscar(filho)
        if item_pai is None:
            raise ValueError(f"item pai {pai} não encontrado")
        if item_filho is None:
            raise ValueError(f"item componente {filho} não encontrado")
        if quantidade <= 0:
            raise ValueError("a quantidade deve ser maior que zero")
        if item_filho.tipo not in COMPONENTES_PERMITIDOS[item_pai.tipo]:
            raise ValueError(
                f"um {item_pai.tipo} não pode ter {item_filho.tipo} "
                f"como componente (RN03)"
            )
        self.bom.setdefault(pai, {})[filho] = quantidade
        self.salvar()

    def componentes(self, pai):
        """Devolve o dicionário {filho: quantidade} do pai (vazio se não tiver)."""
        return self.bom.get(pai, {})

    def imprimir_arvore(self, codigo, nivel=0, quantidade=None):
        """Imprime a BOM indentada, de forma recursiva, indicando o nível."""
        item = self.cadastro.buscar(codigo)
        recuo = "    " * nivel
        if nivel == 0:
            print(f"{codigo} {item.descricao}  [nível 0]")
        else:
            print(f"{recuo}└── {codigo} {item.descricao} ... "
                  f"{quantidade:g} {item.unidade}  [nível {nivel}]")
        for filho, qtd in self.componentes(codigo).items():
            self.imprimir_arvore(filho, nivel + 1, qtd)

def tela_adicionar(estrutura):
    from utils import ler_float, ler_texto
    pai = ler_texto("Código do item pai: ").upper()
    filho = ler_texto("Código do componente: ").upper()
    qtd = ler_float("Quantidade por unidade: ", minimo=0.0001)
    try:
        estrutura.adicionar_componente(pai, filho, qtd)
        print(f"Componente {filho} adicionado a {pai}.")
    except ValueError as erro:
        print(f"ERRO: {erro}.")


def tela_exibir(estrutura):
    from utils import ler_texto
    codigo = ler_texto("Código do produto: ").upper()
    if estrutura.cadastro.buscar(codigo) is None:
        print(f"ERRO: item {codigo} não encontrado.")
        return
    estrutura.imprimir_arvore(codigo)


def menu_estrutura(estrutura):
    """Submenu da BOM, chamado pelo menu principal."""
    while True:
        print("\n--- ESTRUTURA DE PRODUTO (BOM) ---")
        print("1. Adicionar componente  2. Exibir árvore  0. Voltar")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            tela_adicionar(estrutura)
        elif opcao == "2":
            tela_exibir(estrutura)
        elif opcao == "0":
            return
        else:
            print("ERRO: opção inválida.")


if __name__ == "__main__":
    from itens import CadastroItens
    menu_estrutura(Estrutura(CadastroItens()))