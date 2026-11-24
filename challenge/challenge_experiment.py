"""Additional evaluation (Y = 5 + 2*X1 - 3*X2): no-noise recovery, noisy data with n = 5 and n = 25, and 1000-replication Monte Carlo.
Usage: python challenge_experiment.py [output_dir]
Requires: numpy, scipy.
"""
"""Reviewer I point 5: challenge the Cramer's-rule MLR with intercept, unequal coefficients, and noise."""
import numpy as np, json, sys
from scipy import stats

def cramer_fit(x1, x2, y):
    n = len(y)
    A = np.array([[n, x1.sum(), x2.sum()], [x1.sum(), (x1**2).sum(), (x1*x2).sum()], [x2.sum(), (x1*x2).sum(), (x2**2).sum()]], float)
    h = np.array([y.sum(), (x1*y).sum(), (x2*y).sum()], float)
    D = np.linalg.det(A)
    if abs(D) < 1e-9: return None
    b = []
    for k in range(3):
        Ak = A.copy(); Ak[:, k] = h; b.append(np.linalg.det(Ak) / D)
    return np.array(b), A

def anova_t(x1, x2, y, b, A):
    n = len(y); yhat = b[0] + b[1]*x1 + b[2]*x2
    sse = ((y - yhat)**2).sum(); sst = ((y - y.mean())**2).sum(); ssr = sst - sse
    dfe = n - 3
    out = dict(SSR=ssr, SSE=sse, SST=sst, dfR=2, dfE=dfe, R2=1 - sse/sst)
    if dfe > 0 and sse > 1e-9 * sst:
        mse = sse / dfe; F = (ssr/2) / mse
        C = np.linalg.inv(A); se = np.sqrt(mse * np.diag(C)); t = b / se
        out.update(F=F, pF=stats.f.sf(F, 2, dfe), se=se.tolist(), t=t.tolist(), pt=(2*stats.t.sf(abs(t), dfe)).tolist())
    else:
        out.update(F='Undefined', pF='Undefined', se=[0, 0, 0], t=['Undefined']*3, pt=['Undefined']*3)
    return out

def metrics(y, yhat):
    e = y - yhat
    mse = (e**2).mean()
    return dict(MSE=mse, MAE=np.abs(e).mean(), RMSE=np.sqrt(mse), R2=1 - (e**2).sum()/((y - y.mean())**2).sum())

TRUE = np.array([5.0, 2.0, -3.0])
gen = lambda x1, x2: TRUE[0] + TRUE[1]*x1 + TRUE[2]*x2

# article X values
trX = np.array([(1,1),(0,3),(0,7),(4,0),(3,5)], float)
teX = np.array([(1,1),(3,1),(2,3),(6,3),(4,5),(5,-6),(8,-4),(3,-9),(6,-8),(9,-7),(5,6),(7,4),(3,9),(6,8),(9,2),
                (-5,-6),(-7,-4),(-3,-9),(-6,-8),(-9,-2),(55,66),(77,44),(33,99),(66,88),(99,99)], float)
res = {}
# Scenario 1: intercept + unequal coefficients, no noise, same X as article
b, A = cramer_fit(trX[:,0], trX[:,1], gen(trX[:,0], trX[:,1]))
yte = gen(teX[:,0], teX[:,1]); yp = b[0] + b[1]*teX[:,0] + b[2]*teX[:,1]
res['S1'] = dict(b=b.round(10).tolist(), test=metrics(yte, yp), anova=anova_t(trX[:,0], trX[:,1], gen(trX[:,0], trX[:,1]), b, A))

# Scenario 2: same rule + Gaussian noise; training n = 5 and n = 25; independent test set of 25
rng = np.random.default_rng(2026)
SIG = 2.0
def draw(n): return rng.integers(-10, 11, size=(n, 2)).astype(float)
Xtest = draw(25); ytest = np.round(gen(Xtest[:,0], Xtest[:,1]) + rng.normal(0, SIG, 25), 2)
for n in (5, 25):
    X = draw(n)
    while cramer_fit(X[:,0], X[:,1], np.zeros(n)) is None: X = draw(n)
    y = np.round(gen(X[:,0], X[:,1]) + rng.normal(0, SIG, n), 2)
    b, A = cramer_fit(X[:,0], X[:,1], y)
    yp = b[0] + b[1]*Xtest[:,0] + b[2]*Xtest[:,1]
    res[f'S2_n{n}'] = dict(train=[list(map(int, r)) + [round(float(v), 2)] for r, v in zip(X, y)],
                           b=b.tolist(), test=metrics(ytest, yp), anova=anova_t(X[:,0], X[:,1], y, b, A))
res['S2_test'] = [list(map(int, r)) + [round(float(v), 2)] for r, v in zip(Xtest, ytest)]
# Monte Carlo: variability of coefficients over 1000 replications
mc = {}
for n in (5, 25):
    B = []; T = []; R2tr = []; R2te = []
    for _ in range(1000):
        X = draw(n)
        f = cramer_fit(X[:,0], X[:,1], np.zeros(n))
        if f is None: continue
        y = np.round(gen(X[:,0], X[:,1]) + rng.normal(0, SIG, n), 2)
        b, _ = cramer_fit(X[:,0], X[:,1], y); B.append(b)
        R2tr.append(metrics(y, b[0] + b[1]*X[:,0] + b[2]*X[:,1])['R2'])
        yp = b[0] + b[1]*Xtest[:,0] + b[2]*Xtest[:,1]; m = metrics(ytest, yp); T.append(m['RMSE']); R2te.append(m['R2'])
    B = np.array(B)
    mc[n] = dict(mean=B.mean(0).tolist(), sd=B.std(0, ddof=1).tolist(), test_RMSE_median=float(np.median(T)), test_RMSE_p95=float(np.percentile(T, 95)),
                 train_R2_median=float(np.median(R2tr)), test_R2_median=float(np.median(R2te)), test_R2_p5=float(np.percentile(R2te, 5)), reps=len(B))
res['MC'] = mc
import csv, os
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else '.'
json.dump(res, open(os.path.join(OUTDIR, 'challenge_results.json'), 'w'), indent=1, default=float)
for name, rows in (('challenge_train_n5.csv', res['S2_n5']['train']), ('challenge_train_n25.csv', res['S2_n25']['train']), ('challenge_test.csv', res['S2_test'])):
    with open(os.path.join(OUTDIR, name), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['X1', 'X2', 'Y']); w.writerows(rows)
def p(x): return json.dumps(x, default=lambda v: round(float(v), 4))
print('S1', p(res['S1']['b']), p(res['S1']['test']), p({k: res['S1']['anova'][k] for k in ('SSE', 'F', 't')}))
for n in (5, 25):
    r = res[f'S2_n{n}']; a = r['anova']
    print(f'S2 n={n}', p(r['b']), 'test', p(r['test']), 'train R2', round(a['R2'], 4), 'F', p(a['F']), 'pF', p(a['pF']), 't', p(a['t']), 'pt', p(a['pt']), 'se', p(a['se']))
print('MC', p(mc))
