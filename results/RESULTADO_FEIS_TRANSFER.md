# RESULTADO — professor-gabarito no FEIS (EEG 14 ch Emotiv EPOC+ salino, 16 fonemas do inglês)
*05/09/2026, revisado 07/09/2026 · 21 sujeitos · log-bandpower θαβγ · LogReg C=0,05 · validação leave-one-SESSION-out (sessões; 20 sujeitos com 3 sessões, 1 com 2) · nulo perm ×200, p=(r+1)/(N+1) · acaso 16 classes = 6,25%*

**Revisão 07/09/2026.** A versão de 05/09 dizia que as sessões do FEIS não eram recuperáveis e usava terços contíguos. Estava errado: os autores concatenaram as 3 gravações somando +64/+112 ao índice de epoch (`B059691/code/merge_trial_csvs.py`), e o índice se recupera do `Time` (passo fixo 22 s a partir de 11 s). Sessões = epochs 0–63 / 64–111 / 112–159 (64/48/48 trials; sujeito 12: 2 sessões, 112 trials). Todos os números abaixo foram recalculados com as sessões reais. Também entraram os controles Tm_eq, C_par/C_impar/C_viz e I_bin_rand, e o p passou ao estimador (r+1)/(N+1).

## Por sujeito (14 canais)
| suj | sessões (trials) | I think→think | I p | P speak→speak | **T speak→think** | T p | M misto→think | Tm todos→mesmos | Tm_eq 2 ses→mesmas | C par / ímpar | I bin LOSO | I bin rand | T bin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 3 (64/48/48) | 8.0% | 0.149 | 14.2% | **6.1%** | 0.602 | 7.6% | 8.1% | 6.5% | 13.8 / 3.8% | 55.0% | 49.6% | 53.8% |
| 02 | 3 (64/48/48) | 7.3% | 0.264 | 6.9% | **5.0%** | 0.786 | 5.9% | 8.8% | 8.0% | 10.0 / 1.2% | 49.6% | 48.3% | 51.7% |
| 03 | 3 (64/48/48) | 6.8% | 0.413 | 11.5% | **5.7%** | 0.667 | 8.2% | 10.0% | 10.9% | 11.2 / 3.8% | 54.2% | 52.5% | 51.7% |
| 04 | 3 (64/48/48) | 6.9% | 0.373 | 10.2% | **6.4%** | 0.448 | 6.9% | 6.9% | 7.9% | 12.5 / 5.0% | 49.6% | 49.2% | 50.0% |
| 05 | 3 (64/48/48) | 6.4% | 0.483 | 12.7% | **6.9%** | 0.338 | 4.0% | 7.5% | 9.0% | 11.2 / 3.8% | 52.9% | 49.6% | 49.2% |
| 06 | 3 (64/48/48) | 6.9% | 0.303 | 10.1% | **9.7%** | 0.030 | 8.3% | 9.4% | 8.7% | 12.5 / 3.8% | 52.1% | 51.2% | 51.2% |
| 07 | 3 (64/48/48) | 7.6% | 0.184 | 13.2% | **8.2%** | 0.129 | 6.1% | 11.2% | 9.0% | 12.5 / 1.2% | 49.6% | 51.2% | 49.6% |
| 08 | 3 (64/48/48) | 10.8% | 0.010 | 14.2% | **8.7%** | 0.090 | 8.0% | 10.6% | 11.1% | 17.5 / 6.2% | 50.8% | 50.4% | 54.6% |
| 09 | 3 (64/48/48) | 9.5% | 0.040 | 12.3% | **8.9%** | 0.085 | 6.9% | 15.0% | 12.5% | 13.8 / 6.2% | 47.1% | 49.2% | 47.9% |
| 10 | 3 (64/48/48) | 5.0% | 0.771 | 16.8% | **8.3%** | 0.129 | 7.1% | 6.9% | 7.4% | 15.0 / 1.2% | 48.3% | 48.8% | 50.8% |
| 11 | 3 (64/48/48) | 6.1% | 0.498 | 9.0% | **4.2%** | 0.925 | 7.5% | 7.5% | 9.0% | 15.0 / 5.0% | 50.0% | 49.6% | 50.0% |
| 12 | 2 (64/48) | 3.6% | 0.925 | 5.2% | **7.6%** | 0.234 | 3.6% | 12.5% | 13.3% | 17.9 / 3.6% | 49.4% | 50.0% | 50.0% |
| 13 | 3 (64/48/48) | 6.1% | 0.607 | 10.9% | **6.8%** | 0.408 | 4.0% | 4.4% | 7.5% | 7.5 / 1.2% | 51.7% | 48.8% | 51.2% |
| 14 | 3 (64/48/48) | 4.7% | 0.871 | 7.5% | **5.4%** | 0.831 | 5.4% | 12.5% | 10.3% | 15.0 / 1.2% | 50.0% | 49.6% | 49.2% |
| 15 | 3 (64/48/48) | 5.4% | 0.667 | 7.5% | **5.4%** | 0.746 | 6.9% | 6.9% | 6.8% | 8.8 / 2.5% | 47.1% | 49.2% | 50.0% |
| 16 | 3 (64/48/48) | 12.0% | 0.005 | 9.0% | **5.4%** | 0.731 | 8.2% | 6.9% | 8.8% | 7.5 / 6.2% | 50.4% | 49.6% | 47.9% |
| 17 | 3 (64/48/48) | 6.1% | 0.478 | 7.5% | **6.2%** | 0.488 | 8.5% | 6.9% | 9.8% | 17.5 / 1.2% | 51.7% | 49.2% | 50.4% |
| 18 | 3 (64/48/48) | 7.3% | 0.279 | 12.3% | **8.5%** | 0.100 | 5.9% | 10.0% | 8.5% | 13.8 / 3.8% | 49.2% | 47.9% | 45.4% |
| 19 | 3 (64/48/48) | 9.9% | 0.050 | 9.2% | **3.8%** | 0.940 | 8.0% | 5.6% | 7.8% | 11.2 / 5.0% | 50.4% | 48.8% | 50.0% |
| 20 | 3 (64/48/48) | 5.2% | 0.746 | 16.7% | **7.1%** | 0.259 | 5.4% | 5.6% | 6.6% | 6.2 / 1.2% | 48.8% | 50.4% | 54.6% |
| 21 | 3 (64/48/48) | 5.9% | 0.532 | 10.8% | **7.3%** | 0.274 | 4.7% | 8.8% | 9.0% | 8.8 / 2.5% | 50.0% | 50.0% | 48.8% |

