"""El ensayo debe repartirse como el temario, no como el banco.

Antes la cuota de cada eje salía del tamaño del banco. Con los nodos parejos en
68, eso convertía "cuántos nodos tiene el eje" en el reparto de la prueba:
Geometría quedaba en 31% por tener 5 nodos para 4 unidades oficiales, y
Probabilidad en 13% por tener 2 nodos para 3 unidades. Estos tests fijan que el
peso venga del temario y no se mueva cuando el banco crezca.
"""

from collections import Counter
from dataclasses import dataclass

from paes_api.modules.exam_focus.service import (
    MINIMO_POR_TEXTO,
    UNIDADES_POR_EJE,
    VENTANA_SIN_REPETIR,
    _select_questions,
)
from paes_api.modules.skill_tree.models import SkillAxis, Subject


@dataclass
class _Nodo:
    axis: SkillAxis


@dataclass
class _Dif:
    value: str


@dataclass
class _Pregunta:
    id: int
    skill_node: _Nodo
    difficulty: _Dif


def _banco(por_eje: dict[str, int]) -> list[_Pregunta]:
    """Cada eje con un tercio de cada dificultad, como está construido el banco."""
    preguntas, i = [], 0
    for eje, cuantas in por_eje.items():
        for k in range(cuantas):
            i += 1
            nivel = ("facil", "medio", "dificil")[k % 3]
            preguntas.append(_Pregunta(i, _Nodo(SkillAxis(eje)), _Dif(nivel)))
    return preguntas


def _reparto(elegidas: list[_Pregunta]) -> Counter:
    return Counter(q.skill_node.axis.value for q in elegidas)


def test_las_unidades_por_eje_calzan_con_el_temario() -> None:
    """Los temarios 2027: M1 lista 16 unidades y M2 quince PROPIAS más."""
    assert UNIDADES_POR_EJE[Subject.M1] == {
        "numeros": 3,
        "algebra": 6,
        "geometria": 4,
        "probabilidad": 3,
    }
    assert sum(UNIDADES_POR_EJE[Subject.M1].values()) == 16
    assert UNIDADES_POR_EJE[Subject.M2] == {
        "numeros": 3,
        "algebra": 3,
        "geometria": 5,
        "probabilidad": 4,
    }
    assert sum(UNIDADES_POR_EJE[Subject.M2].values()) == 15


def test_un_ensayo_de_65_sigue_el_reparto_del_temario() -> None:
    pool = _banco({"numeros": 300, "algebra": 300, "geometria": 300, "probabilidad": 300})
    reparto = _reparto(_select_questions(pool, [], 65))
    # 3, 6, 4 y 3 unidades sobre 16 dan 12,19 / 24,38 / 16,25 / 12,19. Al
    # truncar suman 64, y la plaza suelta va a Álgebra, que es la de mayor peso
    # y además la de mayor resto.
    assert reparto["algebra"] == 25
    assert reparto["geometria"] == 16
    assert reparto["numeros"] == 12
    assert reparto["probabilidad"] == 12
    assert sum(reparto.values()) == 65


def test_el_reparto_no_depende_del_tamano_del_banco() -> None:
    """Este es el bug que se corrigió: con el reparto viejo, duplicar el banco
    de un eje le duplicaba la presencia en la prueba."""
    equilibrado = _banco({"numeros": 200, "algebra": 200, "geometria": 200, "probabilidad": 200})
    desbalanceado = _banco({"numeros": 200, "algebra": 200, "geometria": 800, "probabilidad": 100})
    assert _reparto(_select_questions(equilibrado, [], 65)) == _reparto(
        _select_questions(desbalanceado, [], 65)
    )


def test_un_ensayo_corto_toca_todos_los_ejes() -> None:
    pool = _banco({"numeros": 100, "algebra": 100, "geometria": 100, "probabilidad": 100})
    reparto = _reparto(_select_questions(pool, [], 20))
    assert set(reparto) == {"numeros", "algebra", "geometria", "probabilidad"}
    assert sum(reparto.values()) == 20


def test_respeta_los_ejes_elegidos_por_el_estudiante() -> None:
    pool = _banco({"numeros": 100, "algebra": 100, "geometria": 100, "probabilidad": 100})
    elegidas = _select_questions(pool, ["algebra", "geometria"], 30)
    reparto = _reparto(elegidas)
    assert set(reparto) == {"algebra", "geometria"}
    # Entre esos dos, 6 y 4 unidades reparten 30 en 18 y 12.
    assert reparto["algebra"] == 18
    assert reparto["geometria"] == 12


