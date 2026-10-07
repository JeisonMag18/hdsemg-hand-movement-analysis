# HD-sEMG Hand Movement Analysis

Temporal, spectral and spatial analysis of high-density surface electromyography
(HD-sEMG) during hand movements, with emphasis on features that may support
future estimation of motor intention for myoelectric prosthetic control.

## Motivation

Myoelectric prosthetic devices rely on residual muscle activity to infer the
movement intended by the user.

Different hand movements can produce partially overlapping activation patterns
in forearm muscles. HD-sEMG provides multiple spatial channels and therefore
allows the analysis of temporal, spectral and spatial characteristics that may
help distinguish motor tasks.

The long-term goal is to investigate whether these characteristics can support
movement classification or continuous estimation of hand kinematics.

The present stage focuses first on signal characterization: before training a
movement estimator, we investigate whether the HD-sEMG features change
systematically with the performed task and movement speed.

## Research question

> Which temporal, spectral and spatial characteristics of HD-sEMG signals are
> most sensitive to different hand movements, and how are these activation
> patterns related to hand kinematics?

## Working hypothesis

Different hand movements and execution speeds produce distinct recruitment
patterns in the Extensor Digitorum Communis (EDC) and Flexor Digitorum
Superficialis (FDS). These differences should be observable in:

- temporal amplitude;
- spectral content;
- spatial distribution across HD-sEMG channels.

These features may later be used as inputs to movement-intention estimators.

## Dataset

The project uses the public dataset:

**HD sEMG of Forearm Muscles and 3D Hand Kinematics During
Sinusoidally-Modulated Finger Movements and Grasping Tasks**

DOI: `10.6084/m9.figshare.31032934`

Main characteristics:

- 21 healthy participants;
- 8 hand-movement tasks;
- 2 execution frequencies: 0.50 Hz and 0.75 Hz;
- 3 repetitions per task/frequency condition;
- 1007 valid movement recordings;
- 128 HD-sEMG channels:
  - channels 1â€“64: EDC;
  - channels 65â€“128: FDS;
- HD-sEMG sampling frequency: 2052.52 Hz;
- hand kinematics sampling frequency: 100 Hz.

The eight tasks are:

1. Index finger flexion-extension;
2. Middle finger flexion-extension;
3. Coupled ring-little finger flexion-extension;
4. Thumb opposition-reposition;
5. Index-thumb pinch;
6. Middle-thumb pinch;
7. Tripod pinch;
8. Five-finger opening-closing.

The 0.50 Hz and 0.75 Hz movement frequencies are part of the original
experimental protocol. Participants followed a sinusoidal visual reference.

Therefore:

- 0.50 Hz corresponds to one complete movement cycle every 2 s;
- 0.75 Hz corresponds to one complete movement cycle every ~1.33 s.

## Why analyze two movement speeds?

The same task is available at two execution speeds.

This is useful for movement-intention analysis because a future prosthetic
controller should ideally recognize the same intended movement even when the
user performs it faster or slower.

The two-speed protocol allows us to investigate whether a feature is mainly
related to the task itself or strongly influenced by execution speed.

## Signal-processing pipeline

```text
Raw HD-sEMG + hand kinematics
              |
              v
        5â€“40 s interval
              |
              v
20 Hz high-pass Butterworth filter
              |
              v
      +-------------------+
      |                   |
      v                   v
Temporal analysis    Spectral analysis
RMS, 100 ms          Welch PSD
                     Median frequency
      |                   |
      +---------+---------+
                |
                v
          EDC and FDS
                |
                v
    8 tasks Ã— 2 movement speeds
                |
                v
Repeated-measures statistical analysis
```

## Why these processing choices?

The preprocessing parameters were not selected arbitrarily.

Exploratory analyses were used to study:

- low-frequency content in the raw HD-sEMG;
- possible 60 Hz interference;
- high-pass cutoffs of 5, 10 and 20 Hz;
- RMS windows of 50, 100, 150 and 200 ms.

A 20 Hz high-pass filter was selected because it strongly reduced the
low-frequency contribution while preserving almost all power in the relevant
EMG band.

A 100 ms RMS window was selected as a compromise between temporal smoothness
and temporal resolution.

More details are provided in
[`docs/analysis_decisions.md`](docs/analysis_decisions.md).

## Mandatory signal-analysis technique: power spectral density

The main spectral-analysis technique is the power spectral density (PSD)
estimated using Welch's method.

Conceptually, Welch's estimator averages modified periodograms computed from
overlapping signal segments:

\[
\hat{S}_{xx}(f) =
\frac{1}{K}\sum_{k=1}^{K} P_k(f)
\]

where \(P_k(f)\) is the periodogram of segment \(k\).

The median frequency is then obtained from the PSD as the frequency that
divides the spectral power into two equal parts:

\[
\int_{f_{\min}}^{f_{\mathrm{med}}} S_{xx}(f)\,df
=
\frac{1}{2}
\int_{f_{\min}}^{f_{\max}} S_{xx}(f)\,df
\]

## Temporal analysis: RMS

Muscle activation amplitude is characterized with a sliding RMS:

