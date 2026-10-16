# Cap. 5 - Teoría de segundo orden para pórticos planos (viga-columna)

Compendio de Cálculo Estructural II (UNC-FCEFyN, 2024). Capítulo 5, páginas del libro 5-1 a 5-19 = PDF 79-97
(regla: página PDF = 78 + página del libro). Todas las fórmulas de abajo se leyeron en la imagen de la página.
Los valores numéricos marcados "[calc. propio]" los calculé yo en Python para validar el libro (no están en el libro).

---------------------------------------------------------------------------------------------------

## 1. Qué resuelve y para qué sirve en diseño

Plantea el equilibrio de la barra en la posición DEFORMADA (viga-columna): la carga axial P multiplica a los
desplazamientos transversales y genera un momento extra (P*y) que (a) reduce la rigidez flexional de la barra
comprimida (o la aumenta si es tracción) y (b) agranda momentos y tensiones. Con la barra resuelta de forma
exacta se obtiene una matriz de rigidez de 6x6 con "funciones de estabilidad" alfa1..alfa4 que dependen de P/Pe.
Con eso se hacen: análisis de segundo orden de pórticos (iterando las axiles), control de estabilidad
(signo del determinante), cargas críticas de columnas (det = 0), y verificación de tensiones con el momento
máximo real (flexión compuesta amplificada).
Para el diseño: dice cuánto se amplifican momentos/flechas por la compresión, cuánto falta para el pandeo, y
justifica que la teoría de 1er orden NUNCA puede predecir pandeo (p. 5-11).
El libro evita a propósito hablar de "pandeo/carga crítica" y enfatiza la amplificación de la flexión (p. 5-17, 6c).

---------------------------------------------------------------------------------------------------

## 2. Fórmulas y algoritmos clave

Convenciones del libro: P > 0 = COMPRESIÓN (en Struttura N > 0 es tracción: P = -N). Giro phi positivo
antihorario, y hacia arriba (Fig. 5, p. 5-6 / PDF 84), igual que el pórtico plano de Struttura. EI = rigidez
flexional en el plano del pórtico. Barra de i a j sobre el eje x local.

### 2.1 Planteo general (ec. 1, 2; p. 5-2 / PDF 80)
    [K(P)] w = 0     (1)   -> carga crítica: det K(P) = 0; el autovalor es Pcrit y el autovector el modo de pandeo
    [K(P)] w = H     (2)   -> flexión con axiles conocidas (P < Pcrit)
K(P) no es lineal en P (funciones trascendentes), por eso el problema de pandeo es un problema de autovalores
NO lineal; no sirve el eig de matrices constantes salvo que se use la matriz geométrica (ver 5.3).

