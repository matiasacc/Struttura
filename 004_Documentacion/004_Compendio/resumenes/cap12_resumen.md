# Cap. 12 - Método de los Elementos Finitos (PDF págs. 182-216, libro 12-1 a 12-35)

Convención de páginas: página del libro 12-N = página PDF 181+N. Todas las fórmulas de las secciones 5 y 6 fueron verificadas mirando la imagen de la página (el texto extraído pierde símbolos). Los números marcados **[calc. propio]** NO son del libro: los calculé yo con un script para tener valores de validación.

---

## 1. Qué resuelve el capítulo y para qué sirve

Es la generalización del método matricial de rigidez a continuos 2D/3D: se divide el sólido en elementos (triángulos, cuadriláteros, tetraedros...) unidos por nodos, se aproxima el campo de desplazamientos dentro de cada elemento con un polinomio (función de aproximación) y se llega a K·u = F igual que con barras. El capítulo es 70 % conceptual (historia, proceso idealización-discretización-solución, verificación vs. validación, recomendaciones de malla, ensamble, contexto de un sistema MEF) y 30 % formulación: **un único elemento desarrollado de punta a punta, el Triángulo de Tensión Constante (TTC, "CST")** para estado plano de tensión. Los demás elementos (TTL/LST, cuadriláteros, tetraedro, isoparamétricos, axilsimétrico, bandas finitas) se describen sin desarrollar la matriz.

Para diseño sirve para: placas/chapas cargadas en su plano (cartelas, herrajes, nervios, revestimiento resistente de un fuselaje, uniones atornilladas), concentraciones de tensión en agujeros/entallas, y para entender cómo funcionan los programas comerciales (criterios de malla, equilibrio global y nodal como control).

---

## 2. Fórmulas y algoritmos clave

Notación del libro: nodos i, j, k en sentido ANTIHORARIO (obligatorio: si no, A < 0). Coordenadas x1 (horizontal), x2 (vertical). Subíndice = dirección, supraíndice = nodo o lado.

### 2.1 Coordenadas de los lados (sec. 5.2, ec. (6), PDF 190)
```
a1^i = x1^k - x1^j      a1^j = x1^i - x1^k      a1^k = x1^j - x1^i
a2^i = x2^k - x2^j      a2^j = x2^i - x2^k      a2^k = x2^j - x2^i
```
El lado "i" es el opuesto al nodo i; a^lado_dirección es la componente del vector del lado recorrido en sentido antihorario. En notación estándar: b_i = -a2^i, c_i = a1^i.

### 2.2 Área (ec. (10)-d, PDF 191)
```
A = 1/2 ( a1^j a2^k - a2^j a1^k )          (> 0 si i,j,k antihorario)
```

### 2.3 Coordenadas triangulares (ec. (7), (8), (11), PDF 190-191)
```
zeta_i = A_i / A ,  zeta_j = A_j / A ,  zeta_k = A_k / A ,   zeta_i + zeta_j + zeta_k = 1
zeta_i(x1,x2) = [ (x1^j - x1) a2^i - (x2^j - x2) a1^i ] / (2A)
zeta_j(x1,x2) = [ (x1^k - x1) a2^j - (x2^k - x2) a1^j ] / (2A)
zeta_k(x1,x2) = [ (x1^i - x1) a2^k - (x2^i - x2) a1^k ] / (2A)
```
Puntos notables (Ej. 2, PDF 191): baricentro (1/3,1/3,1/3); punto medio del lado jk = (0,1/2,1/2); del lado ki = (1/2,0,1/2); del lado ij = (1/2,1/2,0).

### 2.4 Función de aproximación lineal (ec. (9), PDF 191)
```
u1(x1,x2) = u1^i zeta_i + u1^j zeta_j + u1^k zeta_k
u2(x1,x2) = u2^i zeta_i + u2^j zeta_j + u2^k zeta_k
```
Alternativa polinomial (ec. (2)-(5), PDF 189-190): u = a0 + a1 x1 + a2 x2, con {alpha} = [X]^-1 {u}; el libro la presenta solo para mostrar por qué conviene usar coordenadas triangulares (evita invertir [X] 6x6).

