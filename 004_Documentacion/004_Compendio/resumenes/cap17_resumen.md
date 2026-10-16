# Cap. 17 - Estructuras metálicas: Torres (Compendio CE-II, PDF págs. 328-352)

Fuente: Compendio de Cálculo Estructural II, UNC-FCEFyN, ed. 2024. Numeración de páginas del libro "17-n" = PDF 327+n.
Todas las fórmulas de abajo fueron releídas en imagen de la página y las numéricas verificadas con un script propio (ver sección 7).

## 1. Qué resuelve el capítulo y para qué sirve

Es una introducción al análisis y verificación de torres metálicas (antenas arriendadas/autoportantes y torres de transmisión eléctrica), modeladas como **reticulados espaciales** (las normas lo exigen) o pórticos espaciales equivalentes. Da: (a) criterios de modelado y control del modelo (simetría, reacciones por peso propio, hipostaticidad); (b) verificación de barras de perfil ángulo: tracción en sección neta, compresión con coeficiente omega (DIN 4114) y longitudes de pandeo según el armado; (c) verificación de uniones abulonadas/remachadas (corte y aplastamiento); (d) en los Anexos, el **comportamiento no lineal de cables** (riendas) con una ecuación cúbica P-delta, su rigidez tangente y un lazo iterativo mástil+riendas, y el cálculo de **flecha de montaje de conductores** en función de la temperatura.
En diseño sirve para: dimensionar/verificar barras de reticulados 3D con criterio normativo, y para modelar cables pretensados (tensores, riendas) dentro de un modelo lineal por iteración.
No trae ejemplo numérico de una torre completa. El único ejemplo resuelto es de flecha de conductor (Anexo 2). Las normas citadas (VDE 0210 / DIN EN 50341, ASCE 10, AEA 95301, TIA/EIA-222, CIRSOC 102/103) no se desarrollan: el libro solo las nombra.

## 2. Fórmulas y algoritmos clave

### 2.1 Modelado (sec. 6.1, pág. 17-8/17-9, PDF 335-336)
- Controles recomendados: dibujo desde varios puntos de vista; reacciones solo por peso propio (si hay plano de simetría, reacciones simétricas deben coincidir; si no, hay error de geometría/conectividad).
- Cada nudo debe tener las 3 traslaciones restringidas "en algún sentido". Nudos con barras coplanares (ej. 4 barras en plano yz, fuera del plano libre) dan matriz singular. Soluciones históricas (Fig. 10): apoyo ficticio o barra ficticia de rigidez despreciable. Hoy se suma una rigidez ínfima a toda la diagonal de K. (El texto dice "a todos los elementos de la diagonal".)

### 2.2 Tracción en barras (sec. 6.4.1, pág. 17-10, PDF 337)
- (1) sigma_t = F / Ac < sigma_adm
- (2) un solo bulón en el ala: Ac = (L - d) t   (L = ala del ángulo, t espesor, d diámetro del agujero)
- (3) más de un bulón: Ac = 0,8 (A - t d)   con A = (2L - t) t (área bruta del ángulo)
- Espesor mínimo de barras 4 mm. Distancias mínimas en Anexo 6.
- Observación: la "(L-d)t" de (2) es el área neta de un solo ala con agujero (el ala no conectada se desprecia). El 0,8 de (3) es una reducción por "shear lag" simplificada. El libro no dice si "d" es el diámetro del agujero (con holgura) o del bulón: dice "diámetro del agujero para el bulón".

### 2.3 Compresión y pandeo (sec. 6.4.2, pág. 17-11/17-12, PDF 338-339)
- (4) sigma_c = omega F / A < sigma_adm ; omega = sigma_adm(tracción) / sigma_adm,pandeo ; A es el área **total** (no neta).
- Si lambda < 20 no se verifica pandeo: omega = 1 (texto). Para lambda >= 20 se usa la tabla del Anexo 7 (DIN 4114, acero St 37-2).
- (5) lambda = lp / i ; i = sqrt(I/A) ; para ángulo de alas iguales i_x ~ 1,54 i_eta (ver nota de riesgos: el catálogo da 1,53 a 1,63).
- Elección de I: si en un punto interior hay restricción lateral en una dirección (montante con diagonales concurrentes al centro del tramo, Fig. 12), solo puede pandear en la otra dirección: usar I_x e i_x. Si puede pandear en cualquier dirección (Fig. 13), usar el mínimo I_eta, i_eta.
- Longitud de pandeo, **montantes (esquineros)**:
  - (6) armado Fig. 13: lp = l
  - (7) armado Fig. 12: lp = l si lambda_x = l / i_x < 80
  - Para lambda_x > 80 se puede tomar lp = l si las fuerzas de las montantes crecen de arriba hacia abajo y las longitudes de las barras superiores no son mayores que las inferiores; si no, (8) lp = 1,1 l
