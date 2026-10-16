# Cap. 13 - Mecánica de Fractura (PDF págs. 217-223, libro 13-1 a 13-7)

Convención de páginas: página del libro 13-N = página PDF 216+N. Las fórmulas de los textos y del Anexo 3 fueron verificadas mirando las imágenes de las páginas. Los números marcados **[calc. propio]** NO son del libro: los calculé con un script para tener valores de validación.

---

## 1. Qué resuelve el capítulo y para qué sirve

Es una introducción breve a la mecánica de fractura elástica lineal (Modo I, tracción) para chapas con una grieta pasante o superficial: dada una tensión nominal, un tamaño de grieta y la geometría, calcula el factor de intensidad de tensión K y lo compara con la resistencia a fractura del material Kc para obtener un coeficiente de seguridad **a fractura**, distinto del coeficiente a fluencia. Incluye la corrección por zona plástica en la punta (Irwin), tres definiciones de coeficiente de seguridad, el cálculo de la **grieta admisible** por iteración, límites de validez (espesor mínimo, zona plástica < 10 % de a) y una tabla de 31 materiales (aceros, aluminios, titanios).

Sirve en diseño para: (1) definir qué grieta no detectable hay que suponer; (2) evaluar qué hacer si en servicio se detecta una grieta (reparar o limitar tensiones); (3) elegir material/tratamiento: Kc baja cuando sube la tensión de fluencia (ec. (7)). Es verificación adicional, NO reemplaza la verificación a fluencia (p. 13-4, Advertencias 1-3).

---

## 2. Fórmulas y algoritmos clave

Notación: Ko (el libro lo llama así; en la bibliografía es K_I), Kc (= K_Ic), sigma_f = tensión de FLUENCIA (no de rotura), CS = coef. de seguridad a fractura, Cs = a fluencia (p. 13-3). Unidades de K: N/mm^1.5 (o MPa·m^0.5; 1 MPa·m^0.5 = 31.623 N/mm^1.5).

| Sec./ec. | PDF | Fórmula | Explicación |
|---|---|---|---|
| 3, (1) | 218 | `Ko = C * sigma * sqrt(pi * a)` | C adimensional según geometría/carga; a = longitud característica (según figura de cada caso); sigma = tensión nominal ignorando la grieta |
| 3, (2) | 218 | `Ko >= Kc  =>  falla por fractura` | criterio |
| 3, (3) | 218 | `Kr = C * sigma * sqrt(pi * (a + r))` | grieta efectiva a + r por plastificación (Fig. 3) |
| 3, (4) | 218 | `r = (Kr/sigma_f)^2 / (6 pi)` | radio plástico (Irwin, deformación plana) |
| 3, (5) | 218 | `Kr = C * sigma * sqrt(pi a) / beta` | despeje directo (sin iterar) |
| 3, (6) | 218 | `beta = sqrt( 1 - (C*sigma/sigma_f)^2 / 6 ) < 1` | Kr > Ko (más conservativo). Verificado: sale de reemplazar (4) en (3). Requiere (C sigma/sigma_f)^2 < 6 |
| 6, (8) | 219 | `CSo = Kc / Ko` | seguridad respecto de K elástico |
| 6, (9) | 219 | `CSr = Kc / Kr` | con corrección de zona plástica |
| 6, (10) | 219 | `CSr = beta * CSo < CSo` | verificado algebraicamente |
| 7, (11) | 219 | `C * (CSR * sigma) * sqrt(pi (a + R)) = Kc` | CSR = factor que se puede multiplicar a sigma hasta la falla |
| 7, (12) | 219 | `CSR = Kc / ( C * sigma * sqrt(pi (a + R)) )` | coeficiente de seguridad en la TENSIÓN nominal (el más conservativo) |
| 7, (13) | 219 | `R = (Kc/sigma_f)^2 / (6 pi)` | radio plástico al momento de la falla, propiedad del material (tabulada en Anexo 1) |
| 7, (14) | 219 | `CSR < CSr < CSo` | ver Riesgos 7.1 |
| 8, (15) | 220 | `B = 2.5 (Kc/sigma_f)^2` | espesor mínimo para validez de deformación plana |
| 9, (16) | 220 | `a_(i+1) = Phi / [C(a_i)]^2 - R`, con `Phi = Kc^2 / [ pi (CSR*sigma)^2 ]` | iteración de punto fijo para la **grieta admisible** a partir de (12) |