### 2.5 Ecuaciones de la elasticidad plana (ec. (15)-(17), PDF 193)
```
equilibrio:  d s11/dx1 + d s21/dx2 + F1 = 0 ;   d s12/dx1 + d s22/dx2 + F2 = 0
constitutiva (estado plano de TENSION):
   { s11 }       E       [ 1   nu    0     ] { e11 }
   { s22 }  = ------- *  [ nu  1     0     ] { e22 }
   { s12 }    1 - nu^2   [ 0   0   1 - nu  ] { e12 }
cinemática:  e11 = du1/dx1 ; e22 = du2/dx2 ; e12 = 1/2 (du1/dx2 + du2/dx1)
```
**Ojo:** e12 es la deformación TENSORIAL (la mitad de la distorsión gamma). Por eso el término de corte de la constitutiva es (1-nu) y no (1-nu)/2. Es equivalente a la forma usual con gamma, pero hay que ser coherente al programar.

### 2.6 Deformaciones del TTC (ec. (19), PDF 193)
```
e11 = - ( u1^i a2^i + u1^j a2^j + u1^k a2^k ) / (2A)
e22 =   ( u2^i a1^i + u2^j a1^j + u2^k a1^k ) / (2A)
e12 = [ ( u1^m a1^m ) - ( u2^m a2^m ) ] / (4A)          (suma sobre m = i,j,k)
```
Verificadas contra la forma estándar B = 1/(2A) [b 0; 0 c; c b]: coinciden con b=-a2, c=a1 (e12 tensorial = gamma/2). Son CONSTANTES en el elemento (por eso "tensión constante"); las tensiones salen de (16).

### 2.7 Energía y potencial (ec. (12)-(14), (20)-(27), (28), PDF 192-195)
```
pi = W + U ;   pi = Int(omega dV) - Int(F.u dV) - Int(f.u dS)       (13)
Wk = h E A / [2(1-nu^2)] * [ e11^2 + e22^2 + 2 nu e11 e22 + 2(1-nu) e12^2 ]      (23)
U  = - F1 A/3 (u1^i+u1^j+u1^k) - F2 A/3 (u2^i+u2^j+u2^k)                          (27)
   usando  Int zeta dA = A/3  (26)  (fuerzas másicas constantes, sin cargas de borde)
equilibrio: d pi / d u = 0  para cada GDL                                         (14),(29)
```

### 2.8 Matriz de rigidez del TTC (ec. (32)-(35), PDF 195-196) - EL RESULTADO CENTRAL
```
alpha = E h / [ 4 A (1 - nu^2) ]            (33-a)
beta  = (1 - nu) / 2                        (33-b)

Bloque 2x2 K_im  (fila = fuerza en nodo i, columna = desplazamiento en nodo m):
 k11_im =  alpha ( a2^m a2^i + beta a1^m a1^i )
 k12_im = -alpha ( nu a1^m a2^i + beta a2^m a1^i )
 k21_im = -alpha ( nu a2^m a1^i + beta a1^m a2^i )
 k22_im =  alpha ( a1^m a1^i + beta a2^m a2^i )                  (35)

Sistema del elemento (34):  [K_e] {u} = (A/3) {F}      F = fuerza másica (ver Riesgos 7.4)
```
Verificada: coincide exactamente con K = h A B^T D B (diferencia ~1e-10 **[calc. propio]**), es simétrica, tiene 3 autovalores nulos (3 movimientos de cuerpo rígido) y 3 positivos. Notación (34): k^{ab}_{nm}: a = dirección de la fuerza, b = dirección del desplazamiento, subíndices = nodo de la fuerza, nodo del desplazamiento (se confirma con la imagen del PDF 196).

### 2.9 Ensamble (sec. 8.3, Ej. 4, PDF 207-209)
Cada elemento de m nodos con g GDL/nodo tiene matriz de orden n = m·g con m² bloques g x g; la global tiene M² bloques (N = M·g GDL). Cada bloque K_ab^e se suma en el bloque (nodo global de a, nodo global de b). Se transforma cada matriz a ejes globales antes (en TTC ya está en ejes globales). Elementos de distinto tipo se combinan sumando bloques si comparten GDL compatibles (Fig. 20: TTC + "tensor" de refuerzo, ec. (48)). Matriz global simétrica, en banda; ancho de banda depende de la numeración (recomendación 9).

