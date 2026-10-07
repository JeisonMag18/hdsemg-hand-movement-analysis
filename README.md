# AnÃ¡lise de Movimentos da MÃ£o com HD-sEMG

AnÃ¡lise temporal, espectral e espacial de sinais de eletromiografia de superfÃ­cie de alta densidade (HD-sEMG) durante movimentos da mÃ£o, com foco em caracterÃ­sticas que possam futuramente contribuir para a estimativa da intenÃ§Ã£o motora e o controle de prÃ³teses mioelÃ©tricas.

## MotivaÃ§Ã£o

PrÃ³teses mioelÃ©tricas utilizam a atividade muscular residual para inferir a intenÃ§Ã£o de movimento do usuÃ¡rio.

Diferentes movimentos da mÃ£o podem produzir padrÃµes de ativaÃ§Ã£o parcialmente sobrepostos nos mÃºsculos do antebraÃ§o. O HD-sEMG permite observar essa atividade em mÃºltiplos canais e, portanto, investigar caracterÃ­sticas temporais, espectrais e espaciais que podem ajudar a diferenciar tarefas motoras.

O objetivo de longo prazo deste projeto Ã© investigar se essas caracterÃ­sticas podem ser utilizadas para estimar movimentos da mÃ£o ou parÃ¢metros cinemÃ¡ticos relacionados ao movimento.

Nesta primeira etapa, o foco estÃ¡ na caracterizaÃ§Ã£o dos sinais: antes de treinar um estimador de movimento, buscamos verificar se as caracterÃ­sticas do HD-sEMG variam de forma sistemÃ¡tica com a tarefa realizada e com a velocidade de execuÃ§Ã£o.

## Pergunta de pesquisa

> Quais caracterÃ­sticas temporais, espectrais e espaciais dos sinais HD-sEMG apresentam maior sensibilidade aos diferentes movimentos da mÃ£o, e como esses padrÃµes de ativaÃ§Ã£o se relacionam com a cinemÃ¡tica?

## HipÃ³tese de trabalho

Diferentes movimentos e velocidades de execuÃ§Ã£o produzem padrÃµes distintos de recrutamento dos mÃºsculos Extensor Digitorum Communis (EDC) e Flexor Digitorum Superficialis (FDS).

Essas diferenÃ§as podem aparecer em:

- amplitude temporal;
- conteÃºdo espectral;
- distribuiÃ§Ã£o espacial da atividade nos canais de HD-sEMG.

Essas caracterÃ­sticas poderÃ£o futuramente ser utilizadas como entrada para estimadores de intenÃ§Ã£o motora.

## Base de dados

O projeto utiliza a base pÃºblica:

**HD sEMG of Forearm Muscles and 3D Hand Kinematics During Sinusoidally-Modulated Finger Movements and Grasping Tasks**

DOI: `10.6084/m9.figshare.31032934`

Principais caracterÃ­sticas:

- 21 participantes saudÃ¡veis;
- 8 tarefas motoras da mÃ£o;
- 2 frequÃªncias de execuÃ§Ã£o: 0,50 Hz e 0,75 Hz;
- 3 repetiÃ§Ãµes por condiÃ§Ã£o;
- 1007 gravaÃ§Ãµes vÃ¡lidas de movimento;
- 128 canais de HD-sEMG:
  - canais 1â€“64: EDC;
  - canais 65â€“128: FDS;
- frequÃªncia de amostragem do HD-sEMG: 2052,52 Hz;
- frequÃªncia de amostragem da cinemÃ¡tica: 100 Hz.

As oito tarefas sÃ£o:

1. flexÃ£o-extensÃ£o do dedo indicador;
2. flexÃ£o-extensÃ£o do dedo mÃ©dio;
3. flexÃ£o-extensÃ£o acoplada dos dedos anelar e mÃ­nimo;
4. oposiÃ§Ã£o-reposiÃ§Ã£o do polegar;
5. pinÃ§a indicador-polegar;
6. pinÃ§a mÃ©dio-polegar;
7. pinÃ§a trÃ­pode;
8. abertura e fechamento dos cinco dedos.

