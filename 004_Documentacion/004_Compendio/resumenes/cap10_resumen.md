# Capítulo 10 – Vigas de pared delgada (PDF págs. 142-165, pág. interna 10-1 a 10-24)

Resumen para Struttura. Todas las fórmulas fueron leídas sobre la imagen de la página. Las verificaciones numéricas marcadas "(verif. propia)" las hice con un prototipo Python (no son del libro). Notación del libro: x = eje de la viga; (y, z) o (y*, z*) = ejes principales; (η, ξ) = ejes principales en secciones cerradas; G = baricentro; C = centro de corte; Γ = área encerrada por la línea media; β = dθ/dx; JR = módulo torsional; Iω = inercia sectorial.

## 1. Qué resuelve y para qué sirve

Da las propiedades y tensiones de vigas de pared delgada (abiertas y cerradas): centro de corte, flujos de corte por esfuerzo de corte (Jourawski/Jourasky) y por torsión (Bredt, Saint Venant), y torsión con alabeo restringido (Vlasov: tensión axial secundaria, bimomento). En diseño sirve para: (a) saber dónde aplicar la carga para no torsionar; (b) calcular el JR real de un perfil (los abiertos son ~100 veces más blandos que los cerrados); (c) tensiones de corte en uniones soldadas/remachadas; (d) detectar cuándo el alabeo restringido agrega tensiones normales (perfiles abiertos empotrados). Para tubos circulares y cerrados "gordos" (caso típico de fuselaje tubular) casi todo se reduce a Bredt y no hay alabeo.

## 2. Fórmulas y algoritmos clave

(Pág. = página del PDF; ec. = número del libro.)

**2.1 Flexión compuesta (ec. 1, 3; pág. 142-143).** σx = N/A + (My/Iy) z − (Mz/Iz) y (ejes principales por G). La ec. (3) le suma un término σ(T, s, β) = tensión axial secundaria por alabeo (ec. 37/41/91).

**2.2 Sección cerrada unicelular (págs. 143-144).**
- q = τ t = constante en el contorno (4); T = 2 Γ q (6); q = T/(2Γ) (7a); τ = T/(2Γ t) (7c).
- β = (q/(2GΓ)) ∮ ds/t = T/(4GΓ²) ∮ ds/t (11); β = T/(G JR) (12b).
- JR = 4Γ² / ∮(ds/t) (13a); con t constante JR = 4Γ² t / perímetro (13b).
- Con aletas abiertas pegadas: JR = 4Γ²/∮(ds/t) + Σ ∫ (1/3) ts³ ds (14).
- Error de Bredt para tubo circular con t = 0,2 r_m: τmax 8 % por debajo, β 1 % por exceso (verif. propia: 8,2 % y 1,0 %).
- Comparación (Fig. 3, pág. 144): tubo r_m = 10, t = 1: JR cerrado / JR abierto = 3 (r_m/t)² = 300; τmax abierto / τmax cerrado = 3 r_m/t = 30 (verif. propia: correcto).

**2.3 Multicelular (págs. 145; ec. 15-22).**
- Flujo en tabique compartido q3 = q1 − q2 (15) (como corrientes de malla).
- Todas las células giran igual: β = βi = (1/(2GΓi)) ∮ qi/t ds (16); T = 2 Σ qi Γi (18).
- Sistema lineal: se define β̄ = 2Gβ y q̄i = qi/β̄ (19). De (16): C q̄ = Γ (20), con Cii = ∮_celda ds/t y Cij = −∫_pared común ds/t (el libro no define explícitamente cij; es lo que resulta de (16) con flujo neto en el tabique). De (18): T = 2 β̄ Σ Γi q̄i, o sea β̄ = T/(2 Σ Γi q̄i) y qi = β̄ q̄i (21). JR = 4 Σ Γi q̄i (22), con β = T/(G JR).
- (Verif. propia: dos células cuadradas iguales, de lado s=100, t=5 en todas las paredes: q̄1 = q̄2 = 166,67, tabique sin flujo, JR = 1,3333e7 mm⁴ = JR de la sección unicelular 2s×s.)