def test_no_pide_mas_preguntas_de_las_que_tiene_un_eje() -> None:
    """Si un eje tiene poco banco, su cuota se recorta y el resto se reparte."""
    pool = _banco({"numeros": 5, "algebra": 100, "geometria": 100, "probabilidad": 100})
    elegidas = _select_questions(pool, [], 65)
    reparto = _reparto(elegidas)
    assert reparto["numeros"] <= 5
    assert sum(reparto.values()) == 65


def test_un_ensayo_corto_no_sale_cargado_a_una_dificultad() -> None:
    """Elegir al azar dentro del eje podía dar 12 fáciles en 20 preguntas."""
    pool = _banco(
        {"numeros": 300, "algebra": 300, "geometria": 300, "probabilidad": 300}
    )
    for _ in range(20):
        elegidas = _select_questions(pool, [], 24)
        reparto = Counter(q.difficulty.value for q in elegidas)
        assert set(reparto) == {"facil", "medio", "dificil"}
        # Las tres franjas quedan parejas salvo el sobrante del redondeo, que
        # se acumula a propósito en "medio": es la franja más poblada de una
        # prueba real. Con 24 preguntas eso da 10 / 7 / 7.
        assert max(reparto.values()) - min(reparto.values()) <= 3
        assert reparto["medio"] >= reparto["facil"]
        assert reparto["medio"] >= reparto["dificil"]


def test_el_equilibrio_de_dificultad_aguanta_un_banco_desparejo() -> None:
    """Si una dificultad escasea, se completa con el resto sin fallar."""
    pool = [
        _Pregunta(i, _Nodo(SkillAxis("algebra")), _Dif("facil" if i > 3 else "dificil"))
        for i in range(1, 101)
    ]
    elegidas = _select_questions(pool, ["algebra"], 30)
    assert len(elegidas) == 30


@dataclass
class _NodoPrueba:
    axis: SkillAxis
    subject: Subject


@dataclass
class _PreguntaPrueba:
    id: int
    skill_node: _NodoPrueba
    difficulty: _Dif


def _banco_m1_y_m2(por_m1: int, por_m2: int) -> list[_PreguntaPrueba]:
    """Un banco desbalanceado a propósito, como el real: M1 tiene mucho más."""
    preguntas, i = [], 0
    for subject, cuantas in ((Subject.M1, por_m1), (Subject.M2, por_m2)):
        for eje in ("numeros", "algebra", "geometria", "probabilidad"):
            for k in range(cuantas):
                i += 1
                nivel = ("facil", "medio", "dificil")[k % 3]
                preguntas.append(
                    _PreguntaPrueba(i, _NodoPrueba(SkillAxis(eje), subject), _Dif(nivel))
                )
    return preguntas


def test_un_ensayo_de_m2_reparte_mitad_y_mitad_con_m1() -> None:
    """M2 evalúa 31 unidades: las 16 de M1 más 15 propias. Casi mitad y mitad.

    Antes el reparto salía del tamaño del banco y un ensayo de M2 traía 56
    preguntas de M1 y 9 propias, porque M1 tiene cinco veces más banco.
    """
    pool = _banco_m1_y_m2(por_m1=300, por_m2=300)
    elegidas = _select_questions(pool, [], 65, Subject.M2)
    reparto = Counter(q.skill_node.subject for q in elegidas)
    assert sum(reparto.values()) == 65
    # 16 unidades de M1 y 15 de M2 sobre 31: el reparto queda parejo.
    assert abs(reparto[Subject.M1] - reparto[Subject.M2]) <= 3


def test_el_reparto_entre_pruebas_no_depende_del_tamano_del_banco() -> None:
    """Este es el bug: M1 tenía cinco veces más banco y se llevaba el ensayo."""
    parejo = _banco_m1_y_m2(por_m1=300, por_m2=300)
    real = _banco_m1_y_m2(por_m1=300, por_m2=60)
    a = Counter(q.skill_node.subject for q in _select_questions(parejo, [], 65, Subject.M2))
    b = Counter(q.skill_node.subject for q in _select_questions(real, [], 65, Subject.M2))
    assert a == b


def test_un_ensayo_de_m1_no_trae_nada_de_m2() -> None:
    """M1 no evalúa el temario de M2, así que su ensayo es exclusivo."""
    pool = _banco_m1_y_m2(por_m1=300, por_m2=300)
    solo_m1 = [q for q in pool if q.skill_node.subject is Subject.M1]
    elegidas = _select_questions(solo_m1, [], 65, Subject.M1)
    assert {q.skill_node.subject for q in elegidas} == {Subject.M1}


