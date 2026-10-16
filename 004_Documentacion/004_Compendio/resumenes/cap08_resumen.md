# Capítulo 8 – Pandeo local de elementos compuestos (PDF págs. 125-130; libro 8-1 a 8-6)

Referencias: "(n)" = ecuación del capítulo; p.NNN = página del PDF (libro 8-k = PDF 124+k). Fórmulas releídas en imagen; las polinomiales y el anexo se verificaron numéricamente/algebraicamente.

## 1. Qué resuelve el capítulo y para qué sirve

Evita (o verifica) el pandeo local de las placas que forman una sección de pared delgada (alas, almas, caras de un cajón) cuando trabaja en compresión, flexión, flexo-compresión o corte. Cada placa se trata como independiente, apoyada en las vecinas, con la tensión crítica de placa larga (a ≫ b) tomada del Cap. 6: σcrit = K π² E /(12(1-ν²)) (h/b)². Da los coeficientes K (Tablas 1-3 y ecuaciones (4)-(5)), una forma de combinar flexión+corte (curva de interacción o fórmula DIN 4114), el criterio de "sección compacta" (b/h máximo para que el pandeo local no ocurra antes de la fluencia) y menciona el método omega para barras comprimidas de reticulados. Sirve para elegir espesores/anchos de chapas plegadas y perfiles armados y para saber cuándo hay que verificar pandeo local. Incluye un anexo con propiedades de secciones de pared delgada de espesor uniforme.

## 2. Fórmulas y algoritmos clave

Notación: b ancho de la placa (lado cargado perpendicular), h (o t) espesor, a largo (a ≫ b), E, ν, σf. Cuidado: en el anexo (p.130) "h" es la altura de la sección y "t" el espesor; en las secc. 3-4 "h" es el espesor de la placa.

- (1) (p.126) Pcrit = K∞ π² D / b, D = E h³/(12(1-ν²)) (carga por unidad de largo).
- **(2) σcrit = K∞ π² E /(12(1-ν²)) (h/b)²** (p.126). Para E = 210000, ν = 0,3: π²E/(12(1-ν²)) = 189 800 N/mm² (la constante clásica de DIN 4114). Es independiente de a y de los apoyos de los extremos cargados.
- Tabla 1 (p.126), compresión uniforme, a ≫ b: K∞ = 4,0 (dos lados apoyados), 7,0 (dos empotrados), 5,4 (un lado empotrado y otro apoyado), 1,3 (un lado empotrado y otro libre), 0,42 (un lado apoyado y otro libre).
- Tabla 2 y 3 (p.127), flexo-compresión lineal, x = σ2/σ1, con convención: si ambas son de compresión σ1 es la mayor en valor absoluto; si tienen distinto signo σ1 es la de compresión. Ver sección 3 de este resumen. Se usa σcrit = (2) con K(x), que se refiere a σ1 (la mayor compresión).
- Corte (p.127): **(3) τcrit = K π² E/(12(1-ν²)) (h/b)²**, con b = lado menor (b ≤ a): (4) bordes apoyados K ≈ 5,35 + 4 (b/a)²; (5) bordes empotrados K ≈ 8,98 + 5,6 (b/a)². (Remite a las ec. (49)-(50) del Cap. 6; ver p.127.)
- Flexión compuesta + corte (3.4, p.128): se calculan σcrit con (7) (= (2) con K de Tablas 1-3) y τcrit con (8) (= (3) con K de (4)/(5)). Luego:
  - (6) CS = OP'/OP con una curva de interacción en el plano (σ/σcrit, τ/τcrit) (Fig. 7; la figura sugiere un cuarto de elipse: se podría usar (σ/σcrit)² + (τ/τcrit)² = 1 ⇒ CS = [(σ1/σcrit)² + (τ/τcrit)²]^-0,5 para cargas proporcionales; **el texto no da la ecuación de la curva**, eso es una suposición a confirmar).
  - (9) DIN 4114: **CS = [ (σ1+σ2)/(4 σcrit) + sqrt( ((3σ1-σ2)/(4 σcrit))² + (τ/τcrit)² ) ]^-1**. Propiedades que verifiqué: con τ=0 da CS = σcrit/σ1 para cualquier x (cuando 3σ1-σ2 > 0); con σ=0 da CS = τcrit/τ. Con (9) σcrit se calcula con el K de la Tabla que corresponda al caso real (el libro lo indica en p.128), sin doble contabilizar x.