Límites (sec. 8, PDF 220): (L1) espesor < B -> Kc real es mayor que el tabulado, usar (8),(9),(12) queda del lado de la seguridad; (L2) si r > ~10 % de a, la zona plástica es muy extendida y la teoría elástica es dudosa (no hay mecánica de fractura elastoplástica en el libro).
Falla por fluencia (grietas muy chicas): ver Fig. 1 y Advertencias 1-3 (p. 13-4): se verifica fluencia SIN considerar la grieta; CS a fractura puede ser menor o mayor que CS a fluencia según tamaño de grieta. Figura 1 (PDF 217): chapa de aluminio 2024-T851 con grieta central, sigma crítica en función de 2a; para 2a < 2a0 = 1.9 mm falla por fluencia.

### Coeficiente C (Anexo 3, PDF 223) con x = a/b (0 <= x <= 1), fórmulas leídas de la imagen

1. **Grieta central pasante en placa traccionada** (ancho 2b, alto 2h, grieta 2a):
   `C0 = (1 - 0.45x + 0.3x^2) / sqrt(1-x)` para h >> b; con efecto de la altura: `C = 1 + f_beta (C0 - 1)`, `beta = b/h`, `f_beta = 1 + 0.592 beta^3` si beta < 1.5; `f_beta = 3 beta - 1.5` si beta > 1.5 (continua en beta = 1.5, valor 3).
2. **Dos grietas laterales pasantes, h/b = 1:** `C = (1.12 - 0.61x + 0.13x^2) / sqrt(1-x)`.
3. **Una grieta de borde pasante, tracción:** h/b = 1: `C = (1.12 - 1.06x + 2.09x^2 - 1.03x^3) / (1-x)^1.5`; h/b = 0.5: `C = (1.12 + 0.444x + 0.512x^2)/(1-x)`; tercera fila rotulada "b = inf": `C = (1.12 - 0.8x)/(1-x)` (ver Riesgos 7.2).
4. **Grieta de borde pasante en flexión pura** (M, espesor t, ancho b): `C = (1.12 - 2.4x + 3.15x^2 - 1.5x^3)/(1-x)^1.5` con **sigma = 6M/(t b^2)**.
5. **Agujero con una grieta radial** (sigma vertical y alfa*sigma horizontal, a = largo de la grieta desde el borde del agujero, b = distancia del centro del agujero a la punta): `C = (1-alfa) F0 + alfa F1`, `F0 = 3.36 - 7.17x + 8.08x^2 - 3.57x^3`, `F1 = 2.24 - 2.69x + 1.75x^2 - 0.60x^3`.
6. **Grieta superficial no pasante** (profundidad a, largo b << ancho c, a < espesor, h >= c): `C = 1.12 * { 0.77 + 0.57x + 5.5x^2 - 2.5x^3 + 0.22 [1 - (sigma/sigma_f)^2] }^(-0.5)`. El exponente -0.5 afecta a TODA la llave (lo confirmé ampliando la imagen y por consistencia: con x -> 0 da ~1.12 y con x = 0.5, semicircular, da C = 0.733 = 1.12/Φ con Φ = 1.53, el valor de la fórmula de Irwin para fisura semielíptica). Aquí x = a/b = a/(2c_semieje) y solo tiene sentido hasta ~0.5.
Los casos 1 a 5 son grietas pasantes.

---

