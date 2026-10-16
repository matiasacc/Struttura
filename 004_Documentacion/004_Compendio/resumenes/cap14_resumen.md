# Cap. 14 – Falla por fatiga (Compendio de Cálculo Estructural II, UNC-FCEFyN, 2024)

Páginas del libro 14-1 a 14-30 = PDF 224-253. Relación: página 14-k = PDF 223+k.
Todas las fórmulas de este resumen fueron verificadas contra la imagen de la página. Los números de los ejemplos (47) y del Anexo 1 se reprodujeron con un script independiente (ver sección 4).

Convención de este archivo: `Su` rotura, `Sy` fluencia, `Se'` límite de fatiga de la probeta, `Se` límite de fatiga de la pieza (con todas las reducciones), `Sa`/`σa` alterna, `σm` media (con signo). Cuando algo es propuesta mía y no del libro, lo digo ("propuesta", "derivado").

---------------------------------------------------------------------------------------------------

## 1. Qué resuelve el capítulo y para qué sirve en diseño

Es el único capítulo del compendio que trata cargas repetidas. Resuelve: dada una pieza con tensiones que fluctúan en el tiempo (una fibra de eje rotante, un larguero que ve ±g de ráfaga, un herraje), decidir si resiste vida infinita (coeficiente de seguridad CS) o cuántos ciclos dura (vida N, daño acumulado) cuando se acepta vida limitada. Usa el método clásico tensión-vida (S-N) para ciclos altos (N > 10^3), todo empírico (el libro lo dice en 14-1 y 14-2: las fórmulas son "una guía", no resultados precisos).

Flujo completo (lo que habría que programar), en orden:

1. Material: Su, Sy -> `Se'` (probeta pulida) por regla 0,5·Su (acero) o 0,4·Su (aluminio) o tabla.
2. Pieza: `Se = fT·fC·fS·f1·f2...·Se'` (Marin) -- tamaño, carga, superficie.
3. Entalla: `Kt` (gráficos) -> sensibilidad `q` (Neuber) -> `Kf = 1 + q(Kt-1)`; se aplica a σa (y a σm solo si es frágil).
4. Ciclo: de σmax, σmin -> σm, σa. Si hay tensiones combinadas: tensores medio y alterno, tensión efectiva de cada uno (Von Mises dúctil / Rankine frágil).
5. Criterio de interacción (Soderberg, Goodman, Gerber, Marín, Bagci) -> CS a fatiga, o σE equivalente, o `SN` (resistencia con vida limitada) -> vida N.
6. Verificación a fluencia por separado (con σmax estático).
7. Varios niveles de carga: Miner (sin orden) o Manson (con orden) -> daño / vida remanente.
8. Distribución continua de niveles: Miner generalizado con p(x).
9. Anexo 1: propagación de grieta (Paris) -> vida remanente de pieza con grieta detectada.

---------------------------------------------------------------------------------------------------

## 2. Fórmulas y algoritmos clave

Cada fórmula lleva sección, número de ecuación del libro y página PDF. Unidades salvo que se aclare: MPa y mm.

### 2.1 Definiciones del ciclo (sec. 1.1, 3.3 y 5; Ec. (13), (36), (38); PDF 224, 228, 233)

```
σm = (σmax + σmin)/2        (con signo)
σa = (σmax − σmin)/2        (siempre ≥ 0)
R  = σmin/σmax ≤ 1          R=1 estático; R=0 repetido; R=−1 alternado puro
```
Observación (Ec. 37, PDF 233): σm no es "la parte fija de la señal", es solo el promedio entre máximo y mínimo.

### 2.2 Concentración de tensiones (sec. 3, PDF 226-228)

- `Kt = σmax/σnominal` (Ec. 1); depende solo de geometría y tipo de carga, no del material (Ec. 2). Se saca de los gráficos del Anexo 2 (16 casos), cada uno con su fórmula de σ nominal.
- Estática, material dúctil: NO se usa Kt (Ec. 3). Estática, frágil: SÍ (Ec. 4).
- Fatiga: `Kf = 1 + q (Kt − 1)`, `q = (Kf−1)/(Kt−1)` (Ec. 5-6), 0 ≤ q ≤ 1 (Ec. 7).
- Neuber (Ec. 9): `q = 1 / (1 + √ρ/√r)`, con r radio de la entalla en mm y √ρ parámetro del material (en √mm).
- Aceros, axial y flexión (Ec. 10-a; Su en MPa, mm):
  `√ρ = 1,24 − 0,00225·Su + 1,6e-6·Su² − 4,1e-10·Su³`
- Aceros, torsión (Ec. 10-b):
  `√ρ = 0,958 − 0,001834·Su + 1,43e-6·Su² − 4,1e-10·Su³`
- Aluminio 2024 (Ec. 11, r en mm): `q = 0,52·r^0,34` si r ≤ 3 mm; `q = 1 − 0,73/r` si r > 3 mm (continua en r=3: 0,7556 vs 0,7567).
- "Acero fundido" (Ec. 12): `q = 0,2`. Y el recuadro dice que para la fundición q varía entre 0 y 0,2 y que conviene usar el máximo.
- Tabla (14) (PDF 228), para el ciclo:

| Material | se aplica a σm | se aplica a σa |
|---|---|---|
| Dúctil | 1 (nada) | Kf |
| Frágil | Kt | Kf |

### 2.3 Límite de fatiga de la probeta Se' (sec. 4.1, PDF 230)

- Acero (Ec. 17): `Se' ≈ menor(0,5·Su ; SM)`, con SM = 690 MPa (100 kpsi, 7000 kg/cm², 70 kg/mm²). El recuadro de Fig. 9 dice que la relación Se'/Su está típicamente entre 0,4 y 0,6, y que para Su > 1380 MPa se estabiliza en ~690 MPa.
- Dureza (Ec. 18): `Su[MPa] ≈ 3,5·HB` para HB < 400.
- Aluminio (Ec. 19): `Se' ≈ menor(0,4·Su ; SL)`, SL = 131 MPa (19 kpsi, 1340 kg/cm², 13,4 kg/mm²).
- Fundición gris y aluminio: usar tablas de los Anexos 3-f y 3-d.
- Acero: Se' corresponde a N = 10^6 (Ec. 15: S < Se' => vida ilimitada). Aluminio: no hay codo; se define Se' a 10^7 (Ec. 16) y para pistones 5e8 (PDF 229).

### 2.4 Límite de fatiga de la pieza Se (sec. 4.2, PDF 231)

`Se = fT · fC · fS · f1 · f2 ... · Se'` (Ec. 20)