- **Diagonales**: (9) lp = l ; (10) lp = 0,9 l si la sección es menor que la de los esquineros contiguos y la diagonal está suficientemente empotrada en la dirección de pandeo ; (11) diagonales cruzadas una traccionada y otra comprimida: el punto de cruce se toma fijo (Fig. 14) y lp es la distancia del extremo al cruce con radio i_eta (la figura marca lp con i_eta).
- Barras compuestas (2 o más ángulos): se analizan como una barra única con "esbeltez ideal"; el libro no da la fórmula (remite a normas).
- Comprobación visual hecha: en el texto extraído algunas ecuaciones perdían símbolos; las anteriores están leídas de la imagen.

### 2.4 Uniones (sec. 6.4.3, pág. 17-13, PDF 340)
- (12) tau_c = 4F / (N pi d^2) < tau_c,adm   (corte simple; N = n° de bulones/remaches)
- (13) sigma_apl = F / (N d t) < sigma_apl,adm   (t = espesor del ala del ángulo)
- Uniones soldadas en torres: "según DIN 18800" (no se desarrolla; ver Cap. 18).
- Solo corte simple (una sección de corte). Para doble corte dividir por el número de planos de corte (no lo dice el libro).

### 2.5 Cables no lineales (Anexo 1, págs. 17-14 a 17-17, PDF 341-344)
Notación: l = distancia entre apoyos (cuerda), P = tracción del cable (subíndice 0 = estado inicial), f = flecha, W = fuerza transversal total sobre el cable (peso, viento, hielo, **vectorial**), delta = alargamiento de la cuerda (variación de distancia entre extremos), A, E, alpha, t.
- (14) f0 / l = W0 / (8 P0) ;  (15) f / (l + delta) = W / (8 P)   (parábola)
- (16) L = l + 8 f^2 / (3 l)  ;  (17) L0 = l + l W0^2 / (24 P0^2) ;  (18) L = (l+delta) + (l+delta) W^2 / (24 P^2)
- (19)-(20) cambio geométrico de longitud (con delta << l): dL = delta + l W^2/(24 P^2) - l W0^2/(24 P0^2)
- (21) dL por Hooke y temperatura: dL = (P - P0) l/(A E) + l alpha (t - t0)
- **(22) ecuación cúbica del cable**: P^3 + P^2 [ A E alpha (t - t0) + a0/(2 P0^2) - P0 - A E delta / l ] - a/2 = 0
  con (23) a = E A W^2 / 12 ; a0 = E A W0^2 / 12.
  Verificada por derivación propia: igualando (20) y (21) y multiplicando por A E P^2 / l se obtiene exactamente (22). Check útil: con delta=0, t=t0, W=W0 la raíz es P=P0.
- **(26) rigidez variable**: K = dP/d delta = (A E / l) P^3 / (P^3 + a). Si P^3 >> a, K -> A E / l (cable tenso, lineal); si P^3 << a, K -> 0 (cable flojo). Verificada derivando (22).
- Algoritmo iterativo (sec. 2, págs. 17-16/17-17):
  1. Datos de montaje P0, t0, a0 (a0 por (23) con W0). Si cambió temperatura/viento/hielo: recalcular P0 de cada rienda con (22) y delta=0.
  2. (27) K0 = (A E / l) P0^3 / (P0^3 + a)
  3. (28) P_L = P0 + K0 delta (cable linealizado). Armar K de mástil+riendas, vector de cargas con cargas exteriores y P0 de riendas, resolver desplazamientos.
  4. (29) delta = t^T . dU (t = vector unitario de la cuerda, dU = diferencia de desplazamientos extremo-extremo). Con delta, resolver (22) para P_NL (cúbica por cable).
  5. (30) K_delta = (A E / l) P_NL^3 / (P_NL^3 + a) ;  (30-b) P0_bar = P_NL - K_delta delta  (intersección de la tangente con el eje P) ; (31) P_L = P0_bar + K_delta delta
  6. (32) control: (P_NL,n - P_NL,n-1) / P_NL,n < epsilon. Dicen que bastan 3 o 4 iteraciones.
  7. Resultados finales: esfuerzos en extremos de tramos del mástil, fuerzas en las barras del reticulado de cada tramo, tensiones (sec. 6.4), fuerzas en anclajes componiendo cables.
  8. (sec. 2.7) se puede incluir en el mismo lazo el efecto no lineal de la compresión axial del mástil (efecto P-delta de columna); no se da el procedimiento.
