# Capítulo 9 – Vigas curvas (PDF págs. 131-141; libro 9-1 a 9-11)

Referencias: "(n)" = ecuación del capítulo; p.NNN = página del PDF (libro 9-k = PDF 130+k). Verificaciones propias: (14) cumple equilibrio (1)-(2) analíticamente; (16) y (38) re-deducidas; Tabla 1 reproducida con (14); Tabla 2 (10 secciones) verificada por integración numérica; Tabla 3 y (25) verificadas numéricamente.

## 1. Qué resuelve el capítulo y para qué sirve

Da la tensión normal circunferencial σθ (hipérbola, no lineal) en vigas de eje curvo (secciones simétricas, cargas en el plano de simetría) cuando el radio de curvatura R es comparable con la altura h (R/h < 5; "curvatura grande" R/h<2): fórmula de flexión compuesta para viga curva, posición del eje neutro, secciones compuestas y tabla de A, R y Am para secciones usuales; tensión radial σr (importante en almas delgadas); corrección de Bleich para alas de secciones T y doble T (alas reducidas y tensión σz de flexión del ala); ovalización y factores k, i de codos (tubos curvos), con y sin presión interior; y cálculo de desplazamientos por Castigliano. Sirve para ganchos, anillos, eslabones, prensas en C, arcos mecánicos, codos de tubería y tubos curvados de estructuras soldadas.

## 2. Fórmulas y algoritmos clave

Notación: O centro de curvatura, r radio de una fibra medido desde O, R radio del baricentro, Rn radio del eje neutro, a radio interior, c radio exterior, h altura, A área, Am área modificada, e = R - Rn excentricidad. Convención de signos: **N positivo = tracción; Mz positivo = tracción en las fibras del radio interior (el momento tiende a disminuir la curvatura, a "abrir" la viga)** (p.133; confirmado en p.141).

### 2.1 Tensión circunferencial (secc. 2, p.132-134)
- (1)-(2) equilibrio: ∫σθ dA = N ; ∫σθ (R - r) dA = Mz.
- (3)-(5) cinemática y Hooke: εθ = (Rn/r - 1) ω, ω = Δ(dθ)/dθ; σθ = E ω Rn/r - E ω (se desprecia σr; (6)-(7) justifican).
- (8)-(9): N = Rn E ω Am - E ω A ; Mz = Rn E ω (R Am - A). (10) **Am = ∫A dA/r**; (11) Am ≈ A/R pero Am > A/R.
- (12) Rn E ω = Mz/(R Am - A); (13) E ω = Am Mz/(A (R Am - A)) - N/A.
- **(14) σθ = N/A + [Mz/(R Am - A)] · (1/r - Am/A)**. Es hiperbólica en r. Verificado: ∫σθ dA = N y ∫σθ(R-r)dA = Mz. Máximos en las fibras extremas r = a (interior) y r = c (exterior).
- (15) viga recta: σ = N/A + Mz y/Iz (límite R/h → ∞).
- (16) eje neutro (σθ=0): **Rn = A / [ Am + (A - R Am) N/Mz ]**; (17) flexión pura: **Rn = A/Am**.
- Precisión numérica: R Am - A ≈ I/R² es una diferencia de números casi iguales (el libro lo advierte en p.133-134). Para R/h grandes calcular Am con la forma estable (p.ej. rectángulo: Am = b ln(c/a) = 2 b atanh(h/(2R)); círculo: Am = 2π b²/(R + sqrt(R²-b²))); para R/h > ~20-30 usar (15) o series.
- (18) secciones compuestas: A = ΣAi, Am = ΣAmi, R = Σ(Ri Ai)/A (aditividad de la integral).
- Tabla 1 (p.133), flexión pura de sección rectangular: relación de σθ máx. de viga curva (14) y de viga recta (15) respecto de la teoría de la elasticidad (exacta): R/h = 0,75: 1,012 y 0,526 (error recta 47,4 %); 1: 0,997 y 0,654 (35,6 %); 2: 0,997 y 0,831 (16,9 %); 5: 0,999 y 0,933 (6,7 %); 10: 1,000 y 0,967 (3,3 %).
- Tabla 2 (p.135): A, R y Am (Am = ∫dA/r; a radio interior, c exterior, o distancias desde O) para: (1) rectángulo b×(c-a): A = b(c-a), R = (a+c)/2, **Am = b ln(c/a)**; (2) triángulo (base b en r=a, vértice en r=c): A = b(c-a)/2, R = (2a+c)/3, Am = b c/(c-a) ln(c/a) - b; (3) trapecio (b1 en a, b2 en c): A = (b1+b2)(c-a)/2, R = [a(2b1+b2) + c(b1+2b2)]/(3(b1+b2)), Am = (b1 c - b2 a)/(c-a) ln(c/a) - b1 + b2; (4) círculo radio b, centro a distancia R de O: A = π b², **Am = 2π (R - sqrt(R²-b²))**; (5) elipse (semiejes b axial, h radial): A = π b h, Am = (2π b/h)(R - sqrt(R²-h²)); (6) corona/tubo (b1 exterior, b2 interior): A = π(b1²-b2²), **Am = 2π( sqrt(R²-b2²) - sqrt(R²-b1²) )**, forma estable Am = 2π(b1²-b2²)/(sqrt(R²-b2²)+sqrt(R²-b1²)) (idéntica algebraicamente); (7) elipse hueca: A = π(b1 h1 - b2 h2), Am = 2π( b1R/h1 - b2R/h2 - (b1/h1) sqrt(R²-h1²) + (b2/h2) sqrt(R²-h2²) ); (8) segmento circular lado exterior (θ semiángulo, círculo de radio b con centro a distancia a): A = b²θ - (b²/2) sen2θ, R = a + 4b sen³θ/(3(2θ - sen2θ)), Am = 2aθ - 2b senθ - π sqrt(a²-b²) + 2 sqrt(a²-b²) asen[(b + a cosθ)/(a + b cosθ)] si a > b, y Am = 2aθ - 2b senθ + 2 sqrt(b²-a²) ln[(b + a cosθ + sqrt(b²-a²) senθ)/(a + b cosθ)] si a < b; (9) segmento circular lado interior: R = a - 4b sen³θ/(3(2θ - sen2θ)), Am = 2aθ + 2b senθ - π sqrt(a²-b²) - 2 sqrt(a²-b²) asen[(b - a cosθ)/(a - b cosθ)]; (10) media elipse (plano a distancia a, curva hacia O): A = π b h/2, R = a - 4h/(3π), Am = 2b + (π b/h)(a - sqrt(a²-h²)) - (2b/h) sqrt(a²-h²) asen(h/a). Todas verificadas contra integración numérica (casos a>b y a<b, y varios θ); el caso (7) se verifica por ser diferencia de dos de tipo (5). Para T, doble T, L, canal: sumar rectángulos con (1) y (18).

