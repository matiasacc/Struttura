# Cap. 4 - Teoría de placas (Compendio Cálculo Estructural II, UNC 2024)

PDF págs. 61-78 (libro 4-1 a 4-18). Página del libro N = PDF 60+N.
Ejes: x1, x2 en el plano medio, x3 perpendicular **hacia abajo**; h = espesor; c = lado menor (ojo: en placas circulares **c es el DIÁMETRO**, verificado con las tablas); α = c/ℓ ≤ 1.
Estado: **[V]** verificado numéricamente / contra teoría clásica; **[L]** leído de imagen; **[!]** inconsistencia (sección 7).

## 1. Qué resuelve y para qué sirve
Reduce el sólido 3D de poca altura a una placa de Kirchhoff (fibras normales rectas e inextensibles, σ33=0, pequeños desplazamientos): desacopla el estado membranal (plano) del flexional, define esfuerzos resultantes por unidad de longitud (N, M), rigideces C=Eh/(1−ν²) y D=Eh³/(12(1−ν²)) y llega a la ecuación de Navier ∇⁴u3 = p3/D. Como la solución analítica con condiciones de borde reales es casi imposible, el capítulo da **fórmulas aproximadas tabuladas** para placas circulares/elípticas/rectangulares con carga uniforme (teoría lineal y no lineal con efecto membrana), carga central, placas anulares, y carga de colapso. Sirve para dimensionar el espesor de paneles planos bajo presión transversal (tapas, chapas, tableros), verificando tensión y flecha.

## 2. Fórmulas y algoritmos clave

### 2.1 Cinemática y esfuerzos (§2-3, PDF 61-65)
- Kirchhoff (8), PDF 62 [L]: u1* = u1 − x3 ∂u3/∂x1; u2* = u2 − x3 ∂u3/∂x2; u3* = u3. Giros βi = −∂u3/∂xi (6), antihorario +.
- Curvaturas (11) [L]: χ11=−∂²u3/∂x1²; χ22=−∂²u3/∂x2²; χ12=−∂²u3/∂x1∂x2. Deformaciones (12): εij* = εij + x3 χij.
- Resultantes (14)-(16): Nij=∫σij dx3; Mij=∫x3 σij dx3 (espesor −h/2..h/2). Hay 8 resultantes: N11, N22, N12 (membrana); M11, M22, M12 y cortes N13, N23. Momento flector + si tracciona fibras inferiores (x3>0); torsor (17): M21 = −M12.
- Equilibrio membranal (18)-(19): ∂N11/∂x1+∂N12/∂x2+p1=0; ∂N22/∂x2+∂N12/∂x1+p2=0.
- Equilibrio flexional (20)-(22): ∂M11/∂x1+∂M21/∂x2−N13=0; ∂M21/∂x1+∂M22/∂x2−N23=0; ∂N13/∂x1+∂N23/∂x2+p3=0.

### 2.2 Constitutivas integradas (§4, PDF 65-66)
- (23): σ11=E/(1−ν²)(ε11*+νε22*), σ22 análoga, σ12=E/(1+ν)ε12*.
- Membrana (26)-(27) [L]: N11=C(ε11+νε22); N22=C(ε22+νε11); N12=C(1−ν)ε12; C=Eh/(1−ν²) (análogo a EA).
- Flexión (31)-(32) [!]: M11=D(χ11+νχ22); M22=D(χ22+νχ11); D=Eh³/(12(1−ν²)) (análogo a EI). El libro imprime M21 = −D(1−ν)χ12: **signo inconsistente** con (17) y con (40); correcto: M21 = +D(1−ν)χ12 (⇒ M12 = −D(1−ν)χ12).