- Modelo de mástil: tramos reticulados reemplazados por vigas de pórtico espacial de rigidez equivalente (Fig. 18: 7 nudos x 6 GL = 42 GL, 6 tramos, 3 planos de riendas a 120 grados, 15 riendas, 6 anclajes). El libro no da cómo calcular EA, EI, GJ equivalentes del tramo reticulado.

### 2.6 Flecha de montaje de conductores (Anexo 2, págs. 17-18 a 17-21, PDF 345-348)
- (33) f = W l/(8P), con W = rho A l  =>  f_min = rho l^2 / (8 sigma_adm)  (rho = peso específico; cota inferior de flecha).
- Condiciones: (34) flecha máxima mínima ; (35) tiro máximo <= admisible. Estado 0 = temperatura mínima con peso + hielo + viento sobre el manguito, con tiro P0 = sigma_adm A. Estado de montaje (sin viento ni hielo), delta = 0.
- (36) cúbica en P ; (37) f = W l / (8 P)
- **(38)** f^3 - { 3 l^2 [ W0^2/(24 P0^2) + alpha (t - t0) - P0/(A E) ] / 8 } f = 3 W l^3 / (64 A E)
- Si se definen (41-a) a = l^2 [ W0^2/(24 P0^2) + alpha (T - t0) - P0/(A E) ] / 8 ;  (41-b) b = 3 W l^3 / (128 A E) ; (41-c) Delta = b^2 - a^3, la (38) es f^3 - 3 a f - 2 b = 0 (verificado) con solución:
  - (42-a) Delta > 0: c = sqrt(Delta) ; f = (b + c)^(1/3) + (b - c)^(1/3)  (raíz cúbica real con signo)
  - (42-b) Delta < 0: theta = arccos( b / a^1,5 ) ; f = 2 sqrt(a) cos(theta/3)
- Aproximación de Taylor 2do orden en t alrededor de T (ej. 20 °C): (39)/(44) f_t = f_T + f'_T (t - T) + 0,5 f''_T (t - T)^2
  - (43) d = 12 (f_T^2 - a) ; e = 3 l^2 alpha ; f'_T = e f_T / (2 d) ; **f''_T = (e - 24 f_T f'_T) / d** como está impreso (ver ERROR en sección 7).
- Vano económico (qualitativo, sin fórmula): al crecer l suben alturas de torre, bajan cantidad de torres; hay un mínimo de costo total (Fig. 21-b).

## 3. Datos tabulados / gráficos a cargar

| Dato | Dónde | Cantidad | Reemplazable por fórmula |
|---|---|---|---|
| Tabla omega(lambda), DIN 4114 St 37-2 | Anexo 7, pág. 17-25 (PDF 352) | 231 valores (lambda = 20..249 de a 1, más 250) | Para lambda >= ~120: omega = 1,6886e-4 lambda^2 (Euler con sigma=140 MPa, nu=2,5, E=210000). Verificado en 120, 150, 200, 250 (error < 0,005). Para 20-119 hay que usar la tabla (en lambda=100 la fórmula Euler da 1,69 y la tabla 1,90) |
| Perfiles ángulo IRAM-IAS U 500-558 | Anexo 5, págs. 17-23/17-24 (PDF 350-351) | 24 perfiles, ~15 columnas | No. Ver nota: la pág. "2/2" es idéntica a la "1/2" |
| Tensiones admisibles VDE 0210 | Anexo 3, pág. 17-22 (PDF 349) | ~28 valores (normal/excepcional) | No |
| Dimensiones mínimas de uniones | Anexo 6, pág. 17-25 (PDF 352) | 6 medidas x 5 filas | No |
| Tabla de riendas de la torre de 174 m | Fig. 18, pág. 17-16 (PDF 343) | 15 filas | Solo datos geométricos |
| Curvas P-delta, flecha vs temperatura | Figs. 17, 20, 22 | cualitativas | Se regeneran con (22) y (38) |

