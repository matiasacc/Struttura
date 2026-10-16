# Cap. 2 - Criterios de falla para tensiones combinadas / Coeficiente de seguridad (PDF págs 27-42; libro 2-1 a 2-16)

Convenciones: "p.NN" = página del PDF; "(NN)" = ecuación del libro (la numeración del Cap. 2 reinicia en 1). σt = resistencia a tracción (+), σc = resistencia a compresión (**negativa**, el libro escribe |σc| donde la necesita), σf = tensión de falla de un material dúctil (fluencia) con |σc| = σt. Tensiones principales σ(1) > σ(2) > σ(3). En tensión plana el libro usa σ1, σ2 "no ordenadas" (sec. 5.1) y σI > σII (Anexo 4); cuidado con la notación (ver Riesgos). Todas las fórmulas fueron verificadas mirando la página como imagen.

---

## 1. Qué resuelve y para qué sirve

Pasa de "falla en tracción uniaxial" a "falla con tensiones combinadas": presenta los cuatro criterios clásicos (máxima tensión normal/Rankine, máxima tensión de corte/Tresca, energía de distorsión/Von Mises, Mohr y Mohr modificado), define el **coeficiente de seguridad Cs como factor por el que hay que multiplicar las cargas** hasta que la variable del criterio alcance la de falla en el punto crítico, y la **tensión efectiva σ\*** (tal que Cs = σf/σ\*). Cierra con el problema de Cs cuando la tensión no es proporcional a la carga (casos no lineales).

Para diseño: es el paso final de la cadena Cargas → Esfuerzos → Tensiones → criterio → σ\* → Cs (esquema p.34). Qué criterio usar según el material (conclusiones sec. 7, p.32): frágil isótropo → Rankine; frágil con |σc| ≠ σt → Mohr modificado; dúctil → Von Mises (Tresca casi igual de bueno); dúctil con |σc| > σt → Mohr.

---

## 2. Fórmulas y algoritmos clave

### 2.1 Criterios (sec. 2-4, p.27-29)
- **Rankine** (1), p.27: falla si `σ(1) ≥ σt` o `σ(3) ≤ σc`. No usar en dúctiles (predice falla bajo presión hidrostática y no se verifica) (p.28).
- **Tresca** (2)-(4), p.28: `τmáx = ½(σ(1)−σ(3))`; en tracción simple τf = σf/2 ⇒ falla si `σ(1) − σ(3) ≥ σf`.
- **Von Mises** (5)-(7), p.29: densidad de energía de distorsión `Wd = (1+ν)/(6E) [(σ1−σ2)²+(σ2−σ3)²+(σ3−σ1)²]` (5) (deducción Anexo 2, (53)); en tracción Wd = (1+ν)/(6E)·2σf² (6); falla si `(σ1−σ2)²+(σ2−σ3)²+(σ3−σ1)² ≥ 2σf²` (7).
- Propiedad (p.29): Tresca y Von Mises no cambian al sumar Δ a las tres principales (insensibles a la presión hidrostática).
- Superficies de falla en σi/σf (p.29): Rankine = cubo; Tresca = prisma hexagonal infinito; Von Mises = cilindro infinito; mismo eje σ1=σ2=σ3.
- Tensión plana (σ3=0), sec. 5.1, p.29-30: Rankine `|σ1/σf| ≤ 1` y `|σ2/σf| ≤ 1` (8) cuadrado; Tresca: mismo signo (9) `|σ1/σf| ≤ 1` (rectas verticales/horizontales), signo distinto (10) `|σ1/σf − σ2/σf| ≤ 1` (rectas a 45°); Von Mises: `(σ1/σf)² + (σ2/σf)² − (σ1/σf)(σ2/σf) ≤ 1` (11) elipse a 45° (Fig. 1, p.30).

