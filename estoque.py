"""Controle de movimentações de estoque, saldo e histórico kardex."""

from datetime import datetime
from persistencia import carregar_csv, salvar_csv


class Estoque:
    """Gerencia o kardex e o saldo dos itens em memória e em CSV."""

    CAMPOS_CSV = ["data", "codigo", "tipo", "quantidade", "saldo", "documento"]

    def __init__(self, cadastro_itens=None, movimentos=None):
        """Inicializa o estoque com histórico de movimentos."""
        self.cadastro_itens = cadastro_itens
        self.movimentos = []
        if movimentos:
            for mov in movimentos:
                self._registrar_carregado(mov)

    def _registrar_carregado(self, registro):
        """Insere na lista um movimento já lido do histórico sem alterar o saldo."""
        codigo = str(registro["codigo"]).strip().upper()
        tipo = str(registro["tipo"]).strip().upper()
        quantidade = float(registro["quantidade"])
        saldo_apos = float(registro["saldo"])
        data = str(registro.get("data", "")).strip()
        documento = str(registro.get("documento", "")).strip()

        if saldo_apos < 0:
            raise ValueError(f"Saldo negativo detectado no histórico de {codigo}.")

        self.movimentos.append(
            {
                "data": data,
                "codigo": codigo,
                "tipo": tipo,
                "quantidade": quantidade,
                "saldo": saldo_apos,
                "documento": documento,
            }
        )

    def saldo(self, codigo_item):
        """Retorna o saldo atual percorrendo o kardex de trás para frente."""
        codigo = codigo_item.strip().upper()
        for mov in reversed(self.movimentos):
            if mov["codigo"] == codigo:
                return float(mov["saldo"])
        return 0.0

    def kardex(self, codigo_item):
        """Retorna o histórico do item e informa se está abaixo do estoque de segurança."""
        codigo = codigo_item.strip().upper()
        historico = [mov for mov in self.movimentos if mov["codigo"] == codigo]
        saldo_atual = self.saldo(codigo)
        alerta_seguranca = False
        estoque_seguranca = 0.0

        if self.cadastro_itens is not None and codigo in self.cadastro_itens.itens:
            item = self.cadastro_itens.itens[codigo]
            estoque_seguranca = float(item.estoque_seguranca)
            alerta_seguranca = saldo_atual < estoque_seguranca

        return {
            "codigo": codigo,
            "saldo": saldo_atual,
            "estoque_seguranca": estoque_seguranca,
            "alerta_seguranca": alerta_seguranca,
            "movimentos": historico,
        }

    def movimentar(self, codigo_item, tipo, quantidade, documento="", data=None):
        """Registra entrada, saída ou ajuste bloqueando saldo negativo antes de gravar."""
        codigo = codigo_item.strip().upper()
        tipo_mov = tipo.strip().upper()
        qtd = float(quantidade)
        doc = str(documento).strip()
        data_mov = str(data).strip() if data else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not codigo:
            raise ValueError("O código do item é obrigatório.")
        if self.cadastro_itens is not None:
            self.cadastro_itens.obter(codigo)
        if tipo_mov not in ("ENTRADA", "SAIDA", "AJUSTE"):
            raise ValueError("Tipo de movimento inválido. Use ENTRADA, SAIDA ou AJUSTE.")
        if not doc:
            raise ValueError("O documento ou motivo do movimento é obrigatório.")

        saldo_atual = self.saldo(codigo)

        if tipo_mov == "ENTRADA":
            if qtd <= 0:
                raise ValueError("A quantidade de entrada deve ser maior que zero.")
            novo_saldo = saldo_atual + qtd
            qtd_registrada = qtd
        elif tipo_mov == "SAIDA":
            if qtd <= 0:
                raise ValueError("A quantidade de saída deve ser maior que zero.")
            novo_saldo = saldo_atual - qtd
            qtd_registrada = -qtd
        else:
            if qtd == 0:
                raise ValueError("A quantidade de ajuste não pode ser zero.")
            novo_saldo = saldo_atual + qtd
            qtd_registrada = qtd

        if novo_saldo < 0:
            raise ValueError(
                f"Saldo insuficiente para {codigo}. Saldo atual: {saldo_atual:g}, "
                f"saldo resultante seria: {novo_saldo:g}."
            )

        movimento = {
            "data": data_mov,
            "codigo": codigo,
            "tipo": tipo_mov,
            "quantidade": qtd_registrada,
            "saldo": novo_saldo,
            "documento": doc,
        }
        self.movimentos.append(movimento)
        return movimento

    def salvar(self, arquivo="movimentos.csv"):
        """Grava o histórico do kardex em arquivo CSV."""
        salvar_csv(arquivo, self.movimentos, self.CAMPOS_CSV)

    def carregar(self, arquivo="movimentos.csv"):
        """Carrega o histórico do kardex a partir de um arquivo CSV."""
        registros = carregar_csv(arquivo)
        self.movimentos.clear()
        for registro in registros:
            self._registrar_carregado(registro)