### 2.2 Tensión radial σr (secc. 3, p.136)
- (19) F = ∫ₐʳ σθ dA ; (20) σr = F/(t r) (equilibrio radial del elemento ABCD; sen(dθ/2) ≈ dθ/2), donde **t = ancho de la sección a la distancia r** (no es el espesor del tubo).
- **(21) σr = N A*/(t r A) + Mz (A A*m - A* Am)/(t r A (R Am - A))**, con (22) A*m = ∫ₐʳ dA/r y A* = ∫ₐʳ dA (porción de sección entre el radio interior a y r). σr = 0 en r = a; máximo cerca del eje neutro; vuelve a 0 en r = c si N = 0. Error respecto de elasticidad < 6 % para rectangulares con R/h > 1, del lado conservador.
- Importa en secciones de alma delgada (T, doble T); en llenas es despreciable.

### 2.3 Corrección de Bleich para T y doble T (secc. 4, p.136-139)
- Fenómeno: las fuerzas de las alas flexionan las alas hacia afuera; las tensiones σθ en los extremos de las alas bajan y en la zona del alma suben.
- **(23) b'i = 2 (αi ℓi) + t**: alas reducidas (ℓi = voladizo de semiala, t = espesor del alma). Se usa (14) con la sección reducida.
- **(24) σz = -β σθ** (tensión de flexión del ala; σθ de (14) en la sección reducida, con el radio a mitad de espesor del ala).
- (25)-a **α = (1/(λℓ)) (senh z + sen z)/(2 + cosh z + cos z)**; (25)-b **β = sqrt3 (cosh z - cos z)/(2 + cosh z + cos z)**; (26) **λ = [3(1-ν²)/(r²ω²)]^¼ , z = 2λℓ**. Variable de entrada ℓ²/(rω) (ω = espesor del ala, r radio del ala medido hasta su mitad, ν=0,3). Cada ala tiene su r, α y β (el ala interna tiene menor α).
- Tabla 3 (p.138), ν = 0,3, para ℓ²/(rω) = 0,2; 0,4; 0,6; 0,8; 1,0; 1,2; 1,5; 2,0; 3,0; 5,0: α = 0,979; 0,923; 0,850; 0,776; 0,708; 0,651; 0,583; 0,506; 0,422; 0,341 ; β = 0,555; 1,018; 1,347; 1,550; 1,661; 1,713; 1,732; 1,711; 1,674; 1,692. Reproducidos por (25) (3 decimales).
- (27)-(28) semiala muy larga (ν=0,3): lim(αℓ) = 0,778 sqrt(rω) (=1/λ, demostrado) ⇒ **b' = t + 1,56 sqrt(rω)** (ancho efectivo de la chapa que colabora con un anillo de refuerzo; se usa en recipientes con presión exterior, conecta con Cap. 7 6.2.3).
- Perfil rectangular hueco (Fig. 10): hay un efecto Bleich análogo pero el libro dice que **no hay fórmula** de corrección.

