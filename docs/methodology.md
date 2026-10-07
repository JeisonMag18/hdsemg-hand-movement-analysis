# Methodology

## Objective

The current objective is to characterize temporal, spectral and eventually
spatial HD-sEMG features associated with different hand motor tasks.

The analysis is designed as a first step toward future estimation of motor
intention for myoelectric prosthetic control.

## Dataset

The dataset contains simultaneous HD-sEMG and hand kinematics from 21 healthy
participants.

Eight motor tasks were performed at 0.50 Hz and 0.75 Hz, with three repetitions
per condition.

The HD-sEMG contains 128 channels:

- 64 EDC channels;
- 64 FDS channels.

## Analysis interval

The analysis uses the interval from 5 s to 40 s of each recording.

## Filtering

A fourth-order Butterworth high-pass filter with a 20 Hz cutoff is applied
using zero-phase forward-backward filtering.

## Temporal analysis

A sliding RMS with a 100 ms window is used to characterize HD-sEMG amplitude.

## Spectral analysis

Power spectral density is estimated using Welch's method.

A Hamming window, 2 s segments and 50% overlap are used in the current
implementation.

The spectral analysis is the principal signal-analysis technique of the study.

## Median frequency

Median frequency is calculated from the PSD as the frequency dividing the
spectral power into two equal areas.

## Kinematic validation

Hand-angle signals are analyzed with Welch PSD to estimate their dominant
movement frequency.

The dominant frequency is compared with the nominal experimental frequencies
of 0.50 Hz and 0.75 Hz.

## Statistical analysis

The three repetitions are first averaged within each participant and
experimental condition.

Comparisons among the eight tasks are performed with the Friedman test.

Kendall's W is reported as an effect-size measure.

Paired comparisons between 0.50 and 0.75 Hz are performed with the Wilcoxon
signed-rank test, followed by Holm correction for multiple comparisons.

## Interpretation strategy

Statistical significance is not treated as sufficient by itself.

Results are interpreted in terms of muscle activation demand, task-specific
recruitment, spectral distribution, sensitivity to execution speed and
potential usefulness for future movement-intention estimation.
