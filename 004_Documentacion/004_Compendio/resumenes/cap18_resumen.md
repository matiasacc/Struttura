# Cap. 18 - Uniones (Compendio CE-II, PDF págs. 353-376)

Fuente: Compendio de Cálculo Estructural II, UNC-FCEFyN, ed. 2024. Página del libro "18-n" = PDF 352+n.
Fórmulas releídas en imagen; las del Anexo 1 y la teoría de filete verificadas numéricamente con script propio (ver sección 7).

## 1. Qué resuelve el capítulo y para qué sirve

Presenta los métodos de unión (desmontables: pernos/tornillos; permanentes: soldaduras, remaches, adhesivos) y da el cálculo de verificación de tres de ellos: **soldaduras** (a tope y de filete, con método simplificado de garganta + propiedades de grupos de cordones como líneas para carga axial, corte, flexión y torsión), **remaches/pernos** (placas con borde cargado y grupos con carga excéntrica) y **adhesivos** (criterios de diseño y la distribución de corte de Volkersen para solape doble, con efecto térmico). Incluye notas sobre procesos, calidad e inspección de soldaduras y el comentario aeronáutico de que no se permite reparar con soldadura ciertas partes críticas (trenes de aterrizaje).
Sirve en diseño para: dimensionar el pie "w" de un cordón de filete, verificar un grupo de cordones bajo cargas combinadas, repartir carga entre remaches/bulones con excentricidad y estimar la resistencia de una junta pegada.
**No trae ejemplos numéricos resueltos** (menciona un "problema 6" de adhesivos con temperatura que no está en el capítulo). Los tests de validación de abajo son calculados por mí, no del libro. Las uniones desmontables con precarga no se desarrollan (solo la descripción cualitativa y la regla conservadora: se pierde la precarga y se verifica como remache).

## 2. Fórmulas y algoritmos clave

### 2.1 Soldadura a tope (sec. 3.1.2, págs. 18-4/18-5, PDF 356-357)
- (1) sigma = P/(t l) tracción/compresión ; (2) tau = P/(t l) corte. t = garganta = espesor de las piezas (sin sobremonta/refuerzo), l = longitud del cordón.
- Con cargas combinadas usar Von Mises o Tresca (dúctiles). Recomienda mecanizar el refuerzo si hay fatiga. Siempre verificar contra la resistencia del material base además del aporte.

### 2.2 Soldadura de filete (págs. 18-5 a 18-8, PDF 357-360)
- (3) t = 0,707 w (garganta con catetos iguales w).
- (4) Pn = P cos(theta) ; Ps = P sen(theta) (fuerzas en un plano de la soldadura inclinado theta; P es la fuerza por cordón, ver Fig. 5)
- (5) t' = w / (cos(theta) + sen(theta))
- (6) sigma = (P/(w l)) (cos^2 th + sen th cos th) ; (7) tau = (P/(w l)) (sen th cos th + sen^2 th)
- (8) sigma* = sqrt(sigma^2 + 3 tau^2)
- (9)-(10) Von Mises máximo en theta = 62,5 grados: sigma* = 2,16 P/(w l), con sigma = 0,623 y tau = 1,196 (en unidades de P/(w l)).
- (11) "Tresca" (máximo tau de (7)): theta = 67,5 grados, tau_max = 1,207 P/(w l), sigma = 0,5 P/(w l).
- (12) **Método simplificado (AWS/AISC)**: tau = P/(t l) = P/(0,707 w l) = 1,414 P/(w l), todo como corte en la garganta mínima. Es 17 % mayor que (11) y 18 % mayor que (10): reserva conservadora.
- (13) f = t tau = 0,707 w tau (fuerza por unidad de longitud de cordón).
- **Tabla 4** (pág. 18-7): para cargas sobre el grupo de cordones: tensión simplificada y fuerza por unidad de longitud:
  - Axil P: tau_P = P/A ; f_P = P/Aw
  - Corte V: tau_V = V/A ; f_V = V/Aw
  - Flector M: tau_M = M/S ; f_M = M/Sw
  - Torsor T: tau_T = T c / J ; f_T = T c / Jw
  con A = área de garganta del cordón; Aw, Sw, Jw = propiedades "unitarias" (cordón tratado como línea de espesor 1; ver Anexo 1), c = distancia del punto de control al centro del grupo. Se pasa de f a tau con tau = f / (0,707 w) = f/t.