### 2.2 Mohr (sec. 6, p.31-32; Anexo 4, p.40-42)
- Idea (p.31): de los 3 círculos de Mohr solo el mayor (σ(1), σ(3)) decide; se construye una envolvente a partir de ensayos de tracción y compresión (y torsión); por simplicidad se usa **recta tangente a los círculos de tracción y compresión** (Fig. 14, p.40).
- Propiedad (Anexo 3, (54)-(62), p.38-39): los pares (σνν, σνs) posibles están en la zona entre los 3 círculos; τmáx = (σ1−σ3)/2 (62).
- **Dúctil con |σc| = σt**: Mohr = Tresca, `Cs = σf/(σ(1)−σ(3))` (63).
- **Dúctil con |σc| ≠ σt (σt < |σc|)**, con σ(1) > 0 > σ(3) (distinto signo), (64), p.40:
  `Cs = |σc| σt / ( σ(1) |σc| + |σ(3)| σt )`  ⇔ `Cs = ( σ(1)/σt + |σ(3)|/|σc| )⁻¹`
  (construcción: S1=Cs σ(1), S3=Cs σ(3), A=(S1+S3)/2, R=(S1−S3)/2, R1=σt/2, R2=|σc|/2, R=R2−(R2−R1)(R2+A)/(R2+R1); igualando se despeja Cs).
- **Tensión plana** (σ3 = 0), σI > σII (65)-(67), p.41 (con σc negativa):
  - ambas positivas: `Cs = σt/σI` (65)
  - distinto signo: `Cs = (σI/σt + |σII|/|σc|)⁻¹` (66) (= (13) p.32)
  - ambas negativas: `Cs = |σc|/|σII|` (67)
  - Equivalente por cuadrantes (12)-(14), p.32: 1er cuadrante `Cs = σt/mayor(σ1;σ2)`; 3er cuadrante `Cs = |σc|/mayor(|σ1|;|σ2|)`; 4º cuadrante (σ1>0, σ2<0) `Cs = (σ1/σt + |σ2|/|σc|)⁻¹` (13); 2º cuadrante (σ1<0, σ2>0) `Cs = (|σ1|/|σc| + σ2/σt)⁻¹` (14).
  - Zona segura (Fig. 5-b): hexágono de vértices (σt,σt), (σt,0), (0,σc), (σc,σc), (σc,0), (0,σt) (lo deduje de (12)-(14); el libro solo lo muestra en la figura).
- **Mohr modificado (frágil, |σc| > σt)**, Anexo 4 sec. 3, p.41-42. Con α = σt/|σc| y solo σ(1), σ(3):
  - `σ(1) > 0` y `|σ(3)| ≤ σ(1)`: `Cs = σt/σ(1)` (70)
  - `σ(1) > 0` y `|σ(3)| > σ(1)`: `Cs = menor{Φ1, Φ3}` (71), con `Φ1 = σt/σ(1)` y `Φ3 = |σc| / ( |σ(3)| + σ(1)(|σc|/σt − 1) )` (73)
  - `σ(1) ≤ 0` y `σ(3) < 0`: `Cs = |σc|/|σ(3)|` (72)
  - Tensión plana (74)-(76), p.42: `σI>0, |σII|<σI`: `Cs=σt/σI`; `σI>0, |σII|>σI`: `Cs = σc/[σII + σI(1+σc/σt)]` (σc, σII negativas); ambas negativas: `Cs = σc/σII`.
  - Nota: si |σc|→σt coincide con Rankine (p.32). En (71) siempre gana Φ3 (es menor), se puede simplificar (verificado, ver 7).

### 2.3 Coeficiente de seguridad (sec. 8, p.33-34)
- Definición (p.33): factor por el que hay que multiplicar las cargas para que la variable del criterio alcance la de falla en el punto más crítico. En problemas lineales: `Cs = tensión de falla / tensión máxima de trabajo = carga de falla / carga de trabajo` (15): `Cs = OP'/OP` sobre el rayo desde el origen en el plano σ1-σ2 (Fig. 6).
- Rankine (16): `Cs = σt/σ(1)` (todas ≥0); `Cs = σc/σ(3)` (todas ≤0); distinto signo `Cs = menor(σt/σ(1) ; σc/σ(3))`.
- Tresca (17): `Cs = σf/(σ(1) − σ(3))`, con las **tres** principales ordenadas.
- Tensión plana + Tresca (18)-(20), p.34: `A=(σx+σy)/2`, `R=sqrt(((σx−σy)/2)²+τxy²)`; `σx' = A+R`, `σy' = A−R`, `σz = 0` (19). `Cs = σf/(2 τmáx)`, con `τmáx = ½(|A|+R)` si |A| > R, y `τmáx = R` si |A| ≤ R (20). (No confundir τmáx con el radio R: Fig. 8, 4 casos que se reducen a 2 resultados).
- Von Mises (21)-(24), p.34: `Cs = σf / sqrt(½[(σ1−σ2)²+(σ2−σ3)²+(σ3−σ1)²])` (22); con componentes (sin principales) **(23)**: `Cs = σf / sqrt( (σx²+σy²+σz²) − (σxσy+σyσz+σzσx) + 3(τxy²+τyz²+τzx²) )`; plana (24): `sqrt(σx²+σy²−σxσy+3τxy²)`.

