from dataclasses import dataclass
import pandas as pd
import marimo as mo
import urllib.request
from pathlib import Path
import zipfile


PROJECT_ROOT = Path(__file__).parent.resolve()
DOWNLOADS_DIR = PROJECT_ROOT / "data"

# Presidente - Votação por seção eleitoral - 2026
# https://dadosabertos.tse.jus.br/dataset/resultados-2026/resource/01ea4ccd-f443-469c-9f29-c69ff97f7d4c
VOTOS_URL = (
    "https://cdn.tse.jus.br/estatistica/sead/odsele/"
    "votacao_secao/votacao_secao_2026_BR.zip"
)
VOTOS_ZIP = VOTOS_URL.split("/")[-1]
VOTOS_CSV = Path(VOTOS_ZIP).with_suffix(".csv")


class VoteData:
    def __init__(self):
        self.ask_download = (
            mo.ui.checkbox(value=True, label="Baixar os dados de votação (1,6 GB)")
            .form(submit_button_label="Continuar")
        )

    @property
    def file_exists(self) -> bool:
        return (DOWNLOADS_DIR / VOTOS_CSV).is_file()


    def download(self):
        if self.ask_download.value is False:
            print("Ignorando download como solicitado pelo usuário.")
            return

        if not self.file_exists:
            print("Fazendo download dos dados...")
            urllib.request.urlretrieve(VOTOS_URL, VOTOS_ZIP)
            print(f"Extraindo arquivos para {DOWNLOADS_DIR}")
            zipfile.ZipFile(PROJECT_ROOT / VOTOS_ZIP).extractall(DOWNLOADS_DIR)
            print(f"Excluindo arquivo compactado {PROJECT_ROOT / VOTOS_ZIP}")
            (PROJECT_ROOT / VOTOS_ZIP).unlink()
            print("Download concluído.")
        else:
            print("Dados já encontrados no diretório esperado, ignorando download.")

    def load(self):
        if not self.file_exists:
            print("Ignorando carregamento, dados não encontrados.")
            return

        print("Carregando dados...")
        self.df = pd.read_csv(
            DOWNLOADS_DIR / "votacao_secao_2026_BR.csv",
            sep=";",
            encoding="latin1",
            usecols=[
                "CD_CARGO",
                "CD_MUNICIPIO",
                "NR_ZONA",
                "NR_SECAO",
                "NR_VOTAVEL",
                "NM_VOTAVEL",
                "NR_TURNO",
                "QT_VOTOS",
                "NR_SECAO",
                "NR_ZONA"
            ],
            dtype={
                "CD_CARGO": "int16",
                "NR_VOTAVEL": "int16",
                "NM_VOTAVEL": "category",
                "NR_TURNO": "int16",
                "QT_VOTOS": "int64",
                "NR_SECAO": "int64",
                "NR_ZONA": "int64",
            }
        )
        print("Dados carregados.")


