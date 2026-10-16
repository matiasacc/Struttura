# Capítulo 16 - Recipientes de presión (ASME BPVC Sec. VIII Div. 1)

Compendio de Cálculo Estructural II (UNC-FCEFyN, 2024). PDF págs. 282-327 (numeración del libro 16-1 a 16-46; página PDF = 281 + N del libro).
Convención de citas: `(ec. N, PDF p.XXX / 16-Y)`. Todas las fórmulas de este resumen fueron verificadas mirando la página como imagen (el texto extraído pierde los símbolos <, >, π, ≥ y los exponentes).

---

## 1. Qué resuelve el capítulo y para qué sirve

Es una introducción práctica al diseño de recipientes a presión según ASME VIII Div. 1 (presión > 0,1 MPa y en general < 20 MPa). Da: espesor mínimo (y presión admisible) de cuerpos cilíndricos/esféricos y de cabezales bajo presión interna y externa; refuerzo de aberturas por "áreas equivalentes"; eficiencia de juntas soldadas según tipo de unión y grado de radiografiado; presión de prueba hidráulica/neumática; tensiones por viento y peso en torres (recipientes verticales); y tensiones en recipientes horizontales sobre dos silletas (método de Zick). Los capítulos de sismo y de recipientes grandes de almacenaje quedan afuera.

Para diseño sirve como "paso a paso" del dimensionamiento de un tanque de aire, un recipiente de proceso o una torre: elegir material y E, calcular t, verificar aberturas, definir presión de prueba y verificar soportes. El libro es un **resumen**: no trae ejemplos numéricos y deriva muchas cosas a gráficos/tablas del código que no están reproducidos en forma numérica (ver sección 3).

---

## 2. Fórmulas y algoritmos clave

Notación del libro: S = tensión admisible del material a la temperatura de diseño [MPa]; E = eficiencia de junta (adimensional); P = presión de diseño [MPa]; R, R0 = radio interior/exterior; t = espesor; tr = espesor requerido; Pa = presión admisible. **R y R0 se toman sin sobreespesor por corrosión** (nota en PDF p.286 / 16-5): se resta la corrosión a t, y R es el radio corroído.

### 2.1 Presión de diseño y generalidades (PDF p.284-285)
```
P = max( 1,1·P0 ; P0 + 0,2 )   [MPa]                           (ec. 3, p.284)  (recomendación de bibliografía, no del código)
t_min (cuerpo y cabezales) >= 1,6 mm, sin contar corrosión      (3.2.3, p.285)
```
Cargas a considerar (UG-22, p.285): presión, peso (con agua de prueba), cargas estáticas, dinámicas, viento/nieve/hielo/sismo, térmicas, presiones anormales.

### 2.2 Presión interna - cuerpos (PDF p.285-286)
```
Cilindro, tensión circunferencial (domina):
  tr = P R /(S E - 0,6 P) = P R0 /(S E + 0,4 P)       Pa = S E t /(R + 0,6 t) = S E t /(R0 - 0,4 t)     (ec. 6)
  válida si t <= R/2  o  P <= 0,385 S E
Cilindro, tensión longitudinal (juntas circunferenciales):
  tr = P R /(2 S E + 0,4 P) = P R0 /(2 S E + 1,4 P)    Pa = 2 S E t /(R - 0,4 t) = 2 S E t /(R0 - 1,4 t)  (ec. 7)
  válida si t <= R/2  o  P <= 1,25 S E
Esfera:
  tr = P R /(2 S E - 0,2 P) = P R0 /(2 S E + 0,8 P)    Pa = 2 S E t /(R + 0,2 t) = 2 S E t /(R0 - 0,8 t)  (ec. 8)
```
Tensiones de pared delgada (ec. 4, 5): sigma_t = P R / t ; sigma_L = P R /(2 t). Se adopta el mayor tr entre (6) y (7), con la E que corresponda a cada tipo de junta (longitudinal -> Cat. A, circunferencial -> Cat. B).
Verifiqué algebraicamente que las formas con R0 son equivalentes a las de R (sustituyendo R = R0 - t).

### 2.3 Presión interna - cabezales (PDF p.286-289)
Notación: D = diámetro interior (eje mayor en elipsoidales); L = radio de conformado (crown); r = radio de transición (knuckle); alfa = semiángulo del cono; Di = diámetro interno de la parte cónica del toricónico.
```
Elipsoidal 2:1 (D/h = 4):   tr = P D /(2 S E - 0,2 P)         Pa = 2 S E t /(D + 0,2 t)            (ec. 9)
Torisférico ASME (r=0,06 L, L=D):  tr = 0,885 P L /(S E - 0,1 P)   Pa = S E t /(0,885 L + 0,1 t)    (ec. 10)   (t/L >= 0,002)
Hemisférico:                tr = P L /(2 S E - 0,2 P)         Pa = 2 S E t /(L + 0,2 t)            (ec. 11)   (t <= 0,356 L  o  P <= 0,665 S E)
Cono / cabezal cónico (alfa <= 30°, sin transición):
                            tr = P D /(2 cos(alfa) (S E - 0,6 P))                                   (ec. 12)
Toricónico: parte cónica con (12) usando Di en lugar de D si r >= 6 % del diámetro exterior de la falda y r >= 3 t; la zona de transición se calcula en los apéndices obligatorios (no está en el libro).
Plano soldado:              tr = d sqrt( C P /(S E) )                                              (ec. 13)
Plano abulonado (Fig. 7 j,k): tr = d sqrt( C P /(S E) + 1,9 W hG /(S E d^3) )                       (ec. 14)
```
C sale de la Fig. 7 (FIG. UG-34), p.288 / 16-7. **Valores de C leídos de la figura**: a) 0,17 ó 0,10; b-1) 0,17; b-2) 0,33(tr/ts) con Cmin=0,2; c) 0,3 (también figuran 0,2 ó 0,13); d) 0,13; e,f,g) 0,33(tr/ts) con Cmin=0,2; h) 0,33; i) 0,33(tr/ts) con Cmin=0,2; j,k) 0,3; m,n,o) 0,30; p) 0,25; q) 0,75; r) 0,33; s) 0,33. Condición de geometría de cada croquis (radio r >= 3t, ts >= 2 tr, etc.) está en el dibujo. Cuando hay dos valores posibles de C rige UG-34(d) (no reproducido).

