# Cap. 3 - Cilindros gruesos con elevada presión (Compendio Cálculo Estructural II, UNC 2024)

PDF págs. 43-60 (páginas del libro 3-1 a 3-18). Página del libro N = PDF 42+N.
Convención: tracción +, presión negativa en σr. `σt` = tensión tangencial (σθθ), `σr` radial, `σz` axial.
Estado de verificación: **[V]** = reproducido numéricamente con un cálculo independiente (Lamé + superposición, scripts mios); **[L]** = leído de la imagen de la página, coherente con la teoría estándar pero no recalculado; **[!]** = inconsistencia detectada (ver sección 7).

## 1. Qué resuelve y para qué sirve

Resuelve el cilindro de pared gruesa (radio interior a, exterior b) con carga axilsimétrica: presión interior pi, exterior pe y tensión axial σo uniforme. Con las ecuaciones de la elasticidad en coordenadas cilíndricas (equilibrio, cinemática, constitutivas) llega a la solución exacta de Lamé: σr(r), σt(r), u(r). Sobre esa base desarrolla: zunchado (dos o tres tubos con interferencia), autozunchado por plastificación, presión de estallido, y fórmulas **de dimensionamiento directo** (dado pi, a, Cs, σf, sale b) para Rankine, Tresca y Von Mises, incluyendo zunchado óptimo (b, c, δ sin tanteos).
En diseño sirve para: cilindros hidráulicos, recipientes de alta presión, cañones, y (lo que más le toca a un mecánico) **ajustes a presión / montajes forzados** de bujes, mazas, poleas, engranajes sobre ejes. Cuando b/a > ~2 agregar espesor casi no baja la tensión (Fig. 11), por eso se zuncha.

## 2. Fórmulas y algoritmos clave

### 2.1 Ecuaciones básicas (§2, PDF 44-47)
- Equilibrio en coordenadas cilíndricas, ec. (3), PDF 45 [L]: dσrr/dr + (1/r)dσθr/dθ + dσzr/dz + (σrr−σθθ)/r + Fr = 0; análogas en θ (con 2σrθ/r) y z (con σrz/r).
- Cinemática lineal, ec. (11), PDF 46 [L]: εrr=∂u/∂r; εθθ=(1/r)∂v/∂θ+u/r; εzz=∂w/∂z; εrθ=½[∂v/∂r+(1/r)∂u/∂θ−v/r]; εθz=½[(1/r)∂w/∂θ+∂v/∂z]; εrz=½[∂u/∂z+∂w/∂r].
- Constitutivas (12)-(13), PDF 47 [L]: igual que Cap. 1 (direcciones ortogonales).

### 2.2 Cilindro con presión interior y exterior (§3, PDF 47-50)
Hipótesis: axilsimetría, v=0, σz=σo uniforme → corte nulo, todo independiente de θ y z.
- Equilibrio radial (14) [L]: r·dσr/dr + σr − σt = 0.
- Ecuación del desplazamiento (19) [L]: u'' + u'/r − u/r² = 0; solución (20): u = A r + B/r.
- Condiciones de borde (21): σr(a) = −pi, σr(b) = −pe.
- Constantes (22), PDF 48 [!]: A = (1−ν)/E · (pi a² − pe b²)/(b²−a²);  B = (1+ν)/E · a²b²(pi−pe)/(b²−a²).
  **Ojo**: esa A es la del caso σz=0. Con σo≠0 aparece un término extra −ν σz/E en A (verificado: con cierre axial σz=pi a²/(b²−a²) el u dado por (22) no coincide con εt·r). Las tensiones (23)-(24) no se ven afectadas.
- Tensiones (23)-(24), PDF 48 [V]. Con x=(b/a)²−1 en el denominador:
  σr = −{ pi[(b/r)²−1] + pe[(b/a)²−(b/r)²] } / [(b/a)²−1]
  σt =  { pi[(b/r)²+1] − pe[(b/a)²+(b/r)²] } / [(b/a)²−1]