class RejectionPolls:
    @property
    def polls(self) -> list[pd.Series]:
        return self._polls

    def __init__(self):
        self._polls: list[pd.Series] = []

    def add(
        self,
        n: int,
        ic: float,
        name: str,
        vote_a: float,
        vote_b: float,
        reject_a: float,
        reject_b: float,
    ):
        """Adds a poll dataset with vote intentions and rejections.

        :param n: Poll sample size.
        :param ic: Poll estimated confidence interval in percentage points.
        :param name: Poll name, identifying it in the dataset.
        :param vote_flavio: Percentage of votes declared to candidate Flávio.
        :param vote_lula: Percentage of votes declared to candidate Lula.
        :paran reject_flavio: Percentage of voters declared not voting on candidate Flávio.
        :paran reject_lula: Percentage of voters declared not voting on candidate Lula.
        """
        vote_a_hi, vote_a_lo = vote_a + ic, vote_a - ic
        vote_b_hi, vote_b_lo = vote_b + ic, vote_b - ic
        reject_a_hi, reject_a_lo = reject_a + ic, reject_a - ic
        reject_b_hi, reject_b_lo = reject_b + ic, reject_b - ic
        n_va = n * vote_a
        n_vb = n * vote_b
        n_ra = n * reject_a
        n_rb = n * reject_b
        n_ua = n - n_va - n_ra
        n_ub = n - n_vb - n_rb
        unsure_a = n_ua / n
        unsure_b = n_ub / n
        unsure_a_hi, unsure_a_lo = unsure_a + ic, unsure_a - ic
        unsure_b_hi, unsure_b_lo = unsure_b + ic, unsure_b - ic

        colnames = [
            "n", "ic",
            "vote_a", "vote_a_hi", "vote_a_lo",
            "vote_b", "vote_b_hi", "vote_b_lo",
            "unsure_a", "unsure_a_hi", "unsure_a_lo",
            "unsure_b", "unsure_b_hi", "unsure_b_lo",
            "reject_a", "reject_a_hi", "reject_a_lo",
            "reject_b", "reject_b_hi", "reject_b_lo",
            "n_vote_a", "n_vote_b",
            "n_unsure_a", "n_unsure_b",
            "n_reject_a", "n_reject_b",
        ]

        self._polls.append(pd.Series(
            [
            n, ic,
            vote_a, vote_a_hi, vote_a_lo,
            vote_b, vote_b_hi, vote_b_lo,
            unsure_a, unsure_a_hi, unsure_a_lo,
            unsure_b, unsure_b_hi, unsure_b_lo,
            reject_a, reject_a_hi, reject_a_lo,
            reject_b, reject_b_hi, reject_b_lo,
            n_va, n_vb,
            n_ua, n_ub,
            n_ra, n_rb,
        ],
        name=name,
        index=colnames
        ))
        self.df = pd.DataFrame(data=self._polls)


import numpy as np
import pandas as pd

