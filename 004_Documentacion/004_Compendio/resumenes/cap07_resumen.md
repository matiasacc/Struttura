# Capítulo 7 – Pandeo de cilindros delgados (PDF págs. 111-124; páginas del libro 7-1 a 7-14)

Convención de referencias: "(n)" es el número de ecuación del capítulo; "p.NNN" es la página del PDF. Libro p. 7-k = PDF 110+k.
Todas las fórmulas de abajo fueron releídas en la imagen de la página y verificadas numéricamente (script propio) salvo donde se indica "ERROR/DUDA".

## 1. Qué resuelve el capítulo y para qué sirve

Calcula la carga (tensión o presión) crítica de pandeo de una cáscara cilíndrica delgada (radio medio r, espesor h, largo ℓ) sometida a compresión axial, presión lateral externa (o vacío interior) o ambas, con bordes simplemente apoyados. Parte de las ecuaciones de Donnell (bifurcación del equilibrio), llega a fórmulas cerradas ("clásicas"), muestra que los cilindros reales pandean a una fracción (a veces 20 %) de lo clásico por imperfecciones, y entrega fórmulas de diseño con factores de reducción, "límites inferiores" de Croll, un esquema de diseño de recipientes con presión exterior con anillos de refuerzo y curvas de interacción axial-lateral. En diseño sirve para: dimensionar espesor y distancia entre anillos de tanques/recipientes/tubos con vacío, y verificar tubos y envolventes comprimidos. Siempre se verifica también fluencia (sección 6.5, p.124).

## 2. Fórmulas y algoritmos clave

Notación: r radio medio, h espesor, ℓ largo entre apoyos, E, ν; D = E h³/(12(1-ν²)) (2, p.111); C = E h/(1-ν²) (rigidez membranal, p.112); σf fluencia en compresión.

### 2.1 Ecuaciones de gobierno (secc. 2 y 3, p.111-112)
- (1)-a,b,c Donnell (p.111): r ∂Nx/∂x + ∂Nxθ/∂θ = 0 ; r ∂Nxθ/∂x + ∂Nθ/∂θ = 0 ; -[Nx ∂²w/∂x² + (2/r) Nxθ ∂²w/∂x∂θ + (Nθ/r²) ∂²w/∂θ²] + D ∇⁴w + Nθ/r = p. Aquí z positivo es hacia arriba (distinto de placas).
- (2) bilaplaciano en cilíndricas: ∇⁴ = ∂⁴/∂x⁴ + (2/r²) ∂⁴/∂x²∂θ² + (1/r⁴) ∂⁴/∂θ⁴.
- (3) solución membranal (w=0): Nθ = p r (3)-c.
- (5)-c estabilidad desacoplada (p.112): D ∇⁸w1 = ∇⁴( Nx0 ∂²w1/∂x² + (2/r) Nxθ0 ∂²w1/∂x∂θ + (Nθ0/r²) ∂²w1/∂θ² ) - C (1+ν²)/r² ∂⁴w1/∂x⁴ tal como está impreso. **DUDA de notación:** la forma consistente con (9), (24) y (35) (y con Donnell clásico) tiene (1-ν²)C/r² = E h/r² delante de ∂⁴w1/∂x⁴; el "+" impreso en (5)-c y (21) parece una errata. (21) es (5)-c con (20) y también trae (1+ν²). No afecta nada de lo que se implementa.
- Modo de pandeo propuesto, bordes apoyados (7)-(8): w1 = A_mn sen(nθ) sen(m̄ x / r), m̄ = m π r / ℓ (m semiondas axiales, n ondas circunferenciales).

