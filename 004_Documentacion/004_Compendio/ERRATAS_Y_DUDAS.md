# Posibles erratas y dudas sobre el Compendio (a confirmar con la cátedra)

**Importante**: salvo que se indique lo contrario, son observaciones hechas al leer el texto extraído y las imágenes de las páginas
y recalcular las fórmulas. Pueden ser errores de transcripción del PDF o de lectura. **No tomarlas como ciertas sin confirmarlas.**
En el código, ante duda, se usa la versión coherente y se deja un aviso. (Páginas = páginas del PDF.)

| Cap | Dónde | Observación |
|---|---|---|
| 1 | Convención de λ | El libro usa σ' = λᵀ·σ·λ, que es la transpuesta de la convención habitual; ojo al transformar |
| 2 | Sec. 3 (ejemplo de tensión plana) | Con Von Mises (0,6; 0,2; −0,5)·σf no falla, aunque el texto dice que Tresca "acierta"; revisar |
| 2 | Sec. 6–7 | **Verificado**: la fórmula (13) es el criterio de *Mohr* (dúctiles, |σc|≠σt); para frágiles va *Mohr modificado*. Struttura 1.1.4 lo rotula mal (se corrige en U0) |
| 3 | Ec. (39) | Signo: debería ser +ν₂ |
| 3 | c̄máx por Von Mises | El valor 13,0486 no cierra; la raíz exacta da 14,01 |
| 3 | Ecs. (97)–(99) | Coeficientes de Von Mises para tres tubos: el tubo medio da 1,05 a 1,16 veces σf |
| 4 | Ec. (31) | Signo inconsistente en M21 |
| 4 | Placas circulares | "c" es el diámetro, no el radio |
| 4 | Intervalo 0,5h < w < w̄0·h | Falta un método |
| 5 | Ec. (55) | En α4 de tracción dice "sen" y debería ser "senh" |
| 6 | Ec. (58) | Signo invertido |
| 7 | Ecs. (24), (35), (67), (52) | (24) y (35) sin r; (67) no homogénea; (52) no reproducible desde (26) |
| 8 | Ecuación (6) y tabla ω | Falta la ecuación de la curva de interacción y la tabla del método ω |
| 9 | Ecs. (35)–(36) | Codos con presión: con p = 0 no dan el valor sin presión; **no implementar sin otra fuente** |
| 10 | Ecs. (88), (54) | (88) signo de B1; (54) superíndices de Sω cruzados respecto de (51)/(52); referencias cruzadas erróneas |
| 11 | Ec. (30), Figs. 1 y 3 | Signo en (30); Q con sentidos opuestos en las Figs. 1 y 3; cita "Cap. 10 (58)" mal referida |
| 12 | Texto / Tabla 1 | Llama "tensión plana" a una pieza larga (sería deformación plana); triángulo cúbico con 9 nodos (completo lleva 10) |
| 13 | Casos 3, 5 y 6 | Confirmar "b = ∞" del caso 3 y la definición de x en los casos 5 y 6 |
| 14 | Fig. 13, Fig. 21, aluminio | Fig. 13 rotula σm = 0,016·Su pero el cálculo usa 0,16; distribución 3 de la Fig. 21 integra 0,375 en vez de 1; el aluminio mezcla límites a 10⁷ y 5·10⁸ ciclos |
| 15 | Cap. 9 vs Anexo 14; Anexos 6-c y 11; ec. (6) | El factor i difiere unas 2,3 veces (el libro dice "levemente"); probables typos en Anexo 6-c y Anexo 11 (SA-335 P1); signos perdidos en la ec. (6) del texto extraído |
| 16 | Ecs. 19, 12, 9, 40; Anexos 8–11 | Eq. 19 sin el cuadrado; eq. 12 sin cos α en el numerador de Pa; eq. 9 pide una condición t/L que no corresponde al elipsoidal; eq. 40 llama "externo" a Rm; flujogramas de E ambiguos respecto de UW-12 |
| 17 | Ec. (43) | f'' mal impresa; corregida da f45 = 3867 mm y H = 9867 mm (el libro: 3877 y 9877) |
| 18 | — | Sin observaciones |


## Soldaduras (Shigley cap. 9 vs Compendio cap. 18) — detalle en `resumenes/fuente2_shigley_cap09_soldaduras.md`
- Coinciden Tablas 9-1/9-2 de Shigley con el Anexo 1 del Compendio (verificado numéricamente para C y círculo). Sin discrepancias de fórmula detectadas.
- Shigley Tabla 9-6, Cuadro B: una nota (límite de 5/16 pulg "por cada 3/4 pulg de material") es ilegible en la imagen a 110 dpi: releer a mayor resolución antes de implementar.
- Shigley Tabla 9-2, fila 7: mismas fórmulas que la fila 5 con otro dibujo; confirmar el dibujo antes de usarla como caso de prueba.
- Compendio: escribe τu y τy para los electrodos donde debería decir σu y σy (ya anotado en cap. 18).
- Fatiga de soldaduras (pendiente): de dónde salen kc = 0,59 y Ssu = 0,67 Sut en el Shigley (cap. 6); Kfs de la Tabla 9-5 aplica al metal base y al de aporte.