### 2.4 Tensión efectiva (sec. 9 y Anexo 5, p.35 y p.42)
- `Cs = σf/σ*` (25) y carga segura si `σ* ≤ σadm` (26). (En Anexo 5 (77): Cs = σt/σ\*; para dúctil con |σc|=σt se usa σf=σt.)
- 3D (tensor lleno): Tresca `σ* = σ(1) − σ(3)` (27); Von Mises (28) y (29) con componentes.
- Plana (30) (una fila nula): Tresca `σ* = |A| + R` si |A| > R; `2R` si |A| ≤ R (31); Von Mises `sqrt(σx²+σy²−σxσy+3τxy²)` (32).
- Caso intermedio (33) (τxz=τyz=0, σz ≠ 0): Tresca `σ* = mayor{σx';σy';σz} − menor{σx';σy';σz}` (34) con σx',σy' = A±R; Von Mises (35): `sqrt((σx²+σy²+σz²) − (σxσy+σyσz+σzσx) + 3τxy²)`.
- **Tabla resumen (Anexo 5, p.42)**, con α = σt/|σc|:

| Material | σ\* caso general | σ\* tensión plana |
|---|---|---|
| Dúctil ∣σc∣=σt, Von Mises | `sqrt(½[(σ(1)−σ(2))²+(σ(2)−σ(3))²+(σ(3)−σ(1))²])` | `sqrt(σx²+σy²−σxσy+3τxy²)` |
| Dúctil ∣σc∣=σt, Tresca | `σ(1) − σ(3)` | `R+∣A∣` si ∣A∣>R; `2R` si ∣A∣≤R |
| Dúctil ∣σc∣>σt, Mohr | `σ(1) + α∣σ(3)∣` | `R+A` (A>R); `R+A+α(R−A)` (∣A∣<R); `α(R+∣A∣)` (A<−R) |
| Frágil ∣σc∣=σt, Rankine | `mayor{∣σ(1)∣;∣σ(3)∣}` | `R+∣A∣` |
| Frágil ∣σc∣>σt, Mohr modificado | `σ(1)` (σ(1)>0, ∣σ(3)∣≤σ(1)); `mayor{σ(1);Φ}` (σ(1)>0, ∣σ(3)∣>σ(1)); `α∣σ(3)∣` (σ(1)≤0, σ(3)<0), con `Φ = α∣σ(3)∣ + (1−α)σ(1)` | `R+A` (A>0); `R+A(1−2α)` (−R<A<0); `α(R+∣A∣)` (A≤−R) |

  Verifiqué que Φ = α|σ(3)|+(1−α)σ(1) coincide con (73) vía Cs = σt/Φ, y que la fila "Mohr" concuerda con (64)/(66). La fila Rankine con tensión plana `R+|A|` = mayor{|σ(1)|,|σ(3)|} con σ(2)=0.

### 2.5 Cs en casos no lineales (sec. 10, p.36)
- Lineal: `Cs_tensiones = σfalla/σ*` (36) y `Cs_cargas = carga última/carga aplicada` (37) coinciden.
- No lineal (σ\* crece más rápido que la carga, Fig. 10): `(Cs)cargas < (Cs)tensiones` (38) y el cálculo lineal es **inseguro**. Si σ\* crece más lento (Fig. 11): `(Cs)cargas > (Cs)tensiones` (39) y el lineal queda del lado seguro.
- **Recomendación del libro: en casos no lineales usar `(Cs)cargas`** (37). Algoritmo: hallar λ\* tal que σ\*(λ·P) = σf en el punto crítico (raíz de una función monótona: bisección/secante con una corrida no lineal por evaluación).
- Números de las figuras: Fig. 10: Cs cargas 1,83; Cs tensiones 2,24; Cs lineal 2,71. Fig. 11: 3,70; 3,00; 2,75. (Ver 4.)