### 2.2 Ecuaciones diferenciales en el sistema deformado (3)-(14) (p. 5-4 y 5-5 / PDF 82-83)
Flexión (3), (4) y torsión con alabeo (5). Con las contribuciones de P (10) y de las reacciones (6)-(9) se
llega a tres ecuaciones DESACOPLADAS (12), (13), (14):
    (12)  EIx2 u3'' + P u3 - (M2-M1)/L * x1 - M1 = 0              (flexión EN el plano del pórtico, plano x1-x3)
    (13)  EIx3 u2'' - P u2 - [(M2-M1)/L x1 - M1] phi = 0           (flexión fuera del plano, acoplada con la torsión)
    (14)  EIw phi'''' - (GJR - P Io/A) phi'' - [M1 + (M2-M1)/L x1] u2'' = 0    (torsión, Io = Ix2 + Ix3)
Solo (12) se resuelve en el capítulo (matriz de la barra de pórtico plano). (13) y (14) se dejan "sin resolver":
ahí vive el pandeo fuera del plano y el torsional/flexo-torsional (clave para el 3D, ver sección 5).
Nota útil (derivada por mí de (14) con M1=M2=0, articulada, NO está en el libro): Pcrit torsional
= (A/Io) (GJ + pi^2 E Iw / L^2). Para tubos redondos casi nunca gobierna.

### 2.3 Matriz de rigidez de la barra comprimida (ec. 15-44; p. 5-5 a 5-8 / PDF 83-86)
Deducción: solución de y'' + k^2 y = (K23 x - K33)/EI  (ec. 20), con
    k^2 = P/EI   (19);   kL = L sqrt(P/EI) = pi sqrt(P/Pe)   (44),(45);   Pe = pi^2 EI/L^2   (46)
Resultado (ec. 41, p. 5-8), constantes K = AE/L, K1 = 12EI/L^3, K2 = 6EI/L^2, K3 = 4EI/L,
GDL locales [u1i, u2i, phi_i, u1j, u2j, phi_j]:

    [  K     0        0        -K     0        0      ]
    [  0   K1 a1    K2 a2       0   -K1 a1    K2 a2   ]
    [  0   K2 a2    K3 a3       0   -K2 a2   (1/2)K3 a4]
    [ -K     0        0         K     0        0      ]
    [  0  -K1 a1   -K2 a2       0    K1 a1   -K2 a2   ]
    [  0   K2 a2  (1/2)K3 a4    0   -K2 a2    K3 a3   ]

Es la MISMA matriz de 1er orden (la de Struttura, portico/barra.py::rigidez_local) con a_i = 1. Las filas/columnas
axiales (1 y 4) no cambian: no hay efecto de 2do orden en el acortamiento (p. 5-5 y 5-17, ec. 86-87 = efecto de 3er orden).

Funciones de estabilidad, COMPRESIÓN (ec. 42-43, p. 5-8):
    D  = 2 (1 - cos kL) - kL sen kL
    a1 = (kL)^3 sen kL / (12 D)                (K22 = K1 a1; ec. 38)
    a2 = (kL)^2 (1 - cos kL) / (6 D)           (K23 = K2 a2; ec. 29)
    a3 = kL (sen kL - kL cos kL) / (4 D)       (K33 = K3 a3; ec. 30)
    a4 = kL (kL - sen kL) / (2 D)              (K63 = (1/2) K3 a4; ec. 33)
Relaciones de deducción verificadas: K32 = K23 (34), K53 = -K23 (31), K63 = ... (32), K22 = (2 K32 - P)/L (37)
(verificado numéricamente [calc. propio]: 12 a1 coincide con (2*K23 - P)/L).
Rango de validez: 0 < P < 4 Pe (kL < 2 pi), p. 5-9 "ninguna barra puede soportar una compresión superior a 4 Pe".
D = 0 justo en kL = 2 pi (4 Pe), que es la carga crítica de la barra empotrada-empotrada (ver 2.8).
Comportamiento: a1 se anula en P/Pe = 1 y a3 en P/Pe = 2,046 (ec. 52; mi cálculo: 2,0457); a1 -> -3,28 y a2 -> 0,
a3 -> -inf, a4 -> +inf cuando P/Pe -> 4 (ec. 50).
Barra con P = 0: los cocientes son 0/0 (ec. 47); el libro manda tomar a_i = 1 si 0 <= kL < 0,03 (P/Pe < 1e-4, ec. 48).
Sugerencia mía (no es del libro): usar series en vez de saltar a 1: a1 ~ 1 - (kL)^2/10, a2 ~ 1 - (kL)^2/60,
a3 ~ 1 - (kL)^2/30, a4 ~ 1 + (kL)^2/60 (verificadas [calc. propio] contra las exactas con kL^2 = 0,987: error < 3e-4).

Aproximaciones polinómicas, x = P/Pe (Tabla 1, ec. 49, p. 5-9) - NO recomiendo usarlas en el código:
    x <= 1      : a1 = 1 - x ; a2 = 1 - 0,17x ; a3 = 1 - 0,35x ; a4 = 1 + 0,20x
    1 < x <= 2  : a1 = 1 - 0,985x - 0,0148x^2 ; a2 = 1 - 0,164x - 0,0138x^2 ; a3 = 1 - 0,319x - 0,065x^2 ; a4 = 1 + 0,149x + 0,087x^2
    2 < x < 3   : a3 = -1,834 + 2,42 x - 0,7428 x^2   (ec. 51)
Contra las exactas [calc. propio]: en x = 1, a3 aprox = 0,65 vs 0,617 exacta (5 %), a4 = 1,20 vs 1,234; en x = 2,
a3 aprox = 0,102 vs 0,0357. Sirven para estimar a mano, no para validar.

### 2.4 Barra traccionada (ec. 53-56; p. 5-10 / PDF 88)
Misma matriz (41), con funciones hiperbólicas, x = P/Pe con P = tracción en valor absoluto, kL = pi sqrt(P/Pe):
    D  = 2 (1 - cosh kL) + kL senh kL
    a1 = (kL)^3 senh kL / (12 D)
    a2 = (kL)^2 (cosh kL - 1) / (6 D)
    a3 = kL (kL cosh kL - senh kL) / (4 D)
    a4 = kL (senh kL - kL) / (2 D)          <-- el libro imprime "sen kL - kL" (ERRATA, ver sección 7)
Aprox. (P/Pe < 2): a1 = 1 + 0,985x - 0,01x^2 ; a2 = 1 + 0,164x - 0,01x^2 ; a3 = 1 + 0,318x - 0,025x^2 ; a4 = 1 - 0,158x + 0,033x^2.
a1, a2, a3 crecen (> 1), a4 decrece (< 1). En tracción Pe es solo una referencia, sin significado físico.
Verificación [calc. propio]: las exactas coinciden con las aprox. hasta x = 2; a x = 5 la aprox. de a4 ya diverge (1,03 vs 0,69).
Para P = 0 o muy chico usar a_i = 1 (o series con los signos cambiados).

### 2.5 Sistemas de barras y procedimiento iterativo (4.1 y 4.4; p. 5-10 y 5-13 / PDF 88, 91)
    a) Paso inicial: P_b tentativos (pueden ser 0; en columnas obvias, la mitad de la carga, Fig. 12-a).
    b) Con esas P_b:
         1) armar K de cada barra con (41) y (42)/(55), rotar a globales (T k T^T) y ensamblar;
         2) calcular las fuerzas de empotramiento del estado I (dependen de P, ver 2.6);
         3) armar vector de cargas del estado II (cargas nodales);
         4) resolver K u = F;
         5) hallar la axil P_b de cada barra con la ec. (65): P = K (u1i - u1j) en ejes locales.
    c) Convergencia: repetir hasta que cada P_b calculada ~ P_b usada (tolerancia a fijar).
    d) Estabilidad: durante la triangularización (b-4), todos los pivotes de la diagonal deben ser > 0.
    e) Tensiones: con las cargas multiplicadas por el coeficiente de seguridad Cs (ec. 62: Ps = Cs P), verificar
       sigma_max <= sigma_f en los extremos (y en máximos interiores).
Reglas: es un problema no lineal -> las tensiones crecen más rápido que las cargas -> siempre se aplica Cs a las
cargas ANTES de calcular y se predimensiona; no vale superposición de resultados entre casos (4.2).
Sin control de estabilidad se pueden obtener resultados "razonables" pero imposibles (Fig. 13: estructura
que sube por una carga hacia abajo si Q > Q_estabilidad). Lo confirmé numéricamente [calc. propio]: ménsula con
P = 0,5 Pe (> Pcrit = 0,25 Pe) y carga Q en la punta da flecha NEGATIVA -0,3225 con el sistema "resoluble".

### 2.6 Superposición y fuerzas de empotramiento con axil (4.2; p. 5-11 / PDF 89)
Con 2do orden NO vale superponer cargas laterales con efectos axiales duplicados (Fig. 9-a), pero SÍ vale la
superposición de la Fig. 9-b: el estado I (barra biempotrada con carga interior y la axil P) + el estado II
(cargas nodales), con P presente en ambos. La solución homogénea es la misma; la carga transversal solo cambia
la solución particular.
Con u = kL/2 = (pi/2) sqrt(P/Pe) (ec. 60):
    q uniforme, biempotrada : eta1 = 3 (tan u - u) / (u^2 tan u)        Me = q L^2/12 * eta1      (57)
                              eta2 = 6 (u - sen u) / (u^2 sen u)        Mc = q L^2/24 * eta2      (58)  (momento en el centro)
    Q al centro, biempotrada: eta3 = 2 (1 - cos u) / (u sen u)          Me = Q L/8 * eta3         (59)
Las fuerzas de empotramiento DEPENDEN de P -> recalcularlas en cada iteración. Las reacciones verticales de la
biempotrada simétrica no cambian (qL/2 y Q/2). Para una carga puntual en el interior conviene poner un nudo ahí.
Valores [calc. propio], P/Pe = 0,5 (u = 1,1107): eta1 = 1,0933 ; eta2 = 1,1654 ; eta3 = 1,1173.
Extensión mía (NO está en el libro, por continuación analítica u -> i u): para tracción
    eta1 = 3 (u - tanh u)/(u^2 tanh u) ; eta2 = 6 (senh u - u)/(u^2 senh u) ; eta3 = 2 (cosh u - 1)/(u senh u).

### 2.7 Estabilidad del equilibrio (4.3; p. 5-12 / PDF 90)
a1 y a3 (rigideces directas) son los que más caen y pueden ser negativos: la barra "toma" rigidez del nudo.
Si det K(P) cambia de signo, K deja de ser definida positiva: sistema inestable. Gráfico det K vs carga
creciente (Figs. 11, 12): solo se diseña en la "zona 1" (hasta la primera raíz P1 = Pmáx). Cerca de P1 los
desplazamientos son enormes y manda la tensión (por eso se calcula con cargas Cs*P).
Idea de implementación (no del libro): contar pivotes negativos de la factorización LDL^T (o el signo del det)
mientras se barre el factor de carga lambda; la primera lambda con det = 0 es la carga crítica (bisección entre
el último lambda estable y el primero inestable).
Mi comentario sobre el límite "4 Pe" (no está en el libro): es justo la carga crítica de la barra biempotrada,
que en la teoría de Wittrick-Williams entra como corrección J0; mientras ninguna barra supere 4 Pe, el número de
pivotes negativos = número de cargas críticas superadas (a verificar con tests antes de confiar).

### 2.8 Cargas críticas de columnas de un tramo (4.5; ec. 61, Fig. 14; p. 5-14 / PDF 92)
    Pcrit = Phi Pe = Phi pi^2 EI/L^2 ; I = A r^2 ; lambda = L/r ; sigma_crit = Pcrit/A = Phi pi^2 E / lambda^2
Phi para los 6 casos de la Fig. 14: (a) 0,25 ; (b) 0,25 ; (c) 1 ; (d) 1 ; (e) 2,04 ; (f) 4.
Se obtienen anulando el determinante de la matriz reducida de (41):
    a: GDL (u_j, phi_j): det = K1 a1 K3 a3 - (K2 a2)^2 = 0  -> Pcrit = 0,25 Pe  (ménsula; verificado, [calc. propio] raíz 0,24996 y 2da raíz 2,2488)
    b: GDL (phi_i, u_j): det = K3 a3 K1 a1 - (K2 a2)^2 = 0  -> 0,25 Pe
    c: GDL phi_i = -phi_j: det = (K3 a3)^2 - (K3 a4/2)^2 = 0 -> Pe
    d: GDL u_j: K1 a1 = 0 -> a1 = 0 -> P/Pe = 1 -> Pe
    e: GDL phi_j: K3 a3 = 0 -> a3 = 0 -> P/Pe = 2,04 [calc. propio 2,0457]
    f: GDL u_m (dos tramos, nudo medio) -> 4 Pe
El libro NO describe los apoyos de cada letra con palabras (solo Fig. 14). Interpretación mía por los GDL libres:
a = ménsula (empotrada-libre); b = equivalente a la ménsula (articulada abajo y rotación impedida arriba con
desplazamiento libre); c y d = empotrada-guiada (rotación impedida arriba, traslación libre); e = empotrada-articulada;
f = biempotrada. La "articulada-articulada" (Phi = 1) no está en la figura: se obtiene con la matriz condensada.
Resultado exacto útil [calc. propio]: la rigidez transversal de una barra articulada-articulada condensada con
(41) es exactamente -P/L para cualquier P (a P=Pe no se anula; la barra pandea en su modo propio, que la
condensación esconde: ver riesgos).

### 2.9 Pandeo por temperatura (4.6; p. 5-14 / PDF 92)
El libro NO da fórmulas: solo menciona el caso de rieles de ferrocarril que, al impedirse la dilatación, quedan
comprimidos y pandean (viga-columna). Lo que se podría implementar (mío, no del libro):
    - barra totalmente restringida axialmente: P = E A alfa DeltaT ; Pcrit = Phi pi^2 EI/L^2
      -> DeltaT_crit = Phi pi^2 / (alfa lambda^2)   (independiente de E, A y de la sección salvo por lambda)
    - pórtico o reticulado: resolver 1er orden con la carga térmica (Struttura ya tiene carga 'temp' en el pórtico),
      tomar las axiles P_b^(1) y buscar el factor lambda_T tal que det K(lambda_T P_b^(1)) = 0 -> DeltaT_crit = lambda_T * DeltaT.
      Supone que el estado previo es lineal en DeltaT (válido si la flexión previa es chica).
Es la misma maquinaria que el pandeo por cargas, cambiando el origen de las axiles.

### 2.10 Tensiones y momento máximo en la barra (5, 5.1; ec. 62-85; p. 5-14 a 5-16 / PDF 92-94)
    sigma_max = P/A + M_max/W        (63)  ;  verificación  sigma_max <= sigma_f   (64) ;  Ps = Cs P  (62)
Esfuerzos de extremo en ejes locales (65)-(68), con las fuerzas de empotramiento del estado I (barra, con sobrerrayado):
    P   = K (u1i - u1j)
    Ri  = K1 a1 (u2i - u2j) + K2 a2 (phi_i + phi_j) + R_i0
    Mi  = K2 a2 (u2i - u2j) + K3 a3 phi_i + (1/2) K3 a4 phi_j + M_i0
    Mj  = K2 a2 (u2i - u2j) + K3 a3 phi_j + (1/2) K3 a4 phi_i + M_j0
El P de (65) debe ser casi igual al usado para calcular los a_i en la última iteración.
Momento máximo local en el interior (carga uniforme q; q = 0 sin cargas), con k^2 = P/EI, Y = y - u2i (Fig. 16):
    M(x)  = -P Y + Ri x - Mi + q x^2/2                                   (69)   [M(0) = -Mi, convención de la Fig. 16]
    Y(x)  = (phi_i/k - Ri/(kP)) sen kx + (Mi/P + q/(P k^2)) cos kx - (Mi/P + q/(P k^2)) + (Ri/P) x + q x^2/(2P)   (78)
    M(x)  = ((Ri - phi_i P)/k) sen kx - (Mi + q/k^2) cos kx + q/k^2      (79)
    x0    = (1/k) artg( (phi_i P - Ri) / (k Mi + q/k) )                  (81) ; si artg < 0 sumar pi (82)
    M0    = M(x0)                                                        (83)
    |Mmax| = max{|Mi|, |Mj|, |M0|} si 0 < x0 < L ; max{|Mi|, |Mj|} si no     (84)
    q = 0:  x0 = (1/k) artg((phi_i P - Ri)/(k Mi)) ; M0 = ((Ri - phi_i P)/k) sen k x0 - Mi cos k x0   (85)
(78)->(79) y (81) verificadas numéricamente [calc. propio] (diferencia 1e-15). La expresión de M0 en (83) usa M(x), por
lo que su signo sigue la convención de (69): comparar siempre en valor absoluto, como pide (84).

### 2.11 Anexo 1 - viga simplemente apoyada comprimida (p. 5-18 / PDF 96)
Con u = kL/2 = (pi/2) sqrt(P/Pe), 2u = pi sqrt(P/Pe) (ec. 60, 88) y verificación P/A + Mmax/W <= sigma_f (88):
    1) q uniforme       : Mmax = (q L^2/8) eta,  eta = 2 (1 - cos u) / (u^2 cos u)
    2) Q al centro      : Mmax = (Q L/4) eta,    eta = tan u / u
    3) Q en alfa L (alfa < 1/2): Mmax = alfa (1-alfa) Q L [ sen(alfa 2u) / (2u (alfa - alfa^2) sen 2u) ] A,
                          A = sen[(1-alfa) 2u] si 2u < pi / (2 (1-alfa)); A = 1 si no
    4) momento Mo en un extremo: Mmax = Mo B, B = 1/sen 2u si 2u > pi/2; B = 1 si no
    5) momentos Mo y beta Mo en los extremos (-1 <= beta <= 1): Mmax = Mo C, C = sqrt(beta^2 - 2 beta cos 2u + 1)/sen 2u
                          si 0 < D < 1 ; C = 1 si no ; D = (1/2u) artg((beta - cos 2u)/sen 2u)
    6) q + momentos MA, MB: Mo = q [L/(2u)]^2 ; D1 = MA + Mo ; D2 = MB + Mo ; theta = (D2 - D1 cos 2u)/(D1 sen 2u) ;
                          xm = (artg theta / 2u) L ; Mmax = D1 sqrt(1 + theta^2) - Mo si 0 < xm < L ; si no max{MA, MB}
Todos los factores de amplificación -> infinito cuando P -> Pe (ec. 89: u -> pi/2).
Valores de control [calc. propio], P/Pe = 0,5: caso 1 eta = 2,0299 ; caso 2 eta = 1,8168.

---------------------------------------------------------------------------------------------------

## 3. Datos tabulados / gráficos / curvas a cargar

No hace falta cargar ninguna tabla: todo se reemplaza por fórmulas cerradas.
- Fig. 8 (p. 5-8), Anexo 2 (comprimida) y Anexo 3 (traccionada) (p. 5-19 / PDF 97): curvas de a1..a4 vs P/Pe.
  Se reemplazan por (42)-(43) y (55); las curvas del libro sirven solo para verificar. Las curvas del Anexo 2 tienen
  zoom por tramos (a4/2, a4/4, a4/20, a1/3, a3/3...) porque a1, a3, a4 divergen cerca de 4 Pe.
- Tabla 1 (ec. 49) y (51), (55): aproximaciones polinómicas (4 x 2 + 1 coeficientes, y 4 de tracción). Opcionales; ya dije que
  no recomiendo usarlas.
- Fig. 14: 6 valores de Phi: 0,25 ; 0,25 ; 1 ; 1 ; 2,04 ; 4 (exactos: 0,25 ; 0,25 ; 1 ; 1 ; 2,0457 ; 4).
- Figs. 1, 2, 3, 4, 5, 6, 7, 9-13, 15-18: esquemas, no datos.
Valores exactos de referencia para tests de funciones alfa [calc. propio] (compresión, x = P/Pe):
    x=0,25 : 0,7525 0,9581 0,9149 1,0445     x=0,5 : 0,5035 0,9147 0,8236 1,0968
    x=1    : 0,0000 0,8225 0,6169 1,2337     x=2   : -1,0337 0,6113 0,0357 1,7624
    x=3    : -2,1188 0,3486 -1,2580 3,5618   x=3,9 : -3,1673 0,0404 -19,5837 39,2885
(tracción): x=1 : 1,9765 1,1540 1,2937 0,8747 ; x=3 : 3,8819 1,4145 1,7470 0,7495.

---------------------------------------------------------------------------------------------------

## 4. Ejemplos resueltos del texto

El capítulo NO trae ejemplos numéricos resueltos (solo esquemas conceptuales: Figs. 1, 9, 11-13, 17, 18).
Qué se puede usar como tests de validación (todos calculados por mí; ninguno es del libro):
 1. Funciones alfa contra la tabla de la sección 3 y contra los valores de referencia del libro: a1 = 0 en P/Pe = 1,
    a3 = 0 en 2,046 (ec. 52), a1 -> -3,28 y a2 -> 0 en P/Pe -> 4 (ec. 50), a_i -> 1 con P -> 0.
 2. Cargas críticas Phi de la Fig. 14 (casos a-f) por determinante: 0,25 ; 0,25 ; 1 ; 1 ; 2,0457 ; 4.
 3. Ménsula con carga Q en la punta y compresión P (EI = 1, L = 1, Q = 1; fórmula exacta delta = Q (tan kL - kL)/(P k),
    k = sqrt(P/EI)): con P/Pe = 0,1 -> delta = 0,55254, giro 0,84318 ; P/Pe = 0,2 -> 1,64780 y 2,56235 ;
    P/Pe = 0,24 -> 8,21812 y 12,88245 (1er orden: delta = 1/3, giro 1/2). El modelo con la matriz (41) coincide a precisión de máquina.
 4. Ménsula con P/Pe = 0,5 (> 0,25): debe detectar INESTABLE (el "resultado absurdo" -0,3225 de la sección 2.5).
 5. Viga biempotrada con q y P/Pe = 0,5: eta1 = 1,0933 ; eta2 = 1,1654 ; con Q al centro eta3 = 1,1173. Barra apoyada: 2,0299 y 1,8168.
 6. Contraste con la matriz geométrica (solo para tests del Kg): columna articulada-articulada de Pe = 1 con 1, 2, 4, 8
    elementos de Kg consistente da Pcrit/Pe = 1,2159 ; 1,0075 ; 1,0005 ; 1,00003 (la solución exacta con (41) da 1 con un solo elemento).
 7. Tensión: P/A + Mmax/W con Mmax calculado por (84)/(85) y por Anexo 1 en una barra apoyada (deben coincidir).

---------------------------------------------------------------------------------------------------

## 5. Propuesta de implementación en Struttura

Hallazgo sobre el código existente: portico/barra.py::rigidez_local (K, K1, K2, K3 de la cátedra) es EXACTAMENTE
el caso a_i = 1 de (41); la condensación de rótulas (barra.condensar) se reutiliza tal cual; el solver ya revisa
estabilidad con eigh (portico/solver.py::_verificar_estabilidad); el pórtico ya tiene carga 'temp'.

### 5.1 Tipo A - extensión del pórtico plano: "análisis de 2do orden" (recomendado)
Entradas CSV nuevas (bloque opcional, p. ej. SEGUNDO_ORDEN): activar (si/no), Cs, tolerancia sobre axiles (relativa),
iteraciones máximas, axiles iniciales opcionales por barra (default 0), amortiguamiento (default 0,5 si oscila).
Los datos E, A, I, L ya existen por barra.
Cálculo: el lazo de 2.5; por barra x = |P|/Pe y kL = pi sqrt(x); P > 0 compresión: a_i de (42); P < 0: (55); kL < 0,03 -> series o 1;
si x >= 4 en alguna iteración: error claro ("barra con P >= 4 Pe: estructura inestable o carga demasiado grande").
P (libro) = -N (Struttura). Cargas de barra: fuerzas de empotramiento con alfa (2.6) para q uniforme y P puntual central;
para el resto (q trapezoidal, puntual excéntrica, gradiente térmico) hay dos caminos: (i) subdividir la barra en
n tramos con nudos auxiliares (más simple, cada tramo con su (41)); (ii) resolver la EDO de la viga-columna para
cada tipo de carga (más trabajo; el libro solo trae q uniforme y Q al centro).
Salidas (informe HTML): para cada caso, tabla de iteraciones (P por barra vs iteración, error), a_i y kL por barra, K
local 6x6 de la última iteración, desplazamientos, esfuerzos de extremo (65)-(68), Mmax (84), tensión (63) y
CS = sigma_f/sigma_max (con Cs ya aplicado en las cargas), P/Pe por barra, advertencia si P/Pe > 0,5-ish
(umbral a definir con el usuario), comparación 1er orden vs 2do orden (amplificación de momentos y flechas),
margen de estabilidad (último pivote o lambda crítico).
Cómo se conecta: reutiliza entrada.py, cargas_barra.py (parte), esfuerzos.py (reemplazar por (65)-(68) y (79) en barras con P), informe.py.
Mejora de reporte: gráfico det(K) o menor autovalor vs lambda (Fig. 11).
Dificultad 3/5. Tiempo: grande (lazo + fuerzas de empotramiento + esfuerzos de 2do orden + informe + tests).
Dependencias: ninguna de otros capítulos; Cap. 10 (alabeo) solo si se quiere resolver (14).
IMPORTANTE de integración:
 - combinar() (portico/solver.py:205) superpone resultados linealmente: con 2do orden NO es válido (sec. 4.2).
   Cada combinación de cargas debe resolverse como caso propio con las cargas combinadas y multiplicadas por Cs.
 - equilibrio() usa la geometría indeformada; con 2do orden hay que plantear el equilibrio global en la posición
   deformada (o declarar la tolerancia) porque el término P-Delta ya está dentro de K.
 - Las axiles se suponen constantes a lo largo de la barra: con carga axial distribuida (peso propio axial) hay que
   adoptar un P representativo (promedio) o subdividir.

### 5.2 Tipo A - cargas críticas del pórtico plano (autovalores / determinante)
Modo A (exacto, con la matriz del libro): P_b(lambda) = lambda * P_b^ref, donde P_b^ref viene de un análisis de 1er orden
con el caso de carga pedido; barrer lambda en (0, lambda_max) con lambda_max tal que ninguna barra supera 4 Pe; marcar
cambios de signo de det K(lambda) o de pivotes negativos; refinar por bisección/secante. Salida: lambda_crit, Pcrit por barra,
modo de pandeo (autovector de la matriz K(lambda_crit) por inversa o por menor autovalor), longitud efectiva
equivalente K_ef = pi / (kL) por barra, y gráfico det vs lambda.
Modo B (rápido, matriz geométrica): (K0 + lambda Kg) phi = 0 como autovalor generalizado (scipy.linalg.eigh); Kg de
barra (tracción +; por barra 4x4 sobre (v, phi)):
    Kg = N/(30 L) * [[ 36, 3L, -36, 3L], [3L, 4L^2, -3L, -L^2], [-36, -3L, 36, -3L], [3L, -L^2, -3L, 4L^2]]
(forma consistente estándar de la literatura, NO está en el libro; verificada [calc. propio] contra Euler: con 1 elemento
da Pcrit = 1,2159 Pe, con 2: 1,0075 Pe, con 4: 1,0005 Pe; su desarrollo reproduce a1 ~ 1 - 0,987 P/Pe, que coincide con
el coef. 0,985 de la Tabla 1). Para obtener < 1 % de error hay que subdividir cada barra comprimida en >= 2-4 elementos.
Se puede usar el Modo B como "semilla" y el Modo A como refinamiento exacto (sin subdividir).
Dificultad 3/5 (A) y 2/5 (B). Tiempo: mediano. Dependencias: 5.1 (comparte la barra de 2do orden).

### 5.3 Tipo A - extensión del pórtico espacial 3D (matriz geométrica 12x12)
El libro NO da la matriz 3D: solo el marco teórico (ecuaciones (12)-(14) desacopladas, p. 5-5; la matriz plana de (41)).
Extensión recomendada (estándar de la literatura, a validar): Kg 12x12 de la barra de Euler-Bernoulli con axil N
(tracción +, constante) en el orden local [u,v,w,thx,thy,thz]x2 de portico3d/barra.py (theta_y = -dw/dx, theta_z = +dv/dx):
    - flexión x-y (v1, thz1, v2, thz2): el 4x4 de arriba;
    - flexión x-z (w1, thy1, w2, thy2): el mismo 4x4 con las filas/columnas de giro cambiadas de signo (igual que ky de rigidez_local);
    - torsión (thx1, thx2): N Io/(A L) * [[1,-1],[-1,1]],  Io = Iy + Iz  (de (14): GJ -> GJ - P Io/A para P de compresión);
    - axial: sin término.
Con eso: (a) cargas críticas de la estructura 3D (autovalores de (K0 + lambda Kg) phi = 0; modos de pandeo en el
espacio, incluyendo fuera del plano y torsionales); (b) análisis de 2do orden por iteración con N_b actualizados (K0 + Kg(N));
(c) chequeo de estabilidad. Para tubos redondos soldados no hace falta la parte de momentos de extremo (pandeo lateral-torsional
no existe en sección circular); para perfiles abiertos haría falta un Kg con momentos (Yang-Kuo), no previsto en el libro.
Para un 3D con aprox. < 1 %, subdividir las barras comprimidas largas en 2-4 tramos (o 1 si la barra es corta).
Dificultad 4/5. Tiempo: grande. Dependencias: 5.1 y 5.2. Hay que mantener los tests propios (comparar con Euler y con solver
validado contra FEA, como ya se hace con el fuselaje).
Aplicación al fuselaje de tubos soldados: es lo más valioso. Las longitudes efectivas de montantes y diagonales con nudos
rígidos no son 1,0 ni 0,5: el autovalor de la estructura completa las da. Permite hallar el lambda crítico de las
cargas de diseño (con Cs) y ver qué barra pandea primero. Además hay que chequear pandeo local del tubo (D/t) que NO está
en este capítulo (ver Cap. 8 del Compendio).

### 5.4 Tipo A - reticulados
Hallazgo [calc. propio]: la rigidez transversal condensada de la barra articulada-articulada de (41) es -P/L (compresión), exacta
para cualquier P. Entonces la matriz geométrica de una barra de reticulado es simple y exacta: Kg = (N/L) [[0,0,0,0],[0,1,0,-1],[0,0,0,0],[0,-1,0,1]]
sobre (u, v, u, v) locales (N tracción +), rotada a globales. Con ella: carga crítica global del reticulado (nudos
desplazándose lateralmente) y análisis de segundo orden. NO captura el pandeo de Euler de cada barra entre nudos
(la rotación condensada oculta ese modo): eso se mantiene con reticulado/analisis.py::carga_critica, o subdividiendo la barra en 2-4 elementos
de viga-columna con (41). Tipo A, dificultad 2/5 (global), 3/5 (con subdivisión). Tiempo: chico-mediano. Aplicación: cerchas de
fuselaje abierto, estructuras de soporte, entramados con barras largas.

### 5.5 Tipo B - calculadora "viga-columna"
Entradas CSV: E, A, I (y W o c), L, fy, tipo de apoyo (caso a-f o articulada-articulada), P (compresión), Cs, y cargas: q uniforme, Q al centro,
Q en alfa L, momentos de extremo (todos los casos del Anexo 1) o los esfuerzos de extremo provenientes del pórtico.
Salidas: Pe, Pcrit = Phi Pe, sigma_crit, P/Pcrit, amplificación eta, Mmax, x0, sigma_max (63) y CS = fy/sigma_max, curva Mmax vs P (tipo Fig. 18-c),
detalle paso a paso. Dificultad 2/5. Tiempo: chico. Dependencias: ninguna. Es el entregable de mayor valor/esfuerzo para empezar.
Se puede usar como verificación independiente de la barra del pórtico de 2do orden.

### 5.6 Qué aplica a qué
- Fuselaje de tubos soldados: 5.3 (autovalores 3D con Kg), 5.5 (verificación de montantes) y 5.2. Hay que cuidar el pandeo fuera del plano (ecs. 13-14) y
  que la axil de diseño use Cs. El libro no trae imperfecciones: se puede agregar una carga lateral pequeña (Fig. 18-b) para ver el efecto de 2do orden real.
- Estructuras mecánicas generales: pórticos de soporte, columnas, bastidores, estructuras de máquinas: 5.1 y 5.5.

---------------------------------------------------------------------------------------------------

## 6. Anexo teórico para los informes (referencia: Cap. 5 del Compendio)

- Viga-columna y equilibrio en la deformada: EI u'' + P u = M_ext(x) (ec. 12 / 18); k^2 = P/EI (19); kL = pi sqrt(P/Pe); Pe = pi^2 EI/L^2 (46).
- Matriz de rigidez de 2do orden de la barra (41) con a1..a4 de (42)-(43) (compresión) y (55) (tracción); a_i = 1 si kL < 0,03 (48); validez P < 4 Pe.
- Axiles por (65); iteración de axiles hasta convergencia; estabilidad por pivotes > 0 (4.4 d); Cs aplicado a las cargas (62).
- Momento máximo (79)-(85) y tensión de flexión compuesta (63)-(64).
- Cargas críticas de columnas: Pcrit = Phi pi^2 EI/L^2 con Phi de la Fig. 14 (a: 0,25 ; c, d: 1 ; e: 2,04 ; f: 4); sigma_crit = Phi pi^2 E/lambda^2 (61).
- Aclaraciones del libro para incluir: la teoría de 1er orden no predice pandeo; sin control de estabilidad pueden salir resultados
  imposibles (Fig. 13); la formulación no incluye acortamiento axial por flexión (86)-(87).

---------------------------------------------------------------------------------------------------

## 7. Riesgos, ambigüedades y preguntas para el usuario

Errata / inconsistencias detectadas:
 1. Ec. (55), a4 de tracción (p. 5-10 / PDF 88): el libro imprime kL (sen kL - kL)/(2D) con "sen" en vez de "senh" (las otras tres usan senh;
    lo confirmé en la imagen ampliada). Con sen da -0,327 en P/Pe = 1; con senh da 0,8747, que es lo que muestra el Anexo 3 y las aprox. de (55). Usar senh.
 2. Tabla 1: a3 ~ 1 - 0,35x y a4 ~ 1 + 0,20x tienen errores del 5 % en x = 1; las de 1 < x <= 2 son mejores. No validar tests contra la Tabla 1 con tolerancia fina.
 3. Los apoyos de los casos a-f (Fig. 14) están solo en figura; la asignación de GDL es inferida (sección 2.8). Los casos a y b dan el mismo Phi = 0,25 pero son
    físicamente distintos en la figura (hay que dibujarlos igual que el libro si se reproducen).
 4. Ec. (70)-(85): la convención de signos de M(x) es M(0) = -Mi (Fig. 16) mientras que Mi de (67) se define como acción de nudo; el libro compara en valor
    absoluto (84), pero para graficar M(x) hay que alinear con la convención de esfuerzos de Struttura (M > 0 tracciona -yl).
 5. Rango de validez: las funciones alfa son válidas hasta 4 Pe; si durante la iteración una barra pasa de 4 Pe el resultado cambia de rama sin aviso (a1, a3 explotan).
    Hay que detectar, no confiar en el número.
 6. El libro supone P constante a lo largo de cada barra y sin deformación por corte (Euler-Bernoulli); para barras cortas/gruesas el error puede ser
    significativo. Tampoco incluye imperfecciones iniciales (el único modelo es el de la Fig. 18-b).
 7. Una barra articulada-articulada condensada tiene rigidez transversal -P/L: a P = Pe no hay singularidad; el pandeo de Euler de esa barra se pierde en la
    condensación (ver 5.4). Si se activan rótulas en barras comprimidas del pórtico de 2do orden, conviene dejar la rotación como GDL o subdividir.
 8. Con 2do orden no se pueden superponer casos ni combinaciones (4.2): rompe el diseño actual de combinar().
 9. El libro dice (6c) que evita "pandeo/carga crítica": el enfoque de diseño es amplificación de tensiones con Cs, no el cálculo de Pcrit. Conviene reportar ambas.

Preguntas al usuario (para que decida):
 - Coeficiente de seguridad Cs por defecto y su significado (¿se aplica a las cargas como en (62)?).
 - Tolerancia de convergencia de axiles y número máximo de iteraciones; ¿criterio relativo o absoluto?
 - ¿Se acepta subdividir barras automáticamente (nudos auxiliares) para cargas generales, o prefiere resolver cada tipo de carga con la EDO?
 - Imperfecciones: ¿se agrega una carga/geometría inicial tipo L/1000 por defecto? (no está en el libro).
 - Para el fuselaje, ¿interesa el modo de pandeo (autovalores) o solo verificar tensiones con Cs?
 - ¿Quiere el Kg (matriz geométrica) estándar de la literatura, aunque no sea del Compendio, o solo lo que trae el libro?
 - Material: ¿cuál es el criterio sigma_f (fluencia, admisible)? ¿Se incorpora pandeo inelástico (no está en este capítulo)?
