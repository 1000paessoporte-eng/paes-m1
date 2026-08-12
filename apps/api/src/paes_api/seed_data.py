"""Datos semilla: Árbol de Habilidades + banco de preguntas PAES M1.

Primer lote (36 preguntas, repartidas por eje). Cada pregunta trae
`explanation`: el desarrollo paso a paso de por qué la respuesta correcta
lo es, que es lo que ve el estudiante al revisar su ensayo. Las
alternativas incorrectas conservan `justification` (el error conceptual
que las genera) como dato interno para analítica futura; no se muestra.

La posición de la alternativa correcta se mezcla en tiempo de carga (ver
seed.py) para no sesgar siempre hacia "A". Por eso ni las explicaciones ni
las justificaciones mencionan nunca letras de alternativa.
"""

# code, name, axis, tier, prerequisites (codes)
SKILL_NODES = [
    # Números
    ("num_racionales", "Operatoria en números racionales", "numeros", 1, []),
    ("num_potencias_raices", "Potencias y raíces", "numeros", 2, ["num_racionales"]),
    ("num_porcentajes", "Porcentajes y proporcionalidad", "numeros", 2, ["num_racionales"]),
    # Álgebra
    ("alg_expresiones", "Expresiones algebraicas y factorización", "algebra", 1, []),
    ("alg_lineal", "Ecuaciones e inecuaciones lineales", "algebra", 2, ["alg_expresiones"]),
    ("alg_sistemas", "Sistemas de ecuaciones lineales 2x2", "algebra", 3, ["alg_lineal"]),
    (
        "alg_cuadratica",
        "Ecuaciones cuadráticas",
        "algebra",
        3,
        ["alg_lineal", "num_potencias_raices"],
    ),
    ("alg_funciones", "Funciones lineales y cuadráticas", "algebra", 4, ["alg_cuadratica"]),
    # Geometría
    ("geo_plana", "Perímetros y áreas de figuras planas", "geometria", 1, []),
    (
        "geo_pitagoras",
        "Teorema de Pitágoras",
        "geometria",
        2,
        ["geo_plana", "num_potencias_raices"],
    ),
    ("geo_transformaciones", "Transformaciones isométricas", "geometria", 2, ["geo_plana"]),
    ("geo_solidos", "Áreas y volúmenes de cuerpos geométricos", "geometria", 3, ["geo_pitagoras"]),
    # Probabilidad
    (
        "prob_estadistica_desc",
        "Medidas de tendencia central y dispersión",
        "probabilidad",
        1,
        [],
    ),
    (
        "prob_combinatoria",
        "Técnicas de conteo",
        "probabilidad",
        2,
        ["prob_estadistica_desc"],
    ),
    ("prob_reglas", "Reglas de probabilidad", "probabilidad", 3, ["prob_combinatoria"]),
]


def _q(
    skill_node: str,
    difficulty: str,
    stem: str,
    correct: str,
    explanation: str,
    distractors: list[tuple[str, str]],
):
    """Arma una pregunta con la correcta primero y los distractores después.

    `explanation` es lo que ve el estudiante al revisar: el desarrollo de por
    qué la respuesta correcta lo es. No debe mencionar letras de alternativa,
    porque `seed.py` mezcla el orden final A-D.
    """
    return {
        "skill_node": skill_node,
        "difficulty": difficulty,
        "stem": stem,
        "explanation": explanation,
        "alternatives": [{"text": correct, "is_correct": True, "justification": None}]
        + [
            {"text": text, "is_correct": False, "justification": just}
            for text, just in distractors
        ],
    }