### 3.1 Tabla omega, Anexo 7 (DIN 4114, St 37-2) - transcripta de la imagen
Formato: fila = decena de lambda, columnas = unidad 0..9.
```
20: 1.04 1.04 1.04 1.05 1.05 1.06 1.06 1.07 1.07 1.08
30: 1.08 1.09 1.09 1.10 1.10 1.11 1.11 1.12 1.13 1.13
40: 1.14 1.14 1.15 1.16 1.16 1.17 1.18 1.19 1.19 1.20
50: 1.21 1.22 1.23 1.23 1.24 1.25 1.26 1.27 1.28 1.29
60: 1.30 1.31 1.32 1.33 1.34 1.35 1.36 1.37 1.39 1.40
70: 1.41 1.42 1.44 1.45 1.46 1.48 1.49 1.50 1.52 1.53
80: 1.55 1.56 1.58 1.59 1.61 1.62 1.64 1.66 1.68 1.69
90: 1.71 1.73 1.74 1.76 1.78 1.80 1.82 1.84 1.86 1.88
100: 1.90 1.92 1.94 1.96 1.98 2.00 2.02 2.05 2.07 2.09
110: 2.11 2.14 2.16 2.18 2.21 2.23 2.27 2.31 2.35 2.39
120: 2.43 2.47 2.51 2.55 2.60 2.64 2.68 2.72 2.77 2.81
130: 2.85 2.90 2.94 2.99 3.03 3.08 3.12 3.17 3.22 3.26
140: 3.31 3.36 3.41 3.45 3.50 3.55 3.60 3.65 3.70 3.75
150: 3.80 3.85 3.90 3.95 4.00 4.06 4.11 4.16 4.22 4.27
160: 4.32 4.38 4.43 4.49 4.54 4.60 4.65 4.71 4.77 4.82
170: 4.88 4.94 5.00 5.05 5.11 5.17 5.23 5.29 5.35 5.41
180: 5.47 5.53 5.59 5.66 5.72 5.78 5.84 5.91 5.97 6.03
190: 6.10 6.16 6.23 6.29 6.36 6.42 6.49 6.55 6.62 6.69
200: 6.75 6.82 6.89 6.96 7.03 7.10 7.17 7.24 7.31 7.38
210: 7.45 7.52 7.59 7.66 7.73 7.81 7.88 7.95 8.03 8.10
220: 8.17 8.25 8.32 8.40 8.47 8.55 8.63 8.70 8.78 8.86
230: 8.93 9.01 9.09 9.17 9.25 9.33 9.41 9.49 9.57 9.65
240: 9.73 9.81 9.89 9.97 10.05 10.14 10.22 10.30 10.39 10.47
250: 10.55
```
Ejemplo del libro: lambda = 48 -> omega = 1,19 (fila 40, col. 8) ✓. Para lambda no entero: interpolar linealmente. Para lambda > 250: el libro no da valor (extrapolar con la fórmula Euler, y avisar).