### 2.6 Complemento: deformaciones volumétricas y distorsivas (Anexo 1-2, p.37-38)
- `ΔV = (ε1+ε2+ε3) dV` (42); `εm=⅓(ε1+ε2+ε3)` (44); `ε = εv + εd` (45). Isótropo: σ = σh + σd.
- W en principales (46)-(48): `W = 1/(2E)[σ1²+σ2²+σ3² − 2ν(σ1σ2+σ2σ3+σ3σ1)]`; hidrostática (49)-(51): `Wh = (1−2ν)/(6E) (σ1+σ2+σ3)²`; `Wd = W − Wh` (52) ⇒ (53).

---

## 3. Datos tabulados / gráficos / curvas a cargar

- **No hay tablas numéricas de materiales** ni datos a digitalizar. Todo es analítico y se puede reemplazar por las fórmulas anteriores:
  - Fig. 1 (p.30) lugares de falla plana: (8), (9)-(10), (11).
  - Fig. 5 (p.32) polígonos de Mohr / Mohr modificado: de (12)-(14) y (74)-(76). Vértices de Mohr modificado (Fig. 5-c), deducidos por mí de (70)-(73): (σt,σt), (σt,−σt), (0,σc), (σc,σc), (σc,0), (−σt,σt). Verificar contra la figura al implementar.
  - Fig. 8 (p.34) cuatro casos de Mohr: se cubre con (20)/(31).
- Fig. 2 (p.30) son puntos experimentales (dúctiles: Al, Cu, Ni, aceros; frágiles: Al, fundición 1 y 2) sin valores tabulados; solo ilustran, no hace falta cargarlos.
- Fig. 6, 10, 11: figuras conceptuales; Fig. 10/11 no dan las curvas σ\*(carga), solo cinco números (ver sección 4).
- Los datos de material (σf, σt, σc, σadm) los ingresa el usuario. Struttura ya los tiene: `fy`, `sut`, `suc`, `sadm`, `teoria`.

---

## 4. Ejemplos resueltos del texto

**Ejemplo 1 (Anexo 4, p.40)**: dúctil, σt = 200, σc = −400 (MPa, unidades del libro implícitas), σx = 76, σy = 4, τxy = 48, σz = τxz = τzy = 0.
- A = 40; R = sqrt(36²+48²) = 60 ⇒ σ(1) = 100, σ(3) = −20 (σ(2)=0).
- (64): Cs = 400·200/(100·400 + 20·200) = 80000/44000 = **1,82** (1,8182).
- Mismo estado con |σc| = σt = 200: (64) → 200·200/(100·200+20·200) = 40000/24000 = **1,67**; Tresca (17): 200/[100−(−20)] = **1,67** (1,6667).

**Ejemplo 2 (Anexo 4, p.41)**: σ(1)=100, σ(2)=0, σ(3)=−20; σt=200, σc=−400; 4º cuadrante. (66): Cs = (100/200 + 20/400)⁻¹ = **1,82** (coincide con el Ejemplo 1; (64) y (66) son la misma fórmula).

**Estados cualitativos (p.28-29)** (σi en múltiplos de σf), útiles como casos de test de `no falla`/`falla`:
| σ1, σ2, σ3 | Tresca (σ1−σ3) | Von Mises (Σ(σi−σj)², límite 2) | Libro dice |
|---|---|---|---|
| 9; 8,5; 8,01 | 0,99 | 1,4702 | no falla (hidrostático alto) |
| 5; 4,5; 4,01 | 0,99 | 1,4702 | no falla (Von Mises y Tresca) |
| 1,1; 0,9; 0,2 | 0,9 | 1,34 | Tresca no predice falla "correcto" |
| 0,6; 0,2; −0,5 | 1,1 | 1,86 | Tresca predice falla "correcto" |

(Calculé las columnas Tresca/VM; ver Riesgos sobre el último caso.)

