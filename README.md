# Struttura –  cálculo de estructuras por el método matricial de rigidez (v1.1.15)

Cuatro programas en Python bajo un mismo comando, `python struttura.py ARCHIVO.csv`, con **una plantilla de CSV para cada uno**:

| Programa | Estructura | GDL por nodo | Plantilla | Memoria |
|---|---|---|---|---|
| **Emparrillado plano** | barras en el plano XY, carga perpendicular al plano | `uz, φx, φy` | `002_Plantillas/plantilla_emparrillado.csv` | `004_Documentacion/002_Memorias/Struttura_Memoria_emparrillado.html` |
| **Pórtico plano** | barras en el plano XY, cargas en su plano | `ux, uy, φ` | `002_Plantillas/plantilla_portico.csv` | `004_Documentacion/002_Memorias/Struttura_Memoria_portico.html` |
| **Pórtico espacial 3D** (nudos rígidos o articulados por barra) | barras en el espacio, 12×12 por barra | `ux, uy, uz, φx, φy, φz` | `002_Plantillas/plantilla_portico3d.csv` | `004_Documentacion/002_Memorias/Struttura_Memoria_portico3d.html` |
| **Soldaduras de filete** (modo rápido o dentro del 3D) | grupos de cordones con N, V, T, M | – | `002_Plantillas/plantilla_soldadura.csv` | `004_Documentacion/002_Memorias/Struttura_Memoria_soldadura.html` |
| **Reticulado plano** (bielas) | barras articuladas, cargas solo en nudos | `ux, uy` | `002_Plantillas/plantilla_reticulado.csv` | `004_Documentacion/002_Memorias/Struttura_Memoria_reticulado.html` |

**Guía rápida (PDF):** `004_Documentacion/001_Guia_rapida/Struttura_Guia_rapida.pdf`: todos los bloques, columnas y opciones de las plantillas.

## Organización de carpetas

```
Struttura/
├── struttura.py                 ← comando de entrada
├── README.md
├── 001_Codigo/struttura/        ← paquete Python (emparrillado/, portico/, reticulado/, portico3d/, despachador.py)
├── 002_Plantillas/              ← plantillas comentadas, listas para copiar
├── 003_Ejemplos/
│   ├── 001_Emparrillado/
│   ├── 002_Portico/
│   ├── 003_Reticulado/
│   └── 004_Portico_espacial/
├── 004_Documentacion/
│   ├── 001_Guia_rapida/
│   ├── 002_Memorias/
│   └── 003_Generadores/         ← scripts que regeneran guía y memorias
└── 005_Tests/                   ← python -m unittest discover -s 005_Tests
```

Los paquetes de Python conservan nombres en minúscula y sin número (`struttura`, `emparrillado`, …) porque Python no puede importar carpetas que empiezan con dígitos.

## Versiones

