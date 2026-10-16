# Cap. 6 - Cargas críticas de placas

Compendio de Cálculo Estructural II (UNC-FCEFyN, 2024). Capítulo 6, páginas del libro 6-1 a 6-13 = PDF 98-110
(regla: página PDF = 97 + página del libro). Las fórmulas se leyeron en imagen. Los valores marcados [calc. propio]
son cálculos míos de validación (no están en el libro).

---------------------------------------------------------------------------------------------------

## 1. Qué resuelve y para qué sirve en diseño

Calcula la carga crítica de pandeo (bifurcación del equilibrio) de placas planas delgadas rectangulares sometidas a
compresión en una o dos direcciones o a corte uniforme en su plano, con distintas condiciones de borde. Parte de la
teoría de placas de Kirchhoff con deformaciones intermedias (términos no lineales de u3), linealiza con el criterio
del equilibrio adyacente y llega a un problema de autovalores con solución analítica cuando los 4 bordes están
simplemente apoyados. Para otros apoyos o cargas da coeficientes K en gráficos.
Para diseño: tensión crítica de chapas de revestimiento, almas, paneles de chapa, alas de perfiles de pared delgada
(el "pandeo local" se retoma en Cap. 8; la resistencia postcrítica y ancho efectivo en Cap. 11). Aclara además que la carga
crítica de una placa NO es su resistencia última (hay reserva postcrítica) y que en placas reales el pandeo es gradual.

---------------------------------------------------------------------------------------------------

## 2. Fórmulas y algoritmos clave

Notación del libro: placa de espesor h, lados a (en x1) y b (en x2); D = rigidez flexional; N_ij = esfuerzos de membrana;
las cargas de compresión son positivas en las secciones 4.2 y siguientes. Los N_ij^0 son los esfuerzos del estado lineal previo.

### 2.1 Fundamentos (sec. 2 y 3; p. 6-1 a 6-5 / PDF 98-102)
- Cinemática de Kirchhoff (1)-(3): beta_i = -du3/dxi ; chi_ij = -d2u3/(dxi dxj) ; u_i* = u_i - x3 du3/dxi.
- Hipótesis de deformaciones intermedias (4): u1*/h, u2*/h << 1 pero u3/h hasta ~ 10 (valor "tentativo", dice el libro).
  Tensor de Lagrange con solo el cuadrático de u3 (6) y (7)-(8).
- Equilibrio en la deformada: (15), (16) iguales a la teoría lineal; (17), (18) momentos; (19) fuerzas según x3 con términos de
  membrana por curvatura (el único término que cambia).
- Constitutivas (20)-(22): N11 = C (g11 + nu g22), N22 = C (g22 + nu g11), N12 = C (1-nu) g12 ; M11 = -D (chi11 + nu chi22) ...
  M11 = D (chi11 + nu chi22), M22 = D (chi22 + nu chi11), M12 = -D (1-nu) chi12 (ec. 21, leído en la imagen); C = E h/(1-nu^2) ; D = E h^3/(12 (1-nu^2)).
- Con el bilaplaciano (23) se reduce a tres ecuaciones (24)-(26) y (27)-a,b,c (acopladas, con términos lineales, cuadráticos y cúbicos).
- Linealización (28): u_i = u_i^0 + u_i^1 (estado previo + perturbación infinitesimal). Resulta una ecuación DESACOPLADA para u3^1 (29)-c:
      D grad^4 u3^1 - [ N11^0 d2u3^1/dx1^2 + 2 N12^0 d2u3^1/(dx1 dx2) + N22^0 d2u3^1/dx2^2 ] = 0        (29)-c
  (equivale a (26): -D grad^4 u3 - [N11 chi11 + 2 N12 chi12 + N22 chi22] + p3 = 0 con chi = -d2u3/dx dx; con N11^0 = -P/b queda D grad^4 u + (P/b) d2u/dx1^2 = 0, ec. 32).
  Los N_ij^0 salen de la teoría lineal (30). Para la carga crítica el estado previo es el membranal lineal.

### 2.2 Compresión en una dirección, 4 bordes simplemente apoyados (4.1.1; ec. 31-38; p. 6-6 y 6-7 / PDF 103-104)
Estado previo: N11^0 = -P/b, N22^0 = 0, N12^0 = 0 (P total sobre el borde de largo b). Ecuación (32):
    D grad^4 u3^1 + (P/b) d2u3^1/dx1^2 = 0
