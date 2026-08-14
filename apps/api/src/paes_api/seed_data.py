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
    # ==================================================================
    # LOTE 4 — eje NÚMEROS (36 preguntas: 6 por nodo)
    # Originales, escritas sobre el temario DEMRE. Ningún enunciado
    # proviene de ítems liberados ni de otros sitios de ensayos.
    # ==================================================================
    # ---------- num_racionales ----------
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 5/8 − 1/6?",
        "11/24",
        "Para restar fracciones ambas deben tener el mismo denominador.\n\n"
        "1) Busca el mínimo común múltiplo de 8 y 6. Los múltiplos de 8 son 8, 16, 24… "
        "y los de 6 son 6, 12, 18, 24… El primero que comparten es 24.\n"
        "2) Lleva cada fracción a veinticuatroavos. Como 24 ÷ 8 = 3, multiplicas arriba "
        "y abajo por 3: 5/8 = 15/24. Como 24 ÷ 6 = 4, multiplicas por 4: 1/6 = 4/24.\n"
        "3) Con los denominadores iguales, restas solo los numeradores: "
        "15/24 − 4/24 = 11/24.\n"
        "4) Comprueba si se simplifica: 11 es primo y no divide a 24, así que 11/24 ya "
        "está en su forma mínima.",
        [
            ("4/2", "Restó numeradores entre sí y denominadores entre sí, sin buscar un denominador común."),
            ("19/24", "Igualó bien los denominadores pero sumó en lugar de restar."),
            ("5/48", "Multiplicó las fracciones en lugar de restarlas."),
        ],
    ),
    _q(
        "num_racionales", "facil",
        "En una jarra hay 7/8 de litro de jugo y se sirven 1/4 de litro. ¿Cuánto jugo queda en la jarra?",
        "5/8 de litro",
        "Servir es quitar, así que la operación es una resta de fracciones.\n\n"
        "1) Plantea la resta: 7/8 − 1/4.\n"
        "2) Iguala los denominadores. Como 8 es múltiplo de 4, basta llevar 1/4 a "
        "octavos: multiplicas arriba y abajo por 2 y queda 2/8.\n"
        "3) Resta los numeradores manteniendo el denominador: 7/8 − 2/8 = 5/8.\n"
        "4) Contrasta con el sentido común: quedaba casi un litro y se sirvió un cuarto, "
        "así que el resultado debe estar algo por encima de medio litro. 5/8 = 0,625 lo cumple.",
        [
            ("6/8 de litro", "Restó 1 al numerador sin llevar antes las fracciones a un denominador común."),
            ("9/8 de litro", "Sumó en lugar de restar, obteniendo más jugo del que había al principio."),
            ("7/32 de litro", "Multiplicó las dos fracciones en vez de restarlas."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de (3/4) ÷ (9/8)?",
        "2/3",
        "Dividir por una fracción equivale a multiplicar por su recíproco: la misma "
        "fracción dada vuelta.\n\n"
        "1) El divisor es 9/8, así que su recíproco es 8/9. La división se transforma en "
        "3/4 × 8/9.\n"
        "2) Multiplica numeradores entre sí y denominadores entre sí: "
        "(3 × 8)/(4 × 9) = 24/36.\n"
        "3) Simplifica dividiendo ambos términos por 12: 24 ÷ 12 = 2 y 36 ÷ 12 = 3, "
        "o sea 2/3.\n\n"
        "Control rápido: 9/8 es mayor que 1, así que dividir por él tiene que achicar "
        "el 3/4 original. Y 2/3 es menor que 3/4.",
        [
            ("27/32", "Multiplicó las fracciones directamente, sin invertir el divisor."),
            ("3/2", "Invirtió el dividendo en lugar del divisor al aplicar la regla del recíproco."),
            ("15/8", "Sumó las fracciones en lugar de dividirlas."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "Un ciclista recorre 2/5 de una ruta el primer día y 1/3 del total el segundo. ¿Qué fracción de la ruta le queda por recorrer?",
        "4/15",
        "La ruta completa es 1. Lo que queda es el total menos lo ya recorrido.\n\n"
        "1) Suma lo recorrido: 2/5 + 1/3. El mínimo común múltiplo de 5 y 3 es 15, "
        "así que 2/5 = 6/15 y 1/3 = 5/15.\n"
        "2) 6/15 + 5/15 = 11/15 de la ruta recorrida.\n"
        "3) Resta ese avance del total: 1 − 11/15. Escribe el 1 como 15/15 para poder "
        "restar: 15/15 − 11/15 = 4/15.\n"
        "4) Verifica: 11/15 recorrido más 4/15 restante suman 15/15, es decir la ruta "
        "completa.",
        [
            ("11/15", "Calculó correctamente lo recorrido, pero eso no es lo que se pregunta: falta restarlo del total."),
            ("3/8", "Sumó numeradores entre sí y denominadores entre sí al juntar los dos días."),
            ("2/15", "Multiplicó las dos fracciones en lugar de sumarlas y restarlas del total."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "Si x = 3/8 y y = 5/6, ¿cuál es el valor de (y − x) ÷ (y + x)?",
        "11/29",
        "Conviene resolver por separado el numerador y el denominador antes de dividir.\n\n"
        "1) Iguala denominadores: el mínimo común múltiplo de 8 y 6 es 24, así que "
        "x = 9/24 e y = 20/24.\n"
        "2) Diferencia: y − x = 20/24 − 9/24 = 11/24.\n"
        "3) Suma: y + x = 20/24 + 9/24 = 29/24.\n"
        "4) Divide: (11/24) ÷ (29/24) = 11/24 × 24/29. Los 24 se cancelan y queda 11/29.\n\n"
        "Control: la diferencia es bastante menor que la suma, así que el cociente debe "
        "ser un número pequeño, menor que 1.",
        [
            ("29/11", "Dividió la suma por la diferencia, invirtiendo el orden que pide el enunciado."),
            ("11/24", "Calculó solo la diferencia y no la dividió por la suma."),
            ("29/24", "Calculó solo la suma y la entregó como resultado final."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "¿Cuál es el resultado de (5/6 − 1/2) × (3/4 + 1/2)?",
        "5/12",
        "Primero se resuelve cada paréntesis y recién después se multiplica.\n\n"
        "1) Primer paréntesis: 5/6 − 1/2. Con denominador 6 queda 5/6 − 3/6 = 2/6, "
        "que se simplifica a 1/3.\n"
        "2) Segundo paréntesis: 3/4 + 1/2. Con denominador 4 queda 3/4 + 2/4 = 5/4.\n"
        "3) Multiplica los dos resultados: 1/3 × 5/4 = (1 × 5)/(3 × 4) = 5/12.\n"
        "4) Comprueba que no se simplifique: 5 es primo y no divide a 12.",
        [
            ("19/12", "Sumó los dos paréntesis en lugar de multiplicarlos."),
            ("4/15", "Invirtió el segundo paréntesis y terminó dividiendo en vez de multiplicar."),
            ("1/3", "Resolvió solo el primer paréntesis y olvidó multiplicarlo por el segundo."),
        ],
    ),
    # ---------- num_potencias_raices ----------
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de 3² · 3³?",
        "243",
        "Al multiplicar potencias de igual base, la base se mantiene y los exponentes "
        "se suman.\n\n"
        "1) Ambos factores tienen base 3, así que aplicas la regla: 3² · 3³ = 3^(2+3) = 3⁵.\n"
        "2) Calcula 3⁵ multiplicando cinco veces el 3: 3 · 3 = 9, 9 · 3 = 27, "
        "27 · 3 = 81, 81 · 3 = 243.\n"
        "3) Verificación directa: 3² = 9 y 3³ = 27, y 9 · 27 = 243. Coincide.",
        [
            ("729", "Multiplicó los exponentes en lugar de sumarlos, calculando 3⁶."),
            ("36", "Sumó las potencias en vez de multiplicarlas: 9 + 27."),
            ("59.049", "Multiplicó también las bases, calculando 9⁵ en lugar de 3⁵."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de √169 + √36?",
        "19",
        "Cada raíz se calcula por separado y después se suman los resultados.\n\n"
        "1) √169: busca el número que multiplicado por sí mismo da 169. Como "
        "13 · 13 = 169, la raíz es 13.\n"
        "2) √36: como 6 · 6 = 36, la raíz es 6.\n"
        "3) Suma: 13 + 6 = 19.\n\n"
        "Importante: la raíz de una suma no es la suma de las raíces. Aquí se suman dos "
        "raíces ya calculadas, que es distinto de √(169 + 36).",
        [
            ("14,3", "Sumó primero los números dentro de las raíces y calculó √205."),
            ("78", "Multiplicó las raíces en lugar de sumarlas."),
            ("7", "Restó las raíces en lugar de sumarlas."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de (5⁴ · 5²) ÷ 5³?",
        "125",
        "Se aplican dos reglas seguidas, ambas sobre la misma base.\n\n"
        "1) En el numerador se multiplican potencias de igual base, así que los "
        "exponentes se suman: 5⁴ · 5² = 5⁶.\n"
        "2) Al dividir potencias de igual base, los exponentes se restan: "
        "5⁶ ÷ 5³ = 5^(6−3) = 5³.\n"
        "3) Calcula 5³ = 5 · 5 · 5 = 125.\n"
        "4) Atajo útil: podías operar todos los exponentes de una vez, 4 + 2 − 3 = 3, "
        "y llegar directo a 5³.",
        [
            ("15.625", "Sumó bien los exponentes del numerador pero olvidó restar el del divisor, quedándose en 5⁶."),
            ("25", "Restó los exponentes del numerador en lugar de sumarlos."),
            ("3.125", "Multiplicó los exponentes del numerador en vez de sumarlos, llegando a 5⁵."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de 3⁻³?",
        "1/27",
        "Un exponente negativo no vuelve negativo el resultado: indica que hay que "
        "invertir la base.\n\n"
        "1) La regla es a⁻ⁿ = 1/aⁿ. Aplicada aquí: 3⁻³ = 1/3³.\n"
        "2) Calcula el denominador: 3³ = 3 · 3 · 3 = 27.\n"
        "3) El resultado es 1/27.\n\n"
        "Fíjate en el sentido: elevar a un exponente negativo produce un número más "
        "chico que 1, pero siempre positivo si la base es positiva.",
        [
            ("−27", "Interpretó el signo del exponente como el signo del resultado."),
            ("27", "Ignoró el signo negativo del exponente y calculó 3³."),
            ("1/9", "Invirtió bien la base pero se equivocó de exponente, calculando 1/3²."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "Si 3ˣ = 81, ¿cuál es el valor de x?",
        "4",
        "La pregunta es: ¿cuántas veces hay que multiplicar el 3 por sí mismo para "
        "llegar a 81?\n\n"
        "1) Descompón el 81 en factores de 3: 81 = 3 · 27, 27 = 3 · 9 y 9 = 3 · 3.\n"
        "2) Reuniendo todo: 81 = 3 · 3 · 3 · 3, es decir cuatro factores.\n"
        "3) Por lo tanto 81 = 3⁴, y como las bases coinciden, los exponentes también: "
        "x = 4.\n"
        "4) Verifica reemplazando: 3⁴ = 81. Correcto.",
        [
            ("27", "Dividió 81 por 3 en lugar de buscar el exponente."),
            ("9", "Calculó la raíz cuadrada de 81, que responde otra pregunta."),
            ("5", "Contó una multiplicación de más: 3⁵ da 243, no 81."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "¿Cuál es el valor de √(3² + 4²) · √49?",
        "35",
        "Hay que resolver primero lo que está dentro de cada raíz.\n\n"
        "1) Dentro de la primera raíz: 3² + 4² = 9 + 16 = 25. Esa raíz vale √25 = 5.\n"
        "2) La segunda raíz: √49 = 7.\n"
        "3) Multiplica los dos resultados: 5 · 7 = 35.\n\n"
        "Ojo con el error clásico: √(3² + 4²) no es 3 + 4. Primero se suman los "
        "cuadrados y recién entonces se saca la raíz.",
        [
            ("49", "Calculó la primera raíz como 3 + 4 = 7 y lo multiplicó por 7."),
            ("5", "Resolvió bien la primera raíz pero olvidó multiplicarla por la segunda."),
            ("175", "No extrajo la primera raíz y multiplicó 25 por 7."),
        ],
    ),
    # ---------- num_porcentajes ----------
    _q(
        "num_porcentajes", "facil",
        "¿Cuánto es el 35% de 480?",
        "168",
        "Un porcentaje es una fracción de cada 100.\n\n"
        "1) Convierte el porcentaje a decimal dividiendo por 100: 35% = 0,35.\n"
        "2) Multiplica por la cantidad: 0,35 · 480 = 168.\n"
        "3) Otra vía, útil para calcular mentalmente: el 10% de 480 es 48, así que el "
        "30% es 144. El 5% es la mitad del 10%, o sea 24. Sumando: 144 + 24 = 168.\n"
        "4) Control: el resultado debe estar entre el 25% (120) y la mitad (240).",
        [
            ("16.800", "Multiplicó por 35 pero olvidó dividir por 100."),
            ("312", "Calculó el 65% restante en lugar del 35% pedido."),
            ("144", "Usó un 30% en lugar del 35% del enunciado."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "Un artículo cuesta $24.000 y sube un 15%. ¿Cuál es el nuevo precio?",
        "$27.600",
        "Subir un 15% significa quedarse con el 100% original más un 15% extra.\n\n"
        "1) Calcula el aumento: el 10% de 24.000 es 2.400 y el 5% es la mitad, 1.200. "
        "El 15% es 2.400 + 1.200 = 3.600.\n"
        "2) Suma el aumento al precio original: 24.000 + 3.600 = 27.600.\n"
        "3) Camino directo: como el precio final es el 115% del original, basta "
        "multiplicar 24.000 · 1,15 = 27.600.\n"
        "4) Control: el precio tiene que ser mayor que el original pero no llegar a "
        "una vez y media.",
        [
            ("$20.400", "Aplicó un descuento del 15% en lugar de un alza."),
            ("$3.600", "Calculó correctamente el aumento, pero no lo sumó al precio original."),
            ("$39.000", "Sumó 15.000 pesos en vez del 15% del precio."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "En un curso de 45 estudiantes, 27 aprobaron una prueba. ¿Qué porcentaje del curso aprobó?",
        "60%",
        "Un porcentaje se obtiene comparando la parte con el total.\n\n"
        "1) Escribe la razón entre la parte y el total: 27/45.\n"
        "2) Simplifica dividiendo ambos por 9: 27 ÷ 9 = 3 y 45 ÷ 9 = 5, o sea 3/5.\n"
        "3) Lleva la fracción a porcentaje multiplicando por 100: 3/5 · 100 = 60. "
        "El resultado es 60%.\n"
        "4) Control: 27 es algo más de la mitad de 45, así que el porcentaje debe "
        "superar el 50%.",
        [
            ("40%", "Calculó el porcentaje de quienes no aprobaron."),
            ("27%", "Tomó la cantidad de aprobados como si ya fuera un porcentaje."),
            ("166,7%", "Dividió el total por la parte en lugar de la parte por el total."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "Un producto de $50.000 tiene dos descuentos sucesivos: 20% y luego 10% sobre el precio ya rebajado. ¿Cuál es el precio final?",
        "$36.000",
        "Los descuentos sucesivos no se suman: el segundo se aplica sobre un precio "
        "que ya bajó.\n\n"
        "1) Primer descuento: el 20% de 50.000 es 10.000, así que el precio pasa a "
        "40.000.\n"
        "2) Segundo descuento: el 10% se calcula sobre 40.000, no sobre 50.000. "
        "El 10% de 40.000 es 4.000.\n"
        "3) Precio final: 40.000 − 4.000 = 36.000.\n"
        "4) Camino directo: 50.000 · 0,8 · 0,9 = 36.000. Equivale a un único descuento "
        "del 28%, no del 30%.",
        [
            ("$35.000", "Sumó los descuentos y aplicó un 30% de una sola vez."),
            ("$40.000", "Aplicó solo el primer descuento y olvidó el segundo."),
            ("$45.000", "Aplicó solo el descuento del 10%."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Doce operarios pintan un muro en 10 días. ¿Cuántos días tardarían 8 operarios trabajando al mismo ritmo?",
        "15 días",
        "Esta es una proporcionalidad inversa: menos trabajadores implica más días.\n\n"
        "1) Calcula el trabajo total en días-operario: 12 operarios · 10 días = "
        "120 días-operario. Esa cantidad no cambia.\n"
        "2) Reparte ese mismo trabajo entre 8 operarios: 120 ÷ 8 = 15.\n"
        "3) La respuesta es 15 días.\n"
        "4) Control de sentido: al bajar de 12 a 8 operarios el plazo tiene que "
        "alargarse, nunca acortarse.",
        [
            ("6,7 días", "Aplicó proporcionalidad directa, como si menos operarios significara menos días."),
            ("14 días", "Sumó a los 10 días los 4 operarios que faltan, mezclando unidades distintas."),
            ("30 días", "Repartió el trabajo entre 4 operarios en lugar de entre 8."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "El precio de un artículo sube un 60% y luego baja un 25% sobre el nuevo precio. Respecto del precio inicial, ¿qué ocurre?",
        "Sube un 20%",
        "Conviene trabajar con un precio inicial cómodo, por ejemplo 100.\n\n"
        "1) Alza del 60%: el precio pasa de 100 a 160.\n"
        "2) Baja del 25%, pero calculada sobre 160, no sobre 100: el 25% de 160 es 40.\n"
        "3) Precio final: 160 − 40 = 120.\n"
        "4) Comparando con el inicial: de 100 a 120 hay un alza del 20%.\n\n"
        "El punto clave es que la baja se aplica sobre una base mayor, así que los "
        "porcentajes no se pueden restar directamente.",
        [
            ("Sube un 35%", "Restó los porcentajes o aplicó la baja del 25% sobre el precio inicial en lugar del aumentado."),
            ("Sube un 45%", "Descontó un 25% del aumento (15 puntos) en vez de un 25% del precio nuevo."),
            ("Queda igual que el precio inicial", "Supuso que un alza y una baja consecutivas siempre se anulan entre sí."),
        ],
    ),
    # ---------- num_reales ----------
    _q(
        "num_reales", "facil",
        "¿Cuál es el valor de √75 en su forma más simple?",
        "5√3",
        "Simplificar una raíz consiste en extraer los factores que sean cuadrados "
        "perfectos.\n\n"
        "1) Descompón 75 buscando un cuadrado perfecto entre sus factores: "
        "75 = 25 · 3, y 25 es cuadrado perfecto.\n"
        "2) Separa la raíz del producto: √75 = √25 · √3.\n"
        "3) Extrae la que se puede: √25 = 5, así que queda 5√3.\n"
        "4) Verifica de vuelta: (5√3)² = 25 · 3 = 75. Correcto.",
        [
            ("25√3", "Sacó el 25 de la raíz sin calcular su raíz cuadrada."),
            ("3√5", "Intercambió los papeles: extrajo el 3 y dejó el 5 dentro de la raíz."),
            ("15", "Multiplicó 5 por 3 como si la raíz hubiera desaparecido por completo."),
        ],
    ),
    _q(
        "num_reales", "facil",
        "¿Entre qué dos enteros consecutivos se encuentra √58?",
        "Entre 7 y 8",
        "Se acota la raíz entre los dos cuadrados perfectos más cercanos.\n\n"
        "1) Busca el cuadrado perfecto justo por debajo de 58: 7² = 49.\n"
        "2) Busca el que está justo por encima: 8² = 64.\n"
        "3) Como 49 < 58 < 64, al sacar raíz se mantiene el orden: 7 < √58 < 8.\n"
        "4) De hecho 58 está más cerca de 64 que de 49, así que √58 vale "
        "aproximadamente 7,6.",
        [
            ("Entre 6 y 7", "Usó cuadrados demasiado bajos: 7² ya es 49, menor que 58."),
            ("Entre 8 y 9", "Usó cuadrados demasiado altos: 8² es 64, que ya supera a 58."),
            ("Entre 28 y 29", "Dividió 58 por 2 en lugar de buscar su raíz cuadrada."),
        ],
    ),
    _q(
        "num_reales", "medio",
        "¿Cuál es el resultado de (√5 + √5)²?",
        "20",
        "Primero se simplifica lo que está dentro del paréntesis.\n\n"
        "1) √5 + √5 son dos términos semejantes, igual que x + x = 2x. Entonces la suma "
        "es 2√5.\n"
        "2) Ahora eleva al cuadrado: (2√5)² = 2² · (√5)².\n"
        "3) Calcula cada parte: 2² = 4 y (√5)² = 5.\n"
        "4) Multiplica: 4 · 5 = 20.",
        [
            ("10", "Elevó al cuadrado cada sumando por separado (5 + 5) y olvidó el doble producto."),
            ("2√5", "Simplificó bien la suma pero no llegó a elevarla al cuadrado."),
            ("100", "Sumó los radicandos obteniendo 10 y después elevó ese resultado al cuadrado."),
        ],
    ),
    _q(
        "num_reales", "medio",
        "Si a = √12 y b = √27, ¿cuál es el valor de a + b?",
        "5√3",
        "Dos raíces solo se pueden sumar si tienen el mismo radicando, así que primero "
        "hay que simplificarlas.\n\n"
        "1) Simplifica la primera: 12 = 4 · 3, entonces √12 = √4 · √3 = 2√3.\n"
        "2) Simplifica la segunda: 27 = 9 · 3, entonces √27 = √9 · √3 = 3√3.\n"
        "3) Ahora ambas comparten el radicando 3, así que se suman los coeficientes: "
        "2√3 + 3√3 = 5√3.\n"
        "4) Aproximación de control: √3 ≈ 1,73, así que el resultado ronda 8,66. "
        "Y √12 ≈ 3,46 más √27 ≈ 5,20 dan lo mismo.",
        [
            ("√39", "Sumó los radicandos: √(12 + 27), que no es una operación válida."),
            ("6√3", "Multiplicó los coeficientes en lugar de sumarlos."),
            ("No se pueden sumar porque tienen distinto radicando", "No simplificó las raíces antes de compararlas; una vez simplificadas ambas quedan con radicando 3."),
        ],
    ),
    _q(
        "num_reales", "dificil",
        "¿Cuál es el resultado de racionalizar 10/√5?",
        "2√5",
        "Racionalizar es eliminar la raíz del denominador sin alterar el valor.\n\n"
        "1) Multiplica numerador y denominador por √5. Como equivale a multiplicar por "
        "1, el valor no cambia: (10 · √5)/(√5 · √5).\n"
        "2) El denominador se vuelve entero: √5 · √5 = 5.\n"
        "3) Queda 10√5/5.\n"
        "4) Simplifica el coeficiente: 10 ÷ 5 = 2, así que el resultado es 2√5.",
        [
            ("10√5", "Multiplicó arriba y abajo por √5 pero no simplificó el 10 con el 5 del denominador."),
            ("2/√5", "Simplificó el coeficiente pero dejó la raíz en el denominador, que es justo lo que había que eliminar."),
            ("5√2", "Intercambió el coeficiente con el radicando al simplificar."),
        ],
    ),
    _q(
        "num_reales", "dificil",
        "¿Cuál es el valor de |−9| − |4 − 11|?",
        "2",
        "El valor absoluto entrega siempre la distancia al cero, es decir un número "
        "no negativo.\n\n"
        "1) Primer módulo: |−9| = 9.\n"
        "2) Segundo módulo: resuelve primero lo de adentro, 4 − 11 = −7. Entonces "
        "|−7| = 7.\n"
        "3) Ahora sí resta los dos resultados: 9 − 7 = 2.\n\n"
        "El orden importa: el valor absoluto se aplica a lo que quedó dentro de las "
        "barras, no a cada número por separado.",
        [
            ("16", "Sumó los dos valores absolutos en lugar de restarlos."),
            ("−16", "No aplicó el valor absoluto y operó directamente con −9 y −7."),
            ("12", "Calculó bien el interior pero mantuvo el signo negativo del segundo módulo, restando un número negativo."),
        ],
    ),
    # ---------- num_financiera ----------
    _q(
        "num_financiera", "facil",
        "Se depositan $300.000 al 4% de interés simple anual. ¿Cuánto interés se genera en 3 años?",
        "$36.000",
        "En el interés simple, los intereses se calculan siempre sobre el capital "
        "inicial, que nunca cambia.\n\n"
        "1) Calcula el interés de un año: el 4% de 300.000 es 0,04 · 300.000 = 12.000.\n"
        "2) Como el capital base no varía, cada año genera lo mismo.\n"
        "3) Multiplica por los 3 años: 12.000 · 3 = 36.000.\n"
        "4) En fórmula: I = C · i · t = 300.000 · 0,04 · 3 = 36.000.",
        [
            ("$12.000", "Calculó el interés de un solo año y no lo multiplicó por los 3."),
            ("$336.000", "Entregó el monto final acumulado en lugar del interés generado."),
            ("$37.459", "Aplicó interés compuesto, que capitaliza los intereses año a año, en vez de interés simple."),
        ],
    ),
    _q(
        "num_financiera", "facil",
        "Un capital de $500.000 se invierte al 6% de interés simple anual. ¿Cuál es el monto acumulado al cabo de 2 años?",
        "$560.000",
        "El monto acumulado es el capital inicial más todos los intereses ganados.\n\n"
        "1) Interés de un año: el 6% de 500.000 es 30.000.\n"
        "2) Interés de dos años, con interés simple: 30.000 · 2 = 60.000.\n"
        "3) Monto acumulado: 500.000 + 60.000 = 560.000.\n"
        "4) Distingue bien los dos conceptos: el interés ganado fue 60.000; el monto es "
        "el total que hay al final, 560.000.",
        [
            ("$530.000", "Consideró un solo año de intereses en lugar de dos."),
            ("$60.000", "Entregó únicamente el interés ganado, sin sumarle el capital inicial."),
            ("$561.800", "Aplicó interés compuesto en lugar del interés simple que indica el enunciado."),
        ],
    ),
    _q(
        "num_financiera", "medio",
        "Un capital de $120.000 se invierte al 5% compuesto anual durante 2 años. ¿Cuál es el monto final?",
        "$132.300",
        "En el interés compuesto, los intereses de cada período se suman al capital y "
        "pasan a generar intereses ellos mismos.\n\n"
        "1) Primer año: el 5% de 120.000 es 6.000. El capital pasa a 126.000.\n"
        "2) Segundo año: el 5% se calcula ahora sobre 126.000, no sobre 120.000. "
        "El 5% de 126.000 es 6.300.\n"
        "3) Monto final: 126.000 + 6.300 = 132.300.\n"
        "4) En fórmula: M = C · (1 + i)ᵗ = 120.000 · 1,05² = 132.300.",
        [
            ("$132.000", "Aplicó interés simple: 6.000 por cada año, sin capitalizar el primero."),
            ("$126.000", "Calculó solo el primer año de capitalización."),
            ("$12.300", "Entregó únicamente los intereses ganados, sin sumar el capital."),
        ],
    ),
    _q(
        "num_financiera", "medio",
        "¿Cuál es la diferencia entre el interés compuesto y el interés simple para un capital de $80.000 al 5% anual en 2 años?",
        "$200",
        "Hay que calcular ambos intereses por separado y compararlos.\n\n"
        "1) Interés simple: el 5% de 80.000 es 4.000 por año, y en 2 años son 8.000.\n"
        "2) Interés compuesto: el primer año genera 4.000 y el capital pasa a 84.000. "
        "El segundo año el 5% se calcula sobre 84.000, dando 4.200.\n"
        "3) Interés compuesto total: 4.000 + 4.200 = 8.200.\n"
        "4) Diferencia: 8.200 − 8.000 = 200. Ese monto es exactamente el 5% de los "
        "4.000 del primer año, es decir el interés que generaron los intereses.",
        [
            ("$0", "Supuso que ambos sistemas rinden lo mismo; se diferencian desde el segundo período."),
            ("$8.200", "Entregó el interés compuesto total en lugar de la diferencia entre ambos."),
            ("$8.000", "Entregó el interés simple total en lugar de la diferencia."),
        ],
    ),
    _q(
        "num_financiera", "dificil",
        "Una deuda de $1.200.000 se paga en 12 cuotas iguales sin interés. Si ya se pagaron 5 cuotas, ¿cuánto falta por pagar?",
        "$700.000",
        "Como no hay interés, la deuda se reparte en partes iguales.\n\n"
        "1) Calcula el valor de cada cuota: 1.200.000 ÷ 12 = 100.000.\n"
        "2) Cuenta las cuotas que faltan: 12 − 5 = 7.\n"
        "3) Multiplica: 7 · 100.000 = 700.000.\n"
        "4) Verificación: lo pagado son 5 · 100.000 = 500.000, y 500.000 + 700.000 "
        "devuelve la deuda original.",
        [
            ("$500.000", "Calculó lo que ya se pagó en lugar de lo que falta."),
            ("$100.000", "Entregó el valor de una sola cuota."),
            ("$600.000", "Dividió la deuda por la mitad, sin considerar cuántas cuotas se pagaron realmente."),
        ],
    ),
    _q(
        "num_financiera", "dificil",
        "Un artículo cuesta $45.000 al contado o en 3 cuotas de $16.500. ¿Qué porcentaje de recargo tiene la compra a crédito?",
        "10%",
        "El recargo se mide comparando cuánto más se paga respecto del precio al "
        "contado.\n\n"
        "1) Calcula el total a crédito: 3 · 16.500 = 49.500.\n"
        "2) Obtén el recargo en pesos: 49.500 − 45.000 = 4.500.\n"
        "3) Exprésalo como porcentaje del precio al contado, que es la referencia: "
        "4.500 / 45.000 = 0,1.\n"
        "4) Multiplicando por 100 queda 10%.",
        [
            ("$4.500", "Calculó bien el recargo en pesos, pero la pregunta pide el porcentaje."),
            ("9,1%", "Dividió el recargo por el precio a crédito en lugar del precio al contado."),
            ("36,7%", "Comparó el valor de una cuota con el precio al contado."),
        ],
    ),
    # ---------- num_logaritmos ----------
    _q(
        "num_logaritmos", "facil",
        "¿Cuál es el valor de log₂ 64?",
        "6",
        "Un logaritmo responde a la pregunta: ¿a qué exponente hay que elevar la base "
        "para obtener ese número?\n\n"
        "1) Aquí la base es 2 y el número es 64, así que buscas el x tal que 2ˣ = 64.\n"
        "2) Ve multiplicando por 2: 2, 4, 8, 16, 32, 64. Son seis pasos.\n"
        "3) Entonces 2⁶ = 64 y por lo tanto log₂ 64 = 6.",
        [
            ("32", "Dividió 64 por 2 en lugar de buscar el exponente."),
            ("8", "Calculó la raíz cuadrada de 64, que responde otra pregunta."),
            ("5", "Contó una multiplicación de menos: 2⁵ da 32, no 64."),
        ],
    ),
    _q(
        "num_logaritmos", "facil",
        "¿Cuál es el valor de log 10.000, en base 10?",
        "4",
        "Cuando no se escribe la base, se asume que es 10.\n\n"
        "1) Buscas el exponente x tal que 10ˣ = 10.000.\n"
        "2) Cuenta los ceros: 10.000 tiene cuatro ceros, y cada cero corresponde a un "
        "factor 10. Entonces 10.000 = 10⁴.\n"
        "3) Por lo tanto log 10.000 = 4.\n\n"
        "Regla práctica: en base 10, el logaritmo de una potencia de diez es "
        "simplemente su cantidad de ceros.",
        [
            ("10.000", "Repitió el número en vez de calcular el exponente."),
            ("1.000", "Dividió por 10 en lugar de buscar el exponente."),
            ("5", "Contó los dígitos del número (que son cinco) en lugar de los ceros."),
        ],
    ),
    _q(
        "num_logaritmos", "medio",
        "Si log x = 2 en base 10, ¿cuál es el valor de x?",
        "100",
        "Aquí el logaritmo es el dato y la incógnita es el número.\n\n"
        "1) Traduce la expresión a su forma exponencial: log x = 2 en base 10 significa "
        "10² = x.\n"
        "2) Calcula: 10² = 100.\n"
        "3) Entonces x = 100.\n"
        "4) Verifica en sentido contrario: el logaritmo en base 10 de 100 es 2, porque "
        "100 tiene dos ceros.",
        [
            ("20", "Multiplicó la base por el exponente en lugar de elevar."),
            ("10", "Confundió la base con el resultado buscado."),
            ("1.000", "Usó un exponente 3 en lugar del 2 que da el enunciado."),
        ],
    ),
    _q(
        "num_logaritmos", "medio",
        "¿Cuál es el valor de log₃ 9 + log₂ 8?",
        "5",
        "Cada logaritmo se resuelve por separado porque tienen bases distintas.\n\n"
        "1) log₃ 9: buscas el exponente tal que 3ˣ = 9. Como 3² = 9, vale 2.\n"
        "2) log₂ 8: buscas el exponente tal que 2ˣ = 8. Como 2³ = 8, vale 3.\n"
        "3) Suma los dos resultados: 2 + 3 = 5.\n\n"
        "Cuidado: la propiedad que convierte una suma de logaritmos en el logaritmo de "
        "un producto solo se aplica cuando ambos comparten la misma base, y aquí no "
        "es el caso.",
        [
            ("6", "Multiplicó los dos resultados en lugar de sumarlos."),
            ("17", "Sumó los argumentos (9 + 8) en vez de los logaritmos."),
            ("72", "Aplicó la propiedad del producto pese a que las bases son distintas, multiplicando 9 por 8."),
        ],
    ),
    _q(
        "num_logaritmos", "dificil",
        "Si log 2 ≈ 0,301, ¿cuál es el valor aproximado de log 8?",
        "0,903",
        "La clave es escribir el 8 como una potencia de 2 para poder usar el dato.\n\n"
        "1) Descompón: 8 = 2³.\n"
        "2) Aplica la propiedad del exponente, que lo baja multiplicando: "
        "log 8 = log 2³ = 3 · log 2.\n"
        "3) Reemplaza el dato: 3 · 0,301 = 0,903.\n"
        "4) Control: 8 está entre 1 y 10, así que su logaritmo en base 10 debe caer "
        "entre 0 y 1.",
        [
            ("2,408", "Multiplicó por 8 en lugar de por el exponente 3."),
            ("0,602", "Usó exponente 2, como si 8 fuera 2²."),
            ("1,204", "Usó exponente 4, como si 8 fuera 2⁴."),
        ],
    ),
    _q(
        "num_logaritmos", "dificil",
        "¿Cuál es el valor de log₂ 128 − log₂ 8?",
        "4",
        "Se pueden resolver los dos logaritmos por separado, o usar la propiedad del "
        "cociente. Ambos caminos llegan a lo mismo.\n\n"
        "1) Primer logaritmo: 2⁷ = 128, así que log₂ 128 = 7.\n"
        "2) Segundo logaritmo: 2³ = 8, así que log₂ 8 = 3.\n"
        "3) Resta: 7 − 3 = 4.\n"
        "4) Camino alternativo: como las bases coinciden, la resta equivale al "
        "logaritmo del cociente, log₂ (128/8) = log₂ 16 = 4.",
        [
            ("16", "Dividió los argumentos y entregó ese cociente sin calcular su logaritmo."),
            ("120", "Restó los argumentos en lugar de los logaritmos."),
            ("2,3", "Dividió los resultados (7 entre 3) en vez de restarlos."),
        ],
    ),
    # ==================================================================
    # LOTE 5 — eje ÁLGEBRA Y FUNCIONES (M1)
    # ==================================================================
    # ---------- alg_expresiones ----------
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el resultado de reducir 7x − 3x + 2x?",
        "6x",
        "Todos los términos son semejantes: comparten la misma letra con el mismo "
        "exponente, así que se pueden juntar en uno solo.\n\n"
        "1) Identifica los coeficientes respetando su signo: +7, −3 y +2.\n"
        "2) Súmalos en orden: 7 − 3 = 4, y 4 + 2 = 6.\n"
        "3) La letra se mantiene igual, así que el resultado es 6x.\n\n"
        "Comprobación: si x valiera 1, la expresión original daría 7 − 3 + 2 = 6, "
        "y 6x también daría 6.",
        [
            ("12x", "Sumó los tres coeficientes ignorando el signo negativo del segundo."),
            ("6x³", "Sumó también los exponentes, como si se estuvieran multiplicando los términos."),
            ("2x", "Restó los coeficientes en el orden equivocado: 7 − 3 − 2."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el resultado de reducir 6m + 4n − 2m − 9n?",
        "4m − 5n",
        "Solo se pueden juntar los términos que comparten la misma letra.\n\n"
        "1) Agrupa por letra: los términos con m son 6m y −2m; los términos con n son "
        "+4n y −9n.\n"
        "2) Reduce los de m: 6 − 2 = 4, o sea 4m.\n"
        "3) Reduce los de n: 4 − 9 = −5, o sea −5n.\n"
        "4) La expresión final es 4m − 5n. No se puede seguir reduciendo porque m y n "
        "son letras distintas.",
        [
            ("−1mn", "Mezcló términos con letras distintas, que no son semejantes entre sí."),
            ("4m + 5n", "Reduzco bien los coeficientes pero perdió el signo negativo del resultado en n."),
            ("8m − 13n", "Sumó los coeficientes sin considerar los signos de resta."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el desarrollo de (x + 5)²?",
        "x² + 10x + 25",
        "El cuadrado de un binomio no es el cuadrado de cada término por separado: "
        "aparece un término del medio.\n\n"
        "1) La regla es (a + b)² = a² + 2ab + b². Aquí a = x y b = 5.\n"
        "2) Primer término: x².\n"
        "3) Doble producto: 2 · x · 5 = 10x.\n"
        "4) Último término: 5² = 25.\n\n"
        "Reuniendo todo queda x² + 10x + 25. Puedes comprobarlo con x = 1: "
        "(1 + 5)² = 36, y 1 + 10 + 25 = 36.",
        [
            ("x² + 25", "Elevó al cuadrado cada término por separado y omitió el doble producto."),
            ("x² + 5x + 25", "Usó el 5 una sola vez en el término del medio en lugar del doble producto."),
            ("x² + 10x + 10", "Duplicó el 5 en el último término en vez de elevarlo al cuadrado."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el desarrollo de (x − 3)²?",
        "x² − 6x + 9",
        "Se aplica el cuadrado de binomio con el signo negativo incluido.\n\n"
        "1) La regla es (a − b)² = a² − 2ab + b², con a = x y b = 3.\n"
        "2) Primer término: x².\n"
        "3) Doble producto, con signo negativo: −2 · x · 3 = −6x.\n"
        "4) Último término: (−3)² = 9, positivo, porque todo cuadrado lo es.\n\n"
        "El resultado es x² − 6x + 9. Fíjate en que solo el término del medio queda "
        "negativo.",
        [
            ("x² − 9", "Elevó al cuadrado cada término por separado y omitió el término central."),
            ("x² − 6x − 9", "Arrastró el signo negativo también al último término, pero un cuadrado nunca es negativo."),
            ("x² − 3x + 9", "Olvidó duplicar el producto en el término del medio."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el desarrollo de (x + 6)(x − 6)?",
        "x² − 36",
        "Este es el producto de una suma por su diferencia, que tiene un resultado "
        "especialmente corto.\n\n"
        "1) La regla es (a + b)(a − b) = a² − b², con a = x y b = 6.\n"
        "2) Aplicándola: x² − 36.\n"
        "3) Si prefieres desarrollarlo término a término: x² − 6x + 6x − 36. Los "
        "términos del medio se cancelan entre sí, y por eso el resultado tiene solo "
        "dos términos.",
        [
            ("x² + 36", "Aplicó la resta a las letras pero no al número, que debe quedar negativo."),
            ("x² − 12x − 36", "Sumó los términos del medio en lugar de cancelarlos."),
            ("x² − 6x − 36", "Canceló solo uno de los dos términos centrales."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es la factorización de x² − 64?",
        "(x + 8)(x − 8)",
        "Una resta de dos cuadrados perfectos siempre se factoriza como una suma por "
        "una diferencia.\n\n"
        "1) Reconoce los cuadrados: x² es el cuadrado de x, y 64 es el cuadrado de 8.\n"
        "2) Aplica la regla a² − b² = (a + b)(a − b).\n"
        "3) Con a = x y b = 8 queda (x + 8)(x − 8).\n"
        "4) Verifica multiplicando: x² − 8x + 8x − 64 = x² − 64. Correcto.",
        [
            ("(x − 8)(x − 8)", "Usó dos veces el signo negativo; así se obtendría x² − 16x + 64."),
            ("(x + 8)(x + 8)", "Usó dos veces el signo positivo, que corresponde a un cuadrado de binomio."),
            ("(x + 64)(x − 64)", "No sacó la raíz cuadrada del 64 al identificar los términos."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es la factorización de 4x² + 8x?",
        "4x(x + 2)",
        "Cuando todos los términos comparten un factor, ese factor se saca afuera.\n\n"
        "1) Busca el mayor número que divida a 4 y a 8: es 4.\n"
        "2) Busca la letra común: ambos términos tienen al menos una x.\n"
        "3) El factor común es entonces 4x. Sácalo: 4x² ÷ 4x = x, y 8x ÷ 4x = 2.\n"
        "4) Queda 4x(x + 2). Verifica distribuyendo: 4x · x = 4x² y 4x · 2 = 8x.",
        [
            ("4(x² + 2x)", "Sacó solo el factor numérico y dejó la x dentro del paréntesis."),
            ("4x(x + 8)", "No dividió el segundo término por el factor común completo."),
            ("2x(2x + 4)", "Usó un factor común incompleto: 2 en lugar de 4, así que aún se puede factorizar más."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el resultado de reducir 2(4x + 3) − 5x?",
        "3x + 6",
        "Primero se elimina el paréntesis distribuyendo, y después se reducen los "
        "términos semejantes.\n\n"
        "1) Distribuye el 2: 2 · 4x = 8x y 2 · 3 = 6. Queda 8x + 6 − 5x.\n"
        "2) Junta los términos con x: 8x − 5x = 3x.\n"
        "3) El 6 no tiene con quién juntarse, así que se mantiene.\n"
        "4) El resultado es 3x + 6.",
        [
            ("4x + 6", "Restó el 5x antes de distribuir el 2, alterando el orden de las operaciones."),
            ("3x + 3", "Distribuyó el 2 solo sobre el término con x y no sobre el 3."),
            ("9x", "Sumó el 6 al término con x, pese a que no son términos semejantes."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización de x² + 9x + 20?",
        "(x + 4)(x + 5)",
        "Se buscan dos números que cumplan dos condiciones a la vez.\n\n"
        "1) Necesitas dos números que multiplicados den 20 y sumados den 9.\n"
        "2) Lista las parejas que dan 20: 1 y 20, 2 y 10, 4 y 5.\n"
        "3) Revisa cuál suma 9: 1 + 20 = 21, 2 + 10 = 12, y 4 + 5 = 9. Esa es.\n"
        "4) La factorización es (x + 4)(x + 5). Verifica: x² + 5x + 4x + 20 = "
        "x² + 9x + 20.",
        [
            ("(x + 2)(x + 10)", "Eligió una pareja que multiplica 20 pero suma 12, no 9."),
            ("(x + 9)(x + 20)", "Usó directamente los coeficientes del enunciado sin buscar la pareja correcta."),
            ("(x − 4)(x − 5)", "Usó signos negativos; así el término del medio quedaría −9x."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización de x² − 3x − 10?",
        "(x − 5)(x + 2)",
        "Con signos mezclados hay que fijarse en qué signo lleva cada número.\n\n"
        "1) Buscas dos números que multiplicados den −10 y sumados den −3.\n"
        "2) Como el producto es negativo, uno debe ser positivo y el otro negativo.\n"
        "3) Prueba las parejas: −5 y +2 multiplican −10 y suman −3. Esa cumple.\n"
        "4) La factorización es (x − 5)(x + 2). Verifica: x² + 2x − 5x − 10 = "
        "x² − 3x − 10.",
        [
            ("(x + 5)(x − 2)", "Invirtió los signos: esta pareja suma +3, no −3."),
            ("(x − 5)(x − 2)", "Usó ambos negativos, con lo que el producto daría +10."),
            ("(x − 10)(x + 1)", "Eligió una pareja que multiplica −10 pero suma −9."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el resultado de simplificar (x² − 36)/(x − 6), con x ≠ 6?",
        "x + 6",
        "Para simplificar una fracción algebraica hay que factorizar primero.\n\n"
        "1) El numerador es una diferencia de cuadrados: x² − 36 = (x + 6)(x − 6).\n"
        "2) Reescribe la fracción: [(x + 6)(x − 6)]/(x − 6).\n"
        "3) El factor (x − 6) aparece arriba y abajo, así que se cancela. Por eso el "
        "enunciado exige x ≠ 6: ahí ese factor valdría cero.\n"
        "4) Queda x + 6.",
        [
            ("x − 6", "Canceló el factor equivocado, dejando el que sí se simplificaba."),
            ("x² − 6", "Canceló solo el número, tratando la fracción término a término en lugar de factorizarla."),
            ("6", "Canceló las x entre sí, algo que solo puede hacerse con factores completos."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el resultado de simplificar (3x + 6)/(x + 2), con x ≠ −2?",
        "3",
        "Conviene sacar factor común en el numerador para que aparezca el mismo "
        "paréntesis de abajo.\n\n"
        "1) En el numerador, 3 divide a ambos términos: 3x + 6 = 3(x + 2).\n"
        "2) Reescribe la fracción: [3(x + 2)]/(x + 2).\n"
        "3) El paréntesis (x + 2) está arriba y abajo, así que se cancela.\n"
        "4) Queda simplemente 3, un número que no depende de x.",
        [
            ("3x", "Canceló solo el 6 con el 2, en vez de factorizar y cancelar el paréntesis completo."),
            ("x + 2", "Canceló el 3 con el numerador, dejando el factor que sí se simplificaba."),
            ("3x + 3", "Restó el 2 del denominador al 6 del numerador, que no es una operación válida en una fracción."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el desarrollo de (x + 2)(x + 7)?",
        "x² + 9x + 14",
        "Se multiplica cada término del primer paréntesis por cada término del "
        "segundo.\n\n"
        "1) x · x = x².\n"
        "2) x · 7 = 7x.\n"
        "3) 2 · x = 2x.\n"
        "4) 2 · 7 = 14.\n\n"
        "Sumando todo: x² + 7x + 2x + 14 = x² + 9x + 14. Atajo: el término del medio "
        "es la suma de los números (2 + 7) y el último es su producto (2 · 7).",
        [
            ("x² + 14", "Multiplicó solo los primeros términos entre sí y los últimos entre sí."),
            ("x² + 14x + 9", "Intercambió la suma con el producto de los números."),
            ("x² + 9x + 9", "Sumó los números también en el término final, en lugar de multiplicarlos."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "Si x = −2, ¿cuál es el valor numérico de 3x² − 4x + 1?",
        "21",
        "Se reemplaza la letra por su valor, cuidando los signos y el orden de las "
        "operaciones.\n\n"
        "1) Primer término: 3x² significa 3 · (−2)². Primero el cuadrado: (−2)² = 4. "
        "Luego 3 · 4 = 12.\n"
        "2) Segundo término: −4x = −4 · (−2) = +8. Menos por menos da más.\n"
        "3) Tercer término: +1.\n"
        "4) Suma todo: 12 + 8 + 1 = 21.",
        [
            ("5", "Calculó 3x² como (3 · −2)² o dejó el segundo término negativo, perdiendo el cambio de signo."),
            ("−3", "Elevó al cuadrado el 3 junto con la x y arrastró mal los signos."),
            ("17", "Interpretó (−2)² como −4, aplicando el cuadrado solo al 2."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el resultado de reducir 5(2a − 3) − 3(a − 4)?",
        "7a − 3",
        "Hay que distribuir los dos paréntesis antes de reducir, con especial cuidado "
        "en el segundo por el signo negativo.\n\n"
        "1) Primer paréntesis: 5 · 2a = 10a y 5 · (−3) = −15. Queda 10a − 15.\n"
        "2) Segundo paréntesis: el −3 multiplica a ambos términos. −3 · a = −3a y "
        "−3 · (−4) = +12.\n"
        "3) Junta todo: 10a − 15 − 3a + 12.\n"
        "4) Reduce: 10a − 3a = 7a, y −15 + 12 = −3. El resultado es 7a − 3.",
        [
            ("7a − 27", "No cambió el signo del segundo término al distribuir el −3, dejando −12."),
            ("13a − 3", "Sumó los términos con a en lugar de restarlos."),
            ("7a + 27", "Perdió los dos signos negativos al distribuir."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización completa de 2x² − 18?",
        "2(x + 3)(x − 3)",
        "Cuando hay factor común y además una diferencia de cuadrados, se aplican los "
        "dos pasos en orden.\n\n"
        "1) Saca primero el factor común 2: 2x² − 18 = 2(x² − 9).\n"
        "2) Lo que quedó dentro es una diferencia de cuadrados, porque 9 = 3².\n"
        "3) Factoriza ese paréntesis: x² − 9 = (x + 3)(x − 3).\n"
        "4) La factorización completa es 2(x + 3)(x − 3). Si te detienes en el paso 1, "
        "la factorización queda a medias.",
        [
            ("2(x² − 9)", "Se detuvo tras sacar el factor común; el paréntesis todavía se puede factorizar."),
            ("(2x + 3)(2x − 3)", "Repartió el 2 dentro de los paréntesis; al desarrollarlo daría 4x² − 9."),
            ("2(x − 3)(x − 3)", "Usó dos veces el signo negativo, que corresponde a un cuadrado de binomio."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "Si a + b = 7 y ab = 12, ¿cuál es el valor de a² + b²?",
        "25",
        "No hace falta encontrar a y b por separado: basta una identidad algebraica.\n\n"
        "1) Parte del cuadrado de la suma: (a + b)² = a² + 2ab + b².\n"
        "2) Despeja lo que buscas: a² + b² = (a + b)² − 2ab.\n"
        "3) Reemplaza los datos: 7² − 2 · 12 = 49 − 24.\n"
        "4) El resultado es 25.\n\n"
        "Control: los números que suman 7 y multiplican 12 son 3 y 4, y en efecto "
        "9 + 16 = 25.",
        [
            ("49", "Elevó la suma al cuadrado pero no restó el doble producto."),
            ("73", "Sumó el doble producto en lugar de restarlo."),
            ("37", "Restó el producto una sola vez en vez del doble producto."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "Si a − b = 5 y ab = 6, ¿cuál es el valor de a² + b²?",
        "37",
        "Se usa la identidad del cuadrado de una diferencia, que cambia el signo del "
        "término central.\n\n"
        "1) Parte de (a − b)² = a² − 2ab + b².\n"
        "2) Despeja: a² + b² = (a − b)² + 2ab. Fíjate en que aquí el doble producto "
        "se suma, al revés que con la suma.\n"
        "3) Reemplaza: 5² + 2 · 6 = 25 + 12.\n"
        "4) El resultado es 37.\n\n"
        "Control: 6 y 1 cumplen que su diferencia es 5 y su producto 6, y "
        "36 + 1 = 37.",
        [
            ("13", "Restó el doble producto, aplicando la identidad de la suma en lugar de la de la diferencia."),
            ("25", "Elevó la diferencia al cuadrado pero no agregó el doble producto."),
            ("31", "Sumó el producto una sola vez en vez del doble producto."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "¿Cuál es el resultado de simplificar (x² + 5x + 6)/(x + 2), con x ≠ −2?",
        "x + 3",
        "El numerador es un trinomio factorizable, y al hacerlo aparece el "
        "denominador.\n\n"
        "1) Busca dos números que multipliquen 6 y sumen 5: son 2 y 3.\n"
        "2) Entonces x² + 5x + 6 = (x + 2)(x + 3).\n"
        "3) Reescribe la fracción: [(x + 2)(x + 3)]/(x + 2).\n"
        "4) Cancela el factor (x + 2), que está arriba y abajo, y queda x + 3.",
        [
            ("x + 2", "Canceló el factor equivocado y conservó el que se simplificaba."),
            ("x² + 3", "Canceló solo los términos numéricos en lugar de factorizar el numerador."),
            ("x + 5", "Restó el 2 del denominador al término del medio, sin factorizar."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "¿Cuál es el resultado de simplificar (x² − 4)/(x² + 4x + 4), con x ≠ −2?",
        "(x − 2)/(x + 2)",
        "Hay que factorizar arriba y abajo antes de poder cancelar.\n\n"
        "1) El numerador es una diferencia de cuadrados: x² − 4 = (x + 2)(x − 2).\n"
        "2) El denominador es un cuadrado de binomio: x² + 4x + 4 = (x + 2)².\n"
        "3) La fracción queda [(x + 2)(x − 2)]/[(x + 2)(x + 2)].\n"
        "4) Cancela un factor (x + 2) de arriba con uno de abajo. Queda "
        "(x − 2)/(x + 2), que ya no se simplifica más.",
        [
            ("x − 2", "Canceló los dos factores del denominador, cuando arriba solo había uno para cancelar."),
            ("(x + 2)/(x − 2)", "Invirtió el resultado final."),
            ("−1", "Canceló las expresiones término a término en lugar de factorizarlas."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el resultado de reducir 8y − y + 3y?",
        "10y",
        "Los tres términos son semejantes, así que basta operar sus coeficientes.\n\n"
        "1) Ojo con el segundo término: −y equivale a −1y, aunque el 1 no se escriba.\n"
        "2) Opera los coeficientes: 8 − 1 = 7, y 7 + 3 = 10.\n"
        "3) El resultado es 10y.",
        [
            ("11y", "Ignoró el término −y por no tener número visible delante."),
            ("10y³", "Sumó los exponentes, como si los términos se estuvieran multiplicando."),
            ("4y", "Restó el tercer término en lugar de sumarlo."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el resultado de reducir 3a + 7b − a − 2b?",
        "2a + 5b",
        "Se agrupan por letra, porque términos con letras distintas no son "
        "semejantes.\n\n"
        "1) Términos con a: 3a y −a. Como −a es −1a, queda 3 − 1 = 2, o sea 2a.\n"
        "2) Términos con b: 7b y −2b. Queda 7 − 2 = 5, o sea 5b.\n"
        "3) El resultado es 2a + 5b, y ahí se detiene: a y b no se pueden juntar.",
        [
            ("7ab", "Sumó todos los coeficientes mezclando términos con letras distintas."),
            ("3a + 5b", "Olvidó restar el término −a por no llevar número visible."),
            ("2a + 9b", "Sumó el 2b en lugar de restarlo."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el desarrollo de (x + 1)(x + 9)?",
        "x² + 10x + 9",
        "Se multiplica cada término del primer paréntesis por cada uno del segundo.\n\n"
        "1) x · x = x².\n"
        "2) Los términos del medio: x · 9 = 9x y 1 · x = x. Juntos dan 10x.\n"
        "3) El término final: 1 · 9 = 9.\n\n"
        "El resultado es x² + 10x + 9. Como atajo, el coeficiente central es la suma "
        "de los números (1 + 9) y el término libre es su producto (1 · 9).",
        [
            ("x² + 9", "Multiplicó solo el primer término por el primero y el segundo por el segundo."),
            ("x² + 9x + 10", "Intercambió la suma con el producto de los dos números."),
            ("x² + 10x + 10", "Sumó los números también en el término final."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el desarrollo de (2x + 3)²?",
        "4x² + 12x + 9",
        "Es un cuadrado de binomio en el que el primer término lleva coeficiente.\n\n"
        "1) Aplica (a + b)² = a² + 2ab + b², con a = 2x y b = 3.\n"
        "2) Primer término: (2x)² = 4x². El exponente afecta también al 2.\n"
        "3) Doble producto: 2 · 2x · 3 = 12x.\n"
        "4) Último término: 3² = 9.\n\n"
        "El resultado es 4x² + 12x + 9.",
        [
            ("2x² + 12x + 9", "No elevó al cuadrado el coeficiente del primer término."),
            ("4x² + 9", "Elevó al cuadrado cada término pero omitió el doble producto."),
            ("4x² + 6x + 9", "Calculó el término del medio sin duplicarlo."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es la factorización de x² − 100?",
        "(x + 10)(x − 10)",
        "Es una diferencia de cuadrados perfectos.\n\n"
        "1) x² es el cuadrado de x, y 100 es el cuadrado de 10.\n"
        "2) Aplica a² − b² = (a + b)(a − b).\n"
        "3) Queda (x + 10)(x − 10).\n"
        "4) Verifica: x² − 10x + 10x − 100 = x² − 100.",
        [
            ("(x − 10)(x − 10)", "Usó dos signos negativos, lo que daría x² − 20x + 100."),
            ("(x + 100)(x − 100)", "No sacó la raíz cuadrada de 100 al identificar los términos."),
            ("(x + 50)(x − 50)", "Dividió el 100 por 2 en lugar de calcular su raíz cuadrada."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es la factorización de 5x² − 15x?",
        "5x(x − 3)",
        "Ambos términos comparten factores, así que se saca el factor común.\n\n"
        "1) El mayor número que divide a 5 y a 15 es 5.\n"
        "2) Ambos términos tienen al menos una x, así que la x también sale.\n"
        "3) El factor común es 5x. Divide cada término: 5x² ÷ 5x = x y "
        "15x ÷ 5x = 3.\n"
        "4) Queda 5x(x − 3). Verifica distribuyendo: 5x · x = 5x² y 5x · 3 = 15x.",
        [
            ("5(x² − 3x)", "Sacó solo el factor numérico y dejó la x dentro del paréntesis."),
            ("5x(x − 15)", "No dividió el segundo término por el factor común completo."),
            ("x(5x − 15)", "Sacó solo la letra, dejando un factor numérico aún factorizable."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es la expresión algebraica que representa el doble de un número aumentado en 7?",
        "2n + 7",
        "Conviene traducir la frase por partes, en el mismo orden en que está escrita.\n\n"
        "1) Llama n al número desconocido.\n"
        "2) 'El doble de un número' significa multiplicarlo por 2: 2n.\n"
        "3) 'Aumentado en 7' significa sumarle 7 a lo anterior: 2n + 7.\n\n"
        "El orden importa: aquí primero se dobla y después se suma.",
        [
            ("2(n + 7)", "Sumó primero y dobló después, que corresponde al doble de un número aumentado en 7 tomado como bloque."),
            ("n + 7", "Omitió el doble del número."),
            ("2n − 7", "Interpretó 'aumentado' como una resta."),
        ],
    ),
    _q(
        "alg_expresiones", "facil",
        "¿Cuál es el resultado de reducir 4(x − 2) + 3x?",
        "7x − 8",
        "Primero se distribuye el paréntesis y después se reducen los semejantes.\n\n"
        "1) Distribuye el 4: 4 · x = 4x y 4 · (−2) = −8. Queda 4x − 8 + 3x.\n"
        "2) Junta los términos con x: 4x + 3x = 7x.\n"
        "3) El −8 queda solo, sin término semejante.\n"
        "4) El resultado es 7x − 8.",
        [
            ("7x − 2", "Distribuyó el 4 solo sobre la x y no sobre el −2."),
            ("4x − 8 + 3x", "Dejó la expresión sin reducir los términos semejantes."),
            ("−x", "Restó el 8 al coeficiente de x, mezclando términos que no son semejantes."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización de x² + 11x + 30?",
        "(x + 5)(x + 6)",
        "Se buscan dos números que multiplicados den 30 y sumados den 11.\n\n"
        "1) Parejas que multiplican 30: 1 y 30, 2 y 15, 3 y 10, 5 y 6.\n"
        "2) Revisa cuál suma 11: 5 + 6 = 11. Esa es.\n"
        "3) Como ambos signos del trinomio son positivos, los dos números son "
        "positivos.\n"
        "4) La factorización es (x + 5)(x + 6). Verifica: x² + 6x + 5x + 30.",
        [
            ("(x + 3)(x + 10)", "Eligió una pareja que multiplica 30 pero suma 13."),
            ("(x + 2)(x + 15)", "Eligió una pareja que multiplica 30 pero suma 17."),
            ("(x − 5)(x − 6)", "Usó signos negativos; así el término central quedaría −11x."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización de x² − 8x + 15?",
        "(x − 3)(x − 5)",
        "El signo del término central y el del término libre indican qué signos "
        "buscar.\n\n"
        "1) Necesitas dos números que multipliquen +15 y sumen −8.\n"
        "2) Como el producto es positivo y la suma negativa, ambos deben ser "
        "negativos.\n"
        "3) Prueba: −3 y −5 multiplican 15 y suman −8. Esos son.\n"
        "4) La factorización es (x − 3)(x − 5).",
        [
            ("(x + 3)(x + 5)", "Usó ambos positivos; así el término central quedaría +8x."),
            ("(x − 1)(x − 15)", "Eligió una pareja que multiplica 15 pero suma −16."),
            ("(x + 3)(x − 5)", "Mezcló los signos; así el producto daría −15, no +15."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es la factorización de x² + 2x − 24?",
        "(x + 6)(x − 4)",
        "Con término libre negativo, los dos números tienen signos distintos.\n\n"
        "1) Buscas dos números que multipliquen −24 y sumen +2.\n"
        "2) Como el producto es negativo, uno es positivo y el otro negativo. Y como "
        "la suma es positiva, el mayor en valor absoluto es el positivo.\n"
        "3) Prueba parejas de 24: 6 y 4 se diferencian en 2. Con +6 y −4 se cumple "
        "todo.\n"
        "4) La factorización es (x + 6)(x − 4).",
        [
            ("(x − 6)(x + 4)", "Invirtió los signos: esta pareja suma −2."),
            ("(x + 8)(x − 3)", "Eligió una pareja que multiplica −24 pero suma +5."),
            ("(x + 12)(x − 2)", "Eligió una pareja que multiplica −24 pero suma +10."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el resultado de simplificar (x² − 25)/(x + 5), con x ≠ −5?",
        "x − 5",
        "Se factoriza el numerador para que aparezca el denominador.\n\n"
        "1) El numerador es una diferencia de cuadrados: x² − 25 = (x + 5)(x − 5).\n"
        "2) La fracción queda [(x + 5)(x − 5)]/(x + 5).\n"
        "3) Cancela el factor (x + 5), presente arriba y abajo.\n"
        "4) Queda x − 5.",
        [
            ("x + 5", "Canceló el factor equivocado y conservó el que se simplificaba."),
            ("x² − 5", "Canceló solo los números, tratando la fracción término a término."),
            ("−5", "Canceló las x entre sí, algo que solo puede hacerse con factores completos."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el resultado de simplificar (4x + 12)/(x + 3), con x ≠ −3?",
        "4",
        "Se saca factor común arriba para que aparezca el paréntesis de abajo.\n\n"
        "1) El 4 divide a ambos términos del numerador: 4x + 12 = 4(x + 3).\n"
        "2) La fracción queda [4(x + 3)]/(x + 3).\n"
        "3) Cancela el paréntesis (x + 3).\n"
        "4) Queda 4, un valor que no depende de x.",
        [
            ("4x", "Canceló solo el 12 con el 3 en lugar de factorizar el numerador."),
            ("x + 3", "Canceló el 4, dejando el factor que sí se simplificaba."),
            ("4x + 9", "Restó el 3 del denominador al 12 del numerador, operación no válida en una fracción."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "Si x = 3, ¿cuál es el valor numérico de 2x² − 5x + 4?",
        "7",
        "Se reemplaza la letra por su valor respetando el orden de las operaciones.\n\n"
        "1) Primer término: 2x² es 2 · 3². Primero el cuadrado, 3² = 9, y después "
        "2 · 9 = 18.\n"
        "2) Segundo término: −5x = −5 · 3 = −15.\n"
        "3) Tercer término: +4.\n"
        "4) Suma todo: 18 − 15 + 4 = 7.",
        [
            ("31", "Calculó 2x² como (2 · 3)², elevando al cuadrado también el coeficiente."),
            ("−1", "Restó el 4 en lugar de sumarlo."),
            ("13", "Multiplicó antes de elevar al cuadrado en el primer término y arrastró el error."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el resultado de reducir 3(2m + 5) − 2(m − 1)?",
        "4m + 17",
        "Se distribuyen ambos paréntesis con cuidado en los signos.\n\n"
        "1) Primer paréntesis: 3 · 2m = 6m y 3 · 5 = 15. Queda 6m + 15.\n"
        "2) Segundo paréntesis: el −2 multiplica a los dos términos. −2 · m = −2m y "
        "−2 · (−1) = +2.\n"
        "3) Junta todo: 6m + 15 − 2m + 2.\n"
        "4) Reduce: 6m − 2m = 4m, y 15 + 2 = 17. El resultado es 4m + 17.",
        [
            ("4m + 13", "No cambió el signo del segundo término al distribuir el −2."),
            ("8m + 17", "Sumó los términos con m en lugar de restarlos."),
            ("4m + 15", "Distribuyó el −2 solo sobre la m y olvidó el −1."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "¿Cuál es el desarrollo de (3x − 2)(3x + 2)?",
        "9x² − 4",
        "Es una suma por su diferencia, con coeficiente en el primer término.\n\n"
        "1) Aplica (a − b)(a + b) = a² − b², con a = 3x y b = 2.\n"
        "2) Primer término: (3x)² = 9x². El exponente afecta también al 3.\n"
        "3) Segundo término: 2² = 4, restando.\n"
        "4) El resultado es 9x² − 4. Los términos centrales (−6x y +6x) se cancelan.",
        [
            ("3x² − 4", "No elevó al cuadrado el coeficiente del primer término."),
            ("9x² + 4", "No aplicó el signo negativo al término numérico."),
            ("9x² − 12x − 4", "Sumó los términos centrales en lugar de cancelarlos."),
        ],
    ),
    _q(
        "alg_expresiones", "medio",
        "Un rectángulo tiene largo (x + 5) y ancho (x − 2). ¿Cuál es la expresión reducida de su perímetro?",
        "4x + 6",
        "El perímetro suma los cuatro lados: dos largos y dos anchos.\n\n"
        "1) Plantea: P = 2(x + 5) + 2(x − 2).\n"
        "2) Distribuye: 2x + 10 + 2x − 4.\n"
        "3) Reduce los términos con x: 2x + 2x = 4x.\n"
        "4) Reduce los números: 10 − 4 = 6. El perímetro es 4x + 6.",
        [
            ("2x + 3", "Sumó largo y ancho una sola vez, olvidando que cada lado se repite dos veces."),
            ("x² + 3x − 10", "Calculó el área en lugar del perímetro."),
            ("4x + 14", "No cambió el signo del −2 al duplicar el ancho."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "Si a + b = 10 y ab = 21, ¿cuál es el valor de a² + b²?",
        "58",
        "Se usa la identidad del cuadrado de una suma, sin necesidad de hallar a y b.\n\n"
        "1) Parte de (a + b)² = a² + 2ab + b².\n"
        "2) Despeja: a² + b² = (a + b)² − 2ab.\n"
        "3) Reemplaza: 10² − 2 · 21 = 100 − 42.\n"
        "4) El resultado es 58.\n\n"
        "Control: los números que suman 10 y multiplican 21 son 3 y 7, y "
        "9 + 49 = 58.",
        [
            ("100", "Elevó la suma al cuadrado pero no restó el doble producto."),
            ("142", "Sumó el doble producto en lugar de restarlo."),
            ("79", "Restó el producto una sola vez en vez del doble producto."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "¿Cuál es el resultado de simplificar (x² − 7x + 12)/(x − 3), con x ≠ 3?",
        "x − 4",
        "Se factoriza el trinomio del numerador para que aparezca el denominador.\n\n"
        "1) Buscas dos números que multipliquen 12 y sumen −7: son −3 y −4.\n"
        "2) Entonces x² − 7x + 12 = (x − 3)(x − 4).\n"
        "3) La fracción queda [(x − 3)(x − 4)]/(x − 3).\n"
        "4) Cancela el factor (x − 3) y queda x − 4.",
        [
            ("x − 3", "Canceló el factor equivocado y conservó el que se simplificaba."),
            ("x + 4", "Factorizó con signos positivos, que darían un término central +7x."),
            ("x − 7", "Restó el 3 del denominador al término central, sin factorizar."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "¿Cuál es la factorización completa de 3x² − 27?",
        "3(x + 3)(x − 3)",
        "Primero el factor común, después la diferencia de cuadrados.\n\n"
        "1) Saca el 3, que divide a ambos términos: 3x² − 27 = 3(x² − 9).\n"
        "2) Lo de adentro es una diferencia de cuadrados, con 9 = 3².\n"
        "3) Factoriza: x² − 9 = (x + 3)(x − 3).\n"
        "4) La factorización completa es 3(x + 3)(x − 3). Detenerse en el paso 1 deja "
        "el trabajo a medias.",
        [
            ("3(x² − 9)", "Se detuvo tras el factor común; el paréntesis aún se factoriza."),
            ("(3x + 3)(3x − 3)", "Repartió el 3 dentro de los paréntesis; al desarrollarlo daría 9x² − 9."),
            ("3(x − 3)(x − 3)", "Usó dos signos negativos, que corresponden a un cuadrado de binomio."),
        ],
    ),
    _q(
        "alg_expresiones", "dificil",
        "¿Cuál es el resultado de simplificar (x² + 6x + 9)/(x² − 9), con x ≠ 3 y x ≠ −3?",
        "(x + 3)/(x − 3)",
        "Hay que factorizar numerador y denominador antes de cancelar.\n\n"
        "1) El numerador es un cuadrado de binomio: x² + 6x + 9 = (x + 3)².\n"
        "2) El denominador es una diferencia de cuadrados: x² − 9 = (x + 3)(x − 3).\n"
        "3) La fracción queda [(x + 3)(x + 3)]/[(x + 3)(x − 3)].\n"
        "4) Cancela un factor (x + 3) arriba con uno abajo. Queda (x + 3)/(x − 3), "
        "que ya no se simplifica más.",
        [
            ("x + 3", "Canceló los dos factores del denominador cuando solo correspondía cancelar uno."),
            ("(x − 3)/(x + 3)", "Invirtió el resultado final."),
            ("−1", "Canceló término a término en lugar de factorizar."),
        ],
    ),
    # ---------- alg_lineal ----------
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 3x + 4 = 19?",
        "x = 5",
        "Se despeja la x dejándola sola a un lado de la igualdad.\n\n"
        "1) Quita el +4 restando 4 a ambos lados: 3x = 19 − 4, o sea 3x = 15.\n"
        "2) Quita el 3 que multiplica dividiendo por 3 a ambos lados: x = 15 ÷ 3.\n"
        "3) Entonces x = 5.\n"
        "4) Verifica reemplazando: 3 · 5 + 4 = 15 + 4 = 19. Correcto.",
        [
            ("x = 7", "Restó el 4 solo en un lado o lo sumó en vez de restarlo antes de dividir."),
            ("x = 15", "Despejó el 4 pero no dividió por el coeficiente 3."),
            ("x = 69", "Multiplicó por 3 en lugar de dividir."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 5x − 8 = 12?",
        "x = 4",
        "Se aísla el término con x y después se elimina su coeficiente.\n\n"
        "1) El −8 pasa sumando: 5x = 12 + 8, o sea 5x = 20.\n"
        "2) El 5 está multiplicando, así que pasa dividiendo: x = 20 ÷ 5.\n"
        "3) Entonces x = 4.\n"
        "4) Verifica: 5 · 4 − 8 = 20 − 8 = 12. Correcto.",
        [
            ("x = 0,8", "Restó el 8 en lugar de sumarlo al despejar."),
            ("x = 20", "Despejó bien el 8 pero no dividió por el coeficiente."),
            ("x = 100", "Multiplicó por 5 en vez de dividir."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de x/4 + 3 = 8?",
        "x = 20",
        "Primero se despeja la fracción y después se elimina el denominador.\n\n"
        "1) Resta 3 a ambos lados: x/4 = 8 − 3, o sea x/4 = 5.\n"
        "2) El 4 está dividiendo, así que pasa multiplicando: x = 5 · 4.\n"
        "3) Entonces x = 20.\n"
        "4) Verifica: 20/4 + 3 = 5 + 3 = 8. Correcto.",
        [
            ("x = 32", "Multiplicó por 4 antes de restar el 3, alterando el orden del despeje."),
            ("x = 5", "Se detuvo en x/4 = 5 sin multiplicar por el denominador."),
            ("x = 1,25", "Dividió por 4 en lugar de multiplicar."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 2x + 9 = 3x − 1?",
        "x = 10",
        "Cuando hay x a ambos lados, se juntan todas de un mismo lado.\n\n"
        "1) Resta 2x a ambos lados: 9 = x − 1.\n"
        "2) Suma 1 a ambos lados: 10 = x.\n"
        "3) Entonces x = 10.\n"
        "4) Verifica: a la izquierda 2 · 10 + 9 = 29, y a la derecha 3 · 10 − 1 = 29. "
        "Coinciden.",
        [
            ("x = 8", "Restó el 1 en lugar de sumarlo al despejar."),
            ("x = −10", "Movió los términos con x al lado equivocado y perdió el signo."),
            ("x = 2", "Restó los coeficientes de x y los términos libres por separado, sin despejar."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es el conjunto solución de la inecuación x + 5 > 12?",
        "x > 7",
        "Una inecuación se resuelve igual que una ecuación, cuidando el sentido del "
        "signo.\n\n"
        "1) Resta 5 a ambos lados: x > 12 − 5.\n"
        "2) Entonces x > 7.\n"
        "3) Como solo se sumó o restó (no se multiplicó ni dividió por un negativo), "
        "el signo mayor que se mantiene igual.\n"
        "4) Comprueba con un valor: x = 8 cumple, porque 8 + 5 = 13 > 12.",
        [
            ("x < 7", "Invirtió el sentido de la desigualdad sin motivo: eso solo ocurre al multiplicar o dividir por un negativo."),
            ("x > 17", "Sumó el 5 en lugar de restarlo."),
            ("x > 12", "Ignoró el 5 al despejar."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es el conjunto solución de la inecuación 4x ≤ 20?",
        "x ≤ 5",
        "Se divide por el coeficiente, que en este caso es positivo.\n\n"
        "1) Divide ambos lados por 4: x ≤ 20 ÷ 4.\n"
        "2) Entonces x ≤ 5.\n"
        "3) Como se dividió por un número positivo, el sentido de la desigualdad no "
        "cambia.\n"
        "4) Comprueba: x = 5 cumple con igualdad (4 · 5 = 20) y x = 4 también cumple.",
        [
            ("x ≥ 5", "Invirtió el sentido de la desigualdad pese a haber dividido por un número positivo."),
            ("x ≤ 80", "Multiplicó por 4 en lugar de dividir."),
            ("x ≤ 16", "Restó 4 en vez de dividir por 4."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 7 − x = 2?",
        "x = 5",
        "Aquí la incógnita aparece restando, así que conviene ordenarla primero.\n\n"
        "1) Resta 7 a ambos lados: −x = 2 − 7, o sea −x = −5.\n"
        "2) Multiplica ambos lados por −1 para dejar la x positiva: x = 5.\n"
        "3) Verifica: 7 − 5 = 2. Correcto.\n\n"
        "Otra vía: pasar la x al lado derecho y el 2 al izquierdo, quedando "
        "7 − 2 = x.",
        [
            ("x = −5", "Se quedó en −x = −5 sin multiplicar por −1 para despejar la x."),
            ("x = 9", "Sumó el 2 al 7 en lugar de restarlo."),
            ("x = 14", "Multiplicó en lugar de restar."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 6x = 4x + 14?",
        "x = 7",
        "Se agrupan los términos con x de un solo lado.\n\n"
        "1) Resta 4x a ambos lados: 6x − 4x = 14, o sea 2x = 14.\n"
        "2) Divide por 2: x = 7.\n"
        "3) Verifica: a la izquierda 6 · 7 = 42, y a la derecha 4 · 7 + 14 = 42. "
        "Coinciden.",
        [
            ("x = 14", "Restó los términos con x pero olvidó dividir por el coeficiente 2."),
            ("x = 1,4", "Sumó los coeficientes de x en lugar de restarlos, dividiendo por 10."),
            ("x = 3,5", "Dividió el 14 por 4 en vez de por la diferencia de coeficientes."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de 4(x + 3) = 2x + 20?",
        "x = 4",
        "Primero se elimina el paréntesis y después se agrupan los términos.\n\n"
        "1) Distribuye el 4: 4x + 12 = 2x + 20.\n"
        "2) Resta 2x a ambos lados: 2x + 12 = 20.\n"
        "3) Resta 12: 2x = 8.\n"
        "4) Divide por 2: x = 4. Verifica: 4(4 + 3) = 28 y 2 · 4 + 20 = 28.",
        [
            ("x = 8", "Distribuyó el 4 solo sobre la x y no sobre el 3."),
            ("x = 16", "Agrupó bien pero no dividió por el coeficiente final."),
            ("x = 2", "Restó el 12 antes de agrupar los términos con x y perdió un paso."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de 5(x − 1) = 3(x + 3)?",
        "x = 7",
        "Se distribuyen ambos paréntesis y luego se agrupa.\n\n"
        "1) Lado izquierdo: 5x − 5. Lado derecho: 3x + 9.\n"
        "2) Resta 3x a ambos lados: 2x − 5 = 9.\n"
        "3) Suma 5: 2x = 14.\n"
        "4) Divide por 2: x = 7. Verifica: 5(7 − 1) = 30 y 3(7 + 3) = 30.",
        [
            ("x = 2", "No distribuyó los factores sobre los términos numéricos de los paréntesis."),
            ("x = 14", "Agrupó correctamente pero no dividió por 2 al final."),
            ("x = −7", "Movió los términos al lado equivocado y arrastró un signo cambiado."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es el conjunto solución de la inecuación −4x + 2 < 14?",
        "x > −3",
        "El paso clave aparece al dividir por un número negativo.\n\n"
        "1) Resta 2 a ambos lados: −4x < 12.\n"
        "2) Divide por −4. Al dividir por un número negativo, la desigualdad cambia "
        "de sentido: x > 12 ÷ (−4).\n"
        "3) Entonces x > −3.\n"
        "4) Comprueba con x = 0: −4 · 0 + 2 = 2, que efectivamente es menor que 14.",
        [
            ("x < −3", "Dividió por un número negativo sin invertir el sentido de la desigualdad."),
            ("x > 3", "Perdió el signo negativo al dividir."),
            ("x > −4", "Restó el 2 al 14 en el lado equivocado antes de dividir."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es el conjunto solución de la inecuación 5x − 3 ≥ 2x + 9?",
        "x ≥ 4",
        "Se agrupan los términos con x de un lado, igual que en una ecuación.\n\n"
        "1) Resta 2x a ambos lados: 3x − 3 ≥ 9.\n"
        "2) Suma 3: 3x ≥ 12.\n"
        "3) Divide por 3, que es positivo, así que el sentido se mantiene: x ≥ 4.\n"
        "4) Comprueba con x = 4: a la izquierda 17 y a la derecha 17, y la igualdad "
        "está incluida.",
        [
            ("x ≤ 4", "Invirtió el sentido de la desigualdad pese a haber dividido por un positivo."),
            ("x ≥ 12", "Agrupó bien pero no dividió por el coeficiente 3."),
            ("x ≥ 2", "Restó el 3 en lugar de sumarlo al despejar."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de x/2 + x/3 = 5?",
        "x = 6",
        "Conviene eliminar los denominadores antes de despejar.\n\n"
        "1) El mínimo común múltiplo de 2 y 3 es 6. Multiplica toda la ecuación por 6: "
        "6 · (x/2) + 6 · (x/3) = 6 · 5.\n"
        "2) Queda 3x + 2x = 30.\n"
        "3) Reduce: 5x = 30.\n"
        "4) Divide por 5: x = 6. Verifica: 6/2 + 6/3 = 3 + 2 = 5.",
        [
            ("x = 30", "Eliminó los denominadores pero no redujo ni dividió por el coeficiente final."),
            ("x = 2,5", "Sumó las fracciones como si x/2 + x/3 fuera x/5."),
            ("x = 12", "Usó como denominador común el producto 6 pero multiplicó solo un lado de la igualdad."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "El doble de un número disminuido en 5 es 19. ¿Cuál es el número?",
        "12",
        "Se traduce el enunciado a una ecuación y se despeja.\n\n"
        "1) Llama n al número. 'El doble' es 2n, y 'disminuido en 5' es 2n − 5.\n"
        "2) La ecuación es 2n − 5 = 19.\n"
        "3) Suma 5: 2n = 24.\n"
        "4) Divide por 2: n = 12. Verifica: el doble de 12 es 24, y 24 − 5 = 19.",
        [
            ("7", "Restó el 5 en lugar de sumarlo al despejar."),
            ("24", "Despejó bien pero olvidó dividir por 2 para deshacer el doble."),
            ("14", "Interpretó el enunciado como 2(n − 5) = 19 y redondeó el resultado."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "La suma de dos números consecutivos es 47. ¿Cuál es el menor de ellos?",
        "23",
        "Dos números consecutivos se diferencian en 1, así que basta una incógnita.\n\n"
        "1) Llama n al menor. El siguiente es n + 1.\n"
        "2) La ecuación es n + (n + 1) = 47.\n"
        "3) Reduce: 2n + 1 = 47, entonces 2n = 46.\n"
        "4) Divide por 2: n = 23. Los números son 23 y 24, y en efecto suman 47.",
        [
            ("24", "Encontró el número correcto pero entregó el mayor en lugar del menor."),
            ("23,5", "Dividió 47 por 2 sin considerar que los números se diferencian en 1."),
            ("46", "Despejó el 1 pero olvidó dividir por 2."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de 3(2x − 1) = 4x + 7?",
        "x = 5",
        "Se distribuye el paréntesis y luego se agrupan los términos con x.\n\n"
        "1) Distribuye: 6x − 3 = 4x + 7.\n"
        "2) Resta 4x a ambos lados: 2x − 3 = 7.\n"
        "3) Suma 3: 2x = 10.\n"
        "4) Divide por 2: x = 5. Verifica: 3(2 · 5 − 1) = 27 y 4 · 5 + 7 = 27.",
        [
            ("x = 10", "Agrupó bien pero no dividió por el coeficiente final."),
            ("x = 2", "Restó el 3 en lugar de sumarlo al despejar."),
            ("x = 4", "Distribuyó el 3 solo sobre el 2x y no sobre el −1."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "¿Cuál es la solución de (x + 2)/3 = (x − 4)/2?",
        "x = 16",
        "Con una fracción a cada lado, conviene multiplicar en cruz.\n\n"
        "1) Multiplica en cruz: 2(x + 2) = 3(x − 4).\n"
        "2) Distribuye ambos lados: 2x + 4 = 3x − 12.\n"
        "3) Resta 2x: 4 = x − 12.\n"
        "4) Suma 12: x = 16. Verifica: (16 + 2)/3 = 6 y (16 − 4)/2 = 6. Coinciden.",
        [
            ("x = −16", "Movió los términos al lado equivocado y arrastró el signo cambiado."),
            ("x = 8", "Multiplicó en cruz pero no distribuyó los factores sobre los términos numéricos."),
            ("x = 2", "Igualó los numeradores entre sí y los denominadores entre sí."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "Un padre tiene 40 años y su hijo 10. ¿En cuántos años más la edad del padre será el doble de la del hijo?",
        "20 años",
        "El truco es que ambos envejecen la misma cantidad de años.\n\n"
        "1) Llama t a los años que deben pasar. En ese momento el padre tendrá 40 + t "
        "y el hijo 10 + t.\n"
        "2) La condición es que el padre duplique al hijo: 40 + t = 2(10 + t).\n"
        "3) Distribuye: 40 + t = 20 + 2t.\n"
        "4) Despeja: 40 − 20 = 2t − t, o sea t = 20. En 20 años el padre tendrá 60 y "
        "el hijo 30, y 60 es el doble de 30.",
        [
            ("10 años", "Igualó las edades futuras sin plantear la relación de doble."),
            ("30 años", "Restó las edades actuales en lugar de plantear la ecuación."),
            ("5 años", "Sumó los años solo a la edad del hijo, dejando fija la del padre."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "¿Cuál es el conjunto solución de la inecuación 2(x − 3) > 3(x + 1)?",
        "x < −9",
        "Al despejar queda un coeficiente negativo, y ahí cambia el sentido.\n\n"
        "1) Distribuye ambos lados: 2x − 6 > 3x + 3.\n"
        "2) Resta 3x a ambos lados: −x − 6 > 3.\n"
        "3) Suma 6: −x > 9.\n"
        "4) Multiplica por −1 e invierte el sentido de la desigualdad: x < −9.\n\n"
        "Comprueba con x = −10: a la izquierda 2(−13) = −26 y a la derecha "
        "3(−9) = −27. En efecto −26 > −27.",
        [
            ("x > −9", "Multiplicó por −1 sin invertir el sentido de la desigualdad."),
            ("x < 9", "Perdió el signo negativo al despejar."),
            ("x < −3", "No distribuyó los factores sobre los términos numéricos de los paréntesis."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "Un número aumentado en su mitad es igual a 27. ¿Cuál es el número?",
        "18",
        "Se traduce el enunciado usando una fracción.\n\n"
        "1) Llama n al número. Su mitad es n/2.\n"
        "2) La ecuación es n + n/2 = 27.\n"
        "3) Multiplica todo por 2 para quitar el denominador: 2n + n = 54, o sea "
        "3n = 54.\n"
        "4) Divide por 3: n = 18. Verifica: 18 + 9 = 27. Correcto.",
        [
            ("13,5", "Dividió 27 por 2, respondiendo cuál es la mitad en lugar del número."),
            ("54", "Multiplicó por 2 pero no dividió por el coeficiente 3."),
            ("9", "Resolvió cuánto vale la mitad del número en lugar del número mismo."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 2x − 7 = 9?",
        "x = 8",
        "Se despeja la x en dos pasos.\n\n"
        "1) El −7 pasa sumando: 2x = 9 + 7, o sea 2x = 16.\n"
        "2) El 2 pasa dividiendo: x = 16 ÷ 2.\n"
        "3) Entonces x = 8.\n"
        "4) Verifica: 2 · 8 − 7 = 16 − 7 = 9. Correcto.",
        [
            ("x = 1", "Restó el 7 en lugar de sumarlo al despejar."),
            ("x = 16", "Despejó el 7 pero no dividió por el coeficiente."),
            ("x = 32", "Multiplicó por 2 en vez de dividir."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 8 + 3x = 23?",
        "x = 5",
        "El término con x puede estar en segundo lugar; el procedimiento no cambia.\n\n"
        "1) Resta 8 a ambos lados: 3x = 23 − 8, o sea 3x = 15.\n"
        "2) Divide por 3: x = 5.\n"
        "3) Verifica: 8 + 3 · 5 = 8 + 15 = 23. Correcto.",
        [
            ("x = 15", "Despejó bien el 8 pero no dividió por el coeficiente 3."),
            ("x = 10,3", "Sumó el 8 en lugar de restarlo antes de dividir."),
            ("x = 45", "Multiplicó por 3 en vez de dividir."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de x/5 = 7?",
        "x = 35",
        "La x está dividida, así que se deshace multiplicando.\n\n"
        "1) El 5 está dividiendo, por lo tanto pasa multiplicando al otro lado.\n"
        "2) x = 7 · 5.\n"
        "3) Entonces x = 35.\n"
        "4) Verifica: 35/5 = 7. Correcto.",
        [
            ("x = 1,4", "Dividió por 5 en lugar de multiplicar."),
            ("x = 12", "Sumó el 5 en vez de multiplicar por él."),
            ("x = 2", "Restó el 5 al 7 en lugar de multiplicar."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 9x = 5x + 24?",
        "x = 6",
        "Se juntan los términos con x de un mismo lado.\n\n"
        "1) Resta 5x a ambos lados: 9x − 5x = 24, o sea 4x = 24.\n"
        "2) Divide por 4: x = 6.\n"
        "3) Verifica: a la izquierda 9 · 6 = 54, y a la derecha 5 · 6 + 24 = 54.",
        [
            ("x = 24", "Restó los términos con x pero no dividió por el coeficiente."),
            ("x = 1,7", "Sumó los coeficientes de x en lugar de restarlos."),
            ("x = 4,8", "Dividió el 24 por 5 en vez de por la diferencia de coeficientes."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es el conjunto solución de la inecuación x − 4 ≥ 6?",
        "x ≥ 10",
        "Se despeja igual que una ecuación.\n\n"
        "1) Suma 4 a ambos lados: x ≥ 6 + 4.\n"
        "2) Entonces x ≥ 10.\n"
        "3) Como solo se sumó, el sentido de la desigualdad no cambia.\n"
        "4) Comprueba con x = 10: 10 − 4 = 6, y la igualdad está incluida.",
        [
            ("x ≤ 10", "Invirtió el sentido de la desigualdad sin motivo."),
            ("x ≥ 2", "Restó el 4 en lugar de sumarlo."),
            ("x ≥ 24", "Multiplicó por 4 en vez de sumarlo."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es el conjunto solución de la inecuación 3x < 21?",
        "x < 7",
        "Se divide por el coeficiente, que es positivo.\n\n"
        "1) Divide ambos lados por 3: x < 21 ÷ 3.\n"
        "2) Entonces x < 7.\n"
        "3) El sentido se mantiene porque el 3 es positivo.\n"
        "4) Comprueba con x = 6: 3 · 6 = 18, que es menor que 21.",
        [
            ("x > 7", "Invirtió el sentido pese a haber dividido por un número positivo."),
            ("x < 63", "Multiplicó por 3 en lugar de dividir."),
            ("x < 18", "Restó 3 en vez de dividir por 3."),
        ],
    ),
    _q(
        "alg_lineal", "facil",
        "¿Cuál es la solución de 10 − 2x = 4?",
        "x = 3",
        "El término con x aparece restando, así que se ordena primero.\n\n"
        "1) Resta 10 a ambos lados: −2x = 4 − 10, o sea −2x = −6.\n"
        "2) Divide por −2: x = (−6) ÷ (−2) = 3.\n"
        "3) Verifica: 10 − 2 · 3 = 10 − 6 = 4. Correcto.",
        [
            ("x = −3", "Perdió uno de los dos signos negativos al dividir."),
            ("x = 7", "Restó el 4 al 10 sin considerar el coeficiente 2."),
            ("x = 2", "Dividió el 4 por 2 sin despejar primero el 10."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de 6(x − 2) = 3x + 6?",
        "x = 6",
        "Se distribuye el paréntesis y luego se agrupan los términos con x.\n\n"
        "1) Distribuye: 6x − 12 = 3x + 6.\n"
        "2) Resta 3x: 3x − 12 = 6.\n"
        "3) Suma 12: 3x = 18.\n"
        "4) Divide por 3: x = 6. Verifica: 6(6 − 2) = 24 y 3 · 6 + 6 = 24.",
        [
            ("x = 18", "Agrupó correctamente pero no dividió por el coeficiente final."),
            ("x = 2", "Distribuyó el 6 solo sobre la x y no sobre el −2."),
            ("x = −2", "Restó el 12 en lugar de sumarlo al despejar."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de 2(x + 4) + 3 = 5x − 4?",
        "x = 5",
        "Primero se ordena el lado izquierdo por completo.\n\n"
        "1) Distribuye: 2x + 8 + 3 = 5x − 4.\n"
        "2) Reduce el lado izquierdo: 2x + 11 = 5x − 4.\n"
        "3) Resta 2x y suma 4 a ambos lados: 15 = 3x.\n"
        "4) Divide por 3: x = 5. Verifica: 2(5 + 4) + 3 = 21 y 5 · 5 − 4 = 21.",
        [
            ("x = 15", "Agrupó bien pero no dividió por el coeficiente final."),
            ("x = 3,7", "Olvidó sumar el 3 al reducir el lado izquierdo."),
            ("x = 2,3", "Restó el 4 en lugar de sumarlo al pasarlo de lado."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es el conjunto solución de la inecuación −2x ≥ 10?",
        "x ≤ −5",
        "Dividir por un coeficiente negativo obliga a invertir la desigualdad.\n\n"
        "1) Divide ambos lados por −2.\n"
        "2) Como el divisor es negativo, el signo mayor o igual se transforma en menor "
        "o igual: x ≤ 10 ÷ (−2).\n"
        "3) Entonces x ≤ −5.\n"
        "4) Comprueba con x = −6: −2 · (−6) = 12, que efectivamente es mayor que 10.",
        [
            ("x ≥ −5", "Dividió por un negativo sin invertir el sentido de la desigualdad."),
            ("x ≤ 5", "Perdió el signo negativo del resultado."),
            ("x ≥ 5", "Perdió el signo negativo y además no invirtió el sentido."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es el conjunto solución de la inecuación 4(x + 1) < 2x + 10?",
        "x < 3",
        "Se distribuye y luego se agrupa, igual que en una ecuación.\n\n"
        "1) Distribuye: 4x + 4 < 2x + 10.\n"
        "2) Resta 2x: 2x + 4 < 10.\n"
        "3) Resta 4: 2x < 6.\n"
        "4) Divide por 2, que es positivo, así que el sentido se conserva: x < 3.",
        [
            ("x > 3", "Invirtió el sentido pese a haber dividido por un número positivo."),
            ("x < 6", "Agrupó bien pero no dividió por el coeficiente 2."),
            ("x < 1,5", "Distribuyó el 4 solo sobre la x y no sobre el 1."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "¿Cuál es la solución de x/3 − x/6 = 2?",
        "x = 12",
        "Se eliminan los denominadores multiplicando por el mínimo común múltiplo.\n\n"
        "1) El mínimo común múltiplo de 3 y 6 es 6. Multiplica toda la ecuación por 6.\n"
        "2) Queda 2x − x = 12.\n"
        "3) Reduce: x = 12.\n"
        "4) Verifica: 12/3 − 12/6 = 4 − 2 = 2. Correcto.",
        [
            ("x = 4", "Restó los denominadores como si x/3 − x/6 fuera x/3."),
            ("x = 6", "Multiplicó solo un lado de la igualdad por el denominador común."),
            ("x = 36", "Multiplicó por el producto de los denominadores en lugar de por su mínimo común múltiplo."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "El triple de un número aumentado en 4 es igual a 25. ¿Cuál es el número?",
        "7",
        "Se traduce la frase a una ecuación respetando el orden.\n\n"
        "1) Llama n al número. El triple es 3n, y aumentado en 4 es 3n + 4.\n"
        "2) La ecuación es 3n + 4 = 25.\n"
        "3) Resta 4: 3n = 21.\n"
        "4) Divide por 3: n = 7. Verifica: 3 · 7 + 4 = 25.",
        [
            ("21", "Despejó el 4 pero olvidó dividir por 3."),
            ("9,7", "Sumó el 4 en lugar de restarlo al despejar."),
            ("4,3", "Interpretó el enunciado como 3(n + 4) = 25."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "La suma de dos números pares consecutivos es 66. ¿Cuál es el menor de ellos?",
        "32",
        "Dos pares consecutivos se diferencian en 2, no en 1.\n\n"
        "1) Llama n al menor. El siguiente par es n + 2.\n"
        "2) La ecuación es n + (n + 2) = 66.\n"
        "3) Reduce: 2n + 2 = 66, entonces 2n = 64.\n"
        "4) Divide por 2: n = 32. Los números son 32 y 34, que suman 66.",
        [
            ("34", "Encontró los números correctos pero entregó el mayor."),
            ("33", "Trató los números como consecutivos comunes, con diferencia 1."),
            ("64", "Despejó el 2 pero no dividió por el coeficiente."),
        ],
    ),
    _q(
        "alg_lineal", "medio",
        "Si 3x + 2y = 12 e y = 3, ¿cuál es el valor de x?",
        "x = 2",
        "Con el valor de y conocido, la ecuación queda con una sola incógnita.\n\n"
        "1) Reemplaza y por 3: 3x + 2 · 3 = 12.\n"
        "2) Calcula: 3x + 6 = 12.\n"
        "3) Resta 6: 3x = 6.\n"
        "4) Divide por 3: x = 2. Verifica: 3 · 2 + 2 · 3 = 6 + 6 = 12.",
        [
            ("x = 6", "Despejó el 6 pero no dividió por el coeficiente 3."),
            ("x = 3", "Reemplazó el valor en el término equivocado."),
            ("x = 4", "Ignoró el término 2y al despejar."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "¿Cuál es la solución de (2x − 1)/4 = (x + 3)/3?",
        "x = 7,5",
        "Con una fracción a cada lado, se multiplica en cruz.\n\n"
        "1) Multiplica en cruz: 3(2x − 1) = 4(x + 3).\n"
        "2) Distribuye: 6x − 3 = 4x + 12.\n"
        "3) Resta 4x y suma 3: 2x = 15.\n"
        "4) Divide por 2: x = 7,5. Verifica: (15 − 1)/4 = 3,5 y (7,5 + 3)/3 = 3,5.",
        [
            ("x = 15", "Agrupó correctamente pero no dividió por el coeficiente final."),
            ("x = 4", "Multiplicó en cruz sin distribuir sobre los términos numéricos."),
            ("x = 2", "Igualó numeradores entre sí y denominadores entre sí."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "Ana tiene el triple de la edad de Beto. Juntos suman 48 años. ¿Cuántos años tiene Beto?",
        "12 años",
        "Conviene llamar incógnita a la cantidad menor.\n\n"
        "1) Llama b a la edad de Beto. La de Ana es 3b.\n"
        "2) La suma es 48: b + 3b = 48.\n"
        "3) Reduce: 4b = 48.\n"
        "4) Divide por 4: b = 12. Ana tiene 36, y 12 + 36 = 48. Correcto.",
        [
            ("36 años", "Calculó la edad de Ana en lugar de la de Beto."),
            ("16 años", "Dividió 48 por 3 en vez de por la suma de las partes."),
            ("24 años", "Repartió la suma en dos partes iguales, ignorando que una es el triple de la otra."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "¿Cuál es el conjunto solución de la inecuación (x + 5)/2 ≤ x − 1?",
        "x ≥ 7",
        "Primero se elimina el denominador y después se agrupa.\n\n"
        "1) Multiplica ambos lados por 2, que es positivo, así que el sentido no "
        "cambia: x + 5 ≤ 2(x − 1).\n"
        "2) Distribuye: x + 5 ≤ 2x − 2.\n"
        "3) Resta x y suma 2: 7 ≤ x.\n"
        "4) Escrito con la incógnita a la izquierda, eso es x ≥ 7. Comprueba con "
        "x = 7: a la izquierda 6 y a la derecha 6.",
        [
            ("x ≤ 7", "Dio vuelta la desigualdad al reescribirla con la x a la izquierda."),
            ("x ≥ 3", "Multiplicó por 2 solo el lado izquierdo."),
            ("x ≥ 1", "Distribuyó el 2 solo sobre la x y no sobre el −1."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "Un número más su tercera parte es igual a 32. ¿Cuál es el número?",
        "24",
        "Se plantea la ecuación con la fracción y se elimina el denominador.\n\n"
        "1) Llama n al número. Su tercera parte es n/3.\n"
        "2) La ecuación es n + n/3 = 32.\n"
        "3) Multiplica todo por 3: 3n + n = 96, o sea 4n = 96.\n"
        "4) Divide por 4: n = 24. Verifica: 24 + 8 = 32. Correcto.",
        [
            ("96", "Multiplicó por 3 pero no dividió por el coeficiente 4."),
            ("10,7", "Dividió 32 por 3, respondiendo cuál es la tercera parte."),
            ("8", "Calculó la tercera parte del número en lugar del número mismo."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "¿Cuál es la solución de 5(x − 2) − 3(x + 1) = 7?",
        "x = 10",
        "Hay que distribuir los dos paréntesis cuidando el signo del segundo.\n\n"
        "1) Primer paréntesis: 5x − 10.\n"
        "2) Segundo paréntesis: el −3 multiplica a ambos términos, dando −3x − 3.\n"
        "3) Junta y reduce: 5x − 10 − 3x − 3 = 2x − 13. La ecuación es 2x − 13 = 7.\n"
        "4) Suma 13 y divide por 2: 2x = 20, entonces x = 10. Verifica: "
        "5 · 8 − 3 · 11 = 40 − 33 = 7.",
        [
            ("x = 7", "No cambió el signo del +1 al distribuir el −3, obteniendo 2x − 7."),
            ("x = 20", "Agrupó bien pero no dividió por el coeficiente final."),
            ("x = −3", "Restó el 13 en lugar de sumarlo al despejar."),
        ],
    ),
    _q(
        "alg_lineal", "dificil",
        "Si al doble de un número se le resta 9, se obtiene el mismo número aumentado en 4. ¿Cuál es el número?",
        "13",
        "Ambos lados de la ecuación describen la misma cantidad de formas distintas.\n\n"
        "1) Llama n al número. 'El doble menos 9' es 2n − 9.\n"
        "2) 'El mismo número aumentado en 4' es n + 4.\n"
        "3) Iguala: 2n − 9 = n + 4.\n"
        "4) Resta n y suma 9: n = 13. Verifica: el doble de 13 menos 9 es 17, y "
        "13 + 4 también es 17.",
        [
            ("5", "Restó el 4 en lugar de sumarlo al despejar."),
            ("26", "Calculó el doble del número en lugar del número."),
            ("2,5", "Sumó los términos con n en vez de restarlos al agrupar."),
        ],
    ),
    # ---------- alg_sistemas ----------
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema x + y = 9 ; x − y = 3?",
        "x = 6, y = 3",
        "Cuando una incógnita aparece sumando en una ecuación y restando en la otra, "
        "conviene sumar ambas ecuaciones.\n\n"
        "1) Suma las dos ecuaciones término a término: (x + y) + (x − y) = 9 + 3. "
        "Las y se cancelan y queda 2x = 12.\n"
        "2) Divide por 2: x = 6.\n"
        "3) Reemplaza en la primera ecuación: 6 + y = 9, entonces y = 3.\n"
        "4) Verifica en la segunda: 6 − 3 = 3. Correcto.",
        [
            ("x = 3, y = 6", "Intercambió los valores de las incógnitas al final."),
            ("x = 12, y = 3", "Sumó las ecuaciones pero no dividió por 2 al despejar."),
            ("x = 4,5, y = 4,5", "Repartió el 9 en partes iguales, ignorando la segunda ecuación."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema x + y = 20 ; x = 3y?",
        "x = 15, y = 5",
        "Cuando una incógnita ya está despejada, lo más rápido es sustituir.\n\n"
        "1) La segunda ecuación dice que x vale 3y. Reemplázalo en la primera: "
        "3y + y = 20.\n"
        "2) Reduce: 4y = 20.\n"
        "3) Divide por 4: y = 5.\n"
        "4) Vuelve a la sustitución: x = 3 · 5 = 15. Verifica: 15 + 5 = 20.",
        [
            ("x = 5, y = 15", "Intercambió los valores: x debe ser el triple, no la tercera parte."),
            ("x = 10, y = 10", "Repartió el total en partes iguales, ignorando la relación de triple."),
            ("x = 6,7, y = 13,3", "Dividió 20 por 3 en lugar de por la suma de las partes."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema x + y = 8 ; 2x + y = 13?",
        "x = 5, y = 3",
        "Como la y tiene el mismo coeficiente en ambas ecuaciones, conviene "
        "restarlas.\n\n"
        "1) Resta la primera de la segunda: (2x + y) − (x + y) = 13 − 8. Las y se "
        "cancelan y queda x = 5.\n"
        "2) Reemplaza en la primera: 5 + y = 8, entonces y = 3.\n"
        "3) Verifica en la segunda: 2 · 5 + 3 = 13. Correcto.",
        [
            ("x = 3, y = 5", "Intercambió los valores de las incógnitas."),
            ("x = 21, y = −13", "Sumó las ecuaciones en lugar de restarlas, sin cancelar nada."),
            ("x = 5, y = 8", "Encontró bien la x pero no la reemplazó para calcular la y."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema y = 2x ; x + y = 15?",
        "x = 5, y = 10",
        "La primera ecuación entrega la y ya despejada, así que se sustituye.\n\n"
        "1) Reemplaza y por 2x en la segunda: x + 2x = 15.\n"
        "2) Reduce: 3x = 15.\n"
        "3) Divide por 3: x = 5.\n"
        "4) Calcula la y: y = 2 · 5 = 10. Verifica: 5 + 10 = 15.",
        [
            ("x = 10, y = 5", "Intercambió los valores: la y debe ser el doble de la x."),
            ("x = 7,5, y = 15", "Repartió el total en dos partes iguales, ignorando la relación de doble."),
            ("x = 15, y = 30", "Usó el total como valor de x sin resolver el sistema."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "La suma de dos números es 24 y su diferencia es 6. ¿Cuáles son los números, del mayor al menor?",
        "15 y 9",
        "Se plantea un sistema con la suma y la diferencia.\n\n"
        "1) Llama x al mayor e y al menor: x + y = 24 y x − y = 6.\n"
        "2) Suma las dos ecuaciones: 2x = 30, entonces x = 15.\n"
        "3) Reemplaza: 15 + y = 24, entonces y = 9.\n"
        "4) Verifica: suman 24 y se diferencian en 6. Correcto.",
        [
            ("18 y 6", "Tomó la diferencia como si fuera directamente el número menor."),
            ("12 y 12", "Repartió la suma en partes iguales, ignorando la diferencia."),
            ("16 y 8", "Buscó números que se diferenciaran en 8 en lugar de en 6."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 3x + y = 14 ; x + y = 6?",
        "x = 4, y = 2",
        "La y tiene el mismo coeficiente en ambas ecuaciones, así que se eliminan "
        "restando.\n\n"
        "1) Resta la segunda de la primera: (3x + y) − (x + y) = 14 − 6. Queda "
        "2x = 8.\n"
        "2) Divide por 2: x = 4.\n"
        "3) Reemplaza en la segunda: 4 + y = 6, entonces y = 2.\n"
        "4) Verifica en la primera: 3 · 4 + 2 = 14. Correcto.",
        [
            ("x = 8, y = −2", "Restó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 2, y = 4", "Intercambió los valores de las incógnitas."),
            ("x = 5, y = 1", "Sumó las ecuaciones en lugar de restarlas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 2x + 3y = 16 ; x − y = 3?",
        "x = 5, y = 2",
        "Conviene despejar de la ecuación más simple y sustituir.\n\n"
        "1) De la segunda ecuación: x = y + 3.\n"
        "2) Reemplaza en la primera: 2(y + 3) + 3y = 16.\n"
        "3) Distribuye y reduce: 2y + 6 + 3y = 16, o sea 5y = 10, entonces y = 2.\n"
        "4) Calcula la x: x = 2 + 3 = 5. Verifica: 2 · 5 + 3 · 2 = 16.",
        [
            ("x = 2, y = 5", "Intercambió los valores de las incógnitas."),
            ("x = 8, y = 5", "Despejó x = y − 3 en vez de x = y + 3, cambiando el signo."),
            ("x = 3, y = 0", "Tomó la diferencia de la segunda ecuación como valor directo de x."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 4x − y = 10 ; 2x + y = 8?",
        "x = 3, y = 2",
        "La y aparece restando en una ecuación y sumando en la otra: se suman.\n\n"
        "1) Suma las dos ecuaciones: (4x − y) + (2x + y) = 10 + 8. Las y se cancelan "
        "y queda 6x = 18.\n"
        "2) Divide por 6: x = 3.\n"
        "3) Reemplaza en la segunda: 2 · 3 + y = 8, entonces y = 2.\n"
        "4) Verifica en la primera: 4 · 3 − 2 = 10. Correcto.",
        [
            ("x = 18, y = 2", "Sumó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 1, y = 6", "Restó las ecuaciones en lugar de sumarlas, sin cancelar la y."),
            ("x = 2, y = 3", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema x + 2y = 11 ; 3x − 2y = 9?",
        "x = 5, y = 3",
        "Los términos en y son opuestos, así que sumando se eliminan.\n\n"
        "1) Suma ambas ecuaciones: (x + 2y) + (3x − 2y) = 11 + 9. Queda 4x = 20.\n"
        "2) Divide por 4: x = 5.\n"
        "3) Reemplaza en la primera: 5 + 2y = 11, entonces 2y = 6 e y = 3.\n"
        "4) Verifica en la segunda: 3 · 5 − 2 · 3 = 9. Correcto.",
        [
            ("x = 20, y = 3", "Sumó las ecuaciones pero olvidó dividir por 4."),
            ("x = 5, y = 6", "Despejó 2y = 6 y no dividió por 2 para obtener la y."),
            ("x = 3, y = 5", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "En una librería, 2 cuadernos y 3 lápices cuestan $4.300, mientras que 1 cuaderno y 2 lápices cuestan $2.400. ¿Cuánto cuesta un cuaderno?",
        "$1.400",
        "Cada tipo de artículo es una incógnita.\n\n"
        "1) Llama c al precio del cuaderno y l al del lápiz: 2c + 3l = 4.300 y "
        "c + 2l = 2.400.\n"
        "2) De la segunda ecuación despeja c = 2.400 − 2l.\n"
        "3) Reemplaza en la primera: 2(2.400 − 2l) + 3l = 4.300, o sea "
        "4.800 − 4l + 3l = 4.300. Queda −l = −500, entonces l = 500.\n"
        "4) Calcula el cuaderno: c = 2.400 − 2 · 500 = 1.400. Verifica: "
        "2 · 1.400 + 3 · 500 = 4.300.",
        [
            ("$500", "Entregó el precio del lápiz en lugar del cuaderno."),
            ("$1.900", "Restó los dos totales sin considerar las cantidades de cada artículo."),
            ("$2.150", "Dividió el primer total por 2, como si los 4.300 fueran solo cuadernos."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 5x + 2y = 24 ; 3x − 2y = 8?",
        "x = 4, y = 2",
        "Los términos en y son opuestos, así que se eliminan sumando.\n\n"
        "1) Suma ambas ecuaciones: 8x = 32.\n"
        "2) Divide por 8: x = 4.\n"
        "3) Reemplaza en la primera: 5 · 4 + 2y = 24, o sea 20 + 2y = 24, entonces "
        "2y = 4 e y = 2.\n"
        "4) Verifica en la segunda: 3 · 4 − 2 · 2 = 8. Correcto.",
        [
            ("x = 32, y = 2", "Sumó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 4, y = 4", "Despejó 2y = 4 y no dividió por 2."),
            ("x = 2, y = 4", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "En un estacionamiento hay autos y motos. En total se cuentan 20 vehículos y 70 ruedas. ¿Cuántos autos hay?",
        "15 autos",
        "Se plantea una ecuación por vehículos y otra por ruedas.\n\n"
        "1) Llama a a los autos y m a las motos: a + m = 20.\n"
        "2) Cada auto tiene 4 ruedas y cada moto 2: 4a + 2m = 70.\n"
        "3) De la primera, m = 20 − a. Reemplaza: 4a + 2(20 − a) = 70, o sea "
        "4a + 40 − 2a = 70. Queda 2a = 30.\n"
        "4) Divide por 2: a = 15. Hay 15 autos y 5 motos, que suman "
        "60 + 10 = 70 ruedas.",
        [
            ("5 autos", "Entregó la cantidad de motos en lugar de la de autos."),
            ("10 autos", "Repartió los vehículos en partes iguales, sin usar el dato de las ruedas."),
            ("17,5 autos", "Dividió las 70 ruedas por 4 sin considerar las motos."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 6x + y = 20 ; 2x + y = 8?",
        "x = 3, y = 2",
        "La y tiene igual coeficiente en ambas ecuaciones, así que se elimina "
        "restando.\n\n"
        "1) Resta la segunda de la primera: 4x = 12.\n"
        "2) Divide por 4: x = 3.\n"
        "3) Reemplaza en la segunda: 2 · 3 + y = 8, entonces y = 2.\n"
        "4) Verifica en la primera: 6 · 3 + 2 = 20. Correcto.",
        [
            ("x = 12, y = 2", "Restó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 3,5, y = 1", "Sumó las ecuaciones en lugar de restarlas."),
            ("x = 2, y = 3", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema x − y = 5 ; x + y = 11?",
        "x = 8, y = 3",
        "Sumando ambas ecuaciones se elimina la y.\n\n"
        "1) Suma término a término: 2x = 16.\n"
        "2) Divide por 2: x = 8.\n"
        "3) Reemplaza en la segunda: 8 + y = 11, entonces y = 3.\n"
        "4) Verifica en la primera: 8 − 3 = 5. Correcto.",
        [
            ("x = 3, y = 8", "Intercambió los valores de las incógnitas."),
            ("x = 16, y = 3", "Sumó las ecuaciones pero no dividió por 2."),
            ("x = 5,5, y = 5,5", "Repartió el 11 en partes iguales, ignorando la diferencia."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es la solución del sistema 3x + 2y = 19 ; 2x + 3y = 16?",
        "x = 5, y = 2",
        "Ningún coeficiente se cancela directamente, así que conviene igualarlos "
        "primero.\n\n"
        "1) Multiplica la primera por 3 y la segunda por 2: 9x + 6y = 57 y "
        "4x + 6y = 32.\n"
        "2) Resta la segunda de la primera: 5x = 25, entonces x = 5.\n"
        "3) Reemplaza en la primera original: 3 · 5 + 2y = 19, o sea 15 + 2y = 19, "
        "entonces 2y = 4 e y = 2.\n"
        "4) Verifica en la segunda: 2 · 5 + 3 · 2 = 16. Correcto.",
        [
            ("x = 2, y = 5", "Intercambió los valores de las incógnitas."),
            ("x = 3,5, y = 3,5", "Sumó ambas ecuaciones y repartió el resultado en partes iguales."),
            ("x = 25, y = 2", "Eliminó bien una incógnita pero no dividió por el coeficiente resultante."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es la solución del sistema x/2 + y = 7 ; x + y = 10?",
        "x = 6, y = 4",
        "Primero conviene quitar el denominador de la primera ecuación.\n\n"
        "1) Multiplica la primera ecuación por 2: x + 2y = 14.\n"
        "2) Resta la segunda: (x + 2y) − (x + y) = 14 − 10. Queda y = 4.\n"
        "3) Reemplaza en la segunda: x + 4 = 10, entonces x = 6.\n"
        "4) Verifica en la primera original: 6/2 + 4 = 3 + 4 = 7. Correcto.",
        [
            ("x = 4, y = 6", "Intercambió los valores de las incógnitas."),
            ("x = 3, y = 7", "Trató x/2 como si fuera x, sin eliminar el denominador."),
            ("x = 14, y = 0", "Multiplicó por 2 solo un término de la primera ecuación."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "De dos números, el mayor excede al menor en 8 y su suma es 34. ¿Cuáles son, del mayor al menor?",
        "21 y 13",
        "'Excede en 8' significa que la diferencia entre ambos es 8.\n\n"
        "1) Llama x al mayor e y al menor: x − y = 8 y x + y = 34.\n"
        "2) Suma ambas ecuaciones: 2x = 42, entonces x = 21.\n"
        "3) Reemplaza: 21 + y = 34, entonces y = 13.\n"
        "4) Verifica: 21 − 13 = 8 y 21 + 13 = 34. Correcto.",
        [
            ("26 y 8", "Tomó el 8 como si fuera directamente el número menor."),
            ("17 y 17", "Repartió la suma en partes iguales, ignorando el exceso."),
            ("13 y 21", "Encontró los números correctos pero los entregó en el orden inverso."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es la solución del sistema 4x + 3y = 27 ; 2x − y = 1?",
        "x = 3, y = 5",
        "La segunda ecuación permite despejar la y con facilidad.\n\n"
        "1) De la segunda: y = 2x − 1.\n"
        "2) Reemplaza en la primera: 4x + 3(2x − 1) = 27.\n"
        "3) Distribuye y reduce: 4x + 6x − 3 = 27, o sea 10x = 30, entonces x = 3.\n"
        "4) Calcula la y: y = 2 · 3 − 1 = 5. Verifica: 4 · 3 + 3 · 5 = 27.",
        [
            ("x = 5, y = 3", "Intercambió los valores de las incógnitas."),
            ("x = 2,4, y = 3,8", "Despejó y = 2x + 1, cambiando el signo del término independiente."),
            ("x = 3, y = 7", "Calculó la y reemplazando en la ecuación equivocada."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "En una función de teatro las entradas de adulto cuestan $5.000 y las de niño $3.000. Se vendieron 40 entradas y se recaudaron $164.000. ¿Cuántas entradas de adulto se vendieron?",
        "22 entradas",
        "Una ecuación cuenta entradas y la otra cuenta dinero.\n\n"
        "1) Llama a a las entradas de adulto y n a las de niño: a + n = 40.\n"
        "2) Por la recaudación: 5.000a + 3.000n = 164.000.\n"
        "3) De la primera, n = 40 − a. Reemplaza: 5.000a + 3.000(40 − a) = 164.000, "
        "o sea 5.000a + 120.000 − 3.000a = 164.000.\n"
        "4) Queda 2.000a = 44.000, entonces a = 22. Se vendieron 22 de adulto y 18 de "
        "niño, que recaudan 110.000 + 54.000 = 164.000.",
        [
            ("18 entradas", "Entregó la cantidad de entradas de niño en lugar de las de adulto."),
            ("20 entradas", "Repartió las 40 entradas en partes iguales, sin usar la recaudación."),
            ("32,8 entradas", "Dividió la recaudación total por 5.000, como si todas fueran de adulto."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es el valor de x − y si x + y = 14 y x − 2y = 2?",
        "6",
        "Primero se resuelve el sistema y después se calcula lo que se pide.\n\n"
        "1) De la primera ecuación: x = 14 − y.\n"
        "2) Reemplaza en la segunda: (14 − y) − 2y = 2, o sea 14 − 3y = 2.\n"
        "3) Despeja: 3y = 12, entonces y = 4, y por lo tanto x = 10.\n"
        "4) La pregunta pide x − y: 10 − 4 = 6.",
        [
            ("10", "Entregó el valor de x en lugar de la diferencia pedida."),
            ("14", "Entregó la suma de las incógnitas en vez de su diferencia."),
            ("4", "Entregó el valor de y en lugar de la diferencia."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "Si 2x + y = 9 y x + 2y = 9, ¿cuál es el valor de x + y?",
        "6",
        "No hace falta resolver el sistema completo: basta con sumar las ecuaciones.\n\n"
        "1) Suma ambas ecuaciones: (2x + y) + (x + 2y) = 9 + 9, o sea 3x + 3y = 18.\n"
        "2) Saca factor común 3: 3(x + y) = 18.\n"
        "3) Divide por 3: x + y = 6.\n"
        "4) Comprobación: por la simetría del sistema, x = y = 3, y en efecto suman 6.",
        [
            ("18", "Sumó las ecuaciones pero no dividió por 3 al factorizar."),
            ("9", "Entregó el término independiente de una de las ecuaciones."),
            ("3", "Calculó el valor de una incógnita en lugar de la suma de ambas."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema x + y = 12 ; y = x + 4?",
        "x = 4, y = 8",
        "La segunda ecuación ya entrega la y despejada.\n\n"
        "1) Reemplaza y por x + 4 en la primera: x + (x + 4) = 12.\n"
        "2) Reduce: 2x + 4 = 12, entonces 2x = 8.\n"
        "3) Divide por 2: x = 4.\n"
        "4) Calcula la y: y = 4 + 4 = 8. Verifica: 4 + 8 = 12.",
        [
            ("x = 8, y = 4", "Intercambió los valores: la y debe ser la mayor por el +4."),
            ("x = 6, y = 6", "Repartió el total en partes iguales, ignorando la segunda ecuación."),
            ("x = 8, y = 12", "Usó el total como valor de y sin resolver el sistema."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema 2x + y = 10 ; y = 4?",
        "x = 3, y = 4",
        "Una de las incógnitas ya viene dada, así que basta reemplazarla.\n\n"
        "1) Sustituye y = 4 en la primera ecuación: 2x + 4 = 10.\n"
        "2) Resta 4: 2x = 6.\n"
        "3) Divide por 2: x = 3.\n"
        "4) Verifica: 2 · 3 + 4 = 10. Correcto.",
        [
            ("x = 6, y = 4", "Despejó el 4 pero no dividió por el coeficiente 2."),
            ("x = 5, y = 4", "Dividió el 10 por 2 sin restar antes el valor de y."),
            ("x = 4, y = 3", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema x + y = 30 ; x − y = 10?",
        "x = 20, y = 10",
        "Con una suma y una diferencia, sumar las ecuaciones elimina la y.\n\n"
        "1) Suma término a término: 2x = 40.\n"
        "2) Divide por 2: x = 20.\n"
        "3) Reemplaza en la primera: 20 + y = 30, entonces y = 10.\n"
        "4) Verifica en la segunda: 20 − 10 = 10. Correcto.",
        [
            ("x = 10, y = 20", "Intercambió los valores de las incógnitas."),
            ("x = 40, y = 10", "Sumó las ecuaciones pero no dividió por 2."),
            ("x = 15, y = 15", "Repartió la suma en partes iguales, ignorando la diferencia."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema y = x − 3 ; x + y = 17?",
        "x = 10, y = 7",
        "La primera ecuación entrega la y en función de x.\n\n"
        "1) Reemplaza en la segunda: x + (x − 3) = 17.\n"
        "2) Reduce: 2x − 3 = 17, entonces 2x = 20.\n"
        "3) Divide por 2: x = 10.\n"
        "4) Calcula la y: y = 10 − 3 = 7. Verifica: 10 + 7 = 17.",
        [
            ("x = 7, y = 10", "Intercambió los valores: la y debe ser la menor por el −3."),
            ("x = 8,5, y = 8,5", "Repartió el total en partes iguales, ignorando la primera ecuación."),
            ("x = 20, y = 17", "No dividió por 2 tras agrupar los términos con x."),
        ],
    ),
    _q(
        "alg_sistemas", "facil",
        "¿Cuál es la solución del sistema 3x = y ; x + y = 16?",
        "x = 4, y = 12",
        "La primera ecuación dice que y es el triple de x.\n\n"
        "1) Reemplaza y por 3x en la segunda: x + 3x = 16.\n"
        "2) Reduce: 4x = 16.\n"
        "3) Divide por 4: x = 4.\n"
        "4) Calcula la y: y = 3 · 4 = 12. Verifica: 4 + 12 = 16.",
        [
            ("x = 12, y = 4", "Intercambió los valores: la y es el triple, no la tercera parte."),
            ("x = 8, y = 8", "Repartió el total en partes iguales, ignorando la relación de triple."),
            ("x = 5,3, y = 16", "Dividió el total por 3 en lugar de por la suma de las partes."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 2x − y = 7 ; x + y = 8?",
        "x = 5, y = 3",
        "La y aparece restando en una ecuación y sumando en la otra: se suman.\n\n"
        "1) Suma ambas ecuaciones: 3x = 15.\n"
        "2) Divide por 3: x = 5.\n"
        "3) Reemplaza en la segunda: 5 + y = 8, entonces y = 3.\n"
        "4) Verifica en la primera: 2 · 5 − 3 = 7. Correcto.",
        [
            ("x = 15, y = 3", "Sumó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 3, y = 5", "Intercambió los valores de las incógnitas."),
            ("x = 1, y = 7", "Restó las ecuaciones en lugar de sumarlas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 3x + 4y = 26 ; x − 2y = 2?",
        "x = 6, y = 2",
        "Conviene despejar de la segunda ecuación y sustituir.\n\n"
        "1) De la segunda: x = 2y + 2.\n"
        "2) Reemplaza en la primera: 3(2y + 2) + 4y = 26.\n"
        "3) Distribuye y reduce: 6y + 6 + 4y = 26, o sea 10y = 20, entonces y = 2.\n"
        "4) Calcula la x: x = 2 · 2 + 2 = 6. Verifica: 3 · 6 + 4 · 2 = 26.",
        [
            ("x = 2, y = 6", "Intercambió los valores de las incógnitas."),
            ("x = 10, y = 4", "Despejó x = 2y − 2, cambiando el signo del término independiente."),
            ("x = 26, y = 2", "Encontró bien la y pero no la reemplazó para obtener la x."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 5x − 2y = 11 ; 3x + 2y = 13?",
        "x = 3, y = 2",
        "Los términos en y son opuestos: se eliminan sumando.\n\n"
        "1) Suma ambas ecuaciones: 8x = 24.\n"
        "2) Divide por 8: x = 3.\n"
        "3) Reemplaza en la segunda: 3 · 3 + 2y = 13, o sea 9 + 2y = 13, entonces "
        "2y = 4 e y = 2.\n"
        "4) Verifica en la primera: 5 · 3 − 2 · 2 = 11. Correcto.",
        [
            ("x = 24, y = 2", "Sumó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 3, y = 4", "Despejó 2y = 4 y no dividió por 2."),
            ("x = 2, y = 3", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema x + 3y = 14 ; 2x − 3y = 1?",
        "x = 5, y = 3",
        "Los términos en y son opuestos, así que sumando desaparecen.\n\n"
        "1) Suma ambas ecuaciones: 3x = 15.\n"
        "2) Divide por 3: x = 5.\n"
        "3) Reemplaza en la primera: 5 + 3y = 14, o sea 3y = 9, entonces y = 3.\n"
        "4) Verifica en la segunda: 2 · 5 − 3 · 3 = 1. Correcto.",
        [
            ("x = 15, y = 3", "Sumó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 5, y = 9", "Despejó 3y = 9 y no dividió por 3."),
            ("x = 3, y = 5", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "En un almacén, 2 kilos de pan y 3 litros de leche cuestan $6.500. Un kilo de pan y un litro de leche cuestan $2.700. ¿Cuánto cuesta un litro de leche?",
        "$1.100",
        "Cada producto es una incógnita distinta.\n\n"
        "1) Llama p al kilo de pan y l al litro de leche: 2p + 3l = 6.500 y "
        "p + l = 2.700.\n"
        "2) De la segunda: p = 2.700 − l.\n"
        "3) Reemplaza en la primera: 2(2.700 − l) + 3l = 6.500, o sea "
        "5.400 − 2l + 3l = 6.500.\n"
        "4) Queda 5.400 + l = 6.500, entonces l = 1.100. El pan cuesta 1.600, y "
        "2 · 1.600 + 3 · 1.100 = 6.500.",
        [
            ("$1.600", "Entregó el precio del kilo de pan en lugar del litro de leche."),
            ("$1.350", "Repartió los $2.700 en partes iguales entre ambos productos."),
            ("$3.800", "Restó los dos totales sin considerar las cantidades de cada producto."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema 4x + y = 17 ; 2x + y = 11?",
        "x = 3, y = 5",
        "La y tiene el mismo coeficiente en ambas ecuaciones, así que se elimina "
        "restando.\n\n"
        "1) Resta la segunda de la primera: 2x = 6.\n"
        "2) Divide por 2: x = 3.\n"
        "3) Reemplaza en la segunda: 2 · 3 + y = 11, entonces y = 5.\n"
        "4) Verifica en la primera: 4 · 3 + 5 = 17. Correcto.",
        [
            ("x = 6, y = 5", "Restó las ecuaciones pero no dividió por el coeficiente resultante."),
            ("x = 4,7, y = 14", "Sumó las ecuaciones en lugar de restarlas."),
            ("x = 5, y = 3", "Intercambió los valores de las incógnitas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "En una granja hay ovejas y patos. Se cuentan 25 cabezas y 80 patas. ¿Cuántos patos hay?",
        "10 patos",
        "Una ecuación cuenta cabezas y la otra cuenta patas.\n\n"
        "1) Llama o a las ovejas y p a los patos: o + p = 25.\n"
        "2) Las ovejas tienen 4 patas y los patos 2: 4o + 2p = 80.\n"
        "3) De la primera, o = 25 − p. Reemplaza: 4(25 − p) + 2p = 80, o sea "
        "100 − 4p + 2p = 80.\n"
        "4) Queda 100 − 2p = 80, entonces 2p = 20 y p = 10. Hay 15 ovejas y 10 patos: "
        "60 + 20 = 80 patas.",
        [
            ("15 patos", "Entregó la cantidad de ovejas en lugar de la de patos."),
            ("40 patos", "Dividió las 80 patas por 2 sin considerar a las ovejas."),
            ("12,5 patos", "Repartió las cabezas en partes iguales, sin usar el dato de las patas."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es la solución del sistema 2x + 3y = 17 ; 5x − 2y = 14?",
        "x = 4, y = 3",
        "Ningún coeficiente se cancela solo, así que hay que igualarlos primero.\n\n"
        "1) Multiplica la primera por 2 y la segunda por 3: 4x + 6y = 34 y "
        "15x − 6y = 42.\n"
        "2) Suma ambas: 19x = 76, entonces x = 4.\n"
        "3) Reemplaza en la primera original: 2 · 4 + 3y = 17, o sea 8 + 3y = 17, "
        "entonces 3y = 9 e y = 3.\n"
        "4) Verifica en la segunda: 5 · 4 − 2 · 3 = 14. Correcto.",
        [
            ("x = 3, y = 4", "Intercambió los valores de las incógnitas."),
            ("x = 76, y = 3", "Eliminó bien una incógnita pero no dividió por el coeficiente resultante."),
            ("x = 4, y = 9", "Despejó 3y = 9 y no dividió por 3."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es la solución del sistema x/3 + y = 5 ; x + y = 9?",
        "x = 6, y = 3",
        "Primero se elimina el denominador de la primera ecuación.\n\n"
        "1) Multiplica la primera por 3: x + 3y = 15.\n"
        "2) Resta la segunda: (x + 3y) − (x + y) = 15 − 9, o sea 2y = 6.\n"
        "3) Divide por 2: y = 3.\n"
        "4) Reemplaza en la segunda: x + 3 = 9, entonces x = 6. Verifica en la "
        "primera original: 6/3 + 3 = 2 + 3 = 5.",
        [
            ("x = 3, y = 6", "Intercambió los valores de las incógnitas."),
            ("x = 4, y = 5", "Trató x/3 como si fuera x, sin eliminar el denominador."),
            ("x = 15, y = 0", "Multiplicó por 3 solo un término de la primera ecuación."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "La suma de dos números es 40 y uno de ellos es 4 veces el otro. ¿Cuáles son, del mayor al menor?",
        "32 y 8",
        "Conviene llamar incógnita al número menor.\n\n"
        "1) Llama y al menor. El mayor es 4y.\n"
        "2) La suma es 40: y + 4y = 40.\n"
        "3) Reduce: 5y = 40, entonces y = 8.\n"
        "4) El mayor es 4 · 8 = 32. Verifica: 32 + 8 = 40 y 32 es 4 veces 8.",
        [
            ("8 y 32", "Encontró los números correctos pero los entregó en el orden inverso."),
            ("20 y 20", "Repartió la suma en partes iguales, ignorando la relación."),
            ("30 y 10", "Dividió el total por 4 en lugar de por la suma de las partes."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "¿Cuál es la solución del sistema 5x + 3y = 29 ; 2x − y = 5?",
        "x = 4, y = 3",
        "La segunda ecuación permite despejar la y directamente.\n\n"
        "1) De la segunda: y = 2x − 5.\n"
        "2) Reemplaza en la primera: 5x + 3(2x − 5) = 29.\n"
        "3) Distribuye y reduce: 5x + 6x − 15 = 29, o sea 11x = 44, entonces x = 4.\n"
        "4) Calcula la y: y = 2 · 4 − 5 = 3. Verifica: 5 · 4 + 3 · 3 = 29.",
        [
            ("x = 3, y = 4", "Intercambió los valores de las incógnitas."),
            ("x = 4, y = 13", "Despejó y = 2x + 5, cambiando el signo del término independiente."),
            ("x = 44, y = 3", "Agrupó bien pero no dividió por el coeficiente resultante."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "En un cine, 3 entradas de adulto y 2 de niño cuestan $19.000. Una entrada de adulto y una de niño cuestan $7.000. ¿Cuánto cuesta una entrada de niño?",
        "$2.000",
        "Cada tipo de entrada es una incógnita.\n\n"
        "1) Llama a a la entrada de adulto y n a la de niño: 3a + 2n = 19.000 y "
        "a + n = 7.000.\n"
        "2) De la segunda: a = 7.000 − n.\n"
        "3) Reemplaza en la primera: 3(7.000 − n) + 2n = 19.000, o sea "
        "21.000 − 3n + 2n = 19.000.\n"
        "4) Queda 21.000 − n = 19.000, entonces n = 2.000. La de adulto cuesta 5.000, "
        "y 3 · 5.000 + 2 · 2.000 = 19.000.",
        [
            ("$5.000", "Entregó el precio de la entrada de adulto en lugar de la de niño."),
            ("$3.500", "Repartió los $7.000 en partes iguales entre ambos tipos de entrada."),
            ("$12.000", "Restó los dos totales sin considerar las cantidades de cada tipo."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es el valor de x · y si x + y = 9 y x − y = 1?",
        "20",
        "Primero se resuelve el sistema y después se calcula el producto.\n\n"
        "1) Suma ambas ecuaciones: 2x = 10, entonces x = 5.\n"
        "2) Reemplaza en la primera: 5 + y = 9, entonces y = 4.\n"
        "3) La pregunta pide el producto: 5 · 4 = 20.\n"
        "4) Verifica el sistema: 5 + 4 = 9 y 5 − 4 = 1. Correcto.",
        [
            ("9", "Entregó la suma de las incógnitas en lugar de su producto."),
            ("5", "Entregó el valor de x en vez del producto pedido."),
            ("1", "Entregó la diferencia de las incógnitas en lugar del producto."),
        ],
    ),
    _q(
        "alg_sistemas", "dificil",
        "Si 3x + y = 11 y x + 3y = 9, ¿cuál es el valor de x + y?",
        "5",
        "No hace falta resolver el sistema completo: basta sumar las ecuaciones.\n\n"
        "1) Suma ambas: (3x + y) + (x + 3y) = 11 + 9, o sea 4x + 4y = 20.\n"
        "2) Saca factor común 4: 4(x + y) = 20.\n"
        "3) Divide por 4: x + y = 5.\n"
        "4) Comprobación: resolviendo el sistema se obtiene x = 3 e y = 2, que en "
        "efecto suman 5.",
        [
            ("20", "Sumó las ecuaciones pero no dividió por 4 al factorizar."),
            ("11", "Entregó el término independiente de una de las ecuaciones."),
            ("3", "Calculó el valor de una incógnita en lugar de la suma de ambas."),
        ],
    ),
    _q(
        "alg_sistemas", "medio",
        "¿Cuál es la solución del sistema x + y = 18 ; x = y + 6?",
        "x = 12, y = 6",
        "La segunda ecuación entrega la x en función de y.\n\n"
        "1) Reemplaza en la primera: (y + 6) + y = 18.\n"
        "2) Reduce: 2y + 6 = 18, entonces 2y = 12.\n"
        "3) Divide por 2: y = 6.\n"
        "4) Calcula la x: x = 6 + 6 = 12. Verifica: 12 + 6 = 18 y 12 − 6 = 6.",
        [
            ("x = 6, y = 12", "Intercambió los valores: la x debe ser la mayor por el +6."),
            ("x = 9, y = 9", "Repartió el total en partes iguales, ignorando la segunda ecuación."),
            ("x = 24, y = 18", "No dividió por 2 tras agrupar los términos con y."),
        ],
    ),
    # ---------- alg_cuadratica ----------
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² − 36 = 0?",
        "x = 6 y x = −6",
        "Cuando falta el término con x, se despeja el cuadrado directamente.\n\n"
        "1) Suma 36 a ambos lados: x² = 36.\n"
        "2) Saca raíz cuadrada. Aquí está la clave: hay dos números cuyo cuadrado da "
        "36, el positivo y el negativo.\n"
        "3) Las soluciones son x = 6 y x = −6.\n"
        "4) Verifica la negativa: (−6)² − 36 = 36 − 36 = 0. Correcto.",
        [
            ("x = 6", "Consideró solo la raíz positiva; toda ecuación de este tipo tiene dos soluciones."),
            ("x = 18 y x = −18", "Dividió 36 por 2 en lugar de calcular su raíz cuadrada."),
            ("x = 36", "Despejó el término pero no aplicó la raíz cuadrada."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² = 81?",
        "x = 9 y x = −9",
        "La ecuación ya está despejada, solo falta la raíz.\n\n"
        "1) Aplica raíz cuadrada a ambos lados, recordando que hay dos valores "
        "posibles.\n"
        "2) Como 9 · 9 = 81 y también (−9) · (−9) = 81, ambos sirven.\n"
        "3) Las soluciones son x = 9 y x = −9.",
        [
            ("x = 9", "Olvidó la raíz negativa, que también cumple la ecuación."),
            ("x = 40,5 y x = −40,5", "Dividió por 2 en vez de calcular la raíz cuadrada."),
            ("x = 81 y x = −81", "No aplicó la raíz cuadrada al despejar."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² − 6x = 0?",
        "x = 0 y x = 6",
        "Cuando no hay término independiente, se factoriza sacando la x.\n\n"
        "1) Saca factor común x: x(x − 6) = 0.\n"
        "2) Un producto es cero cuando alguno de sus factores lo es. Entonces x = 0 o "
        "bien x − 6 = 0.\n"
        "3) Del segundo caso: x = 6.\n"
        "4) Las soluciones son 0 y 6. El error típico es dividir por x, que hace "
        "desaparecer la solución x = 0.",
        [
            ("x = 6", "Dividió toda la ecuación por x, perdiendo la solución x = 0."),
            ("x = 0", "Encontró una solución y no revisó el segundo factor."),
            ("x = 6 y x = −6", "Trató la ecuación como si fuera x² = 36."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² + 5x + 6 = 0?",
        "x = −2 y x = −3",
        "Se factoriza el trinomio y se iguala cada factor a cero.\n\n"
        "1) Busca dos números que multiplicados den 6 y sumados den 5: son 2 y 3.\n"
        "2) Factoriza: (x + 2)(x + 3) = 0.\n"
        "3) Iguala cada factor a cero: x + 2 = 0 da x = −2, y x + 3 = 0 da x = −3.\n"
        "4) Verifica la primera: (−2)² + 5(−2) + 6 = 4 − 10 + 6 = 0. Correcto.",
        [
            ("x = 2 y x = 3", "Copió los números de la factorización sin cambiarles el signo al despejar."),
            ("x = −1 y x = −6", "Eligió una pareja que multiplica 6 pero suma 7."),
            ("x = −5 y x = −6", "Usó directamente los coeficientes del enunciado."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² − 9x + 20 = 0?",
        "x = 4 y x = 5",
        "Ambos signos indican que los dos números buscados son negativos en la "
        "factorización.\n\n"
        "1) Busca dos números que multipliquen 20 y sumen −9: son −4 y −5.\n"
        "2) Factoriza: (x − 4)(x − 5) = 0.\n"
        "3) Iguala cada factor a cero: x = 4 y x = 5.\n"
        "4) Verifica: 4² − 9 · 4 + 20 = 16 − 36 + 20 = 0. Correcto.",
        [
            ("x = −4 y x = −5", "Copió los signos de la factorización sin invertirlos al despejar."),
            ("x = 2 y x = 10", "Eligió una pareja que multiplica 20 pero suma 12."),
            ("x = 9 y x = 20", "Usó directamente los coeficientes del enunciado."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² + 3x − 18 = 0?",
        "x = 3 y x = −6",
        "Con término independiente negativo, los dos números tienen signos "
        "distintos.\n\n"
        "1) Busca dos números que multipliquen −18 y sumen 3: son 6 y −3.\n"
        "2) Factoriza: (x + 6)(x − 3) = 0.\n"
        "3) Iguala cada factor a cero: x = −6 y x = 3.\n"
        "4) Verifica: 3² + 3 · 3 − 18 = 9 + 9 − 18 = 0. Correcto.",
        [
            ("x = −3 y x = 6", "Invirtió los signos de ambas soluciones."),
            ("x = 2 y x = −9", "Eligió una pareja que multiplica −18 pero suma −7."),
            ("x = 3 y x = 6", "Ignoró que el producto debe ser negativo, así que un factor debe serlo."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² − 2x − 8 = 0?",
        "x = 4 y x = −2",
        "Se factoriza buscando la pareja adecuada de números.\n\n"
        "1) Necesitas dos números que multipliquen −8 y sumen −2: son −4 y 2.\n"
        "2) Factoriza: (x − 4)(x + 2) = 0.\n"
        "3) Iguala cada factor a cero: x = 4 y x = −2.\n"
        "4) Verifica la segunda: (−2)² − 2(−2) − 8 = 4 + 4 − 8 = 0. Correcto.",
        [
            ("x = −4 y x = 2", "Invirtió los signos de ambas soluciones."),
            ("x = 8 y x = −1", "Eligió una pareja que multiplica −8 pero suma 7."),
            ("x = 2 y x = 4", "Ignoró que una de las soluciones debe ser negativa."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de 3x² − 12 = 0?",
        "x = 2 y x = −2",
        "Conviene simplificar antes de despejar.\n\n"
        "1) Suma 12: 3x² = 12.\n"
        "2) Divide por 3: x² = 4.\n"
        "3) Saca raíz cuadrada considerando ambos signos: x = 2 y x = −2.\n"
        "4) Verifica: 3 · 4 − 12 = 0 para los dos valores, porque el cuadrado elimina "
        "el signo.",
        [
            ("x = 4 y x = −4", "Despejó x² = 4 pero entregó ese valor sin sacarle la raíz."),
            ("x = 2", "Consideró solo la raíz positiva."),
            ("x = 6 y x = −6", "Dividió 12 por 2 en lugar de por el coeficiente 3."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² − 10x + 25 = 0?",
        "x = 5, una única solución",
        "Este trinomio es un cuadrado perfecto, y eso cambia el número de "
        "soluciones.\n\n"
        "1) Busca dos números que multipliquen 25 y sumen −10: ambos son −5.\n"
        "2) Factoriza: (x − 5)(x − 5) = 0, o sea (x − 5)² = 0.\n"
        "3) Al haber un solo factor distinto, hay una sola solución: x = 5.\n"
        "4) Se dice que es una raíz doble: la parábola toca el eje X en un único "
        "punto en lugar de cruzarlo.",
        [
            ("x = 5 y x = −5", "Trató la ecuación como una diferencia de cuadrados."),
            ("x = 10 y x = 25", "Usó directamente los coeficientes del enunciado."),
            ("x = −5, una única solución", "Copió el signo de la factorización sin invertirlo al despejar."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de 2x² − 5x − 3 = 0?",
        "x = 3 y x = −1/2",
        "Con coeficiente distinto de 1 conviene la fórmula general.\n\n"
        "1) Identifica a = 2, b = −5 y c = −3.\n"
        "2) Calcula el discriminante: b² − 4ac = 25 − 4 · 2 · (−3) = 25 + 24 = 49.\n"
        "3) Su raíz es 7. Aplica la fórmula: x = (5 ± 7)/(2 · 2) = (5 ± 7)/4.\n"
        "4) Las dos soluciones son (5 + 7)/4 = 3 y (5 − 7)/4 = −1/2.",
        [
            ("x = 3 y x = 1/2", "Perdió el signo negativo en la solución obtenida con la resta."),
            ("x = −3 y x = 1/2", "Invirtió el signo de ambas soluciones al aplicar la fórmula."),
            ("x = 5 y x = −3", "Usó los coeficientes b y c como si fueran las soluciones."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "El área de un rectángulo es 40 cm² y su largo mide 3 cm más que su ancho. ¿Cuánto mide el ancho?",
        "5 cm",
        "Se plantea el área en función de una sola incógnita.\n\n"
        "1) Llama a al ancho. El largo es a + 3.\n"
        "2) El área es largo por ancho: a(a + 3) = 40.\n"
        "3) Desarrolla y ordena: a² + 3a − 40 = 0.\n"
        "4) Factoriza buscando dos números que multipliquen −40 y sumen 3: son 8 y "
        "−5. Queda (a + 8)(a − 5) = 0, con soluciones a = −8 y a = 5. Una medida no "
        "puede ser negativa, así que el ancho es 5 cm (y el largo, 8 cm).",
        [
            ("8 cm", "Entregó la medida del largo en lugar del ancho."),
            ("−8 cm", "Eligió la solución negativa de la ecuación, imposible para una longitud."),
            ("20 cm", "Dividió el área por 2, como si fuera un perímetro."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "El cuadrado de un número, menos el triple de ese mismo número, es igual a 28. ¿Cuál es el número, si se sabe que es positivo?",
        "7",
        "Se traduce el enunciado a una ecuación cuadrática.\n\n"
        "1) Llama n al número: n² − 3n = 28.\n"
        "2) Pasa todo a un lado: n² − 3n − 28 = 0.\n"
        "3) Factoriza buscando dos números que multipliquen −28 y sumen −3: son −7 y "
        "4. Queda (n − 7)(n + 4) = 0.\n"
        "4) Las soluciones son 7 y −4. Como el enunciado pide el positivo, es 7. "
        "Verifica: 49 − 21 = 28.",
        [
            ("−4", "Eligió la solución negativa, descartada por el enunciado."),
            ("4", "Copió el signo de la factorización sin invertirlo al despejar."),
            ("28", "Entregó el resultado de la operación en lugar del número buscado."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Usando la fórmula general, ¿cuáles son las soluciones de x² − 4x − 12 = 0?",
        "x = 6 y x = −2",
        "La fórmula general sirve para cualquier ecuación cuadrática.\n\n"
        "1) Identifica a = 1, b = −4 y c = −12.\n"
        "2) Calcula el discriminante: b² − 4ac = 16 − 4 · 1 · (−12) = 16 + 48 = 64.\n"
        "3) Su raíz es 8. Aplica la fórmula: x = (4 ± 8)/2.\n"
        "4) Las soluciones son (4 + 8)/2 = 6 y (4 − 8)/2 = −2. Verifica: "
        "36 − 24 − 12 = 0.",
        [
            ("x = −6 y x = 2", "Invirtió el signo de b al aplicar la fórmula."),
            ("x = 6 y x = 2", "Perdió el signo negativo en la solución obtenida con la resta."),
            ("x = 2 y x = −8", "Restó 4ac en lugar de sumarlo, con c negativo, y calculó mal el discriminante."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuáles son las soluciones de 2x² + 7x + 3 = 0?",
        "x = −3 y x = −1/2",
        "Se aplica la fórmula general por tener coeficiente distinto de 1.\n\n"
        "1) Identifica a = 2, b = 7 y c = 3.\n"
        "2) Discriminante: 49 − 4 · 2 · 3 = 49 − 24 = 25, cuya raíz es 5.\n"
        "3) Fórmula: x = (−7 ± 5)/4.\n"
        "4) Las soluciones son (−7 + 5)/4 = −1/2 y (−7 − 5)/4 = −3. Ambas negativas, "
        "coherente con que todos los coeficientes sean positivos.",
        [
            ("x = 3 y x = 1/2", "Olvidó el signo negativo del −b en la fórmula."),
            ("x = −3 y x = −2", "Dividió por 2 en lugar de por 2a al final."),
            ("x = −7 y x = 3", "Usó los coeficientes b y c como si fueran las soluciones."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuántas soluciones reales tiene la ecuación x² − 6x + 9 = 0?",
        "Una única solución real (el discriminante vale 0)",
        "El discriminante decide cuántas soluciones reales hay.\n\n"
        "1) Identifica a = 1, b = −6 y c = 9.\n"
        "2) Calcula b² − 4ac = 36 − 36 = 0.\n"
        "3) Cuando el discriminante es cero, la raíz cuadrada aporta el mismo valor "
        "sumando y restando, así que las dos soluciones coinciden.\n"
        "4) Hay una única solución real, x = 3. Gráficamente, la parábola toca el eje "
        "X en un solo punto.",
        [
            ("Dos soluciones reales distintas", "Supuso que toda ecuación cuadrática tiene siempre dos soluciones distintas."),
            ("No tiene soluciones reales", "Confundió el caso de discriminante cero con el de discriminante negativo."),
            ("Infinitas soluciones", "Una ecuación cuadrática nunca tiene infinitas soluciones."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuántas soluciones reales tiene la ecuación 2x² + 3x + 5 = 0?",
        "Ninguna: el discriminante vale −31",
        "Se calcula el discriminante antes de intentar resolver.\n\n"
        "1) Identifica a = 2, b = 3 y c = 5.\n"
        "2) Calcula b² − 4ac = 9 − 4 · 2 · 5 = 9 − 40 = −31.\n"
        "3) El discriminante es negativo, y no existe ningún número real cuya raíz "
        "cuadrada sea negativa.\n"
        "4) Por lo tanto la ecuación no tiene soluciones reales. Gráficamente, la "
        "parábola no llega a cortar el eje X.",
        [
            ("Dos soluciones reales distintas", "No calculó el discriminante antes de resolver."),
            ("Una única solución real", "Confundió el caso de discriminante negativo con el de discriminante cero."),
            ("Dos soluciones, ambas negativas", "Dedujo el signo de las soluciones por los coeficientes sin verificar que existan."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Se lanza una pelota hacia arriba y su altura en metros, t segundos después, es h = −5t² + 20t. ¿En qué instante vuelve a tocar el suelo?",
        "4 segundos",
        "Tocar el suelo significa que la altura vale cero.\n\n"
        "1) Plantea h = 0: −5t² + 20t = 0.\n"
        "2) Saca factor común t: t(−5t + 20) = 0.\n"
        "3) Un producto es cero si alguno de sus factores lo es: t = 0 o "
        "−5t + 20 = 0.\n"
        "4) El segundo caso da t = 4. La solución t = 0 corresponde al instante del "
        "lanzamiento, así que la pelota vuelve al suelo a los 4 segundos.",
        [
            ("2 segundos", "Entregó el instante de altura máxima, que es el vértice de la parábola."),
            ("0 segundos", "Eligió la solución que corresponde al momento del lanzamiento."),
            ("20 segundos", "Tomó el coeficiente del término lineal como si fuera el tiempo."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Si las soluciones de una ecuación cuadrática son x = 3 y x = −4, ¿cuál es la ecuación en su forma factorizada?",
        "(x − 3)(x + 4) = 0",
        "Se reconstruye la ecuación invirtiendo el proceso de resolución.\n\n"
        "1) Si x = 3 es solución, entonces x − 3 = 0 y ese es un factor.\n"
        "2) Si x = −4 es solución, entonces x + 4 = 0 y ese es el otro factor.\n"
        "3) El producto de ambos factores igualado a cero reproduce la ecuación: "
        "(x − 3)(x + 4) = 0.\n"
        "4) Desarrollando quedaría x² + x − 12 = 0, cuyas soluciones son en efecto 3 "
        "y −4.",
        [
            ("(x + 3)(x − 4) = 0", "Copió los signos de las soluciones sin invertirlos al armar los factores."),
            ("(x − 3)(x − 4) = 0", "Invirtió el signo de una solución pero no de la otra."),
            ("(x + 3)(x + 4) = 0", "Sumó ambas soluciones en los factores, sin considerar sus signos."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuál es la suma de las soluciones de la ecuación x² − 7x + 10 = 0?",
        "7",
        "Se puede resolver la ecuación, o usar una propiedad que ahorra trabajo.\n\n"
        "1) Factoriza: buscas dos números que multipliquen 10 y sumen −7, que son −2 "
        "y −5. Queda (x − 2)(x − 5) = 0.\n"
        "2) Las soluciones son 2 y 5.\n"
        "3) Su suma es 7.\n"
        "4) Atajo: en una ecuación de la forma x² + bx + c = 0, la suma de las "
        "soluciones es siempre −b. Aquí b = −7, así que la suma es 7 sin necesidad de "
        "resolver.",
        [
            ("10", "Entregó el producto de las soluciones en lugar de su suma."),
            ("−7", "Aplicó el atajo pero olvidó cambiar el signo del coeficiente."),
            ("3", "Restó las soluciones en vez de sumarlas."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "El producto de dos números enteros consecutivos es 72. ¿Cuál es el menor de ellos, considerando solo los positivos?",
        "8",
        "Dos consecutivos se diferencian en 1, así que basta una incógnita.\n\n"
        "1) Llama n al menor. El siguiente es n + 1.\n"
        "2) El producto es 72: n(n + 1) = 72.\n"
        "3) Desarrolla y ordena: n² + n − 72 = 0.\n"
        "4) Factoriza buscando dos números que multipliquen −72 y sumen 1: son 9 y "
        "−8. Queda (n + 9)(n − 8) = 0, con soluciones −9 y 8. El menor positivo es 8, "
        "y en efecto 8 · 9 = 72.",
        [
            ("9", "Entregó el mayor de los dos números consecutivos."),
            ("−9", "Eligió la solución negativa, descartada por el enunciado."),
            ("36", "Dividió 72 por 2, como si los números fueran iguales."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² − 121 = 0?",
        "x = 11 y x = −11",
        "Sin término lineal, se despeja el cuadrado y se saca raíz.\n\n"
        "1) Suma 121: x² = 121.\n"
        "2) Saca raíz cuadrada considerando los dos signos posibles.\n"
        "3) Como 11 · 11 = 121 y (−11) · (−11) = 121, las soluciones son 11 y −11.",
        [
            ("x = 11", "Consideró solo la raíz positiva."),
            ("x = 60,5 y x = −60,5", "Dividió por 2 en lugar de calcular la raíz cuadrada."),
            ("x = 121", "Despejó el término pero no aplicó la raíz."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² = 144?",
        "x = 12 y x = −12",
        "La ecuación ya está despejada.\n\n"
        "1) Aplica raíz cuadrada a ambos lados, con los dos signos.\n"
        "2) Como 12² = 144 y (−12)² = 144, ambos valores sirven.\n"
        "3) Las soluciones son 12 y −12.",
        [
            ("x = 12", "Omitió la raíz negativa."),
            ("x = 72 y x = −72", "Dividió por 2 en vez de calcular la raíz."),
            ("x = 14 y x = −14", "Usó una raíz aproximada incorrecta: 14² es 196."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² + 8x = 0?",
        "x = 0 y x = −8",
        "Sin término independiente, se factoriza sacando la x.\n\n"
        "1) Factor común x: x(x + 8) = 0.\n"
        "2) El producto es cero si algún factor lo es: x = 0 o x + 8 = 0.\n"
        "3) Del segundo caso: x = −8.\n"
        "4) Dividir por x haría desaparecer la solución x = 0, que sí es válida.",
        [
            ("x = −8", "Dividió por x y perdió la solución x = 0."),
            ("x = 0 y x = 8", "No cambió el signo al despejar el segundo factor."),
            ("x = 8 y x = −8", "Trató la ecuación como si fuera x² = 64."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² + 6x + 8 = 0?",
        "x = −2 y x = −4",
        "Se factoriza el trinomio y se anula cada factor.\n\n"
        "1) Busca dos números que multipliquen 8 y sumen 6: son 2 y 4.\n"
        "2) Factoriza: (x + 2)(x + 4) = 0.\n"
        "3) Iguala cada factor a cero: x = −2 y x = −4.\n"
        "4) Verifica: (−2)² + 6(−2) + 8 = 4 − 12 + 8 = 0.",
        [
            ("x = 2 y x = 4", "No invirtió los signos al despejar cada factor."),
            ("x = −1 y x = −8", "Eligió una pareja que multiplica 8 pero suma 9."),
            ("x = −6 y x = −8", "Usó directamente los coeficientes del enunciado."),
        ],
    ),
    _q(
        "alg_cuadratica", "facil",
        "¿Cuáles son las soluciones de x² − 11x + 24 = 0?",
        "x = 3 y x = 8",
        "El signo negativo del término central y el positivo del último indican dos "
        "números negativos en la factorización.\n\n"
        "1) Busca dos números que multipliquen 24 y sumen −11: son −3 y −8.\n"
        "2) Factoriza: (x − 3)(x − 8) = 0.\n"
        "3) Iguala a cero: x = 3 y x = 8.\n"
        "4) Verifica: 9 − 33 + 24 = 0.",
        [
            ("x = −3 y x = −8", "No invirtió los signos al despejar."),
            ("x = 4 y x = 6", "Eligió una pareja que multiplica 24 pero suma 10."),
            ("x = 11 y x = 24", "Usó directamente los coeficientes del enunciado."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² − x − 20 = 0?",
        "x = 5 y x = −4",
        "Cuidado con el término central: su coeficiente es −1, aunque no se escriba.\n\n"
        "1) Busca dos números que multipliquen −20 y sumen −1: son −5 y 4.\n"
        "2) Factoriza: (x − 5)(x + 4) = 0.\n"
        "3) Iguala a cero: x = 5 y x = −4.\n"
        "4) Verifica: 25 − 5 − 20 = 0.",
        [
            ("x = −5 y x = 4", "Invirtió los signos de ambas soluciones."),
            ("x = 10 y x = −2", "Eligió una pareja que multiplica −20 pero suma 8."),
            ("x = 5 y x = 4", "Ignoró que una solución debe ser negativa para que el producto lo sea."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² + 4x − 21 = 0?",
        "x = 3 y x = −7",
        "El término independiente negativo obliga a signos distintos.\n\n"
        "1) Busca dos números que multipliquen −21 y sumen 4: son 7 y −3.\n"
        "2) Factoriza: (x + 7)(x − 3) = 0.\n"
        "3) Iguala a cero: x = −7 y x = 3.\n"
        "4) Verifica: 9 + 12 − 21 = 0.",
        [
            ("x = −3 y x = 7", "Invirtió los signos de ambas soluciones."),
            ("x = 21 y x = −1", "Eligió una pareja que multiplica −21 pero suma 20."),
            ("x = 3 y x = 7", "Ignoró que una solución debe ser negativa."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de 5x² − 45 = 0?",
        "x = 3 y x = −3",
        "Conviene simplificar el coeficiente antes de sacar la raíz.\n\n"
        "1) Suma 45: 5x² = 45.\n"
        "2) Divide por 5: x² = 9.\n"
        "3) Saca raíz con ambos signos: x = 3 y x = −3.\n"
        "4) Verifica: 5 · 9 − 45 = 0 para los dos valores.",
        [
            ("x = 9 y x = −9", "Despejó x² = 9 pero no le sacó la raíz."),
            ("x = 3", "Consideró solo la raíz positiva."),
            ("x = 22,5 y x = −22,5", "Dividió 45 por 2 en lugar de por el coeficiente 5."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de x² + 12x + 36 = 0?",
        "x = −6, una única solución",
        "Este trinomio es un cuadrado perfecto.\n\n"
        "1) Busca dos números que multipliquen 36 y sumen 12: ambos son 6.\n"
        "2) Factoriza: (x + 6)² = 0.\n"
        "3) Al repetirse el factor, hay una sola solución: x = −6.\n"
        "4) Es una raíz doble: la parábola toca el eje X sin cruzarlo.",
        [
            ("x = 6 y x = −6", "Trató la ecuación como una diferencia de cuadrados."),
            ("x = 6, una única solución", "No invirtió el signo al despejar el factor."),
            ("x = −12 y x = −36", "Usó directamente los coeficientes del enunciado."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuáles son las soluciones de 3x² − 10x + 3 = 0?",
        "x = 3 y x = 1/3",
        "Con coeficiente distinto de 1 conviene la fórmula general.\n\n"
        "1) Identifica a = 3, b = −10 y c = 3.\n"
        "2) Discriminante: 100 − 4 · 3 · 3 = 100 − 36 = 64, cuya raíz es 8.\n"
        "3) Fórmula: x = (10 ± 8)/6.\n"
        "4) Las soluciones son (10 + 8)/6 = 3 y (10 − 8)/6 = 1/3.",
        [
            ("x = 3 y x = 3", "Usó solo el signo positivo de la fórmula, obteniendo la misma solución dos veces."),
            ("x = −3 y x = −1/3", "Invirtió el signo de b al aplicar la fórmula."),
            ("x = 9 y x = 1", "Dividió por a en lugar de por 2a al final."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "Un terreno rectangular tiene 5 m más de largo que de ancho y su área es de 84 m². ¿Cuánto mide el ancho?",
        "7 m",
        "Se expresa el área con una sola incógnita.\n\n"
        "1) Llama a al ancho. El largo es a + 5.\n"
        "2) El área es a(a + 5) = 84.\n"
        "3) Ordena: a² + 5a − 84 = 0.\n"
        "4) Factoriza buscando dos números que multipliquen −84 y sumen 5: son 12 y "
        "−7. Queda (a + 12)(a − 7) = 0, con soluciones −12 y 7. Una longitud no puede "
        "ser negativa, así que el ancho es 7 m y el largo 12 m.",
        [
            ("12 m", "Entregó la medida del largo en lugar del ancho."),
            ("−12 m", "Eligió la solución negativa, imposible para una longitud."),
            ("42 m", "Dividió el área por 2, como si se tratara de un perímetro."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "La suma de un número y su cuadrado es igual a 42. ¿Cuál es el número, si se sabe que es positivo?",
        "6",
        "Se traduce el enunciado y se ordena la ecuación.\n\n"
        "1) Llama n al número: n + n² = 42.\n"
        "2) Ordena: n² + n − 42 = 0.\n"
        "3) Factoriza buscando dos números que multipliquen −42 y sumen 1: son 7 y "
        "−6. Queda (n + 7)(n − 6) = 0.\n"
        "4) Las soluciones son −7 y 6. Como se pide el positivo, es 6. Verifica: "
        "6 + 36 = 42.",
        [
            ("−7", "Eligió la solución negativa, descartada por el enunciado."),
            ("7", "No invirtió el signo al despejar el factor correspondiente."),
            ("21", "Dividió 42 por 2 sin plantear la ecuación."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Usando la fórmula general, ¿cuáles son las soluciones de x² − 3x − 10 = 0?",
        "x = 5 y x = −2",
        "La fórmula general funciona con cualquier ecuación cuadrática.\n\n"
        "1) Identifica a = 1, b = −3 y c = −10.\n"
        "2) Discriminante: 9 − 4 · 1 · (−10) = 9 + 40 = 49, cuya raíz es 7.\n"
        "3) Fórmula: x = (3 ± 7)/2.\n"
        "4) Las soluciones son (3 + 7)/2 = 5 y (3 − 7)/2 = −2. Verifica: "
        "25 − 15 − 10 = 0.",
        [
            ("x = −5 y x = 2", "Invirtió el signo de b al aplicar la fórmula."),
            ("x = 5 y x = 2", "Perdió el signo negativo en la solución obtenida con la resta."),
            ("x = 3 y x = −10", "Usó los coeficientes b y c como si fueran las soluciones."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuáles son las soluciones de 3x² + 5x − 2 = 0?",
        "x = 1/3 y x = −2",
        "Se aplica la fórmula general por el coeficiente distinto de 1.\n\n"
        "1) Identifica a = 3, b = 5 y c = −2.\n"
        "2) Discriminante: 25 − 4 · 3 · (−2) = 25 + 24 = 49, cuya raíz es 7.\n"
        "3) Fórmula: x = (−5 ± 7)/6.\n"
        "4) Las soluciones son (−5 + 7)/6 = 1/3 y (−5 − 7)/6 = −2.",
        [
            ("x = −1/3 y x = 2", "Invirtió el signo de ambas soluciones."),
            ("x = 1/3 y x = −12", "Dividió solo una de las soluciones por 2a."),
            ("x = 2 y x = −5", "Usó los coeficientes b y c como si fueran las soluciones."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuántas soluciones reales tiene la ecuación x² + 4x + 4 = 0?",
        "Una única solución real (el discriminante vale 0)",
        "El discriminante determina la cantidad de soluciones reales.\n\n"
        "1) Identifica a = 1, b = 4 y c = 4.\n"
        "2) Calcula b² − 4ac = 16 − 16 = 0.\n"
        "3) Con discriminante cero, sumar y restar la raíz da el mismo valor, así que "
        "las soluciones coinciden.\n"
        "4) Hay una única solución real, x = −2. La parábola toca el eje X en un solo "
        "punto.",
        [
            ("Dos soluciones reales distintas", "Supuso que toda cuadrática tiene siempre dos soluciones distintas."),
            ("No tiene soluciones reales", "Confundió el discriminante cero con uno negativo."),
            ("Depende del valor de x", "La cantidad de soluciones es una propiedad de la ecuación, no depende de x."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "¿Cuántas soluciones reales tiene la ecuación x² − 2x + 7 = 0?",
        "Ninguna: el discriminante vale −24",
        "Conviene calcular el discriminante antes de intentar resolver.\n\n"
        "1) Identifica a = 1, b = −2 y c = 7.\n"
        "2) Calcula b² − 4ac = 4 − 28 = −24.\n"
        "3) Es negativo, y ningún número real tiene raíz cuadrada negativa.\n"
        "4) La ecuación no tiene soluciones reales: la parábola no corta el eje X.",
        [
            ("Dos soluciones reales distintas", "No calculó el discriminante antes de resolver."),
            ("Una única solución real", "Confundió el discriminante negativo con uno igual a cero."),
            ("Dos soluciones, ambas positivas", "Dedujo el signo de las soluciones sin verificar que existan."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Un proyectil se dispara verticalmente y su altura en metros, t segundos después, está dada por h = −5t² + 30t. ¿A los cuántos segundos vuelve a tocar el suelo?",
        "6 segundos",
        "Tocar el suelo equivale a que la altura sea cero.\n\n"
        "1) Plantea h = 0: −5t² + 30t = 0.\n"
        "2) Saca factor común t: t(−5t + 30) = 0.\n"
        "3) Las soluciones son t = 0 y −5t + 30 = 0, es decir t = 6.\n"
        "4) La primera corresponde al instante del disparo, así que el proyectil "
        "vuelve al suelo a los 6 segundos.",
        [
            ("3 segundos", "Entregó el instante de altura máxima, que es el vértice de la parábola."),
            ("0 segundos", "Eligió la solución que corresponde al momento del disparo."),
            ("30 segundos", "Tomó el coeficiente del término lineal como si fuera el tiempo."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "Si las soluciones de una ecuación cuadrática son x = −2 y x = 5, ¿cuál es la ecuación en su forma factorizada?",
        "(x + 2)(x − 5) = 0",
        "Se reconstruye la ecuación invirtiendo el despeje.\n\n"
        "1) Si x = −2 es solución, entonces x + 2 = 0 es un factor.\n"
        "2) Si x = 5 es solución, entonces x − 5 = 0 es el otro factor.\n"
        "3) El producto igualado a cero da (x + 2)(x − 5) = 0.\n"
        "4) Desarrollando queda x² − 3x − 10 = 0, cuyas soluciones son en efecto −2 "
        "y 5.",
        [
            ("(x − 2)(x + 5) = 0", "Copió los signos de las soluciones sin invertirlos."),
            ("(x + 2)(x + 5) = 0", "Invirtió el signo de una solución pero no de la otra."),
            ("(x − 2)(x − 5) = 0", "Usó signo negativo en ambos factores, ignorando la solución negativa."),
        ],
    ),
    _q(
        "alg_cuadratica", "medio",
        "¿Cuál es el producto de las soluciones de la ecuación x² − 9x + 18 = 0?",
        "18",
        "Se puede factorizar, o usar una propiedad de los coeficientes.\n\n"
        "1) Busca dos números que multipliquen 18 y sumen −9: son −3 y −6. Queda "
        "(x − 3)(x − 6) = 0.\n"
        "2) Las soluciones son 3 y 6.\n"
        "3) Su producto es 18.\n"
        "4) Atajo: en x² + bx + c = 0, el producto de las soluciones es siempre c. "
        "Aquí c = 18, sin necesidad de resolver.",
        [
            ("9", "Entregó la suma de las soluciones en lugar de su producto."),
            ("−18", "Aplicó el atajo pero cambió el signo de c innecesariamente."),
            ("3", "Entregó una de las soluciones en vez del producto."),
        ],
    ),
    _q(
        "alg_cuadratica", "dificil",
        "El cuadrado de la edad de Ana, menos cuatro veces su edad, es igual a 45. ¿Cuántos años tiene Ana?",
        "9 años",
        "Se plantea la ecuación con la edad como incógnita.\n\n"
        "1) Llama n a la edad: n² − 4n = 45.\n"
        "2) Ordena: n² − 4n − 45 = 0.\n"
        "3) Factoriza buscando dos números que multipliquen −45 y sumen −4: son −9 y "
        "5. Queda (n − 9)(n + 5) = 0.\n"
        "4) Las soluciones son 9 y −5. Una edad no puede ser negativa, así que Ana "
        "tiene 9 años. Verifica: 81 − 36 = 45.",
        [
            ("−5 años", "Eligió la solución negativa, imposible para una edad."),
            ("5 años", "No invirtió el signo al despejar el factor correspondiente."),
            ("45 años", "Tomó el resultado de la operación como si fuera la edad."),
        ],
    ),
    # ---------- alg_funciones ----------
    _q(
        "alg_funciones", "facil",
        "Si f(x) = 4x + 1, ¿cuál es el valor de f(3)?",
        "13",
        "Evaluar una función es reemplazar la x por el valor indicado.\n\n"
        "1) Sustituye x por 3: f(3) = 4 · 3 + 1.\n"
        "2) Multiplica primero: 4 · 3 = 12.\n"
        "3) Suma: 12 + 1 = 13.",
        [
            ("16", "Sumó el 1 antes de multiplicar, alterando el orden de las operaciones."),
            ("7", "Sumó el 3 al coeficiente en lugar de multiplicarlos."),
            ("12", "Multiplicó correctamente pero olvidó sumar el término independiente."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "Si f(x) = x² − 2, ¿cuál es el valor de f(4)?",
        "14",
        "Se reemplaza la x y se respeta el orden de las operaciones.\n\n"
        "1) Sustituye: f(4) = 4² − 2.\n"
        "2) Calcula la potencia primero: 4² = 16.\n"
        "3) Resta: 16 − 2 = 14.",
        [
            ("4", "Restó antes de elevar al cuadrado, calculando (4 − 2)²."),
            ("6", "Multiplicó la base por 2 en lugar de elevarla al cuadrado."),
            ("16", "Calculó el cuadrado pero olvidó restar el 2."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿Cuál es la pendiente de la recta que pasa por los puntos (2, 3) y (6, 11)?",
        "2",
        "La pendiente mide cuánto sube la recta por cada unidad que avanza.\n\n"
        "1) La fórmula es m = (y₂ − y₁)/(x₂ − x₁).\n"
        "2) Reemplaza: m = (11 − 3)/(6 − 2).\n"
        "3) Calcula: 8/4 = 2.\n"
        "4) Interpretación: por cada unidad que avanza en x, la recta sube 2 en y.",
        [
            ("0,5", "Invirtió la fórmula, dividiendo el avance en x por el avance en y."),
            ("8", "Calculó solo la diferencia de las y sin dividir por la de las x."),
            ("4", "Calculó solo la diferencia de las x."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿Cuál es la pendiente de la recta y = 5x − 2?",
        "5",
        "En la forma y = mx + n, la pendiente es el número que acompaña a la x.\n\n"
        "1) Compara y = 5x − 2 con y = mx + n.\n"
        "2) El coeficiente de x es 5, así que m = 5.\n"
        "3) El −2 es el coeficiente de posición: indica dónde corta el eje Y, no la "
        "inclinación.",
        [
            ("−2", "Confundió la pendiente con el coeficiente de posición."),
            ("3", "Restó los dos números de la ecuación."),
            ("−10", "Multiplicó los dos números de la ecuación."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿En qué punto corta al eje Y la recta y = 3x + 7?",
        "(0, 7)",
        "Sobre el eje Y todos los puntos tienen x = 0.\n\n"
        "1) Reemplaza x por 0: y = 3 · 0 + 7.\n"
        "2) Calcula: y = 7.\n"
        "3) El punto de corte es (0, 7).\n"
        "4) Atajo: en y = mx + n, el corte con el eje Y es siempre (0, n).",
        [
            ("(7, 0)", "Intercambió las coordenadas: ese punto está sobre el eje X."),
            ("(0, 3)", "Usó la pendiente en lugar del coeficiente de posición."),
            ("(−7/3, 0)", "Calculó el corte con el eje X en lugar del eje Y."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es el vértice de la parábola y = x² − 8x + 12?",
        "(4, −4)",
        "El vértice se obtiene primero en x y después reemplazando.\n\n"
        "1) La coordenada x del vértice es −b/(2a). Aquí a = 1 y b = −8, así que "
        "x = 8/2 = 4.\n"
        "2) Reemplaza en la función para obtener la y: 4² − 8 · 4 + 12.\n"
        "3) Calcula: 16 − 32 + 12 = −4.\n"
        "4) El vértice es (4, −4). Como a es positivo, la parábola se abre hacia "
        "arriba y ese punto es su mínimo.",
        [
            ("(−4, 60)", "Olvidó el signo negativo en la fórmula −b/(2a)."),
            ("(4, 12)", "Usó el término independiente como coordenada y en vez de evaluar la función."),
            ("(8, 12)", "Tomó el coeficiente b directamente, sin dividir por 2a."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es el eje de simetría de la parábola y = x² + 4x − 5?",
        "x = −2",
        "El eje de simetría es la recta vertical que pasa por el vértice.\n\n"
        "1) Su ecuación es x = −b/(2a).\n"
        "2) Aquí a = 1 y b = 4, así que x = −4/2.\n"
        "3) El eje de simetría es x = −2.\n"
        "4) Comprueba la simetría: en x = −1 y en x = −3 la función vale lo mismo "
        "(−8 en ambos casos).",
        [
            ("x = 2", "Olvidó el signo negativo de la fórmula."),
            ("x = −5", "Usó el término independiente en lugar de calcular el eje."),
            ("y = −2", "Escribió el eje como una recta horizontal; el eje de simetría de una parábola vertical es vertical."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuáles son las intersecciones con el eje X de la parábola y = x² − 5x + 6?",
        "(2, 0) y (3, 0)",
        "Sobre el eje X la coordenada y vale cero.\n\n"
        "1) Iguala la función a cero: x² − 5x + 6 = 0.\n"
        "2) Factoriza buscando dos números que multipliquen 6 y sumen −5: son −2 y "
        "−3. Queda (x − 2)(x − 3) = 0.\n"
        "3) Las soluciones son x = 2 y x = 3.\n"
        "4) Los puntos son (2, 0) y (3, 0), porque están sobre el eje X.",
        [
            ("(0, 2) y (0, 3)", "Intercambió las coordenadas: esos puntos están sobre el eje Y."),
            ("(−2, 0) y (−3, 0)", "No invirtió los signos al despejar los factores."),
            ("(0, 6)", "Calculó la intersección con el eje Y en lugar de con el eje X."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "Una recta pasa por el punto (0, 5) y tiene pendiente −2. ¿Cuál es su ecuación?",
        "y = −2x + 5",
        "El punto entregado está justo sobre el eje Y, lo que simplifica el trabajo.\n\n"
        "1) La forma general es y = mx + n, donde m es la pendiente y n el corte con "
        "el eje Y.\n"
        "2) La pendiente es m = −2.\n"
        "3) Como el punto (0, 5) tiene x = 0, corresponde al corte con el eje Y, así "
        "que n = 5.\n"
        "4) La ecuación es y = −2x + 5.",
        [
            ("y = 5x − 2", "Intercambió la pendiente con el coeficiente de posición."),
            ("y = 2x + 5", "Perdió el signo negativo de la pendiente."),
            ("y = −2x − 5", "Cambió el signo del coeficiente de posición."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "La función f(x) = 3x + b cumple que f(2) = 11. ¿Cuál es el valor de b?",
        "5",
        "Se reemplaza el dato conocido y se despeja la incógnita.\n\n"
        "1) Evalúa en x = 2: f(2) = 3 · 2 + b = 6 + b.\n"
        "2) Como f(2) vale 11: 6 + b = 11.\n"
        "3) Despeja: b = 11 − 6 = 5.\n"
        "4) Verifica: f(x) = 3x + 5, y f(2) = 6 + 5 = 11. Correcto.",
        [
            ("17", "Sumó el 6 en lugar de restarlo al despejar."),
            ("11", "Tomó el valor de la función como si fuera directamente b."),
            ("2", "Entregó el valor de x en lugar del de b."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "Un taxi cobra $500 fijos al subir más $300 por cada kilómetro recorrido. ¿Cuál es la función que representa el costo total según los kilómetros x?",
        "C(x) = 300x + 500",
        "Se separa lo que es fijo de lo que depende de la distancia.\n\n"
        "1) El cobro de $500 no cambia con la distancia: es el término independiente.\n"
        "2) Los $300 se cobran por cada kilómetro, así que se multiplican por x: "
        "300x. Ese es el término variable.\n"
        "3) El costo total es la suma: C(x) = 300x + 500.\n"
        "4) En el lenguaje de funciones lineales, 300 es la pendiente y 500 el "
        "coeficiente de posición.",
        [
            ("C(x) = 500x + 300", "Intercambió el cobro fijo con el cobro por kilómetro."),
            ("C(x) = 800x", "Sumó ambos valores y los aplicó a cada kilómetro."),
            ("C(x) = 300x", "Omitió el cobro fijo de subida."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "Un taxi cobra $500 fijos al subir más $300 por kilómetro. ¿Cuánto cuesta un viaje de 8 kilómetros?",
        "$2.900",
        "Se aplica la función de costo al valor pedido.\n\n"
        "1) El costo es C(x) = 300x + 500.\n"
        "2) Reemplaza x por 8: C(8) = 300 · 8 + 500.\n"
        "3) Multiplica: 300 · 8 = 2.400.\n"
        "4) Suma el cobro fijo: 2.400 + 500 = 2.900.",
        [
            ("$2.400", "Calculó el cobro por distancia pero olvidó el cobro fijo."),
            ("$6.400", "Aplicó el cobro fijo a cada kilómetro en lugar de una sola vez."),
            ("$4.000", "Sumó los $500 a los $300 antes de multiplicar por los kilómetros."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es la imagen de f(x) = −2x + 7 cuando x = −3?",
        "13",
        "Hay que cuidar el doble signo negativo.\n\n"
        "1) Sustituye: f(−3) = −2 · (−3) + 7.\n"
        "2) Multiplica primero: menos por menos da más, así que −2 · (−3) = 6.\n"
        "3) Suma: 6 + 7 = 13.",
        [
            ("1", "Trató el producto como negativo, calculando −6 + 7."),
            ("−13", "Cambió el signo de todo el resultado."),
            ("11", "Multiplicó el −2 por 3 sin considerar el signo de x, y ajustó mal el resto."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuál es el vértice de la parábola y = 2x² − 8x + 5?",
        "(2, −3)",
        "Con coeficiente principal distinto de 1, la fórmula del vértice sigue "
        "siendo la misma.\n\n"
        "1) La coordenada x es −b/(2a). Aquí a = 2 y b = −8, así que x = 8/4 = 2.\n"
        "2) Reemplaza en la función: 2 · 2² − 8 · 2 + 5.\n"
        "3) Calcula: 2 · 4 = 8, luego 8 − 16 + 5 = −3.\n"
        "4) El vértice es (2, −3), y como a es positivo se trata de un mínimo.",
        [
            ("(4, 5)", "Dividió b por a en lugar de por 2a."),
            ("(2, 5)", "Usó el término independiente como coordenada y sin evaluar la función."),
            ("(−2, 29)", "Olvidó el signo negativo en la fórmula −b/(2a)."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuál es el valor mínimo que alcanza la función y = x² − 6x + 11?",
        "2",
        "El valor mínimo de una parábola que se abre hacia arriba está en su "
        "vértice.\n\n"
        "1) Como a = 1 es positivo, la parábola se abre hacia arriba y el vértice es "
        "un mínimo.\n"
        "2) La coordenada x del vértice es −b/(2a) = 6/2 = 3.\n"
        "3) Evalúa la función ahí: 3² − 6 · 3 + 11 = 9 − 18 + 11 = 2.\n"
        "4) El valor mínimo es 2, y se alcanza cuando x = 3.",
        [
            ("3", "Entregó la coordenada x del vértice en lugar del valor mínimo de la función."),
            ("11", "Tomó el término independiente como si fuera el mínimo."),
            ("−2", "Cambió el signo del resultado al evaluar la función."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuál es la ecuación de la recta que pasa por los puntos (1, 4) y (3, 10)?",
        "y = 3x + 1",
        "Primero se calcula la pendiente y después el coeficiente de posición.\n\n"
        "1) Pendiente: m = (10 − 4)/(3 − 1) = 6/2 = 3.\n"
        "2) La ecuación tiene la forma y = 3x + n.\n"
        "3) Reemplaza uno de los puntos, por ejemplo (1, 4): 4 = 3 · 1 + n, entonces "
        "n = 1.\n"
        "4) La ecuación es y = 3x + 1. Verifica con el otro punto: "
        "3 · 3 + 1 = 10. Correcto.",
        [
            ("y = 3x − 1", "Cambió el signo del coeficiente de posición al despejarlo."),
            ("y = 3x + 4", "Usó la coordenada y del primer punto como coeficiente de posición."),
            ("y = (1/3)x + 1", "Invirtió la fórmula de la pendiente."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Para qué valor de x la función f(x) = 4x − 20 se hace cero?",
        "x = 5",
        "Se busca el punto donde la recta cruza el eje X.\n\n"
        "1) Iguala la función a cero: 4x − 20 = 0.\n"
        "2) Suma 20: 4x = 20.\n"
        "3) Divide por 4: x = 5.\n"
        "4) Ese valor se llama cero o raíz de la función: el punto (5, 0) está sobre "
        "la recta.",
        [
            ("x = 20", "Despejó el 20 pero no dividió por el coeficiente."),
            ("x = −5", "Cambió el signo al despejar."),
            ("x = −20", "Evaluó la función en x = 0 en lugar de igualarla a cero."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "Una empresa tiene un ingreso dado por I(x) = 50x y un costo dado por C(x) = 20x + 900, donde x son las unidades vendidas. ¿Cuántas unidades debe vender para no ganar ni perder?",
        "30 unidades",
        "No ganar ni perder significa que el ingreso iguala exactamente al costo.\n\n"
        "1) Iguala ambas funciones: 50x = 20x + 900.\n"
        "2) Resta 20x: 30x = 900.\n"
        "3) Divide por 30: x = 30.\n"
        "4) Verifica: con 30 unidades el ingreso es 1.500 y el costo es "
        "600 + 900 = 1.500. Coinciden, así que ese es el punto de equilibrio.",
        [
            ("18 unidades", "Dividió los 900 de costo fijo por 50 en lugar de por la diferencia entre ingreso y costo variable."),
            ("45 unidades", "Dividió los 900 por 20, usando solo el costo variable."),
            ("900 unidades", "Tomó el costo fijo como si fuera la cantidad de unidades."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es la pendiente de la recta que pasa por los puntos (−2, 1) y (2, 9)?",
        "2",
        "La fórmula funciona igual con coordenadas negativas, cuidando los signos.\n\n"
        "1) Aplica m = (y₂ − y₁)/(x₂ − x₁).\n"
        "2) Numerador: 9 − 1 = 8.\n"
        "3) Denominador: 2 − (−2) = 2 + 2 = 4. Restar un negativo equivale a sumar.\n"
        "4) Pendiente: 8/4 = 2.",
        [
            ("8", "Calculó solo la diferencia de las y sin dividir."),
            ("4", "Restó mal el denominador, tratando 2 − (−2) como 2 − 2 y ajustando el resultado."),
            ("0,5", "Invirtió la fórmula, dividiendo el avance en x por el avance en y."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "La parábola y = x² + bx + 3 pasa por el punto (1, 6). ¿Cuál es el valor de b?",
        "2",
        "Que la parábola pase por un punto significa que sus coordenadas satisfacen "
        "la ecuación.\n\n"
        "1) Reemplaza x = 1 e y = 6: 6 = 1² + b · 1 + 3.\n"
        "2) Simplifica: 6 = 1 + b + 3, o sea 6 = b + 4.\n"
        "3) Despeja: b = 2.\n"
        "4) Verifica: y = x² + 2x + 3 evaluada en x = 1 da 1 + 2 + 3 = 6. Correcto.",
        [
            ("10", "Sumó el 4 en lugar de restarlo al despejar."),
            ("6", "Tomó la coordenada y del punto como si fuera directamente b."),
            ("3", "Entregó el término independiente de la parábola en lugar de b."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "Si f(x) = 2x − 5, ¿cuál es el valor de f(4)?",
        "3",
        "Evaluar es reemplazar la x por el valor dado.\n\n"
        "1) Sustituye: f(4) = 2 · 4 − 5.\n"
        "2) Multiplica primero: 2 · 4 = 8.\n"
        "3) Resta: 8 − 5 = 3.",
        [
            ("−2", "Restó antes de multiplicar, calculando 2(4 − 5)."),
            ("8", "Multiplicó pero olvidó restar el término independiente."),
            ("13", "Sumó el 5 en lugar de restarlo."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "Si f(x) = x² + 3, ¿cuál es el valor de f(2)?",
        "7",
        "Se reemplaza y se respeta el orden de las operaciones.\n\n"
        "1) Sustituye: f(2) = 2² + 3.\n"
        "2) Calcula la potencia primero: 2² = 4.\n"
        "3) Suma: 4 + 3 = 7.",
        [
            ("25", "Sumó antes de elevar al cuadrado, calculando (2 + 3)²."),
            ("10", "Multiplicó la base por 2 en lugar de elevarla al cuadrado, y sumó mal."),
            ("4", "Calculó el cuadrado pero olvidó sumar el 3."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿Cuál es la pendiente de la recta que pasa por los puntos (0, 0) y (4, 12)?",
        "3",
        "La pendiente compara el avance vertical con el horizontal.\n\n"
        "1) Aplica m = (y₂ − y₁)/(x₂ − x₁).\n"
        "2) Reemplaza: m = (12 − 0)/(4 − 0) = 12/4.\n"
        "3) La pendiente es 3.\n"
        "4) Como la recta pasa por el origen, su ecuación es simplemente y = 3x.",
        [
            ("12", "Calculó solo el avance vertical sin dividir por el horizontal."),
            ("1/3", "Invirtió la fórmula de la pendiente."),
            ("4", "Entregó el avance horizontal en lugar de la pendiente."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿Cuál es la pendiente de la recta y = −3x + 8?",
        "−3",
        "En y = mx + n la pendiente es el coeficiente de x, con su signo.\n\n"
        "1) Compara y = −3x + 8 con y = mx + n.\n"
        "2) El coeficiente de x es −3, así que m = −3.\n"
        "3) El signo negativo indica que la recta baja de izquierda a derecha.",
        [
            ("3", "Ignoró el signo negativo del coeficiente."),
            ("8", "Confundió la pendiente con el coeficiente de posición."),
            ("5", "Sumó los dos números de la ecuación."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "¿En qué punto corta al eje Y la recta y = −4x + 2?",
        "(0, 2)",
        "Sobre el eje Y la coordenada x vale cero.\n\n"
        "1) Reemplaza x por 0: y = −4 · 0 + 2 = 2.\n"
        "2) El punto de corte es (0, 2).\n"
        "3) Regla práctica: en y = mx + n, el corte con el eje Y es siempre (0, n).",
        [
            ("(2, 0)", "Intercambió las coordenadas: ese punto está sobre el eje X."),
            ("(0, −4)", "Usó la pendiente en lugar del coeficiente de posición."),
            ("(0,5, 0)", "Calculó el corte con el eje X en lugar del eje Y."),
        ],
    ),
    _q(
        "alg_funciones", "facil",
        "Si f(x) = 6 − x, ¿cuál es el valor de f(10)?",
        "−4",
        "El resultado puede ser negativo, y eso es perfectamente válido.\n\n"
        "1) Sustituye: f(10) = 6 − 10.\n"
        "2) Como se resta un número mayor, el resultado es negativo: −4.\n"
        "3) Gráficamente, la recta ya cruzó el eje X en ese punto.",
        [
            ("4", "Restó en el orden inverso, calculando 10 − 6."),
            ("16", "Sumó en lugar de restar."),
            ("60", "Multiplicó los dos números en vez de restarlos."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es el vértice de la parábola y = x² + 2x − 3?",
        "(−1, −4)",
        "Primero la coordenada x, después se evalúa.\n\n"
        "1) x del vértice: −b/(2a) = −2/2 = −1.\n"
        "2) Reemplaza en la función: (−1)² + 2(−1) − 3.\n"
        "3) Calcula: 1 − 2 − 3 = −4.\n"
        "4) El vértice es (−1, −4), y por ser a positivo corresponde a un mínimo.",
        [
            ("(1, 0)", "Olvidó el signo negativo en la fórmula −b/(2a)."),
            ("(−1, −3)", "Usó el término independiente como coordenada y sin evaluar."),
            ("(−2, −3)", "Tomó el coeficiente b directamente, sin dividir por 2a."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es el eje de simetría de la parábola y = 2x² − 12x + 7?",
        "x = 3",
        "El eje pasa por el vértice y es vertical.\n\n"
        "1) Su ecuación es x = −b/(2a).\n"
        "2) Aquí a = 2 y b = −12, así que x = 12/4.\n"
        "3) El eje de simetría es x = 3.\n"
        "4) Ojo con el denominador: es 2a, no solo a.",
        [
            ("x = 6", "Dividió b por a en lugar de por 2a."),
            ("x = −3", "Olvidó el signo negativo de la fórmula, con b ya negativo."),
            ("x = 7", "Usó el término independiente en vez de calcular el eje."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuáles son las intersecciones con el eje X de la parábola y = x² − 9?",
        "(3, 0) y (−3, 0)",
        "Sobre el eje X la coordenada y vale cero.\n\n"
        "1) Iguala a cero: x² − 9 = 0.\n"
        "2) Despeja: x² = 9.\n"
        "3) Saca raíz con ambos signos: x = 3 y x = −3.\n"
        "4) Los puntos son (3, 0) y (−3, 0), simétricos respecto del eje Y.",
        [
            ("(0, 3) y (0, −3)", "Intercambió las coordenadas: esos puntos están sobre el eje Y."),
            ("(9, 0) y (−9, 0)", "Despejó x² = 9 pero no le sacó la raíz."),
            ("(3, 0)", "Consideró solo la raíz positiva."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "Una recta pasa por el punto (2, 7) y tiene pendiente 3. ¿Cuál es su ecuación?",
        "y = 3x + 1",
        "Se conoce la pendiente, así que falta el coeficiente de posición.\n\n"
        "1) La ecuación tiene la forma y = 3x + n.\n"
        "2) Reemplaza el punto (2, 7): 7 = 3 · 2 + n.\n"
        "3) Despeja: 7 = 6 + n, entonces n = 1.\n"
        "4) La ecuación es y = 3x + 1. Verifica: en x = 2 da 7. Correcto.",
        [
            ("y = 3x + 7", "Usó la coordenada y del punto como coeficiente de posición, sin despejar."),
            ("y = 3x − 1", "Cambió el signo del coeficiente de posición."),
            ("y = 2x + 3", "Intercambió la coordenada x del punto con la pendiente."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "La función f(x) = mx + 2 cumple que f(4) = 14. ¿Cuál es el valor de m?",
        "3",
        "Se reemplaza el dato y se despeja la pendiente.\n\n"
        "1) Evalúa en x = 4: f(4) = 4m + 2.\n"
        "2) Como f(4) = 14: 4m + 2 = 14.\n"
        "3) Resta 2: 4m = 12.\n"
        "4) Divide por 4: m = 3. Verifica: f(x) = 3x + 2 y f(4) = 14.",
        [
            ("12", "Despejó el 2 pero no dividió por el coeficiente 4."),
            ("4", "Entregó el valor de x en lugar de la pendiente."),
            ("3,5", "Dividió 14 por 4 sin restar antes el término independiente."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "Un plan de internet cobra $12.000 fijos al mes más $200 por cada GB adicional. ¿Cuánto se paga en un mes con 15 GB adicionales?",
        "$15.000",
        "Se separa el cargo fijo del variable.\n\n"
        "1) El costo se modela como C(x) = 200x + 12.000.\n"
        "2) Reemplaza x por 15: C(15) = 200 · 15 + 12.000.\n"
        "3) Multiplica: 200 · 15 = 3.000.\n"
        "4) Suma el cargo fijo: 3.000 + 12.000 = 15.000.",
        [
            ("$3.000", "Calculó solo el cargo por GB adicionales, sin el cargo fijo."),
            ("$180.000", "Aplicó el cargo fijo a cada GB en lugar de una sola vez."),
            ("$12.200", "Sumó los $200 una sola vez en lugar de multiplicarlos por los 15 GB."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "Una piscina se vacía siguiendo la función V(t) = 2000 − 50t, donde V son litros y t los minutos transcurridos. ¿Cuánta agua queda a los 12 minutos?",
        "1.400 litros",
        "Se evalúa la función en el tiempo indicado.\n\n"
        "1) Reemplaza t por 12: V(12) = 2.000 − 50 · 12.\n"
        "2) Multiplica primero: 50 · 12 = 600.\n"
        "3) Resta: 2.000 − 600 = 1.400.\n"
        "4) Interpretación: la pendiente −50 significa que se pierden 50 litros por "
        "minuto, y los 2.000 son el volumen inicial.",
        [
            ("600 litros", "Calculó el agua que salió en lugar de la que queda."),
            ("1.988 litros", "Restó los 12 minutos en vez de multiplicarlos por 50."),
            ("2.600 litros", "Sumó en lugar de restar, pese a que la piscina se está vaciando."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuál es el vértice de la parábola y = −x² + 4x + 1?",
        "(2, 5)",
        "El signo negativo del coeficiente principal invierte la parábola.\n\n"
        "1) x del vértice: −b/(2a), con a = −1 y b = 4. Entonces x = −4/(−2) = 2.\n"
        "2) Evalúa: −(2²) + 4 · 2 + 1 = −4 + 8 + 1 = 5.\n"
        "3) El vértice es (2, 5).\n"
        "4) Como a es negativo, la parábola se abre hacia abajo y ese punto es un "
        "máximo, no un mínimo.",
        [
            ("(−2, −11)", "Perdió uno de los signos negativos al calcular −b/(2a)."),
            ("(2, 13)", "Elevó al cuadrado sin aplicar el signo negativo del primer término."),
            ("(2, 1)", "Usó el término independiente como coordenada y sin evaluar la función."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuál es el valor máximo que alcanza la función y = −2x² + 8x − 3?",
        "5",
        "Con coeficiente principal negativo, el vértice es un máximo.\n\n"
        "1) Como a = −2 es negativo, la parábola se abre hacia abajo.\n"
        "2) x del vértice: −b/(2a) = −8/(−4) = 2.\n"
        "3) Evalúa: −2 · 2² + 8 · 2 − 3 = −8 + 16 − 3 = 5.\n"
        "4) El valor máximo es 5, alcanzado en x = 2.",
        [
            ("2", "Entregó la coordenada x del vértice en lugar del valor máximo."),
            ("−3", "Tomó el término independiente como si fuera el máximo."),
            ("No tiene máximo", "Confundió la orientación: con a negativo la parábola sí tiene un máximo."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿Cuál es la ecuación de la recta que pasa por los puntos (−1, 2) y (2, 11)?",
        "y = 3x + 5",
        "Primero la pendiente, después el coeficiente de posición.\n\n"
        "1) Pendiente: m = (11 − 2)/(2 − (−1)) = 9/3 = 3.\n"
        "2) La ecuación es y = 3x + n.\n"
        "3) Reemplaza el punto (−1, 2): 2 = 3(−1) + n, o sea 2 = −3 + n.\n"
        "4) Despeja: n = 5. La ecuación es y = 3x + 5. Verifica con (2, 11): "
        "6 + 5 = 11.",
        [
            ("y = 3x − 1", "Sumó el −3 en lugar de restarlo al despejar el coeficiente de posición."),
            ("y = 3x + 2", "Usó la coordenada y del primer punto como coeficiente de posición."),
            ("y = 9x + 5", "Olvidó dividir por la diferencia de las x al calcular la pendiente."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "¿En qué punto corta al eje X la recta y = 5x − 15?",
        "(3, 0)",
        "Sobre el eje X la coordenada y vale cero.\n\n"
        "1) Iguala y a cero: 5x − 15 = 0.\n"
        "2) Suma 15: 5x = 15.\n"
        "3) Divide por 5: x = 3.\n"
        "4) El punto de corte es (3, 0). Ese valor de x es el cero de la función.",
        [
            ("(0, 3)", "Intercambió las coordenadas: ese punto está sobre el eje Y."),
            ("(0, −15)", "Calculó el corte con el eje Y en lugar de con el eje X."),
            ("(15, 0)", "Despejó el 15 pero no dividió por el coeficiente 5."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "Una empresa tiene ingresos I(x) = 40x y costos C(x) = 15x + 1000, con x el número de unidades vendidas. ¿Cuál es su punto de equilibrio?",
        "40 unidades",
        "El punto de equilibrio es donde los ingresos igualan a los costos.\n\n"
        "1) Iguala: 40x = 15x + 1.000.\n"
        "2) Resta 15x: 25x = 1.000.\n"
        "3) Divide por 25: x = 40.\n"
        "4) Verifica: con 40 unidades el ingreso es 1.600 y el costo "
        "600 + 1.000 = 1.600. Coinciden.",
        [
            ("25 unidades", "Dividió el costo fijo por 40 en lugar de por la diferencia entre precio y costo variable."),
            ("66,7 unidades", "Dividió el costo fijo por 15, usando solo el costo variable."),
            ("1.000 unidades", "Tomó el costo fijo como si fuera el número de unidades."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "¿Cuál es la pendiente de la recta que pasa por los puntos (3, −2) y (7, 6)?",
        "2",
        "La fórmula es la misma, cuidando el signo de la coordenada negativa.\n\n"
        "1) Aplica m = (y₂ − y₁)/(x₂ − x₁).\n"
        "2) Numerador: 6 − (−2) = 6 + 2 = 8. Restar un negativo equivale a sumar.\n"
        "3) Denominador: 7 − 3 = 4.\n"
        "4) Pendiente: 8/4 = 2.",
        [
            ("1", "Calculó el numerador como 6 − 2, sin aplicar la resta de un negativo."),
            ("8", "Calculó solo el avance vertical sin dividir."),
            ("0,5", "Invirtió la fórmula de la pendiente."),
        ],
    ),
    _q(
        "alg_funciones", "dificil",
        "La parábola y = ax² + 2 pasa por el punto (2, 14). ¿Cuál es el valor de a?",
        "3",
        "Las coordenadas del punto deben satisfacer la ecuación.\n\n"
        "1) Reemplaza x = 2 e y = 14: 14 = a · 2² + 2.\n"
        "2) Calcula la potencia: 14 = 4a + 2.\n"
        "3) Resta 2: 4a = 12.\n"
        "4) Divide por 4: a = 3. Verifica: y = 3x² + 2 evaluada en x = 2 da "
        "12 + 2 = 14.",
        [
            ("12", "Despejó el 2 pero no dividió por el 4 que aporta el cuadrado."),
            ("6", "Multiplicó la base por 2 en vez de elevarla al cuadrado."),
            ("2", "Entregó el término independiente de la parábola en lugar de a."),
        ],
    ),
    _q(
        "alg_funciones", "medio",
        "Si f(x) = x² − 4x, ¿qué valor toma la función cuando x = −1?",
        "5",
        "Hay que cuidar los signos al reemplazar un valor negativo.\n\n"
        "1) Sustituye: f(−1) = (−1)² − 4 · (−1).\n"
        "2) Primer término: (−1)² = 1, porque todo cuadrado es positivo.\n"
        "3) Segundo término: −4 · (−1) = +4. Menos por menos da más.\n"
        "4) Suma: 1 + 4 = 5.",
        [
            ("−3", "Calculó (−1)² como −1, aplicando el cuadrado sin considerar el paréntesis."),
            ("−5", "Cambió el signo del resultado final."),
            ("3", "Dejó negativo el segundo término, calculando 1 − 4 y ajustando el signo."),
        ],
    ),
    # ==================================================================
    # LOTE 6 — eje NÚMEROS (M1), ampliación hasta la cuota por nodo
    # ==================================================================
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 1/3 + 2/5?",
        "11/15",
        "Para sumar fracciones se necesita un denominador común.\n\n"
        "1) El mínimo común múltiplo de 3 y 5 es 15, porque no tienen factores "
        "comunes: basta multiplicarlos.\n"
        "2) Convierte: 1/3 = 5/15 y 2/5 = 6/15.\n"
        "3) Suma los numeradores: 5/15 + 6/15 = 11/15.\n"
        "4) No se simplifica: 11 es primo y no divide a 15.",
        [
            ("3/8", "Sumó numeradores entre sí y denominadores entre sí."),
            ("2/15", "Multiplicó las fracciones en lugar de sumarlas."),
            ("1/15", "Restó las fracciones en vez de sumarlas."),
        ],
    ),
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 7/10 − 2/5?",
        "3/10",
        "Como 10 es múltiplo de 5, basta convertir una sola fracción.\n\n"
        "1) Lleva 2/5 a décimos: multiplicas arriba y abajo por 2, quedando 4/10.\n"
        "2) Resta los numeradores: 7/10 − 4/10 = 3/10.\n"
        "3) No se simplifica: 3 no divide a 10.",
        [
            ("5/5", "Restó numeradores entre sí y denominadores entre sí."),
            ("11/10", "Sumó las fracciones en lugar de restarlas."),
            ("14/50", "Multiplicó las fracciones en vez de restarlas."),
        ],
    ),
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 3/8 × 4/9?",
        "1/6",
        "Multiplicar fracciones no requiere denominador común.\n\n"
        "1) Multiplica numeradores entre sí y denominadores entre sí: "
        "(3 × 4)/(8 × 9) = 12/72.\n"
        "2) Simplifica dividiendo ambos por 12: 12 ÷ 12 = 1 y 72 ÷ 12 = 6.\n"
        "3) El resultado es 1/6.\n\n"
        "Atajo: podías simplificar antes de multiplicar, cancelando el 3 con el 9 y "
        "el 4 con el 8.",
        [
            ("7/17", "Sumó numeradores entre sí y denominadores entre sí."),
            ("27/32", "Invirtió la segunda fracción, como si fuera una división."),
            ("12/72", "Multiplicó correctamente pero no simplificó el resultado."),
        ],
    ),
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de (5/6) ÷ (5/12)?",
        "2",
        "Dividir por una fracción es multiplicar por su recíproco.\n\n"
        "1) El divisor es 5/12, cuyo recíproco es 12/5.\n"
        "2) La operación pasa a ser 5/6 × 12/5 = 60/30.\n"
        "3) Simplifica: 60 ÷ 30 = 2.\n"
        "4) Control: como 5/12 es menor que 5/6, el cociente debe ser mayor que 1.",
        [
            ("25/72", "Multiplicó directamente sin invertir el divisor."),
            ("1/2", "Invirtió el dividendo en lugar del divisor."),
            ("15/6", "Sumó las fracciones en lugar de dividirlas."),
        ],
    ),
    _q(
        "num_racionales", "facil",
        "¿Cuál es el resultado de 2/3 + 1/6 + 1/2?",
        "4/3",
        "Con tres fracciones se busca un único denominador común para todas.\n\n"
        "1) El mínimo común múltiplo de 3, 6 y 2 es 6.\n"
        "2) Convierte: 2/3 = 4/6, 1/6 queda igual, y 1/2 = 3/6.\n"
        "3) Suma: 4/6 + 1/6 + 3/6 = 8/6.\n"
        "4) Simplifica dividiendo por 2: 8/6 = 4/3.",
        [
            ("4/11", "Sumó numeradores entre sí y denominadores entre sí."),
            ("8/6", "Sumó correctamente pero no simplificó el resultado."),
            ("1/6", "Multiplicó las tres fracciones en lugar de sumarlas."),
        ],
    ),
    _q(
        "num_racionales", "facil",
        "Una receta pide 3/4 de taza de azúcar, pero se prepara solo la mitad de la receta. ¿Cuánta azúcar se necesita?",
        "3/8 de taza",
        "Calcular 'la mitad de' algo es multiplicar por 1/2.\n\n"
        "1) Plantea la operación: 3/4 × 1/2.\n"
        "2) Multiplica numeradores y denominadores: (3 × 1)/(4 × 2) = 3/8.\n"
        "3) Se necesitan 3/8 de taza.\n"
        "4) Control: 3/8 debe ser menor que 3/4, y en efecto lo es.",
        [
            ("3/2 de taza", "Dividió por 1/2 en lugar de multiplicar, obteniendo el doble."),
            ("1/4 de taza", "Restó 1/2 a 3/4 en vez de calcular la mitad."),
            ("5/4 de taza", "Sumó las fracciones en lugar de multiplicarlas."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de 1 − (2/7 + 1/3)?",
        "8/21",
        "Primero se resuelve el paréntesis y después se resta del entero.\n\n"
        "1) Denominador común de 7 y 3: 21. Convierte: 2/7 = 6/21 y 1/3 = 7/21.\n"
        "2) Suma: 6/21 + 7/21 = 13/21.\n"
        "3) Escribe el 1 como 21/21 para poder restar.\n"
        "4) Resta: 21/21 − 13/21 = 8/21.",
        [
            ("13/21", "Resolvió el paréntesis pero olvidó restarlo del entero."),
            ("3/10", "Sumó numeradores entre sí y denominadores entre sí dentro del paréntesis."),
            ("19/21", "Restó solo una de las dos fracciones del entero."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de (3/4) × (8/15)?",
        "2/5",
        "Conviene simplificar antes de multiplicar para trabajar con números "
        "pequeños.\n\n"
        "1) El 3 del numerador y el 15 del denominador se dividen por 3: quedan 1 y "
        "5.\n"
        "2) El 8 del numerador y el 4 del denominador se dividen por 4: quedan 2 y 1.\n"
        "3) Multiplica lo que queda: (1 × 2)/(1 × 5) = 2/5.\n"
        "4) Sin simplificar antes daría 24/60, que se reduce igualmente a 2/5.",
        [
            ("24/60", "Multiplicó correctamente pero no simplificó el resultado."),
            ("45/32", "Invirtió la segunda fracción, como si fuera una división."),
            ("11/19", "Sumó numeradores entre sí y denominadores entre sí."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de 5/2 ÷ 3/4?",
        "10/3",
        "Se multiplica por el recíproco del divisor.\n\n"
        "1) El recíproco de 3/4 es 4/3.\n"
        "2) La operación pasa a ser 5/2 × 4/3 = 20/6.\n"
        "3) Simplifica dividiendo por 2: 10/3.\n"
        "4) Control: 3/4 es menor que 1, así que dividir por él debe agrandar el "
        "5/2. Y 10/3 ≈ 3,33 es mayor que 2,5.",
        [
            ("15/8", "Multiplicó directamente sin invertir el divisor."),
            ("6/10", "Invirtió el dividendo en lugar del divisor."),
            ("20/6", "Aplicó bien la regla pero no simplificó."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "Un estanque está lleno hasta 5/6 de su capacidad. Si se consume 2/5 del agua que contiene, ¿qué fracción de la capacidad total queda?",
        "1/2",
        "Ojo con la referencia: el 2/5 se calcula sobre el agua que hay, no sobre la "
        "capacidad total.\n\n"
        "1) Si se consume 2/5 de lo que hay, queda 3/5 de esa cantidad.\n"
        "2) Calcula 3/5 de 5/6: multiplica 3/5 × 5/6 = 15/30.\n"
        "3) Simplifica: 15/30 = 1/2.\n"
        "4) Queda la mitad de la capacidad total.",
        [
            ("13/30", "Restó 2/5 directamente a 5/6, como si el 2/5 fuera de la capacidad total."),
            ("1/3", "Calculó el agua consumida en lugar de la que queda."),
            ("3/5", "Entregó la fracción del agua que queda, pero medida respecto del agua inicial y no de la capacidad total."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de 3 − 2/5 × 5/6?",
        "8/3",
        "La multiplicación se resuelve antes que la resta.\n\n"
        "1) Multiplica primero: 2/5 × 5/6 = 10/30, que se simplifica a 1/3.\n"
        "2) Ahora resta: 3 − 1/3.\n"
        "3) Escribe el 3 como 9/3: 9/3 − 1/3 = 8/3.\n"
        "4) Si hubieras restado primero, el resultado sería otro: el orden de las "
        "operaciones no es negociable.",
        [
            ("13/6", "Restó antes de multiplicar, calculando (3 − 2/5) × 5/6."),
            ("1/3", "Resolvió la multiplicación pero olvidó restarla del 3."),
            ("3/3", "Restó el 1/3 al numerador y al denominador por separado."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "Un albañil avanza 3/8 de un muro el lunes y 1/4 del muro el martes. ¿Qué fracción del muro lleva construida?",
        "5/8",
        "Se suman las dos fracciones de avance.\n\n"
        "1) Plantea: 3/8 + 1/4.\n"
        "2) Como 8 es múltiplo de 4, lleva 1/4 a octavos: 1/4 = 2/8.\n"
        "3) Suma: 3/8 + 2/8 = 5/8.\n"
        "4) Control: lleva algo más de la mitad del muro, coherente con 5/8 = 0,625.",
        [
            ("4/12", "Sumó numeradores entre sí y denominadores entre sí."),
            ("3/32", "Multiplicó las fracciones en lugar de sumarlas."),
            ("1/8", "Restó las fracciones en vez de sumarlas."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "¿Cuál es el resultado de (1/2 + 1/3) ÷ (1/2 − 1/3)?",
        "5",
        "Se resuelve cada paréntesis por separado y después se divide.\n\n"
        "1) Numerador: 1/2 + 1/3 con denominador 6 da 3/6 + 2/6 = 5/6.\n"
        "2) Denominador: 1/2 − 1/3 da 3/6 − 2/6 = 1/6.\n"
        "3) Divide: (5/6) ÷ (1/6) = 5/6 × 6/1 = 30/6.\n"
        "4) Simplifica: 5. El 6 se cancela porque ambos paréntesis quedaron con el "
        "mismo denominador.",
        [
            ("1/5", "Invirtió el orden de la división, dividiendo la resta por la suma."),
            ("5/6", "Resolvió el numerador pero no llegó a dividir."),
            ("6", "Canceló mal los denominadores al aplicar el recíproco."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "Si m = 3/4 y n = 2/3, ¿cuál es el valor de (m × n) + (m ÷ n)?",
        "13/8",
        "Se calculan las dos operaciones por separado y después se suman.\n\n"
        "1) Producto: 3/4 × 2/3 = 6/12 = 1/2.\n"
        "2) Cociente: 3/4 ÷ 2/3 = 3/4 × 3/2 = 9/8.\n"
        "3) Suma ambos resultados. Denominador común de 2 y 8 es 8: "
        "1/2 = 4/8.\n"
        "4) Resultado: 4/8 + 9/8 = 13/8.",
        [
            ("1", "Calculó el producto y el cociente pero los restó en lugar de sumarlos."),
            ("5/8", "Invirtió la fracción equivocada en la división, obteniendo 1/8 en vez de 9/8."),
            ("9/16", "Multiplicó los dos resultados en lugar de sumarlos."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "¿Cuál es el resultado de (2/3)² + 1/9?",
        "5/9",
        "Elevar una fracción al cuadrado afecta al numerador y al denominador.\n\n"
        "1) Calcula la potencia: (2/3)² = 2²/3² = 4/9.\n"
        "2) Ahora suma: 4/9 + 1/9. Los denominadores ya coinciden.\n"
        "3) Suma los numeradores: 5/9.\n"
        "4) No se simplifica: 5 no divide a 9.",
        [
            ("4/9", "Elevó al cuadrado correctamente pero olvidó sumar el 1/9."),
            ("2/3", "Elevó al cuadrado solo el numerador, obteniendo 4/3 y ajustando mal."),
            ("5/18", "Sumó también los denominadores al juntar las fracciones."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "Un depósito está lleno hasta sus 3/5 y se le agrega agua equivalente a 2/7 de su capacidad. ¿Qué fracción falta para llenarlo por completo?",
        "4/35",
        "Se suma lo que hay y se resta del total.\n\n"
        "1) Denominador común de 5 y 7: 35. Convierte: 3/5 = 21/35 y 2/7 = 10/35.\n"
        "2) Suma lo que hay: 21/35 + 10/35 = 31/35.\n"
        "3) El depósito completo es 35/35.\n"
        "4) Falta: 35/35 − 31/35 = 4/35.",
        [
            ("31/35", "Calculó lo que hay en el depósito, no lo que falta."),
            ("1/2", "Restó los numeradores y denominadores por separado."),
            ("6/35", "Multiplicó las fracciones en lugar de sumarlas antes de restar."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "¿Cuál de estas dos fracciones es mayor: 5/8 o 7/12?",
        "5/8",
        "Para comparar fracciones se llevan a un denominador común.\n\n"
        "1) El mínimo común múltiplo de 8 y 12 es 24.\n"
        "2) Convierte: 5/8 = 15/24 y 7/12 = 14/24.\n"
        "3) Con el mismo denominador manda el numerador: 15 > 14.\n"
        "4) Por lo tanto 5/8 es mayor. En decimales: 0,625 contra 0,583.",
        [
            ("7/12", "Comparó los denominadores suponiendo que el mayor indica una fracción mayor."),
            ("Son iguales", "No llevó las fracciones a un denominador común antes de comparar."),
            ("No se pueden comparar", "Fracciones con distinto denominador sí se comparan, igualándolas primero."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "Ordena de menor a mayor las fracciones 2/3, 3/5 y 7/10.",
        "3/5, 2/3, 7/10",
        "Se llevan todas a un denominador común, o se pasan a decimal.\n\n"
        "1) El mínimo común múltiplo de 3, 5 y 10 es 30.\n"
        "2) Convierte: 2/3 = 20/30, 3/5 = 18/30 y 7/10 = 21/30.\n"
        "3) Ordena por numerador: 18 < 20 < 21.\n"
        "4) El orden es 3/5, 2/3, 7/10. En decimales: 0,6 < 0,67 < 0,7.",
        [
            ("2/3, 3/5, 7/10", "Comparó los numeradores sin igualar los denominadores."),
            ("7/10, 2/3, 3/5", "Ordenó de mayor a menor en lugar de menor a mayor."),
            ("3/5, 7/10, 2/3", "Comparó bien las dos primeras pero invirtió las dos últimas."),
        ],
    ),
    _q(
        "num_racionales", "dificil",
        "¿Cuál es el resultado de (3/4 − 1/6) ÷ (1/2 + 1/3)?",
        "7/10",
        "Se resuelve cada paréntesis y después se aplica la división.\n\n"
        "1) Numerador: 3/4 − 1/6 con denominador 12 da 9/12 − 2/12 = 7/12.\n"
        "2) Denominador: 1/2 + 1/3 con denominador 6 da 3/6 + 2/6 = 5/6.\n"
        "3) Divide multiplicando por el recíproco: 7/12 × 6/5 = 42/60.\n"
        "4) Simplifica dividiendo por 6: 7/10.",
        [
            ("10/7", "Invirtió el orden de la división."),
            ("35/72", "Multiplicó los dos paréntesis en lugar de dividirlos."),
            ("42/60", "Aplicó bien la regla pero no simplificó el resultado."),
        ],
    ),
    _q(
        "num_racionales", "medio",
        "Se reparten 3/4 de kilo de café en 6 bolsas iguales. ¿Cuánto café lleva cada bolsa?",
        "1/8 de kilo",
        "Repartir en partes iguales es dividir.\n\n"
        "1) Plantea: 3/4 ÷ 6.\n"
        "2) Un entero se puede escribir como fracción: 6 = 6/1, cuyo recíproco es "
        "1/6.\n"
        "3) Multiplica: 3/4 × 1/6 = 3/24.\n"
        "4) Simplifica dividiendo por 3: 1/8 de kilo por bolsa.",
        [
            ("9/2 de kilo", "Multiplicó por 6 en lugar de dividir."),
            ("1/2 de kilo", "Dividió solo el numerador por 6 sin ajustar la fracción."),
            ("3/10 de kilo", "Restó 6 al denominador en vez de dividir la fracción."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de 4³?",
        "64",
        "Una potencia indica cuántas veces se multiplica la base por sí misma.\n\n"
        "1) El exponente 3 significa tres factores: 4 · 4 · 4.\n"
        "2) Calcula por pasos: 4 · 4 = 16.\n"
        "3) Luego 16 · 4 = 64.",
        [
            ("12", "Multiplicó la base por el exponente en lugar de elevar."),
            ("16", "Se detuvo en 4², usando un factor de menos."),
            ("256", "Usó un factor de más, calculando 4⁴."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de √100 + √9?",
        "13",
        "Cada raíz se resuelve por separado antes de sumar.\n\n"
        "1) √100 = 10, porque 10 · 10 = 100.\n"
        "2) √9 = 3, porque 3 · 3 = 9.\n"
        "3) Suma: 10 + 3 = 13.\n\n"
        "Recuerda que la raíz de una suma no es la suma de las raíces: "
        "√109 no vale 13.",
        [
            ("10,4", "Sumó primero dentro de las raíces y calculó √109."),
            ("30", "Multiplicó las raíces en lugar de sumarlas."),
            ("7", "Restó las raíces en vez de sumarlas."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de 2⁵ · 2²?",
        "128",
        "Al multiplicar potencias de igual base se suman los exponentes.\n\n"
        "1) Aplica la regla: 2⁵ · 2² = 2^(5+2) = 2⁷.\n"
        "2) Calcula 2⁷ duplicando siete veces: 2, 4, 8, 16, 32, 64, 128.\n"
        "3) Verificación directa: 2⁵ = 32 y 2² = 4, y 32 · 4 = 128.",
        [
            ("1.024", "Multiplicó los exponentes en lugar de sumarlos, calculando 2¹⁰."),
            ("36", "Sumó las potencias en vez de multiplicarlas: 32 + 4."),
            ("64", "Usó un exponente de menos, calculando 2⁶."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de (2²)⁴?",
        "256",
        "Una potencia de otra potencia multiplica los exponentes.\n\n"
        "1) Aplica la regla: (2²)⁴ = 2^(2·4) = 2⁸.\n"
        "2) Calcula 2⁸ = 256.\n"
        "3) Verificación: 2² = 4, y 4⁴ = 4 · 4 · 4 · 4 = 256. Coincide.",
        [
            ("64", "Sumó los exponentes en lugar de multiplicarlos, calculando 2⁶."),
            ("16", "Se quedó en el primer paso, calculando solo 2⁴."),
            ("32", "Usó el exponente equivocado, calculando 2⁵."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de 10⁻²?",
        "1/100",
        "El exponente negativo indica que hay que invertir la base, no cambiar el "
        "signo.\n\n"
        "1) Aplica a⁻ⁿ = 1/aⁿ: 10⁻² = 1/10².\n"
        "2) Calcula el denominador: 10² = 100.\n"
        "3) El resultado es 1/100, que también se escribe 0,01.",
        [
            ("−100", "Interpretó el signo del exponente como signo del resultado."),
            ("100", "Ignoró el signo negativo del exponente."),
            ("−1/100", "Invirtió correctamente pero además arrastró un signo negativo que no corresponde."),
        ],
    ),
    _q(
        "num_potencias_raices", "facil",
        "¿Cuál es el valor de √64 · √4?",
        "16",
        "Se puede resolver cada raíz por separado o juntarlas primero.\n\n"
        "1) Camino directo: √64 = 8 y √4 = 2.\n"
        "2) Multiplica: 8 · 2 = 16.\n"
        "3) Camino alternativo: el producto de raíces es la raíz del producto, "
        "√(64 · 4) = √256 = 16. Coincide.",
        [
            ("10", "Sumó las raíces en lugar de multiplicarlas."),
            ("256", "Multiplicó los números sin extraer después la raíz."),
            ("4", "Dividió las raíces en vez de multiplicarlas."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de (4³ · 4²) ÷ 4⁴?",
        "4",
        "Se combinan dos reglas sobre la misma base.\n\n"
        "1) En el numerador se suman los exponentes: 4³ · 4² = 4⁵.\n"
        "2) Al dividir se restan: 4⁵ ÷ 4⁴ = 4^(5−4) = 4¹.\n"
        "3) El resultado es 4.\n"
        "4) Atajo: opera todos los exponentes de una vez, 3 + 2 − 4 = 1.",
        [
            ("1.024", "Sumó los exponentes del numerador pero olvidó restar el del divisor."),
            ("16", "Restó los exponentes del numerador en lugar de sumarlos."),
            ("4⁹", "Sumó también el exponente del divisor en vez de restarlo."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de √72 en su forma más simple?",
        "6√2",
        "Se extraen los factores que sean cuadrados perfectos.\n\n"
        "1) Descompón 72 buscando el mayor cuadrado perfecto: 72 = 36 · 2.\n"
        "2) Separa: √72 = √36 · √2.\n"
        "3) Extrae la raíz exacta: √36 = 6.\n"
        "4) El resultado es 6√2. Verifica: (6√2)² = 36 · 2 = 72.",
        [
            ("36√2", "Sacó el 36 de la raíz sin calcular su raíz cuadrada."),
            ("2√6", "Intercambió el factor extraído con el que queda dentro."),
            ("12", "Multiplicó 6 por 2 como si la raíz hubiera desaparecido."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de (5²)³ ÷ 5⁴?",
        "25",
        "Primero la potencia de potencia, después la división.\n\n"
        "1) (5²)³ = 5^(2·3) = 5⁶, multiplicando los exponentes.\n"
        "2) Divide restando exponentes: 5⁶ ÷ 5⁴ = 5².\n"
        "3) Calcula: 5² = 25.",
        [
            ("5", "Sumó los exponentes de la potencia de potencia en lugar de multiplicarlos."),
            ("15.625", "Resolvió la potencia de potencia pero olvidó dividir."),
            ("625", "Restó mal los exponentes, quedándose en 5⁴."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de 3⁰ + 2⁻¹?",
        "3/2",
        "Hay dos reglas distintas en juego, una por cada término.\n\n"
        "1) Todo número distinto de cero elevado a cero vale 1, así que 3⁰ = 1.\n"
        "2) El exponente negativo invierte la base: 2⁻¹ = 1/2.\n"
        "3) Suma: 1 + 1/2 = 3/2.",
        [
            ("1/2", "Consideró que 3⁰ vale 0 en lugar de 1."),
            ("5/2", "Interpretó 2⁻¹ como 2, ignorando el exponente negativo."),
            ("−1", "Trató el exponente negativo como si volviera negativo el resultado."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de √98 − √50?",
        "2√2",
        "Dos raíces solo se restan si tienen el mismo radicando, así que primero se "
        "simplifican.\n\n"
        "1) √98: como 98 = 49 · 2, queda √49 · √2 = 7√2.\n"
        "2) √50: como 50 = 25 · 2, queda √25 · √2 = 5√2.\n"
        "3) Ahora comparten radicando, así que se restan los coeficientes: "
        "7√2 − 5√2 = 2√2.\n"
        "4) Control aproximado: 9,9 − 7,07 ≈ 2,83, y 2√2 ≈ 2,83.",
        [
            ("√48", "Restó los radicandos: √(98 − 50), que no es una operación válida."),
            ("12√2", "Sumó los coeficientes en lugar de restarlos."),
            ("2", "Restó bien los coeficientes pero perdió el radical."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "Una plaza cuadrada tiene un área de 121 m². ¿Cuánto mide cada uno de sus lados?",
        "11 m",
        "El área de un cuadrado es el lado elevado al cuadrado, así que el lado es "
        "la raíz del área.\n\n"
        "1) Plantea: lado² = 121.\n"
        "2) Saca raíz cuadrada: lado = √121.\n"
        "3) Como 11 · 11 = 121, el lado mide 11 m.\n"
        "4) Aunque −11 también cumple la ecuación, una medida no puede ser negativa.",
        [
            ("60,5 m", "Dividió el área por 2 en lugar de calcular su raíz cuadrada."),
            ("30,25 m", "Dividió el área por 4, confundiendo el área con el perímetro."),
            ("242 m", "Multiplicó el área por 2 en vez de sacarle la raíz."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de 2⁻³ · 2⁵?",
        "4",
        "La regla de sumar exponentes también vale cuando alguno es negativo.\n\n"
        "1) Suma los exponentes respetando el signo: −3 + 5 = 2.\n"
        "2) Queda 2² = 4.\n"
        "3) Verificación: 2⁻³ = 1/8 y 2⁵ = 32, y 32/8 = 4. Coincide.",
        [
            ("1/256", "Restó los exponentes en lugar de sumarlos, obteniendo 2⁻⁸."),
            ("256", "Ignoró el signo negativo, sumando 3 + 5."),
            ("−4", "Arrastró el signo del exponente al resultado."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "Si 5ˣ = 625, ¿cuál es el valor de x?",
        "4",
        "Se busca cuántas veces hay que multiplicar el 5 para llegar a 625.\n\n"
        "1) Ve multiplicando: 5, 25, 125, 625. Son cuatro factores.\n"
        "2) Entonces 625 = 5⁴.\n"
        "3) Como las bases coinciden, los exponentes también: x = 4.\n"
        "4) Verifica: 5⁴ = 625. Correcto.",
        [
            ("125", "Dividió 625 por 5 en lugar de buscar el exponente."),
            ("25", "Calculó la raíz cuadrada de 625, que responde otra pregunta."),
            ("5", "Contó una multiplicación de más: 5⁵ da 3.125."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "¿Cuál es el valor de (3⁻² · 3⁵) ÷ 3²?",
        "3",
        "Todos los exponentes se pueden operar de una sola vez.\n\n"
        "1) En el numerador se suman: −2 + 5 = 3, quedando 3³.\n"
        "2) Al dividir se resta el exponente del divisor: 3 − 2 = 1.\n"
        "3) Queda 3¹ = 3.\n"
        "4) Atajo: −2 + 5 − 2 = 1 directamente.",
        [
            ("27", "Sumó bien el numerador pero olvidó restar el exponente del divisor."),
            ("1/3", "Restó los exponentes del numerador en lugar de sumarlos."),
            ("243", "Ignoró el signo negativo del primer exponente."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "¿Cuál es el valor de √(5² + 12²)?",
        "13",
        "Primero se resuelve todo lo que está dentro de la raíz.\n\n"
        "1) Calcula los cuadrados: 5² = 25 y 12² = 144.\n"
        "2) Suma: 25 + 144 = 169.\n"
        "3) Saca la raíz: √169 = 13.\n\n"
        "Ojo con el error clásico: √(5² + 12²) no es 5 + 12. Estos números forman "
        "además un trío pitagórico conocido.",
        [
            ("17", "Sacó la raíz de cada término por separado y sumó: 5 + 12."),
            ("169", "Sumó correctamente pero no aplicó la raíz."),
            ("60", "Multiplicó los números dentro de la raíz en lugar de sumar sus cuadrados."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "¿Cuál es el valor de 2³ + 3²?",
        "17",
        "Cada potencia se calcula por separado, cuidando cuál es la base y cuál el "
        "exponente.\n\n"
        "1) 2³ significa 2 · 2 · 2 = 8.\n"
        "2) 3² significa 3 · 3 = 9.\n"
        "3) Suma: 8 + 9 = 17.\n\n"
        "Confundir base con exponente cambia el resultado: 3² no es lo mismo que 2³.",
        [
            ("13", "Multiplicó base por exponente en cada término: 6 + 6, y ajustó mal."),
            ("72", "Multiplicó las potencias en lugar de sumarlas."),
            ("16", "Calculó ambas potencias con la misma base, como 2³ + 2³."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "¿Cuál es el valor de √(16 · 25)?",
        "20",
        "La raíz de un producto es el producto de las raíces.\n\n"
        "1) Camino corto: √(16 · 25) = √16 · √25 = 4 · 5 = 20.\n"
        "2) Camino largo: 16 · 25 = 400, y √400 = 20.\n"
        "3) Ambos caminos coinciden. Esta propiedad vale para el producto, pero no "
        "para la suma.",
        [
            ("9", "Sumó las raíces en lugar de multiplicarlas."),
            ("400", "Multiplicó los números sin aplicar después la raíz."),
            ("41", "Sacó la raíz de cada factor y los sumó al cuadrado, mezclando operaciones."),
        ],
    ),
    _q(
        "num_potencias_raices", "medio",
        "¿Cuál es el valor de (7²)⁰?",
        "1",
        "Cualquier número distinto de cero elevado a cero vale 1.\n\n"
        "1) Multiplica los exponentes: (7²)⁰ = 7^(2·0) = 7⁰.\n"
        "2) Por la regla del exponente cero, 7⁰ = 1.\n"
        "3) No importa cuán grande sea la base: mientras no sea cero, el resultado "
        "es 1.",
        [
            ("0", "Supuso que elevar a cero anula el resultado."),
            ("49", "Ignoró el exponente exterior y calculó solo 7²."),
            ("7", "Aplicó el exponente cero solo a una parte de la expresión."),
        ],
    ),
    _q(
        "num_potencias_raices", "dificil",
        "Si 2^(x−1) = 16, ¿cuál es el valor de x?",
        "5",
        "Se iguala el exponente después de expresar ambos lados con la misma base.\n\n"
        "1) Escribe 16 como potencia de 2: 16 = 2⁴.\n"
        "2) La ecuación queda 2^(x−1) = 2⁴.\n"
        "3) Con bases iguales, los exponentes deben coincidir: x − 1 = 4.\n"
        "4) Despeja: x = 5. Verifica: 2^(5−1) = 2⁴ = 16.",
        [
            ("4", "Igualó x directamente al exponente, sin despejar el −1."),
            ("3", "Restó el 1 en lugar de sumarlo al despejar."),
            ("8", "Dividió 16 por 2 en vez de trabajar con los exponentes."),
        ],
    ),
    # ---------- num_porcentajes ----------
    _q(
        "num_porcentajes", "facil",
        "¿Cuánto es el 25% de 320?",
        "80",
        "El 25% equivale a la cuarta parte.\n\n"
        "1) Convierte el porcentaje a decimal: 25% = 0,25.\n"
        "2) Multiplica: 0,25 · 320 = 80.\n"
        "3) Camino mental: el 25% es dividir por 4, y 320 ÷ 4 = 80.",
        [
            ("8.000", "Multiplicó por 25 pero olvidó dividir por 100."),
            ("240", "Calculó el 75% restante en lugar del 25% pedido."),
            ("64", "Usó un 20% en lugar del 25%."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "¿Cuánto es el 60% de 45?",
        "27",
        "Se pasa el porcentaje a decimal y se multiplica.\n\n"
        "1) 60% = 0,6.\n"
        "2) Multiplica: 0,6 · 45 = 27.\n"
        "3) Camino mental: el 10% de 45 es 4,5, así que el 60% es 4,5 · 6 = 27.",
        [
            ("2.700", "Multiplicó por 60 sin dividir por 100."),
            ("18", "Calculó el 40% restante en lugar del 60%."),
            ("75", "Sumó 60 y 45 en lugar de calcular el porcentaje."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "Un producto cuesta $16.000 y tiene un descuento del 10%. ¿Cuál es su precio final?",
        "$14.400",
        "Con un 10% de descuento se paga el 90% del precio.\n\n"
        "1) Calcula el descuento: el 10% de 16.000 es 1.600.\n"
        "2) Réstalo: 16.000 − 1.600 = 14.400.\n"
        "3) Camino directo: 16.000 · 0,9 = 14.400.",
        [
            ("$1.600", "Calculó el descuento pero no lo restó del precio."),
            ("$17.600", "Sumó el 10% en lugar de restarlo."),
            ("$15.900", "Restó 100 pesos en vez del 10% del precio."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "Un sueldo de $450.000 sube un 8%. ¿Cuál es el nuevo sueldo?",
        "$486.000",
        "Subir un 8% significa quedar con el 108% del sueldo original.\n\n"
        "1) Calcula el aumento: el 8% de 450.000. Como el 1% es 4.500, el 8% es "
        "4.500 · 8 = 36.000.\n"
        "2) Suma: 450.000 + 36.000 = 486.000.\n"
        "3) Camino directo: 450.000 · 1,08 = 486.000.",
        [
            ("$36.000", "Calculó el aumento pero no lo sumó al sueldo original."),
            ("$414.000", "Restó el 8% en lugar de sumarlo."),
            ("$458.000", "Sumó 8.000 pesos en vez del 8% del sueldo."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "¿Qué porcentaje representa 18 de un total de 60?",
        "30%",
        "Se compara la parte con el total.\n\n"
        "1) Escribe la razón: 18/60.\n"
        "2) Simplifica dividiendo por 6: 3/10.\n"
        "3) Multiplica por 100: 3/10 · 100 = 30. El resultado es 30%.",
        [
            ("70%", "Calculó el porcentaje de la parte restante."),
            ("18%", "Tomó la cantidad como si ya fuera un porcentaje."),
            ("333%", "Dividió el total por la parte en lugar de la parte por el total."),
        ],
    ),
    _q(
        "num_porcentajes", "facil",
        "¿Qué porcentaje representa 9 de un total de 36?",
        "25%",
        "Se divide la parte por el total y se lleva a porcentaje.\n\n"
        "1) Razón: 9/36.\n"
        "2) Simplifica dividiendo por 9: 1/4.\n"
        "3) Un cuarto equivale al 25%.",
        [
            ("75%", "Calculó el porcentaje de la parte restante."),
            ("9%", "Tomó la cantidad como si fuera directamente un porcentaje."),
            ("400%", "Dividió el total por la parte."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "Después de aplicar un descuento del 40%, un producto queda en $9.000. ¿Cuál era su precio original?",
        "$15.000",
        "El precio final representa el 60% del original, no el 40%.\n\n"
        "1) Si se descontó un 40%, lo que se paga es el 100% − 40% = 60%.\n"
        "2) Plantea: 0,6 · precio = 9.000.\n"
        "3) Despeja dividiendo: precio = 9.000 ÷ 0,6 = 15.000.\n"
        "4) Verifica: el 40% de 15.000 es 6.000, y 15.000 − 6.000 = 9.000.",
        [
            ("$12.600", "Le sumó un 40% al precio final en lugar de deshacer el descuento."),
            ("$22.500", "Dividió por 0,4 en vez de por 0,6, usando el porcentaje descontado."),
            ("$13.000", "Sumó los 4.000 del descuento estimado a ojo."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "El precio de un artículo subió de $8.000 a $10.000. ¿Cuál fue el porcentaje de aumento?",
        "25%",
        "El aumento se mide siempre respecto del precio inicial.\n\n"
        "1) Calcula la diferencia: 10.000 − 8.000 = 2.000.\n"
        "2) Divide por el precio inicial, que es la referencia: 2.000/8.000 = 0,25.\n"
        "3) Multiplica por 100: 25%.\n"
        "4) Error frecuente: dividir por el precio final, que daría 20%.",
        [
            ("20%", "Dividió el aumento por el precio final en lugar del inicial."),
            ("2.000%", "Entregó la diferencia en pesos como si fuera un porcentaje."),
            ("125%", "Dividió el precio final por el inicial sin restar antes."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "El precio de un artículo bajó de $25.000 a $20.000. ¿Cuál fue el porcentaje de descuento?",
        "20%",
        "El descuento se mide respecto del precio original.\n\n"
        "1) Diferencia: 25.000 − 20.000 = 5.000.\n"
        "2) Divide por el precio original: 5.000/25.000 = 0,2.\n"
        "3) Multiplica por 100: 20%.\n"
        "4) Si dividieras por el precio final darías 25%, que responde otra pregunta.",
        [
            ("25%", "Dividió la rebaja por el precio final en lugar del original."),
            ("5.000%", "Entregó la rebaja en pesos como si fuera un porcentaje."),
            ("80%", "Calculó qué porcentaje del original representa el precio final."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "En una elección votaron 4.500 personas y un candidato obtuvo el 36% de los votos. ¿Cuántos votos obtuvo?",
        "1.620 votos",
        "Se calcula el porcentaje sobre el total de votantes.\n\n"
        "1) Convierte: 36% = 0,36.\n"
        "2) Multiplica: 0,36 · 4.500 = 1.620.\n"
        "3) Camino mental: el 1% de 4.500 es 45, así que el 36% es 45 · 36 = 1.620.",
        [
            ("2.880 votos", "Calculó los votos que no obtuvo, es decir el 64%."),
            ("162.000 votos", "Multiplicó por 36 sin dividir por 100."),
            ("125 votos", "Dividió el total por 36 en lugar de calcular el porcentaje."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "El 15% de un número es 45. ¿Cuál es ese número?",
        "300",
        "Aquí se conoce la parte y se busca el total.\n\n"
        "1) Plantea: 0,15 · n = 45.\n"
        "2) Despeja dividiendo: n = 45 ÷ 0,15.\n"
        "3) Calcula: 45 ÷ 0,15 = 300.\n"
        "4) Verifica: el 15% de 300 es 45. Correcto.",
        [
            ("6,75", "Calculó el 15% de 45 en lugar de despejar el total."),
            ("51,75", "Le sumó un 15% al 45."),
            ("675", "Multiplicó por 15 en vez de dividir por 0,15."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "En un curso de 30 estudiantes, el 40% son hombres. ¿Cuántas mujeres hay?",
        "18 mujeres",
        "Conviene calcular primero el porcentaje que corresponde a las mujeres.\n\n"
        "1) Si el 40% son hombres, el 60% son mujeres.\n"
        "2) Calcula el 60% de 30: 0,6 · 30 = 18.\n"
        "3) Hay 18 mujeres.\n"
        "4) Verifica: los hombres son el 40% de 30, o sea 12, y 12 + 18 = 30.",
        [
            ("12 mujeres", "Calculó la cantidad de hombres en lugar de la de mujeres."),
            ("40 mujeres", "Tomó el porcentaje como si fuera la cantidad de personas."),
            ("15 mujeres", "Repartió el curso en mitades iguales, ignorando el porcentaje."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "Un producto de $60.000 tiene descuentos sucesivos de 10% y 20%, aplicados uno después del otro. ¿Cuál es el precio final?",
        "$43.200",
        "El segundo descuento se calcula sobre el precio ya rebajado.\n\n"
        "1) Primer descuento: el 10% de 60.000 es 6.000, así que queda en 54.000.\n"
        "2) Segundo descuento: el 20% de 54.000 es 10.800.\n"
        "3) Precio final: 54.000 − 10.800 = 43.200.\n"
        "4) Camino directo: 60.000 · 0,9 · 0,8 = 43.200. Equivale a un único "
        "descuento del 28%, no del 30%.",
        [
            ("$42.000", "Sumó los descuentos y aplicó un 30% de una sola vez."),
            ("$54.000", "Aplicó solo el primer descuento."),
            ("$48.000", "Aplicó solo el descuento del 20%."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "El precio de un producto sube un 30% y luego baja un 30% sobre el nuevo precio. Respecto del precio inicial, ¿qué ocurre?",
        "Baja un 9%",
        "Conviene partir de un precio cómodo, por ejemplo 100.\n\n"
        "1) Alza del 30%: el precio pasa de 100 a 130.\n"
        "2) Baja del 30%, pero sobre 130: el 30% de 130 es 39.\n"
        "3) Precio final: 130 − 39 = 91.\n"
        "4) Comparado con el inicial, bajó 9 de cada 100, es decir un 9%. La clave es "
        "que la baja se aplica sobre una base mayor que la del alza.",
        [
            ("Queda igual que al principio", "Supuso que un alza y una baja del mismo porcentaje se anulan."),
            ("Baja un 30%", "Consideró solo la baja, ignorando el alza previa."),
            ("Sube un 9%", "Calculó bien la magnitud pero invirtió el sentido del cambio."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Cinco máquinas producen 200 piezas en 4 horas. Trabajando al mismo ritmo, ¿cuántas piezas producen 8 máquinas en esas mismas 4 horas?",
        "320 piezas",
        "Con el tiempo fijo, la producción es directamente proporcional al número de "
        "máquinas.\n\n"
        "1) Calcula la producción de una sola máquina: 200 ÷ 5 = 40 piezas en 4 "
        "horas.\n"
        "2) Multiplica por las 8 máquinas: 40 · 8 = 320.\n"
        "3) Control de sentido: más máquinas en el mismo tiempo produce más piezas, "
        "así que el resultado debe superar las 200.",
        [
            ("125 piezas", "Aplicó proporcionalidad inversa, como si más máquinas produjeran menos."),
            ("203 piezas", "Sumó las 3 máquinas adicionales como si fueran piezas."),
            ("1.600 piezas", "Multiplicó las 200 piezas por las 8 máquinas, sin dividir antes por 5."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Tres obreros pintan una casa en 12 días. ¿Cuántos días tardarían 4 obreros trabajando al mismo ritmo?",
        "9 días",
        "Más obreros implica menos días: es proporcionalidad inversa.\n\n"
        "1) Calcula el trabajo total en días-obrero: 3 · 12 = 36.\n"
        "2) Reparte ese trabajo entre 4 obreros: 36 ÷ 4 = 9.\n"
        "3) Tardarían 9 días.\n"
        "4) Control: al aumentar los obreros el plazo debe acortarse, y 9 < 12.",
        [
            ("16 días", "Aplicó proporcionalidad directa, alargando el plazo al sumar obreros."),
            ("11 días", "Restó un día por cada obrero adicional."),
            ("48 días", "Multiplicó los días por los obreros en lugar de dividir."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "Un capital aumenta un 20% y después ese nuevo monto aumenta un 25%. ¿Cuál es el aumento total respecto del capital inicial?",
        "50%",
        "Los aumentos sucesivos se multiplican, no se suman.\n\n"
        "1) Parte de 100. Tras el primer aumento: 100 · 1,2 = 120.\n"
        "2) El segundo aumento se aplica sobre 120: 120 · 1,25 = 150.\n"
        "3) De 100 a 150 hay un aumento de 50, es decir un 50%.\n"
        "4) El resultado supera la suma simple (20 + 25 = 45) porque el segundo "
        "aumento actúa sobre una base ya crecida.",
        [
            ("45%", "Sumó los porcentajes directamente en lugar de encadenarlos."),
            ("25%", "Consideró solo el segundo aumento."),
            ("5%", "Restó los porcentajes en vez de componerlos."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "Una camisa cuesta $19.900 y está con un 30% de descuento. ¿Cuánto se paga por ella?",
        "$13.930",
        "Con un 30% de descuento se paga el 70% del precio.\n\n"
        "1) Calcula el 70%: 19.900 · 0,7.\n"
        "2) Multiplica: 19.900 · 0,7 = 13.930.\n"
        "3) Camino alternativo: el 30% de 19.900 es 5.970, y "
        "19.900 − 5.970 = 13.930.",
        [
            ("$5.970", "Calculó el descuento pero no lo restó del precio."),
            ("$25.870", "Sumó el 30% en lugar de restarlo."),
            ("$16.900", "Restó 3.000 pesos en vez del 30% del precio."),
        ],
    ),
    _q(
        "num_porcentajes", "dificil",
        "El precio de un producto con IVA incluido de 19% es $23.800. ¿Cuál es su precio neto, sin IVA?",
        "$20.000",
        "El precio con IVA es el 119% del neto, no el 100%.\n\n"
        "1) Plantea: neto · 1,19 = 23.800.\n"
        "2) Despeja dividiendo: neto = 23.800 ÷ 1,19.\n"
        "3) Calcula: 20.000.\n"
        "4) Verifica: el 19% de 20.000 es 3.800, y 20.000 + 3.800 = 23.800.\n\n"
        "Error frecuente: restarle el 19% al precio con IVA, que daría 19.278 y no "
        "reconstruye el total al volver a aplicar el impuesto.",
        [
            ("$19.278", "Restó el 19% del precio con IVA en vez de dividir por 1,19."),
            ("$4.522", "Calculó el 19% del precio con IVA, que tampoco es el impuesto real."),
            ("$28.322", "Sumó el 19% en lugar de quitarlo."),
        ],
    ),
    _q(
        "num_porcentajes", "medio",
        "¿Cuánto es el 120% de 250?",
        "300",
        "Un porcentaje mayor que 100 da un resultado mayor que la cantidad "
        "original.\n\n"
        "1) Convierte: 120% = 1,2.\n"
        "2) Multiplica: 1,2 · 250 = 300.\n"
        "3) Otra lectura: el 100% de 250 es 250, y el 20% adicional es 50. "
        "Sumando, 300.",
        [
            ("250", "Supuso que un porcentaje nunca puede superar la cantidad original."),
            ("50", "Calculó solo el 20% adicional, sin sumar el 100%."),
            ("30.000", "Multiplicó por 120 sin dividir por 100."),
        ],
    ),
    # ==================================================================
    # LOTE 7 — eje GEOMETRÍA (M1)
    # ==================================================================
    # ---------- geo_plana ----------
    _q(
        "geo_plana", "facil",
        "¿Cuál es el área de un cuadrado de lado 7 cm?",
        "49 cm²",
        "El área de un cuadrado es el lado multiplicado por sí mismo.\n\n"
        "1) Aplica la fórmula A = lado².\n"
        "2) Calcula: 7 · 7 = 49.\n"
        "3) El área es 49 cm². Las unidades van al cuadrado porque se multiplican dos "
        "longitudes.",
        [
            ("28 cm²", "Calculó el perímetro en lugar del área."),
            ("14 cm²", "Multiplicó el lado por 2 en vez de elevarlo al cuadrado."),
            ("49 cm", "Calculó bien el número pero usó unidades de longitud en lugar de área."),
        ],
    ),
    _q(
        "geo_plana", "facil",
        "¿Cuál es el perímetro de un cuadrado de lado 9 cm?",
        "36 cm",
        "El perímetro es la suma de todos los lados.\n\n"
        "1) Un cuadrado tiene cuatro lados iguales, así que P = 4 · lado.\n"
        "2) Calcula: 4 · 9 = 36.\n"
        "3) El perímetro es 36 cm, en unidades de longitud.",
        [
            ("81 cm", "Calculó el área en lugar del perímetro."),
            ("18 cm", "Sumó solo dos lados."),
            ("36 cm²", "Calculó bien el número pero usó unidades de área."),
        ],
    ),
    _q(
        "geo_plana", "facil",
        "¿Cuál es el área de un rectángulo de 12 cm de largo y 6 cm de ancho?",
        "72 cm²",
        "El área de un rectángulo es largo por ancho.\n\n"
        "1) Aplica A = largo · ancho.\n"
        "2) Calcula: 12 · 6 = 72.\n"
        "3) El área es 72 cm².",
        [
            ("36 cm²", "Calculó el perímetro en lugar del área."),
            ("18 cm²", "Sumó las dimensiones en vez de multiplicarlas."),
            ("144 cm²", "Elevó el largo al cuadrado, tratándolo como un cuadrado."),
        ],
    ),
    _q(
        "geo_plana", "facil",
        "¿Cuál es el perímetro de un rectángulo de 15 cm de largo y 8 cm de ancho?",
        "46 cm",
        "El perímetro suma los cuatro lados: dos largos y dos anchos.\n\n"
        "1) Aplica P = 2 · (largo + ancho).\n"
        "2) Suma primero: 15 + 8 = 23.\n"
        "3) Multiplica por 2: 46.\n"
        "4) El perímetro es 46 cm.",
        [
            ("23 cm", "Sumó largo y ancho una sola vez, olvidando que cada lado se repite."),
            ("120 cm", "Multiplicó las dimensiones, que da el área y no el perímetro."),
            ("30 cm", "Duplicó solo el largo."),
        ],
    ),
    _q(
        "geo_plana", "facil",
        "¿Cuál es el área de un triángulo de base 14 cm y altura 5 cm?",
        "35 cm²",
        "El área de un triángulo es la mitad del producto entre base y altura.\n\n"
        "1) Aplica A = (base · altura)/2.\n"
        "2) Multiplica: 14 · 5 = 70.\n"
        "3) Divide por 2: 35.\n"
        "4) El área es 35 cm². La división por 2 viene de que el triángulo es la "
        "mitad de un rectángulo con la misma base y altura.",
        [
            ("70 cm²", "Multiplicó base por altura pero olvidó dividir por 2."),
            ("19 cm²", "Sumó base y altura en lugar de multiplicarlas."),
            ("9,5 cm²", "Sumó base y altura y después dividió por 2."),
        ],
    ),
    _q(
        "geo_plana", "facil",
        "¿Cuál es el perímetro de un triángulo equilátero de lado 12 cm?",
        "36 cm",
        "En un triángulo equilátero los tres lados son iguales.\n\n"
        "1) Aplica P = 3 · lado.\n"
        "2) Calcula: 3 · 12 = 36.\n"
        "3) El perímetro es 36 cm.",
        [
            ("48 cm", "Multiplicó por 4, como si fuera un cuadrilátero."),
            ("24 cm", "Sumó solo dos lados."),
            ("72 cm²", "Calculó base por altura suponiendo que la altura vale lo mismo que el lado."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "¿Cuál es el área de un círculo de radio 4 cm? (usa π ≈ 3,14)",
        "50,24 cm²",
        "El área de un círculo depende del cuadrado del radio.\n\n"
        "1) Aplica A = π · r².\n"
        "2) Eleva el radio al cuadrado primero: 4² = 16.\n"
        "3) Multiplica por π: 3,14 · 16 = 50,24.\n"
        "4) El área es 50,24 cm².",
        [
            ("25,12 cm²", "Calculó el perímetro (2πr) en lugar del área."),
            ("12,56 cm²", "Multiplicó π por el radio sin elevarlo al cuadrado."),
            ("100,48 cm²", "Usó el diámetro en lugar del radio dentro de la fórmula."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "¿Cuál es la longitud de una circunferencia de radio 7 cm? (usa π ≈ 3,14)",
        "43,96 cm",
        "La longitud de la circunferencia es su contorno.\n\n"
        "1) Aplica L = 2 · π · r.\n"
        "2) Calcula: 2 · 3,14 = 6,28.\n"
        "3) Multiplica por el radio: 6,28 · 7 = 43,96.\n"
        "4) La longitud es 43,96 cm, en unidades de longitud.",
        [
            ("153,86 cm", "Calculó el área en lugar de la longitud."),
            ("21,98 cm", "Olvidó multiplicar por 2 en la fórmula."),
            ("43,96 cm²", "Calculó bien el número pero usó unidades de área."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Un trapecio tiene bases de 10 cm y 6 cm, y una altura de 4 cm. ¿Cuál es su área?",
        "32 cm²",
        "El área de un trapecio usa el promedio de las dos bases.\n\n"
        "1) Aplica A = [(base mayor + base menor)/2] · altura.\n"
        "2) Suma las bases: 10 + 6 = 16.\n"
        "3) Divide por 2: 8. Ese es el promedio de las bases.\n"
        "4) Multiplica por la altura: 8 · 4 = 32 cm².",
        [
            ("64 cm²", "Sumó las bases y multiplicó por la altura sin dividir por 2."),
            ("240 cm²", "Multiplicó las dos bases entre sí y por la altura."),
            ("20 cm²", "Usó solo una de las bases en la fórmula del rectángulo."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Un rombo tiene diagonales que miden 12 cm y 8 cm. ¿Cuál es su área?",
        "48 cm²",
        "El área de un rombo se calcula con sus diagonales.\n\n"
        "1) Aplica A = (D · d)/2, donde D y d son las diagonales.\n"
        "2) Multiplica: 12 · 8 = 96.\n"
        "3) Divide por 2: 48.\n"
        "4) El área es 48 cm².",
        [
            ("96 cm²", "Multiplicó las diagonales pero olvidó dividir por 2."),
            ("40 cm²", "Calculó el perímetro suponiendo que las diagonales son lados."),
            ("20 cm²", "Sumó las diagonales en lugar de multiplicarlas."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Una cancha rectangular mide 30 m de largo y 18 m de ancho. ¿Cuántos metros de alambre se necesitan para cercarla completamente?",
        "96 m",
        "Cercar significa rodear el borde, así que se pide el perímetro.\n\n"
        "1) Aplica P = 2 · (largo + ancho).\n"
        "2) Suma: 30 + 18 = 48.\n"
        "3) Multiplica por 2: 96.\n"
        "4) Se necesitan 96 m de alambre.",
        [
            ("540 m", "Calculó el área en lugar del perímetro."),
            ("48 m", "Sumó largo y ancho una sola vez."),
            ("60 m", "Duplicó solo el largo de la cancha."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Una sala rectangular mide 6,5 m por 4 m. ¿Cuál es su superficie?",
        "26 m²",
        "La superficie de un rectángulo es el producto de sus dimensiones.\n\n"
        "1) Aplica A = largo · ancho.\n"
        "2) Calcula: 6,5 · 4. Puedes verlo como 6 · 4 = 24 más 0,5 · 4 = 2.\n"
        "3) Total: 26.\n"
        "4) La superficie es 26 m².",
        [
            ("21 m²", "Calculó el perímetro en lugar de la superficie."),
            ("10,5 m²", "Sumó las dimensiones en vez de multiplicarlas."),
            ("24 m²", "Ignoró los 0,5 m al multiplicar."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Un cuadrado tiene un perímetro de 48 cm. ¿Cuál es su área?",
        "144 cm²",
        "Primero hay que recuperar el lado a partir del perímetro.\n\n"
        "1) El perímetro de un cuadrado es 4 veces el lado, así que "
        "lado = 48 ÷ 4 = 12 cm.\n"
        "2) Ahora calcula el área: 12² = 144.\n"
        "3) El área es 144 cm².",
        [
            ("2.304 cm²", "Elevó el perímetro al cuadrado en lugar del lado."),
            ("48 cm²", "Entregó el perímetro con unidades de área."),
            ("24 cm²", "Dividió el perímetro por 2 en lugar de calcular el lado y elevarlo."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "Un triángulo tiene un área de 36 cm² y su altura mide 9 cm. ¿Cuánto mide su base?",
        "8 cm",
        "Se despeja la base a partir de la fórmula del área.\n\n"
        "1) La fórmula es A = (base · altura)/2.\n"
        "2) Reemplaza: 36 = (base · 9)/2.\n"
        "3) Multiplica ambos lados por 2: 72 = base · 9.\n"
        "4) Divide por 9: base = 8 cm.",
        [
            ("4 cm", "Dividió el área por la altura sin multiplicar antes por 2."),
            ("324 cm", "Multiplicó el área por la altura en lugar de dividir."),
            ("18 cm", "Multiplicó por 2 pero dividió por la mitad de la altura."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Un círculo tiene un diámetro de 10 cm. ¿Cuál es su área? (usa π ≈ 3,14)",
        "78,5 cm²",
        "La fórmula usa el radio, no el diámetro: ese es el paso que se olvida.\n\n"
        "1) El radio es la mitad del diámetro: 10 ÷ 2 = 5 cm.\n"
        "2) Aplica A = π · r²: eleva primero, 5² = 25.\n"
        "3) Multiplica: 3,14 · 25 = 78,5.\n"
        "4) El área es 78,5 cm².",
        [
            ("314 cm²", "Usó el diámetro como si fuera el radio."),
            ("31,4 cm²", "Calculó la longitud de la circunferencia en lugar del área."),
            ("15,7 cm²", "Multiplicó π por el radio sin elevarlo al cuadrado."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Un terreno rectangular tiene un perímetro de 44 m y su largo mide 4 m más que su ancho. ¿Cuál es su área?",
        "117 m²",
        "Primero se hallan las dimensiones y después el área.\n\n"
        "1) Llama a al ancho. El largo es a + 4.\n"
        "2) El perímetro es 2(a + a + 4) = 44, o sea 4a + 8 = 44.\n"
        "3) Despeja: 4a = 36, entonces a = 9. El largo es 13.\n"
        "4) Área: 9 · 13 = 117 m². Verifica el perímetro: 2(9 + 13) = 44.",
        [
            ("44 m²", "Entregó el perímetro con unidades de área."),
            ("121 m²", "Repartió el perímetro en partes iguales, ignorando la diferencia de 4 m."),
            ("22 m²", "Dividió el perímetro por 2 y lo tomó como área."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Si el radio de un círculo se duplica, ¿qué ocurre con su área?",
        "Queda multiplicada por 4",
        "El radio aparece elevado al cuadrado, y eso amplifica el efecto.\n\n"
        "1) El área original es A = π · r².\n"
        "2) Con el radio duplicado: π · (2r)² = π · 4r².\n"
        "3) Eso es 4 veces el área original.\n"
        "4) Ejemplo concreto: con r = 3 el área es 28,26; con r = 6 es 113,04, "
        "exactamente el cuádruple.",
        [
            ("Queda multiplicada por 2", "Supuso que el área crece en la misma proporción que el radio."),
            ("Queda multiplicada por 8", "Aplicó el factor del volumen, que eleva al cubo."),
            ("Queda multiplicada por 16", "Elevó al cuadrado el factor 4 en lugar del 2."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Un cuadrado de lado 8 cm tiene inscrito un círculo que toca sus cuatro lados. ¿Cuál es el área de la región del cuadrado que queda fuera del círculo? (usa π ≈ 3,14)",
        "13,76 cm²",
        "Se resta el área del círculo a la del cuadrado.\n\n"
        "1) Área del cuadrado: 8² = 64 cm².\n"
        "2) El círculo inscrito tiene diámetro igual al lado, así que su radio es "
        "8 ÷ 2 = 4 cm.\n"
        "3) Área del círculo: 3,14 · 4² = 3,14 · 16 = 50,24 cm².\n"
        "4) Resta: 64 − 50,24 = 13,76 cm².",
        [
            ("50,24 cm²", "Entregó el área del círculo en lugar de la región que queda fuera."),
            ("64 cm²", "Entregó el área del cuadrado sin descontar el círculo."),
            ("−136,96 cm²", "Usó el lado completo como radio del círculo, obteniendo un área mayor que la del cuadrado."),
        ],
    ),
    _q(
        "geo_plana", "medio",
        "¿Cuál es el área de un paralelogramo de base 9 cm y altura 5 cm?",
        "45 cm²",
        "El área de un paralelogramo es base por altura, sin dividir por dos.\n\n"
        "1) Aplica A = base · altura.\n"
        "2) Calcula: 9 · 5 = 45.\n"
        "3) El área es 45 cm².\n\n"
        "Ojo: la altura es la distancia perpendicular entre las bases, no la medida "
        "del lado inclinado.",
        [
            ("22,5 cm²", "Dividió por 2, aplicando la fórmula del triángulo."),
            ("28 cm²", "Calculó el perímetro suponiendo que la altura es un lado."),
            ("14 cm²", "Sumó base y altura en lugar de multiplicarlas."),
        ],
    ),
    _q(
        "geo_plana", "dificil",
        "Una piscina rectangular mide 12 m por 5 m y está rodeada por una vereda de 1 m de ancho en todo su contorno. ¿Cuál es el área de la vereda?",
        "38 m²",
        "Se calcula el área total incluyendo la vereda y se le resta la piscina.\n\n"
        "1) La vereda agrega 1 m por cada lado, así que el rectángulo exterior mide "
        "12 + 2 = 14 m por 5 + 2 = 7 m.\n"
        "2) Área exterior: 14 · 7 = 98 m².\n"
        "3) Área de la piscina: 12 · 5 = 60 m².\n"
        "4) Área de la vereda: 98 − 60 = 38 m².",
        [
            ("98 m²", "Entregó el área total incluyendo la piscina."),
            ("22 m²", "Agregó 1 m a cada dimensión en vez de 2, olvidando que la vereda rodea ambos extremos."),
            ("34 m²", "Calculó el perímetro de la piscina y lo multiplicó por el ancho de la vereda, sin contar las esquinas."),
        ],
    ),
    # ---------- geo_pitagoras ----------
    _q(
        "geo_pitagoras", "facil",
        "Un triángulo rectángulo tiene catetos de 5 cm y 12 cm. ¿Cuánto mide la hipotenusa?",
        "13 cm",
        "El teorema de Pitágoras relaciona los tres lados de un triángulo "
        "rectángulo.\n\n"
        "1) La fórmula es h² = a² + b², con h la hipotenusa.\n"
        "2) Calcula los cuadrados: 5² = 25 y 12² = 144.\n"
        "3) Suma: 25 + 144 = 169.\n"
        "4) Saca la raíz: h = √169 = 13 cm.",
        [
            ("17 cm", "Sumó los catetos directamente, sin elevarlos al cuadrado."),
            ("169 cm", "Sumó los cuadrados pero no aplicó la raíz."),
            ("7 cm", "Restó los catetos en lugar de aplicar el teorema."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "Un triángulo rectángulo tiene catetos de 8 cm y 15 cm. ¿Cuánto mide la hipotenusa?",
        "17 cm",
        "Se aplica el teorema de Pitágoras.\n\n"
        "1) h² = 8² + 15².\n"
        "2) Calcula: 64 + 225 = 289.\n"
        "3) Saca la raíz: √289 = 17.\n"
        "4) La hipotenusa mide 17 cm. Siempre es el lado más largo del triángulo.",
        [
            ("23 cm", "Sumó los catetos sin elevarlos al cuadrado."),
            ("289 cm", "Sumó los cuadrados pero olvidó la raíz."),
            ("12,7 cm", "Sacó la raíz de cada cateto antes de sumar."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "En un triángulo rectángulo, la hipotenusa mide 10 cm y uno de sus catetos mide 6 cm. ¿Cuánto mide el otro cateto?",
        "8 cm",
        "Cuando se busca un cateto, el teorema se usa restando.\n\n"
        "1) De h² = a² + b² se despeja b² = h² − a².\n"
        "2) Calcula: 10² − 6² = 100 − 36 = 64.\n"
        "3) Saca la raíz: √64 = 8 cm.\n"
        "4) Verifica: 6² + 8² = 36 + 64 = 100 = 10².",
        [
            ("4 cm", "Restó las medidas directamente, sin elevarlas al cuadrado."),
            ("11,7 cm", "Sumó los cuadrados en lugar de restarlos."),
            ("64 cm", "Restó los cuadrados pero no aplicó la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "En un triángulo rectángulo, la hipotenusa mide 17 cm y un cateto mide 8 cm. ¿Cuánto mide el otro cateto?",
        "15 cm",
        "Se despeja el cateto desconocido.\n\n"
        "1) b² = h² − a² = 17² − 8².\n"
        "2) Calcula: 289 − 64 = 225.\n"
        "3) Saca la raíz: √225 = 15 cm.\n"
        "4) Verifica: 8² + 15² = 64 + 225 = 289 = 17².",
        [
            ("9 cm", "Restó las medidas sin elevarlas al cuadrado."),
            ("18,8 cm", "Sumó los cuadrados en vez de restarlos."),
            ("225 cm", "Restó bien los cuadrados pero olvidó la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "facil",
        "Un triángulo rectángulo tiene catetos de 7 cm y 24 cm. ¿Cuánto mide la hipotenusa?",
        "25 cm",
        "Se aplica el teorema de Pitágoras.\n\n"
        "1) h² = 7² + 24² = 49 + 576.\n"
        "2) Suma: 625.\n"
        "3) Saca la raíz: √625 = 25 cm.\n"
        "4) Los números 7, 24 y 25 forman un trío pitagórico, igual que 3-4-5.",
        [
            ("31 cm", "Sumó los catetos sin elevarlos al cuadrado."),
            ("625 cm", "Sumó los cuadrados pero no aplicó la raíz."),
            ("17 cm", "Restó los catetos en lugar de aplicar el teorema."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "¿Cuánto mide la diagonal de un rectángulo que mide 9 cm por 12 cm?",
        "15 cm",
        "La diagonal divide al rectángulo en dos triángulos rectángulos.\n\n"
        "1) Los lados del rectángulo son los catetos y la diagonal es la "
        "hipotenusa.\n"
        "2) d² = 9² + 12² = 81 + 144 = 225.\n"
        "3) Saca la raíz: √225 = 15 cm.\n"
        "4) Control: la diagonal siempre debe ser mayor que cualquiera de los lados.",
        [
            ("21 cm", "Sumó los lados sin elevarlos al cuadrado."),
            ("108 cm", "Calculó el área del rectángulo en lugar de la diagonal."),
            ("3 cm", "Restó los lados en vez de aplicar el teorema."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "¿Cuánto mide la diagonal de un cuadrado de lado 10 cm?",
        "10√2 cm",
        "La diagonal de un cuadrado forma un triángulo rectángulo con dos lados "
        "iguales.\n\n"
        "1) d² = 10² + 10² = 100 + 100 = 200.\n"
        "2) Saca la raíz: √200.\n"
        "3) Simplifica: 200 = 100 · 2, así que √200 = 10√2.\n"
        "4) Aproximadamente 14,1 cm. En general, la diagonal de un cuadrado es su "
        "lado multiplicado por √2.",
        [
            ("20 cm", "Sumó los dos lados sin elevarlos al cuadrado."),
            ("100 cm", "Calculó el área del cuadrado en lugar de la diagonal."),
            ("10 cm", "Supuso que la diagonal mide lo mismo que el lado."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "Una rampa sube 3 m de altura a lo largo de una base horizontal de 4 m. ¿Cuánto mide la superficie inclinada de la rampa?",
        "5 m",
        "La rampa, la altura y la base forman un triángulo rectángulo.\n\n"
        "1) La altura y la base son los catetos; la rampa es la hipotenusa.\n"
        "2) r² = 3² + 4² = 9 + 16 = 25.\n"
        "3) Saca la raíz: √25 = 5 m.\n"
        "4) Este es el trío pitagórico más conocido: 3, 4 y 5.",
        [
            ("7 m", "Sumó altura y base sin elevarlas al cuadrado."),
            ("12 m", "Multiplicó altura por base, que da el doble del área."),
            ("1 m", "Restó la altura de la base."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "Un mástil de 12 m de alto se sujeta con un cable tensado desde su punta hasta un punto del suelo situado a 5 m de su base. ¿Cuánto mide el cable?",
        "13 m",
        "El mástil, el suelo y el cable forman un triángulo rectángulo.\n\n"
        "1) El mástil y la distancia en el suelo son los catetos; el cable es la "
        "hipotenusa.\n"
        "2) c² = 12² + 5² = 144 + 25 = 169.\n"
        "3) Saca la raíz: √169 = 13 m.\n"
        "4) Control: el cable debe ser más largo que el mástil, y 13 > 12.",
        [
            ("17 m", "Sumó las medidas sin elevarlas al cuadrado."),
            ("60 m", "Multiplicó las dos medidas."),
            ("10,9 m", "Restó los cuadrados en lugar de sumarlos."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "Un triángulo rectángulo tiene catetos de 20 cm y 21 cm. ¿Cuánto mide la hipotenusa?",
        "29 cm",
        "Se aplica el teorema aunque los números no sean los habituales.\n\n"
        "1) h² = 20² + 21² = 400 + 441.\n"
        "2) Suma: 841.\n"
        "3) Saca la raíz: √841 = 29 cm.\n"
        "4) Verifica: 29² = 841. Correcto.",
        [
            ("41 cm", "Sumó los catetos sin elevarlos al cuadrado."),
            ("841 cm", "Sumó los cuadrados pero no aplicó la raíz."),
            ("1 cm", "Restó los catetos en vez de aplicar el teorema."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "En un triángulo rectángulo la hipotenusa mide 15 cm y un cateto mide 9 cm. ¿Cuánto mide el otro cateto?",
        "12 cm",
        "Se despeja el cateto restando los cuadrados.\n\n"
        "1) b² = 15² − 9² = 225 − 81 = 144.\n"
        "2) Saca la raíz: √144 = 12 cm.\n"
        "3) Verifica: 9² + 12² = 81 + 144 = 225 = 15².\n"
        "4) Este triángulo es el 3-4-5 multiplicado por 3.",
        [
            ("6 cm", "Restó las medidas directamente, sin elevarlas al cuadrado."),
            ("17,5 cm", "Sumó los cuadrados en lugar de restarlos."),
            ("144 cm", "Restó bien pero olvidó aplicar la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "Una cancha rectangular mide 60 m por 80 m. ¿Cuánto mide su diagonal?",
        "100 m",
        "La diagonal es la hipotenusa del triángulo que forman dos lados.\n\n"
        "1) d² = 60² + 80² = 3.600 + 6.400 = 10.000.\n"
        "2) Saca la raíz: √10.000 = 100 m.\n"
        "3) Control: la diagonal debe superar al lado más largo, y 100 > 80.\n"
        "4) Es el trío 3-4-5 multiplicado por 20.",
        [
            ("140 m", "Sumó los lados sin elevarlos al cuadrado."),
            ("4.800 m", "Calculó el área de la cancha en lugar de la diagonal."),
            ("20 m", "Restó los lados en vez de aplicar el teorema."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "¿Cuál de estos tríos de medidas SÍ puede formar un triángulo rectángulo?",
        "9, 40 y 41",
        "Un trío forma triángulo rectángulo si cumple el teorema de Pitágoras, con "
        "el mayor como hipotenusa.\n\n"
        "1) Prueba 9, 40 y 41: 9² + 40² = 81 + 1.600 = 1.681, y 41² = 1.681. "
        "Cumple.\n"
        "2) Prueba 5, 6 y 8: 25 + 36 = 61, pero 8² = 64. No cumple.\n"
        "3) Prueba 7, 8 y 12: 49 + 64 = 113, pero 12² = 144. No cumple.\n"
        "4) Prueba 10, 12 y 15: 100 + 144 = 244, pero 15² = 225. No cumple.",
        [
            ("5, 6 y 8", "La suma de los cuadrados de los dos menores da 61, no 64."),
            ("7, 8 y 12", "La suma de los cuadrados de los dos menores da 113, no 144."),
            ("10, 12 y 15", "La suma de los cuadrados de los dos menores da 244, no 225."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "Un triángulo rectángulo tiene hipotenusa 10 cm y un cateto de 6 cm. ¿Cuál es su área?",
        "24 cm²",
        "Primero hay que encontrar el cateto que falta, porque el área los usa a "
        "ambos.\n\n"
        "1) Calcula el otro cateto: b² = 10² − 6² = 100 − 36 = 64, entonces b = 8 cm.\n"
        "2) En un triángulo rectángulo los catetos son la base y la altura.\n"
        "3) Área = (6 · 8)/2 = 48/2.\n"
        "4) El área es 24 cm².",
        [
            ("30 cm²", "Usó la hipotenusa como si fuera un cateto: (6 · 10)/2."),
            ("48 cm²", "Multiplicó los catetos pero olvidó dividir por 2."),
            ("8 cm²", "Entregó la medida del cateto faltante en lugar del área."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "Una escalera de 13 m se apoya contra una pared vertical y su base está a 5 m de la pared. ¿A qué altura llega la escalera?",
        "12 m",
        "La escalera es la hipotenusa; la pared y el suelo son los catetos.\n\n"
        "1) Despeja la altura: a² = 13² − 5².\n"
        "2) Calcula: 169 − 25 = 144.\n"
        "3) Saca la raíz: √144 = 12 m.\n"
        "4) Control: la altura debe ser menor que la escalera, y 12 < 13.",
        [
            ("8 m", "Restó las medidas directamente, sin elevarlas al cuadrado."),
            ("13,9 m", "Sumó los cuadrados en lugar de restarlos, obteniendo una altura mayor que la escalera."),
            ("144 m", "Restó bien los cuadrados pero olvidó la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "¿Cuál es el perímetro de un triángulo rectángulo de catetos 6 cm y 8 cm?",
        "24 cm",
        "El perímetro necesita los tres lados, así que primero hay que hallar la "
        "hipotenusa.\n\n"
        "1) h² = 6² + 8² = 36 + 64 = 100, entonces h = 10 cm.\n"
        "2) Suma los tres lados: 6 + 8 + 10.\n"
        "3) El perímetro es 24 cm.",
        [
            ("14 cm", "Sumó solo los dos catetos, sin incluir la hipotenusa."),
            ("48 cm", "Calculó el doble del producto de los catetos."),
            ("10 cm", "Entregó la hipotenusa en lugar del perímetro."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "¿Cuál es la altura de un triángulo equilátero de lado 8 cm?",
        "4√3 cm",
        "La altura divide al triángulo equilátero en dos triángulos rectángulos "
        "iguales.\n\n"
        "1) La altura cae en el punto medio de la base, así que uno de los catetos "
        "mide 8 ÷ 2 = 4 cm.\n"
        "2) La hipotenusa es el lado completo, 8 cm.\n"
        "3) Despeja la altura: a² = 8² − 4² = 64 − 16 = 48.\n"
        "4) Saca la raíz y simplifica: √48 = √(16 · 3) = 4√3 cm, aproximadamente "
        "6,93 cm.",
        [
            ("8 cm", "Supuso que la altura mide lo mismo que el lado."),
            ("4 cm", "Entregó la mitad de la base en lugar de la altura."),
            ("√48 cm", "Aplicó bien el teorema pero no simplificó la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "Dos personas parten del mismo punto: una camina 9 km hacia el norte y la otra 12 km hacia el este. ¿A qué distancia quedan una de la otra?",
        "15 km",
        "Norte y este forman un ángulo recto, así que los recorridos son los "
        "catetos.\n\n"
        "1) La distancia entre ambas es la hipotenusa: d² = 9² + 12².\n"
        "2) Calcula: 81 + 144 = 225.\n"
        "3) Saca la raíz: √225 = 15 km.\n"
        "4) Control: la distancia directa debe ser menor que la suma de los "
        "recorridos (21 km) y mayor que cada uno por separado.",
        [
            ("21 km", "Sumó las distancias como si hubieran caminado en la misma dirección."),
            ("3 km", "Restó las distancias recorridas."),
            ("108 km", "Multiplicó las dos distancias."),
        ],
    ),
    _q(
        "geo_pitagoras", "medio",
        "En un triángulo rectángulo la hipotenusa mide 26 cm y un cateto mide 10 cm. ¿Cuánto mide el otro cateto?",
        "24 cm",
        "Se despeja restando los cuadrados.\n\n"
        "1) b² = 26² − 10² = 676 − 100 = 576.\n"
        "2) Saca la raíz: √576 = 24 cm.\n"
        "3) Verifica: 10² + 24² = 100 + 576 = 676 = 26².\n"
        "4) Es el trío 5-12-13 multiplicado por 2.",
        [
            ("16 cm", "Restó las medidas sin elevarlas al cuadrado."),
            ("27,9 cm", "Sumó los cuadrados en lugar de restarlos."),
            ("576 cm", "Restó bien los cuadrados pero no aplicó la raíz."),
        ],
    ),
    _q(
        "geo_pitagoras", "dificil",
        "Un rombo tiene diagonales que miden 16 cm y 12 cm. ¿Cuánto mide cada uno de sus lados?",
        "10 cm",
        "Las diagonales de un rombo se cortan en el punto medio y forman ángulo "
        "recto.\n\n"
        "1) Cada diagonal queda dividida en dos mitades: 16 ÷ 2 = 8 cm y "
        "12 ÷ 2 = 6 cm.\n"
        "2) Esas mitades son los catetos de un triángulo rectángulo cuyo lado "
        "inclinado es el lado del rombo.\n"
        "3) l² = 8² + 6² = 64 + 36 = 100.\n"
        "4) Saca la raíz: l = 10 cm. Los cuatro lados del rombo miden lo mismo.",
        [
            ("14 cm", "Sumó las mitades de las diagonales sin aplicar el teorema."),
            ("20 cm", "Usó las diagonales completas como catetos en lugar de sus mitades."),
            ("28 cm", "Sumó las diagonales completas y dividió por 1, sin usar el teorema."),
        ],
    ),
    # ---------- geo_transformaciones ----------
    _q(
        "geo_transformaciones", "facil",
        "El punto (5, 2) se traslada según el vector (3, −4). ¿Cuáles son sus nuevas coordenadas?",
        "(8, −2)",
        "Trasladar es sumar el vector a las coordenadas del punto.\n\n"
        "1) Suma las primeras coordenadas: 5 + 3 = 8.\n"
        "2) Suma las segundas: 2 + (−4) = −2.\n"
        "3) El punto trasladado es (8, −2).",
        [
            ("(2, 6)", "Restó el vector en lugar de sumarlo."),
            ("(8, 2)", "Ignoró el signo negativo de la segunda componente del vector."),
            ("(15, −8)", "Multiplicó las coordenadas por el vector en vez de sumarlas."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "El punto (−1, 3) se traslada según el vector (2, 5). ¿Cuáles son sus nuevas coordenadas?",
        "(1, 8)",
        "Se suma componente a componente.\n\n"
        "1) Primera coordenada: −1 + 2 = 1.\n"
        "2) Segunda coordenada: 3 + 5 = 8.\n"
        "3) El punto trasladado es (1, 8).",
        [
            ("(−3, −2)", "Restó el vector en lugar de sumarlo."),
            ("(3, 8)", "Trató el −1 como si fuera 1 al sumar."),
            ("(−2, 15)", "Multiplicó las coordenadas por las del vector."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "¿Cuáles son las coordenadas del punto (7, −2) al reflejarlo respecto del eje Y?",
        "(−7, −2)",
        "Al reflejar respecto del eje Y, la coordenada horizontal cambia de signo.\n\n"
        "1) El eje Y es la línea vertical: la reflexión invierte el lado izquierdo "
        "con el derecho.\n"
        "2) La primera coordenada cambia de signo: 7 pasa a −7.\n"
        "3) La segunda se mantiene: −2.\n"
        "4) El punto reflejado es (−7, −2).",
        [
            ("(7, 2)", "Cambió de signo la coordenada equivocada: eso corresponde al eje X."),
            ("(−7, 2)", "Cambió el signo de ambas coordenadas, lo que equivale a una rotación de 180°."),
            ("(−2, 7)", "Intercambió las coordenadas en lugar de cambiar un signo."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "¿Cuáles son las coordenadas del punto (−5, 4) al reflejarlo respecto del eje X?",
        "(−5, −4)",
        "Al reflejar respecto del eje X, la coordenada vertical cambia de signo.\n\n"
        "1) El eje X es la línea horizontal: la reflexión invierte arriba con abajo.\n"
        "2) La primera coordenada se mantiene: −5.\n"
        "3) La segunda cambia de signo: 4 pasa a −4.\n"
        "4) El punto reflejado es (−5, −4).",
        [
            ("(5, 4)", "Cambió de signo la coordenada equivocada: eso corresponde al eje Y."),
            ("(5, −4)", "Cambió el signo de ambas coordenadas, equivalente a una rotación de 180°."),
            ("(4, −5)", "Intercambió las coordenadas."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "El punto (3, 0) se rota 90° en sentido antihorario en torno al origen. ¿Cuáles son sus nuevas coordenadas?",
        "(0, 3)",
        "Conviene visualizar dónde está el punto antes de rotar.\n\n"
        "1) El punto (3, 0) está sobre el eje X, a 3 unidades a la derecha del "
        "origen.\n"
        "2) Al girar 90° en sentido antihorario, ese punto sube hasta el eje Y "
        "positivo, manteniendo su distancia al origen.\n"
        "3) Queda en (0, 3).\n"
        "4) La regla general es (x, y) → (−y, x).",
        [
            ("(0, −3)", "Rotó en sentido horario en lugar de antihorario."),
            ("(−3, 0)", "Rotó 180° en vez de 90°."),
            ("(3, 0)", "Dejó el punto sin mover."),
        ],
    ),
    _q(
        "geo_transformaciones", "facil",
        "El punto (0, 5) se rota 180° en torno al origen. ¿Cuáles son sus nuevas coordenadas?",
        "(0, −5)",
        "Una rotación de 180° manda cada punto al lado opuesto del origen.\n\n"
        "1) La regla es (x, y) → (−x, −y).\n"
        "2) Primera coordenada: −0 = 0.\n"
        "3) Segunda coordenada: −5.\n"
        "4) El punto queda en (0, −5), justo al otro lado del origen y a la misma "
        "distancia.",
        [
            ("(5, 0)", "Intercambió las coordenadas, que corresponde a una rotación de 90°."),
            ("(0, 5)", "Dejó el punto sin mover."),
            ("(−5, 0)", "Rotó 90° y además cambió el signo."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "El punto (2, 5) se rota 180° en torno al origen. ¿Cuáles son sus nuevas coordenadas?",
        "(−2, −5)",
        "En una rotación de 180° ambas coordenadas cambian de signo.\n\n"
        "1) Aplica la regla (x, y) → (−x, −y).\n"
        "2) Primera coordenada: 2 pasa a −2.\n"
        "3) Segunda coordenada: 5 pasa a −5.\n"
        "4) El punto queda en (−2, −5).",
        [
            ("(−5, 2)", "Aplicó la regla de una rotación de 90° antihorario."),
            ("(2, −5)", "Cambió el signo de una sola coordenada, que es una reflexión."),
            ("(5, 2)", "Intercambió las coordenadas sin cambiar signos."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "¿Cuáles son las coordenadas del punto (4, 6) al reflejarlo respecto del origen?",
        "(−4, −6)",
        "La reflexión respecto del origen cambia el signo de ambas coordenadas.\n\n"
        "1) Aplica (x, y) → (−x, −y).\n"
        "2) Primera: 4 pasa a −4.\n"
        "3) Segunda: 6 pasa a −6.\n"
        "4) El resultado es (−4, −6). Esta transformación produce el mismo efecto que "
        "una rotación de 180° en torno al origen.",
        [
            ("(−4, 6)", "Reflejó solo respecto del eje Y."),
            ("(4, −6)", "Reflejó solo respecto del eje X."),
            ("(6, 4)", "Intercambió las coordenadas en lugar de cambiar sus signos."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "El punto (8, −3) se traslada según el vector (−5, 7). ¿Cuáles son sus nuevas coordenadas?",
        "(3, 4)",
        "Se suma el vector componente a componente, cuidando los signos.\n\n"
        "1) Primera coordenada: 8 + (−5) = 3.\n"
        "2) Segunda coordenada: −3 + 7 = 4.\n"
        "3) El punto trasladado es (3, 4).",
        [
            ("(13, −10)", "Restó el vector en lugar de sumarlo."),
            ("(3, −10)", "Sumó bien la primera coordenada pero restó en la segunda."),
            ("(13, 4)", "Ignoró el signo negativo de la primera componente del vector."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "El punto (1, 4) se rota 90° en sentido antihorario en torno al origen. ¿Cuáles son sus nuevas coordenadas?",
        "(−4, 1)",
        "La rotación de 90° antihorario intercambia las coordenadas y cambia un "
        "signo.\n\n"
        "1) La regla es (x, y) → (−y, x).\n"
        "2) La nueva primera coordenada es −4, el opuesto de la antigua segunda.\n"
        "3) La nueva segunda coordenada es 1, la antigua primera.\n"
        "4) El punto queda en (−4, 1).",
        [
            ("(4, −1)", "Rotó en sentido horario en lugar de antihorario."),
            ("(4, 1)", "Intercambió las coordenadas pero no cambió ningún signo."),
            ("(−1, −4)", "Aplicó una rotación de 180°."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "El punto (−2, 3) se rota 90° en sentido horario en torno al origen. ¿Cuáles son sus nuevas coordenadas?",
        "(3, 2)",
        "La rotación horaria usa una regla distinta a la antihoraria.\n\n"
        "1) La regla del giro horario es (x, y) → (y, −x).\n"
        "2) La nueva primera coordenada es 3, la antigua segunda.\n"
        "3) La nueva segunda coordenada es −(−2) = 2.\n"
        "4) El punto queda en (3, 2).",
        [
            ("(−3, −2)", "Rotó en sentido antihorario en lugar de horario."),
            ("(3, −2)", "Aplicó la regla horaria pero olvidó que el opuesto de −2 es +2."),
            ("(2, −3)", "Cambió el signo de ambas coordenadas sin intercambiarlas."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "El punto A(2, 3) se refleja respecto del eje X y el resultado se traslada según el vector (1, 5). ¿Dónde queda?",
        "(3, 2)",
        "Se aplican las dos transformaciones en el orden indicado.\n\n"
        "1) Reflexión respecto del eje X: cambia el signo de la segunda coordenada, "
        "así que (2, 3) pasa a (2, −3).\n"
        "2) Traslación: suma el vector (1, 5) a ese resultado.\n"
        "3) Primera coordenada: 2 + 1 = 3. Segunda: −3 + 5 = 2.\n"
        "4) El punto final es (3, 2).",
        [
            ("(3, 8)", "Trasladó el punto original sin aplicar antes la reflexión."),
            ("(−1, 2)", "Reflejó respecto del eje Y en lugar del eje X."),
            ("(1, −8)", "Restó el vector en vez de sumarlo tras reflejar."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "¿Qué vector traslada el punto (2, 1) hasta el punto (7, −3)?",
        "(5, −4)",
        "El vector de traslación es la diferencia entre el punto final y el "
        "inicial.\n\n"
        "1) Primera componente: 7 − 2 = 5.\n"
        "2) Segunda componente: −3 − 1 = −4.\n"
        "3) El vector es (5, −4).\n"
        "4) Verifica: (2 + 5, 1 − 4) = (7, −3). Correcto.",
        [
            ("(−5, 4)", "Restó en el orden inverso, del punto inicial al final."),
            ("(9, −2)", "Sumó las coordenadas en lugar de restarlas."),
            ("(5, 4)", "Perdió el signo negativo de la segunda componente."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "El punto (3, −5) se refleja respecto del eje Y y después se rota 180° en torno al origen. ¿Dónde queda?",
        "(3, 5)",
        "Se aplican las transformaciones una tras otra.\n\n"
        "1) Reflexión respecto del eje Y: cambia el signo de la primera coordenada, "
        "quedando (−3, −5).\n"
        "2) Rotación de 180°: cambia el signo de ambas coordenadas, quedando (3, 5).\n"
        "3) El punto final es (3, 5).\n"
        "4) Nota: la combinación de ambas equivale a una sola reflexión respecto del "
        "eje X.",
        [
            ("(−3, −5)", "Aplicó solo la reflexión y omitió la rotación."),
            ("(−3, 5)", "Cambió el signo de una sola coordenada en la rotación."),
            ("(5, 3)", "Intercambió las coordenadas, que no corresponde a ninguna de las dos transformaciones."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "Un triángulo con vértices (0, 0), (4, 0) y (0, 3) se traslada según el vector (2, 5). ¿Cuál es la nueva posición del vértice (4, 0)?",
        "(6, 5)",
        "En una traslación, todos los vértices se mueven con el mismo vector.\n\n"
        "1) Toma el vértice pedido: (4, 0).\n"
        "2) Suma el vector: 4 + 2 = 6 y 0 + 5 = 5.\n"
        "3) El vértice queda en (6, 5).\n"
        "4) La forma y el tamaño del triángulo no cambian: la traslación es una "
        "isometría.",
        [
            ("(2, 5)", "Entregó el vector de traslación en lugar del vértice trasladado."),
            ("(2, −5)", "Restó el vector en lugar de sumarlo."),
            ("(6, 8)", "Sumó el vector al vértice equivocado, usando el (0, 3)."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "¿Qué transformación lleva el punto (5, 2) al punto (2, 5)?",
        "Una reflexión respecto de la recta y = x",
        "Cuando las coordenadas se intercambian sin cambiar de signo, se trata de "
        "una reflexión en la diagonal.\n\n"
        "1) Observa el cambio: el 5 y el 2 se intercambiaron de posición, "
        "conservando su signo.\n"
        "2) La reflexión respecto de la recta y = x hace exactamente eso: "
        "(x, y) → (y, x).\n"
        "3) Una rotación de 180° habría cambiado los signos, y una traslación habría "
        "movido ambas coordenadas en la misma dirección.\n"
        "4) La respuesta es la reflexión respecto de la recta y = x.",
        [
            ("Una rotación de 180° en torno al origen", "Esa transformación daría (−5, −2), cambiando ambos signos."),
            ("Una reflexión respecto del eje X", "Esa transformación daría (5, −2), sin intercambiar coordenadas."),
            ("Una traslación según el vector (3, 3)", "Ese vector daría (8, 5), moviendo ambas coordenadas hacia arriba."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "¿Cuál de estas transformaciones invierte la orientación de una figura, como ocurre con una imagen en un espejo?",
        "La reflexión",
        "Las isometrías conservan las medidas, pero no todas conservan la "
        "orientación.\n\n"
        "1) La traslación mueve la figura sin girarla ni voltearla.\n"
        "2) La rotación la gira, pero el recorrido de sus vértices mantiene el mismo "
        "sentido.\n"
        "3) La reflexión, en cambio, produce una imagen especular: si los vértices "
        "iban en sentido horario, pasan a ir en sentido antihorario.\n"
        "4) Por eso se dice que la reflexión invierte la orientación.",
        [
            ("La traslación", "Mueve la figura pero conserva tanto sus medidas como su orientación."),
            ("La rotación", "Gira la figura, pero el sentido en que se recorren sus vértices no cambia."),
            ("Ninguna, todas conservan la orientación", "Las isometrías conservan las medidas, pero la reflexión sí invierte la orientación."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "El punto (4, 1) se rota 270° en sentido antihorario en torno al origen. ¿Cuáles son sus nuevas coordenadas?",
        "(1, −4)",
        "Girar 270° en un sentido equivale a girar 90° en el sentido contrario.\n\n"
        "1) Una vuelta completa son 360°, así que 270° antihorario deja el punto en "
        "la misma posición que 90° horario.\n"
        "2) La regla del giro horario de 90° es (x, y) → (y, −x).\n"
        "3) Aplicada al punto: primera coordenada 1, segunda −4.\n"
        "4) El punto queda en (1, −4).",
        [
            ("(−1, 4)", "Aplicó una rotación de 90° antihorario en lugar de 270°."),
            ("(−4, −1)", "Aplicó una rotación de 180°."),
            ("(4, 1)", "Supuso que 270° devuelve el punto a su posición original."),
        ],
    ),
    _q(
        "geo_transformaciones", "medio",
        "El punto (−3, −2) se traslada según el vector (0, 6). ¿Cuáles son sus nuevas coordenadas?",
        "(−3, 4)",
        "Un vector con primera componente cero mueve el punto solo verticalmente.\n\n"
        "1) Primera coordenada: −3 + 0 = −3, no cambia.\n"
        "2) Segunda coordenada: −2 + 6 = 4.\n"
        "3) El punto queda en (−3, 4): subió 6 unidades sin desplazarse a los lados.",
        [
            ("(3, 4)", "Cambió el signo de la primera coordenada sin motivo."),
            ("(−3, −8)", "Restó el vector en lugar de sumarlo."),
            ("(6, 4)", "Reemplazó la primera coordenada por la componente del vector."),
        ],
    ),
    _q(
        "geo_transformaciones", "dificil",
        "El punto (6, 8) se refleja respecto del origen y el resultado se traslada según el vector (2, −3). ¿Dónde queda?",
        "(−4, −11)",
        "Se aplican las dos transformaciones en orden.\n\n"
        "1) Reflexión respecto del origen: cambia el signo de ambas coordenadas, "
        "quedando (−6, −8).\n"
        "2) Traslación: suma el vector (2, −3).\n"
        "3) Primera coordenada: −6 + 2 = −4. Segunda: −8 + (−3) = −11.\n"
        "4) El punto final es (−4, −11).",
        [
            ("(8, 5)", "Trasladó el punto original sin aplicar antes la reflexión."),
            ("(−8, −5)", "Restó el vector en lugar de sumarlo tras reflejar."),
            ("(−4, −5)", "Sumó el 3 en vez de restarlo en la segunda coordenada."),
        ],
    ),
    # ---------- geo_solidos ----------
    _q(
        "geo_solidos", "facil",
        "¿Cuál es el volumen de un cubo de arista 3 cm?",
        "27 cm³",
        "El volumen de un cubo es la arista elevada al cubo.\n\n"
        "1) Aplica V = arista³.\n"
        "2) Calcula: 3 · 3 · 3 = 27.\n"
        "3) El volumen es 27 cm³. Las unidades van al cubo porque se multiplican "
        "tres longitudes.",
        [
            ("9 cm³", "Elevó al cuadrado en lugar de al cubo: eso da el área de una cara."),
            ("54 cm³", "Calculó el área total de las seis caras, no el volumen."),
            ("12 cm³", "Multiplicó la arista por 4, como si fuera un perímetro."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "Una caja mide 6 cm de largo, 4 cm de ancho y 2 cm de alto. ¿Cuál es su volumen?",
        "48 cm³",
        "El volumen de un paralelepípedo es el producto de sus tres dimensiones.\n\n"
        "1) Aplica V = largo · ancho · alto.\n"
        "2) Multiplica por pasos: 6 · 4 = 24.\n"
        "3) Luego 24 · 2 = 48.\n"
        "4) El volumen es 48 cm³.",
        [
            ("12 cm³", "Sumó las tres dimensiones en lugar de multiplicarlas."),
            ("88 cm³", "Calculó el área total de la caja en vez del volumen."),
            ("24 cm³", "Multiplicó solo dos de las tres dimensiones."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "¿Cuántas caras tiene un cubo?",
        "6",
        "Conviene contarlas por pares opuestos.\n\n"
        "1) Hay una cara arriba y una abajo: 2.\n"
        "2) Hay una al frente y una atrás: 2 más.\n"
        "3) Hay una a cada lado: 2 más.\n"
        "4) En total, 6 caras, todas cuadradas e iguales.",
        [
            ("8", "Contó los vértices en lugar de las caras."),
            ("12", "Contó las aristas en lugar de las caras."),
            ("4", "Contó solo las caras laterales, omitiendo la base y la tapa."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "¿Cuántos vértices tiene un cubo?",
        "8",
        "Los vértices son las esquinas donde se juntan tres aristas.\n\n"
        "1) La cara de abajo es un cuadrado, con 4 esquinas.\n"
        "2) La cara de arriba es otro cuadrado, con otras 4.\n"
        "3) En total, 4 + 4 = 8 vértices.",
        [
            ("6", "Contó las caras en lugar de los vértices."),
            ("12", "Contó las aristas en lugar de los vértices."),
            ("4", "Contó las esquinas de una sola cara."),
        ],
    ),
    _q(
        "geo_solidos", "facil",
        "¿Cuál es el área total de un cubo de arista 3 cm?",
        "54 cm²",
        "El área total es la suma de las áreas de todas las caras.\n\n"
        "1) Cada cara es un cuadrado de área 3² = 9 cm².\n"
        "2) El cubo tiene 6 caras iguales.\n"
        "3) Multiplica: 6 · 9 = 54.\n"
        "4) El área total es 54 cm², en unidades de superficie.",
        [
            ("27 cm²", "Calculó el volumen en lugar del área total."),
            ("9 cm²", "Calculó el área de una sola cara."),
            ("18 cm²", "Multiplicó el área de una cara por 2 en lugar de por 6."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "¿Cuál es el volumen de un cilindro de radio 5 cm y altura 4 cm? (usa π ≈ 3,14)",
        "314 cm³",
        "El volumen de un cilindro es el área de su base circular por la altura.\n\n"
        "1) Área de la base: π · r² = 3,14 · 25 = 78,5 cm².\n"
        "2) Multiplica por la altura: 78,5 · 4 = 314.\n"
        "3) El volumen es 314 cm³.",
        [
            ("62,8 cm³", "Multiplicó π por el radio sin elevarlo al cuadrado."),
            ("78,5 cm³", "Calculó el área de la base pero no la multiplicó por la altura."),
            ("104,7 cm³", "Dividió por 3, aplicando la fórmula del cono."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "¿Cuál es el volumen de un cono de radio 3 cm y altura 4 cm? (usa π ≈ 3,14)",
        "37,68 cm³",
        "El cono ocupa un tercio del cilindro que lo contiene.\n\n"
        "1) Aplica V = (π · r² · h)/3.\n"
        "2) Área de la base: 3,14 · 9 = 28,26 cm².\n"
        "3) Multiplica por la altura: 28,26 · 4 = 113,04.\n"
        "4) Divide por 3: 37,68 cm³.",
        [
            ("113,04 cm³", "Calculó el volumen del cilindro, sin dividir por 3."),
            ("12,56 cm³", "Multiplicó π por el radio sin elevarlo al cuadrado."),
            ("28,26 cm³", "Se quedó en el área de la base."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "Una esfera tiene radio 6 cm. ¿Cuál es su volumen? (usa π ≈ 3,14 y V = (4/3)πr³)",
        "904,32 cm³",
        "En la esfera el radio va elevado al cubo.\n\n"
        "1) Calcula r³: 6³ = 216.\n"
        "2) Multiplica por π: 3,14 · 216 = 678,24.\n"
        "3) Multiplica por 4/3: 678,24 · 4 = 2.712,96, y dividido por 3 da 904,32.\n"
        "4) El volumen es 904,32 cm³.",
        [
            ("452,16 cm³", "Elevó el radio al cuadrado en lugar de al cubo, y ajustó el resto."),
            ("678,24 cm³", "Olvidó multiplicar por el factor 4/3."),
            ("2.712,96 cm³", "Multiplicó por 4 pero no dividió por 3."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "Un paralelepípedo mide 6 cm, 4 cm y 3 cm. ¿Cuál es su área total?",
        "108 cm²",
        "El área total suma las seis caras, que son iguales de a pares.\n\n"
        "1) Calcula el área de cada par de caras: 6 · 4 = 24, 6 · 3 = 18 y "
        "4 · 3 = 12.\n"
        "2) Suma esas tres: 24 + 18 + 12 = 54.\n"
        "3) Multiplica por 2, porque cada cara tiene su opuesta: 54 · 2 = 108.\n"
        "4) El área total es 108 cm².",
        [
            ("72 cm²", "Calculó el volumen en lugar del área total."),
            ("54 cm²", "Sumó las tres caras distintas pero no las duplicó."),
            ("13 cm²", "Sumó las tres dimensiones en lugar de multiplicarlas de a pares."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "Un prisma tiene base triangular de 6 cm de base y 4 cm de altura, y el prisma mide 10 cm de largo. ¿Cuál es su volumen?",
        "120 cm³",
        "El volumen de un prisma es el área de su base por su longitud.\n\n"
        "1) Área de la base triangular: (6 · 4)/2 = 12 cm².\n"
        "2) Multiplica por el largo del prisma: 12 · 10 = 120.\n"
        "3) El volumen es 120 cm³.",
        [
            ("240 cm³", "No dividió por 2 al calcular el área del triángulo de la base."),
            ("12 cm³", "Se quedó en el área de la base sin multiplicar por el largo."),
            ("40 cm³", "Dividió por 3, aplicando la fórmula de una pirámide."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "Un estanque cilíndrico tiene 2 m de radio y 3 m de altura. ¿Cuál es su capacidad? (usa π ≈ 3,14)",
        "37,68 m³",
        "La capacidad corresponde al volumen del cilindro.\n\n"
        "1) Área de la base: 3,14 · 2² = 3,14 · 4 = 12,56 m².\n"
        "2) Multiplica por la altura: 12,56 · 3 = 37,68.\n"
        "3) La capacidad es 37,68 m³.",
        [
            ("18,84 m³", "Multiplicó π por el radio sin elevarlo al cuadrado."),
            ("12,56 m³", "Se quedó en el área de la base."),
            ("12,56 m³ por metro", "Confundió capacidad total con área de base."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Si la arista de un cubo se triplica, ¿por cuánto queda multiplicado su volumen?",
        "Por 27",
        "El volumen depende del cubo de la arista, y eso amplifica mucho el "
        "cambio.\n\n"
        "1) Volumen original: a³.\n"
        "2) Con la arista triplicada: (3a)³ = 27a³.\n"
        "3) El volumen queda multiplicado por 27.\n"
        "4) Ejemplo: un cubo de arista 2 tiene volumen 8; uno de arista 6 tiene "
        "volumen 216, exactamente 27 veces más.",
        [
            ("Por 3", "Supuso que el volumen crece en la misma proporción que la arista."),
            ("Por 9", "Aplicó el factor del área, que eleva al cuadrado."),
            ("Por 6", "Multiplicó el factor 3 por las dos dimensiones restantes."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Un cubo tiene un volumen de 64 cm³. ¿Cuánto mide su arista?",
        "4 cm",
        "Se invierte la fórmula del volumen.\n\n"
        "1) El volumen es arista³, así que la arista es la raíz cúbica del volumen.\n"
        "2) Busca el número que multiplicado tres veces por sí mismo da 64: "
        "4 · 4 · 4 = 64.\n"
        "3) La arista mide 4 cm.\n"
        "4) Verifica: 4³ = 64 cm³.",
        [
            ("8 cm", "Calculó la raíz cuadrada en lugar de la raíz cúbica."),
            ("21,3 cm", "Dividió el volumen por 3 en vez de calcular la raíz cúbica."),
            ("16 cm", "Dividió el volumen por 4 sin invertir correctamente la fórmula."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Un cilindro tiene un volumen de 502,4 cm³ y un radio de 4 cm. ¿Cuál es su altura? (usa π ≈ 3,14)",
        "10 cm",
        "Se despeja la altura de la fórmula del volumen.\n\n"
        "1) La fórmula es V = π · r² · h.\n"
        "2) Calcula el área de la base: 3,14 · 16 = 50,24 cm².\n"
        "3) Despeja: h = 502,4 ÷ 50,24.\n"
        "4) La altura es 10 cm. Verifica: 50,24 · 10 = 502,4 cm³.",
        [
            ("40 cm", "Dividió por π · r en lugar de por π · r²."),
            ("125,6 cm", "Dividió el volumen por 4 en vez de por el área de la base."),
            ("160 cm", "Dividió por π sin considerar el radio."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "¿Cuántas aristas tiene un prisma de base triangular?",
        "9",
        "Conviene contar por grupos.\n\n"
        "1) El triángulo de la base tiene 3 aristas.\n"
        "2) El triángulo de arriba aporta otras 3.\n"
        "3) Las aristas verticales que unen ambos triángulos son 3 más.\n"
        "4) En total: 3 + 3 + 3 = 9 aristas.",
        [
            ("6", "Contó solo las aristas de las dos bases, olvidando las verticales."),
            ("5", "Contó las caras en lugar de las aristas."),
            ("12", "Usó el número de aristas de un cubo."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "¿Cuántas caras tiene una pirámide de base cuadrada?",
        "5",
        "Se cuentan la base y las caras laterales.\n\n"
        "1) La base es un cuadrado: 1 cara.\n"
        "2) Cada lado del cuadrado sostiene un triángulo que sube hasta la punta: "
        "4 caras laterales.\n"
        "3) En total: 1 + 4 = 5 caras.",
        [
            ("4", "Contó solo las caras triangulares, olvidando la base."),
            ("6", "Usó el número de caras de un cubo."),
            ("8", "Contó las aristas en lugar de las caras."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "¿Cuántos cubos de 5 cm de arista caben exactamente dentro de una caja de 20 cm × 15 cm × 10 cm?",
        "24 cubos",
        "Se puede comparar volúmenes, porque las medidas encajan sin sobras.\n\n"
        "1) Volumen de la caja: 20 · 15 · 10 = 3.000 cm³.\n"
        "2) Volumen de cada cubo: 5³ = 125 cm³.\n"
        "3) Divide: 3.000 ÷ 125 = 24.\n"
        "4) Comprobación por dimensiones: caben 4 a lo largo, 3 a lo ancho y 2 de "
        "alto, y 4 · 3 · 2 = 24.",
        [
            ("600 cubos", "Dividió el volumen de la caja por la arista en vez de por el volumen del cubo."),
            ("9 cubos", "Sumó las divisiones de cada dimensión en lugar de multiplicarlas."),
            ("125 cubos", "Entregó el volumen de un cubo como si fuera la cantidad."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "¿Cuál es el área total de un cilindro de radio 3 cm y altura 7 cm? (usa π ≈ 3,14)",
        "188,4 cm²",
        "El área total suma las dos tapas circulares y la superficie lateral.\n\n"
        "1) Las dos tapas: 2 · π · r² = 2 · 3,14 · 9 = 56,52 cm².\n"
        "2) La superficie lateral es un rectángulo cuyo ancho es la circunferencia de "
        "la base: 2 · π · r · h = 2 · 3,14 · 3 · 7 = 131,88 cm².\n"
        "3) Suma: 56,52 + 131,88 = 188,4.\n"
        "4) El área total es 188,4 cm².",
        [
            ("131,88 cm²", "Calculó solo la superficie lateral, sin las dos tapas."),
            ("197,82 cm²", "Calculó el volumen del cilindro en lugar del área."),
            ("28,26 cm²", "Calculó el área de una sola tapa."),
        ],
    ),
    _q(
        "geo_solidos", "medio",
        "¿Cuál es el volumen de una pirámide de base cuadrada de lado 6 cm y altura 10 cm?",
        "120 cm³",
        "La pirámide ocupa un tercio del prisma que la contiene.\n\n"
        "1) Área de la base: 6² = 36 cm².\n"
        "2) Multiplica por la altura: 36 · 10 = 360.\n"
        "3) Divide por 3: 120.\n"
        "4) El volumen es 120 cm³.",
        [
            ("360 cm³", "Calculó el volumen del prisma, sin dividir por 3."),
            ("36 cm³", "Se quedó en el área de la base."),
            ("180 cm³", "Dividió por 2 en lugar de por 3."),
        ],
    ),
    _q(
        "geo_solidos", "dificil",
        "Si se duplica la altura de un cilindro y se mantiene su radio, ¿por cuánto queda multiplicado su volumen?",
        "Por 2",
        "La altura aparece elevada a la primera potencia, no al cuadrado.\n\n"
        "1) Volumen original: π · r² · h.\n"
        "2) Con la altura duplicada: π · r² · 2h = 2 · (π · r² · h).\n"
        "3) El volumen queda multiplicado por 2.\n"
        "4) Distinto sería duplicar el radio: ahí el volumen se cuadruplicaría, "
        "porque el radio va al cuadrado.",
        [
            ("Por 4", "Aplicó el factor que corresponde a duplicar el radio, no la altura."),
            ("Por 8", "Aplicó el factor de duplicar las tres dimensiones a la vez."),
            ("No cambia", "La altura sí influye directamente en el volumen del cilindro."),
        ],
    ),
]