- **Sección compacta (4), (10)** (p.128): σcrit > σf ⇔ **b/h < sqrt( K π² E /(12(1-ν²) σf) )**. Si todas las placas lo cumplen no hace falta verificar pandeo local. Con E=210000, ν=0,3, σf=235: K=4 → 56,8; K=7 → 75,2; K=5,4 → 66,0; K=1,3 → 32,4; K=0,42 → 18,4; corte apoyado (b/a→0, K=5,35) → 65,7. (Calculado por mí; el libro no trae valores.)
- Reticulados (secc. 5, p.129): **método omega**: (11) ω F/A < σadm; (12) ω = (σadm tracción)/(σadm pandeo); (13) λ = Lp/r, r = sqrt(I/A). ω se toma de las tablas de las normas en función de λ y del material (no figuran en el libro; remite al Cap. 17). Comentarios cualitativos: verificar extremos como articulados (lado seguro); en columna reticulada puede pandear cualquier montante (el inferior si hay peso propio); en viga reticulada el elemento comprimido con M máximo; en hiperestáticas hay redistribución después del pandeo de un elemento.
- Anexo (p.130): propiedades de secciones de pared delgada de espesor uniforme t (T, doble T, cajón, canal "∩", ángulo L, tubo circular de radio r, línea media): A no figura (A_T = t(b+h), A_I = t(2b+h), A_cajón = 2t(b+h), A_canal = t(b+2h), A_L = t(b+h), A_tubo = 2π r t; las deduzco yo). Del libro, con x horizontal (ancho b), y vertical (alto h):
  | | T | doble T | cajón | canal ∩ | L | tubo |
  |---|---|---|---|---|---|---|
  | Ix | t h³(4b+h)/(12(b+h)) | t h²(6b+h)/12 | t h²(3b+h)/6 | t h³(2b+h)/(3(b+2h)) | t h³(4b+h)/(12(b+h)) | π t r³ |
  | Wx | arriba t h(4b+h)/6 ; abajo t h²(4b+h)/(6(2b+h)) | t h(6b+h)/6 | t h(3b+h)/3 | arriba t h(2b+h)/3 ; abajo t h²(2b+h)/(3(b+h)) | arriba t h(4b+h)/6 ; abajo t h²(4b+h)/(6(2b+h)) | π t r² |
  | Iy | t b³/12 | t b³/6 | t b²(b+3h)/6 | t b²(b+6h)/12 | t b³(b+4h)/(12(b+h)) | — |
  | Wy | t b²/6 | t b²/3 | t b(b+3h)/3 | t b(b+6h)/6 | der. t b²(b+4h)/(6(b+2h)) ; izq. t b(b+4h)/6 | — |
  | Ixy | 0 | 0 | 0 | 0 | t b²h²/(4(b+h)) | 0 |
  | JR | (b+h)t³/3 | (2b+h)t³/3 | 2 t b²h²/(b+h) | (b+2h)t³/3 | (b+h)t³/3 | 2π t r³ |
  | rx | sqrt(h³(4b+h)/12)/(b+h) | sqrt(h²(6b+h)/(12(2b+h))) | sqrt(h²(3b+h)/(12(b+h))) | sqrt(h³(2b+h)/3)/(b+2h) | — | 0,7071 r |
  | eje neutro desde arriba | h²/(2(b+h)) | — | — | h²/(b+2h) | h²/(2(b+h)) | — |
  | ry | sqrt(b³/(12(b+h))) | sqrt(b³/(6(2b+h))) | sqrt(b²(b+3h)/(12(b+h))) | sqrt(b²(b+6h)/(12(b+2h))) | — | — |
  Verificación: recalculé por mano (método de líneas medias) T, doble T, cajón, canal, L y tubo: coinciden Ix, Wx, Iy, Wy, JR (Bredt para el cajón), eje neutro y radios. Para L, Ix e Iy son respecto de ejes por G paralelos a los lados, Ixy ≠ 0 (el signo depende de la orientación) y faltan ejes principales.