**Fig. 10/11 (sec. 10, p.36)**: valores 1,83/2,24/2,71 y 3,70/3,00/2,75 (leídos de curvas no dadas). No se pueden reproducir sin la curva; para test usar curvas analíticas propias.

**Tests derivados (calculados por mí con numpy, NO del libro)**, con σt=200, σc=−400 (α=0,5) y los estados principales (σ(1), σ(3)):
| (σ(1), σ(3)) | Mohr (64)/(66) | Mohr modificado (70)-(73) |
|---|---|---|
| (100, −20) | 1,8182 | 2,0 |
| (50, −150) | 1,6 | 2,0 |
| (0, −100) | 4,0 | 4,0 |
| (150, −300) | 0,6667 | 0,8889 |
| (100, +100) | 2,0 (σ(3) tratado como 0) | 2,0 |

Von Mises del Ejemplo 1 (σf = 200): σ\* = sqrt(76²+4²−76·4+3·48²) = 111,3553 ⇒ Cs = 1,7961 (derivado). Chequeo cruzado con (22) usando principales (100, 0, −20): igual valor.
Térmica/energía: Wd (53) = W − Wh (52) verificado con σ=(100,−40,25), E=210000, ν=0,3: Wd = 0,0303849 N·mm/mm³ (derivado).

---

## 5. Propuesta de implementación en Struttura

### 5.1 Lo que ya está (portico3d/tensor.py) vs. lo que agrega el capítulo

Lo que ya hay:
- Estado de viga [σx,τxy,τxz] con σ2 = 0; principales analíticas σ1=(σx+√(σx²+4τ²))/2 ≥ 0 ≥ σ3 (coincide con (18)-(19) donde |A| ≤ R siempre, es decir Tresca = 2R = √(σx²+4τ²), caso c/d de la Fig. 8).
- Von Mises √(σx²+3τ²) = (24) con σy=0 (τ = hypot(τxy, τxz)); Tresca √(σx²+4τ²) (27)/(31); Rankine con CS = mín(sut/σ1, suc/|σ3|) (16); "Mohr-Coulomb" con CS = 1/(σ1/sut + |σ3|/suc) = (64) ≡ (66)/(65)-(67) (verifiqué que tiene los mismos casos: ambas positivas → sut/σ1; ambas negativas → suc/|σ3|; es la fórmula de Mohr **para dúctiles con |σc|>σt**). Lee sut, suc (por defecto = sut), fy, sadm y elige la teoría; calcula también cs_adm = sadm/σeq (26).
- Informe con tensor en puntos, círculo de Mohr, equilibrio.

Lo que agrega el capítulo y **falta**:
| Ítem | Estado | Comentario |
|---|---|---|
| **Mohr modificado (frágil, σt≠∣σc∣)**, (70)-(76), Anexo 5 fila 5 | falta | El código llama "Mohr-Coulomb (frágil)" a lo que el libro llama Mohr (dúctil, σt<∣σc∣). Para fundición/frágiles el libro recomienda Mohr modificado. Es ≥ Mohr en CS (menos conservador) y coincide con Rankine si ∣σc∣=σt. Es agregar una teoría "mohrmod". |
| **σ\* de Mohr** (Anexo 5: σ(1)+α∣σ(3)∣) | falta/inconsistente | En `criterios()` la teoría "mohr" reporta como σeq el valor de Rankine (`eq["mohr"] = rankine`), mientras Cs = 1/(σ1/sut+∣σ3∣/suc). Entonces Cs ≠ σt/σeq para Mohr y la "utilización" puede no ser coherente. Agregar σ\*mohr = σ1 + (sut/suc)∣σ3∣ y σ\*mohrmod. |
| Tensor lleno (σy, σz, τyz ≠ 0): (22)-(23), (27)-(29) | falta | Hoy asume σy=σz=τyz=0. Necesario para presión interna en tubos (σθ), caso intermedio (33)-(35), y para pegar tensores de un FEA. Necesita principales 3×3 (Cap. 1). |
| Tensión plana general: Fig. 8, (20), (31) | parcial | Funciona porque en vigas ∣A∣≤R; con σy≠0 aparece el caso ∣A∣>R (Tresca = ∣A∣+R), hay que implementarlo. |
| Lugar de falla σ1-σ2 con punto P y Cs=OP'/OP (Fig. 6, Fig. 1, Fig. 5) | falta | Gráfico SVG para informe (cuadrado/hexágono/elipse/hexágono Mohr) con el estado. Alta utilidad didáctica. |
| **Cs en casos no lineales** (sec. 10) | falta | Struttura es 100 % lineal (matricial). Hay que definir "Cs_cargas = λ\* tal que σ\*(λP)=σf" cuando exista un análisis no lineal (p.ej. P-Delta). En el caso lineal ya se cumple (36)=(37). |
| Tensión efectiva σ\* unificada y `σ* ≤ σadm` | hecho (eq_gob, cs_adm) | Falla solo el σ\* de Mohr (ver arriba). |
| Descomposición volumétrica/distorsiva, Wd (53) | falta | Informativo; sirve para el anexo (de dónde sale Von Mises). |
| Elección entre fluencia y rotura como σf (p.28) | parcial | El código usa fy; el libro dice que σf depende del modo de falla (fluencia, rotura...). |