- (14) tau_total = sqrt(tau_x^2 + tau_y^2 + tau_z^2) ; f_total = sqrt(f_x^2 + f_y^2 + f_z^2) (composición **vectorial** de las contribuciones en cada punto).
- (15) f_total <= f_adm = 0,707 w tau_adm  ; o con CS: tau_total <= tau_falla / CS ; f_total <= 0,707 w tau_falla / CS.
- (16) w >= f_total / (0,707 tau_adm)  o  w >= CS f_total / (0,707 tau_falla).
- Control: w <= espesores de las piezas unidas (debe tener respaldo).
- Criterios AISC del Anexo 2: CS_tracción = 1/0,60 = 1,67 ; CS_corte = 0,577/0,40 = 1,44 (Von Mises). Para electrodo E70xx: tau_adm = menor(0,3 sigma_u ; 0,4 sigma_y) = 145 MPa (0,3 x 482 = 144,6 ✓). El libro escribe tau_u y tau_y, debería ser sigma_u y sigma_y.

### 2.3 Propiedades de cordones como líneas (Anexo 1, pág. 18-20, PDF 372; fuente Mott)
Los 9 casos fueron verificados numéricamente (integrando segmentos): [b = dimensión horizontal, d = vertical, a = brazo de la carga]
1. Línea vertical d: Aw = d ; Sw = d^2/6 ; Jw = d^3/12 (c = d/2 en torsión)
2. Dos líneas verticales d separadas b: Aw = 2d ; Sw = d^2/3 ; Jw = d (3 b^2 + d^2)/6
3. Dos líneas horizontales b separadas d: Aw = 2b ; Sw = b d ; Jw = (b^3 + 3 b d^2)/6
4. Una horizontal b + una vertical d (L): Aw = b + d ; x_ = b^2/(2(b+d)) ; y_ = d^2/(2(b+d)) ; Sw(arriba) = (4bd + d^2)/6 ; Sw(abajo) = d^2 (4b + d)/(6 (2b + d)) ; Jw = ((b+d)^4 - 6 b^2 d^2)/(12 (b+d))
5. C: dos horizontales b + vertical d: Aw = d + 2b ; x_ = b^2/(2b + d) ; Sw = b d + d^2/6 ; Jw = (2b+d)^3/12 - b^2 (b+d)^2/(2b+d)
6. C invertida (una horizontal b + dos verticales d): Aw = b + 2d ; y_ = d^2/(b+2d) ; Sw(arriba) = (2bd + d^2)/3 ; Sw(abajo) = d^2 (2b + d)/(3 (b+d)) ; Jw = (b+2d)^3/12 - d^2 (b+d)^2/(b+2d)
7. Rectángulo todo alrededor: Aw = 2b + 2d ; Sw = b d + d^2/3 ; Jw = (b+d)^3/6
8. Perfil doble T (alas con un cordón por ala, alma con dos): Aw = 2b + 2d ; Sw = b d + d^2/3 ; Jw = (b^3 + 3 b d^2 + d^3)/6
9. **Círculo (tubo soldado todo alrededor)**: Aw = pi d ; Sw = pi d^2/4 ; Jw = pi d^3/4
Convención: Sw = Ix_w / c con Ix_w momento de inercia de la línea respecto del eje horizontal por el centroide del grupo; Jw = polar de la línea respecto del centroide. El libro solo trae flexión respecto del eje horizontal (carga vertical con brazo a).

### 2.4 Resistencia del material de aporte (Anexo 2, pág. 18-21, PDF 373)
Ver sección 3 (datos).