### 2.10 Otros elementos (solo descripción, sin matriz)
- TTL (6 nodos, "tensión lineal"), ec. (37)-(38), PDF 197: u = Σ u_v zeta_v (2 zeta_v - 1) [v=i,j,k] + 4 u^l zeta_i zeta_j + 4 u^m zeta_j zeta_k + 4 u^n zeta_k zeta_i. Nodos l, m, n en los puntos medios de los lados ij, jk, ki (Fig. 9a). 12 GDL.
- Cuadrilátero: 2 TTC superpuestos, o 4 TTC con condensación del nodo central (Fig. 10, PDF 198). Sin fórmulas.
- Axilsimétrico (ec. (39)-(42), PDF 200): eps = {e_z, e_r, e_theta, gamma_rz}, sigma = {s_z, s_r, s_theta, tau_rz}, sigma = C eps con
  `C = D [ (1-nu) nu nu 0 ; nu (1-nu) nu 0 ; nu nu (1-nu) 0 ; 0 0 0 (1-2nu)/2 ]`, `D = E / [(1+nu)(1-2nu)]`. Falta la matriz B (con el término u_r/r) y la integración con 2 pi r.
- Bandas finitas (ec. (43), PDF 201): w = Σ w_i(x,y) sen(i pi z / L). Solo apoyos simples en los extremos.
- Tetraedro de tensión constante y prisma rectangular: solo mencionados.

### 2.11 Teoría de convergencia (sec. 5.3-5.4, PDF 192)
Condiciones: (i) compatibilidad entre elementos (continuidad de u en bordes), (ii) incluir movimiento de cuerpo rígido, (iii) poder representar deformación constante. El TTC cumple las tres. Con funciones compatibles, la rigidez del modelo es ≥ la real (los desplazamientos dan por DEBAJO y convergen creciendo al refinar). Esto es la base de un chequeo de convergencia en el programa.

### 2.12 Recomendaciones de malla (sec. 8.2, PDF 205-206) - lista de 10 reglas para un "control de calidad de malla"
1 elementos regulares (triángulos ~equiláteros, evitar obtusos); 2 respetar contorno; 3 densificar donde hay gradiente de tensiones o radios chicos; 4 densificación gradual; 5 nodos compartidos por similar cantidad de elementos; 6 mallas refinadas contienen a las gruesas; 7 densificación localizada; 8 numeración sistemática; 9 nodos de un mismo elemento con numeración cercana (ancho de banda); 10 mostrar convergencia asintótica al refinar. Además (p. 12-26): mal condicionamiento se detecta por falta de equilibrio global (cargas vs reacciones) y nodal: hacer ambos controles antes de mirar resultados.

---

## 3. Datos tabulados / gráficos / curvas

El TTC no necesita ninguna tabla ni curva: solo E, nu, h y coordenadas. Lo tabulado/graficado del capítulo es descriptivo:

| Dato | Página | Valores | ¿Cargar? |
|---|---|---|---|
| Tabla 1: grado de función / nodos / GDL para triángulo | PDF 198 | 3 filas: lineal 3 nodos 6 GDL; cuadrática 6 nodos 12 GDL; cúbica 9 nodos 18 GDL | Solo como texto en el anexo (ver Riesgos 7.6: la cúbica completa tiene 10 nodos) |
| Tabla 2: librería de elementos NISA | PDF 202-203 | matriz de doble entrada (tipo de elemento x función de aproximación), imagen | No; solo ilustrativa |
| Tabla 3: modelos de la viga Fig. 16 | PDF 204 | 3 filas: 96 el/65 nodos/130 GDL; 150/96/192; 600/341/682 | Sí, como datos del caso de validación (sec. 4) |
| Fig. 16-g, 16-h: deflexiones y tensiones de la viga | PDF 204 | curvas, sin valores numéricos | No digitalizar; usar valores calculados (sec. 4) |
| Figs. 17-18: mallas de placa con orificio y accesorio de montaje | PDF 206 | dibujos sin cotas | No |
| Sec. 10: 8 modelos de ejemplo con nodos/GDL | PDF 213-215 | pistón 12.600 GDL; múltiple 234 el/1.488 nodos/4.464 GDL; diferencial 192 el/1.308 nodos/7.800 GDL; chasis camión 1.400 el/4.400 nodos/24.000 GDL; cigüeñal 750 el/5.300 nodos/15.900 GDL; chasis F2 tubular con piel de aluminio 550 el/193 nodos/~1.000 GDL | No (informativo). Ver el chasis F2 (PDF 215): barras + TTC |

