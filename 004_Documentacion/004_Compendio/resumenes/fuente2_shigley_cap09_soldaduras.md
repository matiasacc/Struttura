# Fuente 2 para soldaduras: Shigley's Mechanical Engineering Design, ed. 2024, cap. 9 (págs. 500–519)

Página del libro = PDF − 25 (ej.: libro 505 = PDF 530). Todo lo de abajo está leído del libro (texto o imagen de la página); lo que es mío está marcado **[propio]**.
Se usa junto con el Compendio cap. 18 (ver `cap18_resumen.md`): donde coinciden se cita ambos; donde difieren, se marca.

## 1. Método (igual al Compendio)
| Qué | Ecuación / lugar en Shigley | Compendio cap. 18 |
|---|---|---|
| Tope: σ = F/(h l), τ = F/(h l); h = garganta sin refuerzo; con fatiga conviene amolar el refuerzo | (9-1), (9-2), p. 500 | (1), (2) |
| Filete, ángulo θ: t = h/(cosθ + senθ); σ, τ, Von Mises en θ; máx. Von Mises en θ = 62,5° con σ' = 2,16 F/(hl) (τ = 1,196; σ = 0,623); máx. τ en θ = 67,5° con 1,207 F/(hl) (σ = 0,5) | (a)–(f), p. 501–502 | (4)–(11) |
| **Modelo de diseño**: todo como corte en la garganta mínima, τ = F/(0,707 h l) = 1,414 F/(h l) (17 % sobre 1,207) | (9-3), p. 503 | (12) |
| Primario τ' = V/A (A = área de garganta de todos los cordones) | (9-4), p. 503 | Tabla 4 |
| Secundario por torsión τ'' = M r / J (r desde el centroide del grupo) | (9-5), p. 504 | Tabla 4 |
| Cordón como línea (ancho unitario): J = 0,707 h Ju | (9-6), p. 505 | Anexo 1 (Jw) |
| Flexión: τ'' = M c / I, I = 0,707 h Iu; ej.: dos cordones separados d: τ'' = 1,414 M/(b d h); combinación vectorial τ = (τ'² + τ''²)^½ | (a)–(e), p. 509 | Tabla 4 |
| Pasos de verificación: tensiones primarias, secundarias, resistencia del base, del aporte, cargas admisibles de ambos | p. 503 | (15)–(16) |
| Advertencia: el electrodo suele ser el material más resistente → **verificar siempre las tensiones del metal base** | p. 512 | "verificar contra el material base" |
| Tratar el cordón como línea no afecta la conservadurismo del modelo (los ensayos de validación lo respaldan) | p. 509 | – |

## 2. Propiedades de grupos de cordones (como líneas). Coinciden con el Compendio Anexo 1
Tabla 9-1 (torsión, A y Ju) p. 506 y Tabla 9-2 (flexión, A e Iu respecto de un eje horizontal por G) p. 510–511. h = pie del filete; b = horizontal, d = vertical.
| Caso | A (garganta) | Ju (Tabla 9-1) | Iu (Tabla 9-2) |
|---|---|---|---|
| Una línea vertical d | 0,707 h d | d³/12 | d³/12 |
| Dos líneas verticales d, separadas b | 1,414 h d | d (3b² + d²)/6 | d³/6 |
| Dos líneas horizontales b, separadas d | 1,414 h b | (no está en 9-1) | b d²/2 |
| L (una b + una d) | 0,707 h (b + d) | [(b+d)⁴ − 6 b² d²] / [12 (b+d)]; x̄ = b²/(2(b+d)), ȳ = d²/(2(b+d)) | (no está en 9-2) |
| C (dos horizontales b + vertical d) | 0,707 h (2b + d) | (8b³ + 6bd² + d³)/12 − b⁴/(2b+d); x̄ = b²/(2b+d) | d² (6b + d)/12 |
| C invertida (una b + dos verticales d) | 0,707 h (b + 2d) | (no está en 9-1) | 2d³/3 − 2d²ȳ + (b+2d)ȳ²; ȳ = d²/(b+2d) |
| Rectángulo todo alrededor | 1,414 h (b + d) | (b + d)³/6 | d² (3b + d)/6 |
| Doble T (alas + alma) | 1,414 h (b + d) (Tabla 9-2, caso 8) | – | d² (3b + d)/6 |
| **Círculo (tubo)** radio r | 1,414 π h r | 2 π r³ | π r³ |
Verificación mía **[propio]**: C de Shigley (b = 50, d = 100): Ju = 385 416,7 y la fórmula del Compendio da lo mismo; círculo: Ju = 2πr³ = π d³/4 con d = 2r (igual al Compendio).
Pendiente al implementar: la fila 7 de la Tabla 9-2 trae las mismas fórmulas que la 5 con otro dibujo (T con dos verticales); confirmar en la imagen antes de cargarla. Como el programa calcula las propiedades para segmentos arbitrarios, estas tablas pasan a ser **casos de prueba**.

## 3. Datos
- **Tabla 9-3, electrodos AWS** (p. 511): E60 62/50 ksi (427/345 MPa), E70 70/57 (482/393), E80 80/67 (551/462), E90 90/77 (620/531), E100 100/87 (689/600), E120 120/107 (827/737); alargamiento 17–25, 22, 19, 14–17, 13–16, 14 %. (Igual al Compendio Anexo 2.)
- **Tabla 9-4, tensiones permitidas por AISC** (p. 512): tracción a tope 0,60 Sy (n = 1,67); aplastamiento a tope 0,90 Sy (1,11); flexión a tope 0,60–0,66 Sy (1,52–1,67); compresión simple a tope 0,60 Sy (1,67); **corte, tope o filete: 0,30 Sut del electrodo; el corte en el metal base no debe exceder 0,40 Sy del base**. (Igual al Compendio.)
- **Tabla 9-6, Cuadro A: corte admisible en la garganta** (p. 513): E60 18, E70 21, E80 24, E90 27, E100 30, E110 33, E120 36 ksi; fuerza unitaria admisible f = 0,707 h τadm (E60 12,73 h … E120 25,45 h kip/pulg, h en pulg). Hay una tabla de f para pies de 1/16 a 1 pulg. (**NUEVO respecto del Compendio**; coincide con sus 124/145/165/186/207/228 MPa.)
- **Tabla 9-6, Cuadro B: pie mínimo de filete h según el espesor de la pieza más gruesa** (p. 513): hasta 1/4 pulg → 1/8; 1/4–1/2 → 3/16; 1/2–3/4 → 1/4; 3/4–1½ → 5/16; 1½–2¼ → 3/8; 2¼–6 → 1/2; más de 6 → 5/8 pulg. Notas: no debe superar el espesor de la pieza más delgada; en puentes no baja de 3/16 pulg. Una nota con "5/16" y "3/4 pulg" está poco legible en la imagen: **volver a leerla con mayor resolución antes de implementar**. (**NUEVO respecto del Compendio**, que solo pide w ≤ espesor.)
- **Tabla 9-5, Kfs de fatiga (para la unidad de fatiga, más adelante)** (p. 512): tope con refuerzo 1,2; borde de filete transversal 1,5; extremo de filete paralelo 2,7; unión en T con esquinas vivas 2,0. "Deben usarse tanto para el metal base como para el de aporte."

## 4. Ejemplos del libro → casos de prueba reales (el Compendio no trae ninguno)
- **Ejemplo 9-1** (p. 506–508): fitting con 3 filetes de 6 mm sobre canal; placa de 25 kN (la mitad de 50 kN), b = 56, d = 190 mm. Resultados del libro: A = 1280 mm², τ' = 19,5 MPa, x̄ = 10,4 mm, rA = rB = 105 mm, rC = rD = 95,6 mm, J = 7,07·10⁶ mm⁴, M = 2760 N·m, τ''A = τ''B = 41,0 MPa, τ''C = τ''D = 37,3 MPa, τA = τB = 37,0 MPa, **τmáx = τC = τD = 43,9 MPa**.
- **Ejemplo 9-2** (p. 514): barra 1/2 × 2 pulg, 14 kip, filete de 3/8 pulg, 2 pulg de largo a ambos lados, E70xx. Peso: f = 5,57 kip/pulg → F = 22,28 kip > 14 (cumple); corte en el base 9,3 kpsi < 0,4 Sy = 11 kpsi; σ en la barra 14 kpsi ≤ 0,6 Sy = 16,5 kpsi.
- **Ejemplo 9-3** (p. 515–516): longitudes de cordones asimétricos con carga centrada: l1 = 2,16 pulg, l2 = 1,4 l1 = 3,02 pulg.
- **Ejemplo 9-4** (p. 516–517): flexión con 2 cordones: A = 1,06 pulg², Iu = 1,33 pulg³, I = 0,353 pulg⁴, τ' = 0,472 kpsi, τ'' = 8,50 kpsi, **τ = 8,51 kpsi**, n = 3,39 (aporte); base: σ = 12 kpsi, n = 2,67 (no cumple n ≥ 3); por código n = 3,38.
- **Ejemplos 9-5 y 9-6** (p. 518–519, fatiga, para después): Sse = 9,9 kpsi, τ'a = 2545 psi, nf = 3,9 (alternado puro, Kfs = 2,7); repetido (Fa = Fm = 1000 lbf): Kfs = 2, Ssu = 0,67 Sut, Goodman, nf = 4,2.

## 5. Observaciones a decidir entre ambos
1. **Fatiga de soldaduras** (para la unidad posterior): Shigley indica factor de superficie "forjado" para soldaduras salvo acabado superior especificado, kb = 1 para corte uniforme en la garganta, kc = 0,59 (torsión/corte), Ssu = 0,67 Sut y Goodman adaptado a corte. Falta ver de dónde salen kc = 0,59 y 0,67 (cap. 6 del Shigley) y combinarlo con la norma que se elija (IIW, AWS D1.1…).
2. **Solo flexión alrededor de un eje horizontal** en las dos fuentes. Para flexión biaxial en 3D el programa calculará Ix, Iy, Ixy del grupo por segmentos (mismo principio, **[propio]**: extensión a verificar con casos 2D antes de usar).
3. Los dos libros tratan el cordón de **tubo redondo completo** (caso 9). Cordones parciales sobre tubo y nudos en silla (tubo con tubo): ninguna fuente da el método → quedan marcados como **extensión** al usarlos.
4. Los valores del Cuadro B de tamaño mínimo están en pulgadas; al cargarlos habrá que convertirlos a mm (**[propio]**: conversión directa, sin redondear).