### 2.4 Codos con y sin presión interior (secc. 5, p.139-140)
- Ovalización (Von Kármán 1911): la sección se ovaliza, baja la rigidez y sube la tensión máxima, cualquiera sea el signo del momento.
- (29) I_nom = π r_m³ t (tubo recto, r_m radio medio, t espesor); **I_o = I_nom/k_o**.
- (30) M̄ = sqrt(M1² + M2² + T²) (momento resultante: dos flexiones y torsión; "criterio de Tresca").
- (31) σ_nom = M̄ r_m/I_nom ; **σ_o = i_o σ_nom**.
- (32) **λ = R t/(r_m² sqrt(1-ν²))** (R = radio del codo al eje, no confundir con las λ de Bleich/Croll), **γ = R/r_m**.
- (33) **k_o = 1,66/λ**, para λ ≤ 1 (si λ > 1 no hay ovalización: k_o = 1).
- (34) **i_o = 2 λ^-0,667 (1 + 0,25/γ)**, para 0,05 ≤ λ ≤ 1.
- Con presión interior p: (37) ψ = p R²/(E r_m t); (35)-a k_p = k_o/(1 + 1,75 λ^-1,333 e^(-1,15(ψ-0,25))) ; I_p = I_nom/k_p ; (36)-a i_p = i_o/(1 + λ^-1,333 e^-(ψ-0,25)) ; σ_p = i_p σ_nom ; válidos para 0,05 ≤ λ ≤ 1 y 0 ≤ ψ ≤ 0,1. **ERROR probable (ver riesgos): tal como están impresas, con ψ = 0 no dan k_o ni i_o.**

### 2.5 Desplazamientos (secc. 6, p.141)
- **(38) W = ∫ Q²/(2 Ac G) R dθ + ∫ N²/(2 A E) R dθ + ∫ Am Mz²/(2 A E (R Am - A)) dθ - ∫ Mz N/(A E) dθ** (corte, axial, flexión, acoplamiento Mz-N). Re-deduje (38) a partir de (13) y (16): coincide (incluido el signo del acoplamiento con Mz positivo = reduce curvatura y N positivo = tracción). Ac = área de corte (no está definida en el texto).
- (39) u(X) = ∂W/∂X con fuerza ficticia X (se hace X=0 al final, o X=P si la carga ya existe en ese punto y dirección).
- (40) si R/h > 3: reemplazar los términos 3º y 4º de (38) por la flexión de viga recta ∫Mz²/(2EI) R dθ, error < 2 % en desplazamientos; (41) **u(X) = ∫ [Mz(X)/(EI)] [∂Mz(X)/∂X]|X=0 R dθ**. Si predomina flexión y R/h > 3 ⇒ (41) alcanza (se ignoran N y Q).
- Para T y doble T usar la sección reducida de Bleich en (38); en codos usar I_o de (29)-(35).

## 3. Datos tabulados / gráficos / curvas a cargar

| Dato | Pág. | Cantidad | Reemplazable por fórmula |
|---|---|---|---|
| Tabla 1 (R/h, cociente curva y recta/elasticidad, error %) | 133 | 5 filas × 3 | No (es dato de validación); la columna "viga recta" es 1/ratio de (14) vs (15) |
| Tabla 2 (A, R, Am de 10 secciones) | 135 | 10 secciones, ~35 expresiones | Es fórmula; se implementa en código (verificada). Es preferible integración numérica de rectángulos para perfiles generales |
| Tabla 3 de Bleich (α, β) | 138 | 10 × 2 | Sí: (25)-(26) (reproducen la tabla) |
| Fig. 9 (curvas α, β) | 138 | 2 curvas | Sí: (25)-(26) |
| Constantes de codos (33)-(37) | 140 | 4 expresiones | son fórmulas, pero (35)-(36) sospechosas |
No hay figuras de curvas a digitalizar.