A partir del nombre Struttura la numeración es **1.1.x**: 1.1.0 = reorganización (nombre, carpetas, comando) sobre lo que antes figuraba como «2.3».
**1.1.1** = programa de pórtico espacial 3D (`tipo;portico3d`, nudos rígidos) + 4 ejercicios de parcial validados (pórtico y emparrillado).  **1.1.2** = todos los informes traen el Anexo A con las matrices de rigidez (por barra y ensambladas) sin límite de tamaño (`anexo_matrices;no` lo apaga); el 3D muestra k local y global de 12×12.  **1.1.3** = tensor de tensiones en el 3D (puntos críticos automáticos + bloque `PUNTOS DE TENSION`), teorías Von Mises / Tresca / Rankine / Mohr-Coulomb (`teoria`, `sut`, `suc` en MATERIALES), `tensores.csv` y mapa de utilización en el visor.  **1.1.4** = estándar común de los 4 visores (`visor_comun.py`): modo Estructura limpio (sin cargas ni deformada), selector de Barra en los diagramas, navegación tipo SolidWorks (girar; Ctrl+arrastrar = desplazar; rueda o Shift+arrastrar = zoom; doble clic = ajustar) y redibujado liviano.  **1.1.5** = apoyos como nudos de color (verde = apoyo, naranja = solo resorte) con recuadro al pasar el mouse que muestra las condiciones de borde (restringidos = 0 o valor prefijado, libres, rigidez de resortes), igual en los 4 visores.  **1.1.6** (unidad U0 del plan del Compendio) = en el 3D: articulaciones por barra (`art_i` / `art_j`: rótula esférica o `my`/`mz`/`t`, con condensación estática; los nudos con todas las barras articuladas se estabilizan solos), peso propio automático (`peso_propio;CASO` en PROYECTO + `rho` en kg/m³ en MATERIALES, `gravedad;-z`), aviso de columnas no reconocidas en cualquier bloque, y corrección de los criterios de Mohr: `mohr` (dúctil con |σc| > σt, σ* = σ1 + α·|σ3|) y nueva `mohrmod` (Mohr modificado para frágiles); `CS_MohrMod` en `tensores.csv`.  Ejemplos nuevos: `ejemplo5_articulaciones_y_peso_propio.csv`; el ejemplo 3 (fundición) pasa a Mohr modificado.  **1.1.7** (unidad U0b) = tensiones por sección en el 3D: perfiles abiertos de pared delgada `canal`, `doble_t`, `te`, `z` y `angular` (dimensiones de línea media `h`, `b`, `t` o `tf`/`tw`) con propiedades, ejes principales, centro de corte, corte de Jourawski y torsión de Saint-Venant (J = Σ l·t³/3); la torsión incluye el momento V·e cuando la carga no pasa por el centro de corte (se desprecia el alabeo impedido); la **Memoria del programa 3D** (`Struttura_Memoria_portico3d.html`) deja asentado qué se usa: fórmula, fuente y caso (lo propio va marcado [propio]); cada unidad nueva agrega ahí sus filas.  Ejemplo: `ejemplo6_perfiles_pared_delgada.csv`.  **1.1.8** (unidad S) = **soldaduras (filete y a tope)**: verificación de grupos de cordones (método de la garganta, cordones como líneas; Shigley cap. 9 + Compendio cap. 18).  Modo rápido: `python struttura.py --soldadura \"circulo d=50.8 Vz=3000 My=200000 electrodo=E70 w=3\"` o un CSV mínimo con `tipo;soldadura`; da la fuerza por mm de cordón en el punto crítico, el **pie de filete requerido** (sin `w`) o el CS (con `w`), verificación del metal base y pie mínimo, y dibujo 2D del cordón coloreado por carga.  Disposiciones: círculo, arco, rectángulo, solo costados, solo arriba y abajo, línea, L, C, C invertida, doble T y segmentos propios; electrodos E60–E120 y aportes propios (bloque ELECTRODOS).  Unión **a tope** (`tipo=tope`, `esp` = espesor): tensiones σ y τ, admisibles de la Tabla 9-4 de Shigley y Von Mises.  En el pórtico 3D, el bloque `SOLDADURAS` toma los esfuerzos del solver en el extremo de la barra (todos los casos y combinaciones) y escribe `soldaduras.csv`.  Memoria propia con fórmulas y fuentes; ejemplos 9-1, 9-2 y 9-4 de Shigley como pruebas.  **1.1.9** = **biblioteca de materiales** (`006_Biblioteca/materiales.csv`, personal; viene en la carpeta del programa desde 1.1.12): una fila por material con número permanente; en MATERIALES, `lib;N` completa E, G, nu, fy, sut y rho en el 3D (y E, nu o G y fy en pórtico plano, emparrillado y reticulado), y lo escrito a mano manda; `--biblioteca listar | ver N`; también se puede agregar una fila a mano.  Pórtico 3D: la **utilización** se ve al pasar el mouse sobre la estructura (1 = fluencia).  Soldadura: **arcos** múltiples (`arcos`), pie mínimo según el espesor de la parte más gruesa (Tabla 9-6 B) y asterisco rojo cuando el pie a adoptar supera el espesor de la parte fina (queda a criterio del diseñador).  **Peso propio** (`peso_propio;CASO`, `gravedad`, `rho`) y modo **Utilización** del visor (σeq/fy y σeq/σadm al pasar el mouse) en los cuatro programas; qué tiene cada programa: `004_Documentacion/MATRIZ_DE_PARIDAD.md`.  **Todas las memorias** (3D, emparrillado, pórtico, reticulado, soldadura y biblioteca) tienen ahora un mapa de uso visual.  También en los cuatro: aviso de columnas no usadas en cualquier bloque, `corte_tensiones`, `escala_diagramas` (con casilla «escala única» en el 3D), diagramas V/T/M en el visor del emparrillado y **articulaciones por barra en el emparrillado** (`art_i` / `art_j` = `m` flexión, `t` torsión, `mt` ambas; ejemplo 10).  **Paridad de los cuatro programas**: `pandeo` por barra (Euler) en 3D y pórtico plano; criterios de falla (`teoria`, `sut`, `suc`: Von Mises, Tresca, Rankine, Mohr) y perfiles de pared delgada en pórtico plano y emparrillado; soldaduras en pórtico plano y emparrillado (ejemplos 12 y 13); biblioteca de electrodos (`006_Biblioteca/electrodos.csv`, `lib` en ELECTRODOS) y `sy_base` desde `lib`; `escala_diagramas` por defecto `barra` en todos.  **Ejemplo 16 del 3D**: fuselaje Sonerai II con soldaduras en los 10 extremos de barra más exigidos (`ejemplo16_fuselaje_soldaduras_criticas.csv`).  **Ejemplo 14 del pórtico plano**: pórtico biempotrado con doble T de pared delgada, contrastado a mano (`ejemplo14_verificacion.txt`).  **1.1.10** = **editor visual de modelos**: `python struttura.py --editor [modelo.csv]` abre en el navegador (servidor local, sin internet) tablas guiadas con todas las columnas de cada bloque (ayuda y opciones) y un dibujo donde se ve la estructura (nodos, barras, apoyos, cargas); se crean nodos y barras con el mouse, se ponen apoyos y cargas, se arrastran nodos; Revisar marca el bloque y la fila con error; Guardar como en cualquier carpeta; Calcular corre el cálculo de siempre y abre el informe.  Los cuatro tipos (3D, pórtico plano, emparrillado, reticulado) y el modo soldaduras (solo tablas); el CSV sigue siendo la fuente de verdad y conserva comentarios y columnas extra.  Memoria: `Struttura_Memoria_editor.html`.  **1.1.11** = pulido del editor tras la primera prueba: nombres claros con unidades en todas las columnas y opciones, desplegables «id: detalle» para nodos, materiales y secciones, material de la biblioteca como primera columna (y «Agregar material de la biblioteca»), secciones que muestran solo las medidas de su forma, apoyos Fijo/Libre con tipo de apoyo, articulaciones por nombre, Enter para aceptar, nodos repetidos evitados (y «Unir»), etiquetas y cargas que no se pisan, y Guardar como que muestra la ruta completa con «Abrir carpeta».  **1.1.12** = **biblioteca de perfiles** (`006_Biblioteca/perfiles.csv`: tablas CIRSOC 301/302 de perfiles laminados IPN, IPB, IPBl, IPBv, IPE, W, HP, M, UPN, C, MC, ángulos, tes y tubos circulares, cuadrados y rectangulares; 895 perfiles, valores tal cual figuran en las tablas con la unidad en el nombre de cada columna; el PDF de origen está en `006_Biblioteca/fuentes/`): en SECCIONES, `tipo;perfil` + `lib;N` completa A, I, J, c… en las unidades del modelo (los cuatro programas; lo escrito a mano manda) y el editor lo elige de un desplegable agrupado por familia; `--biblioteca perfiles [FAMILIA]` y `--biblioteca perfil N`; ejemplos nuevos (3D 17, pórtico 15, emparrillado 13, reticulado 6).  La carpeta `006_Biblioteca` (materiales, electrodos y perfiles) **ahora viene dentro del zip**.  Dos datos de la tabla no cierran y quedan anotados en `observaciones` (IPBv 320: Sx; UPN 50: Iy).  **1.1.13** = el visor del reticulado muestra solo el diagrama de axil (sin corte ni flector).  **1.1.14** = `py struttura.py` sin argumentos (o con `-h`) muestra el menú de opciones en vez del error.  **1.1.15** = el aviso «datos de la biblioteca» pasa a ser una nota informativa (gris, «Nota:») en el editor, la consola y los informes; los avisos quedan solo para lo que importa.  Los cambios siguientes se numeran 1.1.16, 1.1.17… El historial de abajo conserva la numeración anterior (v1.2–v2.3) tal como se fue desarrollando.