\[
RMS[n] =
\sqrt{
\frac{1}{N}
\sum_{k=0}^{N-1} x^2[n-k]
}
\]

A 100 ms window is used.

RMS is treated as a complementary temporal descriptor; the mandatory spectral
analysis remains the Welch PSD.

## Statistical design

The experimental unit is the participant, not the individual recording.

The three repetitions are first averaged within each participant and
task-frequency condition.

The following repeated-measures analyses are then used:

- Friedman test: comparison among the eight tasks;
- Kendall's W: effect size;
- paired Wilcoxon test: comparison between 0.50 and 0.75 Hz;
- Holm correction: multiple paired comparisons.

# Project progress â€” Milestone 1

## 1. Kinematic validation

Before interpreting the HD-sEMG, the kinematic signals were used to verify
whether participants actually followed the nominal execution frequencies.

| Nominal frequency | Mean observed dominant frequency |
|---:|---:|
| 0.50 Hz | 0.491 Hz |
| 0.75 Hz | 0.736 Hz |

Only 5 of 1007 recordings showed an absolute deviation greater than 0.10 Hz
from the nominal frequency.

![Kinematic validation](results/figures/05_kinematic_frequency_validation.png)

## 2. Temporal results â€” RMS

RMS differed significantly among the eight tasks for both EDC and FDS.

![EDC RMS](results/figures/01_rms_edc_normalized_by_task.png)

![FDS RMS](results/figures/02_rms_fds_normalized_by_task.png)

Task-related effect sizes:

| Signal | Speed | Kendall's W |
|---|---:|---:|
| EDC RMS | 0.50 Hz | 0.271 |
| EDC RMS | 0.75 Hz | 0.268 |
| FDS RMS | 0.50 Hz | 0.262 |
| FDS RMS | 0.75 Hz | 0.277 |

Paired comparisons also showed that RMS increased significantly at 0.75 Hz
relative to 0.50 Hz for all eight tasks in both muscles.

### Interpretation

Different tasks require different levels and patterns of activation in EDC and
FDS.

However, RMS is also strongly influenced by execution speed. This is relevant
for future prosthetic control because a movement estimator based only on
amplitude could confuse task identity with movement speed.

## 3. Spectral results â€” median frequency

PSD was estimated using Welch's method and median frequency was extracted from
the spectrum.

![EDC median frequency](results/figures/03_fmed_edc_by_task.png)

![FDS median frequency](results/figures/04_fmed_fds_by_task.png)

Task-related effect sizes:

| Signal | Speed | Kendall's W |
|---|---:|---:|
| EDC median frequency | 0.50 Hz | 0.283 |
| EDC median frequency | 0.75 Hz | 0.330 |
| FDS median frequency | 0.50 Hz | 0.590 |
| FDS median frequency | 0.75 Hz | 0.661 |

The strongest task-related effect was observed for the FDS median frequency.

### Interpretation

The spectral distribution of FDS activity is particularly sensitive to the
performed motor task.

At this stage, this result indicates **task sensitivity**, not demonstrated
classification performance.

## 4. Why this matters for movement estimation

The first milestone provides evidence that hand tasks are associated with
measurable differences in temporal and spectral HD-sEMG characteristics.

A future prosthetic-control pipeline may follow:

```text
Motor intention
      |
      v
Forearm muscle activation
      |
      v
HD-sEMG
      |
      v
Temporal + spectral + spatial features
      |
      v
Movement estimator
      |
      v
Predicted movement / prosthetic command
```

This project does not yet claim to provide a complete prosthetic controller.

## 5. Current status

Completed:

- full-dataset preprocessing;
- 1007 movement recordings analyzed;
- temporal RMS analysis;
- Welch PSD analysis;
- median-frequency extraction;
- validation of movement frequency using kinematics;
- participant-level repeated-measures statistics;
- task comparison with Friedman and Kendall's W;
- 0.50 vs 0.75 Hz comparison with paired Wilcoxon tests and Holm correction.

In progress:

- spatial analysis across the 8 Ã— 8 EDC and FDS arrays;
- systematic EMG-kinematic relationship analysis;
- physiological interpretation supported by literature.

Future work:

- evaluate whether the identified features support movement classification;
- investigate continuous estimation of finger kinematics from HD-sEMG;
- assess robustness to movement speed;
- explore implications for myoelectric prosthetic control.

## Repository structure

```text
hdsemg-hand-movement-analysis/
|
+-- src/
|   +-- 01_preliminary_analysis.py
|   +-- 02_full_dataset_analysis.py
|   +-- 03_analyze_results.py
|
+-- docs/
|   +-- methodology.md
|   +-- analysis_decisions.md
|   +-- project_progress.md
|
+-- data/
|   +-- README.md
|
+-- results/
|   +-- figures/
|   +-- tables/
|
+-- README.md
+-- requirements.txt
+-- .gitignore
```

## Reproducibility

Install dependencies with:

```bash
pip install -r requirements.txt
```

The raw dataset is not redistributed in this repository because of its size.

## Course

IA753 â€” AnÃ¡lise de Sinais BiolÃ³gicos  
FEEC â€” Universidade Estadual de Campinas