def test_si_a_m2_le_falta_banco_propio_lo_completa_con_m1() -> None:
    """Sin banco propio suficiente, el ensayo se completa en vez de fallar."""
    pool = _banco_m1_y_m2(por_m1=300, por_m2=1)
    elegidas = _select_questions(pool, [], 65, Subject.M2)
    assert len(elegidas) == 65


# --- Competencia Lectora: el ensayo se arma por TEXTO ---------------------
# La prueba real son 7 textos de mil y tantas palabras con 8 a 11 preguntas
# cada uno. Antes el armador elegía 65 preguntas sueltas y las barajaba, así
# que podía montar un texto largo para una sola pregunta.


@dataclass
class _Texto:
    kind: str


@dataclass
class _Dificultad:
    """El armador lee `.value`, igual que el enum real."""

    value: str


@dataclass
class _PreguntaTexto:
    id: int
    passage_id: int | None
    difficulty: _Dificultad
    passage: _Texto | None = None


def _banco_de_lectura(
    textos: int, por_texto: int, literarios: int = 1
) -> list[_PreguntaTexto]:
    """Los primeros `literarios` textos son literarios; el resto, no.

    Las dificultades se reparten en ciclo dentro de cada texto: el armador las
    usa para que el ensayo no herede la mezcla del banco.
    """
    niveles = ("facil", "medio", "dificil")
    return [
        _PreguntaTexto(
            id=t * 100 + k,
            passage_id=t,
            difficulty=_Dificultad(niveles[k % 3]),
            passage=_Texto("literario" if t <= literarios else "no_literario"),
        )
        for t in range(1, textos + 1)
        for k in range(por_texto)
    ]


def _bloques(elegidas: list[_PreguntaTexto]) -> list[tuple[int | None, int]]:
    """(texto, cuántas seguidas) recorriendo el ensayo en orden."""
    out: list[tuple[int | None, int]] = []
    for q in elegidas:
        if out and out[-1][0] == q.passage_id:
            out[-1] = (q.passage_id, out[-1][1] + 1)
        else:
            out.append((q.passage_id, 1))
    return out


def test_las_preguntas_de_un_texto_llegan_juntas() -> None:
    """Si se barajan, el alumno tiene que releer el texto en cada pregunta."""
    elegidas = _select_questions(_banco_de_lectura(12, 9), [], 63, Subject.LECTORA)
    bloques = _bloques(elegidas)
    # Cada texto aparece en UN solo bloque, no repartido por el ensayo.
    assert len(bloques) == len({t for t, _ in bloques})


def test_ningun_texto_entra_por_menos_preguntas_que_el_minimo() -> None:
    """Mil palabras para dos preguntas es tiempo regalado."""
    elegidas = _select_questions(_banco_de_lectura(12, 9), [], 65, Subject.LECTORA)
    assert all(n >= MINIMO_POR_TEXTO for _, n in _bloques(elegidas))


def test_un_ensayo_de_lectura_se_parece_a_la_prueba_oficial() -> None:
    """7 u 8 textos y 65 preguntas es la forma que declara el temario."""
    elegidas = _select_questions(_banco_de_lectura(20, 9), [], 65, Subject.LECTORA)
    bloques = _bloques(elegidas)
    assert 7 <= len(bloques) <= 8
    assert len(elegidas) == 65


def test_un_ensayo_de_lectura_entrega_las_preguntas_que_promete() -> None:
    """El botón "Completo" dice "la prueba oficial entera": tiene que darla.

    Este control existe porque el armador entregaba de menos y nadie lo notaba.
    Cuando tomaba textos ENTEROS y cortaba al quedar menos preguntas que el
    mínimo, un banco con textos de nueve y once preguntas hacía que pedir 65
    devolviera entre 60 y 65 —y solo un cuarto de las veces las 65— en 6
    lecturas en vez de 7 u 8. El test recorre los tres formatos que ofrece la
    aplicación y varios bancos, porque el defecto dependía de cómo se mezclaban
    los tamaños de los textos.
    """
    for por_texto in (9, 10, 11):
        banco = _banco_de_lectura(20, por_texto)
        for pedidas in (20, 34, 65):
            for _ in range(20):
                elegidas = _select_questions(banco, [], pedidas, Subject.LECTORA)
                assert len(elegidas) == pedidas, (
                    f"pidió {pedidas} con textos de {por_texto} "
                    f"y entregó {len(elegidas)}"
                )


