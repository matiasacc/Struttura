# Capítulo 11 – Vigas compuestas y estructuras con recubrimiento resistente (PDF págs. 166-181, pág. interna 11-1 a 11-16)

Todas las fórmulas fueron leídas sobre imagen. "(verif. propia)" = chequeo mío con cuentas/prototipo, no del libro. Notación: A_i = área de cordón (platabanda, larguero), t = espesor del panel (alma), q = flujo de corte, Γ = área encerrada, h = altura, d = distancia entre montantes.

## 1. Qué resuelve y para qué sirve

Es la teoría "semi-monocoque" aeronáutica: un alma delgada (panel) que solo transmite corte, más cordones/largueros que toman la flexión como fuerzas axiales concentradas. Con esa idealización los flujos de corte son constantes en cada panel y todo se resuelve con estática, Jourawski y Bredt: flujos en paneles, centro de corte, torsión de cajones multicelulares, viga Wagner (campo de tensión diagonal poscrítico), ancho efectivo de paneles comprimidos y análisis de cuadernas. En diseño sirve para dimensionar uniones alma-cordón (remaches/soldadura), verificar paneles, montantes y largueros, y estimar el momento flector último de un fuselaje o ala con revestimiento resistente.

## 2. Fórmulas y algoritmos clave

**2.1 Teoría simplificada (pág. 166).** Hipótesis: alma solo corte; cordones toman toda la flexión; el área del alma se ignora en Iy y en el momento estático, así q es constante en cada panel. Ejes principales obligatorios para Jourawski (pág. 170).

**2.2 Almas planas, casos 1-4 (págs. 166-168).**
- Caso 1 (voladizo, 2 cordones A1, A2, carga Q): q = Q/h; F1 = Q x/h; F2 = −Q x/h; σi = ∓Fi/Ai (1). Atención al signo: en la Fig. 1 la Q apunta hacia arriba y el cordón superior está comprimido; en la Fig. 3 (caso 2) la Q apunta hacia abajo y el cordón superior está traccionado.
- Caso 2 (3 cordones): ȳ(A1+A2+A3) = A1(a+b) + A2 b; I = ΣAi ai²; q1 = Q A1 a1/I; q2 = q1 + Q A2 a2/I; σi = Q x ai/I; Fi = σi Ai (2). (Verif. propia: A1=A2=A3=100 mm², a=b=100 mm, Q=1000 N: ȳ=100, a1=100, a2=0, a3=−100, I=2e6 mm⁴, q1=q2=5 N/mm, F1=5x N con x en mm.)
- Caso 3 (sección variable, Fig. 5, pág. 168): no vale teoría de vigas; solo equilibrio. h = 20 + 0,4x; q = 50 P/[h (50 + x)] (momento respecto de A, vértice de intersección de cordones; la imagen dice (50+x), el texto extraído dice "−"); F2 = P x/h; F1 = 1,077 F2 = F2/cos θ con tgθ = 0,4. El libro deja la solución "como ejercicio". (Verif. propia: x=0: q = P/20 y q h = P; x=100: h=60, q = P/180, q h = P/3, F2 = 1,667 P, F1 = 1,795 P; la componente vertical de F1 es 2P/3, suma P. Unidades de la figura no indicadas.)
- Caso 4 (viga Wagner simplemente apoyada, Fig. 6): vale teoría de vigas con M(x), Q(x); alternativa por cuerpo libre.

**2.3 Desplazamientos (págs. 168-169).** PTV: δ = ∫ M̄ M/(EI) dx + ∫ Q̄ Q/(Ac G) dx (3). Castigliano con W* = Σalma ∫ (1/2G)(q/t)² h t dx + Σcordones ∫ (1/2E)(F/A)² A dx, δ = ∂W*/∂X |X=0 (4).