Comandos: `python struttura.py ARCHIVO.csv` (elige el programa solo), `--solo-esquema`, `--sin-graficos`, `-o CARPETA`, `--tipo portico|portico3d|reticulado|emparrillado`, `--editor [ARCHIVO.csv]` (editor visual), `--version`.
También sirve `python -m struttura ARCHIVO.csv` (con `001_Codigo` en el `PYTHONPATH`).

Requiere **Python ≥ 3.9**, `numpy` y `matplotlib`. Nada más.  Basado en las tablas de matrices de rigidez de cátedra.

**Elección del programa:** `struttura.py` lee la línea `tipo;portico` / `tipo;emparrillado` del bloque PROYECTO; si falta, mira el
encabezado del bloque APOYOS (`ux;uy;phi` = pórtico, `uz;phix;phiy` = emparrillado).  También se puede forzar con `--tipo portico`.


## PÓRTICO PLANO – uso rápido

```
python struttura.py 003_Ejemplos/002_Portico/ejemplo1_portico_simple.csv                  # calcula y genera el informe
python struttura.py 003_Ejemplos/002_Portico/ejemplo1_portico_simple.csv --solo-esquema   # solo dibuja los datos para revisarlos
```

Resultados en `<archivo>_salida/`: `informe.html` y CSV (`desplazamientos, reacciones, resortes, esfuerzos, tensiones, matriz_K`).

