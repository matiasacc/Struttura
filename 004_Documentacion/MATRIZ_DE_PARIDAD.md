# Matriz de funciones por programa (estándar de Struttura)

Regla: lo que se agrega a un tipo de estructura se lleva a los otros tres; si algo no corresponde a un tipo, se anota acá por qué.
✔ = tiene · ✘ = falta (pendiente de decidir) · — = no corresponde

| Función | Pórtico 3D | Pórtico plano | Emparrillado | Reticulado |
|---|---|---|---|---|
| Biblioteca de materiales (`lib`, `rho` de la ficha) | ✔ | ✔ | ✔ | ✔ |
| Biblioteca de perfiles (SECCIONES `tipo;perfil` + `lib`; tablas CIRSOC 301/302) | ✔ | ✔ | ✔ | ✔ |
| Peso propio (`peso_propio`, `gravedad`, `rho`) | ✔ | ✔ | ✔ | ✔ (mitad del peso en cada nudo [propio]) |
| Visor: modo Utilización (σeq/fy y σeq/σadm al pasar el mouse) | ✔ | ✔ | ✔ | ✔ |
| Visor: diagramas (V, T, M en planta en el emparrillado) | ✔ | ✔ | ✔ | ✔ |
| Mapa de uso en la Memoria | ✔ | ✔ | ✔ | ✔ |
| Sección «Funciones comunes» en la Memoria | (en su tabla de fundamento) | ✔ | ✔ | ✔ |
| Soldaduras (bloque SOLDADURAS; `sy_base` desde `lib`; electrodos en `006_Biblioteca/electrodos.csv`) | ✔ | ✔ | ✔ (según cada esfuerzo) | — |
| Articulaciones por barra | ✔ | ✔ | ✔ (flexión `m` y/o torsión `t`) | — (todas articuladas) |
| Perfiles abiertos de pared delgada (canal, doble T, te, Z, ángulo) | ✔ | ✔ | ✔ | ✔ (solo A e I) |
| Tensor de tensiones y criterios de falla (Tresca, Rankine, Mohr...) | ✔ | ✔ | ✔ | — |
| Aviso de columnas no reconocidas en cualquier bloque | ✔ | ✔ | ✔ | ✔ |
| Temperatura y desajuste de longitud en barras | ✘ | ✔ | ✔ (temp) | ✔ |
| Resortes inclinados y desajuste de resortes | ✘ | ✔ | ✔ (giro inclinado) | ✔ |
| Pandeo de Euler (`pandeo` por barra, por defecto art-art) | ✔ | ✔ | — (sin axil) | ✔ |
| `anexo_matrices`, `csv_salida`, `escala_deformada` | ✔ | ✔ | ✔ | ✔ |
| `escala_diagramas` (barra \| global; casilla «escala única» en el visor) | ✔ | ✔ | ✔ | ✔ |
| `corte_tensiones` | ✔ | ✔ | ✔ | — |
| Editor visual (`--editor`: tablas con todas las columnas + dibujo) | ✔ | ✔ | ✔ | ✔ (soldadura: solo tablas) |

## Pendientes

1. **3D**: temperatura, resortes inclinados y desajuste de resortes (diferido por el usuario).
2. Fatiga, cementado/nitrurado en la biblioteca, uniones tubo-tubo, penetración parcial: diferidos.
3. Completar `electrodos.csv` con más datos (los enviará el usuario).