## Grupo (média entre sujeitos, IC95 bootstrap, Wilcoxon unilateral vs acaso)
| condição | 14 canais | 7 canais (os nossos: F7 FC5 T7 P7 F8 T8 P8) |
|---|---|---|
| I | 7.0% [IC95 6.2–7.9] Wilcoxon p=0.0932 | 6.2% [IC95 5.3–7.2] Wilcoxon p=0.717 |
| P | 10.8% [IC95 9.5–12.2] Wilcoxon p=3.97e-05 | 9.8% [IC95 8.8–10.9] Wilcoxon p=5.28e-05 |
| T | 6.7% [IC95 6.1–7.4] Wilcoxon p=0.102 | 6.5% [IC95 5.8–7.3] Wilcoxon p=0.301 |
| M | 6.5% [IC95 5.9–7.2] Wilcoxon p=0.197 | 6.1% [IC95 5.3–6.9] Wilcoxon p=0.649 |
| Tm | 8.7% [IC95 7.6–9.7] Wilcoxon p=0.000191 | 8.3% [IC95 7.3–9.2] Wilcoxon p=0.000654 |
| Tm_eq | 9.0% [IC95 8.3–9.8] Wilcoxon p=2.96e-05 | 8.7% [IC95 7.8–9.7] Wilcoxon p=2.62e-05 |
| C_par | 12.3% [IC95 11.0–13.7] Wilcoxon p=4.31e-05 | 11.8% [IC95 10.6–13.1] Wilcoxon p=2.87e-05 |
| C_impar | 3.3% [IC95 2.6–4.1] Wilcoxon p=1 | 3.3% [IC95 2.6–4.0] Wilcoxon p=1 |
| I_bin | 50.4% [IC95 49.6–51.2] Wilcoxon p=0.293 | 50.1% [IC95 49.7–50.5] Wilcoxon p=0.486 |
| I_bin_rand | 49.7% [IC95 49.2–50.1] Wilcoxon p=0.959 | 49.9% [IC95 49.6–50.2] Wilcoxon p=0.791 |
| T_bin | 50.4% [IC95 49.5–51.3] Wilcoxon p=0.267 | 50.1% [IC95 49.3–50.8] Wilcoxon p=0.213 |