### 2.2 Compresión axial, bordes apoyados (secc. 3.1, p.112-114)
- (6) trayectoria fundamental: Nx0 = σx h = -P/(2π r); Nθ0 = Nxθ0 = 0.
- (9) autovalores: P/(2π r) = χ D/r² + (1/χ)(1-ν²) C, con χ = (m̄²+n²)²/m̄². Hay que tantear enteros m, n (el mínimo P).
- (10) mínimo continuo: χ_crit = sqrt(12(1-ν²)) r/h.
- (11) σcrit = E h /( r sqrt(3(1-ν²)) ); (12) para ν = 0,3: **σcrit = 0,605 E h/r**.
- (13) parámetro de Batdorf: **Z = sqrt(1-ν²) ℓ²/(r h)**.
- (14)-(15) σcrit = (π² D /(h ℓ²)) Ka, con **Ka = 0,702 Z** (0,702 = 12/(π² sqrt3)), equivalente a (12).
- (16)-(17), (18): válido sólo para Z > 2,85. Para Z ≤ 2,85 hay que tantear (9) y usar Ka de la Fig. 3 (p.114).
  - **Resultado propio, verificado (no está en el libro):** para Z ≤ 2,85 el mínimo de (9) es el modo axisimétrico m=1, n=0 y da la forma cerrada **Ka = 1 + 12 Z²/π⁴** (≈1 + 0,1232 Z²). Esta curva es tangente a 0,702 Z justo en Z = 2,85 (discriminante cero), lo que explica el 2,85. En general Ka(Z) = min sobre m∈ℕ de [m² + 12 Z²/(π⁴ m²)] para el modo axisimétrico, y Ka → 0,702 Z para Z>2,85. Verificado contra una búsqueda discreta en (9) (m≤40, n≤400): Z=0,5→1,031; 1→1,123; 2→1,493; 2,85→2,001; 4→2,81; 10→7,02; 100→70,2; 1000→702. Con esto no hace falta digitalizar la Fig. 3.
- Recordatorio del libro (p.114): cilindros muy esbeltos pandean además como columna: verificar con (43).

