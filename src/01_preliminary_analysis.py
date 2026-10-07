#!/usr/bin/env python3
"""
01_preliminary_analysis.py

Análise preliminar reprodutível de um registro do dataset HD-sEMG + cinemática.

Fluxo:
1) carrega HD-sEMG e ângulos;
2) recorta 5--40 s;
3) seleciona EDC_01 e FDS_01;
4) aplica passa-altas Butterworth de 4ª ordem em 20 Hz;
5) calcula RMS causal com janela de 100 ms;
6) estima PSD por Welch;
7) compara RMS com ângulo e velocidade angular;
8) salva figuras e um CSV com métricas.

Exemplo:
python 01_preliminary_analysis.py \
    --emg Dataset/Sub001/HD_sEMG/Sub001_1_05_450_0.csv \
    --angles Dataset/Sub001/HandKinematics/Angles/Sub001_1_05_450_0.csv \
    --task-name "Sub001_Index_050Hz" \
    --outdir figures
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt, welch
from scipy.stats import pearsonr


FS_EMG = 2052.52
FS_KIN = 100.0
T_START = 5.0
T_END = 40.0

# Matriz EDC = canais 1--64; matriz FDS = canais 65--128.
# Índices Python: EDC_01 -> 0, FDS_01 -> 64.
EDC_COL = 0
FDS_COL = 64

# Estrutura informada para Angles:
# 0 Frame, 1 Sub Frame,
# 2--4 Thumb XYZ, 5--7 Index XYZ, ...
# Como o eixo de rotação é Z, o ângulo do indicador fica no índice 7.
INDEX_ANGLE_COL = 7


def read_numeric_csv(path: Path) -> pd.DataFrame:
    """
    Lê arquivos CSV mesmo quando existem linhas de metadados
    antes da tabela numérica.
    """

    rows = []

    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            parts = [p.strip() for p in line.split(",")]

            # Mantém apenas linhas que parecem pertencer à tabela
            if len(parts) > 2:
                rows.append(parts)

    if not rows:
        raise ValueError(f"Nenhuma tabela encontrada em {path}")

    # Descobre o número de colunas mais comum
    lengths = [len(row) for row in rows]
    ncols = max(set(lengths), key=lengths.count)

    rows = [row for row in rows if len(row) == ncols]

    df = pd.DataFrame(rows)

    # Converte texto para número; cabeçalhos viram NaN
    df = df.apply(pd.to_numeric, errors="coerce")

    # Remove linhas que eram apenas cabeçalhos
    df = df.dropna(how="all")

    # Remove colunas completamente vazias
    df = df.dropna(axis=1, how="all")

    return df.reset_index(drop=True)

def crop_by_time(x: np.ndarray, fs: float, t0: float, t1: float) -> tuple[np.ndarray, np.ndarray]:
    i0 = int(round(t0 * fs))
    i1 = min(int(round(t1 * fs)), len(x))
    if i0 >= i1:
        raise ValueError("Intervalo temporal inválido para o tamanho do sinal.")
    y = x[i0:i1]
    t = np.arange(len(y)) / fs + t0
    return y, t


def highpass(x: np.ndarray, fs: float, fc: float = 20.0, order: int = 4) -> np.ndarray:
    sos = butter(order, fc, btype="highpass", fs=fs, output="sos")
    return sosfiltfilt(sos, x)


def causal_rms(x: np.ndarray, fs: float, window_ms: float = 100.0) -> tuple[np.ndarray, int]:
    n = max(1, int(round(window_ms * 1e-3 * fs)))
    kernel = np.ones(n) / n
    mean_sq = np.convolve(x * x, kernel, mode="full")[: len(x)]
    rms = np.sqrt(mean_sq)
    # Os primeiros n-1 pontos usam janela incompleta; marcamos como NaN.
    rms[: n - 1] = np.nan
    return rms, n


def welch_psd(x: np.ndarray, fs: float, segment_s: float = 2.0):
    nperseg = min(len(x), int(round(segment_s * fs)))
    f, pxx = welch(
        x,
        fs=fs,
        window="hamming",
        nperseg=nperseg,
        noverlap=nperseg // 2,
        detrend="constant",
        scaling="density",
    )
    return f, pxx


def dominant_frequency(x: np.ndarray, fs: float, max_freq: float = 5.0) -> float:
    f, pxx = welch_psd(x, fs, segment_s=min(20.48, len(x) / fs))
    mask = (f > 0) & (f <= max_freq)
    if not np.any(mask):
        return float("nan")
    return float(f[mask][np.argmax(pxx[mask])])


def band_power(f: np.ndarray, pxx: np.ndarray, lo: float, hi: float) -> float:
    mask = (f >= lo) & (f < hi)
    if np.count_nonzero(mask) < 2:
        return float("nan")
    return float(np.trapezoid(pxx[mask], f[mask]))


def safe_pearson(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(mask) < 3:
        return float("nan")
    return float(pearsonr(x[mask], y[mask]).statistic)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emg", required=True, type=Path, help="CSV de HD-sEMG")
    parser.add_argument("--angles", required=True, type=Path, help="CSV de ângulos")
    parser.add_argument("--task-name", default="recording", help="Nome curto usado nos arquivos de saída")
    parser.add_argument("--outdir", default=Path("figures"), type=Path)
    parser.add_argument("--edc-col", default=EDC_COL, type=int)
    parser.add_argument("--fds-col", default=FDS_COL, type=int)
    parser.add_argument("--angle-col", default=INDEX_ANGLE_COL, type=int)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    emg_df = read_numeric_csv(args.emg)
    kin_df = read_numeric_csv(args.angles)

    if emg_df.shape[1] < 128:
        raise ValueError(f"Esperava pelo menos 128 colunas de HD-sEMG; encontrei {emg_df.shape[1]}.")
    if kin_df.shape[1] <= args.angle_col:
        raise ValueError(f"Coluna de ângulo {args.angle_col} não existe. O arquivo tem {kin_df.shape[1]} colunas.")

    edc_raw_full = emg_df.iloc[:, args.edc_col].to_numpy(float)
    fds_raw_full = emg_df.iloc[:, args.fds_col].to_numpy(float)
    angle_full = kin_df.iloc[:, args.angle_col].to_numpy(float)

    edc_raw, t_emg = crop_by_time(edc_raw_full, FS_EMG, T_START, T_END)
    fds_raw, _ = crop_by_time(fds_raw_full, FS_EMG, T_START, T_END)
    angle, t_kin = crop_by_time(angle_full, FS_KIN, T_START, T_END)

    # Filtragem
    edc_hp = highpass(edc_raw, FS_EMG, 20.0, 4)
    fds_hp = highpass(fds_raw, FS_EMG, 20.0, 4)

    # RMS causal de 100 ms
    edc_rms, n_rms = causal_rms(edc_hp, FS_EMG, 100.0)
    fds_rms, _ = causal_rms(fds_hp, FS_EMG, 100.0)

    # Compensação visual do atraso aproximado de meia janela
    delay_s = (n_rms - 1) / (2 * FS_EMG)
    t_rms = t_emg - delay_s

    # PSDs
    f_edc_raw, p_edc_raw = welch_psd(edc_raw, FS_EMG, 2.0)
    f_edc_hp, p_edc_hp = welch_psd(edc_hp, FS_EMG, 2.0)
    f_fds_raw, p_fds_raw = welch_psd(fds_raw, FS_EMG, 2.0)
    f_fds_hp, p_fds_hp = welch_psd(fds_hp, FS_EMG, 2.0)
    f_ang, p_ang = welch_psd(angle, FS_KIN, min(20.48, len(angle) / FS_KIN))

    # RMS interpolado para o eixo temporal da cinemática
    good_edc = np.isfinite(edc_rms)
    good_fds = np.isfinite(fds_rms)

    edc_rms_kin = np.interp(t_kin, t_rms[good_edc], edc_rms[good_edc])
    fds_rms_kin = np.interp(t_kin, t_rms[good_fds], fds_rms[good_fds])

    # Velocidade angular
    velocity = np.gradient(angle, 1.0 / FS_KIN)

    # Correlações
    r_edc_angle = safe_pearson(edc_rms_kin, angle)
    r_fds_angle = safe_pearson(fds_rms_kin, angle)
    r_edc_vel = safe_pearson(edc_rms_kin, velocity)
    r_fds_vel = safe_pearson(fds_rms_kin, velocity)
    r_edc_absvel = safe_pearson(edc_rms_kin, np.abs(velocity))
    r_fds_absvel = safe_pearson(fds_rms_kin, np.abs(velocity))

    # Métricas espectrais
    kin_fdom = dominant_frequency(angle, FS_KIN, 5.0)

    metrics = {
        "task": args.task_name,
        "fs_emg_hz": FS_EMG,
        "fs_kin_hz": FS_KIN,
        "interval_s": f"{T_START}-{T_END}",
        "hp_cutoff_hz": 20.0,
        "hp_order": 4,
        "rms_window_ms": 100.0,
        "rms_delay_compensation_ms": delay_s * 1000.0,
        "kinematic_dominant_frequency_hz": kin_fdom,
        "r_edc_rms_vs_angle": r_edc_angle,
        "r_fds_rms_vs_angle": r_fds_angle,
        "r_edc_rms_vs_velocity": r_edc_vel,
        "r_fds_rms_vs_velocity": r_fds_vel,
        "r_edc_rms_vs_abs_velocity": r_edc_absvel,
        "r_fds_rms_vs_abs_velocity": r_fds_absvel,
        "edc_raw_power_0_20": band_power(f_edc_raw, p_edc_raw, 0, 20),
        "edc_hp20_power_0_20": band_power(f_edc_hp, p_edc_hp, 0, 20),
        "edc_hp20_power_30_500": band_power(f_edc_hp, p_edc_hp, 30, 500),
        "fds_raw_power_0_20": band_power(f_fds_raw, p_fds_raw, 0, 20),
        "fds_hp20_power_0_20": band_power(f_fds_hp, p_fds_hp, 0, 20),
        "fds_hp20_power_30_500": band_power(f_fds_hp, p_fds_hp, 30, 500),
    }
    pd.DataFrame([metrics]).to_csv(args.outdir / f"{args.task_name}_metrics.csv", index=False)

    # FIGURA A: HD-sEMG bruto (zoom de 5 s)
    zoom_mask = (t_emg >= 10) & (t_emg <= 15)
    plt.figure(figsize=(10, 5))
    plt.plot(t_emg[zoom_mask], edc_raw[zoom_mask], label="EDC_01")
    plt.plot(t_emg[zoom_mask], fds_raw[zoom_mask], label="FDS_01")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.title("HD-sEMG bruto: EDC_01 e FDS_01")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.outdir / f"03_raw_emg_zoom_{args.task_name}.png", dpi=300)
    plt.close()

    # FIGURA B: PSD raw x HP20
    plt.figure(figsize=(10, 5))
    m1 = f_edc_raw <= 500
    m2 = f_edc_hp <= 500
    plt.semilogy(f_edc_raw[m1], p_edc_raw[m1], label="EDC_01 bruto")
    plt.semilogy(f_edc_hp[m2], p_edc_hp[m2], label="EDC_01 HP20")
    plt.axvline(20, linestyle="--", linewidth=1, label="20 Hz")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("PSD")
    plt.title("Efeito do filtro passa-altas de 20 Hz")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.outdir / f"10_highpass_psd_EDC_01_{args.task_name}.png", dpi=300)
    plt.close()

    # FIGURA C: PSD da cinemática
    plt.figure(figsize=(10, 5))
    mk = f_ang <= 5
    plt.plot(f_ang[mk], p_ang[mk])
    plt.axvline(kin_fdom, linestyle="--", linewidth=1, label=f"f dominante = {kin_fdom:.3f} Hz")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("PSD")
    plt.title("PSD do ângulo do dedo indicador")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.outdir / f"07_index_angle_psd_{args.task_name}.png", dpi=300)
    plt.close()

    # FIGURA D: RMS x cinemática
    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.plot(t_kin, edc_rms_kin, label="RMS EDC_01")
    ax1.plot(t_kin, fds_rms_kin, label="RMS FDS_01")
    ax1.set_xlabel("Tempo (s)")
    ax1.set_ylabel("RMS")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(t_kin, angle, alpha=0.7, label="Ângulo indicador")
    ax2.set_ylabel("Ângulo (graus)")
    ax2.legend(loc="upper right")

    plt.title("RMS do HD-sEMG e cinemática do dedo indicador")
    fig.tight_layout()
    fig.savefig(args.outdir / f"16_sliding_rms_vs_index_angle_{args.task_name}.png", dpi=300)
    plt.close(fig)

    print("Análise concluída.")
    print(f"Figuras e métricas salvas em: {args.outdir.resolve()}")
    print(f"f dominante da cinemática: {kin_fdom:.4f} Hz")
    print(f"r(RMS EDC, ângulo): {r_edc_angle:.4f}")
    print(f"r(RMS FDS, ângulo): {r_fds_angle:.4f}")
    print(f"r(RMS EDC, velocidade): {r_edc_vel:.4f}")
    print(f"r(RMS FDS, velocidade): {r_fds_vel:.4f}")


if __name__ == "__main__":
    main()