**2.4 Almas curvas (págs. 169-171).**
- q = Qx/AB (5): el flujo de un panel curvo entre cordones A y B solo depende de la cuerda; Qy = 0.
- Excentricidad del centro de corte: e = 2Γ/AB (6) = 2 y_m (Γ = área entre arco y cuerda). Con 3 cordones y 2 paneles curvos: e1 = 2Γ1/h1, e2 = 2Γ2/h2 (Fig. 9); centro de corte en la intersección de las dos rectas de acción.
- Abierta general: Fi = qi li; Q e = Σ Fi di (7). Simétrica con 3 paneles: Q e = F2 d ⇒ e = q2 ℓ d/Q (8). Con áreas barridas: Q e = Σ 2Γi qi ⇒ e = (2/Q) Σ Γi qi (9)-(10) (Γi = triángulo entre el panel y el punto de momentos).

**2.5 Cerrada simétrica (págs. 171-173).**
- Estado I (q=0 en un panel de referencia, Jourawski desde ahí) + Estado II (q0 constante): qi = qIi + q0 (11, 15).
- Q conocido a distancia d de un punto P: Q d = Σ 2Γi (qIi + q0) (13) ⇒ q0 = (Q d − 2 Σ Γi qIi)/(2Γ) (14).
- Giro: β = (1/(2GΓ)) Σ qi li/ti (16).
- Centro de corte (β=0, Q aplicado en C): q0 = −Σ qIi li/ti / Σ li/ti (17); e = (2/Q) Σ Γi qi (19). Es la misma ecuación (56) del Cap. 10.

**2.6 Cerrada asimétrica (págs. 173-175; ec. 20-25).** Idéntico al Cap. 10 pero con sumatorias: qξA = −Σ qIξi li/ti / Σ li/ti (20); qT = T/(2Γ) (21); qi = (qIξi+qξA)+(qIηi+qηA)+qT (22); alternativa 2 sin centro de corte: qi = qξi + qηi + q0, q0 = [Σ Pk dk − Σ 2Γi (qξi+qηi)]/(2Γ) (24). Centro de corte: Qξ ηC = Σ 2Γi qξi; −Qη ξC = Σ 2Γi qηi (25).

**2.7 Viga Wagner / campo de tensión diagonal (págs. 175-176).**
- σ = Q/(h t sen α cos α) (26); F1 = −Q x/h − Q/(2 tg α); F2 = +Q x/h − Q/(2 tg α) (27, 28) (la imagen de (27) dice "−Qx/h"; Q positiva hacia arriba).
- Fuerza en montantes: FV = Q d tg α/h (29); los ensayos dan valores "bastante inferiores".
- Primer montante (30): N = −FV/2 − Q x/h; Q(x) = Q/(2 tg α) − Q x/(h tg α); M = M0 − Q x/(2 tg α) + Q x²/(2 h tg α). Se puede ignorar M0 (conservador).
- Ángulo: (tg α)⁴ = (1 + t h/Aplat)/(1 + t d/Amont) (31) ⇒ α ≈ 45° si h/Aplat ≈ d/Amont (32). El propio libro avisa: teoría resumida, "poco exacta", solo valores tentativos.
- (Verif. propia: ángulo 45° ⇒ σ = 2Q/(h t); FV = Q d/h.)

**2.8 Ancho efectivo (págs. 177-179).**
- Área efectiva Ā = Ar + b t (33); pandeo de placa σcrit = K π² E t²/(12(1−ν²) b²) (34), K ≈ 4 apoyada con a/b > 1 (remite a Cap. 6, ec. 40).
- be = (1/σmax) ∫0b σ(x) dx (35). Von Kármán: be = b √(σcrit/σmax) para σmax ≥ σcrit (36); con ν=0,3: be = 0,95 t √(K E/σmax) (38); con K=4: be = 1,9 t √(E/σmax) (39). (Verif. propia: 0,95 = π/√(12·0,91) ✓.)
- Tensión máxima por panel con la fórmula de flexión σmax = M ymax/I (40) con I y eje neutro que dependen de be: iterar. Área efectiva del larguero i: Ai = (Ar)i + (t be/2)i + (t be/2)i+1 (41). Último momento: fijar σMAX = menor{σflu,rec ; σcrit,lar} (42) y iterar la posición del eje neutro; "converge en 3 o 4 pasos". Ej. figura 26: sección circular con 32 largueros y 32 paneles (sin valores).
- (Verif. propia, número de referencia: acero E=210000 MPa, t=1 mm, σmax=300 MPa ⇒ be = 1,9·1·√700 = 50,3 mm.)

