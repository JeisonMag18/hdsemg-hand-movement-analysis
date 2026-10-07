#!/usr/bin/env python3
"""
02_full_dataset_analysis.py

Processamento sistemático do conjunto de movimentos HD-sEMG.

Pipeline:
    HD-sEMG bruto
        -> recorte 5--40 s
        -> passa-altas Butterworth de 4ª ordem, 20 Hz, fase zero
        -> RMS móvel de 100 ms
        -> PSD por Welch
        -> métricas por registro e por músculo

Também usa a cinemática, quando disponível, para verificar se a frequência
dominante da execução é compatível com a frequência nominal da tarefa.

Saídas:
1) full_dataset_metrics.csv
2) full_dataset_channel_rms.csv
3) processing_errors.csv (se houver erros)
4) dataset_condition_counts.csv

Teste rápido:
python 02_full_dataset_analysis.py ^
  --dataset-root "D:\\Data\\Downloads\\Dataset" ^
  --outdir "C:\\Users\\Jeison\\PycharmProjects\\PythonProject\\results_test" ^
  --limit 3

Execução completa:
python 02_full_dataset_analysis.py ^
  --dataset-root "D:\\Data\\Downloads\\Dataset" ^
  --outdir "C:\\Users\\Jeison\\PycharmProjects\\PythonProject\\results_full_dataset"
"""

from __future__ import annotations

import argparse
import gc
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
from scipy.signal import butter, sosfiltfilt, welch


FS_EMG = 2052.52
FS_KIN = 100.0
T_START = 5.0
T_END = 40.0

HP_CUTOFF_HZ = 20.0
HP_ORDER = 4
RMS_WINDOW_MS = 100.0

PSD_SEGMENT_S = 2.0
PSD_MAX_HZ = 450.0

TASK_NAMES = {
    1: "Index",
    2: "Middle",
    3: "Ring-Little",
    4: "Thumb",
    5: "I. Pinch",
    6: "M. Pinch",
    7: "Tripod",
    8: "5-Finger",
}

# Índices Python dos ângulos Z após pular as 5 linhas de cabeçalho do Vicon.
ACTIVE_ANGLE_COLS = {
    1: [7],
    2: [10],
    3: [13, 16],
    4: [4],
    5: [4, 7],
    6: [4, 10],
    7: [4, 7, 10],
    8: [4, 7, 10, 13, 16],
}

FILE_RE = re.compile(
    r"^(Sub\d{3})_(?P<task>[1-8])_(?P<freq>05|075)_450_(?P<rep>[0-2])\.csv$",
    re.IGNORECASE,
)


def read_emg_csv(path: Path) -> np.ndarray:
    try:
        df = pd.read_csv(path, header=None, dtype=np.float32)
    except (ValueError, TypeError):
        df = pd.read_csv(path, header=None, low_memory=False)
        df = df.apply(pd.to_numeric, errors="coerce")
        df = df.dropna(how="all").astype(np.float32)

    if df.shape[1] < 128:
        raise ValueError(
            f"{path.name}: esperava 128 canais de HD-sEMG; "
            f"foram encontradas {df.shape[1]} colunas."
        )

    return df.iloc[:, :128].to_numpy(dtype=np.float32, copy=False)


def read_angles_csv(path: Path) -> np.ndarray:
    df = pd.read_csv(
        path,
        skiprows=5,
        header=None,
        usecols=range(17),
    )
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.dropna(how="all").reset_index(drop=True)

    if df.shape[1] < 17:
        raise ValueError(
            f"{path.name}: esperava 17 colunas de cinemática; "
            f"foram encontradas {df.shape[1]}."
        )

    return df.to_numpy(dtype=np.float64, copy=False)


def crop_samples(x: np.ndarray, fs: float, t0: float, t1: float) -> np.ndarray:
    i0 = int(round(t0 * fs))
    i1 = min(int(round(t1 * fs)), x.shape[0])

    if i0 >= i1:
        raise ValueError(
            f"Intervalo {t0}-{t1} s incompatível com sinal de "
            f"{x.shape[0]} amostras a {fs} Hz."
        )

    return x[i0:i1]


def highpass_matrix(
    x: np.ndarray,
    fs: float,
    cutoff_hz: float = HP_CUTOFF_HZ,
    order: int = HP_ORDER,
) -> np.ndarray:
    sos = butter(
        order,
        cutoff_hz,
        btype="highpass",
        fs=fs,
        output="sos",
    )
    return sosfiltfilt(sos, x, axis=0)