- Tamaño fT, ejes rotantes de acero (Ec. 21, d en mm):
  `fT = 1,24·d^−0,107` para 3 ≤ d ≤ 51;  `fT = 1,51·d^−0,157` para 51 < d ≤ 254.
- Ejes no rotantes: se usa (21) con diámetro equivalente `de` (Ec. 22): circular `de = 0,37·d`; rectangular `de = 0,88·√(a·b)`.
- Solo axial: `fT = 1` (Ec. 23).
- Carga fC (Ec. 24): flexión 1; axial 0,85; torsión pura 0,59. IMPORTANTE (recuadro PDF 231): 0,59 solo para torsión pura; si hay otra carga combinada usar fC = 1 porque el criterio de Von Mises (0,577) o Tresca (0,5) ya hace ese trabajo.
- Superficie fS, aceros (Ec. 25): `fS = a / Su^b`, con `b` positivo (el factor es a·Su^(−b)). Constantes (Ec. 26), Su en MPa:

| Terminación | a [MPa] | a [kpsi] | a [kg/cm²] | a [kg/mm²] | b |
|---|---|---|---|---|---|
| Rectificado | 1,58 | 1,34 | 1,92 | 1,30 | 0,085 |
| Maquinado / estirado en frío | 4,51 | 2,70 | 8,33 | 2,46 | 0,265 |
| Laminado en caliente | 57,7 | 14,4 | 305,6 | 11,2 | 0,718 |
| Forjado | 272 | 39,3 | 2750 | 28,7 | 0,995 |

- Alternativa cuadrática (Ec. 27-28, Su en MPa): `fS = (a0 + a1·Su + a2·Su²)·1e-4`. Los a1 son NEGATIVOS (el texto extraído pierde el signo; la imagen lo muestra):

| Terminación | a0 | a1 | a2 |
|---|---|---|---|
| Rectificado | 9800 | −1,22 | 0,00037 |
| Maquinado / estirado | 10300 | −4,30 | 0,00122 |
| Laminado en caliente | 10170 | −8,57 | 0,00260 |
| Forjado | 8350 | −7,87 | 0,00258 |
| Agua común | 9600 | −9,81 | 0,00313 |
| Agua salada | 6860 | −7,24 | 0,00223 |

  Chequeo mío: Su=600, rectificado: potencia 0,9173, cuadrática 0,9201 (coinciden ~0,3 %). Las dos últimas filas (agua común/salada, corrosión) solo existen en la forma cuadrática.
- No hay en el capítulo factor de temperatura ni de confiabilidad; solo "f1, f2... otros efectos" sin valores.

### 2.5 Diagrama S-N, vida limitada (sec. 4.3, PDF 232)