## 4. Ejemplos resueltos del texto

El capítulo **no trae ejemplos numéricos resueltos.** Anclajes del libro:
1. Tabla 1 (p.133): con una sección rectangular (b=h=1) y flexión pura, (14)/(15) debe dar: inner(curva)/6M/(bh²) = 1,0121/0,526 = 1,924 en R/h=0,75; 0,997/0,654 = 1,5245 (R/h=1); 0,997/0,831 = 1,1998 (R/h=2); 0,999/0,933 = 1,0707 (R/h=5); 1,000/0,967 = 1,0341 (R/h=10). Lo calculé con (14) en la fibra interior: 1,9240; 1,5235; 1,1996; 1,0711; 1,0344 (diferencia ≤ 0,1 %, coincide). Fibra exterior/recta: 0,6515; 0,7300; 0,8531; 0,9370; 0,9676. Posición de Rn (con h=1): R/h=0,75 → Rn=0,6213 (e=0,1287); R/h=1 → 0,9102 (0,0898); 2 → 1,9576 (0,0424); 5 → 4,9833 (0,0167); 10 → 9,9917 (0,0083).
2. Tabla 3 de Bleich (p.138): 20 valores (ver arriba).
3. (28): 1,56 sqrt(rω) y (27): 0,778 sqrt(rω); α·ℓ → 1/λ.
4. p.133: error de viga recta 7 % a R/h=5; 35 % a R/h=1; 47 % a R/h=0,75.
Valores de referencia que calculé yo con las fórmulas (no del libro):
- Codo de tubo 25,4 × 1,65 mm (r_m = 11,875), R = 76,2, ν=0,3: λ = 0,9347; γ = 6,417; k_o = 1,776; i_o = 2,174; I_nom = π r_m³ t = 8680 mm⁴ ⇒ I_o = 4887 mm⁴.
- Codo de tubo 38 × 2 (r_m = 18), R = 114: λ = 0,7377; γ = 6,333; k_o = 2,250; i_o = 2,547.
- Sección rectangular b=1,h=1, R=2: a=1,5, c=2,5, A=1, Am = ln(5/3) = 0,510826; Rn = A/Am = 1,95760.

## 5. Propuesta de implementación en Struttura

**Fase 1, tipo B: calculadora "viga_curva" (CSV → informe HTML con paso a paso).**
- Entrada: PROYECTO; MATERIALES (E, nu, fy); SECCIONES (tipo: rectangulo(b,h) | circulo(d) | tubo(d,t) | trapecio | triangulo | elipse | T/doble T/canal/L como lista de rectángulos con (b_i, a_i, c_i) | generica(A,Am,R) | segmento/semielipse); GEOMETRIA (R, o a y c); ESFUERZOS (casos: N, Mz, Q, signo según convención del libro). Opciones: Bleich (ℓ, ω, t, r de cada ala), σr en el punto pedido, comparación con viga recta.
- Salidas: A, R, Am, Rn, e, σθ en cada fibra extrema y en una tabla de r, σr(r), σz (Bleich), CS vs fy con el criterio de falla del Cap. 2 (σθ y σr/σz forman un estado biaxial: σθ-σr o σθ-σz), gráfico hipérbola vs recta, error de la viga recta (Tabla 1).
- Dificultad: 2/5. Tiempo: **mediana** (secciones + Bleich + tests); **chica** si sólo rectángulo, círculo, tubo y suma de rectángulos.

**Fase 2, tipo A (extensión del pórtico plano y del 3D): elemento "arco circular".** Opción A1 (recomendada): bloque ARCOS (id; nodo_i; nodo_j; centro o R; sentido; material; seccion; n_tramos) que se expande en n barras rectas del solver existente (error < 2 % en desplazamientos si R/h > 3 según p.141), y post-proceso por barra que aplica (14) con N y Mz (de cada tramo) para dar σθ hiperbólica y las fibras extremas; marca "R/h < 5" y avisa si R/h < 2. Opción A2 (más fina): matriz de rigidez exacta del arco por Castigliano con (38) (flexibilidad 3×3 en el plano, luego rigidez 6×6 por transformación y, en el 3D, torsión): dificultad 4/5, tiempo grande. Dificultad A1: 3/5; tiempo mediana a grande (hay que mapear convención de signo de Mz del programa a la del libro, geometría de nodos intermedios y salida de tensiones).
- Dependencias: Cap. 2 (criterios de falla), Cap. 7 (anillos con ancho efectivo (28)), formación de tensiones del 3D existente (tensor), nada más.