### 3.2 Perfiles ángulo de alas iguales (Anexo 5; unidades: b,t mm; A cm2; peso kg/m; ex cm; Ix=Iy cm4; rx cm; Iv=I_eta cm4; iv=i_eta cm)
Transcripto de imagen a 220 dpi: **verificar contra la norma IRAM antes de usar en producción**. Columnas omitidas: radios, Sx, Iz, iz, J, Cw.
```
designacion        b     t    A     peso  ex    Ix     rx    Iv    iv
L16x16x3.2        15.9  3.2  0.94  0.74  0.50   0.20  0.46  0.08  0.30
L19x19x3.2        19.0  3.2  1.13  0.89  0.58   0.35  0.55  0.14  0.36
L22x22x3.2        22.2  3.2  1.32  1.04  0.65   0.56  0.65  0.23  0.42
L25x25x3.2        25.4  3.2  1.51  1.19  0.73   0.84  0.75  0.34  0.48
L25x25x4.8        25.4  4.8  2.19  1.72  0.79   1.17  0.73  0.50  0.48
L25x25x6.4        25.4  6.4  2.81  2.20  0.85   1.44  0.72  0.66  0.48
L29x29x3.2        28.6  3.2  1.65  1.30  0.77   1.06  0.80  0.42  0.51
L32x32x3.2        31.7  3.2  1.97  1.55  0.89   1.83  0.96  0.72  0.61
L32x32x4.8        31.7  4.8  2.87  2.25  0.96   2.58  0.95  1.06  0.61
L32x32x6.4        31.7  6.4  3.71  2.91  1.02   3.24  0.93  1.38  0.61
L38x38x3.2        38.1  3.2  2.37  1.86  1.03   3.11  1.15  1.20  0.71
L38x38x4.8        38.1  4.8  3.46  2.71  1.10   4.45  1.13  1.78  0.72
L38x38x6.4        38.1  6.4  4.49  3.53  1.17   5.63  1.12  2.33  0.72
L45x45x3.2        44.4  3.2  2.83  2.22  1.19   5.24  1.36  1.98  0.84
L45x45x4.8        44.4  4.8  4.14  3.25  1.27   7.57  1.35  2.97  0.85
L45x45x6.4        44.4  6.4  5.40  4.24  1.34   9.67  1.34  3.90  0.85
L51x51x3.2        50.8  3.2  3.21  2.52  1.34   7.76  1.55  2.95  0.96
L51x51x4.8        50.8  4.8  4.72  3.70  1.42  11.26  1.54  4.41  0.97
L51x51x6.4        50.8  6.4  6.17  4.84  1.49  14.45  1.53  5.80  0.97
L51x51x7.9        50.8  7.9  7.49  5.88  1.54  17.19  1.52  7.06  0.97
L51x51x9.5        50.8  9.5  8.84  6.94  1.60  19.87  1.50  8.38  0.97
L57x57x3.2        57.1  3.2  3.61  2.84  1.48  10.88  1.73  4.05  1.06
L57x57x4.8        57.1  4.8  5.31  4.17  1.56  15.88  1.73  6.13  1.07
L57x57x6.4        57.1  6.4  6.96  5.46  1.63  20.49  1.72  8.10  1.08
```
Observación: el catálogo solo llega a L57 (torres reales usan ángulos mucho mayores). Las dos páginas del Anexo 5 son **la misma tabla** (la "Página 2/2" repite la 1/2). Faltan los perfiles grandes: pedir al usuario el catálogo completo si se quiere usar en torres.

### 3.3 Tensiones admisibles VDE 0210 (Anexo 3) [N/mm2: normales / excepcionales]
- Estructura metálica, tracción o compresión: St 37-2 160/220 ; St 52-3 240/330. Corte: St 37-2 104/143 ; St 52-3 156/214.
- Bulones calibrados (DIN 7968) corte: 4.6 o USt 36 160/220 ; 5.6 240/320.
- Remaches (DIN 124) aplastamiento (4.6/5.6/USt 36 con St 37-2 o St 52-3): 320/440.
- Bulones comunes (DIN 7990) corte: 4.6 126/173 ; 5.6 168/231 ; 10.9 270/371.
- Bulones alta resistencia sin pretensado (DIN 6914) aplastamiento: (4.6/5.6/10.9 con St 37-2) 280/385 ; (4.6 con St 52-3) 280/385 ; (5.6 o 10.9 con St 52-3) 420/575.
- Tracción en bulón: calibrados 4.6 125/171 ; comunes 5.6 150/206 ; alta resistencia 10.9 410/563.
- Nota del libro: es un extracto de la Tabla 9 de la VDE 0210. "Normales" = hipótesis normales; "excepcionales" = con rotura de conductor, sin viento (sec. 4.3).

### 3.4 Dimensiones mínimas de uniones (Anexo 6) [mm]
| | M12 | M16 | M20 | M24 | M27 | M30 |
|---|---|---|---|---|---|---|
| Diám. máx. agujero, bulón | 14 | 18 | 22 | 26 | 29 | 32 |
| Diám. máx. agujero, remache | 13 | 17 | 21 | 25 | 28 | 31 |
| Ancho mínimo del ala | 35 | 50 | 60 | 70 | 75 | 80 |
| Dist. mín. al extremo, compresión | 20 | 25 | 30 | 40 | 45 | 50 |
| Dist. mín. al extremo, tracción | 25 | 35 | 40 | 50 | 55 | 65 |
Notas: distancias desde el centro del agujero; si el esfuerzo es de tracción cumplir el valor mayor (el texto dice "cumpliendo con el valor menor. Si el esfuerzo es de tracción se debe cumplir el valor mayor": ambiguo). Borde perpendicular >= 1,2 x diámetro del agujero; entre centros >= 2,5 x diámetro del agujero.

### 3.5 Fig. 18: plano de riendas (torre 174 m, 5 niveles)
Altura del nivel [m] / distancia horizontal al anclaje [m] / n° alambres / diámetro [mm]: nivel 1: 30/75/19/14 ; nivel 2: 60/75/19/16 ; nivel 3: 90/75/19/17,5 ; nivel 4: 126/115/19/17,5 ; nivel 5: 160/115/37/22. Altura inicial del anclaje = 0 (anclajes a nivel). Riendas 1,4,7 / 2,5,8 / 3,6,9 / 10,12,14 / 11,13,15 (3 planos a 120 grados). **No se dan** E, A de cable, P0 de montaje, cargas ni resultados.