No hay fórmula aproximada que reemplace nada: no hay curvas a digitalizar para implementar el TTC.

---

## 4. Ejemplos resueltos del texto

El capítulo NO trae ejemplos con números finales de tensiones/desplazamientos. Dice (p. 12-29) que hay "problemas prácticos al final de este capítulo", pero esta edición no los incluye (el capítulo termina con la bibliografía). Ejemplos:

- **Ej. 1 (PDF 189-190):** desarrollo simbólico de la función lineal en un triángulo; sin números.
- **Ej. 2 (PDF 191):** coordenadas triangulares de puntos notables (resultado en 2.3). Test trivial de coordenadas baricéntricas.
- **Ej. 3 (PDF 196):** partición "4-4" de K del TTC de la Fig. 8. Datos: nodos 3 (20,10), 4 (80,10), 5 (80,90) (unidades sin especificar). Orden local i,j,k = 3,4,5. Resultado simbólico, ec. (36):
  `k44_11 = alpha[(-80)^2 + (-60)^2 beta]`, `k44_12 = -alpha[(-60)(-80) nu + (-80)(-60) beta]`, `k44_21` igual a k44_12, `k44_22 = alpha[(-60)^2 + (-80)^2 beta]`
  (a1^4 = -60, a2^4 = -80; A = 2400). **No da E, nu, h.**
  **Valores numéricos para test [calc. propio], E = 200000 N/mm2, nu = 0.3, h = 10 mm:** A = 2400 mm2, alpha = 228.9377 N/mm3, beta = 0.35,
  K44 = [[1 753 663.0, -714 285.7], [-714 285.7, 1 336 996.3]] N/mm.
  Matriz completa 6x6 (orden u1_3,u2_3,u1_4,u2_4,u1_5,u2_5), N/mm:
  ```
  [ 1465201.5        0  -1465201.5   329670.3         0  -329670.3 ]
  [       0     512820.5   384615.4  -512820.5  -384615.4        0 ]
  [-1465201.5   384615.4  1753663.0  -714285.7  -288461.5  329670.3 ]
  [  329670.3  -512820.5  -714285.7  1336996.3   384615.4 -824175.8 ]
  [        0   -384615.4  -288461.5   384615.4    288461.5       0 ]
  [ -329670.3         0   329670.3  -824175.8          0  824175.8 ]
  ```
  Autovalores: 0, 0, 0, 894 907.8, 1 602 564.1, 3 683 846.8.
  Test de deformación: u = (0,0,0,0,0.01,0) mm -> e11 = e22 = 0, gamma12 = 1.25e-4 (e12 tensorial = 6.25e-5), s12 = G*gamma = 9.615 N/mm2.
- **Ej. 4 (PDF 208-209):** ensamble simbólico de 3 TTC: A = (1,2,4), B = (1,3,4), C = (3,4,5) (deducido de las ec. (44)-(47)), 5 nodos. Verifica estructura de bloques: K12 no nulo, K15 = K23 = K25 = 0; nodos 1 y 3 reciben 2 elementos, nodo 4 recibe 3, nodos 2 y 5 uno solo. Con el tensor D entre 1 y 5 (Fig. 20, ec. (48)) se suman K11, K55, K15, K51. **Test estructural de patrón de ensamble**, sin números.
- **Viga de gran altura de Rockey (sec. 8.1, PDF 203-205, Fig. 16 y Tabla 3):** el único caso con datos completos para validar. Datos (Fig. 16-a): luz 15 in, altura 5 in, espesor 1 in, E = 13 400 ton/in2, nu = 0.3, carga uniforme 0.8 ton/in sobre el borde superior, simplemente apoyada. Mallas de triángulos con diagonales en un solo sentido: 16-d: 12x4 celdas (1.25 in), 96 el, 65 nodos; 16-e: 15x5 celdas (1.0 in), 150 el, 96 nodos; 16-f: 30x10 celdas (0.5 in), 600 el, 341 nodos. Resultados del libro: SOLO gráficos (16-g deflexiones, 16-h tensiones sx y sy en la sección central); conclusiones: los MEF dan por debajo y convergen al refinar.
  **Referencias analíticas [calc. propio]:** flecha en el centro Euler-Bernoulli = 5qL^4/(384 E I) = 3.778e-3 in; con corte (Timoshenko, k = 5/6, G = E/2.6) suma 1.048e-3 in -> 4.826e-3 in; M máx = 22.5 ton.in, sx extrema = 5.4 ton/in2; sy bajo la carga = -0.8 ton/in2.
  **Resultados de mi TTC [calc. propio]** (nodos del borde inferior; uy=0 en TODOS los nodos de los dos bordes extremos y ux=0 en un nodo; carga consistente 0.8*dx, mitad en los extremos): flecha en el centro del borde inferior: 96 el: 3.807e-3 in; 150 el: 4.015e-3 in (promedio de los dos nodos centrales); 600 el: 4.402e-3 in; (malla extra 60x20 = 2400 el: 4.507e-3 in). Convergen creciendo desde abajo hacia ~4.7-4.8e-3 como en la Fig. 16-g. Usar como test de regresión con tolerancia ~1 %, y como test cualitativo de convergencia monótona.
  **Aviso:** con apoyo puntual solo en las dos esquinas inferiores (lo que dice textualmente "nodos del borde inferior de ambos extremos" y dibuja la Fig. 16-a) la flecha NO converge desde abajo (4.82e-3, 5.2e-3, 6.19e-3, 6.94e-3 al refinar: singularidad de la reacción puntual). Parece que el libro restringió el desplazamiento vertical de todos los nodos de los bordes extremos. Hay que confirmarlo (Riesgos 7.5).
