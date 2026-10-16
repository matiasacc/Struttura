import sys, math; sys.path.insert(0, __import__('os').path.dirname(__file__))
from parse_perfiles import page, NUM, f
NUMX=__import__('re').compile(r'^\d+(\.\d+)?$')
TIPOS={'circ':(range(29,36),10,1),'cuad':(range(36,40),10,1),'rect':(range(40,45),14,2)}
def parse_tubos(tipo):
    pags,N,NL=TIPOS[tipo]; segs=[]
    for p in pags:
        on=False; cur=None; last_t=None; lab=[]
        rows=[]
        for l in page(p):
            if '[mm]' in l: on=True; continue
            if not on: continue
            t=l.split()
            if not t or not all(NUMX.match(x) for x in t): continue
            v=[float(x) for x in t]
            if len(v)>=N:
                ex=v[:len(v)-N]; row=v[len(v)-N:]
                rows.append(('r',row,ex))
            else: rows.append(('l',v,None))
        # segmentar por reinicio de espesor
        grp=[]; labs=[]
        for k,r,ex in rows:
            if k=='l': labs.extend(r); continue
            if grp and r[0]<=grp[-1][0]:
                segs.append((grp,labs)); grp=[]; labs=[]
            grp.append(r)
            if ex: labs.extend(ex)
        if grp: segs.append((grp,labs))
    return segs
def verificar(tipo,segs):
    out=[]; prev=None
    for grp,labs in segs:
        if len(labs)!=(2 if tipo=='rect' else 1):
            if len(labs)==0 and prev: labs=prev
            else: raise SystemExit(f'{tipo} etiqueta {labs} {grp[0][:3]}')
        prev=labs
        for r in grp: out.append((labs,r))
    return out
if __name__=='__main__':
    for tp in TIPOS:
        o=verificar(tp,parse_tubos(tp)); print(tp,len(o))
        mal=0
        for labs,r in o:
            t=r[0]
            if tp=='circ': D=labs[0]; A=math.pi*t*(D-t)/100
            elif tp=='cuad': B=labs[0]; A=(t*(2*B+2*B-4*t)-(4-math.pi)*((2*t)**2-t**2))/100
            else: B,H=labs; A=(t*(2*B+2*H-4*t)-(4-math.pi)*((2*t)**2-t**2))/100
            if abs(A-r[2])/r[2]>0.04: mal+=1; print('  ?',labs,r[:4],round(A,3))
        print('  incoherentes',mal)
