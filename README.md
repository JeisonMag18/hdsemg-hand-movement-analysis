# HD-sEMG Hand Movement Analysis

Temporal, spectral and spatial analysis of high-density surface electromyography (HD-sEMG) during hand movements and its relationship with hand kinematics.

## Research question

Which temporal, spectral and spatial characteristics of HD-sEMG signals show the greatest sensitivity to different hand movements, and how are these activation patterns related to movement kinematics?

## Dataset

- 21 healthy participants
- 8 hand-movement tasks
- 2 execution frequencies: 0.50 Hz and 0.75 Hz
- 3 repetitions per condition
- 1007 valid movement recordings
- 128 HD-sEMG channels
  - 64 EDC channels
  - 64 FDS channels
- Hand kinematics sampled at 100 Hz

## Signal-processing pipeline

1. Selection of the 5–40 s interval
2. Fourth-order Butterworth high-pass filtering at 20 Hz
3. Sliding RMS with a 100 ms window
4. Power spectral density estimation using Welch's method
5. Median-frequency calculation
6. Kinematic frequency validation
7. Repeated-measures statistical analysis

## Statistical analysis

The three repetitions were first averaged within each participant and experimental condition.

- Friedman test: comparison among the eight hand tasks
- Kendall's W: effect size
- Paired Wilcoxon test: comparison between 0.50 and 0.75 Hz
- Holm correction: multiple comparisons

## Main preliminary findings

The strongest task-related effect was observed for the median frequency of the FDS:

- 0.50 Hz: Kendall W = 0.590
- 0.75 Hz: Kendall W = 0.661

Kinematic validation:

- nominal 0.50 Hz -> mean observed frequency: 0.491 Hz
- nominal 0.75 Hz -> mean observed frequency: 0.736 Hz

## Scripts

- src/01_preliminary_analysis.py
- src/02_full_dataset_analysis.py
- src/03_analyze_results.py

## Course

IA753 — Análise de Sinais Biológicos  
FEEC — Universidade Estadual de Campinas
## Main Results

### Temporal analysis — RMS

The RMS amplitude differed significantly among the eight hand-movement tasks
for both EDC and FDS.

![EDC RMS](results/figures/01_rms_edc_normalized_by_task.png)

![FDS RMS](results/figures/02_rms_fds_normalized_by_task.png)

Increasing the movement frequency from 0.50 to 0.75 Hz significantly increased
RMS in all eight tasks for both muscles.

### Spectral analysis — Median Frequency

Power spectral density was estimated using Welch's method. Median frequency
was then extracted from the HD-sEMG spectrum.

![EDC median frequency](results/figures/03_fmed_edc_by_task.png)

![FDS median frequency](results/figures/04_fmed_fds_by_task.png)

The strongest task-related effect was observed in the FDS:

- 0.50 Hz: Kendall's W = 0.590
- 0.75 Hz: Kendall's W = 0.661

This indicates that FDS median frequency was particularly sensitive to the
motor task performed.

### Kinematic validation

![Kinematic validation](results/figures/05_kinematic_frequency_validation.png)

The dominant kinematic frequency was:

- 0.491 Hz for the nominal 0.50 Hz condition
- 0.736 Hz for the nominal 0.75 Hz condition

Only 5 of 1007 recordings showed an absolute deviation greater than 0.10 Hz.