- Deformación axial (25) [V]: εz = σo/E − (2ν/E)(pi a² − pe b²)/(b²−a²), uniforme en r.
- Solo presión interior (26)-(27) [V]: σt = pi a²/(b²−a²)·(1+b²/r²);  σr = pi a²/(b²−a²)·(1−b²/r²). Máximos en r=a: σr=−pi (32), σt=pi(b²+a²)/(b²−a²) (33), τmax=½(σt−σr)=pi b²/(b²−a²) (34).
- Solo presión exterior (35)-(36) [V]: σt = −pe b²/(b²−a²)·(1+a²/r²);  σr = −pe b²/(b²−a²)·(1−a²/r²).
- Casos de cierre axial (28)-(31): actuador con pistón σz=0 (28); recipiente cerrado σz = pi a²/(b²−a²) (29) lejos de los extremos. En ambos casos σr<σz<σt en r=a, de modo que gobierna τmax.

### 2.3 Zunchado (§4, PDF 50-51)
Interferencia radial δ en r=b. Inner tube a-b con pz externa, outer tube b-c con pz interior; ambos con σz=0.
- Compatibilidad (37)-(38): δ = |u1(b)| + u2(b).
- (39) PDF 51 [!]: b·pz/E1·[(b²+a²)/(b²−a²) − ν1] + b·pz/E2·[(c²+b²)/(c²−b²) **+ ν2**] = δ. El libro imprime "−ν2" en el segundo corchete: es erratum (con "+ν2" da (40); verificado).
- Presión de zunchado, mismo material (40) [V]: pz = E δ (b²−a²)(c²−b²) / (2 b³ (c²−a²)).
- Tensiones: exterior = (26)-(27) con (a→b, b→c, pi=pz); interior = (35)-(36) con pe=pz. Si después hay presión interior pi, se suma la solución del cilindro único (a,c) (Fig. 12 / Fig. 17). Condición conveniente (41): τa=τb.

### 2.4 Autozunchado por tensiones residuales (§5, PDF 51-53)
Material elastoplástico perfecto, Tresca (τf=σf/2), σz intermedia.
- Inicio de fluencia (42)-(43) [V]: pf = τf (b²−a²)/b²  (= σf/2·(1−(a/b)²)).
- Zona plástica: r dσr/dr = 2τf (44) → σr = 2τf ln r + c (45); toda la pared plástica (σr(b)=0): σr = 2τf ln(r/b) (46); σt = 2τf[1+ln(r/b)] (48).
- Presión de plastificación total (47)-b [V]: pp = σf ln(b/a). Chequeo del libro (Fig. 15): b/a=2 → pf/τf=0.75, pp/τf=1.39 (ratio 1.85); b/a=1.05 → 0.093 y 0.098 (ratio 1.05).
- Tensiones residuales: restar la solución elástica con pi=pp (Fig. 14). **El libro no da la fórmula cerrada**; surge de (46),(48) menos (26),(27) con pi=pp (derivación mía, para plastificación total, sin reflujo plástico): σr,res = 2τf ln(r/b) + pp a²/(b²−a²)(1−b²/r²); σt,res = 2τf[1+ln(r/b)] − pp a²/(b²−a²)(1+b²/r²). Se cumple σr,res(a)=0.
- Plastificación parcial: "conceptualmente poco cambio", **no se desarrolla**.

### 2.5 Diseño de un cilindro simple dúctil (§6.1, PDF 54-55). Variables: p̄ = Cs·pi/σf, b̄ = b/a
| Criterio | Radio exterior | Límite de pi |
|---|---|---|
| Tresca (49)-(52), σr<σz<σt [V] | b = a / √(1 − 2 Cs pi/σf) | pi < 0.5 σf/Cs |
| Von Mises σz=0 (53)-(55) [V] | α=p̄²;  b = a √[(1+√(α(4−3α)))/(1−3α)] | pi < 0.577 σf/Cs |
| Von Mises σz por pi (56)-(60) [V] | b = a √[σf/(σf − √3 Cs pi)] | pi < 0.577 σf/Cs |
Nota del libro: (54) da espesores algo mayores que (59), diferencia ≤15 % (verificado: ~12-15 % en espesor, ~2 % en b).