## 3. Datos tabulados / gráficos / curvas a cargar

- Tabla 1 (p.126): 5 valores K∞ (ver arriba). Tabla 2 (p.127): 8 casos × 3 columnas (x = 1, 0, -1) = 24 valores. Tabla 3 (p.127): 8 polinomios cúbicos K(x) = c0 + c1 x + c2 x² + c3 x³ (más los 24 valores de control). Se cargan como datos (listas) o directamente los polinomios.
  | Caso | borde con σ1 → σ2 | c0 | c1 | c2 | c3 | K(-1) | K(0) | K(+1) |
  |---|---|---|---|---|---|---|---|---|
  | 1 | empotrado → empotrado | 13,6 | -13 | 9,7 | -3,3 | 39,6 | 13,6 | 7,0 |
  | 2 | empotrado → apoyado | 11,6 | -12 | 8,6 | -2,8 | 35,0 | 11,6 | 5,4 |
  | 3 | apoyado → empotrado | 9,8 | -9 | 6,9 | -2,3 | 28,0 | 9,8 | 5,4 |
  | 4 | apoyado → apoyado | 7,7 | -7 | 6,2 | -2,9 | 23,8 | 7,7 | 4,0 |
  | 5 | empotrado → libre | 5,9 | -6 | 2,2 | -0,8 | 14,9 | 5,9 | 1,3 |
  | 6 | libre → empotrado | 1,6 | -0,37 | 0,13 | -0,06 | 2,16 | 1,6 | 1,3 |
  | 7 | apoyado → libre | 1,7 | -2,55 | 1,91 | -0,64 | 6,80 | 1,7 | 0,42 |
  | 8 | libre → apoyado | 0,57 | -0,19 | 0,06 | -0,02 | 0,84 | 0,57 | 0,42 |
  Verificación propia: para los 8 casos el polinomio reproduce exactamente K(-1), K(0), K(+1) de la Tabla 2 (p.ej. caso 1: 13,6+13+9,7+3,3 = 39,6). Los polinomios son aproximaciones para x intermedio; no hay datos entre x=-1 y 1 en el libro. Para x < -1 (más tracción que compresión) no hay datos: extrapolar es riesgo.
- (4), (5): fórmulas de K de corte (no hay tabla). Tabla de ω del método omega: NO está en el libro (Cap. 17 / normas CIRSOC o DIN 4114): habría que cargarla aparte (cantidad: ~2 materiales × 100-200 λ).
- No hay figuras con curvas para digitalizar (la curva de interacción Fig. 7 es esquemática).
- El anexo son ~40 fórmulas, equivalentes a un generador de propiedades de perfil de pared delgada.

## 4. Ejemplos resueltos del texto

El capítulo **no trae ejemplos numéricos**. Para tests se pueden usar valores calculados con las fórmulas (a validar por el usuario con su cátedra), con E=210000, ν=0,3:
- Placa apoyada-apoyada (K=4), b/h=60: σcrit = 210,9 N/mm². Ala saliente (K=0,42), b/h=10: 797,2 N/mm².
- Corte, relación b/a = 1: K apoyado = 9,35, empotrado = 14,58; b/a = 0,5: 6,35 y 10,38.
- Tabla 3 caso 4 en x=0,5: K = 5,3875.
- DIN (9): σ1=60, σ2=-30, τ=20, σcrit=100, τcrit=60 → CS = 1,435.
- Límites de compacidad (10): arriba (σf=235).
Anclajes del libro útiles como test unitario: K(1), K(0), K(-1) de la Tabla 2 (24 valores) y la constancia π²E/(12(1-ν²)) = 189 800 N/mm².

## 5. Propuesta de implementación en Struttura