- **Tests propios recomendados (no del libro, solución exacta conocida):** (a) patch test de tracción uniaxial: placa 100x50 mm, E = 200000, nu = 0.3, h = 10, 2 triángulos, sx = 100 N/mm2 -> ux = 0.05 mm, uy(superior) = -0.0075 mm **[calc. propio, reproducido exactamente]**, tensiones uniformes; (b) 3 modos rígidos con fuerzas nulas; (c) equilibrio global y nodal; (d) simetría de K y 3 autovalores nulos; (e) viga en voladizo: el TTC es demasiado rígido en flexión (el libro lo insinúa al hablar de mallas muy densas, p. 12-16) - sirve para mostrar el efecto del refinamiento.

---

## 5. Propuesta de implementación en Struttura

### 5.1 Tipo A: programa nuevo "elasticidad plana 2D" (`tipo;plano2d`)

Qué se puede implementar con lo que da el libro, en orden:

| Elemento / función | Respaldo del libro | Estado |
|---|---|---|
| **TTC, estado plano de tensión** | Completo: (6),(10),(19),(33),(35) | implementar ya |
| TTC + **barras** (refuerzos, "tensor D", Fig. 20 y chasis F2 de PDF 215) | Ej. 4 y ec. (48) | implementar ya (reusar barra de reticulado, mismos 2 GDL/nodo) |
| Cuadrilátero = 2 TTC o 4 TTC con condensación del nodo central | Descripción, Fig. 10 | fácil: Schur complement; fuera del libro la fórmula, pero es estándar |
| Estado plano de **deformación** | Mencionado (p. 12-2, 12-16) pero la matriz constitutiva NO está en el cap. | agregar cambiando (E, nu) por E' = E/(1-nu^2), nu' = nu/(1-nu) en alpha, beta (identidad estándar, no del libro) |
| TTL / LST (6 nodos) | Solo funciones de forma (38) | requiere derivar B y integrar (fórmula de integración de coordenadas triangulares, no del libro); dificultad 3 |
| Q4 isoparamétrico | Solo descripción conceptual (7.3) | no hay fórmulas en el libro; opcional con fuente externa |
| Axilsimétrico | Solo constitutiva (41) | opcional, falta B y 2 pi r |

**Estructura de archivos** (clonar la de los otros programas): `plano2d/{__init__,__main__,entrada,elemento,solver,tensiones,informe,visor}.py`; `elemento.py` = ec. (6),(10),(19),(33),(35); `solver.py` = ensamble por bloques 2x2, condiciones de apoyo, resolución; `tensiones.py` reusa `portico3d/tensor.py` (Von Mises, Tresca, Rankine, Mohr-Coulomb, círculo de Mohr) con tensor plano s11,s22,s12.

**Despachador:** hay que exigir `tipo;plano2d` en PROYECTO, porque hoy el bloque APOYOS con solo `ux;uy` se deduce como reticulado (despachador.detectar_tipo). Alternativa: detectar el bloque ELEMENTOS/TRIANGULOS.