### 2.6 Presión de estallido (§6.2, PDF 55-56)
- (61)-(62): pE = σR ln(b/a)  (con τR≈σR/2). Svensson (63): pE = η σR ln(b/a), η = (1/(4m+0.908))·(2.718/m)^m, m = 0.4(1−σf/σR) (64, solo aceros de bajo/medio carbono). Nota: σf/σR=0.6 → m=0.16, η≈1.017 [V].
- CsE = pE/pi (65). Diseño a estallido (66): b = a·exp(CsE·pi/(η σR)) (siempre tiene solución). No usar para cilindros hidráulicos (la fluencia ya es falla).

### 2.7 Zunchado óptimo, dos tubos (§6.3, PDF 56-58)
Se aplica Cs a la presión: ps = Cs·pi (67), porque con la interferencia fijada la relación presión-tensión no es lineal.
- Tresca (69)-(78) [V]: condiciones de óptimo: σa*=σb* (71), σm* mínimo (72), σm*=σf (73). Resultado:
  1) c = a/(1 − ps/σf) (77);  2) b = √(a c) (76);  3) pz = ps (c−a)/(2(c+a)),  δ = b·ps/E (78).
  Límite: ps<σf, o sea pi < σf/Cs (79): duplica el rango del cilindro simple (52).
- Von Mises, σo=0 (80)-(87), PDF 58 [V]: se adopta b=√c (óptimo exacto en ese caso; el libro dice <1 % de diferencia con el óptimo global). Adimensionales c̄=c/a, b̄=√c̄, p̄=ps/σf, p̄z=pz/σf.
  - Von Mises plano (83): σ*² = σt² + σr² + σt|σr| (con σt>0, σr<0).
  - p̄z = α p̄ con α=(3c̄²+1−√(6c̄⁴+6c̄³+3c̄²+1))/(c̄²−1) (84) [V].
  - p̄ admisible (85) [V]: p̄ = (c̄²−1)/√(3c̄⁴ + α(c̄+1)[4αc̄²(c̄+1) − 6c̄³ − 2c̄] + 1).
  - Radio por fórmula aproximada (86) (error <0.5 %) [V]: c̄ = ([(4p̄−9.6)p̄ − 0.5] p̄² + 20)/(20 − 19 p̄).
  - Interferencia (87): δ = 2 b pz (c+a)/(E (c−a)) [V, consistente con (40)].
  - Secuencia: datos a, pi, Cs, E, σf → p̄ → c̄ (86) → b=a√c̄ → pz=αpσf (84) → δ (87).
- Rankine, frágil (§6.3.3, tabla (106), PDF 60) [V]: c̄ = (1+p̄+2√(1+p̄))/(3−p̄), c̄ < 2.4142 (=1+√2; (88) dice c/a<2.41); p̄z = [p̄(c̄²+1) − c̄² + 1]/(2c̄(c̄+1)).
- Tres tubos, dúctil (§6.3.4, (91)-(99), PDF 59): radios b=√x·a, c=x·a, d=x^1.5·a; x=αx/(1−2p̄/3) si p̄≤0.951, x=αx·(1/(1−p̄))^(1/3) si 0.951<p̄≤1; presiones pb (94), pc (95); interferencias δb, δc (96); coeficientes Von Mises (97)-(99): αx=1−0.2387p̄²+0.08535p̄³, αb=0.76+0.116p̄²+0.064p̄³, αc=0.755+0.1933p̄³ (Tresca: todos 1).
  Tresca verificado [V] (τ igual en los tres radios internos para p̄≤0.951, δb y δc coinciden con compatibilidad directa). **Von Mises [!]: ver sección 7, no cierra.**
- Máximo absoluto: pi,máx = σf/Cs (σr(a)=−pi ≥ −σf) (89)-(90).

### 2.8 Resumen del libro (§7, PDF 60)
Tablas (100)-(112): p̄ admisible, b̄ necesario y pz para Rankine/Tresca/VM(σz=0)/VM(σz por pi) y zunchado óptimo. Son los mismos resultados de 2.5-2.7 reescritos [V]; (102)-(103) coinciden con (54),(59).