def test_un_ensayo_de_lectura_no_apila_las_preguntas_en_pocos_textos() -> None:
    """Un texto con doce preguntas no existe en la prueba oficial.

    El rango medido en las pruebas del DEMRE va de 7 a 11 preguntas por
    lectura. Repartir de a nueve mantiene los bloques dentro de esa forma
    aunque el banco tenga textos más largos.
    """
    elegidas = _select_questions(_banco_de_lectura(20, 11), [], 65, Subject.LECTORA)
    assert all(n <= 11 for _, n in _bloques(elegidas))


def test_el_ensayo_corto_se_reparte_en_dos_lecturas() -> None:
    """Veinte preguntas van en DOS textos, no en tres.

    La prueba oficial reparte 65 preguntas en 7 u 8 lecturas: nueve por texto
    en promedio. Un ensayo de veinte que se abriera en tres lecturas dejaría
    bloques de siete, y sobre todo obligaría a leer tres textos largos para
    responder veinte preguntas: pasa a ser más lectura que práctica.

    Con textos de nueve preguntas dos no alcanzaban para veinte y entraba un
    tercero. Por eso el banco se llevó a once por texto: el faltante se cubre
    ahora desde los textos ya elegidos, que es justamente lo que el armador
    intenta antes de sumar otra lectura.
    """
    for por_texto in (11, 12, 13):
        banco = _banco_de_lectura(20, por_texto)
        for _ in range(20):
            elegidas = _select_questions(banco, [], 20, Subject.LECTORA)
            assert len(_bloques(elegidas)) == 2, (
                f"con textos de {por_texto} preguntas, un ensayo de 20 se abrió "
                f"en {len(_bloques(elegidas))} lecturas"
            )


def test_el_faltante_sale_de_los_textos_ya_elegidos() -> None:
    """Completar un ensayo no debe costar una lectura más.

    Si a un ensayo le faltan dos preguntas, el armador tiene dos salidas:
    pedirle esas dos a un texto que ya está adentro, o montar una lectura
    entera para sacarle dos preguntas. La segunda es la mala: el alumno tendría
    que leer novecientas palabras para responder dos veces.

    Con holgura en cada texto —once preguntas y cuotas de nueve o diez— el
    faltante se cubre sin abrir otra lectura. El test lo comprueba en el
    formato que más lo tensiona.
    """
    banco = _banco_de_lectura(20, 11)
    for pedidas in (20, 34, 65):
        for _ in range(20):
            elegidas = _select_questions(banco, [], pedidas, Subject.LECTORA)
            bloques = _bloques(elegidas)
            assert len(elegidas) == pedidas
            # Ningún bloque queda por debajo del mínimo que justifica montar
            # una lectura: eso delataría un texto agregado solo para rellenar.
            assert all(n >= MINIMO_POR_TEXTO for _, n in bloques), (
                f"pidió {pedidas} y quedó un bloque corto: {bloques}"
            )


def test_dos_ensayos_no_traen_siempre_los_mismos_textos() -> None:
    """Con banco de sobra, repetir el mismo ensayo no sirve para practicar."""
    banco = _banco_de_lectura(20, 9)
    a = {q.passage_id for q in _select_questions(banco, [], 65, Subject.LECTORA)}
    b = {q.passage_id for q in _select_questions(banco, [], 65, Subject.LECTORA)}
    c = {q.passage_id for q in _select_questions(banco, [], 65, Subject.LECTORA)}
    assert not (a == b == c)


def _textos_de(elegidas: list[_PreguntaTexto]) -> set[int | None]:
    return {q.passage_id for q in elegidas}


def test_el_ensayo_de_lectura_no_hereda_la_dificultad_del_banco() -> None:
    """El puntaje estimado depende de que el ensayo se parezca a la prueba real.

    El armador de lectura tomaba de cada texto las primeras preguntas del
    montón, así que la mezcla del ensayo era la mezcla del banco. Si el banco
    se carga de preguntas difíciles —y esta tanda lo carga, porque las
    preguntas de reserva se escriben difíciles a propósito—, el alumno rinde un
    ensayo más duro que la PAES y recibe un puntaje estimado más bajo del que
    sacaría, calculado con las tablas de transformación del DEMRE, que suponen
    la dificultad de la prueba real.

    Acá cada texto está torcido a propósito —tres fáciles, tres medias y siete
    difíciles de trece— y la cuota por lectura es de nueve. Tomando las
    primeras del montón, el ensayo saldría con más de la mitad difíciles;
    repartiendo, sale parejo, porque hay con qué.
    """
    banco = [
        _PreguntaTexto(
            id=t * 100 + k,
            passage_id=t,
            difficulty=_Dificultad(
                "facil" if k < 3 else "medio" if k < 6 else "dificil"
            ),
            passage=_Texto("no_literario"),
        )
        for t in range(1, 21)
        for k in range(13)
    ]

    conteo = Counter()
    for _ in range(30):
        for q in _select_questions(banco, [], 65, Subject.LECTORA):
            conteo[q.difficulty.value] += 1

    total = sum(conteo.values())
    proporciones = {n: conteo[n] / total for n in ("facil", "medio", "dificil")}
    assert proporciones["dificil"] <= 0.40, proporciones
    assert all(p >= 0.25 for p in proporciones.values()), proporciones