### 2.5 Remaches y pernos (sec. 3.2, págs. 18-12 a 18-14, PDF 364-366)
Uniones a solape con N = carga por unidad de longitud en el borde de las placas, b = paso entre remaches, a = distancia de la línea de remaches al borde, d = diámetro, t = espesor de la placa:
- (17) tau_r = N b/(pi d^2/4) = 4 N b/(pi d^2)   (corte en remache, un plano)
- (18) sigma_apl = N b/(t d)   (aplastamiento remache o placa; área proyectada t d)
- (19) sigma_p = N b/(t (b - d))   (tracción de la placa en la línea de agujeros)
- (20) tau = N b/(2 a t)   (corte de la placa en los planos c-c; "arranque" de remaches)
Carga excéntrica (Fig. 17), n remaches iguales:
- (21) F1 = P/n (paralela a P en cada remache)
- (22) P e = sum(S r) ; (23) F2 = k r (proporcional a la distancia al centro de gravedad del grupo) ; (24) P e = k sum(r^2) ; (25) k = P e / sum(r^2) ; (26) **F2 = P e r / sum(r^2)**, dirección perpendicular a r.
- Componer vectorialmente F1 y F2 en cada remache; con la resultante calcular corte (17-like con F) y aplastamiento F/(t d). Aplica igual a bulones (sin precarga). Los criterios de resistencia y CS quedan a elección del diseñador (Anexo 3 da datos).

### 2.6 Adhesivos (sec. 3.3, págs. 18-14 a 18-19, PDF 366-371)
- Cualitativo: diseñar para corte y no pelado; ahusar extremos; ductilidad; ambiente; inspección; área amplia; combinaciones con remache o soldadura por puntos.
- Resistencia al corte aparente = carga de rotura / área de solape (promedio, subestima picos).
- **Volkersen, solape doble simétrico (Fig. 20) - ec. (27)-(28)**:
  tau(x) = P w/(4 b sinh(w l/2)) cosh(w x) + P w/(4 b cosh(w l/2)) ((2 Eo to - Ei ti)/(2 Eo to + Ei ti)) sinh(w x) + (ai - ao) dT w / ((1/(Eo to) + 2/(Ei ti)) cosh(w l/2)) sinh(w x)
  con w = sqrt( (G/h) (1/(Eo to) + 2/(Ei ti)) ). (Uso w como omega del libro; no confundir con omega de pandeo del Cap. 17 ni con w de soldadura.)
  Subíndice o = adherentes exteriores (2 piezas), i = adherente interior; G, h = módulo transversal y espesor del adhesivo; b ancho; l longitud de solape; x desde el centro del solape; dT = variación de temperatura respecto de la de curado.
  Verificado: integra a P/2 por interfaz (test numérico). Es dimensionalmente consistente en cualquier sistema coherente (el libro dice "unidades inglesas", no es necesario).
- Solape simple (Fig. 21-22): excentricidad -> flexión de las piezas, corte hasta 2x el de solape doble y tracción de desprendimiento elevada; tensiones de flexión hasta 4x. Solo se describe (Goland-Reissner, sin fórmulas).

## 3. Datos tabulados / gráficos a cargar

| Dato | Dónde | Cantidad | Fórmula alternativa |
|---|---|---|---|
| Propiedades de cordones como línea (9 casos) | Anexo 1, pág. 18-20 | 9 casos x (Aw, Sw, Jw, centroides) | Sí: se calculan para segmentos arbitrarios (mejor que las 9 tablas) |
| Resistencia de electrodos AWS (tracción, fluencia) | Anexo 2, pág. 18-21 (tabla 1) | 6 filas | No |
| Esfuerzos permisibles AISC y CS | Anexo 2 (tabla 2) | 5 filas | Fórmulas dadas |
| Corte admisible por electrodo (acero y aluminio) | Anexo 2 (tabla 3) | 6 + 4x4 | tau_adm = min(0,3 sigma_u; 0,4 sigma_y) para acero |
| Placas Al 2024-T42 (Ftu, Fty, Fcy, Fsu, Fbru, Fbry, E, G, mu, peso) | Anexo 3, pág. 18-22 | 8 espesores x ~14 propiedades | No |
| Resistencia última al corte de remaches (Fsu y carga por remache) | Anexo 3 cont., pág. 18-23 | 10 materiales x 9 diámetros | Carga = Fsu x area del **agujero** (ver riesgo 5) |
| Tipos de remaches y tornillos aeronáuticos (MS, NAS, AN) | Anexo 3, págs. 18-23/24 | solo figuras | No |
| Propiedades de adhesivos (corte y pelado) | Anexo 4, pág. 18-24 | 15 tipos x 2 | No |

