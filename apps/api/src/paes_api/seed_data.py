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


# ---------------------------------------------------------------------------
# Ampliación del banco — agosto 2026
#
# Preguntas propias construidas sobre el temario oficial DEMRE (Admisión 2027),
# con el mismo formato de la prueba: enunciado breve, cuatro alternativas y un
# único distractor por error conceptual típico. No reproducen preguntas
# liberadas del DEMRE, que son material con derechos de la Universidad de
# Chile: replican su temario, su formato y su nivel de exigencia.
#
# Cada valor numérico está verificado en scripts/verificar_banco.py.
# ---------------------------------------------------------------------------

QUESTIONS += [
    # ---------- NÚMEROS: racionales ----------
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 5/6 − 2/9?",
        "11/18",
        "Para restar fracciones ambas deben tener el mismo denominador.\n\n"
        "1) El mínimo común múltiplo de 6 y 9 es 18: los múltiplos de 6 son 6, 12, 18… "
        "y los de 9 son 9, 18…\n"
        "2) Convierte cada fracción a dieciochoavos. Como 18 ÷ 6 = 3, multiplicas arriba "
        "y abajo por 3: 5/6 = 15/18. Como 18 ÷ 9 = 2, multiplicas por 2: 2/9 = 4/18.\n"
        "3) Resta solo los numeradores: 15/18 − 4/18 = 11/18.\n"
        "4) Como 11 es primo y no divide a 18, la fracción ya está simplificada.",
        [
            ("3/3", "Restó numeradores entre sí y denominadores entre sí, sin buscar denominador común."),
            ("7/18", "Usó bien el denominador 18, pero convirtió mal 5/6 (lo dejó en 11/18 en vez de 15/18)."),
            ("19/18", "Sumó las fracciones en lugar de restarlas."),
        ],
    ),
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de (3/5) × (10/9)?",
        "2/3",
        "Al multiplicar fracciones se multiplican numeradores entre sí y denominadores "
        "entre sí; conviene simplificar antes para trabajar con números chicos.\n\n"
        "1) Escribe el producto: (3 × 10)/(5 × 9) = 30/45.\n"
        "2) Simplifica: el máximo común divisor de 30 y 45 es 15. Entonces "
        "30 ÷ 15 = 2 y 45 ÷ 15 = 3, o sea 2/3.\n"
        "3) Atajo: podías simplificar cruzado antes de multiplicar. El 3 de arriba con "
        "el 9 de abajo dejan 1 y 3; el 10 de arriba con el 5 de abajo dejan 2 y 1. "
        "Queda (1 × 2)/(1 × 3) = 2/3.",
        [
            ("13/14", "Sumó numeradores entre sí y denominadores entre sí en vez de multiplicar."),
            ("27/50", "Invirtió la segunda fracción y multiplicó, que es la regla de la división, no de la multiplicación."),
            ("30/45", "Multiplicó correctamente pero no simplificó el resultado."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de 2 + (1/2) ÷ (2/3)?",
        "11/4",
        "Se respeta la prioridad de operaciones: primero la división, después la suma.\n\n"
        "1) Resuelve la división. Dividir por 2/3 es multiplicar por su recíproco 3/2: "
        "(1/2) × (3/2) = 3/4.\n"
        "2) Ahora suma: 2 + 3/4. Escribe el 2 como fracción de denominador 4: "
        "2 = 8/4.\n"
        "3) Suma los numeradores: 8/4 + 3/4 = 11/4.\n\n"
        "Como referencia, 11/4 = 2,75, coherente con sumarle algo menor que 1 al 2.",
        [
            ("15/4", "Sumó primero (2 + 1/2) y después dividió, sin respetar la prioridad de la división."),
            ("2/3", "Resolvió solo la división y olvidó sumar el 2."),
            ("7/3", "Multiplicó las fracciones en vez de dividir, obteniendo 1/3, y luego sumó 2."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "Un tambor tiene 3/4 de su capacidad con agua. Se saca 1/3 del agua que "
        "contiene. ¿Qué fracción de la capacidad total del tambor queda con agua?",
        "1/2",
        "Ojo con el referente: la fracción que se saca está calculada sobre el agua "
        "que hay, no sobre la capacidad total.\n\n"
        "1) El agua presente es 3/4 de la capacidad.\n"
        "2) Se saca 1/3 de esa agua: (1/3) × (3/4) = 3/12 = 1/4 de la capacidad total.\n"
        "3) Queda el agua inicial menos lo sacado: 3/4 − 1/4 = 2/4 = 1/2.\n\n"
        "Otra forma: si se saca un tercio, quedan dos tercios del agua. "
        "(2/3) × (3/4) = 6/12 = 1/2, el mismo resultado.",
        [
            ("5/12", "Restó 1/3 de la capacidad total en vez de 1/3 del agua presente: 3/4 − 1/3 = 5/12."),
            ("1/4", "Calculó cuánta agua se sacó y entregó ese valor en lugar de lo que queda."),
            ("2/3", "Entregó la fracción del agua que queda respecto del agua inicial, no respecto de la capacidad total."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "¿Cuál es el resultado de (2/3 − 1/4) ÷ (5/6 + 1/2)?",
        "5/16",
        "Se resuelven por separado el paréntesis de arriba y el de abajo, y recién "
        "después se divide.\n\n"
        "1) Numerador: el mínimo común múltiplo de 3 y 4 es 12. "
        "2/3 = 8/12 y 1/4 = 3/12, así que 8/12 − 3/12 = 5/12.\n"
        "2) Denominador: el mínimo común múltiplo de 6 y 2 es 6. "
        "5/6 se mantiene y 1/2 = 3/6, así que 5/6 + 3/6 = 8/6 = 4/3.\n"
        "3) Divide multiplicando por el recíproco: (5/12) ÷ (4/3) = (5/12) × (3/4) = "
        "15/48.\n"
        "4) Simplifica por 3: 15 ÷ 3 = 5 y 48 ÷ 3 = 16, o sea 5/16.",
        [
            ("5/9", "Al dividir multiplicó por 3/4 mal simplificado, o dividió los paréntesis término a término."),
            ("15/48", "Hizo bien toda la operación pero no simplificó el resultado final."),
            ("16/5", "Invirtió el resultado: dividió el denominador por el numerador."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "Si a = 2/5 y b = 3/4, ¿cuál es el valor de (a + b) ÷ (b − a)?",
        "23/7",
        "Conviene calcular por separado la suma y la resta antes de dividir.\n\n"
        "1) Suma: el mínimo común múltiplo de 5 y 4 es 20. a = 8/20 y b = 15/20, "
        "así que a + b = 23/20.\n"
        "2) Resta: b − a = 15/20 − 8/20 = 7/20.\n"
        "3) Divide multiplicando por el recíproco: (23/20) ÷ (7/20) = "
        "(23/20) × (20/7).\n"
        "4) Los 20 se cancelan y queda 23/7.\n\n"
        "Como ambas fracciones quedaron con el mismo denominador, el resultado es "
        "simplemente el cociente de los numeradores.",
        [
            ("7/23", "Calculó (b − a) ÷ (a + b), invirtiendo el orden de la división."),
            ("23/20", "Resolvió solo la suma del numerador y no dividió."),
            ("31/20", "Sumó las dos expresiones en vez de dividirlas."),
        ],
    ),
]

QUESTIONS += [
    # ---------- NÚMEROS: potencias y raíces ----------
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de 2³ · 2⁴?",
        "128",
        "Al multiplicar potencias de igual base se conserva la base y se suman los "
        "exponentes.\n\n"
        "1) Aplica la propiedad: 2³ · 2⁴ = 2³⁺⁴ = 2⁷.\n"
        "2) Calcula 2⁷ = 128.\n\n"
        "Comprobación directa: 2³ = 8 y 2⁴ = 16, y 8 · 16 = 128.",
        [
            ("64", "Multiplicó los exponentes en vez de sumarlos, obteniendo 2⁶."),
            ("4096", "Multiplicó los exponentes y luego elevó de nuevo, o calculó (2³)⁴ = 2¹²."),
            ("14", "Sumó las potencias por separado (8 + 16 sería 24) o sumó bases y exponentes sueltos."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de √81 − √16?",
        "5",
        "Se calcula cada raíz por separado y después se restan.\n\n"
        "1) √81 = 9, porque 9 · 9 = 81.\n"
        "2) √16 = 4, porque 4 · 4 = 16.\n"
        "3) Resta: 9 − 4 = 5.\n\n"
        "Cuidado: la raíz de una resta no es la resta de las raíces. "
        "√(81 − 16) = √65 ≈ 8,06, que es otra cosa.",
        [
            ("√65", "Restó primero dentro de las raíces en lugar de calcular cada una."),
            ("65", "Restó los números sin sacar las raíces."),
            ("13", "Sumó las raíces en vez de restarlas."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de (3⁵ · 3²) ÷ 3⁴?",
        "27",
        "Se aplican las propiedades de potencias de igual base: al multiplicar se suman "
        "exponentes y al dividir se restan.\n\n"
        "1) Numerador: 3⁵ · 3² = 3⁵⁺² = 3⁷.\n"
        "2) División: 3⁷ ÷ 3⁴ = 3⁷⁻⁴ = 3³.\n"
        "3) Calcula 3³ = 27.",
        [
            ("9", "Restó mal los exponentes y llegó a 3², o dividió antes de multiplicar."),
            ("81", "Sumó los tres exponentes (5 + 2 − 4 mal calculado) y llegó a 3⁴."),
            ("2187", "Sumó los exponentes del numerador pero no dividió, quedándose en 3⁷."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de 5⁻²?",
        "1/25",
        "Un exponente negativo indica el recíproco de la potencia con exponente "
        "positivo.\n\n"
        "1) Por definición, 5⁻² = 1/5².\n"
        "2) Calcula 5² = 25.\n"
        "3) Por lo tanto, 5⁻² = 1/25.\n\n"
        "El signo del exponente no vuelve negativo el resultado: una potencia de base "
        "positiva siempre da un número positivo.",
        [
            ("−25", "Interpretó el exponente negativo como si el resultado fuera negativo."),
            ("−10", "Multiplicó la base por el exponente en vez de aplicar la definición de potencia."),
            ("25", "Ignoró el signo del exponente y calculó 5²."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "¿Cuál es el valor de √50 − √18?",
        "2√2",
        "Conviene descomponer cada raíz para dejarlas con el mismo radical y poder "
        "restarlas.\n\n"
        "1) Descompone 50 = 25 · 2, entonces √50 = √25 · √2 = 5√2.\n"
        "2) Descompone 18 = 9 · 2, entonces √18 = √9 · √2 = 3√2.\n"
        "3) Ahora ambos términos tienen el mismo radical √2, así que se restan los "
        "coeficientes: 5√2 − 3√2 = 2√2.\n\n"
        "Verificación aproximada: √50 ≈ 7,07 y √18 ≈ 4,24; su diferencia ≈ 2,83, "
        "que coincide con 2√2 ≈ 2,83.",
        [
            ("√32", "Restó los números dentro de la raíz: √(50 − 18), que no es una propiedad válida."),
            ("8√2", "Sumó los coeficientes en lugar de restarlos."),
            ("2", "Restó los coeficientes pero perdió el radical √2 en el camino."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "Si 2ˣ = 32, ¿cuál es el valor de x?",
        "5",
        "Hay que expresar 32 como potencia de la misma base para comparar exponentes.\n\n"
        "1) Escribe 32 como potencia de 2: 2 · 2 · 2 · 2 · 2 = 32, es decir, 32 = 2⁵.\n"
        "2) La ecuación queda 2ˣ = 2⁵.\n"
        "3) Con bases iguales y potencias iguales, los exponentes deben ser iguales: "
        "x = 5.",
        [
            ("16", "Dividió 32 por 2 en lugar de buscar el exponente."),
            ("6", "Contó mal las multiplicaciones y llegó a 2⁶ = 64."),
            ("4", "Se quedó en 2⁴ = 16, un paso antes del valor pedido."),
        ],
    ),

    # ---------- NÚMEROS: porcentajes y proporcionalidad ----------
    _q(
        "num_porcentajes", "medio",
        "Un producto cuesta $18.000 y se le aplica un descuento del 25%. "
        "¿Cuál es el precio final?",
        "$13.500",
        "Conviene calcular directamente lo que se paga, no lo que se descuenta.\n\n"
        "1) Si el descuento es 25%, se paga el 75% del precio original.\n"
        "2) Multiplica: 0,75 · 18.000 = 13.500.\n\n"
        "Camino alternativo: el 25% de 18.000 es 4.500, y 18.000 − 4.500 = 13.500.",
        [
            ("$4.500", "Entregó el monto del descuento en lugar del precio final."),
            ("$22.500", "Sumó el 25% en vez de restarlo."),
            ("$17.975", "Restó 25 pesos en lugar del 25 por ciento."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "En un curso de 40 estudiantes, 24 son mujeres. ¿Qué porcentaje del curso "
        "son mujeres?",
        "60%",
        "El porcentaje es la parte dividida por el total, llevada a base 100.\n\n"
        "1) Escribe la razón: 24/40.\n"
        "2) Divide: 24 ÷ 40 = 0,6.\n"
        "3) Multiplica por 100 para expresarlo como porcentaje: 0,6 · 100 = 60%.\n\n"
        "Control: si 24 de 40 son mujeres, quedan 16 hombres, que corresponden al 40%. "
        "Ambos porcentajes suman 100%.",
        [
            ("40%", "Calculó el porcentaje de hombres (16 de 40) en lugar del de mujeres."),
            ("24%", "Tomó la cantidad de mujeres como si ya fuera el porcentaje."),
            ("166,7%", "Dividió el total por la parte (40 ÷ 24) en lugar de la parte por el total."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Un artículo sube un 20% y después baja un 20% sobre el nuevo precio. "
        "Respecto del precio inicial, el precio final es:",
        "un 4% menor",
        "Las variaciones porcentuales sucesivas no se cancelan, porque la segunda se "
        "calcula sobre un valor distinto de la primera.\n\n"
        "1) Toma un precio cómodo, por ejemplo 100.\n"
        "2) Sube 20%: 100 · 1,2 = 120.\n"
        "3) Baja 20% sobre 120, no sobre 100: 120 · 0,8 = 96.\n"
        "4) Compara con el inicial: 96 es 4 menos que 100, es decir, un 4% menor.\n\n"
        "En general el factor total es 1,2 · 0,8 = 0,96, que siempre implica una caída "
        "del 4% sea cual sea el precio de partida.",
        [
            ("igual al inicial", "Supuso que subir y bajar el mismo porcentaje se anula, ignorando que la segunda variación se aplica sobre un valor mayor."),
            ("un 4% mayor", "Identificó la diferencia del 4% pero se equivocó en el sentido: el precio termina más bajo."),
            ("un 20% menor", "Restó los porcentajes directamente sin considerar el orden de las operaciones."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Ocho trabajadores construyen un muro en 15 días. Trabajando al mismo ritmo, "
        "¿cuántos días demoran 12 trabajadores en construir el mismo muro?",
        "10 días",
        "Es una proporcionalidad inversa: a más trabajadores, menos días, porque el "
        "trabajo total es el mismo.\n\n"
        "1) Calcula el trabajo total en días-trabajador: 8 · 15 = 120.\n"
        "2) Ese total no cambia. Con 12 trabajadores: 12 · d = 120.\n"
        "3) Despeja: d = 120 ÷ 12 = 10 días.\n\n"
        "Coherencia: 12 trabajadores son más que 8, así que el plazo tiene que ser "
        "menor a 15 días.",
        [
            ("22,5 días", "Planteó una proporción directa (más trabajadores, más días), que invierte la relación real."),
            ("7,5 días", "Supuso que al aumentar de 8 a 12 el tiempo se reduce a la mitad."),
            ("12 días", "Restó la diferencia de trabajadores al plazo original en lugar de usar la proporcionalidad."),
        ],
    ),
]

QUESTIONS += [
    # ---------- ÁLGEBRA: expresiones y factorización ----------
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el resultado de reducir 5a + 3b − 2a + 7b?",
        "3a + 10b",
        "Solo se pueden sumar o restar términos semejantes, es decir, los que tienen "
        "la misma letra.\n\n"
        "1) Agrupa los términos con a: 5a − 2a = 3a.\n"
        "2) Agrupa los términos con b: 3b + 7b = 10b.\n"
        "3) La expresión reducida es 3a + 10b. No se puede seguir simplificando, "
        "porque a y b son términos distintos.",
        [
            ("13ab", "Sumó todos los coeficientes y juntó las letras, tratando términos distintos como semejantes."),
            ("3a + 4b", "Restó los términos en b en lugar de sumarlos."),
            ("7a + 10b", "Sumó los términos en a en lugar de restarlos."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el desarrollo de (x + 4)²?",
        "x² + 8x + 16",
        "El cuadrado de un binomio es el cuadrado del primero, más el doble producto, "
        "más el cuadrado del segundo.\n\n"
        "1) Cuadrado del primer término: x² .\n"
        "2) Doble producto de ambos: 2 · x · 4 = 8x.\n"
        "3) Cuadrado del segundo término: 4² = 16.\n"
        "4) Une los tres: x² + 8x + 16.\n\n"
        "Comprueba con un valor: si x = 1, (1 + 4)² = 25 y "
        "1 + 8 + 16 = 25.",
        [
            ("x² + 16", "Elevó cada término al cuadrado por separado y omitió el doble producto."),
            ("x² + 4x + 16", "Usó el producto simple en vez del doble producto."),
            ("x² + 8x + 8", "Duplicó el 4 en lugar de elevarlo al cuadrado."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización de x² − 49?",
        "(x + 7)(x − 7)",
        "Se reconoce una diferencia de cuadrados: un cuadrado menos otro cuadrado.\n\n"
        "1) Identifica los cuadrados: x² es el cuadrado de x, y 49 es el cuadrado de 7.\n"
        "2) La diferencia de cuadrados a² − b² siempre factoriza como (a + b)(a − b).\n"
        "3) Reemplaza a = x y b = 7: (x + 7)(x − 7).\n\n"
        "Verifica desarrollando: x² − 7x + 7x − 49 = x² − 49.",
        [
            ("(x − 7)²", "Confundió la diferencia de cuadrados con un cuadrado de binomio, que daría x² − 14x + 49."),
            ("(x + 7)²", "Aplicó el cuadrado del binomio con signo positivo, que daría x² + 14x + 49."),
            ("x(x − 49)", "Factorizó por factor común, que no aplica porque 49 no tiene x."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización de x² + 7x + 12?",
        "(x + 3)(x + 4)",
        "Para un trinomio de la forma x² + bx + c se buscan dos números que multiplicados "
        "den c y sumados den b.\n\n"
        "1) Necesitas dos números cuyo producto sea 12 y cuya suma sea 7.\n"
        "2) Prueba los pares que dan 12: 1 y 12 suman 13; 2 y 6 suman 8; 3 y 4 suman 7. "
        "Este último sirve.\n"
        "3) La factorización es (x + 3)(x + 4).\n\n"
        "Verifica: x² + 4x + 3x + 12 = x² + 7x + 12.",
        [
            ("(x + 2)(x + 6)", "Eligió un par que multiplica 12 pero suma 8, no 7."),
            ("(x + 1)(x + 12)", "Eligió el par que multiplica 12 pero suma 13."),
            ("(x − 3)(x − 4)", "Usó los números correctos pero con signo negativo, lo que daría x² − 7x + 12."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "Si a + b = 9 y a · b = 20, ¿cuál es el valor de a² + b²?",
        "41",
        "No hace falta encontrar a y b por separado: sirve la identidad del cuadrado de "
        "una suma.\n\n"
        "1) Parte de (a + b)² = a² + 2ab + b².\n"
        "2) Despeja lo que buscas: a² + b² = (a + b)² − 2ab.\n"
        "3) Reemplaza los datos: 9² − 2 · 20 = 81 − 40 = 41.\n\n"
        "Control: los números que cumplen ambas condiciones son 4 y 5, y "
        "4² + 5² = 16 + 25 = 41.",
        [
            ("81", "Calculó (a + b)² y olvidó restar el doble producto."),
            ("121", "Sumó el doble producto en lugar de restarlo: 81 + 40."),
            ("61", "Restó una sola vez el producto (81 − 20) en vez del doble producto."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "¿Cuál es el resultado de simplificar (x² − 9)/(x + 3), con x ≠ −3?",
        "x − 3",
        "Conviene factorizar el numerador para buscar un factor común con el "
        "denominador.\n\n"
        "1) El numerador es una diferencia de cuadrados: x² − 9 = (x + 3)(x − 3).\n"
        "2) La fracción queda [(x + 3)(x − 3)]/(x + 3).\n"
        "3) Como x ≠ −3, el factor (x + 3) no es cero y se puede cancelar.\n"
        "4) Queda x − 3.\n\n"
        "Verifica con x = 5: el original da (25 − 9)/8 = 2, y x − 3 = 2.",
        [
            ("x + 3", "Canceló el factor equivocado, dejando el que era igual al denominador."),
            ("x² − 3", "Canceló el 3 y la x por separado, que no es válido: solo se cancelan factores completos."),
            ("x − 9", "Restó el denominador al numerador en vez de factorizar y cancelar."),
        ],
    ),

    # ---------- ÁLGEBRA: ecuaciones e inecuaciones lineales ----------
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 4x − 7 = 13?",
        "x = 5",
        "Se despeja x dejando los números a un lado y la incógnita al otro.\n\n"
        "1) Suma 7 a ambos lados: 4x = 13 + 7 = 20.\n"
        "2) Divide ambos lados por 4: x = 20 ÷ 4 = 5.\n\n"
        "Verifica en la ecuación original: 4 · 5 − 7 = 20 − 7 = 13.",
        [
            ("x = 1,5", "Restó 7 en lugar de sumarlo al pasar al otro lado: (13 − 7)/4."),
            ("x = 80", "Multiplicó por 4 en vez de dividir."),
            ("x = 3,25", "Dividió 13 por 4 sin ocuparse antes del −7."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de 3(x − 2) = 2x + 5?",
        "x = 11",
        "Primero se elimina el paréntesis y después se agrupan las x a un lado.\n\n"
        "1) Distribuye el 3: 3x − 6 = 2x + 5.\n"
        "2) Resta 2x a ambos lados: x − 6 = 5.\n"
        "3) Suma 6 a ambos lados: x = 11.\n\n"
        "Verifica: 3(11 − 2) = 3 · 9 = 27, y 2 · 11 + 5 = 27.",
        [
            ("x = 1", "No distribuyó el 3 al −2, resolviendo 3x − 2 = 2x + 5."),
            ("x = −1", "Al agrupar las x restó en el sentido equivocado."),
            ("x = 5,5", "Sumó las x de ambos lados (5x) en lugar de restarlas."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es el conjunto solución de la inecuación 2x + 1 < 9?",
        "x < 4",
        "Una inecuación se despeja como una ecuación, cuidando el sentido del signo.\n\n"
        "1) Resta 1 a ambos lados: 2x < 8.\n"
        "2) Divide por 2, que es positivo, así que el signo < se mantiene: x < 4.\n\n"
        "Comprueba con un valor: x = 3 cumple (2 · 3 + 1 = 7 < 9), y x = 5 no "
        "(2 · 5 + 1 = 11).",
        [
            ("x > 4", "Invirtió el signo de la desigualdad, algo que solo corresponde al dividir por un número negativo."),
            ("x < 5", "Dividió 9 por 2 antes de restar el 1."),
            ("x < 8", "Restó el 1 pero no dividió por 2."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "¿Cuál es el conjunto solución de −3x + 4 ≥ 16?",
        "x ≤ −4",
        "El punto clave es que al dividir por un número negativo la desigualdad cambia "
        "de sentido.\n\n"
        "1) Resta 4 a ambos lados: −3x ≥ 12.\n"
        "2) Divide por −3. Como es negativo, el ≥ se transforma en ≤: x ≤ −4.\n\n"
        "Comprueba: x = −5 cumple, porque −3(−5) + 4 = 19 ≥ 16. En cambio x = 0 no, "
        "porque da 4.",
        [
            ("x ≥ −4", "Dividió por −3 sin invertir el sentido de la desigualdad."),
            ("x ≤ 4", "Perdió el signo negativo al dividir."),
            ("x ≥ 4", "Cometió los dos errores: no invirtió el signo y perdió el negativo."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "La suma de tres números consecutivos es 72. ¿Cuál es el mayor de ellos?",
        "25",
        "Conviene nombrar el menor con una letra y escribir los otros en función de él.\n\n"
        "1) Sea x el menor. Los tres son x, x + 1 y x + 2.\n"
        "2) Plantea la suma: x + (x + 1) + (x + 2) = 72.\n"
        "3) Reduce: 3x + 3 = 72, entonces 3x = 69 y x = 23.\n"
        "4) Los números son 23, 24 y 25, así que el mayor es 25.\n\n"
        "Atajo: al ser consecutivos, el del medio es el promedio: 72 ÷ 3 = 24, y el "
        "mayor es 25.",
        [
            ("24", "Encontró el número del medio y lo entregó como respuesta."),
            ("23", "Entregó el menor de los tres en lugar del mayor."),
            ("26", "Planteó los consecutivos partiendo desde x + 1 y se corrió un lugar."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "Si 5x + 3 = 2x + 18, ¿cuál es el valor de x?",
        "5",
        "Se agrupan las x a un lado y los números al otro.\n\n"
        "1) Resta 2x a ambos lados: 3x + 3 = 18.\n"
        "2) Resta 3 a ambos lados: 3x = 15.\n"
        "3) Divide por 3: x = 5.\n\n"
        "Verifica: 5 · 5 + 3 = 28 y 2 · 5 + 18 = 28.",
        [
            ("3", "Restó mal los términos numéricos, llegando a 3x = 9."),
            ("7", "Sumó las x de ambos lados en lugar de restarlas."),
            ("2,1", "Dividió 18 − 3 por 7, sumando los coeficientes de x."),
        ],
    ),
]

QUESTIONS += [
    # ---------- ÁLGEBRA: sistemas 2x2 ----------
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema x + y = 12 ; x − y = 2?",
        "x = 7 , y = 5",
        "Con una incógnita de signos opuestos, sumar las ecuaciones la elimina.\n\n"
        "1) Suma ambas: (x + y) + (x − y) = 12 + 2, o sea 2x = 14.\n"
        "2) Despeja: x = 7.\n"
        "3) Reemplaza en la primera: 7 + y = 12, entonces y = 5.\n\n"
        "Verifica en la segunda: 7 − 5 = 2.",
        [
            ("x = 5 , y = 7", "Intercambió los valores de las incógnitas."),
            ("x = 6 , y = 6", "Repartió el 12 en partes iguales sin usar la segunda ecuación."),
            ("x = 14 , y = 2", "Sumó las ecuaciones pero no dividió por 2 al despejar x."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es el valor de y en el sistema 2x + y = 11 ; x − y = 1?",
        "3",
        "Conviene sumar las ecuaciones para eliminar y, hallar x y luego volver.\n\n"
        "1) Suma: (2x + y) + (x − y) = 11 + 1, o sea 3x = 12.\n"
        "2) Despeja: x = 4.\n"
        "3) Reemplaza en la segunda: 4 − y = 1, entonces y = 3.\n\n"
        "Verifica en la primera: 2 · 4 + 3 = 11.",
        [
            ("4", "Entregó el valor de x en lugar del de y."),
            ("5", "Reemplazó x = 4 en la primera ecuación pero despejó mal el término y."),
            ("−3", "Cambió el signo al despejar y en la segunda ecuación."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "En una feria, 3 kilos de manzanas y 2 de peras cuestan $4.600. "
        "Un kilo de manzanas y 2 de peras cuestan $2.600. "
        "¿Cuánto cuesta el kilo de manzanas?",
        "$1.000",
        "Se traduce a un sistema y se elimina la incógnita que aparece igual en ambas "
        "ecuaciones.\n\n"
        "1) Sea m el precio del kilo de manzanas y p el de peras: "
        "3m + 2p = 4.600 y m + 2p = 2.600.\n"
        "2) Ambas tienen 2p, así que resta la segunda de la primera: "
        "2m = 2.000.\n"
        "3) Despeja: m = 1.000.\n\n"
        "Control: si m = 1.000, entonces 2p = 1.600 y p = 800. "
        "Y 3 · 1.000 + 2 · 800 = 4.600.",
        [
            ("$800", "Entregó el precio del kilo de peras en lugar del de manzanas."),
            ("$2.000", "Restó bien las ecuaciones pero no dividió por 2 al despejar m."),
            ("$1.533", "Dividió el total de la primera ecuación por los 3 kilos de manzanas, ignorando las peras."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es el valor de x + y si 3x + 2y = 16 y 2x + 3y = 14?",
        "6",
        "No hace falta resolver el sistema completo: sumar ambas ecuaciones entrega "
        "directamente lo que se pide.\n\n"
        "1) Suma las dos ecuaciones: (3x + 2x) + (2y + 3y) = 16 + 14, "
        "o sea 5x + 5y = 30.\n"
        "2) Factoriza el 5: 5(x + y) = 30.\n"
        "3) Divide por 5: x + y = 6.\n\n"
        "Si quieres comprobar, los valores son x = 4 e y = 2, cuya suma es 6.",
        [
            ("30", "Sumó las ecuaciones pero no dividió por 5 al despejar."),
            ("2", "Restó las ecuaciones en lugar de sumarlas, obteniendo x − y."),
            ("4", "Resolvió el sistema y entregó solo el valor de x."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es la solución del sistema 4x − 3y = 6 ; 2x + y = 8?",
        "x = 3 , y = 2",
        "Conviene igualar coeficientes para eliminar una incógnita.\n\n"
        "1) Multiplica la segunda ecuación por 3: 6x + 3y = 24.\n"
        "2) Súmala con la primera, donde y tiene signo opuesto: "
        "(4x − 3y) + (6x + 3y) = 6 + 24, es decir, 10x = 30.\n"
        "3) Despeja: x = 3.\n"
        "4) Reemplaza en 2x + y = 8: 6 + y = 8, entonces y = 2.\n\n"
        "Verifica en la primera: 4 · 3 − 3 · 2 = 12 − 6 = 6.",
        [
            ("x = 2 , y = 3", "Intercambió los valores de las incógnitas."),
            ("x = 3 , y = 14", "Reemplazó x en la primera ecuación con un error de signo al despejar y."),
            ("x = 1,5 , y = 5", "Multiplicó solo un lado de la segunda ecuación al igualar coeficientes."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "Si x = 2y y x + y = 12, ¿cuál es el valor de y?",
        "4",
        "Cuando una incógnita ya está despejada, conviene sustituirla.\n\n"
        "1) Reemplaza x = 2y en la segunda ecuación: 2y + y = 12.\n"
        "2) Reduce: 3y = 12.\n"
        "3) Despeja: y = 4.\n\n"
        "Entonces x = 2 · 4 = 8, y efectivamente 8 + 4 = 12.",
        [
            ("8", "Entregó el valor de x en lugar del de y."),
            ("6", "Repartió el 12 en dos partes iguales sin usar la relación x = 2y."),
            ("12", "Reemplazó pero no resolvió la ecuación resultante."),
        ],
    ),

    # ---------- ÁLGEBRA: ecuaciones cuadráticas ----------
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² − 25 = 0?",
        "x = 5 y x = −5",
        "Una ecuación de la forma x² = c tiene dos soluciones opuestas.\n\n"
        "1) Despeja: x² = 25.\n"
        "2) Saca raíz considerando ambos signos: x = 5 o x = −5.\n\n"
        "También sirve factorizar como diferencia de cuadrados: (x + 5)(x − 5) = 0.",
        [
            ("x = 5", "Consideró solo la raíz positiva y perdió la negativa."),
            ("x = 12,5 y x = −12,5", "Dividió 25 por 2 en lugar de sacar la raíz cuadrada."),
            ("x = 25", "No aplicó la raíz cuadrada al despejar."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² + x − 12 = 0?",
        "x = 3 y x = −4",
        "Se buscan dos números que multiplicados den −12 y sumados den 1.\n\n"
        "1) Como el producto es negativo, los números tienen signos distintos.\n"
        "2) Prueba pares: 3 y −4 multiplican −12 y suman −1; −3 y 4 suman 1. "
        "El par que sirve es −3 y 4… revisando el signo del término central, los "
        "factores correctos son (x − 3)(x + 4).\n"
        "3) Iguala cada factor a cero: x = 3 y x = −4.\n\n"
        "Verifica con x = 3: 9 + 3 − 12 = 0. Y con x = −4: 16 − 4 − 12 = 0.",
        [
            ("x = −3 y x = 4", "Invirtió los signos de ambas soluciones."),
            ("x = 2 y x = −6", "Eligió un par que multiplica −12 pero suma −4."),
            ("x = 12 y x = 1", "Tomó los coeficientes de la ecuación como soluciones."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² − 7x = 0?",
        "x = 0 y x = 7",
        "Cuando no hay término independiente conviene factorizar por factor común, no "
        "usar la fórmula.\n\n"
        "1) Saca x como factor común: x(x − 7) = 0.\n"
        "2) Iguala cada factor a cero: x = 0, o bien x − 7 = 0, que da x = 7.\n\n"
        "Un error frecuente es dividir toda la ecuación por x: eso elimina la solución "
        "x = 0, que sí es válida.",
        [
            ("x = 7", "Dividió ambos lados por x, perdiendo la solución x = 0."),
            ("x = 0 y x = −7", "Se equivocó en el signo al despejar el segundo factor."),
            ("x = 7 y x = −7", "Trató la ecuación como si fuera x² = 49."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuáles son las soluciones de 2x² − 7x + 3 = 0?",
        "x = 3 y x = 1/2",
        "Con el coeficiente de x² distinto de 1 conviene aplicar la fórmula general.\n\n"
        "1) Identifica a = 2, b = −7, c = 3.\n"
        "2) Calcula el discriminante: b² − 4ac = 49 − 4 · 2 · 3 = 49 − 24 = 25.\n"
        "3) Su raíz es 5, así que x = (7 ± 5)/(2 · 2) = (7 ± 5)/4.\n"
        "4) Las soluciones son (7 + 5)/4 = 3 y (7 − 5)/4 = 1/2.\n\n"
        "Verifica con x = 3: 2 · 9 − 21 + 3 = 0.",
        [
            ("x = 3 y x = 2", "Dividió por a solo en una de las dos soluciones."),
            ("x = −3 y x = −1/2", "Usó −b con el signo cambiado en la fórmula."),
            ("x = 1 y x = 3/2", "Calculó mal el discriminante, usando 49 − 24 como si fuera 1."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuántas soluciones reales tiene la ecuación x² + 2x + 5 = 0?",
        "Ninguna",
        "El discriminante determina la cantidad de soluciones reales sin necesidad de "
        "resolver.\n\n"
        "1) Identifica a = 1, b = 2, c = 5.\n"
        "2) Calcula b² − 4ac = 4 − 4 · 1 · 5 = 4 − 20 = −16.\n"
        "3) El discriminante es negativo, y no existe raíz cuadrada real de un número "
        "negativo, así que la ecuación no tiene soluciones reales.\n\n"
        "Interpretación gráfica: la parábola abre hacia arriba y su vértice queda sobre "
        "el eje X, por lo que nunca lo corta.",
        [
            ("Dos", "Supuso que toda ecuación cuadrática tiene siempre dos soluciones reales."),
            ("Una", "Confundió el discriminante negativo con un discriminante igual a cero."),
            ("Infinitas", "Confundió una ecuación sin soluciones reales con una identidad."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "Si las soluciones de una ecuación cuadrática son x = 5 y x = −2, "
        "¿cuál es la ecuación en su forma factorizada igualada a cero?",
        "(x − 5)(x + 2) = 0",
        "Cada solución se transforma en un factor con el signo invertido.\n\n"
        "1) La solución x = 5 proviene del factor (x − 5).\n"
        "2) La solución x = −2 proviene del factor (x + 2).\n"
        "3) El producto igualado a cero es (x − 5)(x + 2) = 0.\n\n"
        "Al desarrollar queda x² − 3x − 10 = 0, y puedes comprobar que x = 5 la "
        "satisface: 25 − 15 − 10 = 0.",
        [
            ("(x + 5)(x − 2) = 0", "Copió los signos de las soluciones en vez de invertirlos."),
            ("(x − 5)(x − 2) = 0", "Invirtió el signo de una solución pero no el de la otra."),
            ("(x + 5)(x + 2) = 0", "Mantuvo ambos signos tal como aparecen en las soluciones."),
        ],
    ),
]

QUESTIONS += [
    # ---------- ÁLGEBRA: funciones ----------
    _q(
        "alg_funciones", "facil",
        "Si f(x) = 3x − 4, ¿cuál es el valor de f(6)?",
        "14",
        "Evaluar una función es reemplazar la x por el valor indicado.\n\n"
        "1) Sustituye x por 6: f(6) = 3 · 6 − 4.\n"
        "2) Multiplica primero: 3 · 6 = 18.\n"
        "3) Resta: 18 − 4 = 14.",
        [
            ("6", "Entregó el valor que se reemplaza en lugar del resultado de la función."),
            ("18", "Multiplicó pero olvidó restar el 4."),
            ("2", "Restó antes de multiplicar: 3 · (6 − 4)."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es la pendiente de la recta que pasa por los puntos (1, 2) y (5, 10)?",
        "2",
        "La pendiente es el cambio vertical dividido por el cambio horizontal entre dos "
        "puntos.\n\n"
        "1) Calcula la diferencia de las y: 10 − 2 = 8.\n"
        "2) Calcula la diferencia de las x en el mismo orden: 5 − 1 = 4.\n"
        "3) Divide: 8 ÷ 4 = 2.\n\n"
        "Interpretación: por cada unidad que avanza x, la recta sube 2 unidades.",
        [
            ("1/2", "Dividió el cambio horizontal por el vertical, invirtiendo la fórmula."),
            ("8", "Calculó solo la diferencia de las y sin dividir."),
            ("4", "Calculó solo la diferencia de las x."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿En qué punto la recta y = 2x − 6 corta al eje X?",
        "(3, 0)",
        "Un punto está sobre el eje X cuando su coordenada y vale cero.\n\n"
        "1) Iguala la función a cero: 2x − 6 = 0.\n"
        "2) Despeja: 2x = 6, entonces x = 3.\n"
        "3) El punto de corte es (3, 0).\n\n"
        "No confundir con el corte en el eje Y, que se obtiene con x = 0 y da (0, −6).",
        [
            ("(0, −6)", "Calculó el corte con el eje Y en vez de con el eje X."),
            ("(−3, 0)", "Se equivocó en el signo al despejar x."),
            ("(6, 0)", "Despejó sin dividir por el coeficiente 2."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "La función f(x) = 2x + b cumple f(3) = 11. ¿Cuál es el valor de b?",
        "5",
        "Se reemplaza el dato conocido y se despeja el parámetro.\n\n"
        "1) Evalúa en x = 3: f(3) = 2 · 3 + b = 6 + b.\n"
        "2) Iguala al valor dado: 6 + b = 11.\n"
        "3) Despeja: b = 11 − 6 = 5.\n\n"
        "Verifica: f(x) = 2x + 5, y f(3) = 6 + 5 = 11.",
        [
            ("17", "Sumó 6 en lugar de restarlo al despejar."),
            ("11", "Tomó el valor de la función como si fuera directamente b."),
            ("3", "Entregó el valor de x en lugar del parámetro b."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "Una recta tiene pendiente 4 y pasa por el punto (0, −3). ¿Cuál es su ecuación?",
        "y = 4x − 3",
        "El punto (0, −3) está sobre el eje Y, así que entrega directamente el "
        "coeficiente de posición.\n\n"
        "1) La forma principal de la recta es y = mx + n, donde m es la pendiente y n "
        "el valor de y cuando x = 0.\n"
        "2) La pendiente dada es m = 4.\n"
        "3) Como la recta pasa por (0, −3), el coeficiente de posición es n = −3.\n"
        "4) La ecuación es y = 4x − 3.",
        [
            ("y = 4x + 3", "Copió el 3 sin su signo negativo."),
            ("y = −3x + 4", "Intercambió la pendiente con el coeficiente de posición."),
            ("y = 4x", "Ignoró el punto por el que pasa la recta."),
        ],
    ),

    # ---------- GEOMETRÍA: perímetros y áreas ----------
    _q(
        "geo_plana", "facil",
        "¿Cuál es el área de un triángulo de base 12 cm y altura 7 cm?",
        "42 cm²",
        "El área de un triángulo es la mitad del producto entre base y altura.\n\n"
        "1) Multiplica base por altura: 12 · 7 = 84.\n"
        "2) Divide por 2: 84 ÷ 2 = 42.\n"
        "3) Como es área, la unidad va al cuadrado: 42 cm².",
        [
            ("84 cm²", "Multiplicó base por altura pero olvidó dividir por 2."),
            ("19 cm²", "Sumó base y altura en lugar de multiplicarlas."),
            ("38 cm", "Calculó algo parecido a un perímetro en vez del área."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Una circunferencia tiene radio 5 cm. ¿Cuál es su área? (usa π ≈ 3,14)",
        "78,5 cm²",
        "El área del círculo es π multiplicado por el radio al cuadrado.\n\n"
        "1) Eleva el radio al cuadrado: 5² = 25.\n"
        "2) Multiplica por π: 3,14 · 25 = 78,5.\n"
        "3) El área es 78,5 cm².\n\n"
        "Ojo con no confundirla con el perímetro, que es 2πr = 31,4 cm.",
        [
            ("31,4 cm²", "Calculó el perímetro de la circunferencia en lugar del área."),
            ("15,7 cm²", "Multiplicó π por el radio sin elevarlo al cuadrado."),
            ("157 cm²", "Usó el diámetro en lugar del radio al elevar al cuadrado."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Un rectángulo tiene perímetro 36 cm y su largo mide 11 cm. "
        "¿Cuál es su área?",
        "77 cm²",
        "Primero se obtiene el ancho a partir del perímetro y después se calcula el "
        "área.\n\n"
        "1) El perímetro es 2(largo + ancho): 2(11 + a) = 36.\n"
        "2) Divide por 2: 11 + a = 18, entonces a = 7 cm.\n"
        "3) El área es largo por ancho: 11 · 7 = 77 cm².",
        [
            ("396 cm²", "Multiplicó el perímetro por el largo en lugar de hallar el ancho."),
            ("275 cm²", "Restó el largo al perímetro sin dividir por 2, usando 25 como ancho."),
            ("36 cm²", "Entregó el perímetro como si fuera el área."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Un cuadrado de lado 10 cm tiene inscrito un círculo que toca sus cuatro lados. "
        "¿Cuál es el área de la región del cuadrado que queda fuera del círculo? "
        "(usa π ≈ 3,14)",
        "21,5 cm²",
        "Se calcula el área de cada figura y se restan.\n\n"
        "1) Área del cuadrado: 10 · 10 = 100 cm².\n"
        "2) El círculo inscrito toca los cuatro lados, así que su diámetro es igual al "
        "lado: 10 cm, y su radio es 5 cm.\n"
        "3) Área del círculo: 3,14 · 5² = 78,5 cm².\n"
        "4) Resta: 100 − 78,5 = 21,5 cm².",
        [
            ("78,5 cm²", "Entregó el área del círculo en vez de la región que queda fuera."),
            ("−214 cm²", "Usó el lado como radio del círculo, obteniendo un área mayor que la del cuadrado."),
            ("100 cm²", "Entregó el área del cuadrado sin descontar el círculo."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Si el lado de un cuadrado se duplica, ¿qué ocurre con su área?",
        "Queda multiplicada por 4",
        "El área depende del cuadrado del lado, así que no crece en la misma proporción "
        "que este.\n\n"
        "1) Con lado L, el área es L².\n"
        "2) Al duplicar el lado queda 2L, y su área es (2L)² = 4L².\n"
        "3) La nueva área es 4 veces la original.\n\n"
        "Ejemplo concreto: un cuadrado de lado 3 tiene área 9; uno de lado 6 tiene "
        "área 36, que es 9 · 4.",
        [
            ("Queda multiplicada por 2", "Aplicó al área el mismo factor que al lado, sin considerar que el área depende del cuadrado."),
            ("Queda multiplicada por 8", "Usó el factor que corresponde al volumen de un cuerpo, no al área de una figura plana."),
            ("No cambia", "Supuso que el área es independiente de la medida del lado."),
        ],
    ),
]

QUESTIONS += [
    # ---------- GEOMETRÍA: Pitágoras ----------
    _q(
        "geo_pitagoras", "facil",
        "En un triángulo rectángulo los catetos miden 15 cm y 20 cm. "
        "¿Cuánto mide la hipotenusa?",
        "25 cm",
        "El teorema de Pitágoras relaciona los catetos con la hipotenusa.\n\n"
        "1) Eleva cada cateto al cuadrado: 15² = 225 y 20² = 400.\n"
        "2) Súmalos: 225 + 400 = 625.\n"
        "3) Saca la raíz: √625 = 25 cm.\n\n"
        "Es el triángulo 3-4-5 amplificado por 5.",
        [
            ("35 cm", "Sumó los catetos directamente sin elevarlos al cuadrado."),
            ("625 cm", "Sumó los cuadrados pero no sacó la raíz."),
            ("13,2 cm", "Restó los cuadrados en lugar de sumarlos."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "En un triángulo rectángulo la hipotenusa mide 25 cm y un cateto 7 cm. "
        "¿Cuánto mide el otro cateto?",
        "24 cm",
        "Cuando el dato desconocido es un cateto, su cuadrado se despeja restando.\n\n"
        "1) Plantea: 7² + c² = 25².\n"
        "2) Calcula los cuadrados conocidos: 49 + c² = 625.\n"
        "3) Despeja: c² = 625 − 49 = 576.\n"
        "4) Saca la raíz: c = 24 cm.",
        [
            ("26 cm", "Sumó los cuadrados en vez de restarlos, tratando la hipotenusa como cateto."),
            ("18 cm", "Restó las medidas directamente (25 − 7) sin elevar al cuadrado."),
            ("576 cm", "Despejó el cuadrado del cateto pero no sacó la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "¿Cuánto mide la diagonal de un cuadrado de lado 6 cm?",
        "6√2 cm",
        "La diagonal divide el cuadrado en dos triángulos rectángulos cuyos catetos son "
        "los lados.\n\n"
        "1) Aplica Pitágoras con ambos catetos iguales a 6: d² = 6² + 6² = 36 + 36 = 72.\n"
        "2) Saca la raíz: d = √72.\n"
        "3) Simplifica: 72 = 36 · 2, así que √72 = 6√2 cm.\n\n"
        "En cualquier cuadrado la diagonal mide el lado multiplicado por √2, "
        "aproximadamente 8,49 cm en este caso.",
        [
            ("12 cm", "Sumó los lados en lugar de aplicar el teorema."),
            ("72 cm", "Calculó el cuadrado de la diagonal pero no sacó la raíz."),
            ("3√2 cm", "Dividió el lado por 2 antes de aplicar el teorema."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "Un poste de 8 m se sujeta con un cable tensado desde su punta hasta un punto "
        "del suelo ubicado a 15 m de la base. ¿Cuánto mide el cable?",
        "17 m",
        "El poste, el suelo y el cable forman un triángulo rectángulo donde el cable es "
        "la hipotenusa.\n\n"
        "1) Plantea: 8² + 15² = c².\n"
        "2) Calcula: 64 + 225 = 289.\n"
        "3) Saca la raíz: c = 17 m.\n\n"
        "El cable tiene que ser más largo que la distancia al suelo, y 17 > 15 lo "
        "cumple.",
        [
            ("23 m", "Sumó las medidas directamente sin elevarlas al cuadrado."),
            ("12,7 m", "Restó los cuadrados, como si buscara un cateto en vez de la hipotenusa."),
            ("289 m", "Sumó los cuadrados pero no sacó la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "¿Cuál de estos tríos de medidas NO puede formar un triángulo rectángulo?",
        "6, 8, 12",
        "Un trío forma triángulo rectángulo solo si el cuadrado del lado mayor es igual "
        "a la suma de los cuadrados de los otros dos.\n\n"
        "1) Para 6, 8, 12: 6² + 8² = 36 + 64 = 100, pero 12² = 144. "
        "No coinciden, así que no es rectángulo.\n"
        "2) Para 5, 12, 13: 25 + 144 = 169 = 13². Sí cumple.\n"
        "3) Para 9, 12, 15: 81 + 144 = 225 = 15². Sí cumple.\n"
        "4) Para 8, 15, 17: 64 + 225 = 289 = 17². Sí cumple.",
        [
            ("5, 12, 13", "Este trío sí cumple el teorema: 25 + 144 = 169."),
            ("9, 12, 15", "Este trío sí cumple: es el 3-4-5 amplificado por 3."),
            ("8, 15, 17", "Este trío sí cumple: 64 + 225 = 289."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "En un triángulo rectángulo los catetos miden 3 cm y 4 cm. "
        "¿Cuál es su área?",
        "6 cm²",
        "En un triángulo rectángulo los catetos son perpendiculares, así que uno hace de "
        "base y el otro de altura.\n\n"
        "1) Multiplica los catetos: 3 · 4 = 12.\n"
        "2) Divide por 2: 12 ÷ 2 = 6 cm².\n\n"
        "No se necesita la hipotenusa, que en este caso mide 5 cm, para calcular el "
        "área.",
        [
            ("12 cm²", "Multiplicó los catetos pero no dividió por 2."),
            ("5 cm²", "Calculó la hipotenusa en lugar del área."),
            ("7,5 cm²", "Usó la hipotenusa como una de las medidas del área."),
        ],
    ),

    # ---------- GEOMETRÍA: transformaciones isométricas ----------
    _q(
        "geo_transformaciones", "facil",
        "El punto P(6, 1) se traslada según el vector (−4, −3). "
        "¿Cuáles son las coordenadas del punto trasladado?",
        "(2, −2)",
        "En una traslación se suma cada componente del vector a la coordenada "
        "correspondiente, respetando los signos.\n\n"
        "1) Coordenada x: 6 + (−4) = 2.\n"
        "2) Coordenada y: 1 + (−3) = −2.\n"
        "3) El punto trasladado es (2, −2).",
        [
            ("(10, 4)", "Restó el vector en lugar de sumarlo, ignorando que sus componentes ya son negativas."),
            ("(−4, −3)", "Entregó el vector de traslación como si fuera el punto final."),
            ("(−2, 2)", "Cambió el signo de ambas coordenadas del resultado."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "¿Cuáles son las coordenadas del punto B(−2, 7) al reflejarlo respecto del "
        "eje X?",
        "(−2, −7)",
        "En una reflexión respecto del eje X la coordenada x se conserva y la y cambia "
        "de signo.\n\n"
        "1) La coordenada x se mantiene en −2.\n"
        "2) La coordenada y pasa de 7 a −7.\n"
        "3) El punto reflejado es (−2, −7).\n\n"
        "Respecto del eje Y, en cambio, el que cambiaría de signo sería el −2.",
        [
            ("(2, 7)", "Reflejó respecto del eje Y en lugar del eje X."),
            ("(2, −7)", "Cambió el signo de ambas coordenadas, que corresponde a una rotación en 180°."),
            ("(7, −2)", "Intercambió las coordenadas en vez de reflejar."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "El punto B(2, 0) se rota 90° en sentido antihorario en torno al origen. "
        "¿Cuáles son sus nuevas coordenadas?",
        "(0, 2)",
        "Una rotación de 90° antihoraria en torno al origen transforma el punto (x, y) "
        "en (−y, x).\n\n"
        "1) Aplica la regla con x = 2 e y = 0: el nuevo punto es (−0, 2).\n"
        "2) Como −0 es 0, queda (0, 2).\n\n"
        "Tiene sentido geométrico: el punto estaba sobre el eje X a distancia 2 del "
        "origen, y al girar un cuarto de vuelta hacia arriba queda sobre el eje Y a la "
        "misma distancia.",
        [
            ("(0, −2)", "Rotó en sentido horario en lugar de antihorario."),
            ("(−2, 0)", "Rotó 180° en vez de 90°."),
            ("(2, 0)", "Dejó el punto sin cambios."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "¿Cuál de estas transformaciones NO conserva las medidas de la figura "
        "original?",
        "La homotecia de razón 2",
        "Las transformaciones isométricas conservan las medidas de la figura; solo "
        "cambian su posición u orientación.\n\n"
        "1) La traslación mueve la figura sin deformarla.\n"
        "2) La rotación la gira manteniendo todas sus medidas.\n"
        "3) La reflexión la invierte, pero lados y ángulos siguen iguales.\n"
        "4) La homotecia de razón 2 duplica cada longitud, así que la figura resultante "
        "es semejante pero no congruente con la original.",
        [
            ("La traslación", "Es una isometría: mueve la figura conservando todas sus medidas."),
            ("La rotación en 90°", "Es una isometría: gira la figura sin alterar sus medidas."),
            ("La reflexión respecto del eje Y", "Es una isometría: invierte la figura conservando lados y ángulos."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "El punto P(−3, 4) se refleja respecto del eje Y y el resultado se traslada "
        "según el vector (2, −1). ¿Cuál es el punto final?",
        "(5, 3)",
        "Se aplican las transformaciones en el orden indicado.\n\n"
        "1) Reflexión respecto del eje Y: cambia el signo de la x. "
        "El punto (−3, 4) pasa a (3, 4).\n"
        "2) Traslación según (2, −1): suma cada componente. "
        "x: 3 + 2 = 5; y: 4 + (−1) = 3.\n"
        "3) El punto final es (5, 3).",
        [
            ("(−1, 3)", "Trasladó primero y reflejó después, alterando el orden pedido."),
            ("(5, 5)", "Restó la componente y del vector en lugar de sumarla."),
            ("(3, 4)", "Se detuvo en la reflexión y no aplicó la traslación."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "¿Cuáles son las coordenadas del punto C(−6, 2) al reflejarlo respecto del "
        "eje Y?",
        "(6, 2)",
        "En una reflexión respecto del eje Y cambia el signo de la coordenada x y la y "
        "se conserva.\n\n"
        "1) La coordenada x pasa de −6 a 6.\n"
        "2) La coordenada y se mantiene en 2.\n"
        "3) El punto reflejado es (6, 2).",
        [
            ("(−6, −2)", "Reflejó respecto del eje X en lugar del eje Y."),
            ("(6, −2)", "Cambió el signo de ambas coordenadas."),
            ("(2, −6)", "Intercambió las coordenadas en vez de reflejar."),
        ],
    ),
]

QUESTIONS += [
    # ---------- GEOMETRÍA: cuerpos geométricos ----------
    _q(
        "geo_solidos", "medio",
        "Un paralelepípedo mide 5 cm de largo, 3 cm de ancho y 2 cm de alto. "
        "¿Cuál es su área total?",
        "62 cm²",
        "El área total es la suma de las seis caras, que son iguales dos a dos.\n\n"
        "1) Cara largo-ancho: 5 · 3 = 15, y hay dos: 30.\n"
        "2) Cara largo-alto: 5 · 2 = 10, y hay dos: 20.\n"
        "3) Cara ancho-alto: 3 · 2 = 6, y hay dos: 12.\n"
        "4) Suma todo: 30 + 20 + 12 = 62 cm².",
        [
            ("30 cm²", "Calculó el volumen (5 · 3 · 2) en lugar del área total."),
            ("31 cm²", "Sumó una sola vez cada par de caras, olvidando que van dobles."),
            ("10 cm²", "Sumó las tres dimensiones en vez de calcular las caras."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Si el radio de una esfera se duplica, ¿por cuánto queda multiplicado su "
        "volumen?",
        "Por 8",
        "El volumen de la esfera depende del cubo del radio, así que el factor se eleva "
        "al cubo.\n\n"
        "1) El volumen es (4/3)πr³.\n"
        "2) Al duplicar el radio queda 2r, y su cubo es (2r)³ = 8r³.\n"
        "3) El nuevo volumen es 8 veces el original.\n\n"
        "Como referencia, si el radio se duplica el área de la superficie se "
        "cuadruplica, porque depende del cuadrado del radio.",
        [
            ("Por 2", "Aplicó al volumen el mismo factor que al radio."),
            ("Por 4", "Usó el factor que corresponde al área de la superficie, no al volumen."),
            ("Por 6", "Multiplicó el factor por 3 en lugar de elevarlo al cubo."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Un cono tiene radio 6 cm y altura 10 cm. ¿Cuál es su volumen? "
        "(usa π ≈ 3,14)",
        "376,8 cm³",
        "El volumen del cono es un tercio del volumen del cilindro de igual base y "
        "altura.\n\n"
        "1) Área de la base: 3,14 · 6² = 3,14 · 36 = 113,04 cm².\n"
        "2) Multiplica por la altura: 113,04 · 10 = 1.130,4.\n"
        "3) Divide por 3: 1.130,4 ÷ 3 = 376,8 cm³.",
        [
            ("1130,4 cm³", "Calculó el volumen del cilindro y olvidó dividir por 3."),
            ("113,04 cm³", "Se quedó en el área de la base sin usar la altura."),
            ("188,4 cm³", "Dividió por 2 en lugar de por 3."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "¿Cuántas aristas tiene un cubo?",
        "12",
        "Conviene contarlas por grupos según su dirección.\n\n"
        "1) Un cubo tiene 4 aristas verticales.\n"
        "2) Tiene 4 aristas en la cara superior.\n"
        "3) Tiene 4 aristas en la cara inferior.\n"
        "4) En total: 4 + 4 + 4 = 12 aristas.\n\n"
        "Además tiene 6 caras y 8 vértices.",
        [
            ("6", "Contó las caras en lugar de las aristas."),
            ("8", "Contó los vértices en lugar de las aristas."),
            ("4", "Contó solo las aristas de una cara."),
        ],
    ),

    # ---------- PROBABILIDAD: estadística descriptiva ----------
    _q(
        "prob_estadistica_desc", "facil",
        "¿Cuál es el promedio de los datos 4, 8, 10, 6 y 12?",
        "8",
        "El promedio es la suma de los datos dividida por su cantidad.\n\n"
        "1) Suma: 4 + 8 + 10 + 6 + 12 = 40.\n"
        "2) Cuenta los datos: son 5.\n"
        "3) Divide: 40 ÷ 5 = 8.",
        [
            ("40", "Sumó los datos pero no dividió por la cantidad."),
            ("10", "Dividió por 4 en lugar de por 5, contando mal los datos."),
            ("6", "Entregó un dato de la lista en lugar del promedio."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "medio",
        "¿Cuál es la mediana de los datos 7, 3, 9, 1 y 5?",
        "5",
        "La mediana es el valor central una vez ordenados los datos.\n\n"
        "1) Ordena de menor a mayor: 1, 3, 5, 7, 9.\n"
        "2) Como son 5 datos, la posición central es la tercera.\n"
        "3) El tercer valor es 5.\n\n"
        "Con una cantidad par de datos habría que promediar los dos centrales.",
        [
            ("9", "Tomó el valor central sin ordenar previamente los datos."),
            ("5,8", "Calculó el promedio en lugar de la mediana."),
            ("4", "Promedió los dos valores que quedan a los lados del centro."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "medio",
        "En el conjunto 2, 5, 5, 7, 9, 5, 2, ¿cuál es la moda?",
        "5",
        "La moda es el valor que aparece con mayor frecuencia.\n\n"
        "1) Cuenta cada valor: el 2 aparece 2 veces, el 5 aparece 3 veces, el 7 una vez "
        "y el 9 una vez.\n"
        "2) El valor con más repeticiones es el 5.\n\n"
        "La moda no tiene por qué coincidir con el promedio ni con la mediana.",
        [
            ("2", "Eligió el valor que se repite pero no el de mayor frecuencia."),
            ("3", "Entregó la cantidad de repeticiones en lugar del valor que se repite."),
            ("5,3", "Calculó el promedio del conjunto en vez de la moda."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "dificil",
        "El promedio de cuatro números es 15. Si se agrega un quinto número y el nuevo "
        "promedio es 16, ¿cuál es el número agregado?",
        "20",
        "Conviene trabajar con las sumas totales, no con los promedios.\n\n"
        "1) La suma de los cuatro primeros es 4 · 15 = 60.\n"
        "2) Con el quinto dato, la suma debe ser 5 · 16 = 80.\n"
        "3) El número agregado es la diferencia: 80 − 60 = 20.\n\n"
        "Tiene sentido: para subir el promedio, el nuevo dato debe superar al promedio "
        "anterior.",
        [
            ("16", "Supuso que el dato agregado es igual al nuevo promedio."),
            ("1", "Restó los promedios entre sí en lugar de trabajar con las sumas."),
            ("31", "Sumó ambos promedios en vez de restar las sumas totales."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "dificil",
        "¿Cuál es el rango del conjunto 12, 4, 19, 7 y 15?",
        "15",
        "El rango es una medida de dispersión: la diferencia entre el dato mayor y el "
        "menor.\n\n"
        "1) Identifica el mayor: 19.\n"
        "2) Identifica el menor: 4.\n"
        "3) Resta: 19 − 4 = 15.\n\n"
        "El rango solo usa los extremos, por lo que un dato atípico lo altera por "
        "completo.",
        [
            ("11,4", "Calculó el promedio del conjunto en lugar del rango."),
            ("19", "Entregó el dato mayor sin restarle el menor."),
            ("12", "Entregó la mediana del conjunto ordenado."),
        ],
    ),
    _q(
        "prob_estadistica_desc", "facil",
        "En una prueba, 3 estudiantes obtuvieron nota 6 y 2 obtuvieron nota 4. "
        "¿Cuál es el promedio del grupo?",
        "5,2",
        "Con datos repetidos conviene usar el promedio ponderado.\n\n"
        "1) Suma las notas considerando las repeticiones: 3 · 6 + 2 · 4 = 18 + 8 = 26.\n"
        "2) Cuenta el total de estudiantes: 3 + 2 = 5.\n"
        "3) Divide: 26 ÷ 5 = 5,2.",
        [
            ("5", "Promedió solo las dos notas distintas (6 y 4) sin considerar cuántos las obtuvieron."),
            ("26", "Sumó las notas pero no dividió por la cantidad de estudiantes."),
            ("5,5", "Ponderó al revés, como si 2 estudiantes hubieran sacado 6 y 3 hubieran sacado 4."),
        ],
    ),
]

QUESTIONS += [
    # ---------- PROBABILIDAD: técnicas de conteo ----------
    _q(
        "prob_combinatoria", "facil",
        "Un menú ofrece 4 entradas y 5 platos de fondo. ¿Cuántas combinaciones "
        "distintas de entrada y fondo se pueden armar?",
        "20",
        "Cuando hay que elegir una opción de cada grupo, las posibilidades se "
        "multiplican.\n\n"
        "1) Por cada una de las 4 entradas hay 5 fondos posibles.\n"
        "2) Multiplica: 4 · 5 = 20 combinaciones.\n\n"
        "Este es el principio multiplicativo: se usa cuando las elecciones son "
        "sucesivas e independientes.",
        [
            ("9", "Sumó las opciones en lugar de multiplicarlas."),
            ("40", "Multiplicó y luego duplicó, como si el orden de los platos importara."),
            ("5", "Consideró solo uno de los dos grupos."),
        ],
    ),
    _q(
        "prob_combinatoria", "medio",
        "¿De cuántas maneras distintas se pueden ordenar 6 cuadros en una pared?",
        "720",
        "Ordenar todos los elementos de un grupo es una permutación.\n\n"
        "1) Para el primer lugar hay 6 opciones, luego 5, 4, 3, 2 y 1.\n"
        "2) Multiplica: 6 · 5 · 4 · 3 · 2 · 1 = 720.",
        [
            ("36", "Elevó al cuadrado la cantidad de cuadros en vez de calcular el factorial."),
            ("30", "Multiplicó solo los dos primeros factores (6 · 5)."),
            ("120", "Calculó el factorial de 5 en lugar del de 6."),
        ],
    ),
    _q(
        "prob_combinatoria", "medio",
        "¿Cuántos números de 3 cifras distintas se pueden formar usando los dígitos "
        "1, 2, 3, 4 y 5?",
        "60",
        "Como las cifras no pueden repetirse, cada elección reduce las opciones "
        "siguientes.\n\n"
        "1) Para la primera cifra hay 5 opciones.\n"
        "2) Para la segunda quedan 4, porque no puede repetir la anterior.\n"
        "3) Para la tercera quedan 3.\n"
        "4) Multiplica: 5 · 4 · 3 = 60.",
        [
            ("125", "Permitió repetir cifras, calculando 5 · 5 · 5."),
            ("10", "Contó los grupos de 3 sin importar el orden, cuando acá el orden sí cambia el número."),
            ("15", "Multiplicó la cantidad de dígitos por la cantidad de cifras."),
        ],
    ),
    _q(
        "prob_combinatoria", "dificil",
        "De un grupo de 6 personas se debe elegir un comité de 2, sin distinguir "
        "cargos. ¿Cuántos comités distintos se pueden formar?",
        "15",
        "Como no hay cargos, el orden no importa: es una combinación, no una "
        "permutación.\n\n"
        "1) Si el orden importara, habría 6 · 5 = 30 formas.\n"
        "2) Pero cada comité queda contado dos veces, porque elegir a Ana y luego a "
        "Beto es el mismo comité que elegir a Beto y luego a Ana.\n"
        "3) Divide por 2: 30 ÷ 2 = 15.",
        [
            ("30", "Contó como distintos los comités con las mismas personas en distinto orden."),
            ("12", "Multiplicó la cantidad de personas por el tamaño del comité."),
            ("36", "Elevó al cuadrado la cantidad de personas, permitiendo repetir a la misma."),
        ],
    ),
    _q(
        "prob_combinatoria", "dificil",
        "Una clave se forma con 2 letras seguidas de 3 dígitos, y tanto letras como "
        "dígitos pueden repetirse. Si se usan 26 letras y 10 dígitos, "
        "¿cuántas claves distintas existen?",
        "676.000",
        "Se aplica el principio multiplicativo a cada posición, y como se permite "
        "repetir, las opciones no disminuyen.\n\n"
        "1) Las dos letras aportan 26 · 26 = 676 posibilidades.\n"
        "2) Los tres dígitos aportan 10 · 10 · 10 = 1.000.\n"
        "3) Multiplica ambos bloques: 676 · 1.000 = 676.000.",
        [
            ("1.676", "Sumó los bloques en lugar de multiplicarlos."),
            ("468.000", "Usó 26 · 25 para las letras, prohibiendo la repetición que el enunciado sí permite."),
            ("67.600", "Consideró solo dos dígitos en lugar de tres."),
        ],
    ),
    _q(
        "prob_combinatoria", "facil",
        "Con 3 poleras y 4 pantalones, ¿cuántos conjuntos distintos de polera y "
        "pantalón se pueden armar?",
        "12",
        "Cada polera se puede combinar con cualquiera de los pantalones.\n\n"
        "1) Por cada una de las 3 poleras hay 4 pantalones posibles.\n"
        "2) Multiplica: 3 · 4 = 12 conjuntos distintos.",
        [
            ("7", "Sumó las prendas en lugar de multiplicar las opciones."),
            ("24", "Multiplicó por 2 de más, como si el orden de las prendas importara."),
            ("4", "Consideró solo los pantalones."),
        ],
    ),

    # ---------- PROBABILIDAD: reglas ----------
    _q(
        "prob_reglas", "facil",
        "Se lanza un dado común de 6 caras. ¿Cuál es la probabilidad de obtener un "
        "número primo?",
        "1/2",
        "Primero hay que identificar bien cuáles son los casos favorables.\n\n"
        "1) Los números primos entre 1 y 6 son 2, 3 y 5. El 1 no es primo y el 4 y el "
        "6 son compuestos.\n"
        "2) Son 3 casos favorables de 6 posibles.\n"
        "3) La probabilidad es 3/6 = 1/2.",
        [
            ("2/3", "Incluyó el 1 entre los primos, contando 4 casos favorables."),
            ("1/3", "Consideró solo dos números primos."),
            ("1/6", "Consideró un único caso favorable."),
        ],
    ),
    _q(
        "prob_reglas", "medio",
        "En una caja hay 7 fichas blancas y 5 negras. Se saca una al azar. "
        "¿Cuál es la probabilidad de que NO sea blanca?",
        "5/12",
        "Conviene contar directamente los casos que cumplen la condición pedida.\n\n"
        "1) Que no sea blanca significa que sea negra: hay 5 fichas negras.\n"
        "2) El total de fichas es 7 + 5 = 12.\n"
        "3) La probabilidad es 5/12.\n\n"
        "También se obtiene por complemento: 1 − 7/12 = 5/12.",
        [
            ("7/12", "Calculó la probabilidad de que sí sea blanca."),
            ("5/7", "Comparó las negras con las blancas en lugar de con el total."),
            ("1/2", "Supuso que ambos colores son igual de probables."),
        ],
    ),
    _q(
        "prob_reglas", "medio",
        "Se lanzan dos monedas. ¿Cuál es la probabilidad de obtener dos caras?",
        "1/4",
        "Conviene listar todos los resultados posibles del experimento.\n\n"
        "1) Los resultados son: cara-cara, cara-sello, sello-cara y sello-sello. "
        "Son 4 casos igualmente probables.\n"
        "2) Solo uno de ellos es cara-cara.\n"
        "3) La probabilidad es 1/4.\n\n"
        "También se obtiene multiplicando: como los lanzamientos son independientes, "
        "1/2 · 1/2 = 1/4.",
        [
            ("1/2", "Consideró la probabilidad de una sola moneda en lugar de las dos."),
            ("1/3", "Contó los casos como si cara-sello y sello-cara fueran uno solo."),
            ("2/4", "Contó dos casos favorables, incluyendo cara-sello."),
        ],
    ),
    _q(
        "prob_reglas", "dificil",
        "De una baraja de 52 cartas se extrae una al azar. ¿Cuál es la probabilidad de "
        "que sea un as o una carta de corazones?",
        "16/52",
        "Cuando los sucesos pueden ocurrir a la vez hay que descontar la intersección "
        "para no contarla dos veces.\n\n"
        "1) Hay 4 ases.\n"
        "2) Hay 13 cartas de corazones.\n"
        "3) El as de corazones está en ambos grupos, así que se contó dos veces: "
        "hay que restarlo una vez.\n"
        "4) Casos favorables: 4 + 13 − 1 = 16, y la probabilidad es 16/52.",
        [
            ("17/52", "Sumó ambos grupos sin descontar el as de corazones, que quedó contado dos veces."),
            ("13/52", "Consideró solo las cartas de corazones."),
            ("4/52", "Consideró solo los ases."),
        ],
    ),
    _q(
        "prob_reglas", "dificil",
        "En una caja hay 4 bolitas blancas y 6 negras. Se sacan dos bolitas al azar, "
        "una tras otra y sin reposición. ¿Cuál es la probabilidad de que ambas sean "
        "blancas?",
        "2/15",
        "Sin reposición, la segunda extracción ocurre con una bolita menos en la caja.\n\n"
        "1) Primera bolita blanca: hay 4 blancas de 10, o sea 4/10.\n"
        "2) Para la segunda quedan 3 blancas de 9 bolitas: 3/9.\n"
        "3) Multiplica ambas probabilidades: (4/10) · (3/9) = 12/90.\n"
        "4) Simplifica dividiendo por 6: 12 ÷ 6 = 2 y 90 ÷ 6 = 15, o sea 2/15.",
        [
            ("4/25", "Trató la extracción como si fuera con reposición: (4/10) · (4/10)."),
            ("7/10", "Sumó las probabilidades en lugar de multiplicarlas."),
            ("2/5", "Calculó solo la probabilidad de la primera extracción."),
        ],
    ),
    _q(
        "prob_reglas", "facil",
        "La probabilidad de que llueva mañana es 0,3. ¿Cuál es la probabilidad de que "
        "NO llueva?",
        "0,7",
        "La probabilidad de un suceso y la de su contrario suman siempre 1.\n\n"
        "1) Plantea: P(no llueva) = 1 − P(llueva).\n"
        "2) Reemplaza: 1 − 0,3 = 0,7.",
        [
            ("0,3", "Repitió la probabilidad dada en lugar de calcular la del suceso contrario."),
            ("−0,3", "Cambió el signo en vez de restar a 1."),
            ("0,6", "Duplicó el valor dado en lugar de restarlo a 1."),
        ],
    ),
]

QUESTIONS += [
    # ---------- M2 · NÚMEROS: reales ----------
    _q(
        "num_reales", "facil",
        "¿Cuál de los siguientes números es irracional?",
        "√7",
        "Un número es irracional si no puede escribirse como cociente de dos enteros; "
        "su desarrollo decimal es infinito y no periódico.\n\n"
        "1) √7 ≈ 2,6457513… no tiene periodo ni término, y 7 no es cuadrado perfecto, "
        "así que su raíz es irracional.\n"
        "2) 0,25 es 1/4, un racional exacto.\n"
        "3) 2/3 es cociente de enteros, racional aunque su decimal sea periódico.\n"
        "4) √16 = 4, un entero.",
        [
            ("0,25", "Es racional: equivale a la fracción 1/4."),
            ("2/3", "Es racional por definición: es un cociente de dos enteros."),
            ("√16", "Su raíz es exacta (vale 4), por lo tanto es un número entero."),
        ],
    ),
    _q(
        "num_reales", "medio",
        "¿Cuál es el resultado de racionalizar 6/√3?",
        "2√3",
        "Racionalizar es eliminar la raíz del denominador amplificando la fracción.\n\n"
        "1) Multiplica numerador y denominador por √3: (6 · √3)/(√3 · √3).\n"
        "2) El denominador queda √3 · √3 = 3.\n"
        "3) La fracción es 6√3/3.\n"
        "4) Simplifica 6/3 = 2, quedando 2√3.\n\n"
        "Verificación aproximada: 6/1,732 ≈ 3,46, y 2 · 1,732 ≈ 3,46.",
        [
            ("6√3", "Multiplicó el numerador por √3 pero no simplificó con el 3 del denominador."),
            ("2/√3", "Simplificó el 6 con el 3 antes de racionalizar y dejó la raíz abajo."),
            ("√3/2", "Invirtió la fracción resultante."),
        ],
    ),
    _q(
        "num_reales", "medio",
        "¿A qué intervalo corresponde el conjunto de los números reales x tales que "
        "−2 < x ≤ 5?",
        "]−2, 5]",
        "El tipo de paréntesis indica si el extremo se incluye o no.\n\n"
        "1) La desigualdad −2 < x es estricta, así que −2 no pertenece: el intervalo se "
        "abre en ese extremo.\n"
        "2) La desigualdad x ≤ 5 sí incluye el 5: el intervalo se cierra en ese "
        "extremo.\n"
        "3) La notación correcta es ]−2, 5], que también se escribe (−2, 5].",
        [
            ("[−2, 5]", "Incluyó el −2, que la desigualdad estricta deja fuera."),
            ("]−2, 5[", "Excluyó el 5, que la desigualdad no estricta sí incluye."),
            ("[−2, 5[", "Invirtió ambos extremos respecto de lo que indican las desigualdades."),
        ],
    ),
    _q(
        "num_reales", "dificil",
        "¿Cuál es el valor de (√5 + 2)(√5 − 2)?",
        "1",
        "El producto tiene la forma de una suma por su diferencia, que da la diferencia "
        "de cuadrados.\n\n"
        "1) Aplica (a + b)(a − b) = a² − b², con a = √5 y b = 2.\n"
        "2) Calcula a² = (√5)² = 5.\n"
        "3) Calcula b² = 4.\n"
        "4) Resta: 5 − 4 = 1.\n\n"
        "El resultado es racional aunque los factores sean irracionales: por eso este "
        "producto se usa para racionalizar denominadores.",
        [
            ("√5", "Canceló los términos con 2 y dejó la raíz sin operar."),
            ("9", "Sumó los cuadrados en lugar de restarlos."),
            ("5 − 4√5", "Desarrolló como si fuera un cuadrado de binomio."),
        ],
    ),
    _q(
        "num_reales", "dificil",
        "¿Cuál es el valor de |3 − 8| + |−4|?",
        "9",
        "El valor absoluto entrega la distancia al cero, siempre no negativa.\n\n"
        "1) Resuelve primero lo de adentro: 3 − 8 = −5.\n"
        "2) Aplica el valor absoluto: |−5| = 5.\n"
        "3) El segundo término: |−4| = 4.\n"
        "4) Suma: 5 + 4 = 9.",
        [
            ("−1", "Operó sin aplicar el valor absoluto: −5 + 4."),
            ("1", "Aplicó valor absoluto solo al primer término y restó el segundo."),
            ("15", "Sumó los números sin resolver la resta interior: 3 + 8 + 4."),
        ],
    ),

    # ---------- M2 · NÚMEROS: matemática financiera ----------
    _q(
        "num_financiera", "facil",
        "Se depositan $200.000 al 5% de interés simple anual. "
        "¿Cuánto interés se gana en un año?",
        "$10.000",
        "En el interés simple, el interés se calcula siempre sobre el capital "
        "inicial.\n\n"
        "1) El interés de un año es el 5% del capital.\n"
        "2) Calcula: 0,05 · 200.000 = 10.000.\n"
        "3) El interés ganado es $10.000, y el total acumulado sería $210.000.",
        [
            ("$210.000", "Entregó el monto final acumulado en lugar del interés ganado."),
            ("$100.000", "Calculó el 50% en vez del 5%, corriendo la coma decimal."),
            ("$5.000", "Tomó el porcentaje como si fuera un monto fijo en pesos."),
        ],
    ),
    _q(
        "num_financiera", "medio",
        "Un capital de $100.000 se invierte al 10% de interés compuesto anual. "
        "¿Cuánto se tiene al cabo de 2 años?",
        "$121.000",
        "En el interés compuesto los intereses del primer periodo también generan "
        "intereses en el siguiente.\n\n"
        "1) Primer año: 100.000 · 1,1 = 110.000.\n"
        "2) Segundo año, sobre el nuevo monto: 110.000 · 1,1 = 121.000.\n\n"
        "Con la fórmula directa: 100.000 · (1,1)² = 100.000 · 1,21 = 121.000.",
        [
            ("$120.000", "Aplicó interés simple: 10% del capital inicial dos veces."),
            ("$110.000", "Calculó solo el primer año."),
            ("$200.000", "Duplicó el capital, como si la tasa fuera del 100%."),
        ],
    ),
    _q(
        "num_financiera", "medio",
        "Un artículo cuesta $80.000 y se paga en 4 cuotas iguales con un recargo total "
        "del 20%. ¿Cuánto se paga en cada cuota?",
        "$24.000",
        "Primero se calcula el total con recargo y recién después se divide en cuotas.\n\n"
        "1) Total con recargo: 80.000 · 1,2 = 96.000.\n"
        "2) Divide en 4 cuotas iguales: 96.000 ÷ 4 = 24.000.",
        [
            ("$20.000", "Dividió el precio sin aplicar el recargo del 20%."),
            ("$28.800", "Aplicó el 20% de recargo a cada cuota ya calculada, duplicando el efecto."),
            ("$96.000", "Entregó el total con recargo en lugar del valor de cada cuota."),
        ],
    ),
    _q(
        "num_financiera", "dificil",
        "¿Cuál es la tasa de interés simple anual si un capital de $500.000 genera "
        "$60.000 de interés en 2 años?",
        "6%",
        "Se despeja la tasa desde la fórmula del interés simple.\n\n"
        "1) El interés simple es capital · tasa · tiempo.\n"
        "2) Reemplaza: 60.000 = 500.000 · i · 2.\n"
        "3) Simplifica: 60.000 = 1.000.000 · i.\n"
        "4) Despeja: i = 0,06, es decir, 6% anual.\n\n"
        "Control: el 6% de 500.000 es 30.000 al año, y en dos años son 60.000.",
        [
            ("12%", "Calculó la tasa del periodo completo sin dividirla por los 2 años."),
            ("6,5%", "Aplicó la fórmula del interés compuesto en un problema de interés simple."),
            ("3%", "Dividió dos veces por el plazo."),
        ],
    ),
    _q(
        "num_financiera", "dificil",
        "Un producto sube un 10% y luego se le aplica un descuento del 10%. "
        "Si el precio inicial era $50.000, ¿cuál es el precio final?",
        "$49.500",
        "El descuento se aplica sobre el precio ya aumentado, no sobre el original.\n\n"
        "1) Sube 10%: 50.000 · 1,1 = 55.000.\n"
        "2) Baja 10% sobre 55.000: 55.000 · 0,9 = 49.500.\n\n"
        "El factor total es 1,1 · 0,9 = 0,99, una caída del 1% respecto del precio "
        "inicial.",
        [
            ("$50.000", "Supuso que subir y bajar 10% se anulan entre sí."),
            ("$55.000", "Se detuvo tras el alza y no aplicó el descuento."),
            ("$45.000", "Aplicó el descuento del 10% sobre el precio original y restó dos veces."),
        ],
    ),

    # ---------- M2 · NÚMEROS: logaritmos ----------
    _q(
        "num_logaritmos", "facil",
        "¿Cuál es el valor de log₂ 32?",
        "5",
        "El logaritmo responde a qué exponente hay que elevar la base para obtener el "
        "número.\n\n"
        "1) Plantea: 2 elevado a qué da 32.\n"
        "2) Calcula las potencias de 2: 2⁴ = 16 y 2⁵ = 32.\n"
        "3) Por lo tanto, log₂ 32 = 5.",
        [
            ("16", "Dividió 32 por 2 en lugar de buscar el exponente."),
            ("6", "Contó un exponente de más: 2⁶ = 64."),
            ("2", "Entregó la base en lugar del exponente."),
        ],
    ),
    _q(
        "num_logaritmos", "medio",
        "¿Cuál es el valor de log 100 + log 1.000, en base 10?",
        "5",
        "Se calcula cada logaritmo por separado; en base 10 el logaritmo cuenta los "
        "ceros de las potencias de diez.\n\n"
        "1) log 100 = 2, porque 10² = 100.\n"
        "2) log 1.000 = 3, porque 10³ = 1.000.\n"
        "3) Suma: 2 + 3 = 5.\n\n"
        "También sirve la propiedad de la suma de logaritmos: "
        "log 100 + log 1.000 = log(100.000) = 5.",
        [
            ("6", "Multiplicó los logaritmos en lugar de sumarlos."),
            ("1.100", "Sumó los números sin aplicar el logaritmo."),
            ("100.000", "Aplicó la propiedad del producto pero entregó el argumento en vez del logaritmo."),
        ],
    ),
    _q(
        "num_logaritmos", "medio",
        "Si log x = 3 en base 10, ¿cuál es el valor de x?",
        "1.000",
        "Se pasa de la forma logarítmica a la exponencial.\n\n"
        "1) log₁₀ x = 3 significa que 10³ = x.\n"
        "2) Calcula: 10³ = 1.000.\n"
        "3) Por lo tanto, x = 1.000.",
        [
            ("30", "Multiplicó la base por el logaritmo en lugar de elevar."),
            ("100", "Usó el exponente 2 en vez de 3."),
            ("3", "Entregó el valor del logaritmo como si fuera x."),
        ],
    ),
    _q(
        "num_logaritmos", "dificil",
        "¿Cuál es el valor de log₃ 81 − log₃ 9?",
        "2",
        "Se puede calcular cada logaritmo o aplicar la propiedad del cociente.\n\n"
        "1) log₃ 81 = 4, porque 3⁴ = 81.\n"
        "2) log₃ 9 = 2, porque 3² = 9.\n"
        "3) Resta: 4 − 2 = 2.\n\n"
        "Con la propiedad del cociente: log₃(81/9) = log₃ 9 = 2, el mismo resultado.",
        [
            ("9", "Dividió los argumentos y entregó el cociente sin aplicar el logaritmo."),
            ("72", "Restó los argumentos en lugar de los logaritmos."),
            ("6", "Sumó los logaritmos en vez de restarlos."),
        ],
    ),
    _q(
        "num_logaritmos", "dificil",
        "¿Cuál es el valor de log₅ 1?",
        "0",
        "El logaritmo de 1 es cero en cualquier base, porque todo número elevado a cero "
        "da 1.\n\n"
        "1) Plantea: 5 elevado a qué da 1.\n"
        "2) Como 5⁰ = 1, el exponente buscado es 0.\n"
        "3) Por lo tanto, log₅ 1 = 0.",
        [
            ("1", "Confundió el argumento con el resultado."),
            ("5", "Entregó la base en lugar del exponente."),
            ("No está definido", "Confundió este caso con log de 0, que sí es indefinido."),
        ],
    ),
]

QUESTIONS += [
    # ---------- M2 · ÁLGEBRA: sistemas y sus casos ----------
    _q(
        "alg_sistemas_casos", "facil",
        "¿Cuántas soluciones tiene el sistema x + y = 4 ; 2x + 2y = 8?",
        "Infinitas",
        "Conviene comparar si una ecuación es múltiplo de la otra.\n\n"
        "1) Multiplica la primera ecuación por 2: 2x + 2y = 8.\n"
        "2) Es exactamente la segunda ecuación, así que ambas representan la misma "
        "recta.\n"
        "3) Dos rectas coincidentes tienen infinitos puntos en común, por lo que el "
        "sistema tiene infinitas soluciones.",
        [
            ("Una", "Supuso que todo sistema 2x2 tiene solución única, sin notar que las ecuaciones son proporcionales."),
            ("Ninguna", "Confundió rectas coincidentes con rectas paralelas distintas."),
            ("Dos", "Un sistema de dos ecuaciones lineales nunca tiene exactamente dos soluciones."),
        ],
    ),
    _q(
        "alg_sistemas_casos", "medio",
        "¿Cuántas soluciones tiene el sistema 3x + y = 5 ; 6x + 2y = 7?",
        "Ninguna",
        "Se compara la proporción de los coeficientes con la de los términos "
        "independientes.\n\n"
        "1) Los coeficientes de la segunda ecuación son el doble de los de la primera: "
        "6 = 2 · 3 y 2 = 2 · 1.\n"
        "2) Pero el término independiente no sigue esa proporción: 2 · 5 = 10, y la "
        "segunda ecuación tiene 7.\n"
        "3) Son rectas paralelas distintas, que nunca se cortan: el sistema no tiene "
        "solución.",
        [
            ("Una", "No comparó las proporciones entre los coeficientes de ambas ecuaciones."),
            ("Infinitas", "Vio que los coeficientes son proporcionales pero no revisó el término independiente."),
            ("Dos", "Un sistema lineal 2x2 solo puede tener una, ninguna o infinitas soluciones."),
        ],
    ),
    _q(
        "alg_sistemas_casos", "medio",
        "¿Para qué valor de k el sistema 2x + 3y = 7 ; 4x + ky = 9 NO tiene solución?",
        "k = 6",
        "El sistema no tiene solución cuando los coeficientes son proporcionales pero "
        "los términos independientes no siguen la misma proporción.\n\n"
        "1) La segunda ecuación tiene 4 donde la primera tiene 2: el factor es 2.\n"
        "2) Para que los coeficientes sean proporcionales, k debe ser 2 · 3 = 6.\n"
        "3) Con k = 6 los términos independientes serían 7 y 9, y 2 · 7 = 14 ≠ 9, "
        "así que las rectas son paralelas distintas: sin solución.",
        [
            ("k = 3", "Copió el coeficiente de la primera ecuación sin aplicar el factor 2."),
            ("k = 12", "Multiplicó por 4 en lugar de por el factor 2 que relaciona ambas ecuaciones."),
            ("k = 9", "Usó el término independiente en lugar del coeficiente."),
        ],
    ),
    _q(
        "alg_sistemas_casos", "dificil",
        "El sistema x − 2y = 3 ; 3x + my = 1 tiene solución única para todo valor de m, "
        "salvo uno. ¿Cuál es ese valor?",
        "m = −6",
        "La solución única se pierde justo cuando las rectas dejan de tener pendientes "
        "distintas, es decir, cuando los coeficientes se vuelven proporcionales.\n\n"
        "1) El factor entre los coeficientes de x es 3 ÷ 1 = 3.\n"
        "2) Para que los de y sigan esa misma proporción, m debe ser 3 · (−2) = −6.\n"
        "3) Con m = −6 las rectas son paralelas y el sistema deja de tener solución "
        "única.\n\n"
        "Con cualquier otro valor de m las pendientes difieren y las rectas se cortan "
        "en exactamente un punto.",
        [
            ("m = 6", "Olvidó el signo negativo del coeficiente −2 al aplicar la proporción."),
            ("m = −2", "Copió el coeficiente de la primera ecuación sin multiplicarlo por el factor 3."),
            ("m = 3", "Usó el factor de proporcionalidad como si fuera el valor de m."),
        ],
    ),
    _q(
        "alg_sistemas_casos", "dificil",
        "Si dos rectas de un sistema 2x2 tienen la misma pendiente pero distinto "
        "coeficiente de posición, el sistema es:",
        "Incompatible",
        "La pendiente determina la inclinación y el coeficiente de posición dónde corta "
        "el eje Y.\n\n"
        "1) Con la misma pendiente, las rectas son paralelas.\n"
        "2) Con distinto coeficiente de posición, cortan el eje Y en puntos distintos, "
        "así que nunca se tocan.\n"
        "3) Sin puntos en común no hay solución: el sistema es incompatible.\n\n"
        "Si además coincidiera el coeficiente de posición, serían la misma recta y el "
        "sistema tendría infinitas soluciones.",
        [
            ("Compatible determinado", "Ese caso corresponde a rectas con pendientes distintas, que se cortan en un punto."),
            ("Compatible indeterminado", "Ese caso requiere que también coincida el coeficiente de posición."),
            ("Sin pendiente definida", "La pendiente está definida: el problema es que ambas rectas la comparten."),
        ],
    ),

    # ---------- M2 · ÁLGEBRA: función potencia ----------
    _q(
        "alg_funcion_potencia", "facil",
        "Si f(x) = x⁵, ¿cuál es el valor de f(−1)?",
        "−1",
        "Se reemplaza el valor cuidando el signo al elevar.\n\n"
        "1) Sustituye: f(−1) = (−1)⁵.\n"
        "2) Multiplica −1 por sí mismo cinco veces. Como el exponente es impar, el "
        "resultado conserva el signo negativo: −1.\n\n"
        "Con exponente par el resultado habría sido 1.",
        [
            ("1", "Aplicó la regla del exponente par, cuando el exponente 5 es impar."),
            ("−5", "Multiplicó la base por el exponente en lugar de elevar."),
            ("5", "Multiplicó base por exponente e ignoró el signo."),
        ],
    ),
    _q(
        "alg_funcion_potencia", "medio",
        "En la función f(x) = 2x⁴, ¿cuál es el valor de f(2)?",
        "32",
        "Se respeta la prioridad: primero la potencia, después el coeficiente.\n\n"
        "1) Eleva primero: 2⁴ = 16.\n"
        "2) Multiplica por el coeficiente: 2 · 16 = 32.\n\n"
        "Un error frecuente es multiplicar primero el 2 por el 2 y luego elevar, que "
        "daría (2 · 2)⁴ = 256.",
        [
            ("256", "Multiplicó el coeficiente por la variable antes de elevar: (2 · 2)⁴."),
            ("16", "Calculó la potencia pero olvidó el coeficiente 2."),
            ("64", "Usó exponente 5 o duplicó el resultado de más."),
        ],
    ),
    _q(
        "alg_funcion_potencia", "medio",
        "¿Cuál es el comportamiento de la función f(x) = x⁴ respecto del eje Y?",
        "Es simétrica respecto del eje Y",
        "Las funciones potencia de exponente par cumplen f(−x) = f(x), lo que se "
        "traduce en simetría respecto del eje Y.\n\n"
        "1) Evalúa en un valor y su opuesto: f(2) = 16 y f(−2) = (−2)⁴ = 16.\n"
        "2) Ambos entregan el mismo resultado, así que la gráfica se refleja igual a "
        "ambos lados del eje Y.\n"
        "3) Una función con esa propiedad se llama función par.",
        [
            ("Es simétrica respecto del origen", "Esa simetría corresponde a las funciones de exponente impar, como x³."),
            ("No tiene simetría", "Sí la tiene: los valores opuestos de x entregan la misma imagen."),
            ("Es simétrica respecto del eje X", "Ninguna función puede serlo, porque un mismo x tendría dos imágenes."),
        ],
    ),
    _q(
        "alg_funcion_potencia", "dificil",
        "Si f(x) = ax³ y f(2) = 24, ¿cuál es el valor de a?",
        "3",
        "Se reemplaza el punto conocido y se despeja el coeficiente.\n\n"
        "1) Evalúa: f(2) = a · 2³ = 8a.\n"
        "2) Iguala al dato: 8a = 24.\n"
        "3) Despeja: a = 24 ÷ 8 = 3.\n\n"
        "Verifica: f(x) = 3x³, y f(2) = 3 · 8 = 24.",
        [
            ("8", "Entregó el valor de 2³ en lugar del coeficiente a."),
            ("12", "Dividió por 2 en lugar de por 2³."),
            ("24", "Tomó el valor de la función como si fuera directamente a."),
        ],
    ),
    _q(
        "alg_funcion_potencia", "dificil",
        "Para la función f(x) = x⁵, ¿qué ocurre con f(x) cuando x toma valores "
        "negativos cada vez más grandes en magnitud?",
        "f(x) decrece sin límite",
        "Con exponente impar la función conserva el signo de x.\n\n"
        "1) Evalúa algunos valores: f(−2) = −32, f(−3) = −243, f(−10) = −100.000.\n"
        "2) Mientras más negativo es x, más negativo es el resultado, y sin cota "
        "inferior.\n"
        "3) Por lo tanto, f(x) decrece sin límite.\n\n"
        "Si el exponente fuera par, la función crecería hacia valores positivos en ese "
        "mismo tramo.",
        [
            ("f(x) crece sin límite", "Corresponde a exponentes pares, donde el signo negativo se pierde al elevar."),
            ("f(x) se acerca a cero", "Ese comportamiento corresponde a exponentes negativos, no a x⁵."),
            ("f(x) se mantiene constante", "La función potencia no es constante: cambia con cada valor de x."),
        ],
    ),
]

QUESTIONS += [
    # ---------- M2 · GEOMETRÍA: homotecia ----------
    _q(
        "geo_homotecia", "facil",
        "Se aplica al punto P(3, −2) una homotecia de centro en el origen y razón 4. "
        "¿Cuáles son las coordenadas de la imagen?",
        "(12, −8)",
        "En una homotecia con centro en el origen se multiplican ambas coordenadas por "
        "la razón.\n\n"
        "1) Coordenada x: 3 · 4 = 12.\n"
        "2) Coordenada y: −2 · 4 = −8.\n"
        "3) La imagen es (12, −8).",
        [
            ("(7, 2)", "Sumó la razón a cada coordenada en lugar de multiplicar."),
            ("(0,75, −0,5)", "Dividió por la razón, que corresponde a una homotecia de razón 1/4."),
            ("(12, 8)", "Multiplicó bien pero perdió el signo negativo de la coordenada y."),
        ],
    ),
    _q(
        "geo_homotecia", "medio",
        "Un triángulo de área 12 cm² se somete a una homotecia de razón 3. "
        "¿Cuál es el área de la figura resultante?",
        "108 cm²",
        "En una homotecia las longitudes se multiplican por la razón, pero las áreas lo "
        "hacen por el cuadrado de la razón.\n\n"
        "1) La razón es 3, así que el factor para el área es 3² = 9.\n"
        "2) Multiplica: 12 · 9 = 108 cm².\n\n"
        "El razonamiento es el mismo que al ampliar un cuadrado: si el lado se triplica, "
        "el área se hace nueve veces mayor.",
        [
            ("36 cm²", "Multiplicó el área por la razón en lugar de por su cuadrado."),
            ("324 cm²", "Elevó la razón al cubo, que corresponde al volumen y no al área."),
            ("4 cm²", "Dividió por la razón en vez de multiplicar."),
        ],
    ),
    _q(
        "geo_homotecia", "medio",
        "Una homotecia tiene razón −2. ¿Qué le ocurre a la figura original?",
        "Se duplica su tamaño y queda invertida respecto del centro",
        "El valor absoluto de la razón indica el cambio de tamaño y su signo, la "
        "posición respecto del centro.\n\n"
        "1) El valor absoluto es 2, así que todas las longitudes se duplican.\n"
        "2) El signo negativo ubica la imagen al lado opuesto del centro de homotecia, "
        "invertida.\n"
        "3) La figura resultante es semejante a la original, con el doble de tamaño y "
        "orientación invertida.",
        [
            ("Se reduce a la mitad y queda invertida", "Interpretó la razón −2 como si fuera −1/2."),
            ("Se duplica su tamaño y conserva la posición", "Ignoró el efecto del signo negativo."),
            ("No cambia de tamaño, solo se invierte", "Ese caso corresponde a una razón de −1."),
        ],
    ),
    _q(
        "geo_homotecia", "dificil",
        "Dos triángulos son homotéticos. Si un lado del original mide 8 cm y su "
        "correspondiente en la imagen mide 20 cm, ¿cuál es la razón de homotecia?",
        "2,5",
        "La razón es el cociente entre la medida de la imagen y la del original, en ese "
        "orden.\n\n"
        "1) Divide: 20 ÷ 8 = 2,5.\n"
        "2) La razón es 2,5, mayor que 1, lo que confirma que la figura se amplió.\n\n"
        "Si se invirtiera el orden se obtendría 0,4, que es la razón de la homotecia "
        "que lleva de la imagen al original.",
        [
            ("0,4", "Dividió el original por la imagen, invirtiendo el orden de la razón."),
            ("12", "Restó las medidas en lugar de dividirlas."),
            ("160", "Multiplicó las medidas en vez de dividirlas."),
        ],
    ),
    _q(
        "geo_homotecia", "dificil",
        "Un rectángulo de 5 cm por 8 cm se amplía mediante una homotecia de razón 3. "
        "¿Cuál es el perímetro de la figura resultante?",
        "78 cm",
        "El perímetro es una longitud, así que se multiplica directamente por la razón, "
        "no por su cuadrado.\n\n"
        "1) Perímetro original: 2(5 + 8) = 26 cm.\n"
        "2) Multiplica por la razón: 26 · 3 = 78 cm.\n\n"
        "Otra forma: los lados pasan a medir 15 cm y 24 cm, y 2(15 + 24) = 78 cm.",
        [
            ("234 cm", "Multiplicó por el cuadrado de la razón, que corresponde al área y no al perímetro."),
            ("120 cm", "Calculó el área de la figura ampliada en lugar del perímetro."),
            ("26 cm", "Entregó el perímetro original sin aplicar la homotecia."),
        ],
    ),

    # ---------- M2 · GEOMETRÍA: trigonometría ----------
    _q(
        "geo_trigonometria", "facil",
        "En un triángulo rectángulo, el cateto opuesto a un ángulo mide 3 cm y la "
        "hipotenusa 5 cm. ¿Cuál es el seno de ese ángulo?",
        "3/5",
        "El seno de un ángulo agudo es el cateto opuesto dividido por la hipotenusa.\n\n"
        "1) Identifica los datos: cateto opuesto 3 cm, hipotenusa 5 cm.\n"
        "2) Aplica la razón: sen α = 3/5.\n\n"
        "El seno de un ángulo agudo siempre es menor que 1, porque el cateto es siempre "
        "menor que la hipotenusa.",
        [
            ("5/3", "Invirtió la razón, dividiendo la hipotenusa por el cateto."),
            ("3/4", "Usó el cateto adyacente (4 cm) en el denominador, que corresponde a la tangente."),
            ("4/5", "Calculó el coseno, que usa el cateto adyacente."),
        ],
    ),
    _q(
        "geo_trigonometria", "medio",
        "¿Cuál es el valor de tan 45°?",
        "1",
        "La tangente es el cociente entre el cateto opuesto y el adyacente.\n\n"
        "1) En un triángulo rectángulo con un ángulo de 45°, el otro ángulo agudo "
        "también mide 45°, así que es isósceles.\n"
        "2) Al ser isósceles, ambos catetos son iguales.\n"
        "3) El cociente de dos cantidades iguales es 1, así que tan 45° = 1.",
        [
            ("√2/2", "Entregó el valor del seno y del coseno de 45°, no el de la tangente."),
            ("√3", "Corresponde a la tangente de 60°."),
            ("0", "Corresponde a la tangente de 0°."),
        ],
    ),
    _q(
        "geo_trigonometria", "medio",
        "Un triángulo rectángulo tiene un ángulo de 30° y su hipotenusa mide 10 cm. "
        "¿Cuánto mide el cateto opuesto a ese ángulo?",
        "5 cm",
        "Se usa el seno, que relaciona el cateto opuesto con la hipotenusa.\n\n"
        "1) Plantea: sen 30° = cateto opuesto ÷ 10.\n"
        "2) El seno de 30° es 1/2.\n"
        "3) Despeja: cateto = 10 · 1/2 = 5 cm.\n\n"
        "Es una propiedad conocida: en un triángulo de 30-60-90, el cateto menor mide "
        "la mitad de la hipotenusa.",
        [
            ("8,66 cm", "Usó el coseno de 30°, que entrega el cateto adyacente."),
            ("20 cm", "Dividió por el seno en vez de multiplicar, obteniendo un cateto mayor que la hipotenusa."),
            ("10 cm", "Entregó la hipotenusa sin aplicar la razón trigonométrica."),
        ],
    ),
    _q(
        "geo_trigonometria", "dificil",
        "Desde un punto en el suelo, a 20 m de la base de un edificio, se observa su "
        "parte más alta con un ángulo de elevación de 45°. ¿Cuál es la altura del "
        "edificio?",
        "20 m",
        "La distancia horizontal es el cateto adyacente y la altura, el opuesto: los "
        "relaciona la tangente.\n\n"
        "1) Plantea: tan 45° = altura ÷ 20.\n"
        "2) Como tan 45° = 1, queda 1 = altura ÷ 20.\n"
        "3) Despeja: altura = 20 m.\n\n"
        "Con 45° la altura siempre iguala a la distancia horizontal, porque el triángulo "
        "es isósceles.",
        [
            ("28,3 m", "Calculó la hipotenusa del triángulo en lugar de la altura."),
            ("10 m", "Dividió la distancia por 2, como si el ángulo fuera de 30°."),
            ("40 m", "Multiplicó la distancia por 2 en vez de aplicar la tangente."),
        ],
    ),
    _q(
        "geo_trigonometria", "dificil",
        "Si sen α = 0,6 y α es un ángulo agudo, ¿cuál es el valor de cos α?",
        "0,8",
        "Se usa la identidad fundamental: el cuadrado del seno más el cuadrado del "
        "coseno es 1.\n\n"
        "1) Plantea: 0,6² + cos²α = 1.\n"
        "2) Calcula: 0,36 + cos²α = 1, entonces cos²α = 0,64.\n"
        "3) Saca la raíz: cos α = 0,8. Se toma el valor positivo porque el ángulo es "
        "agudo.\n\n"
        "Corresponde al triángulo 3-4-5: si el seno es 3/5, el coseno es 4/5.",
        [
            ("0,4", "Restó el seno a 1 sin usar la identidad con los cuadrados."),
            ("0,64", "Calculó el cuadrado del coseno pero no sacó la raíz."),
            ("1,6", "Sumó el seno a 1 en lugar de aplicar la identidad."),
        ],
    ),
]

QUESTIONS += [
    # ---------- M2 · PROBABILIDAD: dispersión ----------
    _q(
        "prob_dispersion", "facil",
        "¿Cuál de estos conjuntos de datos tiene mayor dispersión?",
        "2, 9, 15, 22",
        "La dispersión indica qué tan separados están los datos entre sí; el rango es "
        "una primera aproximación.\n\n"
        "1) En 2, 9, 15, 22 el rango es 22 − 2 = 20.\n"
        "2) En 10, 11, 12, 13 el rango es 3.\n"
        "3) En 7, 7, 8, 8 el rango es 1.\n"
        "4) En 5, 5, 5, 5 el rango es 0: todos los datos son iguales.\n\n"
        "El primer conjunto tiene el mayor rango, así que sus datos son los más "
        "dispersos.",
        [
            ("10, 11, 12, 13", "Sus datos están muy juntos: el rango es apenas 3."),
            ("7, 7, 8, 8", "Es un conjunto muy concentrado, con rango 1."),
            ("5, 5, 5, 5", "Tiene dispersión cero: todos los datos son idénticos."),
        ],
    ),
    _q(
        "prob_dispersion", "medio",
        "Si todos los datos de un conjunto son iguales, ¿cuál es su desviación "
        "estándar?",
        "0",
        "La desviación estándar mide cuánto se apartan los datos de su promedio.\n\n"
        "1) Si todos los datos son iguales, el promedio coincide con ese mismo valor.\n"
        "2) Cada desviación respecto del promedio es cero.\n"
        "3) El promedio de esas desviaciones al cuadrado es cero, y su raíz también.\n"
        "4) Por lo tanto, la desviación estándar es 0.",
        [
            ("1", "Confundió la desviación estándar con un valor mínimo distinto de cero."),
            ("Igual al promedio", "Mezcló una medida de dispersión con una de tendencia central."),
            ("No se puede calcular", "Sí se puede: el resultado es cero, que es un valor válido."),
        ],
    ),
    _q(
        "prob_dispersion", "medio",
        "¿Cuál es la varianza del conjunto 2, 4, 6?",
        "8/3",
        "La varianza es el promedio de los cuadrados de las desviaciones respecto de la "
        "media.\n\n"
        "1) Calcula el promedio: (2 + 4 + 6) ÷ 3 = 4.\n"
        "2) Obtén las desviaciones: 2 − 4 = −2; 4 − 4 = 0; 6 − 4 = 2.\n"
        "3) Elévalas al cuadrado: 4, 0 y 4.\n"
        "4) Promedia: (4 + 0 + 4) ÷ 3 = 8/3.",
        [
            ("4", "Promedió las desviaciones sin elevarlas al cuadrado, o entregó el promedio del conjunto."),
            ("8", "Sumó los cuadrados pero no dividió por la cantidad de datos."),
            ("2", "Entregó la desviación estándar aproximada en lugar de la varianza."),
        ],
    ),
    _q(
        "prob_dispersion", "dificil",
        "A todos los datos de un conjunto se les suma 5. ¿Qué ocurre con su "
        "desviación estándar?",
        "No cambia",
        "La desviación estándar mide separación entre datos, no su magnitud.\n\n"
        "1) Al sumar 5 a cada dato, el promedio también aumenta en 5.\n"
        "2) Cada desviación respecto del promedio se mantiene igual, porque ambos se "
        "desplazaron lo mismo.\n"
        "3) Como las desviaciones no cambian, la desviación estándar tampoco.\n\n"
        "Distinto sería multiplicar todos los datos por 5: en ese caso la desviación "
        "estándar quedaría multiplicada por 5.",
        [
            ("Aumenta en 5", "Aplicó a la dispersión el mismo desplazamiento que al promedio."),
            ("Queda multiplicada por 5", "Ese efecto corresponde a multiplicar los datos, no a sumarles una constante."),
            ("Se reduce a la mitad", "Sumar una constante no comprime los datos."),
        ],
    ),
    _q(
        "prob_dispersion", "dificil",
        "Dos cursos tienen el mismo promedio en una prueba, pero el curso A tiene una "
        "desviación estándar de 2 y el curso B de 9. ¿Qué se puede afirmar?",
        "Las notas del curso A son más homogéneas",
        "Con promedios iguales, la desviación estándar distingue qué tan parejo es el "
        "grupo.\n\n"
        "1) Una desviación estándar menor indica notas más cercanas al promedio.\n"
        "2) El curso A tiene 2, bastante menor que los 9 del curso B.\n"
        "3) Por lo tanto, las notas del curso A están más agrupadas: el curso es más "
        "homogéneo.\n\n"
        "En el curso B conviven notas muy altas y muy bajas que se compensan en el "
        "promedio.",
        [
            ("El curso B tiene mejor rendimiento", "El rendimiento lo indica el promedio, que es igual en ambos cursos."),
            ("El curso A tiene mejor promedio", "El enunciado dice explícitamente que ambos promedios son iguales."),
            ("Ambos cursos son igual de homogéneos", "Sus desviaciones estándar son muy distintas, así que su dispersión también."),
        ],
    ),

    # ---------- M2 · PROBABILIDAD: condicional ----------
    _q(
        "prob_condicional", "facil",
        "Se lanza un dado y se sabe que el resultado fue par. ¿Cuál es la probabilidad "
        "de que haya sido un 6?",
        "1/3",
        "El dato conocido reduce el espacio muestral: solo se consideran los casos que "
        "cumplen la condición.\n\n"
        "1) Los resultados pares son 2, 4 y 6: quedan 3 casos posibles.\n"
        "2) De ellos, solo uno es el 6.\n"
        "3) La probabilidad condicional es 1/3.\n\n"
        "Sin la condición sería 1/6; saber que salió par la aumenta.",
        [
            ("1/6", "Usó los 6 resultados del dado, sin restringirse a los pares."),
            ("1/2", "Consideró solo dos casos posibles en el espacio reducido."),
            ("3/6", "Entregó la probabilidad de obtener un número par, no la condicional pedida."),
        ],
    ),
    _q(
        "prob_condicional", "medio",
        "En un curso, el 60% practica deporte y el 24% practica deporte y toca un "
        "instrumento. Si se elige a alguien que practica deporte, ¿cuál es la "
        "probabilidad de que toque un instrumento?",
        "0,4",
        "La probabilidad condicional es la probabilidad conjunta dividida por la del "
        "suceso que se da como conocido.\n\n"
        "1) Plantea: P(instrumento | deporte) = P(ambos) ÷ P(deporte).\n"
        "2) Reemplaza: 0,24 ÷ 0,6.\n"
        "3) Calcula: 0,4, es decir, un 40%.",
        [
            ("0,24", "Entregó la probabilidad conjunta sin dividir por la del suceso conocido."),
            ("0,84", "Sumó ambas probabilidades en lugar de dividirlas."),
            ("2,5", "Invirtió la división: dividió 0,6 por 0,24."),
        ],
    ),
    _q(
        "prob_condicional", "medio",
        "Dos sucesos A y B son independientes, con P(A) = 0,5 y P(B) = 0,3. "
        "¿Cuál es P(A y B)?",
        "0,15",
        "En sucesos independientes la probabilidad conjunta es el producto de las "
        "probabilidades individuales.\n\n"
        "1) Plantea: P(A y B) = P(A) · P(B).\n"
        "2) Reemplaza: 0,5 · 0,3 = 0,15.\n\n"
        "La independencia significa que ocurra uno no altera la probabilidad del otro; "
        "por eso no hay que condicionar.",
        [
            ("0,8", "Sumó las probabilidades, que corresponde a la unión de sucesos excluyentes."),
            ("0,2", "Restó las probabilidades en lugar de multiplicarlas."),
            ("0,5", "Entregó solo la probabilidad de A."),
        ],
    ),
    _q(
        "prob_condicional", "dificil",
        "En una urna hay 3 bolitas rojas y 2 verdes. Se extraen dos sin reposición. "
        "Si la primera fue roja, ¿cuál es la probabilidad de que la segunda también "
        "lo sea?",
        "1/2",
        "Tras la primera extracción cambia la composición de la urna.\n\n"
        "1) Al inicio hay 5 bolitas: 3 rojas y 2 verdes.\n"
        "2) Como ya salió una roja y no se repuso, quedan 4 bolitas, de las cuales 2 "
        "son rojas.\n"
        "3) La probabilidad es 2/4 = 1/2.",
        [
            ("3/5", "Usó la composición inicial de la urna, ignorando que ya salió una bolita."),
            ("2/5", "Descontó la bolita roja del numerador pero no del total."),
            ("3/4", "Descontó la bolita del total pero no de las rojas."),
        ],
    ),
    _q(
        "prob_condicional", "dificil",
        "Si P(A) = 0,4 , P(B) = 0,5 y P(A y B) = 0,2 , ¿son A y B independientes?",
        "Sí, porque P(A) · P(B) = P(A y B)",
        "Dos sucesos son independientes exactamente cuando la probabilidad conjunta "
        "coincide con el producto de las individuales.\n\n"
        "1) Calcula el producto: 0,4 · 0,5 = 0,2.\n"
        "2) Compáralo con la probabilidad conjunta dada: también es 0,2.\n"
        "3) Como coinciden, los sucesos son independientes.\n\n"
        "Si el producto hubiera dado distinto de 0,2, habría dependencia entre ambos.",
        [
            ("No, porque P(A y B) no es cero", "Una probabilidad conjunta distinta de cero indica que pueden ocurrir juntos, no que sean dependientes."),
            ("No, porque P(A) es distinto de P(B)", "La independencia no exige que ambas probabilidades sean iguales."),
            ("No se puede determinar", "Sí se puede: basta comparar el producto de las probabilidades con la conjunta."),
        ],
    ),

    # ---------- M2 · PROBABILIDAD: permutación y combinatoria ----------
    _q(
        "prob_permutacion", "facil",
        "¿Cuál es el valor de 6! dividido por 4!?",
        "30",
        "Conviene desarrollar el factorial mayor hasta el menor para simplificar.\n\n"
        "1) Escribe 6! = 6 · 5 · 4!.\n"
        "2) La división queda (6 · 5 · 4!) ÷ 4!.\n"
        "3) Se cancela 4! y queda 6 · 5 = 30.\n\n"
        "No hace falta calcular 720 ÷ 24, aunque también da 30.",
        [
            ("2", "Restó los factoriales como si fueran números sueltos: 6 − 4."),
            ("1,5", "Dividió 6 por 4 sin considerar los factoriales."),
            ("720", "Calculó 6! y no dividió."),
        ],
    ),
    _q(
        "prob_permutacion", "medio",
        "¿De cuántas maneras se pueden elegir 3 delegados de un grupo de 7 personas, "
        "sin distinguir cargos?",
        "35",
        "Como los cargos no se distinguen, el orden no importa: es una combinación.\n\n"
        "1) Si el orden importara habría 7 · 6 · 5 = 210 formas.\n"
        "2) Cada grupo de 3 personas se estaría contando 3! = 6 veces, una por cada "
        "orden posible.\n"
        "3) Divide: 210 ÷ 6 = 35.",
        [
            ("210", "Contó como distintos los grupos con las mismas personas en distinto orden."),
            ("21", "Calculó las parejas posibles en lugar de los grupos de tres."),
            ("343", "Elevó 7 al cubo, permitiendo repetir a la misma persona."),
        ],
    ),
    _q(
        "prob_permutacion", "medio",
        "¿Cuántas palabras distintas, con o sin sentido, se pueden formar con todas "
        "las letras de la palabra CASA?",
        "12",
        "La letra A se repite, así que hay que descontar los ordenamientos que resultan "
        "idénticos.\n\n"
        "1) Si las 4 letras fueran distintas habría 4! = 24 ordenamientos.\n"
        "2) Como la A aparece 2 veces, cada palabra se contó 2! = 2 veces.\n"
        "3) Divide: 24 ÷ 2 = 12.",
        [
            ("24", "Trató las dos A como si fueran letras distintas."),
            ("6", "Dividió por 4 en lugar de por el factorial de las letras repetidas."),
            ("4", "Contó la cantidad de letras en vez de los ordenamientos."),
        ],
    ),
    _q(
        "prob_permutacion", "dificil",
        "¿De cuántas maneras se pueden sentar 4 personas en una fila de 4 asientos si "
        "dos de ellas deben quedar siempre juntas?",
        "12",
        "Conviene tratar a la pareja que va junta como un solo bloque.\n\n"
        "1) Considera la pareja como un bloque único. Junto a las otras 2 personas, hay "
        "3 elementos que ordenar: 3! = 6 formas.\n"
        "2) Dentro del bloque, las dos personas pueden intercambiarse: 2! = 2 formas.\n"
        "3) Multiplica: 6 · 2 = 12.\n\n"
        "Del total de 4! = 24 ordenamientos, en la mitad la pareja queda junta.",
        [
            ("24", "Contó todos los ordenamientos posibles sin imponer la condición."),
            ("6", "Trató el bloque como una sola unidad pero olvidó el intercambio interno."),
            ("48", "Multiplicó el total de ordenamientos por 2 en lugar de partir del bloque."),
        ],
    ),
    _q(
        "prob_permutacion", "dificil",
        "En un grupo de 5 hombres y 4 mujeres se elige un comité de 2 hombres y "
        "1 mujer. ¿Cuántos comités distintos se pueden formar?",
        "40",
        "Se cuenta cada grupo por separado y después se multiplican, porque las "
        "elecciones son independientes.\n\n"
        "1) Elegir 2 hombres de 5, sin importar el orden: (5 · 4) ÷ 2 = 10 formas.\n"
        "2) Elegir 1 mujer de 4: 4 formas.\n"
        "3) Multiplica: 10 · 4 = 40 comités distintos.",
        [
            ("14", "Sumó las opciones de cada grupo en lugar de multiplicarlas."),
            ("80", "Contó los pares de hombres como ordenados, sin dividir por 2."),
            ("20", "Usó 5 formas para elegir a los hombres, como si fuera una sola persona."),
        ],
    ),

    # ---------- M2 · PROBABILIDAD: modelo binomial ----------
    _q(
        "prob_binomial", "facil",
        "Se lanza una moneda 4 veces. ¿Cuántos resultados posibles distintos hay, "
        "considerando el orden?",
        "16",
        "Cada lanzamiento tiene dos resultados posibles e independientes de los "
        "demás.\n\n"
        "1) Por el principio multiplicativo: 2 · 2 · 2 · 2.\n"
        "2) Calcula: 2⁴ = 16 secuencias distintas.",
        [
            ("8", "Usó 2³, considerando solo tres lanzamientos."),
            ("4", "Contó la cantidad de lanzamientos en vez de las secuencias posibles."),
            ("32", "Usó 2⁵, un lanzamiento de más."),
        ],
    ),
    _q(
        "prob_binomial", "medio",
        "En un experimento binomial con 5 intentos y probabilidad de éxito 0,2 en cada "
        "uno, ¿cuál es el número esperado de éxitos?",
        "1",
        "El valor esperado de una variable binomial es la cantidad de intentos por la "
        "probabilidad de éxito.\n\n"
        "1) Plantea: esperanza = n · p.\n"
        "2) Reemplaza: 5 · 0,2 = 1.\n\n"
        "Significa que, repitiendo el experimento muchas veces, el promedio de éxitos "
        "por tanda tiende a 1.",
        [
            ("0,2", "Entregó la probabilidad de éxito individual sin multiplicar por los intentos."),
            ("5", "Entregó la cantidad de intentos en vez del valor esperado."),
            ("2,5", "Dividió los intentos por 2 en lugar de multiplicar por la probabilidad."),
        ],
    ),
    _q(
        "prob_binomial", "dificil",
        "Un experimento se repite 4 veces con probabilidad de éxito 0,5 en cada "
        "intento. ¿Cuál es la probabilidad de obtener exactamente 3 éxitos?",
        "0,25",
        "Se combinan la cantidad de formas de ubicar los éxitos con la probabilidad de "
        "cada secuencia.\n\n"
        "1) Formas de elegir cuáles 3 de los 4 intentos son exitosos: 4.\n"
        "2) Cada secuencia específica tiene probabilidad 0,5³ · 0,5 = 0,0625.\n"
        "3) Multiplica: 4 · 0,0625 = 0,25.\n\n"
        "Equivale a 4/16, coherente con que hay 16 secuencias posibles y 4 favorables.",
        [
            ("0,0625", "Calculó la probabilidad de una secuencia específica sin multiplicar por las 4 formas posibles."),
            ("0,5", "Usó la probabilidad de un solo intento."),
            ("0,75", "Sumó las probabilidades en lugar de aplicar el modelo binomial."),
        ],
    ),
    _q(
        "prob_binomial", "dificil",
        "¿Cuál de las siguientes situaciones NO corresponde a un experimento "
        "binomial?",
        "Medir la estatura de 20 estudiantes",
        "Un experimento binomial requiere una cantidad fija de intentos independientes, "
        "cada uno con solo dos resultados posibles y probabilidad constante.\n\n"
        "1) Medir estaturas entrega valores numéricos en un rango continuo, no un "
        "resultado de dos categorías: no es binomial.\n"
        "2) Lanzar una moneda 10 veces cumple: éxito o fracaso, probabilidad "
        "constante.\n"
        "3) Revisar 15 productos como defectuoso o no defectuoso también cumple.\n"
        "4) Responder al azar 8 preguntas y contar aciertos también cumple.",
        [
            ("Lanzar una moneda 10 veces y contar las caras", "Sí es binomial: dos resultados posibles y probabilidad constante."),
            ("Revisar 15 productos y contar los defectuosos", "Sí es binomial: cada producto es defectuoso o no lo es."),
            ("Responder al azar 8 preguntas de alternativas y contar los aciertos", "Sí es binomial: cada respuesta es acierto o error con probabilidad constante."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Competencia Lectora
#
# La prueba son 8 textos con 65 preguntas asociadas y dura 2 horas 30 minutos
# (temario DEMRE, Admisión 2027). No se organiza por ejes de contenido sino por
# tres habilidades, que son las que ocupan el lugar del eje en el árbol:
# localizar, interpretar y evaluar.
#
# Los textos son ORIGINALES de 1000paes. No se reproducen los del DEMRE, que
# tienen derechos de la Universidad de Chile. Escribirlos también hace la
# pregunta verificable: la respuesta correcta está contenida en un texto que
# controlamos, y `scripts/verificar_banco.py` comprueba que así sea.
# ---------------------------------------------------------------------------

SKILL_NODES_LECTORA = [
    ("lec_localizar", "Localizar información", "localizar", 1, []),
    ("lec_interpretar", "Interpretar y relacionar", "interpretar", 2, ["lec_localizar"]),
    ("lec_evaluar", "Evaluar y reflexionar", "evaluar", 3, ["lec_interpretar"]),
]

PASSAGES = [
    {
        "key": "vinchuca",
        "title": "El insecto que cambió de casa",
        "kind": "no_literario",
        "source_note": "Texto original de 1000paes",
        "body": (
            "La vinchuca es un insecto que se alimenta de sangre y que durante "
            "siglos vivió en las quebradas del norte de Chile, refugiada entre "
            "las piedras y las madrigueras de roedores silvestres. Su vida "
            "transcurría lejos de las personas.\n\n"
            "Eso cambió cuando la agricultura llegó a los valles. Las casas de "
            "adobe, con sus muros agrietados y sus techos de paja, resultaron "
            "ser un refugio mejor que las piedras: más estables, más tibias y "
            "con alimento disponible todas las noches. El insecto no fue "
            "buscado por nadie; simplemente encontró un lugar donde le convenía "
            "quedarse.\n\n"
            "El problema no es la picadura, que suele pasar inadvertida. El "
            "problema es lo que la vinchuca deja después de picar: sus "
            "deposiciones pueden contener un parásito que, si entra al cuerpo "
            "por la herida o por los ojos, provoca la enfermedad de Chagas. "
            "Muchas personas conviven con el parásito durante años sin sentir "
            "nada, y recién décadas más tarde aparecen daños en el corazón o en "
            "el sistema digestivo.\n\n"
            "Por eso las campañas sanitarias del siglo XX no se concentraron en "
            "el insecto sino en la vivienda. Reemplazar el adobe agrietado por "
            "muros lisos, cambiar los techos de paja, sellar las grietas: nada "
            "de eso mata vinchucas, pero les quita el refugio. La estrategia "
            "funcionó mejor que cualquier insecticida, y muestra algo que se "
            "repite en salud pública: a veces la forma más eficaz de combatir "
            "una enfermedad no es atacar al organismo que la transmite, sino "
            "cambiar las condiciones que lo hacen prosperar."
        ),
    },
    {
        "key": "carta",
        "title": "La carta que no se envió",
        "kind": "literario",
        "source_note": "Texto original de 1000paes",
        "body": (
            "Mi padre guardaba las herramientas en una caja de madera que él "
            "mismo había hecho, con las junturas tan ajustadas que no "
            "necesitaba clavos. Cuando yo era chico me dejaba mirar, nunca "
            "tocar. Decía que una herramienta prestada vuelve distinta.\n\n"
            "El invierno en que se enfermó, me pidió que le llevara la caja a "
            "la cama. La abrió, sacó un formón, lo miró un rato largo y me lo "
            "pasó sin decir nada. Yo tenía veintitrés años y no supe qué hacer "
            "con las manos.\n\n"
            "Después de que murió encontré, en el fondo de la caja, un sobre "
            "con mi nombre escrito con su letra grande y despareja. Estaba "
            "cerrado. Lo llevé conmigo tres meses en el bolsillo del abrigo, "
            "hasta que el papel se puso blando de tanto doblarse.\n\n"
            "Nunca lo abrí. No por miedo a lo que dijera, sino porque mientras "
            "estuviera cerrado había algo de él que todavía no había terminado "
            "de pasar. Lo guardé en la caja, junto al formón, y cerré la tapa "
            "con las junturas ajustadas que él había hecho para que no entrara "
            "el polvo."
        ),
    },
    {
        "key": "pantallas",
        "title": "Dormir con el teléfono al lado",
        "kind": "no_literario",
        "source_note": "Texto original de 1000paes",
        "body": (
            "Durante años se repitió que la luz azul de las pantallas era la "
            "culpable del mal dormir de los adolescentes. La explicación era "
            "elegante: esa luz suprime la melatonina, la hormona que le avisa "
            "al cuerpo que es de noche, y por lo tanto retrasa el sueño.\n\n"
            "Los estudios recientes complican esa historia. La cantidad de luz "
            "que emite un teléfono a treinta centímetros de la cara es bastante "
            "menor que la de una ampolleta de techo, y bastante menor todavía "
            "que la luz del día. Si la luz azul fuera el factor decisivo, "
            "cualquier persona que enciende la luz del living después de las "
            "diez debería tener el mismo problema.\n\n"
            "Lo que sí aparece con fuerza en los datos es otra cosa: no importa "
            "tanto la luz como lo que se hace con el aparato. Un video que "
            "termina y encadena con el siguiente, un chat que sigue activo, una "
            "notificación que llega a las dos de la mañana. El teléfono no "
            "impide dormir porque ilumine, sino porque está diseñado para que "
            "no se termine nunca.\n\n"
            "La diferencia importa a la hora de recomendar algo. Si el problema "
            "fuera la luz, bastaría con el modo nocturno que tiñe la pantalla "
            "de amarillo. Si el problema es el diseño de las aplicaciones, ese "
            "modo no sirve de nada y lo que hay que cambiar es dónde pasa la "
            "noche el aparato."
        ),
    },
    {
        "key": "ballenas",
        "title": "El canto que bajó de tono",
        "kind": "no_literario",
        "source_note": "Texto original de 1000paes",
        "body": (
            "Las ballenas azules cantan en frecuencias tan bajas que el oído "
            "humano apenas las alcanza. Ese canto viaja cientos de kilómetros "
            "bajo el agua, y por eso durante la Guerra Fría la marina "
            "estadounidense llenó los océanos de micrófonos submarinos: "
            "buscaba submarinos soviéticos, no ballenas. Las grabaciones "
            "quedaron archivadas durante décadas.\n\n"
            "Cuando esos archivos se abrieron a los científicos, apareció algo "
            "que nadie estaba buscando. Comparando registros de los años "
            "sesenta con los actuales, el tono del canto de las ballenas "
            "azules había bajado de manera sostenida en todas las poblaciones "
            "del planeta, en algunas cerca de un tercio.\n\n"
            "Las explicaciones compiten. Una dice que, al recuperarse las "
            "poblaciones tras el fin de la caza industrial, las ballenas ya no "
            "necesitan cantar tan fuerte para encontrarse: los tonos graves "
            "llegan más lejos, pero exigen más energía, y solo conviene bajar "
            "el tono cuando hay a quién alcanzar. Otra apunta al ruido de los "
            "barcos, que obligaría a buscar frecuencias menos ocupadas. Una "
            "tercera sugiere que los animales simplemente son más grandes que "
            "antes.\n\n"
            "Ninguna se ha impuesto todavía. Lo que sí quedó claro es otra "
            "cosa: el hallazgo no fue posible por un experimento diseñado para "
            "responder la pregunta, sino porque alguien guardó, con otro "
            "propósito y durante mucho tiempo, un registro que después sirvió "
            "para algo que su autor no imaginaba."
        ),
    },
    {
        "key": "columna_celular",
        "title": "Guardar el celular no es un castigo",
        "kind": "no_literario",
        "source_note": "Columna de opinión escrita por 1000paes para ejercitar lectura argumentativa",
        "body": (
            "Cada vez que un colegio anuncia que los celulares se guardan "
            "durante la jornada, aparece la misma objeción: los aparatos son "
            "parte del mundo y lo que corresponde es enseñar a usarlos, no "
            "esconderlos. El argumento suena razonable y por eso conviene "
            "tomárselo en serio.\n\n"
            "El problema es que supone que la atención es una cuestión de "
            "voluntad. No lo es. Un teléfono sobre el banco no interrumpe solo "
            "cuando suena: interrumpe también cuando no suena, porque una parte "
            "de la cabeza queda ocupada esperando que suene. Pedirle a alguien "
            "de quince años que ignore un aparato diseñado por equipos enteros "
            "para que no pueda ser ignorado no es educarlo, es dejarlo solo "
            "frente a una pelea desigual.\n\n"
            "Guardar el teléfono tampoco enseña nada por sí mismo, y ahí los "
            "críticos tienen razón. Una caja con candado a la entrada de la "
            "sala no es una política educativa; es apenas la condición para que "
            "exista una. Lo que la medida hace es devolver algo que se había "
            "vuelto escaso: bloques largos de clase sin interrupciones, que es "
            "donde ocurre lo difícil de aprender.\n\n"
            "La discusión, entonces, no debería ser si guardar o no guardar. "
            "Debería ser qué se hace con el tiempo que se recupera. Si la hora "
            "sin teléfono se llena con la misma clase de siempre, la medida no "
            "habrá servido de mucho."
        ),
    },
    {
        "key": "feria",
        "title": "Los sábados en la feria",
        "kind": "literario",
        "source_note": "Texto original de 1000paes",
        "body": (
            "Mi abuela no compraba en el primer puesto. Recorría la feria "
            "entera, de punta a punta, tocando los tomates sin apretarlos, "
            "preguntando precios que no anotaba en ninguna parte, y recién en "
            "la vuelta de regreso empezaba a comprar. Yo caminaba detrás con el "
            "carro vacío, impaciente, seguro de que estábamos perdiendo el "
            "tiempo.\n\n"
            "—Ya vimos ese —le decía.\n\n"
            "—Vimos el precio —me corregía—. No vimos al que lo vende.\n\n"
            "Le compraba siempre al mismo señor de las paltas, que no era el "
            "más barato. Cuando le pregunté por qué, me dijo que ese hombre le "
            "había fiado tres semanas el invierno en que mi abuelo estuvo sin "
            "trabajo, y que eso no se paga con dinero pero se sigue pagando.\n\n"
            "Ahora voy solo. Recorro la feria entera antes de comprar, aunque "
            "ya sé dónde está todo, y me demoro más de lo necesario. El señor "
            "de las paltas murió hace años; le compro al hijo, que no me "
            "conoce. No sabría explicarle por qué vengo hasta acá pudiendo "
            "comprar en cualquier parte."
        ),
    },
    {
        "key": "poema_puerto",
        "title": "Puerto en invierno",
        "kind": "literario",
        "source_note": "Poema original de 1000paes",
        "body": (
            "Los barcos aprendieron a esperar\n"
            "mejor que los hombres:\n"
            "no miran la hora,\n"
            "no preguntan cuándo.\n\n"
            "Mi padre trabajó treinta años en la grúa,\n"
            "bajando cajas que venían de países\n"
            "cuyos nombres nunca supo pronunciar\n"
            "y a los que jamás fue.\n\n"
            "Decía que el puerto es una puerta\n"
            "que se abre siempre hacia el otro lado.\n\n"
            "Hoy la grúa tiene otro apellido,\n"
            "el muelle otro dueño,\n"
            "y el mar —que no firma contratos—\n"
            "sigue golpeando las mismas piedras\n"
            "con la paciencia de lo que no se va."
        ),
    },
    {
        "key": "tabla_lectura",
        "title": "Tiempo de lectura por placer, según edad",
        "kind": "discontinuo",
        "source_note": "Tabla construida con datos ficticios por 1000paes para ejercitar lectura de textos discontinuos. No corresponde a una encuesta real.",
        "body": (
            "Minutos diarios promedio dedicados a leer por placer\n\n"
            "| Edad | Libros en papel | Textos en pantalla | Total |\n"
            "|---|---|---|---|\n"
            "| 10 años | 21 | 6 | 27 |\n"
            "| 12 años | 17 | 11 | 28 |\n"
            "| 14 años | 9 | 19 | 28 |\n"
            "| 16 años | 6 | 17 | 23 |\n"
            "| 18 años | 5 | 12 | 17 |\n\n"
            "Nota metodológica: se contabiliza solo la lectura voluntaria; "
            "queda fuera la lectura exigida por el colegio. «Textos en "
            "pantalla» incluye artículos, foros y publicaciones extensas, y "
            "excluye mensajería instantánea."
        ),
    },
    {
        "key": "instructivo_sismo",
        "title": "Qué hacer cuando tiembla",
        "kind": "no_literario",
        "source_note": "Texto instruccional escrito por 1000paes",
        "body": (
            "Durante el sismo, la instrucción es una sola: agacharse, cubrirse "
            "y afirmarse. Agacharse antes de que el movimiento lo tire al "
            "suelo; cubrirse la cabeza y el cuello bajo una mesa firme; "
            "afirmarse de esa mesa para desplazarse con ella si se mueve.\n\n"
            "No corra hacia la salida mientras tiembla. La mayoría de las "
            "lesiones en terremotos no las causa el derrumbe del edificio sino "
            "los objetos que caen y los vidrios que se quiebran, y ambos están "
            "justo en el camino de quien corre. Tampoco use el ascensor ni se "
            "pare bajo el marco de una puerta: en las construcciones actuales "
            "ese marco no es más resistente que el resto de la estructura.\n\n"
            "Terminado el movimiento, revise si hay olor a gas antes de "
            "encender cualquier luz o aparato. Si vive en la costa y el sismo "
            "fue tan fuerte que le costó mantenerse en pie, o duró más de un "
            "minuto, evacúe hacia una zona alta sin esperar ninguna alarma: esa "
            "es la alarma. No vuelva hasta que la autoridad lo indique, aunque "
            "el mar se vea tranquilo, porque la primera ola no suele ser la "
            "mayor."
        ),
    },
]


def _ql(
    passage: str,
    skill_node: str,
    difficulty: str,
    stem: str,
    correct: str,
    explanation: str,
    distractors: list[tuple[str, str]],
):
    """Pregunta de Competencia Lectora, asociada a un texto base.

    Igual que `_q` pero con `passage`, que apunta al `key` de PASSAGES. La
    explicación siempre remite a lo que el texto dice, porque en esta prueba la
    respuesta correcta se justifica con el texto y no con conocimiento previo.
    """
    d = _q(skill_node, difficulty, stem, correct, explanation, distractors)
    d["passage"] = passage
    return d


QUESTIONS_LECTORA = [
    # ---------- "El insecto que cambió de casa" ----------
    _ql(
        "vinchuca", "lec_localizar", "facil",
        "Según el texto, ¿dónde vivía la vinchuca antes de que llegara la "
        "agricultura a los valles?",
        "Entre las piedras y las madrigueras de roedores silvestres",
        "La respuesta está en el primer párrafo, que describe dónde vivía el "
        "insecto durante siglos: «refugiada entre las piedras y las madrigueras "
        "de roedores silvestres».\n\n"
        "Es una pregunta de localizar: el dato aparece dicho con todas sus "
        "letras y no hay que deducir nada. Basta con volver al párrafo donde el "
        "texto habla del pasado del insecto.",
        [
            ("En las casas de adobe de los valles", "Ahí se mudó DESPUÉS de que llegó la agricultura; el texto lo presenta como el cambio, no como el punto de partida."),
            ("En los techos de paja de las viviendas", "Los techos de paja aparecen como parte del refugio nuevo, no del original."),
            ("En los cultivos de los valles agrícolas", "El texto nunca dice que viviera en los cultivos: menciona la agricultura como la causa del cambio, no como su hábitat."),
        ],
    ),
    _ql(
        "vinchuca", "lec_localizar", "medio",
        "De acuerdo con el texto, ¿por qué la picadura de la vinchuca suele "
        "pasar inadvertida?",
        "El texto lo afirma sin explicar la causa",
        "Acá hay que distinguir entre lo que el texto dice y lo que uno supone. "
        "El tercer párrafo afirma que la picadura «suele pasar inadvertida», "
        "pero en ningún momento explica por qué.\n\n"
        "La pregunta pone a prueba si el lector se queda con lo que está "
        "escrito o completa con conocimiento propio. En una prueba de "
        "comprensión, lo que no está en el texto no se puede afirmar.",
        [
            ("Porque el insecto pica mientras la persona duerme", "Es una explicación plausible, pero el texto no la da: sería completar con lo que uno imagina."),
            ("Porque la vinchuca inyecta una sustancia anestésica", "El texto no menciona ninguna sustancia anestésica. Es información traída de afuera."),
            ("Porque la herida es demasiado pequeña para verse", "El texto no describe el tamaño de la herida en ningún momento."),
        ],
    ),
    _ql(
        "vinchuca", "lec_interpretar", "medio",
        "¿Qué relación establece el texto entre la agricultura y la enfermedad "
        "de Chagas?",
        "La agricultura creó viviendas que resultaron mejores refugios para el "
        "insecto, acercándolo a las personas",
        "La relación es indirecta y hay que armarla uniendo dos párrafos.\n\n"
        "1) El segundo párrafo dice que con la agricultura llegaron las casas "
        "de adobe, y que esas casas fueron para el insecto un refugio mejor que "
        "las piedras.\n"
        "2) El tercero explica que el contacto con el insecto es lo que "
        "transmite el parásito.\n\n"
        "Encadenando ambos: la agricultura no causa la enfermedad, pero produce "
        "las condiciones que ponen al insecto donde están las personas. El "
        "propio texto subraya que «el insecto no fue buscado por nadie».",
        [
            ("La agricultura introdujo el parásito que provoca la enfermedad", "El texto nunca dice que la agricultura trajera el parásito: el insecto ya lo portaba."),
            ("Los cultivos atrajeron a los roedores que contagian a las personas", "Los roedores aparecen solo como parte del hábitat original del insecto, y el texto no dice que contagien a nadie."),
            ("La agricultura obligó a las vinchucas a alimentarse de sangre humana", "El texto dice que el insecto se alimenta de sangre desde siempre y que se quedó donde le convenía, no que fuera forzado."),
        ],
    ),
    _ql(
        "vinchuca", "lec_evaluar", "dificil",
        "¿Cuál es el propósito principal del último párrafo del texto?",
        "Extraer una lección general sobre cómo se combaten las enfermedades",
        "El último párrafo cambia de nivel: deja de hablar de la vinchuca en "
        "particular y saca una conclusión que vale más allá del caso.\n\n"
        "La frase que lo delata es la del cierre: «muestra algo que se repite en "
        "salud pública: a veces la forma más eficaz de combatir una enfermedad "
        "no es atacar al organismo que la transmite, sino cambiar las "
        "condiciones que lo hacen prosperar».\n\n"
        "El caso concreto pasa a ser un ejemplo de un principio más amplio. Esa "
        "es la función del párrafo dentro del texto.",
        [
            ("Detallar las técnicas de construcción que reemplazaron al adobe", "El párrafo menciona los cambios de vivienda, pero solo como apoyo: no se detiene en cómo se construye."),
            ("Criticar el uso de insecticidas en las campañas sanitarias", "El texto compara ambas estrategias y dice que una funcionó mejor, pero no critica el uso de insecticidas."),
            ("Explicar cuándo aparecen los síntomas de la enfermedad", "Eso corresponde al párrafo anterior, que habla de los daños que aparecen décadas después."),
        ],
    ),

    # ---------- "La carta que no se envió" ----------
    _ql(
        "carta", "lec_localizar", "facil",
        "¿Qué objeto le entrega el padre al narrador cuando está enfermo?",
        "Un formón",
        "El dato está en el segundo párrafo: el padre «sacó un formón, lo miró "
        "un rato largo y me lo pasó sin decir nada».\n\n"
        "Es información explícita. La dificultad está en no confundir este "
        "objeto con los otros que aparecen en el relato: la caja, que el padre "
        "pide que le lleven, y el sobre, que el narrador encuentra después de "
        "su muerte.",
        [
            ("La caja de madera con las herramientas", "El narrador le lleva la caja a la cama; no es algo que el padre le entregue."),
            ("Un sobre cerrado con su nombre", "El sobre aparece después de la muerte del padre, en el fondo de la caja."),
            ("Las junturas ajustadas que él había hecho", "Las junturas son una característica de la caja, no un objeto que se pueda entregar."),
        ],
    ),
    _ql(
        "carta", "lec_interpretar", "dificil",
        "¿Qué sugiere el narrador cuando dice que no abrió la carta «porque "
        "mientras estuviera cerrado había algo de él que todavía no había "
        "terminado de pasar»?",
        "Que dejar la carta cerrada le permitía sentir que el vínculo con su "
        "padre seguía abierto",
        "La frase hay que leerla junto a lo que el narrador descarta antes: "
        "aclara que no fue «por miedo a lo que dijera». Es decir, el contenido "
        "no es el punto.\n\n"
        "Lo que dice es que el sobre cerrado mantiene algo en suspenso. Mientras "
        "no se lea, queda una parte del padre que todavía no ocurre del todo, y "
        "por lo tanto tampoco termina. Abrirlo sería cerrar eso último.\n\n"
        "El gesto final refuerza la lectura: guarda la carta junto al formón, en "
        "la caja que el padre construyó, y cierra la tapa.",
        [
            ("Que temía que la carta contuviera un reproche de su padre", "El narrador descarta esa lectura de forma explícita: dice que no fue por miedo a lo que dijera."),
            ("Que planeaba leerla cuando estuviera preparado emocionalmente", "El texto no anuncia ninguna intención de leerla más adelante: dice «nunca lo abrí» y la guarda."),
            ("Que la carta era el único recuerdo material que le quedaba", "No es el único: también están la caja y el formón, que el relato destaca."),
        ],
    ),
    _ql(
        "carta", "lec_evaluar", "dificil",
        "El relato menciona dos veces «las junturas tan ajustadas». ¿Qué efecto "
        "produce esa repetición al final del texto?",
        "Cierra el relato con la misma imagen del comienzo, dándole al gesto "
        "final el peso de lo que el padre hacía bien",
        "La imagen aparece al principio describiendo el oficio del padre: hizo "
        "la caja «con las junturas tan ajustadas que no necesitaba clavos». Es "
        "un detalle de competencia, de alguien que sabe hacer las cosas.\n\n"
        "Al final vuelve, pero ahora es el hijo quien cierra la tapa «con las "
        "junturas ajustadas que él había hecho». El narrador no construyó nada: "
        "usa lo que su padre dejó hecho.\n\n"
        "El texto termina donde empezó, y esa vuelta convierte un gesto simple "
        "en el cierre del relato.",
        [
            ("Subraya que el narrador aprendió el oficio de carpintero de su padre", "El relato dice lo contrario: al narrador le dejaban mirar, nunca tocar, y no se menciona que aprendiera el oficio."),
            ("Indica que la caja estaba en mal estado y necesitaba repararse", "Nada en el texto sugiere deterioro: las junturas ajustadas son señal de que la caja está bien hecha."),
            ("Anticipa que el narrador abrirá la carta más adelante", "El cierre apunta a lo contrario: guarda la carta y cierra la tapa."),
        ],
    ),

    # ---------- "Dormir con el teléfono al lado" ----------
    _ql(
        "pantallas", "lec_localizar", "medio",
        "Según el texto, ¿qué compara el autor con la luz que emite un teléfono "
        "a treinta centímetros de la cara?",
        "La luz de una ampolleta de techo y la luz del día",
        "El segundo párrafo hace la comparación de forma directa: esa luz «es "
        "bastante menor que la de una ampolleta de techo, y bastante menor "
        "todavía que la luz del día».\n\n"
        "El punto de la comparación es mostrar que, si la luz azul fuera "
        "decisiva, encender cualquier luz de la casa tendría el mismo efecto.",
        [
            ("La luz de una pantalla de computador y la de un televisor", "El texto no menciona computadores ni televisores en ningún momento."),
            ("La luz del modo nocturno y la de la pantalla normal", "El modo nocturno aparece recién en el último párrafo, y no como término de esta comparación."),
            ("La luz de la mañana y la del atardecer", "El texto habla de «la luz del día» en general, sin distinguir momentos."),
        ],
    ),
    _ql(
        "pantallas", "lec_interpretar", "medio",
        "¿Qué quiere decir el texto con que el teléfono «está diseñado para que "
        "no se termine nunca»?",
        "Que las aplicaciones encadenan contenido de forma continua, sin un "
        "punto natural de término",
        "La frase resume los ejemplos que el propio párrafo entrega justo antes: "
        "«un video que termina y encadena con el siguiente, un chat que sigue "
        "activo, una notificación que llega a las dos de la mañana».\n\n"
        "Todos comparten un rasgo: no hay un momento en que el contenido se "
        "acabe y uno pueda decir que terminó. El diseño evita ese punto de "
        "corte, y eso es lo que retrasa el sueño según el texto.",
        [
            ("Que la batería de los teléfonos dura toda la noche", "El texto no habla de batería ni de autonomía en ningún momento."),
            ("Que los teléfonos están construidos para no descomponerse", "«No se termine» se refiere al contenido, no a la vida útil del aparato."),
            ("Que las notificaciones llegan incluso con el aparato apagado", "El texto menciona notificaciones de madrugada, pero nunca dice que lleguen con el teléfono apagado."),
        ],
    ),
    _ql(
        "pantallas", "lec_evaluar", "dificil",
        "¿Qué función cumple el último párrafo respecto del resto del texto?",
        "Muestra que la diferencia entre ambas explicaciones cambia qué "
        "recomendación tiene sentido dar",
        "El texto viene discutiendo dos explicaciones del mal dormir: la luz "
        "azul y el diseño de las aplicaciones. El último párrafo responde a la "
        "pregunta de por qué importa distinguirlas.\n\n"
        "Y lo hace de forma concreta: si el problema fuera la luz, bastaría con "
        "el modo nocturno; si es el diseño, ese modo «no sirve de nada» y hay "
        "que cambiar dónde pasa la noche el aparato.\n\n"
        "O sea, el párrafo lleva la discusión desde la causa hasta la "
        "consecuencia práctica. Sin él, el texto quedaría en una corrección "
        "teórica sin utilidad.",
        [
            ("Reconoce que la evidencia sobre la luz azul sigue siendo válida", "El párrafo hace lo contrario: usa la hipótesis de la luz como el caso en que la recomendación NO funcionaría."),
            ("Propone eliminar el modo nocturno de los teléfonos", "El texto dice que ese modo no serviría si el problema es el diseño, pero no propone eliminarlo."),
            ("Resume los estudios recientes citados en el texto", "El párrafo no resume estudios: extrae la consecuencia práctica de la discusión anterior."),
        ],
    ),
    # ---------- "El canto que bajó de tono" ----------
    _ql(
        "ballenas", "lec_localizar", "facil",
        "Según el texto, ¿con qué propósito se instalaron los micrófonos "
        "submarinos que después sirvieron para estudiar a las ballenas?",
        "Para detectar submarinos soviéticos durante la Guerra Fría",
        "El primer párrafo lo dice de forma directa: la marina estadounidense "
        "llenó los océanos de micrófonos porque «buscaba submarinos "
        "soviéticos, no ballenas».\n\n"
        "Es una pregunta de localizar. El texto incluso subraya el contraste "
        "entre el motivo original y el uso posterior, así que el dato no hay "
        "que deducirlo: está escrito.",
        [
            ("Para estudiar el canto de las ballenas azules", "El texto niega esto expresamente: los micrófonos no se pusieron para eso, y ahí está la gracia de la historia."),
            ("Para medir el ruido que producen los barcos", "El ruido de los barcos aparece después, como una de las explicaciones posibles del fenómeno, no como el motivo de las grabaciones."),
            ("Para vigilar la caza industrial de ballenas", "El fin de la caza industrial se menciona en otra parte del texto y nada lo vincula con la instalación de los micrófonos."),
        ],
    ),
    _ql(
        "ballenas", "lec_localizar", "medio",
        "De acuerdo con el texto, ¿qué relación hay entre el tono del canto y "
        "la energía que gasta el animal?",
        "Los tonos más graves llegan más lejos, pero exigen más energía",
        "El tercer párrafo entrega las dos mitades del dato en una sola frase: "
        "«los tonos graves llegan más lejos, pero exigen más energía».\n\n"
        "La pregunta exige leer la frase completa. Quedarse con la primera "
        "mitad —que los graves llegan más lejos— deja fuera justamente el "
        "costo que hace interesante la explicación.",
        [
            ("Los tonos más graves llegan más lejos y ahorran energía", "Invierte el costo: el texto dice que exigen más energía, y por eso bajarlos es una decisión y no una ganancia gratis."),
            ("Los tonos más agudos llegan más lejos y exigen más energía", "El texto atribuye el mayor alcance a los graves, no a los agudos."),
            ("El texto no relaciona el tono con el gasto de energía", "Sí lo hace, y esa relación es la base de la primera explicación que presenta."),
        ],
    ),
    _ql(
        "ballenas", "lec_interpretar", "medio",
        "La explicación que atribuye el cambio a la recuperación de las "
        "poblaciones supone que las ballenas cantan de cierto modo porque",
        "hay más individuos cerca a los que alcanzar con el canto",
        "El texto razona así: cantar grave cuesta más energía y solo «conviene "
        "bajar el tono cuando hay a quién alcanzar». Si las poblaciones se "
        "recuperaron tras el fin de la caza, hay más ballenas cerca y ya no "
        "hace falta gritar tan fuerte para encontrarse.\n\n"
        "Esto es interpretar: la idea no está enunciada como tal, hay que "
        "armarla uniendo el costo energético con el aumento de individuos que "
        "el párrafo menciona.",
        [
            ("el ruido de los barcos les tapó las frecuencias agudas", "Esa es otra de las explicaciones que el texto presenta, y es distinta de la que pregunta el enunciado."),
            ("su cuerpo creció y ya no pueden emitir sonidos agudos", "Corresponde a la tercera explicación, la del tamaño, no a la de la recuperación poblacional."),
            ("aprendieron a imitar el sonido de los submarinos", "El texto no sugiere nada parecido; los submarinos solo aparecen como motivo de las grabaciones."),
        ],
    ),
    _ql(
        "ballenas", "lec_evaluar", "medio",
        "¿Qué actitud adopta el texto frente a las tres explicaciones que "
        "presenta?",
        "Las expone como alternativas en competencia y advierte que ninguna se "
        "ha impuesto",
        "El texto introduce las explicaciones diciendo que «compiten» y cierra "
        "esa discusión con una frase explícita: «ninguna se ha impuesto "
        "todavía».\n\n"
        "Evaluar incluye reconocer cuánta certeza reclama un texto. Este "
        "informa un desacuerdo abierto entre científicos en vez de resolverlo, "
        "y lo dice con todas sus letras.",
        [
            ("Defiende la explicación de la recuperación de las poblaciones", "Es la primera que menciona, pero el texto no la respalda por sobre las otras dos."),
            ("Descarta las tres por falta de evidencia suficiente", "No las descarta: dice que todavía no hay una ganadora, que es distinto de rechazarlas."),
            ("Las presenta como versiones distintas de una misma idea", "El texto las contrapone —recuperación, ruido, tamaño— y por eso dice que compiten entre sí."),
        ],
    ),
    _ql(
        "ballenas", "lec_evaluar", "dificil",
        "¿Qué función cumple el último párrafo dentro del texto?",
        "Extrae una lección sobre el valor de los registros conservados con "
        "otro fin",
        "El párrafo abandona la discusión sobre el tono y se detiene en cómo "
        "fue posible el hallazgo: «alguien guardó, con otro propósito y "
        "durante mucho tiempo, un registro que después sirvió para algo que su "
        "autor no imaginaba».\n\n"
        "No agrega evidencia ni toma partido entre las explicaciones; cambia "
        "de nivel y comenta el episodio completo. Reconocer ese giro es lo que "
        "distingue leer el contenido de leer la construcción del texto.",
        [
            ("Resuelve la discusión entre las tres explicaciones posibles", "El párrafo empieza justamente reconociendo que ninguna se impuso; no resuelve nada."),
            ("Resume los datos entregados en los párrafos anteriores", "No repite datos: introduce una idea nueva sobre el origen del registro."),
            ("Critica a la marina por haber ocultado las grabaciones", "El texto dice que los archivos se abrieron a los científicos y no reprocha nada."),
        ],
    ),
    # ---------- "Guardar el celular no es un castigo" ----------
    _ql(
        "columna_celular", "lec_localizar", "facil",
        "¿Cuál es la objeción a guardar los celulares que menciona el texto al "
        "comienzo?",
        "Que los aparatos son parte del mundo y corresponde enseñar a usarlos",
        "El primer párrafo la enuncia tal cual: cada vez que un colegio "
        "anuncia la medida «aparece la misma objeción: los aparatos son parte "
        "del mundo y lo que corresponde es enseñar a usarlos, no "
        "esconderlos».\n\n"
        "Localizar acá tiene una dificultad extra: la objeción es de otros, no "
        "del autor. Hay que ubicar el dato sin confundirlo con la postura de "
        "quien escribe.",
        [
            ("Que las cajas con candado son demasiado caras para los colegios", "El texto menciona la caja con candado, pero nunca discute su costo."),
            ("Que los estudiantes necesitan el teléfono para emergencias", "Es una objeción habitual en la vida real, pero este texto no la trae."),
            ("Que la medida no mejora los resultados académicos", "El texto no cita resultados académicos en ninguna parte."),
        ],
    ),
    _ql(
        "columna_celular", "lec_interpretar", "medio",
        "Cuando el texto afirma que el teléfono «interrumpe también cuando no "
        "suena», quiere decir que",
        "la sola posibilidad de un aviso ya ocupa parte de la atención",
        "La frase siguiente lo explica: «una parte de la cabeza queda ocupada "
        "esperando que suene». La interrupción no es el sonido sino la espera "
        "del sonido.\n\n"
        "Interpretar una expresión así exige apoyarse en lo que viene "
        "inmediatamente después, que es donde el texto aclara su propia "
        "imagen.",
        [
            ("los teléfonos actuales emiten avisos silenciosos constantemente", "El texto no habla de avisos silenciosos: habla de la espera del aviso, que ocurre en la cabeza del estudiante."),
            ("los estudiantes revisan el teléfono aunque esté apagado", "El texto nunca menciona aparatos apagados ni describe esa conducta."),
            ("el profesor pierde tiempo pidiendo que guarden el aparato", "Ese conflicto no aparece; la interrupción de la que habla el texto es de la atención, no de la clase."),
        ],
    ),
    _ql(
        "columna_celular", "lec_interpretar", "dificil",
        "¿Qué idea sostiene la comparación con «una pelea desigual»?",
        "Que un estudiante enfrenta solo a aparatos diseñados por equipos "
        "expertos para captar su atención",
        "La imagen cierra una frase que contrapone dos fuerzas: alguien «de "
        "quince años» por un lado y «un aparato diseñado por equipos enteros "
        "para que no pueda ser ignorado» por el otro. Lo desigual es esa "
        "asimetría.\n\n"
        "El punto que la comparación defiende es que no se trata de falta de "
        "voluntad, y por eso el texto la usa justo después de negar que la "
        "atención sea una cuestión de carácter.",
        [
            ("Que los profesores no tienen herramientas para competir con el celular", "El texto centra la asimetría en el estudiante frente al aparato, no en el profesor."),
            ("Que unos estudiantes tienen mejores teléfonos que otros", "La desigualdad de la que habla el texto no es entre estudiantes, sino entre el estudiante y el diseño del aparato."),
            ("Que los adolescentes se distraen más que los adultos", "El texto no compara edades; su argumento es que la atención no depende de la voluntad de nadie."),
        ],
    ),
    _ql(
        "columna_celular", "lec_evaluar", "medio",
        "¿Con qué propósito el autor escribe que «ahí los críticos tienen "
        "razón»?",
        "Para conceder un punto a quienes se oponen y precisar el alcance de "
        "su propia postura",
        "El autor admite que guardar el teléfono «tampoco enseña nada por sí "
        "mismo», que es exactamente lo que sostienen sus adversarios. Acto "
        "seguido acota su tesis: la medida no es una política educativa sino "
        "«la condición para que exista una».\n\n"
        "Ceder un punto y usar esa concesión para afinar la propia posición es "
        "un movimiento argumentativo, no un cambio de bando. Reconocerlo es "
        "parte de evaluar cómo está construido un texto.",
        [
            ("Para abandonar su postura inicial sobre la medida", "No la abandona: inmediatamente después explica qué sí logra la medida y en qué debería continuar."),
            ("Para ironizar sobre quienes se oponen a la medida", "No hay ironía; el texto ya había dicho que la objeción «conviene tomársela en serio»."),
            ("Para introducir un dato que respalda a los críticos", "No introduce ningún dato: hace una concesión de razonamiento, sin evidencia nueva."),
        ],
    ),
    _ql(
        "columna_celular", "lec_evaluar", "dificil",
        "¿Cuál de estas afirmaciones resume mejor la tesis del texto?",
        "Guardar el teléfono no educa por sí solo, pero crea la condición para "
        "que la clase pueda hacerlo",
        "El texto niega que la medida sea una política educativa y a la vez "
        "defiende que devuelve algo escaso: «bloques largos de clase sin "
        "interrupciones». El cierre lo confirma al decir que lo que importa es "
        "qué se hace con el tiempo recuperado.\n\n"
        "Una tesis bien resumida tiene que sostener las dos mitades. Quedarse "
        "solo con «hay que guardar los teléfonos» pierde precisamente la parte "
        "que el autor concede.",
        [
            ("Los colegios deben prohibir los celulares porque distraen a los estudiantes", "Recoge la mitad del texto y deja fuera la concesión, que es donde el autor precisa su postura."),
            ("Enseñar a usar el teléfono es preferible a guardarlo durante la jornada", "Esa es la objeción que el texto discute, no su tesis."),
            ("El tiempo de clase sin interrupciones ya no existe en los colegios", "El texto dice que se volvió escaso, no que haya desaparecido, y esa no es su conclusión."),
        ],
    ),
    # ---------- "Los sábados en la feria" ----------
    _ql(
        "feria", "lec_localizar", "facil",
        "Según el relato, ¿por qué la abuela le compraba siempre al mismo "
        "vendedor de paltas?",
        "Porque él le había fiado cuando su marido estuvo sin trabajo",
        "El narrador lo pregunta y la abuela responde: ese hombre «le había "
        "fiado tres semanas el invierno en que mi abuelo estuvo sin "
        "trabajo».\n\n"
        "El dato está dicho de manera explícita, en el mismo párrafo donde "
        "aparece la pregunta del nieto.",
        [
            ("Porque vendía las paltas más baratas de la feria", "El texto dice lo contrario: «no era el más barato»."),
            ("Porque era el único puesto que quedaba de regreso", "El recorrido de vuelta explica cuándo compraba, no a quién le compraba."),
            ("Porque sus paltas eran de mejor calidad que las otras", "El relato nunca compara la calidad de la fruta; la razón que da la abuela es otra."),
        ],
    ),
    _ql(
        "feria", "lec_interpretar", "medio",
        "Cuando la abuela responde «Vimos el precio. No vimos al que lo "
        "vende», está señalando que",
        "en su decisión de compra pesa la persona y no solo el valor del "
        "producto",
        "La corrección de la abuela separa dos cosas que el nieto confundía: "
        "el precio del puesto y quién está detrás del puesto. El relato le da "
        "la razón después, cuando explica que le compra al que la ayudó "
        "aunque no sea el más barato.\n\n"
        "Interpretar un diálogo así es reconstruir lo que el personaje "
        "sostiene sin decirlo de forma directa.",
        [
            ("los precios de la feria cambian de un puesto a otro", "Eso es cierto en la feria, pero no es lo que la abuela está corrigiendo con su frase."),
            ("conviene recorrer toda la feria antes de decidir", "Describe su costumbre, no lo que la frase agrega: la frase habla del vendedor, no del recorrido."),
            ("el nieto no prestaba atención a lo que ella hacía", "El nieto sí observaba; lo que no entendía era el criterio, que es lo que la abuela le señala."),
        ],
    ),
    _ql(
        "feria", "lec_interpretar", "dificil",
        "¿Qué quiere decir la abuela con que eso «no se paga con dinero pero "
        "se sigue pagando»?",
        "Que el gesto recibido genera una lealtad que se sostiene en el tiempo",
        "La frase distingue entre saldar una cuenta y corresponder a un favor. "
        "El dinero de esas tres semanas pudo devolverse; la deuda que ella "
        "reconoce se paga volviendo cada sábado al mismo puesto.\n\n"
        "Que el relato termine con el nieto comprándole al hijo del vendedor "
        "confirma esa lectura: el pago continúa incluso cuando ya no queda "
        "ninguno de los dos originales.",
        [
            ("Que la deuda económica nunca alcanzó a saldarse por completo", "El relato no plantea una deuda pendiente de dinero; distingue el dinero de otra cosa."),
            ("Que el vendedor le cobraba más caro por haberle fiado antes", "Nada indica un cobro extra; el texto solo dice que no era el más barato."),
            ("Que la abuela prefería no hablar de los años difíciles", "Al contrario: se los cuenta al nieto cuando él pregunta."),
        ],
    ),
    _ql(
        "feria", "lec_interpretar", "medio",
        "¿Qué cambio ocurre en el narrador entre el comienzo y el final del "
        "relato?",
        "Pasa de considerar el recorrido una pérdida de tiempo a repetirlo por "
        "su cuenta",
        "Al comienzo camina detrás «impaciente, seguro de que estábamos "
        "perdiendo el tiempo». Al final recorre la feria entera aunque ya sabe "
        "dónde está todo y se demora «más de lo necesario».\n\n"
        "El cambio no se declara: se muestra repitiendo la misma conducta con "
        "otro sentido. Compararlas es lo que responde la pregunta.",
        [
            ("Pasa de acompañar a su abuela a hacer las compras del hogar", "El texto no dice de quién son las compras ahora; el cambio que muestra es de actitud."),
            ("Pasa de desconfiar del vendedor a confiar en su hijo", "El narrador dice que el hijo no lo conoce, y nunca desconfió del padre."),
            ("Pasa de comprar en la feria a comprar en cualquier parte", "Es lo contrario: podría comprar en cualquier parte y sin embargo sigue yendo."),
        ],
    ),
    _ql(
        "feria", "lec_evaluar", "dificil",
        "¿Qué efecto produce que el relato termine con el narrador diciendo "
        "que «no sabría explicarle por qué vengo hasta acá»?",
        "Muestra que la costumbre heredada sigue operando aunque él no pueda "
        "justificarla",
        "El narrador conserva el gesto —recorrer entero, comprar en ese "
        "puesto— cuando ya no están ni la abuela ni el vendedor que le daban "
        "sentido. Que no pueda explicarlo es justamente el punto: lo aprendido "
        "sobrevive a la razón que lo originó.\n\n"
        "Evaluar un cierre así es preguntarse qué gana el relato terminando "
        "ahí. Si el narrador explicara su motivo, la escena se volvería una "
        "moraleja; al no hacerlo, deja el gesto en pie.",
        [
            ("Sugiere que el narrador olvidó la historia que le contó su abuela", "La acaba de contar en el relato; no la olvidó."),
            ("Indica que el hijo del vendedor no merece la misma lealtad", "El narrador le compra igual, sin poner en duda al hijo."),
            ("Revela que el narrador se arrepiente de seguir yendo a la feria", "No hay arrepentimiento en el texto: hay una costumbre que no sabe explicar."),
        ],
    ),
    # ---------- "Puerto en invierno" ----------
    _ql(
        "poema_puerto", "lec_localizar", "facil",
        "Según el poema, ¿en qué trabajó el padre del hablante durante treinta "
        "años?",
        "En la grúa del puerto",
        "El segundo grupo de versos lo dice sin rodeos: «Mi padre trabajó "
        "treinta años en la grúa, / bajando cajas que venían de países».\n\n"
        "Aunque se trate de un poema, hay datos que están enunciados de forma "
        "directa y la pregunta solo pide ubicarlos.",
        [
            ("En los barcos que llegaban al puerto", "El padre descargaba lo que traían los barcos desde la grúa; el poema no lo embarca en ellos."),
            ("En la construcción del muelle", "El muelle aparece únicamente para decir que hoy tiene otro dueño."),
            ("En una empresa de países extranjeros", "Los países extranjeros son el origen de las cajas, no el empleador del padre."),
        ],
    ),
    _ql(
        "poema_puerto", "lec_interpretar", "medio",
        "¿Qué sugieren los versos «bajando cajas que venían de países / cuyos "
        "nombres nunca supo pronunciar / y a los que jamás fue»?",
        "Que el trabajo lo conectaba con un mundo al que él no tenía acceso",
        "El padre manipulaba todos los días mercancía llegada de lugares que "
        "no podía nombrar ni visitar. El poema pone juntas la cercanía "
        "material y la distancia real.\n\n"
        "Interpretar un verso es reconstruir esa tensión: no dice «era pobre» "
        "ni «el comercio es desigual», lo muestra con las cajas y los nombres "
        "impronunciables.",
        [
            ("Que el padre no tenía interés en aprender otros idiomas", "El poema no atribuye desinterés: describe una distancia, no una elección."),
            ("Que las cajas llegaban con las etiquetas mal escritas", "Nada en el poema habla de etiquetas ni de errores de escritura."),
            ("Que el padre viajó a esos países después de jubilarse", "El verso dice exactamente lo contrario: «a los que jamás fue»."),
        ],
    ),
    _ql(
        "poema_puerto", "lec_interpretar", "dificil",
        "«Decía que el puerto es una puerta / que se abre siempre hacia el "
        "otro lado». ¿Qué expresa esta imagen?",
        "Que el puerto beneficia a quienes están fuera y no a quienes trabajan "
        "en él",
        "Una puerta que se abre siempre hacia el otro lado deja pasar en una "
        "sola dirección. Aplicada al puerto, dice que la riqueza que circula "
        "por ahí va hacia afuera, mientras el que la mueve se queda.\n\n"
        "El resto del poema sostiene esa lectura: el padre baja cajas de "
        "países a los que nunca fue, y hoy la grúa y el muelle tienen otros "
        "apellidos y otros dueños.",
        [
            ("Que el puerto permite a los trabajadores conocer otros países", "El poema insiste en que el padre nunca fue a ninguno de esos lugares."),
            ("Que las puertas del puerto se cierran durante el invierno", "El invierno da el ambiente del poema, pero la puerta acá es una imagen, no una puerta real."),
            ("Que cualquiera puede entrar a trabajar al puerto", "El poema no trata sobre el acceso al empleo, sino sobre hacia dónde va lo que pasa por ahí."),
        ],
    ),
    _ql(
        "poema_puerto", "lec_evaluar", "medio",
        "¿Qué efecto produce el contraste entre los dueños que cambian y el "
        "mar que «sigue golpeando las mismas piedras»?",
        "Opone la permanencia de lo natural a lo transitorio de la propiedad",
        "Los versos finales enumeran lo que cambió —el apellido de la grúa, el "
        "dueño del muelle— y frente a eso ponen un mar que «no firma "
        "contratos» y sigue igual.\n\n"
        "El contraste ordena todo el cierre: lo que parecía sólido resulta "
        "provisorio, y lo que nadie administra es lo que permanece.",
        [
            ("Anuncia que el puerto será abandonado en el futuro", "El poema no proyecta un cierre del puerto; contrapone lo que cambia con lo que permanece."),
            ("Explica por qué el padre dejó de trabajar en la grúa", "El poema nunca cuenta cómo terminó ese trabajo."),
            ("Sugiere que el mar dañará las instalaciones del muelle", "El golpe del mar aparece como constancia, no como amenaza."),
        ],
    ),
    _ql(
        "poema_puerto", "lec_evaluar", "dificil",
        "Los versos iniciales dicen que los barcos «aprendieron a esperar / "
        "mejor que los hombres». ¿Qué función cumple esta apertura?",
        "Instala la espera como tema y anticipa la comparación entre lo humano "
        "y lo que perdura",
        "El poema empieza atribuyendo a los barcos una virtud humana —saber "
        "esperar— y midiendo con ella a las personas. Esa comparación regresa "
        "al final con el mar y «la paciencia de lo que no se va».\n\n"
        "Evaluar la apertura de un texto es preguntarse qué prepara. Estos "
        "versos preparan el contraste que el poema desarrolla después: lo que "
        "aguanta y lo que pasa.",
        [
            ("Describe el retraso habitual de los barcos en el puerto", "Los barcos que esperan no ilustran un problema logístico: sirven para hablar de la espera humana."),
            ("Critica la impaciencia del padre en su trabajo diario", "El poema no reprocha nada al padre; lo presenta con respeto."),
            ("Explica el funcionamiento del puerto durante el invierno", "La apertura no informa sobre el funcionamiento del puerto."),
        ],
    ),
    # ---------- "Tiempo de lectura por placer, según edad" ----------
    _ql(
        "tabla_lectura", "lec_localizar", "facil",
        "Según la tabla, ¿cuántos minutos diarios dedican en promedio a leer "
        "en papel los estudiantes de 14 años?",
        "9 minutos",
        "La fila de 14 años entrega tres cifras: 9 minutos en papel, 19 en "
        "pantalla y 28 en total. La pregunta pide la primera.\n\n"
        "En un texto discontinuo, localizar es cruzar bien la fila con la "
        "columna. El error más común es leer el total o la columna vecina.",
        [
            ("19 minutos", "Ese es el tiempo en pantalla de esa edad, no en papel."),
            ("28 minutos", "Ese es el total de la fila, que suma papel y pantalla."),
            ("17 minutos", "Corresponde al papel de los 12 años, una fila más arriba."),
        ],
    ),
    _ql(
        "tabla_lectura", "lec_localizar", "medio",
        "De acuerdo con la nota metodológica, ¿qué tipo de lectura queda fuera "
        "de la medición?",
        "La lectura exigida por el colegio y la mensajería instantánea",
        "La nota fija dos exclusiones: «se contabiliza solo la lectura "
        "voluntaria; queda fuera la lectura exigida por el colegio», y "
        "«Textos en pantalla» «excluye mensajería instantánea».\n\n"
        "En los textos discontinuos, la nota al pie no es un adorno: define "
        "qué significan realmente los números de la tabla.",
        [
            ("Solo la lectura exigida por el colegio", "Es una de las dos exclusiones; la nota también deja fuera la mensajería instantánea."),
            ("Solo los mensajes instantáneos entre estudiantes", "También queda fuera la lectura obligatoria del colegio, según la misma nota."),
            ("Los artículos y foros leídos en pantalla", "La nota los incluye expresamente dentro de «Textos en pantalla»."),
        ],
    ),
    _ql(
        "tabla_lectura", "lec_interpretar", "medio",
        "¿Qué tendencia muestran los datos entre los 10 y los 18 años?",
        "La lectura en papel cae de forma sostenida en todas las edades",
        "La columna de papel va de 21 minutos a los 10 años hasta 5 a los 18, "
        "bajando en cada fila sin excepción. Es la única columna que se mueve "
        "en una sola dirección.\n\n"
        "Interpretar una tabla es leer columnas completas y no casos sueltos: "
        "la pantalla sube y después baja, y el total se mantiene un tramo "
        "antes de caer.",
        [
            ("La lectura en pantalla aumenta de forma sostenida hasta los 18 años", "Sube hasta los 14 años y luego baja a 17 y a 12 minutos."),
            ("El tiempo total de lectura se mantiene estable en todas las edades", "Se mantiene cerca de 27 y 28 minutos hasta los 12 años, pero después baja hasta 17."),
            ("La lectura en papel supera a la de pantalla en todas las edades", "Deja de superarla a partir de los 14 años, donde el papel marca 9 y la pantalla 19."),
        ],
    ),
    _ql(
        "tabla_lectura", "lec_interpretar", "dificil",
        "¿A qué edad la lectura en pantalla supera por primera vez a la "
        "lectura en papel?",
        "A los 14 años",
        "A los 12 años el papel todavía gana por poco: 17 contra 11. En la "
        "fila siguiente la relación se da vuelta: 9 en papel contra 19 en "
        "pantalla.\n\n"
        "La pregunta exige comparar dos columnas fila por fila hasta encontrar "
        "el punto de cruce, no leer un solo valor.",
        [
            ("A los 12 años", "Ahí el papel todavía va adelante, 17 contra 11 minutos."),
            ("A los 16 años", "La pantalla ya iba adelante desde dos filas antes."),
            ("A los 10 años", "Es la edad con mayor diferencia a favor del papel: 21 contra 6."),
        ],
    ),
    _ql(
        "tabla_lectura", "lec_evaluar", "dificil",
        "Alguien afirma, citando esta tabla, que «los jóvenes de 18 años leen "
        "menos que nunca». ¿Qué objeción cabe hacerle a esa conclusión?",
        "La tabla mide solo lectura voluntaria, de modo que no registra todo "
        "lo que leen",
        "La nota metodológica excluye la lectura exigida por el colegio, que a "
        "los 18 años es considerable. Con esa exclusión, los 17 minutos "
        "diarios no representan todo lo que esos estudiantes leen.\n\n"
        "Evaluar un dato es revisar qué mide antes de aceptar lo que parece "
        "decir. Acá la caída del total es real, pero la conclusión va más "
        "lejos que la evidencia disponible.",
        [
            ("La tabla no incluye a los estudiantes mayores de 18 años", "El reclamo se refiere a los de 18 años, que sí están en la tabla."),
            ("Los datos de pantalla y papel no pueden sumarse entre sí", "La tabla los suma en su columna de total y nada indica que sea incorrecto."),
            ("La tabla muestra que a los 18 años se lee más que a los 16", "Muestra lo contrario: el total baja de 23 a 17 minutos."),
        ],
    ),
    # ---------- "Qué hacer cuando tiembla" ----------
    _ql(
        "instructivo_sismo", "lec_localizar", "facil",
        "Según el texto, ¿qué hay que hacer durante el movimiento sísmico?",
        "Agacharse, cubrirse la cabeza bajo una mesa firme y afirmarse de ella",
        "El primer párrafo entrega la instrucción completa: «agacharse, "
        "cubrirse y afirmarse», y luego explica cada paso, incluido afirmarse "
        "de la mesa «para desplazarse con ella si se mueve».\n\n"
        "Es información explícita y ordenada; la pregunta solo pide "
        "recuperarla sin agregar nada.",
        [
            ("Salir del edificio lo más rápido posible", "El texto lo desaconseja de forma expresa: «No corra hacia la salida mientras tiembla»."),
            ("Ubicarse bajo el marco de una puerta", "El texto descarta esa creencia: en las construcciones actuales ese marco no es más resistente."),
            ("Bajar por el ascensor hasta la planta baja", "El texto prohíbe usar el ascensor durante el sismo."),
        ],
    ),
    _ql(
        "instructivo_sismo", "lec_localizar", "medio",
        "De acuerdo con el texto, ¿qué causa la mayoría de las lesiones "
        "durante un terremoto?",
        "Los objetos que caen y los vidrios que se quiebran",
        "El segundo párrafo lo afirma con precisión: la mayoría de las "
        "lesiones «no las causa el derrumbe del edificio sino los objetos que "
        "caen y los vidrios que se quiebran».\n\n"
        "El dato importa porque sostiene la instrucción anterior: esos objetos "
        "están «justo en el camino de quien corre».",
        [
            ("El derrumbe de los edificios mal construidos", "El texto lo menciona justamente para descartarlo como causa principal."),
            ("Las caídas al intentar bajar por las escaleras", "El texto habla de correr hacia la salida, pero no atribuye las lesiones a las escaleras."),
            ("Los incendios provocados por escapes de gas", "El gas aparece como precaución posterior al sismo, no como causa de lesiones durante el movimiento."),
        ],
    ),
    _ql(
        "instructivo_sismo", "lec_interpretar", "medio",
        "¿Por qué el texto indica evacuar sin esperar ninguna alarma cuando el "
        "sismo fue muy fuerte o muy largo?",
        "Porque la intensidad y la duración del sismo funcionan como la alarma "
        "misma",
        "El texto lo dice con una frase breve después de describir el caso: "
        "«esa es la alarma». Si costó mantenerse en pie o el movimiento duró "
        "más de un minuto, esa experiencia ya es la señal de evacuar.\n\n"
        "Interpretar acá es entender por qué el texto no manda esperar un "
        "aviso externo: la señal está en lo que la persona acaba de sentir.",
        [
            ("Porque las alarmas de tsunami suelen estar descompuestas", "El texto no cuestiona el estado de las alarmas."),
            ("Porque la autoridad solo avisa cuando el mar ya subió", "El texto no describe así el trabajo de la autoridad; de hecho pide esperar su indicación para volver."),
            ("Porque las zonas altas se llenan si se espera demasiado", "La razón que da el texto es la señal del propio sismo, no la congestión."),
        ],
    ),
    _ql(
        "instructivo_sismo", "lec_evaluar", "medio",
        "¿Qué justifica que el texto advierta no volver «aunque el mar se vea "
        "tranquilo»?",
        "Que la primera ola no suele ser la mayor, de modo que la calma puede "
        "engañar",
        "El texto entrega la razón en la misma frase: «porque la primera ola "
        "no suele ser la mayor». La calma aparente entre olas es precisamente "
        "el momento de riesgo.\n\n"
        "Evaluar un instructivo incluye reconocer contra qué error está "
        "escrita cada advertencia. Esta apunta a la tentación de volver cuando "
        "todo parece haber pasado.",
        [
            ("Que el mar demora varias horas en recuperar su nivel normal", "El texto no habla del nivel del mar ni de cuánto demora en normalizarse."),
            ("Que la autoridad necesita tiempo para revisar las viviendas", "El texto pide esperar la indicación de la autoridad, pero la razón que da es el comportamiento de las olas."),
            ("Que puede haber réplicas más fuertes que el sismo principal", "Las réplicas no se mencionan en el texto; la advertencia se refiere a las olas."),
        ],
    ),
    _ql(
        "instructivo_sismo", "lec_evaluar", "dificil",
        "¿Qué distingue a este texto de una simple lista de instrucciones?",
        "Que explica la razón de cada indicación en lugar de solo enunciarla",
        "Cada instrucción viene con su motivo: no correr, porque las lesiones "
        "las causan los objetos que caen; no usar el marco de la puerta, "
        "porque en las construcciones actuales no es más resistente; no "
        "volver, porque la primera ola no suele ser la mayor.\n\n"
        "Esa elección de escritura importa: una indicación con razón se "
        "recuerda mejor y permite decidir en situaciones que la lista no "
        "previó.",
        [
            ("Que ordena las instrucciones según su grado de urgencia", "El orden del texto es temporal —durante y después del sismo—, no por urgencia."),
            ("Que se dirige exclusivamente a quienes viven en la costa", "La evacuación por tsunami es solo una parte; el resto vale para cualquier lugar."),
            ("Que evita dar instrucciones directas al lector", "Las da y en modo imperativo: «No corra», «revise», «evacúe»."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Ciencias
#
# La prueba son 80 preguntas (54 del módulo común y 26 del electivo) en 2 horas
# 40 minutos, y 75 puntúan. El temario la organiza en tres ejes por disciplina:
# Biología, Física y Química.
#
# El banco parte por Física y Química a propósito. Sus preguntas son
# cuantitativas, así que `scripts/verificar_banco.py` puede recalcular cada
# resultado igual que en matemática. Biología es contenido factual: una
# afirmación errada no la detecta ningún script, y este proyecto no publica
# contenido que no pueda verificar. Sus nodos quedan creados y el configurador
# muestra 0 preguntas disponibles, que es la verdad.
# ---------------------------------------------------------------------------

SKILL_NODES_CIENCIAS = [
    # Física
    ("cie_movimiento", "Movimiento rectilíneo", "fisica", 1, []),
    ("cie_fuerzas", "Fuerzas y leyes de Newton", "fisica", 2, ["cie_movimiento"]),
    ("cie_energia", "Trabajo, energía y potencia", "fisica", 3, ["cie_fuerzas"]),
    ("cie_ondas", "Ondas y sonido", "fisica", 2, []),
    ("cie_electricidad", "Circuitos eléctricos", "fisica", 3, []),
    # Química
    ("cie_atomo", "Estructura atómica", "quimica", 1, []),
    ("cie_estequiometria", "Cantidad de sustancia y estequiometría", "quimica", 2, ["cie_atomo"]),
    ("cie_soluciones", "Disoluciones y concentración", "quimica", 3, ["cie_estequiometria"]),
    ("cie_acidobase", "Ácido-base y pH", "quimica", 3, ["cie_soluciones"]),
    # Biología: estructura creada, banco pendiente (ver nota de arriba).
    ("cie_celula", "Célula y transporte de membrana", "biologia", 1, []),
    ("cie_genetica", "Genética y herencia", "biologia", 2, ["cie_celula"]),
    ("cie_ecosistemas", "Ecosistemas y flujo de energía", "biologia", 2, []),
]

QUESTIONS_CIENCIAS = [
    # ---------- FÍSICA: movimiento ----------
    _q(
        "cie_movimiento", "facil",
        "Un ciclista recorre 120 m en 15 s con velocidad constante. "
        "¿Cuál es su rapidez?",
        "8 m/s",
        "La rapidez constante es la distancia recorrida dividida por el tiempo "
        "empleado.\n\n"
        "1) Escribe la relación: v = d / t.\n"
        "2) Reemplaza: v = 120 m ÷ 15 s.\n"
        "3) Calcula: v = 8 m/s.\n\n"
        "Comprobación: si recorre 8 metros cada segundo, en 15 segundos avanza "
        "8 · 15 = 120 m.",
        [
            ("1800 m/s", "Multiplicó la distancia por el tiempo en vez de dividir."),
            ("0,125 m/s", "Dividió el tiempo por la distancia, invirtiendo la fórmula."),
            ("135 m/s", "Sumó distancia y tiempo, que son magnitudes distintas y no se pueden sumar."),
        ],
    ),
    _q(
        "cie_movimiento", "medio",
        "Un auto parte del reposo y acelera uniformemente a 2 m/s² durante 6 s. "
        "¿Qué distancia recorre en ese tiempo?",
        "36 m",
        "Con aceleración constante y partiendo del reposo, la distancia crece "
        "con el cuadrado del tiempo.\n\n"
        "1) La relación es d = ½ · a · t², válida porque la velocidad inicial "
        "es cero.\n"
        "2) Reemplaza: d = ½ · 2 m/s² · (6 s)².\n"
        "3) Calcula el cuadrado: 6² = 36.\n"
        "4) Resuelve: d = ½ · 2 · 36 = 36 m.",
        [
            ("72 m", "Olvidó el factor ½ de la fórmula y calculó a · t²."),
            ("12 m", "Usó d = a · t, que corresponde a la velocidad final, no a la distancia."),
            ("18 m", "Usó el tiempo sin elevarlo al cuadrado."),
        ],
    ),
    _q(
        "cie_fuerzas", "medio",
        "Sobre un cuerpo de 4 kg actúa una fuerza neta de 20 N. "
        "¿Cuál es su aceleración?",
        "5 m/s²",
        "La segunda ley de Newton relaciona la fuerza neta con la masa y la "
        "aceleración.\n\n"
        "1) La ley es F = m · a.\n"
        "2) Despeja la aceleración: a = F / m.\n"
        "3) Reemplaza: a = 20 N ÷ 4 kg = 5 m/s².\n\n"
        "Las unidades cuadran: un newton es un kg·m/s², así que N/kg da m/s².",
        [
            ("80 m/s²", "Multiplicó fuerza por masa en lugar de dividir."),
            ("0,2 m/s²", "Dividió la masa por la fuerza, invirtiendo la relación."),
            ("24 m/s²", "Sumó fuerza y masa, que son magnitudes distintas."),
        ],
    ),
    _q(
        "cie_energia", "medio",
        "Una grúa eleva una caja de 50 kg a 4 m de altura. "
        "¿Cuánto trabajo realiza contra la gravedad? (usa g = 10 m/s²)",
        "2000 J",
        "El trabajo contra la gravedad es igual a la energía potencial que gana "
        "el cuerpo.\n\n"
        "1) La relación es W = m · g · h.\n"
        "2) Reemplaza: W = 50 kg · 10 m/s² · 4 m.\n"
        "3) Calcula: 50 · 10 = 500, y 500 · 4 = 2000 J.\n\n"
        "El joule es un newton por metro: la grúa aplica 500 N durante 4 m.",
        [
            ("200 J", "Omitió la aceleración de gravedad y calculó solo m · h."),
            ("500 J", "Calculó el peso del cuerpo (m · g) sin multiplicar por la altura."),
            ("125 J", "Dividió por la altura en vez de multiplicar."),
        ],
    ),
    _q(
        "cie_ondas", "medio",
        "Una onda tiene una frecuencia de 50 Hz y una longitud de onda de 4 m. "
        "¿Cuál es su rapidez de propagación?",
        "200 m/s",
        "La rapidez de una onda es el producto de su frecuencia por su longitud "
        "de onda.\n\n"
        "1) La relación es v = f · λ.\n"
        "2) Reemplaza: v = 50 Hz · 4 m.\n"
        "3) Calcula: v = 200 m/s.\n\n"
        "Tiene sentido dimensional: el hertz es 1/s, así que (1/s) · m da m/s.",
        [
            ("12,5 m/s", "Dividió la frecuencia por la longitud de onda en lugar de multiplicar."),
            ("54 m/s", "Sumó ambas magnitudes, que no son del mismo tipo."),
            ("0,08 m/s", "Dividió la longitud de onda por la frecuencia."),
        ],
    ),
    _q(
        "cie_electricidad", "medio",
        "Por una resistencia de 20 Ω circula una corriente de 3 A. "
        "¿Cuál es la diferencia de potencial entre sus extremos?",
        "60 V",
        "La ley de Ohm relaciona voltaje, corriente y resistencia.\n\n"
        "1) La ley es V = I · R.\n"
        "2) Reemplaza: V = 3 A · 20 Ω.\n"
        "3) Calcula: V = 60 V.",
        [
            ("6,7 V", "Dividió la resistencia por la corriente en vez de multiplicar."),
            ("23 V", "Sumó corriente y resistencia, que son magnitudes distintas."),
            ("0,15 V", "Dividió la corriente por la resistencia."),
        ],
    ),
    _q(
        "cie_electricidad", "dificil",
        "Dos resistencias de 6 Ω y 3 Ω se conectan en paralelo. "
        "¿Cuál es la resistencia equivalente?",
        "2 Ω",
        "En paralelo se suman los inversos de las resistencias, y el resultado "
        "es siempre menor que la más pequeña.\n\n"
        "1) Plantea: 1/Req = 1/6 + 1/3.\n"
        "2) Lleva a denominador común: 1/6 + 2/6 = 3/6 = 1/2.\n"
        "3) Invierte: Req = 2 Ω.\n\n"
        "Control: 2 Ω es menor que 3 Ω, la más chica del par, como debe ser en "
        "un circuito paralelo.",
        [
            ("9 Ω", "Sumó las resistencias directamente, que es la regla de la conexión en serie."),
            ("4,5 Ω", "Promedió ambas resistencias, que no es la regla del paralelo."),
            ("18 Ω", "Multiplicó las resistencias sin dividir por su suma."),
        ],
    ),

    # ---------- QUÍMICA ----------
    _q(
        "cie_atomo", "facil",
        "Un átomo neutro tiene número atómico 17 y número másico 35. "
        "¿Cuántos neutrones tiene su núcleo?",
        "18",
        "El número másico cuenta protones y neutrones juntos; el número atómico "
        "cuenta solo los protones.\n\n"
        "1) Los protones son 17, porque ese es el número atómico.\n"
        "2) Los neutrones son la diferencia: 35 − 17 = 18.\n\n"
        "Al ser neutro también tiene 17 electrones, pero esos no están en el "
        "núcleo ni cuentan para el número másico.",
        [
            ("17", "Entregó la cantidad de protones, que es el número atómico."),
            ("35", "Entregó el número másico, que suma protones y neutrones."),
            ("52", "Sumó ambos números en lugar de restarlos."),
        ],
    ),
    _q(
        "cie_estequiometria", "medio",
        "¿Cuántos moles hay en 88 g de dióxido de carbono (CO₂), si su masa "
        "molar es 44 g/mol?",
        "2 mol",
        "Los moles son la masa dividida por la masa molar.\n\n"
        "1) La relación es n = m / M.\n"
        "2) Reemplaza: n = 88 g ÷ 44 g/mol.\n"
        "3) Calcula: n = 2 mol.\n\n"
        "Control: si un mol pesa 44 g, en 88 g caben exactamente dos.",
        [
            ("3872 mol", "Multiplicó la masa por la masa molar en vez de dividir."),
            ("0,5 mol", "Dividió la masa molar por la masa, invirtiendo la relación."),
            ("44 mol", "Entregó la masa molar como si fuera la cantidad de sustancia."),
        ],
    ),
    _q(
        "cie_soluciones", "medio",
        "Se disuelven 0,5 mol de soluto en agua hasta completar 250 mL de "
        "disolución. ¿Cuál es su concentración molar?",
        "2 mol/L",
        "La molaridad es la cantidad de soluto en moles por litro de "
        "disolución, así que primero hay que pasar el volumen a litros.\n\n"
        "1) Convierte: 250 mL = 0,25 L.\n"
        "2) La relación es M = n / V.\n"
        "3) Reemplaza: M = 0,5 mol ÷ 0,25 L = 2 mol/L.\n\n"
        "El error más común acá es dividir por 250 sin convertir, que da un "
        "número mil veces menor.",
        [
            ("0,002 mol/L", "Dividió por 250 sin convertir los mililitros a litros."),
            ("0,125 mol/L", "Multiplicó los moles por el volumen en lugar de dividir."),
            ("125 mol/L", "Multiplicó por 250 en vez de dividir por 0,25."),
        ],
    ),
    _q(
        "cie_acidobase", "medio",
        "Una disolución tiene una concentración de iones hidrógeno de "
        "1 × 10⁻³ mol/L. ¿Cuál es su pH?",
        "3",
        "El pH es el logaritmo negativo en base 10 de la concentración de iones "
        "hidrógeno.\n\n"
        "1) La relación es pH = −log[H⁺].\n"
        "2) Reemplaza: pH = −log(1 × 10⁻³).\n"
        "3) El logaritmo de 10⁻³ es −3, y su negativo es 3.\n\n"
        "Un pH de 3 corresponde a una disolución ácida, coherente con una "
        "concentración de hidrógeno alta.",
        [
            ("−3", "Olvidó el signo negativo de la definición: el pH de una disolución acuosa común no es negativo."),
            ("11", "Calculó el pOH, que es 14 menos el pH."),
            ("0,001", "Entregó la concentración misma en lugar de su logaritmo."),
        ],
    ),
    _q(
        "cie_acidobase", "dificil",
        "Si el pH de una disolución es 5, ¿cuál es su pOH a 25 °C?",
        "9",
        "A 25 °C, el pH y el pOH de una disolución acuosa siempre suman 14.\n\n"
        "1) La relación es pH + pOH = 14.\n"
        "2) Despeja: pOH = 14 − 5.\n"
        "3) Calcula: pOH = 9.\n\n"
        "La suma constante viene del producto iónico del agua a esa "
        "temperatura, por eso la condición de 25 °C aparece en el enunciado.",
        [
            ("5", "Repitió el pH: ambos coinciden solo cuando valen 7, es decir, en una disolución neutra."),
            ("19", "Sumó el pH a 14 en vez de restarlo."),
            ("7", "Entregó el valor del pH neutro, que no depende del dato del enunciado."),
        ],
    ),
    _q(
        "cie_estequiometria", "dificil",
        "En la reacción 2 H₂ + O₂ → 2 H₂O, ¿cuántos moles de agua se producen a "
        "partir de 6 mol de hidrógeno, con oxígeno en exceso?",
        "6 mol",
        "Los coeficientes de la ecuación balanceada dan la proporción entre las "
        "sustancias.\n\n"
        "1) La ecuación dice que 2 mol de H₂ producen 2 mol de H₂O: la "
        "proporción es 1 a 1.\n"
        "2) Con 6 mol de hidrógeno se producen 6 mol de agua.\n\n"
        "El oxígeno está en exceso, así que el hidrógeno es el reactivo "
        "limitante y es él quien fija cuánto producto se forma.",
        [
            ("3 mol", "Dividió por el coeficiente 2 sin notar que también el agua lo lleva: la proporción es 1 a 1."),
            ("12 mol", "Multiplicó por 2 en lugar de aplicar la proporción de la ecuación."),
            ("2 mol", "Usó el coeficiente de la ecuación como si fuera la respuesta."),
        ],
    ),
    # ---------- FÍSICA: movimiento ----------
    _q(
        "cie_movimiento", "facil",
        "Un tren viaja a 90 km/h. ¿Cuál es su rapidez en metros por segundo?",
        "25 m/s",
        "Para pasar de km/h a m/s se divide por 3,6, porque un kilómetro son "
        "1.000 metros y una hora son 3.600 segundos: $\\frac{1000}{3600} = "
        "\\frac{1}{3,6}$.\n\n"
        "Entonces $90 \\div 3,6 = 25$ m/s.\n\n"
        "Conviene tener a mano la conversión inversa: para pasar de m/s a km/h "
        "se multiplica por 3,6.",
        [
            ("32,4 m/s", "Multiplicó por 3,6 en vez de dividir: esa es la conversión al revés, de m/s a km/h."),
            ("90 m/s", "Dejó el número igual, como si las unidades no importaran."),
            ("1,5 m/s", "Dividió por 60 una sola vez, convirtiendo horas a minutos pero no a segundos."),
        ],
    ),
    _q(
        "cie_movimiento", "medio",
        "Un objeto se deja caer desde el reposo. Si se desprecia el roce del "
        "aire, ¿qué rapidez tiene a los 3 segundos? (Usa $g = 10$ m/s².)",
        "30 m/s",
        "En caída libre la rapidez crece según $v = g \\cdot t$, porque la "
        "velocidad inicial es cero.\n\n"
        "Reemplazando: $v = 10 \\cdot 3 = 30$ m/s.\n\n"
        "Ojo con no confundir esta fórmula con la de la distancia recorrida, "
        "que lleva el tiempo al cuadrado y un medio: $h = \\frac{1}{2} g t^2$.",
        [
            ("45 m/s", "Usó la fórmula de la distancia ($\\frac{1}{2}gt^2 = 45$) y entregó ese número como si fuera rapidez. Es una distancia en metros, no una velocidad."),
            ("10 m/s", "Entregó la aceleración de gravedad sin multiplicarla por el tiempo."),
            ("90 m/s", "Multiplicó $g$ por $t^2$ sin el factor un medio, y además eso da distancia."),
        ],
    ),
    _q(
        "cie_movimiento", "medio",
        "Un automóvil aumenta su rapidez de 5 m/s a 25 m/s en 4 segundos. "
        "¿Cuál es su aceleración media?",
        "5 m/s²",
        "La aceleración media es el cambio de velocidad dividido por el tiempo "
        "que tomó: $a = \\frac{v_f - v_i}{t}$.\n\n"
        "Reemplazando: $a = \\frac{25 - 5}{4} = \\frac{20}{4} = 5$ m/s².\n\n"
        "Lo que importa es la DIFERENCIA de velocidades, no la velocidad final: "
        "un auto que ya venía moviéndose no partió de cero.",
        [
            ("6,25 m/s²", "Dividió la velocidad final por el tiempo, olvidando que el auto ya llevaba 5 m/s."),
            ("20 m/s²", "Calculó el cambio de velocidad pero no lo dividió por el tiempo."),
            ("7,5 m/s²", "Sumó las dos velocidades y dividió por el tiempo, en vez de restarlas."),
        ],
    ),
    _q(
        "cie_movimiento", "facil",
        "Un camión mantiene una rapidez constante de 25 m/s durante 8 segundos. "
        "¿Qué distancia recorre?",
        "200 m",
        "Con rapidez constante la distancia es simplemente $d = v \\cdot t$, "
        "sin ningún término de aceleración.\n\n"
        "Reemplazando: $d = 25 \\cdot 8 = 200$ m.\n\n"
        "La palabra clave del enunciado es «constante»: si hubiera aceleración, "
        "habría que usar otra fórmula.",
        [
            ("100 m", "Aplicó el factor un medio de la fórmula con aceleración, que acá no corresponde porque la rapidez es constante."),
            ("3,1 m", "Dividió la rapidez por el tiempo en vez de multiplicar."),
            ("33 m", "Sumó los dos valores en lugar de multiplicarlos."),
        ],
    ),
    _q(
        "cie_movimiento", "dificil",
        "Un auto que va a 20 m/s frena uniformemente hasta detenerse en 5 "
        "segundos. ¿Cuál es su aceleración?",
        "−4 m/s²",
        "La aceleración sigue siendo $a = \\frac{v_f - v_i}{t}$, y acá la "
        "velocidad final es cero porque el auto se detiene.\n\n"
        "$a = \\frac{0 - 20}{5} = \\frac{-20}{5} = -4$ m/s².\n\n"
        "El signo negativo no es un detalle: indica que la aceleración apunta en "
        "sentido contrario al movimiento, que es lo que significa frenar.",
        [
            ("4 m/s²", "El valor está bien pero le falta el signo: una aceleración positiva describiría un auto que acelera, no uno que frena."),
            ("−100 m/s²", "Multiplicó la velocidad por el tiempo en vez de dividir."),
            ("−0,25 m/s²", "Dividió el tiempo por la velocidad, invirtiendo la fórmula."),
        ],
    ),
    # ---------- FÍSICA: fuerzas ----------
    _q(
        "cie_fuerzas", "facil",
        "¿Cuál es el peso de un cuerpo de 8 kg en la superficie terrestre? "
        "(Usa $g = 10$ m/s².)",
        "80 N",
        "El peso es la fuerza con que la Tierra atrae al cuerpo, y se calcula "
        "como $P = m \\cdot g$.\n\n"
        "Reemplazando: $P = 8 \\cdot 10 = 80$ N.\n\n"
        "Masa y peso no son lo mismo: la masa se mide en kilogramos y no cambia "
        "de lugar; el peso es una fuerza, se mide en newtons y depende de dónde "
        "esté el cuerpo.",
        [
            ("8 N", "Entregó la masa con unidad de fuerza, sin multiplicar por la gravedad."),
            ("0,8 N", "Dividió la masa por la gravedad en vez de multiplicar."),
            ("18 N", "Sumó la masa y la gravedad en lugar de multiplicarlas."),
        ],
    ),
    _q(
        "cie_fuerzas", "medio",
        "Sobre un cuerpo de 6 kg actúan dos fuerzas horizontales opuestas: una "
        "de 30 N hacia la derecha y otra de 12 N hacia la izquierda. ¿Cuál es "
        "su aceleración?",
        "3 m/s²",
        "Primero se calcula la fuerza NETA, que es la suma considerando el "
        "sentido: $30 - 12 = 18$ N hacia la derecha.\n\n"
        "Después se aplica la segunda ley de Newton, $F = m \\cdot a$, "
        "despejando: $a = \\frac{18}{6} = 3$ m/s².\n\n"
        "El orden importa: la segunda ley se aplica a la fuerza neta, no a cada "
        "fuerza por separado.",
        [
            ("5 m/s²", "Usó solo la fuerza de 30 N e ignoró la que se le opone."),
            ("7 m/s²", "Sumó las dos fuerzas en vez de restarlas, como si apuntaran en el mismo sentido."),
            ("2 m/s²", "Usó solo la fuerza de 12 N."),
        ],
    ),
    _q(
        "cie_fuerzas", "dificil",
        "Una caja de 5 kg es empujada con una fuerza de 40 N sobre una "
        "superficie que ejerce 10 N de roce. ¿Cuál es su aceleración?",
        "6 m/s²",
        "El roce siempre se opone al movimiento, así que la fuerza neta es "
        "$40 - 10 = 30$ N.\n\n"
        "Con la segunda ley: $a = \\frac{30}{5} = 6$ m/s².\n\n"
        "Un error frecuente es sumar el roce: es una fuerza que frena, nunca una "
        "que empuja.",
        [
            ("8 m/s²", "Ignoró el roce y usó los 40 N completos."),
            ("10 m/s²", "Sumó el roce a la fuerza aplicada, cuando el roce se opone al movimiento."),
            ("2 m/s²", "Usó solo la fuerza de roce."),
        ],
    ),
    _q(
        "cie_fuerzas", "dificil",
        "Sobre un objeto actúan dos fuerzas perpendiculares entre sí: una de 3 N "
        "y otra de 4 N. ¿Cuál es la magnitud de la fuerza neta?",
        "5 N",
        "Las fuerzas son vectores: cuando forman ángulo recto no se suman "
        "directamente, se combinan con el teorema de Pitágoras.\n\n"
        "$F = \\sqrt{3^2 + 4^2} = \\sqrt{9 + 16} = \\sqrt{25} = 5$ N.\n\n"
        "Solo se pueden sumar como números cuando las fuerzas apuntan en la "
        "misma dirección.",
        [
            ("7 N", "Sumó las magnitudes como si las fuerzas apuntaran en la misma dirección, ignorando que son perpendiculares."),
            ("1 N", "Restó las magnitudes, que sería el caso si apuntaran en sentidos opuestos."),
            ("12 N", "Multiplicó las dos fuerzas, operación que no corresponde a la suma de vectores."),
        ],
    ),
    _q(
        "cie_fuerzas", "medio",
        "Un libro descansa inmóvil sobre una mesa. Si su peso es de 15 N, ¿cuál "
        "es la magnitud de la fuerza normal que la mesa ejerce sobre él?",
        "15 N",
        "El libro está en reposo, así que la fuerza neta sobre él es cero: eso "
        "es lo que significa el equilibrio.\n\n"
        "Como el peso tira hacia abajo con 15 N, la mesa debe empujar hacia "
        "arriba con exactamente 15 N para que se cancelen.\n\n"
        "La normal no siempre vale lo mismo que el peso —cambia en un plano "
        "inclinado o si alguien presiona el libro—, pero acá el enunciado dice "
        "que está inmóvil sobre una superficie horizontal.",
        [
            ("30 N", "Duplicó el peso, como si la normal tuviera que superarlo para sostener el libro. Si así fuera, el libro saldría disparado hacia arriba."),
            ("0 N", "Supuso que no hay fuerza porque no hay movimiento; en realidad hay dos fuerzas que se anulan."),
            ("1,5 N", "Confundió el peso con la masa y aplicó la gravedad al revés."),
        ],
    ),
    # ---------- FÍSICA: energía ----------
    _q(
        "cie_energia", "facil",
        "¿Cuál es la energía potencial gravitatoria de un cuerpo de 2 kg "
        "ubicado a 5 m de altura? (Usa $g = 10$ m/s².)",
        "100 J",
        "La energía potencial gravitatoria es $E_p = m \\cdot g \\cdot h$.\n\n"
        "Reemplazando: $E_p = 2 \\cdot 10 \\cdot 5 = 100$ J.\n\n"
        "Se mide desde un nivel de referencia: la misma caja tiene distinta "
        "energía potencial según si se mide desde el suelo o desde una mesa.",
        [
            ("10 J", "Multiplicó solo la masa por la altura, olvidando la gravedad."),
            ("50 J", "Aplicó el factor un medio, que corresponde a la energía cinética y no a la potencial."),
            ("17 J", "Sumó los tres valores en vez de multiplicarlos."),
        ],
    ),
    _q(
        "cie_energia", "medio",
        "Un cuerpo de 4 kg se mueve a 3 m/s. ¿Cuál es su energía cinética?",
        "18 J",
        "La energía cinética es $E_c = \\frac{1}{2} m v^2$.\n\n"
        "Reemplazando: $E_c = \\frac{1}{2} \\cdot 4 \\cdot 3^2 = 2 \\cdot 9 "
        "= 18$ J.\n\n"
        "La velocidad va al cuadrado ANTES de multiplicar: por eso duplicar la "
        "rapidez cuadruplica la energía cinética, un dato que explica por qué "
        "los choques a alta velocidad son tan destructivos.",
        [
            ("36 J", "Olvidó el factor un medio de la fórmula."),
            ("6 J", "Multiplicó la masa por la velocidad sin elevarla al cuadrado ni aplicar el medio."),
            ("72 J", "Elevó al cuadrado el producto completo en vez de solo la velocidad."),
        ],
    ),
    _q(
        "cie_energia", "medio",
        "Una máquina realiza un trabajo de 600 J en 20 segundos. ¿Cuál es su "
        "potencia media?",
        "30 W",
        "La potencia es el trabajo dividido por el tiempo que tomó: "
        "$P = \\frac{W}{t}$.\n\n"
        "Reemplazando: $P = \\frac{600}{20} = 30$ W.\n\n"
        "Dos máquinas pueden hacer el mismo trabajo con potencias muy distintas: "
        "la más potente simplemente lo hace en menos tiempo.",
        [
            ("12.000 W", "Multiplicó el trabajo por el tiempo en lugar de dividir."),
            ("0,03 W", "Dividió el tiempo por el trabajo, invirtiendo la fórmula."),
            ("620 W", "Sumó ambos valores."),
        ],
    ),
    _q(
        "cie_energia", "dificil",
        "Un objeto se suelta desde 20 m de altura. Si se desprecia el roce, "
        "¿con qué rapidez llega al suelo? (Usa $g = 10$ m/s².)",
        "20 m/s",
        "Por conservación de la energía, toda la energía potencial del inicio se "
        "convierte en cinética al llegar abajo: $mgh = \\frac{1}{2}mv^2$.\n\n"
        "La masa se cancela a ambos lados, así que $v = \\sqrt{2gh}$. "
        "Reemplazando: $v = \\sqrt{2 \\cdot 10 \\cdot 20} = \\sqrt{400} = "
        "20$ m/s.\n\n"
        "Que la masa se cancele explica algo que parece raro: sin roce, dos "
        "cuerpos de distinta masa soltados desde la misma altura llegan al suelo "
        "con la misma rapidez.",
        [
            ("400 m/s", "Se quedó con el valor de $2gh$ sin sacarle la raíz cuadrada."),
            ("200 m/s", "Multiplicó la gravedad por la altura sin el factor 2 ni la raíz."),
            ("40 m/s", "Duplicó el resultado correcto, aplicando el 2 fuera de la raíz."),
        ],
    ),
    _q(
        "cie_energia", "facil",
        "Una fuerza de 25 N desplaza un cuerpo 8 m en la misma dirección de la "
        "fuerza. ¿Cuánto trabajo realiza?",
        "200 J",
        "Cuando la fuerza y el desplazamiento van en la misma dirección, el "
        "trabajo es $W = F \\cdot d$.\n\n"
        "Reemplazando: $W = 25 \\cdot 8 = 200$ J.\n\n"
        "Si la fuerza fuera perpendicular al movimiento, el trabajo sería cero: "
        "por eso cargar un bolso caminando en horizontal no realiza trabajo "
        "sobre él, por cansador que resulte.",
        [
            ("3,1 J", "Dividió la fuerza por la distancia en vez de multiplicar."),
            ("33 J", "Sumó ambos valores."),
            ("100 J", "Aplicó un factor un medio que no corresponde a la definición de trabajo."),
        ],
    ),
    # ---------- FÍSICA: ondas ----------
    _q(
        "cie_ondas", "facil",
        "Una onda tiene un periodo de 0,2 s. ¿Cuál es su frecuencia?",
        "5 Hz",
        "La frecuencia y el periodo son inversos: $f = \\frac{1}{T}$.\n\n"
        "Reemplazando: $f = \\frac{1}{0,2} = 5$ Hz.\n\n"
        "El periodo es cuánto demora UN ciclo; la frecuencia, cuántos ciclos "
        "ocurren en un segundo. Si cada ciclo dura una quinta parte de segundo, "
        "caben cinco en un segundo.",
        [
            ("0,2 Hz", "Entregó el periodo con unidad de frecuencia, sin invertirlo."),
            ("2 Hz", "Movió la coma sin hacer la división."),
            ("0,5 Hz", "Invirtió mal el decimal: $\\frac{1}{0,2}$ es 5, no 0,5."),
        ],
    ),
    _q(
        "cie_ondas", "medio",
        "El sonido viaja en el aire a unos 340 m/s. Si una onda sonora tiene una "
        "frecuencia de 170 Hz, ¿cuál es su longitud de onda?",
        "2 m",
        "La relación entre rapidez, frecuencia y longitud de onda es "
        "$v = \\lambda \\cdot f$. Despejando la longitud: $\\lambda = "
        "\\frac{v}{f}$.\n\n"
        "Reemplazando: $\\lambda = \\frac{340}{170} = 2$ m.\n\n"
        "En un mismo medio la rapidez es fija, así que a mayor frecuencia menor "
        "longitud de onda: los sonidos agudos tienen ondas más cortas.",
        [
            ("57.800 m", "Multiplicó la rapidez por la frecuencia en vez de dividir."),
            ("0,5 m", "Dividió la frecuencia por la rapidez, invirtiendo la fórmula."),
            ("510 m", "Sumó ambos valores."),
        ],
    ),
    _q(
        "cie_ondas", "medio",
        "Una onda avanza con una longitud de onda de 3 m y una frecuencia de 12 "
        "Hz. ¿Cuál es su rapidez de propagación?",
        "36 m/s",
        "Se usa directamente $v = \\lambda \\cdot f$.\n\n"
        "Reemplazando: $v = 3 \\cdot 12 = 36$ m/s.\n\n"
        "Esta rapidez depende del medio, no de quien genera la onda: si la misma "
        "onda pasa a otro medio, cambia la longitud pero la frecuencia se "
        "mantiene.",
        [
            ("4 m/s", "Dividió la frecuencia por la longitud en vez de multiplicar."),
            ("15 m/s", "Sumó ambos valores."),
            ("0,25 m/s", "Dividió la longitud por la frecuencia."),
        ],
    ),
    _q(
        "cie_ondas", "dificil",
        "Una onda de radio se propaga a $3 \\times 10^8$ m/s con una longitud "
        "de onda de 100 m. ¿Cuál es su frecuencia?",
        "3 × 10⁶ Hz",
        "Despejando de $v = \\lambda \\cdot f$: $f = \\frac{v}{\\lambda}$."
        "\n\n"
        "Reemplazando: $f = \\frac{3 \\times 10^8}{100} = 3 \\times 10^8 "
        "\\div 10^2 = 3 \\times 10^6$ Hz.\n\n"
        "Al dividir potencias de diez se RESTAN los exponentes. Ese resultado, 3 "
        "millones de hertz, son 3 MHz: el rango de la radio.",
        [
            ("3 × 10¹⁰ Hz", "Sumó los exponentes en vez de restarlos, que es lo que corresponde a una división."),
            ("3 × 10⁸ Hz", "Entregó la rapidez de la luz sin dividir por la longitud de onda."),
            ("100 Hz", "Entregó la longitud de onda con unidad de frecuencia."),
        ],
    ),
    # ---------- FÍSICA: electricidad ----------
    _q(
        "cie_electricidad", "facil",
        "Una ampolleta conectada a 220 V deja pasar una corriente de 0,5 A. "
        "¿Cuál es su resistencia?",
        "440 Ω",
        "De la ley de Ohm, $V = I \\cdot R$, se despeja $R = \\frac{V}{I}$."
        "\n\n"
        "Reemplazando: $R = \\frac{220}{0,5} = 440$ Ω.\n\n"
        "Dividir por un número menor que uno AUMENTA el resultado: por eso una "
        "corriente pequeña con voltaje alto implica una resistencia grande.",
        [
            ("110 Ω", "Multiplicó el voltaje por la corriente en vez de dividir."),
            ("220 Ω", "Entregó el voltaje sin dividir por la corriente."),
            ("0,002 Ω", "Dividió la corriente por el voltaje, invirtiendo la fórmula."),
        ],
    ),
    _q(
        "cie_electricidad", "medio",
        "Dos resistencias de 4 Ω y 6 Ω se conectan en SERIE. ¿Cuál es la "
        "resistencia equivalente?",
        "10 Ω",
        "En serie las resistencias simplemente se suman: "
        "$R_{eq} = R_1 + R_2 = 4 + 6 = 10$ Ω.\n\n"
        "Tiene sentido físico: la corriente debe atravesar las dos una tras "
        "otra, así que los obstáculos se acumulan.\n\n"
        "En paralelo es distinto —ahí la equivalente es MENOR que la más "
        "pequeña— porque la corriente encuentra dos caminos.",
        [
            ("2,4 Ω", "Aplicó la fórmula de paralelo, que corresponde cuando hay dos caminos para la corriente y no uno solo."),
            ("24 Ω", "Multiplicó las resistencias en vez de sumarlas."),
            ("2 Ω", "Restó las resistencias."),
        ],
    ),
    _q(
        "cie_electricidad", "medio",
        "Un artefacto funciona con 12 V y consume 2 A. ¿Cuál es su potencia "
        "eléctrica?",
        "24 W",
        "La potencia eléctrica es $P = V \\cdot I$.\n\n"
        "Reemplazando: $P = 12 \\cdot 2 = 24$ W.\n\n"
        "Esta es la fórmula que explica la cuenta de la luz: lo que se paga es "
        "potencia por tiempo, y por eso los artefactos de alto consumo son los "
        "que combinan voltaje y corriente altos.",
        [
            ("6 W", "Dividió el voltaje por la corriente en vez de multiplicar."),
            ("14 W", "Sumó ambos valores."),
            ("48 W", "Duplicó el resultado, quizá aplicando la corriente dos veces."),
        ],
    ),
    _q(
        "cie_electricidad", "dificil",
        "Una resistencia de 10 Ω es atravesada por una corriente de 3 A. ¿Qué "
        "potencia disipa?",
        "90 W",
        "Cuando se conocen la corriente y la resistencia conviene usar "
        "$P = I^2 \\cdot R$.\n\n"
        "Reemplazando: $P = 3^2 \\cdot 10 = 9 \\cdot 10 = 90$ W.\n\n"
        "La corriente va al cuadrado, así que duplicarla cuadruplica la potencia "
        "disipada en calor. Es la razón por la que un cable sobrecargado se "
        "calienta tan rápido.",
        [
            ("30 W", "Usó $I \\cdot R$ sin elevar la corriente al cuadrado."),
            ("300 W", "Elevó al cuadrado el producto completo en vez de solo la corriente."),
            ("0,9 W", "Dividió en lugar de multiplicar."),
        ],
    ),
    # ---------- QUÍMICA: átomo ----------
    _q(
        "cie_atomo", "facil",
        "Un átomo neutro tiene 11 protones. ¿Cuántos electrones tiene?",
        "11 electrones",
        "En un átomo NEUTRO la carga total es cero, y como protones y electrones "
        "tienen cargas iguales y opuestas, deben ser la misma cantidad.\n\n"
        "Por eso 11 protones implican 11 electrones.\n\n"
        "Si el número de electrones fuera distinto, ya no sería un átomo neutro "
        "sino un ion: con menos electrones sería un catión y con más, un anión.",
        [
            ("22 electrones", "Duplicó el número de protones, quizá confundiendo con el número másico."),
            ("0 electrones", "Interpretó «neutro» como ausencia de carga eléctrica en las partículas, cuando significa que las cargas se compensan."),
            ("12 electrones", "Agregó un electrón de más, lo que describiría un ion negativo y no un átomo neutro."),
        ],
    ),
    _q(
        "cie_atomo", "medio",
        "El ion $Ca^{2+}$ proviene de un átomo de calcio con número atómico 20. "
        "¿Cuántos electrones tiene el ion?",
        "18 electrones",
        "El número atómico dice que el átomo neutro tiene 20 protones y 20 "
        "electrones.\n\n"
        "La carga $2+$ significa que PERDIÓ dos electrones: quedan $20 - 2 = 18$."
        "\n\n"
        "Una carga positiva siempre indica electrones perdidos, no protones "
        "ganados: el número de protones define al elemento y no cambia en una "
        "reacción química.",
        [
            ("22 electrones", "Sumó dos electrones en vez de restarlos: eso describiría un ion negativo."),
            ("20 electrones", "Ignoró la carga del ion y respondió por el átomo neutro."),
            ("2 electrones", "Entregó la carga del ion como si fuera la cantidad de electrones."),
        ],
    ),
    _q(
        "cie_atomo", "medio",
        "Un átomo tiene número másico 40 y 20 neutrones. ¿Cuál es su número "
        "atómico?",
        "20",
        "El número másico es la suma de protones y neutrones: $A = Z + N$."
        "\n\n"
        "Despejando el número atómico: $Z = 40 - 20 = 20$.\n\n"
        "El número atómico es la identidad del elemento —20 protones son calcio, "
        "siempre— mientras que el número de neutrones puede variar entre sus "
        "isótopos.",
        [
            ("60", "Sumó ambos valores en vez de restarlos."),
            ("40", "Entregó el número másico sin descontar los neutrones."),
            ("2", "Dividió el número másico por los neutrones."),
        ],
    ),
    _q(
        "cie_atomo", "facil",
        "Un átomo de cloro tiene 17 protones y 18 neutrones. ¿Cuál es su "
        "número másico?",
        "35",
        "El número másico cuenta las partículas del núcleo: protones más "
        "neutrones, $A = Z + N$.\n\n"
        "Reemplazando: $A = 17 + 18 = 35$.\n\n"
        "Los electrones no entran en la cuenta. Su masa es unas 1.800 veces "
        "menor que la de un protón, así que no alcanzan a mover el número "
        "másico.",
        [
            ("17", "Entregó el número atómico, que cuenta solo los protones."),
            ("18", "Contó solo los neutrones."),
            ("1", "Restó los protones a los neutrones en vez de sumarlos."),
        ],
    ),
    # ---------- QUÍMICA: estequiometría ----------
    _q(
        "cie_estequiometria", "facil",
        "¿Cuántos gramos hay en 3 moles de agua (H₂O), si su masa molar es 18 "
        "g/mol?",
        "54 g",
        "La masa molar dice cuántos gramos pesa un mol, así que la masa es "
        "$m = n \\cdot M$.\n\n"
        "Reemplazando: $m = 3 \\cdot 18 = 54$ g.\n\n"
        "Si el ejercicio pidiera lo contrario —moles a partir de gramos— habría "
        "que dividir. Conviene fijarse siempre en qué unidad pide la respuesta.",
        [
            ("6 g", "Dividió los moles por la masa molar en vez de multiplicar."),
            ("21 g", "Sumó ambos valores."),
            ("18 g", "Entregó la masa de un solo mol, sin considerar que son tres."),
        ],
    ),
    _q(
        "cie_estequiometria", "medio",
        "En la reacción $N_2 + 3H_2 \\rightarrow 2NH_3$, ¿cuántos moles de "
        "amoníaco se producen a partir de 4 moles de nitrógeno, con hidrógeno "
        "en exceso?",
        "8 mol",
        "Los coeficientes de la ecuación dan la proporción: por cada 1 mol de "
        "$N_2$ se forman 2 de $NH_3$.\n\n"
        "Con 4 moles de nitrógeno: $4 \\times 2 = 8$ moles de amoníaco.\n\n"
        "«Hidrógeno en exceso» significa que el nitrógeno es el reactivo "
        "limitante: es él quien determina cuánto producto se forma.",
        [
            ("4 mol", "Copió los moles de nitrógeno sin aplicar la proporción 1 a 2 de la ecuación."),
            ("2 mol", "Entregó el coeficiente de la ecuación en vez de calcular."),
            ("12 mol", "Usó el coeficiente del hidrógeno, que no es el reactivo limitante."),
        ],
    ),
    _q(
        "cie_estequiometria", "dificil",
        "¿Cuántas moléculas hay en 2 moles de una sustancia? (Número de "
        "Avogadro: $6 \\times 10^{23}$ partículas por mol.)",
        "1,2 × 10²⁴ moléculas",
        "Un mol contiene $6 \\times 10^{23}$ partículas, así que dos moles "
        "contienen el doble.\n\n"
        "$2 \\times 6 \\times 10^{23} = 12 \\times 10^{23} = 1,2 \\times "
        "10^{24}$.\n\n"
        "El último paso es de notación científica: $12 \\times 10^{23}$ se "
        "escribe con un solo dígito antes de la coma, moviendo el exponente.",
        [
            ("6 × 10²³ moléculas", "Entregó el número de Avogadro sin multiplicarlo por los dos moles."),
            ("1,2 × 10²³ moléculas", "Movió la coma pero olvidó subir el exponente: $12 \\times 10^{23}$ son $1,2 \\times 10^{24}$."),
            ("3 × 10²³ moléculas", "Dividió por dos en vez de multiplicar."),
        ],
    ),
    # ---------- QUÍMICA: disoluciones ----------
    _q(
        "cie_soluciones", "facil",
        "¿Cuál es la concentración molar de una disolución que contiene 2 moles "
        "de soluto en 4 litros de disolución?",
        "0,5 mol/L",
        "La molaridad es moles de soluto por litro de disolución: "
        "$M = \\frac{n}{V}$.\n\n"
        "Reemplazando: $M = \\frac{2}{4} = 0,5$ mol/L.\n\n"
        "El volumen es el de la DISOLUCIÓN terminada, no el del solvente que se "
        "agregó: al disolverse, el soluto también ocupa espacio.",
        [
            ("2 mol/L", "Entregó los moles sin dividir por el volumen."),
            ("8 mol/L", "Multiplicó en vez de dividir."),
            ("4 mol/L", "Entregó el volumen como si fuera la concentración."),
        ],
    ),
    _q(
        "cie_soluciones", "medio",
        "¿Cuántos moles de soluto hay en 500 mL de una disolución 0,4 mol/L?",
        "0,2 mol",
        "Primero se pasan los mililitros a litros, porque la molaridad se define "
        "por litro: $500\\ \\text{mL} = 0,5$ L.\n\n"
        "Después, despejando de $M = \\frac{n}{V}$: $n = M \\cdot V = 0,4 "
        "\\cdot 0,5 = 0,2$ mol.\n\n"
        "Saltarse la conversión de unidades es el error más común de todo el "
        "tema, y multiplica el resultado por mil.",
        [
            ("200 mol", "Multiplicó por 500 sin convertir los mililitros a litros."),
            ("0,8 mol", "Dividió la concentración por el volumen en vez de multiplicar."),
            ("1,25 mol", "Dividió el volumen por la concentración."),
        ],
    ),
    _q(
        "cie_soluciones", "dificil",
        "Se diluye una disolución de 100 mL y 2 mol/L agregando agua hasta "
        "completar 400 mL. ¿Cuál es la concentración final?",
        "0,5 mol/L",
        "Al diluir, la cantidad de soluto NO cambia: solo aumenta el volumen. "
        "Eso se expresa como $M_1 V_1 = M_2 V_2$.\n\n"
        "Reemplazando: $2 \\cdot 100 = M_2 \\cdot 400$, entonces "
        "$M_2 = \\frac{200}{400} = 0,5$ mol/L.\n\n"
        "Cuadruplicar el volumen deja la concentración en la cuarta parte, que "
        "es exactamente lo que muestra el resultado.",
        [
            ("2 mol/L", "Supuso que la concentración no cambia al agregar agua; lo que no cambia es la cantidad de soluto."),
            ("8 mol/L", "Multiplicó por la razón de volúmenes en vez de dividir: agregar agua nunca concentra una disolución."),
            ("0,05 mol/L", "Se equivocó en un factor diez al operar los volúmenes."),
        ],
    ),
    _q(
        "cie_soluciones", "medio",
        "¿Qué masa de hidróxido de sodio se necesita para preparar 2 litros de "
        "una disolución 0,5 mol/L? La masa molar del $NaOH$ es 40 g/mol.",
        "40 g",
        "Son dos pasos y el orden importa. Primero, cuántos moles hace falta: "
        "$n = M \\cdot V = 0,5 \\cdot 2 = 1$ mol.\n\n"
        "Recién ahí se pasa de moles a gramos con la masa molar: "
        "$m = 1 \\cdot 40 = 40$ g.\n\n"
        "La molaridad nunca entrega gramos directamente: siempre pasa por los "
        "moles, y por eso la masa molar es imprescindible en este tipo de "
        "problema.",
        [
            ("20 g", "Se saltó el volumen y usó solo la concentración por la masa molar."),
            ("80 g", "Multiplicó por el volumen dos veces."),
            ("1 g", "Se quedó en los moles y no convirtió a gramos."),
        ],
    ),
    # ---------- QUÍMICA: ácido-base ----------
    _q(
        "cie_acidobase", "facil",
        "Una disolución tiene pH 9. ¿Es ácida, neutra o básica?",
        "Básica",
        "A 25 °C la escala de pH tiene su punto neutro en 7: bajo ese valor la "
        "disolución es ácida y sobre él, básica.\n\n"
        "Como 9 es mayor que 7, la disolución es básica.\n\n"
        "Cada unidad de pH representa un factor de diez en la concentración de "
        "iones hidrógeno, así que pH 9 tiene cien veces menos $H^+$ que pH 7.",
        [
            ("Ácida", "Invirtió la escala: los valores bajo 7 son los ácidos."),
            ("Neutra", "El punto neutro es exactamente 7, no cualquier valor cercano."),
            ("Depende de la temperatura, no se puede saber", "La temperatura sí mueve el punto neutro, pero el enunciado se refiere a las condiciones habituales de 25 °C, donde 9 es básico."),
        ],
    ),
    _q(
        "cie_acidobase", "medio",
        "¿Cuál es el pH de una disolución cuya concentración de iones hidrógeno "
        "es $1 \\times 10^{-5}$ mol/L?",
        "5",
        "El pH es el logaritmo negativo de la concentración de $H^+$: "
        "$pH = -\\log[H^+]$.\n\n"
        "Cuando la concentración es una potencia exacta de diez, el pH es el "
        "exponente sin el signo: $-\\log(10^{-5}) = 5$.\n\n"
        "Ese atajo solo funciona con potencias exactas de diez; con otros "
        "valores hay que calcular el logaritmo.",
        [
            ("−5", "Olvidó el signo negativo de la definición: el pH de una disolución acuosa común nunca es negativo."),
            ("9", "Calculó el pOH en vez del pH."),
            ("10⁻⁵", "Entregó la concentración misma en lugar de su logaritmo."),
        ],
    ),
    _q(
        "cie_acidobase", "dificil",
        "Una disolución tiene pOH 3. ¿Cuál es su concentración de iones "
        "hidróxido $[OH^-]$?",
        "1 × 10⁻³ mol/L",
        "El pOH se define como $pOH = -\\log[OH^-]$, así que para volver a la "
        "concentración se invierte: $[OH^-] = 10^{-pOH}$.\n\n"
        "Con pOH 3: $[OH^-] = 10^{-3}$ mol/L.\n\n"
        "Y como $pH + pOH = 14$, esta disolución tiene pH 11: es básica, lo que "
        "calza con tener bastante $OH^-$.",
        [
            ("1 × 10³ mol/L", "Olvidó el signo negativo del exponente. Una concentración de mil moles por litro es físicamente imposible."),
            ("1 × 10⁻¹¹ mol/L", "Usó el pH (11) en vez del pOH: esa sería la concentración de $H^+$."),
            ("3 mol/L", "Entregó el valor del pOH como si fuera una concentración."),
        ],
    ),
    # ---------- BIOLOGÍA: célula y transporte ----------
    # Biología es el único eje donde la respuesta no siempre sale de un
    # cálculo. Por eso el banco se apoya en lo que sí se puede recalcular
    # —conteos de cromosomas, estequiometría, proporciones— y en invariantes
    # de libro que no dependen de una fuente específica.
    _q(
        "cie_celula", "facil",
        "Una célula animal se coloca en una disolución con mayor concentración "
        "de sales que su interior. ¿Qué le ocurre?",
        "Pierde agua y se arruga",
        "El agua se mueve por osmosis desde donde está más diluida hacia donde "
        "está más concentrada, buscando igualar ambos lados.\n\n"
        "Si afuera hay más sal, el medio es hipertónico respecto de la célula: "
        "el agua sale y la célula se deshidrata y se arruga.\n\n"
        "El error de fondo es pensar que se mueve la sal. En osmosis la "
        "membrana deja pasar el agua, no el soluto: por eso lo que se desplaza "
        "es siempre el agua.",
        [
            ("Gana agua y se hincha", "Eso pasaría en un medio hipotónico, con menos sales afuera que adentro."),
            ("No cambia, porque la membrana es impermeable", "La membrana es selectivamente permeable y el agua la atraviesa con facilidad."),
            ("Absorbe sal hasta igualar las concentraciones", "En osmosis se mueve el agua, no el soluto; la sal no cruza libremente la membrana."),
        ],
    ),
    _q(
        "cie_celula", "medio",
        "La bomba sodio-potasio saca 3 iones $Na^+$ e ingresa 2 iones $K^+$ en "
        "cada ciclo. ¿Cuántas cargas positivas netas pierde la célula por "
        "ciclo?",
        "1 carga positiva",
        "Se cuentan las cargas que entran y las que salen: salen 3 positivas y "
        "entran 2 positivas.\n\n"
        "El balance es $3 - 2 = 1$ carga positiva que la célula pierde en cada "
        "ciclo.\n\n"
        "Ese desbalance es justamente el punto: la bomba no solo mueve iones, "
        "deja el interior más negativo que el exterior, y ese potencial de "
        "membrana es lo que después permite el impulso nervioso.",
        [
            ("5 cargas positivas", "Sumó los dos flujos en vez de restarlos; van en direcciones opuestas."),
            ("Ninguna, queda equilibrada", "Supuso un intercambio uno a uno, pero salen 3 y entran 2."),
            ("2 cargas positivas", "Contó solo los iones que entran."),
        ],
    ),
    _q(
        "cie_celula", "medio",
        "Una célula somática humana tiene 46 cromosomas y se divide por "
        "mitosis. ¿Cuántos cromosomas tiene cada célula hija?",
        "46 cromosomas",
        "La mitosis duplica el material genético antes de repartirlo, así que "
        "cada célula hija recibe una copia completa.\n\n"
        "De una célula con 46 cromosomas salen dos células con 46 cromosomas "
        "cada una: la mitosis conserva el número.\n\n"
        "La que reduce el número a la mitad es la meiosis, y solo ocurre para "
        "formar gametos. Confundirlas es el error más frecuente del tema.",
        [
            ("23 cromosomas", "Describió la meiosis, que sí reduce el número a la mitad."),
            ("92 cromosomas", "Se quedó en el paso intermedio, cuando el material ya se duplicó pero todavía no se reparte."),
            ("46 en una y 23 en la otra", "La mitosis reparte en partes iguales; no produce células distintas entre sí."),
        ],
    ),
    _q(
        "cie_celula", "medio",
        "Una sustancia entra a la célula desde donde está menos concentrada "
        "hacia donde está más concentrada. ¿Qué tipo de transporte es?",
        "Transporte activo, con gasto de ATP",
        "Ir de menor a mayor concentración es moverse EN CONTRA del gradiente, "
        "y eso nunca ocurre solo.\n\n"
        "Como el proceso no es espontáneo, la célula tiene que pagarlo con "
        "energía: por eso se llama transporte activo y consume ATP.\n\n"
        "La regla es corta: a favor del gradiente es gratis (transporte "
        "pasivo), en contra del gradiente se paga.",
        [
            ("Difusión simple, sin gasto de energía", "La difusión simple solo va a favor del gradiente, nunca en contra."),
            ("Difusión facilitada por proteínas", "También es pasiva: la proteína da el paso, pero no aporta energía para subir el gradiente."),
            ("Osmosis", "La osmosis describe el movimiento del agua, no el de un soluto contra su gradiente."),
        ],
    ),
    _q(
        "cie_celula", "dificil",
        "En la fotosíntesis, la ecuación global es $6CO_2 + 6H_2O \\rightarrow "
        "C_6H_{12}O_6 + 6O_2$. ¿Cuántas moléculas de $CO_2$ se necesitan para "
        "formar una molécula de glucosa?",
        "6 moléculas",
        "La ecuación está balanceada, así que los coeficientes se leen "
        "directamente como proporción.\n\n"
        "Delante del $CO_2$ hay un 6 y delante de la glucosa un 1: se "
        "necesitan 6 moléculas de $CO_2$ por cada molécula de glucosa.\n\n"
        "Ese 6 no es arbitrario. La glucosa es $C_6H_{12}O_6$ y tiene seis "
        "carbonos: cada uno tuvo que llegar desde una molécula de $CO_2$, "
        "porque los átomos no aparecen de la nada.",
        [
            ("12 moléculas", "Usó el subíndice del hidrógeno en vez del coeficiente del dióxido de carbono."),
            ("1 molécula", "Leyó el coeficiente de la glucosa en lugar del reactivo."),
            ("18 moléculas", "Sumó los coeficientes de ambos reactivos."),
        ],
    ),
    # ---------- BIOLOGÍA: genética ----------
    _q(
        "cie_genetica", "facil",
        "Se cruzan dos plantas heterocigotas $Aa$, donde $A$ es dominante. "
        "¿Qué porcentaje de la descendencia muestra el carácter recesivo?",
        "25%",
        "El cuadro de Punnett de $Aa \\times Aa$ da cuatro combinaciones "
        "igualmente probables: $AA$, $Aa$, $aA$ y $aa$.\n\n"
        "El carácter recesivo solo se ve cuando NO hay ningún alelo dominante, "
        "es decir únicamente en $aa$: 1 de cada 4, o sea el 25%.\n\n"
        "Las otras tres se ven iguales entre sí aunque su genotipo difiera. Por "
        "eso la proporción de fenotipos es 3:1 y la de genotipos 1:2:1.",
        [
            ("75%", "Entregó la proporción del carácter dominante, que son las otras tres combinaciones."),
            ("50%", "Confundió la proporción con la de los heterocigotos, que son dos de cuatro."),
            ("100%", "Supondría que ambos padres son recesivos, pero acá los dos son heterocigotos."),
        ],
    ),
    _q(
        "cie_genetica", "medio",
        "Se cruza una planta heterocigota $Aa$ con una homocigota recesiva "
        "$aa$. ¿Qué porcentaje de la descendencia muestra el carácter "
        "dominante?",
        "50%",
        "El progenitor $Aa$ aporta $A$ o $a$ con igual probabilidad; el $aa$ "
        "solo puede aportar $a$.\n\n"
        "Las combinaciones posibles son entonces $Aa$ y $aa$, mitad y mitad: el "
        "50% muestra el carácter dominante.\n\n"
        "Este cruce se llama retrocruzamiento de prueba y sirve justamente para "
        "eso: si aparece descendencia recesiva, el otro progenitor era "
        "heterocigoto sin lugar a dudas.",
        [
            ("25%", "Aplicó la proporción del cruce entre dos heterocigotos, que no es este caso."),
            ("75%", "Usó la proporción 3:1, que corresponde a $Aa \\times Aa$."),
            ("100%", "Eso ocurriría si el primer progenitor fuera homocigoto dominante $AA$."),
        ],
    ),
    _q(
        "cie_genetica", "medio",
        "Una célula humana con 46 cromosomas entra en meiosis. ¿Cuántos "
        "cromosomas tiene cada gameto resultante?",
        "23 cromosomas",
        "La meiosis es una división reduccional: su función es dejar la mitad "
        "del material genético en cada gameto.\n\n"
        "De 46 cromosomas se pasa a $46 \\div 2 = 23$ por gameto.\n\n"
        "Tiene que ser así para que la especie se mantenga estable: al unirse "
        "dos gametos de 23, el nuevo individuo vuelve a tener 46. Si la meiosis "
        "no redujera, cada generación duplicaría su número de cromosomas.",
        [
            ("46 cromosomas", "Describió la mitosis, que conserva el número; la meiosis lo reduce a la mitad."),
            ("92 cromosomas", "Duplicó en vez de reducir."),
            ("12 cromosomas", "No corresponde a ninguna división de 46; la mitad exacta es 23."),
        ],
    ),
    _q(
        "cie_genetica", "dificil",
        "Una mujer portadora de hemofilia ($X^H X^h$) tiene hijos con un hombre "
        "sano ($X^H Y$). La hemofilia es recesiva y está ligada al cromosoma X. "
        "¿Qué porcentaje de los HIJOS VARONES será hemofílico?",
        "50%",
        "Los varones reciben el Y del padre y uno de los dos X de la madre.\n\n"
        "La madre puede aportar $X^H$ o $X^h$ con igual probabilidad, así que "
        "los hijos varones son $X^H Y$ (sano) o $X^h Y$ (hemofílico): la mitad "
        "de ellos.\n\n"
        "Los varones no tienen un segundo X que compense el alelo enfermo, y "
        "por eso basta con uno para manifestar la enfermedad. Las hijas, en "
        "cambio, reciben el $X^H$ del padre y ninguna resulta hemofílica.",
        [
            ("25%", "Ese es el porcentaje sobre el total de hijos e hijas, no sobre los varones."),
            ("100%", "Requeriría que la madre fuera hemofílica $X^h X^h$, no portadora."),
            ("0%", "Ignoró que la madre portadora puede transmitir el alelo enfermo."),
        ],
    ),
    _q(
        "cie_genetica", "medio",
        "Dos personas de grupo sanguíneo $AB$ tienen descendencia. ¿Qué "
        "porcentaje de los hijos será del grupo $AB$?",
        "50%",
        "Cada progenitor $AB$ aporta el alelo $A$ o el $B$ con igual "
        "probabilidad.\n\n"
        "Las cuatro combinaciones son $AA$, $AB$, $BA$ y $BB$: dos de las "
        "cuatro son $AB$, o sea el 50%.\n\n"
        "El grupo $AB$ es el caso clásico de codominancia: ninguno de los dos "
        "alelos tapa al otro, y por eso se expresan ambos en vez de mezclarse.",
        [
            ("100%", "Supuso que dos padres $AB$ solo pueden tener hijos $AB$, pero cada uno aporta un solo alelo."),
            ("25%", "Contó solo una de las dos combinaciones que dan $AB$."),
            ("0%", "El cruce sí puede producir descendencia $AB$; de hecho es la mitad."),
        ],
    ),
    # ---------- BIOLOGÍA: ecosistemas ----------
    _q(
        "cie_ecosistemas", "facil",
        "En una cadena trófica, los productores fijan 10.000 kcal. Si en cada "
        "nivel se transfiere aproximadamente el 10% de la energía, ¿cuánta "
        "energía llega al consumidor secundario?",
        "100 kcal",
        "Se aplica el 10% una vez por cada salto de nivel.\n\n"
        "Del productor al consumidor primario: $10.000 \\times 0,1 = 1.000$ "
        "kcal. Del primario al secundario: $1.000 \\times 0,1 = 100$ kcal."
        "\n\n"
        "El 90% restante se pierde en cada paso como calor y actividad "
        "metabólica. Por eso las cadenas tróficas casi nunca superan los cuatro "
        "o cinco niveles: no queda energía suficiente para sostener otro.",
        [
            ("1.000 kcal", "Aplicó el 10% una sola vez: eso corresponde al consumidor primario."),
            ("10 kcal", "Aplicó el 10% tres veces, un nivel de más."),
            ("9.000 kcal", "Calculó lo que se pierde en el primer salto en vez de lo que se transfiere."),
        ],
    ),
    _q(
        "cie_ecosistemas", "facil",
        "En un ecosistema, ¿qué organismos ocupan el primer nivel trófico?",
        "Los productores, que fabrican su propio alimento",
        "El primer nivel trófico es el que introduce la energía al ecosistema "
        "sin tomarla de otro ser vivo.\n\n"
        "Eso lo hacen los productores —plantas, algas y algunas bacterias— "
        "capturando energía luminosa o química y transformándola en materia "
        "orgánica.\n\n"
        "Todos los demás niveles dependen de este. Sin productores no hay "
        "energía entrando al sistema, y la cadena completa se cae.",
        [
            ("Los herbívoros, porque comen directamente de las plantas", "Son el segundo nivel: dependen de los productores para obtener energía."),
            ("Los descomponedores, porque reciclan la materia", "Actúan sobre restos de todos los niveles; no son el punto de entrada de la energía."),
            ("Los depredadores tope, porque controlan el ecosistema", "Ocupan el último nivel, no el primero."),
        ],
    ),
    _q(
        "cie_ecosistemas", "medio",
        "Un consumidor primario recibe 500 kcal. Con una eficiencia de "
        "transferencia del 10%, ¿cuánta energía había en el nivel de los "
        "productores?",
        "5.000 kcal",
        "Acá se va hacia atrás en la cadena, así que en vez de multiplicar por "
        "0,1 hay que dividir.\n\n"
        "Si $500$ kcal son el 10% del nivel anterior, entonces ese nivel tenía "
        "$500 \\div 0,1 = 5.000$ kcal.\n\n"
        "Conviene comprobarlo en el sentido directo: el 10% de 5.000 es 500. Si "
        "el resultado no es mayor que el dato, el cálculo está al revés.",
        [
            ("50 kcal", "Multiplicó por 0,1 en vez de dividir: eso da el nivel siguiente, no el anterior."),
            ("5.500 kcal", "Sumó el 10% al dato en vez de tratarlo como una fracción del total."),
            ("450 kcal", "Restó el 10%, pero el nivel anterior siempre contiene mucha más energía."),
        ],
    ),
    _q(
        "cie_ecosistemas", "medio",
        "¿Por qué la energía fluye en un solo sentido en un ecosistema, "
        "mientras la materia circula?",
        "Porque la energía se degrada a calor y no se puede reutilizar",
        "La materia son átomos: el carbono de una hoja pasa al herbívoro, "
        "vuelve al suelo con los descomponedores y regresa a otra planta. Los "
        "mismos átomos dan vueltas indefinidamente.\n\n"
        "La energía no. En cada transformación una parte se disipa como calor, "
        "y ese calor ya no sirve para sostener procesos biológicos.\n\n"
        "Por eso el ecosistema necesita una entrada CONSTANTE de energía desde "
        "el Sol, pero no necesita que le lleguen átomos nuevos.",
        [
            ("Porque los depredadores impiden que la energía retroceda", "La dirección del flujo es una consecuencia física, no del comportamiento de los organismos."),
            ("Porque la materia se crea en los productores", "Los productores transforman materia existente; no la crean."),
            ("Porque la energía se acumula en el último nivel trófico", "Ocurre lo contrario: cada nivel dispone de mucha menos energía que el anterior."),
        ],
    ),
    _q(
        "cie_ecosistemas", "dificil",
        "Una pirámide de energía tiene 8.000 kcal en los productores. Con un "
        "10% de transferencia por nivel, ¿cuánta energía llega al consumidor "
        "terciario?",
        "8 kcal",
        "El consumidor terciario está a tres saltos del productor, así que el "
        "10% se aplica tres veces.\n\n"
        "$8.000 \\times 0,1 = 800$; $800 \\times 0,1 = 80$; $80 \\times "
        "0,1 = 8$ kcal.\n\n"
        "Equivale a dividir por mil de una vez. Ese desplome explica por qué los "
        "grandes depredadores son escasos: sostener uno exige una base enorme "
        "de productores debajo.",
        [
            ("80 kcal", "Aplicó el 10% dos veces: eso corresponde al consumidor secundario."),
            ("800 kcal", "Aplicó el 10% una sola vez, quedándose en el consumidor primario."),
            ("0,8 kcal", "Aplicó el 10% cuatro veces, un nivel más allá del terciario."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Historia y Ciencias Sociales
#
# 65 preguntas en 2 horas, 60 puntuadas. Tres ejes: Historia (Mundo, América y
# Chile), Formación ciudadana, y Economía y sociedad.
#
# El temario del DEMRE evalúa tres habilidades: pensamiento temporal y
# espacial, ANÁLISIS DE FUENTES y pensamiento crítico. Eso es lo que hace
# posible un banco verificable acá: las preguntas se apoyan en fuentes que
# escribe el proyecto (tablas de datos, textos de análisis), igual que en
# Competencia Lectora, y la respuesta correcta se comprueba contra la fuente.
# En Economía se suman preguntas de cálculo, verificables como las de
# matemática.
#
# Lo que NO hay acá es preguntas de memoria de contenido ("en qué año ocurrió
# tal cosa"). Ningún script puede comprobar que una afirmación histórica sea
# verdadera, y este proyecto no publica contenido que no pueda verificar. Ese
# tramo del temario necesita revisión de un profesor antes de existir.
# ---------------------------------------------------------------------------

SKILL_NODES_HISTORIA = [
    ("his_fuentes", "Análisis de fuentes históricas", "historia", 1, []),
    ("his_temporal", "Pensamiento temporal y cambio histórico", "historia", 2, ["his_fuentes"]),
    ("civ_democracia", "Democracia y participación", "ciudadania", 1, []),
    ("civ_derechos", "Derechos y deberes ciudadanos", "ciudadania", 2, ["civ_democracia"]),
    ("eco_indicadores", "Indicadores económicos", "economia", 1, []),
    ("eco_mercado", "Oferta, demanda y mercado", "economia", 2, ["eco_indicadores"]),
]

PASSAGES_HISTORIA = [
    {
        "key": "migracion_tabla",
        "title": "Población de la comuna de San Alberto, 1990-2020",
        "kind": "discontinuo",
        "source_note": (
            "Tabla construida con datos ficticios por 1000paes para ejercitar "
            "lectura de fuentes. No corresponde a una comuna real."
        ),
        "body": (
            "| Año | Población total | Población rural | Población urbana |\n"
            "|---|---|---|---|\n"
            "| 1990 | 12.400 | 8.100 | 4.300 |\n"
            "| 2000 | 15.800 | 6.900 | 8.900 |\n"
            "| 2010 | 21.300 | 5.200 | 16.100 |\n"
            "| 2020 | 28.700 | 3.800 | 24.900 |\n\n"
            "La comuna incorporó servicios de agua potable urbana en 1998 y un "
            "camino pavimentado hacia la capital regional en 2005."
        ),
    },
    {
        "key": "fuente_participacion",
        "title": "Dos miradas sobre la participación electoral",
        "kind": "no_literario",
        "source_note": "Textos originales de 1000paes, escritos como fuentes de contraste.",
        "body": (
            "FUENTE 1\n"
            "«Cuando el voto es voluntario, quien acude a las urnas lo hace por "
            "convicción. El resultado refleja la voluntad de quienes de verdad "
            "quieren decidir, y no la de quienes votan solo para evitar una "
            "multa. Una participación menor puede ser señal de un electorado "
            "más consciente, no de uno más indiferente.»\n\n"
            "FUENTE 2\n"
            "«El problema del voto voluntario no es cuánta gente vota, sino "
            "quién deja de votar. La abstención no se reparte parejo: se "
            "concentra en los sectores con menos ingresos y menos años de "
            "escolaridad. Un padrón que se achica por ese lado produce "
            "autoridades que responden a una parte del país y no al conjunto.»"
        ),
    },
]

QUESTIONS_HISTORIA = [
    # ---------- Análisis de fuentes: la tabla ----------
    _ql(
        "migracion_tabla", "his_fuentes", "facil",
        "Según la tabla, ¿cuánto aumentó la población total de la comuna entre "
        "1990 y 2020?",
        "16.300 habitantes",
        "El dato se obtiene restando los dos valores que la tabla entrega.\n\n"
        "1) Población total en 2020: 28.700.\n"
        "2) Población total en 1990: 12.400.\n"
        "3) Diferencia: 28.700 − 12.400 = 16.300 habitantes.\n\n"
        "Es una pregunta de lectura de fuente: el dato no requiere conocimiento "
        "previo, solo ubicar las dos celdas correctas y restar.",
        [
            ("28.700 habitantes", "Es la población de 2020, no el aumento respecto de 1990."),
            ("24.900 habitantes", "Es la población urbana de 2020, no la variación de la población total."),
            ("41.100 habitantes", "Sumó ambas poblaciones en lugar de restarlas."),
        ],
    ),
    _ql(
        "migracion_tabla", "his_temporal", "medio",
        "¿Qué proceso muestra la tabla entre 1990 y 2020?",
        "Un aumento de la población total acompañado de una migración del campo "
        "a la ciudad dentro de la comuna",
        "Hay que leer dos tendencias a la vez y relacionarlas.\n\n"
        "1) La población total sube de 12.400 a 28.700: la comuna crece.\n"
        "2) La población rural baja de 8.100 a 3.800, mientras la urbana sube "
        "de 4.300 a 24.900.\n"
        "3) O sea, el crecimiento se concentra en lo urbano mientras lo rural "
        "se reduce en términos absolutos.\n\n"
        "Ese doble movimiento es lo que describe un proceso de urbanización.",
        [
            ("Un despoblamiento general de la comuna", "La población total no baja: sube de 12.400 a 28.700."),
            ("Un crecimiento parejo entre zonas rurales y urbanas", "La tabla muestra lo contrario: lo rural cae mientras lo urbano crece."),
            ("Una migración desde otras regiones hacia el campo", "La tabla no informa de dónde llega la gente, y la población rural disminuye."),
        ],
    ),
    _ql(
        "migracion_tabla", "his_fuentes", "dificil",
        "Un estudiante afirma que el camino pavimentado de 2005 causó el "
        "crecimiento urbano de la comuna. ¿Qué se puede decir de esa "
        "afirmación a partir de la fuente?",
        "La fuente no permite afirmarlo: el crecimiento urbano ya venía "
        "ocurriendo antes de 2005",
        "Acá se evalúa si el estudiante distingue entre lo que la fuente muestra "
        "y lo que interpreta.\n\n"
        "1) La población urbana pasó de 4.300 en 1990 a 8.900 en 2000, es "
        "decir, ya se había duplicado antes de que existiera el camino.\n"
        "2) La tabla registra la obra de 2005, pero no entrega ninguna "
        "información que permita atribuirle el crecimiento.\n"
        "3) Que dos hechos ocurran en el mismo periodo no prueba que uno cause "
        "el otro.\n\n"
        "Lo correcto es decir que la fuente no alcanza para sostener esa "
        "afirmación, sin negar que el camino haya podido influir.",
        [
            ("La afirmación es correcta: el crecimiento se acelera después de 2005", "El crecimiento urbano ya venía desde antes, así que la fuente no permite atribuirlo al camino."),
            ("La afirmación es falsa: el camino redujo la población urbana", "La población urbana siguió creciendo después de 2005, de 8.900 a 24.900."),
            ("La afirmación es correcta porque la fuente menciona el camino", "Que la fuente mencione un hecho no significa que establezca su efecto."),
        ],
    ),

    # ---------- Formación ciudadana: contraste de fuentes ----------
    _ql(
        "fuente_participacion", "civ_democracia", "medio",
        "¿En qué se diferencian las dos fuentes respecto de la participación "
        "electoral?",
        "La primera valora la convicción de quien vota; la segunda se preocupa "
        "de quiénes quedan fuera",
        "Ambas hablan de lo mismo pero miden cosas distintas.\n\n"
        "1) La Fuente 1 pone el foco en la calidad del voto: quien acude lo "
        "hace «por convicción», y una participación menor podría indicar un "
        "electorado «más consciente».\n"
        "2) La Fuente 2 desplaza la pregunta: dice explícitamente que el "
        "problema «no es cuánta gente vota, sino quién deja de votar», y apunta "
        "a que la abstención se concentra en ciertos sectores.\n\n"
        "La diferencia no es el dato sino qué consideran relevante de él.",
        [
            ("La primera defiende el voto obligatorio y la segunda el voluntario", "Ninguna de las dos propone un sistema: discuten cómo interpretar la participación."),
            ("La primera usa datos estadísticos y la segunda opiniones personales", "Ninguna entrega cifras; ambas argumentan."),
            ("Ambas coinciden en que la baja participación es un problema grave", "La Fuente 1 sugiere lo contrario: que puede ser señal de un electorado más consciente."),
        ],
    ),
    _ql(
        "fuente_participacion", "civ_derechos", "dificil",
        "¿Qué supuesto sobre la representación política sostiene la Fuente 2?",
        "Que una autoridad electa por un padrón sesgado responde a una parte "
        "del país y no al conjunto",
        "El supuesto no está dicho como tesis, hay que extraerlo del cierre del "
        "texto.\n\n"
        "1) La fuente sostiene que la abstención «se concentra en los sectores "
        "con menos ingresos y menos años de escolaridad».\n"
        "2) De ahí concluye que ese padrón «produce autoridades que responden a "
        "una parte del país y no al conjunto».\n"
        "3) El supuesto que conecta ambas ideas es que la composición de quienes "
        "votan determina a quién termina representando la autoridad electa.\n\n"
        "Sin ese supuesto, el argumento no se sostendría.",
        [
            ("Que el voto obligatorio garantiza mejores autoridades", "La fuente no habla de la calidad de las autoridades ni propone la obligatoriedad."),
            ("Que la participación electoral siempre disminuye con el tiempo", "La fuente no afirma ninguna tendencia temporal."),
            ("Que quienes no votan carecen de interés en la política", "La fuente atribuye la abstención a factores socioeconómicos, no a falta de interés."),
        ],
    ),

    # ---------- Economía: cuantitativo, verificable ----------
    _q(
        "eco_indicadores", "medio",
        "En un país hay 8.000.000 de personas en la fuerza de trabajo y 640.000 "
        "están desocupadas. ¿Cuál es la tasa de desempleo?",
        "8%",
        "La tasa de desempleo es la proporción de desocupados dentro de la "
        "fuerza de trabajo, no dentro de la población total.\n\n"
        "1) Divide: 640.000 ÷ 8.000.000 = 0,08.\n"
        "2) Expresa en porcentaje: 0,08 · 100 = 8%.\n\n"
        "El denominador importa: si se usara la población total, que incluye "
        "niños y personas fuera de la fuerza de trabajo, la tasa quedaría "
        "artificialmente baja.",
        [
            ("0,08%", "Olvidó multiplicar por 100 al pasar la proporción a porcentaje."),
            ("12,5%", "Dividió la fuerza de trabajo por los desocupados, invirtiendo la razón."),
            ("64%", "Corrió la coma decimal al calcular la proporción."),
        ],
    ),
    _q(
        "eco_indicadores", "medio",
        "Si una canasta de bienes costaba $50.000 el año pasado y hoy cuesta "
        "$53.500, ¿cuál fue la variación porcentual de precios?",
        "7%",
        "La variación porcentual compara el cambio con el valor inicial.\n\n"
        "1) Calcula el alza: 53.500 − 50.000 = 3.500.\n"
        "2) Divide por el valor inicial: 3.500 ÷ 50.000 = 0,07.\n"
        "3) Expresa en porcentaje: 7%.\n\n"
        "Es el mismo cálculo con que se construye el IPC, que mide cuánto varía "
        "el costo de una canasta representativa entre dos momentos.",
        [
            ("3,5%", "Dividió el alza por 100.000 o corrió la coma decimal."),
            ("6,5%", "Dividió por el precio nuevo en vez del inicial."),
            ("3.500%", "Entregó el alza en pesos como si fuera un porcentaje."),
        ],
    ),
    _q(
        "eco_mercado", "medio",
        "En un mercado, cuando el precio de un bien sube y todo lo demás se "
        "mantiene constante, ¿qué ocurre según la ley de demanda?",
        "La cantidad demandada disminuye",
        "La ley de demanda describe una relación inversa entre precio y "
        "cantidad demandada.\n\n"
        "1) Si el precio sube, el bien se vuelve más caro respecto de sus "
        "alternativas y respecto del ingreso de las personas.\n"
        "2) Por eso, manteniendo todo lo demás igual, la cantidad que los "
        "consumidores están dispuestos a comprar disminuye.\n\n"
        "La condición «todo lo demás constante» es parte de la ley: si al mismo "
        "tiempo cambiara el ingreso o el precio de un sustituto, el resultado "
        "podría ser otro.",
        [
            ("La cantidad demandada aumenta", "Eso describiría una relación directa, contraria a la ley de demanda."),
            ("La demanda se desplaza hacia la derecha", "Un cambio de precio mueve la cantidad demandada a lo largo de la curva; la curva se desplaza cuando cambia otro factor."),
            ("La cantidad demandada se mantiene igual", "Eso solo ocurriría en un caso extremo de demanda perfectamente inelástica, que no es lo que describe la ley."),
        ],
    ),
    _q(
        "eco_mercado", "dificil",
        "El precio de equilibrio de un mercado es aquel en que:",
        "La cantidad ofrecida es igual a la cantidad demandada",
        "El equilibrio es el punto donde las dos fuerzas del mercado coinciden.\n\n"
        "1) Si el precio estuviera por encima, habría más oferta que demanda y "
        "el excedente presionaría el precio a la baja.\n"
        "2) Si estuviera por debajo, la demanda superaría a la oferta y la "
        "escasez lo empujaría al alza.\n"
        "3) Solo cuando ambas cantidades coinciden desaparece la presión y el "
        "precio se estabiliza.\n\n"
        "Por eso el equilibrio se define por la igualdad de cantidades, no por "
        "el nivel del precio ni por el beneficio de alguna de las partes.",
        [
            ("El precio alcanza su valor más bajo posible", "El equilibrio no es un mínimo: puede ser un precio alto si la oferta es escasa."),
            ("Los productores obtienen su mayor ganancia", "El equilibrio iguala cantidades; no maximiza la ganancia de ninguna de las partes."),
            ("Toda la población puede comprar el bien", "El equilibrio no garantiza acceso universal: quienes no pueden pagar ese precio quedan fuera."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Lecciones del Árbol de Habilidades
#
# El árbol medía sin enseñar: un estudiante que fallaba en "Potencias y raíces"
# solo recibía más preguntas de potencias y raíces. Estas lecciones son lo que
# se estudia ANTES de practicar el nodo.
#
# Cada una tiene cuatro partes con trabajos distintos:
#   intro              para qué sirve esto (una o dos frases, sin jerga)
#   theory             las propiedades que hay que saber
#   example_statement  un ejercicio del tipo que sale en la prueba
#   example_steps      su resolución, donde cada paso dice POR QUÉ se hace
#   common_error       la trampa en la que cae casi todo el mundo
#
# El "porque" de cada paso es obligatorio. Un paso sin justificación produce
# estudiantes que copian el procedimiento y se pierden apenas cambia el
# enunciado, que es exactamente lo que hace la PAES.
#
# Los números de cada ejemplo se recalculan en scripts/verificar_banco.py.
# ---------------------------------------------------------------------------

LESSONS: dict[str, dict] = {
    "num_racionales": {
        "intro": (
            "Sumar, restar, multiplicar y dividir fracciones aparece dentro de "
            "casi todos los otros temas: si esto se te enreda, se te enreda "
            "también lo que viene después."
        ),
        "theory": (
            "**Para sumar o restar** hace falta el mismo denominador. Se busca "
            "el mínimo común múltiplo de los denominadores, se amplifica cada "
            "fracción hasta él y recién ahí se suman los numeradores. El "
            "denominador NO se suma.\n\n"
            "**Para multiplicar** no hace falta nada: numerador por numerador y "
            "denominador por denominador.\n\n"
            "**Para dividir** se multiplica por el inverso de la segunda: "
            "$\\frac{a}{b} \\div \\frac{c}{d} = \\frac{a}{b} \\cdot \\frac{d}{c}$.\n\n"
            "**El orden de las operaciones** manda sobre todo lo anterior: "
            "primero paréntesis, después multiplicaciones y divisiones, y al "
            "final sumas y restas."
        ),
        "example_statement": "Calcula $\\frac{5}{6} - \\frac{2}{9}$.",
        "example_steps": [
            {
                "accion": "Busco el mínimo común múltiplo de 6 y 9. Los múltiplos de 6 son 6, 12, 18… y los de 9 son 9, 18… El primero que comparten es 18.",
                "porque": "Restar fracciones exige que las dos midan con la misma unidad. Sextos y novenos son unidades distintas: no se pueden restar directamente.",
            },
            {
                "accion": "Amplifico cada fracción a dieciochoavos: $\\frac{5}{6} = \\frac{15}{18}$ (multipliqué arriba y abajo por 3) y $\\frac{2}{9} = \\frac{4}{18}$ (por 2).",
                "porque": "Multiplicar numerador y denominador por el mismo número no cambia el valor de la fracción, solo cómo está escrita.",
            },
            {
                "accion": "Ahora sí resto los numeradores: $\\frac{15}{18} - \\frac{4}{18} = \\frac{11}{18}$.",
                "porque": "Con la misma unidad abajo, restar quince dieciochoavos menos cuatro dieciochoavos es restar 15 − 4.",
            },
            {
                "accion": "Reviso si se puede simplificar: 11 es primo y no divide a 18, así que $\\frac{11}{18}$ es la respuesta final.",
                "porque": "En la PAES las alternativas vienen simplificadas; una respuesta correcta sin simplificar puede no aparecer entre ellas.",
            },
        ],
        "common_error": (
            "Restar los denominadores entre sí: $\\frac{5}{6} - \\frac{2}{9} \\neq "
            "\\frac{3}{3}$. El denominador dice en cuántas partes se dividió el "
            "entero, no es una cantidad que se sume ni se reste."
        ),
    },
    "num_potencias_raices": {
        "intro": (
            "Las potencias son la forma corta de escribir multiplicaciones "
            "repetidas, y sus propiedades permiten operar sin desarrollar nada. "
            "Aparecen en notación científica, interés compuesto y funciones."
        ),
        "theory": (
            "**Mismo base, se suman los exponentes** al multiplicar: "
            "$a^m \\cdot a^n = a^{m+n}$. Al dividir se restan: "
            "$\\frac{a^m}{a^n} = a^{m-n}$.\n\n"
            "**Potencia de potencia**: se multiplican los exponentes, "
            "$(a^m)^n = a^{m \\cdot n}$.\n\n"
            "**Exponente negativo** significa recíproco, no número negativo: "
            "$a^{-n} = \\frac{1}{a^n}$. Así, $2^{-3} = \\frac{1}{8}$, que es "
            "positivo.\n\n"
            "**Exponente cero**: $a^0 = 1$ para cualquier $a \\neq 0$.\n\n"
            "**Raíces**: una raíz es una potencia de exponente fraccionario, "
            "$\\sqrt[n]{a^m} = a^{m/n}$. Por eso $\\sqrt{a} = a^{1/2}$ y valen "
            "las mismas propiedades."
        ),
        "example_statement": "Calcula $\\dfrac{2^5 \\cdot 2^{-3}}{2^{-1}}$.",
        "example_steps": [
            {
                "accion": "Arriba tengo la misma base multiplicándose, así que sumo los exponentes: $2^5 \\cdot 2^{-3} = 2^{5+(-3)} = 2^2$.",
                "porque": "La propiedad del producto vale igual con exponentes negativos: sumar −3 es lo mismo que restar 3.",
            },
            {
                "accion": "Ahora divido: $\\frac{2^2}{2^{-1}} = 2^{2-(-1)} = 2^{3}$.",
                "porque": "Al dividir se resta el exponente de abajo. Restar un número negativo suma, y ahí es donde se pierde la mayoría.",
            },
            {
                "accion": "Calculo la potencia: $2^3 = 8$.",
                "porque": "El resultado se pide como número, y $2^3$ significa $2 \\cdot 2 \\cdot 2$.",
            },
        ],
        "common_error": (
            "Creer que $2^{-3}$ es $-8$. El signo del exponente no pasa al "
            "resultado: indica que la potencia va al denominador. "
            "$2^{-3} = \\frac{1}{2^3} = \\frac{1}{8}$, un número positivo."
        ),
    },
    "num_porcentajes": {
        "intro": (
            "Un porcentaje es una fracción de denominador 100. Es el contenido "
            "que más aparece en la vida real —descuentos, IVA, sueldos— y uno de "
            "los que más se repite en la prueba."
        ),
        "theory": (
            "**El $p\\%$ de una cantidad** es multiplicarla por "
            "$\\frac{p}{100}$. El 20% de 350 es $350 \\cdot 0{,}20 = 70$.\n\n"
            "**Aumentar un $p\\%$** es multiplicar por $1 + \\frac{p}{100}$; "
            "**descontar un $p\\%$**, por $1 - \\frac{p}{100}$. Subir 20% es "
            "multiplicar por 1,2; bajar 15%, por 0,85.\n\n"
            "**Los porcentajes sucesivos se multiplican, no se suman.** Subir "
            "20% y luego bajar 20% NO devuelve al valor original.\n\n"
            "**Proporcionalidad directa**: si una cantidad crece, la otra crece "
            "en la misma razón, y $\\frac{a}{b}$ se mantiene constante. En la "
            "**inversa**, el producto $a \\cdot b$ es el que se mantiene."
        ),
        "example_statement": (
            "Una bicicleta cuesta $\\$20.000$. En marzo sube un 20% y en abril, "
            "sobre el precio nuevo, baja un 15%. ¿Cuánto cuesta después de los "
            "dos cambios?"
        ),
        "example_steps": [
            {
                "accion": "Aplico la subida: $20.000 \\cdot 1{,}20 = 24.000$.",
                "porque": "Subir 20% es quedarse con el 100% original más 20 puntos: el 120%, o sea 1,20.",
            },
            {
                "accion": "Aplico la baja SOBRE los $\\$24.000$: $24.000 \\cdot 0{,}85 = 20.400$.",
                "porque": "El enunciado dice «sobre el precio nuevo». El 15% se calcula del valor vigente en abril, no del precio de partida.",
            },
            {
                "accion": "El precio final es $\\$20.400$, es decir 400 pesos más caro que al principio.",
                "porque": "Subir 20% y bajar 15% no se cancelan: $1{,}20 \\cdot 0{,}85 = 1{,}02$, un alza neta del 2%.",
            },
        ],
        "common_error": (
            "Sumar y restar los porcentajes: creer que +20% y −15% dejan un +5% "
            "y responder $\\$21.000$. Los porcentajes se aplican uno sobre el "
            "resultado del otro, así que se multiplican."
        ),
    },
    "alg_expresiones": {
        "intro": (
            "Factorizar es escribir una suma como una multiplicación. Sirve para "
            "simplificar fracciones algebraicas y para resolver ecuaciones: si un "
            "producto es cero, alguno de sus factores es cero."
        ),
        "theory": (
            "**Factor común**: lo que se repite en todos los términos sale "
            "afuera. $6x^2 + 9x = 3x(2x + 3)$.\n\n"
            "**Diferencia de cuadrados**: "
            "$a^2 - b^2 = (a+b)(a-b)$. Ojo: la SUMA de cuadrados no se factoriza "
            "en los reales.\n\n"
            "**Trinomio cuadrado perfecto**: "
            "$a^2 \\pm 2ab + b^2 = (a \\pm b)^2$.\n\n"
            "**Trinomio de la forma** $x^2 + bx + c$: se buscan dos números que "
            "multiplicados den $c$ y sumados den $b$. Para $x^2 + 5x + 6$ son 2 y "
            "3, así que queda $(x+2)(x+3)$."
        ),
        "example_statement": "Factoriza completamente $2x^2 - 8$.",
        "example_steps": [
            {
                "accion": "Saco el factor común 2: $2x^2 - 8 = 2(x^2 - 4)$.",
                "porque": "Los dos términos son divisibles por 2. El factor común siempre se busca primero, porque deja adentro una expresión más simple.",
            },
            {
                "accion": "Reconozco que $x^2 - 4$ es una diferencia de cuadrados, con $a = x$ y $b = 2$, porque $4 = 2^2$.",
                "porque": "Ambos términos son cuadrados perfectos y están restándose, que es exactamente la forma $a^2 - b^2$.",
            },
            {
                "accion": "Aplico la identidad: $x^2 - 4 = (x+2)(x-2)$, así que el resultado es $2(x+2)(x-2)$.",
                "porque": "«Completamente» significa que ningún factor se puede seguir descomponiendo, y $x+2$ y $x-2$ ya no se pueden.",
            },
        ],
        "common_error": (
            "Detenerse en $2(x^2 - 4)$ y darlo por factorizado, o intentar "
            "factorizar $x^2 + 4$. La suma de cuadrados no tiene factorización "
            "en los números reales."
        ),
    },
    "alg_lineal": {
        "intro": (
            "Resolver una ecuación es encontrar el valor que hace verdadera la "
            "igualdad. Es la herramienta base: modelar un problema en palabras y "
            "despejar la incógnita."
        ),
        "theory": (
            "**Lo que se hace a un lado se hace al otro.** Sumar, restar, "
            "multiplicar o dividir por lo mismo a ambos lados mantiene la "
            "igualdad.\n\n"
            "**El orden conviene así**: primero se eliminan paréntesis, después "
            "se juntan las incógnitas a un lado y los números al otro, y recién "
            "al final se divide.\n\n"
            "**Inecuaciones**: se resuelven igual, con UNA diferencia crítica. "
            "Al multiplicar o dividir por un número **negativo**, el signo de "
            "desigualdad se da vuelta: de $-2x < 6$ se pasa a $x > -3$.\n\n"
            "**Siempre conviene verificar**: reemplazar la solución en la "
            "ecuación original y comprobar que los dos lados dan lo mismo."
        ),
        "example_statement": "Resuelve $3(x - 2) + 4 = 2x + 7$.",
        "example_steps": [
            {
                "accion": "Elimino el paréntesis multiplicando: $3x - 6 + 4 = 2x + 7$.",
                "porque": "El 3 multiplica a TODO lo que está dentro del paréntesis, tanto a la $x$ como al −2.",
            },
            {
                "accion": "Junto los números del lado izquierdo: $3x - 2 = 2x + 7$.",
                "porque": "$-6 + 4 = -2$. Ordenar antes de despejar evita arrastrar términos de más.",
            },
            {
                "accion": "Resto $2x$ a ambos lados: $x - 2 = 7$.",
                "porque": "Quiero las incógnitas juntas de un solo lado, y restar lo mismo a ambos lados no altera la igualdad.",
            },
            {
                "accion": "Sumo 2 a ambos lados: $x = 9$.",
                "porque": "Queda la incógnita sola, que es lo que significa resolver.",
            },
            {
                "accion": "Verifico en la ecuación original: a la izquierda $3(9-2)+4 = 21+4 = 25$, y a la derecha $2 \\cdot 9 + 7 = 25$. Coinciden.",
                "porque": "La verificación detecta cualquier error de signo en menos de diez segundos, y en la prueba vale lo mismo que resolver bien.",
            },
        ],
        "common_error": (
            "En las inecuaciones, no dar vuelta el signo al dividir por un "
            "negativo. Si $-2x < 6$, dividir por −2 obliga a escribir $x > -3$, "
            "no $x < -3$."
        ),
    },
    "alg_sistemas": {
        "intro": (
            "Un sistema 2x2 son dos ecuaciones con dos incógnitas. Resolverlo es "
            "encontrar el par de valores que cumple las dos a la vez: el punto "
            "donde se cruzan las dos rectas."
        ),
        "theory": (
            "**Sustitución**: se despeja una incógnita en una ecuación y se "
            "reemplaza en la otra. Conviene cuando alguna ya está casi "
            "despejada.\n\n"
            "**Igualación**: se despeja la MISMA incógnita en ambas y se igualan "
            "las expresiones.\n\n"
            "**Reducción (o suma y resta)**: se multiplican las ecuaciones por "
            "los números necesarios para que una incógnita quede con "
            "coeficientes opuestos, y se suman para que desaparezca.\n\n"
            "**La solución es un par $(x, y)$**, no un solo número, y tiene que "
            "cumplir LAS DOS ecuaciones. Siempre se verifica en ambas."
        ),
        "example_statement": "Resuelve el sistema $x + y = 12$ ; $x - y = 2$.",
        "example_steps": [
            {
                "accion": "Sumo las dos ecuaciones término a término: $(x+y) + (x-y) = 12 + 2$, que da $2x = 14$.",
                "porque": "Los términos $+y$ y $-y$ son opuestos, así que al sumar se cancelan y queda una sola incógnita. Es el método de reducción.",
            },
            {
                "accion": "Despejo: $x = \\frac{14}{2} = 7$.",
                "porque": "Con una sola incógnita, la ecuación se resuelve dividiendo.",
            },
            {
                "accion": "Reemplazo $x = 7$ en la primera ecuación: $7 + y = 12$, entonces $y = 5$.",
                "porque": "Ya conocido un valor, cualquiera de las dos ecuaciones originales entrega el otro.",
            },
            {
                "accion": "Verifico en la SEGUNDA: $7 - 5 = 2$. Correcto. La solución es $(7, 5)$.",
                "porque": "Verificar en la ecuación que no se usó para despejar es lo que detecta un error de reemplazo.",
            },
        ],
        "common_error": (
            "Encontrar $x$ y entregar eso como respuesta. La solución de un "
            "sistema 2x2 son los dos valores; una alternativa con el $x$ correcto "
            "y el $y$ equivocado es una trampa clásica de la prueba."
        ),
    },
    "alg_cuadratica": {
        "intro": (
            "Una ecuación cuadrática tiene la incógnita elevada al cuadrado y "
            "puede tener dos soluciones, una o ninguna. Describe todo lo que "
            "sube y baja: áreas, trayectorias, máximos."
        ),
        "theory": (
            "**Forma general**: $ax^2 + bx + c = 0$, con $a \\neq 0$.\n\n"
            "**Fórmula general**: "
            "$x = \\dfrac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$. Sirve siempre.\n\n"
            "**El discriminante** $\\Delta = b^2 - 4ac$ dice cuántas soluciones "
            "hay antes de calcularlas: si $\\Delta > 0$ hay dos, si "
            "$\\Delta = 0$ hay una, y si $\\Delta < 0$ no hay solución "
            "real.\n\n"
            "**Por factorización**: si la ecuación se puede escribir como "
            "$(x - p)(x - q) = 0$, entonces $x = p$ o $x = q$, porque un producto "
            "solo da cero si alguno de sus factores es cero."
        ),
        "example_statement": "Resuelve $x^2 - 5x + 6 = 0$.",
        "example_steps": [
            {
                "accion": "Calculo el discriminante: $\\Delta = (-5)^2 - 4 \\cdot 1 \\cdot 6 = 25 - 24 = 1$.",
                "porque": "Es positivo, así que sé de antemano que hay dos soluciones reales distintas.",
            },
            {
                "accion": "Busco dos números que multiplicados den 6 y sumados den −5: son −2 y −3.",
                "porque": "Con números enteros pequeños, factorizar es más rápido y seguro que aplicar la fórmula.",
            },
            {
                "accion": "Escribo la ecuación factorizada: $(x - 2)(x - 3) = 0$.",
                "porque": "Al desarrollarla se obtiene $x^2 - 5x + 6$, así que es la misma ecuación escrita como producto.",
            },
            {
                "accion": "Un producto es cero solo si algún factor lo es, así que $x = 2$ o $x = 3$.",
                "porque": "Esta es la propiedad que hace útil factorizar, y es la que la prueba evalúa.",
            },
        ],
        "common_error": (
            "Entregar una sola solución. Una cuadrática con discriminante "
            "positivo tiene dos, y el enunciado suele pedir la suma, el producto "
            "o la mayor de ellas."
        ),
    },
    "alg_funciones": {
        "intro": (
            "Una función asigna a cada valor de entrada exactamente un valor de "
            "salida. La lineal crece siempre al mismo ritmo; la cuadrática "
            "cambia de dirección una vez."
        ),
        "theory": (
            "**Función lineal**: $f(x) = mx + n$. Su gráfico es una recta. La "
            "**pendiente** $m$ dice cuánto sube $y$ cuando $x$ aumenta en 1: si "
            "$m > 0$ la recta sube, si $m < 0$ baja. El **coeficiente de "
            "posición** $n$ es donde corta al eje $Y$.\n\n"
            "**Pendiente entre dos puntos**: "
            "$m = \\dfrac{y_2 - y_1}{x_2 - x_1}$.\n\n"
            "**Función cuadrática**: $f(x) = ax^2 + bx + c$. Su gráfico es una "
            "parábola: abre hacia arriba si $a > 0$ y hacia abajo si $a < 0$.\n\n"
            "**Vértice**: está en $x = -\\dfrac{b}{2a}$, y ahí ocurre el mínimo "
            "(si abre hacia arriba) o el máximo (si abre hacia abajo)."
        ),
        "example_statement": (
            "Una recta pasa por los puntos $(1, 5)$ y $(3, 11)$. Encuentra su "
            "ecuación."
        ),
        "example_steps": [
            {
                "accion": "Calculo la pendiente: $m = \\frac{11 - 5}{3 - 1} = \\frac{6}{2} = 3$.",
                "porque": "La pendiente es cuánto cambia $y$ dividido por cuánto cambió $x$. Acá $y$ subió 6 mientras $x$ avanzaba 2.",
            },
            {
                "accion": "Uso $y = 3x + n$ y reemplazo el punto $(1, 5)$: $5 = 3 \\cdot 1 + n$.",
                "porque": "Si el punto pertenece a la recta, sus coordenadas tienen que satisfacer la ecuación.",
            },
            {
                "accion": "Despejo: $n = 5 - 3 = 2$. La ecuación es $y = 3x + 2$.",
                "porque": "Con la pendiente y un punto queda determinada una única recta.",
            },
            {
                "accion": "Verifico con el otro punto: $3 \\cdot 3 + 2 = 11$. Coincide.",
                "porque": "Si el segundo punto no calzara, el error estaría en la pendiente.",
            },
        ],
        "common_error": (
            "Invertir la pendiente y calcular $\\frac{x_2 - x_1}{y_2 - y_1}$. "
            "La pendiente es el cambio vertical dividido por el horizontal, en "
            "ese orden."
        ),
    },
    "geo_plana": {
        "intro": (
            "Perímetro es cuánto mide el contorno; área, cuánta superficie cubre. "
            "Son magnitudes distintas y en la prueba conviven en el mismo "
            "enunciado para ver si se confunden."
        ),
        "theory": (
            "**Rectángulo**: área $= a \\cdot b$, perímetro $= 2(a+b)$.\n\n"
            "**Triángulo**: área $= \\dfrac{base \\cdot altura}{2}$. La altura "
            "es perpendicular a la base, no el lado inclinado.\n\n"
            "**Círculo**: área $= \\pi r^2$, perímetro (circunferencia) "
            "$= 2\\pi r$. El diámetro es $2r$: si el enunciado da el diámetro, "
            "hay que dividirlo entre 2 antes de usar la fórmula.\n\n"
            "**Trapecio**: área $= \\dfrac{(B + b) \\cdot h}{2}$.\n\n"
            "**Figuras compuestas**: se descomponen en figuras conocidas y se "
            "suman o restan sus áreas."
        ),
        "example_statement": (
            "Un jardín rectangular mide 8 m por 5 m y tiene en el centro una "
            "fuente circular de 2 m de radio. ¿Cuál es el área de pasto? "
            "(Usa $\\pi \\approx 3{,}14$.)"
        ),
        "example_steps": [
            {
                "accion": "Área del rectángulo completo: $8 \\cdot 5 = 40$ m².",
                "porque": "Es la superficie total antes de descontar nada.",
            },
            {
                "accion": "Área de la fuente: $\\pi r^2 = 3{,}14 \\cdot 2^2 = 3{,}14 \\cdot 4 = 12{,}56$ m².",
                "porque": "El radio se eleva al cuadrado ANTES de multiplicar por $\\pi$; el exponente afecta solo al radio.",
            },
            {
                "accion": "Resto: $40 - 12{,}56 = 27{,}44$ m² de pasto.",
                "porque": "El pasto es lo que queda del rectángulo una vez sacada la fuente. Es una figura compuesta por resta.",
            },
        ],
        "common_error": (
            "Confundir radio con diámetro. Si el enunciado dice «una fuente de 2 "
            "metros de diámetro», el radio es 1 y el área es la cuarta parte de "
            "la calculada acá."
        ),
    },
    "geo_pitagoras": {
        "intro": (
            "En cualquier triángulo rectángulo, conocer dos lados basta para "
            "obtener el tercero. Es la herramienta que aparece en diagonales, "
            "alturas y distancias."
        ),
        "theory": (
            "**El teorema**: en un triángulo rectángulo, "
            "$a^2 + b^2 = c^2$, donde $c$ es la **hipotenusa** —el lado opuesto "
            "al ángulo recto, siempre el más largo— y $a$, $b$ son los "
            "catetos.\n\n"
            "**Solo vale si hay ángulo recto.** En un triángulo cualquiera no se "
            "puede aplicar.\n\n"
            "**Para buscar un cateto** se despeja restando: "
            "$a = \\sqrt{c^2 - b^2}$.\n\n"
            "**Tríos pitagóricos** que conviene reconocer de memoria: "
            "(3, 4, 5), (5, 12, 13), (8, 15, 17) y sus múltiplos, como "
            "(6, 8, 10)."
        ),
        "example_statement": (
            "Una escalera de 13 m se apoya en un muro vertical y su base está a "
            "5 m del muro. ¿A qué altura llega la escalera?"
        ),
        "example_steps": [
            {
                "accion": "Identifico los elementos: la escalera es la hipotenusa ($c = 13$), la distancia al muro es un cateto ($b = 5$) y la altura buscada es el otro cateto.",
                "porque": "El muro es vertical y el suelo horizontal, así que forman el ángulo recto. La escalera, opuesta a él, es la hipotenusa.",
            },
            {
                "accion": "Planteo: $a^2 + 5^2 = 13^2$, es decir $a^2 + 25 = 169$.",
                "porque": "El teorema relaciona los cuadrados de los tres lados, y acá el desconocido es un cateto.",
            },
            {
                "accion": "Despejo: $a^2 = 169 - 25 = 144$, entonces $a = \\sqrt{144} = 12$ m.",
                "porque": "Para buscar un cateto se RESTA, no se suma: la hipotenusa es la mayor y su cuadrado contiene a los otros dos.",
            },
        ],
        "common_error": (
            "Sumar cuando había que restar: dar $\\sqrt{13^2 + 5^2}$ como "
            "respuesta. Eso entrega un lado más largo que la escalera, lo que es "
            "imposible: la hipotenusa siempre es el lado mayor."
        ),
    },
    "geo_transformaciones": {
        "intro": (
            "Trasladar, rotar y reflejar una figura cambia su posición pero no "
            "su forma ni su tamaño. Por eso se llaman isométricas: «misma "
            "medida»."
        ),
        "theory": (
            "**Traslación** según un vector $(a, b)$: cada punto se mueve $a$ "
            "en horizontal y $b$ en vertical. El punto $(x, y)$ llega a "
            "$(x+a,\\; y+b)$.\n\n"
            "**Reflexión (simetría axial)**: respecto del eje $X$, "
            "$(x, y) \\to (x, -y)$; respecto del eje $Y$, "
            "$(x, y) \\to (-x, y)$. Cambia solo la coordenada del eje "
            "perpendicular al espejo.\n\n"
            "**Rotación en 90° antihorario** con centro en el origen: "
            "$(x, y) \\to (-y, x)$. En 180°: $(x, y) \\to (-x, -y)$.\n\n"
            "**Las tres conservan** las longitudes de los lados y la medida de "
            "los ángulos: la figura resultante es congruente con la original."
        ),
        "example_statement": (
            "El punto $P(-3, 4)$ se refleja respecto del eje $Y$ y el resultado "
            "se traslada según el vector $(2, -1)$. ¿Dónde queda?"
        ),
        "example_steps": [
            {
                "accion": "Reflejo respecto del eje $Y$: $(-3, 4)$ pasa a $(3, 4)$.",
                "porque": "El eje $Y$ actúa como espejo vertical, así que cambia el signo de la coordenada horizontal y la vertical se mantiene.",
            },
            {
                "accion": "Traslado ese resultado según $(2, -1)$: $(3+2,\\; 4-1) = (5, 3)$.",
                "porque": "Trasladar es sumar el vector a las coordenadas: 2 a la derecha y 1 hacia abajo.",
            },
            {
                "accion": "El punto final es $(5, 3)$.",
                "porque": "El orden importa: reflejar y después trasladar no da lo mismo que trasladar y después reflejar.",
            },
        ],
        "common_error": (
            "Cambiar la coordenada equivocada al reflejar. Respecto del eje $Y$ "
            "cambia la $x$; respecto del eje $X$ cambia la $y$. Conviene pensar "
            "en cuál eje es el espejo y mover el punto perpendicular a él."
        ),
    },
    "geo_solidos": {
        "intro": (
            "El volumen mide cuánto cabe adentro; el área de superficie, cuánto "
            "papel se necesita para forrarlo. Aparecen en problemas de "
            "capacidad, envases y pintura."
        ),
        "theory": (
            "**Prisma o cubo**: volumen $= $ área de la base $\\times$ altura. "
            "Para el cubo de arista $a$: $V = a^3$ y superficie $= 6a^2$.\n\n"
            "**Cilindro**: $V = \\pi r^2 h$. Su superficie total es "
            "$2\\pi r^2 + 2\\pi r h$: las dos tapas más el manto.\n\n"
            "**Cono**: $V = \\dfrac{\\pi r^2 h}{3}$, un tercio del cilindro de "
            "igual base y altura.\n\n"
            "**Esfera**: $V = \\dfrac{4}{3}\\pi r^3$ y superficie "
            "$= 4\\pi r^2$.\n\n"
            "**Las unidades cambian de exponente**: el área va en unidades "
            "cuadradas y el volumen en cúbicas. Y $1$ litro $= 1000$ cm³."
        ),
        "example_statement": (
            "Un tarro cilíndrico tiene 10 cm de radio y 20 cm de altura. ¿Cuál "
            "es su volumen? (Usa $\\pi \\approx 3{,}14$.)"
        ),
        "example_steps": [
            {
                "accion": "Calculo el área de la base, que es un círculo: $\\pi r^2 = 3{,}14 \\cdot 10^2 = 314$ cm².",
                "porque": "El volumen de un cilindro es la base repetida a lo largo de toda la altura, así que primero hay que saber cuánto mide esa base.",
            },
            {
                "accion": "Multiplico por la altura: $314 \\cdot 20 = 6.280$ cm³.",
                "porque": "Apilar el área de la base 20 cm hacia arriba es exactamente multiplicar por la altura.",
            },
            {
                "accion": "Si el enunciado pidiera litros: $6.280 \\div 1000 = 6{,}28$ litros.",
                "porque": "Un litro equivale a 1000 cm³, y la prueba suele pedir el resultado en la unidad que no viene dada.",
            },
        ],
        "common_error": (
            "Elevar al cuadrado todo el producto en vez de solo el radio, o "
            "usar el diámetro como si fuera radio. En $\\pi r^2 h$ el exponente "
            "afecta únicamente a $r$."
        ),
    },
    "prob_estadistica_desc": {
        "intro": (
            "Media, mediana y moda resumen un conjunto de datos en un solo "
            "número, pero no dicen lo mismo. Elegir cuál mirar es parte de lo "
            "que evalúa la prueba."
        ),
        "theory": (
            "**Media aritmética**: la suma de todos los datos dividida por "
            "cuántos son. Le afectan mucho los valores extremos.\n\n"
            "**Mediana**: el valor del medio con los datos ORDENADOS. Si la "
            "cantidad de datos es par, es el promedio de los dos centrales. No "
            "le afectan los extremos.\n\n"
            "**Moda**: el dato que más se repite. Puede no existir o haber "
            "varias.\n\n"
            "**Rango**: la diferencia entre el mayor y el menor.\n\n"
            "**Cuándo usar cuál**: si hay un dato muy alejado del resto (un "
            "sueldo enorme entre sueldos normales), la mediana representa mejor "
            "al grupo que la media."
        ),
        "example_statement": (
            "Las notas de un estudiante son 4, 5, 5, 6 y 10. Calcula la media y "
            "la mediana, y decide cuál lo representa mejor."
        ),
        "example_steps": [
            {
                "accion": "Media: $\\frac{4+5+5+6+10}{5} = \\frac{30}{5} = 6{,}0$.",
                "porque": "Es la suma de todas las notas repartida en partes iguales entre las cinco evaluaciones.",
            },
            {
                "accion": "Ordeno los datos —ya están— y tomo el central: 4, 5, **5**, 6, 10. La mediana es 5.",
                "porque": "Con cinco datos, el tercero deja dos por debajo y dos por encima. Ordenar primero es obligatorio.",
            },
            {
                "accion": "La media (6,0) es mayor que la mediana (5) porque el 10 la empuja hacia arriba; cuatro de las cinco notas están por debajo de la media.",
                "porque": "Un solo valor extremo arrastra la media pero no mueve la mediana, y por eso acá la mediana representa mejor el desempeño habitual.",
            },
        ],
        "common_error": (
            "Calcular la mediana sin ordenar los datos. En la lista 10, 4, 5, 6, "
            "5 el valor central es 5, no el 5 que aparece tercero en el desorden: "
            "hay que ordenar siempre antes de contar."
        ),
    },
    "prob_combinatoria": {
        "intro": (
            "Contar cuántas opciones hay sin escribirlas todas. Es lo que "
            "permite después calcular probabilidades: casos favorables sobre "
            "casos posibles."
        ),
        "theory": (
            "**Principio multiplicativo**: si una decisión tiene $m$ opciones y "
            "otra independiente tiene $n$, juntas dan $m \\cdot n$ "
            "posibilidades.\n\n"
            "**Permutaciones** (importa el orden, se usan todos): $n! = n \\cdot "
            "(n-1) \\cdots 2 \\cdot 1$.\n\n"
            "**Variaciones** (importa el orden, se eligen $k$ de $n$): "
            "$\\dfrac{n!}{(n-k)!}$.\n\n"
            "**Combinaciones** (NO importa el orden): "
            "$\\binom{n}{k} = \\dfrac{n!}{k!\\,(n-k)!}$.\n\n"
            "**La pregunta que decide todo**: ¿cambia el resultado si altero el "
            "orden? Un podio sí cambia (primero y segundo no son lo mismo); un "
            "comité de dos personas no."
        ),
        "example_statement": (
            "De un grupo de 6 personas se debe elegir un comité de 2, sin "
            "distinguir cargos. ¿De cuántas formas distintas se puede hacer?"
        ),
        "example_steps": [
            {
                "accion": "Me pregunto si importa el orden. Elegir a Ana y Beto es el mismo comité que elegir a Beto y Ana, así que NO importa: es una combinación.",
                "porque": "El enunciado dice «sin distinguir cargos». Si dijera presidente y secretario, el orden sí importaría y el número sería el doble.",
            },
            {
                "accion": "Aplico la fórmula: $\\binom{6}{2} = \\frac{6!}{2!\\,4!}$.",
                "porque": "Son $n = 6$ personas disponibles y $k = 2$ lugares por llenar.",
            },
            {
                "accion": "Simplifico: $\\frac{6 \\cdot 5}{2 \\cdot 1} = \\frac{30}{2} = 15$.",
                "porque": "El $4!$ del denominador cancela la parte baja del $6!$, así que basta multiplicar los dos primeros factores y dividir por $2!$.",
            },
        ],
        "common_error": (
            "Usar variaciones donde correspondían combinaciones y responder 30. "
            "Ese número cuenta dos veces cada comité, una por cada orden posible "
            "de las mismas dos personas."
        ),
    },
    "prob_reglas": {
        "intro": (
            "La probabilidad mide qué tan posible es algo, en una escala de 0 a "
            "1. Con dos o tres reglas se resuelve la mayoría de las preguntas de "
            "la prueba."
        ),
        "theory": (
            "**Definición clásica**: $P(A) = \\dfrac{\\text{casos "
            "favorables}}{\\text{casos posibles}}$, cuando todos los casos son "
            "igualmente probables. Siempre está entre 0 y 1.\n\n"
            "**Complemento**: $P(\\text{no } A) = 1 - P(A)$. Es el atajo para "
            "cualquier pregunta que diga «al menos uno».\n\n"
            "**Unión**: $P(A \\text{ o } B) = P(A) + P(B) - P(A \\text{ y } B)$. "
            "Se resta la intersección para no contarla dos veces.\n\n"
            "**Eventos independientes** (uno no afecta al otro): "
            "$P(A \\text{ y } B) = P(A) \\cdot P(B)$.\n\n"
            "**Con o sin reposición**: si el objeto extraído no se devuelve, el "
            "total cambia para la segunda extracción y los eventos dejan de ser "
            "independientes."
        ),
        "example_statement": (
            "Una bolsa tiene 5 bolitas rojas y 3 azules. Se sacan dos sin "
            "reposición. ¿Cuál es la probabilidad de que ambas sean rojas?"
        ),
        "example_steps": [
            {
                "accion": "Primera extracción: hay 5 rojas entre 8 bolitas, así que $P = \\frac{5}{8}$.",
                "porque": "Todas las bolitas tienen la misma posibilidad de salir, así que es casos favorables sobre casos totales.",
            },
            {
                "accion": "Segunda extracción, suponiendo que la primera fue roja: quedan 4 rojas entre 7 bolitas, $P = \\frac{4}{7}$.",
                "porque": "«Sin reposición» significa que la bolita no vuelve: cambian tanto las rojas disponibles como el total.",
            },
            {
                "accion": "Multiplico las dos: $\\frac{5}{8} \\cdot \\frac{4}{7} = \\frac{20}{56} = \\frac{5}{14}$.",
                "porque": "Para que ocurran los dos sucesos encadenados se multiplica la probabilidad del primero por la del segundo dado que ocurrió el primero.",
            },
        ],
        "common_error": (
            "Usar $\\frac{5}{8}$ dos veces y responder $\\frac{25}{64}$. Eso "
            "sería correcto CON reposición; sin reposición el segundo cálculo "
            "parte de una bolsa distinta."
        ),
    },
}
