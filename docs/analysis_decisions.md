# Analysis Decisions

## 1. Why analyze the 5â€“40 s interval?

A common central interval is used to avoid the beginning and end of each
recording and to keep the same analysis duration across conditions.

## 2. Why investigate low-frequency content?

Initial PSD analyses showed a large contribution below 20 Hz in many HD-sEMG
channels.

## 3. Why was a 60 Hz notch filter not automatically used?

The 40â€“80 Hz PSD inspection did not show a consistently dominant narrow peak
at 60 Hz.

Therefore, a notch filter was not applied automatically.

## 4. Why use a 20 Hz high-pass filter?

Cutoffs of 5, 10 and 20 Hz were compared.

The 20 Hz high-pass filter substantially reduced low-frequency content while
preserving approximately all power in the main EMG passband above the filter
transition region.

## 5. Why use a 100 ms RMS window?

RMS windows of 50, 100, 150 and 200 ms were compared.

A 100 ms window was selected as a compromise between smoothness and temporal
resolution.

## 6. Why use Welch PSD?

Welch PSD describes how signal power is distributed in frequency while
reducing variance by averaging periodograms across overlapping segments.

## 7. Why use median frequency?

Median frequency provides a compact descriptor of spectral distribution and
allows participant-level repeated-measures comparisons.

## 8. Why validate movement frequency using kinematics?

The original protocol defines movement frequencies of 0.50 and 0.75 Hz.

The kinematic signals therefore provide an independent check that participants
followed the intended movement rhythm.

## 9. Why average the three repetitions?

The participant is the experimental unit.

Averaging repetitions within participant/task/frequency avoids
pseudoreplication.

## 10. Why use Friedman and Wilcoxon tests?

The same participants perform all tasks and both speed conditions, so the
design is repeated-measures.

Friedman compares the eight tasks.

Paired Wilcoxon tests compare 0.50 and 0.75 Hz.

Holm correction controls multiple comparisons.

## 11. Why is classification not yet the main result?

The current objective is to determine whether signal characteristics contain
task-related information and to understand how those characteristics behave.

A future classifier can then test whether this information is sufficient for
movement recognition.
