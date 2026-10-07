# Base de dados

Os arquivos brutos da base de dados não são redistribuídos neste repositório devido ao tamanho do conjunto.

Base pública utilizada:

**HD sEMG of Forearm Muscles and 3D Hand Kinematics During Sinusoidally-Modulated Finger Movements and Grasping Tasks**

DOI:

`10.6084/m9.figshare.31032934`

## Organização local esperada

```text
Dataset/
├── Sub001/
│   ├── HD_sEMG/
│   └── HandKinematics/
│       ├── Angles/
│       └── Trajectories/
├── Sub002/
│   └── ...
├── ...
└── Sub021/
```

Os scripts de análise utilizam uma pasta raiz comum para localizar os diretórios de cada participante.

A pasta contendo os dados brutos deve permanecer fora do controle de versão do Git.