### 2.3 Presión lateral externa, bordes apoyados (secc. 3.2, p.114-117)
- (20) membranal: Nx0 = 0, Nθ0 = σθ h = -p r.
- (24) autovalores. **ERROR en el libro (p.115):** impreso con (m̄²+n²)²/**m̄²** en el primer término; lo correcto (y lo que sale de (35) con R=0 y lo que reproduce (26)) es (m̄²+n²)²/**n²**:
  p r = ((m̄²+n²)²/n²) D/r² + (m̄⁴ / (n² (m̄²+n²)²)) (1-ν²) C ; el mínimo es con m = 1.
- (25) adimensionales: p̄ = ℓ² r p/(π² D); n̄ = ℓ n/(π r).
- (26) p̄ = (1+n̄²)²/n̄² + (1/(n̄²(1+n̄²)²)) (12/π⁴) Z² ; se minimiza respecto de n entero (tanteo) → p̄crit; (27) **pcrit = (π² D/(ℓ² r)) p̄crit**. (Comprobé (26) derivándola de (24) corregida.)
- Cilindros no largos (ℓ < ℓ2): (28) p̄crit ≈ sqrt(Z) (recta pendiente ½ en escala log, Fig. 5); (29) **pcrit = 0,82 E/(1-ν²)^0,75 · (h/r)^2,5 · (r/ℓ)**. Forma auxiliar p.116: p r/(E h) = 0,28 (h/r)^1,5 [ℓ/(π r)]^-1 (ν=0,3).
- Cilindros largos (ℓ > ℓ2): n = 2, (30) p̄crit = (2ℓ/(π r))²; (31) pcrit = 0,333 E (h/r)³/(1-ν²) (Donnell); (32) **pcrit = 0,267 E (h/r)³/(1-ν²)** (80 % de (31), por la teoría exacta con presión siguiendo la superficie deformada, Fig. 6).
- (33) límite entre ambos: **ℓ2 ≈ 3 r sqrt(r/h)** (igualando (29) y (32) sale 3,07 (1-ν²)^¼ ≈ 3,0).

### 2.4 Carga combinada (secc. 3.3, p.117)
- (34) Nx0 = -P/(2π r), Nθ0 = -p r; (36) R = P/(2π r² p) (relación de cargas; hidrostática sobre cilindro cerrado ⇒ R = 1/2).
- (35) p = [ (m̄²+n²)⁴ D/r² + m̄⁴ (1-ν²) C ] / [ (m̄²+n²)² (n² + R m̄²) ] ; se minimiza en m, n enteros. **DUDA/ERROR dimensional:** el lado izquierdo debería ser **p r** (como en (24)); tal cual está, p tendría unidades de N/mm, no N/mm². Con R = 0 reduce a (24) corregida.
- (37)-(38): σcx = E h/(r sqrt(3(1-ν²))) ; σcθ = pcrit r/h = 0,82 E (h/r)^1,5 (r/ℓ)/(1-ν²)^0,75.
- Hidrostática (Fig. 9): predomina el efecto axial para Z < 3 y el lateral para Z > 3. Valores de p̄ propios (mínimo discreto de (35), r/h=300): lateral R=0: Z=1→4,03; 3→4,22; 10→5,18; 100→11,9; 1000→34,4. Hidrostática R=1/2: Z=1→2,18; 3→2,72; 10→4,08; 100→11,1; 1000→33,7.

### 2.5 Cilindros reales, límites inferiores y diseño (secc. 4 a 6, p.118-124)
- (39) límite inferior de Croll-Batista para σx (p.120), con λ = (π r/ℓ)² y n entero a tantear:
  σx,inf = E [ (λ+n²)² (h/r)²/6 + 2(1-ν²) λ²/(λ+n²)² ] / [ (2-ν²) λ + ν n² ].
  (releído en imagen ampliada: el denominador dice (2-ν²)λ + ν n²; si el original fuera (2-ν) la diferencia es del orden de 5 %, ver riesgos.)
- (40) σθ,inf = 0,617 E/(1-ν²)^0,75 (h/r)^1,5 (r/ℓ) (cilindro no largo; = 75 % de (29)).
- Diseño axial (6.1):
  - (41) σx = P/(2π r h); (42) **CS = min{ σf/σx, σcx/σx, σE/σx }**.
  - (43) Euler del cilindro como columna: σE = ½ π² E (r/ℓ)² (apoyado-apoyado) ; 2 π² E (r/ℓ)² (empotrado-empotrado). (Sale de radio de giro r/√2.)
  - (44) Z>7: Ka teórico 0,702 Z, Ka de diseño **K̄a = 0,88 Z^0,74**; (45) **Kr = K̄a/Ka = 1,254 Z^-0,26**.
  - (46) **σcx = 0,605 E (h/r) Kr = 0,76 E h^1,26/(ℓ^0,52 r^0,74)** (el 0,76 absorbe un factor (1-ν²)^-0,13 ≈ 1,012, ver riesgos).
  - Z<7 bordes apoyados: usar (46). Z<7 empotrados: (47) **σcx = (π² D/(h ℓ²)) 3,7 = 3,34 E (h/ℓ)²**. (Continuidad: 0,88·7^0,74 = 3,71 ✔.)
  - Fig. 13 (p.119): Kr = (h/r)^0,25 con 90 % de probabilidad para 100 < r/h < 3300; el libro dice que no es adecuado para diseño (no se informó ℓ).
- Diseño lateral (6.2):
  - (48) σθ = p r/h; (49) **CS = min{ σf/σθ, σcθ/σθ }**.
  - Largos (ℓ > ℓ2, tubos), (50): pcrit = 0,227 E (h/r)³/(1-ν²) (85 % de (32)); σcθ = pcrit r/h = 0,227 E (h/r)²/(1-ν²).
  - Intermedios (ℓ < ℓ2, recipientes), (51): **pcrit = 0,74 E K*/(1-ν²)^0,75 (h/r)^2,5 (r/ℓ)** (90 % de (29)); σcθ = 0,74 E K* h^1,5/((1-ν²)^0,75 r^0,5 ℓ).
  - (52) **K* = 1 + 4,8/Z - 1,8/Z²** para 1 < Z < 500 (4 > K* > 1); K* = 1 para Z ≥ 500. Si falta un dato para Z, usar K*=1 e iterar; Z sobreestimado ⇒ lado seguro.
  - Anillo de Levy (53)-(55): σcrit = 3 E I/(r² A); σ = q r/A; **Ireq ≥ q r³/(3E)**.
- Recipiente con presión exterior (6.3, p.122-123):
  - (56) σx = ½ p r/h ; (57) σθ = p r/h.
  - (58) espesor tentativo sin anillos (ν=0,3, K*=1 inicial): **h ≥ (1,26 r^1,5 L Cs p/(E K*))^0,4**.
  - Con anillos: (59) ℓ1 = 0,794 E K* h1^2,5/(Cs p r^1,5); m = entero superior de L/ℓ1; anillos = m-1; (60) q = ℓ Cs p; **I ≥ r³ ℓ Cs p/(3E)**.
  - (61) fluencia: h ≥ Cs p r/σf.
  - Notas: no vale para vapor (E depende de T).
