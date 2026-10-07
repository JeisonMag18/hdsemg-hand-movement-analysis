#!/usr/bin/env python3
"""
03_analyze_results.py

Analisa os CSVs produzidos por 02_full_dataset_analysis.py.

Entrada:
    full_dataset_metrics.csv
    full_dataset_channel_rms.csv

Saídas:
    participant_condition_metrics.csv
    task_summary.csv
    friedman_tests.csv
    frequency_wilcoxon_tests.csv
    kinematic_summary.csv
    channel_profiles_by_task.csv
    figuras PNG para o relatório

Princípios:
- As três repetições são primeiro agregadas dentro de cada participante.
- O participante, e não cada gravação, é a unidade estatística principal.
- RMS é normalizado dentro de cada participante para reduzir diferenças
  interindividuais de amplitude.
- Comparações entre as oito tarefas usam Friedman (medidas repetidas).
- Comparações 0.50 vs 0.75 Hz usam Wilcoxon pareado + correção de Holm.
- O arquivo de canais é usado para perfis de canais; NÃO são gerados mapas 8x8
  enquanto a topologia/orientação física dos canais não estiver explicitamente
  confirmada na documentação do dataset.

Exemplo:
python 03_analyze_results.py ^
  --metrics "C:\\Users\\Jeison\\PycharmProjects\\PythonProject\\results_full_dataset\\full_dataset_metrics.csv" ^
  --channels "C:\\Users\\Jeison\\PycharmProjects\\PythonProject\\results_full_dataset\\full_dataset_channel_rms.csv" ^
  --outdir "C:\\Users\\Jeison\\PycharmProjects\\PythonProject\\analysis_results"
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.stats import friedmanchisquare, wilcoxon


TASK_ORDER = [
    "Index",
    "Middle",
    "Ring-Little",
    "Thumb",
    "I. Pinch",
    "M. Pinch",
    "Tripod",
    "5-Finger",
]

FREQUENCIES = [0.50, 0.75]

MAIN_METRICS = [
    "rms100_edc_mean",
    "rms100_fds_mean",
    "fmed_edc_hz",
    "fmed_fds_hz",
]


def holm_adjust(p_values):
    """Correção de Holm-Bonferroni."""
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    order = np.argsort(p)
    adjusted = np.empty(n, dtype=float)

    running_max = 0.0
    for rank, idx in enumerate(order):
        value = (n - rank) * p[idx]
        running_max = max(running_max, value)
        adjusted[idx] = min(running_max, 1.0)

    return adjusted


def aggregate_repetitions(df):
    """
    Uma linha por participante × tarefa × frequência.
    A média das repetições evita tratar repetições como indivíduos independentes.
    """
    return (
        df.groupby(
            ["subject", "task_id", "task", "freq_hz"],
            as_index=False
        )
        .mean(numeric_only=True)
    )


def add_subject_normalized_rms(cond):
    """
    RMS relativo à média global do próprio participante, separadamente
    para EDC e FDS. Valor 1.0 = média daquele participante.
    """
    out = cond.copy()

    for muscle in ["edc", "fds"]:
        source = f"rms100_{muscle}_mean"
        target = f"{source}_norm"
        denominator = out.groupby("subject")[source].transform("mean")
        out[target] = out[source] / denominator

    return out


def build_task_summary(cond):
    variables = [
        "rms100_edc_mean",
        "rms100_fds_mean",
        "rms100_edc_mean_norm",
        "rms100_fds_mean_norm",
        "fmed_edc_hz",
        "fmed_fds_hz",
        "power_20_450_edc",
        "power_20_450_fds",
        "relpower_20_50_edc",
        "relpower_20_50_fds",
        "relpower_50_100_edc",
        "relpower_50_100_fds",
        "relpower_100_200_edc",
        "relpower_100_200_fds",
        "relpower_200_450_edc",
        "relpower_200_450_fds",
    ]

    rows = []

    for (task, freq), g in cond.groupby(["task", "freq_hz"]):
        for var in variables:
            x = g[var].dropna().to_numpy()
            if x.size == 0:
                continue

            rows.append({
                "task": task,
                "freq_hz": freq,
                "metric": var,
                "n_subjects": x.size,
                "mean": np.mean(x),
                "std": np.std(x, ddof=1) if x.size > 1 else np.nan,
                "sem": (
                    np.std(x, ddof=1) / np.sqrt(x.size)
                    if x.size > 1 else np.nan
                ),
                "median": np.median(x),
                "q25": np.quantile(x, 0.25),
                "q75": np.quantile(x, 0.75),
            })

    return pd.DataFrame(rows)


def friedman_tests(cond):
    rows = []

    for metric in MAIN_METRICS:
        for freq in FREQUENCIES:
            d = cond[cond["freq_hz"] == freq]
            pivot = d.pivot(
                index="subject",
                columns="task",
                values=metric,
            )

            available_tasks = [t for t in TASK_ORDER if t in pivot.columns]
            complete = pivot[available_tasks].dropna()

            if len(available_tasks) < 3 or complete.shape[0] < 2:
                continue

            samples = [complete[t].to_numpy() for t in available_tasks]
            chi2, p = friedmanchisquare(*samples)

            n = complete.shape[0]
            k = len(available_tasks)
            kendall_w = chi2 / (n * (k - 1))

            rows.append({
                "metric": metric,
                "freq_hz": freq,
                "n_subjects": n,
                "n_tasks": k,
                "friedman_chi2": chi2,
                "p_value": p,
                "kendall_W": kendall_w,
            })

    return pd.DataFrame(rows)


def frequency_wilcoxon_tests(cond):
    rows = []

    for metric in MAIN_METRICS:
        metric_rows = []

        for task in TASK_ORDER:
            d = cond[cond["task"] == task]
            pivot = d.pivot(
                index="subject",
                columns="freq_hz",
                values=metric,
            )

            if 0.50 not in pivot.columns or 0.75 not in pivot.columns:
                continue

            paired = pivot[[0.50, 0.75]].dropna()

            if paired.shape[0] < 2:
                continue

            x = paired[0.50].to_numpy()
            y = paired[0.75].to_numpy()

            try:
                stat, p = wilcoxon(y, x, zero_method="wilcox")
            except ValueError:
                stat, p = np.nan, 1.0

            metric_rows.append({
                "metric": metric,
                "task": task,
                "n_subjects": paired.shape[0],
                "mean_050": np.mean(x),
                "mean_075": np.mean(y),
                "median_difference_075_minus_050": np.median(y - x),
                "mean_ratio_075_over_050": np.mean(y / x),
                "wilcoxon_statistic": stat,
                "p_value_raw": p,
            })

        if metric_rows:
            adjusted = holm_adjust([r["p_value_raw"] for r in metric_rows])

            for row, p_adj in zip(metric_rows, adjusted):
                row["p_value_holm"] = p_adj
                row["significant_0p05_holm"] = bool(p_adj < 0.05)
                rows.append(row)

    return pd.DataFrame(rows)


def kinematic_summary(metrics):
    rows = []

    for freq, g in metrics.groupby("freq_hz"):
        x = g["kin_fdom_hz"].dropna().to_numpy()
        err = g["kin_fdom_error_hz"].dropna().to_numpy()

        rows.append({
            "nominal_freq_hz": freq,
            "n_recordings": x.size,
            "mean_fdom_hz": np.mean(x),
            "std_fdom_hz": np.std(x, ddof=1),
            "median_fdom_hz": np.median(x),
            "mean_error_hz": np.mean(err),
            "median_error_hz": np.median(err),
            "n_abs_error_gt_0p10_hz": int(np.sum(np.abs(err) > 0.10)),
        })

    return pd.DataFrame(rows)


def build_channel_profiles(channels):
    """
    Perfis de RMS por canal.

    Primeiro:
      média das repetições por participante/tarefa/frequência/canal.

    Depois:
      normalização de cada perfil pelos 64 canais da mesma condição.

    Isso descreve a distribuição relativa entre canais sem assumir que
    channel 1...64 corresponde a uma orientação 2D específica da matriz.
    """
    d = (
        channels.groupby(
            [
                "subject",
                "task_id",
                "task",
                "freq_hz",
                "muscle",
                "channel_in_muscle",
            ],
            as_index=False,
        )["rms100_mean"]
        .mean()
    )

    denom = d.groupby(
        ["subject", "task", "freq_hz", "muscle"]
    )["rms100_mean"].transform("mean")

    d["rms_channel_relative"] = d["rms100_mean"] / denom

    summary = (
        d.groupby(
            ["task_id", "task", "freq_hz", "muscle", "channel_in_muscle"],
            as_index=False,
        )
        .agg(
            mean_relative=("rms_channel_relative", "mean"),
            std_relative=("rms_channel_relative", "std"),
            n_subjects=("subject", "nunique"),
        )
    )

    summary["sem_relative"] = (
        summary["std_relative"] / np.sqrt(summary["n_subjects"])
    )

    return summary


def grouped_boxplot(cond, metric, ylabel, title, outpath):
    """
    Boxplots pareados por tarefa.

    0,50 Hz -> hachura //
    0,75 Hz -> hachura \\\\

    Não são usados marcadores coloridos sobre as medianas, evitando
    inconsistência entre as caixas e a legenda.
    """
    data = []
    positions = []
    labels = []

    base_positions = np.arange(len(TASK_ORDER)) * 3.0
    offsets = {0.50: -0.45, 0.75: 0.45}

    for i, task in enumerate(TASK_ORDER):
        for freq in FREQUENCIES:
            values = cond[
                (cond["task"] == task) &
                (cond["freq_hz"] == freq)
            ][metric].dropna().to_numpy()

            data.append(values)
            positions.append(base_positions[i] + offsets[freq])

        labels.append(task)

    fig = plt.figure(figsize=(13, 6))
    ax = fig.add_subplot(111)

    bp = ax.boxplot(
        data,
        positions=positions,
        widths=0.7,
        patch_artist=True,
        showfliers=False,
    )

    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor("white")
        patch.set_edgecolor("black")

        if i % 2 == 0:
            patch.set_hatch("//")      # 0,50 Hz
        else:
            patch.set_hatch("\\\\")    # 0,75 Hz

    # Mantém a linha da mediana como informação central do boxplot.
    for median in bp["medians"]:
        median.set_linewidth(1.5)

    ax.set_xticks(base_positions)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.25)

    legend_elements = [
        Patch(
            facecolor="white",
            edgecolor="black",
            hatch="//",
            label="0,50 Hz",
        ),
        Patch(
            facecolor="white",
            edgecolor="black",
            hatch="\\\\",
            label="0,75 Hz",
        ),
    ]
    ax.legend(handles=legend_elements)

    fig.tight_layout()
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)

def plot_kinematic_validation(metrics, outpath):
    data_050 = metrics.loc[
        metrics["freq_hz"] == 0.50, "kin_fdom_hz"
    ].dropna()

    data_075 = metrics.loc[
        metrics["freq_hz"] == 0.75, "kin_fdom_hz"
    ].dropna()

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111)

    ax.boxplot(
        [data_050, data_075],
        positions=[0.50, 0.75],
        widths=0.08,
        showfliers=True,
    )

    ax.plot(
        [0.40, 0.85],
        [0.40, 0.85],
        linestyle="--",
        linewidth=1.2,
        label="frequência observada = nominal",
    )

    ax.set_xlim(0.40, 0.85)
    ax.set_xlabel("Frequência nominal da tarefa (Hz)")
    ax.set_ylabel("Frequência dominante da cinemática (Hz)")
    ax.set_title("Validação espectral da frequência de execução")
    ax.grid(alpha=0.25)
    ax.legend()

    fig.tight_layout()
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_channel_profile(summary, muscle, outpath):
    d = summary[summary["muscle"] == muscle].copy()

    # Para legibilidade, média as duas velocidades aqui.
    d = (
        d.groupby(
            ["task_id", "task", "channel_in_muscle"],
            as_index=False
        )["mean_relative"]
        .mean()
    )

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)

    for task in TASK_ORDER:
        g = d[d["task"] == task].sort_values("channel_in_muscle")
        ax.plot(
            g["channel_in_muscle"],
            g["mean_relative"],
            linewidth=1.2,
            label=task,
        )

    ax.axhline(1.0, linestyle="--", linewidth=1)
    ax.set_xlabel(f"Canal dentro da matriz {muscle} (1–64)")
    ax.set_ylabel("RMS relativo à média dos 64 canais")
    ax.set_title(
        f"Perfil relativo de ativação entre canais — {muscle}\n"
        "(média entre 0,50 e 0,75 Hz)"
    )
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)

    fig.tight_layout()
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--channels", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()

    outdir = args.outdir.resolve()
    figdir = outdir / "figures"
    outdir.mkdir(parents=True, exist_ok=True)
    figdir.mkdir(parents=True, exist_ok=True)

    metrics = pd.read_csv(args.metrics)
    channels = pd.read_csv(args.channels)

    print("=" * 72)
    print("ANÁLISE DOS RESULTADOS DO DATASET COMPLETO")
    print("=" * 72)
    print(f"Gravações: {len(metrics)}")
    print(f"Participantes: {metrics['subject'].nunique()}")
    print(f"Linhas de canais: {len(channels)}")
    print()

    cond = aggregate_repetitions(metrics)
    cond = add_subject_normalized_rms(cond)

    task_summary = build_task_summary(cond)
    friedman = friedman_tests(cond)
    wilcox = frequency_wilcoxon_tests(cond)
    kin_summary = kinematic_summary(metrics)
    channel_profiles = build_channel_profiles(channels)

    cond.to_csv(
        outdir / "participant_condition_metrics.csv",
        index=False,
    )
    task_summary.to_csv(
        outdir / "task_summary.csv",
        index=False,
    )
    friedman.to_csv(
        outdir / "friedman_tests.csv",
        index=False,
    )
    wilcox.to_csv(
        outdir / "frequency_wilcoxon_tests.csv",
        index=False,
    )
    kin_summary.to_csv(
        outdir / "kinematic_summary.csv",
        index=False,
    )
    channel_profiles.to_csv(
        outdir / "channel_profiles_by_task.csv",
        index=False,
    )

    grouped_boxplot(
        cond,
        "rms100_edc_mean_norm",
        "RMS normalizado (razão em relação à média do participante)",
        "Ativação temporal por tarefa — EDC",
        figdir / "01_rms_edc_normalized_by_task.png",
    )

    grouped_boxplot(
        cond,
        "rms100_fds_mean_norm",
        "RMS normalizado (razão em relação à média do participante)",
        "Ativação temporal por tarefa — FDS",
        figdir / "02_rms_fds_normalized_by_task.png",
    )

    grouped_boxplot(
        cond,
        "fmed_edc_hz",
        "Frequência mediana (Hz)",
        "Conteúdo espectral por tarefa — EDC",
        figdir / "03_fmed_edc_by_task.png",
    )

    grouped_boxplot(
        cond,
        "fmed_fds_hz",
        "Frequência mediana (Hz)",
        "Conteúdo espectral por tarefa — FDS",
        figdir / "04_fmed_fds_by_task.png",
    )

    plot_kinematic_validation(
        metrics,
        figdir / "05_kinematic_frequency_validation.png",
    )

    plot_channel_profile(
        channel_profiles,
        "EDC",
        figdir / "06_channel_profile_edc.png",
    )

    plot_channel_profile(
        channel_profiles,
        "FDS",
        figdir / "07_channel_profile_fds.png",
    )

    print("Arquivos de análise salvos em:")
    print(outdir)
    print()
    print("Testes de Friedman:")
    print(
        friedman[
            [
                "metric",
                "freq_hz",
                "friedman_chi2",
                "p_value",
                "kendall_W",
            ]
        ].to_string(index=False)
    )

    print()
    print("Resumo da cinemática:")
    print(kin_summary.to_string(index=False))

    print()
    print(
        "Observação: os perfis de canais NÃO são mapas espaciais 8x8. "
        "Para gerar mapas topográficos, confirme primeiro a ordem física "
        "dos 64 canais na matriz."
    )


if __name__ == "__main__":
    main()
