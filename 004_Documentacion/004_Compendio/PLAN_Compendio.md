# Struttura × Compendio de Cálculo Estructural II (UNC FCEFyN, Massa-Giró, 2024)

Plan de trabajo para incorporar el Compendio a Struttura, unidad por unidad.
Estado: **en marcha** (Struttura v1.1.9: U0, U0b y S (soldaduras) hechas).  Las notas de lectura de cada capítulo están en `resumenes/capNN_resumen.md`
(escritas con palabras propias, con página y número de ecuación del libro; son material de trabajo, no reemplazan al libro).

## 1. Idea general: tres tipos de contenido

| Tipo | Qué es | Ejemplo |
|---|---|---|
| **A** | Programa matricial nuevo o extensión de uno existente (modelo → solver → informe) | pórtico 3D con segundo orden; MEF plano |
| **B** | Calculadora: CSV de entrada → informe HTML con **paso a paso** (fórmula, valores reemplazados, resultado, ecuación del libro) | fatiga, cilindros gruesos, uniones soldadas |
| **C** | Anexo teórico dentro de los informes ("Fundamento: Compendio cap. N") | ecuaciones usadas, hipótesis, límites de validez |

Todo se invoca igual que hoy: `python struttura.py archivo.csv` y la primera línea del CSV (`tipo;fatiga`, `tipo;tensiones`, …) elige el programa.
Mismo estándar en todos: CSV por bloques, informe HTML (con matrices/valores intermedios), visores con la navegación común, tests.

## 2. Dónde vive cada cosa

```
001_Codigo/struttura/
    emparrillado/ portico/ reticulado/ portico3d/        (ya existen)
    tensiones/   fatiga/   fractura/   secciones/        (calculadoras nuevas, un paquete por tema)
    pandeo/      uniones/  cilindros/  placas/  vigas_curvas/  recipientes/  canerias/  torres/
    plano2d/                                             (MEF de elasticidad plana, tipo A)
    datos/                                               (tablas del libro en CSV, cada fila con su fuente: capítulo y página)
    visor_comun.py  informe_comun (a extraer)           (estándar compartido)
002_Plantillas/        una plantilla CSV por programa
003_Ejemplos/          una carpeta por programa, con su _salida
004_Documentacion/004_Compendio/
    PLAN_Compendio.md  ERRATAS_Y_DUDAS.md  resumenes/    (este plan, dudas sobre el libro, notas por capítulo)
005_Tests/             un archivo de tests por programa
```
Los paquetes llevan nombre por **tema** (no "capítulo 14"); el capítulo se cita en el docstring y en el informe.

## 3. Mapa capítulo → programa

| Cap | Tema | Tipo | Paquete | Dif. | Valor para el fuselaje | Valor mecánica general |
|---|---|---|---|---|---|---|
| 1 | Ecuaciones de la elasticidad | B+C | tensiones | 2 | medio (tensor lleno, presión en tubos) | alto (base de todo) |
| 2 | Criterios de falla, CS | A+B | tensiones (extiende `portico3d/tensor.py`) | 2 | alto | alto |
| 3 | Cilindros de pared gruesa, zunchado | B | cilindros | 2 | medio (ajustes a presión) | alto |
| 4 | Placas | B | placas | 2 | alto (paneles entre tubos) | alto |
| 5 | Segundo orden, cargas críticas | A+B | pandeo | 3–4 | **alto** (tubos comprimidos) | alto |
| 6 | Pandeo de placas | B | placas | 2–3 | medio-bajo | medio |
| 7 | Pandeo de cilindros | B | pandeo | 2 | medio | medio |
| 8 | Pandeo local de perfiles | B (+chequeo en 3D) | pandeo | 1–2 | alto (tubos de pared fina) | alto |
| 9 | Vigas curvas | B → A | vigas_curvas | 2–3 | medio (tubos curvados) | alto |
| 10 | Vigas de pared delgada | B | secciones | 3 | alto (A, Iy, Iz, J de cualquier perfil) | alto |
| 11 | Compuestas / recubrimiento resistente | B | secciones | 2–3 | medio (piel, ala) | bajo (Mec. puede omitirlo) |
| 12 | Elementos finitos | A | plano2d | 3 | alto (herrajes, chapas) | alto |
| 13 | Mecánica de fractura | B | fractura | 2 | medio | medio |
| 14 | Fatiga | B+A | fatiga | 2–4 | **muy alto** (tubos 4130) | muy alto |
| 15 | Cañerías | A+B | canerias (codo sobre `portico3d`) | 3–4 | medio (tubos doblados) | alto |
| 16 | Recipientes a presión (ASME) | B | recipientes | 2–4 | bajo | alto |
| 17 | Torres | B+A | torres | 2–4 | medio (ω de pandeo, cables) | medio |
| 18 | Uniones (soldadura, remaches, adhesivos) | B | uniones | 2–3 | alto (cordones sobre tubo) | alto (Mec. puede omitirlo) |