### 2.4 Presión externa (PDF p.289-291)
**Tensión de compresión admisible (axial) en cilindro/esfera**, subsección 3.1.1-b, ec. (1), (2), PDF p.284:
```
A = t /(8 R0)  (= 0,125 /(R0/t));   B = f(A, T) de la carta del material (Anexo 4);  S_comp = min(S, B)
si A cae a la izquierda de la curva de T:  B = A E / 2                                                   (ec. 2)
si A cae a la derecha:  se toma el B máximo (extremo derecho) de la curva de T
```
**Cilindro con presión externa, D0/t >= 10** (PDF p.290-291):
```
1) proponer t; 2) proponer anillos -> L (distancia entre líneas de soporte); 3) L/D0 y D0/t
4) Fig. G (Anexo 5): con L/D0 (ordenadas) y la curva D0/t (interpolando en escala log) -> A (abscisa)
5) carta del material (Anexo 4) con A y T -> B [MPa]
   Pa = 4 B /(3 (D0/t))                                                                               (ec. 15)
   si A queda a la izquierda de la curva:  Pa = 2 A E /(3 (D0/t))                                     (ec. 16)   [sale de (15) con B = A E/2]
6) si Pa < P externa requerida: aumentar t y/o agregar anillos (reducir L)
```
D0/t < 10: se remite a UG-28(c)(2), no desarrollado. Anillos de refuerzo: UG-29 y UG-30, no desarrollado. Líneas de soporte válidas (Fig. 10 = FIG. UG-28.1, p.290): a 1/3 de la profundidad del cabezal, anillos, camisas, uniones cono-cilindro cuando el momento de inercia cumple el punto 1-8.

**Esfera o cabezal hemisférico** (PDF p.291):
```
A = t /(8 R0)                                       (ec. 17)
Pa = B /(R0/t)                                      (ec. 18)
si A < Ao (izquierda de la curva):  Pa = 0,0625 E /(R0/t)^2    (ec. 19)  <-- el libro imprime sin el cuadrado, ver sección 7
```
**Cabezales 2:1 elípticos y torisféricos** (p.291): el espesor es el mayor entre (a) el de presión interna (ecs. 9 / 10) con P_int = 1,67 P_ext y E = 1, y (b) el de (17)-(18) con R0 = 0,9 (D + 2t) para elíptico 2:1 y R0 = L para torisférico.

### 2.5 Aberturas y refuerzos (PDF p.292-295; Fig. 11 p.293, Fig. 12 p.294, Fig. 13 p.295)
Método de áreas equivalentes (solo presión interna; para externa AR = 50 % del de interna con tr debido a la presión externa). No cuenta el sobreespesor de corrosión.
```
AR = d tr F + 2 tn tr F (1 - fr1)                                         (ec. 20)
F  = 0,5 (1 + cos^2 theta)    (theta = ángulo del plano respecto al eje del recipiente; F=1 en el plano longitudinal; F=0,5 a 90°)   (Fig. 12)
fr1 = min(1 ; Sn/Sv) si la derivación atraviesa la pared; fr1 = 1 si no atraviesa
fr2 = Sn/Sv ;  fr3 = min(Sn;Sp)/Sv ;  fr4 = Sp/Sv     (ninguno > 1)
```
Áreas disponibles (Fig. 11, p.293; E1 = 1 si la abertura está en chapa sólida o atraviesa una junta Cat. B; el libro no define E1 explícitamente, ver sección 7):
```
A1 = mayor de { d (E1 t - F tr) - 2 tn (E1 t - F tr)(1 - fr1) ;  2 (t + tn)(E1 t - F tr) - 2 tn (E1 t - F tr)(1 - fr1) }
Sin placa de refuerzo:
  A2 = 5 tau (tn - trn) fr2,   tau = min(t ; tn)
  A3 = tau ti fr2,             tau = min(5t ; 5ti ; 2h)           (parte interna de la derivación)
  A41 = (c41)^2 fr2 ;  A43 = (c43)^2 fr2                           (soldaduras)
  AD = A1 + A2 + A3 + A41 + A43 >= AR  -> no necesita refuerzo   (ec. 21)
Con placa de refuerzo (poncho):
  A2 = tau (tn - trn) fr2,     tau = min(5t ; 5tn + 2 te)
  A41 = (c41)^2 fr3 ; A42 = (c42)^2 fr4 ; A43 = (c43)^2 fr2
  A5 = (Dp - d - 2 tn) te fr4
  AD = A1 + A2 + A3 + A41 + A42 + A43 + A5 >= AR                  (ec. 22)
```
Zona válida (ec. 23, 24, Fig. 13, p.295): H = max{ d ; Rn + tn + t } (paralelo al eje); V1 = min{ 2,5 t ; 2,5 tn + te } (hacia afuera); V2 = min{ h ; 2,5 t ; 2,5 ti } (hacia adentro).
Espesor de la derivación: trn por ec. (6) con su propio radio y su S, E. Sin refuerzo si apertura <= 90 mm (tr <= 10 mm) o <= 60 mm (tr > 10 mm) (3.5.3, p.292). Límites de tamaño: D_int <= 1500 mm -> abertura <= D/2 y <= 500 mm; D_int > 1500 mm -> <= D/3 y <= 1000 mm (3.5.2).
Nota de signo/uso: Nota (1) de la Fig. 11: considerar las áreas A2/A3 con Sn/Sv < 1 a ambos lados del eje.

