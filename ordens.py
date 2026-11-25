"""Ordens de produção (OP) e de compra (OC): status, firmar, liberar e apontar."""

from datetime import datetime
from persistencia import carregar_json, salvar_json

TIPOS_VALIDOS = ("OP", "OC")
STATUS_VALIDOS = ("PLANEJADA", "ATRASADA", "FIRME", "LIBERADA", "ENCERRADA")
STATUS_NAO_FIRMES = ("PLANEJADA", "ATRASADA")
STATUS_RECEBIMENTO = ("FIRME", "LIBERADA")


class Ordem:
    """Representa uma ordem de produção (OP) ou de compra (OC)."""

    def __init__(self, id_ordem, tipo, codigo_item, quantidade,
                 semana_liberacao, semana_entrega, status="PLANEJADA",
                 data_criacao=None):
        """Valida os dados e cria a ordem."""
        tipo_limpo = str(tipo).strip().upper()
        status_limpo = str(status).strip().upper()

        if tipo_limpo not in TIPOS_VALIDOS:
            raise ValueError("Tipo de ordem inválido. Use OP ou OC.")
        if status_limpo not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {status_limpo}.")
        if float(quantidade) <= 0:
            raise ValueError("A quantidade da ordem deve ser maior que zero.")
        if int(semana_entrega) < 1:
            raise ValueError("A semana de entrega deve ser maior ou igual a 1.")

        self.id = str(id_ordem).strip().upper()
        self.tipo = tipo_limpo
        self.codigo_item = str(codigo_item).strip().upper()
        self.quantidade = float(quantidade)
        self.semana_liberacao = int(semana_liberacao)
        self.semana_entrega = int(semana_entrega)
        self.status = status_limpo
        self.data_criacao = data_criacao or datetime.now().strftime("%d/%m/%Y")

    def to_dict(self):
        """Converte a ordem em dicionário para gravar em JSON."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "codigo_item": self.codigo_item,
            "quantidade": self.quantidade,
            "semana_liberacao": self.semana_liberacao,
            "semana_entrega": self.semana_entrega,
            "status": self.status,
            "data_criacao": self.data_criacao,
        }

    @classmethod
    def from_dict(cls, dados):
        """Recria uma ordem a partir de um dicionário lido do JSON."""
        return cls(
            id_ordem=dados["id"],
            tipo=dados["tipo"],
            codigo_item=dados["codigo_item"],
            quantidade=dados["quantidade"],
            semana_liberacao=dados["semana_liberacao"],
            semana_entrega=dados["semana_entrega"],
            status=dados.get("status", "PLANEJADA"),
            data_criacao=dados.get("data_criacao"),
        )


class GerenciadorOrdens:
    """Controla as ordens, seus status e o apontamento de produção."""

    def __init__(self, cadastro_itens=None, estoque=None, estrutura=None):
        """Guarda as dependências e inicia a lista de ordens e os contadores."""
        self.cadastro_itens = cadastro_itens
        self.estoque = estoque
        self.estrutura = estrutura
        self.ordens = []
        self.contadores = {"OP": 0, "OC": 0}

    def _proximo_id(self, tipo):
        """Gera o próximo número sequencial (OP-0010, OC-0004...)."""
        self.contadores[tipo] += 1
        return f"{tipo}-{self.contadores[tipo]:04d}"

    def criar_ordem(self, tipo, codigo_item, quantidade, semana_liberacao,
                    semana_entrega, status="PLANEJADA"):
        """Cria uma ordem com ID sequencial, validando o item e o tipo."""
        tipo_ordem = str(tipo).strip().upper()
        codigo = str(codigo_item).strip().upper()

        if self.cadastro_itens is not None:
            item = self.cadastro_itens.obter(codigo)
            if tipo_ordem == "OC" and item.tipo != "MP":
                raise ValueError("Ordem de compra (OC) só vale para matéria-prima.")
            if tipo_ordem == "OP" and item.tipo == "MP":
                raise ValueError("Ordem de produção (OP) não vale para matéria-prima.")

        ordem = Ordem("PROVISORIO", tipo_ordem, codigo, quantidade,
                      semana_liberacao, semana_entrega, status)
        ordem.id = self._proximo_id(tipo_ordem)
        self.ordens.append(ordem)
        return ordem

    def buscar(self, id_ordem):
        """Devolve a ordem com o ID informado."""
        identificador = str(id_ordem).strip().upper()
        for ordem in self.ordens:
            if ordem.id == identificador:
                return ordem
        raise ValueError(f"Ordem {identificador} não encontrada.")

    def listar(self, tipo=None, status=None):
        """Lista as ordens, ordenadas pelo ID, com filtros opcionais."""
        resultado = sorted(self.ordens, key=lambda ordem: ordem.id)
        if tipo:
            resultado = [o for o in resultado if o.tipo == tipo.strip().upper()]
        if status:
            resultado = [o for o in resultado if o.status == status.strip().upper()]
        return resultado

    def ordens_do_item(self, codigo_item):
        """Devolve as ordens de um item."""
        codigo = str(codigo_item).strip().upper()
        return [ordem for ordem in self.ordens if ordem.codigo_item == codigo]

    def apagar_planejadas(self):
        """RN08: apaga as ordens não firmes (PLANEJADA e ATRASADA)."""
        antes = len(self.ordens)
        self.ordens = [o for o in self.ordens if o.status not in STATUS_NAO_FIRMES]
        return antes - len(self.ordens)

    def gerar_do_mrp(self, registros):
        """RF09: recria as ordens planejadas a partir dos registros do MRP."""
        self.apagar_planejadas()
        criadas = []
        for codigo, registro in registros.items():
            tipo_ordem = "OC" if codigo.startswith("MP") else "OP"
            for planejada in registro["ordens_planejadas"]:
                atrasada = planejada["semana_liberacao"] < 1
                criadas.append(
                    self.criar_ordem(
                        tipo_ordem,
                        codigo,
                        planejada["quantidade"],
                        planejada["semana_liberacao"],
                        planejada["semana_entrega"],
                        "ATRASADA" if atrasada else "PLANEJADA",
                    )
                )
        return criadas

    def mensagens_excecao(self):
        """RN07: mensagens para as ordens com liberação antes da semana 1."""
        mensagens = []
        for ordem in self.listar(status="ATRASADA"):
            mensagens.append(
                f"{ordem.id} ({ordem.codigo_item}): liberação na semana "
                f"{ordem.semana_liberacao}, antes da semana 1."
            )
        return mensagens

    def firmar(self, id_ordem):
        """Passa a ordem de PLANEJADA/ATRASADA para FIRME."""
        ordem = self.buscar(id_ordem)
        if ordem.status not in STATUS_NAO_FIRMES:
            raise ValueError(
                f"Só é possível firmar ordem PLANEJADA ou ATRASADA "
                f"(status atual: {ordem.status})."
            )
        ordem.status = "FIRME"
        return ordem

    def liberar(self, id_ordem):
        """Passa a ordem de FIRME para LIBERADA."""
        ordem = self.buscar(id_ordem)
        if ordem.status != "FIRME":
            raise ValueError(
                f"Só é possível liberar ordem FIRME (status atual: {ordem.status})."
            )
        ordem.status = "LIBERADA"
        return ordem

    def receber_compra(self, id_ordem):
        """Encerra uma OC liberada, dando entrada da matéria-prima no estoque."""
        ordem = self.buscar(id_ordem)
        if ordem.tipo != "OC":
            raise ValueError(f"{ordem.id} não é uma ordem de compra.")
        if ordem.status != "LIBERADA":
            raise ValueError(
                f"Só é possível receber OC LIBERADA (status atual: {ordem.status})."
            )
        self.estoque.movimentar(
            ordem.codigo_item, "ENTRADA", ordem.quantidade,
            f"{ordem.id} (recebimento)",
        )
        ordem.status = "ENCERRADA"
        return ordem

    def apontar_producao(self, id_ordem):
        """RF11: baixa os componentes, dá entrada no produzido e encerra a OP."""
        ordem = self.buscar(id_ordem)
        if ordem.tipo != "OP":
            raise ValueError(f"{ordem.id} não é uma ordem de produção.")
        if ordem.status != "LIBERADA":
            raise ValueError(
                f"Só é possível apontar OP LIBERADA (status atual: {ordem.status})."
            )

        componentes = self.estrutura.obter_componentes(ordem.codigo_item)
        if not componentes:
            raise ValueError(f"{ordem.codigo_item} não possui estrutura cadastrada.")

        necessidades = {
            filho: qtd_unitaria * ordem.quantidade
            for filho, qtd_unitaria in componentes.items()
        }
        faltas = []
        for filho, necessario in necessidades.items():
            saldo = self.estoque.saldo(filho)
            if saldo < necessario:
                faltas.append(
                    f"{filho}: precisa de {necessario:g}, saldo {saldo:g}"
                )
        if faltas:
            raise ValueError(
                "apontamento rejeitado, faltam componentes (" + "; ".join(faltas) + ")."
            )

        documento = f"{ordem.id} ({ordem.codigo_item})"
        for filho, necessario in necessidades.items():
            self.estoque.movimentar(filho, "SAIDA", necessario, documento)
        self.estoque.movimentar(
            ordem.codigo_item, "ENTRADA", ordem.quantidade, documento
        )
        ordem.status = "ENCERRADA"
        return ordem

    def salvar(self, arquivo="ordens.json"):
        """Grava as ordens e os contadores em JSON."""
        dados = {
            "contadores": self.contadores,
            "ordens": [ordem.to_dict() for ordem in self.ordens],
        }
        salvar_json(arquivo, dados)

    def carregar(self, arquivo="ordens.json"):
        """Carrega as ordens e os contadores a partir de JSON."""
        dados = carregar_json(arquivo, {"contadores": {}, "ordens": []})
        self.ordens = [Ordem.from_dict(d) for d in dados.get("ordens", [])]
        self.contadores = {"OP": 0, "OC": 0}
        for tipo, valor in dados.get("contadores", {}).items():
            self.contadores[tipo] = int(valor)
        for ordem in self.ordens:
            numero = int(ordem.id.split("-")[1])
            self.contadores[ordem.tipo] = max(self.contadores[ordem.tipo], numero)