Nota: el prólogo del libro dice que Mecánica puede omitir los caps. 11 y 18 y Aeronáutica los 15, 16 y 17.
La **dinámica** (modos y frecuencias, de la hoja de ruta anterior) no está en este libro: queda para después.

## 4. Orden propuesto de unidades (tentativo, se ajusta con vos)

| Unidad | Versión | Contenido | Por qué en este lugar |
|---|---|---|---|
| U0 ✔ | 1.1.6 | **HECHA.** Base del 3D: articulaciones (`art_i`/`art_j`), peso propio (`peso_propio` + `rho`), aviso de columnas ignoradas, **corrección Mohr / Mohr modificado** (ver §6) | Pendientes de antes; el Mohr es una corrección |
| U0b ✔ | 1.1.7 | **HECHA (núcleo).** Perfiles abiertos de pared delgada (canal, doble T, Té, Z, ángulo) con centro de corte, Jourawski y torsión; sección *Fundamento de cálculo* en el informe; `sectionproperties` solo como validación opcional en los tests. **Quedan para después (no hechos):** mapa de colores por EF (U0c) y tubo de pared gruesa. Texto original del plan: **Tensiones por sección (Gere)**: fórmulas propias para secciones abiertas de pared delgada (τ = T·t/J, flujo de corte, centro de corte), más formas y tubo de pared gruesa; bloque `PUNTOS_ANALISIS` (`barra;x;combinación`); sección por EF opcional con `sectionproperties` (mapa de colores σ/τ) | Fatiga trabaja con la tensión en un punto: primero hay que afinarla |
| **S ✔** | 1.1.8 | **HECHA (sin fatiga).** Modo rápido (`--soldadura` / `tipo;soldadura`) + bloque SOLDADURAS en el 3D, disposiciones, electrodos E60–E120 y propios, metal base, pie mínimo, dibujo 2D; memoria `Struttura_Memoria_soldadura.html`. **Unión a tope agregada** (tensiones, Tabla 9-4, Von Mises). **Pendiente:** fatiga de soldadura, uniones tubo con tubo (silla), penetración parcial, más electrodos/aportes (ampliar `soldadura/datos.py`), nota † de la Tabla 9-6 B (ambigua), dibujo 3D del cordón. Texto original: **PRIORIDAD del usuario, justo después de U0b: SOLDADURAS.** Cap. 18 (uniones soldadas: grupos de cordones, cordón circular sobre tubo) + verificación de la soldadura en los puntos del 3D + su fatiga (cap. 14). Se adelanta desde U6/U3 | Pedido explícito del usuario (fuselaje de tubos soldados) |
| U1 | 1.1.9 | Caps 1–2: calculadora `tensiones` (tensor lleno, principales, Mohr, Mohr modificado, σ\*, CS) | Es la base de todo lo demás |
| U2 | 1.1.10 | Cap 14: fatiga, calculadora (Se, Marin, Kf, Goodman/Soderberg/Gerber, Miner, Kimmelmann) | Mayor valor para tubos 4130 |
| U3 | 1.1.11 | Cap 14: fatiga conectada al pórtico 3D (casos como tensión media y alterna, puntos de tensión) | Cierra el ciclo con el fuselaje |
| U4 | 1.1.12 | Pandeo de barras: columnas (cap. 5), local (cap. 8), ω (cap. 17) como verificación en reticulado/pórtico 3D | Rápido y muy útil |
| U5 | 1.1.13 | Cap 10: calculadora de secciones de pared delgada → alimenta SECCIONES | Reemplaza el J a mano |
| U6 | 1.1.14 | Cap 18: uniones soldadas (grupos de cordones, cordón circular sobre tubo) | Conecta con esfuerzos del 3D |
| U7 | 1.1.15 | Cap 5: segundo orden y cargas críticas (2D → 3D con matriz geométrica) | El "pandeo global" de la hoja de ruta |
| U8 | 1.1.16 | Cap 12: `plano2d` (MEF, triángulo de deformación constante) | Programa nuevo |
| U9+ | 1.1.17… | Caps 3, 4, 6, 7, 9, 13, 15, 16, 17, 11, en el orden que elijas | Calculadoras independientes |

