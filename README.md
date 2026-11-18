# MRP II - Pedal Forte Bicicletas

Sistema de Planejamento dos Recursos de Manufatura (MRP II) em Python para a
fábrica fictícia Pedal Forte Bicicletas, desenvolvido na disciplina de
Programação em Python (CEFET-MG, Campus Divinópolis).

> **Status:** em desenvolvimento. Os módulos de cadastro, estrutura de
> produto e estoque estão prontos; MPS, MRP, ordens, CRP, custos e gráficos
> serão entregues nas próximas etapas.

## Funcionalidades já implementadas

| Módulo | Requisitos | Descrição |
|---|---|---|
| `itens.py` | RF02, RN01 | Cadastro, listagem e alteração de itens (PA, SA, MP) |
| `estrutura.py` | RF03, RN03 | BOM em até 3 níveis, com árvore indentada recursiva |
| `estoque.py` | RF04, RF05, RN02, RN10 | Movimentações, saldo, kardex e alerta de estoque de segurança |
| `persistencia.py` | RF15 | Leitura e gravação de JSON e CSV na pasta `data/` |
| `utils.py` | RNF05 | Validação de entradas e formatação |

## Como executar

Requisito: Python 3.10 ou superior.

```
git clone https://github.com/guilherme1921/MRP2_PedalForte.git
cd MRP2_PedalForte
python itens.py      # cadastro de itens
python estrutura.py  # estrutura de produto (BOM)
python estoque.py    # movimentações e kardex
```

O menu principal (`main.py`) será adicionado nas próximas etapas.

## Decisões de projeto

- **POO simples:** uma classe principal por módulo (`Item`, `Estrutura`, `Estoque`).
- **Dicionários:** itens indexados por código e BOM no formato `{pai: {filho: quantidade}}`.
- **Regra RN03 por tipo:** PA aceita SA e MP; SA aceita só MP; MP não tem estrutura. Isso também impede ciclos.
- **Kardex imutável:** movimentos nunca são excluídos; correções são feitas por ajuste (RN10).
- **Persistência:** JSON para itens e estrutura; CSV para movimentos.

## Estrutura do projeto

```
MRP2_PedalForte/
├── itens.py
├── estrutura.py
├── estoque.py
├── persistencia.py
├── utils.py
└── data/
```

## Autor

Guilherme Maia Mascarenhas - CEFET-MG