Condiciones (33)-(34): u3 = 0 y curvatura nula en los 4 bordes. Solución (35): u3 = A_mn sen(m pi x1/a) sen(n pi x2/b)
(m, n = número de semiondas en x1 y x2). Autovalores (37):
    P = b D (pi a / m)^2 [ (m/a)^2 + (n/b)^2 ]^2
El menor P se da con n = 1 (38):
    Pcrit = K pi^2 D / b ;   K = ( m b/a + a/(m b) )^2 ... escrito en el libro como K = ( m/(a/b) + (a/b)/m )^2   (38)-b
Se toma el m entero que minimiza K. Verificado [calc. propio] que (38)-b sale de (37) con n = 1 y que
las transiciones de m a m+1 ocurren en a/b = sqrt(m(m+1)) ( = 1,414 ; 2,449 ; 3,464 ; 4,472).
Observación del libro (p. 6-7): al crecer a/b la carga crítica queda casi constante (K -> 4), a diferencia de una columna.
K mín. = 4 (cuando a/b es entero, m = a/b) y K = 4,5 ; 4,17 ; 4,08 ; 4,05 en los picos (Fig. 6-b y Fig. 7).

### 2.3 Otras condiciones de borde (4.1.2; ec. 39-40; p. 6-7 / PDF 104-105)
    Pcrit = K pi^2 D / b                              (39)
    sigma_crit = Pcrit/(b h) = K pi^2 E / (12 (1 - nu^2)) (h/b)^2         (40)
K sale de los gráficos 7-11 (ver sección 3). Siempre es mayor si los lados cargados están empotrados en lugar de apoyados;
la diferencia desaparece cuando a/b -> infinito, donde K -> K_inf (indicado en cada figura).
OJO con la geometría: b es el lado sobre el cual actúa P (el lado perpendicular a la carga) y los bordes "no cargados" son los dos lados de largo a (paralelos a la carga).
Mi ejemplo numérico [calc. propio]: Al, E = 70000 MPa, nu = 0,33, h = 1,5 mm, b = 300 mm, K = 4: sigma_crit = 6,461 MPa
(chapa muy esbelta: h/b = 0,005).

### 2.4 Cargas en dos direcciones (4.2; ec. 41-46; p. 6-9 / PDF 106)
    N11^0 = -P1/b ; N22^0 = -P2/a ; N12^0 = 0              (41)       P1 actúa sobre el lado b y P2 sobre el lado a
    R = sigma22/sigma11 = N22/N11 = (P2/a)/(P1/b) = P2 b/(P1 a)   (42)
Ecuación (43): D grad^4 u + (P1/b)( d2u/dx1^2 + R d2u/dx2^2 ) = 0. Compresión > 0, tracción < 0 (R < 0 si una carga es tracción: efecto estabilizante).
Cuatro bordes apoyados (44):
    P1crit = K pi^2 D / b ;   K = [ (m b/a)^2 + n^2 ]^2 / [ (m b/a)^2 + R n^2 ]
Se prueba por tanteo m, n enteros hasta el mínimo. P2crit = P1crit R a/b = P1crit P2/P1 (45).
Interacción (46): para cada (m, n) es una recta  P1crit (m b/a)^2 + P2crit (n^2 b/a) = [ (m b/a)^2 + n^2 ]^2 pi^2 D/b ;
la curva de interacción es la poligonal envolvente (el mínimo P2crit sobre todas las rectas), Fig. 13.
Verificación [calc. propio]: (44)-b y (46) son consistentes con (37) al hacer R = 0 y n = 1 (R = 0 -> K igual a (38)).

### 2.5 Corte uniforme (4.3; ec. 47-50; p. 6-10 / PDF 107)
Estado previo: N12^0 = dato, N11^0 = N22^0 = 0. Ecuación (48): D grad^4 u - 2 N12^0 d2u/(dx1 dx2) = 0, de solución muy difícil porque
mezcla derivadas pares e impares (no sirve la solución tipo (35)).
Para a/b -> infinito hay solución exacta de Southwell (49):
    N12crit = K pi^2 D / b^2 ;  tau12crit = N12crit/h = K pi^2 E / (12 (1 - nu^2)) (h/b)^2
    K = 5,35 (bordes largos apoyados) ; K = 8,98 (bordes largos empotrados)
Placa finita (a >= b): K del gráfico 15 o por la fórmula aproximada (50):
    K ~ 5,35 + 4 (b/a)^2   (4 bordes apoyados)
    K ~ 8,98 + 5,6 (b/a)^2 (4 bordes empotrados)