### Bloques del CSV de pórtico

| Bloque | Oblig. | Columnas |
|---|---|---|
| PROYECTO | no | `clave;valor` (**tipo;portico**, proyecto, autor, unidad_fuerza, unidad_longitud, escala_deformada, escala_diagramas, anexo_matrices, csv_salida) |
| NODOS | sí | `id;x;y` |
| MATERIALES | sí | `id;E;nu;fy;sadm;alfa` |
| SECCIONES | sí | `id;tipo;d;t;b;h;I;A;c;kv` (tubo, circular, rectangular, rect_hueca, generica con I y A; `h` = dimensión en el plano) |
| BARRAS | sí | `id;nodo_i;nodo_j;material;seccion;art_i;art_j` (art = 1: articulación en ese extremo) |
| APOYOS | sí | `nodo;ux;uy;phi` (1 = restringido) |
| RESORTES | no | `nodo;kx;ky;kphi` |
| RESORTES INCLINADOS | no | `nodo;k;angulo` (eje a `angulo` grados de +X, antihorario) |
| CARGAS | no | `caso;nodo;Px;Py;M` (M antihorario +) |
| CARGAS EN BARRAS | no | `caso;barra;tipo;valor;valor2;a;b` — `q` (⊥), `qa` (axial), `qgx`/`qgy` (global, por longitud de barra), `qgxp`/`qgyp` (global, por longitud **proyectada**), `P`, `Pa`, `Pgx`, `Pgy` (puntuales en `a`), `Mp` (momento puntual), `temp` (valor = ΔT cara +yl, valor2 = ΔT cara −yl) |
| DESPLAZAMIENTOS PREFIJADOS | no | `caso;nodo;ux;uy;phi` (solo GDL restringidos) |
| DESAJUSTE DE RESORTES | no | `caso;nodo;ux;uy;phi;inclinado` (apoyo corrido; resorte más corto → e < 0) |
| COMBINACIONES | no | `combinacion;caso;factor` |

Ejemplos en `003_Ejemplos/002_Portico/`: `ejemplo1_portico_simple.csv` (portal, q global, viento, combinación), `ejemplo2_tres_articulaciones.csv`
(pórtico a dos aguas con rótula en la cumbrera, nieve proyectada y viento; el test compara el empuje con qL²/8f),
`ejemplo3_resortes_asentamiento.csv` (resorte recto e inclinado con desajuste, asentamiento), `ejemplo4_temperatura_y_puntuales.csv`
(temperatura uniforme y en gradiente, puntuales, momento puntual y carga axial trapecial), `ejemplo5_reticulado_parcial2020.csv` (reticulado del examen: se resuelve con todas las barras articuladas).

### Convenciones del pórtico

