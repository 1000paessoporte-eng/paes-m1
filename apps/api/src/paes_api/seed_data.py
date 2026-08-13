"""Datos semilla: Árbol de Habilidades + banco de preguntas PAES M1.

Tres lotes (36 + 30 + 45 = 111 preguntas, repartidas por eje). Cada pregunta trae
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

# Nodos exclusivos de M2 (code, name, axis, tier, prerequisites). M2 evalúa
# "todos los conocimientos de M1, además de" contenido propio (temario DEMRE
# Admisión 2026), así que estos nodos se agregan sobre el árbol de M1 en vez
# de duplicarlo: cada uno toma como prerequisito el nodo M1 más relacionado.
# `seed.py` los siembra con subject="m2"; `SUBJECT_INCLUDES` en
# exam_focus/service.py hace que el banco de M2 sea M1 ∪ M2.
SKILL_NODES_M2 = [
    # Números
    ("num_reales", "El conjunto de los números reales", "numeros", 2, ["num_racionales", "num_potencias_raices"]),
    ("num_financiera", "Matemática financiera", "numeros", 3, ["num_porcentajes"]),
    ("num_logaritmos", "Logaritmos", "numeros", 3, ["num_potencias_raices"]),
    # Álgebra y funciones
    ("alg_sistemas_casos", "Sistemas 2x2: única, infinitas o ninguna solución", "algebra", 4, ["alg_sistemas"]),
    ("alg_funcion_potencia", "Función potencia", "algebra", 5, ["alg_funciones"]),
    # Geometría
    ("geo_homotecia", "Homotecia de figuras planas", "geometria", 3, ["geo_transformaciones"]),
    ("geo_trigonometria", "Razones trigonométricas en triángulos rectángulos", "geometria", 3, ["geo_pitagoras"]),
    # Probabilidad y estadística
    ("prob_dispersion", "Medidas de dispersión", "probabilidad", 2, ["prob_estadistica_desc"]),
    ("prob_condicional", "Probabilidad condicional", "probabilidad", 4, ["prob_reglas"]),
    ("prob_permutacion", "Permutación y combinatoria (nivel M2)", "probabilidad", 3, ["prob_combinatoria"]),
    ("prob_binomial", "Modelos probabilísticos (binomial)", "probabilidad", 4, ["prob_permutacion", "prob_condicional"]),
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
    # ---------- LOTE 2 (30 preguntas más, agosto 2026) ----------
    # ---------- NÚMEROS ----------
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 2/5 × 3/4?",
        "3/10",
        "Para multiplicar fracciones se multiplican los numeradores entre sí y "
        "los denominadores entre sí, sin necesidad de buscar un denominador "
        "común.\n\n"
        "1) Multiplica los numeradores: 2 × 3 = 6.\n"
        "2) Multiplica los denominadores: 5 × 4 = 20.\n"
        "3) El resultado es 6/20. Simplifica dividiendo ambos por 2: 3/10.\n\n"
        "A diferencia de la suma, en la multiplicación de fracciones nunca hace "
        "falta igualar los denominadores primero.",
        [
            ("23/20", "Sumó las fracciones (buscando denominador común) en lugar de multiplicarlas."),
            ("6/5", "Multiplicó los numeradores correctamente pero olvidó multiplicar los denominadores."),
            ("8/15", "Trató la multiplicación como si fuera una división e invirtió la segunda fracción."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "¿Cuál es el resultado de 5/6 − 1/3 + 1/4?",
        "3/4",
        "Con tres fracciones se buscan primero el denominador común de todas, y "
        "luego se opera de izquierda a derecha en el orden en que aparecen.\n\n"
        "1) El mínimo común múltiplo de 6, 3 y 4 es 12. Convierte cada fracción: "
        "5/6 = 10/12, 1/3 = 4/12, 1/4 = 3/12.\n"
        "2) Resta y suma los numeradores en el orden del enunciado: "
        "10 − 4 + 3 = 9.\n"
        "3) El resultado es 9/12, que simplificado por 3 da 3/4.\n\n"
        "El orden importa: la resta y la suma tienen la misma prioridad, así que "
        "se resuelven de izquierda a derecha, no agrupando la suma primero.",
        [
            ("1/4", "Sumó 1/3+1/4 antes de restar 5/6, alterando el orden de izquierda a derecha de las operaciones."),
            ("17/12", "Sumó los tres términos en lugar de restar el segundo, ignorando el signo menos antes de 1/3."),
            ("9/12", "Resolvió correctamente la operación pero no simplificó la fracción a su forma más simple."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el resultado de 5² × 5³?",
        "3.125",
        "Al multiplicar potencias de igual base, los exponentes se suman.\n\n"
        "1) La base es la misma (5) en ambos factores, así que se aplica la "
        "propiedad: 5² × 5³ = 5^(2+3) = 5⁵.\n"
        "2) Calcula 5⁵: 5×5×5×5×5 = 3.125.\n\n"
        "Es más rápido sumar los exponentes que desarrollar cada potencia por "
        "separado y multiplicar los resultados, aunque ambos caminos llegan al "
        "mismo valor.",
        [
            ("25", "Calculó solo 5² y olvidó multiplicar por el segundo factor, 5³."),
            ("15.625", "Multiplicó los exponentes (2×3) en lugar de sumarlos (2+3)."),
            ("150", "Sumó las potencias 5²+5³ en lugar de multiplicarlas."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "Si 2^(2x) = 64, ¿cuál es el valor de x?",
        "3",
        "Igual que antes, se escriben ambos lados como potencias de la misma "
        "base y se igualan los exponentes.\n\n"
        "1) Expresa 64 como potencia de 2: 2×2×2×2×2×2 = 64, o sea 64 = 2⁶.\n"
        "2) La ecuación queda 2^(2x) = 2⁶.\n"
        "3) Si las bases son iguales, los exponentes también lo son: 2x = 6.\n"
        "4) Despeja dividiendo por 2: x = 3.\n\n"
        "Verifica reemplazando: 2^(2×3) = 2⁶ = 64. Correcto.",
        [
            ("6", "Igualó x directamente a 6 (el exponente de 64=2⁶), sin dividir por 2 para despejar x."),
            ("12", "Multiplicó 2x=6 por 2 en lugar de dividir, al despejar x."),
            ("2,5", "Confundió 64 con 2⁵ al contar mal las potencias de 2 (2,4,8,16,32,64 corresponden a 2¹...2⁶, no hasta 2⁵), y despejó 2x=5."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "El precio de una entrada al cine subió de $6.000 a $7.500. ¿Cuál fue el porcentaje de aumento?",
        "25%",
        "El porcentaje de variación siempre se calcula sobre el valor original, "
        "no sobre el nuevo.\n\n"
        "1) Calcula cuánto aumentó en pesos: 7.500 − 6.000 = 1.500.\n"
        "2) Divide ese aumento por el precio ORIGINAL: 1.500 ÷ 6.000 = 0,25.\n"
        "3) Exprésalo como porcentaje: 0,25 = 25%.\n\n"
        "Un error común es dividir por el precio nuevo en lugar del original: "
        "eso responde una pregunta distinta (\"qué porcentaje del precio nuevo "
        "es el aumento\"), no el porcentaje de aumento respecto al original.",
        [
            ("20%", "Calculó el aumento (1.500) sobre el precio nuevo (7.500) en lugar de sobre el precio original."),
            ("$1.500", "Entregó el aumento en pesos en lugar del porcentaje que representa."),
            ("125%", "Calculó que el precio nuevo es el 125% del original (7.500÷6.000=1,25), pero confundió ese 125% con el porcentaje de AUMENTO, que es solo la parte que excede el 100% (o sea, 25%)."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Después de aplicar un descuento del 30%, un producto cuesta $21.000. ¿Cuál era su precio original?",
        "$30.000",
        "Cuando se conoce el precio FINAL y el porcentaje de descuento, hay que "
        "despejar el precio original desde una ecuación, no aplicar el "
        "porcentaje directamente sobre el precio final.\n\n"
        "1) Si se descuenta un 30%, el precio final corresponde al 70% del "
        "original: precio final = 0,70 × precio original.\n"
        "2) Reemplaza el dato conocido: 21.000 = 0,70 × precio original.\n"
        "3) Despeja dividiendo: precio original = 21.000 ÷ 0,70 = 30.000.\n\n"
        "Verifica: el 30% de 30.000 es 9.000, y 30.000 − 9.000 = 21.000. "
        "Coincide con el precio final del enunciado.",
        [
            ("$27.300", "Sumó el 30% del precio FINAL (21.000) al propio precio final, en lugar de despejar el original desde la ecuación del descuento."),
            ("$70.000", "Dividió por 0,3 (el porcentaje descontado) en lugar de por 0,7 (el porcentaje que efectivamente se paga)."),
            ("$24.150", "Aumentó el precio final en un 15%, la mitad del descuento real, en un intento incorrecto de revertirlo."),
        ],
    ),
    # ---------- ÁLGEBRA ----------
    _q(
        "alg_expresiones", "facil",
        "Reduce la expresión: 4a − 2b + 3a + 5b",
        "7a + 3b",
        "Se agrupan por separado los términos que tienen la misma parte "
        "literal.\n\n"
        "1) Agrupa los términos con a: 4a + 3a = 7a.\n"
        "2) Agrupa los términos con b: −2b + 5b = 3b.\n"
        "3) Junta ambos resultados: 7a + 3b.\n\n"
        "Los términos en a y en b no se pueden combinar entre sí, porque tienen "
        "distinta parte literal.",
        [
            ("7a − 3b", "Restó los coeficientes de b en lugar de sumarlos (calculó −2−5 en vez de −2+5)."),
            ("a + 3b", "Restó los coeficientes de a en lugar de sumarlos (4−3 en vez de 4+3)."),
            ("7ab", "Multiplicó los términos en a y en b entre sí, en lugar de tratarlos como términos independientes que solo se suman."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "Factoriza la expresión: x² + 2x − 15",
        "(x + 5)(x − 3)",
        "Se buscan dos números que, multiplicados, den el término libre (−15) "
        "y, sumados, den el coeficiente de x (2).\n\n"
        "1) Prueba pares de factores de −15: 5 y −3 cumplen ambas condiciones, "
        "porque 5 × (−3) = −15 y 5 + (−3) = 2.\n"
        "2) Escribe la factorización usando esos números: (x + 5)(x − 3).\n\n"
        "Comprueba multiplicando de vuelta: x² − 3x + 5x − 15 = x² + 2x − 15, "
        "que coincide con la expresión original.",
        [
            ("(x − 5)(x + 3)", "Invirtió los signos de los números encontrados (usó −5 y 3 en lugar de 5 y −3)."),
            ("(x + 3)(x + 5)", "Ignoró que el producto debía ser negativo (−15) y usó ambos números positivos."),
            ("(x − 15)(x + 1)", "Eligió un par de factores de −15 (−15 y 1) sin verificar que también debían sumar 2 (−15+1=−14, no 2)."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "Resuelve: 3(x − 2) = 2x + 1",
        "x = 7",
        "Primero se elimina el paréntesis distribuyendo, y recién después se "
        "agrupan los términos semejantes.\n\n"
        "1) Distribuye el 3: 3x − 6 = 2x + 1.\n"
        "2) Resta 2x a ambos lados para dejar la x sola de un lado: "
        "3x − 2x − 6 = 1, o sea x − 6 = 1.\n"
        "3) Suma 6 a ambos lados: x = 7.\n\n"
        "Verifica en la ecuación original: 3 × (7−2) = 3×5 = 15, y "
        "2×7+1 = 15. Ambos lados coinciden.",
        [
            ("x = 3", "No distribuyó el 3 sobre el −2, dejando la ecuación como 3x−2=2x+1."),
            ("x = -5", "Al pasar los términos, restó en lugar de sumar (3x−2x=1−6 en vez de 1+6)."),
            ("x = 7/3", "Olvidó restar 2x en ambos lados, dejando 3x−6=1 en lugar de x−6=1."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "Resuelve la inecuación: 3x − 7 ≤ x + 5",
        "x ≤ 6",
        "Se despeja igual que una ecuación, prestando atención al signo del "
        "número por el que se divide al final.\n\n"
        "1) Resta x a ambos lados: 2x − 7 ≤ 5.\n"
        "2) Suma 7 a ambos lados: 2x ≤ 12.\n"
        "3) Divide por 2. Como 2 es positivo, el sentido de la desigualdad NO "
        "cambia: x ≤ 6.\n\n"
        "A diferencia de dividir por un número negativo, dividir por uno "
        "positivo nunca invierte el signo de la desigualdad.",
        [
            ("x ≥ 6", "Invirtió el sentido de la desigualdad al dividir por 2, aunque 2 es positivo y no correspondía cambiarlo."),
            ("x ≤ -1", "Al pasar el −7 al otro lado, le cambió el signo de forma incorrecta (2x=5−7=−2 en lugar de 2x=5+7=12)."),
            ("x ≤ 12", "Despejó correctamente 2x≤12 pero olvidó dividir por 2 en el último paso."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "Resuelve el sistema: x = y + 2 ; x + y = 10",
        "x = 6, y = 4",
        "Como la primera ecuación ya tiene x despejada, conviene sustituirla "
        "directamente en la segunda.\n\n"
        "1) Reemplaza x por (y + 2) en la segunda ecuación: (y + 2) + y = 10.\n"
        "2) Reduce los términos semejantes: 2y + 2 = 10.\n"
        "3) Resta 2 y luego divide por 2: 2y = 8, entonces y = 4.\n"
        "4) Reemplaza en la primera ecuación: x = 4 + 2 = 6.\n\n"
        "Verifica en la segunda ecuación original: 6 + 4 = 10. Se cumple.",
        [
            ("x = 4, y = 6", "Invirtió la relación x=y+2, usándola como y=x+2, lo que intercambia los valores finales de x e y."),
            ("x = 10, y = 8", "Despejó 2y=8 pero olvidó dividir entre 2, dejando y=8 en lugar de 4, y arrastró ese error a x."),
            ("x = 8, y = 6", "Al despejar 2y+2=10, sumó el 2 en lugar de restarlo (2y=12 en vez de 8)."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "En un corral hay conejos y gallinas. En total hay 10 cabezas y 26 patas. "
        "¿Cuántos conejos y cuántas gallinas hay?",
        "3 conejos y 7 gallinas",
        "Se traduce el enunciado a un sistema de ecuaciones: una por cabezas "
        "(cada animal aporta 1) y otra por patas (los conejos aportan 4 y las "
        "gallinas 2).\n\n"
        "1) Llama c a los conejos y g a las gallinas. Cabezas: c + g = 10. "
        "Patas: 4c + 2g = 26.\n"
        "2) Despeja g de la primera ecuación: g = 10 − c.\n"
        "3) Sustituye en la segunda: 4c + 2(10 − c) = 26, o sea "
        "4c + 20 − 2c = 26, que se reduce a 2c = 6.\n"
        "4) Despeja: c = 3. Reemplaza en g = 10 − c: g = 7.\n\n"
        "Verifica: 3 + 7 = 10 cabezas, y 4×3 + 2×7 = 12 + 14 = 26 patas.",
        [
            ("7 conejos y 3 gallinas", "Intercambió cuál cantidad corresponde a conejos y cuál a gallinas."),
            ("5 conejos y 5 gallinas", "Usó solo la ecuación de las cabezas (10 en total) e ignoró por completo la de las patas."),
            ("4 conejos y 6 gallinas", "Encontró una combinación que cumple la ecuación de las cabezas (10) pero no verificó las patas: 4×4+2×6=28, no 26."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "Resuelve: x² − 49 = 0",
        "x = 7 y x = −7",
        "Es una ecuación cuadrática incompleta, sin término en x, así que se "
        "despeja directamente.\n\n"
        "1) Suma 49 a ambos lados: x² = 49.\n"
        "2) Extrae raíz cuadrada. Como 7 × 7 = 49 y también (−7) × (−7) = 49, "
        "hay dos soluciones.\n"
        "3) La respuesta es x = 7 y x = −7.\n\n"
        "Olvidar la raíz negativa deja la respuesta incompleta: toda ecuación "
        "cuadrática de este tipo tiene dos soluciones simétricas.",
        [
            ("x = 7", "Solo consideró la raíz positiva, olvidando que x = −7 también es solución."),
            ("x = 24,5", "Dividió 49 por 2 en lugar de calcular su raíz cuadrada."),
            ("x = 2.401", "Elevó 49 al cuadrado en lugar de calcular su raíz cuadrada."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "Resuelve: x² + 7x + 10 = 0",
        "x = −2 y x = −5",
        "Se factoriza buscando dos números que multiplicados den 10 y sumados "
        "den 7.\n\n"
        "1) Los números 2 y 5 cumplen ambas condiciones: 2 × 5 = 10 y "
        "2 + 5 = 7.\n"
        "2) Escribe la factorización: (x + 2)(x + 5) = 0.\n"
        "3) Un producto es cero solo si algún factor lo es: x + 2 = 0 o "
        "x + 5 = 0.\n"
        "4) Despejando cada una: x = −2 y x = −5.\n\n"
        "Verifica con x = −2: (−2)² + 7×(−2) + 10 = 4 − 14 + 10 = 0.",
        [
            ("x = 2 y x = 5", "Cambió el signo de las soluciones al leer la factorización (x+2)(x+5), olvidando que las raíces son los valores que anulan cada factor (−2 y −5, no 2 y 5)."),
            ("x = 1 y x = 10", "Buscó dos números que sumaran 10 y multiplicaran 7, invirtiendo el rol de los coeficientes en la factorización."),
            ("x = -1 y x = -10", "Combinó los dos errores anteriores: usó los números 1 y 10 con el signo correcto de las raíces, en lugar de 2 y 5."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿Cuál es el valor de y cuando x = 3 en la función y = 2x − 4?",
        "y = 2",
        "Evaluar una función es reemplazar la variable por el valor dado y "
        "calcular el resultado, respetando el orden de las operaciones.\n\n"
        "1) Reemplaza x por 3: y = 2 × 3 − 4.\n"
        "2) Multiplica primero: 2 × 3 = 6.\n"
        "3) Resta: 6 − 4 = 2.\n\n"
        "La multiplicación se resuelve antes que la resta, porque en "
        "y = 2x − 4 el 2 multiplica solo a la x, no a toda la expresión.",
        [
            ("y = 10", "Sumó en lugar de restar: calculó 2×3+4 en vez de 2×3−4."),
            ("y = -1", "Olvidó multiplicar x por 2, calculando solo x−4."),
            ("y = -2", "Aplicó la resta antes de multiplicar, como si la función fuera y=2(x−4) en lugar de y=2x−4."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuáles son las intersecciones con el eje X de la parábola y = x² − x − 6?",
        "x = 3 y x = −2",
        "Las intersecciones con el eje X son los puntos donde y = 0, así que "
        "se resuelve la ecuación cuadrática igualada a cero.\n\n"
        "1) Iguala a cero: x² − x − 6 = 0.\n"
        "2) Busca dos números que multiplicados den −6 y sumados den −1: son "
        "−3 y 2, porque (−3) × 2 = −6 y (−3) + 2 = −1.\n"
        "3) Factoriza: (x − 3)(x + 2) = 0.\n"
        "4) Despeja cada factor: x = 3 y x = −2.\n\n"
        "Los puntos de intersección son (3, 0) y (−2, 0). Verifica con x=3: "
        "3² − 3 − 6 = 9 − 3 − 6 = 0.",
        [
            ("x = -3 y x = 2", "Invirtió los signos de los números de la factorización, olvidando que las raíces anulan cada factor."),
            ("x = 1 y x = -6", "Buscó dos números que sumaran −6 y multiplicaran −1, invirtiendo el rol de los coeficientes."),
            ("x = 6", "Tomó el término independiente (6) como si fuera directamente la solución, sin factorizar la ecuación ni notar que tiene dos raíces."),
        ],
    ),
    # ---------- GEOMETRÍA ----------
    _q(
        "geo_plana", "facil",
        "¿Cuál es el perímetro de un rectángulo de 9 cm de largo y 4 cm de ancho?",
        "26 cm",
        "El perímetro es la suma de los cuatro lados: dos veces el largo más "
        "dos veces el ancho.\n\n"
        "1) Suma el largo y el ancho: 9 + 4 = 13.\n"
        "2) Multiplica por 2, porque hay dos lados de cada medida: "
        "2 × 13 = 26.\n\n"
        "El resultado va en cm, la misma unidad de los datos, porque el "
        "perímetro mide una longitud, no una superficie.",
        [
            ("36 cm²", "Calculó el área (9×4) en lugar del perímetro, y arrastró la unidad de superficie."),
            ("13 cm", "Sumó el largo y el ancho pero olvidó multiplicar por 2."),
            ("5 cm", "Restó el ancho al largo en lugar de sumarlos."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Un triángulo tiene base 10 cm y su área es 45 cm². ¿Cuál es su altura?",
        "9 cm",
        "El área del triángulo es A = (base × altura) / 2. Como se conoce el "
        "área, hay que despejar la altura desde esa fórmula.\n\n"
        "1) Reemplaza los datos conocidos: 45 = (10 × h) / 2.\n"
        "2) Multiplica ambos lados por 2 para quitar la división: 90 = 10 × h.\n"
        "3) Divide por 10: h = 9.\n\n"
        "Verifica reemplazando: (10 × 9) / 2 = 90 / 2 = 45 cm², que coincide "
        "con el área dada.",
        [
            ("4,5 cm", "Dividió el área directamente por la base (45÷10) sin considerar el factor 1/2 de la fórmula."),
            ("90 cm", "Multiplicó el área por 2 y por la base, en lugar de despejar correctamente la altura."),
            ("22,5 cm", "Dividió el área entre 2 (45÷2) pero no relacionó ese resultado con la base para terminar de despejar la altura."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "Un triángulo rectángulo tiene catetos de 9 cm y 12 cm. ¿Cuánto mide la hipotenusa?",
        "15 cm",
        "Se aplica el teorema de Pitágoras: a² + b² = c².\n\n"
        "1) Eleva cada cateto al cuadrado: 9² = 81 y 12² = 144.\n"
        "2) Súmalos: 81 + 144 = 225.\n"
        "3) Extrae la raíz cuadrada: c = √225 = 15 cm.\n\n"
        "Control de sentido: la hipotenusa debe ser mayor que cada cateto pero "
        "menor que su suma, y 15 está entre 12 y 21.",
        [
            ("21 cm", "Sumó los catetos directamente en lugar de aplicar el teorema de Pitágoras."),
            ("10,5 cm", "Calculó el promedio de los catetos en lugar de la hipotenusa."),
            ("225 cm", "Calculó correctamente 9²+12²=225 pero olvidó extraer la raíz cuadrada final."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "Un rectángulo mide 12 cm de largo y su diagonal mide 13 cm. ¿Cuánto mide su ancho?",
        "5 cm",
        "La diagonal de un rectángulo, junto con el largo y el ancho, forma un "
        "triángulo rectángulo donde la diagonal es la hipotenusa.\n\n"
        "1) Aplica el teorema: diagonal² = largo² + ancho², o sea "
        "13² = 12² + ancho².\n"
        "2) Calcula los cuadrados conocidos: 169 = 144 + ancho².\n"
        "3) Despeja restando: ancho² = 169 − 144 = 25.\n"
        "4) Extrae la raíz: ancho = √25 = 5 cm.\n\n"
        "Verifica: 12² + 5² = 144 + 25 = 169 = 13².",
        [
            ("1 cm", "Restó los valores directamente (13−12) en lugar de aplicar el teorema de Pitágoras."),
            ("25 cm", "Calculó correctamente 13²−12²=25 pero olvidó extraer la raíz cuadrada final."),
            ("17 cm", "Sumó los cuadrados de la diagonal y el largo (13²+12²) en lugar de restarlos."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "Si el punto (−2, 6) se traslada según el vector (5, −3), ¿cuáles son sus nuevas coordenadas?",
        "(3, 3)",
        "Trasladar un punto es sumarle el vector componente a componente, "
        "respetando los signos de ambos.\n\n"
        "1) Suma la primera componente del vector a la coordenada x: "
        "−2 + 5 = 3.\n"
        "2) Suma la segunda componente a la coordenada y: 6 + (−3) = 3.\n"
        "3) El punto trasladado es (3, 3).\n\n"
        "Cada componente del vector actúa solo sobre su propia coordenada: la "
        "primera nunca afecta a y ni la segunda a x.",
        [
            ("(3, 9)", "Sumó con el signo equivocado la segunda componente, usando +3 en lugar de −3 (6+3=9 en vez de 6−3=3)."),
            ("(-7, 9)", "Restó la primera componente del vector en lugar de sumarla, y también sumó con el signo equivocado la segunda."),
            ("(7, 3)", "Ignoró el signo negativo de la coordenada x del punto original al sumar el vector (trató −2 como si fuera 2)."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "Al rotar el punto (4, 2) en 180° respecto al origen, ¿cuáles son sus nuevas coordenadas?",
        "(−4, −2)",
        "Una rotación de 180° respecto al origen deja al punto exactamente al "
        "otro lado del origen, a la misma distancia, así que invierte el signo "
        "de ambas coordenadas.\n\n"
        "1) Cambia el signo de la coordenada x: 4 pasa a −4.\n"
        "2) Cambia el signo de la coordenada y: 2 pasa a −2.\n"
        "3) El punto rotado es (−4, −2).\n\n"
        "No confundir con una reflexión: reflejar en el eje X solo cambia el "
        "signo de y, y reflejar en el eje Y solo cambia el signo de x. Rotar "
        "180° cambia los dos signos a la vez.",
        [
            ("(4, -2)", "Reflejó el punto respecto al eje X en lugar de rotarlo 180° respecto al origen (cambió solo el signo de y)."),
            ("(-4, 2)", "Reflejó el punto respecto al eje Y en lugar de rotarlo 180° respecto al origen (cambió solo el signo de x)."),
            ("(2, 4)", "Intercambió las coordenadas del punto en lugar de invertir sus signos."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "¿Cuál es el volumen de un cubo de arista 5 cm?",
        "125 cm³",
        "El volumen de un cubo es su arista elevada al cubo: V = arista³.\n\n"
        "1) Reemplaza el dato: V = 5³.\n"
        "2) Calcula: 5 × 5 × 5 = 125.\n"
        "3) El resultado va en cm³, porque el volumen ocupa tres dimensiones: "
        "125 cm³.\n\n"
        "No lo confundas con el área de una cara (5² = 25 cm²), que es una "
        "medida de superficie, no de volumen.",
        [
            ("25 cm²", "Calculó el área de una cara (arista²) en lugar del volumen del cubo completo."),
            ("15 cm³", "Multiplicó la arista por 3 (5×3) en lugar de elevarla al cubo (5×5×5)."),
            ("75 cm³", "Calculó el área de tres caras (arista²×3=75) en lugar del volumen (arista³)."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Una esfera tiene radio 3 cm. ¿Cuál es su volumen aproximado? "
        "(usa π ≈ 3,14 y la fórmula V = (4/3) × π × r³)",
        "113,04 cm³",
        "Se reemplazan los datos en la fórmula del volumen de la esfera, "
        "resolviendo en el orden correcto.\n\n"
        "1) Eleva el radio al cubo: 3³ = 27.\n"
        "2) Multiplica por π: 3,14 × 27 = 84,78.\n"
        "3) Multiplica por 4: 84,78 × 4 = 339,12.\n"
        "4) Divide por 3, el último factor de la fórmula: 339,12 ÷ 3 = 113,04.\n\n"
        "El resultado va en cm³, porque el volumen ocupa tres dimensiones.",
        [
            ("28,26 cm³", "Calculó π×r² (como el área de un círculo) en lugar de aplicar la fórmula del volumen de la esfera."),
            ("339,12 cm³", "Calculó correctamente 4×π×r³ pero olvidó dividir por 3 en el último paso."),
            ("84,78 cm³", "Calculó π×r³ pero olvidó multiplicar por el factor 4/3 de la fórmula."),
        ],
    ),
    # ---------- PROBABILIDAD ----------
    _q(
        "prob_estadistica_desc", "facil",
        "¿Cuál es la moda del siguiente conjunto de datos: 3, 7, 5, 7, 2, 7, 9?",
        "7",
        "La moda es el valor que más veces se repite en el conjunto, a "
        "diferencia de la media (el promedio) o la mediana (el valor central "
        "al ordenar).\n\n"
        "1) Cuenta cuántas veces aparece cada valor: 3 (una vez), 7 (tres "
        "veces), 5 (una vez), 2 (una vez), 9 (una vez).\n"
        "2) El valor 7 es el que más se repite, con 3 apariciones.\n\n"
        "La moda es el dato mismo (7), no la cantidad de veces que se repite "
        "(3): esa cantidad se llama frecuencia, y es un concepto distinto.",
        [
            ("5", "Calculó la mediana (el valor central al ordenar los datos) en lugar de la moda."),
            ("5,71", "Calculó la media (el promedio de los siete datos) en lugar de la moda."),
            ("3", "Confundió la frecuencia del valor moda (cuántas veces se repite) con el valor mismo."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "medio",
        "Un conjunto de 4 datos tiene media 8. Si tres de los datos son 6, 9 y 10, "
        "¿cuál es el cuarto dato?",
        "7",
        "La media es la suma de todos los datos dividida por la cantidad de "
        "datos, así que primero hay que reconstruir la suma total.\n\n"
        "1) Si la media de 4 datos es 8, la suma de los 4 debe ser "
        "8 × 4 = 32.\n"
        "2) Suma los tres datos conocidos: 6 + 9 + 10 = 25.\n"
        "3) El cuarto dato es la diferencia: 32 − 25 = 7.\n\n"
        "Verifica: (6 + 9 + 10 + 7) / 4 = 32 / 4 = 8, que coincide con la "
        "media dada.",
        [
            ("8", "Asumió que el dato faltante debía ser igual a la media, sin calcular la suma total real de los 4 datos."),
            ("25", "Entregó la suma de los tres datos conocidos, sin restarla del total necesario (32) para encontrar el cuarto."),
            ("17", "Al sumar los tres datos conocidos, olvidó incluir uno de ellos (6+9=15 en lugar de 6+9+10=25)."),
        ],
    ),
    _q(
        "prob_combinatoria", "facil",
        "¿De cuántas formas distintas se pueden ordenar 5 fotos diferentes en un álbum, una tras otra?",
        "120",
        "Como importa el orden y se usan las 5 fotos, es una permutación, que "
        "se calcula con el factorial.\n\n"
        "1) Para el primer lugar hay 5 fotos disponibles, para el segundo "
        "quedan 4, luego 3, luego 2 y finalmente 1.\n"
        "2) Multiplica las opciones de cada lugar: 5 × 4 × 3 × 2 × 1 = 120.\n\n"
        "Esa multiplicación es 5! (cinco factorial). Se multiplican y no se "
        "suman porque cada elección se combina con todas las posteriores.",
        [
            ("25", "Calculó 5² en lugar de 5! (confundió una permutación con una potencia)."),
            ("5", "Entregó solo la cantidad de fotos, sin calcular las formas de ordenarlas."),
            ("15", "Sumó 5+4+3+2+1 en lugar de multiplicar esos mismos valores."),
        ],
    ),
    _q(
        "prob_combinatoria", "dificil",
        "¿De cuántas formas se pueden repartir 2 premios distintos (primer y "
        "segundo lugar) entre 6 participantes, si nadie puede ganar más de un "
        "premio?",
        "30",
        "Como los premios son distintos entre sí (no es lo mismo ganar el "
        "primero que el segundo) y nadie repite, se trata de una permutación "
        "de 6 elementos tomados de a 2.\n\n"
        "1) Para el primer premio hay 6 participantes posibles.\n"
        "2) Para el segundo premio, como ya se entregó el primero, quedan "
        "5 participantes posibles.\n"
        "3) Multiplica las opciones: 6 × 5 = 30.\n\n"
        "Si los dos premios fueran idénticos (por ejemplo, dos entradas de "
        "cine iguales), correspondería usar combinatoria en lugar de "
        "permutación, y el resultado sería distinto.",
        [
            ("15", "Calculó la combinación (6×5)/2=15, tratando ambos premios como si fueran idénticos, sin distinguir primer y segundo lugar."),
            ("36", "Calculó 6² en lugar de 6×5, permitiendo que una misma persona ganara ambos premios."),
            ("6", "Entregó solo la cantidad de participantes, sin calcular las formas de asignar los dos premios."),
        ],
    ),
    _q(
        "prob_reglas", "facil",
        "En una bolsa hay 4 bolitas verdes y 6 amarillas. Si se saca una al azar, "
        "¿cuál es la probabilidad de que sea verde?",
        "2/5",
        "La probabilidad es casos favorables dividido por casos posibles.\n\n"
        "1) Casos favorables: las bolitas verdes son 4.\n"
        "2) Casos posibles: el total de bolitas, sumando ambos colores: "
        "4 + 6 = 10.\n"
        "3) La probabilidad es 4/10, que simplificado por 2 da 2/5.\n\n"
        "El denominador siempre es el total de bolitas en la bolsa, nunca "
        "solo la cantidad del otro color.",
        [
            ("6/10", "Calculó la probabilidad de sacar una bolita amarilla en lugar de una verde."),
            ("4/6", "Comparó la cantidad de bolitas verdes con la de amarillas, en lugar de con el total de bolitas en la bolsa."),
            ("1/2", "Asumió que había la misma cantidad de bolitas de cada color, sin considerar los valores reales del enunciado."),
        ],
    ),
    _q(
        "prob_reglas", "medio",
        "Al lanzar un dado de 6 caras, ¿cuál es la probabilidad de obtener un número par o un 5?",
        "2/3",
        "Cuando el evento tiene dos condiciones unidas por \"o\", se cuentan "
        "todos los casos que cumplen al menos una de las dos.\n\n"
        "1) Los números pares del dado son 2, 4 y 6: eso son 3 casos.\n"
        "2) El 5 no es par, así que se suma como un caso adicional: 1 caso "
        "más.\n"
        "3) En total hay 3 + 1 = 4 casos favorables de 6 posibles: 4/6.\n"
        "4) Simplifica dividiendo por 2: 2/3.\n\n"
        "Es clave no contar el 5 dos veces ni confundirlo con un número par: "
        "son dos grupos de casos que no se superponen.",
        [
            ("1/2", "Contó solo los números pares (3 de 6) sin sumar el caso adicional del 5."),
            ("5/6", "Contó erróneamente 5 casos favorables, incluyendo por error algún número que no cumple ninguna de las dos condiciones."),
            ("1", "Asumió que el evento cubre todos los resultados posibles del dado."),
        ],
    ),
    # ---------- AMPLIACIÓN (segundo lote, 45 preguntas) ----------
    # ---------- NÚMEROS ----------
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 2/5 × 3/7?",
        "6/35",
        "Para multiplicar fracciones se multiplican los numeradores entre sí y los "
        "denominadores entre sí, sin necesidad de buscar un denominador común.\n\n"
        "1) Multiplica los numeradores: 2 × 3 = 6.\n"
        "2) Multiplica los denominadores: 5 × 7 = 35.\n"
        "3) El resultado es 6/35, que no se puede simplificar porque 6 y 35 no "
        "comparten factores en común.",
        [
            ("5/12", "Sumó los numeradores y los denominadores por separado (2+3 y 5+7), en lugar de multiplicarlos."),
            ("14/15", "Invirtió la segunda fracción como si fuera una división, en lugar de multiplicar directamente."),
            ("6/12", "Multiplicó los numeradores correctamente, pero sumó los denominadores (5+7) en lugar de multiplicarlos."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de 5/6 − 1/3?",
        "1/2",
        "Para restar fracciones necesitas el mismo denominador en ambas.\n\n"
        "1) El mínimo común múltiplo de 6 y 3 es 6, así que solo hay que convertir "
        "1/3: como 6 ÷ 3 = 2, multiplicas arriba y abajo por 2, y 1/3 = 2/6.\n"
        "2) Resta los numeradores manteniendo el denominador: 5/6 − 2/6 = 3/6.\n"
        "3) Simplifica dividiendo ambos por 3: 3/6 = 1/2.",
        [
            ("4/3", "Restó los numeradores entre sí y los denominadores entre sí, sin buscar un denominador común."),
            ("7/6", "Sumó las fracciones en lugar de restarlas."),
            ("2/3", "No convirtió 1/3 a sextos antes de restar: usó 1/6 en su lugar."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "¿Cuál es el resultado de 2 − 3/4 × 2/3?",
        "3/2",
        "El orden de las operaciones exige resolver primero la multiplicación y "
        "recién después la resta.\n\n"
        "1) Multiplica primero: 3/4 × 2/3 = 6/12 = 1/2.\n"
        "2) Ahora resta ese resultado de 2: 2 − 1/2.\n"
        "3) Escribe el 2 como 4/2 para restar: 4/2 − 1/2 = 3/2.\n\n"
        "Resolver la resta antes que la multiplicación cambia por completo el "
        "resultado, porque la multiplicación tiene prioridad.",
        [
            ("5/6", "Restó primero (2 − 3/4 = 5/4) y multiplicó después por 2/3, sin respetar que la multiplicación va primero."),
            ("1/2", "Calculó solo la multiplicación (3/4 × 2/3) y olvidó restarla de 2."),
            ("7/12", "Restó ambas fracciones de 2 por separado (2 − 3/4 − 2/3), en lugar de multiplicarlas primero y restar solo el resultado."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de 2⁴?",
        "16",
        "Una potencia indica cuántas veces se multiplica la base por sí misma.\n\n"
        "1) El exponente 4 dice que el 2 se multiplica por sí mismo cuatro veces: "
        "2 × 2 × 2 × 2.\n"
        "2) Multiplica de a pares: 2 × 2 = 4, y 4 × 2 = 8, y 8 × 2 = 16.\n\n"
        "No se debe confundir con multiplicar la base por el exponente (2 × 4 = 8): "
        "una potencia es una multiplicación repetida, no una multiplicación simple.",
        [
            ("8", "Sumó la base consigo misma 4 veces (2+2+2+2) en lugar de multiplicarla por sí misma 4 veces."),
            ("32", "Multiplicó la base una vez de más, usando 5 factores en lugar de 4."),
            ("1/16", "Calculó 2⁻⁴ (el recíproco) en lugar de 2⁴."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de √50 en su forma más simple?",
        "5√2",
        "Para simplificar una raíz no exacta, se busca el mayor factor cuadrado "
        "perfecto que la divida.\n\n"
        "1) Descompón 50 buscando un factor que sea cuadrado perfecto: 50 = 25 × 2, "
        "y 25 es cuadrado perfecto (5²).\n"
        "2) Separa la raíz del producto: √50 = √25 × √2.\n"
        "3) Calcula la raíz del factor cuadrado perfecto: √25 = 5.\n"
        "4) El resultado queda como 5√2, porque √2 no se puede simplificar más.",
        [
            ("25√2", "Factorizó 50 como 25×2 pero no calculó la raíz de 25, dejándolo fuera de la raíz sin simplificar."),
            ("10√5", "Buscó un factor distinto de 25 (usó 10×5), que no es un cuadrado perfecto y no simplifica correctamente la raíz."),
            ("≈7,1", "Dio una aproximación decimal de la raíz en lugar de su forma exacta simplificada."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de (3²)³?",
        "729",
        "Al elevar una potencia a otro exponente, se multiplican los exponentes.\n\n"
        "1) Aplica la regla de potencia de una potencia: (3²)³ = 3^(2×3) = 3⁶.\n"
        "2) Calcula 3⁶ multiplicando seis veces: 3×3=9, 9×3=27, 27×3=81, 81×3=243, "
        "243×3=729.\n\n"
        "Es fácil confundirse y sumar los exponentes en lugar de multiplicarlos: esa "
        "regla (sumar) es para multiplicar potencias de igual base, no para una "
        "potencia elevada a otra.",
        [
            ("243", "Sumó los exponentes (2+3=5) en lugar de multiplicarlos, obteniendo 3⁵."),
            ("9", "Calculó solo 3² y olvidó aplicar el exponente exterior (elevar al cubo)."),
            ("216", "Multiplicó la base por el exponente interior (3×2=6) antes de elevar al cubo, en lugar de multiplicar los exponentes."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "¿A cuánto equivale el 20% de 150?",
        "30",
        "Calcular un porcentaje es multiplicar el número por el porcentaje escrito "
        "como decimal.\n\n"
        "1) Convierte 20% a decimal dividiendo por 100: 20% = 0,20.\n"
        "2) Multiplica: 150 × 0,20 = 30.",
        [
            ("130", "Restó 20 directamente de 150 en lugar de calcular el 20% de 150."),
            ("7,5", "Dividió 150 entre 20 en lugar de multiplicarlo por 0,20."),
            ("3", "Usó 2% en lugar de 20% al convertir el porcentaje a decimal (error de coma decimal)."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "Un producto cuesta $8.000 y tiene un descuento del 25%. ¿Cuál es su precio final?",
        "$6.000",
        "Primero se calcula el monto del descuento y luego se resta del precio "
        "original.\n\n"
        "1) Calcula el 25% de $8.000: 8.000 × 0,25 = $2.000.\n"
        "2) Resta ese descuento del precio original: 8.000 − 2.000 = $6.000.",
        [
            ("$2.000", "Calculó el monto del descuento pero no lo restó del precio original."),
            ("$6.400", "Calculó un 20% de descuento en lugar del 25% indicado en el enunciado."),
            ("$10.000", "Sumó el descuento al precio original en lugar de restarlo."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "Un pantalón cuesta $12.000 después de un descuento del 20%. ¿Cuál era su precio original?",
        "$15.000",
        "El precio con descuento equivale al 80% del precio original, así que hay "
        "que deshacer ese porcentaje para encontrar el 100%.\n\n"
        "1) Si hubo un 20% de descuento, lo que queda es el 80% del precio "
        "original: precio_original × 0,8 = 12.000.\n"
        "2) Despeja dividiendo: precio_original = 12.000 ÷ 0,8 = $15.000.\n\n"
        "Verifica: el 20% de $15.000 es $3.000, y 15.000 − 3.000 = $12.000. "
        "Coincide con el enunciado.",
        [
            ("$14.400", "Sumó un 20% al precio con descuento (12.000×1,2) en lugar de deshacer el descuento para encontrar el precio original."),
            ("$9.600", "Volvió a aplicar el 20% de descuento sobre 12.000, en lugar de calcular el precio original."),
            ("$16.000", "Dividió por 0,75 en lugar de por 0,8, confundiendo el 20% de descuento con un 25%."),
        ],
    ),
    # ---------- ÁLGEBRA ----------
    _q(
        "alg_expresiones", "facil",
        "Reduce la expresión: 5x + 3y − 2x + y",
        "3x + 4y",
        "Se agrupan y combinan los términos semejantes: los que tienen x entre sí, y "
        "los que tienen y entre sí.\n\n"
        "1) Combina los términos en x: 5x − 2x = 3x.\n"
        "2) Combina los términos en y: 3y + y = 4y. El término \"y\" solo tiene "
        "coeficiente 1, aunque no se escriba.\n"
        "3) El resultado final es 3x + 4y.",
        [
            ("3x + 3y", "No consideró el coeficiente 1 del término y aislado al sumarlo con 3y."),
            ("7x + 4y", "Sumó los términos en x en lugar de restarlos, ignorando el signo negativo de 2x."),
            ("3xy", "Combinó los términos en x y en y como si fueran semejantes, cuando no lo son."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "Factoriza la expresión: 6x² + 9x",
        "3x(2x + 3)",
        "Se busca el máximo factor común de ambos términos, tanto en los "
        "coeficientes como en la parte literal.\n\n"
        "1) El máximo común divisor de 6 y 9 es 3.\n"
        "2) Ambos términos tienen al menos una x, así que el factor común "
        "completo es 3x.\n"
        "3) Divide cada término por 3x: 6x² ÷ 3x = 2x, y 9x ÷ 3x = 3.\n"
        "4) El resultado factorizado es 3x(2x + 3).\n\n"
        "Verifica expandiendo: 3x × 2x = 6x², y 3x × 3 = 9x. Coincide con la "
        "expresión original.",
        [
            ("3(2x² + 3x)", "Sacó como factor común solo el 3, sin incluir la x que también es común a ambos términos."),
            ("x(6x + 9)", "Sacó como factor común solo la x, sin incluir el 3 que también es común a ambos términos."),
            ("3x(2x + 9)", "Sacó correctamente el factor común 3x, pero al dividir 9x ÷ 3x cometió un error y dejó 9 en lugar de 3."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "Simplifica la expresión (x² − 4)/(x − 2), para x ≠ 2",
        "x + 2",
        "El numerador es una diferencia de cuadrados que se puede factorizar y "
        "cancelar con el denominador.\n\n"
        "1) Factoriza x² − 4 como (x + 2)(x − 2).\n"
        "2) La expresión queda [(x + 2)(x − 2)] / (x − 2).\n"
        "3) Como x ≠ 2, el factor (x − 2) no es cero y se puede cancelar arriba y "
        "abajo, dejando solo x + 2.",
        [
            ("x − 2", "Canceló mal los factores, quedándose con el denominador en lugar del factor que realmente se simplifica."),
            ("x² − 2", "Restó el denominador del numerador en lugar de factorizar y cancelar."),
            ("x + 4", "Sumó ambos términos independientes con el mismo signo (2 y 2), en lugar de reconocer que provienen de signos opuestos (x+2)(x−2)."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "Resuelve: x/3 + 2 = 7",
        "15",
        "Se despeja x deshaciendo las operaciones en orden inverso.\n\n"
        "1) Resta 2 a ambos lados: x/3 = 5.\n"
        "2) Multiplica ambos lados por 3: x = 15.\n\n"
        "Verifica: 15/3 + 2 = 5 + 2 = 7. Coincide con la ecuación original.",
        [
            ("21", "Multiplicó 7 por 3 sin restar primero el 2, saltándose el primer paso del despeje."),
            ("5", "Encontró que x/3 = 5 pero no multiplicó por 3 para terminar de despejar x."),
            ("27", "Sumó 2 en lugar de restarlo al despejar el término independiente."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "Resuelve la inecuación: 3(x − 1) ≤ 2x + 4",
        "x ≤ 7",
        "Primero se distribuye el paréntesis y luego se despeja x como en una "
        "ecuación normal.\n\n"
        "1) Distribuye el 3: 3x − 3 ≤ 2x + 4.\n"
        "2) Pasa los términos en x a un lado y los números al otro: "
        "3x − 2x ≤ 4 + 3.\n"
        "3) Queda x ≤ 7.\n\n"
        "Como no se dividió por ningún número negativo, el sentido de la "
        "desigualdad no cambia en ningún paso.",
        [
            ("x ≥ 7", "Invirtió el sentido de la desigualdad sin haber multiplicado ni dividido por un número negativo."),
            ("x ≤ 5", "No distribuyó el 3 en el paréntesis: multiplicó por x pero no por el −1 dentro de él."),
            ("x ≤ 1", "Al mover el −3 al otro lado de la desigualdad, no le cambió el signo correctamente."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "El triple de un número, disminuido en 7, es igual al doble del mismo número aumentado en 5. "
        "¿Cuál es el número?",
        "12",
        "Primero se traduce el enunciado a una ecuación y luego se despeja.\n\n"
        "1) Llama x al número. \"El triple disminuido en 7\" es 3x − 7. \"El doble "
        "aumentado en 5\" es 2x + 5. El enunciado dice que son iguales: "
        "3x − 7 = 2x + 5.\n"
        "2) Pasa los términos en x a un lado y los números al otro: "
        "3x − 2x = 5 + 7.\n"
        "3) Queda x = 12.\n\n"
        "Verifica: el triple de 12 disminuido en 7 es 36 − 7 = 29. El doble de 12 "
        "aumentado en 5 es 24 + 5 = 29. Ambos coinciden.",
        [
            ("2", "Interpretó 'aumentado en 5' como una resta en lugar de una suma al plantear la ecuación."),
            ("−2", "Interpretó 'disminuido en 7' como una suma en lugar de una resta al plantear la ecuación."),
            ("−12", "Al pasar los términos independientes de lado, no cambió correctamente sus signos, obteniendo el opuesto del valor correcto."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "Resuelve el sistema: y = x + 2 ; y = 3x − 4",
        "x = 3, y = 5",
        "Como ambas ecuaciones ya están despejadas en función de y, se pueden "
        "igualar directamente (método de sustitución).\n\n"
        "1) Iguala las dos expresiones de y: x + 2 = 3x − 4.\n"
        "2) Agrupa los términos en x de un lado y los números del otro: "
        "2 + 4 = 3x − x, es decir 6 = 2x.\n"
        "3) Despeja: x = 3.\n"
        "4) Reemplaza en cualquiera de las ecuaciones: y = 3 + 2 = 5.\n\n"
        "Verifica en la otra ecuación: y = 3(3) − 4 = 9 − 4 = 5. Coincide.",
        [
            ("x = 3, y = 13", "Encontró correctamente x=3, pero al calcular y cambió el signo del término independiente (usó +4 en lugar de −4)."),
            ("x = 2, y = 4", "Llegó correctamente a 2x = 6, pero dividió por 3 en lugar de por 2 al despejar x."),
            ("x = 5, y = 3", "Encontró los valores correctos pero los intercambió entre las variables."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "Resuelve el sistema: 2x + y = 11 ; x + y = 7",
        "x = 4, y = 3",
        "Conviene el método de reducción, restando una ecuación de la otra para "
        "eliminar y.\n\n"
        "1) Resta la segunda ecuación de la primera: (2x + y) − (x + y) = 11 − 7, "
        "lo que da x = 4.\n"
        "2) Reemplaza x = 4 en la segunda ecuación: 4 + y = 7, entonces y = 3.\n\n"
        "Verifica en la primera ecuación: 2(4) + 3 = 8 + 3 = 11. Coincide.",
        [
            ("x = 4, y = 7", "Sustituyó x=4 en la primera ecuación pero olvidó el coeficiente 2 (usó x+y=11 en lugar de 2x+y=11), obteniendo y=7."),
            ("x = 3, y = 4", "Encontró los valores correctos pero los intercambió entre las variables."),
            ("x = 4, y = 11", "Sustituyó x=4 en la ecuación pero no completó el despeje de y, dejando el valor de la constante sin restarle 2x."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "La suma de dos números es 18. El primero es el doble del segundo. "
        "¿Cuáles son los números (el primero y el segundo)?",
        "12 y 6",
        "Se traduce el enunciado a un sistema de ecuaciones y se resuelve por "
        "sustitución.\n\n"
        "1) Llama a al primer número y b al segundo. El enunciado dice a + b = 18 "
        "y a = 2b.\n"
        "2) Sustituye a = 2b en la primera ecuación: 2b + b = 18, o sea 3b = 18.\n"
        "3) Despeja: b = 6.\n"
        "4) Calcula a: a = 2 × 6 = 12.\n\n"
        "Verifica: 12 + 6 = 18 y 12 es el doble de 6. Ambas condiciones se cumplen.",
        [
            ("6 y 12", "Intercambió cuál número es el primero y cuál el segundo."),
            ("9 y 9", "Repartió el total en partes iguales, sin usar la condición de que el primero es el doble del segundo."),
            ("10 y 8", "Interpretó 'el doble del segundo' como 'el segundo más 2', en lugar de multiplicarlo por 2."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "Resuelve: x² = 49",
        "x = 7 y x = −7",
        "Al extraer la raíz cuadrada de ambos lados hay que considerar las dos "
        "soluciones posibles.\n\n"
        "1) Extrae raíz cuadrada a ambos lados de x² = 49.\n"
        "2) Tanto 7 como −7 elevados al cuadrado dan 49, así que ambos son "
        "solución: x = 7 y x = −7.",
        [
            ("x = 24,5", "Dividió 49 por 2 en lugar de calcular su raíz cuadrada."),
            ("x = 7", "Solo consideró la raíz positiva, olvidando que x = −7 también es solución."),
            ("x = 2401", "Elevó 49 al cuadrado en lugar de calcular su raíz cuadrada."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "Resuelve: x² + 2x − 15 = 0",
        "x = −5 y x = 3",
        "Se factoriza buscando dos números que sumados den 2 y multiplicados den "
        "−15.\n\n"
        "1) Busca los dos números: 5 y −3 cumplen, porque 5 + (−3) = 2 y "
        "5 × (−3) = −15.\n"
        "2) La factorización queda (x + 5)(x − 3) = 0.\n"
        "3) Cada factor puede ser cero: x + 5 = 0 da x = −5, y x − 3 = 0 da x = 3.",
        [
            ("x = 5 y x = −3", "Invirtió los signos de las soluciones al despejar cada factor."),
            ("x = −5 y x = −3", "Usó el mismo signo para ambas soluciones, sin notar que su producto debe ser negativo (−15)."),
            ("x = 15 y x = −1", "Eligió un par de números cuyo producto es −15 pero cuya suma no es 2 (no verificó ambas condiciones)."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Resuelve usando la fórmula general: x² − 4x − 5 = 0",
        "x = 5 y x = −1",
        "Se aplica la fórmula general x = (−b ± √(b² − 4ac)) / 2a con a=1, b=−4, "
        "c=−5.\n\n"
        "1) Calcula el discriminante: b² − 4ac = (−4)² − 4(1)(−5) = 16 + 20 = 36.\n"
        "2) Calcula su raíz: √36 = 6.\n"
        "3) Aplica la fórmula: x = (−(−4) ± 6) / 2(1) = (4 ± 6) / 2.\n"
        "4) Las dos soluciones son (4 + 6)/2 = 5 y (4 − 6)/2 = −1.",
        [
            ("x = 10 y x = −2", "Calculó correctamente el discriminante y (4±6), pero olvidó dividir por 2a al final."),
            ("x = 1 y x = −5", "Usó −b = −4 en lugar de −b = 4 (el opuesto de b=−4), invirtiendo el signo en la fórmula."),
            ("x = 5", "Calculó solo la raíz con el signo positivo del discriminante y no consideró la solución con signo negativo."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿Cuál es la pendiente de la recta que pasa por los puntos (1, 2) y (3, 8)?",
        "3",
        "La pendiente es el cambio en y dividido por el cambio en x entre dos "
        "puntos.\n\n"
        "1) Calcula el cambio en y: 8 − 2 = 6.\n"
        "2) Calcula el cambio en x: 3 − 1 = 2.\n"
        "3) Divide: 6 / 2 = 3.",
        [
            ("6", "Calculó solo la diferencia de las coordenadas y (8−2=6) y no la dividió por la diferencia de las coordenadas x."),
            ("1/3", "Calculó el cociente invertido (Δx/Δy) en lugar de la pendiente correcta (Δy/Δx)."),
            ("−3", "Restó las coordenadas y en el orden correcto pero usó el orden opuesto para las coordenadas x, invirtiendo el signo del resultado."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es el vértice de la parábola y = x² − 6x + 5?",
        "(3, −4)",
        "La coordenada x del vértice se calcula con −b/2a, y luego se reemplaza en "
        "la función para obtener y.\n\n"
        "1) Identifica los coeficientes: a=1, b=−6, c=5.\n"
        "2) Calcula la coordenada x: −b/2a = −(−6)/2(1) = 6/2 = 3.\n"
        "3) Reemplaza x=3 en la función: y = 3² − 6(3) + 5 = 9 − 18 + 5 = −4.\n"
        "4) El vértice es (3, −4).",
        [
            ("(6, 5)", "Usó los valores de b y c directamente como coordenadas del vértice, sin aplicar la fórmula −b/2a."),
            ("(−3, 32)", "Cometió un error de signo al calcular la coordenada x del vértice, y evaluó la función en ese punto equivocado."),
            ("(3, 4)", "Calculó correctamente la coordenada x del vértice, pero cometió un error de signo al evaluar y en ese punto."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es la imagen (el valor de y) de f(x) = 2x² − 3 cuando x = −2?",
        "5",
        "Se reemplaza x por −2 y se sigue el orden de operaciones: primero la "
        "potencia, luego la multiplicación y al final la resta.\n\n"
        "1) Eleva al cuadrado primero: (−2)² = 4.\n"
        "2) Multiplica por 2: 2 × 4 = 8.\n"
        "3) Resta 3: 8 − 3 = 5.",
        [
            ("−11", "Calculó (−2)² como −4 en lugar de 4, olvidando que el cuadrado de un número negativo es positivo."),
            ("1", "Olvidó multiplicar por 2 antes de restar 3: solo elevó al cuadrado y restó."),
            ("13", "Multiplicó 2 por x antes de elevar al cuadrado (2×(−2))², en lugar de elevar x al cuadrado primero y luego multiplicar por 2."),
        ],
    ),
    # ---------- GEOMETRÍA ----------
    _q(
        "geo_plana", "facil",
        "¿Cuál es el área de un triángulo de base 10 cm y altura 6 cm?",
        "30 cm²",
        "El área de un triángulo es base por altura, dividido por 2.\n\n"
        "1) Multiplica base por altura: 10 × 6 = 60.\n"
        "2) Divide por 2: 60 / 2 = 30 cm².",
        [
            ("60 cm²", "Multiplicó base por altura pero olvidó dividir por 2, calculando el área como si fuera un rectángulo."),
            ("16 cm²", "Sumó la base y la altura (10+6) en lugar de multiplicarlas."),
            ("8 cm²", "Promedió la base y la altura en lugar de aplicar la fórmula del área de un triángulo."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Un rectángulo tiene un área de 48 cm² y su base mide 8 cm. ¿Cuánto mide su altura?",
        "6 cm",
        "El área de un rectángulo es base por altura, así que la altura se "
        "despeja dividiendo el área por la base.\n\n"
        "1) Área = base × altura, entonces altura = área / base.\n"
        "2) Reemplaza: 48 / 8 = 6 cm.",
        [
            ("40 cm", "Restó la base del área (48−8) en lugar de dividir el área por la base."),
            ("384 cm", "Multiplicó el área por la base (48×8) en lugar de dividirla."),
            ("16 cm", "Dividió el área por 3 en lugar de por 8, usando un valor equivocado para la base."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Un terreno rectangular tiene un perímetro de 60 m. Si el largo mide el doble que el ancho, "
        "¿cuál es el área del terreno?",
        "200 m²",
        "Se plantea el perímetro en función del ancho y se despeja, para luego "
        "calcular el área.\n\n"
        "1) Llama a al ancho; el largo es 2a. El perímetro es 2(a + 2a) = 6a.\n"
        "2) Iguala al perímetro dado: 6a = 60, entonces a = 10 m (ancho).\n"
        "3) El largo es 2 × 10 = 20 m.\n"
        "4) El área es ancho × largo: 10 × 20 = 200 m².",
        [
            ("225 m²", "Calculó el lado asumiendo que el terreno es un cuadrado (60÷4=15), sin usar la condición de que el largo es el doble del ancho."),
            ("100 m²", "Calculó correctamente que el ancho mide 10 m, pero no aplicó la condición de que el largo es el doble, asumiendo un cuadrado de 10×10."),
            ("30 m²", "Sumó el largo y el ancho (10+20) en lugar de multiplicarlos para obtener el área."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "Un triángulo rectángulo tiene catetos de 6 cm y 8 cm. ¿Cuánto mide su hipotenusa?",
        "10 cm",
        "El teorema de Pitágoras dice que el cuadrado de la hipotenusa es igual a "
        "la suma de los cuadrados de los catetos.\n\n"
        "1) Eleva al cuadrado los catetos: 6² = 36 y 8² = 64.\n"
        "2) Súmalos: 36 + 64 = 100.\n"
        "3) Extrae la raíz cuadrada: √100 = 10 cm.",
        [
            ("14 cm", "Sumó los catetos directamente (6+8) en lugar de aplicar el teorema de Pitágoras."),
            ("48 cm", "Multiplicó los catetos entre sí, calculando el área del triángulo en lugar de la hipotenusa."),
            ("100 cm", "Sumó los cuadrados de los catetos correctamente (36+64=100), pero olvidó calcular la raíz cuadrada."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "Un triángulo rectángulo tiene hipotenusa de 13 cm y un cateto de 5 cm. "
        "¿Cuánto mide el otro cateto?",
        "12 cm",
        "Cuando se conoce la hipotenusa y un cateto, el teorema de Pitágoras se "
        "despeja restando en lugar de sumando.\n\n"
        "1) Eleva al cuadrado la hipotenusa y el cateto conocido: 13² = 169 y "
        "5² = 25.\n"
        "2) Resta: 169 − 25 = 144.\n"
        "3) Extrae la raíz cuadrada: √144 = 12 cm.",
        [
            ("18 cm", "Sumó la hipotenusa y el cateto conocido directamente (13+5), en lugar de aplicar el teorema de Pitágoras."),
            ("8 cm", "Restó el cateto conocido de la hipotenusa directamente (13−5), en lugar de restar sus cuadrados y luego calcular la raíz."),
            ("≈13,9 cm", "Sumó los cuadrados de la hipotenusa y el cateto conocido (169+25), en lugar de restarlos."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "Una escalera de 10 m se apoya en una pared vertical. Si la base de la escalera está a 6 m "
        "de la pared, ¿a qué altura de la pared llega la escalera?",
        "8 m",
        "La escalera es la hipotenusa de un triángulo rectángulo, la distancia a "
        "la pared es un cateto y la altura buscada es el otro cateto.\n\n"
        "1) Eleva al cuadrado la escalera y la distancia a la pared: 10² = 100 y "
        "6² = 36.\n"
        "2) Resta para obtener el cateto que falta: 100 − 36 = 64.\n"
        "3) Extrae la raíz cuadrada: √64 = 8 m.",
        [
            ("4 m", "Restó directamente la base de la longitud de la escalera (10−6), en lugar de aplicar el teorema de Pitágoras."),
            ("16 m", "Sumó la longitud de la escalera y la distancia a la pared (10+6), en lugar de tratarlas como hipotenusa y cateto."),
            ("64 m", "Calculó correctamente 10² − 6² = 64, pero olvidó calcular la raíz cuadrada para obtener la altura."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "¿Cuáles son las coordenadas del punto (3, 5) al reflejarlo respecto del eje X?",
        "(3, −5)",
        "Al reflejar un punto respecto del eje X, la coordenada x no cambia y la "
        "coordenada y cambia de signo.\n\n"
        "1) La coordenada x se mantiene: 3.\n"
        "2) La coordenada y cambia de signo: 5 pasa a −5.\n"
        "3) El punto reflejado es (3, −5).",
        [
            ("(−3, 5)", "Reflejó el punto respecto del eje Y en lugar del eje X, cambiando el signo de la coordenada x en lugar de la y."),
            ("(−3, −5)", "Reflejó el punto respecto del origen, cambiando el signo de ambas coordenadas, en lugar de reflejarlo solo respecto del eje X."),
            ("(5, 3)", "Intercambió las coordenadas x e y del punto, en lugar de aplicar la reflexión respecto del eje X."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "Se traslada el punto (2, −3) según el vector (4, 1). ¿Cuáles son las coordenadas del punto "
        "trasladado?",
        "(6, −2)",
        "Trasladar un punto según un vector significa sumar las componentes del "
        "vector a las coordenadas del punto.\n\n"
        "1) Suma la primera componente del vector a la coordenada x: 2 + 4 = 6.\n"
        "2) Suma la segunda componente a la coordenada y: −3 + 1 = −2.\n"
        "3) El punto trasladado es (6, −2).",
        [
            ("(−2, −4)", "Restó las componentes del vector de traslación en lugar de sumarlas a las coordenadas originales."),
            ("(3, 1)", "Intercambió las componentes del vector de traslación, usando (1, 4) en lugar de (4, 1)."),
            ("(8, −3)", "Multiplicó la coordenada x por la primera componente del vector en lugar de sumarla, y no modificó la coordenada y."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "Un cuadrado tiene un vértice en (4, 0). Si se rota 90° en torno al origen, en sentido "
        "antihorario, ¿en qué punto queda ese vértice?",
        "(0, 4)",
        "Una rotación de 90° antihoraria en torno al origen transforma cada punto "
        "(x, y) en (−y, x).\n\n"
        "1) Identifica las coordenadas originales: x = 4, y = 0.\n"
        "2) Aplica la regla: el nuevo punto es (−y, x) = (−0, 4) = (0, 4).",
        [
            ("(4, 0)", "No aplicó la rotación: dejó el punto en su posición original."),
            ("(0, −4)", "Aplicó la regla de rotación en sentido horario (y, −x) en lugar de antihorario, invirtiendo el signo del resultado."),
            ("(−4, 0)", "Calculó la posición del punto tras una rotación de 180° en lugar de 90°."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "¿Cuál es el volumen de un cubo de arista 4 cm?",
        "64 cm³",
        "El volumen de un cubo es la arista elevada al cubo, porque tiene tres "
        "dimensiones iguales.\n\n"
        "1) Eleva la arista al cubo: 4³ = 4 × 4 × 4.\n"
        "2) Calcula: 4 × 4 = 16, y 16 × 4 = 64 cm³.",
        [
            ("16 cm³", "Calculó el área de una cara del cubo (4²) en lugar de su volumen (4³)."),
            ("12 cm³", "Multiplicó la arista por 3 (el número de dimensiones) en lugar de elevarla al cubo."),
            ("8 cm³", "Multiplicó la arista por 2 en lugar de elevarla al cubo."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "¿Cuántas caras tiene un prisma de base triangular?",
        "5",
        "Un prisma de base triangular tiene dos bases triangulares (iguales y "
        "paralelas) y tres caras laterales rectangulares, una por cada lado del "
        "triángulo.\n\n"
        "1) Cuenta las bases: 2 caras triangulares.\n"
        "2) Cuenta las caras laterales: 3 caras rectangulares, una por cada lado "
        "del triángulo de la base.\n"
        "3) Suma: 2 + 3 = 5 caras en total.",
        [
            ("3", "Contó solo las caras laterales (rectangulares), sin incluir las dos bases triangulares."),
            ("6", "Confundió este sólido con un prisma de base cuadrada, que sí tiene 6 caras."),
            ("4", "Contó una sola base triangular y las tres caras laterales, olvidando la segunda base."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "Un cilindro tiene radio 3 cm y altura 10 cm. ¿Cuál es su volumen? (usa π ≈ 3,14)",
        "282,6 cm³",
        "El volumen de un cilindro es el área de su base circular multiplicada "
        "por la altura.\n\n"
        "1) Calcula el área de la base: π × r² = 3,14 × 3² = 3,14 × 9 = 28,26 cm².\n"
        "2) Multiplica por la altura: 28,26 × 10 = 282,6 cm³.",
        [
            ("94,2 cm³", "No elevó el radio al cuadrado: multiplicó π por el radio (sin elevarlo) y por la altura."),
            ("188,4 cm³", "Calculó el área lateral del cilindro (2πrh) en lugar de su volumen (πr²h)."),
            ("1130,4 cm³", "Usó el diámetro (6 cm) en lugar del radio en la fórmula, elevándolo al cuadrado por error."),
        ],
    ),
    # ---------- PROBABILIDAD ----------
    _q(
        "prob_estadistica_desc", "facil",
        "¿Cuál es la moda del conjunto de datos: 4, 7, 4, 9, 4, 2?",
        "4",
        "La moda es el valor que más veces se repite en el conjunto, sin "
        "necesidad de ordenar los datos.\n\n"
        "1) Cuenta cuántas veces aparece cada valor: el 4 aparece 3 veces, y los "
        "demás (7, 9, 2) aparecen solo una vez cada uno.\n"
        "2) El valor que más se repite es 4, así que esa es la moda.",
        [
            ("9", "Identificó el valor máximo del conjunto en lugar de el que más se repite."),
            ("5", "Calculó la media (promedio) del conjunto en lugar de identificar la moda."),
            ("3", "Entregó la cantidad de veces que se repite el valor más frecuente, en lugar del valor mismo."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "medio",
        "Las notas de un curso en una prueba son: 5,5 − 6,0 − 4,5 − 5,5 − 7,0 − 5,5 − 6,0. "
        "¿Cuál es la moda?",
        "5,5",
        "Se cuenta cuántas veces aparece cada nota distinta.\n\n"
        "1) El 5,5 aparece 3 veces.\n"
        "2) El 6,0 aparece 2 veces.\n"
        "3) El 4,5 y el 7,0 aparecen solo 1 vez cada uno.\n"
        "4) El valor que más se repite es 5,5, así que esa es la moda del curso.",
        [
            ("6,0", "Identificó un valor que se repite, pero no el que más veces aparece: 5,5 se repite 3 veces, más que 6,0."),
            ("5,71", "Calculó el promedio del curso en lugar de identificar la nota que más se repite."),
            ("7,0", "Identificó la nota máxima del curso en lugar de la que más se repite."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "dificil",
        "Un conjunto de 5 datos tiene media 8. Si cuatro de los datos son 6, 7, 9 y 10, "
        "¿cuál es el quinto dato?",
        "8",
        "Si la media de 5 datos es 8, la suma total de esos 5 datos debe ser "
        "8 × 5.\n\n"
        "1) Calcula la suma total necesaria: 8 × 5 = 40.\n"
        "2) Suma los cuatro datos conocidos: 6 + 7 + 9 + 10 = 32.\n"
        "3) El quinto dato es la diferencia: 40 − 32 = 8.",
        [
            ("40", "Calculó la suma total necesaria (8×5=40) pero no la usó para despejar el quinto dato: la entregó como si fuera la respuesta."),
            ("6,4", "Dividió la suma de los cuatro datos conocidos por la cantidad total de datos (32÷5), en lugar de restarla de la suma total necesaria."),
            ("32", "Calculó la suma de los cuatro datos conocidos pero no continuó el cálculo para encontrar el quinto dato."),
        ],
    ),
    _q(
        "prob_combinatoria", "facil",
        "Un local vende helados con 3 sabores y 2 tipos de cono. ¿Cuántas combinaciones distintas de "
        "sabor y cono se pueden formar?",
        "6",
        "Cuando dos elecciones son independientes, el total de combinaciones es "
        "el producto de las opciones de cada una (principio multiplicativo).\n\n"
        "1) Hay 3 sabores posibles.\n"
        "2) Por cada sabor, hay 2 tipos de cono posibles.\n"
        "3) Multiplica: 3 × 2 = 6 combinaciones distintas.",
        [
            ("5", "Sumó la cantidad de sabores y tipos de cono (3+2), en lugar de multiplicarlas."),
            ("3", "Consideró solo la cantidad de sabores disponibles, sin tomar en cuenta los tipos de cono."),
            ("9", "Calculó 3² en lugar de multiplicar la cantidad de sabores por la cantidad de tipos de cono."),
        ],
    ),
    _q(
        "prob_combinatoria", "medio",
        "¿De cuántas formas distintas se pueden ordenar las letras de la palabra \"AMOR\" "
        "(todas sus letras son distintas)?",
        "24",
        "Como se usan las 4 letras y el orden importa, se trata de una "
        "permutación de las 4, que se calcula con el factorial.\n\n"
        "1) Para la primera posición hay 4 letras disponibles, para la segunda "
        "quedan 3, para la tercera 2 y para la última 1.\n"
        "2) Multiplica las opciones de cada paso: 4 × 3 × 2 × 1 = 24.",
        [
            ("16", "Calculó 4² (4×4) en lugar de 4! (4×3×2×1), confundiendo una potencia con un factorial."),
            ("10", "Sumó los números del 1 al 4 (4+3+2+1=10) en lugar de multiplicarlos."),
            ("4", "Entregó la cantidad de letras de la palabra, sin calcular de cuántas formas se pueden ordenar."),
        ],
    ),
    _q(
        "prob_combinatoria", "facil",
        "En una carrera de 3 personas, ¿de cuántas formas distintas pueden llegar en 1er y "
        "2do lugar (sin empates)?",
        "6",
        "Para el primer lugar hay 3 personas posibles; una vez ocupado ese "
        "lugar, quedan 2 personas posibles para el segundo.\n\n"
        "1) Opciones para el primer lugar: 3.\n"
        "2) Opciones para el segundo lugar, ya elegido el primero: 2.\n"
        "3) Multiplica: 3 × 2 = 6 formas distintas.",
        [
            ("3", "Consideró solo las opciones para el primer lugar, sin multiplicar por las opciones restantes para el segundo lugar."),
            ("9", "Multiplicó 3×3, permitiendo que la misma persona ocupe el primer y el segundo lugar a la vez."),
            ("1", "Asumió que solo existe un orden posible de llegada, sin considerar que distintas personas pueden ocupar cada lugar."),
        ],
    ),
    _q(
        "prob_reglas", "facil",
        "Se lanza una moneda dos veces. ¿Cuál es la probabilidad de obtener cara ambas veces?",
        "1/4",
        "Como los dos lanzamientos son independientes, se multiplican sus "
        "probabilidades individuales.\n\n"
        "1) La probabilidad de obtener cara en un lanzamiento es 1/2.\n"
        "2) Como son dos lanzamientos independientes, se multiplica: "
        "1/2 × 1/2 = 1/4.",
        [
            ("1/2", "Calculó la probabilidad de obtener cara en un solo lanzamiento, sin considerar que el evento pide dos lanzamientos seguidos."),
            ("1", "Asumió que el evento es seguro, sin calcular la probabilidad real de que ocurra dos veces seguidas."),
            ("3/4", "Calculó la probabilidad de obtener al menos una cara en los dos lanzamientos, en lugar de obtener cara en ambos."),
        ],
    ),
    _q(
        "prob_reglas", "medio",
        "En una bolsa hay 4 bolitas numeradas del 1 al 4. Se saca una, se observa su número y se "
        "devuelve a la bolsa; luego se saca otra. ¿Cuál es la probabilidad de que ambas bolitas "
        "sean el número 3?",
        "1/16",
        "Como la bolita se devuelve a la bolsa, las dos extracciones son "
        "independientes y se multiplican sus probabilidades.\n\n"
        "1) La probabilidad de sacar el 3 en una extracción es 1/4.\n"
        "2) Como se devuelve la bolita, la segunda extracción también tiene "
        "probabilidad 1/4 de dar el 3.\n"
        "3) Multiplica: 1/4 × 1/4 = 1/16.",
        [
            ("1/4", "Calculó la probabilidad de sacar el número 3 en una sola extracción, sin multiplicar por la segunda extracción."),
            ("1/2", "Sumó las probabilidades de cada extracción (1/4+1/4) en lugar de multiplicarlas, ya que ambos eventos deben ocurrir a la vez."),
            ("1/12", "Calculó la probabilidad como si la primera bolita no se devolviera a la bolsa, cuando el enunciado indica que sí se devuelve."),
        ],
    ),
    _q(
        "prob_reglas", "dificil",
        "En un curso, el 60% de los estudiantes practica algún deporte y, de ellos, el 25% practica "
        "natación. ¿Qué porcentaje del curso completo practica natación?",
        "15%",
        "Cuando un porcentaje se aplica sobre otro porcentaje (y no sobre el "
        "total), hay que multiplicarlos como decimales para obtener la "
        "proporción real sobre el total.\n\n"
        "1) Convierte ambos porcentajes a decimal: 60% = 0,60 y 25% = 0,25.\n"
        "2) Multiplícalos: 0,60 × 0,25 = 0,15.\n"
        "3) Convierte de vuelta a porcentaje: 0,15 = 15%.",
        [
            ("25%", "Entregó el 25% tal como aparece en el enunciado, sin considerar que ese porcentaje es solo sobre el 60% que practica deporte, no sobre el curso completo."),
            ("85%", "Sumó los dos porcentajes del enunciado (60%+25%) en lugar de multiplicarlos."),
            ("35%", "Restó los porcentajes del enunciado (60%−25%) en lugar de multiplicarlos."),
        ],
    ),
    # ==================== M2 (contenido exclusivo) ====================
    # ---------- NÚMEROS ----------
    _q(
        "num_reales", "facil",
        "Ordena de menor a mayor: √2, 1,5, 4/3",
        "4/3 < √2 < 1,5",
        "Para ordenar hay que comparar los tres valores en la misma forma "
        "(decimal es lo más simple).\n\n"
        "1) 4/3 = 1,333…\n"
        "2) √2 = 1,4142… (está entre 1,4² = 1,96 y 1,5² = 2,25, más cerca de 1,4).\n"
        "3) 1,5 ya está en forma decimal.\n"
        "4) Comparando: 1,333 < 1,414 < 1,5, es decir, 4/3 < √2 < 1,5.",
        [
            ("√2 < 4/3 < 1,5", "Subestimó el valor de √2, ubicándolo por debajo de 4/3 cuando en realidad 1,414 es mayor que 1,333."),
            ("1,5 < √2 < 4/3", "Invirtió por completo el orden de los tres valores."),
            ("4/3 < 1,5 < √2", "Sobreestimó el valor de √2, ubicándolo como el mayor de los tres cuando es menor que 1,5."),
        ],
    ),
    _q(
        "num_reales", "medio",
        "¿Cuál es el valor de |−7| + |3 − 8|?",
        "12",
        "Se resuelve cada valor absoluto por separado antes de sumar.\n\n"
        "1) |−7| = 7.\n"
        "2) Dentro del segundo valor absoluto: 3 − 8 = −5, y |−5| = 5.\n"
        "3) Suma: 7 + 5 = 12.",
        [
            ("−12", "No aplicó el valor absoluto: sumó los números directamente con su signo (−7 + (3−8) = −12)."),
            ("2", "Aplicó el valor absoluto solo al primer término, dejando el segundo con su signo original (7 + (3−8) = 2)."),
            ("18", "Calculó el valor absoluto de cada número por separado (7, 3 y 8) y los sumó, en lugar de restar primero 3−8 y recién ahí aplicar el valor absoluto."),
        ],
    ),
    _q(
        "num_reales", "dificil",
        "El área de un cuadrado es 18 cm². ¿Cuánto mide, aproximadamente, su lado?",
        "3√2 cm (≈4,24 cm)",
        "El lado de un cuadrado es la raíz cuadrada de su área.\n\n"
        "1) Lado = √18.\n"
        "2) Simplifica: 18 = 9 × 2, y 9 es cuadrado perfecto, así que "
        "√18 = √9 × √2 = 3√2.\n"
        "3) Como √2 ≈ 1,41, el lado mide aproximadamente 3 × 1,41 ≈ 4,24 cm.",
        [
            ("9 cm", "Dividió el área por 2 en lugar de calcular su raíz cuadrada."),
            ("6 cm", "Dividió el área por 3 en lugar de calcular su raíz cuadrada."),
            ("4 cm", "Aproximó a la raíz del cuadrado perfecto más cercano por debajo (√16=4) en lugar de calcular √18."),
        ],
    ),
    _q(
        "num_financiera", "facil",
        "Un banco ofrece un interés simple del 2% mensual. Si depositas $100.000, "
        "¿cuánto interés ganas en 3 meses?",
        "$6.000",
        "En interés simple, el interés de cada mes se calcula siempre sobre el "
        "capital inicial, y se suman los meses.\n\n"
        "1) Interés de un mes: 100.000 × 0,02 = $2.000.\n"
        "2) Como son 3 meses y el interés simple no se acumula sobre sí mismo: "
        "2.000 × 3 = $6.000.",
        [
            ("$2.000", "Calculó el interés de un solo mes y olvidó multiplicarlo por los 3 meses."),
            ("$106.000", "Calculó el monto final (capital + interés) en lugar de solo el interés ganado."),
            ("$6.121", "Calculó interés compuesto (aplicando el 2% sobre el saldo acumulado cada mes) en lugar de interés simple, que siempre se calcula sobre el capital inicial."),
        ],
    ),
    _q(
        "num_financiera", "medio",
        "Pides un crédito de consumo de $500.000 a pagar en 1 cuota, con un interés "
        "simple del 3% mensual a 4 meses. ¿Cuánto debes pagar en total?",
        "$560.000",
        "El total a pagar es el capital más el interés acumulado en los 4 "
        "meses.\n\n"
        "1) Interés de un mes: 500.000 × 0,03 = $15.000.\n"
        "2) Interés de los 4 meses: 15.000 × 4 = $60.000.\n"
        "3) Total a pagar: 500.000 + 60.000 = $560.000.",
        [
            ("$500.000", "Olvidó agregar el interés: pagó solo el capital original."),
            ("$60.000", "Entregó solo el interés acumulado, sin sumarlo al capital que también hay que devolver."),
            ("$515.000", "Calculó el interés de un solo mes y lo sumó al capital, sin multiplicarlo por los 4 meses del crédito."),
        ],
    ),
    _q(
        "num_financiera", "dificil",
        "Un ahorro de $200.000 gana un interés simple mensual. Después de 5 meses, "
        "el ahorro creció a $230.000. ¿Cuál es la tasa de interés mensual?",
        "3% mensual",
        "Primero se calcula el interés total ganado y luego se reparte entre "
        "los meses.\n\n"
        "1) Interés total ganado: 230.000 − 200.000 = $30.000.\n"
        "2) Ese interés se generó en 5 meses, así que el interés de un mes es "
        "30.000 ÷ 5 = $6.000.\n"
        "3) La tasa mensual es ese interés sobre el capital: "
        "6.000 ÷ 200.000 = 0,03 = 3%.",
        [
            ("15%", "Calculó la tasa de interés total del periodo completo (30.000/200.000=15%) pero no la dividió entre los 5 meses para obtener la tasa mensual."),
            ("1,5%", "Calculó correctamente que el interés total fue de 15%, pero lo dividió por 10 en lugar de por los 5 meses reales."),
            ("$30.000", "Entregó el monto de interés ganado en lugar de calcular la tasa de interés mensual que pedía el enunciado."),
        ],
    ),
    _q(
        "num_logaritmos", "facil",
        "¿Cuál es el valor de log₂(8)?",
        "3",
        "log₂(8) es la pregunta \"¿a qué exponente hay que elevar 2 para "
        "obtener 8?\".\n\n"
        "1) Prueba con exponentes de 2: 2¹=2, 2²=4, 2³=8.\n"
        "2) El exponente que da 8 es 3, así que log₂(8) = 3.",
        [
            ("4", "Calculó log₂(16) en lugar de log₂(8): 2⁴=16, no 8."),
            ("6", "Multiplicó la base por el resultado esperado (2×3=6) en lugar de identificar el exponente."),
            ("0,375", "Calculó 3/8 en lugar de identificar a qué exponente se eleva 2 para obtener 8."),
        ],
    ),
    _q(
        "num_logaritmos", "medio",
        "Resuelve: log₅(x) = 2",
        "x = 25",
        "La definición de logaritmo dice que log_b(x) = n equivale a x = b^n.\n\n"
        "1) Aquí la base es 5 y el resultado del logaritmo es 2.\n"
        "2) Despeja aplicando la definición: x = 5² = 25.",
        [
            ("x = 10", "Multiplicó la base por el exponente (5×2) en lugar de elevar la base al exponente (5²)."),
            ("x = 2,5", "Dividió la base por el exponente en lugar de elevar la base al exponente dado."),
            ("x = 32", "Invirtió la base y el exponente: calculó 2⁵ en lugar de 5²."),
        ],
    ),
    _q(
        "num_logaritmos", "dificil",
        "Usando que log(2) ≈ 0,301 y log(3) ≈ 0,477, ¿cuál es el valor aproximado "
        "de log(6)?",
        "≈0,778",
        "6 = 2 × 3, y el logaritmo de un producto es la suma de los "
        "logaritmos de cada factor.\n\n"
        "1) log(6) = log(2 × 3) = log(2) + log(3).\n"
        "2) Reemplaza: 0,301 + 0,477 = 0,778.",
        [
            ("≈0,144", "Multiplicó los logaritmos entre sí en lugar de sumarlos: la propiedad del logaritmo de un producto es una suma, no una multiplicación."),
            ("≈0,176", "Restó los logaritmos en lugar de sumarlos, calculando log(3/2) en vez de log(2×3)."),
            ("5", "Sumó los números 2 y 3 directamente, en lugar de sumar sus logaritmos."),
        ],
    ),
    # ---------- ÁLGEBRA Y FUNCIONES ----------
    _q(
        "alg_sistemas_casos", "facil",
        "¿Cuántas soluciones tiene el sistema: x + y = 5 ; x + y = 8?",
        "Ninguna solución",
        "Ambas ecuaciones tienen exactamente los mismos coeficientes para x e "
        "y, pero distinto término independiente.\n\n"
        "1) Eso significa que ambas rectas tienen la misma pendiente (son "
        "paralelas).\n"
        "2) Como los términos independientes son distintos (5 ≠ 8), no es la "
        "misma recta: son paralelas y nunca se cruzan.\n"
        "3) Por lo tanto, el sistema no tiene solución.",
        [
            ("Una única solución", "No reconoció que ambas ecuaciones tienen los mismos coeficientes de x e y, lo que las hace rectas paralelas sin intersección."),
            ("Infinitas soluciones", "Confundió este caso con el de rectas coincidentes; aquí los términos independientes son distintos (5≠8), así que no es la misma recta."),
            ("x=5, y=8", "Interpretó cada ecuación como si diera directamente el valor de una variable, en lugar de analizar el sistema como un todo."),
        ],
    ),
    _q(
        "alg_sistemas_casos", "medio",
        "¿Cuántas soluciones tiene el sistema: 2x + 4y = 10 ; x + 2y = 5?",
        "Infinitas soluciones",
        "Hay que comparar si una ecuación es múltiplo de la otra.\n\n"
        "1) Multiplica la segunda ecuación completa por 2: "
        "2(x + 2y) = 2(5), es decir, 2x + 4y = 10.\n"
        "2) Es exactamente igual a la primera ecuación: ambas representan la "
        "misma recta.\n"
        "3) Cuando las dos ecuaciones son la misma recta, cualquier punto de "
        "esa recta es solución del sistema: hay infinitas soluciones.",
        [
            ("Ninguna solución", "Notó que las ecuaciones son proporcionales, pero concluyó que son rectas paralelas distintas en lugar de la misma recta coincidente."),
            ("Una única solución, x=5, y=0", "Encontró un par de valores que sí satisface ambas ecuaciones, pero no reconoció que el sistema tiene infinitas soluciones (cualquier punto de esa recta funciona, no solo ese)."),
            ("El sistema no se puede resolver", "Interpretó que el sistema no tiene solución determinable, cuando en realidad tiene infinitas soluciones porque ambas ecuaciones representan la misma recta."),
        ],
    ),
    _q(
        "alg_sistemas_casos", "dificil",
        "¿Para qué valor de k el sistema 3x + ky = 6 ; x + 2y = 4 NO tiene solución "
        "única (es paralelo)?",
        "k = 6",
        "Un sistema no tiene solución única cuando los coeficientes de ambas "
        "ecuaciones son proporcionales.\n\n"
        "1) La proporción entre los coeficientes de x debe igualar a la de "
        "los coeficientes de y: 3/1 = k/2.\n"
        "2) Despeja: k = 3 × 2 = 6.\n"
        "3) Verifica que no sea la misma recta comparando con los términos "
        "independientes: 6/4 = 1,5, que es distinto de 3/1 = 3, así que con "
        "k=6 el sistema es paralelo (sin solución), no coincidente.",
        [
            ("k = 3", "Igualó directamente los coeficientes (k=3) sin considerar la proporción correcta entre ambas ecuaciones (3/1 = k/2)."),
            ("k = 12", "Multiplicó 3×2×2 en lugar de resolver correctamente la proporción 3/1 = k/2."),
            ("k = 4", "Usó un término independiente de las ecuaciones en lugar de los coeficientes de las variables para plantear la proporción."),
        ],
    ),
    _q(
        "alg_funcion_potencia", "facil",
        "¿Cuál es el valor de f(x) = x³ cuando x = −2?",
        "−8",
        "Se reemplaza x por −2 y se eleva al cubo, respetando el signo.\n\n"
        "1) (−2)³ = (−2) × (−2) × (−2).\n"
        "2) (−2) × (−2) = 4, y 4 × (−2) = −8.\n"
        "3) El cubo de un número negativo es negativo (a diferencia del "
        "cuadrado).",
        [
            ("8", "Olvidó que el cubo de un número negativo es negativo: perdió el signo al elevar al cubo."),
            ("−6", "Multiplicó la base por el exponente (−2×3) en lugar de elevarla al cubo."),
            ("6", "Multiplicó el valor absoluto de la base por el exponente, ignorando tanto el signo como la operación de potencia."),
        ],
    ),
    _q(
        "alg_funcion_potencia", "medio",
        "¿Cuál de las siguientes funciones potencia tiene un gráfico simétrico "
        "respecto al origen (función impar)?",
        "f(x) = x³",
        "Una función potencia con exponente impar es simétrica respecto al "
        "origen; con exponente par, es simétrica respecto al eje Y.\n\n"
        "1) x³ tiene exponente 3, que es impar.\n"
        "2) Verifica con la definición de función impar: f(−x) = −f(x). Aquí "
        "(−x)³ = −x³, se cumple.\n"
        "3) Las otras opciones tienen exponente par, así que son simétricas "
        "respecto al eje Y, no al origen.",
        [
            ("f(x) = x²", "Tiene exponente par: su gráfico es simétrico respecto al eje Y, no respecto al origen."),
            ("f(x) = x⁴", "También tiene exponente par: al igual que x², su simetría es respecto al eje Y, no al origen."),
            ("f(x) = 2x²", "El coeficiente 2 no cambia la paridad del exponente: sigue siendo una función par, simétrica respecto al eje Y."),
        ],
    ),
    _q(
        "alg_funcion_potencia", "dificil",
        "Si f(x) = x⁵, ¿cuál es el valor de f(−1) + f(2)?",
        "31",
        "Se evalúa la función en cada valor por separado y luego se suman "
        "los resultados.\n\n"
        "1) f(−1) = (−1)⁵ = −1, porque un exponente impar conserva el signo "
        "negativo de la base.\n"
        "2) f(2) = 2⁵ = 32.\n"
        "3) Suma: −1 + 32 = 31.",
        [
            ("33", "Calculó (−1)⁵ como 1 en lugar de −1, olvidando que un exponente impar conserva el signo negativo de la base."),
            ("−31", "Cometió un error de signo en ambos términos: calculó (−1)⁵=1 y 2⁵=−32."),
            ("1", "Sumó los valores de x primero (−1+2=1) y evaluó la función una sola vez, en lugar de evaluar f en cada valor por separado y sumar los resultados."),
        ],
    ),
    # ---------- GEOMETRÍA ----------
    _q(
        "geo_homotecia", "facil",
        "Un triángulo tiene lados de 3 cm, 4 cm y 5 cm. Se le aplica una homotecia "
        "de razón k=2. ¿Cuáles son las medidas de los lados del triángulo "
        "resultante?",
        "6 cm, 8 cm y 10 cm",
        "En una homotecia, cada medida lineal de la figura se multiplica por "
        "la razón k.\n\n"
        "1) Multiplica cada lado por 2: 3×2=6, 4×2=8, 5×2=10.",
        [
            ("5 cm, 6 cm y 7 cm", "Sumó 2 a cada lado en lugar de multiplicarlo por la razón de homotecia."),
            ("1,5 cm, 2 cm y 2,5 cm", "Dividió cada lado por la razón de homotecia en lugar de multiplicarlo."),
            ("9 cm, 16 cm y 25 cm", "Elevó al cuadrado cada lado en lugar de multiplicarlo por la razón (confundió con el cambio de área, que sí es cuadrático)."),
        ],
    ),
    _q(
        "geo_homotecia", "medio",
        "Un cuadrado de área 9 cm² se somete a una homotecia de razón k=3. ¿Cuál "
        "es el área de la figura resultante?",
        "81 cm²",
        "A diferencia de las longitudes, el área escala según el cuadrado de "
        "la razón de homotecia.\n\n"
        "1) La razón de homotecia es k=3.\n"
        "2) El área se multiplica por k²: 9 × 3² = 9 × 9 = 81 cm².",
        [
            ("27 cm²", "Multiplicó el área original por la razón de homotecia (k) en lugar de por k², que es cómo escala el área."),
            ("9 cm²", "No aplicó la homotecia al área: la dejó igual a la original."),
            ("12 cm²", "Sumó la razón de homotecia al área original en lugar de aplicar el escalamiento correspondiente."),
        ],
    ),
    _q(
        "geo_homotecia", "dificil",
        "Un punto P(2, 3) se somete a una homotecia de centro en el origen (0,0) "
        "y razón k = −2. ¿Cuáles son las coordenadas del punto resultante?",
        "(−4, −6)",
        "Con centro en el origen, las coordenadas del punto resultante se "
        "obtienen multiplicando cada coordenada por la razón k.\n\n"
        "1) Coordenada x: 2 × (−2) = −4.\n"
        "2) Coordenada y: 3 × (−2) = −6.\n"
        "3) El punto resultante es (−4, −6). El signo negativo de k invierte "
        "el punto respecto al centro, además de escalarlo.",
        [
            ("(4, 6)", "Aplicó la razón de homotecia ignorando su signo negativo, como si k fuera 2 en lugar de −2."),
            ("(0, 1)", "Sumó la razón de homotecia a cada coordenada en lugar de multiplicarlas."),
            ("(−2, −3)", "Solo invirtió el signo de las coordenadas, sin multiplicarlas también por 2."),
        ],
    ),
    _q(
        "geo_trigonometria", "facil",
        "En un triángulo rectángulo, el cateto opuesto a un ángulo mide 6 cm y la "
        "hipotenusa mide 10 cm. ¿Cuál es el seno de ese ángulo?",
        "3/5 (0,6)",
        "El seno de un ángulo agudo en un triángulo rectángulo es el cateto "
        "opuesto dividido por la hipotenusa.\n\n"
        "1) sen(ángulo) = cateto opuesto / hipotenusa = 6/10.\n"
        "2) Simplifica dividiendo por 2: 6/10 = 3/5 = 0,6.",
        [
            ("5/3", "Invirtió la razón: dividió la hipotenusa por el cateto opuesto en lugar de el cateto opuesto por la hipotenusa."),
            ("4/5", "Calculó el coseno del ángulo (cateto adyacente/hipotenusa, con adyacente=8 vía Pitágoras) en lugar del seno (cateto opuesto/hipotenusa)."),
            ("3/4", "Calculó la tangente del ángulo (cateto opuesto/cateto adyacente = 6/8) en lugar del seno (cateto opuesto/hipotenusa)."),
        ],
    ),
    _q(
        "geo_trigonometria", "medio",
        "En un triángulo rectángulo, un ángulo agudo tiene coseno 0,8. Si la "
        "hipotenusa mide 15 cm, ¿cuánto mide el cateto adyacente a ese ángulo?",
        "12 cm",
        "El coseno es el cateto adyacente dividido por la hipotenusa, así "
        "que el cateto adyacente se despeja multiplicando.\n\n"
        "1) cos(ángulo) = cateto adyacente / hipotenusa.\n"
        "2) Despeja: cateto adyacente = cos(ángulo) × hipotenusa = 0,8 × 15 "
        "= 12 cm.",
        [
            ("18,75 cm", "Dividió la hipotenusa por el coseno en lugar de multiplicarla."),
            ("0,053 cm", "Dividió el coseno por la hipotenusa en lugar de multiplicar ambos valores."),
            ("9 cm", "Calculó el cateto opuesto (usando Pitágoras a partir del adyacente=12) en lugar de responder con el cateto adyacente que pedía el enunciado."),
        ],
    ),
    _q(
        "geo_trigonometria", "dificil",
        "Desde un punto en el suelo a 20 m de la base de un edificio, el ángulo de "
        "elevación hacia la parte superior del edificio tiene una tangente de "
        "1,5. ¿Cuál es la altura del edificio?",
        "30 m",
        "La tangente del ángulo de elevación es la altura (cateto opuesto) "
        "dividida por la distancia al edificio (cateto adyacente).\n\n"
        "1) tan(ángulo) = altura / distancia.\n"
        "2) Despeja: altura = tan(ángulo) × distancia = 1,5 × 20 = 30 m.",
        [
            ("13,33 m", "Dividió la distancia por la tangente en lugar de multiplicarla."),
            ("21,5 m", "Sumó la tangente a la distancia en lugar de multiplicarlas."),
            ("24 m", "Leyó mal el valor de la tangente del enunciado (usó 1,2 en lugar de 1,5)."),
        ],
    ),
    # ---------- PROBABILIDAD Y ESTADÍSTICA ----------
    _q(
        "prob_dispersion", "facil",
        "¿Cuál es la varianza de los datos: 2, 4, 6? (la media es 4)",
        "8/3 (≈2,67)",
        "La varianza es el promedio de las diferencias al cuadrado respecto "
        "a la media.\n\n"
        "1) Calcula cada diferencia respecto a la media (4) y elévala al "
        "cuadrado: (2−4)²=4, (4−4)²=0, (6−4)²=4.\n"
        "2) Súmalas: 4+0+4=8.\n"
        "3) Divide por la cantidad de datos: 8/3 ≈ 2,67.",
        [
            ("0", "Sumó las diferencias respecto a la media sin elevarlas al cuadrado: como son −2, 0 y 2, se cancelaron y dieron 0."),
            ("8", "Calculó la suma de los cuadrados de las diferencias respecto a la media (8) pero olvidó dividir por la cantidad de datos."),
            ("≈1,63", "Calculó la raíz cuadrada de la varianza (que es la desviación estándar) en lugar de la varianza misma."),
        ],
    ),
    _q(
        "prob_dispersion", "medio",
        "¿Cuál es la desviación estándar de los datos: 3, 5, 7? (la media es 5 y "
        "la varianza es 8/3)",
        "≈1,63",
        "La desviación estándar es la raíz cuadrada de la varianza.\n\n"
        "1) La varianza ya está dada: 8/3 ≈ 2,67.\n"
        "2) Calcula su raíz cuadrada: √2,67 ≈ 1,63.",
        [
            ("8/3 (≈2,67)", "Entregó la varianza directamente, sin calcular su raíz cuadrada para obtener la desviación estándar."),
            ("≈2,83", "Calculó la raíz cuadrada de la suma de los cuadrados (8) sin dividirla antes por la cantidad de datos."),
            ("4", "Calculó el rango de los datos (7−3=4) en lugar de la desviación estándar."),
        ],
    ),
    _q(
        "prob_dispersion", "dificil",
        "Dos cursos rindieron una prueba. El curso A tiene media 5,5 y desviación "
        "estándar 0,3. El curso B tiene media 5,5 y desviación estándar 1,2. "
        "¿Qué significa esto?",
        "Ambos cursos tuvieron el mismo promedio, pero las notas del curso A "
        "fueron más parejas entre sí que las del curso B.",
        "La media dice cuál fue el promedio; la desviación estándar dice qué "
        "tan dispersos (parejos o no) están los datos alrededor de esa "
        "media.\n\n"
        "1) Ambos cursos tienen la misma media (5,5): en promedio, les fue "
        "igual de bien.\n"
        "2) El curso A tiene una desviación estándar más baja (0,3): sus "
        "notas están más concentradas cerca del promedio.\n"
        "3) El curso B tiene una desviación estándar más alta (1,2): sus "
        "notas están más dispersas, con más estudiantes lejos del promedio "
        "(tanto por arriba como por abajo).",
        [
            ("El curso B tuvo mejores resultados que el curso A, porque su desviación estándar es mayor.", "Interpretó una desviación estándar más alta como mejor desempeño, cuando en realidad indica mayor dispersión (menos consistencia), no mejores notas."),
            ("El curso A tuvo un promedio más alto que el curso B.", "Confundió la desviación estándar con el promedio: ambos cursos tienen la misma media (5,5), la diferencia está solo en qué tan dispersas están las notas."),
            ("No se puede comparar nada porque los cursos son distintos.", "No usó la información entregada: la desviación estándar sí permite comparar qué tan homogéneas son las notas entre ambos cursos."),
        ],
    ),
    _q(
        "prob_condicional", "facil",
        "En una bolsa hay 4 bolitas rojas y 6 azules. Se saca una al azar y resulta "
        "azul. Sin devolverla, se saca una segunda bolita. ¿Cuál es la "
        "probabilidad de que la segunda también sea azul?",
        "5/9",
        "Como la primera bolita azul no se devuelve, hay que recalcular "
        "tanto las azules restantes como el total antes de la segunda "
        "extracción.\n\n"
        "1) Antes: 4 rojas + 6 azules = 10 en total.\n"
        "2) Tras sacar una azul sin devolverla, quedan 4 rojas + 5 azules = "
        "9 en total.\n"
        "3) La probabilidad de que la segunda también sea azul es 5/9.",
        [
            ("6/10 (3/5)", "No actualizó la cantidad de bolitas tras la primera extracción: calculó la probabilidad como si todavía hubiera 6 azules de 10 en total."),
            ("5/10 (1/2)", "Actualizó la cantidad de bolitas azules restantes, pero no descontó la bolita ya sacada del total."),
            ("4/9", "Usó la cantidad de bolitas rojas restantes en el numerador en lugar de las azules."),
        ],
    ),
    _q(
        "prob_condicional", "medio",
        "En un curso, el 40% de los estudiantes practica deporte y el 15% "
        "practica deporte Y toca un instrumento musical. De los que practican "
        "deporte, ¿qué porcentaje también toca un instrumento?",
        "37,5%",
        "Se pide una probabilidad condicional: entre quienes practican "
        "deporte, cuántos también tocan un instrumento.\n\n"
        "1) La fórmula es: P(instrumento | deporte) = P(deporte y "
        "instrumento) / P(deporte).\n"
        "2) Reemplaza: 15% / 40% = 0,15 / 0,40 = 0,375.\n"
        "3) Como porcentaje: 37,5%.",
        [
            ("15%", "Entregó el porcentaje conjunto (15%) directamente, sin dividirlo por el porcentaje de quienes practican deporte para obtener la probabilidad condicional."),
            ("6%", "Multiplicó los porcentajes en lugar de dividir el porcentaje conjunto por el porcentaje de quienes practican deporte."),
            ("55%", "Sumó los porcentajes (40%+15%) en lugar de dividir el porcentaje conjunto por el porcentaje de quienes practican deporte."),
        ],
    ),
    _q(
        "prob_condicional", "dificil",
        "En una fábrica, el 2% de los productos tiene un defecto. De los productos "
        "defectuosos, el 30% son detectados por el control de calidad. ¿Qué "
        "porcentaje de TODOS los productos son defectuosos Y fueron detectados?",
        "0,6%",
        "Acá se pide lo contrario del ejercicio típico: en vez de dividir "
        "para obtener una probabilidad condicional, hay que multiplicar la "
        "probabilidad total por la condicional para obtener la conjunta.\n\n"
        "1) P(defectuoso) = 2% = 0,02.\n"
        "2) P(detectado | defectuoso) = 30% = 0,30.\n"
        "3) P(defectuoso Y detectado) = P(defectuoso) × P(detectado | "
        "defectuoso) = 0,02 × 0,30 = 0,006 = 0,6%.",
        [
            ("30%", "Entregó el porcentaje condicional (30%) directamente, sin multiplicarlo por el porcentaje de productos defectuosos."),
            ("32%", "Sumó los porcentajes (2%+30%) en lugar de multiplicarlos."),
            ("15%", "Dividió los porcentajes (30/2) en lugar de multiplicarlos."),
        ],
    ),
    _q(
        "prob_permutacion", "facil",
        "¿De cuántas formas distintas se pueden ordenar las letras de la palabra "
        "\"ANA\"? (la letra A se repite 2 veces)",
        "3",
        "Cuando hay letras repetidas, el total de permutaciones se divide "
        "por el factorial de las repeticiones, porque intercambiar letras "
        "iguales entre sí no genera un orden distinto.\n\n"
        "1) Si las 3 letras fueran distintas, habría 3! = 6 formas.\n"
        "2) Pero la A se repite 2 veces, así que se divide por 2!: "
        "6 / 2 = 3.",
        [
            ("6", "Calculó 3! como si las 3 letras fueran distintas, sin dividir por las repeticiones de la letra A."),
            ("2", "Dividió 3! entre 3 en lugar de entre 2! (el factorial de la cantidad de letras repetidas)."),
            ("9", "Calculó 3² en lugar de aplicar la fórmula de permutaciones con elementos repetidos (3!/2!)."),
        ],
    ),
    _q(
        "prob_permutacion", "medio",
        "¿De cuántas formas distintas se pueden ordenar las letras de la palabra "
        "\"MAMA\"? (la M se repite 2 veces y la A se repite 2 veces)",
        "6",
        "Con dos letras repetidas, se divide por el factorial de cada una "
        "de las repeticiones.\n\n"
        "1) Si las 4 letras fueran distintas, habría 4! = 24 formas.\n"
        "2) Se divide por las repeticiones de M (2!) y también por las de A "
        "(2!): 24 / (2! × 2!) = 24 / 4 = 6.",
        [
            ("24", "Calculó 4! sin dividir por las repeticiones de ninguna letra."),
            ("12", "Dividió 4! solo por el factorial de las repeticiones de una letra, olvidando dividir también por las de la otra."),
            ("8", "Dividió 4! entre un valor que no corresponde a las repeticiones reales (2!×2!=4)."),
        ],
    ),
    _q(
        "prob_permutacion", "dificil",
        "Un comité de 4 personas se debe formar eligiendo 2 hombres de un grupo de "
        "5 hombres, y 2 mujeres de un grupo de 4 mujeres. ¿De cuántas formas "
        "distintas se puede formar el comité?",
        "60",
        "Se calcula la cantidad de formas de elegir cada grupo por separado "
        "y luego se multiplican (principio multiplicativo), porque ambas "
        "elecciones ocurren a la vez.\n\n"
        "1) Formas de elegir 2 hombres de 5 (el orden no importa, es una "
        "combinación): C(5,2) = 10.\n"
        "2) Formas de elegir 2 mujeres de 4: C(4,2) = 6.\n"
        "3) Multiplica ambas cantidades: 10 × 6 = 60.",
        [
            ("16", "Sumó las combinaciones de hombres y mujeres (10+6) en lugar de multiplicarlas."),
            ("20", "Multiplicó la cantidad total de hombres y mujeres disponibles (5×4) en lugar de las combinaciones posibles de elegir 2 de cada grupo."),
            ("120", "Calculó una permutación (P(5,2)=20) en lugar de una combinación (C(5,2)=10) para elegir a los hombres, sin notar que el orden dentro del comité no importa."),
        ],
    ),
    _q(
        "prob_binomial", "facil",
        "Se lanza una moneda 3 veces. ¿Cuál es la probabilidad de obtener "
        "exactamente 2 caras?",
        "3/8",
        "Es un modelo binomial: hay que considerar tanto la probabilidad de "
        "cada resultado como la cantidad de formas distintas en que puede "
        "ocurrir.\n\n"
        "1) La probabilidad de una secuencia específica con 2 caras y 1 "
        "sello es (1/2)² × (1/2)¹ = 1/8.\n"
        "2) Hay C(3,2) = 3 formas distintas de elegir en cuáles de los 3 "
        "lanzamientos caen las 2 caras (CCS, CSC, SCC).\n"
        "3) Multiplica: 3 × 1/8 = 3/8.",
        [
            ("1/2", "Calculó la probabilidad de un solo lanzamiento, en lugar de usar el modelo binomial para los 3 lanzamientos."),
            ("1/8", "Calculó la probabilidad de una secuencia específica ((1/2)³) sin multiplicar por la cantidad de formas distintas en que pueden ocurrir las 2 caras (C(3,2)=3)."),
            ("3/4", "Contó el doble de los casos favorables reales (6 en lugar de 3), duplicando alguna combinación por error."),
        ],
    ),
    _q(
        "prob_binomial", "medio",
        "La probabilidad de que un estudiante apruebe un examen de manera "
        "independiente es 0,8. Si 2 estudiantes rinden el examen, ¿cuál es la "
        "probabilidad de que AMBOS aprueben?",
        "0,64 (64%)",
        "Cuando dos eventos son independientes, la probabilidad de que "
        "ambos ocurran es el producto de sus probabilidades individuales.\n\n"
        "1) Probabilidad de que el primero apruebe: 0,8.\n"
        "2) Probabilidad de que el segundo apruebe: 0,8.\n"
        "3) Como son independientes, se multiplican: 0,8 × 0,8 = 0,64.",
        [
            ("1,6 (160%)", "Sumó las probabilidades en lugar de multiplicarlas — el resultado ni siquiera podría ser una probabilidad válida, porque supera a 1."),
            ("0,8 (80%)", "Calculó la probabilidad de que apruebe un solo estudiante, sin considerar que se pide la probabilidad de que ambos aprueben."),
            ("0,4 (40%)", "Dividió la probabilidad por la cantidad de estudiantes en lugar de multiplicar las probabilidades independientes."),
        ],
    ),
    _q(
        "prob_binomial", "dificil",
        "Un tirador acierta al blanco con probabilidad 0,6 en cada disparo, de "
        "forma independiente. Si dispara 3 veces, ¿cuál es la probabilidad de "
        "que acierte EXACTAMENTE 1 vez?",
        "0,288 (28,8%)",
        "Es un modelo binomial con 3 intentos, donde interesa exactamente 1 "
        "éxito.\n\n"
        "1) La probabilidad de una secuencia específica con 1 acierto y 2 "
        "fallas es 0,6 × 0,4 × 0,4 = 0,096.\n"
        "2) Hay C(3,1) = 3 formas distintas de elegir en cuál de los 3 "
        "disparos ocurre el acierto.\n"
        "3) Multiplica: 3 × 0,096 = 0,288.",
        [
            ("0,6", "Entregó directamente la probabilidad de acierto de un solo disparo, sin aplicar el modelo binomial para los 3 disparos."),
            ("0,096", "Calculó la probabilidad de una secuencia específica (acierto en el primer disparo y falla en los otros dos) sin multiplicar por las 3 formas distintas en que puede ocurrir exactamente 1 acierto."),
            ("0,216", "Calculó la probabilidad de acertar los 3 disparos (0,6³) en lugar de la de acertar exactamente 1."),
        ],
    ),
]