### 5.2 Propuesta

- **Tipo A (extensión de lo existente, prioridad alta)**: en `portico3d/tensor.py` (a) agregar teoría `mohrmod` y el σ\* correcto para `mohr`; (b) aceptar opcionalmente sy, sz, tyz por punto. Mantener salidas actuales. **Dificultad 2/5; tiempo: chica** (a) y **mediana** (b).
- **Tipo B (calculadora, compartida con Cap. 1)**: "Estado tensional 3D / Coeficiente de seguridad": entrada `ESTADOS id;sx;sy;sz;txy;tyz;txz` (o principales directamente `PRINCIPALES id;s1;s2;s3`) y `MATERIALES id;fy;sut;suc;teoria;sadm;sf_tipo`; salida HTML paso a paso: principales, tabla de los 5 criterios con σ\* y Cs (todos), gráfico del lugar de falla con P/P' si es plano, aviso de criterio recomendado según el material (sec. 7). **Dificultad 2/5, tiempo: mediana.**
- **Tipo B'**: `cs_cargas(f_sigma_eq, P)` con raíz por bisección para el caso no lineal; solo útil cuando exista P-Delta u otro no lineal; hoy se puede dejar como utilidad y test (con curvas analíticas inventadas). **Dificultad 1/5 (utilidad) / 4/5 (si incluye un solver no lineal; fuera de estos capítulos), chica/grande.**
- **Tipo C**: anexo teórico (sec. 6) y la explicación de cada criterio en el informe del pórtico 3D.

**Dependencias**: Cap. 1 (principales, invariantes, Mohr). Sec. 10 requeriría un no lineal (otros capítulos: Cap. 5 de pandeo).

**Fuselaje de avión ligero (tubos soldados)** y estructuras mecánicas: materiales dúctiles (aceros/aluminio) → Von Mises/Tresca con σf = fluencia; Cs en el sentido del libro = factor de cargas, que es el mismo concepto que el "factor de carga última/límite" de reglamentos de aeronavegabilidad (verificar la norma aplicable y el factor requerido; no lo fijo acá). Para uniones soldadas hay que decidir qué σf usar (zona afectada por el calor). Fundición/frágiles (soportes, carcasas) → Rankine/Mohr modificado. Los criterios son **estáticos**; no cubren fatiga ni concentración de tensiones.

---

## 6. Anexo teórico para los informes (con referencia "Cap. 2")

1. Definición de Cs y de σ\*: Cs = σf/σ\*; σ\* ≤ σadm (25)-(26), esquema Cargas→Esfuerzos→Tensiones→σ\*→Cs (p.34).
2. Rankine: σ(1) ≥ σt ó σ(3) ≤ σc (1); Cs (16).
3. Tresca: σ\* = σ(1)−σ(3) (27); en plano con A, R: (31). Recordar siempre la tercera principal (nula en plano) (p.34, Anexo 4 p.40).
4. Von Mises: σ\* = √(½Σ(σi−σj)²) (28); con componentes (29); viga/plano: σ\* = √(σx²+σy²−σxσy+3τxy²) (32); para el estado de viga σ\* = √(σx²+3τ²).
5. Mohr (σt<|σc|): Cs = (σ(1)/σt + |σ(3)|/|σc|)⁻¹ (64), (66), σ\* = σ(1)+α|σ(3)| (Anexo 5).
6. Mohr modificado (70)-(76) y α=σt/|σc|, si se agrega.
7. Cuándo usar cada uno (sec. 7, p.32) y nota de "dúctil = alargamiento > 5 %".
8. Cs lineal vs. no lineal: (36)-(39) y recomendación Cs_cargas (una nota).