def mean_sliding_rms_per_channel(
    x: np.ndarray,
    fs: float,
    window_ms: float = RMS_WINDOW_MS,
) -> np.ndarray:
    w = max(1, int(round(window_ms * 1e-3 * fs)))

    if x.shape[0] < w:
        raise ValueError("Sinal menor que a janela RMS.")

    sq = np.asarray(x, dtype=np.float64) ** 2
    cs = np.cumsum(sq, axis=0, dtype=np.float64)
    cs = np.vstack(
        [np.zeros((1, x.shape[1]), dtype=np.float64), cs]
    )

    win_sum = cs[w:] - cs[:-w]
    rms_valid = np.sqrt(win_sum / w)

    return np.nanmean(rms_valid, axis=0)


def welch_mean_psd_128(
    x: np.ndarray,
    fs: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    nperseg = min(x.shape[0], int(round(PSD_SEGMENT_S * fs)))
    noverlap = nperseg // 2

    f, pxx = welch(
        x,
        fs=fs,
        window="hamming",
        nperseg=nperseg,
        noverlap=noverlap,
        detrend="constant",
        scaling="density",
        axis=0,
    )

    p_edc = np.nanmean(pxx[:, :64], axis=1)
    p_fds = np.nanmean(pxx[:, 64:128], axis=1)

    return f, p_edc, p_fds


def integrate_band(
    f: np.ndarray,
    pxx: np.ndarray,
    lo: float,
    hi: float,
) -> float:
    mask = (f >= lo) & (f < hi)

    if np.count_nonzero(mask) < 2:
        return float("nan")

    return float(np.trapezoid(pxx[mask], f[mask]))


def median_frequency(
    f: np.ndarray,
    pxx: np.ndarray,
    lo: float = 20.0,
    hi: float = PSD_MAX_HZ,
) -> float:
    mask = (f >= lo) & (f <= hi)

    ff = f[mask]
    pp = pxx[mask]

    if ff.size < 2:
        return float("nan")

    cumulative = cumulative_trapezoid(pp, ff, initial=0.0)
    total = cumulative[-1]

    if not np.isfinite(total) or total <= 0:
        return float("nan")

    idx = int(np.searchsorted(cumulative, total / 2.0))
    idx = min(idx, len(ff) - 1)

    return float(ff[idx])


def dominant_frequency(
    x: np.ndarray,
    fs: float,
    max_hz: float = 2.0,
) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]

    if x.size < 10:
        return float("nan")

    nperseg = min(x.size, 2048)

    f, pxx = welch(
        x,
        fs=fs,
        window="hamming",
        nperseg=nperseg,
        noverlap=nperseg // 2,
        detrend="constant",
        scaling="density",
    )

    mask = (f > 0) & (f <= max_hz)

    if not np.any(mask):
        return float("nan")

    return float(f[mask][np.argmax(pxx[mask])])


def parse_recording_name(path: Path) -> dict | None:
    m = FILE_RE.match(path.name)

    if m is None:
        return None

    task_id = int(m.group("task"))
    freq_token = m.group("freq")
    rep = int(m.group("rep"))
    subject = path.name.split("_")[0]

    freq_hz = 0.50 if freq_token == "05" else 0.75

    return {
        "subject": subject,
        "task_id": task_id,
        "task": TASK_NAMES[task_id],
        "freq_token": freq_token,
        "freq_hz": freq_hz,
        "rep": rep,
    }


def find_movement_files(dataset_root: Path) -> list[Path]:
    files: list[Path] = []

    for subject_dir in sorted(dataset_root.glob("Sub[0-9][0-9][0-9]")):
        if not subject_dir.is_dir():
            continue

        emg_dir = subject_dir / "HD_sEMG"

        if not emg_dir.exists():
            continue

        for p in sorted(emg_dir.glob("*.csv")):
            if parse_recording_name(p) is not None:
                files.append(p)

    return files


def corresponding_angles_path(emg_path: Path) -> Path:
    subject_dir = emg_path.parent.parent
    return subject_dir / "HandKinematics" / "Angles" / emg_path.name


