# Cap. 15 - Cañerías (Compendio Cálculo Estructural II, UNC-FCEFyN, ed. 2024)

Páginas del PDF: 254-281 (numeración del libro 15-1 a 15-28; PDF = libro + 253).
Cada fórmula se verificó mirando la página como imagen (el texto extraído pierde letras griegas, signos menos y subíndices).
Lo marcado como **[mío]** no está en el libro: lo calculé o lo deduje yo (y lo verifiqué numéricamente cuando se indica) o es conocimiento externo que conviene contrastar con la norma.

---

## 1. Qué resuelve el capítulo y para qué sirve en diseño

Es una introducción corta (el propio libro lo llama "breve presentación") al análisis de sistemas de cañerías por el método de la rigidez. Hace tres cosas:

1. Lista los componentes y cómo se modelan estructuralmente (Tabla 1, p. 257): tramo recto = viga con presión, junta de expansión = elemento flexible (resorte), válvula/bomba = rígido, codo = elemento codo, T = accesorio T, reducción = sección promediada, soporte = barra biarticulada/resorte.
2. Deduce la **matriz de rigidez del codo de radio constante** (sección 4), que es el único elemento nuevo respecto de lo que ya tiene un programa de pórticos 3D. La ovalización se mete como "factor de flexibilidad k" que ablanda la flexibilidad de viga curva.
3. Da las **verificaciones mínimas del código ASME B31.1** (espesor por presión, tensión longitudinal sostenida, sostenida + ocasional, rango de tensiones por expansión térmica con fatiga) y los anexos de datos (tensiones admisibles, E de junta, coeficiente y, factores k e i).

Para diseño sirve para: decidir si una cañería (o un tubo curvo) soporta presión + peso + dilatación térmica sin exceder admisibles, y cuánta flexibilidad hay que darle (liras, juntas de expansión, pretensión de apoyos) para bajar las solicitaciones térmicas. No trae ningún ejemplo numérico.

---

## 2. Fórmulas y algoritmos clave

### 2.1 Geometría del elemento codo (sec. 4, p. 261, ec. (1)-(3), Fig. 12)

Datos: coordenadas de los extremos I y J, sección (D exterior y t), radio de curvatura R, y un punto K que da la orientación del eje del elemento anterior (vector KI = tangente en I).

```
N3 = KI x IJ            (normal al plano del codo -> eje local x3)         (1)
N2 = N3 x KI            (en el plano, apunta hacia el centro C -> eje x2)  (1)
OC = OI + R * N2/|N2|   (centro de curvatura)                              (2)
cos(phi) = (CI . CJ) / (|CI| |CJ|)   (ángulo de apertura)                  (3)
x1 = KI/|KI|  (tangente en I, apunta de K hacia I; en la Fig. 12 va hacia la izquierda y J queda del lado +x1)
```

Verifiqué que (x1, x2, x3) así construida es terna derecha (x1 x x2 = x3).

### 2.2 Matriz de equilibrio H (p. 261-262, ec. (4) y (5))

Con A = (Ax, Ay, Az) = componentes del vector IJ **en ejes locales del codo**:

```
        [ I3   0 ]          [  0  -Az  Ay ]
[H] =   [ S    I3]    S =   [  Az   0  -Ax ]      (S*F = A x F)         (5)
                            [ -Ay  Ax   0  ]

Pi + [H] Pj = 0      y      Pj + [H]^-1 Pi = 0                           (4)
```
Pi, Pj = (fuerza, momento) aplicados en I y J. Verifiqué que es equilibrio de fuerzas y de momentos respecto de I.

### 2.3 Matriz de rigidez (p. 262, ec. (6), (7))

Se empotra el codo en I, se obtiene la flexibilidad F_JJ (6x6) del extremo J (desplazamientos de J por cargas unitarias en J; "Método de las fuerzas") y:

```
K_JJ = F_JJ^-1
K_II =  H K_JJ H^T
K_IJ = -H K_JJ
K_JI = -K_JJ H^T            (el texto extraído perdió los signos menos; la imagen los muestra)
K = [ K_II  K_IJ ; K_JI  K_JJ ]   (12x12, ejes locales del codo)         (7)
```
Después hay que rotar a globales (T^T K T) y ensamblar. Ojo: el orden de GDL del libro (u1,u2,u3,th1,th2,th3 por nodo en ejes x1,x2,x3 del codo) coincide con el de Struttura (u,v,w,θx,θy,θz) si se usa la terna del codo como "terna local" (x1,x2,x3).

**El libro NO da la matriz F_JJ explícita** ("se pueden seguir los lineamientos del método de las fuerzas"). Hay que deducirla. Mi deducción **[mío]** (verificada numéricamente):

