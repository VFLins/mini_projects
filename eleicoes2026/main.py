import marimo

__generated_with = "0.25.2"
app = marimo.App(
    app_title="Entendendo a transferência de votos nas eleições presidenciais de 2026",
    css_file="theme.css",
)


@app.cell
def _():
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np
    import pandas as pd

    from datetime import date
    from pathlib import Path

    return Path, date, pd, ticker


@app.cell
def _():
    import marimo as mo

    def figcaption(text: str) -> mo.Html:
        """HTML element styled as a figure caption."""
        return mo.md(f"<span style='font-size: 13px'>{text}</span>").center()

    return figcaption, mo


@app.cell
def _():
    import formulas as f
    import datasets as d
    import graphics as g

    return d, f, g


@app.cell
def _(d):
    votos = d.VoteData()
    if not votos.file_exists:
        votos.ask_download
    return (votos,)


@app.cell
def _(mo, votos):
    mo.stop(
        not votos.file_exists,
        mo.md("Dados de votação não solicitados, pulando..."),
    )

    votos.download()
    votos.load()
    return


@app.cell
def _(mo, votos):
    mo.stop(not hasattr(votos, "df"))
    prim_turno = votos.df.loc[votos.df["NR_TURNO"] == 1]
    seg_turno = votos.df.loc[votos.df["NR_TURNO"] == 2]

    _is_valid_r1 = prim_turno["NR_VOTAVEL"].isin([13, 22])
    _voted_lula_r1 = prim_turno["NR_VOTAVEL"] == 13
    _voted_flavio_r1 = prim_turno["NR_VOTAVEL"] == 22
    _is_valid_r2 = seg_turno["NR_VOTAVEL"].isin([13, 22])
    _voted_lula_r2 = seg_turno["NR_VOTAVEL"] == 13
    _voted_flavio_r2 = seg_turno["NR_VOTAVEL"] == 22

    n_votos_r1 = prim_turno["QT_VOTOS"].sum()
    n_votos_validos_r1 = prim_turno.loc[_is_valid_r1]["QT_VOTOS"].sum()
    n_votos_r2 = seg_turno["QT_VOTOS"].sum()
    n_votos_validos_r2 = seg_turno.loc[_is_valid_r2]["QT_VOTOS"].sum()

    vote_stats = dict(
        r1=dict(
            lula={
                "n": prim_turno.loc[_voted_lula_r1]["QT_VOTOS"].sum(),
                "p": prim_turno.loc[_voted_lula_r1]["QT_VOTOS"].sum() / n_votos_r1,
                "p_validos": prim_turno.loc[_voted_lula_r1]["QT_VOTOS"].sum()
                / n_votos_validos_r1,
            },
            flavio={
                "n": prim_turno.loc[_voted_flavio_r1]["QT_VOTOS"].sum(),
                "p": prim_turno.loc[_voted_flavio_r1]["QT_VOTOS"].sum() / n_votos_r1,
                "p_validos": prim_turno.loc[_voted_flavio_r1]["QT_VOTOS"].sum()
                / n_votos_validos_r1,
            },
            votos={
                "n": n_votos_r1,
                "n_validos": n_votos_validos_r1,
            },
        ),
        r2=dict(
            lula={
                "n": seg_turno.loc[_voted_lula_r2]["QT_VOTOS"].sum(),
                "p": seg_turno.loc[_voted_lula_r2]["QT_VOTOS"].sum() / n_votos_r2,
                "p_validos": seg_turno.loc[_voted_lula_r2]["QT_VOTOS"].sum()
                / n_votos_validos_r2,
            },
            flavio={
                "n": seg_turno.loc[_voted_flavio_r2]["QT_VOTOS"].sum(),
                "p": seg_turno.loc[_voted_flavio_r2]["QT_VOTOS"].sum() / n_votos_r2,
                "p_validos": seg_turno.loc[_voted_flavio_r2]["QT_VOTOS"].sum()
                / n_votos_validos_r2,
            },
            votos={
                "n": n_votos_r2,
                "n_validos": n_votos_validos_r2,
            },
        ),
    )
    return (vote_stats,)


@app.cell
def _(d):
    _n = d.rpolls.df["n"]
    _nua = d.rpolls.df["n_unsure_a"]
    _nub = d.rpolls.df["n_unsure_b"]
    _w = d.rpolls.df["n"] / _n.sum()

    poll_stats = dict(
        lula={
            "p": d.rpolls.df["vote_b"].mean(), # avg. percentage
            "wp": (d.rpolls.df["vote_b"] * _w).sum(), # weighted avg. percentage
            "p_valid": (d.rpolls.df["n_vote_b"] / (_n - _nub)).mean(),
            "wp_valid": (d.rpolls.df["n_vote_b"] * _w / (_n - _nub)).sum(),
            "r": d.rpolls.df["reject_b"].mean(),
            "wr": (d.rpolls.df["reject_b"] * _w).sum(),
            "n": d.rpolls.df["n_vote_b"].sum().round(),
        },
        flavio={
            "p": d.rpolls.df["vote_a"].mean(),
            "wp": (d.rpolls.df["vote_a"] * _w).sum(),
            "p_valid": (d.rpolls.df["n_vote_a"] / (_n - _nua)).mean(),
            "wp_valid": (d.rpolls.df["n_vote_a"] * _w / (_n - _nua)).sum(),
            "r": d.rpolls.df["reject_a"].mean(),
            "wr": (d.rpolls.df["reject_a"] * _w).sum(),
            "n": d.rpolls.df["n_vote_a"].sum().round(),
        },
        votos={
            "n": d.rpolls.df["n"].sum(),
            "n_validos": (d.rpolls.df["n_vote_a"] + d.rpolls.df["n_vote_b"]).sum(),
        },
    )
    return