def process_one_record(
    emg_path: Path,
) -> tuple[dict, list[dict]]:
    meta = parse_recording_name(emg_path)

    if meta is None:
        raise ValueError(f"Nome de arquivo não reconhecido: {emg_path.name}")

    emg = read_emg_csv(emg_path)
    emg = crop_samples(emg, FS_EMG, T_START, T_END)

    emg_hp = highpass_matrix(
        emg,
        FS_EMG,
        HP_CUTOFF_HZ,
        HP_ORDER,
    )

    del emg
    gc.collect()

    rms_edc_channels = mean_sliding_rms_per_channel(
        emg_hp[:, :64],
        FS_EMG,
        RMS_WINDOW_MS,
    )
    rms_fds_channels = mean_sliding_rms_per_channel(
        emg_hp[:, 64:128],
        FS_EMG,
        RMS_WINDOW_MS,
    )

    f, p_edc, p_fds = welch_mean_psd_128(emg_hp, FS_EMG)

    total_edc = integrate_band(f, p_edc, 20, PSD_MAX_HZ)
    total_fds = integrate_band(f, p_fds, 20, PSD_MAX_HZ)

    bands = [
        (20, 50),
        (50, 100),
        (100, 200),
        (200, 450),
    ]

    record = {
        "subject": meta["subject"],
        "task_id": meta["task_id"],
        "task": meta["task"],
        "freq_hz": meta["freq_hz"],
        "rep": meta["rep"],
        "file": emg_path.name,
        "n_emg_samples_used": int(emg_hp.shape[0]),
        "interval_start_s": T_START,
        "interval_end_s": T_END,
        "hp_cutoff_hz": HP_CUTOFF_HZ,
        "hp_order": HP_ORDER,
        "rms_window_ms": RMS_WINDOW_MS,
        "rms100_edc_mean": float(np.nanmean(rms_edc_channels)),
        "rms100_edc_std_channels": float(np.nanstd(rms_edc_channels, ddof=1)),
        "rms100_fds_mean": float(np.nanmean(rms_fds_channels)),
        "rms100_fds_std_channels": float(np.nanstd(rms_fds_channels, ddof=1)),
        "fmed_edc_hz": median_frequency(f, p_edc),
        "fmed_fds_hz": median_frequency(f, p_fds),
        "power_20_450_edc": total_edc,
        "power_20_450_fds": total_fds,
    }

    for lo, hi in bands:
        pedc = integrate_band(f, p_edc, lo, hi)
        pfds = integrate_band(f, p_fds, lo, hi)

        record[f"power_{lo}_{hi}_edc"] = pedc
        record[f"power_{lo}_{hi}_fds"] = pfds

        record[f"relpower_{lo}_{hi}_edc"] = (
            pedc / total_edc
            if np.isfinite(total_edc) and total_edc > 0
            else float("nan")
        )
        record[f"relpower_{lo}_{hi}_fds"] = (
            pfds / total_fds
            if np.isfinite(total_fds) and total_fds > 0
            else float("nan")
        )

    angles_path = corresponding_angles_path(emg_path)
    kin_fdom_values: list[float] = []

    if angles_path.exists():
        angles = read_angles_csv(angles_path)
        angles = crop_samples(angles, FS_KIN, T_START, T_END)

        for col in ACTIVE_ANGLE_COLS[meta["task_id"]]:
            fd = dominant_frequency(angles[:, col], FS_KIN, max_hz=2.0)
            if np.isfinite(fd):
                kin_fdom_values.append(fd)

        if kin_fdom_values:
            kin_fdom = float(np.median(kin_fdom_values))
        else:
            kin_fdom = float("nan")

        record["kinematics_available"] = True
        record["kin_fdom_hz"] = kin_fdom
        record["kin_fdom_error_hz"] = (
            kin_fdom - meta["freq_hz"]
            if np.isfinite(kin_fdom)
            else float("nan")
        )
        record["kin_active_angle_count"] = len(
            ACTIVE_ANGLE_COLS[meta["task_id"]]
        )
    else:
        record["kinematics_available"] = False
        record["kin_fdom_hz"] = float("nan")
        record["kin_fdom_error_hz"] = float("nan")
        record["kin_active_angle_count"] = 0

    channel_rows: list[dict] = []

    for i, value in enumerate(rms_edc_channels, start=1):
        channel_rows.append({
            "subject": meta["subject"],
            "task_id": meta["task_id"],
            "task": meta["task"],
            "freq_hz": meta["freq_hz"],
            "rep": meta["rep"],
            "muscle": "EDC",
            "channel_in_muscle": i,
            "global_channel": i,
            "rms100_mean": float(value),
        })

    for i, value in enumerate(rms_fds_channels, start=1):
        channel_rows.append({
            "subject": meta["subject"],
            "task_id": meta["task_id"],
            "task": meta["task"],
            "freq_hz": meta["freq_hz"],
            "rep": meta["rep"],
            "muscle": "FDS",
            "channel_in_muscle": i,
            "global_channel": i + 64,
            "rms100_mean": float(value),
        })

    del emg_hp, p_edc, p_fds
    gc.collect()

    return record, channel_rows