### 2.6 Soldaduras, categorías y eficiencia de junta (PDF p.295-297, Anexos 6-11)
- Categorías A, B, C, D = **ubicación** de la junta (Fig. 15, p.296). A: longitudinales en cuerpo, cabezales hemisféricos, esferas; B: circunferenciales de cuerpo y de cabezales no hemisféricos; C: bridas, placas y cabezales planos; D: derivaciones.
- 8 tipos de unión (Fig. 16, p.297): 1 a tope doble arco; 2 simple arco con respaldo; 3 simple arco sin respaldo; 4 filete doble solape; 5 simple solape con plug; 6 simple solape sin plug; 7 esquina; 8 en ángulo.
- **E máximo (Tabla UW-12, Anexo 6, PDF p.316)** por tipo y radiografiado (a total / b parcial / c nada):

| Tipo | Categorías | Total | Parcial | Nada |
|---|---|---|---|---|
| 1 | A,B,C,D | 1,0 | 0,85 | 0,70 |
| 2 | A,B,C,D | 0,9 | 0,80 | 0,65 |
| 3 | A,B,C | NA | NA | 0,60 |
| 4 | A (long. t<=10 mm), B,C (circ. t<=16 mm) | NA | NA | 0,55 |
| 5 | B, C | NA | NA | 0,50 |
| 6 | A,B | NA | NA | 0,45 |
| 7, 8 | C,D / B,C,D | NA | NA | NA (ver notas UW-12) |

- Juntas a tope en **compresión**: E = 1 (ec. 25, p.297).
- En cabezales hemisféricos se usa la menor E de las juntas del cabezal **incluyendo la unión con el cuerpo**; en el resto, solo las del cabezal (Anexo 8).
- Radiografiado total obligatorio: letal, vapor (calderas), UCS-57 (Anexo 7, espesor mínimo por material), etc. Los flujogramas de los Anexos 8-11 (extracto del Apéndice L) deciden E y tipo de junta.

### 2.7 Pruebas de presión (PDF p.297-298)
```
Hidrostática (mínima):  Pp = 1,3 MAWP (Sp/S)        (ec. 26)    Sp = S a la temperatura de prueba, S = S a la temperatura de diseño
Neumática (excepción):  Pp = 1,1 MAWP (Sp/S)        (ec. 27)
MAWP = máxima presión de trabajo admisible en el punto superior (UG-98); en general MAWP = P de diseño.
```
Neumática permitida si el recipiente/soportes no resisten el agua o no puede secarse.

### 2.8 Recipientes verticales / torres (PDF p.298-301)
Etapas a analizar: traslado, montaje, prueba, operación, errores de operación, desmontaje. En traslado/montaje/desmontaje **no** va presión de operación. Viento y sismo no actúan juntos (UG-23(d)) y en esas combinaciones la tensión admisible se aumenta 20 %.
```
Fuerza de viento por tramo (CIRSOC 102):   Fi = qz G Cf Afi            [N]                 (ec. 28)
Presión dinámica:                          qz = 0,613 Kz Kzt Kd V^2 I  [N/m2, V en m/s]    (ec. 29)
Factor topográfico:                        Kzt = (1 + K1 K2 K3)^2                          (ec. 30)
G = 0,85 (estructura rígida, f >= 1 Hz); Kd = 0,95; I = 1,15 (para recipientes en altura); Cf: Anexo 12; Kz: Anexo 13
Tensión de flexión por viento en la sección a altura zs:
   SV = ± Σ_i Fi (zi - zs) / (π Rm^2 t)                                                    (ec. 31)
Tensión axial por peso:   SP = (Wc + Wr) /(2 π Rm t)    (compresión)                       (ec. 32)
Combinación y verificación:  sigma* = S_presión + S_peso + S_viento + S_sismo + ... <= S E  (ec. 33)
```
Las tensiones tangenciales y longitudinales se suman por separado. En compresión la admisible es min(S, B) con E = 1 (3.1.1-b). Sismo: se limita a decir que se aplica INPRES-CIRSOC 103 y que se compone con el resto; **no se desarrolla**.