As frequÃªncias de 0,50 Hz e 0,75 Hz fazem parte do protocolo experimental original. Os participantes seguiam uma referÃªncia visual sinusoidal.

Assim:

- 0,50 Hz corresponde a um ciclo completo de movimento a cada 2 s;
- 0,75 Hz corresponde a um ciclo completo aproximadamente a cada 1,33 s.

## Por que analisar duas velocidades?

A mesma tarefa estÃ¡ disponÃ­vel em duas velocidades de execuÃ§Ã£o.

Isso Ã© importante para estudos de intenÃ§Ã£o motora porque um futuro controlador de prÃ³tese deve idealmente reconhecer o mesmo movimento mesmo quando o usuÃ¡rio o executa mais rÃ¡pido ou mais devagar.

A comparaÃ§Ã£o entre 0,50 Hz e 0,75 Hz permite verificar se uma caracterÃ­stica estÃ¡ associada principalmente ao tipo de movimento ou se Ã© fortemente influenciada pela velocidade.

## Fluxo de processamento dos sinais

```text
HD-sEMG bruto + cinemÃ¡tica
             |
             v
       Intervalo 5â€“40 s
             |
             v
Filtro passa-altas Butterworth de 20 Hz
             |
             v
     +-------------------+
     |                   |
     v                   v
AnÃ¡lise temporal     AnÃ¡lise espectral
RMS, 100 ms          PSD por Welch
                     FrequÃªncia mediana
     |                   |
     +---------+---------+
               |
               v
          EDC e FDS
               |
               v
    8 tarefas Ã— 2 velocidades
               |
               v
AnÃ¡lise estatÃ­stica de medidas repetidas
```

## Justificativa das escolhas de processamento

As escolhas de prÃ©-processamento nÃ£o foram arbitrÃ¡rias.

Foram realizadas anÃ¡lises exploratÃ³rias para avaliar:

- conteÃºdo de baixa frequÃªncia no HD-sEMG bruto;
- possÃ­vel interferÃªncia em 60 Hz;
- filtros passa-altas com cortes de 5, 10 e 20 Hz;
- janelas RMS de 50, 100, 150 e 200 ms.

O filtro passa-altas de 20 Hz foi selecionado por reduzir fortemente o conteÃºdo de baixa frequÃªncia e preservar praticamente toda a potÃªncia na principal banda de interesse do EMG acima da regiÃ£o de transiÃ§Ã£o do filtro.

A janela RMS de 100 ms foi escolhida como compromisso entre suavizaÃ§Ã£o e resoluÃ§Ã£o temporal.

Mais detalhes estÃ£o disponÃ­veis em:

[`docs/analysis_decisions.md`](docs/analysis_decisions.md)

## TÃ©cnica principal de anÃ¡lise de sinais: densidade espectral de potÃªncia

A principal tÃ©cnica espectral utilizada Ã© a densidade espectral de potÃªncia (PSD) estimada pelo mÃ©todo de Welch.

Conceitualmente, o mÃ©todo de Welch calcula periodogramas em segmentos sobrepostos do sinal e realiza a mÃ©dia desses espectros:

\[
\hat{S}_{xx}(f) =
\frac{1}{K}\sum_{k=1}^{K} P_k(f)
\]

em que \(P_k(f)\) representa o periodograma do segmento \(k\).

A partir da PSD Ã© calculada a frequÃªncia mediana, definida como a frequÃªncia que divide a potÃªncia espectral em duas partes iguais:

\[
\int_{f_{\min}}^{f_{\mathrm{med}}} S_{xx}(f)\,df
=
\frac{1}{2}
\int_{f_{\min}}^{f_{\max}} S_{xx}(f)\,df
\]

## AnÃ¡lise temporal: RMS

A amplitude da ativaÃ§Ã£o muscular Ã© caracterizada utilizando RMS mÃ³vel com janela de 100 ms:

\[
RMS[n] =
\sqrt{
\frac{1}{N}
\sum_{k=0}^{N-1} x^2[n-k]
}
\]