### 3.1 Electrodos AWS (Anexo 2)  [resistencia a tracción / fluencia, MPa]
E60xx 427/345 (elong. 17-25 %) ; E70xx 482/393 (22 %) ; E80xx 551/462 (19 %) ; E90xx 620/531 (14-17 %) ; E100xx 689/600 (13-16 %) ; E120xx 827/737 (14 %).
Tabla de esfuerzos permisibles (AISC; Sy fluencia, Sut última): tensión a tope 0,60 Sy (n=1,67) ; aplastamiento a tope 0,90 Sy (n=1,11) ; flexión a tope 0,60-0,66 Sy (n=1,52-1,67) ; compresión simple a tope 0,60 Sy (n=1,67) ; cortante (tope o filete) 0,30 Sut del electrodo, y el corte en el metal base no debe exceder 0,40 Sy del base.
Corte admisible del filete (acero) MPa: E60 124 (18 ksi) ; E70 145 (21 ksi) ; E80 165 (24 ksi) ; E90 186 (27 ksi) ; E100 207 (30 ksi) ; E110 228 (33 ksi). Metales base típicos: E60 A36/A500 ; E70 A242/A441 ; E80 A572 gr. 65.
Aluminio, corte admisible [ksi/MPa], aleación de aporte 1100 / 4043 / 5356 / 5556: base 1100: 3,2/22 y 4,8/33 (4043) ; base 3003: 3,2/22 y 5,0/34 ; base 6061: 5,0/34 (4043), 7,0/48 (5356), 8,5/59 (5556) ; base 6063: 5,0/34 (4043), 6,5/45 (5356), 6,5/45 (5556).

### 3.2 Remaches aeronáuticos: carga última de corte simple por remache [lbf], diámetros nominales 3/32, 1/8, 5/32, 3/16, 1/4, 5/16, 3/8, 7/16, 1/2, 9/16 pulg (Anexo 3 cont.)
Fsu en ksi entre paréntesis; "-" = sin dato.
```
1100F(A)   (9)   sin cargas listadas
5056(B)    (28)  203 363  556  802 1450 2295  3275
2117-T3(AD)(30)  217 388  596  862 1555 2460  3510
2017-T31(D)(34)  247 442  675  977 1765 2785  3980
2017-T3(D) (38)  275 494  755 1090 1970 3115  4445
2024-T31(DD)(41) 296 531  814 1175 2125 3360  4800
7075-T73(E)(41)  sin cargas listadas
7075-T731(E)(43) 311 558  854 1230 2230 3525  5030
A-286 CRES (90)  -   -   1726 2485 4415 6906  9938
Ti-6Al-4V y acero de aleación (95)  - - 1822 2623 4660 7290 10490 14280 18650 23610
Acero de aleación (108)  - - 2071 2982 5300 8280 11930 16240 21210 26840
Acero de aleación (125)  - - 2397 3452 6140 9590 13810 18790 24540 31060
Acero de aleación (132)  - - 2531 3645 6480 10120 14580 19840 25920 32800
```
(Las filas de 7 columnas cubren los diámetros 3/32 a 3/8; las de 10 columnas llegan a 9/16.)

### 3.3 Placa Al 2024-T42 clad (Anexo 3, ksi)
Rangos de espesor (pulg): 0,008-0,009 ; 0,010-0,062 ; 0,063-0,249 ; 0,250-0,499 ; 0,500-1,000 ; 1,001-2,000 ; 2,001-3,000 con bases A, B (S desde 0,250). Ejemplo 0,063-0,249 base A / B: Ftu 60/62 (L y LT) ; Fty 36/38 ; Fcy 36/38 ; Fsu 36/37 ; Fbru (e/D=1,5) 90/93 ; (e/D=2,0) 114/118 ; Fbry (1,5) 50/53 ; (2,0) 58/61 ; E 10,5 (primario) 10,0 (secundario) x10^3 ksi ; Ec 10,7 / 10,2 ; mu = 0,33 ; peso específico 0,101 lb/pulg3. El resto de la tabla hay que transcribirlo de la imagen (PDF 374) al implementar; es una tabla de MMPDS/MIL-HDBK-5 de fuente Niu.