### 2.9 Recipientes horizontales sobre dos silletas - método de Zick (PDF p.301-307, Anexos 17-18)
Q = carga sobre cada silleta (2Q = peso total, lleno de fluido de operación o de agua de prueba, el mayor). Geometría: L = longitud del cuerpo cilíndrico, A = distancia del centro de la silleta a la unión cuerpo/cabezal, H = altura del cabezal, Rm = radio medio, t = espesor, b = ancho de silleta, theta = ángulo de contacto (120° a 180°; ASME recomienda >= 120°). Ubicación óptima para recipientes largos: a = 0,207 ℓ (a ≈ A + 2H/3, ℓ ≈ L + 4H/3, ec. en p.303 / Fig. 22); voladizo a <= 0,2 ℓ.
```
Flexión longitudinal en el plano de la silleta:
  S1 = ± (Q A /(K* Rm^2 t)) [ 1 - (1 - A/L + (Rm^2 - H^2)/(2 A L)) / (1 + 4H/(3L)) ]              (ec. 34)
    K* = π  (con anillos en el plano de la silleta y A > Rm/2, o sin anillos y A < Rm/2)
    K* = K1 (parte superior, tracción, resto de casos) ; K* = K7 (parte inferior, compresión, solo si t/Rm < 0,005; si t/Rm >= 0,005 no se verifica S1 en compresión)
  Tracción:     sigma* = S1 + SL <= S E,   SL = P (R0/(2t) - 0,7) = P (R/(2t) - 0,2)                  (ec. 35, 36)
  Compresión:   E = 1;  |S1| <= SC (SC de 3.1.1-b); caso crítico: lleno y a presión atmosférica      (ec. 37)
Flexión longitudinal en el plano medio:
  S1 = ± (Q L /(4 π Rm^2 t)) [ (1 + 2 (Rm^2 - H^2)/L^2)/(1 + 4H/(3L)) - 4A/L ]                    (ec. 38)
Corte:
  A > Rm/2:  S2 = (K̄ Q /(Rm t)) (L - 2A)/(L + 4H/3),  K̄ = 1/π con anillos en el plano de la silleta, K̄ = K2 si no  (ec. 39)
  A < Rm/2:  S2 = K3 Q /(Rm t)                                                                      (ec. 40)
  Criterio:  S2 <= 0,8 S                                                                            (ec. 41)
Circunferencial en el cuerno de la silleta (sin anillo):
  S3 = - Q /(4 t (b + 1,56 sqrt(Rm t))) - 3 K6 Q /(2 t^2)         si L >= 8 Rm                       (ec. 42a)
  S3 = - Q /(4 t (b + 1,56 sqrt(Rm t))) - 12 K6 Q Rm /(L t^2)     si L <  8 Rm                       (ec. 42b)
  Criterio:  |S3| <= 1,5 S                                                                          (ec. 43)
Circunferencial en el fondo (con o sin anillo):
  S3 = - K5 Q /(t (b + 1,56 sqrt(Rm t)))                                                            (ec. 44)
  Criterio:  |S3| <= 0,5 Sy                                                                         (ec. 45)
Con placa de apoyo (poncho) de espesor tp: usar t + tp y t^2 -> t^2 + tp^2 (en corte y circunferencial).
```
Los coeficientes K1...K9 (Anexo 17) y K6 (Anexo 18) están en la sección 3. El término 1,56 sqrt(Rm t) es la corrección de Bleich (ancho colaborante); se menciona que el cuerpo actúa como viga curva (Cap. 9, ec. 28). Los anillos de refuerzo (5.4, p.308) no se calculan: el libro remite a bibliografía (K4, K8 y K9 de la tabla serían para anillos y no se usan en el texto).

---

## 3. Datos tabulados, gráficos y curvas a cargar

Marco: lo que "está en el libro" puede transcribirse directo; lo que es solo gráfico habría que digitalizarlo o conseguir la tabla numérica de ASME Sec. II Parte D.

| Dato | Dónde | Cantidad de valores | ¿Fórmula alternativa en el libro? |
|---|---|---|---|
| Tabla UW-12 (E por tipo de junta/radiografiado) | Anexo 6, PDF 316 | 8 tipos x 3 columnas (+ categorías y limitaciones) | no, es tabla |
| Tabla UCS-57 (espesor mínimo para RT total) | Anexo 7, PDF 317 | 10 filas | no |
| Flujogramas de E (cabezal, cuerpo, Cat. A/D, Cat. B/C) | Anexos 8-11, PDF 317-320 | 4 diagramas de decisión (lógica ~30 nodos) | no; se pueden codificar como función |
| Tabla 1A extracto (S vs T) | Anexo 2, PDF 310-311 | 25 renglones x 19 temperaturas (-30 a 40, 65, 100, 125, 150, 200, 250, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575 °C) + Sy, Su, límites de uso, tipo/grado; muchas celdas "..." | no |
| Resumen de materiales usados en Argentina (S vs T) | Anexo 3, PDF 312 | 21 renglones x 13 temperaturas (-30/40, 65, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600 °C); SA-283C, SA-285C, SA-515 60/65/70, SA-516 55/60/65/70, SA-234 WPB, SA-105, SA-181-60, SA-350 LF1/LF2, SA-53 E/B, SA-106 B, SA-193 B7, SA-194 H2, SA-307 B, SA-36 | no |
| Lista UCS-23 (materiales válidos) | Anexo 1, PDF 309 | lista de especificaciones (sin valores) | no |
| Carta CS-1 (B vs A, acero C/baja aleación Sy < 207 MPa) | Anexo 4, PDF 313 | 5 curvas de T (hasta 150, 260, 370, 425, 480 °C) + 5 rectas elásticas (E = 200, 186, 169, 157, 143 GPa); **el libro remite a "Tabla CS-1" que no está** | tramo elástico: B = A E/2 (ec. 2) |
| Carta CS-2 (Sy >= 207 MPa) | Anexo 4, PDF 313 | igual que CS-1 | ídem |
| Cartas HA-1 (304) y HA-2 (316) | Anexo 4, PDF 314 | 6 curvas (hasta 40, 205, 370, 480, 650, 815 °C) + 6 rectas elásticas (E = 193, 179, 164, 154, 140, 125 GPa); tablas HA-1/HA-2 no incluidas | ídem |
| Fig. G (A vs L/D0 y D0/t) | Anexo 5, PDF 315 | ~24 curvas de D0/t (4 a 1000), L/D0 de 0,05 a 50, A de 1e-5 a 0,1; "Tabla G" no incluida | **no** en el libro (ver nota de abajo) |
| Fig. 7 / FIG. UG-34 (valores de C) | PDF 288 | ~20 croquis con su C | no; ver lista en 2.3 |
| Cf para torres (Tabla 10 CIRSOC 102) | Anexo 12, PDF 321 | sección circular: 3 filas de rugosidad x 3 valores de h/D (1, 7, 25) + cuadrada/hexagonal; criterio D·sqrt(qz) > 5,3 ó <= 5,3 | interpolación lineal en h/D (nota 2) |
| Kz (Tabla 5 CIRSOC 102) | Anexo 13, PDF 322 | 22 alturas (0-5 m a 150 m) x 6 columnas (A caso 1/2, B caso 1/2, C, D) | sí: Kz = 2,01 (z/zg)^(2/alfa) para z >= 5 m y 2,01 (5/zg)^(2/alfa) para z < 5 m; alfa y zg están en la Tabla 4 del CIRSOC **que no está en el libro** |
| Kzt: multiplicadores K1, K2, K3 | Anexo 14, PDF 323 | 3 tablas (K1 vs H/Lh: 7 filas x 3 cols; K2 vs x/Lh: 9 filas x 2 cols; K3 vs z/Lh: 12 filas x 3 cols), solo exposición C | no |
| Velocidad básica V (mapa) | Anexo 15, PDF 324 | solo mapa de contornos | no; V se ingresa a mano |
| Zonificación sísmica | Anexo 16, PDF 325 | solo mapa | no se usa en el capítulo |
| Factores de Zick K1...K9 vs theta | Anexo 17, PDF 326 | 31 filas (theta = 120° a 180° cada 2°) x 8 columnas (K1,K2,K3,K4,K5,K7,K8,K9) = 248 valores | **sí**: polinomios de 2º grado en theta_bar = theta/1000 (ver abajo) |
| K6 (Zick, cuerno) | Anexo 18, PDF 327, Fig. 26 | gráfico con 7 curvas (theta 120° a 180°, paso 10°) | **sí**: fórmula analítica por tramos (ver abajo) |