- Sujeitos com I significativo (p<0,05): **4/21** · com T significativo: **1/21** (esperado ao acaso: ~1.1).

## Comparações pareadas entre sujeitos (14 canais; diferença em pp, IC95 bootstrap, Wilcoxon pareado bicaudal)
| comparação | diferença | IC95 | p |
|---|---|---|---|
| Tm − T (treino 160 vs ~106: confunde trial E tamanho) | +1.92 pp | [+0.93; +2.94] | 0.00249 |
| **Tm_eq − T** (mesmos trials vs sessão retida, MESMO tamanho de treino) | **+2.24 pp** | [+1.37; +3.10] | 0.000161 |
| Tm − Tm_eq (efeito do tamanho de treino, teste nos mesmos trials) | -0.32 pp | [-1.03; +0.41] | 0.394 |
| C_par − C_impar (pareado vs intercalado não pareado, mesmo modelo) | +9.01 pp | [+7.59; +10.49] | 5.9e-05 |
| C_viz − esperado (predição nos ímpares = rótulo do par vizinho) | +4.65 pp | [+3.72; +5.62] | 9.54e-07 |

## Leitura
- **T** é a pergunta do projeto: treinar só em FALADO e ler IMAGINADO em sessões distintas. Se T ≈ acaso no grupo, o professor falado NÃO transfere em EEG linear com 14 canais salinos.
- **P** alto é esperado e NÃO é vitória: fala tem EMG facial e movimento; o classificador lê músculo, não córtex.
- **Tm** (todos os trials → mesmos trials) mistura dois efeitos: identidade do trial E tamanho de treino (160 vs ~106). **Tm_eq** isola o primeiro.
- **I** entre sessões do mesmo protocolo mede se o imaginado tem sinal linear estável em ~1 h; as 3 sessões são consecutivas na mesma visita — não é entre dias.
- Limites honestos: Emotiv EPOC+ salino (feltro + solução salina, não seco), sem ICA, 10 repetições por classe (7 no sujeito 12), linear. "Sem evidência ≠ impossível".

## Observações
- **Mesmos trials vs sessão retida, com tamanho de treino igualado:** Tm_eq 8.98% vs T 6.74% = +2.24 pp (IC95 [+1.37; +3.10], p=0.00016). O tamanho de treino em si vale -0.32 pp (p=0.39). A versão de 05/09 dizia que "a única diferença é a proximidade temporal" — havia DUAS diferenças (identidade do trial e tamanho de treino); a frase caiu, a conclusão sobreviveu.
- **O mecanismo é identidade do trial, não proximidade temporal:** com o mesmo modelo treinado nos trials pares de speaking, thinking nos MESMOS pares dá 12.34% e thinking nos ímpares INTERCALADOS (vizinhos a ≤22 s) dá 3.32% (+9.01 pp, p=5.9e-05). Nos ímpares, a predição coincide com o rótulo do par vizinho em 13.1% dos casos contra 8.5% esperado (+4.65 pp, p=9.5e-07): o modelo memoriza estado lento trial a trial.
- **Poder:** IC95 do grupo para T = [6.08; 7.42]% → o que o IC licencia é "efeito médio de grupo ≤ +1.17 pp sobre o acaso". Isso NÃO é piso por sujeito: um efeito concentrado em poucos sujeitos escapa deste teste (a frase de 05/09, "≥1,5 pp teria aparecido", só vale para efeito homogêneo).
- **7 canais ≈ 14 canais** em todas as condições → o gargalo é SNR (eletrodo salino de consumo), volume (10 rep/classe) e tarefa (16 classes), não contagem de canais.
- **Binário vogal/consoante:** LOSO 50.4% e split ALEATÓRIO estratificado 49.7% — os dois no acaso (50%). O 69 % ± 13 dos autores (5 sujeitos sorteados, features 22.344-d, SVM-RBF com grid search) NÃO replica com este pipeline sob nenhum dos dois splits; portanto o esquema de validação não explica a diferença — a versão de 05/09 atribuía a diferença ao split, e isso caiu.
- **Sessões do FEIS recuperadas** pelo índice de epoch (ver cabeçalho). As 3 sessões de cada sujeito são consecutivas na mesma visita (~59 min no total), então I e T aqui são "entre sessões da mesma visita", não entre dias.