### 3.4 Adhesivos (Anexo 4): corte a temp. ambiente MPa (psi) / pelado kN/m (lbf/pulg)
Sensible a presión 0,01-0,07 / 0,18-0,88 ; almidón 0,07-0,7 / 0,18-0,88 ; celulósicos 0,35-3,5 / 0,18-1,8 ; base caucho 0,35-3,5 / 1,8-7 ; fusión caliente 0,35-4,8 / 0,88-3,5 ; fusión sintética 0,7-6,9 / 0,88-3,5 ; PVAc 1,4-6,9 / 0,88-1,8 ; cianoacrilato 6,9-13,8 / 0,18-3,5 ; proteína 6,9-13,8 / 0,18-1,8 ; acrílico anaeróbico 6,9-13,8 / 0,18-1,8 ; uretano 6,9-17,2 / 1,8-8,8 ; acrílico de caucho modificado 13,8-24,1 / 1,8-8,8 ; fenólico modificado 13,8-27,6 / 3,6-7 ; epóxico sin modificar 10,3-27,6 / 0,35-1,8 ; bismaleimida 13,8-27,6 / 0,18-3,5 ; poliimida 13,8-27,6 / 0,18-0,88 ; epóxico de caucho modificado 20,7-41,4 / 4,4-14. (Fuente Shigley/Pocius; son rangos, no valores de diseño.)

## 4. Ejemplos resueltos del texto

El capítulo **no trae ejemplos numéricos resueltos** (solo las curvas de la Fig. 6 foto-elástica y la Fig. 22 de una junta ASTM D1002: l=0,5 pulg, t=0,064 pulg, Al E=10 Msi, epoxi Ea=500 ksi, P=1000 lbf; curvas Volkersen y Goland-Reissner, sin tabla de valores).
Tests propios, calculados con script (no son del libro; usarlos como casos de regresión una vez implementado):
- Filete, verificación de ángulos: máximo de sigma* para theta en [0,90]: 62,5 grados, sigma* = 2,164, sigma = 0,6228, tau = 1,1964 ; máximo de (7): theta = 67,5 grados, 1,2071, con sigma = 0,5000.
- Grupo de cordones tipo 2 (dos verticales d=100 mm separadas b=100 mm), P=20 kN a a=150 mm del plano de los cordones, torsión sobre el grupo: Aw=200 mm ; Jw = d(3b^2+d^2)/6 = 666666,7 mm3 ; T = P a = 3e6 N mm ; f_V = P/Aw = 100 N/mm ; torsión en la esquina (50,50): f_T = T r/Jw = 318,2 N/mm con componentes ±225 en x e y ; resultante máxima (suma vectorial con el corte) = 395,3 N/mm en las esquinas donde se suman, 257,4 N/mm en las opuestas ; con E70xx (tau_adm = 145 MPa -> 0,707 x 145 = 102,5 N/mm por mm de pie): w >= 395,3/102,5 = 3,86 mm.
- Grupo de 4 remaches en (±25, ±25) mm, P=10 kN con e=100 mm: F1 = 2500 N ; sum r^2 = 5000 mm2 ; F2 = P e r/sum r^2 = 7071 N cada uno (r = 35,36 mm) ; resultante máxima = sqrt(7500^2 + 5000^2) = 9014 N (dos remaches), 5590 N (los otros dos).
- Volkersen (SI): Eo=Ei=70000 MPa, to=1,6 mm, ti=3,2 mm, G=1000 MPa, h=0,2 mm, b=l=25 mm, P=5000 N, dT=0 -> w = 0,2988 1/mm ; tau(0) = 0,714 MPa ; tau(+-12,5) = 14,957 MPa ; promedio P/(2 b l) = 4,0 MPa ; integral b x tau dx = P/2 = 2500 N ✓. (Datos inventados.)

## 5. Propuesta de implementación en Struttura

