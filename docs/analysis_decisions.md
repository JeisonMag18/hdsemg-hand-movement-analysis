# Decisões de análise

Este documento registra as principais escolhas metodológicas e a razão de cada uma delas.

## 1. Por que analisar o intervalo de 5–40 s?

Foi utilizado um intervalo central comum entre as gravações.

Isso reduz a influência do início e do final de cada aquisição e mantém a mesma duração de análise entre condições.

## 2. Por que investigar o conteúdo de baixa frequência?

As análises exploratórias da PSD mostraram forte contribuição abaixo de 20 Hz em muitos canais de HD-sEMG.

Esse comportamento foi investigado antes de definir o filtro de pré-processamento.

O conteúdo de baixa frequência não é chamado automaticamente de “ruído”, porque sua origem não foi estabelecida de forma definitiva. Ele pode incluir componentes associadas a movimento, deriva de linha de base ou outros efeitos de aquisição.

## 3. Por que não aplicar automaticamente um filtro notch em 60 Hz?

A inspeção da PSD entre 40 e 80 Hz não mostrou um pico estreito em 60 Hz que fosse dominante de forma consistente.

Por isso, um notch em 60 Hz não foi aplicado automaticamente.

Essa decisão evita remover conteúdo espectral sem evidência clara de interferência estreita da rede elétrica.

## 4. Por que utilizar um filtro passa-altas de 20 Hz?

Foram comparadas frequências de corte de 5, 10 e 20 Hz.

O filtro de 20 Hz apresentou forte redução da potência abaixo de 20 Hz, preservando aproximadamente 99,8% da potência na faixa de 30–500 Hz na validação global.

A faixa entre 20 e 30 Hz corresponde à região de transição do filtro e, por isso, não deve ser interpretada como totalmente preservada.

Assim, a escolha de 20 Hz foi baseada no comportamento medido dos sinais, e não em um valor arbitrário.

## 5. Por que utilizar uma janela RMS de 100 ms?

Foram comparadas janelas de:

- 50 ms;
- 100 ms;
- 150 ms;
- 200 ms.

Janelas menores preservam variações rápidas, mas geram envelopes mais irregulares.

Janelas maiores aumentam a suavização, porém reduzem a resolução temporal.

A janela de 100 ms foi escolhida como compromisso entre suavização e resolução temporal.

## 6. Por que utilizar PSD pelo método de Welch?

O objetivo espectral é analisar como a potência do HD-sEMG está distribuída em frequência.

O método de Welch reduz a variabilidade da estimativa espectral ao calcular e promediar periodogramas de segmentos sobrepostos.

Além de permitir a inspeção do espectro, a PSD é utilizada para calcular a frequência mediana.

## 7. Por que utilizar frequência mediana?

A frequência mediana resume a distribuição espectral em uma única característica.

Isso facilita comparações entre tarefas, velocidades e participantes sem substituir a inspeção da PSD completa.

Os resultados atuais indicam que a frequência mediana do FDS apresenta forte sensibilidade às diferenças entre tarefas.

Isso não significa, por si só, que ela seja suficiente para classificar movimentos.

## 8. Por que validar as frequências de 0,50 Hz e 0,75 Hz com a cinemática?

As frequências de 0,50 Hz e 0,75 Hz pertencem ao protocolo original do dataset.

Elas representam a velocidade de execução dos movimentos, e não a frequência do EMG.

Antes de comparar o HD-sEMG entre essas condições, foi verificado se os participantes realmente seguiram os ritmos definidos.

A frequência dominante da cinemática apresentou média de:

- 0,491 Hz para a condição nominal de 0,50 Hz;
- 0,736 Hz para a condição nominal de 0,75 Hz.

Apenas 5 das 1007 gravações apresentaram desvio absoluto superior a 0,10 Hz em relação à frequência nominal.

## 9. Por que agrupar as três repetições antes da estatística?

O participante é a unidade experimental.

Tratar as três repetições de uma mesma pessoa como três indivíduos independentes produziria pseudorreplicação.

Por isso, as repetições são agregadas dentro de cada participante, tarefa e frequência antes das análises estatísticas em grupo.

## 10. Por que utilizar Friedman e Wilcoxon?

O desenho experimental é de medidas repetidas, pois os mesmos participantes realizam diferentes tarefas e as duas condições de velocidade.

O teste de Friedman é utilizado para comparar as oito tarefas.

O teste pareado de Wilcoxon é utilizado para comparar 0,50 Hz e 0,75 Hz dentro de cada tarefa.

A correção de Holm é aplicada às comparações múltiplas.

## 11. Por que ainda não considerar classificação como resultado principal?

A etapa atual busca responder uma pergunta anterior à classificação:

> As características do HD-sEMG realmente mudam de forma sistemática com o movimento?

Primeiro são caracterizados RMS, PSD e frequência mediana.

Depois, em uma etapa futura, um modelo de classificação poderá testar se essas características são suficientes para reconhecer os oito movimentos.

Essa separação evita confundir “diferença estatística entre tarefas” com “desempenho de classificação”.
