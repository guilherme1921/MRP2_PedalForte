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