- Interacción axial-lateral (6.4, p.123-124):
  - (62) CS = 0Q1/0Q (cargas proporcionales); (63) CS = AQ2/AQ (σθ fija, σx crece); (64) CS = BQ3/BQ (σx fija, σθ crece).
  - (65) círculo normalizado: **CS = [ (σθ/σcθ)² + (σx/σcx)² ]^-0,5**; (66) recta (seguro): **CS = (σθ/σcθ + σx/σcx)^-1**.
  - (67) intermedia: CS = (σθ/σcθ + σx/σcx)^-α, 0,5 ≤ α ≤ 1. **ERROR de homogeneidad:** con α<1 el CS no escala como 1/carga (si σθ=0, CS = (σx/σcx)^-α ≠ σcx/σx). Probable intención: familia CS = [ (σθ/σcθ)^β + (σx/σcx)^β ]^(-1/β) con β entre 1 (recta) y 2 (círculo). Preguntar al usuario/profesor.
  - Derivadas propias para (63) y (64) con la hipótesis circular: CS(63) = (σcx/σx) sqrt(1-(σθ/σcθ)²); CS(64) = (σcθ/σθ) sqrt(1-(σx/σcx)²). El libro sólo da la definición geométrica.
  - σcx se calcula con (39), (46) o (47); σcθ con (40), (50) o (51).
- 6.5 (p.124): la verificación de fluencia (criterio del Cap. 2) siempre es independiente: σ* < σadm.

## 3. Datos tabulados / gráficos / curvas a cargar

No hace falta cargar tablas: todas las figuras son reemplazables por fórmulas del libro o por minimización directa de las ecuaciones.
| Figura | Pág. | Qué es | Cómo reemplazar |
|---|---|---|---|
| Fig. 3 | 114 | Ka(Z), axial apoyado, curva con codo en Z=2,85 | Forma cerrada propia: Ka = 1+12Z²/π⁴ (Z≤2,85), 0,702 Z (Z>2,85). Alternativa: min discreto de (9). |
| Fig. 5 | 115 | p̄crit(Z), lateral apoyado | min en n de (26); aproximación (28) sqrt(Z) corregida por K* (52). |
| Fig. 6 | 116 | pr/(E h) vs ℓ/(π r), Donnell vs exacta, para r/h = 100, 200, 500 | (29) y (32). Puntos de lectura: n=2 comienza en ℓ/(π r) = 9,6; 13,5; 21,4. |
| Fig. 8 | 117 | interacción qualitativa (curva, recta, poligonal) | (65)-(67). |
| Fig. 9 | 117 | p̄crit axial / lateral / hidrostática | (9)-(27) y (35) con R=1/2. |
| Fig. 11 | 118 | Ka experimental, empotrado; teórica 0,702 Z y de diseño 0,88 Z^0,74, plateau 3,7 hasta Z=7 | (44)-(47). 146/702 ≈ 0,2 en Z=1000. |
| Fig. 12 | 119 | puntos experimentales lateral / hidrostática | solo cualitativa (la curva es (26)). |
| Fig. 13 | 119 | Kr vs r/h (nube) y curva 90 % | Kr = (h/r)^0,25. |
Cantidad de datos puntuales a cargar para tests: unos 12 (ver secc. 4).

## 4. Ejemplos resueltos del texto (para tests de validación)

El capítulo no trae ejemplos numéricos resueltos completos. Hay estos anclajes numéricos:
1. p.114, ec. (19): r=1500 mm, h=3 mm, ℓ=120 mm, acero E=210000, ν=0,3, σf=280. Resultados del libro: σcrit (12) = 254 N/mm² (< σf); Z = 3,05 (> 2,85). Recalculado: 254,20 y 3,0526.
2. p.118, Fig. 11: Z=1000: Ka teórico 702, de diseño 146 (146/702 ≈ 0,2). Recalculado: 0,88·1000^0,74 = 146,04.
3. p.116, Fig. 6: puntos n=2 en ℓ/(π r) = 9,6; 13,5; 21,4 para r/h = 100; 200; 500. Con (33): 3·sqrt(r/h)/π = 9,55; 13,50; 21,35 (tolerancia 1 %).
4. p.114 Fig. 3: Ka = 2 en Z = 2,85 (punto marcado).
5. p.123: Z>500 ⇒ 1 < K* < 1,01 (K*(500)=1,0096 ✔); K*(1)=4 ✔.
6. p.117: hidrostática, cambio de dominio en Z ≈ 3 (Fig. 9).