**2.9 Cuadernas (págs. 179-181; ec. 43-44).** Cuaderna = pórtico plano cerrado cargado por P y el flujo de corte reactivo del revestimiento. Carga simétrica: mitad con empotramientos deslizantes + restricción de cuerpo rígido (Figs. 28-31). Carga asimétrica (P a distancia a del eje de simetría): suma de simétrico (P/2 en cada lado: q1 = Q Sy/Iy, Jourawski) y antisimétrico (T = P d; q2 = P d/(2Γ), Bredt), S = S1+S2 a la izquierda y S1−S2 a la derecha (Fig. 33). El flujo que "sostiene" a la cuaderna depende del revestimiento, no de la cuaderna. Recomienda discretizar el panel en áreas concentradas sumadas a los largueros.

## 3. Datos tabulados / gráficos a cargar

- Sin tablas ni curvas numéricas. Todo son fórmulas. Constantes: K ≈ 4 (placa apoyada), ν = 0,3, 0,95 y 1,9 (ancho efectivo), 45° (α), 1,077 (caso 3, depende de geometría).
- Nota: K de Cap. 6 (ec. 40) se necesita para otras condiciones de borde (el Cap. 11 solo usa K ≈ 4). Si se quiere K(a/b, bordes) hay que leerlo del Cap. 6 (fuera de mi asignación).
- Figs. 25-26 (distribución de tensión pospandeo, 32 largueros): cualitativas.

## 4. Ejemplos resueltos del texto

El capítulo **no trae ejemplos numéricos resueltos**. Solo datos y resultados parciales: caso 3 (Fig. 5, pág. 168: h = 20+0,4x; q = 50P/[h(50+x)]; F2 = Px/h; F1 = 1,077F2) y casos de la Fig. 26 (32 largueros, sin cifras). Para tests propongo (calculados por mí): (a) el caso 2 de arriba; (b) caja de 4 cordones iguales B de lado s con Q vertical en C: q = Q/(2s) en las dos almas verticales, q = 0 en las horizontales, e centrado (Jourawski + ec. 14/17); (c) torsión pura de una caja de 4 cordones: q = T/(2Γ) uniforme; (d) viga Wagner con α = 45° (σ = 2Q/(ht)); (e) be = 50,3 mm (arriba) con iteración de be/σmax en una viga de dos paneles.

## 5. Propuesta de implementación en Struttura

**Tipo B (calculadora de cajón semi-monocoque) + parte reutilizable del Cap. 10 (ver cap10_resumen.md); extensiones tipo A solo si surge el uso.**

*B3. Calculadora de sección de cordones y paneles* (dificultad 3, tamaño mediano; si se hace sobre B1 del Cap. 10, la parte nueva es chica).
- Entrada CSV: CORDONES (id, y, z, área), PANELES (id, cordón_i, cordón_j, espesor t, longitud de arco o "recto"/"Γ" si es curvo), CARGAS (Qy, Qz, T o punto de aplicación (y,z)), MATERIAL (E, G).
- Salidas: G, ejes principales, I sin alma (teoría simplificada), flujos qi por panel (abierta: Jourawski; cerrada: q0 por 14/17/24), centro de corte, giro β (16), fuerzas en cordones F(x), carga por remache/soldadura por mm (= q), verificación de panel a corte (τ = q/t vs. τcrit de placa del Cap. 6).
- Conexión: comparte con B1 (Cap. 10) el motor de Jourawski/Bredt; aquí la sección es un caso especial de B1 con "tramos con t ≠ 0 pero momento estático aportado solo por cordones". Es un buen primer paso para B1 porque las cuentas son sumatorias simples.
- *B4. Ancho efectivo/flexión de revestimiento resistente:* iteración (36), (38)-(42) para una sección de cordones + paneles con M dado. Dificultad 3, tamaño mediano.
- *B5. Viga Wagner:* entradas h, d, t, Aplat, Amont, Q: salidas α, σ, F1, F2, FV, diagramas del montante (26-32). Dificultad 2, tamaño chico. El libro dice que es de resultado "tentativo".
- *A (cuadernas):* el pórtico plano ya existente resuelve el marco; faltan (i) el generador de cargas (flujo reactivo q = Q S/I + Bredt) y (ii) las condiciones de apoyo isostáticas contra cuerpo rígido (Fig. 31). Dificultad 2-3 sobre lo existente; tamaño chico-mediano. Alternativa C: solo texto.