Control [calc. propio]: a/b = 1 -> 9,35 (apoyada) y 14,58 (empotrada), coinciden con el comienzo de las curvas de la Fig. 15 (~9,3 y ~14,5).
El libro usa a >= b (b es el lado corto); para a < b intercambiar los nombres.

### 2.6 Placas reales (5; p. 6-11 / PDF 108)
Las placas reales se desvían de la ideal (Fig. 16): el pandeo es gradual (la carga crítica es una noción imprecisa) y
la placa puede soportar más carga después del pandeo (Pcrit no es la resistencia última, a diferencia de la columna).
Wagner 1929: campo de tensión diagonal (Cap. 11). Ancho efectivo (Cap. 11, sec. 3). Pandeo local de secciones de pared delgada (Cap. 8).
El libro NO da correcciones plásticas ni factores de imperfección.

### 2.7 Anexo 1 - placa ortótropa (p. 6-12 / PDF 109)
Constitutivas generales (51): N11 = C11 g11 + C12 g22 ; N22 = C12 g11 + C22 g22 ; N12 = C33 g12 ; M11 = C44 chi11 + C45 chi22 ; M22 = C45 chi11 + C55 chi22 ; M12 = C66 chi12.
Cuatro bordes apoyados, compresión P en x1 (52):
    P = (pi^2 b/a^2) C44 m^2 + (pi^2 a^2/b^3) C55 / m^2 + (2 pi^2/b)(C45 + C66)
Se minimiza por tanteo en m = 1, 2, 3... Rigideces con rigidizadores (53):
    C44 = D + E I1/d1 ; C55 = D + E I2/d2 ; C45 = nu D ; C66 = (1-nu) D + (1/2)(G JR1/d1 + G JR2/d2)
    (I_i = inercia de los refuerzos en dirección i, d_i = separación, JR_i ~ (1/3) l t^3 de pared delgada)
Verificado [calc. propio]: con C44 = C55 = D, C45 = nu D, C66 = (1-nu) D recupera K = (m b/a + a/(m b))^2 de (38)
(dato útil como test). El libro propone al lector explicitar (53) para chapa acanalada (Fig. 18) pero no lo hace.

### 2.8 Anexo 2 - placa sándwich (p. 6-13 / PDF 110)
Kirchhoff deja de valer (deformación por corte del núcleo): (54) con Rc = rigidez de corte por unidad de longitud ~ (5/6) hn Gn (55).
Linealizada (56) y para compresión en x1 con 4 bordes apoyados (58). Resultado (59)-(60):
    Pcrit = K pi^2 Dbar / b ;  K = (phi + 1/phi)^2 / (1 + r (1 + phi^2)) ;  phi = m b/a ;  r = pi^2 Dbar/(b^2 Rc) ;  Dbar = (1/2) Ep hp (hn + hp)^2
Se tantea m. Desarrollé (58) con la solución (35) y obtuve exactamente (59)-b [calc. propio] - pero con el signo de (58): ver errata (sección 7).

---------------------------------------------------------------------------------------------------

## 3. Datos tabulados / gráficos / curvas a cargar

Con las fórmulas cerradas se calcula todo lo de 4 bordes apoyados (cualquier a/b) y la ortótropa/sándwich apoyada.
Hay que cargar (digitalizar) los gráficos de K para las otras condiciones de borde:
 - Fig. 7 (p. 6-7 / PDF 104): K vs a/b, bordes no cargados APOYADO-APOYADO. 2 curvas (bordes cargados apoyados: coincide con (38); bordes cargados
   empotrados: hay que digitalizarla). K_inf = 4. Etiquetas de la curva apoyada: 4,50 en 1,41 ; 4,17 en 2,45 ; 4,08 en 3,46 ; 4,05 en 4,47.
 - Fig. 8 (p. 6-8 / PDF 105): EMPOTRADO-EMPOTRADO, 2 curvas, K_inf = 7 (eje a/b 0 a 4, K 6 a 12).
 - Fig. 9: EMPOTRADO-APOYADO, 2 curvas, K_inf = 5,4.
 - Fig. 10: EMPOTRADO-LIBRE, 2 curvas, K_inf = 1,3.
 - Fig. 11: APOYADO-LIBRE, 2 curvas, K_inf = 0,42.
 - Fig. 15 (p. 6-10 / PDF 107): K de corte, a/b de 1 a 6, 2 curvas (apoyada, empotrada); se reemplazan por (50) con error pequeño; K_inf = 5,35 y 8,98.