## 4. Ejemplos resueltos del texto

Solo el Anexo 2, sec. 5 (págs. 17-20/17-21, PDF 347-348): flecha de montaje de conductor de cobre.
Datos: A=70 mm2, l=140 m (140000 mm), E=90000 N/mm2, alpha=1,7e-5 1/°C, sigma_adm=120 N/mm2 (-> P0=8400 N), h_min=6000 mm, t_min=-15, t_max=45 °C, peso conductor 6,44 N/m, hielo 5 N/m, viento sobre manguito 4 N/m, viento sobre conductor 3 N/m.
Derivados: W=901,6 N ; q0=sqrt((6,44+5)^2+4^2)=12,12 N/m -> W0=1697 N ; q_bar=sqrt(6,44^2+3^2)=7,105 N/m -> W_bar=995 N.
Resultados del libro (todos reproducidos con mi script salvo la nota):
| Caso | a | b | Delta | f [mm] |
|---|---|---|---|---|
| A (T=20, W=901,6) | 2,3575e6 | 9,2038e9 | 7,131e19 (el libro escribe 71,31e18) | f20 = 3510 (exacto 3509,6) |
| B (T=0, W=W0=1697) | 1,5245e6 | 1,7324e10 | 2,9656e20 | f0 = 3725 |
| C (T=45, W=995, estado 0 en -15 con W0=1697, P0=8400) | 3,40e6 | 1,0157e10 | 6,391e19 | f = 3921 ; proyección vertical 3921 x 6,44/7,105 = 3554 |
| D (estado 0: t0=20, W0=901,6, P0=4495 N) | 3,4e6 | 1,0157e10 | 6,39e19 | f45 = 3921 (mismo que C) |
Taylor (Paso 2, T=20): d=1,1952e8 ; e=999600 ; f'_20=14,6764 mm/°C ; **el libro da f''_20=-0,00198 (incorrecto, ver sección 7)**; resultado impreso f_t = 3510 + 14,676 (t-20) - 0,00099 (t-20)^2 ; f_max = f_45 = 3877 mm ; H = h_min + f_max = 9877 mm.
Valores corregidos (mis cálculos): f''_20 = -0,02905 ; f_45 por Taylor = 3867,4 mm (exacto de (38) = 3867,3) ; H = 9867 mm. Diferencia con el libro: ~10 mm (0,26 %), dentro del "2 %" que afirma el libro, pero el valor impreso es erróneo.
Tests sugeridos: f(-15)=2979,5 ; f(0)=3210,5 ; f(20)=3509,6 ; f(45)=3867,3 (W=901,6, mismo estado 0). Tiro de montaje a 20 °C: P = W l/(8 f) = 4495,7 N (el libro: 4495).

Test propio para el cable no lineal (no del libro): E=150000 N/mm2, A=500 mm2, l=100000 mm, q=40 N/m (W=4000 N), P0=30000 N, t=t0: a=1e14 ; P(delta=0)=30000 ✓ (cumple la cúbica) ; K0 = 159,45 N/mm (vs AE/l = 750) ; delta=+5 mm -> P=30823 N, K=169,88 ; delta=+10 -> P=31700 N, K=181,20 ; delta=-5 -> P=29227 N, K=149,84. (Datos inventados, solo para validar que la implementación cumple (22) y (26).)

## 5. Propuesta de implementación en Struttura

### 5.1 Verificación de barras con criterio normativo (tipo B sobre resultados de reticulado/pórtico 3D)
- Entradas CSV (bloques nuevos): `PERFILES` (catálogo ángulo o tubo: A, i_min, i_x, material), `VERIF_BARRAS` (barra, perfil, tipo=montante/diagonal, armado=simple/doble/cruzada, l, factor lp, n° bulones, d_agujero, t), `ADMISIBLES` (material -> sigma_adm normal/excepcional, tau, apl). Salidas: sigma_t con Ac (2)/(3), lambda, omega por interpolación, sigma_c, relación sigma/sigma_adm por hipótesis, esfuerzo máximo de tracción/compresión por barra (envolvente, paso f del sec. 5.2), corte y aplastamiento de bulones (12)(13), peso/cómputo.
- Se conecta con `portico3d` (esfuerzos axiles de barras vía `esfuerzos.py`) y con `reticulado` (plano). Dificultad 2. Tiempo: mediano. Dependencia: Cap. 18 para remaches/bulones excéntricos (opcional) y pandeo general (otro capítulo del compendio si lo hay).