def main():
    parser = argparse.ArgumentParser(
        description="Análise do dataset completo HD-sEMG."
    )

    parser.add_argument(
        "--dataset-root",
        required=True,
        type=Path,
        help="Pasta raiz Dataset.",
    )

    parser.add_argument(
        "--outdir",
        required=True,
        type=Path,
        help="Pasta para CSVs de saída.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Processa apenas N arquivos. Útil para teste.",
    )

    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=10,
        help="Salva resultados parciais a cada N registros.",
    )

    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not dataset_root.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {dataset_root}"
        )

    files = find_movement_files(dataset_root)

    if args.limit is not None:
        files = files[: args.limit]

    if not files:
        raise RuntimeError(
            "Nenhuma gravação de movimento foi encontrada."
        )

    print("=" * 70)
    print("ANÁLISE DO DATASET COMPLETO")
    print("=" * 70)
    print(f"Dataset: {dataset_root}")
    print(f"Registros encontrados para processar: {len(files)}")
    print(f"Saída: {outdir}")
    print()

    records: list[dict] = []
    channels: list[dict] = []
    errors: list[dict] = []

    t0 = time.time()

    for idx, emg_path in enumerate(files, start=1):
        meta = parse_recording_name(emg_path)

        if meta is None:
            continue

        tag = (
            f"{meta['subject']} | "
            f"{meta['task']} | "
            f"{meta['freq_hz']:.2f} Hz | "
            f"rep {meta['rep']}"
        )

        print(f"[{idx:4d}/{len(files):4d}] {tag}")

        try:
            rec, ch = process_one_record(emg_path)
            records.append(rec)
            channels.extend(ch)

        except Exception as exc:
            print(f"   ERRO: {type(exc).__name__}: {exc}")

            errors.append({
                "file": str(emg_path),
                "subject": meta["subject"],
                "task_id": meta["task_id"],
                "task": meta["task"],
                "freq_hz": meta["freq_hz"],
                "rep": meta["rep"],
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })

        if (
            idx % args.checkpoint_every == 0
            or idx == len(files)
        ):
            pd.DataFrame(records).to_csv(
                outdir / "full_dataset_metrics.csv",
                index=False,
            )

            pd.DataFrame(channels).to_csv(
                outdir / "full_dataset_channel_rms.csv",
                index=False,
            )

            if errors:
                pd.DataFrame(errors).to_csv(
                    outdir / "processing_errors.csv",
                    index=False,
                )

            elapsed = time.time() - t0
            print(
                f"   checkpoint salvo | "
                f"{len(records)} OK | "
                f"{len(errors)} erros | "
                f"{elapsed/60:.1f} min"
            )

    elapsed = time.time() - t0

    print()
    print("=" * 70)
    print("PROCESSAMENTO CONCLUÍDO")
    print("=" * 70)
    print(f"Registros processados com sucesso: {len(records)}")
    print(f"Registros com erro: {len(errors)}")
    print(f"Tempo total: {elapsed/60:.1f} min")
    print()
    print("Arquivos:")
    print(f"  {outdir / 'full_dataset_metrics.csv'}")
    print(f"  {outdir / 'full_dataset_channel_rms.csv'}")

    if errors:
        print(f"  {outdir / 'processing_errors.csv'}")

    if records:
        df = pd.DataFrame(records)

        summary = (
            df.groupby(["task", "freq_hz"])
              .size()
              .reset_index(name="n_records")
        )

        summary.to_csv(
            outdir / "dataset_condition_counts.csv",
            index=False,
        )

        print(f"  {outdir / 'dataset_condition_counts.csv'}")


if __name__ == "__main__":
    main()
