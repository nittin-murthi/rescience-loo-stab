# Summary of the authors' result files (github.com/KiljaeL/LOO-StabCP, commit 3b37682)

Computed by us from `result/results_synthetic.csv` and `result/results_real.csv`. Used only to check which code version produced the paper's Table 2 and Table 3.

## Synthetic

```
                               Coverage        Length            Time        
                                   mean    std   mean    std     mean     std
DGP       Algorithm Method                                                   
Linear    RLM       OracleCP      0.903  0.040  3.271  0.249    3.460   0.531
                    FullCP        0.896  0.043  3.301  0.259  191.919  34.080
                    SplitCP       0.903  0.059  3.456  0.516    0.019   0.008
                    RO-StabCP     0.910  0.039  3.443  0.258    3.433   0.594
                    LOO-StabCP    0.910  0.039  3.442  0.258    0.039   0.012
          SGD       OracleCP      0.903  0.041  3.251  0.248    0.829   0.247
                    FullCP        0.896  0.043  3.301  0.259   25.369  10.676
                    SplitCP       0.900  0.059  3.420  0.556    0.006   0.005
                    RO-StabCP     0.912  0.039  3.465  0.258    0.805   0.228
                    LOO-StabCP    0.906  0.040  3.405  0.259    0.012   0.008
Nonlinear RLM       OracleCP      0.892  0.046  3.658  0.317    2.639   0.282
                    FullCP        0.886  0.047  3.690  0.341  130.733  20.648
                    SplitCP       0.893  0.059  3.811  0.554    0.014   0.003
                    RO-StabCP     0.898  0.044  3.828  0.345    2.626   0.257
                    LOO-StabCP    0.898  0.045  3.828  0.345    0.030   0.005
          SGD       OracleCP      0.891  0.046  3.639  0.318    0.453   0.080
                    FullCP        0.886  0.047  3.690  0.341    7.941   2.606
                    SplitCP       0.895  0.062  3.858  0.614    0.003   0.002
                    RO-StabCP     0.900  0.044  3.850  0.347    0.449   0.079
                    LOO-StabCP    0.894  0.045  3.790  0.347    0.007   0.003
```

## Real

```
                                  Coverage        Length           Time        
                                      mean    std   mean    std    mean     std
m   Dataset  Algorithm Method                                                  
1   Boston   RLM       OracleCP      0.920  0.273  2.841  0.000   0.016   0.001
100 Boston   RLM       OracleCP      0.906  0.031  2.854  0.053   1.368   0.228
1   Boston   RLM       FullCP        0.910  0.288  2.797  0.024   0.936   0.040
100 Boston   RLM       FullCP        0.897  0.031  2.807  0.055  82.859  13.765
1   Boston   RLM       SplitCP       0.910  0.288  2.797  0.233   0.012   0.001
100 Boston   RLM       SplitCP       0.898  0.040  2.860  0.310   0.011   0.003
1   Boston   RLM       RO-StabCP     0.920  0.273  2.866  0.012   0.016   0.003
100 Boston   RLM       RO-StabCP     0.905  0.030  2.874  0.053   1.362   0.223
1   Boston   RLM       LOO-StabCP    0.920  0.273  2.864  0.008   0.015   0.001
100 Boston   RLM       LOO-StabCP    0.905  0.030  2.873  0.053   0.017   0.006
1   Boston   SGD       OracleCP      0.900  0.302  1.703  0.001   0.016   0.004
100 Boston   SGD       OracleCP      0.905  0.029  1.776  0.064   1.373   0.222
1   Boston   SGD       FullCP        0.920  0.273  2.053  0.035   0.379   0.015
100 Boston   SGD       FullCP        0.901  0.032  2.173  0.078  32.532   5.295
1   Boston   SGD       SplitCP       0.910  0.288  1.851  0.241   0.011   0.000
100 Boston   SGD       SplitCP       0.901  0.036  1.908  0.264   0.010   0.004
1   Boston   SGD       RO-StabCP     0.900  0.302  1.829  0.071   0.016   0.000
100 Boston   SGD       RO-StabCP     0.910  0.028  1.892  0.063   1.380   0.237
1   Boston   SGD       LOO-StabCP    0.900  0.302  1.762  0.036   0.015   0.000
100 Boston   SGD       LOO-StabCP    0.906  0.029  1.833  0.064   0.017   0.005
1   Diabetes RLM       OracleCP      0.910  0.288  2.878  0.000   0.013   0.000
100 Diabetes RLM       OracleCP      0.900  0.035  2.867  0.043   1.455   0.094
1   Diabetes RLM       FullCP        0.900  0.302  2.828  0.030   0.692   0.029
100 Diabetes RLM       FullCP        0.889  0.037  2.824  0.045  80.135   2.611
1   Diabetes RLM       SplitCP       0.890  0.314  2.881  0.130   0.010   0.000
100 Diabetes RLM       SplitCP       0.894  0.043  2.872  0.144   0.011   0.004
1   Diabetes RLM       RO-StabCP     0.910  0.288  2.895  0.007   0.012   0.001
100 Diabetes RLM       RO-StabCP     0.900  0.035  2.888  0.044   1.453   0.074
1   Diabetes RLM       LOO-StabCP    0.910  0.288  2.894  0.005   0.012   0.001
100 Diabetes RLM       LOO-StabCP    0.900  0.035  2.887  0.044   0.019   0.008
1   Diabetes SGD       OracleCP      0.920  0.273  2.337  0.000   0.014   0.000
100 Diabetes SGD       OracleCP      0.902  0.031  2.403  0.037   1.522   0.067
1   Diabetes SGD       FullCP        0.910  0.288  2.576  0.030   0.284   0.013
100 Diabetes SGD       FullCP        0.890  0.036  2.620  0.044  30.316   0.738
1   Diabetes SGD       SplitCP       0.920  0.273  2.430  0.122   0.010   0.000
100 Diabetes SGD       SplitCP       0.902  0.037  2.513  0.152   0.010   0.005
1   Diabetes SGD       RO-StabCP     0.930  0.256  2.437  0.047   0.014   0.000
100 Diabetes SGD       RO-StabCP     0.914  0.030  2.512  0.038   1.531   0.073
1   Diabetes SGD       LOO-StabCP    0.920  0.273  2.385  0.020   0.014   0.000
100 Diabetes SGD       LOO-StabCP    0.906  0.031  2.457  0.038   0.020   0.008
```