def test_un_texto_recien_leido_no_vuelve_en_los_dos_ensayos_siguientes() -> None:
    """Releer el mismo texto no entrena: el alumno responde de memoria.

    Un texto de Competencia Lectora son novecientas palabras. Si vuelve a salir
    en el ensayo siguiente, el estudiante ya sabe lo que dice y contesta sin
    leer, que es exactamente lo contrario de lo que la prueba mide.
    """
    # Cinco literarios de veinte, la proporción del banco real (13 de 67). Con
    # uno solo, la regla de "todo ensayo trae un literario" lo haría entrar
    # siempre y el enfriamiento no tendría nada que hacer.
    banco = _banco_de_lectura(20, 11, literarios=5)

    primero = _select_questions(banco, [], 20, Subject.LECTORA)
    recientes = {t: 1 for t in _textos_de(primero)}

    segundo = _select_questions(banco, [], 20, Subject.LECTORA, recientes)
    assert not _textos_de(primero) & _textos_de(segundo)

    # Y en el que le sigue tampoco: el primero pasa a antigüedad 2.
    recientes = {t: 1 for t in _textos_de(segundo)}
    recientes |= {t: 2 for t in _textos_de(primero)}
    tercero = _select_questions(banco, [], 20, Subject.LECTORA, recientes)
    assert not _textos_de(tercero) & (_textos_de(primero) | _textos_de(segundo))


def test_un_texto_viejo_vuelve_a_competir_de_igual_a_igual() -> None:
    """La penalización se apaga sola: no es una lista negra.

    Pasada la ventana, el texto vuelve a valer lo mismo que uno que nunca
    salió. Sin eso, un estudiante constante terminaría con la mitad del banco
    vetada para siempre.
    """
    # Sin literarios, para mirar el orden del enfriamiento y nada más: la regla
    # de "todo ensayo trae un literario" tiene precedencia y adelantaría un
    # texto aunque estuviera recién leído.
    banco = _banco_de_lectura(3, 11, literarios=0)
    # Dos textos recién leídos y uno visto justo en el borde de la ventana.
    recientes = {1: 1, 2: 1, 3: VENTANA_SIN_REPETIR}

    for _ in range(20):
        elegidas = _select_questions(banco, [], 20, Subject.LECTORA, recientes)
        # El que salió de la ventana entra primero, antes que los dos recientes.
        assert _bloques(elegidas)[0][0] == 3


def test_sin_banco_suficiente_el_ensayo_igual_se_arma_completo() -> None:
    """Es una postergación, no una exclusión, y esa diferencia importa.

    Un estudiante que rinde muchos ensayos seguidos puede dejar todo el banco
    dentro de la ventana. Si la regla fuera excluir, el armador se quedaría sin
    textos y entregaría un ensayo corto; posponer significa que igual lo arma,
    empezando por lo más antiguo.
    """
    banco = _banco_de_lectura(4, 11)
    recientes = {1: 1, 2: 1, 3: 2, 4: 3}

    elegidas = _select_questions(banco, [], 34, Subject.LECTORA, recientes)
    assert len(elegidas) == 34
    # Se prefirió lo más antiguo: el texto del ensayo recién pasado queda fuera
    # mientras haya con qué reemplazarlo.
    assert 4 in _textos_de(elegidas)


def test_todo_ensayo_de_lectura_trae_al_menos_un_texto_literario() -> None:
    """El temario dedica trece conocimientos exclusivos a los literarios."""
    banco = _banco_de_lectura(20, 9, literarios=2)
    for _ in range(20):
        elegidas = _select_questions(banco, [], 65, Subject.LECTORA)
        tipos = {q.passage.kind for q in elegidas if q.passage}
        assert "literario" in tipos