O RMS Ã© utilizado como descritor temporal complementar.

## Desenho estatÃ­stico

A unidade experimental Ã© o participante, e nÃ£o cada gravaÃ§Ã£o individual.

As trÃªs repetiÃ§Ãµes sÃ£o inicialmente agrupadas dentro de cada participante, tarefa e frequÃªncia de execuÃ§Ã£o.

Em seguida sÃ£o utilizados:

- teste de Friedman para comparaÃ§Ã£o entre as oito tarefas;
- Kendall's W como medida de tamanho de efeito;
- teste pareado de Wilcoxon para comparar 0,50 Hz e 0,75 Hz;
- correÃ§Ã£o de Holm para mÃºltiplas comparaÃ§Ãµes.

# Progresso do projeto â€” Etapa 1

## 1. ValidaÃ§Ã£o cinemÃ¡tica

Antes de interpretar o HD-sEMG, os sinais de cinemÃ¡tica foram utilizados para verificar se os participantes realmente executaram os movimentos prÃ³ximos Ã s frequÃªncias definidas pelo protocolo.

| FrequÃªncia nominal | FrequÃªncia dominante mÃ©dia observada |
|---:|---:|
| 0,50 Hz | 0,491 Hz |
| 0,75 Hz | 0,736 Hz |

Apenas 5 das 1007 gravaÃ§Ãµes apresentaram desvio absoluto superior a 0,10 Hz em relaÃ§Ã£o Ã  frequÃªncia nominal.

![ValidaÃ§Ã£o cinemÃ¡tica](results/figures/05_kinematic_frequency_validation.png)

Esse resultado indica boa consistÃªncia do protocolo experimental.

## 2. Resultados temporais â€” RMS

O RMS apresentou diferenÃ§as significativas entre as oito tarefas tanto para EDC quanto para FDS.

![RMS EDC](results/figures/01_rms_edc_normalized_by_task.png)

![RMS FDS](results/figures/02_rms_fds_normalized_by_task.png)

Tamanhos de efeito relacionados Ã  tarefa:

| Sinal | Velocidade | Kendall's W |
|---|---:|---:|
| RMS EDC | 0,50 Hz | 0,271 |
| RMS EDC | 0,75 Hz | 0,268 |
| RMS FDS | 0,50 Hz | 0,262 |
| RMS FDS | 0,75 Hz | 0,277 |

As comparaÃ§Ãµes pareadas tambÃ©m mostraram aumento significativo do RMS em 0,75 Hz em relaÃ§Ã£o a 0,50 Hz para as oito tarefas, tanto no EDC quanto no FDS.

### InterpretaÃ§Ã£o

Diferentes tarefas exigem nÃ­veis e padrÃµes distintos de ativaÃ§Ã£o muscular.

Entretanto, o RMS tambÃ©m Ã© influenciado pela velocidade de execuÃ§Ã£o. Isso Ã© relevante para uma futura aplicaÃ§Ã£o em prÃ³teses, pois um estimador baseado somente em amplitude poderia confundir o tipo de movimento com a velocidade com que ele Ã© executado.

## 3. Resultados espectrais â€” frequÃªncia mediana

A PSD foi estimada pelo mÃ©todo de Welch e a frequÃªncia mediana foi extraÃ­da do espectro.

![FrequÃªncia mediana EDC](results/figures/03_fmed_edc_by_task.png)

![FrequÃªncia mediana FDS](results/figures/04_fmed_fds_by_task.png)

Tamanhos de efeito:

| Sinal | Velocidade | Kendall's W |
|---|---:|---:|
| FrequÃªncia mediana EDC | 0,50 Hz | 0,283 |
| FrequÃªncia mediana EDC | 0,75 Hz | 0,330 |
| FrequÃªncia mediana FDS | 0,50 Hz | 0,590 |
| FrequÃªncia mediana FDS | 0,75 Hz | 0,661 |

O maior efeito relacionado Ã  tarefa foi observado na frequÃªncia mediana do FDS.

### InterpretaÃ§Ã£o

