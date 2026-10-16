# Cap. 1 - Ecuaciones fundamentales de la elasticidad (PDF págs 7-26; libro 1-1 a 1-20)

Convenciones de cita: "p.NN" = página del PDF; "(NN)" = número de ecuación del libro; "libro 1-N" = numeración impresa. Tracción positiva, compresión negativa. Tensiones principales ordenadas σ(1) > σ(2) > σ(3) (ec. 39). Todas las fórmulas de abajo fueron verificadas mirando la página como imagen (el texto extraído pierde los símbolos griegos).

---

## 1. Qué resuelve y para qué sirve

Es el marco teórico de todo el curso: define vector tensión, tensor de tensiones y de deformaciones (cartesianos, simétricos), cómo cambian con el sistema de ejes, los problemas de autovalores (tensiones principales, τmáx), la ley de Hooke 3D (con temperatura), el planteo general de la elasticidad lineal (15 incógnitas; método de la rigidez = ecuaciones de Lamé vs. método de las fuerzas) y los teoremas energéticos (trabajos virtuales, mínima energía potencial total).

Para diseño sirve para: (a) pasar de las tensiones de la teoría de vigas a un estado tensional completo en un punto (tensiones principales, planos y ejes, Mohr), que es el insumo del Cap. 2 (criterios de falla); (b) pasar entre deformaciones medidas (galgas) y tensiones; (c) justificar de dónde sale el método matricial de rigidez (TV ⇒ equilibrio; π mínima).

---

## 2. Fórmulas y algoritmos clave

### 2.1 Tensión en un punto (sec. 2, p.8-10)
- Vector tensión sobre el plano de normal ν: σ_ν = lim ΔF/ΔA (2). Se descompone en normal y cortante (3).
- Componentes cartesianas σij (1er índice: plano; 2º: dirección) (4)-(5).
- **Fórmula de Cauchy** (10), p.9: `σ_ν = σij · νi · tj`, o sea σ_ν = σᵀ·ν (vector columna con σ simétrico: σ_ν = σ·ν).
- Tensión normal (14) p.10: `σνν = σij νi νj = νᵀ σ ν`.
- Tensión cortante (15): `σνs = sqrt(|σ_ν|² − σνν²)`.
- Reciprocidad (18) p.10: σij = σji (equilibrio de momentos sobre el cubo).

### 2.2 Cambio de ejes (sec. 2.5, p.10-11)
- Convención del libro: `t_m = λ_mn t'_n` (20), es decir matricialmente `[t] = [λ][t']` (19). **λij es la proyección de ti sobre t'j** (columnas de λ = ejes nuevos expresados en los viejos; filas = ejes viejos expresados en los nuevos, ver (49)).
- Vector: `σ'_n = λ_mn σ_m` (24); inversa `σ_m = λ_mn σ'_n` (25).
- Tensor (30), p.11: `σ'_{lm} = λ_il λ_jm σ_ij`, o sea **σ' = λᵀ σ λ**. (Si en el código la matriz de rotación R tiene por filas los ejes nuevos en base vieja, entonces λ = Rᵀ y σ' = R σ Rᵀ.)
- Rotación antihoraria θ alrededor de z (49)-(51), p.14:
  ```
  σx' =  cos²θ σx + sin²θ σy + 2 sinθ cosθ τxy
  σy' =  sin²θ σx + cos²θ σy − 2 sinθ cosθ τxy
  τxy' = −sinθ cosθ σx + sinθ cosθ σy + (cos²θ − sin²θ) τxy
  ```
  y en ángulo doble (51): `A=(σx+σy)/2, B=(σx−σy)/2; σx'=A+B cos2θ+τxy sin2θ; σy'=A−B cos2θ−τxy sin2θ; τxy'=−B sin2θ+τxy cos2θ`.

