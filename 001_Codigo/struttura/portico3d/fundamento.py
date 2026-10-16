"""Fundamento de cálculo del programa 3D (para la Memoria del programa, no para el informe de cada modelo)."""

def filas() -> list:
    """Todo lo que usa el programa 3D: (tema, fórmula, fuente, caso).  Lo que no está en los libros va marcado [propio].
    REGLA: cada unidad nueva agrega aquí sus filas."""
    F = []                                                # filas (tema, fórmula, fuente, caso)
    F.append(("Rigidez de la barra (12×12)", "método matricial de rigidez; viga de Euler-Bernoulli (sin deformación por corte), "
              "torsión de Saint-Venant (GJ/L)", "Navier-Bernoulli; Gere & Goodno 7ª ed., cap. 5–6 (flexión)", "todas las barras"))
    F.append(("Tensión normal", "σ<sub>x</sub> = N/A + M<sub>y</sub>·z/I<sub>y</sub> − M<sub>z</sub>·y/I<sub>z</sub>",
              "Gere 7ª ed., (6-38) §6.5 (flexión de vigas asimétricas, ejes principales); signos según las convenciones de este informe",
              "ejes y, z principales y baricéntricos"))
    if True:
        F.append(("Articulaciones en barras", "condensación estática: k<sub>c</sub> = k<sub>AA</sub> − k<sub>AB</sub>·k<sub>BB</sub><sup>−1</sup>·k<sub>BA</sub>; "
                  "f<sub>0c</sub> = f<sub>0A</sub> − k<sub>AB</sub>·k<sub>BB</sub><sup>−1</sup>·f<sub>0B</sub>",
                  "[propio] álgebra estándar del método de rigidez (no es una fórmula de los libros cargados)", "barras con art_i / art_j"))
    if True:
        F.append(("Peso propio", "q = ρ·g·A (carga uniforme por unidad de longitud, en la dirección de la gravedad)",
                  "[propio] definición de peso por unidad de longitud", "caso con 'peso_propio'"))
    if True:
        F.append(("Torsión circular / tubo", "τ = T·r/J (circular y tubo); J = π(d⁴ − d<sub>i</sub>⁴)/32", "Gere cap. 3; Compendio cap. 10",
                  "secciones circular y tubo"))
        F.append(("Corte de flexión circular / tubo", "circular macizo: τ = 4V/(3A)·(1 − (c/R)²);  tubo de pared delgada: τ = V·cosφ/(π·R<sub>m</sub>·t)",
                  "Gere 7ª ed., §5.9 (viga circular); pared delgada: [propio] mismo planteamiento de Jourawski, §5.10", "circular / tubo"))
    if True:
        F.append(("Rectangular maciza", "corte τ = (3V/2A)(1 − (2c/h)²);  torsión τ = T/W<sub>t</sub> (cara mayor)",
                  "Gere 7ª ed., §5.8 (corte); Compendio cap. 10 (torsión)", "sección rectangular"))
    if True:
        F.append(("Tubo rectangular", "torsión de Bredt: τ = T/(2·A<sub>m</sub>·t);  corte de Jourawski en almas y alas: τ = V·Q/(I·2t)",
                  "Compendio cap. 10 (Bredt); Jourawski: Gere §5.10 / §6.7", "sección rect_hueca (pared delgada)"))
    if True:
        F.append(("Perfil abierto de pared delgada: propiedades", "A = Σ t·l;  I = Σ t·l·(distancia al baricentro)² + t·l³·sen²/12; dimensiones de línea media; "
                  "si I<sub>yz</sub> ≠ 0 se giran los ejes a los principales (tan 2θ = −2I<sub>yz</sub>/(I<sub>y</sub> − I<sub>z</sub>))",
                  "Gere 7ª ed., (6-62) §6.9 (idea de línea media); giro de ejes principales: Gere 7ª ed., §12.9", "canal, doble T, Té, Z, ángulo"))
        F.append(("Corte de flexión en pared delgada abierta", "τ = V·Q/(I·t), Q = momento estático de la parte más allá del punto",
                  "Gere 7ª ed., (6-45) §6.7", "toda la línea media del perfil; flujo de corte q = τ·t tangente a la línea media"))
        F.append(("Centro de corte", "la resultante del flujo de V<sub>z</sub> = 1 (V<sub>y</sub> = 1) da el momento y<sub>s</sub> (−z<sub>s</sub>) respecto del baricentro; "
                  "canal: e = 3b²t<sub>f</sub>/(h·t<sub>w</sub> + 6b·t<sub>f</sub>) desde el alma",
                  "Gere 7ª ed., (6-65) §6.9 (canal); casos particulares §6.9 (ángulo en la unión de patas, Z y doble T en el baricentro). "
                  "El cálculo general por equilibrio de momentos es [propio] y se validó con esos casos", "canal, doble T, Té, Z, ángulo"))
        F.append(("Torsión en pared delgada abierta", "J = Σ l·t³/3 ;  τ = T·t/J (superficie de la chapa)",
                  "Compendio cap. 10, Anexo caso 7", "perfiles abiertos"))
        F.append(("Torsión efectiva y suma de tensiones", "T<sub>SV</sub> = T − (y<sub>s</sub>·V<sub>z</sub> − z<sub>s</sub>·V<sub>y</sub>);  τ = τ<sub>corte</sub> + τ<sub>torsión</sub> en módulo, tangente a la línea media",
                  "[propio]: equilibrio de momentos de las tensiones respecto del baricentro = T del solver; suma en módulo = envolvente conservadora; "
                  "se desprecia el alabeo impedido", "perfiles abiertos con corte fuera del centro de corte"))
        F.append(("Puntos evaluados", "sobre la línea media (tensión normal con coordenadas de línea media, no de la fibra extrema: diferencia ≈ t/2 sobre c)",
                  "[propio]", "perfiles abiertos"))
    crit = {"vm": ("Von Mises", "σ<sub>eq</sub> = √(σ<sub>x</sub>² + 3τ²);  CS = f<sub>y</sub>/σ<sub>eq</sub>", "Compendio cap. 2", "materiales dúctiles"),
            "tresca": ("Tresca", "σ<sub>eq</sub> = σ<sub>1</sub> − σ<sub>3</sub> = √(σ<sub>x</sub>² + 4τ²);  CS = f<sub>y</sub>/σ<sub>eq</sub>", "Compendio cap. 2", "materiales dúctiles"),
            "rankine": ("Rankine", "σ<sub>eq</sub> = máx(σ<sub>1</sub>, |σ<sub>3</sub>|);  CS = mín(σ<sub>ut</sub>/σ<sub>1</sub>, σ<sub>uc</sub>/|σ<sub>3</sub>|)", "Compendio cap. 2", "materiales frágiles"),
            "mohr": ("Mohr", "σ* = σ<sub>1</sub> + α|σ<sub>3</sub>|, α = σ<sub>ut</sub>/σ<sub>uc</sub>;  CS = σ<sub>ut</sub>/σ*", "Compendio cap. 2, (64)-(66)", "dúctil con |σ<sub>c</sub>| > σ<sub>t</sub>"),
            "mohrmod": ("Mohr modificado", "σ* = máx{σ<sub>1</sub>; α|σ<sub>3</sub>| + (1 − α)σ<sub>1</sub>};  CS = σ<sub>ut</sub>/σ*", "Compendio cap. 2, (70)-(73)", "frágil con |σ<sub>c</sub>| > σ<sub>t</sub>")}
    F.append(("Tensiones principales", "σ<sub>1,3</sub> = (σ<sub>x</sub> ± √(σ<sub>x</sub>² + 4τ²))/2;  σ<sub>2</sub> = 0;  τ² = τ<sub>xy</sub>² + τ<sub>xz</sub>²",
              "Gere 7ª ed., §7.3 (tensiones principales, estado plano)", "todos los puntos"))
    for t in ("vm", "tresca", "rankine", "mohr", "mohrmod"):
        if True:
            F.append((crit[t][0], crit[t][1], crit[t][2], crit[t][3]))
    F.append(("Utilización (mapa y valor al pasar el mouse)", "u = σ<sub>eq</sub>/f<sub>y</sub> en Von Mises y Tresca;  u = 1/CS en las demás teorías;  u = 1 es la fluencia (no es un admisible).  Si el material tiene σ<sub>adm</sub>, el recuadro muestra además σ<sub>eq</sub>/σ<sub>adm</sub> (igual que en los programas planos)",
              "[propio] definición del programa (el CS de cada teoría es el del libro)", "visor 3D, modo Utilización"))
    F.append(("Material de la biblioteca (lib)", "E, G, nu, f<sub>y</sub>, σ<sub>ut</sub> y ρ se toman de la ficha del material, convertidos a las unidades del modelo; lo escrito a mano en MATERIALES manda; un dato que la ficha no trae queda vacío",
              "ficha del material (valores típicos, no garantizados); ver Memoria de la biblioteca", "columna lib de MATERIALES"))
    F.append(("Perfil de la biblioteca (tipo perfil, lib en SECCIONES)", "A = A<sub>g</sub>, I<sub>y</sub> = I<sub>x</sub> del catálogo (eje fuerte, altura d sobre z), I<sub>z</sub> = I<sub>y</sub> del catálogo, J = J, c<sub>z</sub> = d/2 y c<sub>y</sub> = b/2 (te: la fibra más lejana; canal: máx(e, b − e)), W<sub>t</sub> = C (solo tubos); convertidos de cm a la unidad del modelo; lo escrito a mano manda; un dato que la tabla no trae queda vacío.  En ángulos se usan los ejes paralelos a las alas (aviso: no hay flexión asimétrica) [propio]",
              "Tablas de perfiles laminados y tubos, Reglamento CIRSOC 301-EL / 302-EL (valores tal cual figuran); ver Memoria de la biblioteca, sección 7", "columna lib de SECCIONES (tipo perfil)"))
    F.append(("Pandeo de Euler", "P<sub>c</sub> = π²·E·I/(K·L)², K = 1 (art-art), 2 (emp-lib), 1/√2 (emp-art), 1/2 (emp-emp);  I = menor de I<sub>y</sub> e I<sub>z</sub>;  CS = P<sub>c</sub>/|N<sub>min</sub>| en barras comprimidas",
              "tabla de la cátedra (Compendio): π²EI/L², 2π²EI/L², 4π²EI/L², π²EI/(4L²).  La condición de extremos de cada barra la elige el diseñador (columna <code>pandeo</code>)*; usar el eje débil es el criterio del programa [propio]",
              "barras comprimidas"))
    F.append(("Material de la biblioteca de electrodos (lib en ELECTRODOS)", "τ<sub>adm</sub>, S<sub>ut</sub> y S<sub>y</sub> del electrodo se leen de 006_Biblioteca/electrodos.csv (E60 … E120 de Shigley y los que se carguen); lo escrito a mano manda",
              "Shigley 2024, Tabla 9-3 (S<sub>ut</sub>, S<sub>y</sub>) y Tabla 9-6 cuadro A (τ<sub>adm</sub>)", "bloque SOLDADURAS"))
    F.append(("Fluencia del metal base (lib en SOLDADURAS)", "sy_base = f<sub>y</sub> del material N de la biblioteca de materiales (convertido a las unidades del modelo); lo escrito a mano manda",
              "ficha del material (valores típicos, no garantizados)", "bloque SOLDADURAS"))
    F.append(("Escala de los diagramas", "<code>escala_diagramas</code> = barra (defecto) | global; casilla «escala única» en el visor", "[propio] criterio del programa", "visor 3D"))
    return [list(x) for x in F]