Valores de referencia que calculé yo (no son del libro; sirven para fijar regresión) con E=210000, ν=0,3:
- A (axial): r=500, h=3, ℓ=1500, σf=250, apoyado: Z=1430,9; σcl (12) = 762,6; Kr (45) = 0,1896; (46) = 144,5 (forma simplificada 0,76E h^1,26/(ℓ^0,52 r^0,74) = 143,0); (39) mínimo en n=5: 159,8; (43): 115 145 (apoyado) / 460 582 (empotrado) N/mm² [no gobierna, ℓ/r=3 es corto]. Para P=942,5 kN: σx=100 N/mm² ⇒ CS=min(250/100, 144,5/100, 115145/100)=1,445.
- B (lateral): mismo cilindro: ℓ2 = 19365 mm (⇒ ℓ<ℓ2, "no largo"); (29) pcrit = 0,1718 N/mm²; K*=1 (Z>500); (51) pcrit = 0,1550 N/mm² (σcθ = 25,8 N/mm²); mínimo discreto exacto de (26): n=6, pcrit = 0,1894 N/mm². (32) = 0,0133 y (50) = 0,0113 N/mm² (largos, no aplican acá).
- C (recipiente con vacío): r=1000, L=6000, p=0,1 N/mm², Cs=3, σf=250: (58) con K*=1 → h ≥ 10,3 mm sin anillos; (61) → h ≥ 1,2 mm. Con h1=6 mm: ℓ1 (59) = 1550 mm → m = 4 tramos, 3 anillos, ℓ = 1500; Z=357,7 → K*=1,0134 → ℓ1 = 1570 (m sigue 4); q = ℓ Cs p = 450 N/mm; **Ireq = 714 286 mm⁴** por anillo.
- Interacción: σθ=60, σx=40, σcθ=150, σcx=300 ⇒ CS(65)=2,372; CS(66)=1,875.

## 5. Propuesta de implementación en Struttura

**Tipo B (calculadora CSV -> informe HTML con paso a paso), módulo `cilindros` o `pandeo_cascaras`; opcionalmente un chequeo C/A "pandeo local de tubo" dentro del pórtico 3D.**
- Entrada (bloques): PROYECTO; MATERIALES (id;E;nu;fy); CILINDROS (id;r_medio o d_ext;h;L;apoyo=apoyado|empotrado;material); CASOS (id;cilindro;P compresión;p externa; opcional anillos: h1, Cs, etc.); opciones: criterio de CS (circular|recta|exponente beta), K* sí/no, mostrar límites inferiores.
- Salidas: Z, ℓ2, clasificación (corto/intermedio/largo/Z<2,85), σcx clásica, de diseño, límite inferior de Croll, Euler, σcθ/pcrit (todas las variantes), CS parcial y global, factor gobernante, verificación de fluencia, curva de interacción en SVG, y en modo "recipiente": espesor tentativo (58), ℓ1 (59), m, I requerido de anillo (60) con iteración sobre h1. Se puede imprimir la minimización discreta de (9) y (26) como tabla n×m (paso a paso real).
- Conexión con lo existente: la sección `tubo (d,t)` del pórtico 3D ya da r y h; el chequeo puede tomar Nx de cada barra del 3D (N<0 compresión, σx=N/A) con ℓ = largo de barra y CS por (42); y la presión no aplica al fuselaje.
- Dificultad: 2/5 (fórmulas cerradas; lo más fino es el tanteo discreto y el diseño de anillos). Tiempo: **mediana** (calculadora completa con tests y gráfico) ; "chica" si sólo se hace axial+lateral sin recipiente.
- Dependencias: Cap. 2 (criterios de falla) para fluencia, Cap. 4 (D, C), Cap. 6 (placas: mismo procedimiento de bifurcación), Cap. 8 (para tubos, el Cap. 8 remite a este).
- Aplicación a fuselaje tubular soldado de avión liviano: la tensión clásica 0,605 E h/r es 4000-13000 MPa para r/h = 10-30, pero la de diseño (46) con ℓ = 600 mm da 1147 MPa (r=12, h=1,2; r/h=10), 594 MPa (r=12,5, h=0,9, ℓ=1000), 530 MPa (r=25, h=1; r/h=25) y 323 MPa (r=15, h=0,5; r/h=30). Contra una fluencia de ~450 MPa (4130 normalizado, a confirmar con el usuario) el pandeo de cáscara **no gobierna para r/h ≲ 15, compite para r/h ≈ 25-30 y gobierna para paredes más finas**; además el pandeo como columna (Euler, (43)) y la fluencia suelen gobernar antes. Por eso conviene el chequeo automático (barra comprimida del 3D) más que un cálculo manual. Para estructuras mecánicas generales (tanques, vacío, recipientes, silos, chimeneas, revestimientos de aluminio con r/h > 300): aplica por completo, sobre todo 6.3 y anillos.