**Entradas CSV (bloques):**
- PROYECTO: `tipo;plano2d`, `estado;tension|deformacion`, unidad_fuerza, unidad_longitud, escala_deformada.
- NODOS: `id;x;y`
- MATERIALES: `id;E;nu;fy;sadm` (más los parámetros de Rankine/Mohr-Coulomb como en pórtico espacial)
- TRIANGULOS (o ELEMENTOS): `id;ni;nj;nk;material;espesor` (el programa verifica orden antihorario, A > 0, y avisa/corrige)
- BARRAS (opcional): `id;ni;nj;material;area` (refuerzo)
- APOYOS: `nodo;ux;uy` (con asentamientos opcionales)
- CARGAS_NODALES: `nodo;Fx;Fy`
- CARGAS_MASICAS (opcional): `elemento;F1;F2` con la unidad aclarada (ver Riesgos 7.4)
- CARGAS_BORDE (extensión no cubierta por el libro, que fija f = 0): `ni;nj;qx;qy` por unidad de longitud; carga nodal consistente = q·h·L/2 a cada nodo (derivable de la misma energía (24)).
- Opcional: generador de malla estructurada rectangular (nx, ny, diagonal) para evitar cargar cientos de triángulos a mano (la Fig. 16 usa mallas regulares).

**Salidas:** desplazamientos nodales; reacciones; **equilibrio global (cargas vs reacciones) y por nodo** (recomendado en p. 12-26, y ya lo tienen los otros programas); por elemento: e11, e22, e12 (y gamma), s11, s22, s12, tensiones principales y ángulo, Von Mises (tensión plana), Tresca, Rankine, Mohr-Coulomb, CS; deformada; mapa de colores por elemento (tensión constante -> mapa "a trozos") y opcionalmente suavizado nodal; informe HTML con K de un elemento, patrón de bloques del ensamble (como Ej. 4) y semi-ancho de banda; módulo de **estudio de convergencia** (varias mallas -> tabla y gráfico, como Fig. 16-g) y **control de calidad de malla** (ángulo mínimo, relación de aspecto, orden antihorario) según 8.2.

**Conexión con lo existente:** mismo formato de bloques/CSV, mismo informe HTML, mismo tensor de tensiones y CS, mismo visor_comun; barras idénticas al reticulado.

**Dificultad:** 3/5 (la matemática del TTC es de nivel 2; entrada de malla, visor por elementos e informe suben la dificultad).
**Tiempo:** núcleo TTC + solver + tests = mediana; entrada CSV + informe + visor = mediana; generador de malla + convergencia + calidad de malla = chica a mediana; LST/Q4 = mediana cada uno; **membrana 3D** (ver abajo) = grande.
**Dependencias:** ninguna dura de otros capítulos de este tramo; usa el tensor de tensiones ya existente. El capítulo cita Cap. 1 ec. (131) y Cap. 3 ec. (12) solo para el axilsimétrico. Cap. 13 (fractura) puede consumir tensiones de este programa (ver resumen del cap. 13).

### 5.2 Aplicación a la estructura tubular soldada de un fuselaje
- Directamente: chapas planas del fuselaje cargadas en su plano (cartelas de unión de tubos, placas de herrajes de alas/tren, tapa de motor/mamparo cortafuego, piso, revestimiento de chapa) y **concentración de tensiones** en agujeros y bordes de herrajes, que el modelo de barras no ve.
- El caso del libro del chasis tubular de un F2 con piel de aluminio (PDF 215: barras + TTC, 550 elementos) es exactamente la idea de "fuselaje de tubos + piel", pero ahí la piel está en 3D. Con el TTC plano solo se puede hacer un panel plano. Para un fuselaje real haría falta una **membrana triangular en el espacio** (CST con matriz de transformación a ejes globales, 3 GDL traslacionales/nodo, sin rigidez de giro): el libro lo sugiere ("las matrices de los elementos se definen en ejes locales y se transforman", p. 12-26) pero no lo desarrolla. Al conectarla a los nodos de pórtico 3D (6 GDL) los giros quedan sin rigidez de membrana -> hay que cuidar la singularidad numérica. Es una segunda etapa "grande" y opcional.
- Estructuras mecánicas generales: soportes, bridas, bielas planas, placas con agujeros, ménsulas, uniones a corte.

---

## 6. Qué incluir como "Anexo teórico" en los informes