* **Global:** X → derecha, Y ↑; φ y momentos **antihorarios positivos**; las cargas gravitatorias son negativas (en Y).
* **Local de barra:** `xl` de `nodo_i` a `nodo_j`, `yl` a 90° antihorario.  `k_glo = T·k_loc·Tᵀ` con R = [γ1 −γ2 0; γ2 γ1 0; 0 0 1].
* **Esfuerzos (ejes locales):** `N` > 0 tracción; `V` > 0 si actúa hacia −yl sobre la cara +xl (corte "horario"); `M` > 0 si tracciona la fibra −yl.
  Los diagramas de M se dibujan del lado traccionado; N y V hacia +yl.  Intercambiar i↔j cambia el signo de M (no el de N ni el de V).
* Sin conversión de unidades: usar un sistema coherente.  `CS fluencia = fy/σVM`, `CS admisible = σadm/σVM`.
* Articulaciones por condensación estática; nodo con todas las barras articuladas: su φ se fija internamente (aviso).

### Reticulado plano – uso rápido

```
python struttura.py 003_Ejemplos/003_Reticulado/ejemplo5_cercha_con_pandeo.csv
```

Mismos bloques que el pórtico pero sin giros ni momentos (APOYOS `nodo;ux;uy`, CARGAS `caso;nodo;Px;Py`, RESORTES `nodo;kx;ky`);
BARRAS admite la columna `pandeo`; en CARGAS EN BARRAS solo `temp`, `corta` y `larga`. Detalles en la guía rápida (`004_Documentacion/001_Guia_rapida/Struttura_Guia_rapida.pdf`).

### Limitaciones del pórtico

Teoría de Euler-Bernoulli lineal (sin corte, sin 2º orden, sin pandeo); articulaciones solo en extremos de barra; secciones simétricas; matriz densa.

## Novedades de la v2.2

* **Reticulado plano (bielas)** (`reticulado/`, `tipo;reticulado`, plantilla `002_Plantillas/plantilla_reticulado.csv`): 2 GDL por nodo, barras articuladas, N, σ, ΔL, CS fluencia/admisible y
  **pandeo de Euler** con la tabla de la cátedra (columna `pandeo` en BARRAS: `art-art`, `emp-lib`, `emp-art`, `emp-emp`). Las barras son bielas: **cargas solo en nudos** (sin carga en el tramo ni perpendicular). Acepta resortes, resortes inclinados, desajustes, prefijados, combinaciones y, en CARGAS EN BARRAS, solo los efectos de Estado I de Brewer: `temp` (ΔT uniforme), `corta` y `larga` (desajuste e de longitud).
  Ejemplos en `003_Ejemplos/003_Reticulado/`: los 4 ejercicios de Brewer (reproducidos) y una cercha con pandeo. El parcial 2020 (con q axial) queda en `003_Ejemplos/002_Portico/ejemplo5` porque tiene carga en el tramo. Salida: `informe.html`, `barras.csv`, `desplazamientos.csv`, `reacciones.csv`, `resortes.csv`.
* **Resortes con forma de resorte** en todos los gráficos (estáticos y visor interactivo): zigzag verde con rayado para los lineales (X, Y, inclinados), espiral para el torsional (`kphi`), y leyenda «resorte (no es una barra)».
* **Guía rápida en PDF** (`004_Documentacion/001_Guia_rapida/Struttura_Guia_rapida.pdf`, generada por `004_Documentacion/003_Generadores/generar_guia_rapida.py`): todos los bloques y columnas de las tres plantillas, tipos de carga y sección, signos, recetas y errores frecuentes.
* Tres ejercicios de la cátedra reproducidos y con test (`003_Ejemplos/002_Portico/ejemplo6..8`): TP5 2022 (resorte inclinado + giro y desplazamiento prefijados), parcial con desplazamiento prefijado y pórtico con barra de reticulado.
* `003_Ejemplos/002_Portico/ejemplo9_todos_los_resortes.csv`: catálogo de resortes.
* Una barra con sección sin `c` ni `I` (barra de reticulado) ahora informa su tensión axial N/A.
* El despachador `struttura.py` reconoce `tipo;reticulado` (o, sin tipo, `APOYOS` con `ux;uy` sin `phi`).
* Nuevo tipo de carga en barra `dl` (desajuste de longitud, e > 0 barra larga) también en el pórtico.
* Tests: 121.

## Novedades de la v2.1