Con I en el origen, x1 tangente en I, centro C en (0,R,0), J en (R sin(phi), R(1-cos(phi)), 0). Para una carga unitaria en J, el esfuerzo en la sección de ángulo theta (0..phi) es el de equilibrio del trozo theta..phi. Con T = (cos th, sin th, 0) tangente, Nn = (-sin th, cos th, 0) hacia C, e3 = (0,0,1) y r = PJ - P(theta):

```
M(theta) = r x F + M_J
N = F.T ;  Mt = M.T ;  M_out = M.Nn ;  M_in = M.e3        (axial, torsor, flexión fuera y dentro del plano)
F_JJ = Integral_0^phi  B^T D B  R dtheta
D = diag( 1/(E A),  1/(G J),  ko/(E I),  ko/(E I) )        (corte opcional; el libro lo desprecia en R/h>3, Cap.9 p.9-11)
```
`ko` = factor de flexibilidad k (ec. (8) o Cap. 9 ec. (33)): **solo multiplica la flexibilidad de flexión** (en ambos planos); axial y torsión quedan con la teoría de viga recta. Eso es lo que hace B31.1/CAESAR II y es lo que dice la frase del libro "sus componentes deben ser corregidos por k", aunque el libro no aclara a qué componentes. Se puede integrar con cuadratura de Gauss (no hace falta forma cerrada).