### 5.2 Reticulado espacial 3D (tipo A, extensión de portico3d)
- Un tipo de barra "biarticulada" (solo axil, 6x6 por barra en 3 GL por nudo, o 12x12 con liberaciones de rotación) + regularización de rigidez ínfima en la diagonal (sec. 6.1) o detección de GL sin rigidez con aviso. Salidas: axiles, reacciones, control de simetría de reacciones por peso propio (recomendación del libro 6.1-b).
- Dificultad 3. Tiempo: mediano. Dependencia: ninguna (usa `barra.py`/`solver.py` de portico3d). Es la base natural para torres, cerchas espaciales, soportes de motor tipo reticulado.

### 5.3 Elemento cable no lineal (tipo A, extensión)
- Elemento cable de 2 nudos (3 GL c/u) con cuerda l, A, E, alpha, P0 de montaje, t0, W (vector transversal) -> rigidez tangente K_delta (26)/(30) a lo largo de la cuerda + fuerza inicial P0_bar como carga nodal; lazo de iteración 2.1-2.6 hasta (32). Entrada: bloque `CABLES` (nudo i, nudo j, A, E, alpha, P0, t0, q_transversal, material), `TEMPERATURA`. Salida: P_NL, delta, K por iteración (tabla de convergencia), fuerza en anclajes.
- Dificultad 4. Tiempo: grande (lazo no lineal + vector W + validación). Depende de 5.2 o de portico3d con barras axiales.
- Alternativa más barata: tipo B "calculadora de un cable aislado" que resuelve (22) para P(delta) y traza la curva con K(delta) (dificultad 1, unidad chica).

### 5.4 Calculadora de flecha de montaje (tipo B, Anexo 2)
- Entradas: A, l, E, alpha, sigma_adm, W (o q, hielo, viento), t_min, t_max, t0. Salidas: f(t) exacta por (41)-(42), polinomio de Taylor corregido (43)-(44), tiro P(t), gráfico f(t) y P(t). Reproduce el ejemplo del libro (con la fórmula de f'' corregida). Dificultad 2. Tiempo: chico.

### 5.5 Anexo teórico (tipo C)
Ver sección 6.

### Aplicabilidad
- **Fuselaje de tubos soldados**: (a) la verificación de pandeo con omega + longitud de pandeo (6)-(11) es transferible en estructura (barra comprimida de cercha espacial), pero la tabla omega es de St 37-2 y los ángulos no aplican (para tubo i es isótropo: usar i = sqrt(I/A) sin 1,54). Para acero aeronáutico de tubos (ej. aceros tipo 4130 normalizados) hace falta otra curva de pandeo o la fórmula de Euler/Johnson con las propiedades del material (preguntar al usuario con qué material y criterio de pandeo trabaja). (b) La idea de cruce de diagonales con el punto de cruce fijo (11) se aplica a fuselajes con diagonales cruzadas (tipo Warren doble o tensores). (c) Los nudos de un fuselaje soldado son rígidos: lp < l; el libro supone nudos articulados, así que su coeficiente de longitud de pandeo no sirve directamente. (d) La sec. 6.4.1 (sección neta con agujeros) solo aplica a herrajes abulonados, no a tubos soldados. (e) Control de modelo (simetría de reacciones por peso propio, plano de simetría) sí es útil en el modelo del fuselaje ya hecho con pórtico espacial.
- **Estructuras mecánicas generales**: cables/tensores pretensados con temperatura (5.3/5.4), cerchas espaciales soporte, verificación de ángulos y uniones abulonadas, estructuras con tensores de bicicleta tipo rueda, puentes grúa livianos, etc.

## 6. Anexo teórico para los informes (qué incluir, sin copiar texto)
- Verificación de barras: ecuaciones (1)-(5) con la definición de omega y la tabla/interpolación usada; reglas de longitud de pandeo (6)-(11) con el criterio de lambda_x < 80; tipo de hipótesis y tensión admisible usada.
- Uniones: (12) y (13) con la aclaración de planos de corte.
- Cables: (14), (22), (23), (26), (27)-(32) en forma de algoritmo, y la observación de que K tiende a AE/l o a 0 según P^3 vs a. Referencia: Cap. 17 Anexo 1.
- Flecha de montaje: (33), (38), (41)-(44) con la corrección de f''. Referencia: Cap. 17 Anexo 2.
Citar siempre "Compendio CE-II, Cap. 17, sec./ec. n" y las normas originales como referencia indirecta (DIN 4114, VDE 0210).

