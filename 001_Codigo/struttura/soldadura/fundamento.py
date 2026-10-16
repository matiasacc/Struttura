"""Fundamento de cálculo del programa de soldaduras (para la Memoria del programa).  Lo que no está en los libros va marcado [propio].
REGLA: cada ampliación (más electrodos, fatiga, uniones tubo-tubo...) agrega acá sus filas."""
from __future__ import annotations


def filas() -> list:
    S = "Shigley's Mechanical Engineering Design, ed. 2024, cap. 9"
    C = "Compendio CE-II cap. 18"
    return [list(x) for x in [
        ("Garganta del filete", "t = 0,707·w (w = cateto = pie del filete; t = distancia desde la raíz, perpendicular a la hipotenusa)", f"{S}, (9-3) p. 503;  {C}, (3)", "filete de catetos iguales"),
        ("Método de diseño (simplificado)", "todo se verifica como corte en la garganta mínima: τ = F/(0,707·w·l) = 1,414·F/(w·l)",
         f"{S}, (9-3) p. 503;  {C}, (12)", "filetes con cualquier dirección de carga (conservador: 17 % sobre el máximo teórico)"),
        ("Cordones como líneas", "A<sub>w</sub> = Σ l;  I<sub>yu</sub> = ∫ z'² ds;  I<sub>zu</sub> = ∫ y'² ds;  J<sub>u</sub> = I<sub>yu</sub> + I<sub>zu</sub> (desde el baricentro del grupo); "
         "J = 0,707·w·J<sub>u</sub>", f"{S}, (9-6) p. 505, Tablas 9-1 y 9-2 pp. 506 y 510-511;  {C}, Anexo 1 (J<sub>w</sub>)", "grupos de cordones cualesquiera (el programa integra los segmentos; las tablas son casos de prueba)"),
        ("Fuerza por unidad de longitud: corte primario", "f = V/A<sub>w</sub>  (τ' = V/A)", f"{S}, (9-4) p. 503;  {C}, Tabla 4", "corte en el plano de los cordones (V<sub>y</sub>, V<sub>z</sub>)"),
        ("Torsión en el plano", "f = T·r/J<sub>u</sub>, perpendicular al radio r desde el baricentro del grupo", f"{S}, (9-5) p. 504;  {C}, Tabla 4", "T = momento alrededor del eje de la barra"),
        ("Flexión y axil", "f = N/A<sub>w</sub> + M·c/I<sub>u</sub>, normal al plano de los cordones (con una dirección: M<sub>y</sub>·z'/I<sub>yu</sub> o M<sub>z</sub>·y'/I<sub>zu</sub>)",
         f"{S}, ej. 9-4 p. 509 y 516;  {C}, Tabla 4", "momento alrededor de un eje de simetría del grupo"),
        ("Flexión en dos ejes y grupos no simétricos", "f<sub>x</sub> = N/A<sub>w</sub> + a·z' + b·y' con [I<sub>yu</sub> I<sub>yzu</sub>; I<sub>yzu</sub> I<sub>zu</sub>]·(a, b) = (M<sub>y</sub>, −M<sub>z</sub>)",
         "[propio]: los libros solo traen flexión alrededor de un eje horizontal; se verifica por equilibrio y por invariancia al giro (tests)", "flexión biaxial o grupos L, custom"),
        ("Composición vectorial", "f = √(f<sub>x</sub>² + f<sub>y</sub>² + f<sub>z</sub>²);  τ = f/(0,707·w)", f"{C}, (14);  {S}, p. 509 (combinación vectorial)", "en cada punto del cordón"),
        ("Punto crítico", "en tramos rectos f es afín en la posición, |f| es convexa: el máximo está en los extremos; arcos: muestreo cada 2°",
         "[propio] propiedad matemática (verificada en los tests)", "búsqueda del máximo"),
        ("Traslado de las cargas al baricentro del grupo", "T' = T + (y<sub>p</sub> − y<sub>g</sub>)·V<sub>z</sub> − (z<sub>p</sub> − z<sub>g</sub>)·V<sub>y</sub>;  M<sub>y</sub>' = M<sub>y</sub> + (z<sub>p</sub> − z<sub>g</sub>)·N;  M<sub>z</sub>' = M<sub>z</sub> − (y<sub>p</sub> − y<sub>g</sub>)·N",
         f"estática; ejemplo 9-1 de {S} (M = F·l, p. 507)", "carga aplicada fuera del baricentro del grupo"),
        ("Verificación con código", "f<sub>máx</sub> ≤ f<sub>adm</sub> = 0,707·w·τ<sub>adm</sub>;  CS = τ<sub>adm</sub>/τ;  w ≥ f<sub>máx</sub>/(0,707·τ<sub>adm</sub>)",
         f"{C}, (15)-(16);  {S}, ej. 9-2 p. 514 y 9-4(c) p. 517", "electrodos de la tabla"),
        ("τ<sub>adm</sub> del electrodo", "E60 18 · E70 21 · E80 24 · E90 27 · E100 30 · E110 33 · E120 36 ksi (= 0,30·S<sub>ut</sub> del electrodo)",
         f"{S}, Tabla 9-6 Cuadro A p. 513 y Tabla 9-4 p. 512;  {C}, Anexo 2", "aceros; para otros aportes se carga τ<sub>adm</sub> a mano (bloque ELECTRODOS)"),
        ("Resistencias de electrodos", "E60 62/50 · E70 70/57 · E80 80/67 · E90 90/77 · E100 100/87 · E120 120/107 ksi (S<sub>ut</sub>/S<sub>y</sub>)",
         f"{S}, Tabla 9-3 p. 511;  {C}, Anexo 2 (E110 no figura en la Tabla 9-3)", "CS convencional"),
        ("CS convencional", "n = 0,577·S<sub>y</sub>(aporte)/τ", f"{S}, ej. 9-4(a) p. 517", "comparación con el método de cálculo convencional"),
        ("Metal base", "τ<sub>base</sub> = f/w ≤ 0,40·S<sub>y,base</sub>;  w ≥ f<sub>máx</sub>/(0,40·S<sub>y,base</sub>)", f"{S}, ej. 9-2(b) p. 514 y Tabla 9-4 p. 512;  {C}, Anexo 2",
         "siempre verificar además el material base (Shigley p. 512)"),
        ("Pie mínimo", "según el espesor de la pieza más gruesa: ≤ 1/4 in → 1/8 in; ≤ 1/2 → 3/16; ≤ 3/4 → 1/4; ≤ 1 1/2 → 5/16; ≤ 2 1/4 → 3/8; ≤ 6 → 1/2; > 6 → 5/8; "
         "no debe superar el espesor de la pieza más delgada", f"{S}, Tabla 9-6 Cuadro B p. 513. Las notas * (puentes: no menos de 3/16 in) y † (\"no pasar de 5/16 in por cada 3/4 in de material\") no se aplican: el texto de † es ambiguo, se decide entre ambos",
         "pie mínimo constructivo"),
        ("Pie a adoptar", "w<sub>adoptar</sub> = máx(w requerido, w mínimo); si supera el espesor de la pieza más delgada se marca con * y queda a criterio del diseñador (no se corrige)", "[propio] criterio de presentación; el mínimo de la tabla no contempla tubos de pared fina", "informe"),
        ("Cordón sobre tubo redondo", "A<sub>w</sub> = π·d;  J<sub>u</sub> = π·d³/4;  I<sub>u</sub> = π·d³/8 (d = diámetro del cordón = exterior del tubo)", f"{S}, Tabla 9-1 y 9-2 (círculo) pp. 506 y 511;  {C}, Anexo 1 caso 9", "vuelta completa"),
        ("Arcos parciales de tubo", "mismas integrales sobre cada arco (arcos = centro:abertura, sin superponerse)", "[propio] extensión: los libros solo tratan la vuelta completa", "disposición 'arco'"),
        ("Corte uniforme en el cordón", "el corte V se reparte uniforme (V/A<sub>w</sub>); no se aplica la distribución cos φ del corte de un tubo", f"{S}, (9-4) p. 503 (tensión primaria uniforme)", "todas las disposiciones"),
        ("Unión a tope: tensiones", "σ = N/(t·L<sub>w</sub>) + M·c/(t·I<sub>u</sub>);  τ = V/(t·L<sub>w</sub>) (más T·r/(t·J<sub>u</sub>));  t = garganta = espesor de las piezas, sin refuerzo",
         f"{S}, (9-1) y (9-2) p. 500 (σ = F/(h·l), τ = F/(h·l));  {C}, (1) y (2)", "unión a tope de penetración completa. Flexión y torsión con las propiedades del grupo: [propio] (los libros dan solo carga axial y corte)"),
        ("Unión a tope de pared delgada", "el cordón es la línea media de la pared (d − t) y σ, τ se evalúan en la fibra exterior (coordenadas ampliadas por d/(d − t))",
         "[propio] aproximación de pared delgada; error < 1 % frente a las fórmulas exactas del tubo (tests)", "tubo y tubo rectangular a tope"),
        ("Unión a tope: admisibles", "σ ≤ 0,60·S<sub>y</sub> (tracción, compresión y flexión: se toma el menor de 0,60–0,66);  τ ≤ 0,30·S<sub>ut</sub> del electrodo y ≤ 0,40·S<sub>y</sub> del metal base",
         f"{S}, Tabla 9-4 p. 512;  {C}, Anexo 2", "S<sub>y</sub> = el menor entre el del aporte y el del base [propio: criterio del menor]"),
        ("Unión a tope: cargas combinadas", "σ<sub>VM</sub> = √(σ² + 3τ²);  CS = S<sub>y</sub>/σ<sub>VM</sub> (se informa aparte del veredicto por admisibles)", f"{C}, cap. 18 (soldadura a tope: con cargas combinadas, Von Mises o Tresca)", "dúctiles"),
        ("Unión a tope: espesor requerido", "t<sub>req</sub> ≈ t / mín(CS<sub>σ</sub>, CS<sub>τ</sub>)", "[propio] aproximado: mismo diámetro o lados y tensión ∝ 1/t", "orientativo"),
        ("No incluido", "uniones tubo con tubo (silla), fatiga de la soldadura, penetración parcial",
         "los libros cargados no dan el método para las uniones en silla; la fatiga queda para una etapa posterior", "—"),
    ]]