* Nuevo `003_Ejemplos/002_Portico/ejemplo5_reticulado_parcial2020.csv`: reticulado del 1er parcial 2do sem. 2020 (barras articuladas, ΔT uniforme, q axial, uy prefijado); el test reproduce los resultados del examen.
* Corrección: una temperatura uniforme en una barra cuya sección no tiene `h` daba error; ahora `h` solo se pide si hay gradiente.

## Novedades de la v2.0

* **Programa de pórtico plano** completo (`portico/`), con su plantilla de CSV separada, informe, visor 2D interactivo, memoria y tests.
* `struttura.py` elige el programa según el archivo; plantillas comentadas en `002_Plantillas/`; ejemplos reorganizados en `003_Ejemplos/001_Emparrillado/` y `003_Ejemplos/002_Portico/`.
* Tests: 102 (`python -m unittest discover -s tests`).

## EMPARRILLADO – uso rápido

```
python struttura.py 003_Ejemplos/001_Emparrillado/ejemplo2_parrilla.csv                  # calcula y genera el informe
python struttura.py 003_Ejemplos/001_Emparrillado/ejemplo2_parrilla.csv --solo-esquema   # solo dibuja los datos para revisarlos
```

Los resultados quedan en `<archivo>_salida/` (`informe.html` y CSV de resultados).
Opciones: `-o CARPETA`, `--sin-graficos`.
Tests: `python -m unittest discover -s tests -v`

### Archivo de datos: UN solo CSV con bloques titulados

Cada bloque empieza con una línea que tiene solo su título, luego los encabezados y los datos.
Líneas vacías y líneas con `#` se ignoran. Acepta `;` con coma decimal (Excel en español) o `,` con punto.

| Bloque | Oblig. | Columnas |
|---|---|---|
| PROYECTO | no | `clave;valor` (tipo, proyecto, autor, unidad_fuerza, unidad_longitud, escala_deformada, anexo_matrices, csv_salida) |
| NODOS | sí | `id;x;y` |
| MATERIALES | sí | `id;E;nu;G;fy;sadm;alfa` (G o nu; fy y sadm opcionales; alfa solo para cargas térmicas) |
| SECCIONES | sí | `id;tipo;d;t;b;h;I;J;A;c;Wt;kv` (tipos: tubo, circular, rectangular, rect_hueca, generica; `h` = altura, se usa en cargas térmicas) |
| BARRAS | sí | `id;nodo_i;nodo_j;material;seccion` |
| APOYOS | sí | `nodo;uz;phix;phiy` (1 = restringido) |
| RESORTES | no | `nodo;kz;kphix;kphiy` |
| CARGAS | no | `caso;nodo;Pz;Mx;My` (cargas en nodos) |
| CARGAS EN BARRAS | no | `caso;barra;tipo;valor;valor2;a;b` — tipos `q` (distribuida: valor en a, valor2 en b, vacío = uniforme; a,b vacíos = toda la barra), `P` (puntual en a), `temp` (valor = ΔT fibra superior, valor2 = ΔT fibra inferior). a y b se miden desde nodo_i; positivo hacia +z |
| RESORTES GIRO INCLINADO | no | `nodo;k;angulo` — resorte de torsión con eje en el plano a `angulo` grados de +X (antihorario). Se opone a θa = φx·cosβ + φy·senβ; aporta k·a·aᵀ a K |
| DESPLAZAMIENTOS PREFIJADOS | no | `caso;nodo;uz;phix;phiy` (solo GDL restringidos) |
| DESAJUSTE DE RESORTES | no | `caso;nodo;uz;phix;phiy` — desplazamiento impuesto al apoyo del resorte recto (fuerza = −k(u−e)). Resorte 5 mm más corto (estirado al conectarlo): e = −5 |
| COMBINACIONES | no | `combinacion;caso;factor` |

Ejemplos en `003_Ejemplos/001_Emparrillado/`: `ejemplo1_voladizo_L.csv` (con solución analítica), `ejemplo2_parrilla.csv`
(casos, descenso de apoyo y combinaciones), `ejemplo3_resortes.csv` (apoyada solo en resortes),
`ejemplo5_parcial2020.csv` (1er parcial 2020 de la cátedra: q, gradiente térmico, resorte y giros prefijados; el test lo compara con el examen resuelto),
`ejemplo6_cargas_en_tramos.csv` (parrilla con q uniforme, trapecial parcial, P puntual, gradiente térmico y momentos nodales).