### 2.3 Direcciones y tensiones principales (sec. 2.6, p.12-14)
- Condición de dirección principal (31)-(34): `(σij − σ δij) νi = 0` (autovalores/autovectores del tensor simétrico).
- Ecuación característica (35): **σ³ − I1 σ² + I2 σ − I3 = 0**.
- Invariantes (36)-(38): `I1 = σii = σ11+σ22+σ33`; `I2 = ½(σii σjj − σij σji) = σ11σ22+σ22σ33+σ33σ11 − (τ12²+τ23²+τ13²)`; `I3 = det(σij)`.
- Las 3 raíces son reales; si son distintas, los autovectores son ortogonales (p.12). En ejes principales el tensor es diagonal (40).
- Extremos (41)-(45): `σνν = σ(1)ν1²+σ(2)ν2²+σ(3)ν3²`; σνν,máx = σ(1) (43); σνν,mín = σ(3) (44); **τmáx = ½(σ(1) − σ(3))** (45) (demostración en Cap. 2, Anexo 3, ec. 62).
- **Tensión plana con una principal nula** (46)-(48), p.13: con `A = (σα+σβ)/2`, `R = sqrt(((σα−σβ)/2)² + τ²)`:
  `σ(1) = mayor[A+R, 0]`, `σ(3) = menor[A−R, 0]`, `τmáx = ½(σ(1)−σ(3))`.
  Importante: hay que considerar **tres** círculos de Mohr (Fig. 9, p.13), no olvidarse de la σ nula; τmáx NO es R salvo cuando |A| ≤ R.
- Círculo de Mohr (52), p.14: `R = sqrt(B² + τxy²)`, `σx' = A + R cosβ`, `τxy' = R sinβ`, `σmáx = A+R`, `σmín = A−R`, `τmáx(plano) = R`. Convención gráfica del libro: **τxy positivo hacia abajo** (Fig. 11).
- Caso general 3D (2.6.3, p.14): calcular I1, I2, I3 → resolver (35) → máximos con (43)-(45); los autovectores solo si se necesitan, resolviendo (34) para cada σ(k).

### 2.4 Equilibrio (sec. 2.7-2.8, p.15-16)
- Interior (55): `∂σij/∂xi + Fj = 0` (3 ecuaciones, 6 incógnitas: indeterminado). En (118) se escribe ∂σij/∂xj + Fi = 0 (equivale por simetría).
- Contorno (58): `σij νj = fi` (fuerza de superficie).
- Observación (p.16, Fig. 14): f = 0 en el contorno o F = 0 en un punto NO implican tensiones nulas ni constantes.

### 2.5 Deformaciones (sec. 3, p.16-20)
- Alargamiento de una fibra de dirección λ (60): `E_λ = (|dR| − |dr|)/|dr|`.
- **Tensor de Lagrange (no lineal)** (68)=(78), p.17-18: `γij = ½(∂ui/∂xj + ∂uj/∂xi + ∂um/∂xi · ∂um/∂xj)`. Simétrico (79). Se transforma como tensor (77): `γ'_{lm} = λ_il λ_jm γij`.
- Alargamiento (72): `E_λ = sqrt(1 + 2 γij λi λj) − 1`. Sobre un eje: `Ei = sqrt(1+2γii) − 1` (81) ⇒ `γii = Ei + ½Ei²` (82).
- Distorsión angular entre fibras λ, μ inicialmente a 90° (73): `sin φ = 2γij λi μj / (sqrt(1+2γij λiλj) sqrt(1+2γij μiμj))`; sobre ejes (83)-(85): `γij = ½(1+Ei)(1+Ej) sin φij` (i≠j).
- Pequeñas deformaciones (86)-(87): `γij ≈ [E1, φ12/2, φ13/2; ·, E2, φ23/2; ·, ·, E3]` → los εij fuera de la diagonal son **la mitad** de la distorsión angular (φ = γ_ingenieril).
- **Tensor lineal** (90)=(104): `εij = ½(∂ui/∂xj + ∂uj/∂xi)`, válido para pequeñas deformaciones Y pequeños giros. El término cuadrático (88) es un "pequeño giro"; es imprescindible conservarlo en pandeo de placas y cáscaras (Caps. 6-8) (p.19).
- Tabla 3.6 (p.20): [grandes def. y giros: (78), E=√(1+2γii)−1, φ=arcsen(...)] / [pequeñas def., grandes giros: γij, E≈γii, φ≈2γij] / [pequeñas def. y giros: εij, E≈εii, φ≈2εij].
- Cambio de volumen (Cap. 2, Anexo 1, ec. 42): ΔV ≈ (ε1+ε2+ε3)dV = traza(ε) dV (invariante). Descomposición volumétrica + distorsiva (43)-(45): `εm = ⅓(ε1+ε2+ε3)`, `ε = εv + εd`.

