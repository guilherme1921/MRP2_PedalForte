"""Gerenciamento de ordens de produção (OP) e ordens de compra (OC)."""

from datetime import datetime
from persistencia import carregar_json, salvar_json


class GerenciadorOrdens:
    """Controla ordens de produção e compra, status e persistência em JSON."""

    STATUS_VALIDOS = ("PLANEJADA", "LIBERADA", "CONCLUIDA", "CANCELADA")
    TIPOS_VALIDOS = ("OP", "OC")

    def __init__(self, cadastro_itens=None, estoque=None, ordens=None):
        """Inicializa o gerenciador de ordens com referências opcionais."""
        self.cadastro_itens = cadastro_itens
        self.estoque = estoque
        self.ordens = []
        if ordens:
            for ordem in ordens:
                self._registrar_carregada(ordem)

    def _registrar_carregada(self, ordem):
        """Valida e adiciona em memória uma ordem já carregada de arquivo."""
        codigo_ordem = str(ordem.get("id", "")).strip().upper()
        tipo = str(ordem.get("tipo", "")).strip().upper()
        codigo_item = str(ordem.get("codigo_item", "")).strip().upper()
        quantidade = float(ordem.get("quantidade", 0))
        semana = int(ordem.get("semana", 1))
        status = str(ordem.get("status", "PLANEJADA")).strip().upper()
        data_criacao = str(ordem.get("data_criacao", "")).strip()

        if not codigo_ordem:
            raise ValueError("O ID da ordem é obrigatório.")
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de ordem inválido: {tipo}.")
        if not codigo_item:
            raise ValueError("O código do item da ordem é obrigatório.")
        if quantidade <= 0:
            raise ValueError("A quantidade da ordem deve ser maior que zero.")
        if semana <= 0:
            raise ValueError("A semana da ordem deve ser maior que zero.")
        if status not in self.STATUS_VALIDOS:
            raise ValueError(f"Status de ordem inválido: {status}.")

        self.ordens.append(
            {
                "id": codigo_ordem,
                "tipo": tipo,
                "codigo_item": codigo_item,
                "quantidade": quantidade,
                "semana": semana,
                "status": status,
                "data_criacao": data_criacao or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    def criar_ordem(self, tipo, codigo_item, quantidade, semana, status="PLANEJADA"):
        """Cria uma nova ordem (OP ou OC) com ID sequencial e valida o item."""
        tipo_ordem = str(tipo).strip().upper()
        codigo = str(codigo_item).strip().upper()
        qtd = float(quantidade)
        sem = int(semana)
        status_ordem = str(status).strip().upper()

        if tipo_ordem not in self.TIPOS_VALIDOS:
            raise ValueError("Tipo de ordem inválido. Use OP ou OC.")
        if not codigo:
            raise ValueError("O código do item é obrigatório.")
        if qtd <= 0:
            raise ValueError("A quantidade da ordem deve ser maior que zero.")
        if sem <= 0:
            raise ValueError("A semana da ordem deve ser maior que zero.")
        if status_ordem not in self.STATUS_VALIDOS:
            raise ValueError("Status da ordem inválido.")

        if self.cadastro_itens is not None:
            self.cadastro_itens.obter(codigo)

        numero = len(self.ordens) + 1
        while any(o["id"] == f"{tipo_ordem}-{numero:04d}" for o in self.ordens):
            numero += 1
        novo_id = f"{tipo_ordem}-{numero:04d}"

        ordem = {
            "id": novo_id,
            "tipo": tipo_ordem,
            "codigo_item": codigo,
            "quantidade": qtd,
            "semana": sem,
            "status": status_ordem,
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.ordens.append(ordem)
        return ordem

    def gerar_do_mrp(self, resultado_mrp):
        """Gera ordens PLANEJADAS a partir da liberação planejada de cada item no MRP."""
        criadas = []
        for codigo_item, info in sorted(resultado_mrp.items()):
            liberacao = info.get("liberacao_planejada", {})
            tipo_ordem = "OC" if codigo_item.startswith("MP") else "OP"
            if self.cadastro_itens is not None and codigo_item in self.cadastro_itens.itens:
                item = self.cadastro_itens.itens[codigo_item]
                tipo_ordem = "OC" if getattr(item, "tipo", "") == "MP" else "OP"

            for semana, qtd in sorted(liberacao.items(), key=lambda par: int(par[0])):
                quantidade = float(qtd)
                if quantidade > 0:
                    ordem = self.criar_ordem(
                        tipo=tipo_ordem,
                        codigo_item=codigo_item,
                        quantidade=quantidade,
                        semana=int(semana),
                        status="PLANEJADA",
                    )
                    criadas.append(ordem)
        return criadas

    def alterar_status(self, id_ordem, novo_status, documento=None):
        """Atualiza o status de uma ordem e registra entrada no estoque ao concluir."""
        identificador = str(id_ordem).strip().upper()
        status_destino = str(novo_status).strip().upper()

        if status_destino not in self.STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {status_destino}.")

        ordem_alvo = None
        for ordem in self.ordens:
            if ordem["id"] == identificador:
                ordem_alvo = ordem
                break

        if ordem_alvo is None:
            raise ValueError(f"Ordem não encontrada: {identificador}.")

        status_atual = ordem_alvo["status"]
        if status_atual == "CONCLUIDA" and status_destino != "CONCLUIDA":
            raise ValueError(f"A ordem {identificador} já está concluída e não pode retroceder.")
        if status_atual == "CANCELADA" and status_destino != "CANCELADA":
            raise ValueError(f"A ordem {identificador} está cancelada e não pode ser reaberta.")

        if status_destino == "CONCLUIDA" and status_atual != "CONCLUIDA":
            if self.estoque is not None:
                doc_mov = documento or f"CONCLUSAO-{identificador}"
                self.estoque.movimentar(
                    codigo_item=ordem_alvo["codigo_item"],
                    tipo="ENTRADA",
                    quantidade=ordem_alvo["quantidade"],
                    documento=doc_mov,
                )

        ordem_alvo["status"] = status_destino
        return ordem_alvo

    def salvar(self, arquivo="ordens.json"):
        """Grava a lista de ordens em arquivo JSON."""
        salvar_json(arquivo, self.ordens)

    def carregar(self, arquivo="ordens.json"):
        """Carrega a lista de ordens a partir de um arquivo JSON."""
        registros = carregar_json(arquivo, [])
        self.ordens.clear()
        for ordem in registros:
            self._registrar_carregada(ordem)