## 3. Datos tabulados / gráficos / curvas

| Dato | Página | Qué es | Cuántos valores | ¿Se reemplaza por fórmula? |
|---|---|---|---|---|
| **Anexo 1**: Kc, sigma_f, B, R de 31 materiales | PDF 221 | 15 aceros, 9 aluminios, 7 titanios; columnas Kc [N/mm^1.5], sigma_f [N/mm2], B [mm], R [mm] | 31 filas x 4 = 124 números | **Sí en parte**: B y R salen de (15) y (13) a partir de Kc y sigma_f (verifiqué las 31 filas: coinciden salvo redondeo, p. ej. 2024-T851: B calc 7.37 vs 7, R 0.156 vs 0.16). Cargar solo (nombre, Kc, sigma_f) = 31 x 2 y calcular B y R |
| Fig. 4 (texto): C vs a/b para h/b = 0.4, 0.5, 0.7, 1, inf, placa con grieta central | PDF 218 | 5 curvas, a/b de 0 a ~0.7, C de 1 a 4 | ~5 x 8 = 40 puntos | **Sí**: Anexo 3 caso 1. Contrasté: a/b = 0.6, h/b = 0.4 da C = 2.95 (la figura marca ~3.0) |
| Anexo 2 Fig. 1: grieta no centrada | PDF 222 | familia de curvas A y B para d/b distintos (1, 0.4, 0.2), a/b 0-0.9 | ~7 curvas x 10 = 70 | No: digitalizar si se quiere |
| Anexo 2 Fig. 2: flexión pura y flexión en 3 puntos (l/h = 2, 4), a/h 0-0.8 | PDF 222 | 3 curvas | ~30 | Parcial: flexión pura queda cubierta por caso 4 del Anexo 3 (nota: allí se usa b como altura) |
| Anexo 2 Fig. 3: grieta de borde, h/b = 0.5, 1, inf | PDF 222 | 3 curvas | ~30 | **Sí**: caso 3 del Anexo 3 (consistente hasta ~0.7) |
| Anexo 2 Fig. 4: cilindro con grieta longitudinal (presión interior), ri/ro = 0.35, 0.75, 0.9 | PDF 222 | 3 curvas, a/(ro-ri) 0-0.7, C 1.1-3.4 | ~30 | No: digitalizar (relevante para tubos a presión) |
| Anexo 2 Fig. 5: cilindro traccionado con grieta circunferencial de 360 grados, ri/ro = 0, 0.1, 0.4, 0.8 | PDF 222 | 4 curvas, C 1-4 | ~40 | No: digitalizar (**relevante para un tubo con grieta circunferencial en soldadura**) |
| Anexo 2 Fig. 6: placa con agujero central y dos grietas, r/b = 0, 0.25, 0.5 | PDF 222 | 3 curvas | ~30 | No |
| Fig. 1 (PDF 217): sigma crítica vs 2a, aluminio 2024-T851 | PDF 217 | 1 curva | ver sec. 4 | **Sí**: Ko = Kc con C = 1 |

Total si se digitalizaran todas las curvas del Anexo 2 que no tienen fórmula: ~170-200 puntos. Recomiendo no hacerlo salvo que el usuario lo pida: con los 6 casos del Anexo 3 alcanza para una primera calculadora.

Conversión útil: Kc del Anexo 1 en MPa·m^0.5: dividir por 31.623 (p. ej. 2024-T851: 790 -> 25.0; AISI 4340 (fila 9): 3160 -> 99.9).

---

## 4. Ejemplos resueltos del texto