**Polinomios de Anexo 17 (PDF 326)** con theta_bar = theta[grados]/1000:
```
K1 = 0,3588 θ̄ + 20,1 θ̄²              K5 = 1,48 - 8,53 θ̄ + 21 θ̄²
K2 = 4,121 - 34,6 θ̄ + 83 θ̄²          K7 = 1,91 θ̄ + 26 θ̄²
K3 = 4,113 - 38,26 θ̄ + 93,8 θ̄²       K8 = 0,323 + 1,244 θ̄ - 9,14 θ̄²
K4 = 1,083 - 7,44 θ̄ + 14,6 θ̄²        K9 = 0,2 - 1,66 θ̄ + 3,6 θ̄²
```
Verificación que hice contra la tabla de 31 filas (error máximo respecto de la tabla): K1 ~0,003, K2 0,007, K3 0,0075, K4 0,0013, K5 0,0012, K7 0,006, K8 0,0008, K9 0,00016. Alcanza para uso de diseño; para tests de regresión conviene interpolar la tabla.
**K6 (Anexo 18, PDF 327)**, x = A/Rm:
```
a = 0,0513 - 0,44 θ̄ + θ̄² ;  b = 0,2135 - 1,843 θ̄ + 4,2 θ̄² ;  c = 0,2697 - 2,33 θ̄ + 5,3 θ̄²
K6 = a                          x <= 0,4
   = a + 5 c (x - 0,4)^2        0,4 < x < 0,5
   = a + c (x - 0,45)           0,5 <= x <= 1,0
   = b - 5 c (1,1 - x)^2        1,0 < x < 1,1
   = b                          x >= 1,1
```
Chequeé continuidad en x = 0,5 y x = 1,0 (coinciden) y que a(120°) = 0,0129, a(180°) = 0,0045, b(120°) = 0,0528, b(180°) = 0,0178, igual que los valores marcados en el gráfico.

**Nota sobre Fig. G**: el libro no da la expresión. En la zona elástica las curvas siguen formas cerradas (de memoria, **no del libro; verificar contra la Tabla G de Sec. II-D antes de usar**): A ≈ 1,3 (t/D0)^1,5 /(L/D0) para cilindros de longitud intermedia y A ≈ 1,1 (t/D0)^2 para cilindros largos (L/D0 >= 50). Con eso se podría evitar digitalizar la figura salvo en el tramo plástico, que sí requiere tabla.

**Tablas ASME que NO están en el libro y que hay que conseguir** (Sec. II Parte D, Sec. VIII-1): Tablas numéricas CS-1, CS-2, HA-1, HA-2 y G (Subparte 3); Tabla 1A completa (Subparte 1) para otros materiales (inoxidables SA-240 304/316, SA-179/SA-192 tubos, etc.); Tabla TM-1/TM-2 (E vs T); UG-28(c)(2) (cilindros de pared gruesa); UG-29/30 (anillos); UG-32(e) general (torisférico con factor M); UG-36/37/40 detalle; UW-11/UW-12(d); Apéndice L; Tabla 4 de CIRSOC 102 (alfa, zg); CIRSOC 103 completo (sismo).

---

## 4. Ejemplos resueltos del texto

**El capítulo no trae ningún ejemplo numérico resuelto** (confirmado: la palabra "ejemplo" no aparece con ese sentido en las 46 páginas; solo hay figuras con mapas de tensiones por elementos finitos sin valores, p.287 y p.307). No hay datos de entrada/salida para validar contra el libro.

