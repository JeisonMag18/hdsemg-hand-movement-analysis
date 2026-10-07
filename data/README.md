# Dataset

The raw dataset is not redistributed in this repository because of its size.

Public dataset:

**HD sEMG of Forearm Muscles and 3D Hand Kinematics During
Sinusoidally-Modulated Finger Movements and Grasping Tasks**

DOI:

`10.6084/m9.figshare.31032934`

## Expected local organization

```text
Dataset/
+-- Sub001/
|   +-- HD_sEMG/
|   +-- HandKinematics/
|       +-- Angles/
|       +-- Trajectories/
+-- ...
+-- Sub021/
```

The analysis scripts expect the participant directories under a common dataset
root supplied through command-line arguments.

The raw dataset should remain outside Git version control.