El capítulo **no trae ejemplos numéricos resueltos** (ni problemas propuestos, aunque diga "ejercicios prácticos" en la p. 13-1). Solo hay dos datos numéricos citados:
- **Fig. 1 (PDF 217):** placa 2024-T851, Kc = 790 N/mm^1.5, sigma_f = 460 N/mm2; falla por fluencia para 2a < 2a0 = 1.9 mm; con sigma = 200 N/mm2 la grieta crítica es 2a = 10 mm.
  Verificación con (1)-(2) y C = 1 **[calc. propio]**: a0 = Kc^2/(pi sigma_f^2) = 0.9388 mm (2a0 = 1.878 ≈ 1.9 OK); con sigma = 200: a = 4.966 mm, 2a = 9.93 ≈ 10 OK. El libro usa C = 1 (placa infinita) aunque la placa dibujada es de 80 x 80 mm: con la fórmula del caso 1 (b = 40, h = 40, beta = 1) y a = 5, C = 1.022 y la grieta crítica sería algo menor.
- Tabla del Anexo 1 como dato de entrada.

**Valores de validación [calc. propio]** (2024-T851, Kc = 790, sigma_f = 460, C = 1, a = 5 mm, R = 0.1565 mm, B calc. 7.37 mm):

| sigma [N/mm2] | Ko | beta | Kr | r [mm] | CSo | CSr | CSR |
|---|---|---|---|---|---|---|---|
| 100 | 396.33 | 0.99605 | 397.90 | 0.0397 | 1.9933 | 1.9854 | 1.9628 |
| 150 | 594.50 | 0.99110 | 599.84 | 0.0902 | 1.3288 | 1.3170 | 1.3085 |
| 200 | 792.67 | 0.98412 | 805.46 | 0.1627 | 0.9966 | 0.9808 | 0.9814 |

Con sigma = 196.28 (= Kc / sqrt(pi (a+R))) CSR = 1 exacto; con sigma = 199.33 (= Kc/sqrt(pi a)) CSo = 1.

**Grieta admisible, ec. (16) [calc. propio]:** 7075-T651 (fila 22: Kc = 850, sigma_f = 530), placa con grieta central, caso 1 con h >> b, b = 50 mm, sigma = 250 N/mm2, CSR = 1.5: R = 0.13645 mm, Phi = 1.63541 mm; la iteración converge en 4-5 pasos a **a_adm = 1.4927 mm** (C(a) = 1.0019; con C = 1: 1.4990 mm); chequeo: CSR = 1.5000.

**Tabla de regresión de C [calc. propio]** (para tests de las fórmulas del Anexo 3, 4 decimales):

| x | caso1 h>>b | caso1 beta=1 | caso1 beta=2.5 | caso2 | caso3 h/b=1 | caso3 h/b=0.5 | caso3 "inf" | caso4 | caso5 alfa=0 | caso5 alfa=1 | caso6 sigma=0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.2 | 1.0308 | 1.0491 | 1.1850 | 1.1216 | 1.3743 | 1.5366 | 1.2000 | 1.0537 | 2.2206 | 1.7672 | 0.9808 |
| 0.4 | 1.1206 | 1.1920 | 1.7235 | 1.1578 | 2.0752 | 2.2992 | 1.3333 | 1.2221 | 1.5563 | 1.4056 | 0.8045 |
| 0.5 | 1.2021 | 1.3217 | 2.2125 | 1.1985 | 2.7825 | 2.9400 | 1.4400 | 1.4708 | 1.3487 | 1.2575 | 0.7326 |
| 0.6 | 1.3250 | 1.5174 | 2.9500 | 1.2662 | 4.0079 | 3.9268 | 1.6000 | 1.9369 | 1.1957 | 1.1264 | 0.6727 |

Comparación con soluciones clásicas **[calc. propio]**: el caso 1 (h>>b) es 1-3 % mayor que la secante de Feddersen sqrt(sec(pi x/2)) (a favor de la seguridad: x = 0.5: 1.202 vs 1.189); el caso 4 (flexión) da 1.47 en x = 0.5 vs ~1.49 de las fórmulas de manual; el caso 5 da 3.36 y 2.24 en x = 0 (= 1.12 x 3 y 1.12 x 2, concentración de tensión del agujero uniaxial/biaxial: consistente).