**Fase 3 (opcional): codos (secc. 5)** como tipo de barra `codo` en el 3D: reduce I a I_nom/k_o y multiplica la tensión por i_o; **no implementar presión interior hasta resolver (35)-(36)**. Dificultad 2-3/5 (la lógica es simple pero requiere decidir cómo tratar el codo discretizado). Tiempo chica-mediana.

**Aplicación a fuselaje tubular soldado:** los tubos curvados (cuadros de motor, arcos de cabina, roll-bars, trenes de aterrizaje) tienen R/h grande (R/D ≈ 3-4, pared 1-1,6 mm): la teoría de curvatura (14) es casi viga recta (error < 7 % si R/h > 5) y lo que importa es la ovalización: ejemplo 25,4×1,65, R=76,2: la rigidez cae a 1/1,78 y la tensión sube ×2,17 respecto de la fórmula recta. En uniones soldadas de tubos curvos es un dato de diseño real. Para estructuras mecánicas generales: ganchos de grúa, anillos de carga, eslabones de cadena, prensas, arcos, bastidores en C, tuberías.

## 6. Anexo teórico para los informes

Ecuaciones: hipótesis (secciones planas, σr y τ despreciables), σθ viga curva (14) con convención de signos, eje neutro (16)-(17), Am y secciones compuestas (10), (18), Tabla 2; σr (21); Bleich (23)-(26); codos (29)-(34); Castigliano (38)-(41). Poner la tabla comparativa de error de viga recta (Tabla 1) para justificar la curva. Referencia: Cap. 9 del Compendio sin copiar.

## 7. Riesgos, ambigüedades y preguntas

- **(35)-(36) como están impresas son incoherentes:** k_p = k_o/(1 + 1,75 λ^-1,333 e^(-1,15(ψ-0,25))). Con ψ=0 (sin presión), λ=0,935 da k_p = 0,50 (k_o=1,78): "con presión" es menos de la mitad del valor sin presión; con ψ creciente 0 → 0,1 k_p sube (0,50 → 0,55) o sea la presión reduciría la rigidez, al revés de lo físico (la presión rigidiza); k_p<1 es imposible (menos flexible que el tubo recto). Lo mismo para i_p (0,87 con ψ=0). Falta casi seguramente el factor ψ (en la literatura, ASME/Rodabaugh, el denominador es 1 + c·ψ'·λ^-4/3...; exponente 4/3 = 1,333). Hay que consultar la fuente original antes de implementar.
- (34): i_o con (1 + 0,25/γ) y 2 λ^-0,667 (≈ 2 λ^-2/3): no hay forma de contrastar con el texto; parece derivado de Roark/Von Kármán. i_o es la tensión máxima (no el SIF de fatiga de ASME). Tener presente al compararlo con otras normas.
- (21) con N ≠ 0: da σr(c) = N/(t c) ≠ 0 en el borde libre exterior (porque F = ∫σθ dA = N). Es una limitación: sólo usar con Mz (o con N como aproximación); en un arco real N y Q varían con θ y eso equilibra el término.
- "t" en (20)-(21) es el ancho de la sección a la altura r (no el espesor del tubo ni del alma en general); "r" es radio desde O, no radio del tubo. La letra λ se usa con tres significados (Bleich (26), Croll en Cap. 7 y codos (32)); r_m ≠ r. En Bleich "ω" es el espesor del ala, que no es la ω de (4).
- (38): Ac (área de corte) no está definida. Hay que elegir A/κ.
- Sección compuesta: el libro dice que Am "debe calcularse con gran precisión" por la cancelación en R Am - A; en el código usar las formas estables o mpmath/decimal si R/h > 30.
- Para tubos (Tabla 2, #6) hace falta R > b1 (el tubo no puede contener a O). Para #8/#9 el segmento debe cumplir a + b cosθ > 0 (el libro los llama "sector circular" pero son segmentos).
- Las fórmulas suponen sección simétrica, carga en el plano de simetría y barra con curvatura constante en el plano; no cubre torsión (resortes helicoidales) ni curvatura variable ni arcos espaciales (el 3D con tubos curvos fuera del plano requiere discretización).
- Preguntarle al usuario: ¿qué signo de Mz usa en sus pórticos (para conectar con la convención del libro)? ¿le interesa más el arco discretizado en el solver o la calculadora de una sección? ¿aplicará los codos con presión interior (si es así, necesitamos la fuente de (35)-(36))? ¿Se usa σr/σz combinado con σθ para el CS (Von Mises/Tresca con tensión biaxial)?
