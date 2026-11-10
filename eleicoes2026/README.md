# Entendendo a transferência de votos entre o primeiro e segundo turno das eleições presidenciais de 2026

Este repositório contém o subprojeto **eleicoes2026**, integrante do repositório de miniprojetos [`mini_projects`](https://github.com/VFLins/mini_projects) de [@VFLins](https://github.com/VFLins).

[![Leia online](https://img.shields.io/badge/Leia%20online-teal?style=for-the-badge)](https://vflins.github.io/mini_projects/eleicoes2026/)

---


### 📂 Estrutura de arquivos

```text
eleicoes2026/
├── data/             # Pesquisas eleitorais e dados de votação do STE
├── bib/              # Referências bibliográficas usadas
├── datasets.py       # Conjuntos de dados customizados
├── formulas.py       # Algoritmos usados nas estatísticas
├── graphics.py       # Visualizações de dados customizadas
├── main.py           # Notebook principal com o relatório
├── pyproject.toml    # Configurações do projeto lidas pelo marimo
└── requirements.txt  # Dependências do projeto
```


### 🚀 Para executar localmente


#### Pré-requisitos

- Git
- Python 3.10+

#### Passo a passo
Clone o repositório principal:

```Bash
git clone https://github.com/VFLins/mini_projects.git
cd mini_projects/eleicoes2026
```

Instale as dependências:

```Bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Execute o relatório localmente:

```Bash
marimo edit main.py
```

E espere o notebook abrir no seu navegador padrão.