## 5. Receta de cada unidad (la misma siempre)

1. Releer las páginas del capítulo y confirmar fórmulas (no se implementa nada "de memoria").
2. Módulo con las fórmulas, citando capítulo / sección / ecuación en el código.
3. Plantilla CSV + ejemplo(s) en `003_Ejemplos`.
4. Informe HTML con paso a paso y anexo teórico.
5. Tests: casos analíticos, cálculo independiente (numpy), y los ejemplos del libro/prácticos si existen.
6. Actualizar guía rápida y README, subir versión, empaquetar zip.

## 6. Criterios de trabajo

* **Citas y propiedad**: se implementan las fórmulas y se cita el libro (capítulo, sección, ecuación). No se copian textos ni figuras; las tablas largas se cargan como datos en `datos/` con la página de origen y marcadas "transcriptas, a verificar".
* **Tablas que el libro no trae** (p. ej. cartas ASME de presión externa, tabla ω completa): no se inventan; se avisa y se pide el dato.
* **Validación**: el libro casi no trae ejemplos numéricos. Se valida con casos analíticos, cálculo independiente y, si los hay, los ejercicios de "Prácticos Resueltos".
* **Erratas / dudas**: la lectura detectó posibles erratas (`ERRATAS_Y_DUDAS.md`). En el código se usa la fórmula coherente y se deja un aviso visible; nada se da por cierto hasta confirmarlo con la cátedra.
* **Corrección propia detectada**: en `portico3d/tensor.py` la teoría `mohr` está rotulada "Mohr-Coulomb (frágil)". Según el libro (cap. 2, sec. 6–7) esa fórmula es el criterio de **Mohr** para dúctiles con |σc| ≠ σt; para frágiles con |σc| > σt corresponde **Mohr modificado**. El ejemplo 3 (fundición) debería usar el modificado. Además, la tensión equivalente que muestra la teoría `mohr` es la de Rankine. **Corregido en U0 (1.1.6)**: `mohr` usa σ* = σ1 + α|σ3|, nueva teoría `mohrmod`, ejemplo 3 migrado.

## 7. Preguntas abiertas

Ver el final de cada `resumenes/capNN_resumen.md` (sección 7). Las generales: orden de las unidades, si hay "Prácticos Resueltos" para validar, y qué estructura real vas a analizar primero.

## 8. Diseño general (no solo fuselaje): cómo se arma

**Dos piezas que se combinan**

1. **Solvers** (tipo A): emparrillado, pórtico plano, reticulado, pórtico 3D, y a futuro `plano2d`. Dan esfuerzos, tensiones y desplazamientos de *cualquier* estructura (mecánica, civil, aeronáutica).
2. **Verificaciones** (tipo B/C), enchufables sobre un modelo ya resuelto. Cada una recibe `(modelo, resultados, config)` y devuelve una tabla por barra/punto con el paso a paso: tensiones y CS (cap. 1–2), fatiga (14), pandeo de barras (5, 8, 17), uniones (18), curvas (9), fractura (13).
   Se activan con un bloque opcional `VERIFICACIONES` en el mismo CSV del modelo (p. ej. `fatiga;barra;material;acabado…`), o se usan solas como calculadoras (`tipo;fatiga`) para una pieza suelta.

**Componentes sueltos** (recipientes, cilindros gruesos, placas, cañerías, torres) son calculadoras independientes; las que tienen esfuerzos de barra (cañerías, torres) además se apoyan en el solver 3D.