Como alternativa, dejo **casos de prueba calculados por mí a partir de las fórmulas del capítulo** (NO provienen del libro; sirven como regresión interna y deben contrastarse con otra fuente, por ejemplo una planilla del cátedra o PV Elite). Unidades N, mm, MPa.

| Caso | Entradas | Resultado calculado |
|---|---|---|
| T1 cilindro presión interna | P=1,0; R=500; S=138 (SA-516-70, T<=250 °C); E=0,85 | tr(6)=4,2845 mm; tr(7)=2,1277 mm (rige 6). Pa para t=10: 2,3182 MPa |
| T2 cabezales (mismos datos, D=1000, L=D, E=0,85) | | elipsoidal 2:1 tr=4,2662 mm; torisférico ASME tr=7,5512 mm; hemisférico tr=2,1331 mm (con L=500). Pa elipsoidal t=10: 2,3413 MPa; Pa esfera t=10: 4,6733 MPa |
| T3 cono | P=1,0; D=1000; alfa=30°; S=138; E=0,85 | tr(12)=4,9473 mm. Comprobación de consistencia de Pa: ver sección 7 (el Pa impreso en el libro no devuelve P) |
| T4 tapa plana soldada | d=500; C=0,33; P=1,0; S=138; E=0,85 | tr(13)=26,52 mm (con E=1 daría 24,45 mm) |
| T5 esfera presión externa (rama elástica) | R0=3000; t=5; E=200000 MPa | A=t/(8R0)=2,083e-4; B=AE/2=20,83 MPa; Pa(18)=B/(R0/t)=0,03472 MPa; igual con (19) corregida 0,0625E/(R0/t)^2 |
| T6 cilindro presión externa (rama elástica) | D0/t=300; A=1e-4; E=200000 | Pa(16)=2AE/(3 D0/t)=0,04444 MPa |
| T7 refuerzo de abertura sin placa | cuerpo R=500, t=12, P=1, S=138, E=1 (tr=3,639); derivación d=200, Rn=100, tn=8, trn=0,728, fr=1, c41=6 | AR=727,8 mm²; A1=1672,2; A2=290,9; A41=36 -> AD=1999,1 mm² >= AR: no requiere refuerzo |
| T8 Zick (K de la tabla) | Q=150000 N; Rm=1000; t=10; L=8000; H=500; A=800; b=250; theta=120°; sin anillos ni placa | f=0,11514; S1 silleta (K1=0,335)=4,13 MPa; S1 con K*=π=0,44 MPa; S1 plano medio=5,20 MPa; S2 (K2=1,171)=12,97 MPa; K6(x=0,8)=0,0361; S3 cuerno(L=8Rm, 42a)=-90,6 MPa; S3 fondo (K5=0,760)=-28,1 MPa |
| T9 viento | V=45 m/s; Kz=1,00 (exposición C, z=10 m); Kzt=1; Kd=0,95; I=1,15 | qz=1356,1 N/m²; para D=1 m, tramo de 5 m, Cf=0,5667 (interp. h/D=5, "moderadamente suave"), G=0,85: Fi=3266 N |

---

## 5. Propuesta de implementación en Struttura

**Tipo B** (calculadora paso a paso: CSV de entrada -> informe HTML), no es un solver matricial. Paquete nuevo `struttura/recipientes/` con submódulos independientes y un CSV por bloques como los otros programas (`PROYECTO` con `tipo;recipiente`):

| Módulo | Entradas del CSV | Salidas | Dificultad | Tiempo | Dependencias |
|---|---|---|---|---|---|
| B1 Espesores a presión interna (cuerpo cilíndrico, esfera, cabezales 2:1, torisférico, hemisférico, cono, planos) + prueba hidráulica/neumática + MAWP | bloque MATERIAL (S(T) o código del Anexo 3), CORROSION, CUERPOS (tipo, D, L, E, tipo de junta, radiografiado), CABEZALES (tipo, parámetros), PRESION (P0, T, P de prueba) | tr, t adoptado, Pa/MAWP, Pp, tabla de verificación | 2 | mediana | tablas de materiales (Anexo 3) y UW-12 |
| B2 Eficiencia de junta E | tipo de unión, categoría, grado de RT, sin costura | E con la cadena de decisión (UW-12 + flujogramas Anexos 8-11) | 3 (ambigüedad en flujogramas, ver sec. 7) | chica-mediana | Anexos 6-11 |
| B3 Presión externa | D0, t, L (o anillos), T, material | A, B, Pa, ¿cumple? y t mínimo | 4 (depende de cartas) | mediana-grande (digitalizar Fig. G y CS-1/2, o conseguir tablas de Sec. II-D) | tablas CS/HA/G no incluidas |
| B4 Aberturas y refuerzos | cuerpo (R, t, tr, E1), derivación (d, tn, trn, Sn, h, ti), placa (Dp, te, Sp), soldaduras c41/c42/c43, ángulo theta | AR, A1, A2, A3, A41-A43, A5, AD, zona válida, cumple/no | 2-3 | mediana | B1 (tr y trn) |
| B5 Torres: viento + peso (+ presión) | geometría por tramos (D, t, h), V, exposición, Kzt, G, pesos Wr/Wc, presión | qz(z), Fi, M(z), SV, SP, sigma* por sección y combinación, verificación con 1,2 S en viento | 3 | mediana-grande | B1, tablas Anexos 12-14; sismo fuera de alcance |
| B6 Horizontal sobre silletas (Zick) | Rm, t, L, H, A, b, theta, Q (o pesos), anillos sí/no, placa tp, S, Sy, P | S1 (silleta, medio), S2, S3 (cuerno, fondo), verificaciones 35, 37, 41, 43, 45 | 2 | chica-mediana (las fórmulas son cerradas y las K se calculan con polinomios) | B1; K1-K9 |