## 6. Anexo teórico para los informes

Poner: hipótesis de Kirchhoff y ecuaciones de Donnell (1), parámetro de Batdorf (13); σcrit clásica axial (12) y Ka (15)/(18); (26)-(27) y (29)/(32)/(33) lateral; factores de reducción (45)-(47) y (50)-(52) con el motivo (imperfecciones, Fig. 10-11); CS (42), (49); interacción (65)-(66); anillos (55), (58)-(60); fluencia independiente (6.5). Remitir al Cap. 7 del Compendio (UNC-FCEFyN 2024) sin copiar texto, y aclarar la advertencia de que la teoría clásica sobreestima mucho la carga real axial.

## 7. Riesgos, ambigüedades y preguntas al usuario

- ERROR en (24): m̄² en el denominador del primer término debe ser n² (verificado por (35) R=0 y por (26)).
- ERROR dimensional en (35): falta r (debería ser p r =). Resultados de Fig. 9 reproducidos usando p r.
- ERROR conceptual en (67): ver 2.5; exigir confirmación del exponente.
- (5)-c y (21): se imprime C(1+ν²)/r²; lo consistente es (1-ν²)C/r² = E h/r². No impacta a la implementación.
- (52) no se reproduce a partir de (26): el mínimo continuo de (26) dividido sqrt(Z) da 1,64 (Z=10), 1,34 (30), 1,19 (100), 1,10 (500), 1,083 (1000), 1,053 (10⁴) frente a K* de (52) = 1,46; 1,16; 1,05; 1,00; 1,00; 1,00. Asintóticamente p̄ ≈ 1,04 sqrt(Z)+2, no sqrt(Z). Esto queda cubierto por el 0,9 de seguridad de (51) (el mínimo discreto exacto de B arriba es 10-20 % mayor que (29)), pero se recomienda mostrar ambos (fórmula del libro y mínimo numérico) y preguntarle al profesor si K* viene de otra figura.
- (46): forma 0,605·1,254 = 0,759 vs la simplificada 0,76 con sqrt(1-ν²) absorbido: 1 % de diferencia. Con Z < 2,4, Kr > 1: limitar σcx de diseño a la clásica.
- 6.1.1 deduce Kr de la Fig. 11 (bordes empotrados) y la usa también para apoyados con Z>7 (el libro afirma independencia de bordes). Supuesto del libro.
- (39): confirmar el denominador (2-ν²) con el docente/fuente (Croll-Batista).
- Datos del libro: ν=0,3 fijo en (12), (29), (32), (58), (59). Decidir si el programa admite ν distinto (las fórmulas con (1-ν²) sí lo permiten; (12), (58) y (59) con coeficientes numéricos no).
- Sólo bordes simplemente apoyados en 3.x; para empotrados sólo hay (47). No hay tratamiento de cargas excéntricas, cilindros con aberturas, ni pandeo por corte/torsión.
- Preguntarle al usuario: ¿qué CS mínimo pide la cátedra (Cs por defecto)? ¿radio medio o exterior en su CSV? ¿interacción: círculo, recta o exponente? ¿se agrega el chequeo al pórtico 3D o es una calculadora aparte?
