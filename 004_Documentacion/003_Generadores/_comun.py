"""Funciones que son COMUNES a los 4 programas (pórtico 3D, pórtico plano, emparrillado, reticulado): una sola redacción para las 4 memorias.
Regla del programa: lo que se agrega a un tipo de estructura se lleva a los demás; cuando algo es común, se escribe aquí."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "001_Codigo"))
from struttura.emparrillado.informe import tabla  # noqa: E402


def seccion_comun(programa):
    """programa: 'portico' | 'emparrillado' | 'reticulado'.  Devuelve el HTML de la sección «Funciones comunes a los cuatro programas»."""
    grav = {"portico": "±x, ±y (por defecto -y)", "reticulado": "±x, ±y (por defecto -y)", "emparrillado": "±z (por defecto -z)"}[programa]
    peso = {"portico": "carga distribuida uniforme q = ρ·g·A por unidad de longitud de la barra, en la dirección de la gravedad (tipo qgx / qgy)",
            "emparrillado": "carga distribuida uniforme q = ρ·g·A por unidad de longitud, en z (tipo q)",
            "reticulado": "mitad del peso ρ·g·A·L de cada barra en cada nudo extremo (las barras son bielas y no admiten carga en el tramo)"}[programa]
    marca = " <b>[propio]</b>" if programa == "reticulado" else ""
    filas = [
        ["Peso propio (opcional)", f"PROYECTO: <code>peso_propio;CASO</code> y <code>gravedad;…</code> {grav}; MATERIALES: <code>rho</code> en kg/m³.  Se calcula solo si se escribe <code>peso_propio</code>.  {peso}.{marca}  g = 9,80665 m/s²; ρ se convierte a las unidades del modelo",
         "[propio] criterio del programa (igual que el pórtico 3D)" if programa != "reticulado" else "[propio] criterio del programa: la repartición en nudos es la estática de una biela biapoyada", "todas las barras"],
        ["Biblioteca de materiales", "MATERIALES: <code>lib;N</code> completa E, nu o G, fy y rho con la ficha N de la biblioteca (convertida a las unidades del modelo); lo escrito a mano manda; un dato que la ficha no trae queda vacío",
         "ficha del material (valores típicos, no garantizados); ver Memoria de la biblioteca", "columna lib de MATERIALES"],
        ["Biblioteca de perfiles", "SECCIONES: <code>tipo;perfil</code> + <code>lib;N</code> completa " + {"portico": "i, a, c, h", "reticulado": "i, a, c, h", "emparrillado": "i, j, a, c, wt, h"}[programa] + " con el perfil N de las tablas CIRSOC 301/302 (I = I<sub>x</sub>, eje fuerte; c = d/2 o la fibra más lejana; h = d), convertido de cm a la unidad del modelo; lo escrito a mano manda; un dato que la tabla no trae queda vacío.  En ángulos se usan los ejes paralelos a las alas y el programa avisa que no hay flexión asimétrica [propio]",
         "Tablas de perfiles laminados y tubos, Reglamento CIRSOC 301-EL / 302-EL (valores tal cual figuran); ver Memoria de la biblioteca, sección 7", "columna lib de SECCIONES (tipo perfil)"],
        ["Utilización (visor, modo «Utilización»)", "σ<sub>eq</sub>/(fy o sut según la teoría) y σ<sub>eq</sub>/σ<sub>adm</sub> en 21 puntos por barra; el recuadro al pasar el mouse muestra ambos; el color usa fy o σadm según el selector «Color según»; 1 = fluencia (fy) o tensión admisible",
         "[propio] definición del programa; σ<sub>eq</sub> es la de la teoría del material (Von Mises por defecto) ya calculada por el programa (ver «Tensiones y coeficientes de seguridad»)", "visor del informe; necesita fy o σadm en MATERIALES"],
        ["Estándar de los visores", "mismos modos y nombres: Estructura · Cargas · Deformada · Utilización · diagramas; mismos controles de navegación y mismo recuadro al pasar el mouse sobre nudos y barras",
         "criterio del programa (visor_comun.py)", "los cuatro programas"],
    ]
    es_ret, es_emp = programa == "reticulado", programa == "emparrillado"
    filas += [
        ["Pandeo de Euler", ("no corresponde: el emparrillado no tiene esfuerzo axil" if es_emp else
                             "BARRAS: <code>pandeo</code> = art-art (defecto) | emp-lib | emp-art | emp-emp.  P<sub>c</sub> = π²·E·I/(K·L)², con K = 1 ; 2 ; 1/√2 ; 1/2 según los extremos.  CS pandeo = P<sub>c</sub>/|N<sub>min</sub>| en barras comprimidas (N<sub>min</sub>: la mayor compresión a lo largo de la barra).  "
                             + ("I es la que informó el usuario o, en perfiles de pared delgada, la menor inercia principal." if es_ret else "I de la flexión en el plano.") + "  *La condición de extremos se deja a criterio del diseñador"),
         "tabla de la cátedra (Compendio): π²EI/L², 2π²EI/L², 4π²EI/L², π²EI/(4L²)" if not es_emp else "—", "reticulado, pórtico plano y pórtico 3D" if not es_emp else "—"],
        ["Criterios de falla", ("no corresponde: el reticulado solo tiene axil (CS = fy/σ y σadm/σ)" if es_ret else
                                "MATERIALES: <code>sut</code>, <code>suc</code>, <code>teoria</code> = vm (defecto) | tresca | rankine | mohr | mohrmod.  Se evalúan en los puntos de control del programa (fibras extremas y eje neutro en los planos); "
                                "CS = fy/σ<sub>eq</sub> (Von Mises, Tresca) o sut, suc (Rankine, Mohr, Mohr modificado).  Fórmulas en la Memoria del pórtico 3D"),
         "Compendio cap. 2 (Von Mises, Tresca, Rankine, Mohr, Mohr modificado)" if not es_ret else "—", "pórtico 3D, pórtico plano y emparrillado" if not es_ret else "—"],
        ["Perfiles de pared delgada", ("SECCIONES: <code>canal</code>, <code>doble_t</code>, <code>te</code>, <code>z</code>, <code>angular</code> con <code>h</code>, <code>b</code>, <code>t</code> (o <code>tf</code>, <code>tw</code>), dimensiones de línea media.  "
                                       + ("En el reticulado solo aportan A e I (pandeo con la menor inercia principal).  " if es_ret else
                                          "Flexión alrededor del eje principal fuerte (h en el plano de la flexión); tensiones con Jourawski y torsión de Saint-Venant (J = Σ l·t³/3)" + ("" if programa == "portico" else ", incluido el momento V·e cuando la carga no pasa por el centro de corte [propio]") + ".  Perfiles sin simetría (ángulo, Z) trabajan en flexión oblicua en la realidad: el modelo plano los trata alrededor del eje principal*")),
         "Gere & Goodno 7.ª ed. cap. 6.7–6.9; Compendio cap. 10; lo marcado [propio] es criterio del programa", "los cuatro programas"],
        ["Soldaduras", ("no corresponde: las bielas se unen por nudos" if es_ret else
                        "SOLDADURAS / ELECTRODOS: igual que el pórtico 3D (id; barra; extremo; disposicion; electrodo; w; sy_base | lib ...).  Esfuerzos del extremo de la barra → cargas del grupo: "
                        + ("N = N, V<sub>z</sub> = −V, M<sub>y</sub> = −M" if programa == "portico" else "V<sub>z</sub> = −V, T = T, M<sub>y</sub> = −M" if es_emp else "los del solver 3D") + ".  Genera <code>soldaduras.csv</code>"),
         "Shigley cap. 9; Compendio cap. 18 (ver Memoria de soldadura)", "pórtico 3D, pórtico plano y emparrillado" if not es_ret else "—"],
        ["Articulaciones por barra", ("todas las barras son articuladas (biela)" if es_ret else
                                      "BARRAS: <code>art_i</code> / <code>art_j</code>" + (": m = flexión, t = torsión, mt = ambas" if es_emp else ": 1 = articulación (M = 0)" if programa == "portico" else ": giros liberados (rótula esférica o my, mz, t)") + ".  Condensación estática del giro liberado"),
         "criterio del programa (condensación estática)", "pórtico 3D, pórtico plano y emparrillado" if not es_ret else "—"],
        ["Escala de los diagramas", "PROYECTO: <code>escala_diagramas</code> = barra (defecto: cada barra a su escala, se ve bien aunque sea chica) | global; en el visor, casilla «escala única»", "criterio del programa", "los cuatro programas"],
        ["Corte en las tensiones", "PROYECTO: <code>corte_tensiones</code> = si (defecto) | no", "criterio del programa", "pórtico 3D, pórtico plano y emparrillado" if not es_ret else "—"],
    ]
    return ("<h2>Funciones comunes a los cuatro programas</h2><p>Estas funciones se escriben igual en la memoria de cada programa: si se agrega una a un tipo de estructura, se lleva a los demás.</p>"
            + tabla(["Función", "Qué hace / fórmula", "Fuente", "Se aplica a"], filas))