### Convenciones

* **Global:** X → derecha, Y ↑, **z hacia el lector**. `Pz > 0` apunta a +z: **las cargas gravitatorias son negativas**.
  Momentos y giros son vectores (mano derecha).
* **Local de barra:** `xl` de `nodo_i` a `nodo_j`, `yl` a 90° antihorario, `z` común.
* Desplazamientos, reacciones y cargas: ejes **globales**. Esfuerzos y tensiones: ejes **locales**.
* `V`, `T`, `M`: ver la memoria del programa (M > 0 tracciona la fibra inferior).
* Sin conversión de unidades: usar un sistema coherente (por ej. N, mm, MPa).
* `CS fluencia = fy/σVM`, `CS admisible = σadm/σVM` (cumple si ≥ 1).

### Limitaciones actuales

Sin articulaciones internas ni apoyos inclinados; matriz densa. Cargas en el tramo: q, P y gradiente térmico
(sin momentos/torsores concentrados en el tramo; la parte uniforme de la temperatura produce solo axil y no se considera).

### Novedades de la v1.4

* Diagramas de esfuerzos **normalizados por barra** (se ve la forma aunque una barra tenga valores chicos; los números rotulados son los reales).
  Se puede volver a una escala única con `escala_diagramas;global` en PROYECTO (por defecto: `barra`).
* Nueva tabla **Funciones de esfuerzos de cada barra**: V(x) y M(x) exactos por tramo (x desde el nodo i) y T.

### Novedades de la v1.3

* Bloque `RESORTES GIRO INCLINADO` (resorte de torsión con eje inclinado en el plano) y `DESAJUSTE DE RESORTES` (resorte corto/largo).
* `003_Ejemplos/001_Emparrillado/ejercicio7_TP6_2022.csv`: TP6 2do semestre 2022 (con los supuestos de geometría anotados en el archivo).

### Novedades de la v1.2

* **Cargas en el tramo** (q uniforme/trapecial/parcial, P puntual, gradiente térmico) con cargas nodales equivalentes consistentes:
  `K·u = F + ΣF_eq`, fuerzas de extremo `f = k·u + f0`. Diagramas de V y M curvos, M máx/mín con su posición,
  tensiones a lo largo de toda la barra y elástica corregida. Validado con el 1er parcial 2020 de la cátedra.
* **Vista 3D interactiva** en el informe (girar con el mouse, zoom, vistas predefinidas, selector de caso): Pz rojo, Mx azul, My ámbar,
  flechas proporcionales, momentos con doble punta (mano derecha), una resultante por componente y por nodo.
* El CSV puede venir de Excel en Windows (cp1252); el bloque CARGAS ya no es obligatorio si hay cargas en barras.
* Corrección de texto: al invertir i↔j cambia el signo de V, no el de T ni el de M.


## Pórtico espacial 3D (v1.1.1)

`tipo;portico3d`.  Barra de Euler-Bernoulli de 12 GDL (axil, torsión y flexión en los dos planos), rotación por terna local
`(x de i a j; z local = +Z global proyectado, o +X en barras verticales; se cambia con `rx;ry;rz` o `giro`)`.  Nudos rígidos, apoyos,
resortes en globales, desplazamientos prefijados, cargas nodales y en barras (uniformes/trapeciales/puntuales, locales o globales), combinaciones,
esfuerzos exactos N, Vy, Vz, T, My, Mz en cada estación, tensiones y Von Mises, equilibrio global de fuerzas y momentos y detección de mecanismos.
El informe incluye un visor 3D (girar, deformada, diagramas).  **Validación:** contra el pórtico plano (en XY y en XZ) y contra el emparrillado
(mismos resultados a 1e-9), invarianza ante rotaciones rígidas, voladizos analíticos, empotramientos perfectos y equilibrio.
**Tensor de tensiones:** σx, τxy, τxz con torsión y corte de flexión (Jourawski; circular, tubo, rectangular y rect_hueca), tensiones principales, τmáx y CS por teoría.  Valores nominales de teoría de vigas.
**Pendiente:** articulaciones (liberaciones), temperatura, desajustes, pandeo, resortes inclinados/apoyos oblicuos.