---

## 5. Propuesta de implementación en Struttura

**Tipo B: calculadora** (`tipo;fractura`). No es un método matricial; tampoco hay que tocar los programas existentes. Hay que exigir `tipo;fractura` en PROYECTO porque el despachador no tiene bloque APOYOS que lo identifique.

**Entradas del CSV (bloques):**
- PROYECTO: tipo, unidad_fuerza, unidad_longitud (el programa trabaja con N y mm).
- MATERIAL: `nombre|indice (1-31 del Anexo 1)` o `Kc;sigma_f` propios (con aviso de unidades N/mm^1.5; opcional entrada en MPa·m^0.5 con conversión x 31.623).
- GEOMETRIA: `caso` (1-6), `b`, `h`, `a`, `t` (espesor), `M` o `sigma` según el caso, `alfa` (caso 5).
- CARGA: `sigma` nominal (o M para el caso 4), `sigma_fluencia_verificar` opcional, `CSR_objetivo`.
- OPCIONAL: tabla de varias grietas / varios sigmas (barrido).

**Salidas:** C (con la fórmula), Ko, beta, Kr, r y r/a (aviso si > 10 %), CSo, CSr, CSR, comparación con CS a fluencia (Cs = fy/sigma, nunca asumiendo que uno sea menor que el otro), espesor mínimo B vs. t (aviso si t < B: queda del lado de la seguridad pero conservador), grieta admisible por iteración (16) mostrando cada paso, **curva sigma crítica vs 2a** (repro de la Fig. 1) y curva CS vs a, informe HTML paso a paso con los números de ecuación del libro.

**Conexión con lo existente:** la tensión nominal sigma puede venir de cualquier programa (axil + flexión en una barra del pórtico espacial; tensión principal en un elemento del programa de elasticidad plana). El libro NO trata cómo obtener K desde un campo de tensiones de elementos finitos; usarlo con la tensión nominal de la sección neta lejos de la concentración (o la máxima, si se quiere conservador, aclarándolo).

**Dificultad:** 2/5. **Tiempo:** chica (fórmulas y tabla) + chica (informe y gráficos); curvas del Anexo 2 sin fórmula: mediana extra si se digitalizan. **Dependencias:** ninguna dura; opcional conexión con Cap. 12 (elasticidad plana) y con el CS a fluencia ya existente.

**Aplicación al fuselaje tubular soldado:**
- Útil como verificación cualitativa/diseño por tolerancia al daño: ¿qué defecto/grieta admite un cordón, una cartela o el borde de un agujero antes de fractura?
- Limitaciones: (a) el material típico de fuselajes de tubo (acero 4130 normalizado) **no está** en la tabla (hay 4340, aceros PH y aluminios 2024/6061/7075 para piel y herrajes); habría que pedirle a usuario Kc de una fuente de confianza, y la zona afectada por la soldadura tiene Kc y tensiones residuales desconocidas; (b) espesores de tubo de 1-2 mm son << B: se está en tensión plana, el libro dice que usar Kc de deformación plana es conservador; (c) no hay C para tubos de pared delgada (solo cilindros gruesos, Fig. 4 y 5 del Anexo 2, ri/ro hasta 0.9); (d) no hay propagación por fatiga (Paris, vida a fatiga), que en aviación es lo central; (e) temperatura: el libro marca que aluminios y aceros de alta resistencia no pierden Kc a baja temperatura, pero los aceros blandos sí entre -50 y -100 °C (p. 13-3).
- Estructuras mecánicas generales: ejes/placas con defectos detectados, herrajes de aluminio, recipientes (Fig. 4/5 del Anexo 2), placas con agujero (caso 5).

---

## 6. Qué incluir como "Anexo teórico" en los informes