@app.cell(hide_code=True)
def _(d, mo):
    mo.md(rf"""
    [{mo.image(d.PROJECT_ROOT / "static" / "logo.svg", height=28, style={"margin-left": "8.5px", "margin-top": "2px"})}](https://vitorlins.com.br)
    """)
    return


@app.cell
def _(mo):
    mo.hstack(
        items=[
            mo.md(
                "[![Ver outros projetos](https://img.shields.io/badge/"
                "ver%20outros%20projetos-white.svg?"
                "style=for-the-badge&logo=data:image/svg%2bxml;base64,"
                "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZ"
                "pZXdCb3g9IjAgMCA0OCA0OCIgaGVpZ2h0PSI0OHB4IiB3aWR0aD0iNDhweCI"
                "gZmlsbD0iIzIxMmMzOCI+PHBhdGggZD0iTTIxLjIsNDUuMkwwL"
                "DI0TDIxLjIsMi44bDQsNC4wNUw4LjA1LDI0TDI1LjIsNDEuMTVsL"
                "TQsNC4wNVoiLz48L3N2Zz4=)](https://vflins.github.io/mini_projects/)"
            ),
            mo.md(
                "[![Repositório](https://img.shields.io/badge/"
                "Reposit%C3%B3rio-white?logo=github&"
                "logoColor=212c38&style=for-the-badge)](https://"
                "github.com/VFLins/mini_projects/tree/main/eleicoes2026)"
            ),
        ],
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Entendendo a transferência de votos nas eleições presidenciais de 2026
    """)
    return


@app.cell
def _(date, mo):
    import locale
    locale.setlocale(locale.LC_ALL, "pt_BR")

    mo.md(rf"""
    <span style='font-family: space mono, monospace; font-size: 13px; text-transform: uppercase'><b>
        {date.today().strftime('%A, %d de %B de %Y')}</b> | 18 minutos de leitura</span>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    </br>

    /// note | Resumo
    As eleições presidenciais de 2026 sofreram com uma quantidade de acusações de fraude e por causa do resultado inesperado para muitos depois das votações. Esta análise tenta entender se o fluxo de votos entre turnos que vimos é possível e o que explicaria ele, para isso, usamos um modelo de inferência nos dados oficiais da votação, e complementamos a análise dos resultados deste modelo com uma análise exploratória em dados das pesquisas eleitorais e fatos divulgados pela imprensa.

    Os resultados mostram que a diferença de estratégia entre as campanhas eleitorais no segundo turno definiram o resultado no segundo turno. Enquanto a campanha de Flávio Bolsonaro diminuiu esforços com a perspectiva de vitória certa, a capanha de Lula se intensificou, conseguindo votos suficientes para empatar a disputa ao atrair eleitores que votaram no primeiro turno, e somando-se a estes, suficientes para virar a votação ao atrair eleitores que se abstiveram no primeiro turno.
    ///

    <br/ >

    ## Introdução

    O candidato Flávio Bolsonaro terminou o primeiro turno com uma votação maior que a do seu adversário Lula, isto levou os bolsonaristas a acreditar que a vitória no segundo turno seria certa, já que historicamente, o primeiro colocado no primeiro turno sempre acabava ganhando a disputa no segundo turno.

    Depois da derrota, já nos Estados Unidos, Flávio Bolsonaro alegou uma "impossibilidade matemática", que permitiu que o seu adversário Lula ganhasse mais de 10 Milhões de votos do primeiro para o segundo turno. Além disso, se aponta que a maioria das pesquisas de intenções de voto indicava a vitória iminente do candidato.

    O objetivo desta análise é combinar os dados de votação com os resultados de pesquisas de opinião anteriores às votações do segundo turno para entender se esta transferência é realmente impossível como alegado. Para isso, vamos separar esta análise em partes:

    1. Estimar a transferência possível de votos com dados oficiais das votações, e comparar com fatos das estratégias de campanha para entender se este ganho de votos foi realmente possível; depois vamos

    2. Tentar entender se mesmo com a discrepância entre as pesquisas eleitorais realizadas após o resultado do primeiro turno e o resultado nas urnas, a vitória de Lula era possível.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inferindo a transferência de votos

    Os dias de votação das eleições presidenciais de 2026 foram 4 de outubro para o primeiro turno e 25 do mesmo mês para o segundo. Os candidatos tiveram um período de apenas três semanas para convencer o eleitorado e atrair votos para si.

    Neste cenário de curto período de tempo, é razoavelmente seguro considerar que os esforços de campanha tenham se concentrado nos eleitores indecisos, como foi a estratégia da campanha do então candidato a reeleição, Lula, no segundo turno[^1].

    Por outro lado, para alguns especialistas[^2] e até para a própria equipe de campanha do Flávio Bolsonaro, sua vitória parecia ser muito segura. No fim das contas não foi feita nenhuma grande estratégia para garantir a vitória no segundo turno[^3].




    [^1]: **Terra**. [A revolução da linguagem no segundo turno das eleições de 2026](https://www.terra.com.br/noticias/a-revolucao-da-linguagem-no-segundo-turno-das-eleicoes-de-2026,23066fe203723310bd23f18087066c3f15bi85pz.html?utm_source=clipboard) por Djiovanni Marioto

    [^2]: **Veja**. [A estratégia de Flávio e o dilema de Lula no segundo turno](https://veja.abril.com.br/politica/a-estrategia-de-flavio-e-o-dilema-de-lula-no-segundo-turno/)

    [^3]: **BBC**. ['Ele achou que já estava eleito': os erros da campanha de Flávio Bolsonaro no segundo turno apontados por analistas](https://www.bbc.com/portuguese/articles/cmrryxg991d8o)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Metodologia

    Para estimar a transferência de votos, será um modelo de inferência de Rosen et al. (2001)[^4], mas com uma restrição: Não há transferência de votos entre os candidatos do primeiro turno. Isto significa que todo o potencial de receber votos dos candidatos no segundo turno está entre os eleitores que:

    1. Votaram em outros candidatos que não passaram para o segundo turno,
    2. Votaram Branco ou anularam o voto,
    3. Se abstiveram de votar no primeiro turno.

    Esta restrição assume que todos os que votaram no Lula no primeiro turno vão continuar votando nele, e o mesmo vale para o Flávio. Embora crie um pressuposto capaz de introduzir viés no modelo, também traz outros dois benefícios importantes na minha análise.

    O viés potencialmente introduzido por esta restrição é controlado pela a diferença entre as datas de votações dos turnos. Como a possibilidade de converter um eleitor do candidato adversário aumenta como tempo disponível para a campanha, o prazo de 21 dias provavelmente será insuficiente para este propósito.



    [^4]: **Statistica Neerlandica**. [Bayesian and Frequentist Inference for Ecological Inference: The R×C Case](https://onlinelibrary.wiley.com/doi/abs/10.1111/1467-9574.00162) por Ori Rosen, Wenxin Jiang, Gary King e Martin A. Tanner
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Dados de votação

    Para treinar este modelo serão usados os dados oficiais de votação divulgados pelo STE, obtidos pelo repositório oficial[^5].Algumas outras restrições precisaram ser feitas no modelo empregado por causa de limitações de _hardware_:

    - **Memória de vídeo:** Para treinar o modelo já com a restrição mencionada mas usando todas as seções eleitorais, eu precisaria de aproximadamente 60GB de VRAM, para contornar isso, os dados foram agregados em zonas eleitorais, o que reduz o requisito de VRAM para menos de 1GB.

    - **Tempo de processamento:** A precisão e qualidade do resultado depende da quantidade e da qualidade das iterações realizadas, cada uma delas exige tempo de processamento:

        1. **Qualidade:** cada iteração pode ser rápida ou não dependendo do tempo que cada uma precisa para atingir uma condição de parada, as condições podem ser um limite fixo ou o momento que o modelo entende que não fará mais progresso mesmo que continue tentando se ajustar. Quase todas as iterações pararam no limite fixo, o que indica que o modelo provavelmente se ajustaria melhor com um limite fix mais alto, e

        2. **Quantidade**: Com a configuração `chains=8`, `tune=1000` e `draws=1000`, o modelo faz 2000 iterações por grupo, das quais as últimas 1000 são guardadas na memória para cada um dos oito grupos trabalhando em paralelo. Esta combinação exigiu aproximadamente 50 minutos de processamento no meu _hardware_.

    Os dados de fluxo de votos retornados pelo modelo vão divergir um pouco dos números reais da votação, eles devem ser interpretados como estimativas, e estão sujeitas a uma margem de erro, informada na parte inferior do gráfico.

    Como a amostra foi reduzida para menos de 3 mil depois de agrupar por zona eleitoral, ele não atinge um tamanho de amostra efetiva (ESS) suficiente para retornar métricas de erro confiáveis, mas os fluxos obtidos mostram uma variância pequena e proporções plausíveis.



    [^5]: **Portal de Dados Abertos do TSE**. [Presidente - Votação por seção eleitoral - 2026](https://dadosabertos.tse.jus.br/dataset/resultados-2026/resource/01ea4ccd-f443-469c-9f29-c69ff97f7d4c)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Fluxo de votos estimado

    O fluxo de votos estimado mostra, diferente do esperado pela equipe do Flávio e de alguns analistas, o Lula conseguindo atrair uma uma parcela relevante do eleitorado que tinha votado em candidatos que não passaram para o segundo turno, e junto com isso, também a maior parte dos que se abstiveram e dos que votaram branco e nulo.
    """)
    return


@app.cell
def _(d, votos):
    X, Y, report = d.build_matrices(
        votos.df,
        position_code=1,
        candidate_a_number=22,
        candidate_b_number=13,
        electorate_total=158_700_000,
        granularity="ZONA",
    )
    return X, Y


@app.cell(hide_code=True)
def _(Path, X, Y, d, f, mo):
    mo.stop(Path(d.DOWNLOADS_DIR, "model_flows.csv").is_file())
    model = (
        f.DirichletTransfer(
            idx_a=0,
            idx_b=1,
            u_cols=[2, 3, 4],
            tune=1000,
            draws=1000,
            max_depth=16,
        )
        .fit(X.values, Y.values)
    )
    model.summary().to_csv(Path(d.DOWNLOADS_DIR, "model_summary.csv"), index=True)
    model.flows().to_csv(Path(d.DOWNLOADS_DIR, "model_flows.csv"), index=False)
    return


@app.cell
def _(Path, d, figcaption, g, mo, pd):
    flows = pd.read_csv(Path(d.DOWNLOADS_DIR, "model_flows.csv"))
    summary = pd.read_csv(Path(d.DOWNLOADS_DIR, "model_summary.csv"))
    _avg_percent_error = str(
        round(
            ((1.96 * summary["sd"] * 100) / (summary["mean"] * 100)).sum(), 2
    )
    ).replace(".", ",")

    _plot = g.SankeyPlot(
        flows,
        left_labels=["Outros candidatos", "Branco/Nulo", "Abstenções"],
        right_labels=["Flávio", "Lula", "Branco/Nulo", "Abstenções"],
        right_colors=["#008181", "#942020", "#212c38", "#ced6de"],
        disclaimer=(
            "1. Estimado por um modelo de inferência com restrição: Assume-se "
            "que os eleitores de Lula e Flávio Bolsonaro não mudaram seu voto "
            "entre o primeiro e o segundo turno.\n"
            "2. Número de abstenções obtido pela discrepância entre quantidade "
            "de votos registrados e quantidade de eleitores aptos divulgados. "
            "As abstenções foram distribuídas igualmente entre as zonas "
            "eleitorais nos dados de treinamento do modelo."
            "\n\nAs quantidades variam com margem de erro média de "
            f"±{_avg_percent_error}% do valor informado.\n\n"
            "Fonte: vitorlins.com.br"
        )
    )
    _plot.cfg["disclaimer"]["clearance"] = 0.35
    mo.vstack([
        _plot.show(),
        figcaption("Gráfico 1: Fluxos de votos estimados"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Este resultado é plausível porque se aproxima muito do resultado obtido nas urnas, incluindo as quantidades de transferência de votos, 3 milhões para Flávio e 10 milhões para Lula[^1], além dos votos Branco e Nulo totais no primeiro e no segundo turno: aproximadamente 6 e 4 milhões, respectivamente[^1].

    A quantidade total de abstenções é medida pela discrepância entre a quantidade de votos registrada e a quantidade de eleitores aptos segundo o TSE[^2], para a estimativa, o modelo distribui a quantidade total de abstenções entre todas as seções eleitorais. Além de assumir que não há transferência de votos entre os finalistas, o fato de assumir que a abstenção está distribuida igualmente entre todas as seções eleitorais pode explicar a leve discrepância entre os números oficiais e a estimativa.

    Para justificar os 10 milhões de votos recebidos pelo candidato Lula, o modelo mediu uma transferência de aproximadamente 4 milhões de votos vindo de pessoas que não foram votar no primeiro turno, este número pode ser verificado em [`model_flows.csv`](https://github.com/VFLins/mini_projects/blob/main/eleicoes2026/data/model_flows.csv), terceira linha, segunda coluna.

    Esta grande transferência faz sentido quando comparamos a abordagem das campanhas eleitorais durante o segundo turno já discutidas. O cenário que se pode interpretar do resultado do modelo é:

    1. Flávio recebeu os três milhões de votos "garantidos", dos eleitores que o tinham como segunda opção no primeiro turno, mas como a atvidade da campanha diminuiu depois do resultado do primeiro turno, não conseguiu mais eleitores além desses, enquanto que

    2. A campanha mais ativa de Lula conseguiu convencer os eleitores que ficaram indecisos depois de ver seu candidato perder no primeiro turno, além de converter alguns votos inválidos e muitos eleitores que se abstiveram no primeiro turno.

    Se não tivesse convencido as pessoas que não foram votar no primeiro turno, Lula poderia não ter recebido votos o suficiente para ganhar, enquanto que a suspeição das urnas eletrônicas inflada pelos bolsonaristas[^3] pode acabar fazendo o efeito contrário, desincentivando o comparecimento de seus eleitores à votação.



    [^1]: **TSE**. [Eleição Geral Ordinária 2026](https://resultados.tse.jus.br/oficial/app/index.html#/eleicao/6257/uf/br/cargo/1/vis/nominal/resultados)

    [^2]: **TSE**. [Faltam 30 dias: Brasil tem mais de 158 milhões de eleitoras e eleitores aptos a votar](https://www.tse.jus.br/comunicacao/noticias/2026/Setembro/faltam-30-dias-brasil-tem-mais-de-158-milhoes-de-eleitoras-e-eleitores-aptos-a-votar)

    [^3]: **G1**. [Flávio Bolsonaro repete discurso do pai sobre urnas e amplia desafios para crescer fora da base bolsonarista](https://g1.globo.com/politica/blog/julia-duailibi/post/2026/07/22/flavio-bolsonaro-urnas.ghtml)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rejeição e intenções de voto

    Outro fato importante que levantou a indignação do Flávio Bolsonaro e seus apoiadores foi a grande diferença entre a quantidade de votos nas urnas e as intenções de votos medidas pelas pesquisas realizadas entre o primeiro e o segundo turno.

    Segundo auditoria independente de Barberia et al. (2026)[^1], os institutos de pesquisa apresentaram um viés consistente entre os turnos. O estudo mostrou que a maioria das pesquisas superestimou o desempenho do candidato Lula no primeiro turno e depois da votação, passou a fazer o mesmo para o Flávio Bolsonaro no segundo.

    Muitas pesquisas apontavam vantagem para Flávio Bolsonaro nas intenções de votos, e resultados similarmente favoráveis a ele na rejeição. Se um candidato é rejeitado por aproximadamente de 50% dos eleitores, não é impossível que ele tenha um desempenho competitivo no primeiro turno, mas tenha um segundo turno muito difícil tentando disputar a parcela de eleitores que ainda não votou nele no primeiro turno, mas também não o rejeita.

    Entre os bolsonaristas, este parecia ser a situaçaõ do Lula, as pesquisas apontavam um nível de rejeição mais alta e intenções de votos mais baixas para ele. O que indicaria uma grande dificuldade de conquistar votos suficientes para virar a disputa ao seu favor no segundo turno.

    A quantidade de votos conquistáveis por um candidato pode ser definida pela quantidade de eleitores que ainda não decidiram o voto, mas que ainda não o rejeitam. Esta quantidade pode ser estimada pelos dados divulgados pelas pesquisas eleitorais, mas não pode ser confiavelmente mapeada das pesquisas para as votações, por alguns motivos:

    1. Viés apresentado pelas pesquisas pode também mostrar valores desajustados com a rejeição real, além dos desajustes já percebidos nas intenções de votos[^1];

    2. Distribuição do comparecimento às urnas e votos inválidos não são diretamente alinhados com as respostas "Não opinou" ou "Não soube responder" nas pesquisas.

    /// warning | Aviso
    Com limitações tão importantes, um estudo de potencial de votos teria resultados muito pouco confiáveis para se usar seriamente como parte de uma estratégia de campanha ou em um estudo da transferência de votos. Por isso todo o progresso nesta seção da análise deve ser considerado experimental e exploratória.
    ///

    Como as pesquisas não costumam divulgar o cruzamento de dados entre intenções de votos e rejeição, teremos que estimar a distribuição da rejeição a cada candidato entre entre os que ainda não decidiram o voto e os que já decidiram votar no adversário.



    [^1]: **Jota**. [A eleição de 2026 terminou. Agora, abram seus dados](https://www.jota.info/opiniao-e-analise/colunas/lorena-barberia/a-eleicao-de-2026-terminou-agora-abram-seus-dados) por Lorena G. Barberia, Natália de Paula Moreira e Gustavo Fernandes de Paula
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Dados de pesquisas eleitorais

    A rejeição é medida em um questionário por uma pergunta do tipo "Em qual(is) candidatos você não votaria de jeito nenhum?", enquanto que a intenção de voto A diferença entre a rejeição e a intenção de voto de um candidato é composto por dois grupos: 1. eleitores que ainda não decidiram o voto; e 2. eleitores decididos a votar no candidato adversário.

    Este segundo grupo também pode estar presente entre os eleitores que rejeitam o candidato observado. Para entender quantos votos podem ser adquiridos por um candidato no segundo turno, precisamos destas informações e da distribuição de eleitores.

    Quando existe distinção entre pesquisa estimulada e espontânea, vamos preferir a primeira. Algumas pesquisas não distinguem entre o tipo de abordagem, nestes casos, vamos simplesmente usar os valores que estejam dados.

    Aqui consideramos que os eleitores com intenção de votar em um candidato terão respondido "Pretendo votar neste candidato com certeza", já a rejeição ao candidato será medida pela proporção de respostas "Não votaria neste candidado de maneira alguma".

    Isto quer dizer que dificilmente a mesma pessoa estará entre os eleitores que declararam intenção de voto e ao mesmo tempo rejeitam o mesmo candidato, o que facilita um pouco a modelagem a seguir.

    A primeira etapa desta análise consiste em montar um conjunto de dados com as intenções de voto e rejeição, todas as pesquisas selecionadas foram feitas após os resultados do primeiro turno:

    1. [Futura](https://www.futurainteligencia.com.br/pesquisas): BR-00650/2026, BR-00650/2026, BR-06715/2026
    2. [Data Folha](https://datafolha.folha.uol.com.br/): BR-09709/2026 e BR-09540/2026
    3. [Gerp](https://www.gerp.com.br/relatorios.html): BR-07877/2026, BR-05187/2026, BR-03835/2026, e BR-09327/2026
    4. [Nexus](https://www.nexus.fsb.com.br/estudos-divulgados/): BR-07997/2026, BR-044499/2026 e BR-08234/2026
    5. [Palver](https://www.palver.com.br/survey): BR-00198/2026, BR-08028/2026, BR-04612/2026, e BR-01794/2026
    6. [Poder Data](https://www.poder360.com.br/poderdata/): BR-08134/2026, BR-07926/2026, BR-04258/2026, BR-02586/2026 e BR-01209/2026
    7. [Quaest](https://quaest.com.br/relatorios-quaest/): BR-08535/2026 e BR-09158/2026
    8. [Vox Brasil](https://voxbrasilpesquisas.com.br/imprensa/): BR-09623/2026, BR-04332/2026 e BR-03259/2026
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Metodologia

    Para dizer exatamente quantos votos um candidato pode receber, ainda considerando que um candidato $A$ não pode conquistar que já está decidido por votar em seu adversário $B$, isto significa que o percentual de eleitores conquistaveis por A, $p_A$ é composto pelos percentuais de eleitores que não decidiram o voto $v_U$ e ao mesmo tempo também não o rejeitam:

    $$
    p_A = v_U \times (1 - P(\text{rejeita A} \mid \text{indeciso})) \tag 1
    $$

    Os eleitores que rejeitam o candidato $A$ estarão distribuídos entre os que não decidiram o voto $v_U$ e os que já decidiram votar no candidato adversário $v_B$. No cenário mais favorárel, todos os que o rejeitam já decidiram votar no adversário, isto deixa uma proporção conquistável maior, e no pior cenário, todos os indecisos já o rejeitam, o que significa que a decisão deles será apenas entre votar no adversário, se abster ou votar nulo/branco.
    """)
    return


@app.cell
def _(d, figcaption, mo):
    mo.vstack([
        mo.image(src=d.PROJECT_ROOT / "static" / "scenarios.png"),
        figcaption("Figura 1: Cenários de melhor x pior distribuição de rejeição"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Como as pesquisas não costumam entregar estatísticas cruzadas de rejeição e intenção de votos, não podemos saber exatamente o percentual de indecisos que rejeitam cada candidato. Esta rejeição pode estar distribuída em qualquer ponto entre o pior e o melhor cenário, para medir estes cenários-limite, vamos nos basear nos limites de Fréchet (1951)[^5] [^6].

    $$
    \max(0, v_U + (1 - r_A) - 1) \le p_A \le \min(v_U, (1 - r_A)) \tag 2
    $$

    O limite superior original $\min(v_U, (1 - r_A))$ pode ficar muito amplo se a rejeição ao candidato $A$ for maior que as intenções de voto ao candidato $B$, neste caso, os votos conquistáveis serão os votos indecisos menos a diferença entre $r_A$ e  $v_B$. Com o ajuste no limite superior, teremos:

    $$
    \max(0, v_U + (1 - r_A) - 1) \le p_A \le v_U - \max(0, r_A - v_B) \tag 3
    $$



    [^5]: **Mathematics Magazine**. [Abstract Sets, Abstract Spaces and General Analysis
    ](https://doi.org/10.1080/19300980.1951.12467234)

    [^6]: **Wikipedia**. [Fréchet inequalities](https://en.wikipedia.org/wiki/Fr%C3%A9chet_inequalities)
    """)
    return


@app.cell
def _(d, figcaption, mo):
    mo.vstack([
        mo.image(src=d.PROJECT_ROOT / "static" / "scenarios2.png"),
        figcaption("Figura 2: Cenários de votos conquistáveis sem x com ajuste conceitual"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Os limites conqistáveis sem ajuste são efetivamente os limites de Fréchet aplicados à este problema, já o limite superior com ajuste é a estimativa adequada para o pressuposto de que quem rejeita o candidato A também não pode ter declarado a intenção de voto nele.

    Em outras palavras, quem rejeita o candidato A, está em um de dois grupos: 1- Não decidiu o voto ainda, ou 2- Já decidiu votar em seu adversário. Assim podemos dizer que a distribuição da rejeição a $A$ depende de como estes dois grupos estão distribuidos através de probabilidades condicionais:

    $$
    r_A = v_B \cdot P(\text{rejeita A} \mid \text{vota B}) + v_U \cdot P(\text{rejeita A} \mid \text{indeciso}) \tag 4
    $$

    Como não sabemos antecipadamente qual a distribuição dentro desses grupos, vamos criar um parâmetro $\beta$ para testar diferentes distribuições possíveis:

    $$
    \beta = \frac{ P(\text{rejeita A} \mid \text{indeciso}) }{ P(\text{rejeita A} \mid \text{vota B}) } \tag 5
    $$

    Nesta configuração, podemos dizer que quando $\beta=1$, a proporção de rejeições é igual entre os eleitores do adversário e indecisos. Aumentando o valor, a proporção passa a ser maior entre os indecisos, e valores entre 0 e 1 aumentam a proporção entre os eleitores do candidato adversário.
    """)
    return


@app.cell
def _(d, figcaption, mo):
    mo.vstack([
        mo.image(src=d.PROJECT_ROOT / "static" / "scenarios3.png"),
        figcaption(r"Figura 3: Exemplos de distribuição de rejeição estimada para diferentes valores de $\beta$"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Agora podemos usar o $\beta$ da equação 5 que criamos para resolver a equação 4 da probabilidade condicional de um eleitor que não decidiu o voto rejeitar o candidato $A$:

    $$
    P(\text{rejeita A} \mid \text{indeciso}) = \beta \cdot \frac{r_A}{v_B + \beta \cdot v_U} \tag 6
    $$

    Com isto definido, podemos substituir a equação 6 na definição inicial da equação 1, isto define formalmente o potencial de receber votos de um candidato para qualquer valor de $\beta$:

    $$
    p_A = v_U \times \left(1 - \frac{\beta \cdot r_A}{v_B + \beta \cdot v_U}\right) \tag 7
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Potencial de votos versus Votos obtidos

    Agora que sabemos como medir a proporção de votos que podem ser conquistados, podemos encontrar o valor de $\beta$ que aproxima o teto ajustado do resultado real das eleições. Isto nos dará um parâmetro para fixar um $\beta$ para cada candidato.

    As conclusões que podem ser tiradas desta abordagem assumem que ambos os candidatos conseguiram aproximadamente todos os votos que poderiam conseguir, e que portanto, nenhum eleitor que tenha anulado o voto ou deixado de votar o fez por falta de esforços de convencimento das partes.

    Como vimos antes, isto só é verdade para o candidato Lula, e portanto, o valor de $\beta$ obtido para o candidato Flávio pode ser mais baixo do que o que medimos aqui.

    A proporção de votos conquistadas no gráfico abaixo é medida pela diferença de votos entre o primeiro e o segundo turno, dividido pela quantidade de votos totais no segundo turno.
    """)
    return


@app.cell
def _(d, f, figcaption, g, mo, pd, ticker, vote_stats):
    _p_acquired_a = (
        (vote_stats["r2"]["flavio"]["n"]
        - vote_stats["r1"]["flavio"]["n"])
        / vote_stats["r2"]["votos"]["n"]
    )
    _p_acquired_b = (
        (vote_stats["r2"]["lula"]["n"]
        - vote_stats["r1"]["lula"]["n"])
        / vote_stats["r2"]["votos"]["n"]
    )

    vas = d.rpolls.df["vote_a"]
    vbs = d.rpolls.df["vote_b"]
    ras = d.rpolls.df["reject_a"]
    rbs = d.rpolls.df["reject_b"]
    limits = [
        f.vote_potential(va, vb, ra, rb, beta=0.55)
        for va, vb, ra, rb in zip(vas, vbs, ras, rbs)
    ]
    high_limits = [
        f.vote_potential(va, vb, ra, rb, beta=0.1)
        for va, vb, ra, rb in zip(vas, vbs, ras, rbs)
    ]

    _df = pd.DataFrame(
        [
            pd.Series(vp.a.est for vp in limits),
            pd.Series(vp.b.est for vp in high_limits),
        ],
        index=["β=0,55 Flávio", "β=0,10 Lula"]
    ).T

    _df = pd.melt(_df)
    _df[["group", "variable"]] = _df["variable"].str.split(" ", n=1, expand=True)
    _df = pd.concat(
        [
            _df,
            pd.DataFrame(
                [("Flávio", _p_acquired_a, "Votos adquiridos")],
                columns=["variable", "value", "group"],
            ),
            pd.DataFrame(
                [("Lula", _p_acquired_b, "Votos adquiridos")],
                columns=["variable", "value", "group"],
            ),
        ],
    )

    _plot = g.GroupedBarPlot(
        values=_df["value"],
        categories=_df["variable"],
        groups=_df["group"],
        horizontal=True,
        disclaimer=(
            f"Estimativa produzida com dados de {len(d.rpolls.polls)} pesquisas "
            "eleitorais de 8 institutos diferentes. As barras escuras mostram a "
            "estimativa média da proporção de votos conquistáveis, dado um valor "
            "do coeficiente β que a aproxima da proporção de votos efetimvamente "
            "conquistados, as barras de erro mostram os valores máximo e mínimo.\n\n"
            "Um β maior é um indicativo de que uma proporção maior dos eleitores que se "
            "tornaram indecisos depois do primeiro turno já rejeitava este candidato, "
            "e portanto, dificilmente passariam a votar nele no segundo turno.\n\n"
            "Fonte: vitorlins.com.br"
        ),
    )
    _plot.cfg["bar"]["colors"] = ["#212c38", "#008181", "#ced6de"]
    _plot.cfg["bar"]["error_colors"] = ["#ced6de"]
    _plot.cfg["disclaimer"]["clearance"] = 0.44
    (
        _plot.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    mo.vstack([
        _plot.show(),
        figcaption("Gráfico 2: Conquista de votos ex post"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Não foi possível encotrar um valor de $\beta$ que aproximasse a média das estimativas mais do que o que já está mostrado no gráfico, valores abaixo de 0,1 não têm impacto no resultado.

    Uma possível explicação para os votos adquiridos pelo Lula estar acima da média das estimativas está na própria natureza das pesquisas: As respostas "não soube responder" não podem ser mapeadas de nenhuma maneira aceitável para as abstenções e votos inválidos nas urnas.

    Uma segunda explicação plausível, se baseia no fato já identificado de que as pesquisas eleitorais de segundo turno apresentavam viés favorável ao Flávio Bolsonaro nas intenções de votos, este viés também pode ter se refletido nas rejeições.

    Os vieses das instituições de pesquisa se anulariam se fossem distribuídos normalmente, mas a maioria das casas apresentou viés a favor do Flávio acima da margem de erro. Com níveis menores de rejeição, a média das estimativas poderia ser mais alta do que o observado aqui.

    Os dados das pesquisas não permitem dizer quantas pessoas que se abstiveram no primeiro turno passariam a votar no segundo, se desconsiderar-mos os aproximadamente 4 milhões de votos adquiridos por Lula desta fonte, a média das estimativas passaria a ficar próxima dos votos adquiridos.


    ### Motivos para votar

    Outra coisa que vale análise é a grande diferença entre os coeficientes $\beta$ estimados para cada candidato, se esta diferença é verdadeira, significa pode existir uma diferença importante no motivo para o voto entre os eleitores de cada candidato.

    Um valor de $\beta$ muito baixo para um candidato pode indicar que uma grande parte do seu eleitorado vota em você por rejeição ao candidato adversário, isso pode parecer bom à primeira vista, porque pode indicar um eleitorado conquistável maior.

    Mesmo assim, isto pode ser uma fraqueza, uma vez que seus eleitores podem ter opiniões mais fortes contra o seu adversário que ao seu favor, isto te torna competitivo contra este candidato em específico, mas fraco contra outros.

    Para testar se este era o caso do candidato Lula, vamos comparar alguns dados das pesquisas e comparar com a correlação entre as intenções de votos e níveis de rejeição cruzados.
    """)
    return


@app.cell
def _(d, figcaption, g, mo, ticker):
    _plot = g.ScatterPlot(
        x=d.rpolls.df["vote_a"],
        y=d.rpolls.df["reject_b"],
        x_label="Vota Flávio Bolsonaro",
        y_label="Rejeita Lula",
        with_regression=True,
        title="Intenção de votos ao\nFlávio x Rejeição ao Lula",
        disclaimer=(
            f"Produzido com dados de {len(d.rpolls.polls)} pesquisas de 8 institutos "
            'diferentes realizadas após os resultados do primeiro turno. "Vota Flávio '
            'Bolsonaro" representa o percentual de entrevistados que responderam '
            '"vou votar no candidato com certeza" na pesquisa estimulada, enquanto que '
            '"Rejeita Lula" representa os entrevistados que responderam "não '
            'votaria no candidato de jeito nenhum".\n\n'
            "Fonte: vitorlins.com.br"
        ),
    )
    _plot.cfg["disclaimer"]["clearance"] = 0.4
    (
        _plot.ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    (
        _plot.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )

    mo.vstack([
        _plot.show(),
        figcaption("Gráfico 3: Intenção de votos ao Flávio x Rejeição ao Lula"),
    ])
    return


@app.cell
def _(d, figcaption, g, mo, ticker):

    _plot = g.ScatterPlot(
        x=d.rpolls.df["vote_b"],
        y=d.rpolls.df["reject_a"],
        x_label="Vota Lula",
        y_label="Rejeita Flávio Bolsonaro",
        with_regression=True,
        title="Intenção de votos ao\nLula x Rejeição ao Flávio",
        disclaimer=(
            f"Produzido com dados de {len(d.rpolls.polls)} pesquisas de 8 institutos "
            'diferentes realizadas após os resultados do primeiro turno. "Vota Lula" '
            'representa o percentual de entrevistados que responderam "vou votar no '
            'candidato com certeza" na pesquisa estimulada, enquanto que "Rejeita '
            'Flávio Bolsonaro" representa os entrevistados que responderam "não '
            'votaria no candidato de jeito nenhum".\n\n'
            "Fonte: vitorlins.com.br"
        ),
    )
    _plot.cfg["disclaimer"]["clearance"] = 0.4
    (
        _plot.ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    (
        _plot.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    mo.vstack([
        _plot.show(),
        figcaption("Gráfico 4: Intenção de votos ao Lula x Rejeição ao Flávio"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A análise de correlação indica uma correlação forte entre rejeição e intenção de  votos, mas apenas nas intenções de voto ao Flávio Bolsonaro, quando observamos a intenção de voto no Lula contra a rejeição ao Flávio, esta correlação passa a ser muito fraca para ser considerada relevante. Isto fica evidente no coeficiente de inclinação com confiança de 37,9%, que idealmente seria igual ou superior 95%, como nos demais.

    Este resultado discorda do que obtivemos na análise de conquista de votos, mas é coerente com o resultado do questionário da pesquisa da Palver (BR-01794/2026, página 29), onde os entrevistados que votariam no Lula justificavam seu voto principalmente com a "Defesa da democracia e direitos", enquanto que os eleitores do Flávio justificaram principalmente com a "Rejeição ao Lula e o PT".

    Esta análise de correlação mede a distribuições de intenções de voto e rejeição agregados pelas pesquisas, e não leva em consideração as margens de erro, por isso, tem intenção de determinar o comportamento individual de cada eleitor, mas de ajudar a identificar um padrão entre as pesquisas.

    A presença de uma correlação mais forte as intenções de voto ao Flávio e a rejeição à Lula pode ser um indicativo de que o coeficiente $\beta$ verdadeiro do candidato era mais baixo do que o medido. A métrica pode ter sido superestimada por que ele teve um desempenho abaixo do esperado em atrair votos dos eleitores de candidatos derrotados no primeiro turno, o que é coerente com a expectativa de analistas políticos mencionados antes.
    """)
    return


@app.cell(hide_code=True)
def _(mo, vote_stats):
    mo.md(rf"""
    ## Conclusão

    A estimativa do fluxo de votos estimou aproximadamente 4 milhões de votos vindos das abstenções no primeiro turno, Lula ganhou com vantagem de {str(round((vote_stats["r2"]["lula"]["n"] - vote_stats["r2"]["flavio"]["n"]) / 1_000_000, 1)).replace(".", ",")} Milhões. Isto pode indicar que a camapanha de Lula poderia ter falhado se tivesse se concentrado apenas em conquistar votos de quem votou em outros candidatos no primeiro turno.

    A mesma estimativa também mostrou que Flávio não recebeu votos dos antes absentos, e não recebeu todos os votos que esperava dos outros candidatos mais bem colocados, o que é coerente com o fato do abrandamento da sua campanha eleitoral no segundo turno, em contraste com a intensificação da campanha do seu adversário.

    Após analisar a quantidade de votos conquistáveis, observamos que Lula conseguiu mais votos do que seria esperado pelas pesquisas eleitorais, o que pode ser explicado tanto pelo viés a favor do Flávio que quase todas as pesquisas eleitorais apresentaram após o primeiro turno, quanto pelo abrandamento de sua campanha.

    Flávio mostra um alto nível de correlação entre intenções de votos com rejeição ao adversário, uma distribuição com $\beta$ mais baixo que o medido (como na figura 3). Não foi investigado mais a fundo aqui, mas isto pode confirmar que ele teria mais capacidade de atrair votos dos eleitores de outros candidatos.

    Com muitos de seus votos sendo justificados pela rejeição ao seu adversário, Flávio se beneficiaria se sua campanha tivesse focado em melhorar sua imagem, mapeando e atacando os maiores receios em relação à ele entre os eleitores indecisos, além de tentar convencer seus apoiadores a votar, deixando de lado a suspeita às urnas.
    """)
    return


if __name__ == "__main__":
    app.run()