**2.4 Área sectorial y propiedades sectoriales (págs. 146-147).**
- dω = r ds, ω(s) = ∫ r ds (23) = 2 × área barrida desde el polo P; positivo antihorario. Cada polo y punto inicial dan un diagrama distinto.
- Mω = ∫ ω t ds (24); Sω^x = ∫ y ω t ds, Sω^y = ∫ x ω t ds (25); Iω = ∫ ω² t ds (26).
- Diagrama principal (secciones abiertas): polo = centro de corte (27); ω = ω1 − ω0 (28); ω0 = (1/A) ∫ ω1 t ds (30) para que Mω = 0. Si hay eje de simetría basta partir del eje de simetría.
- Verif. propia con la Fig. 6b (pág. 146): polo en P=(2a,−a), inicio I=(2a,0): ω = 4a² en el extremo del ala superior y −a² en el extremo del tramo derecho. Coincide con el libro.
- Fórmulas elementales para tramos rectos (derivación propia, exactas): Δω = (yi−yp)(zj−zp) − (yj−yp)(zi−zp) por tramo; ∫ ω² t ds = (t l/3)(ωi²+ωiωj+ωj²); ∫ z ω t ds = (t l/6)[(2zi+zj)ωi + (zi+2zj)ωj].

**2.5 Alabeo (págs. 147-149; ec. 31-41).**
- γ = rβ + du/ds (31); abierta: u = −β ω − u0 (33); cerrada: u = −β ω + (q/G)∫ds/t (34); con Bredt u(s) = (T/(2GΓ)) [−ω(s)/(2Γ) ∮ds/t + ∫0s ds/t] (35).
- No alabean: secciones abiertas de segmentos concurrentes (ω ≡ 0, Fig. 8: L, T, cruz) y cerradas circular, cuadrada y rectangular con t_a/a = t_b/b (Fig. 9).
- σx = −E β' ω = −E θ'' ω (37), abierta. Cerrada (41): σx = (E/(2GΓ)) [−ω/(2Γ) ∮ds/t + ∫ ds/t] dT/dx; solo existe si T varía.

**2.6 Flujos de corte por esfuerzo de corte (págs. 150-152).**
- Jourawski (45): q(s) = −Qz Sy(s)/Iy*, Sy = ∫ z t ds desde el extremo libre; I* "consistente" (área concentrada en la línea media). Signo: q > 0 si apunta hacia s creciente. (46): superposición para ejes principales de una sección asimétrica.
- Cerrada simétrica: partir del punto de q = 0 sobre el eje de simetría (Fig. 13).

**2.7 Centro de corte.**
- Abierta con un eje de simetría: momentos de los flujos respecto a C = 0 (48). Canal (49): −F1 h/2 + F2 e − F3 h/2 = 0.
- Abierta general (50)-(53): ey* = −(1/Iy*) ∫ Sy*(s) r(s) ds (50) = Sω^y*/Iy* (51); ez* = −Sω^z*/Iz* (52), con ω calculado con polo G y Sω^y = ∫ z ω t ds, Sω^z = ∫ y ω t ds. Corolario (53): con polo en C, Sω = 0.
- Ejes no principales (54): ey = (Iz Sω^z − Iyz Sω^y)/(Iy Iz − Iyz²); ez = (−Iy Sω^y + Iyz Sω^z)/(Iy Iz − Iyz²). **Ver riesgos: los superíndices están cruzados respecto de (51)/(52).**
- Verif. propia (canal b=100 mm de ala, h=200 mm de alma, t=5; medidas de línea media; ala hacia +y): A = 2000 mm², yG = 25 mm del eje del alma, Iy = ∫z²dA = 1,3333e7 mm⁴, Iz = 2,0833e6 mm⁴, centro de corte a e = 3b²/(h+6b) = 37,5 mm del eje del alma, del lado opuesto a las alas (62,5 mm de G). La ec. (51) da exactamente eso. Con (54) literal y ejes principales da 0 (incorrecto).
- Cerrada asimétrica (55)-(57): estado I con q=0 en un punto A (Jourawski desde A) + estado II con qA constante. qA = −∮(qI/t)ds / ∮(1/t)ds (56) (β=0 por actuar en C). Luego ηc = ∮ q r ds (57) para corte unitario.
- Cerrada con corte y torsión (págs. 156-158): alternativa 1: qtot = (qIξ+qξA)+(qIη+qηA)+qT con qT = T/(2Γ) (58, 59); T respecto de C. Alternativa 2 (no requiere C): q = qξ + qη + q0 (60), q0 = [Σ Pi di − ∮(qξ+qη) r ds]/(2Γ) (61), momentos respecto de un punto cualquiera.