(Referenciar "Compendio de Cálculo Estructural II, cap. 13", sin copiar texto.)
- Criterio de fractura (1)-(2): Ko = C sigma sqrt(pi a) frente a Kc; aclarar que K no es una tensión y sus unidades.
- Corrección por zona plástica (3)-(6) y coeficientes CSo, CSr, CSR (8)-(14), con una frase sobre cuál es más conservativo.
- Radio plástico R (13) y espesor mínimo B (15); límites de validez (L1, L2).
- Iteración de grieta admisible (16).
- Aviso de que la verificación a fractura no reemplaza a la de fluencia y que la de fluencia se hace sin grieta.
- Fórmula de C del caso usado (Anexo 3) y su rango de validez.

---

## 7. Riesgos

1. **Ec. (14) vale solo para CS > 1.** `CSR < CSr < CSo` se cumple cuando la estructura es segura. Con CS < 1 (tabla, sigma = 200) CSR (0.9814) pasa a ser mayor que CSr (0.9808), porque Kr(sigma) es superlineal en sigma. Para sigma > sigma_crítica el criterio ya dio "falla" igual. No es un error del programa; documentarlo.
2. **Fila 3 del caso 3 ("b = inf"):** el título del caso 3 en el Anexo 3 y el pie de la Fig. 3 (Anexo 2) dicen que "inf" significa placa **impedida de flexionarse** (h/b -> inf), no ancho infinito; con ancho infinito x = a/b = 0 y C valdría simplemente 1.12. Interpreto que es el caso h/b = inf (apoyo/agarre que impide flexión). Preguntarle al usuario o al docente. Además, comparada con la Fig. 3 la fórmula da ~2.4 en x = 0.8 contra ~2.1 de la curva: usarlas dentro de x <= 0.7.
3. **Tabla de fórmulas leídas de imagen:** el texto extraído del PDF pierde las divisiones (p. ej. `(1-0.45x+0.3x^2)/(1-x)^0.5`) y el exponente -0.5 del caso 6 aparece en el lugar equivocado. Las fórmulas de arriba están leídas de la imagen; cualquier carga de datos debe tomarse de allí.
4. **Definición de x en los casos 5 y 6:** el encabezado dice x = a/b en todos; en el caso 5, b es la distancia del centro del agujero a la punta (a = grieta, b = r + a); en el caso 6, b es el LARGO de la grieta superficial (no el ancho de la placa), y la fórmula solo es razonable para x <= ~0.5. Confirmar.
5. **Notación solapada:** sigma_f es tensión de fluencia (en los programas actuales fy); beta es sqrt(...) en la ec. (6) y b/h en el Anexo 3 caso 1; alfa es biaxialidad en el caso 5 y factor de rigidez en el cap. 12; R es radio plástico (no reacción); Cs (fluencia) vs CS (fractura) difieren solo por mayúsculas: en el informe usar CS_fluencia y CS_fractura.
6. **Interpretación de C en la Fig. 1:** el libro dibuja una placa de 80 mm de ancho pero la curva usa C = 1; diferencia ~2 % en sigma crítica (ver sec. 4).
7. **Falta información práctica:** no hay ejemplos, no hay propagación de grieta por fatiga, no hay Modos II/III, no hay plasticidad extendida (L2), no hay tubos de pared delgada, Kc de aceros usuales de fuselaje ni de soldaduras.
8. **Unidades:** Kc en N/mm^1.5; un cambio de mm a m o de N a MPa en el CSV hace que Ko y Kc no sean comparables (el propio libro lo advierte). La calculadora debe trabajar internamente en N y mm.
9. **Preguntas para el usuario:** ¿qué material tiene el fuselaje (4130, otro) y de dónde saca Kc?; ¿quiere calcular solo placas o también tubos?; ¿le interesan Paris/fatiga (no está en el libro)?; ¿acepta digitalizar las curvas del Anexo 2 (Fig. 4 y 5 cilindros) o con las fórmulas del Anexo 3 alcanza?
