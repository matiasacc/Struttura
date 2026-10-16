import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from parse_perfiles import page, NUM, f
def parse_angulos():
    out=[]
    for p in (26,27):
        for l in page(p):
            t=l.split()
            if len(t)<19 or not all(NUM.match(x) or x=='-' for x in t[-16:]): continue
            props=[f(x) for x in t[-15:]]; bt=f(t[-16]); head=t[:-16]
            # (b,t) o (b,t,r,r1) justo antes de b/t
            r=r1=None; ok=None
            for k in (0,2):
                if len(head)>=2+k and all(NUM.match(x) for x in head[len(head)-2-k:]):
                    b=f(head[len(head)-2-k]); tt=f(head[len(head)-1-k])
                    if abs(b/tt-bt)/bt<0.03: ok=k; break
            if ok is None: raise SystemExit(f'b/t {t}')
            if ok==2: r,r1=f(head[-2]),f(head[-1])
            d_all=' '.join(head[:len(head)-2-ok])
            out.append(dict(raw=d_all,r=r,r1=r1,b=b,t=tt,bt=bt,rest=props))
    return out
if __name__=='__main__':
    A=parse_angulos(); print(len(A))
    for a in A: print(a['raw'],'|',a['r'],a['r1'],a['b'],a['t'],a['rest'][:3])