### 2.6 Constitutivas (sec. 4, p.20-22 y Anexo p.26)
- 1D: `σ11 = E ε11` (92); corte `σ12 = G (2 ε12)` (93) (el 2 sale de φ=2ε). Poisson (97): `εx = −ν εy` (acero ν ≈ 0,3).
- Constantes de Lamé (98), p.21: `λ = Eν/((1+ν)(1−2ν))`, `μ = G = E/(2(1+ν))`, `E = μ(3λ+2μ)/(λ+μ)`, `ν = λ/(2(λ+μ))`.
- **Hooke isótropo** (99)/(106): `σij = E/(1+ν) [εij + ν/(1−2ν) εkk δij] = 2μ εij + λ εkk δij`. Inversa (100): `εij = (1+ν)/E σij − ν/E σkk δij`.
- Con temperatura: se suma a (99) el término `−E/(1−2ν) α ΔT δij` (102)/(105), p.22; equivalente `λ(1+ν)/ν α ΔT` (124).
- Forma extendida (128)-(129) p.26 (Anexo): `σ11 = E/((1+ν)(1−2ν)) [ε11(1−ν) + ν(ε22+ε33)] − E/(1−2ν) αΔT`, `σ12 = E/(1+ν) ε12 = G(2ε12)`; inversa `ε11 = (1/E)[σ11 − ν(σ22+σ33)] + αΔT`, `ε12 = σ12/(2G)`.
- **Tensión plana (σ33=0)**: (130) `ε33 = −ν/(1−ν)(ε11+ε22) + (1+ν)/(1−ν) αΔT`; (131) `σ11 = E/(1−ν²)[ε11 + ν ε22 − (1+ν)αΔT]` (análogo σ22), `σ12 = E/(1+ν) ε12 = G(2ε12)`; (132) `ε11 = (σ11 − νσ22)/E + αΔT`, `ε22 = (σ22 − νσ11)/E + αΔT`, `ε12 = (1+ν)σ12/E`.
- Anisotropía (p.21): Cijkl 81 → 36 (6×6 con σ,ε simétricos) → 21 si existe W; con simetrías: 13 / 7 / 5 constantes. Relación (95)-(96).

### 2.7 Elasticidad lineal general y Lamé (sec. 5, p.22-23)
- 15 incógnitas (6 σ + 6 ε + 3 u) y 15 ecuaciones (3 equilibrio + 6 cinemáticas + 6 constitutivas) (p.22).
- Método de los desplazamientos (rigidez): sustituyendo (106) y (104) en (103) se llega a las **ecuaciones de Lamé** (111), p.23: `μ ∂²uj/∂xi∂xi + (μ+λ) ∂/∂xj (∂um/∂xm) + Fj = 0` (3 ecuaciones en u). Método de las fuerzas: se resuelven primero las tensiones (no se desarrolla).

### 2.8 Teoremas energéticos (sec. 6, p.23-25)
- Identidad fundamental (112), p.23: `∫V σij ½(∂ui/∂xj+∂uj/∂xi) dV ≡ ∫S νj σij ui dS − ∫V ui ∂σij/∂xj dV` (vale si σij=σji, sin importar si σ y u se relacionan).
- **Ecuación de Trabajos Virtuales** (114): `∫V σij δεij dV = ∫Sf f̄i δui dS + ∫V Fi δui dV` (trabajo virtual interno = externo; no usa constitutivas ⇒ vale para cualquier material, p.24).
- TV ⇒ equilibrio (118) y (119) `νj σij − fi = 0` en S (sec. 6.3, p.24). Teorema de TV: necesario y suficiente para equilibrio. Existe el análogo "complementario" para compatibilidad (nota p.24, sin desarrollar).
- Densidad de energía (120) `σij = dW/dεij`; lineal (121) `W = ½ σij εij`; isótropo (123) `W = μ εij εij + ½ λ εjj εmm`; en desplazamientos (125) `W = μ/4 (∂ui/∂xj + ∂uj/∂xi)² + λ/2 (∂um/∂xm)(∂uℓ/∂xℓ)`, p.25. W es definida positiva.
- **Energía potencial total** (126): `π = ∫V W dV − ∫V Fi ui dV − ∫S fi ui dS`. δπ = 0 ⇒ TV ⇒ equilibrio (127). Mínimo de π ⇒ equilibrio estable; δπ=0 ⇔ Lamé (p.25). Hay un π* complementario (nota p.25).