A distribuiÃ§Ã£o espectral da atividade do FDS apresentou forte sensibilidade ao tipo de tarefa executada.

Nesta etapa, esse resultado deve ser interpretado como **sensibilidade Ã s diferenÃ§as entre tarefas**, e nÃ£o como desempenho comprovado de classificaÃ§Ã£o.

## 4. RelaÃ§Ã£o com estimativa de movimento

Os resultados desta primeira etapa indicam que diferentes movimentos da mÃ£o estÃ£o associados a diferenÃ§as mensurÃ¡veis nas caracterÃ­sticas temporais e espectrais do HD-sEMG.

Uma aplicaÃ§Ã£o futura para controle de prÃ³teses poderia seguir a estrutura:

```text
IntenÃ§Ã£o motora
      |
      v
AtivaÃ§Ã£o muscular do antebraÃ§o
      |
      v
HD-sEMG
      |
      v
CaracterÃ­sticas temporais + espectrais + espaciais
      |
      v
Estimador de movimento
      |
      v
Movimento previsto / comando para prÃ³tese
```

O projeto ainda nÃ£o propÃµe um controlador completo de prÃ³tese.

A etapa atual busca identificar e compreender quais caracterÃ­sticas do sinal possuem maior potencial para representar a intenÃ§Ã£o motora.

## 5. Estado atual

ConcluÃ­do:

- processamento completo das 1007 gravaÃ§Ãµes;
- anÃ¡lise temporal com RMS;
- anÃ¡lise espectral com PSD por Welch;
- cÃ¡lculo da frequÃªncia mediana;
- validaÃ§Ã£o da frequÃªncia de movimento pela cinemÃ¡tica;
- estatÃ­stica em nÃ­vel de participante;
- comparaÃ§Ã£o entre tarefas com Friedman e Kendall's W;
- comparaÃ§Ã£o entre 0,50 Hz e 0,75 Hz com Wilcoxon pareado e correÃ§Ã£o de Holm.

Em andamento:

- anÃ¡lise espacial das matrizes 8 Ã— 8 de EDC e FDS;
- anÃ¡lise sistemÃ¡tica da relaÃ§Ã£o entre HD-sEMG e cinemÃ¡tica;
- aprofundamento da interpretaÃ§Ã£o fisiolÃ³gica com literatura.

PrÃ³ximas etapas:

- avaliar caracterÃ­sticas espaciais dos canais;
- quantificar relaÃ§Ãµes entre ativaÃ§Ã£o muscular e Ã¢ngulos dos dedos;
- avaliar se as caracterÃ­sticas identificadas permitem classificar os movimentos;
- investigar estimativa contÃ­nua da cinemÃ¡tica;
- analisar a robustez das caracterÃ­sticas Ã  velocidade de execuÃ§Ã£o;
- discutir aplicaÃ§Ã£o futura em prÃ³teses mioelÃ©tricas.

## Estrutura do repositÃ³rio

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

## Scripts principais

### `01_preliminary_analysis.py`

AnÃ¡lise exploratÃ³ria de uma gravaÃ§Ã£o, utilizada para inspecionar o HD-sEMG bruto, PSD, filtragem, RMS e relaÃ§Ãµes preliminares entre EMG e cinemÃ¡tica.

### `02_full_dataset_analysis.py`

Processa todas as gravaÃ§Ãµes vÃ¡lidas e extrai mÃ©tricas temporais, espectrais e cinemÃ¡ticas.

### `03_analyze_results.py`

Agrupa as repetiÃ§Ãµes em nÃ­vel de participante, executa a anÃ¡lise estatÃ­stica de medidas repetidas e gera as principais figuras.

## Reprodutibilidade

Instale as dependÃªncias com:

```bash
pip install -r requirements.txt
```

A base de dados bruta nÃ£o Ã© redistribuÃ­da neste repositÃ³rio devido ao seu tamanho.

## Disciplina

IA753 â€” AnÃ¡lise de Sinais BiolÃ³gicos  
FEEC â€” Universidade Estadual de Campinas
