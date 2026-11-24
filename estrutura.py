"""Gerenciamento da estrutura de produto (BOM) e árvore indentada."""

from persistencia import carregar_json, salvar_json

COMPONENTES_PERMITIDOS = {
    "PA": {"SA", "MP"},
    "SA": {"MP"},
    "MP": set(),
}


class Estrutura:
    """Gerencia a estrutura de produto (BOM) em até três níveis."""

    def __init__(self, cadastro_itens=None, bom=None):
        """Inicializa a estrutura com dicionário aninhado {pai: {filho: qtd}}."""
        self.cadastro_itens = cadastro_itens
        self.bom = {}
        if bom:
            for pai, componentes in bom.items():
                for filho, quantidade in componentes.items():
                    self.adicionar_componente(pai, filho, quantidade)

    def adicionar_componente(self, codigo_pai, codigo_filho, quantidade):
        """Adiciona ou atualiza um componente na BOM respeitando a RN03."""
        pai = codigo_pai.strip().upper()
        filho = codigo_filho.strip().upper()
        qtd = float(quantidade)

        if not pai or not filho:
            raise ValueError("Os códigos do item pai e do componente são obrigatórios.")
        if pai == filho:
            raise ValueError("Um item não pode ser componente de si mesmo.")
        if qtd <= 0:
            raise ValueError("A quantidade do componente deve ser maior que zero.")

        if self.cadastro_itens is not None:
            item_pai = self.cadastro_itens.obter(pai)
            item_filho = self.cadastro_itens.obter(filho)
            tipos_validos = COMPONENTES_PERMITIDOS.get(item_pai.tipo, set())
            if item_filho.tipo not in tipos_validos:
                raise ValueError(
                    f"Componente {filho} ({item_filho.tipo}) não permitido para {pai} ({item_pai.tipo})."
                )
        else:
            tipo_pai = pai[:2]
            tipo_filho = filho[:2]
            tipos_validos = COMPONENTES_PERMITIDOS.get(tipo_pai, set())
            if tipo_filho not in tipos_validos:
                raise ValueError(
                    f"Componente {filho} ({tipo_filho}) não permitido para {pai} ({tipo_pai})."
                )

        if pai not in self.bom:
            self.bom[pai] = {}
        self.bom[pai][filho] = qtd

    def remover_componente(self, codigo_pai, codigo_filho):
        """Remove um componente específico da estrutura de um item pai."""
        pai = codigo_pai.strip().upper()
        filho = codigo_filho.strip().upper()
        if pai not in self.bom or filho not in self.bom[pai]:
            raise ValueError(f"Componente {filho} não encontrado na estrutura de {pai}.")
        del self.bom[pai][filho]
        if not self.bom[pai]:
            del self.bom[pai]

    def obter_componentes(self, codigo_pai):
        """Retorna o dicionário {filho: quantidade} de um item pai."""
        pai = codigo_pai.strip().upper()
        return dict(self.bom.get(pai, {}))

    def explodir(self, codigo_item, quantidade_pai=1.0, nivel=0, visitados=None):
        """Retorna a lista de componentes em profundidade com nível e quantidade acumulada."""
        codigo = codigo_item.strip().upper()
        qtd_acumulada = float(quantidade_pai)
        caminho = set(visitados) if visitados else set()

        if codigo in caminho:
            raise ValueError(f"Ciclo detectado na estrutura envolvendo o item {codigo}.")
        caminho.add(codigo)

        descricao = codigo
        unidade = "un"
        if self.cadastro_itens is not None and codigo in self.cadastro_itens.itens:
            item = self.cadastro_itens.itens[codigo]
            descricao = item.descricao
            unidade = item.unidade

        linhas = [
            {
                "nivel": nivel,
                "codigo": codigo,
                "descricao": descricao,
                "quantidade": qtd_acumulada,
                "unidade": unidade,
            }
        ]

        for filho, qtd_filho in self.obter_componentes(codigo).items():
            linhas.extend(
                self.explodir(
                    filho,
                    quantidade_pai=qtd_acumulada * float(qtd_filho),
                    nivel=nivel + 1,
                    visitados=caminho,
                )
            )
        return linhas

    def formatar_arvore(self, codigo_item):
        """Gera uma representação textual indentada da BOM a partir de um item."""
        linhas_dados = self.explodir(codigo_item)
        linhas_texto = []
        niveis_por_codigo = {}

        for entrada in linhas_dados:
            indentacao = "  " * entrada["nivel"]
            qtd_formatada = f"{entrada['quantidade']:g}".replace(".", ",")
            linhas_texto.append(
                f"{indentacao}{entrada['codigo']} {entrada['descricao']} ..... "
                f"{qtd_formatada} {entrada['unidade']}"
            )
            niveis_por_codigo.setdefault(entrada["codigo"], set()).add(entrada["nivel"])

        resumo_niveis = " | ".join(
            f"{nivel} = {', '.join(sorted(cods))}"
            for nivel, cods in sorted(
                {
                    n: [c for c, ns in niveis_por_codigo.items() if n in ns]
                    for n in {n for ns in niveis_por_codigo.values() for n in ns}
                }.items()
            )
        )
        if resumo_niveis:
            linhas_texto.append(f"Níveis: {resumo_niveis}")
        return "\n".join(linhas_texto)

    def salvar(self, arquivo="estrutura.json"):
        """Grava a estrutura de produto (BOM) em JSON."""
        salvar_json(arquivo, self.bom)

    def carregar(self, arquivo="estrutura.json"):
        """Carrega a estrutura de produto (BOM) a partir de JSON."""
        dados = carregar_json(arquivo, {})
        self.bom.clear()
        for pai, componentes in dados.items():
            for filho, quantidade in componentes.items():
                self.adicionar_componente(pai, filho, quantidade)