---

## 3. Datos tabulados / gráficos / curvas a cargar

- **No hay tablas numéricas ni curvas** a digitalizar en este capítulo.
- Valores de referencia sueltos: acero ν ≈ 0,3 (97, p.21). Tabla de simetría (p.21): diagonal(digonal) 13 / tetragonal 7 / octogonal 5 constantes (solo informativa).
- Las constantes de material (E, ν, G, α) las pone el usuario; Struttura ya las lee (`MATERIALES id;E;G;nu;fy;sadm;alfa`).

---

## 4. Ejemplos resueltos del texto

- Único ejemplo (p.7): barra traccionada, **simbólico**: u = εL, F = σA, σ = Eε ⇒ F = (EA/L)u (1). No hay resultados numéricos.
- El capítulo no trae ejemplos numéricos. Para tests propongo vectores **calculados por mí con numpy (NO son del libro)**; los resultados se dan con 6 cifras:

| Test (derivado) | Entrada | Resultado |
|---|---|---|
| Tensor 3D lleno, MPa | σ=[[50,30,20],[30,−20,10],[20,10,40]] | I1=70; I2=−1200; I3=−61000; σ(1)=75,168233; σ(2)=26,019916; σ(3)=−31,188149; τmáx=53,178191 |
| Rotación plana 30° (50) | σx=76, σy=4, τxy=48 | σx'=99,569219; σy'=−19,569219; τxy'=−7,176915 (σx'+σy' = 80 invariante) |
| Hooke 3D (99) | E=210000, ν=0,3; ε11=1e-3, ε22=−3e-4, ε33=2e-4, ε12=2,5e-4 | G=80769,23; λ=121153,85; σ11=270,576923; σ22=60,576923; σ33=141,346154; σ12=40,384615 |
| Tensión plana (130)-(131) | mismo E, ν; ε11=1e-3, ε22=−3e-4 | ε33=−3,0e-4; σ11=210,0000 |
| Térmico restringido (102) | E=210000, α=12e-6, ΔT=50 | σ=−126 (uniaxial, EαΔT); −180 (biaxial, EαΔT/(1−ν)); −315 (triaxial, EαΔT/(1−2ν)) MPa |

(Los tres últimos térmicos son consistentes con (128), (131), pero el texto no los calcula; ver Riesgos.)

---

## 5. Propuesta de implementación en Struttura

### 5.1 Qué ya está (portico3d/tensor.py) vs. qué agrega el capítulo

| Tema | Ya en Struttura | Agrega el Cap. 1 |
|---|---|---|
| Tensor en un punto | Sí, pero solo la forma de viga: [[σx,τxy,τxz],[τxy,0,0],[τxz,0,0]]; se muestra la matriz y el ángulo de σ(1) | Tensor **lleno** (6 componentes), p.ej. con σy, σz, τyz ≠ 0 |
| Tensiones principales | Sí, analítico 2×2 (A±R, 0), equivale a (47)-(48) con σβ=0 y τ=√(τxy²+τxz²) (rotar los ejes alrededor de x lo reduce a plano) | Cúbica (35) / autovalores 3×3; invariantes I1-I3; autovectores (direcciones principales) |
| τmáx, Mohr | τmáx = ½(σ1−σ3) y círculo/tensor en puntos del informe | Tres círculos en caso 3D; rotación arbitraria (30); Mohr plano con regla "τ hacia abajo" |
| Transformación de tensores | Solo la de esfuerzos de barra a globales (matricial) | Transformación general del tensor de tensiones y de deformaciones (30), (77) para ejes cualesquiera |
| Deformaciones | No hay tensor de deformaciones | εij, γij, E_λ, φ, descomposición volumétrica/distorsiva, ε↔σ por Hooke 3D y tensión plana, con ΔT |
| Hooke / constantes | E, G, ν (G = E/2(1+ν)); alfa leído; cargas térmicas solo en `portico` (plano) | Hooke 3D completo (99)-(100), Lamé (98), térmico (102) |
| Energía | No | W (121)-(125), π (126), TV (114), π mínimo |
| Teoría de elasticidad (Lamé 111) | No | Ecuaciones de Lamé; sin implementación práctica en un programa de barras |