**Tipo C inmediato:** anexo teórico sobre idealización semi-monocoque.

**Aplicación al fuselaje tubular soldado y estructuras mecánicas:** la teoría no aplica directamente a un fuselaje de tubos de acero soldados (no hay revestimiento resistente), pero sí si el fuselaje lleva revestimiento de chapa/tela/fibra que trabaje en corte, o para el ala (largueros + costillas + recubrimiento) y herrajes. La parte de ancho efectivo y viga Wagner es la de mayor valor aeronáutico (peso). En estructuras mecánicas generales sirve para cajones de chapa rigidizada, tolvas, carrocerías.
Dependencias: Cap. 10 (Jourawski, Bredt, centro de corte), Cap. 6 (pandeo de placas, ec. 40), pórtico plano (cuadernas).

## 6. Anexo teórico para los informes

Con referencia "Cap. 11, ec. N": hipótesis de la teoría simplificada (§2); q = Q/h y Fi = M/h para dos cordones (1); Jourawski sobre cordones (2); q de panel curvo (5) y excentricidad (6); cerrado: q = qI + q0 con q0 por (14)/(17)/(24); β (16); viga Wagner σ (26), α (31); área efectiva y ancho efectivo (33), (36), (39); referencia a Cap. 10 (Bredt y Jourawski).

## 7. Riesgos, ambigüedades, supuestos a preguntar

1. **Sin ejemplos numéricos.** No hay resultados finales para validar; tests propios (calculados con las fórmulas del libro) y, para ancho efectivo, comparar contra el procedimiento iterativo manual.
2. **Cap. 11 (43) vs. Cap. 10 (45):** (43) escribe q1 = Q Sy/Iy (sin signo) y dice "Cap. 10 (58)", pero Jourawski es (45) con signo menos y la (58) es la de Bredt qT. Fijar convención de signos propia.
3. **Ec. (30), primer montante:** N = −FV/2 − Q x/h pero la segunda igualdad dice −Q(d tgα/(2h) − x/h): el signo de x/h no es consistente (debería ser +, porque en x=h la fuerza axial vale −(Q + FV/2), coincide con la fuerza en el extremo de la Fig. 22). Es erratas de signo; usar la primera forma.
4. **Dirección de Q:** en la Fig. 1 apunta hacia arriba (cordón superior comprimido), en la Fig. 3 hacia abajo (superior traccionado). Hay que definir positivos propios.
5. **Fig. 5 (50+x vs 50−x):** el texto extraído lee "50−x", la imagen dice 50+x; vale 50+x (momento respecto de A, verificado: qh = P en x=0).
6. **Hipótesis de a/b > 1 y K ≈ 4** para el ancho efectivo: para otros bordes (empotrados, a/b chico) K cambia. Preguntarle al usuario si quiere K de tabla (Cap. 6).
7. **Ancho efectivo**: la fórmula de Von Kármán es aproximada y vale sobre el pandeo local del panel; hay que comparar con el pandeo del conjunto placa-larguero (el libro lo señala) y el pandeo del larguero (42). Fuera del alcance de la calculadora salvo que se agregue Euler/Johnson.
8. **Viga Wagner**: el libro advierte que los resultados son "poco exactos" y FV ensayado es menor al de (29). No usarla para certificar un diseño sin factor de seguridad; ofrecerla como estimación.
9. **Idealización:** áreas de cordón concentradas ⇒ no se capta la distribución real de tensión en el cordón ni la inercia propia del larguero. Preguntar si se prefiere la inercia propia de cada larguero.
10. **Cuadernas**: el estado de solicitación depende de cómo se discretiza el revestimiento; el libro recomienda áreas concentradas. Preguntar si se quiere acople con el pórtico plano existente.
11. **Unidades de la Fig. 5:** el libro no da unidades ni valor de P.