**Tipo B (calculadora "pandeo_local_placas": CSV → informe HTML paso a paso) más un chequeo automático tipo A/C en el pórtico 3D para secciones de pared delgada.**
- Entrada: PROYECTO; MATERIALES (E, nu, fy); PLACAS (id; b; t; a; apoyo_lado1; apoyo_lado2 o caso 1-8; σ1; σ2 [compresión +]; τ; fy), con opción de "modo = chequeo de compacidad".
- Salidas: K (tabla/polinomio), σcrit, τcrit, relación b/t, límite (10), CS por (6) circular/recta y por DIN (9), clasificación compacta/esbelta, aviso de fluencia. Opcional: tabla de propiedades de pared delgada del Anexo para armar secciones `generica` (A, Iy, Iz, J, cy, cz, Wt) que el 3D ya acepta.
- Conexión con el 3D: para secciones `rect_hueca` (b,h,t), `tubo` y `generica` de pared delgada, tomar σ máx. y mín. de cada cara a partir de N, My, Mz de la barra ya calculados (el 3D ya calcula esfuerzos y tensiones), obtener x = σ2/σ1 y K de Tabla 3 caso 4 (apoyada-apoyada) o caso 7/8 para alas libres, y emitir CS de pandeo local por barra y un chip "esbelta" en el visor. Para `tubo` remitir al Cap. 7.
- Dificultad: 1-2/5 (todo es evaluación de fórmulas y tablas). Tiempo: **chica** la calculadora; **mediana** con la integración al 3D (hay que definir cuál es la cara comprimida y manejar signos).
- Dependencias: Cap. 6 (K∞ y fórmulas de corte), Cap. 7 (tubos), Cap. 2 (fluencia), Cap. 17 (tablas ω, no asignado).
- Fuselaje tubular soldado: los tubos redondos se verifican con el Cap. 7; para cajones/rect_hueca soldados (travesaños de 40×60) el b/t = 20-30 ⇒ K=4: σcrit ≈ 4·189800/(b/t)² ⇒ para b/t=20: 1898 MPa ⇒ compacta (límite 56,8 con σf = 235). Es relevante para chapas de revestimiento, nervios de ala y cartelas de chapa plegada (b/t grandes). Estructuras mecánicas generales: vigas armadas, perfiles de chapa plegada, cajones soldados, bastidores.
- El método omega se puede implementar fácil (11)-(13) si el usuario carga la tabla de su norma; sin eso queda como anexo C.

## 6. Anexo teórico para los informes

Ecuaciones: (2) σcrit de placa; Tabla 1 y 3 de K∞ con la convención σ1/σ2 (compresión positiva y σ1 la mayor); (3)-(5) corte; (6)/(9) CS combinado; (10) compacidad; (11)-(13) omega. Citar "Cap. 8 del Compendio" y "Cap. 6 (K∞)". Aclarar que la verificación de fluencia es independiente y que las placas menos solicitadas restringen a las más cargadas (límite inferior = placas simplemente apoyadas entre sí, bordes libres como libres).

## 7. Riesgos, ambigüedades y preguntas

- Texto inconsistente de signos: "σ1 la mayor en valor absoluto" (ambas compresión) vs "σ1 la de compresión" (distinto signo). Hay que programar ambos casos y ordenar siempre con σ1 = compresión máxima; si ambas son de tracción no hay pandeo.
- Tabla 2/3: el borde "superior" es el de σ1 (columna x=1 es compresión uniforme, a x=-1 la tracción del borde inferior). Los casos 5 y 6 (empotrado-libre/libre-empotrado) difieren en cuál borde tiene σ1: no mezclar. En el caso 7 (apoyado-libre, x=-1: 6,8) y 8 (0,84) también.
- Curva de interacción (6): no se da la ecuación; elegir elipse o DIN (9) y preguntar al usuario/cátedra.
- En DIN 4114 original los coeficientes de σe y los límites (por ejemplo σ1 positivo) tienen condiciones adicionales; el libro sólo da (9). Confirmar con la norma que se use.
- Hipótesis de borde "simplemente apoyado en las placas vecinas" es conservadora; el empotramiento elástico real (soldaduras, esquinas) no se modela.
- Placas de corte: (4)/(5) con b = lado menor; las ecuaciones citadas del Cap. 6 no están en estas páginas.
- Método omega: faltan los datos de las tablas; preguntar qué norma (CIRSOC 301, DIN 4114, otra).
- Para flexión con ν ≠ 0,3: (2),(3),(10) usan (1-ν²) (se puede variar); las tablas de K no dependen de ν en el libro.
- Anexo: usa dimensiones de línea media y t ≪ b,h; en secciones soldadas reales hay radios y soldaduras que cambian los valores.