QUESTIONS = [
    # ---------- NÚMEROS ----------
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 3/4 + 1/6?",
        "11/12",
        "Para sumar fracciones necesitas que tengan el mismo denominador.\n\n"
        "1) Busca el mínimo común múltiplo de 4 y 6. Los múltiplos de 4 son 4, 8, 12… "
        "y los de 6 son 6, 12… El primero que comparten es 12.\n"
        "2) Lleva cada fracción a doceavos. Como 12 ÷ 4 = 3, multiplicas arriba y abajo "
        "por 3: 3/4 = 9/12. Como 12 ÷ 6 = 2, multiplicas por 2: 1/6 = 2/12.\n"
        "3) Ahora que los denominadores son iguales, sumas solo los numeradores y "
        "mantienes el denominador: 9/12 + 2/12 = 11/12.\n"
        "4) Verifica si se puede simplificar: 11 es primo y no divide a 12, así que "
        "11/12 ya está en su forma más simple.",
        [
            ("4/10", "Sumó los numeradores entre sí y los denominadores entre sí, sin buscar un denominador común."),
            ("7/12", "Restó las fracciones en lugar de sumarlas."),
            ("1/8", "Multiplicó las fracciones en lugar de sumarlas."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de (2/3) ÷ (4/9)?",
        "3/2",
        "Dividir por una fracción es lo mismo que multiplicar por su recíproco, es "
        "decir, por esa misma fracción dada vuelta.\n\n"
        "1) El divisor es 4/9, así que su recíproco es 9/4. La división se transforma "
        "en 2/3 × 9/4.\n"
        "2) Multiplica numeradores entre sí y denominadores entre sí: "
        "(2 × 9)/(3 × 4) = 18/12.\n"
        "3) Simplifica dividiendo ambos por 6: 18 ÷ 6 = 3 y 12 ÷ 6 = 2, o sea 3/2.\n\n"
        "Un control rápido: como 4/9 es menor que 2/3, el resultado tiene que ser mayor "
        "que 1, y 3/2 = 1,5 lo cumple.",
        [
            ("8/27", "Multiplicó las fracciones directamente en lugar de invertir el divisor y multiplicar."),
            ("2/3", "Invirtió la fracción equivocada al aplicar la regla del recíproco (invirtió el dividendo en vez del divisor)."),
            ("10/9", "Sumó las fracciones en lugar de dividirlas."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el resultado de √144 + √25?",
        "17",
        "Cada raíz se resuelve por separado y recién después se suman los resultados.\n\n"
        "1) √144 = 12, porque 12 × 12 = 144.\n"
        "2) √25 = 5, porque 5 × 5 = 25.\n"
        "3) Suma ambos valores: 12 + 5 = 17.\n\n"
        "Ojo con una tentación frecuente: la raíz no se reparte sobre una suma. "
        "√144 + √25 no es lo mismo que √(144 + 25); de hecho √169 = 13, que es un "
        "número distinto.",
        [
            ("13", "Sumó los números bajo una misma raíz (√(144+25)=√169=13) en lugar de sumar las raíces por separado."),
            ("7", "Restó las raíces en lugar de sumarlas."),
            ("169", "Sumó los radicandos (144+25) pero olvidó extraer la raíz cuadrada del resultado."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el resultado de (2³)² ÷ 2⁴?",
        "4",
        "Se aplican dos propiedades de potencias de igual base.\n\n"
        "1) Potencia de una potencia: los exponentes se multiplican. "
        "(2³)² = 2^(3×2) = 2⁶ = 64.\n"
        "2) División de potencias de igual base: los exponentes se restan. "
        "2⁶ ÷ 2⁴ = 2^(6−4) = 2².\n"
        "3) Calcula el resultado: 2² = 4.\n\n"
        "Puedes comprobarlo con los números desarrollados: 64 ÷ 16 = 4.",
        [
            ("2", "Sumó los exponentes en (2³)² en lugar de multiplicarlos (usó 2⁵ en vez de 2⁶)."),
            ("1024", "Multiplicó por 2⁴ en lugar de dividir."),
            ("64", "Calculó (2³)² correctamente pero olvidó dividir por 2⁴."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "Si 3^(x+1) = 81, ¿cuál es el valor de x?",
        "3",
        "La estrategia es escribir ambos lados de la igualdad como potencias de la "
        "misma base.\n\n"
        "1) Expresa 81 como potencia de 3: 3 × 3 × 3 × 3 = 81, o sea 81 = 3⁴.\n"
        "2) La ecuación queda 3^(x+1) = 3⁴.\n"
        "3) Si dos potencias de igual base son iguales, sus exponentes también lo son: "
        "x + 1 = 4.\n"
        "4) Despeja restando 1 a ambos lados: x = 3.\n\n"
        "Verifica reemplazando: 3^(3+1) = 3⁴ = 81. Correcto.",
        [
            ("4", "Igualó x directamente al exponente de 81 = 3⁴, sin restar 1 para despejar x."),
            ("26", "Interpretó 3^(x+1) como una multiplicación (3·(x+1)) en lugar de una potencia, y despejó 81÷3-1."),
            ("80", "Restó 1 directamente a 81 en lugar de trabajar con los exponentes."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "¿Cuánto es el 15% de 240?",
        "36",
        "Un porcentaje es una fracción de 100, y la palabra \"de\" indica "
        "multiplicación.\n\n"
        "1) Escribe el 15% como decimal: 15 ÷ 100 = 0,15.\n"
        "2) Multiplica por el total: 0,15 × 240 = 36.\n\n"
        "Otra forma de llegar a lo mismo, útil para calcular mental: el 10% de 240 es "
        "24 (basta correr la coma) y el 5% es la mitad de eso, 12. Sumando, "
        "24 + 12 = 36.",
        [
            ("15", "Confundió el porcentaje mismo con el resultado del cálculo."),
            ("3,6", "Corrió el punto decimal un lugar de más, calculando el 1,5% en lugar del 15%."),
            ("225", "Calculó 240 − 15 en lugar de aplicar el porcentaje sobre 240."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "Un producto cuesta $40.000 y tiene un descuento del 20%. ¿Cuál es su precio final?",
        "$32.000",
        "La pregunta pide el precio final, no el monto rebajado.\n\n"
        "1) Calcula el descuento: el 20% de 40.000 es 0,20 × 40.000 = 8.000.\n"
        "2) Réstalo del precio original: 40.000 − 8.000 = 32.000.\n\n"
        "El camino corto es pensar en lo que queda: si te descuentan el 20%, pagas el "
        "80%. Entonces 0,80 × 40.000 = 32.000 directamente, en un solo paso. Ese "
        "factor 0,80 es muy útil cuando hay varios descuentos encadenados.",
        [
            ("$8.000", "Calculó solo el monto del descuento y lo entregó como si fuera el precio final."),
            ("$48.000", "Sumó el descuento al precio original en lugar de restarlo."),
            ("$20.000", "Calculó el 50% del precio en lugar del 20% de descuento."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Un artículo aumenta su precio en un 25% y luego, sobre el nuevo precio, se aplica un "
        "descuento del 20%. Si el precio original era $10.000, ¿cuál es el precio final?",
        "$10.000",
        "La clave es que cada porcentaje se aplica sobre una cantidad distinta, así "
        "que hay que resolverlos en orden y no mezclarlos.\n\n"
        "1) Aumento del 25% sobre 10.000: el nuevo precio es 1,25 × 10.000 = 12.500.\n"
        "2) Descuento del 20%, pero calculado sobre 12.500, no sobre el precio "
        "original: pagas el 80%, o sea 0,80 × 12.500 = 10.000.\n\n"
        "El resultado vuelve al valor inicial, y eso tiene explicación: "
        "1,25 × 0,80 = 1, es decir, los dos cambios se cancelan exactamente. No es una "
        "coincidencia del enunciado, sino que subir un 25% y luego bajar un 20% siempre "
        "deja el precio igual, porque el 20% se descuenta de una base mayor.",
        [
            ("$11.250", "Promedió o restó directamente los porcentajes (25%−20%=5%) en lugar de aplicarlos de forma sucesiva sobre precios distintos."),
            ("$12.500", "Aplicó solo el aumento del 25% y olvidó aplicar el descuento posterior."),
            ("$8.000", "Aplicó el 20% de descuento directamente sobre el precio original, ignorando el aumento previo."),
        ],
    ),
    # ---------- ÁLGEBRA ----------
    _q(
        "alg_expresiones", "facil",
        "Reduce la expresión: 3x + 5 − x + 2",
        "2x + 7",
        "Reducir significa juntar los términos semejantes, es decir, los que tienen la "
        "misma parte literal.\n\n"
        "1) Agrupa los términos con x: 3x − x. Recuerda que x equivale a 1x, así que "
        "3x − 1x = 2x.\n"
        "2) Agrupa los términos sin x: 5 + 2 = 7.\n"
        "3) Junta ambos resultados: 2x + 7.\n\n"
        "Los términos con x y los números sueltos no se pueden combinar entre sí, por "
        "eso la expresión no se reduce más.",
        [
            ("3x + 7", "No restó el término −x, dejando el coeficiente original de x."),
            ("2x + 3", "Operó mal los términos independientes (restó 5−2 en lugar de sumarlos)."),
            ("4x + 7", "Sumó los coeficientes de x en lugar de restarlos (3+1 en vez de 3−1)."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "Factoriza la expresión: x² − 9",
        "(x − 3)(x + 3)",
        "La expresión es una diferencia de cuadrados: dos términos elevados al "
        "cuadrado que se están restando.\n\n"
        "1) Reconoce cada cuadrado: x² es el cuadrado de x, y 9 es el cuadrado de 3.\n"
        "2) La regla dice que a² − b² = (a − b)(a + b). Aquí a = x y b = 3.\n"
        "3) Reemplaza: (x − 3)(x + 3).\n\n"
        "Comprueba multiplicando de vuelta: x·x + x·3 − 3·x − 3·3 = x² + 3x − 3x − 9. "
        "Los términos del medio se cancelan y queda x² − 9, que es justo la expresión "
        "original. Esa cancelación es la razón de que la fórmula funcione.",
        [
            ("(x − 9)(x + 1)", "Buscó dos números que sumen 0 y multipliquen −9, pero los eligió sin verificar que también deben ser raíces de un cuadrado perfecto."),
            ("(x − 3)²", "Trató la diferencia de cuadrados como un cuadrado de binomio."),
            ("x(x − 9)", "Factorizó por término común de forma inválida, ignorando que −9 no comparte el factor x."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "Resuelve: 2x + 5 = 17",
        "6",
        "Se despeja x deshaciendo las operaciones que la acompañan, en orden "
        "inverso.\n\n"
        "1) El 5 está sumando, así que se resta a ambos lados: "
        "2x + 5 − 5 = 17 − 5, o sea 2x = 12.\n"
        "2) El 2 está multiplicando, así que se divide a ambos lados: "
        "2x ÷ 2 = 12 ÷ 2, entonces x = 6.\n\n"
        "Verifica reemplazando en la ecuación original: 2 × 6 + 5 = 12 + 5 = 17. "
        "Coincide con el lado derecho, así que la solución es correcta.",
        [
            ("11", "Sumó 5 en lugar de restarlo al despejar el término independiente."),
            ("8,5", "Dividió 17 ÷ 2 directamente, sin restar primero el 5."),
            ("24", "Despejó multiplicando por 2 en lugar de dividir: (17 − 5) × 2."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "Resuelve la inecuación: −2x + 4 > 10",
        "x < −3",
        "Una inecuación se despeja igual que una ecuación, salvo por una regla "
        "extra que aquí es decisiva.\n\n"
        "1) Resta 4 a ambos lados: −2x > 6.\n"
        "2) Divide ambos lados por −2. Al multiplicar o dividir por un número "
        "negativo, la desigualdad cambia de sentido: el signo > se transforma en <.\n"
        "3) Queda x < −3.\n\n"
        "Comprueba con un valor cualquiera menor que −3, por ejemplo x = −4: "
        "−2 × (−4) + 4 = 8 + 4 = 12, y 12 > 10 se cumple. Si en cambio pruebas con "
        "x = 0, obtienes 4 > 10, que es falso: eso confirma que la solución son los "
        "valores menores que −3 y no los mayores.",
        [
            ("x > −3", "Olvidó invertir el sentido de la desigualdad al dividir ambos lados por un número negativo."),
            ("x < 3", "Perdió el signo negativo del coeficiente de x al despejar."),
            ("x > 3", "Combinó los dos errores anteriores: no invirtió la desigualdad y perdió el signo negativo."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "Resuelve el sistema: x + y = 10 ; x − y = 4",
        "x = 7, y = 3",
        "Conviene el método de reducción, porque el término y aparece con signos "
        "opuestos en cada ecuación.\n\n"
        "1) Suma las dos ecuaciones lado a lado. Los términos +y y −y se cancelan: "
        "(x + y) + (x − y) = 10 + 4, lo que da 2x = 14.\n"
        "2) Despeja: x = 7.\n"
        "3) Reemplaza ese valor en cualquiera de las ecuaciones originales. Usando la "
        "primera: 7 + y = 10, entonces y = 3.\n\n"
        "Verifica en la ecuación que no usaste para despejar: 7 − 3 = 4. Se cumple, "
        "así que el par de valores resuelve el sistema completo.",
        [
            ("x = 3, y = 7", "Intercambió los valores de x e y al finalizar la resolución."),
            ("x = 14, y = 4", "Sumó las ecuaciones para eliminar y, pero olvidó dividir el resultado (2x=14) por 2."),
            ("x = 5, y = 5", "Asumió que ambas incógnitas eran iguales usando solo la ecuación de la suma, ignorando la de la diferencia."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "La suma de dos números es 15 y su diferencia es 3. ¿Cuáles son los números (mayor y menor)?",
        "9 y 6",
        "Primero se traduce el enunciado a ecuaciones y después se resuelve el "
        "sistema.\n\n"
        "1) Llama x al número mayor e y al menor. El enunciado dice x + y = 15 y "
        "x − y = 3.\n"
        "2) Suma ambas ecuaciones: los términos en y se cancelan y queda 2x = 18, "
        "entonces x = 9.\n"
        "3) Reemplaza en la primera: 9 + y = 15, entonces y = 6.\n\n"
        "Verifica las dos condiciones del enunciado: 9 + 6 = 15 y 9 − 6 = 3. Ambas se "
        "cumplen. Como atajo para este tipo de problema, el mayor siempre es "
        "(suma + diferencia) ÷ 2 y el menor (suma − diferencia) ÷ 2.",
        [
            ("6 y 9", "Intercambió cuál valor corresponde al número mayor y cuál al menor."),
            ("18 y 3", "Sumó las ecuaciones sin dividir por 2 para obtener el mayor, y restó directamente para el menor."),
            ("7,5 y 7,5", "Ignoró la ecuación de la diferencia y asumió que ambos números eran iguales usando solo la suma."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "Resuelve: x² − 16 = 0",
        "x = 4 y x = −4",
        "Es una ecuación cuadrática incompleta, sin término en x, así que se despeja "
        "directamente.\n\n"
        "1) Suma 16 a ambos lados: x² = 16.\n"
        "2) Extrae raíz cuadrada. Aquí está el punto importante: hay dos números cuyo "
        "cuadrado da 16, porque 4 × 4 = 16 y también (−4) × (−4) = 16.\n"
        "3) Por eso la solución es x = 4 y x = −4, que suele escribirse x = ±4.\n\n"
        "Toda ecuación de segundo grado puede tener hasta dos soluciones, y quedarse "
        "solo con la positiva es dejar la respuesta a medias.",
        [
            ("x = 8", "Dividió 16 por 2 en lugar de calcular su raíz cuadrada."),
            ("x = 4", "Solo consideró la raíz positiva, olvidando que x = −4 también es solución."),
            ("x = 256", "Elevó 16 al cuadrado en lugar de calcular su raíz cuadrada."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "Resuelve: x² − 5x + 6 = 0",
        "x = 2 y x = 3",
        "Se factoriza buscando dos números que cumplan dos condiciones a la vez.\n\n"
        "1) Necesitas dos números que multiplicados den 6 (el término libre) y sumados "
        "den −5 (el coeficiente de x). Los candidatos son −2 y −3: "
        "(−2) × (−3) = 6 y (−2) + (−3) = −5.\n"
        "2) Escribe la factorización: (x − 2)(x − 3) = 0.\n"
        "3) Un producto es cero solo si alguno de sus factores es cero. Entonces "
        "x − 2 = 0 o x − 3 = 0.\n"
        "4) De ahí salen las soluciones: x = 2 y x = 3.\n\n"
        "Fíjate en el cambio de signo: los números de la factorización son −2 y −3, "
        "pero las soluciones son +2 y +3, porque son los valores que anulan cada "
        "paréntesis. Verifica con x = 2: 4 − 10 + 6 = 0.",
        [
            ("x = −2 y x = −3", "Cambió el signo de las soluciones al leer la factorización (x−2)(x−3), olvidando que las raíces son los valores que anulan cada factor."),
            ("x = 1 y x = 6", "Buscó dos números que sumen 6 y multipliquen −5, invirtiendo el rol de los coeficientes en la factorización."),
            ("x = 5 y x = 6", "Confundió el coeficiente de x (−5) y el término libre (6) con las propias soluciones de la ecuación."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Resuelve: 2x² + 3x − 2 = 0",
        "x = 1/2 y x = −2",
        "Como el coeficiente de x² no es 1, conviene usar la fórmula general: "
        "x = (−b ± √(b² − 4ac)) / (2a).\n\n"
        "1) Identifica los coeficientes: a = 2, b = 3, c = −2.\n"
        "2) Calcula el discriminante: b² − 4ac = 3² − 4 × 2 × (−2) = 9 + 16 = 25. "
        "Como es positivo, hay dos soluciones distintas.\n"
        "3) Su raíz es √25 = 5, así que x = (−3 ± 5) / 4.\n"
        "4) Con el signo +: x = (−3 + 5)/4 = 2/4 = 1/2. Con el signo −: "
        "x = (−3 − 5)/4 = −8/4 = −2.\n\n"
        "También se puede factorizar como (2x − 1)(x + 2) = 0, que lleva a las mismas "
        "soluciones. Verifica con x = −2: 2 × 4 + 3 × (−2) − 2 = 8 − 6 − 2 = 0.",
        [
            ("x = 1 y x = −2", "Factorizó ignorando que el coeficiente de x² es 2, usando (x−1)(x+2) en lugar de (2x−1)(x+2)."),
            ("x = 1/2 y x = 2", "Calculó correctamente una raíz pero cambió el signo de la segunda."),
            ("x = −1/2 y x = 2", "Invirtió el signo de ambas raíces respecto a la solución real."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿Cuál es el eje de simetría de la parábola y = x² − 6x + 8?",
        "x = 3",
        "El eje de simetría es la recta vertical que parte la parábola en dos mitades "
        "iguales, y pasa siempre por el vértice.\n\n"
        "1) Identifica los coeficientes en y = ax² + bx + c: a = 1, b = −6, c = 8.\n"
        "2) Aplica la fórmula del eje: x = −b / (2a).\n"
        "3) Reemplaza cuidando el signo: x = −(−6) / (2 × 1) = 6 / 2 = 3.\n"
        "4) El eje de simetría es la recta x = 3.\n\n"
        "Otra forma de verlo: las raíces de esta parábola son x = 2 y x = 4, y el eje "
        "queda justo al medio de ambas, en x = 3. El término independiente c = 8 no "
        "influye en la posición del eje, solo desplaza la curva hacia arriba o abajo.",
        [
            ("x = −3", "Usó el signo equivocado de b al calcular x=−b/2a (usó b en lugar de −b)."),
            ("x = 6", "Usó directamente el valor de b como eje de simetría, sin dividir por 2a."),
            ("x = 8", "Confundió el término independiente (8) con el eje de simetría de la parábola."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es la pendiente de la recta que pasa por los puntos (1, 2) y (4, 11)?",
        "3",
        "La pendiente mide cuánto sube la recta por cada unidad que avanza hacia la "
        "derecha: m = (y₂ − y₁) / (x₂ − x₁).\n\n"
        "1) Toma los puntos en un orden y respétalo: (x₁, y₁) = (1, 2) y "
        "(x₂, y₂) = (4, 11).\n"
        "2) Calcula la variación vertical: 11 − 2 = 9.\n"
        "3) Calcula la variación horizontal: 4 − 1 = 3.\n"
        "4) Divide: m = 9 / 3 = 3.\n\n"
        "La pendiente 3 significa que por cada unidad que avanzas en x, la recta sube "
        "3 unidades en y. Si tomas los puntos en el orden inverso el resultado no "
        "cambia, siempre que inviertas ambas restas: (2 − 11)/(1 − 4) = −9/−3 = 3.",
        [
            ("1/3", "Invirtió la fórmula de la pendiente, calculando Δx/Δy en lugar de Δy/Δx."),
            ("9", "Calculó solo la diferencia de las coordenadas y (11−2) sin dividir por la diferencia de las coordenadas x."),
            ("−3", "Calculó el valor correcto de la pendiente pero con el signo invertido, al restar las coordenadas en orden inconsistente."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuál es el vértice de la parábola y = x² − 4x + 3?",
        "(2, −1)",
        "El vértice tiene dos coordenadas y hay que calcular ambas: primero la x, "
        "después la y.\n\n"
        "1) Identifica los coeficientes: a = 1, b = −4, c = 3.\n"
        "2) La coordenada x del vértice es x = −b / (2a) = −(−4) / 2 = 2.\n"
        "3) Para la coordenada y, reemplaza x = 2 en la función completa, no solo en "
        "una parte: y = 2² − 4 × 2 + 3 = 4 − 8 + 3 = −1.\n"
        "4) El vértice es el punto (2, −1).\n\n"
        "Como a = 1 es positivo, la parábola se abre hacia arriba y ese punto es su "
        "valor mínimo: ningún punto de la curva baja de y = −1.",
        [
            ("(−2, −1)", "Calculó la coordenada x del vértice con el signo equivocado de b, usando x=b/2a en lugar de x=−b/2a."),
            ("(2, 3)", "Calculó correctamente x=2, pero evaluó solo el término independiente en lugar de reemplazar x=2 en la función completa."),
            ("(4, 3)", "Usó directamente el coeficiente b como coordenada x del vértice, sin dividir por 2a."),
        ],
    ),
    # ---------- GEOMETRÍA ----------
    _q(
        "geo_plana", "facil",
        "¿Cuál es el área de un rectángulo de 8 cm de largo y 5 cm de ancho?",
        "40 cm²",
        "El área de un rectángulo es el producto de sus dos dimensiones: "
        "A = largo × ancho.\n\n"
        "1) Reemplaza los datos: A = 8 cm × 5 cm.\n"
        "2) Multiplica: A = 40 cm².\n\n"
        "Fíjate en la unidad: al multiplicar centímetros por centímetros el resultado "
        "queda en centímetros cuadrados, porque el área mide una superficie. Esa "
        "unidad es una buena señal para distinguirla del perímetro, que suma los "
        "lados y se mide en centímetros simples.",
        [
            ("26 cm²", "Calculó el perímetro (2×(8+5)) en lugar del área."),
            ("13 cm²", "Sumó el largo y el ancho en lugar de multiplicarlos."),
            ("3 cm²", "Restó el ancho al largo en lugar de multiplicarlos."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Un círculo tiene radio 6 cm. ¿Cuál es su área aproximada? (usa π ≈ 3,14)",
        "113,04 cm²",
        "El área del círculo se calcula con A = π × r², donde r es el radio.\n\n"
        "1) Eleva primero el radio al cuadrado: 6² = 36.\n"
        "2) Multiplica por π: A = 3,14 × 36 = 113,04.\n"
        "3) El resultado se expresa en cm², porque es una superficie: 113,04 cm².\n\n"
        "El orden importa: hay que elevar al cuadrado antes de multiplicar por π. Y no "
        "confundas esta fórmula con el perímetro del círculo, que es 2πr y da un valor "
        "mucho menor.",
        [
            ("37,68 cm²", "Calculó el perímetro (2πr) en lugar del área (πr²)."),
            ("18,84 cm²", "Calculó π×r en lugar de π×r², olvidando elevar el radio al cuadrado."),
            ("452,16 cm²", "Usó el diámetro (12 cm) en lugar del radio en la fórmula del área."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "Un triángulo rectángulo tiene catetos de 6 cm y 8 cm. ¿Cuánto mide la hipotenusa?",
        "10 cm",
        "El teorema de Pitágoras dice que en un triángulo rectángulo "
        "a² + b² = c², donde c es la hipotenusa (el lado opuesto al ángulo recto, "
        "siempre el más largo).\n\n"
        "1) Eleva cada cateto al cuadrado: 6² = 36 y 8² = 64.\n"
        "2) Súmalos: 36 + 64 = 100. Ese valor es c², no c todavía.\n"
        "3) Extrae la raíz cuadrada para llegar al lado: c = √100 = 10 cm.\n\n"
        "El paso que más se olvida es el tercero. Un control de sentido común: la "
        "hipotenusa debe ser mayor que cada cateto pero menor que su suma, y 10 está "
        "entre 8 y 14.",
        [
            ("14 cm", "Sumó los catetos directamente en lugar de aplicar el teorema de Pitágoras."),
            ("7 cm", "Calculó el promedio de los catetos en lugar de la hipotenusa."),
            ("100 cm", "Calculó correctamente 6²+8²=100 pero olvidó extraer la raíz cuadrada final."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "La hipotenusa de un triángulo rectángulo mide 13 cm y uno de sus catetos mide 5 cm. "
        "¿Cuánto mide el otro cateto?",
        "12 cm",
        "Se usa el mismo teorema, pero ahora el dato desconocido es un cateto, así que "
        "la operación es una resta.\n\n"
        "1) Escribe la relación: 5² + b² = 13².\n"
        "2) Calcula los cuadrados conocidos: 25 + b² = 169.\n"
        "3) Despeja restando: b² = 169 − 25 = 144.\n"
        "4) Extrae la raíz: b = √144 = 12 cm.\n\n"
        "La resta va siempre en ese orden, hipotenusa al cuadrado menos cateto al "
        "cuadrado, porque la hipotenusa es el lado mayor y su cuadrado es el más "
        "grande. Verifica: 5² + 12² = 25 + 144 = 169 = 13².",
        [
            ("18 cm", "Sumó los cuadrados de la hipotenusa y el cateto (13²+5²) en lugar de restarlos."),
            ("8 cm", "Restó los catetos directamente (13−5) sin elevarlos al cuadrado."),
            ("144 cm", "Calculó correctamente 13²−5²=144 pero olvidó extraer la raíz cuadrada final."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "Si el punto (3, 5) se traslada según el vector (−2, 4), ¿cuáles son sus nuevas coordenadas?",
        "(1, 9)",
        "Trasladar un punto es sumarle el vector componente a componente, respetando "
        "los signos.\n\n"
        "1) La primera componente del vector se suma a la coordenada x: "
        "3 + (−2) = 1. Sumar un número negativo equivale a restar.\n"
        "2) La segunda componente se suma a la coordenada y: 5 + 4 = 9.\n"
        "3) El punto trasladado es (1, 9).\n\n"
        "Geométricamente, el punto se movió 2 unidades hacia la izquierda y 4 hacia "
        "arriba. Cada componente actúa solo sobre su propia coordenada: la primera "
        "nunca afecta a y ni la segunda a x.",
        [
            ("(5, 1)", "Intercambió las componentes del vector, aplicando −2 a la coordenada y y 4 a la coordenada x."),
            ("(5, 9)", "Sumó el valor absoluto de la primera componente del vector en lugar de respetar su signo negativo."),
            ("(1, 1)", "Restó la componente y del vector en lugar de sumarla."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "Al reflejar el punto (4, −3) con respecto al eje X, ¿cuáles son sus nuevas coordenadas?",
        "(4, 3)",
        "Al reflejar respecto al eje X, el punto queda al otro lado de la línea "
        "horizontal, a la misma distancia.\n\n"
        "1) La coordenada x no cambia, porque el punto no se mueve hacia los lados: "
        "sigue siendo 4.\n"
        "2) La coordenada y cambia de signo, porque pasa de estar bajo el eje a estar "
        "sobre él: −3 se transforma en 3.\n"
        "3) El punto reflejado es (4, 3).\n\n"
        "Conviene tener clara la diferencia: reflejar en el eje X cambia el signo de y; "
        "reflejar en el eje Y cambia el signo de x; y reflejar respecto al origen "
        "cambia ambos.",
        [
            ("(−4, −3)", "Reflejó el punto respecto al eje Y en lugar del eje X."),
            ("(−4, 3)", "Reflejó el punto respecto al origen (invirtió ambos signos) en lugar de reflejarlo solo respecto al eje X."),
            ("(4, −3)", "No aplicó ninguna transformación, dejando el punto igual."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "¿Cuál es el volumen de un cilindro de radio 3 cm y altura 10 cm? (usa π ≈ 3,14)",
        "282,6 cm³",
        "El volumen de un cilindro es el área de su base circular multiplicada por la "
        "altura: V = π × r² × h.\n\n"
        "1) Calcula el área de la base: π × 3² = 3,14 × 9 = 28,26 cm².\n"
        "2) Multiplica por la altura: 28,26 × 10 = 282,6.\n"
        "3) El resultado va en cm³, porque el volumen ocupa tres dimensiones: "
        "282,6 cm³.\n\n"
        "Pensarlo como \"área de la base por altura\" ayuda a no olvidar ningún factor, "
        "y sirve igual para prismas y otros cuerpos rectos.",
        [
            ("94,2 cm³", "Calculó el área basal (πr²) pero olvidó multiplicarla por la altura."),
            ("188,4 cm³", "Usó π×d×h en lugar de π×r²×h, sin elevar el radio al cuadrado y usando el diámetro."),
            ("1130,4 cm³", "Usó el diámetro (6 cm) como si fuera el radio en la fórmula del volumen."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Una caja rectangular mide 4 cm de largo, 3 cm de ancho y 5 cm de alto. "
        "¿Cuál es su área total (superficie)?",
        "94 cm²",
        "Una caja tiene 6 caras que se agrupan en 3 pares iguales, uno por cada "
        "combinación de dos dimensiones.\n\n"
        "1) Calcula el área de una cara de cada par: largo × ancho = 4 × 3 = 12; "
        "largo × alto = 4 × 5 = 20; ancho × alto = 3 × 5 = 15.\n"
        "2) Súmalas: 12 + 20 + 15 = 47 cm². Eso corresponde a la mitad de la caja, "
        "una cara de cada par.\n"
        "3) Multiplica por 2, porque cada una tiene su cara opuesta idéntica: "
        "2 × 47 = 94 cm².\n\n"
        "La fórmula resumida es A = 2(lg·an + lg·al + an·al). Recuerda que el área va "
        "en cm² y el volumen en cm³: si te da centímetros cúbicos, calculaste otra "
        "cosa.",
        [
            ("60 cm³", "Calculó el volumen (4×3×5) en lugar del área total de la superficie."),
            ("47 cm²", "Sumó correctamente las tres áreas distintas de las caras, pero olvidó multiplicar el resultado por 2."),
            ("24 cm²", "Sumó solo las tres dimensiones (4+3+5) en lugar de calcular y sumar las áreas de las caras."),
        ],
    ),
    # ---------- PROBABILIDAD ----------
    _q(
        "prob_estadistica_desc", "facil",
        "¿Cuál es la media (promedio) de los datos: 4, 8, 6, 10, 2?",
        "6",
        "La media se obtiene sumando todos los datos y dividiendo por cuántos "
        "son.\n\n"
        "1) Suma los valores: 4 + 8 + 6 + 10 + 2 = 30.\n"
        "2) Cuenta los datos: son 5.\n"
        "3) Divide: 30 ÷ 5 = 6.\n\n"
        "Un control útil: la media siempre queda entre el menor y el mayor de los "
        "datos. Aquí el mínimo es 2 y el máximo 10, y 6 cae dentro de ese rango.",
        [
            ("8", "Identificó el valor máximo del conjunto en lugar de calcular el promedio."),
            ("30", "Entregó la suma total de los datos sin dividir por la cantidad de datos."),
            ("5", "Dividió la suma (30) entre una cantidad de datos incorrecta (6 en lugar de 5)."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "medio",
        "¿Cuál es la mediana del conjunto de datos: 7, 3, 9, 3, 12, 5?",
        "6",
        "La mediana es el valor del centro una vez ordenados los datos, así que el "
        "primer paso es siempre ordenar.\n\n"
        "1) Ordena de menor a mayor: 3, 3, 5, 7, 9, 12.\n"
        "2) Cuenta cuántos son: 6 datos, una cantidad par. Cuando la cantidad es par no "
        "hay un único valor central, sino dos.\n"
        "3) Identifica los dos del medio, en las posiciones tercera y cuarta: 5 y 7.\n"
        "4) Promédialos: (5 + 7) ÷ 2 = 6.\n\n"
        "Nota que la mediana puede ser un número que no aparece en el conjunto, como "
        "ocurre aquí. Si la cantidad de datos fuera impar, bastaría con tomar el valor "
        "del centro sin promediar.",
        [
            ("5", "Ordenó los datos correctamente pero eligió el menor de los dos valores centrales en lugar de promediarlos."),
            ("7", "Ordenó los datos correctamente pero eligió el mayor de los dos valores centrales en lugar de promediarlos."),
            ("3", "Confundió la mediana con la moda (el valor que más se repite en el conjunto)."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "dificil",
        "¿Cuál es el rango del siguiente conjunto de datos: 12, 5, 9, 20, 7?",
        "15",
        "El rango es una medida de dispersión: indica cuánto se separan los datos "
        "extremos entre sí.\n\n"
        "1) Identifica el valor máximo: 20.\n"
        "2) Identifica el valor mínimo: 5.\n"
        "3) Réstalos: 20 − 5 = 15.\n\n"
        "El rango es un solo número, no un par de valores, y no dice nada sobre cómo "
        "se distribuyen los datos intermedios: dos conjuntos muy distintos pueden "
        "tener el mismo rango si comparten sus extremos.",
        [
            ("20", "Entregó el valor máximo del conjunto en lugar de calcular la diferencia entre el máximo y el mínimo."),
            ("5", "Entregó el valor mínimo del conjunto en lugar de calcular el rango."),
            ("10,6", "Calculó el promedio de los datos en lugar del rango."),
        ],
    ),
    _q(
        "prob_combinatoria", "medio",
        "¿De cuántas formas distintas se pueden ordenar 4 libros diferentes en un estante?",
        "24",
        "Como importa el orden y se usan todos los libros, se trata de una "
        "permutación, que se calcula con el factorial.\n\n"
        "1) Razona por posiciones: para el primer lugar tienes 4 libros disponibles.\n"
        "2) Una vez puesto ese, quedan 3 opciones para el segundo lugar, luego 2 para "
        "el tercero y finalmente 1 para el último.\n"
        "3) Multiplica las opciones de cada paso: 4 × 3 × 2 × 1 = 24.\n\n"
        "Esa multiplicación es justamente 4! (cuatro factorial). Se multiplican y no se "
        "suman porque cada elección se combina con todas las siguientes.",
        [
            ("16", "Calculó 4² en lugar de 4! (confundió una permutación con una potencia)."),
            ("4", "Entregó solo la cantidad de libros, sin calcular las formas de ordenarlos."),
            ("10", "Calculó 4+3+2+1 (una suma) en lugar de 4×3×2×1 (el producto factorial)."),
        ],
    ),
    _q(
        "prob_combinatoria", "dificil",
        "¿De cuántas formas se puede formar un comité de 3 personas a partir de un grupo de 6, "
        "si el orden no importa?",
        "20",
        "Al no importar el orden, es una combinación: C(n, k) = n! / (k! × (n − k)!).\n\n"
        "1) Identifica los valores: n = 6 personas en total y k = 3 por elegir.\n"
        "2) Cuenta primero como si el orden importara: 6 × 5 × 4 = 120 formas de elegir "
        "tres personas en secuencia.\n"
        "3) Ese conteo repite cada comité varias veces, porque las mismas 3 personas se "
        "pueden ordenar de 3! = 6 maneras distintas y todas forman el mismo comité.\n"
        "4) Divide para eliminar las repeticiones: 120 ÷ 6 = 20.\n\n"
        "La diferencia entre permutación y combinación está solo en esa división: si el "
        "orden importara (por ejemplo, elegir presidente, secretario y tesorero), la "
        "respuesta sería 120.",
        [
            ("120", "Calculó la permutación P(6,3)=6×5×4, considerando que el orden de elección sí importa."),
            ("18", "Calculó 6×3 en lugar de aplicar la fórmula de combinatoria C(6,3)."),
            ("216", "Calculó 6³, asumiendo que una misma persona puede repetirse dentro del comité."),
        ],
    ),
    _q(
        "prob_reglas", "facil",
        "Al lanzar un dado de 6 caras, ¿cuál es la probabilidad de obtener un número mayor que 4?",
        "1/3",
        "La probabilidad de un evento es casos favorables dividido por casos "
        "posibles.\n\n"
        "1) Casos posibles: el dado tiene 6 caras, así que son 6.\n"
        "2) Casos favorables: los números mayores que 4 son el 5 y el 6. El 4 no "
        "cuenta, porque \"mayor que 4\" excluye al propio 4. Son 2 casos.\n"
        "3) Divide: 2/6.\n"
        "4) Simplifica dividiendo ambos por 2: 1/3.\n\n"
        "Presta atención a esa distinción de lenguaje: si el enunciado dijera \"mayor o "
        "igual que 4\", los casos favorables serían tres (4, 5 y 6) y la respuesta "
        "cambiaría a 1/2.",
        [
            ("2/3", "Contó como casos favorables los números menores o iguales a 4, en lugar de los mayores a 4."),
            ("1/6", "Consideró solo un caso favorable (por ejemplo, únicamente el 6) en lugar de los dos válidos (5 y 6)."),
            ("4/6", "Interpretó 'mayor que 4' como 'mayor o igual que 4', incluyendo el 4 como caso favorable."),
        ],
    ),
    _q(
        "prob_reglas", "medio",
        "En una bolsa hay 5 bolitas rojas y 3 azules. Si se saca una al azar, "
        "¿cuál es la probabilidad de que sea azul?",
        "3/8",
        "De nuevo, casos favorables sobre casos posibles, cuidando qué va en cada "
        "lugar.\n\n"
        "1) Casos favorables: las bolitas azules son 3.\n"
        "2) Casos posibles: el total de bolitas en la bolsa, sumando ambos colores, "
        "5 + 3 = 8.\n"
        "3) La probabilidad es 3/8, que no se puede simplificar.\n\n"
        "El denominador es siempre el total de resultados posibles, nunca la cantidad "
        "del otro color. Como comprobación, la probabilidad de sacar roja es 5/8, y "
        "ambas suman 3/8 + 5/8 = 1, tal como debe ser cuando se cubren todos los "
        "casos.",
        [
            ("5/8", "Calculó la probabilidad de sacar una bolita roja en lugar de una azul."),
            ("3/5", "Comparó la cantidad de bolitas azules con la de rojas, en lugar de con el total de bolitas."),
            ("1/3", "Calculó la probabilidad como 1 dividido en el número de colores distintos, ignorando cuántas bolitas hay de cada color."),
        ],
    ),
    _q(
        "prob_reglas", "dificil",
        "Se lanzan dos monedas al mismo tiempo. ¿Cuál es la probabilidad de obtener al menos una cara?",
        "3/4",
        "Con dos monedas hay que considerar el espacio muestral completo, tratando "
        "cada moneda por separado.\n\n"
        "1) Los resultados posibles son cuatro: cara-cara, cara-sello, sello-cara y "
        "sello-sello. Cara-sello y sello-cara cuentan como casos distintos porque las "
        "monedas son independientes entre sí.\n"
        "2) \"Al menos una cara\" significa una o dos caras, así que sirven los tres "
        "primeros resultados: 3 casos favorables de 4.\n"
        "3) La probabilidad es 3/4.\n\n"
        "El camino más rápido es por el complemento: lo contrario de \"al menos una "
        "cara\" es \"ninguna cara\", que ocurre solo en sello-sello, con probabilidad "
        "1/4. Entonces 1 − 1/4 = 3/4. Ese truco ahorra mucho trabajo cuando hay más "
        "monedas.",
        [
            ("1/2", "Consideró solo dos resultados posibles (cara o sello) en lugar de los cuatro del espacio muestral conjunto (CC, CS, SC, SS)."),
            ("1/4", "Calculó la probabilidad de obtener exactamente dos caras (CC) en lugar de 'al menos una'."),
            ("1", "Asumió que obtener al menos una cara es un evento seguro al lanzar dos monedas."),
        ],
    ),
]