**Lo que se comparte, para no repetir**
* `datos/materiales.csv`: biblioteca de materiales (E, ν, fy, su, Se′, K_Ic…, cada fila con su fuente) que usan todos los módulos.
* `datos/perfiles_*.csv`: tubos, ángulos IRAM, etc. y la calculadora de secciones (cap. 10) para las que no están.
* Un único estilo de informe (paso a paso con la ecuación citada) y los visores comunes.
* Normas y coeficientes como **datos reemplazables** (ASME, CIRSOC, DIN del libro hoy; otra norma mañana sin tocar el código).

**Ejemplos de uso general**: un eje con fatiga (calculadora de fatiga + tensiones), una estructura de acero civil (reticulado/pórtico + pandeo + uniones), un recipiente con silletas (recipientes + cilindros), una chapa con agujeros (plano2d), un fuselaje (pórtico 3D + fatiga + soldaduras).

## 9. Decisiones tomadas por defecto (se pueden cambiar)
* Orden por valor general (tabla §4); U0 primero (corrección del Mohr, articulaciones 3D, peso propio) — **hecha en 1.1.6**.
* **Tensiones por sección antes que fatiga (U0b)**: fórmulas propias del Gere como núcleo (liviano y trazable); `sectionproperties` solo como extra OPCIONAL (mapa de tensiones por EF y validación independiente). Si la librería falta o falla, el programa avisa y sigue con las fórmulas propias; versión fijada en `requirements.txt`.
* Puntos de interés elegidos por el usuario (`PUNTOS_ANALISIS`: barra, x, combinación) para el análisis detallado; el barrido rápido por toda la barra se mantiene con las fórmulas propias.
* **Soldaduras = prioridad inmediatamente después de U0b** (unidad S, v1.1.8); la fatiga (U2/U3) se apoya en ella porque en estructuras soldadas la falla por fatiga suele estar en el cordón.
* **Fuentes de U0b**: Compendio cap. 10 (secciones abiertas/cerradas, centro de corte, Bredt, alabeo) + **Gere & Goodno, 7ª ed. (edición completa, 1045 págs.)**: 3.10 tubos de pared delgada/Bredt (p. 270), 3.11 y 5.13 concentración de tensiones (p. 279, 418), 5.8–5.10 corte en vigas (p. 387–408), 6.5 flexión asimétrica (p. 479), 6.6–6.9 centro de corte y corte en secciones abiertas (p. 487–496), cap. 7 tensión plana/Mohr y cargas combinadas.  El Gere *Brief* (644 págs.) no trae esos temas y solo sirve para validar lo básico.
* **Unidad S (soldaduras) — diseño acordado**: bloque `SOLDADURAS` en el CSV del modelo (`barra; extremo; disposición; electrodo; [w]`: sin w, calcula el pie necesario) y modo rápido sin armar estructura (comando de una línea o CSV mínimo). Disposiciones: todo alrededor, solo costados, solo arriba/abajo, tubo redondo completo, segmentos propios. Dibujo 2D del cordón coloreado por carga (3D después). Fuentes: Compendio cap. 18 + Shigley cap. 9 (`resumenes/fuente2_shigley_cap09_soldaduras.md`, con los ejemplos 9-1 a 9-4 como casos de prueba). **Fatiga de soldaduras: más adelante** (se acopla después).
* **Regla de informes (pedido del usuario)**: cada informe/memoria debe dejar asentado, en el propio documento, **qué se usó para calcular**: fórmula, ecuación y página de la fuente, y en qué caso aplica (sección "Fundamento" por cálculo), para no tener que adivinar. Todo supuesto propio se marca **[propio]**.
* **Fuentes en mano**: Compendio CE-II; Gere & Goodno 7ª ed. (completo) y Gere Brief; Shigley 2024. El usuario ofreció normas AWS: pedir las que se necesiten cuando se llegue a fatiga de soldaduras (candidatas: AWS D1.1, D17.1; IIW; Eurocode 3).
* **Regla del usuario**: no se inventa nada que no esté en el libro (fórmulas, valores, criterios); toda duda o supuesto propio se marca y se decide entre ambos.
* Struttura es un programa de uso personal (no se publica ni comercializa): no hace falta pensarlo para terceros.
* Ante una posible errata: fórmula coherente + aviso visible + registro en `ERRATAS_Y_DUDAS.md`.
* Validación con casos analíticos y cálculo independiente; si aparecen los "Prácticos Resueltos", se suman.
