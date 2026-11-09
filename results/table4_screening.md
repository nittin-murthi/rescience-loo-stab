# Screening (claim C8): ours vs paper Table 4 [App. G.4]

Mean (sd) over 1000 repetitions. Paper values transcribed from Table 4 (they equal the authors' published `result/results_recruit.csv` at commit 3b37682 to 4 d.p.). Time in seconds (machine-dependent).

## Paper protocol (variant text) vs paper

| q | method | FDP ours | FDP paper | power ours | power paper | time ours | time paper |
|---|---|---|---|---|---|---|---|
| 0.1 | cfBH | 0.088 (0.077) | 0.0928 (0.0713) | 0.660 (0.239) | 0.6319 (0.2053) | 0.0002 (0.0006) | 0.0037 (0.0006) |
| 0.1 | RO-cfBH | 0.000 (0.000) | 0.0038 (0.0115) | 0.000 (0.000) | 0.3041 (0.1452) | 0.0065 (0.0028) | 0.2976 (0.0114) |
| 0.1 | LOO-cfBH | 0.006 (0.025) | 0.0657 (0.0617) | 0.185 (0.160) | 0.6744 (0.1295) | 0.0004 (0.0007) | 0.0060 (0.0011) |
| 0.2 | cfBH | 0.189 (0.090) | 0.2000 (0.0807) | 0.921 (0.096) | 0.9277 (0.0838) | 0.0002 (0.0006) | 0.0037 (0.0005) |
| 0.2 | RO-cfBH | 0.000 (0.003) | 0.0602 (0.0813) | 0.002 (0.027) | 0.6522 (0.1450) | 0.0065 (0.0029) | 0.2971 (0.0100) |
| 0.2 | LOO-cfBH | 0.077 (0.057) | 0.1836 (0.0560) | 0.725 (0.164) | 0.9430 (0.0486) | 0.0004 (0.0007) | 0.0060 (0.0002) |
| 0.3 | cfBH | 0.280 (0.081) | 0.2882 (0.0806) | 0.987 (0.031) | 0.9923 (0.0198) | 0.0002 (0.0006) | 0.0037 (0.0002) |
| 0.3 | RO-cfBH | 0.064 (0.146) | 0.2483 (0.1212) | 0.208 (0.361) | 0.9627 (0.0347) | 0.0065 (0.0029) | 0.2970 (0.0101) |
| 0.3 | LOO-cfBH | 0.199 (0.125) | 0.2837 (0.0934) | 0.943 (0.073) | 0.9917 (0.0136) | 0.0004 (0.0007) | 0.0060 (0.0003) |

## All variants: mean FDP / mean power

| variant | q | cfBH FDP | cfBH power | RO-cfBH FDP | RO-cfBH power | LOO-cfBH FDP | LOO-cfBH power |
|---|---|---|---|---|---|---|---|
| text (paper protocol) | 0.1 | 0.088 | 0.660 | 0.000 | 0.000 | 0.006 | 0.185 |
| text (paper protocol) | 0.2 | 0.189 | 0.921 | 0.000 | 0.002 | 0.077 | 0.725 |
| text (paper protocol) | 0.3 | 0.280 | 0.987 | 0.064 | 0.208 | 0.199 | 0.943 |
| a_split: 30% test, split redrawn every 100 reps | 0.1 | 0.083 | 0.652 | 0.000 | 0.000 | 0.000 | 0.168 |
| a_split: 30% test, split redrawn every 100 reps | 0.2 | 0.200 | 0.920 | 0.000 | 0.000 | 0.077 | 0.717 |
| a_split: 30% test, split redrawn every 100 reps | 0.3 | 0.279 | 0.987 | 0.109 | 0.300 | 0.233 | 0.974 |
| a_xscale: authors' X scaling + intercept | 0.1 | 0.086 | 0.670 | 0.025 | 0.473 | 0.051 | 0.602 |
| a_xscale: authors' X scaling + intercept | 0.2 | 0.188 | 0.940 | 0.098 | 0.766 | 0.149 | 0.914 |
| a_xscale: authors' X scaling + intercept | 0.3 | 0.278 | 0.994 | 0.216 | 0.980 | 0.255 | 0.991 |
| a_tau: LOO bound without R | 0.1 | 0.088 | 0.660 | 0.000 | 0.000 | 0.051 | 0.549 |
| a_tau: LOO bound without R | 0.2 | 0.189 | 0.921 | 0.000 | 0.002 | 0.122 | 0.891 |
| a_tau: LOO bound without R | 0.3 | 0.280 | 0.987 | 0.064 | 0.208 | 0.268 | 0.991 |
| a_cal50: cfBH 50/50 | 0.1 | 0.092 | 0.679 | 0.000 | 0.000 | 0.006 | 0.186 |
| a_cal50: cfBH 50/50 | 0.2 | 0.193 | 0.920 | 0.000 | 0.002 | 0.077 | 0.727 |
| a_cal50: cfBH 50/50 | 0.3 | 0.290 | 0.992 | 0.064 | 0.209 | 0.198 | 0.944 |
| authors: all authors' choices | 0.1 | 0.087 | 0.628 | 0.011 | 0.286 | 0.048 | 0.608 |
| authors: all authors' choices | 0.2 | 0.207 | 0.938 | 0.066 | 0.628 | 0.195 | 0.965 |
| authors: all authors' choices | 0.3 | 0.295 | 0.997 | 0.228 | 0.980 | 0.289 | 0.998 |
| authors_resplit: authors, fresh split every rep | 0.1 | 0.091 | 0.645 | 0.012 | 0.326 | 0.067 | 0.654 |
| authors_resplit: authors, fresh split every rep | 0.2 | 0.197 | 0.931 | 0.067 | 0.641 | 0.170 | 0.946 |
| authors_resplit: authors, fresh split every rep | 0.3 | 0.287 | 0.995 | 0.210 | 0.962 | 0.275 | 0.995 |
| authors_fixtau: authors, App. G.1 bound restored | 0.1 | 0.087 | 0.628 | 0.011 | 0.286 | 0.035 | 0.483 |
| authors_fixtau: authors, App. G.1 bound restored | 0.2 | 0.207 | 0.938 | 0.066 | 0.628 | 0.158 | 0.896 |
| authors_fixtau: authors, App. G.1 bound restored | 0.3 | 0.295 | 0.997 | 0.228 | 0.980 | 0.274 | 0.998 |
| paper Table 4 | 0.1 | 0.093 | 0.632 | 0.004 | 0.304 | 0.066 | 0.674 |
| paper Table 4 | 0.2 | 0.200 | 0.928 | 0.060 | 0.652 | 0.184 | 0.943 |
| paper Table 4 | 0.3 | 0.288 | 0.992 | 0.248 | 0.963 | 0.284 | 0.992 |

## Effect of reusing 10 splits (a_split, authors): SE of mean LOO-cfBH power

Naive SE = sd/sqrt(1000); cluster SE = sd of the 10 per-split means / sqrt(10).

| variant | q | naive SE | cluster SE |
|---|---|---|---|
| a_split | 0.1 | 0.0037 | 0.0384 |
| a_split | 0.2 | 0.0046 | 0.0484 |
| a_split | 0.3 | 0.0011 | 0.0117 |
| authors | 0.1 | 0.0034 | 0.0354 |
| authors | 0.2 | 0.0010 | 0.0108 |
| authors | 0.3 | 0.0002 | 0.0021 |
