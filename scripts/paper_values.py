# Numbers quoted from the paper, arXiv:2504.12189v1 (https://arxiv.org/pdf/2504.12189v1; not vendored), for side-by-side comparison.
# Every value is copied from the table/figure named in the comment; nothing here is computed by us.
METHODS = ["OracleCP", "FullCP", "SplitCP", "RO-StabCP", "LOO-StabCP"]

# [App. G.2, Table 2] simulation, mean over 100 reps (sd in parentheses where printed)
TABLE2 = {
    ("linear", "rlm"): dict(
        coverage=[0.903, 0.896, 0.903, 0.910, 0.910],
        coverage_sd=[0.040, 0.043, 0.060, 0.039, 0.039],
        length=[3.272, 3.300, 3.455, 3.442, 3.442],
        length_sd=[0.250, 0.257, 0.514, 0.257, 0.257],
        time=[3.201, 176.783, 0.017, 3.190, 0.035]),
    ("linear", "sgd"): dict(
        coverage=[0.903, 0.896, 0.900, 0.911, 0.906],
        length=[3.252, 3.300, 3.420, 3.464, 3.405],
        length_sd=[None, None, 0.557, None, None],
        time=[0.720, 19.320, 0.005, 0.720, 0.009]),
    ("nonlinear", "rlm"): dict(
        coverage=[0.892, 0.886, 0.893, 0.897, 0.897],
        length=[3.659, 3.690, 3.812, 3.828, 3.827],
        length_sd=[None, None, 0.554, None, None],
        time=[3.289, 163.101, 0.017, 3.275, 0.038]),
    ("nonlinear", "sgd"): dict(
        coverage=[0.892, 0.886, 0.895, 0.900, 0.894],
        length=[3.641, 3.690, 3.855, 3.849, 3.789],
        length_sd=[None, None, 0.612, None, None],
        time=[0.732, 17.425, 0.005, 0.746, 0.009]),
}

# [App. G.3, Table 3] real data, mean coverage over 100 reps
TABLE3 = {
    ("boston", 1, "rlm"): [0.920, 0.910, 0.910, 0.920, 0.920],
    ("boston", 1, "sgd"): [0.900, 0.920, 0.910, 0.900, 0.900],
    ("diabetes", 1, "rlm"): [0.910, 0.900, 0.890, 0.910, 0.910],
    ("diabetes", 1, "sgd"): [0.920, 0.910, 0.920, 0.930, 0.920],
    ("boston", 100, "rlm"): [0.906, 0.897, 0.898, 0.905, 0.905],
    ("boston", 100, "sgd"): [0.905, 0.901, 0.901, 0.910, 0.906],
    ("diabetes", 100, "rlm"): [0.900, 0.889, 0.894, 0.900, 0.900],
    ("diabetes", 100, "sgd"): [0.902, 0.890, 0.902, 0.914, 0.906],
}

# [§5, Fig. 2, length panels] APPROXIMATE, read by eye from the figure image (no table is given in the paper)
FIG2_LENGTH_APPROX = {
    ("boston", "rlm"): "all methods approx. 2.8-2.9",
    ("boston", "sgd"): "Oracle ~1.7, Full ~2.05 (m=1) / ~2.2 (m=100), Split ~1.8, RO ~1.83, LOO ~1.77",
    ("diabetes", "rlm"): "all methods approx. 2.8-2.9",
    ("diabetes", "sgd"): "Oracle ~2.35, Full ~2.6, Split ~2.45, RO ~2.45, LOO ~2.38",
}

# [App. G.4, Table 4] conformalized screening, mean (sd) over 1000 reps; key (q, method) -> (FDP, power, time),
# each a (mean, sd) pair, transcribed from the paper.
TABLE4 = {
    (0.1, "cfBH"): ((0.0928, 0.0713), (0.6319, 0.2053), (0.0037, 0.0006)),
    (0.1, "RO-cfBH"): ((0.0038, 0.0115), (0.3041, 0.1452), (0.2976, 0.0114)),
    (0.1, "LOO-cfBH"): ((0.0657, 0.0617), (0.6744, 0.1295), (0.0060, 0.0011)),
    (0.2, "cfBH"): ((0.2000, 0.0807), (0.9277, 0.0838), (0.0037, 0.0005)),
    (0.2, "RO-cfBH"): ((0.0602, 0.0813), (0.6522, 0.1450), (0.2971, 0.0100)),
    (0.2, "LOO-cfBH"): ((0.1836, 0.0560), (0.9430, 0.0486), (0.0060, 0.0002)),
    (0.3, "cfBH"): ((0.2882, 0.0806), (0.9923, 0.0198), (0.0037, 0.0002)),
    (0.3, "RO-cfBH"): ((0.2483, 0.1212), (0.9627, 0.0347), (0.2970, 0.0101)),
    (0.3, "LOO-cfBH"): ((0.2837, 0.0934), (0.9917, 0.0136), (0.0060, 0.0003)),
}