Recta en log-log entre (10^3, 0,9·Su) y (10^6, Se):
```
SN = a / N^b                            (30)
a = (0,9·Su)²/Se ;  b = (1/3)·log10(0,9·Su/Se) ;  c = 1/b       (31)
N = (a/SN)^c   para 10^3 ≤ N ≤ 10^6 ,  Se ≤ SN ≤ 0,9·Su         (32)
```
Valen tanto para la probeta (con Se') como para la pieza (con Se, que ya incluye las reducciones). Para aluminio (PDF 230): cambiar 10^6 por 10^7 y 1/3 por 1/4 en b (y en (32), (84), (98)).

- Relación entre dos niveles (33): `N1 = N·(SN/SN1)^c`. Caso típico (34): Se'=0,5Su, Se=0,6Se'=0,3Su -> b≈0,16, c≈6; "+20 % de tensión => vida a ~1/3" (1,2^−6 = 0,335; con c exacto 6,29 da 0,318).
- Efecto del CS en la vida cuando σm = 0 (Ec. 35): `N1 = N·(CS/CS1)^c`.
- Resistencia a fatiga "usa" el Se de la pieza; los aceros de alta resistencia recuperan SN/Su alto si se acepta vida limitada (comentario PDF 232).
- Zona de bajo ciclo, extensión en (84) (PDF 241): para 0,9·Su ≤ SN ≤ Su, `N = 1 + 9990·(1 − SN/Su)` (da N=1000 en 0,9·Su y N=1 en Su). Para SN < Se, N = ∞.

### 2.6 Tensiones fluctuantes uniaxiales con σm > 0 (sec. 5, PDF 233-235)

Curvas de falla (Ec. 39), con Se de la pieza (ya con todas las reducciones, Ec. 41):
```
Soderberg:  CS·σm/Sy + CS·Kf·σa/Se = 1             (39-a)
Goodman:    CS·σm/Su + CS·Kf·σa/Se = 1             (39-b)
Gerber:     (CS·σm/Su)² + CS·Kf·σa/Se = 1          (39-c)   parábola
Marín:      (CS·σm/Su)² + (CS·Kf·σa/Se)² = 1       (39-d)   elipse
Bagci:      (CS·σm/Su)^4 + CS·Kf·σa/Se = 1         (39-e)
```
- σm = 0 => todos coinciden: `CS = Se/(Kf·σa)` (Ec. 40).
- σm < 0: solo cuenta σa; la compresión media no daña por fatiga (Ec. 42), pero hay que verificar fluencia en compresión (PDF 234).
- Soderberg es el más conservador y excluye por sí mismo la falla por fluencia; para los demás hay que verificar fluencia aparte (5.2): dúctil `CS(|σm|+σa)/Sy = 1` (43-a); frágil `CS·Kt(|σm|+σa)/Su = 1` (43-b).

CS explícito (Ec. 44-45), con `m = |σm|/Su`, `m̄ = |σm|/Sy`, `a = Kf·σa/Se`:
```
Soderberg: CS = 1/(m̄ + a)                          (44-a)
Goodman:   CS = 1/(m + a)                           (44-b)
Gerber:    CS = (√(a² + 4m²) − a)/(2m²)             (44-c)
Marín:     CS = 1/√(m² + a²)                        (44-d)
Bagci:     CS⁴·m⁴ + CS·a = 1  (cuártica en CS)      (44-e)
```
Bagci con m/a < 0,6 (Ec. 46): iteración `CS_{i+1} = (1 − [m·CS_i]^4)/a`, con `CS_1 = (1 − (m/a)^4)/a`.

Notas de implementación (mías, verificadas):
- Gerber en forma estable (sin 0/0 cuando m→0): `CS = 2/(a + √(a² + 4m²))`; es idéntica algebraicamente.
- Bagci: cuártica monótona en CS>0, tiene una sola raíz positiva; usar bisección/Newton, no hace falta la iteración (46).
- Si σa = 0 (carga estática pura) las fórmulas siguen dando CS = 1/m (Goodman, Gerber, Marín; Soderberg 1/m̄) y el de Bagci 1/m; solo hay que evitar dividir por a en (46)/(58)-(59), donde β se indefine (tratar aparte: σE = σm·Sy/Su).

### 2.7 Vida limitada con σm > 0 (sec. 5.4, PDF 235)

Cuando un CS pedido da primer miembro > 1, se acepta vida finita reemplazando Se por SN en (39) y despejando:
```
A = CS·Kf·σa ;  M = CS·σm/Su ;  M̄ = CS·σm/Sy                       (49)
Soderberg: SN = A/(1 − M̄)      Goodman: SN = A/(1 − M)
Gerber:    SN = A/(1 − M²)     Marín:   SN = A/√(1 − M²)
Bagci:     SN = A/(1 − M⁴)                                         (48-a..e)
```
Con σm = 0: `SN = CS·Kf·σa` (Ec. 50). Luego N de (32) (o de (84) si SN > 0,9Su). Condición implícita (mía): el denominador debe ser > 0 (M<1); si no, no existe solución de vida finita (es falla estática por Su/Sy).

### 2.8 Tensión equivalente por fatiga σE (sec. 6, PDF 236-237)

Definición (51): `CS = Sy/σE`.
- Soderberg (54): `σE = σm + (Kf·σa)·Sy/Se`.
- Goodman (55-56): `σe = σm + (Kf·σa)·Su/Se`, `CS = Su/σe`; y reescrito para usar (51): `σE = σm·Sy/Su + (Kf·σa)·Sy/Se`.
- Forma general (57-59): `σE = Sy/CS` y
```
α = Kf·σa·Sy/Se ;   β = σm·Se/(Kf·σa·Su)
Soderberg: σE = α(1 + β·Su/Sy)     Goodman: σE = α(1 + β)
Gerber:    σE = α·2β²/(√(1+4β²) − 1)       Marín: σE = α·√(1+β²)
Bagci (β < 0,4):  σE ≈ α(1 + β⁴)                                   (58)
```
 (Chequeado: (58) reproduce los CS de la tabla (47); forma estable de Gerber: `σE = α·(1+√(1+4β²))/2`, mía.)
- Soderberg para ejes (6.4, Ec. 60, atribuida a Soderberg 1935): con flexión y torsión simultáneas
```
σe = |σm| + (Kfσ·σa)·Sy/Se ;  τe = |τm| + (Kfτ·τa)·Sy/Se ;  σE = √(σe² + 3·τe²)      (60)
```
 (en (60) se usa el mismo Se para σ y para τ; fC=1 aplicado).
- Modo de falla (6.5, Ec. 61-62): Soderberg => siempre fatiga si σa>0. Otros criterios: `CS_fluencia = Sy/σmax`, `CS_fatiga = Sy/σE`; gobierna el menor; fatiga si `σE > σmax = σm + σa`.

### 2.9 Tensiones combinadas, σm > 0 (sec. 7, PDF 238-239)

Procedimiento (7.1, 4 pasos). Supone: (1) todas las cargas varían con la misma ley temporal; (2) el tensor alterno con Kf es múltiplo del medio (la misma fibra llega a máx y mín). Casi nunca se cumple a rajatabla, pero el procedimiento queda "del lado de la seguridad".
```
1) Pm = ½(Pmax + Pmin) ;  Pa = ½(Pmax − Pmin)       por cada esfuerzo               (63)
2) tensores (σij)m y (σij)a, componentes σx σy σz τxy τyz τxz                         (64)(65)
   2b) aplicar Kt (media, solo frágil) y Kf (alterna), según tipo de solicitación
3) tensiones efectivas: dúctil -> Von Mises (66); frágil -> Rankine (67)
   (σ*m y σ*a NO se calculan a partir de σ*max y σ*min porque ambas resultan positivas)
4) criterio uniaxial (sec. 5.1) o σE (sec. 6) con σ*m, σ*a. En este paso NO se usa Kt ni Kf (ya aplicados en 2b)
```
- Von Mises general (68-69): `σ* = √(½[(σ1−σ2)²+(σ2−σ3)²+(σ3−σ1)²])` o `√((σx²+σy²+σz²) − (σxσy+σyσz+σzσx) + 3(τxy²+τyz²+τzx²))`.
- Plano (70): `√(σx² + σy² − σxσy + 3τxy²)`. Fuera de fase (71) para la alterna: `σ*a = √(σxa² + σya² − [σxa(−σya)] + 3τxya²)`, es decir `+σxaσya` con amplitudes positivas.
- Teoría de vigas, una σ y una τ (72): `σ*m = √(σm² + 3τm²)`, `σ*a = √((Kfσ·σa)² + 3(Kfτ·τa)²)`. Torsión sola (73): `σ*m = √3·τm`, `σ*a = √3·Kfτ·τa`.
- Rankine (frágil) (74-76): Kt·σm; tensiones principales de cada tensor, `σ* = mayor(σ1, |σ3|)`. Para σ y τ: `σ*m = Ktσ·σm/2 + √((Ktσ·σm/2)² + (Ktτ·τm)²)`, análoga para la alterna con Kf.
- Fluencia por separado (7.2, Ec. 77): `CS = Sy/σ*max`, donde `σ*max ≠ σ*m + σ*a` (el libro lo marca explícitamente con "≠"): se calcula con el tensor máximo (media + alterna) con el criterio adecuado.

### 2.10 Coeficiente de Kimmelmann (sec. 8, PDF 240)

Idea: no necesariamente multiplicar todas las tensiones por el mismo CS. `CSK` (79) es un CS "no convencional" que depende de cómo crecen las cargas hasta la falla: línea de evolución en el plano (σm, σa): (a) vertical (solo crece σa), (b) horizontal (solo crece σm), (c) curva, (d) recta por el origen = CS convencional. Se puede aplicar CS solo a algunos esfuerzos (ej. el torsor T repetido, con el peso propio sin incertidumbre).

Ejemplo del libro (8.1, Ec. 80-81): eje dúctil, torsor repetido 0..T y flexión alterna M por peso propio, sin concentración:
```
σm = 0 ; σa = M/W ; τm = τa = ½·(CSK·T/(2W))
σe = (M/W)(Sy/Se) ;  τe = ½·(CSK·T/(2W))·(1 + Sy/Se) ;  Sy = √(σe² + 3τe²)     (81)
```
Derivado por mí (no está en el libro, solo "las ecuaciones (81) permiten despejar CSK"): con `A = (M/W)(Sy/Se)`, `B = (T/(4W))(1 + Sy/Se)` resulta `CSK = √((Sy² − A²)/(3B²))` (requiere A < Sy).

Generalización computable (propuesta): dado un factor λ aplicado solo a un subconjunto de esfuerzos o componentes del tensor (medios y/o alternos), resolver `CS(λ) = 1` en la curva de interacción elegida por búsqueda de raíz (bisección). Cubre los casos a, b, c, d de la Fig. 15.

### 2.11 Daño acumulado (sec. 9, PDF 241-244)

Nivel i: ciclos aplicados `ni`; SNi según (50) o (48); vida `Ni` por (84):
```
Ni = 1 + 9990(1 − SNi/Su)      si 0,9Su ≤ SNi ≤ Su
Ni = (a/SNi)^c                  si Se ≤ SNi ≤ 0,9Su
Ni = ∞  (N>10^6)                si SNi < Se                                        (84)
```
Ejemplo Soderberg (85): `SNi = CS·Kf·σai/(1 − CS·σmi/Sy)`.

**Miner-Palmgren (9.1, Ec. 83):** falla cuando `Σ ni/Ni = 1`. Comentarios del libro: no considera el orden; cualquier nivel con SNi < Se se considera sin daño (86); con niveles mezclados da resultados aceptables (87); con niveles ordenados, crecientes => seguro, decrecientes => inseguro (88).

**Manson (9.2, Ec. 89-92):** reactualiza el diagrama S-N tras cada nivel.
```
Nivel 1: a1,b1,c1 de (31);  N1 por (84);  vida remanente  NR1 = N1 − n1          (89)
Nueva recta por (10^3 ; 0,9Su) y (NR1 ; SN1)                                       (90)
b2 = log10(0,9Su/SN1) / (log10(NR1) − 3) ;  c2 = 1/b2 ;  a2 = 0,9Su·(10^3)^b2      (91)
Se2 = a2·(10^6)^(−b2)   (nuevo límite de fatiga, Se2 < Se)                          (92)
```
Requiere NR1 > 1000. Para el nivel 3 se repite con la curva 2, etc. (Fig. 19).

**Miner con S-N dañada (9.3, Ec. 93-98):** equivale a una recta paralela (misma pendiente b) por (SN1, NR1): `a* = a·(NR1/N1)^b`, `S* = a*/10^(3b)`; tres zonas en (98): `N = 1 + 999(Su − SN2)/(Su − S*)` en `S* ≤ SN2 ≤ Su`; `(a*/SN2)^c` en `Se ≤ SN2 ≤ S*`; `∞` si `SN2 < Se`. Solo sirve para visualizar: se aplica siempre (83)+(84).

Verificación mía de la afirmación (88): ver sección 4 (caso numérico derivado).

### 2.12 Distribución probabilística de niveles (sec. 10, PDF 245)

Miner generalizado (99-104):
```
1/N = Σ pi/Ni            (101)  ->   1/N = ∫ p(σ̄)/N(σ̄) dσ̄ ,  ∫ p dσ̄ = 1      (102)
σ̄(x) = σ̄min + x(σ̄max − σ̄min) , x ∈ [0,1]                                       (103)
N = [ ∫_{x0}^{1} p(x)/N(x) dx ]^(−1)   con x0 tal que SN(x0) = Se                  (104)
```
Secuencia (PDF 245): (σ̄min, σ̄max) -> (103) σ̄(x) -> (13) (σm(x), σa(x)) -> (48) SN(x) -> (32) N(x) -> (104) N.
Distribuciones polinómicas (Fig. 21, Ec. en PDF 245):

| # | nombre | p(x) | ∫p dx (verificado) |
|---|---|---|---|
| 1 | uniforme | 1 | 1 |
| 2 | triangular | 2(1−x) | 1 |
| 3 | parabólica 1 | `1,5·x·(1−x²)` (según texto) | 0,375 (NO normaliza; ver sección 7) |
| 4 | parabólica 2 | 6x(1−x) | 1 |
| 5 | tipo normal 1 | 30x²(1−x)² | 1 |
| 6 | tipo normal 2 | 1,7647·x·{1 + x[11 + 12x(x−2)]} | 1,0000 |

Normal (105): `p(z) = e^(−z²/2)/√(2π)`, `z = (x−μ)/δ`, −3 ≤ z ≤ 3.

### 2.13 Anexo 1 – Propagación de grieta (PDF 246-248)

- Rango de tensiones `Δσ = σmax − σmin` (107); `ΔK = C·Δσ·√(π·a)` (108); estadios I-II-III y curva sigmoidea (Fig. 22-23).
- Paris (109): `da/dN = Cx·(ΔK)^m`. Tabla 1 (Cx en (mm/ciclo)/(N/mm^1,5)^m, m adimensional): ferríticos-perlíticos `2,18e-13`, m=3,00; martensíticos `5,74e-11`, m=2,25; inox austeníticos `7,48e-14`, m=3,25.
- Vida (110): `Nf = (1/Cx)·∫ da/(C·Δσ·√(πa))^m` entre ai y af, con C(a) función del tamaño de la grieta (integrar numéricamente).
- Algoritmo (Fig. 24, 6 pasos): (1) `af = (1/π)(Kc/(C(af)·σmax))²` iterando hasta convergencia; (2) `Δa = (af−ai)/n`; (3) `a_{j+1} = a_j + Δa`; (4) `aprom = (a_j + a_{j+1})/2`; (5) `ΔNj = Δa/(Cx·(C(aprom)·Δσ·√(π·aprom))^m)`; (6) `Nf = Σ ΔNj`.
- Limitaciones: no incluye efecto de R (la tabla da un Cx por material sin R), ni umbral ΔKth, ni etapa III separada; C(a) depende de la geometría y viene del Cap. 13 (Anexo 3 de ese capítulo).

---------------------------------------------------------------------------------------------------

## 3. Datos tabulados / gráficos / curvas a cargar

| Qué | Dónde | Cantidad | ¿Reemplazable por fórmula del libro? |
|---|---|---|---|
| Constantes fS (a, b) acero | Ec. 26, PDF 231 | 4 filas × (a en 4 unidades + b) | Es ya la fórmula; cargar solo MPa (4×2) |
| Coeficientes cuadráticos fS | Ec. 28, PDF 231 | 6 filas × 3 | Alternativa a la anterior |
| Neuber √ρ acero | Ec. 10-a/b | 2 polinomios cúbicos (4 coef. c/u) | Es fórmula |
| q aluminio 2024, acero fundido | Ec. 11, 12 | 2 fórmulas | Es fórmula |
| Fig. 9 (Se' vs Su) | PDF 230 | nube de puntos | Sí: Ec. 17 y 19 (no digitalizar) |
| Fig. 12 (σa/Se vs σm/Su) | PDF 233 | nube de puntos | Sí: curvas (39); no cargar |
| Fig. 21 (distribuciones p(x)) | PDF 245 | 6 curvas | Sí: las 6 fórmulas están escritas (ojo p3) |
| Tabla 1 Paris | PDF 247 | 3 filas × (Cx, m) | Cargar tal cual |
| **Anexo 2-a/b Kt, 16 casos** | PDF 249-250 | ver abajo | Solo el caso 1 tiene fórmula (cúbica) |
| Anexo 3-a aceros laminados HR/CD (Su, Sy, elong., reducc., HB) | PDF 251 | 23 filas (SAE 1006 a 1095) | No |
| Anexo 3-b aceros y aluminios | PDF 251 | 10 filas (Sy, Su) | No |
| Anexo 3-c aceros con tratamiento térmico | PDF 252 | 48 filas (Su, Sy, elong., reducc., HB, T°) | No |
| Anexo 3-d aluminios (incluye límite de fatiga a 5e8) | PDF 253 | 14 filas (9 forjado + 5 fundido) | No |
| Anexo 3-e titanio | PDF 253 | 8 filas (Sy, Su, elong., dureza) | No |
| Anexo 3-f fundición gris (Su tracc/compr/corte, E, Se, HB, Kt) | PDF 253 | 7 filas (ASTM 20 a 60) | No |

Para el usuario (tubos de 4130 soldados) lo más útil de Anexo 3: 4130 normalizado (fila 36: Su 670, Sy 436 MPa, coincide con el fy=435 de su ejemplo de fuselaje) y recocido (fila 37: Su 560, Sy 361), y los 4130 templados y revenidos (filas 31-35). Para chapa de aluminio: 2024 T3 (Su 482, Sy 345, Se 138 a 5e8) y 2017 O.

**Anexo 2: los 16 casos de Kt.** Cada gráfico tiene su σ nominal (hay que programarla). Curvas por caso (lectura de la imagen; contar de nuevo al digitalizar):

| Caso | Geometría y carga | Parámetros | Curvas aprox. |
|---|---|---|---|
| 1 | Barra rectangular con agujero central, tracción | x = d/w. Fórmula: `Kt = 3 − 3,16x + 4x² − 1,91x³` (σo = F/((w−d)t)) | 0 (fórmula) |
| 2 | Barra con agujero, flexión | d/w; d/t = 0; 0,25; 0,5; 1; 2; ∞ | 6 |
| 3 | Barra con entalla en U (ambos lados), tracción | r/h; w/h = 1,05; 1,1; 1,2; 1,5; 3 | 5 |
| 4 | Ídem, flexión | r/h; w/h = 1,02; 1,05; 1,1; 1,5; ∞ | 5 |
| 5 | Barra escalonada con filete, tracción | r/h; w/h = 1,02; 1,05; 1,1; 1,5 | 4 |
| 6 | Ídem, flexión | r/h; w/h = 1,02; 1,05; 1,1; 1,3; 3 | 5 |
| 7 | Eje escalonado, tracción | r/d; D/d = 1,02; 1,05; 1,1; 1,5 | 4 |
| 8 | Eje escalonado, torsión | r/d; D/d = 1,09; 1,2; 1,33; 2 | 4 |
| 9 | Eje escalonado, flexión | r/d; D/d = 1,02; 1,05; 1,1; 1,5; 3 | 5 |
| 10 | Eje con garganta/ranura, tracción | r/d; D/d = 1,02; 1,05; 1,15; 1,5 | 4 |
| 11 | Ídem, flexión | r/d; D/d = 1,02; 1,05; 1,5 | 3 |
| 12 | Ídem, torsión | r/d; D/d = 1,02; 1,05; 1,3 | 3 |
| 13 | Eje con agujero transversal (axial, flexión, torsión) | d/D 0 a 0,45 | 3 |
| 14 | Agujero cargado por perno (lug), tracción | d/w; h/w = 0,35; 0,5; ≥1,0 ("si hay huelgo aumentar Kt 30-50 %") | 3 |
| 15 | Eje con cuello/ranura, axial+flexión combinados | a/t (0,5 a 6); r/t = 0,03 a 1,0 | ~10 |
| 16 | Ídem 15, torsión | a/t (0,5 a 6); r/t = 0,03; 0,04; 0,06; 0,1; 0,2 | 5 |

Total ≈ 66 curvas (≈ 600-700 puntos si se digitalizan con 8-10 puntos por curva). Recomendación de prioridad para el usuario: casos 1, 2, 3, 4, 5, 6 (chapas y herrajes), 7, 9, 13 y 14 (agujero con perno, relevante en herrajes de fuselaje). Ninguno de los 16 casos es un tubo con agujero ni una unión soldada. Tablas de interpolación bilineal (r/d, D/d) con extrapolación prohibida y aviso fuera de rango.

---------------------------------------------------------------------------------------------------

## 4. Ejemplos resueltos del texto (para tests de validación)

El libro trae solo DOS ejemplos numéricos (más el caso típico simbólico (34) y la comparación (47)). No trae ejemplos numéricos de Marin, Neuber, tensiones combinadas, Kimmelmann (solo simbólico), Miner, Manson ni de la distribución probabilística. Las figuras 16, 17, 19 y 20 usan Su = 1000 MPa pero los puntos Se, SN1, N1 salen del gráfico, no del texto (no sirven como test cuantitativo).

### 4.1 Ejemplo (47), p. 14-12 (PDF 235) – CS por cada criterio
Datos: Sy = 0,75 Su; Se = 0,4 Su (Se ya de pieza); σm = 0,16 Su; σa = 0,06 Su; Kf = 1,5.
Intermedios: `a = Kf·σa/Se = 0,225`; `m = σm/Su = 0,16`; `m̄ = σm/Sy = 0,2133`.
Resultados: Soderberg 2,28; Goodman 2,60; Gerber 3,25; Marín 3,62; Bagci 3,82; fluencia (43-a) 3,41.
Reproducido por mí: 2,2814 / 2,5974 / 3,2458 / 3,6220 / 3,8226 / 3,4091. También reproduce (58) (σE de cada criterio, CS = Sy/σE). Uso: test directo de `cs_fatiga_uniaxial()`.
Aviso: la Fig. 13 (PDF 234) rotula "σm = 0,016 Su" pero el cálculo (47) usa 0,16 Su. Es una errata en la figura.

### 4.2 Caso típico (34), p. 14-9 (PDF 232)
Se' = 0,5Su; Se = 0,6Se' = 0,3Su => b = (1/3)log10(0,9/0,3) = 0,159 (el libro: ≈0,16), c ≈ 6,29 (el libro: 6). Test de (33)/(35): `1,2^(−c) = 0,318` (el libro dice "a un tercio"; con c=6 da 0,335).

### 4.3 Anexo 1, ejemplo de la placa con grieta, p. 14-25 (PDF 248)
Placa 70 × 5 mm (b = 35 mm semiancho), grieta pasante central de 2 mm (ai = 1 mm), AISI 4340 (Cap. 13, Anexo 1, material 9: Kc = 3160 N/mm^1,5), Pmin = 12.500 N, Pmax = 125.000 N. Cx = 2,18e-13; m = 3,00. `C(a) = (1 − 0,45x + 0,3x²)/√(1 − x)`, `x = a/b` (caso 1 del Anexo 3 del Cap. 13, h ≫ b).
- σmax = 357,14 MPa; σmin = 35,7; Δσ = 321,4 MPa.
- af converge a 17,3594 mm (x = 0,4960; C = 1,1981; 2af = 34,72 mm = 49,6 % del ancho). Primer iterado con C=1: 24,92 mm.
- 30 tramos: Δa = 0,5453; tabla fila 1: aprom = 1,273, C = 1,0024, ΔK = 644, ΔN = 9354; fila 30: aprom = 17,087, C = 1,1907, ΔK = 2804, ΔN = 113; **Nf = 35.232 ciclos**. Con 100 tramos: **35.621** (+1 %).
Reproducido por mí: af = 17,3592; Nf(30) = 35.231; Nf(100) = 35.621. Buen test (tolerancia 0,1 %).

### 4.4 Casos numéricos DERIVADOS por mí (NO son del libro; sirven como tests de regresión de la implementación y de las afirmaciones (88))
Miner y Manson: Su = 1000, Se = 300 MPa (piezas ya con reducciones) -> a = 2700, b = 0,15904, c = 6,2877.
- Orden decreciente: nivel 1 SN1 = 500, n1 = 0,5·N1 (N1 = 40.279); nivel 2 SN2 = 400 (N2 = 163.841). Miner: N restante en nivel 2 = 81.920. Manson: NR1 = 20.140, b2 = 0,19575, c2 = 5,1085, a2 = 3479,4, Se2 = 232,8; N restante nivel 2 = **62.967** (< Miner: Miner no conservativo, coincide con (88) y Fig. 20).
- Orden creciente: SN1 = 400, n1 = 0,5·N1; luego SN2 = 500. Miner 20.140 vs Manson 24.372 (Miner conservativo).
- Miner con S-N dañada, (97): `a*` hace que `N = (a*/SN2)^c` = 81.920 (coincide con Miner directo; confirma la equivalencia de 9.3).
Tensión combinada (Soderberg para ejes (60) vs 7.1): Su = 670, Sy = 436, Se = 200; σm = 40, σa = 60, τm = 10, τa = 20, Kfσ = 1,5, Kfτ = 1,3. 7.1 con Von Mises: σ*m = 43,589; σ*a = 100,638; Goodman CS = 1,760; Soderberg 1,658; Gerber 1,955; Marín 1,971. Por (60): σe = 236,2; τe = 66,68; σE = 262,92; CS = 1,658. Fluencia (77) con tensor máximo (σ=100, τ=30, sin Kf por ser dúctil): σ*max = 112,69; CS = 3,87.
Kimmelmann derivado: Sy = 436, Se = 200, M/W = 33,33, T/W = 66,67 -> CSK = 4,683 (con M=1e5, T=2e5, W=3e3 en unidades coherentes).

---------------------------------------------------------------------------------------------------

## 5. Propuesta de implementación en Struttura

### 5.1 Tipo y arquitectura

Tipo **B + A** (en dos capas):
- Capa 1: paquete nuevo `struttura/fatiga/` con funciones puras (sin CSV): `material.py` (Se', Marin, Neuber/Kf), `criterios.py` (Soderberg...Bagci, σE, SN, fluencia, Kimmelmann), `sn.py` (a,b,c, N de (84), Miner, Manson, Miner generalizado), `kt.py` (biblioteca Anexo 2), `fractura.py` (Paris, Anexo 1, opcional).
- Capa 2a (tipo B): calculadora autónoma `tipo;fatiga` con CSV de bloques -> informe HTML con paso a paso. Ejemplos: eje con filete (Kt caso 7/9), barra con agujero (caso 1), espectro de cargas con Miner/Manson.
- Capa 2b (tipo A): extensión del pórtico 3D: bloques opcionales al final de su CSV que usan los resultados ya resueltos. Sin tocar el solver.

### 5.2 Capa 2a – calculadora uniaxial/combinada (tipo B)

Entradas (bloques propuestos; ';' y coma decimal como el resto):
```
MATERIAL FATIGA   id; Su; Sy; Se_prima(opc); tipo(ductil|fragil); familia(acero|aluminio|fundicion); HB(opc)
PIEZA             id; material; terminacion; d / dimension equivalente; rotante(si|no); solicitacion(flexion|axial|torsion|combinada); fT(opc); fC(opc); f_otros(opc)
ENTALLA           id; Kt_sigma; Kt_tau; r  | caso_anexo2; parametros   (-> q, Kf)
CICLO             id; sigma_max; sigma_min; tau_max; tau_min | o tensores completos (6 componentes max/min)
ESPECTRO          id; ciclo; n_ciclos          (niveles para Miner/Manson, en el orden dado)
CONFIG            criterio(goodman|soderberg|gerber|marin|bagci|todos); vida(si|no); CS_pedido; cs_para_vida
```
Salidas por pieza: Se' -> factores -> Se; Kf; σm, σa (y tensores si combinada); σ*m, σ*a; CS por los 5 criterios + fluencia + modo de falla; σE; SN y N si CS pedido supera el de vida infinita; diagrama de Haigh con los 5 criterios y los puntos; curva S-N con los niveles; tabla de daño de Miner y comparación con Manson cuando el orden está dado; distribución probabilística (opcional).

### 5.3 Capa 2b – integración con el pórtico 3D (el punto clave)

Lo que ya existe y se reutiliza (leí `portico3d/tensor.py`, `esfuerzos.py`, `solver.py`, `entrada.py`):
- Cada caso o COMBINACION es un `Resultado` con esfuerzos de extremo `fb`; `esfuerzos.diagramas()` da `E = [N, Vy, Vz, T, My, Mz]` en 41 estaciones por barra.
- `tensor.campos(sec, E, y, z)` devuelve σx, τxy, τxz en cualquier punto; `tensor.puntos_candidatos(sec)` da 24 puntos por tubo (cada 15°) o 8-9 por sección rectangular. El tensor es LINEAL en E, es decir que el tensor de una combinación es la suma ponderada de los tensores de los casos. Eso justifica restar/sumar estados.
- COMBINACIONES (combinacion;caso;factor) ya permite armar los estados extremos del ciclo sin cambios (ej. `RAF_MAX: PESO×(1+Δn)`, `RAF_MIN: PESO×(1−Δn)`).

Mapeo al libro (7.1):
- "Carga media/alterna" (63) del libro = dos estados del pórtico: `max = combinación de un caso`, `min = otra combinación`. Entonces tensor medio `(σij)m = (σij,max + σij,min)/2` y tensor alterno `(σij)a = (σij,max − σij,min)/2`, componente a componente CON signo (esto da automáticamente la corrección fuera de fase (71): con signos, Von Mises del tensor diferencia = el término cruzado correcto). Alternativa de entrada: `caso_medio` + `caso_alterno` (max = m+a; min = m−a).
- Kf por esfuerzo (paso 2b): como `campos` es lineal en E, se descompone `E` en partes (N, flexión My/Mz, torsión T, corte V) llamando `campos` con E enmascarado, y se multiplica cada parte alterna por su Kf (Kf_axial, Kf_flexion, Kf_torsion, Kf_corte≈Kf_torsion, a confirmar con el usuario). La parte media dúctil lleva factor 1 (Ec. 14); frágil, Kt.
- Von Mises de cada tensor (66) con la fórmula (70)/(72) ya presente en `criterios()`: `vm = √(σx² + 3τ²)`. Para frágil, Rankine (75)-(76) ya existe en `criterios()`.
- Luego criterio uniaxial (sec. 5.1) con Se de la pieza, SIN Kf (ya aplicado), σE (sec. 6) y verificación a fluencia (77) con el tensor `max` (que ya calcula `analizar()` para el estado max).
- Vida: para cada punto y cada bloque del espectro, SN (48)/(50) -> N (84) -> daño ni/Ni.
- Barrido automático: para cada barra, 41 estaciones × 24 puntos × bloques; ranking por CS mínimo o daño máximo como hace `analizar()` con `criticos`. Salida: tabla de puntos críticos, CS por criterio, vida o daño, mapa de utilización a lo largo de la barra (como ya se hace para σeq).

Nuevos bloques CSV propuestos para el pórtico 3D:
```
FATIGA MATERIAL   material; Su; Sy; Se_prima(opc); acabado(rectificado|maquinado|laminado|forjado|...); ductil_o_fragil
FATIGA PUNTOS     id; barra; x; y; z; Kf_axial; Kf_flexion; Kf_torsion; fT(opc); r(opc)   | o "auto" (barrido)
FATIGA CICLOS     id; caso_max; caso_min; n_ciclos           (un nivel de carga por fila; el orden de filas = orden de Manson)
FATIGA CONFIG     criterio; objetivo(vida_infinita|vida_limitada); CS_pedido; signo_medio(vm_con_signo|abs)
```
Ejemplo de uso en el fuselaje del usuario (tubos 4130, ejemplo4_fuselaje_sonerai_ii): estados `MAX` = N38 (3,8 g), `MIN` = 1 g más la cola o 0 g (según vuelo); ciclo "tierra-aire-tierra" = (0 g -> +n g) y bloques de ráfaga (1 g ± Δn). Dónde usarlo: herrajes y nudos del larguero. IMPORTANTE: la teoría de vigas no ve las concentraciones de tensiones de las soldaduras ni de la zona afectada térmicamente; hay que cargar un Kf manual en los nodos críticos (el libro NO da Kf de uniones soldadas).

Para otros programas (pórtico plano, reticulado, emparrillado): solo hay σx por axil/flexión y τ (no tienen tensor completo), así que se puede conectar con la calculadora de la capa 2a usando `σmax`, `σmin` de la barra, o más adelante con un envoltorio similar.

### 5.4 Dificultad, tiempos y dependencias

| Parte | Tipo | Dificultad (1-5) | Tiempo |
|---|---|---|---|
| Núcleo uniaxial: Se', Marin, Neuber, Kf, 5 criterios, σE, SN, N, fluencia | B | 2 | 1 mediana |
| Miner + Manson + S-N con aluminio + informe HTML (Haigh, S-N, daño) | B | 3 | 1 mediana |
| Calculadora tipo B completa (CSV, validación, informe paso a paso, tests con los ejemplos 4.1-4.4) | B | 3 | 1 mediana |
| Biblioteca de materiales Anexo 3 (≈110 filas) | datos | 1 | 1 chica |
| Biblioteca Kt Anexo 2 (digitalizar 66 curvas + interpolación) | datos | 3 (trabajo manual y de verificación) | 1 grande si son los 16 casos; 1 mediana si solo los 8-10 prioritarios |
| Integración con pórtico 3D (tensores medio/alterno, Kf por esfuerzo, barrido, mapa de utilización, informe) | A | 4 | 1 grande |
| Kimmelmann (raíz sobre λ) | B | 2 | 1 chica |
| Distribución probabilística (Miner continuo, 6 p(x), normal) | B | 2 (pero con ambigüedades, sec. 7) | 1 chica |
| Anexo 1 Paris/vida remanente (necesita C(a) de Cap. 13) | B | 2 | 1 chica |

Dependencias: criterios de falla estática y tensor (ya implementados en `tensor.py`); Cap. 13 (Mecánica de fractura: Kc y C(a)) solo para el Anexo 1; no depende de otros capítulos para el resto.

### 5.5 Qué aplica a cada caso

- **Fuselaje tubular soldado (4130):** aplican Se' = 0,5Su (Su 670 -> 335 MPa), fS de tubo estirado en frío (Ec. 26: 4,51·Su^−0,265 = 0,804 para Su=670), σm + σa por casos de carga del pórtico, Goodman + fluencia, Miner por espectro (ráfaga, maniobra, tierra-aire-tierra). No aplican directamente: Kt (no hay casos de tubo ni soldadura), fT de ejes rotantes (el fuselaje no rota; `de = 0,37d` es para sección maciza), el Kf de soldaduras (hay que pedirlo). Valor alto: un estado de tensión dado por el pórtico en cada punto de cada tubo ya existe, solo falta el criterio de fatiga.
- **Estructuras mecánicas generales (ejes, bielas, herrajes):** aplica todo: Marin, Kt de ejes (casos 7-12), Soderberg para ejes (60), torsión + flexión, Kimmelmann, vida limitada, espectros.

---------------------------------------------------------------------------------------------------

## 6. Anexo teórico para los informes (qué incluir, sin copiar texto)

Para cada informe de fatiga, ecuaciones principales con referencia "Compendio Cap. 14, Ec. (n)":
1. Definición de ciclo (13)/(36); R (38).
2. Límite de fatiga: (17) o (19), Marin (20) con (21)-(26) y Neuber (6), (9), (10).
3. Curva S-N de pieza: (30)-(32); aluminio: 10^7 y b = ¼ log.
4. Criterios de interacción (39) con la tabla (14) de Kt/Kf, fluencia (43), CS (44), σE (58)-(59).
5. Tensiones combinadas: pasos 1-4 (63)-(67), Von Mises (69)-(73), Soderberg para ejes (60); condición de uso (cargas proporcionales).
6. Vida limitada (48)-(50), (32), (84).
7. Daño: Miner (83), Manson (89)-(92); advertencia (88).
8. Si se usa el espectro continuo: (101)-(104).
9. Si se usa propagación de grieta: (108)-(110) con Tabla 1.
Siempre agregar la advertencia del propio libro (14-1): los resultados son "una guía" por el carácter empírico.

---------------------------------------------------------------------------------------------------

## 7. Riesgos, ambigüedades y preguntas para el usuario

Inconsistencias o erratas detectadas (verificadas en la imagen o por cálculo):
1. Fig. 13 (PDF 234) rotula "σm = 0,016 Su" pero el ejemplo (47) usa 0,16 Su: errata en la figura.
2. Fig. 21, curva 3 `p(x) = 1,5·x·(1−x²)`: su integral es 0,375, no 1. Con `1,5·(1−x²)` la integral es 1 y coincide con la curva dibujada (empieza en ~1,5 en x=0). Probable errata; preguntarle al usuario o implementar `1,5(1−x²)` avisando.
3. Eje no rotante rectangular (22): `de = 0,88·√(a·b)`. En la bibliografía clásica (Shigley) recuerdo 0,808, no tengo la fuente a mano para confirmar; verificar antes de usar.
4. Tabla (26) forjado: 272 MPa equivale a 39,45 kpsi y la columna dice 39,3 (en la bibliografía clásica recuerdo 39,9; no lo pude confirmar). Usar solo la columna MPa.
5. Aluminio: el texto (4.1, PDF 230) define Se a 10^7 ciclos, pero (19) con tope 131 MPa y la tabla del Anexo 3-d (límite a 5·10^8) corresponden a vida mucho mayor; hay que decidir si se usa 10^7 o 5e8 y usar valores coherentes (la tabla 3-d da límites de fatiga a 5e8, más bajos que a 10^7).
6. (12) dice "acero fundido q = 0,2" y el recuadro siguiente habla de "fundición" (hierro fundido) con q entre 0 y 0,2; y el Anexo 3-f da una columna "coeficiente de concentración de tensiones Kt" (1,00 a 1,50). No se explica cómo se combina con q=0,2.
7. (18) `Su = 3,5·HB` (el valor usual es 3,45) y tope 690 MPa en (17) (Shigley: 700): diferencias menores.
8. (84) para SNi > Su da N < 1 (y negativo si SNi > 1,1·Su); tratar SNi ≥ Su como falla inmediata (N = 0 o 1).
9. (60): usa el mismo cociente Sy/Se para σ y para τ (la torsión entra por Von Mises con el factor 3 dentro de la raíz). Es coherente con fC = 1 en combinadas, que es lo que el libro pide (PDF 231); no mezclar con fC = 0,59.
10. Notación: el texto extraído pierde barras y signos (m̄ = |σm|/Sy, a1 negativos en (28), el "≠" de (77)). Siempre verificar con la imagen.
11. En (104) y el "procedimiento" de la sección 10: se dice que de σ̄ se pasa a (σm, σa) por (13), pero (13) necesita σmax y σmin. No dice qué es σ̄ (el máximo del ciclo con σmin fijo? con R fijo? el σa con σm fijo?). Hay que fijarlo con el usuario.
12. (105) normal: falta el 1/δ y la truncación a ±3δ no normaliza exacto.

Diferencia de conservadurismo entre el procedimiento 7.1 y la fórmula de Soderberg para ejes (60) (análisis mío): como Von Mises es una norma, `‖σm‖ + ‖Kσa‖·Sy/Se ≥ ‖σm + Kσa·Sy/Se‖`; es decir, 7.1 (VM por separado y sumar) es siempre ≥ conservador que (60) (VM del tensor sumado); son iguales si los tensores son proporcionales (en mi caso derivado: 262,98 vs 262,92). Conviene calcular ambos y mostrar la diferencia.

Supuestos que habría que preguntarle al usuario (el usuario pidió "siempre preguntame, corregime y proponé"):
- Signo de la tensión media efectiva: Von Mises da siempre ≥ 0 y pierde si σm es de compresión; el libro (42) dice que con σm < 0 solo cuenta σa, pero el procedimiento 7.1 trabaja con VM positivos. Propuesta: Von Mises "con signo" (signo de la traza σx+σy+σz, o de la principal dominante) para decidir si se aplica (42). ¿Aceptás?
- Fatiga con CS (vida infinita) o con vida limitada (Se pedido)? ¿CS=1 para vida real y CS>1 como margen en tensión (Ec. 35)?
- ¿Criterio por defecto? El libro recomienda Goodman (6.2) + fluencia aparte; Soderberg si se quiere cubrir ambas fallas. Propuesta: mostrar los 5 y marcar Goodman.
- ¿Orden de los bloques de carga importa (Manson) o espectro mezclado (Miner, Ec. 87)? Para ráfagas aleatorias Miner; para "una vez 1 g -> 3,8 g y después..." Manson.
- Kf de soldaduras y zonas afectadas: el libro no los da; ¿se ingresan manualmente por nodo?
- fT para tubos no rotantes: el libro solo da `de` para sección maciza redonda o rectangular; ¿usar `de` = 0,37·D exterior para tubo? Propuesta mía solo si el usuario lo acepta.
- Alcance de la biblioteca Kt: ¿los 16 casos o solo los prioritarios?
- ¿Confiabilidad?: el libro no tiene factor de confiabilidad (solo menciona curva de 50 % vs 95 % de supervivencia en Fig. 7); si el usuario quiere, se puede agregar un factor, pero eso saldría de otra fuente.
- Las cargas del pórtico se asumen cuasi-estáticas y en fase: no hay efecto dinámico ni amplificación; cualquier amplificación va en los factores de carga del usuario.

Límite de validez: el método asume ciclos altos (N > 10^3), elasticidad lineal, material dúctil o frágil homogéneo, tensiones uniaxiales o combinadas proporcionales y todas con la misma ley temporal. No cubre cargas de amplitud variable con aleatoriedad completa (rainflow), efecto de la secuencia fuera de Manson, corrosión, temperatura, ni propagación con R≠0 (Paris sin R).