### 5.1 Calculadora de grupos de soldadura (tipo B) - **la más valiosa**
- Entrada CSV: bloque `CORDONES` (segmentos: x1,y1,x2,y2 o círculo cx,cy,d; w pie; opcionalmente 3D con plano local), `CARGAS` (punto de aplicación, fuerza y momento en 3D: N, Vy, Vz, Mx, My, Mz sobre el centroide o un punto), `ELECTRODO` (E60..E120 / tau_adm / tau_falla + CS). Salida: Aw, centroide, Ix, Iy, Ixy, ejes principales, Jw (todas calculables para segmentos arbitrarios, sin limitarse a las 9 figuras), f vectorial en puntos de muestreo, f_max, w requerido (16), CS de la unión, chequeo w <= espesor, informe HTML paso a paso con matrices de propiedades. Validación contra los 9 casos del Anexo 1.
- Se conecta con `portico3d`: tomar los esfuerzos de extremo de barra (N, Vy, Vz, T, My, Mz) por combinación (`esfuerzos.py`) en cada nudo y verificar el cordón alrededor del tubo (caso 9, círculo) o el cordón de un herraje. Modo "verificar nudo X de la barra Y".
- Dificultad 2-3. Tiempo: mediano. Dependencias: Cap. 17 (material/bulones) y los resultados de portico3d.

### 5.2 Calculadora de grupos de remaches/bulones (tipo B)
- Entradas: coordenadas de remaches (x,y,d), P (módulo, posición, dirección), t de placas, materiales (Fsu, Fbr), CS. Salidas: centro de gravedad del grupo, sum r^2, F1, F2 vectorial por remache, resultante máxima, tau, sigma_apl, margen. Más modo lineal con (17)-(20) para uniones de borde. Dificultad 1-2. Tiempo: chico. Se complementa con (12)(13) del Cap. 17.

### 5.3 Adhesivo, solape doble (tipo B pequeño) o solo anexo (tipo C)
- Volkersen (27)-(28) con curva tau(x) y tau_max/tau_prom; opcional efecto térmico. Dificultad 2. Tiempo: chico. Valor bajo-medio (carenados, paneles, no el fuselaje de tubo soldado).

### 5.4 Calidad/inspección, tipos de junta (tipo C)
- Resumen cualitativo (EPS/RCPS/RCS/mapa de soldadura, defectos, END) como anexo en informes. Dificultad 1.

### Aplicabilidad
- **Fuselaje de tubos soldados**: núcleo del valor. Casos aplicables: caso 9 (cordón circular completo de pie w sobre tubo: Aw = pi D, Sw = pi D^2/4, Jw = pi D^3/4) para uniones tubo-tubo o tubo-herraje con axil, flexión y torsión; para esfuerzos transversales el valor promedio V/Aw del libro subestima el máximo (en anillo delgado el máximo es ~2 V/Aw): usar el factor 2 o un tratamiento de cortante por posición (preguntar). Nudos tubo-tubo (boca de pez, clusters) tienen geometría de cordón alabeada que el capítulo no cubre (línea de cordón no plana): hay que aproximar con tramos o con factores. El libro advierte que la normativa aeronáutica (FAA) no permite reparar con soldadura ciertas partes críticas.
- **Remaches/bulones**: herrajes, soportes de motor y paneles con grupo de bulones excéntricos (5.2). **Adhesivos**: carenados, paneles.
- **Estructuras mecánicas generales**: uniones soldadas de bastidores, soportes y ménsulas con flexión+torsión; tablas de electrodos AWS; grupos de bulones en bridas.

## 6. Anexo teórico para los informes (qué incluir, sin copiar texto)
- Soldaduras: t = 0,707 w (3) ; método simplificado (12)-(13) con la justificación de conservadurismo (+17-18 % respecto de Tresca/Von Mises, (9)-(11)) ; tabla f = P/Aw, V/Aw, M/Sw, T c/Jw (Tabla 4) ; composición vectorial (14) ; criterio (15)-(16) con tau_adm del electrodo y regla w <= espesor ; propiedades de líneas (Anexo 1) usadas en cada caso del informe, con las fórmulas generales Aw = sum l_i, centroide, Ix, Iy, Jw = Ix + Iy.
- Remaches/bulones: (17)-(20) y (21)-(26) con el esquema de cargas excéntricas.
- Adhesivos: (27)-(28) y las reglas de diseño (corte, no pelado).
Siempre citar "Compendio CE-II, Cap. 18, sec./ec. n" y las fuentes (Shigley, Blodgett, Mott, AISC/AWS) que el propio capítulo da.