### 5.2 Propuesta

**Tipo B (calculadora) - "Estado tensional 3D" (prioridad media/alta)**: programa nuevo `tensor3d` (o `estado`), compartido con Cap. 2 (los criterios de falla). Módulo base `estado.py` con funciones puras reutilizables por `portico3d/tensor.py`.

- **Entrada CSV por bloques** (siguiendo el estilo de Struttura):
  - `MATERIALES id;E;nu;alfa;fy;sut;suc;teoria;sadm` (los mismos campos que ya usa portico3d).
  - `ESTADOS id;sx;sy;sz;txy;tyz;txz` (tensor dado, MPa) y/o `DEFORMACIONES id;e11;e22;e33;e12;e23;e13;dT;material` (ε **tensoriales**; un flag `gamma_ing=si` para pasar φ=2ε) con opción `plana=si` (σ33=0, usa (130)-(132)).
  - `ROTACIONES id;estado;eje;angulo` o los 9 cosenos directores λ (elegir convención explícita, ver Riesgos).
- **Salidas (informe HTML paso a paso)**: matriz σ, I1, I2, I3, ecuación característica, σ(1,2,3) y direcciones (verificar ortogonalidad y que σ' = λᵀσλ sea diagonal), τmáx y su plano (a 45° entre σ(1) y σ(3)), 3 círculos de Mohr (SVG), tensor rotado, descomposición hidrostática/desviadora (Cap. 2, Anexo 1), Hooke ε↔σ con ΔT, y el bloque de criterios/CS del Cap. 2.
- **Cómo se conecta**: (1) `portico3d/tensor.criterios()` hoy asume σy=σz=τyz=0; extenderla para aceptar un tensor lleno por punto (opcional, sin cambiar la salida para barras). (2) Un caso de uso inmediato en tubos: tubo con presión interna (tensión circunferencial σθ ≠ 0) + torsión + flexión → tensión plana con σy ≠ 0, que hoy no se puede evaluar. (3) Permite pegar tensores de un FEA y compararlos con el solver de pórtico en un punto.
- **Dificultad: 2/5. Tiempo: mediana** (autovalores con numpy, validación vs. tests derivados de arriba, SVG de Mohr 3D, informe).

**Extras opcionales (no están en el capítulo, solo aprovechan Cap. 1)**:
- Roseta de galgas (0-45-90 o 0-60-120) → ε principales → σ por (131)-(132): sale de (77) + (131). **Dificultad 2, chica.** Sirve para ensayo del estudiante; proponelo solo si le interesa.
- Test de Clapeyron para el solver: U = ½ Fᵀu = ½ uᵀKu (se deduce de (114) con δu=u y (121); el libro NO lo escribe explícitamente). **Dificultad 1, chica**, para `005_Tests`.

**Tipo C (anexo teórico)**: sec. 2.5, 2.6, 3.5, 4.3, 5.2, 6 (ver sección 6 abajo). Los teoremas energéticos y Lamé NO justifican un programa propio: es solo anexo (la formulación matricial de las barras ya los usa implícitamente).

**Dependencias**: ninguna previa; el Cap. 2 depende de este (principales, Mohr). Citas internas: Cap. 5 (4.6, pandeo térmico), Caps. 6-8 (necesitan γij no lineal), p.16, p.19, p.22.

**Fuselaje tubular soldado y estructuras mecánicas**: aplica la parte de tensiones (principales, Mohr, tensor rotado) a puntos de tubo ya hechos con teoría de vigas (σx, τ), y la de tensor lleno cuando haya presión interna (circuitos hidráulicos/combustible, recipientes) o un FEA para comparar. Hooke 3D con temperatura y la tensión plana sirven para tensiones térmicas de piezas restringidas (soldadura/dilatación). La elasticidad 3D general (Lamé, TV) no aplica directo; el fuselaje se resuelve con barras.

---

## 6. Anexo teórico para los informes (qué incluir, con referencia "Cap. 1")

1. Tensor de tensiones simétrico y fórmula de Cauchy σ_ν = σ·ν; σνν = νᵀσν (ec. 10, 14, 18).
2. Ecuación característica σ³ − I1σ² + I2σ − I3 = 0 e invariantes (35)-(38); σ(1) ≥ σ(2) ≥ σ(3); τmáx = ½(σ(1)−σ(3)) (45).
3. Caso plano: A, R, σ(1)=mayor[A+R,0], σ(3)=menor[A−R,0] (47)-(48) y la aclaración de los tres círculos de Mohr (Fig. 9).
4. Rotación de ejes (30) y (50)-(51) (indicar la convención de λ).
5. Deformaciones: εij lineal (90), φ=2εij (87); Hooke (99)-(100) con (102); plana (130)-(132); G=E/(2(1+ν)) (98).
6. Equilibrio ∂σij/∂xj + Fi = 0 y σij νj = fi (55), (58) como base de las verificaciones de equilibrio.
7. TV (114) y π (126) como justificación de K u = F (una frase, sin desarrollo).

---

## 7. Riesgos, ambigüedades y preguntas

1. **Convención de λ**: (19)-(20)/(30) usan λij = proyección de ti sobre t'j (filas = ejes viejos en base nueva), por lo que σ' = λᵀσλ. Es la transpuesta de la convención habitual R σ Rᵀ (filas de R = ejes nuevos). Definir una sola en el código y testear con la rotación 30° de arriba. No es un error del libro, pero es fácil invertir el sentido del ángulo.
2. **Voigt del libro (95)-(96)**: usa ε4=ε12, ε5=ε13, ε6=ε23 con deformaciones **tensoriales** (no ingenieriles) y orden (12,13,23), distinto del orden habitual de FEA (23,13,12) y de γ ingenieril. Al comparar con un FEA hay que convertir (φ = 2ε).
3. **Símbolo γ**: el libro usa γij para el tensor de Lagrange (no lineal) y φij para la distorsión angular; muchos textos/FEA usan γ para la distorsión ingenieril (=2ε). Riesgo de factor 2.
4. **Tabla 3.6 (p.20)**, columna "pequeñas deformaciones y grandes giros": solo dice "γij" sin escribir la expresión; se entiende que es (78) con E≈γii y φ≈2γij. Es el caso de pandeo de placas/cáscaras (p.19); confirmar al leer los Caps. 6-8.
5. **Nota al pie de (128) (p.26)**: "para más exactitud reemplazar εkℓ por γkℓ" es informal (mezcla tensores lineal/no lineal); no usarlo en código.
6. **Referencia cruzada incorrecta** en Cap. 2, Anexo 2 (p.38): dice que (47) sale de la (128), pero corresponde a la inversa (129)/(100) (ε = f(σ)). Solo notación.
7. **Tabla de simetría (p.21)**: "diagonal" parece ser "digonal" (n=2); informativa, no se usa.
8. **Signo térmico**: (102) agrega −E/(1−2ν)·αΔT·δij a la tensión **3D**; para tensión plana el factor es (131) E/(1−ν)·αΔT (aparece como −(1+ν) dentro del corchete) y en 1D es EαΔT. No mezclar según el estado (uniaxial / biaxial / triaxial dan −126 / −180 / −315 MPa en el ejemplo).
9. **Mohr con "τ hacia abajo"** (p.14, Fig. 11): al dibujar el círculo el signo de τxy se invierte respecto a la convención de ejes matemática; usar un solo criterio al graficar.
10. Índices en el equilibrio: (55) suma sobre el primer índice, (118) y (103) sobre el segundo; equivalentes por simetría, no es error.

Preguntas para el usuario:
- ¿Querés un programa nuevo de "estado tensional 3D" separado, o preferís solo extender el informe del pórtico 3D con σy/σz/τyz opcionales?
- ¿Las deformaciones de entrada vendrían de galgas/FEA (ε ingenieril φ) o tensoriales?
- ¿Te interesan las tensiones por presión interna en tubos (σθ) como caso de estudio?