Cantidad: 10 curvas de K(a/b) (Figs. 7-11) + 2 de corte. Con ~15-25 puntos por curva son ~200-250 valores. Hay que digitalizarlos de la imagen
(los gráficos no traen tablas): el error de lectura es de ~ +-0,05 en K. Alternativa: ajustar o usar fórmulas de la literatura (no del libro). Por ejemplo,
apoyado-libre con lados cargados apoyados, K ~ 0,425 + (b/a)^2 (fórmula clásica de Timoshenko, NO del libro, verificable contra la curva de la Fig. 11: a/b = 1 da 1,43 vs ~1,45 del gráfico).
Nota: las curvas "empotrados" (bordes cargados empotrados) no tienen fórmula cerrada en el libro.

---------------------------------------------------------------------------------------------------

## 4. Ejemplos resueltos del texto

El capítulo NO trae ejemplos numéricos resueltos. Solo hay datos en figuras (K vs a/b) y los valores K_inf.
Tests de validación que sí se pueden hacer (los calculé yo; el libro da los de la Fig. 7):
 1. 4 bordes apoyados, compresión: a/b = 1 -> K = 4 (m = 1) ; a/b = 2 -> K = 4 (m = 2) ; a/b = 3 -> 4 (m = 3) ; a/b = sqrt(2) = 1,4142 -> 4,50 (m = 1 y 2 empatan) ;
    a/b = sqrt(6) = 2,4495 -> 4,1667 (m = 2 y 3) ; 1,5 -> 4,3403 (m = 2) ; 1,2 -> 4,1344 (m = 1). Control contra Fig. 7: picos 4,50 / 4,17 / 4,08 / 4,05.
 2. Chapa de Al: E = 70000, nu = 0,33, h = 1,5, b = 300, a/b = 1 -> sigma_crit = 6,461 MPa (K = 4; ec. 40).
 3. Corte (50): a/b = 1 -> 9,35 (apoyada) y 14,58 (empotrada); a/b -> inf -> 5,35 y 8,98.
 4. Dos direcciones (44)-b: con R = 0 reproduce (38)-b; con R = 1 (compresión biaxial igual),
    a = b, m = n = 1: K = [1 + 1]^2 / [1 + 1*1] = 2 (la carga crítica por dirección baja a la mitad que uniaxial, 4).
 5. Ortótropa (52) con C44 = C55 = D, C45 = nu D, C66 = (1-nu) D -> igual a (38).
 6. Sándwich (59): para r -> 0 (Rc -> infinito) recupera K = (phi + 1/phi)^2 de la placa común.

---------------------------------------------------------------------------------------------------

## 5. Propuesta de implementación en Struttura

No encaja como programa matricial (solo hay formulas cerradas y gráficos). Tipo B (calculadora) + tipo C (anexo).
Tipo B - calculadora "pandeo de placas" (programa nuevo chico, p. ej. struttura/placas):
 Entradas CSV: E, nu, h, a, b, fy (opcional, para comparar), condiciones de borde (4 lados: A apoyado, E empotrado, L libre; se usan solo las
 combinaciones de las Figs. 7-11), tipo de carga (compresión en x1 / biaxial con R / corte), P o sigma aplicado, Cs.
 Cálculo: K por (38)-b/(44)-b buscando el m, n mínimo (tabla paso a paso de m = 1.. con K(m)); para otros bordes interpolar las
 curvas digitalizadas (Figs. 7-11) y mostrar el valor leído; sigma_crit (40); CS_pandeo = sigma_crit/sigma_aplicada; corte (49)-(50).
 Salidas (HTML): fórmulas con valores, gráfico K vs a/b con el punto marcado (usando las curvas), poligonal de interacción biaxial (Fig. 13),
 aviso si sigma_crit > fy (el libro no trae corrección plástica), aviso de que las placas tienen reserva postcrítica (Cap. 11).
 Dificultad: 2/5 (cerradas) a 3/5 (con digitalización e interpolación). Tiempo: chico-mediano (la digitalización es lo más lento).
 Dependencias: Cap. 8 (pandeo local de secciones de pared delgada) y Cap. 11 (ancho efectivo, tensión diagonal) para completar el diseño; ninguna de otros capítulos para la parte de este.
 Se puede acoplar al informe del pórtico/3D como "chequeo de pandeo local de ala/alma" cuando se tengan secciones de pared delgada (futuro).