---

## 7. Riesgos, ambigüedades, preguntas

1. **Notación de principales**: σ(1)>σ(2)>σ(3) (ordenadas, con σ(2) incluyendo posiblemente la nula), σ1, σ2 "sin ordenar" en sec. 5.1/8 y σI>σII (Anexo 4). Para Tresca y Mohr hay que incluir la tensión nula como principal (el libro lo remarca, Fig. 13 p.40).
2. **Signo de σc**: (64)/(66) usan |σc|; (75)/(76) usan σc negativa con signos que cierran (σc/σII>0). Normalizar internamente a magnitudes positivas (suc = |σc|) como ya hace Struttura.
3. **Sec. 3, ejemplo (0,6σf; 0,2σf; −0,5σf)**: el libro dice que Tresca "predice falla, lo cual es correcto". Con Von Mises la suma de cuadrados es 1,86 < 2 (σ\* = 0,964σf; Cs ≈ 1,04): **no falla**. La afirmación depende del criterio tomado como referencia; no usarla como test de "debe fallar". El caso (1,1; 0,9; 0,2) y los hidrostáticos sí son consistentes.
4. **Fig. 12-14 y Anexo 3**: (61) usa "≥/≤" de forma que la interpretación depende del orden σ1>σ2>σ3; si se codifica la verificación de la zona de Mohr, ordenar primero.
5. **Sec. 10, definición de "Cs lineal"** (2,71 y 2,75): el texto no la define. Por los números (σfalla/Cs_lin = 2,24/2,71 = 0,83 y 3,00/2,75 = 1,09) se deduce que es la extrapolación de la **pendiente inicial** de σ\*(carga); es mi interpretación, confirmarla.
6. **Qué cargas se multiplican en Cs (sec. 8)**: "las cargas" sin distinguir permanentes de variables; en un caso real (peso propio fijo + carga variable) escalar todo vs. solo la variable da Cs distintos. Preguntar al usuario.
7. **(71)**: `Cs = menor{Φ1, Φ3}`; como Φ3 ≤ Φ1 siempre que |σ(3)| > σ(1), equivale a usar Φ3. Anexo 5 usa σ\* = mayor{σ(1);Φ}. Consistente, solo redundante.
8. **σ(3) > 0 (ambas principales positivas en 3D)**: (70)-(72) no lo contemplan explícitamente (en plano σ(3)=0). Convención asumida: se trata σ(3) como 0 (Rankine usa σ(1)).
9. **Nombre "Mohr-Coulomb" en Struttura**: el libro nombra Mohr (dúctil) y Mohr modificado (frágil). La docstring de `tensor.py` ("Mohr-Coulomb (frágil)") no coincide con la clasificación del libro (Mohr es para dúctiles con |σc|>σt). Conviene renombrar o aclarar en el informe.
10. **Referencia**: Anexo 2 cita (128) para (47); debería ser (129)/(100). Anexo 3 se refiere a la "(14) del Cap. 1" y "(11)": correctas.
11. **Alcance**: el libro pone la definición de "dúctil" como alargamiento > 5 % sobre 2" y evalúa los criterios con ensayos biaxiales (Fig. 2): no hay indicación para fatiga, soldaduras ni anisotropía.

Preguntas para el usuario:
- ¿Querés que Mohr modificado se agregue como teoría nueva y se corrija el σeq de Mohr (hoy reporta el de Rankine)?
- ¿σf = fluencia o rotura según el caso (dos Cs en el informe)? ¿Qué factor/criterio de aceptación manejás para el fuselaje (se fija con la norma que apliques)?
- Para uniones soldadas: ¿tenés propiedades de la zona afectada o usás las del material base?
- ¿Te interesa el gráfico del lugar de falla (cuadrado/hexágono/elipse) con el punto P y el factor Cs=OP'/OP en el informe?
