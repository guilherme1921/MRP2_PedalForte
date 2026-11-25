from persistencia import carregar_json, salvar_json
from utils import codigo_valido


def deduzir_tipo(codigo):
    codigo_limpo = codigo.strip().upper()
    if not codigo_valido(codigo_limpo):
        raise ValueError("Código inválido. Use o formato PA-001, SA-010 ou MP-201.")
    return codigo_limpo[:2]


class Item:
    def __init__(
        self,
        codigo,
        descricao,
        unidade,
        custo_unitario=0.0,
        lead_time=0,
        estoque_seguranca=0.0,
        lote_minimo=1.0,
    ):
        tipo_deduzido = deduzir_tipo(codigo)
        codigo_formatado = codigo.strip().upper()
        descricao_limpa = descricao.strip()
        unidade_limpa = unidade.strip()

        if not descricao_limpa:
            raise ValueError("A descrição do item não pode ficar vazia.")
        if not unidade_limpa:
            raise ValueError("A unidade de medida não pode ficar vazia.")
        if custo_unitario < 0 or lead_time < 0 or estoque_seguranca < 0 or lote_minimo <= 0:
            raise ValueError("Valores numéricos inválidos para o item.")

        self.codigo = codigo_formatado
        self.tipo = tipo_deduzido
        self.descricao = descricao_limpa
        self.unidade = unidade_limpa
        self.custo_unitario = float(custo_unitario)
        self.lead_time = int(lead_time)
        self.estoque_seguranca = float(estoque_seguranca)
        self.lote_minimo = float(lote_minimo)

    def to_dict(self):
        return {
            "codigo": self.codigo,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "unidade": self.unidade,
            "custo_unitario": self.custo_unitario,
            "lead_time": self.lead_time,
            "estoque_seguranca": self.estoque_seguranca,
            "lote_minimo": self.lote_minimo,
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(
            codigo=dados["codigo"],
            descricao=dados["descricao"],
            unidade=dados["unidade"],
            custo_unitario=dados.get("custo_unitario", 0.0),
            lead_time=dados.get("lead_time", 0),
            estoque_seguranca=dados.get("estoque_seguranca", 0.0),
            lote_minimo=dados.get("lote_minimo", 1.0),
        )


class CadastroItens:
    def __init__(self, itens=None):
        self.itens = {}
        if itens:
            for item in itens.values():
                self.cadastrar(item)

    def cadastrar(self, item):
        if not isinstance(item, Item):
            raise ValueError("O objeto informado deve ser uma instância de Item.")
        if item.codigo in self.itens:
            raise ValueError(f"Já existe um item cadastrado com o código {item.codigo}.")
        self.itens[item.codigo] = item

    def obter(self, codigo):
        codigo_formatado = codigo.strip().upper()
        if codigo_formatado not in self.itens:
            raise ValueError(f"Item {codigo_formatado} não encontrado.")
        return self.itens[codigo_formatado]

    def listar(self, tipo=None):
        tipo_filtro = tipo.strip().upper() if tipo else None
        if tipo_filtro and tipo_filtro not in ("PA", "SA", "MP"):
            raise ValueError("Tipo inválido para filtro. Use PA, SA ou MP.")
        itens_ordenados = sorted(self.itens.values(), key=lambda item: item.codigo)
        if not tipo_filtro:
            return itens_ordenados
        return [item for item in itens_ordenados if item.tipo == tipo_filtro]

    def alterar(
        self,
        codigo,
        descricao=None,
        unidade=None,
        custo_unitario=None,
        lead_time=None,
        estoque_seguranca=None,
        lote_minimo=None,
    ):
        item = self.obter(codigo)

        if descricao is not None:
            descricao_limpa = descricao.strip()
            if not descricao_limpa:
                raise ValueError("A descrição do item não pode ficar vazia.")
            item.descricao = descricao_limpa

        if unidade is not None:
            unidade_limpa = unidade.strip()
            if not unidade_limpa:
                raise ValueError("A unidade de medida não pode ficar vazia.")
            item.unidade = unidade_limpa

        if custo_unitario is not None:
            if custo_unitario < 0:
                raise ValueError("O custo unitário não pode ser negativo.")
            item.custo_unitario = float(custo_unitario)

        if lead_time is not None:
            if lead_time < 0:
                raise ValueError("O lead time não pode ser negativo.")
            item.lead_time = int(lead_time)

        if estoque_seguranca is not None:
            if estoque_seguranca < 0:
                raise ValueError("O estoque de segurança não pode ser negativo.")
            item.estoque_seguranca = float(estoque_seguranca)

        if lote_minimo is not None:
            if lote_minimo <= 0:
                raise ValueError("O lote mínimo deve ser maior que zero.")
            item.lote_minimo = float(lote_minimo)

        return item

    def salvar(self, arquivo="itens.json"):
        dados = {codigo: item.to_dict() for codigo, item in self.itens.items()}
        salvar_json(arquivo, dados)

    def carregar(self, arquivo="itens.json"):
        dados = carregar_json(arquivo, {})
        self.itens.clear()
        for codigo, info in dados.items():
            registro = dict(info)
            registro.setdefault("codigo", codigo)
            self.cadastrar(Item.from_dict(registro))