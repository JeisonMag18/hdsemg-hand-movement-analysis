# Progresso do projeto

## Etapa 1 — Caracterização temporal e espectral

### Objetivo desta etapa

Antes de desenvolver um estimador de movimento, esta etapa verifica se diferentes tarefas da mão e diferentes velocidades de execução produzem alterações mensuráveis no HD-sEMG.

A aplicação de longo prazo é a estimativa de intenção motora para sistemas de controle mioelétrico, incluindo próteses.

## O que já foi concluído

- processamento das 1007 gravações válidas;
- análise dos 21 participantes;
- análise das oito tarefas motoras;
- comparação das condições de 0,50 Hz e 0,75 Hz;
- filtragem passa-altas em 20 Hz;
- RMS móvel de 100 ms;
- PSD pelo método de Welch;
- cálculo da frequência mediana;
- validação da frequência dos movimentos utilizando cinemática;
- teste de Friedman;
- cálculo do W de Kendall;
- comparação 0,50 vs. 0,75 Hz com Wilcoxon pareado;
- correção de Holm.

## Principais resultados

### Validação cinemática

A frequência dominante média da cinemática foi:

- 0,491 Hz para a condição nominal de 0,50 Hz;
- 0,736 Hz para a condição nominal de 0,75 Hz.

Apenas 5 das 1007 gravações apresentaram erro absoluto superior a 0,10 Hz.

Isso indica que, de forma geral, o protocolo de execução foi seguido adequadamente.

### RMS

O RMS apresentou diferenças significativas entre as oito tarefas para EDC e FDS.

Além disso, o RMS aumentou significativamente em 0,75 Hz em relação a 0,50 Hz nas oito tarefas para ambos os músculos.

Isso mostra que a amplitude contém informação associada à tarefa, mas também é sensível à velocidade de execução.

### Frequência mediana

A frequência mediana também apresentou diferenças entre as tarefas.

O maior efeito foi observado no FDS:

- W = 0,590 em 0,50 Hz;
- W = 0,661 em 0,75 Hz.

Esse resultado indica forte sensibilidade da distribuição espectral do FDS ao tipo de tarefa.

Ele ainda não deve ser interpretado como desempenho de classificação.

## Relação com estimativa de movimento

Os resultados atuais apoiam a seguinte direção:

```text
Intenção motora
      ↓
Ativação muscular
      ↓
HD-sEMG
      ↓
Características temporais, espectrais e espaciais
      ↓
Estimador
      ↓
Movimento estimado / comando para prótese
```

Nesta etapa, ainda não foi treinado um classificador nem um modelo de regressão dos ângulos.

## Próxima etapa

Os próximos passos são:

1. confirmar a topologia dos canais das matrizes 8 × 8;
2. construir uma análise espacial correta para EDC e FDS;
3. quantificar a relação entre HD-sEMG e ângulos da mão no dataset completo;
4. definir um primeiro experimento de classificação dos oito movimentos;
5. posteriormente, investigar estimativa contínua da cinemática a partir do HD-sEMG.