Chequeos que hice con ese integral (E=200000 MPa, nu=0,3, tubo 4" Sch40, R=152,4 mm, phi=90 grados):
- límite recto (R->inf, phi->0): reproduce L/EA, L^3/3EI, L/GJ, L/EI.
- carga fuera del plano en J, cuarto de círculo: delta = P R^3 [ ko (pi/4)/EI + (3pi/4 - 2)/GJ ]  (forma cerrada coincide con la numérica a 8 cifras).

### 2.4 Factor de flexibilidad y flexibilidad característica (p. 262, ec. (8), Fig. 13; Anexo 14 fila 1, p. 281)

```
k = 1,65 / h        h = t R / rm^2        rm = (D - t)/2                     (8)
```
(D exterior, t espesor, R radio de curvatura del eje, rm radio medio de la sección). Radios: en la Fig. 13 el libro dice R ~ 2 rm (corto) y R ~ 3 rm (largo). En el Anexo 6-a (p. 273) las dimensiones centro-extremo del codo largo de 90 grados son A = 1,5 DN (NPS 4: 152 mm = 1,5 x 101,6) y del corto C = DN (NPS 4: 102 mm), o sea R = 1,5 DN y R = DN; "R ~ 3 rm" equivale a 1,5 D solo si t es chico. Para calcular conviene usar el R real.

### 2.5 Tabla de factores k e i (Anexo 14, p. 281; reproduce tabla reducida del Anexo D de B31.1)

| Fila | Componente | h (flexibilidad característica) | k | i |
|---|---|---|---|---|
| 1 | Codo/curva para soldar | t R / rm^2 | 1,65 / h | 0,9 / h^(2/3) |
| 2 | Codo mitrado, varios gajos cortos (s < r(1+tan th), B >= 6 tn, th <= 22,5 grados) | s t cot(th) / (2 rm^2) | 1,52 / h^(5/6) | 0,9 / h^(2/3) |
| 3 | Codo mitrado, pocos gajos largos (s >= r(1+tan th), th <= 22,5 grados) | t (1 + cot th) / (2 rm) | 1,52 / h^(5/6) | 0,9 / h^(2/3) |
| 4 | T para soldar B16.9 | 3,1 t / rm | 1 | 0,9 / h^(2/3) |
| 5 | T fabricada reforzada | (t + tr/2)^2,5 / (rm t^1,5) | 1 | 0,9 / h^(2/3) |
| 6 | T fabricada sin refuerzo | t / rm | 1 | 0,9 / h^(2/3) |
| 7 | Reducción concéntrica B16.9 | - | 1 | min( 2,0 ; 0,5 + (alfa/100) sqrt(D2/t2) ), alfa en grados |

En la fila 3 el radio equivalente del mitrado es R = rm (1+cot th)/2 y en la fila 2 es R = s cot(th)/2 (Fig. de la tabla). Las "Notas (1)-(13)" del Anexo D de B31.1 (efectos de bridas en el extremo, límites de validez, etc.) **no están reproducidas** salvo la Nota (5).

**Nota (5) - corrección por presión interior en codos de gran diámetro y pared delgada (filas 1 a 3):**
```
k_p = k / [ 1 + 6 (p/E) (rm/t)^(7/3) (R/rm)^(1/3) ]
i_p = i / [ 1 + 3,25 (p/E) (rm/t)^(5/2) (R/rm)^(2/3) ]
```
(p presión interior, E módulo de Young).

### 2.6 Formulación alternativa del Cap. 9 (sec. 5, PDF p. 140; la remite el libro, p. 262)

```
lambda = R t / ( rm^2 sqrt(1 - nu^2) )          gamma = R/rm                (32)
ko = 1,66 / lambda          (lambda <= 1)                                    (33)
io = 2 lambda^(-0,667) (1 + 0,25/gamma)   (0,05 <= lambda <= 1)              (34)
con presión: psi = p R^2/(E rm t)  (0 <= psi <= 0,1)                          (37)
kp = ko / [1 + 1,75 lambda^(-1,333) exp(-1,15 (psi - 0,25))]                  (35)
ip = io / [1 + lambda^(-1,333) exp(-(psi - 0,25))]   -> sigma = ip*sigma_nom  (36)
```
(las dos últimas con el 0,05 <= lambda <= 1 y 0 <= psi <= 0,1.) Tensión nominal sigma_nom = M rm/I_nom, I_nom = pi rm^3 t, M = sqrt(M1^2+M2^2+T^2) (Tresca) (Cap. 9 ec. (29)-(31)).

**Diferencia que verifiqué numéricamente [mío]** para 4" Sch40 largo (D=114,3; t=6,02; R=152,4; nu=0,3): h = 0,3130, k(Anexo 14) = 5,272, i(Anexo 14) = 1,952; lambda (Cap.9) = 0,3281, ko = 5,059 (-4 %), io = 4,579 (**2,3 veces mayor** que i del Anexo 14). El libro dice (p. 262) que difieren "levemente"; eso vale para k pero **no para i**. Razón probable: el i de B31.1 está normalizado con la soldadura circunferencial a tope (fatiga), no es una relación de tensión pico/nominal como el io del Cap. 9. No hay que mezclarlos: i de B31.1 solo para las ecuaciones (10)-(12); io de Cap. 9 solo para una tensión pico "real" (Von Mises) y con otro criterio de aceptación.

### 2.7 Presión interior en tramos rectos (sec. 7.1, p. 264, ec. (9), Párr. 104.1 de B31.1)

```
tm = P D0 / ( 2 (S E + P y) ) + A          espesor mínimo requerido
Pa = 2 S E (t - A) / ( D0 - 2 y (t - A) )   presión admisible para espesor t          (9)
```
S tensión admisible a la temperatura de diseño (Anexo 11), E eficiencia de junta (Anexo 12; forjados E=1), y coeficiente por temperatura (Anexo 13), A espesor adicional (corrosión, roscas; lo fija el proyectista).
Procedimiento: calcular tm; elegir tn comercial (B36.10M, Anexo 2) tal que tn*(1-0,125) - A >= tm. Tolerancia de fabricación del caño: +0 / -12,5 % (p. 264).
Presión externa -> Sec. VIII Div. 1 (Cap. 16, no cubierto acá). Accesorios estándar: se valen por la curva P-T de su norma o se asimilan al caño recto equivalente (7.3, p. 265).

### 2.8 Tensiones longitudinales (sec. 7.4, p. 265-266, ec. (10)-(17), Párr. 104.8)

```
Sostenidas (presión + peso + permanentes):
  SL = P D0/(4 tr) + Ci MA/W  <=  Sh          Ci = max(1 ; 0,75 i)               (10)

Sostenidas + ocasionales (sismo, viento, alivio de válvulas, transitorios):
  P D0/(4 tr) + Ci MA/W + Ci MB/W  <=  K Sh   Ci = max(1 ; 0,75 i)              (11)
  K = 1,15 (<= 8 h cada vez y <= 800 h/año) ;  K = 1,20 (<= 1 h cada vez y <= 80 h/año)

Rango por desplazamientos (expansión térmica, asentamientos):
  SE = i MC / W  <=  SA                                                           (12)
  SA = f (1,25 Sc + 1,25 Sh - SL)                                                 (13)
  f = 6 / N^0,2  ,  0,15 <= f <= 1                                                (14)
  N = Sum_{k=1..n} Nk (Sk/SM)^5 ,  SM = max(S1..Sn)                               (15)
  Mj = sqrt(Mx^2 + My^2 + Mz^2) ,  j = A, B, C   (Mx,My flectores; Mz torsor)     (16)
  W = pi rm^2 tr                                                                  (17)
```
tr = espesor remanente = tn - A - tolerancia (p. 265). Sc, Sh = admisibles en frío y caliente (Anexo 11). MA = momento de cargas sostenidas; MB = momento de cargas ocasionales; MC = momento del rango por desplazamientos ("momento efectivo"). Unidades de i: adimensional.

Valores de borde de f: f = 1 cuando N <= 6^5 = 7776; f = 0,15 cuando N >= 40^5 = 1,024e8 [mío, aritmética de (14)].

### 2.9 Metodología de análisis térmico (sec. 6, p. 263-264)

Orden recomendado por el libro: (a) solo térmica con empotramientos en los extremos; (b) agregar liras/juntas de expansión; (c) movimiento forzado de apoyos (pretensión en frío); (d) peso propio y del fluido, definiendo soportes (ubicarlos donde los desplazamientos térmicos son chicos; los soportes elásticos se estudian en frío y en caliente); (e) presión y otras permanentes; (f) cargas ocasionales y resonancia; (g) verificar soportes por separado; (h) verificaciones de la norma con las combinaciones que exige; (i) redimensionar y repetir.

### 2.10 Soportes y elementos especiales (sec. 3.3-3.4, p. 257-260)

Tipos de soporte: rígidos (vigas fijas, patines, abrazaderas, cunas, rodillos, "parrales" = estructuras que se analizan aparte), elásticos de carga variable (resorte, reacción proporcional a la deformación), de carga constante (fuerza casi constante, caros), dinámicos (pretensados + amortiguador). **El libro no da rigideces, curvas ni ecuaciones de soportes**: solo clasificación y figuras. Rígido = viga de rigidez "varios órdenes de magnitud superior"; flexible = resorte con constantes axial/flexión/torsión conocidas; reducción = propiedades promedio de los extremos; T y mitrados = armarlos con elementos y **condensación estática** de los nudos interiores (p. 258).

---

## 3. Datos tabulados / gráficos a cargar

Todo está en los anexos (pp. 268-281). Ninguna curva; todo son tablas, más fórmulas cerradas.

| Anexo | Qué es | Pág. PDF | Cuántos valores | Reemplazo por fórmula |
|---|---|---|---|---|
| 1 | Clasificación de materiales ASTM/API (texto) | 268 | solo texto | no aplica |
| 2 | Caños B36.10M: OD y espesor por Sch (arriba: 2" con 13 espesores; abajo resumen ½" a 24") | 269 | ~110 filas (DN, Sch, e) | no |
| 3 | P-T de bridas/válvulas Grupo 1.1 (bar) | 270 | 16 temperaturas x 7 clases (150..2500) = 112 | no |
| 4-a/b/c | Bridas clase 300 (dimensiones, tornillos) | 270-272 | 4-c: 20 filas x 8 col.; 4-a/b son imágenes | no |
| 5 | Texto del Párr. 102.2.4 (+15 %/8 h, +20 %/1 h) | 272 | 2 números (ya están en K de (11)) | - |
| 6-a | Dimensiones B16.9: codos largos 90/45, cortos, tes y cruces | 273 | ~45 filas x 4 col. (codos) + ~45 x 2 (tes) | codo largo 90: A = 1,5 DN (verificar) |
| 6-b | Esquemas de otros accesorios | 274 | imágenes | no |
| 6-c | Espesores de accesorios soldados a tope (STD, XS, Sch160, XXS) | 275 | ~22 filas x 6 col. | no |
| 7 | P-T Grupo 1.5 (bar) | 275 | 16 x 7 = 112 | no |
| 8, 9 | Socket welding y roscados | 276-277 | 12 filas x ~12 col. (Anexo 9) | no |
| 10 | Válvula esférica serie 300 | 278 | imagen | no |
| 11 | S admisible vs T (MPa) de 23 materiales, -30..600 C, + Su, Sy | 279 (girada) | 23 filas x 13 temperaturas + 2 = ~345 | no (interpolar lineal) |
| 12 | Eficiencia de junta E (4 tipos, 7 valores) | 280 | 7 valores | tabla chica |
| 13 | Coeficiente y vs T (3 familias x 8 T) | 280 | 24 valores | y = d/(d+D0) para D0/tm < 6 y T <= 480 C (nota b) |
| 14 | k e i | 281 | 7 filas de fórmulas (sección 2.5) | **todo es fórmula**, no hay datos |

Lo mínimo para empezar: Anexos 11, 12, 13 y 14, y la tabla de caños del Anexo 2 (como catálogo opcional). El resto (bridas, P-T) solo hace falta si el usuario quiere verificar accesorios normalizados (7.3). **Los materiales típicos de fuselaje (SAE 4130, 4130N, 1020, aluminios) NO están**: el usuario tendría que cargar S, Sc, Sh a mano.

---

## 4. Ejemplos resueltos del texto

**El capítulo no trae ningún ejemplo numérico** (solo figuras y el aviso de que la cátedra tiene un programa "ANSI" en Fortran que verifica 7.1 y 7.4, p. 267). Los valores del único ejemplo dimensional del texto: "2" Sch.40 = 2,375" x 0,154"" (p. 256) y "2" BWG 12 = 2" x 0,109"" - coinciden con el Anexo 2 (3,91 mm).

Como no hay casos del libro, propongo **tests propios [míos]**, todos calculados y los marcados (v) verificados con script Python independiente:

**T1 - factores del codo (v).** 4" Sch40 (D=114,3; t=6,02), R=152,4: rm=54,14; h=0,3130; k=5,272; i=1,952. Cap. 9: lambda=0,3281; ko=5,059; io=4,579 (nu=0,3).

**T2 - flexibilidad de un cuarto de codo (v).** E=200000 MPa, nu=0,3 (G=E/2,6), A=2 pi rm t, I=pi rm^3 t, J=2I, R=152,4, phi=90 grados, terna del codo (x1 tangente, x2 al centro). Para ko=1: delta33 = 7,362e-6 mm/N; d11 = 4,924e-6; d22 = 2,393e-6; d12 = -2,762e-6. Para ko=k=5,272: d33 = 2,7145e-5; d11 = 2,4707e-5; d22 = 1,1365e-5; d12 = -1,5357e-5. (d33 tiene forma cerrada: P R^3[ko(pi/4)/EI + (3pi/4-2)/GJ].) Los términos de flexión pura: d11 = ko(pi/4) R^3/EI (+ axial), d22 = ko(3pi/4-2) R^3/EI, d12 = -ko(1/2) R^3/EI.

**T3 - propiedades de K.** K simétrica; 6 autovalores nulos (movimientos de cuerpo rígido); K_II = H K_JJ H^T; equilibrio Pi + H Pj = 0; en el límite R->inf, phi->0 con ko=1 tiene que dar la matriz de la barra recta 12x12 de `rigidez_local`.

**T4 - B31.1, caño recto A106 Gr.B (S=118 MPa hasta 300 C, Anexo 11), 4" Sch40, P=2 MPa, E=1, y=0,4, A=1,5 mm (supuesto) (v):**
tm = 2,462 mm; con t = 0,875 x 6,02 = 5,2675 mm (tolerancia -12,5 %): tr = 3,7675 mm; Pa = 7,990 MPa; PD0/(4 tr) = 15,17 MPa; W = pi rm^2 tr = 34 693 mm^3.

**T5 - sostenidas con el codo de T1 (v).** Ci = max(1; 0,75 x 1,952) = 1,464; MA admisible = (118 - 15,17)/1,464 x 34 693 = 2,436e6 N mm.

**T6 - expansión (v).** Sc=Sh=118, SL=15,17: SA = f x 279,8 (N <= 7776 -> 279,8 MPa); N=1e5 -> f=0,600, SA=167,9; N=1e6 -> f=0,3786, SA=105,9. Momento admisible de rango en el codo: SA/i x W = 4,973e6 (N<=7776), 2,984e6 (N=1e5), 1,883e6 N mm (N=1e6). Ciclos equivalentes: 1000 ciclos a SM y 10000 a 0,5 SM -> N = 1000 + 10000 (0,5)^5 = 1312,5.

**T7 - tubo aeronáutico curvo (ilustrativo, v).** Tubo 25 x 0,9 mm doblado R = 3D = 75 mm: rm=12,05; h=0,465; k=3,55; i=1,50. Una curva de ese tipo flexa ~3,5 veces más que la viga curva sin ovalización.

Nota: se podría pedir a la cátedra el programa ANSI o ejemplos resueltos para contrastar; hoy no hay validación contra el libro.

---

## 5. Propuesta de implementación en Struttura

Hay tres piezas independientes. Recomiendo hacerlas en este orden.

### 5.1 Pieza A1 - elemento CODO dentro del pórtico espacial 3D (tipo A, extensión de `portico3d`) - dificultad 3 (solver), 4 (con visor/informe), tamaño mediano a grande

Cómo se conecta con lo existente (`portico3d`): el solver ensambla `b.k_global` en los GDL (`_dofs`) de cada barra; un codo es una barra con otra `k_local` 12x12 y otra terna. Entonces:

1. `codo.py`: función `rigidez_codo(E, G, A, I, J, R, phi, ko)` que integra F_JJ por Gauss (sec. 2.3), arma K con H, devuelve 12x12 en la terna del codo. La terna R (3x3) sale de (1)-(2) y se pasa a `matriz_T` / `rigidez_global` tal cual (misma convención de GDL).
2. `Barra` pasa a tener un tipo (`recta`/`codo`) y datos del codo (R, phi, C, ko, io). Las cargas de barra distribuidas (peso propio) en el codo necesitan cargas equivalentes por integración con las funciones de forma del arco (no son las del Hermite recto): lo más simple es resolver el peso del tramo con la F_JJ (carga distribuida sobre el arco integrada con el B de 2.3, fuerzas de empotramiento en I, y equilibrio para J) o aproximar con cargas nodales puntuales en I y J (ok si hay un nudo intermedio).
3. Esfuerzos internos: a lo largo del arco salen de equilibrio desde las fuerzas de extremo (traslado de la resultante con r x F) y se llevan a la terna (T, Nn, e3). Como M_res = sqrt(Mx^2+My^2+Mz^2) es invariante de terna, la verificación B31.1 se puede hacer sin elegir ejes.
4. Entrada CSV: bloque nuevo `CODOS` (o columna `tipo_elem=codo` en BARRAS). Propongo que el usuario cargue **el vértice (intersección de las tangentes), dirección de entrada, dirección de salida y R**, y que el programa calcule I y J: `I = V - R tan(phi/2) u1`, `J = V + R tan(phi/2) u2` (ver 7.2: la geometría del libro con I, J, K sobredetermina el problema).
5. Informe: anexo del elemento (matriz F, K, H, k, i, ko) + sección de verificaciones; visor: dibujar el arco como polilínea.
6. Valor: **alto** para tubos curvos y cañerías; los tests T1-T3 sirven para validarlo.

### 5.2 Pieza A2 - carga térmica y soportes (tipo A, extensión de `portico3d`) - dificultad 2, tamaño chico

Hoy `Material` tiene `alfa` pero **no se usa** (no hay cargas térmicas). Agregar bloque `TEMPERATURAS caso;barra;dT` (o T_oper y T_montaje):
- dilatación libre: homotecia respecto de I, desplazamiento relativo del nudo J = alfa dT (xJ - xI), sin giros. Carga equivalente nodal: `f_th = K_local u_th` con `u_th = [0 ; alfa dT * IJ ; 0]` (aplica igual a recta y codo; para recta da la conocida N = E A alfa dT) [mío, deducido].
- esfuerzos finales = K u - f_th. Para el codo vale lo mismo con el K del 5.1.
- Soportes: ya existen restricciones y `RESORTES` en ejes globales (sirve para soportes elásticos de carga variable). Faltan: (a) **resorte entre dos nudos** (junta de expansión, soporte biarticulado), (b) **apoyos inclinados/en dirección** (guías, topes), (c) **elemento rígido** (válvula, brida): con barra de rigidez 1e3-1e6 veces mayor o, mejor, eliminación por restricción maestro-esclavo para no empeorar el condicionamiento, (d) **carga constante** = fuerza nodal. Apoyos unilaterales y con fricción (patines, topes) son no lineales: no los da el libro, quedarían fuera de la primera versión.
- El libro (6c) menciona **pretensión por movimiento forzado de apoyos**: ya existe `PREFIJADOS`.

### 5.3 Pieza B - verificaciones ASME B31.1 (tipo B calculadora + postproceso) - dificultad 2, tamaño mediano

- **B1 calculadora de espesor** (autónoma, CSV -> HTML paso a paso): entradas P, D0, S(T), E, y, A, tolerancia 12,5 %; salidas tm, tn mínimo comercial (tabla Anexo 2), Pa y verificación (ec. (9)).
- **B2 postproceso sobre resultados del pórtico 3D**: el usuario asigna a cada caso/combinación una clase: `sostenida` / `ocasional` / `expansion`. Para cada barra o codo y cada sección (extremos y, en el codo, varias estaciones): calcular M_A, M_B, M_C por (16), SL por (10), (11), SE por (12) con SA por (13)-(15), mostrando relación SL/Sh, etc. Entradas CSV nuevas: `NORMA_B31_1` (P, D0 de cada sección, A, E, y, S_h, S_c, K, ciclos Nk con rango Sk) y `FACTORES_i` por barra (recta i=1; codo/te/reducción por Anexo 14).
- Rango MC: tomar el caso térmico (diferencia T_oper - T_montaje) como rango, o, si hay frío/caliente, combinar la diferencia de resultados.
- Salida: informe con tabla de utilización por elemento y la "peor sección" (similar al CS de `tensor.py`).

### 5.4 Pieza A3 (opcional, después) - T, mitrados, reducciones (tipo A) - dificultad 3, mediano

El libro dice armarlos con elementos conocidos y **condensación estática** de nudos interiores, pero no da la geometría ni la rigidez de la junta; solo los factores k e i (filas 2-7). Implementable como (i) mitrado: n tramos rectos cortos + nudos con k de fila 2/3 aplicado a la rigidez flexional del conjunto, (ii) T: solo i (k=1), y para la rama falta el módulo resistente efectivo (no está en el libro). Lo dejo para después de A1+B.

### 5.5 Dependencias

- Cap. 9 (vigas curvas y codos, secs. 5-6, ec. (29)-(41)): para ko, io, k_p, i_p y la formulación de energía de viga curva (permite también un codo "en forma cerrada").
- Cap. 12/13 (condensación estática, si está allí): para A3.
- Estructuras de `portico3d` ya existentes: `barra.py` (rigidez_local, terna_local, matriz_T), `solver.py`, `esfuerzos.py`, `tensor.py` (para tensión "real" Von Mises con io), `informe.py`.
- Cap. 16 (presión externa, recipientes): para tubos con presión externa.

### 5.6 Qué aplica a un fuselaje tubular soldado y a estructuras mecánicas generales

- **Fuselaje de avión ligero (tubos 4130 soldados):** B31.1 en sí **no aplica** (es de plantas de potencia; la aeronáutica usa otras normas/criterios: ver preguntas). Lo que sí aplica: (a) **elemento codo** para tubos doblados (jaula antivuelco, tren de aterrizaje, escapes, líneas de combustible/aceite/hidráulica); la ovalización puede hacer a un tubo curvo delgado ~3-4 veces más flexible (T7); (b) **dilatación térmica** (escape y cortafuego, diferencia de temperatura entre cabina y tubo, diferencia de coeficiente de dilatación entre tubos de acero y piel/herrajes de aluminio); (c) soportes elásticos y juntas de expansión en líneas de escape y combustible; (d) los factores i de tes soldadas como **indicador grosero** de concentración de tensiones en nudos soldados (no sustituyen a una verificación de fatiga/estática del nudo según otra norma). Las uniones con tubos soldados en el fuselaje (cluster) no están cubiertas por el libro.
- **Estructuras mecánicas generales:** cañerías de planta, intercambiadores, tuberías de aire comprimido; el modelo "caño + codos + rígidos + resortes + dilatación" es el 90 % del uso real.

### 5.7 Resumen de esfuerzo

| Pieza | Tipo | Dificultad (1-5) | Tamaño |
|---|---|---|---|
| A1 codo en portico3d (solver + tests) | A | 3 | mediano |
| A1 + informe + visor curvo | A | 4 | mediano |
| A2 cargas térmicas + resorte de dos nudos + apoyos con dirección + rígido | A | 2 | chico |
| B1 espesor por presión (ec. 9) | B | 1 | chico |
| B2 verificaciones (10)-(17) como postproceso | B | 2 | mediano |
| A3 T / mitrados / reducciones | A | 3 | mediano |
| Todo el paquete "cañerías" | - | 4 | grande |

---

## 6. Anexo teórico para los informes (con referencia al capítulo)

- Si se usa un elemento codo: geometría (1)-(3), matriz de equilibrio H (5), K por (6)-(7), factor de flexibilidad k (8) con h = tR/rm^2, la advertencia de que k solo ablanda la flexión; remitir a Cap. 15 sec. 4 (p. 261-262) y Cap. 9 sec. 5.
- Factores k e i del Anexo 14 (p. 281) y la corrección por presión (Nota 5).
- Verificaciones de B31.1: (9) espesor/presión; (10) sostenidas; (11) ocasionales con K; (12)-(15) rango, fatiga (f, N equivalente); (16)-(17) momentos resultantes y módulo resistente; remitir a Cap. 15 sec. 7 (pp. 264-266) y decir **qué versión de la norma** (no la edición exacta: el libro no la indica).
- Una nota explícita: "i (B31.1) es un factor de fatiga normalizado con la soldadura a tope; no es un factor de concentración de tensiones estático".
- Carga térmica: dilatación libre alfa dT, carga equivalente K u_th (esto lo deduje yo; no es del libro, citar como "deducción propia, ver informe").
- Metodología de análisis por etapas (sec. 6, p. 263-264) como lista de pasos.

---

## 7. Riesgos, ambigüedades e inconsistencias detectadas

### 7.1 Del libro

1. **Falta F_JJ.** El libro no da la matriz de flexibilidad del codo; solo el procedimiento (p. 262). Mi deducción (2.3) es una elección razonable (k solo en flexión), no una cita.
2. **Eq. (6) - signos.** El texto extraído muestra `K_IJ = [H] K_JJ` sin menos; en la imagen los signos menos están (K_IJ = -H K_JJ, K_JI = -K_JJ H^T). Quien copie del .txt se equivoca.
3. **Eq. (3) no verifica consistencia.** Con I, J, K dados y R dado, el centro C sale de (2) y phi de (3), pero nada fuerza a que |CJ| = R ni a que la tangente en J sea la del siguiente tramo; si el usuario da un J que no cae en la circunferencia, el elemento queda mal definido. Propongo definir el codo por el vértice (5.1.4) y chequear |CJ|-R. Si K=I (primer elemento, sin elemento previo) hay que pedir la tangente.
4. **Colineales.** Si K, I, J son colineales (codo de 0 grados) N3 = 0: caso degenerado.
5. **k Cap. 15 vs Cap. 9:** diferencia de ~4 % por el sqrt(1-nu^2) (el libro dice "levemente", correcto para k) pero **i difiere un factor ~2,3** (sec. 2.6), afirmación "levemente" falsa para i. Los límites de validez de las ecuaciones del Cap. 9 (0,05 <= lambda <= 1) no aparecen en Anexo 14. Con h > 1,65 sale k < 1 (viga más rígida que recta): B31.1 pide k >= 1 (conocimiento externo **[mío]**, contrastar).
6. **Fig. 13:** "R ~ 2 rm" corto, "R ~ 3 rm" largo. En el Anexo 6-a los radios normalizados son R = 1,5 DN (largo) y R = DN (corto) (a verificar contra la tabla); R/rm depende del caño. Para el cálculo conviene usar R real.
7. **Eq. (10)-(11):** el texto define tn y tr, pero usa tr (tn - A - tolerancia) tanto en P D0/(4 tr) como en W (17). La ambigüedad: ¿"tolerancia" es 12,5 % de tn o un valor absoluto? La ec. (9) (Pa) usa "(t - A)" sin decir si t ya descuenta la tolerancia. Mi lectura: tr = 0,875 tn - A. (B31.1 original usa tn en estas ecuaciones - **[mío]**; usar tr es conservador.)
8. **Eq. (12):** "MC momento efectivo definido en 7.4.4", pero 7.4.4 solo da la SRSS (16); no dice que MC es el **rango** (diferencia entre estados) ni qué módulo elástico usar (en B31.1 es el módulo en frío, Ec - no figura en el libro), ni distingue i en el plano / fuera del plano (B31.1 usa un solo i). Además (16) mete la torsión Mz dentro de la raíz y multiplica todo por i (conservador, pero no es lo que hacen otros códigos).
9. **Eq. (13):** da solo la forma "1,25 Sc + 1,25 Sh - SL" (válida si SL < Sh). B31.1 permite también "1,25 Sc + 0,25 Sh" (conocimiento externo); no está acá.
10. **Eq. (14)-(15):** (14) con 6/N^0,2 satura en f = 1 para N <= 7776 (B31.1 tabula N <= 7000 -> f=1; diferencia chica). (15) con SM = mayor rango: ok.
11. **Fig. 16-c / eq. (16):** los ejes de la T (x,y,z) no coinciden con "Mz = torsión": cada sección tiene sus ejes; en Struttura la torsión es el eje x local de la barra. Para la **rama** de la T falta la fórmula de módulo resistente efectivo (B31.1 la da, el libro no).
12. **Solo longitudinal.** El libro cubre presión (circunferencial, ec. (9)) y longitudinal (10)-(12); el efecto de fondo de la presión (Bourdon, fuerza de extremo cerrado) no se trata; B31.1 excluye la presión del rango SE.
13. **Anexo 6-c:** en la fila DN 1, el DE aparece 42,2 (debería 33,4); DN 10 aparece 273,3 (B16.9: 273,1). Verificado visualmente solo en el Anexo 2 y 6-a.
14. **Anexo 11:** SA-335 P1 (fila 8): 300 C = 105, 350 C = 108 (no monótono: parece error de tipeo). Verificado en la imagen. Fila 6, SA-333 Gr.1: 200-250 C = 108, 300 C = 107. No usar para P1 sin confirmar con ASME.
15. **Unidades:** Anexo 3/7 en bar (1 MPa = 10 bar), Anexo 11 en MPa; el resto en mm.
16. **No hay soportes con datos** (rigideces, fricción, huelgos); solo clasificación.
17. **Sin ejemplos** ni valores de comprobación (hoy no hay con qué validar contra el libro).

### 7.2 Para preguntarle al usuario (para decidir antes de implementar)

1. ¿Querés el codo solo para **tubos curvos de fuselaje** (jaula, escape) o también cañerías de planta con B31.1? Cambia mucho qué priorizar (A1+A2 vs B).
2. ¿Qué **norma/criterio** usaría para el fuselaje (CS-VLA/FAR 23, AC 43.13, texto de la cátedra)? B31.1 no es de uso aeronáutico.
3. ¿Qué **material** (SAE 4130, 1020?) y qué S/Sc/Sh adoptarías? No están en el Anexo 11.
4. ¿Tenés **ejemplos resueltos de la cátedra** o el programa ANSI (Fortran) para contrastar?
5. ¿Convención de **definición del codo**: por vértice + R (recomendada) o por I, J, K como el libro?
6. ¿Radio de curvatura: R real o R normalizado (largo 1,5 DN / corto DN)?
7. ¿Sistema de unidades de Struttura (N, mm, MPa)? Los anexos mezclan bar y MPa.
8. ¿Querés incluir **corte** en la flexibilidad (R/h < 3) o seguir la sugerencia del libro de despreciarlo (error < 2 %)?
9. ¿Presión: alcanza con verificar ec. (9)-(10), o querés el efecto de la presión sobre k e i (Nota 5)?
10. ¿Coeficiente de dilatación alfa constante o función de la temperatura (el libro no da tabla)?
