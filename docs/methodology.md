# Metodologia

## Objetivo

O objetivo atual é caracterizar propriedades temporais, espectrais e, posteriormente, espaciais do HD-sEMG associadas a diferentes movimentos da mão.

Esta etapa é pensada como base para um objetivo futuro: estimar a intenção motora a partir da atividade muscular, com possível aplicação em controle de próteses mioelétricas.

## Base de dados

A base contém registros simultâneos de HD-sEMG e cinemática da mão de 21 participantes saudáveis.

Foram consideradas oito tarefas motoras, executadas nas frequências de 0,50 Hz e 0,75 Hz, com três repetições por condição.

O HD-sEMG possui 128 canais:

- canais 1–64: Extensor Digitorum Communis (EDC);
- canais 65–128: Flexor Digitorum Superficialis (FDS).

A frequência de amostragem do HD-sEMG é 2052,52 Hz e a da cinemática é 100 Hz.

## Intervalo de análise

Cada registro possui aproximadamente 45 s. Para a análise é utilizado o intervalo entre 5 s e 40 s.

Esse recorte mantém uma região central comum entre as gravações e reduz a influência do início e do final da aquisição.

## Filtragem

É aplicado um filtro passa-altas Butterworth de quarta ordem com frequência de corte de 20 Hz.

A filtragem é realizada em fase zero, utilizando processamento forward-backward.

A escolha de 20 Hz foi baseada em análises exploratórias do conteúdo espectral e na comparação entre cortes de 5, 10 e 20 Hz.

## Análise temporal

A amplitude do HD-sEMG é caracterizada por RMS móvel com janela de 100 ms.

Para um sinal discreto \(x[n]\):

\[
RMS[n] =
\sqrt{
rac{1}{N}
\sum_{k=0}^{N-1}x^2[n-k]
}
\]

O RMS é utilizado como um descritor temporal complementar da ativação muscular.

## Análise espectral

A densidade espectral de potência (PSD) é estimada pelo método de Welch.

Na implementação atual são utilizados:

- janela de Hamming;
- segmentos de 2 s;
- sobreposição de 50%.

A análise espectral por Welch é a principal técnica de análise de sinais utilizada nesta etapa do trabalho.

## Frequência mediana

A frequência mediana é calculada a partir da PSD e corresponde à frequência que divide a potência espectral em duas áreas iguais:

\[
\int_{f_{\min}}^{f_{\mathrm{med}}}S_{xx}(f)\,df
=
rac{1}{2}
\int_{f_{\min}}^{f_{\max}}S_{xx}(f)\,df
\]

Ela é utilizada como um descritor compacto da distribuição espectral do HD-sEMG.

## Validação cinemática

Os sinais de ângulo da mão são utilizados para verificar se os movimentos foram realizados próximos às frequências de 0,50 Hz e 0,75 Hz definidas no protocolo experimental.

A frequência dominante da cinemática é estimada por PSD e comparada com a frequência nominal da tarefa.

Nesta etapa, os ângulos ainda não são utilizados como alvo de regressão para estimativa contínua do movimento.

## Análise estatística

A unidade experimental é o participante.

As três repetições são primeiro agregadas dentro de cada combinação:

**participante × tarefa × frequência de execução**.

Depois são aplicados:

- teste de Friedman para comparar as oito tarefas;
- W de Kendall como tamanho de efeito;
- teste pareado de Wilcoxon para comparar 0,50 Hz e 0,75 Hz;
- correção de Holm para múltiplas comparações.

Esse procedimento evita tratar repetições do mesmo participante como observações independentes.

## Estratégia de interpretação

A significância estatística não é interpretada isoladamente.

Os resultados são discutidos considerando:

- nível de ativação muscular;
- diferenças de recrutamento entre tarefas;
- distribuição espectral;
- influência da velocidade de execução;
- possível utilidade futura para estimativa da intenção motora.

O trabalho atual não demonstra ainda desempenho de classificação ou controle de prótese. Essas etapas são tratadas como desenvolvimento futuro.