Tipo A: no corresponde. Una placa en una malla de elementos finitos (autovalores con matriz geométrica membranal) sería un programa nuevo
distinto (placas por EF), fuera del alcance de este capítulo.
Aplicación al fuselaje de tubos soldados: mínima. Las paredes de un tubo no son placas planas (el pandeo local de tubos es de cáscara y no está acá).
Sí aplica si el fuselaje lleva revestimiento de chapa/aluminio entre largueros, costillas de ala, almas, ménsulas o chapas de unión: ahí se usa 4 bordes apoyados con K ~ 4
y corte con (50) (campo de tensión diagonal es Cap. 11).
Estructuras mecánicas generales: paneles, tapas de chapa, almas de vigas armadas, bastidores de chapa, rigidizadores (ortótropa).

---------------------------------------------------------------------------------------------------

## 6. Anexo teórico para los informes (referencia: Cap. 6 del Compendio)

- Carga crítica de placa por equilibrio adyacente: D grad^4 u3 - [N11^0 u3,11 + 2 N12^0 u3,12 + N22^0 u3,22] = 0 (29)-c con D = E h^3/(12(1-nu^2)) (22).
- 4 bordes apoyados con compresión en x1: Pcrit = K pi^2 D/b, K = (m b/a + a/(m b))^2 (38); sigma_crit (40).
- Dos direcciones: K de (44)-b, R = P2 b/(P1 a) (42), interacción lineal por tramos (46).
- Corte: tau_crit = K pi^2 E/(12(1-nu^2)) (h/b)^2 (49); K aprox. (50).
- Placas ortótropas (52)-(53) y sándwich (59)-(60) como ampliación opcional.
- Advertencias del libro: carga crítica no es resistencia última (sec. 5.1), pandeo gradual en placas reales, reserva postcrítica (Cap. 11).

---------------------------------------------------------------------------------------------------

## 7. Riesgos, ambigüedades y preguntas para el usuario

Errata / inconsistencias detectadas:
 1. Ec. (58) (Anexo 2, p. 6-13 / PDF 110): se imprime D grad^4 u - (1 - D/Rc grad^2)(P/b d2u/dx1^2) = 0, pero a partir de (56) con N11^0 = -P/b (57) y la
    forma de (29)-c, el signo del segundo término debe ser MÁS. Con el signo corregido salen exactamente (59)-(60) (verificado). Es una errata de signo.
 2. Ec. (55): Rc ~ (5/6) hn Gn. Es una aproximación inusual (la corriente para sándwich de caras finas es del tipo Gn (hn+hp)^2/hn): no la usaría sin confirmar
    con el usuario si necesita sándwich.
 3. Notación: P1, P2 son fuerzas totales sobre un borde (no por unidad de longitud); la compresión es N^0 < 0 en (31) y (41). La ec. (27)-b imprime
    "du3/dx" (sin subíndice) en un término: es d u3/dx1 (errata tipográfica).
 4. (4): el límite u3/h <= 10 es "tentativo" según el libro; no es un criterio de validez verificado.
 5. El texto extraído (comp.txt) pierde los signos de (20)-(21), (26) y (29)-c; en la imagen están bien (M12 = -D(1-nu) chi12, -D grad^4 u3 en (26)). Usar siempre la imagen.
 6. Fig. 15 y Figs. 7-11: los gráficos requieren digitalizar. Las líneas de las figuras tienen escalas de ejes poco cómodas (Fig. 7 empieza en K = 4, no en 0; Fig. 8 en 6;
    Fig. 9 en 5), cuidado al calibrar ejes.
 7. Solución para corte (49) vale para a/b -> infinito; (50) vale para a >= b (y se declara aproximada). No usar con a < b sin intercambiar lados.
 8. Todas las fórmulas son elásticas (placa ideal). El libro no trae pandeo inelástico: si sigma_crit > fy (o > límite proporcional) el resultado no es aplicable tal cual.
 9. Placa con bordes apoyados "simplemente" supone rotación libre y desplazamiento impedido; en estructuras reales (soldadura/remaches) la condición está entre apoyada y empotrada.
 
Preguntas al usuario:
 - ¿Qué estructuras de chapa interesan (fuselaje con revestimiento, costillas, almas)? Si no hay chapas planas, este capítulo solo va como anexo teórico (tipo C).
 - ¿Digitalizamos los gráficos de K (Figs. 7-11, 15) o se prefiere limitar la calculadora a 4 bordes apoyados + corte con (50)?
 - ¿Se quiere incluir pandeo inelástico (no está en el libro) o solo advertir cuando sigma_crit > fy?
 - ¿Interesa la placa ortótropa (chapa acanalada, rigidizada) y la sándwich?
