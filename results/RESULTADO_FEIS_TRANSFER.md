# RESULTADO — professor-gabarito no FEIS (EEG 14ch Emotiv, 16 fonemas)
*05/09/2026 · 21 sujeitos · log-bandpower θαβγ · LogReg C=0,05 · validação por blocos temporais (LOBO) · nulo perm ×200 · acaso 16 classes = 6,25%*

## Por sujeito (14 canais)
| suj | blocos | I think→think | I p | P speak→speak | **T speak→think** | T p | M misto→think | Tm mesmos trials | I bin | T bin |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 3 (terços) | 10.0% | 0.005 | 12.5% | **7.5%** | 0.235 | 10.0% | 8.1% | 51.7% | 55.4% |
| 02 | 3 (terços) | 6.3% | 0.365 | 8.1% | **6.3%** | 0.445 | 5.6% | 8.8% | 50.0% | 55.0% |
| 03 | 3 (terços) | 6.2% | 0.500 | 10.0% | **5.6%** | 0.530 | 8.1% | 10.0% | 46.2% | 54.6% |
| 04 | 3 (terços) | 3.8% | 0.860 | 6.2% | **8.1%** | 0.095 | 6.9% | 6.9% | 48.8% | 47.5% |
| 05 | 3 (terços) | 3.7% | 0.920 | 10.6% | **6.2%** | 0.465 | 6.2% | 7.5% | 51.7% | 50.4% |
| 06 | 3 (terços) | 5.6% | 0.585 | 7.5% | **9.4%** | 0.000 | 8.7% | 9.4% | 49.2% | 51.2% |
| 07 | 3 (terços) | 5.6% | 0.490 | 10.0% | **8.7%** | 0.100 | 8.7% | 11.2% | 49.6% | 49.6% |
| 08 | 3 (terços) | 9.4% | 0.035 | 12.5% | **8.1%** | 0.155 | 7.5% | 10.6% | 48.8% | 55.0% |
| 09 | 3 (terços) | 10.6% | 0.005 | 6.3% | **7.5%** | 0.180 | 10.6% | 15.0% | 47.9% | 49.2% |
| 10 | 3 (terços) | 4.4% | 0.775 | 18.8% | **8.1%** | 0.080 | 7.5% | 6.9% | 48.8% | 51.2% |
| 11 | 3 (terços) | 7.5% | 0.170 | 7.5% | **5.0%** | 0.730 | 7.5% | 7.5% | 50.0% | 50.0% |
| 12 | 3 (terços) | 6.3% | 0.395 | 2.7% | **4.5%** | 0.770 | 4.5% | 12.5% | 48.2% | 51.2% |
| 13 | 3 (terços) | 6.9% | 0.270 | 10.0% | **5.6%** | 0.520 | 6.3% | 4.4% | 51.2% | 52.1% |
| 14 | 3 (terços) | 5.0% | 0.825 | 8.1% | **5.0%** | 0.805 | 5.0% | 12.5% | 50.0% | 50.0% |
| 15 | 3 (terços) | 5.0% | 0.745 | 9.4% | **5.6%** | 0.550 | 5.0% | 6.9% | 47.5% | 49.2% |
| 16 | 3 (terços) | 10.0% | 0.010 | 9.3% | **5.0%** | 0.705 | 7.5% | 6.9% | 50.0% | 47.1% |
| 17 | 3 (terços) | 6.3% | 0.475 | 8.7% | **3.8%** | 0.920 | 6.3% | 6.9% | 50.4% | 49.6% |
| 18 | 3 (terços) | 5.6% | 0.545 | 13.1% | **6.3%** | 0.390 | 4.4% | 10.0% | 48.3% | 47.1% |
| 19 | 3 (terços) | 5.6% | 0.520 | 6.2% | **4.4%** | 0.775 | 6.3% | 5.6% | 50.4% | 50.0% |
| 20 | 3 (terços) | 3.1% | 0.940 | 11.9% | **5.0%** | 0.685 | 5.6% | 5.6% | 48.8% | 49.6% |
| 21 | 3 (terços) | 6.3% | 0.325 | 11.9% | **8.1%** | 0.090 | 3.1% | 8.8% | 51.2% | 50.0% |

## Grupo (média entre sujeitos, IC95 bootstrap, Wilcoxon unilateral vs acaso)
| condição | 14 canais | 7 canais (os nossos: F7 FC5 T7 P7 F8 T8 P8) |
|---|---|---|
| I | 6.3% [IC95 5.5–7.2] Wilcoxon p=0.616 | 5.8% [IC95 4.9–6.8] Wilcoxon p=0.822 |
| P | 9.6% [IC95 8.2–11.0] Wilcoxon p=0.000271 | 8.4% [IC95 7.2–9.6] Wilcoxon p=0.00353 |
| T | 6.4% [IC95 5.7–7.1] Wilcoxon p=0.384 | 6.3% [IC95 5.6–7.0] Wilcoxon p=0.432 |
| M | 6.7% [IC95 5.9–7.5] Wilcoxon p=0.145 | 5.6% [IC95 4.8–6.5] Wilcoxon p=0.91 |
| Tm | 8.7% [IC95 7.6–9.8] Wilcoxon p=0.000191 | 8.3% [IC95 7.3–9.2] Wilcoxon p=0.000654 |
| I_bin | 49.5% [IC95 48.8–50.0] Wilcoxon p=0.966 | 49.9% [IC95 49.6–50.2] Wilcoxon p=0.915 |
| T_bin | 50.7% [IC95 49.7–51.8] Wilcoxon p=0.148 | 50.2% [IC95 49.5–50.8] Wilcoxon p=0.23 |

- Sujeitos com I significativo (p<0,05): **4/21** · com T significativo: **1/21** (esperado ao acaso: ~1.1).

## Leitura
- **T** é a pergunta do projeto: treinar só em FALADO e ler IMAGINADO em trials diferentes (blocos distintos). Se T ≈ acaso no grupo, o professor falado NÃO transfere em EEG linear com 14 canais secos.
- **P** alto é esperado e NÃO é vitória: fala tem EMG facial e movimento; o classificador lê músculo, não córtex.
- **Tm** (mesmos trials) é o teto otimista com vazamento temporal possível; só referência.
- **I** dentro do dia (blocos do mesmo protocolo) mede se o imaginado tem sinal linear estável em ~1 h; ainda não é entre-dias.
- Limites honestos: Emotiv seco/salino, sem ICA, 10 repetições por classe, linear. "Sem evidência ≠ impossível".

## Observações
- **Tm ≫ T com o mesmo classificador**: a única diferença é a proximidade temporal treino/teste → o ganho de Tm é deriva/estado compartilhado dentro do trial, não conteúdo fonêmico. Transfer falado→imaginado só vale com treino e teste em trials/blocos distintos.
- **Poder**: meia-largura do IC95 do grupo ≈ 0,7 pp → um efeito real de T ≥ ~1,5 pp sobre o acaso teria aparecido. Sob este método, o transfer é menor que isso, se existir.
- **7 canais ≈ 14 canais** em todas as condições → o gargalo é SNR (eletrodo seco), volume (10 rep/classe) e tarefa (16 classes), não contagem de canais.
- Binário vogal/consoante no acaso sob validação por blocos; o 69% ± 13 dos autores (split aleatório 80/20) não replica aqui.
- Timestamps do dataset foram regravados a intervalo fixo (22 s) → as 3 sessões do protocolo não são recuperáveis; blocos = terços contíguos por índice.