(Referenciar "Compendio de Cálculo Estructural II, cap. 12", sin copiar texto.)
1. Hipótesis: estado plano de tensión (o deformación), material lineal elástico, pequeños desplazamientos, espesor constante por elemento.
2. Elemento TTC: coordenadas de los lados a^lado_dir (6); área (10-d); desplazamientos lineales por coordenadas triangulares (9); deformaciones constantes (19); constitutiva (16).
3. Principio de mínima energía potencial total (12)-(14) y energía de deformación del elemento (23).
4. Matriz de rigidez (33)-(35) con alpha y beta; propiedades: simétrica, 3 modos rígidos, bloques 2x2.
5. Ensamble por bloques (sec. 8.3, Ej. 4) y superposición de barras de refuerzo (ec. (48)).
6. Interpretación de resultados: desplazamientos por debajo de los reales y convergentes al refinar (5.3); tensiones constantes por elemento y discontinuas entre elementos (6.1); controles de equilibrio global/nodal.
7. Recomendaciones de malla (8.2) y verificación vs. validación (Fig. 3).

---

## 7. Riesgos

1. **Estado plano de tensión mal justificado:** en la p. 12-2 el libro dice que una pieza de "profundidad muy grande" se modela con estado plano de TENSIÓN. Es al revés: una pieza prismática larga corresponde a deformación plana. Para chapas delgadas cargadas en su plano sí vale tensión plana. Preguntarle al usuario qué usa y ofrecer ambas opciones.
2. **Deformación tensorial e12:** el libro usa e12 = gamma/2 en (17),(19) y (1-nu) en la constitutiva. Si se mezcla con la convención de ingeniería (gamma y (1-nu)/2) los términos de corte salen errados. Documentar la convención en el código.
3. **No hay matriz para deformación plana:** solo se menciona. Mi sustitución E', nu' no es del libro (es una identidad estándar).
4. **Fuerzas másicas y espesor:** en (24)-(25) la integral de F·u no lleva h, mientras que la energía (21) sí. Para que (27), (32), (34) sean coherentes, F debe ser fuerza por UNIDAD DE ÁREA de la chapa (= peso específico x h). Pero el texto de la p. 12-13 habla de "fuerza másica por unidad de volumen (en este caso por unidad de área)". Definir claramente la unidad en el CSV.
5. **Apoyos de la viga Fig. 16:** "nodos del borde inferior de ambos extremos" es ambiguo; con apoyos puntuales en las esquinas el resultado diverge (sec. 4); lo que reproduce la Fig. 16-g es restringir uy en todos los nodos de los dos bordes extremos. Falta confirmar con el usuario o con la guía de TP.
6. **Tabla 1:** el cúbico completo tiene 10 coeficientes por componente, por lo que corresponde a 10 nodos (20 GDL), no 9 nodos/18 GDL; la tabla y la Fig. 9-b muestran 9 nodos (habría que condensar un nodo interior o usar un polinomio incompleto). No implementar el triángulo cúbico a partir de este capítulo.
7. **Definición de GDL del modelo:** la p. 12-7 dice que los GDL del modelo descuentan los restringidos (31x2 - 3x2 = 56), pero la Tabla 3 cuenta 2 por nodo sin descontar (130, 192, 682). Inconsistencia menor.
8. **Cargas de superficie:** el desarrollo supone f = 0; no hay carga distribuida de borde, que es lo habitual en la práctica. Hay que agregar la carga nodal consistente (no es del libro).
9. **Sin ejemplos numéricos ni problemas:** no hay resultados de tensiones para validar. Pedirle al usuario si tiene la guía de trabajos prácticos de la cátedra (los "problemas prácticos" que cita el texto).
10. **Isoparamétricos, axilsimétrico, bandas finitas, 3D:** solo descripción. Sin integración numérica (Gauss) ni jacobiano en el libro: no alcanza para implementarlos.
11. **Dimensión del problema vs. 3D del fuselaje:** ver 5.2, la membrana espacial y la conexión con pórtico 3D requieren decisiones nuevas.
12. **Preguntas para el usuario:** ¿tensión o deformación plana?; ¿unidades de las cargas másicas?; ¿quiere LST/Q4 además del TTC?; ¿generador de malla propio o carga manual/CSV de otro mallador?; ¿suavizado de tensiones nodales (no está en el libro)?; ¿le interesa la membrana espacial para piel de fuselaje?