## 7. Riesgos, inconsistencias y preguntas al usuario

**Detectado en el texto / verificaciones**
1. Verifiqué numéricamente (8)-(11): theta = 62,5 (sigma* = 2,16) y 67,5 grados (1,207) ✓. El criterio llamado "Tresca" en (11) es el máximo del corte sobre el plano de la garganta, **no** el esfuerzo cortante máximo real del estado (sigma/2, tau): con ese criterio daría 1,237 P/(w l) a theta ~ 64 grados. Nota menor, la reserva de (12) cubre la diferencia (1,414 vs 1,237).
2. En (5)-(7) no se define bien theta (Fig. 5-b); es el ángulo del plano de la soldadura medido desde la dirección de P: t' = w/(cos th + sen th) se cumple. En (4)-(11) P es la carga por cordón: en la Fig. 5-a hay dos cordones y la carga es 2P.
3. Sentido de los momentos: la Tabla 4 solo da magnitudes. Para torsión la dirección de f_T es perpendicular al radio c y depende del punto (f_Tx = -T y/Jw, f_Ty = +T x/Jw respecto del centroide); el libro solo dice "componer vectorialmente" en (14). Para flexión, la distribución es lineal con signo (tracción/compresión en la garganta).
4. Eq. (24) del texto dice "La ecuación 21 se puede presentar así" pero la que se reescribe es la (22). En la Fig. 17 la fuerza se llama S en el texto y F2 en la ecuación (23)/(26); son la misma.
5. Anexo 3, tabla de remaches: las cargas de la tabla = Fsu x área del **agujero/remache colocado** (diámetro 3/32 -> 0,096 pulg, 1/8 -> 0,1285, 1/4 -> 0,257), no del nominal: 363 lbf = 28000 psi x pi 0,1285^2/4. Si se usa el diámetro nominal en (12)/(17) se obtiene ~6 % menos. Hay que decidir cuál usar.
6. Unidades: Anexos 2, 3, 4 están en ksi, psi, lbf, pulg. Conversión: 1 ksi = 6,89476 MPa.
7. Volkersen (27): el libro dice que están en unidades inglesas, pero es coherente en SI. El 2do término (con (2 Eo to - Ei ti)) se anula cuando los adherentes están "balanceados" (2 Eo to = Ei ti).
8. Los esfuerzos permisibles del Anexo 2 son AISC para acero estructural (E60-E120), no para tubo aeronáutico ni para chapa fina. Para t de pared de 1-2 mm el pie w máximo es ~ t (regla w <= espesor): con garganta 0,707 w la capacidad por mm de cordón es baja; hay que comprobar con tubo real.
9. El libro no trata fatiga de soldaduras (solo nota de eliminar refuerzo) ni efecto de zona afectada por el calor, ni cordones de tope en tubo.
10. La tabla Annex 2 lista E110 en la 3era tabla pero no en la primera (resistencia); E120 en la primera pero no en la tercera. Inconsistencia de fuentes (Shigley vs Mott).

**Preguntas al usuario**
- ¿Qué tubo (material, D, espesor) y qué electrodo/varilla de aporte usa el fuselaje? Con ello se cargan los tau_adm propios en lugar de los de acero estructural.
- ¿Usamos el esfuerzo de corte promedio del libro (V/Aw) o el máximo de anillo delgado (2V/Aw) para cordones circulares? (conservador vs fiel al libro)
- ¿Querés que la calculadora de cordones lea directamente las fuerzas de extremo de barra de portico3d (por combinación) y verifique el nudo?
- ¿Criterio de seguridad: CS global sobre tau_falla (ec. 15) o tau_adm de tabla? Hay que decidir y documentarlo en el informe.