**Conexión con lo existente.**
- Reutilizar `visor_comun.py` / el estilo de informe HTML con matrices y paso a paso, y el despachador (`tipo;recipiente`).
- B5: las cargas Fi se pueden aplicar como cargas nodales en un modelo de columna del **pórtico plano** (secciones tubulares variables) para obtener M(z) y compararlo con la suma de la ec. (31): es una validación gratuita del solver existente. Ídem para el momento en el centro y en las silletas de B6: un modelo de viga con dos apoyos y voladizos da M1 y M2, a comparar con las ec. (34)/(38) (que además incluyen la corrección por cabezales).
- Zick y el viento dan tensiones longitudinales/tangenciales y de corte en puntos: se pueden pasar al módulo de tensor/círculo de Mohr del pórtico 3D (criterios Von Mises/Tresca/Rankine) como complemento de la regla de "suma de tensiones" del libro.

**Parte aplicable al fuselaje tubular soldado de avión ligero** (valor bajo-medio):
- Un fuselaje de tubos de pared delgada **no es** un recipiente a presión; B1/B4/B6 no aplican directamente. Lo que sí sirve:
  - La eficiencia de junta como idea para juntas soldadas (en el libro es un factor E de recipientes; no es criterio aeronáutico).
  - La tensión admisible de compresión de cilindros delgados (ec. 1-2, carta B-A) como chequeo conservador de **pandeo local** de un tubo. Con tubos usuales (D0/t entre 20 y 60) sale muy conservador respecto de criterios aeronáuticos (p.ej. Gerard / MIL-HDBK-5); habría que presentarlo como una verificación de cota, con aviso.
  - Si el avión lleva un tanque de combustible o un recipiente de oxígeno/aire comprimido (distinto del fuselaje), B1, B4 y B6 son directamente aplicables a ese componente.
- Para estructuras mecánicas generales (tanques de aire comprimido, depósitos con silletas, columnas altas al viento): aplican B1-B6.

**Orden sugerido (valor/costo):** B1+B2 (base y tablas) -> B6 (Zick, fórmulas cerradas) -> B4 (aberturas) -> B5 (torre) -> B3 (presión externa, cuando se consigan las tablas CS/G).

Dependencias de otros capítulos: Cap. 9 (viga curva, ec. 28, citada en la justificación del término de Bleich, 5.3.1); criterios de falla (Tresca/Von Mises, ya implementados) para eventualmente complementar la regla de la suma de tensiones. No depende de los capítulos matriciales.

---

## 6. Anexo teórico para los informes (referencias al capítulo, sin copiar texto)

Incluir, citando "Compendio Cap. 16":
1. Tensiones de pared delgada: sigma_t = P R/t, sigma_L = P R/(2t) (ec. 4, 5).
2. Espesor por tensión circunferencial y longitudinal con E: tr = P R/(S E - 0,6 P) y tr = P R/(2 S E + 0,4 P) (ec. 6, 7); esfera (ec. 8); los cabezales con sus coeficientes 2 S E - 0,2 P, 0,885, etc. (ec. 9-12).
3. Presión de diseño recomendada P = max(1,1 P0; P0 + 0,2) (ec. 3) y espesor mínimo 1,6 mm + corrosión.
4. Presión externa: A = t/(8 R0), B de la carta, Pa = 4B/(3 D0/t); rama elástica B = A E/2 (ec. 1, 2, 15, 16).
5. Áreas equivalentes: AR = d tr F + 2 tn tr F (1 - fr1), condición AD >= AR y zona válida (ec. 20-24).
6. Tabla UW-12 de eficiencias y la regla E = 1 en compresión (ec. 25).
7. Prueba hidrostática Pp = 1,3 MAWP (Sp/S) (ec. 26).
8. Torre: Fi = qz G Cf Af, qz = 0,613 Kz Kzt Kd V^2 I, SV = M/(π Rm^2 t), SP = W/(2π Rm t), sigma* <= S E, con +20 % por viento/sismo (ec. 28-33).
9. Silletas (Zick): fórmulas S1 (silleta y plano medio), S2, S3 y los criterios de aceptación 0,8 S, 1,5 S, 0,5 Sy (ec. 34-45), indicando que el método es empírico (Zick) y los K dependen de theta.
10. Advertencia explícita: el módulo es una verificación didáctica según un resumen del código ASME VIII-1; no reemplaza el código vigente ni una certificación.

---

## 7. Riesgos, inconsistencias y preguntas para el usuario

