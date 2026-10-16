import os, sys
P = os.path.dirname(os.path.abspath(__file__))
for t in sys.argv[1:]:
    d = dict(l.split('=', 1) for l in open(os.path.join(P, 'raw', f'{t}_raw.txt')).read().strip().split('\n'))
    W = [r.split(',') for r in d['W'].split(';')]; D = [r.split(',') for r in d['D'].split(';')]
    s = lambda a, i: round(sum(float(r[i]) for r in a), 1)
    mine = f"{len(W)} {len(D)} {s(W,1)} {s(W,5)} {s(D,1)} {s(D,4)}"
    exp = d['CHK'].strip()
    ok = all(abs(float(a) - float(b)) < 0.15 for a, b in zip(mine.split(), exp.split()))
    bad = [r for r in W if len(r) != 6] + [r for r in D if len(r) != 5]
    print(t, 'OK' if ok and not bad else 'FEHLER', mine, '| erwartet', exp, bad[:3])