## 3. Datos tabulados, gráficos, curvas
- **No hay tablas de datos numéricos** que cargar. Todo es analítico.
- Fig. 11 (PDF 50): τmax/pi = (b/a)²/((b/a)²−1) → reproducible desde (34).
- Fig. 15 (PDF 53): curvas pf/τf = 1−(a/b)² y pp/τf = 2 ln(b/a) → reproducible con (43) y (47)-a.
- Fig. 10, 12, 14, 17: esquemas cualitativos de σt(r), σr(r), τ(r); conviene regenerarlos en el informe con las ecuaciones (26),(27),(35),(36) (SVG propio, sin dependencias).
- Constantes/polinomios a codificar: (97)-(99) (3 polinomios, 3-4 términos cada uno), umbral 0.951 de (92), fórmula (86), constantes de Svensson (0.908, 2.718, 0.4) en (63)-(64).
- Fórmulas aproximadas que reemplazan un cálculo iterativo: (86) reemplaza el tanteo de (85); se puede dejar (85) + bisección y comparar.

## 4. Ejemplos resueltos del texto
**El capítulo no trae ejemplos numéricos resueltos.** Solo valores sueltos citables como tests: b/a=2: pf/τf=0.75, pp/τf=1.39; b/a=1.05: 0.093/0.098; η=1.017 con σf/σR=0.6; c̄máx Rankine=2.4142; Fig. 11 (b/a=2 → τmax/pi=1.333).
Casos de verificación **calculados por mí** (Lamé independiente, E=210000 MPa, ν=0.3; usar como tests, tolerancia 1e-6 relativa):
1. Lamé a=50, b=100, pi=100, pe=0: σt(a)=166.667, σt(b)=66.667, σr(a)=−100, σr(b)=0, τmax=133.333, σz(cerrado)=33.333, σVM(cerrado)=230.940. Con pi=0, pe=100: σt(a)=−266.667, σt(b)=−166.667, σr(b)=−100.
2. Diseño: a=50, pi=60, σf=400, Cs=1.5 (p̄=0.225): b Tresca=67.420 (51); b VM σz=0=65.182 (54); b VM cerrado=64.003 (59). Para este último: σt(a)=247.920, σz=93.960, σr=−60 → σVM=266.667=σf/Cs.
3. Estallido: σR=600, σf=400 → m=0.13333, η=1.03708; con b=67.420: pE=186.00 MPa, CsE=3.100; b para CsE=3: 66.773.
4. Zunchado Tresca: a=50, pi=100, Cs=1.5, σf=400, E=210000 (p̄=0.375): c=80.000, b=63.2456, pz=17.3077 MPa, δ=0.045175 mm; σ*=σf=400 en r=a y en r=b (tubo exterior).
5. Zunchado Von Mises (mismos datos): c̄=1.51476 → c=75.738, b=61.538, α=0.090031, pz=13.5046 MPa, δ=0.038666 mm.
6. Tres tubos Tresca: a=50, pi=150, Cs=1.5, σf=400 (p̄=0.5625): x=1.6, b=63.2456, c=80.000, d=101.193, pb=36.628, pc=31.395 MPa, δb=0.045175, δc=0.057143 mm.

## 5. Propuesta de implementación en Struttura
- **Tipo B** (calculadora, no matricial). Paquete nuevo p.ej. `struttura/cilindros/` con `entrada.py` (CSV por bloques), `lame.py` (σ(r), u(r) con pi, pe, σo), `diseno.py` ((51),(54),(59),(66)), `zunchado.py` (dos y tres tubos, (40), (78)-(87), (91)-(96)), `autozunchado.py`, `informe.py` (HTML con paso a paso y SVG de σ(r)).
- Entradas CSV: bloque MATERIAL (E, ν, σf, σR, opcional σadm y teoría: vm/tresca/rankine, igual que `portico3d/tensor.py`), GEOMETRIA (a, b o "dimensionar", c, radio intermedio), CARGAS (pi, pe, σo, cierre axial: pistón/cerrado/libre), MODO (verificar | dimensionar | zunchado_dos | zunchado_tres | autozunchado | estallido), Cs.
- Salidas: perfiles σt, σr, σz, τmax, σeq y CS en N puntos de r; b/c/δ de diseño; pz; tensiones totales con superposición pi; CS por criterio; pE y CsE.
- Conexión con lo existente: reutilizar la definición de material y criterios de `portico3d/tensor.py`. **Hay que agregar** una versión por tensiones principales (σ1,σ2,σ3) de `criterios()`, que hoy asume σ2=0; para el cilindro σ2=σz. Reutilizar el estilo de informe HTML con matrices/ecuaciones de los otros programas.
- Dificultad: **2/5**. Tiempo: **1 unidad mediana** (cálculo + CSV + tests) + **1 chica** (informe con gráficos). Dependencias: Cap. 2 (criterios, Cs), Cap. 1 (constitutivas); Cap. 16 (recipientes, códigos ASME) para pared delgada y espesores normativos.
- Aplicación a fuselaje tubular soldado: **baja de forma directa** (tubos de pared delgada, sin presión interna). Sí aplica: ajustes a presión de bujes en orejas de herrajes, mangones/insertos dentro de tubos (interferencia y tensión en el manguito), alojamientos de rodamientos, bielas/rótulas. Para tubo delgado con presión (cañería hidráulica) el límite b/a→1 recupera σt≈p a/t (chequeable con (26)).
- Aplicación a estructuras mecánicas generales: alta (cilindros hidráulicos, prensas, ejes con mazas, poleas, engranajes calados, autozunchado de cilindros).