**2.8 Torsión con alabeo restringido, abierta (págs. 159-161; ec. 62-89).**
- Tq = −E Iω β'' (64); TSV = G JR β (65); Tq + TSV = T (66a) ⇒ E Iω β'' − G JR β = −T (66b).
- K² = G JR/(E Iω) (68); β'' − K² β = −K² T/(G JR) (67); en θ: θ'''' − K² θ'' = −K² T'/(G JR) (69).
- T cte.: β = B1 senh Kx + B2 cosh Kx + T/(G JR) (71). T' cte.: θ = C1+C2 x+C3 senh Kx + C4 cosh Kx + T' x²/(2GJR) (72).
- Voladizo, T en el extremo (75)-(87): β = (T/GJR)[tanh(KL) senh Kx − cosh Kx + 1] (79), θL = (TL/GJR)[1 − tanh(KL)/(KL)] (80), σx = −E (T K/(G JR)) [tanh(KL) cosh Kx − senh Kx] ω (82), máx en x=0: σx = −(E T K/(G JR)) tanh(KL) ω (83), τSV = (T t/JR)[tanh(KL) senh Kx − cosh Kx + 1] (85), τq (86)-(87). (Verif. propia: (79) = (T/GJR)[1 − cosh K(L−x)/cosh KL]. Es la solución clásica.)
- Ambos extremos con alabeo impedido (88)-(89): B2 = −T/(GJR); **B1 = +(T/GJR)(cosh KL −1)/senh KL (el libro imprime signo − en (88): error de signo, ver riesgos)**; θL = (TL/GJR)[1 + (cosh KL −1)²/(KL senh KL) − senh KL/(KL)] (89) = (TL/GJR)[1 − 2 tanh(KL/2)/(KL)] (simplificación propia). Verif. numérica: K=0,01, L=300, T/GJ=1 → θ = 118,970 (integración numérica = (89)).

**2.9 Solución numérica (págs. 162-164; ec. 90-120).**
- Bimomento B = −E Iω β' (90) (N·mm²); σx = (B/Iω) ω (91); B = ∫ σx ω dA (92); con cargas axiales puntuales B = Σ Fi ωi (93).
- Sistema de 1er orden en [Tq, B, β, θ]: Tq + GJR β = T (94); dTq/dx = K² B + T' (95); dB/dx = Tq (96); dβ/dx = −B/(EIω) (97); dθ/dx = β (98).
- Recurrencia trapezoidal (103)-(106): Tq,i+1 = {[1+(KΔx/2)²] Tq,i + Δx(T'i+1+T'i)/2 + K² Δx Bi} / [1 − (KΔx/2)²]; Bi+1 = Bi + Δx(Tq,i+1+Tq,i)/2; βi+1 = βi − Δx(Bi+1+Bi)/(2EIω); θi+1 = θi + Δx(βi+1+βi)/2. (Verif. propia de (103) por sustitución.)
- Tiro (shooting): V = V0 + α1 V1 + α2 V2 (108); en el empotramiento V1(0)=(1,0,0,0), V2(0)=(0,1,0,0); condiciones en x = L: B(L)=0 (110) y Tq + GJR β = T(L) (111) ⇒ sistema 2×2 (113) para α1=Tq(0), α2=B(0).
- Tensiones (114)-(116): σx = (B/Iω) ω; τSV = G β t; τq = −Tq Mω(s)/(Iω t).
- Torsor concentrado To: variante a) repartido en ±ε (117), variante b) salto Tq⁺ = Tq⁻ + To (118). Propiedades variables (119)-(120): dTq/dx = K²B + T' − β d(GJR)/dx; dB/dx = Tq − (dβ/dx) d(EIω)/dx.

**2.10 Anexo (pág. 165, ec. de la tabla; verificadas contra imagen).**
Caso 1 círculo: JR = πD⁴/32, τ = T D/(2JR). Caso 2 tubo: JR = π(D⁴−d⁴)/32 exacto; ≈ (π/4) dm³ e aprox. Caso 3 elipse (a, b = ejes completos, b>a): τA = 16T/(π b a²), JR = π a³ b³/(16(a²+b²)). Caso 4 triángulo equilátero: τ = 20T/a³, JR = a⁴/46,2. Caso 5 hexágono: τ = 5,7T/a³, JR = a⁴/8,8 (a = ? ver riesgos). Caso 6 rectángulo (b ≥ a, x = a/b): τA = T/(Cτ b a²), Cτ = 1/3 − 0,225x + 0,1x²; JR = Cβ b a³, Cβ = 1/3 − 0,211x + 0,0182x⁴; τB = τA(0,74 + x³ − 0,74x⁴). (Verif. propia: x=1 da Cβ=0,1402 y Cτ=0,2083, valores clásicos.) Caso 7 abierta: JR = (1/3)∫ t³ ds = Σ (1/3) l t³; τ = T t/JR. Caso 8 cerrada: ver (13).

## 3. Datos tabulados / gráficos / curvas a cargar

- No hay curvas ni tablas numéricas aparte del Anexo (pág. 165): 8 casos con fórmula cerrada. Se cargan como fórmulas (no tabla). Todos coeficientes ya están en forma polinómica (Cτ, Cβ del rectángulo); no hace falta interpolar.
- Coeficientes sueltos: 0,74 (τB/τA rectángulo, mínimo), 46,2 y 8,8 (triángulo/hexágono), 5,7 y 20 (tensión).
- Las Figs. 6, 8, 9, 20 son ilustraciones (útiles como casos de prueba cualitativos).

## 4. Ejemplos resueltos del libro

El capítulo **no trae ejemplos numéricos resueltos**. Solo hay datos numéricos sueltos que sirven de test:
1. Pág. 144, Fig. 3: tubo r_m = 10 mm, t = 1 mm: relaciones 300 y 30 (verificadas).
2. Pág. 144: tubo circular con t = 0,2 r_m: τ Bredt 8 % bajo el exacto; β 1 % alto (verificado: 8,2 % y 1,0 %).
3. Pág. 146, Fig. 6b: ω = 4a² y −a² (verificado). Las figs. 6c y 6d no las verifiqué.
4. Pág. 148-149, Fig. 9: secciones que no alabean (test cualitativo: ω-error u(s) ≡ 0).
Tests adicionales propuestos (calculados por mí, no del libro): canal 100×200×5 (arriba): Iω = 1,4583e10 mm⁶ (= t b³ h² (3b+2h)/(12(6b+h)), coincide), JR = 16666,7 mm⁴ (= t³(h+2b)/3), ω principal en nodos = ±6250 y ±3750 mm² (extremo de ala y encuentro ala-alma; el signo depende de la orientación). Perfil doble T simétrico: Iω = Iz h²/4. Dos células iguales (arriba). Voladizo KL = 3: θL·GJR/(T L) = 0,6683 (ec. 80) y 0,3966 con ambos extremos impedidos (ec. 89).

## 5. Propuesta de implementación en Struttura

**Tipo B (calculadora de secciones) con salida que alimenta al pórtico 3D, más una extensión opcional tipo A (elemento de alabeo).**

*B1. Calculadora de sección de pared delgada* (dificultad 3, tamaño mediano-grande).
- Entrada CSV por bloques: NODOS (id, y, z), TRAMOS (id, nodo_i, nodo_j, espesor t, opcional "arco": radio/centro para discretizar), MATERIAL (E, G, ν) opcional, CARGAS opcionales (N, My, Mz, Qy, Qz, T respecto de C o de G).
- Detección automática del grafo: árbol (abierta), un ciclo (unicelular), varios ciclos (multicelular).
- Salidas: A, G, Iy, Iz, Iyz, ejes principales, centro de corte (ec. 51/52 o 54 corregida), ω principal por nodo, Iω, JR (abierta: Σ l t³/3; cerrada: 4Γ²/∮ds/t; mixta con ec. 14; multicelular por 20-22), flujos q(s) y τ por Jourawski y Bredt (con q0 para cerrada, ec. 60-61), tensiones σ, τ en puntos, W, y estado del alabeo ("no alabea" si ω ≡ 0). Informe HTML con matrices, figura de la sección y diagramas ω y q.
- Conexión: genera el bloque SECCIONES del pórtico 3D (A, Iy, Iz, J = JR, y opcional "ey_C, ez_C" del centro de corte y Iω). Hoy el pórtico 3D usa nodos en baricentro; si C ≠ G hay que ofrecer un "offset" (brazo rígido del eje de corte al baricentro) o avisar que las cargas deben llevarse a C.
- Parte barata (1-2 unidades chicas): biblioteca del Anexo (8 casos) + tubos circulares/rectangulares exactos con espesor finito (JR exacto del libro).
- Dependencias: ninguna dura. Comparte con Cap. 11 (flujos cerrados, Bredt).

*A1. Extensión Vlasov del pórtico 3D (opcional, dificultad 4-5, tamaño grande).* Elemento de 14 gdl (7 por nodo: u, v, w, θx, θy, θz y θ' como gdl de alabeo). La ecuación (69) da la formulación; el libro propone integración numérica (ec. 99-113), pero en Struttura es más natural agregarlo al método de rigidez. No lo recomiendo hasta tener la calculadora B1 y un caso de uso real de perfiles abiertos empotrados. Alternativa más económica: calculadora de torsión de barra individual con alabeo (B2, dificultad 3, tamaño mediano) con las soluciones analíticas (79)-(89) y la recurrencia (103)-(113): entradas L, E, G, JR, Iω, T(x) por tramos, apoyos (alabeo libre/impedido).

**Qué aplica al fuselaje de tubos soldados:** tubos circulares y rectangulares cerrados no alabean (Fig. 9), por lo que basta JR de Bredt/exacto y τ = T/(2Γt). Útil para reemplazar el "J" a mano por JR exacto del tubo, y para verificar a torsión. Los perfiles abiertos (cartelas, ángulos, canales de herrajes) sí pueden necesitar el centro de corte y el alabeo. **Estructuras mecánicas generales:** toda la calculadora (ejes, bastidores con perfiles C, U, doble T).

## 6. Anexo teórico para los informes

Con referencia "Cap. 10, ec. N":
- Tensión por flexión compuesta (1) y tensión axial secundaria (3), (37), (91).
- Bredt: q = T/(2Γ) (7), β = T/(4GΓ²)∮ds/t (11b), JR (13), JR multicelular (22).
- Abierta: JR = ⅓Σ l t³ (Anexo caso 7), τmax = T tmax/JR.
- Área sectorial (23), ω principal (28), (30), Iω (26).
- Jourawski (45), centro de corte (51)-(52).
- Ecuación de la torsión con alabeo (66b), K (68), bimomento (90).
- Hipótesis a declarar: pared delgada, t ≪ dimensión, sección indeformable en su plano, Saint Venant/Vlasov, sin pandeo local, elástico lineal.

## 7. Riesgos, ambigüedades, supuestos a preguntar

1. **Ec. (88)**: el libro imprime B1 = −[T/(GJR)][cosh KL − 1]/senh KL. Con B2 = −T/(GJR) y β(L)=0 el signo correcto es +. La ec. (89) sí es consistente con el signo + (verificado numéricamente). Usar +.
2. **Ec. (54)** (ejes no principales): los superíndices de Sω están intercambiados respecto de (51)/(52). Con Iyz = 0, (54) da ey = Sω^z/Iy, pero (51) da ey = Sω^y/Iy; mi prototipo confirma (51) (canal: 62,5 mm; con (54) literal da 0). Implementar con la definición Sω^y = ∫ z ω t ds, Sω^z = ∫ y ω t ds y rederivar (54) a partir del sistema 2×2 en vez de copiarla.
3. **Notación de (25):** el libro usa "x" e "y" como ejes principales en el plano en (25), pero x es el eje de la viga en el resto del capítulo; Sω^x = ∫ y ω t ds y Sω^y = ∫ x ω t ds en (25) significan "distancia al eje" (y, x), mientras que (51) usa z*. Ambigüedad de nombre, no de fondo.
4. **Referencia cruzada:** pág. 149 y otras remiten a un "corolario al final de la Subsección 8.2"; en realidad está al final de 7.2 (ec. 53). Cap. 11 cita "(58) del Cap. 10" como Jourawski; Jourawski es la ec. (45) (la 58 es qT = T/2Γ).
5. **Signo de Jourawski (45):** el libro pone q = −Qz Sy/Iy*, pero Cap. 11 (43) lo escribe sin el signo menos. Hay que fijar una convención única: sentido de s, signo de ω (antihorario +), de r y de T.
6. **Definición de cij en (20):** no está explícita; la deduje de (16) (pared común con flujo neto qi − qj). Confirmar con un ejemplo del curso.
7. **Hexágono (Anexo caso 5):** no queda claro si "a" es distancia entre caras o entre vértices. Por la verificación aproximada (J ≈ 0,115 d⁴ con d entre caras) es entre caras; τ = 5,7 T/a³ no lo pude contrastar. No incluir sin confirmar fuente.
8. **Alcance de las fórmulas de Bredt:** exactas solo para t pequeño (el propio libro da 8 % de error con t = 0,2 r). Para tubos de fuselaje (t/r ≈ 0,05-0,1) el error es pequeño; para tubos gruesos usar las fórmulas exactas del Anexo (caso 2).
9. **Aproximación de t³ en JR abierto:** ⅓Σ l t³ ignora el aumento por radios de acuerdo y las alas con espesor variable; preguntar si se quiere el factor de forma (~1,1-1,3 en perfiles laminados) o el valor del catálogo.
10. **El pórtico 3D actual ignora alabeo:** conviene preguntarle al usuario si le sirven perfiles abiertos empotrados, y si quiere advertir cuando Iω ≠ 0 y hay empotramiento que impide alabeo ("la teoría de Saint Venant subestima la rigidez a torsión").
11. **Centro de corte vs. centro de gravedad en el pórtico 3D:** el modelo 12×12 supone ambos coincidentes; los perfiles abiertos asimétricos requieren excentricidad o carga trasladada a C con torsor agregado.
12. **Teoría de pared delgada vs. tubos reales:** para A, Iy, Iz de tubos preferir fórmulas exactas π/64(D⁴−d⁴); la versión de línea media es un sustituto aproximado. Preguntar cuál quiere por defecto.
