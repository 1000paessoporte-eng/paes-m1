# Auditoria de coincidencia literal con las pruebas oficiales

Fecha: **2026-09-03**  ·  Umbral de bandera roja: **12 palabras consecutivas**

## Corpus oficial comparado

- `2024-23-11-29-paes-regular-oficial-historia-p2024.pdf`
- `2025-24-06-19-paes-invierno-oficial-historia-p2025.pdf`
- `2026-25-12-02-paes-regular-ciencias-biologia-p2026.pdf`
- `2026-25-12-02-paes-regular-ciencias-fisica-p2026.pdf`
- `2026-25-12-02-paes-regular-ciencias-quimica-p2026.pdf`
- `2026-25-12-03-paes-regular-historia-p2026.pdf`
- `2024-23-11-29-paes-regular-oficial-matematica1-p2024.pdf`
- `2025-24-12-03-paes-regular-competencia-lectora-p2025.pdf`
- `2025-24-12-04-paes-regular-matematica1-p2025.pdf`
- `2026-25-06-17-paes-invierno-oficial-competencia-lectora-p2026.pdf`
- `2026-25-06-18-paes-invierno-oficial-matematica1-p2026.pdf`

Se excluyen los 6 temarios: un temario es un listado de contenidos y coincidir con el es el objetivo del banco, no un defecto.

## Metodo

Los textos se normalizan (minusculas, sin tildes, sin puntuacion) y se compara la secuencia de palabras consecutivas mas larga que el banco comparte con el corpus. Se revisa el enunciado, la explicacion, las cuatro alternativas con sus justificaciones, y los textos base.

## Resultado

- Piezas del banco revisadas: **5.531**
- Coincidencias de 12 palabras o mas: **0**
- Coincidencias de 8 a 11 palabras: **33**

### Reparto de la coincidencia mas larga

| Palabras consecutivas | Piezas |
|---|---|
| 10 | 2 |
| 9 | 2 |
| 8 | 29 |
| 7 | 95 |
| 6 | 198 |
| sin coincidencia de 6 o mas | 5205 |

Las coincidencias de 6 y 7 palabras son lenguaje de prueba de seleccion multiple ("cual de las siguientes afirmaciones es correcta", "de acuerdo con el texto leido"). No son expresion protegible: aparecen en cualquier prueba del mundo.

### Banderas rojas

**Ninguna.** No hay una sola secuencia de 12 palabras consecutivas en comun entre el banco y las pruebas oficiales comparadas.

### Coincidencias intermedias (8 a 11 palabras)

- matematica / pregunta (10) — `cual es la probabilidad de que la suma de los`
- matematica / pregunta (10) — `cual es la probabilidad de que la suma de los`
- matematica / pregunta (9) — `cual de las siguientes expresiones representa el precio total`
- ciencias / pregunta (9) — `un objeto se coloca frente a un espejo concavo`
- matematica / pregunta (8) — `cual de las siguientes expresiones representa el precio`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `cual de las siguientes expresiones representa el precio`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `la propiedad de la potencia de una potencia`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `cual es la probabilidad de que sea mujer`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `cual de las siguientes expresiones permite calcular la`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `cual es la probabilidad de que la suma`
- matematica / pregunta (8) — `al azar cual es la probabilidad de que`
- matematica / pregunta (8) — `cual de las siguientes expresiones representa el precio`
- lectora / pregunta (8) — `cual es la idea principal de la seccion`
- lectora / pregunta (8) — `cual es la idea principal de la seccion`
- historia / pregunta (8) — `despues del fin de la segunda guerra mundial`
- historia / texto (8) — `despues del fin de la segunda guerra mundial`

## Alcance y limites

- El corpus son los folletos que estan en disco. **No incluye todas las pruebas liberadas por el DEMRE**: un informe limpio dice que no hay copia respecto de ESTOS folletos.
- No hay folleto oficial de M2 en el corpus, asi que los nodos exclusivos de M2 quedan comparados solo contra las pruebas de M1.
- La comparacion es literal. No detecta una pregunta que replique la ESTRUCTURA de una oficial con otros numeros y otras palabras; eso se revisa leyendo.
- Las figuras no se comparan: son archivos SVG propios del repo, dibujados para cada pregunta.