## 7. Riesgos, inconsistencias y preguntas al usuario

**Errores / inconsistencias detectadas**
1. **Ec. (43), f'': el libro imprime f''_T = (e - 24 f_T f'_T)/d y obtiene -0,00198 (ejemplo, pág. 17-20, usando f'_T sin elevar al cuadrado y sin multiplicar e por f').** Derivando (38) dos veces se obtiene f'' = (e f' - 24 f f'^2)/d. Con los datos del ejemplo da -0,02905, coincidente con la derivada numérica (-0,02905) del f exacto. Consecuencia: f_45 pasa de 3877 a 3867 mm y H de 9877 a 9867 mm. Implementar la fórmula corregida y dejarlo señalado en el informe.
2. **Notación P0 en el Anexo 1**: "P0" designa a la vez la fuerza de montaje (usada en (22) y en a0) y la fuerza recalculada con delta=0 para el estado de cálculo (sec. 2.1-a) y la que entra en (27). Hay que distinguir P0_montaje (con a0) de P_ini (con a) en el código. El texto no lo hace.
3. **Tabla omega**: para lambda < 20 el libro dice omega = 1, pero la tabla empieza en 1,04 (salto). La tabla corresponde a DIN 4114 calibrada con sigma_adm = 140 N/mm2 (verifiqué la fórmula de Euler con nu=2,5 y 140 en lambda >= 120), mientras que la sigma_adm de VDE 0210 (Anexo 3) para St 37-2 es 160 (normales) o 220 (excepcionales). Preguntar si se acepta usar omega de DIN 4114 con la sigma_adm de VDE 0210 o hay que recalcular la curva con otra sigma_adm.
4. i_x ~ 1,54 i_eta es aproximado: del catálogo del Anexo 5 sale 1,53-1,63 (ej. L51x4,8: 1,54/0,97 = 1,59). Con 1,54 se subestima i_x (es conservador). Mejor usar las columnas del catálogo.
5. Anexo 5: las dos hojas son idénticas (la 2/2 repite la 1/2).
6. Anexo 6: nota "cumpliendo con el valor menor. Si el esfuerzo es de tracción se debe cumplir el valor mayor" es ambigua.
7. Anexo 1: se asume la cuerda y W normal a la cuerda en el plano (parábola) pero para riendas inclinadas (75 m horizontal x 160 m vertical) el libro no dice si W es q l o q l cos(phi) (componente normal a la cuerda), ni si P es la tracción en el extremo o la componente horizontal. Asumir: W = componente de las cargas normal a la cuerda; confirmar con la fuente (refs. [2],[3] del libro: Desai-Abel y Robinson).
8. La longitud "l" de (7)-(8) en las Figs. 12/13 es la del tramo montante entre nudos; no queda 100 % claro en el texto si es la distancia entre nudos de diagonales o entre arriostramientos. Confirmar en la figura antes de implementar.
9. Eq. (12): corte simple; para doble corte hay 2 planos. Eq. (13): t es el menor espesor de las piezas conectadas en esa dirección.
10. Eq. (3): factor 0,8 aplica a ángulos con 2 o más bulones "en línea"; no se dice nada de bulones en las dos alas.
11. Los coeficientes y tensiones son de normas DIN (St 37-2 / St 52-3); para acero argentino (F-24, F-36, IRAM-IAS U 500-503) no hay equivalencia en el libro.

**Preguntas al usuario**
- ¿El fuselaje es de tubo de acero aeronáutico? ¿Qué material, diámetro, espesor y qué norma de aceptación (certificación) quiere usar? El libro solo trae admisibles de acero estructural DIN.
- ¿Los nudos del fuselaje se modelan articulados (reticulado) o rígidos (pórtico, como ya está)? Define si el pandeo con omega/lp del libro se puede usar o si conviene Euler con k de nudo rígido.
- ¿Querés cables no lineales (riendas) en Struttura o solo la calculadora de flecha? Es el ítem más caro del capítulo.
- ¿Cuál es el sistema de unidades preferido para entrada (mm/N/MPa)? El libro mezcla mm y m (ejemplo en mm con N/m).