**Errores/inconsistencias detectados en el libro (verificados con la imagen de la página):**
1. **Ec. (19), PDF p.291 / 16-10**: imprime `Pa = 0,0625 E /(R0/t)`; debe llevar el cuadrado `Pa = 0,0625 E/(R0/t)^2`. Se deduce de (2), (17) y (18): Pa = B/(R0/t) con B = A E/2 y A = t/(8R0) -> 0,0625 E (t/R0)^2. Con R0=3000, t=5, E=200000 la versión impresa da 0,0625*200000/600 = 20,8 MPa (absurdo) y la corregida 0,0347 MPa.
2. **Ec. (12), PDF p.287 / 16-6**: la presión admisible del cono se imprime `Pa = 2 S E t /(D + 1,2 t cos α)`; despejando de tr = P D/(2 cos α (S E - 0,6 P)) resulta `Pa = 2 S E t cos α /(D + 1,2 t cos α)` (falta cos α en el numerador). Con t = tr el valor impreso no devuelve P (da 1,16 para P=1), el corregido sí.
3. **Ec. (9), PDF p.286 / 16-5**: la condición "t/L >= 0,002" aparece junto a D/h=4 en el elíptico, pero L (radio de conformado) no existe en un elipsoidal 2:1; esa condición es del torisférico. Tratarla como errata y no exigirla (o preguntar).
4. **Ec. (40), PDF p.306**: define Rm como "radio externo", mientras que en todo el resto de Zick Rm es radio medio. Hay que decidir con una referencia (probablemente radio medio).
5. **Símbolos A1/A2/Ao/A'**: en 3.1.1-b se usan A1 y A2 para los extremos de la curva; en 3.4.1 son A', Ao. Mismo concepto, rótulos distintos (p.284 y p.291).
6. **E1 en Fig. 11 / ec. A1 (p.293)** no se define; sólo se define E (p.294). Habría que fijar la regla: E1 = 1 si la abertura está en chapa sin costura o atraviesa una junta Cat. B; si no, E de la junta (según UG-37). El libro dice que para aberturas "en zonas sin soldadura o con soldadura Categoría B, E = 1".
7. **Zona válida H (Fig. 13, p.295)**: no queda claro en el texto si H es el ancho total o la distancia medida a cada lado del eje de la abertura; en el código es a cada lado del eje.
8. **Referencia cruzada errónea**: 3.4.2 (p.291) remite a "la Sección 3.1.1" para el procedimiento del cilindro; es 3.4.1. 3.1.1-b usa "A = t/(8R0)" y 3.4.1 el A de la Fig. G: son dos A distintos.
9. **Flujogramas de E (Anexos 8-11)** (extracto del Apéndice L): en el Anexo 9, la rama "cuerpo sin costura" lista "Categoría A E=1,0/0,9" bajo total y parcial y "E=0,85/0,80" bajo sin radiografiar, cosa que no es evidente respecto de la Tabla UW-12 (0,70/0,65 sin RT) y de UW-12(d) (cuerpo sin costura con juntas circunferenciales con RT parcial: 0,85; sin RT: 0,70). No implementar los flujogramas sin que el usuario confirme, o contrastarlos con el texto del código. Además el Anexo 10 cita "Fig. 10 pág. 390", que corresponde a otro libro.
10. **Ec. (10), torisférico**: el libro da solo el caso r = 0,06 L, L = D (factor 0,885, "ASME 6 %"). El código (UG-32(e)) pide L <= diámetro exterior y r >= 6 % del diámetro y >= 3t, y tiene la fórmula general con M = (3 + sqrt(L/r))/4 (de mi conocimiento, **no está en el libro**; verificar). El torisférico más común en la práctica argentina (Klöpper, r = 0,1 D) **no queda cubierto** por la fórmula 0,885.
11. **Factor de la presión de prueba**: la ec. (26) usa 1,3 (edición actual del código); ediciones antiguas usaban 1,5. Confirmar con el usuario la edición.
12. **Símbolos repetidos con distinto significado** (riesgo de errores de implementación): L = largo del cuerpo (Zick) / radio de conformado (cabezales) / separación entre anillos (presión externa); A = factor geométrico / distancia silleta-cabezal / áreas de refuerzo; E = eficiencia de junta / módulo de elasticidad (ec. 2, 16, 19); K = varios factores; S_P/S_p/P_p = tensión por peso / tensión admisible del refuerzo / presión de prueba; Sp/S de (26) vs Sp de refuerzo.
13. **Signos en Zick**: S1 (ec. 34, 38) se imprime con ±: en el plano de la silleta, tracción arriba y compresión abajo; en el plano medio, compresión arriba y tracción abajo. S3 se imprime negativo (compresión) y los criterios usan módulo. Hay que implementarlos con convención explícita.
14. **Ec. (33), torre**: se limita a "suma de tensiones"; no especifica combinación por lado (barlovento/sotavento). Habitualmente: lado a tracción = presión (axial) + viento - peso; lado a compresión = viento + peso - presión (en vacío o sin presión interna), verificado contra S E y contra min(S, B). Es práctica común, **no está en el libro**; preguntar si se la adopta.
15. Las K de Zick en tabla vs polinomio difieren hasta ~0,007 (K2, K3). La tabla es la referencia; el polinomio es una aproximación.

**Supuestos a consultarle al usuario:**
- Edición de ASME VIII-1 con la que trabaja (factor de prueba 1,3 vs 1,5; tablas Sec. II-D vigentes). Siempre conviene que él las cargue o confirme, porque "responde por el contenido".
- ¿Dispone de las Tablas numéricas CS-1, CS-2, HA-1, HA-2 y G (Sec. II-D Subparte 3) para el módulo de presión externa? Si no, se puede digitalizar de las figuras con error de lectura y quedaría marcado como "aproximado".
- Unidades: el libro mezcla MPa, mm y N, m para viento (N/m²). Mantener MPa-mm-N con conversión explícita de qz.
- ¿Incluir sismo (INPRES-CIRSOC 103)? El libro no lo desarrolla; requeriría otra fuente.
- ¿Quiere el módulo solo con el alcance del libro (resumen didáctico) o ampliar con UG-32(e) general, UG-28(c)(2), anillos, etc.?
- Para el fuselaje: ¿tiene en mente algún tanque/recipiente presurizado en el avión, o solo el chequeo de pandeo local de tubos? Esto define si vale la pena implementar más que B6/B1.
