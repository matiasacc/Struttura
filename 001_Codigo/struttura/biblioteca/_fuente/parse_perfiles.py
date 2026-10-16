"""Pasa las tablas CIRSOC (PDF) a filas.  Uso:  python parse_perfiles.py  → imprime resumen y deja /tmp/perfiles_raw.json"""
import json, math, re, subprocess, sys
PDF = sys.argv[1] if len(sys.argv) > 1 else '/root/.claude/uploads/e40ed4cf-c63d-5165-863a-2fdd5aa141f5/a0138e4f-tablas.pdf'
NUM = re.compile(r'^[+-]?\d+([.,]\d+)?$')

def page(p):
    return subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), PDF, '-'], capture_output=True, text=True).stdout.splitlines()

def f(x):
    if x == '-': return None
    return float(x.replace(',', '.'))

FAM = {  # familia: (páginas pdf, norma, forma)
 'IPN': ([4], 'IRAM-IAS U 500-511', 'I'), 'IPB': ([5], 'IRAM-IAS U 500-215-2', 'I'), 'IPBl': ([6], 'IRAM-IAS U 500-215-3', 'I'),
 'IPBv': ([7], 'IRAM-IAS U 500-215-4', 'I'), 'IPE': ([8], 'IRAM-IAS U 500-215-5', 'I'), 'W': (list(range(9, 20)), 'IRAM-IAS U 500-215-6', 'I'),
 'HP': ([20], 'IRAM-IAS U 500-215-7', 'I'), 'M': ([21], 'IRAM-IAS U 500-215-8', 'I'), 'UPN': ([22], 'IRAM-IAS U 500-509-2', 'U'),
 'C': ([23], 'IRAM-IAS U 500-509-4', 'C'), 'MC': ([24, 25], 'IRAM-IAS U 500-509-4', 'C'),
}
NUMS = {'IPN': 33, 'IPB': 32, 'IPBl': 33, 'IPBv': 33, 'IPE': 32, 'W': 29, 'HP': 29, 'M': 29, 'UPN': 36, 'C': 31, 'MC': 31}
FAM['M'] = ([21], 'IRAM-IAS U 500-215-8', 'I')
def parse_laminados():
    out = []
    for fam, (pags, norma, forma) in FAM.items():
        prefijo = ''
        N = NUMS[fam]
        for p in pags:
            for l in page(p):
                t = l.split()
                if fam == 'UPN':
                    if len(t) < 28 or not all(NUM.match(x) or x == '-' for x in t[1:]): continue
                    d = t[0]; N = len(t) - 1
                else:
                    N = NUMS[fam]
                    if len(t) < N + 1 or not all(NUM.match(x) or x == '-' for x in t[-N:]): continue
                    d = ''.join(t[:-N])
                if not d: continue
                if fam in ('W', 'C', 'MC', 'HP'):
                    m = re.match(r'^((?:HP|[A-Za-z]+)\d+)[xX](.+)$', d)
                    if m: prefijo = m.group(1); d = f'{prefijo}x{m.group(2)}'
                    elif d.startswith('x'): d = prefijo + d
                d = d.replace('X', 'x')
                v = [f(x) for x in t[-N:]]
                # número de columnas de dimensiones: 5 o 6 (se decide con las relaciones)
                nd = None
                for k in (6, 5):
                    bf, tf, hw, tw = v[1], v[2], v[3], v[4]
                    ok1 = any(abs(v[k] - c) / c < 0.03 for c in (bf / (2 * tf), bf / tf))
                    if v[k] is not None and ok1 and abs(v[k + 1] - hw / tw) / (hw / tw) < 0.03:
                        nd = k; break
                if nd is None: raise SystemExit(f'sin relaciones: {fam} {d} {t}')
                i = nd + 2
                r = {'familia': fam, 'norma': norma, 'designacion': d, 'd_mm': v[0], 'bf_mm': v[1], 'tf_mm': v[2], 'hw_mm': v[3], 'tw_mm': v[4]}
                if nd == 6: r['r2_mm'] = v[5]
                r['Ag_cm2'], r['Peso_kgm'] = v[i], v[i + 1]; i += 2
                if forma == 'C':
                    r['xbar_cm'], r['eo_cm'], r['xp_cm'] = v[i:i + 3]; i += 3
                for nom in ('Ix_cm4', 'Sx_cm3', 'rx_cm', 'Qx_cm3', 'Zx_cm3', 'Iy_cm4', 'Sy_cm3', 'ry_cm', 'Qy_cm3', 'Sy15_cm3', 'Zy_cm3'):
                    r[nom] = v[i]; i += 1
                if fam == 'UPN':
                    r['ey_cm'], r['ec_cm'] = v[i:i + 2]
                    w = v[i + 7:] + [None] * 4
                    r['J_cm4'], r['Cw_cm6'], r['X1_MPa'], r['X2_1e6_MPa2'] = w[:4]
                else:
                    r['J_cm4'], r['Cw_cm6'], r['X1_MPa'], r['X2_1e6_MPa2'] = v[-8:-4]
                out.append(r)
    return out

if __name__ == '__main__':
    L = parse_laminados()
    json.dump(L, open('/tmp/perfiles_lam.json', 'w'))
    import collections
    print(collections.Counter(r['familia'] for r in L))