### 2.3 Formulación diferencial (§5, PDF 67-69)
- Membrana (34)-(35): ∂²u1/∂x1² + ν∂²u2/∂x1∂x2 + (1−ν)/2(∂²u2/∂x1∂x2+∂²u1/∂x2²) + p1/C = 0 (y análoga). El texto cita "(31)" donde corresponde (34)-(35).
- Flexión (39)-(41): ∂²M11/∂x1²+2∂²M21/∂x1∂x2+∂²M22/∂x2²+p3=0 → **∂⁴u3/∂x1⁴ + 2∂⁴u3/∂x1²∂x2² + ∂⁴u3/∂x2⁴ = p3/D** (Navier 1820), análoga a viga y''''=q/EI.
- Bordes (42)-(50): empotrado u3=0, ∂u3/∂n=0; apoyado u3=0 y (46) ∂²u3/∂x1²+∂²u3/∂x2²=0 (independiente del material); libre: M22=M21=N23=0 → se combinan con el **corte efectivo** (48)-(49) → (50): ∂³u3/∂x2³+(2−ν)∂³u3/∂x1²∂x2=0 y ∂²u3/∂x2²+ν∂²u3/∂x1²=0.
  (49) [!]: el libro imprime (N23)ef = +D[(2−ν)∂³u3/∂x1²∂x2+∂³u3/∂x2³]; con (31) corregido sale −D[...] (no afecta (50)).
- El libro **no resuelve** analíticamente: remite a Roark (ejemplo citado "Roark's Formulas for Stress and Strain") y al MEF (Cap. 12).

### 2.4 Pequeños desplazamientos, carga q uniforme (§6.1.1, PDF 70-71, 78)
Válido si wmáx < 0.5 h (membrana despreciable):
- (51) wmáx/h = δ (q/E)(c/h)⁴;  (52) σ = β q (c/h)²;  δ=(1−ν²)/δ0; βc (centro), βe (centro del borde empotrado).
- Diseño dúctil: βp=½(βc+βe) (53), admite plastificación localizada; frágil o fatiga: usar βe.
- **Tabla 1 (PDF 71)** da δ0, 1/βc, 1/βe (transcripta abajo) [V contra teoría clásica en los casos circulares, rect. apoyada α=0.5 y límites α→0].
- Espesor de diseño (63)-(64) [V]: h1 = (δ q c⁴/(wadm E))^(1/3); h2 = c √(β q/σadm); h = máx(h1,h2).

### 2.5 Grandes desplazamientos, efecto membrana (§6.1.2, PDF 72-74)
Variables adimensionales (54): w̄=w/h; q̄=(q/E)(c/h)⁴; σ̄=(σ/E)(c/h)².
- (55) q̄ = K1 w̄ + K2 w̄³;  (56) σ̄ = K3 w̄ + K4 w̄².  (57)-(59): K1=1/δ, K3=β/δ.
- Uso válido solo para w̄ > w̄0 = K1K4/(K2K3) (60).
- Dato q: Cardano (61) [V]: T=q̄/(2K2); S=√([K1/(3K2)]³+T²); w̄=(S+T)^(1/3)−(S−T)^(1/3); luego σ̄ por (56). Calcular S y T con muchas cifras.
- Dato σ (p. ej. σadm), (62) [V]: w̄=(√(K3²+4K4σ̄)−K3)/(2K4), luego q̄ por (55).
- Diseño no lineal de h: tanteo h→q̄→w̄→σ̄ y control σ≤σadm, w≤wadm (65); coeficientes de seguridad (Cs)σ<(Cs)q (Fig. 12).
- Carga límite de "carga pequeña" (66) [V]: qL = δ σadm²/(w̄0 β² E) = K2/(K3K4)·σadm²/E (independiente de c).
- Metodología recomendada por el libro: empezar siempre con la teoría lineal; si w̄>w̄0 ya es conservador; usar no lineal solo si hace falta, partiendo del espesor mínimo fabricable.

### 2.6 Carga concentrada central, placa circular (§6.2, Tabla 4, PDF 77)
P=π r0² q; 0.33h<r0<0.5r (r = radio de la placa); si r0<h/3 usar r0=h/3. [V por superposición con momento de borde y contra Roark/Timoshenko para apoyada]
- Apoyada: σmáx(centro)=3P/(2πh²)[1+(1+ν)ln(r/r0)−(1−ν)r0²/(4r²)]; wmáx=3(1−ν)(3+ν)P r²/(4πEh³).
- Empotrada: σmáx(centro)=3(1+ν)P/(2πh²)[ln(r/r0)+r0²/(4r²)]; wmáx=3(1−ν²)P r²/(4πEh³).
- No da la tensión en el borde empotrado (≈ 3P/(2πh²)(1−r0²/(2r²)), derivación mía).

### 2.7 Placas anulares (§6.3, Tabla 5, PDF 77)
σmáx=K1 q a²/h², wmáx=K2 q a⁴/(E h³) (casos de carga distribuida) o σmáx=K1 P/h², wmáx=K2 P a²/(E h³) (carga lineal P); K1, K2 polinomios en x=r0/a, válidos 0.1<x<0.9.

### 2.8 Colapso plástico (§6.4, PDF 78)
qc = γ σf (h/c)² (67); γ=6 circular apoyada; 11.26 circular empotrada; 1.42+4.06 α^1.3 rectangular apoyada. qc≈80 % sobre la carga de primera fluencia de (52). Carga concentrada máxima en cualquier placa (68): Pc = ½ π h² σf [V: = 2π Mp con Mp=σf h²/4].

## 3. Datos tabulados (para cargar como datos)
Todas son expresiones cerradas en α=c/ℓ (y ν), no puntos. Transcripción de las imágenes:

**Tabla 1 (PDF 71, ν general vía δ0; filas elípticas/rectangulares dadas sin ν → ver [!] 7.3)**: δ0 | 1/βc | 1/βe
1. Circular apoyada: 85.333(1+ν)/(5+ν) | 10.667/(3+ν) | —
2. Circular empotrada: 85.333 | 10.667/(1+ν) | 5.333
3. Elipse apoyada: 6.37+5.91α+8.63α⁴ | 1.33+1.9α^2.2 | —
4. Elipse empotrada: 32+53.33α³ | 4+4.2α³ | 2+3.33α³
5. Rect. apoyada: 6.4+14.3α³ | 1.33+2.2α^2.8 | —
6. Rect. empotrada: 32(1+α⁴) | 4(1+α⁴) | 2(1+α⁴)
7. Rect. cortos apoyados / largos empotrados: 32+9.8α⁴ | 4+α⁵ | 2+0.4α⁵
8. Rect. cortos empotrados / largos apoyados: 6.4+37.4α^3.5 | α<0.8: 1.3+5.6α^3.2; α≥0.8: 3+2α³ | 1.33+1.1α^3.6

**Tabla 6 (PDF 78)**: es la Tabla 1 particularizada a ν=0.3 con 1/δ=δ0/0.91 (1/δ, 1/βc, 1/βe): casos 1: 23 | 3.232 | —; 2: 93.77 | 8.205 | 5.333; 3: 7+6.5α+9.5α⁴ | 1.332+1.9α^2.2 | —; 4: 35.2+58.6α³ | 4+4.2α³ | 2+3.33α³; 5: 7+15.7α³ | 1.33+2.2α^2.8 | —; 6: 35.2(1+α⁴) | 4(1+α⁴) | 2(1+α⁴); 7: 35.2+10.8α⁴ | 4+α⁵ | 2+0.4α⁵; 8: 7+41α^3.5 | (α<0.8) 1.3+5.61α^3.2, (α≥0.8) 3+2α³ | 1.33+1.1α^3.6. Sirve de test cruzado de la Tabla 1 (verificado: coinciden).

**Tabla 2 (PDF 75, grandes flechas, 7 casos, K1..K4; ** = en centro del lado empotrado)**:
- 1 circ. libre/libre: K1=85.333/((5+ν)(1−ν)); K2=6; K3=8(3+ν)/((5+ν)(1−ν)); K4=1.18
- 2 circ. empotrado/axial libre: 85.333/(1−ν²); 13.7; 8/(1−ν) y 16/(1−ν²)**; 1.6 y 2**
- 3 circ. empotrado/restringido: 85.333/(1−ν²); 41.6/(1−ν²); 8/(1−ν) y 16/(1−ν²)**; 1.8 y 3.9**
- 4 elipse libre/restr.: (6.4+5.9α+8.6α⁴)/(1−ν²); 20+10α⁴; 5.27+1.84α²; 2
- 5 elipse empotrada/restr.: (32+53.33α³)/(1−ν²); 22+23.7α⁴; 8.8+2.6α³ y 17.58**; 1.8 y 3.4+0.5α**
- 6 rect. libre/restr.: (6.4+14.3α³)/(1−ν²); 20+16.6α⁴; 5.27+1.23α^2.3; 2+0.9α²
- 7 rect. empotrada/restr.: 32(1+α⁴)/(1−ν²); 22+17.6α⁴; 8.8+1.2α³ y 17.58**; 1.8 y 3.4+7.9α**

**Tabla 3 (PDF 76, ν=0.3, 12 casos; apoyo = giro / axial)**: K1 | K2 | K3 | K4
1 circ. libre/libre: 23 | 6 | 7.11 | 1.18
2 circ. libre/restr.: 23 | 30 | 7.11 | 2
3 circ. empot./libre: 93.77 | 13.7 | 11.43 y 17.6** | 1.6 y 2**
4 circ. empot./restr.: 93.77 | 45.7 | 11.43 y 17.6** | 1.8 y 3.9**
5 elipse libre/libre: 7+6.5α+9.5α⁴ | 4+2α⁴ | 5.27+1.84α² | 1.18
6 elipse libre/restr.: 7+6.5α+9.5α⁴ | 20+10α⁴ | 5.27+1.84α² | 2
7 elipse empot./libre: 35.2+58.6α³ | 6.6+7.1α⁴ | 8.8+2.6α³ y 17.58** | 1+0.6α² y 2**
8 elipse empot./restr.: 35.2+58.6α³ | 22+23.7α⁴ | 8.8+2.6α³ y 17.58** | 1.8 y 3.4+0.5α**
9 rect. libre/libre: 7+15.7α³ | 4+3.3α⁴ | 5.27+1.23α^2.3 | 1.18
10 rect. libre/restr.: 7+15.7α³ | 20+16.6α⁴ | 5.27+1.23α^2.3 | 2+0.9α²
11 rect. empot./libre: 35.2(1+α⁴) | 6.6+5.3α⁴ | 8.8+1.2α³ y 17.58** | 1 y 2**
12 rect. empot./restr.: 35.2(1+α⁴) | 22+17.6α⁴ | 8.8+1.2α³ y 17.58** | 1.8 y 3.4+7.9α**
(Coherencia verificada: K1=1/δ, K3=β/δ de (59) reproduce los K3 circulares y rectangulares.)

**Tabla 4**: 2 casos × 2 fórmulas (2.6). **Tabla 5 (PDF 77, x=r0/a, 0.1<x<0.9; 92 coeficientes)**: K1 | K2
1: 3.3−4.37x−4.54x²+18.36x³−12.75x⁴ | 0.52+1.4x−2.46x²+0.54x³
2: 10−34x+56.4x²−48.5x³+16.1x⁴ | 1+3.26x−9.57x²+5.31x³
3: 8−29.76x+48.44x²−40.46x³+13.78x⁴ | 1−2.2x−1.15x²+5.26x³−2.91x⁴
4: 2.06−1.97x−2.56x²+2.48x³ | 0.92−2.56x+2.25x²−0.61x³
5: 6−21.6x+31.6x²−22.4x³+6.4x⁴ | 0.54−1.98x+2.43x²−x³
6: 2.5−9.88x+18.44x²−17.17x³+6.11x⁴ | 0.236−0.764x+0.83x²−0.3x³
7: 2.6−1.8x−1.25x²+0.45x³ | 0.43+3.23x−7.39x²+3.73x³
8: 2.86−6.86x+6.87x²−3.53x³+0.657x⁴ | 0.63−1.57x+0.74x²+0.75x³−0.55x⁴
9: 4−21.3x+48.26x²−48.67x³+17.71x⁴ | 0.274+0.156x−2.35x²+3.12x³−1.2x⁴
10: 0.76+0.09x−0.89x²−1.73x³+1.77x⁴ | 0.19+0.246x−2.1x²+2.7x³−1.036x⁴
(Signos tomados de la imagen; el texto extraído pierde algunos "+"/"−". Casos de carga P (según figura): 1, 6, 8, 9; carga q: 2, 3, 4, 5, 7, 10. Caso 5 dibuja q y reacción P: confirmar con la fuente (Roark, tabla de placas anulares) antes de codificar.)

Figuras 9-12 (PDF 72, 74): curvas cualitativas, nada que cargar (se reproducen con (55)-(56)).

## 4. Ejemplos resueltos del texto
**No trae ejemplos numéricos resueltos** (la metodología remite a un "problema 5, pág. 94", que no es de este PDF: es de la guía de problemas). Casos de verificación **calculados por mí** (E=210000 MPa, ν=0.3):
1. Circular apoyada, c=500 (diámetro), h=5, q=0.02 MPa: δ=0.043477, wmáx=2.0703 mm (w/h=0.414<0.5), β=0.309365, σ=61.873 MPa (coincide con la teoría clásica (5+ν)/(1+ν)·q a⁴/(64D)).
2. Mismo caso, q=0.06 MPa (no lineal, Tabla 3 caso 1: K=23, 6, 7.11, 1.18): q̄=28.5714, T=2.380952, S=2.784813, w̄=0.989499, wmáx=4.9475 mm, σ=172.00 MPa; w̄0=0.6362; lineal daría 6.211 mm y 185.6 MPa (conservador). qL(σadm=250)=0.2128 MPa.
3. Circular empotrada, c=500, h=5, q=0.4 MPa (Tabla 3 caso 3): q̄=190.476, w̄=1.51912, wmáx=7.5956 mm, σ centro=442.17, σ borde=658.39 MPa; w̄0 centro=0.958, borde=0.778.
4. Diseño lineal circular apoyada c=500, q=0.02, σadm=150, wadm=2.5 mm: h1=4.695, h2=3.211 → h=4.695 mm.
5. Rectangular apoyada (caso 5), c=300, ℓ=600 (α=0.5), h=3, q=0.01: δ0=8.1875, wmáx=1.588 mm, σ=60.76 MPa. Contraste con serie de Navier: 1.580 mm y 61.01 MPa (error ≈0.5 %).
6. Tabla 4 (r=100, r0=10, h=5, P=1000): apoyada σ=76.23 MPa, w=0.2101 mm; empotrada σ=57.23 MPa, w=0.08276 mm.
7. Colapso: circular apoyada σf=400, h/c=0.01: qc=0.24 MPa (≈1.86× la fluencia por (52): 0.129 MPa); Pc=½πh²σf=15708 N con h=5.

## 5. Propuesta de implementación en Struttura
- **Tipo B** (calculadora de tablas): `struttura/placas/` con `tablas.py` (todas las expresiones de la sección 3 como funciones de α y ν), `lineal.py` ((51)-(53),(63)-(64)), `nolineal.py` ((55)-(62),(65)-(66)), `anular.py`, `colapso.py`, `entrada.py` (CSV por bloques), `informe.py` (HTML paso a paso con curvas q-w y q-σ lineal vs no lineal).
- Entradas CSV: MATERIAL (E, ν, σf, σadm), GEOMETRIA (forma: circular/elipse/rectangular/anular; c, ℓ, h o "dimensionar"; α se calcula), APOYOS (caso de la tabla; giro libre/empotrado y axial libre/restringido), CARGA (q, P), LIMITES (σadm, wadm).
- Salidas: wmáx, σc, σe, σp; régimen lineal o no lineal (con aviso si 0.5<w̄<w̄0); h necesario; CS a colapso; tablas intermedias (65).
- Dificultad **2/5** (todo tabulado; la parte delicada es no equivocar la tabla/caso). Tiempo: **1 unidad mediana** + **1 chica** (tests contra las tablas 1↔6 y 2↔3).
- Tipo **A (opcional, grande)**: elemento finito de placa (Kirchhoff DKT/DKQ o Mindlin) como extensión de un programa matricial; el propio libro lo deriva al Cap. 12. Dificultad 4-5, tiempo grande. Alternativa liviana (propuesta mía, no del libro, hay que validarla contra Tabla 1): modelar la placa como emparrillado plano con el programa existente (EI por franja = D·paso, GJ=(1−ν)D·paso) y comparar con las fórmulas tabuladas.
- Dependencias: Cap. 1 y 2; Cap. 6 y 8 (pandeo de placas, no está acá); Cap. 12 (MEF placas).
- Fuselaje tubular soldado de avión liviano: aplica a **paneles planos entre tubos** (revestimiento de chapa/tela rígida/compuesto, piso, cortafuego, cartelas planas) como placa rectangular con lados apoyados o empotrados bajo presión aerodinámica uniforme. Con chapa fina w>0.5h es habitual: sirve el cálculo no lineal. No cubre pandeo por compresión/corte del panel (Cap. 6/8).
- Estructuras mecánicas generales: tapas planas de recipientes, platos, placas base, bridas ciegas (circular con carga uniforme/central), placas con orificio central (anulares).

## 6. Anexo teórico sugerido para los informes
- Hipótesis de Kirchhoff (8), curvaturas (11), resultantes (14)-(15), rigidez flexional (32) y ecuación de placa (40) del Cap. 4.
- Fórmulas (51)-(53) con la tabla utilizada y su caso; (55)-(56) y (60)-(62) cuando se use el modelo no lineal; (64) y (66) para dimensionar.
- Aclarar el rango de validez: w<0.5h (lineal), w̄>w̄0 (no lineal), 0.1<x<0.9 (anulares), ν=0.3 para Tablas 3 y 6.
- Citar "Compendio de Cálculo Estructural II, Cap. 4, ec. (N) / Tabla N".

## 7. Riesgos, ambigüedades, preguntas al usuario
1. **Signo en (31) tercera ecuación** (PDF 66): M21=−D(1−ν)χ12 contradice (17) y (40). Con las definiciones del propio libro sale M21=+D(1−ν)χ12. Y (49) sale con signo menos (el (50) no cambia). Si se programa un elemento de placa, usar la versión corregida.
2. **c es el diámetro** en las placas circulares de Tabla 1/2/3/6 y la tabla 4 usa r = radio de la placa; Tabla 5 usa a = radio. Documentarlo en el CSV (no confundir radio con diámetro).
3. **ν en filas elípticas/rectangulares**: Tabla 1 usa δ=(1−ν²)/δ0 con ν general, pero 1/βc y 1/βe de esas filas no dependen de ν y K2-K4 de Tablas 2/3 coinciden con los de ν=0.3. Son aproximaciones de ν=0.3; Roark/Timoshenko. Preguntar si se admiten ν distintos (aluminio 0.33, acero 0.3).
4. **Hueco 0.5h < w < w̄0·h**: lineal "válido hasta 0.5h" y no lineal "desde w̄0" (p. ej. w̄0=0.636 circular apoyada, 0.96 centro empotrada), sin método entre ambos. Criterio propuesto: usar lineal (conservador, el libro lo indica).
5. Origen de w̄0 =K1K4/(K2K3) (60) no explicado; (66) es consecuencia directa y se verificó.
6. Tabla 2/Tabla 3: la leyenda "libre/restringido" se refiere a giro y desplazamiento axial en el borde; elegir mal la condición axial cambia K2 hasta 5 veces (circular: 6 vs 30). Debe pedirse explícitamente.
7. Colapso (67): γ rectangular apoyada con α→0 da 1.42, mientras que una franja apoyada de Tresca da 2 (8Mp/c²); γ=11.26 es de Mises (Tresca daría 12). El libro no aclara el criterio de fluencia; verificar antes de usar para decisiones.
8. Tabla 4: límite r0<0.5 r; para r0 chico el libro usa r0=h/3 (regla propia, no la de Roark). Fórmulas de σ son en el centro de la carga; el borde empotrado puede gobernar con r0 grande.
9. Tabla 5: "ν" y tipo de carga (P o q) por caso no están escritos, solo dibujados; polinomios de ajuste válidos 0.1<x<0.9.
10. Texto extraído: pierde signos y símbolos (δ, β, χ); transcribí de las imágenes. Mezcla de "δ" para flecha y para interferencia (Cap. 3).