SECTION_KEY = ["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]

GRANULARITY_KEYS = {
    "MUNICIPIO": ["CD_MUNICIPIO"],
    "ZONA": ["CD_MUNICIPIO", "NR_ZONA"],  # NR_ZONA só é única dentro do município
    "SECAO": SECTION_KEY,
}

BLANK_OR_NULL_CODES = {95, 96, 97}


def build_matrices(
    votes_df,
    position_code,
    candidate_a_number,
    candidate_b_number,
    electorate_total,
    granularity="SECAO",
):
    """Build the X (Round 1) and Y (Round 2) matrices of the ecological model.

    Abstention is computed per voting section, as the difference in total
    votes between rounds in the same section: the round with fewer votes
    receives the difference as abstention and the other receives zero. The
    electorate of a section is therefore the larger of the two vote totals.
    Sections are then aggregated to the requested granularity, so every row
    of X and Y sums to the electorate of its unit.

    :param votes_df: VOTACAO_SECAO already loaded as a DataFrame (both
        rounds). It must contain ``CD_MUNICIPIO``, ``NR_ZONA``, ``NR_SECAO``,
        ``CD_CARGO``, ``NR_TURNO``, ``NR_VOTAVEL`` and ``QT_VOTOS``.
    :param position_code: ``CD_CARGO`` of the race (e.g. 1 = President,
        3 = Governor).
    :param candidate_a_number: ``NR_VOTAVEL`` of candidate A (Round 2
        finalist).
    :param candidate_b_number: ``NR_VOTAVEL`` of candidate B (Round 2
        finalist).
    :param electorate_total: Total eligible voters.
    :param granularity: Unit of analysis of the rows: ``"MUNICIPIO"``,
        ``"ZONA"`` or ``"SECAO"`` (default).
    :returns: ``(X, Y, report)``. X columns are ``[A, B, OUT, BN, ABS]`` and
        Y columns are ``[A, B, BN, ABS]``; with the VUTransfer class use
        ``idx_a=0, idx_b=1, u_cols=[2, 3, 4]``.
    """
    granularity = granularity.upper()
    if granularity not in GRANULARITY_KEYS:
        raise ValueError(
            f"granularity must be one of {list(GRANULARITY_KEYS)}, "
            f"got {granularity!r}."
        )
    unit_keys = GRANULARITY_KEYS[granularity]

    race_votes = votes_df.loc[
        votes_df["CD_CARGO"] == position_code,
        SECTION_KEY + ["NR_TURNO", "NR_VOTAVEL", "QT_VOTOS"],
    ]
    vote_group = np.select(
        [
            race_votes["NR_VOTAVEL"] == candidate_a_number,
            race_votes["NR_VOTAVEL"] == candidate_b_number,
            race_votes["NR_VOTAVEL"].isin(BLANK_OR_NULL_CODES),
        ],
        ["A", "B", "BN"],
        default="OUT",
    )
    votes_by_section_and_round = (
        race_votes.assign(vote_group=vote_group)
        .groupby(SECTION_KEY + ["NR_TURNO", "vote_group"])["QT_VOTOS"]
        .sum()
        .unstack("vote_group", fill_value=0)
        .reindex(columns=["A", "B", "OUT", "BN"], fill_value=0)
    )

    round1_sections = votes_by_section_and_round.xs(1, level="NR_TURNO")
    round2_sections = votes_by_section_and_round.xs(2, level="NR_TURNO")
    sections_in_both_rounds = round1_sections.join(
        round2_sections, how="inner", lsuffix="_1", rsuffix="_2"
    )

    round1_section_votes = sections_in_both_rounds[
        ["A_1", "B_1", "OUT_1", "BN_1"]
    ].sum(axis=1)
    round2_section_votes = sections_in_both_rounds[
        ["A_2", "B_2", "OUT_2", "BN_2"]
    ].sum(axis=1)
    section_electorate = np.maximum(round1_section_votes, round2_section_votes)

    # Abstention is always derived section by section, regardless of the
    # chosen granularity, so the definition is not diluted by aggregation.
    sections_in_both_rounds["ABS_1"] = section_electorate - round1_section_votes
    sections_in_both_rounds["ABS_2"] = section_electorate - round2_section_votes
    sections_in_both_rounds["ELECTORATE_BASE"] = section_electorate

    has_votes = section_electorate > 0
    sections_kept = sections_in_both_rounds[has_votes]

    units = sections_kept.groupby(level=unit_keys).sum()

    kept_votes_total = units["ELECTORATE_BASE"].sum()
    extra_abstention_total = electorate_total - kept_votes_total
    if extra_abstention_total < 0:
        raise ValueError(
            f"Votes in kept sections ({kept_votes_total:,}) exceed "
            f"electorate_total ({electorate_total:,}); check the territory."
        )
    common_abstention_per_unit = np.round(
        extra_abstention_total * units["ELECTORATE_BASE"] / kept_votes_total
    ).astype(int)
    units["ABS_1"] += common_abstention_per_unit
    units["ABS_2"] += common_abstention_per_unit

    report = {
        "granularity": granularity,
        "sections_round1": len(round1_sections),
        "sections_round2": len(round2_sections),
        "sections_kept": len(sections_kept),
        "units_kept": len(units),
        "net_abstention_part": int(
            sections_in_both_rounds.loc[has_votes, "ABS_1"].sum()
        ),
        "common_abstention_added": int(common_abstention_per_unit.sum()),
        "abstention_rate_round1": float(units["ABS_1"].sum() / electorate_total),
        "abstention_rate_round2": float(units["ABS_2"].sum() / electorate_total),
    }

    round1_matrix = units[["A_1", "B_1", "OUT_1", "BN_1", "ABS_1"]].copy()
    round1_matrix.columns = ["A", "B", "OUT", "BN", "ABS"]
    round2_matrix = units[["A_2", "B_2", "BN_2", "ABS_2"]].copy()
    round2_matrix.columns = ["A", "B", "BN", "ABS"]
    return round1_matrix, round2_matrix, report


# Usando:
# Candidato A: Flávio Bolsonaro
# Candidato B: Lula
rpolls = RejectionPolls()

rpolls.add(
    n=2000, ic=0.022,
    name="futura1_BR-00650/2026",
    vote_a=0.50, vote_b=0.466, reject_a=0.454, reject_b=0.486,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura2_BR-03761/2026",
    vote_a=0.49, vote_b=0.475, reject_a=0.461, reject_b=0.472,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura3_BR-06715/2026",
    vote_a=0.483, vote_b=0.475, reject_a=0.458, reject_b=0.474,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura4_BR-06614/2026",
    vote_a=0.489, vote_b=0.468, reject_a=0.452, reject_b=0.473,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura5_BR-09726/2026",
    vote_a=0.482, vote_b=0.479, reject_a=0.466, reject_b=0.4662,
)
rpolls.add(
    n=2154, ic=0.02, # revisar
    name="datafolha1", # revisar
    vote_a=0.49, vote_b=0.45, reject_a=0.43, reject_b=0.46,
)
rpolls.add(
    n=2154, ic=0.02, # revisar
    name="datafolha2", # revisar
    vote_a=0.47, vote_b=0.45, reject_a=0.44, reject_b=0.46,
)
rpolls.add(
    n=2154, ic=0.02,
    name="datafolha3_BR-09540/2026",
    vote_a=0.47, vote_b=0.46, reject_a=0.46, reject_b=0.45,
)
rpolls.add(
    n=4050, ic=0.02,
    name="datafolha4_BR-09540/2026",
    vote_a=0.46, vote_b=0.45, reject_a=0.48, reject_b=0.49,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp1_BR-07877/2026",
    vote_a=0.53, vote_b=0.44, reject_a=0.42, reject_b=0.53,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp2_BR-05187/2026",
    vote_a=0.50, vote_b=0.45, reject_a=0.46, reject_b=0.49,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp3_BR-03835/2026",
    vote_a=0.50, vote_b=0.45, reject_a=0.46, reject_b=0.49,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp4_BR-09327/2026",
    vote_a=0.49, vote_b=0.46, reject_a=0.45, reject_b=0.48
)
rpolls.add(
    n=2002, ic=0.02,
    name="nexus1_BR-07997/2026",
    vote_a=0.48, vote_b=0.45, reject_a=0.47, reject_b=0.51,
)
rpolls.add(
    n=2002, ic=0.02,
    name="nexus2_BR-04499/2026",
    vote_a=0.465, vote_b=0.459, reject_a=0.468, reject_b=0.478,
)
rpolls.add(
    n=2000, ic=0.022,
    name="nexus2_BR-04499/2026",
    vote_a=0.47, vote_b=0.46, reject_a=0.465, reject_b=0.491,
)
rpolls.add(
    n=5000, ic=0.023,
    name="palverw7_BR-08028/2026",
    vote_a=0.49, vote_b=0.48, reject_a=0.48, reject_b=0.50,
)
rpolls.add(
    n=5000, ic=0.024,
    name="palverw8_BR-04612/2026,",
    vote_a=0.49, vote_b=0.49, reject_a=0.47, reject_b=0.47,
)
rpolls.add(
    n=5000, ic=0.022,
    name="palverw9_BR-01794/2026",
    vote_a=0.49, vote_b=0.48, reject_a=0.47, reject_b=0.48,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata1_BR-08134/2026",
    vote_a=0.49, vote_b=0.44, reject_a=0.43, reject_b=0.46,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata2_BR-01209/2026",
    vote_a=0.48, vote_b=0.46, reject_a=0.44, reject_b=0.46,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata3_BR-04258/2026",
    vote_a=0.47, vote_b=0.47, reject_a=0.45, reject_b=0.46,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata4_BR-07926/2026",
    vote_a=0.49, vote_b=0.48, reject_a=0.45, reject_b=0.47,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata5_BR-02586/2026",
    vote_a=0.49, vote_b=0.46, reject_a=0.44, reject_b=0.48,
)
rpolls.add(
    n=2154, ic=0.02,
    name="quaest1_BR-08535/2026",
    vote_a=0.45, vote_b=0.44, reject_a=0.52, reject_b=0.47,
)
rpolls.add(
    n=3702, ic=0.02,
    name="quaest2_BR-09158/2026",
    vote_a=0.46, vote_b=0.45, reject_a=0.49, reject_b=0.47,
)
rpolls.add(
    n=2100, ic=0.0215,
    name="vox1_BR-09623/2026",
    vote_a=0.427, vote_b=0.442, reject_a=0.442, reject_b=0.452,
)
rpolls.add(
    n=2100, ic=0.0215,
    name="vox2_BR-04332/2026",
    vote_a=0.446, vote_b=0.464, reject_a=0.453, reject_b=0.453,
)
rpolls.add(
    n=2100, ic=0.0215,
    name="vox3_BR-03259/2026",
    vote_a=0.443, vote_b=0.454, reject_a=0.471, reject_b=0.448,
)