## 6. Anexo teórico sugerido para los informes
- Ecuaciones (14), (20), (22)-(24) del Cap. 3: solución de Lamé; (26)-(27) y (35)-(36) para pi o pe solos.
- (32)-(34): tensiones máximas en r=a y τmax; criterio de diseño (49)-(51) Tresca; (53)-(59) Von Mises; (62)-(66) estallido.
- (37)-(40): compatibilidad de zunchado y presión de montaje; (69)-(78) zunchado óptimo Tresca.
- Citar siempre "Compendio de Cálculo Estructural II, Cap. 3, ec. (N)". Aclarar la hipótesis σz uniforme y lejos de los extremos.

## 7. Riesgos, ambigüedades, preguntas al usuario
1. **Errata (39)** (PDF 51): signo de ν2; correcto es "+ν2". Con materiales distintos usar: pz = δ / { (b/E1)[(b²+a²)/(b²−a²)−ν1] + (b/E2)[(c²+b²)/(c²−b²)+ν2] }. (40) vale solo para igual E y ν.
2. **(22)** vale solo con σz≈0 (o sin el término axial); no usar u(r) con cierre axial sin corregir A restando ν·σz/E.
3. **c̄máx Von Mises = 13.0486** (tabla (108), PDF 60) no cierra con (85)/(108): p̄(13.0486)=0.9961 y p̄=1 se alcanza en c̄≈14.01 (por (86) da 13.9). Verificar con el libro o usar la raíz numérica.
4. **Von Mises tres tubos (97)-(99) [!]**: con σz=0 y VM plano (83), aplicando (91)-(96) con αx, αb, αc, el tubo intermedio da σVM entre 1.05σf y 1.16σf en r=b (p̄=0.3 a 0.9), los otros dos entre 0.84 y 1.01. No cierra: no implementar esas fórmulas sin validar; alternativa: optimizar numéricamente (3 incógnitas) tomando Tresca como semilla.
5. VM zunchado: se supone σo=0 (extremos libres); con recipiente cerrado σz≠0 no está cubierto. Pregunta: ¿cilindro abierto (pistón) o cerrado?
6. Autozunchado: solo plastificación total, Tresca perfectamente plástico, sin reflujo plástico en la descarga (puede ocurrir para b/a grande) ni efecto Bauschinger; tensiones residuales las derivé yo.
7. Cs sobre presión (zunchado) vs Cs sobre tensión (simple): son equivalentes solo en el caso lineal; en zunchado la interferencia queda fija, así que el "Cs" real de la presión de servicio es el de ps.
8. Notación: el texto extraído pierde símbolos griegos (σ→ζ, τ→η); usar siempre la imagen del PDF. Mezcla ν y v, b y b̄ (adimensional), p̄ con y sin barra.
9. Temperatura (Δt=0 en (13)), fatiga, concentraciones de tensión y extremos (Saint-Venant) no se tratan. Preguntar al usuario: ¿materiales reales (σf, σR) y cuál criterio quiere por defecto?
