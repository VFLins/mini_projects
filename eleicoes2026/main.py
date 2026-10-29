import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import matplotlib.pyplot as plt
    import urllib.request, zipfile
    from pathlib import Path

    return Path, pd, urllib, zipfile


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(Path, urllib, zipfile):
    # Obtendo dados para a análise
    # ============================

    # Downloads na mesma pasta que o main.py
    PROJECT_ROOT = Path(__file__).parent.resolve()
    DOWNLOADS_DIR = PROJECT_ROOT / "data"

    # Presidente - Votação por seção eleitoral - 2026
    # https://dadosabertos.tse.jus.br/dataset/resultados-2026/resource/01ea4ccd-f443-469c-9f29-c69ff97f7d4c
    VOTOS_URL = (
        "https://cdn.tse.jus.br/estatistica/sead/odsele/"
        "votacao_secao/votacao_secao_2026_BR.zip"
    )
    VOTOS_ZIP = VOTOS_URL.split("/")[-1]
    print("Fazendo download dos dados...")
    urllib.request.urlretrieve(VOTOS_URL, VOTOS_ZIP)
    print(f"Extraindo arquivos para {DOWNLOADS_DIR}")
    zipfile.ZipFile(PROJECT_ROOT / VOTOS_ZIP).extractall(DOWNLOADS_DIR)
    print(f"Excluindo arquivo compactado {PROJECT_ROOT / VOTOS_ZIP}")
    (PROJECT_ROOT / VOTOS_ZIP).unlink()
    print("Concluído!")
    return (DOWNLOADS_DIR,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Entendendo a transferência de votos entre o primeiro e segundo turno das eleições presidenciais de 2026

    O candidato Flávio Bolsonaro terminou o primeiro turno com uma votação maior que a do seu principal adversário Lula, isto levou os bolsonaristas a acreditar que a vitória no segundo turno seria certa, já que históricamente, o primeiro colocado no primeiro turno sempre acabava ganhando a disputa no segundo turno.

    Depois da derrota, já nos Estados Unidos, Flávio Bolsonaro alegou uma "impossibilidade matemática", que permitiu que o seu adversário Lula ganhasse mais de 10 Milhões de votos do primeiro para o segundo turno. O objetivo desta análise é combinar os dados de votação com os resultados de pesquisas de opinião anteriores às votações para entender se esta transferência é realmente impossível como alegado.
    """)
    return


@app.cell
def _(DOWNLOADS_DIR, pd):
    votos = pd.read_csv(
        DOWNLOADS_DIR / "votacao_secao_2026_BR.csv",
        sep=";",
        encoding="latin1",
    )
    votos.dtypes
    return (votos,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A explicação dos códigos acima está no arquivo `"data/leiame.pdf"`.

    Para validar se os dados de votos foram coletados corretamente, vamos tentar reproduzir os resultados das votações em tabelas  abaixo:
    """)
    return


@app.cell
def _(votos):
    # eleições dos presidenciáveis: 1º turno
    prim_turno = votos.loc[votos["NR_TURNO"] == 1]
    prim_turno.groupby("NM_VOTAVEL")["QT_VOTOS"].sum().sort_values(ascending=False)
    return


@app.cell
def _(votos):
    # eleições dos presidenciáveis: 2º turno
    seg_turno = votos.loc[votos["NR_TURNO"] == 2]
    seg_turno.groupby("NM_VOTAVEL")["QT_VOTOS"].sum().sort_values(ascending=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## As pesquisas de intenções

    Se os números estiverem condizentes com o resultado das eleições, os dados devem estar prontos para a análise. Mas antes de começar, vamos buscar mais informações para suportar a análise, para entender a propensão dos eleitores a transferir vontos entre candidatos, vamos apoiare guiar os testes nas intenções de votos das pesquisas independentes realizadas.

    Para esta análise, vamos considerar:

    - Vox Brasil
      - [BR-09623/2026](https://static.poder360.com.br/uploads/2026/10/pesquisa-vox-brasil-9out2026.pdf)
    - Colectta
      - [BR-04291/2026](https://www.colectta.com.br/pesquisas/pesquisa-nacional-da-colectta-aponta-cenarios-de-intencao-de-voto-para-presidente-em-2026)
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
