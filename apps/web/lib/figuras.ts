/**
 * Qué muestra cada figura, en palabras.
 *
 * Es el texto alternativo de la imagen: lo que lee un lector de pantalla y lo
 * que aparece si el archivo no carga. Vive acá y no en la base de datos porque
 * las figuras son archivos del repositorio (`public/preguntas/`), así que su
 * descripción se revisa en el mismo pull request que el dibujo. Si algún día
 * las imágenes se suben desde un panel, la descripción tendrá que viajar con
 * ellas y este archivo deja de alcanzar.
 *
 * La descripción dice qué hay en la figura, NO cuál es la respuesta: es el
 * reemplazo de mirarla, no un atajo para resolver la pregunta.
 */
export const DESCRIPCION_FIGURA: Record<string, string> = {
  // ---------- Física ----------
  "/preguntas/fis-posicion-tiempo-tramos.svg":
    "Gráfico de posición contra tiempo con cuatro tramos rectos rotulados. En P la " +
    "posición sube de 0 a 20 metros en los primeros 2 segundos. En Q se mantiene en " +
    "20 metros hasta el segundo 4. En R sube de 20 a 80 metros entre los segundos 4 " +
    "y 6. En S baja de 80 a 60 metros entre los segundos 6 y 8.",
  "/preguntas/fis-velocidad-tiempo-area.svg":
    "Gráfico de velocidad contra tiempo con forma de trapecio: sube de 0 a 10 metros " +
    "por segundo en los primeros 2 segundos, se mantiene en 10 hasta el segundo 6 y " +
    "baja hasta 0 en el segundo 8. El área bajo la línea está sombreada.",
  "/preguntas/fis-fotos-intervalos.svg":
    "Cinco posiciones sucesivas de un carrito sobre una recta, fotografiadas cada un " +
    "segundo y numeradas del 0 al 4. La separación entre una posición y la siguiente " +
    "es cada vez mayor.",
  "/preguntas/fis-dos-moviles.svg":
    "Gráfico de posición contra tiempo con dos rectas. La del móvil A parte del " +
    "origen y llega a 100 metros a los 10 segundos. La del móvil B parte de 40 " +
    "metros y llega a 90 metros a los 10 segundos. Las dos se cruzan a los 8 " +
    "segundos, en los 80 metros.",
  "/preguntas/fis-cuerpo-libre-roce.svg":
    "Un bloque de 6 kilos apoyado en el suelo con cuatro fuerzas dibujadas: normal " +
    "de 60 newton hacia arriba, peso de 60 newton hacia abajo, una fuerza de 45 " +
    "newton hacia la derecha y otra de 15 newton hacia la izquierda.",
  "/preguntas/fis-plano-inclinado.svg":
    "Bloque apoyado sobre un plano inclinado de 30 grados con tres fuerzas " +
    "numeradas: la 1 apunta verticalmente hacia abajo, la 2 sale perpendicular a la " +
    "superficie del plano y la 3 va paralela al plano, hacia arriba.",
  "/preguntas/fis-polea-atwood.svg":
    "Dos bloques colgando de los extremos de una misma cuerda que pasa por una " +
    "polea fija al techo: uno de 2 kilos y otro de 3 kilos. La cuerda y la polea no " +
    "pesan y no hay roce.",
  "/preguntas/fis-fuerzas-perpendiculares.svg":
    "Dos fuerzas aplicadas en el mismo punto y perpendiculares entre sí: una de 80 " +
    "newton horizontal hacia la derecha y otra de 60 newton vertical hacia arriba.",
  "/preguntas/fis-rampa-energia.svg":
    "Una pista con dos cerros y cuatro puntos marcados: W en la cima más alta, X en " +
    "el valle entre los dos cerros, Y en la cima del segundo cerro, que es más baja " +
    "que W, y Z al nivel del suelo, al final de la bajada.",
  "/preguntas/fis-barras-energia.svg":
    "Barras de energía de un mismo cuerpo en tres instantes. En el primero la " +
    "cinética es 0 y la potencial 100 joule. En el segundo la cinética es 60 y la " +
    "potencial 40. En el tercero la potencial es 0 y la cinética aparece como una " +
    "caja punteada con un signo de interrogación.",
  "/preguntas/fis-pendulo-posiciones.svg":
    "Un péndulo dibujado en tres posiciones: A en el extremo izquierdo de su " +
    "oscilación, B en el punto más bajo y C en el extremo derecho. A y C están a la " +
    "misma altura.",
  "/preguntas/fis-resorte-bloque.svg":
    "Dos escenas. En la primera un resorte comprimido contra un bloque apoyado en " +
    "el suelo. En la segunda el mismo resorte estirado y el bloque alejándose con " +
    "una flecha que indica su velocidad.",
  "/preguntas/fis-onda-magnitudes.svg":
    "Una onda con cuatro medidas marcadas. P es vertical, desde una cresta hasta la " +
    "línea central. Q es horizontal, entre dos crestas seguidas. R es horizontal, " +
    "entre una cresta y el valle siguiente. S es vertical, entre una cresta y un " +
    "valle.",
  "/preguntas/fis-dos-ondas.svg":
    "Dos ondas dibujadas en la misma escala de tiempo y con la misma altura. La M " +
    "completa dos ondulaciones y la N completa cinco en el mismo tramo.",
  "/preguntas/fis-cambio-de-medio.svg":
    "Una onda que cruza de un medio a otro. En el medio 1 las ondulaciones son " +
    "anchas y en el medio 2 quedan mucho más juntas, conservando la misma altura.",
  "/preguntas/fis-interferencia.svg":
    "Dos casos de superposición. En el caso I las dos ondas coinciden cresta con " +
    "cresta y el resultado es una onda del doble de altura. En el caso II una cresta " +
    "coincide con un valle y el resultado es una línea recta.",
  "/preguntas/fis-circuito-serie.svg":
    "Circuito con una pila de 12 volt, una resistencia de 20 ohm y otra de 40 ohm " +
    "conectadas una a continuación de la otra en el mismo camino, y un amperímetro " +
    "en el retorno.",
  "/preguntas/fis-circuito-paralelo.svg":
    "Circuito con una pila de 9 volt y dos lámparas idénticas, L1 y L2, cada una en " +
    "su propia rama conectada a los mismos dos puntos.",
  "/preguntas/fis-circuito-mixto.svg":
    "Circuito con una pila de 12 volt y una resistencia R1 de 10 ohm en el camino " +
    "principal, seguida de dos resistencias de 20 ohm cada una, R2 y R3, montadas en " +
    "ramas paralelas.",
  "/preguntas/fis-grafico-ohm.svg":
    "Gráfico de voltaje contra corriente con dos rectas que parten del origen. La X " +
    "llega a 20 volt cuando la corriente es 4 ampere; la Y llega a 8 volt con esa " +
    "misma corriente.",
  // ---------- Química ----------
  "/preguntas/qui-atomo-bohr.svg":
    "Modelo de un átomo con 11 protones y 12 neutrones en el núcleo y sus electrones " +
    "repartidos en tres niveles: 2 en el más interno, 8 en el siguiente y 1 en el " +
    "más externo.",
  "/preguntas/qui-tabla-periodica.svg":
    "Esquema de la tabla periódica con cuatro casillas marcadas. Q y S están en la " +
    "primera columna de la izquierda, una debajo de la otra. R está en la penúltima " +
    "columna y T en la última columna del extremo derecho.",
  "/preguntas/qui-isotopos.svg":
    "Tres núcleos atómicos dibujados con sus partículas. El X tiene 6 protones y 6 " +
    "neutrones, el Y tiene 6 protones y 7 neutrones, y el Z tiene 7 protones y 7 " +
    "neutrones.",
  "/preguntas/qui-elemento-compuesto-mezcla.svg":
    "Tres recipientes con partículas. El I tiene solo átomos azules sueltos. El II " +
    "tiene solo moléculas iguales, cada una formada por un átomo azul unido a uno " +
    "amarillo. El III tiene átomos azules y amarillos sueltos, mezclados.",
  "/preguntas/qui-ecuacion-particulas.svg":
    "Una molécula de nitrógeno, formada por dos átomos N, más dos moléculas de " +
    "hidrógeno, de dos átomos H cada una, dando como productos dos moléculas de " +
    "amoníaco, cada una con un átomo N unido a tres H.",
  "/preguntas/qui-reactivo-limitante.svg":
    "En un matraz hay 4 moléculas de nitrógeno y 9 de hidrógeno. Al lado se indica " +
    "la proporción en que reaccionan: una molécula de nitrógeno con tres de " +
    "hidrógeno.",
  "/preguntas/qui-masa-producto.svg":
    "Gráfico de la masa de amoníaco obtenida según el hidrógeno agregado, " +
    "manteniendo fija la cantidad de nitrógeno. Sube en línea recta hasta los 6 " +
    "gramos de hidrógeno, donde alcanza 60 gramos de amoníaco, y de ahí en adelante " +
    "se mantiene constante.",
  "/preguntas/qui-conservacion-masa.svg":
    "Dos frascos idénticos sobre balanzas, con la misma reacción que libera un gas. " +
    "El frasco I está tapado y su balanza marca 120 gramos. El frasco II está " +
    "destapado, con gas escapando, y su balanza aparece con un signo de " +
    "interrogación.",
  "/preguntas/qui-tres-disoluciones.svg":
    "Tres vasos. El I tiene 12 gramos de sal en 100 mililitros de agua, el II tiene " +
    "6 gramos en 100 mililitros y el III tiene 6 gramos en 50 mililitros.",
  "/preguntas/qui-curva-solubilidad.svg":
    "Curva creciente de solubilidad contra temperatura. Parte en unos 14 gramos de " +
    "sal por cada 100 gramos de agua a 0 grados y a 50 grados pasa exactamente por " +
    "los 60 gramos, punto que aparece marcado.",
  "/preguntas/qui-dilucion.svg":
    "Un vaso con 12 gramos de sal disueltos en 100 mililitros y, después de " +
    "agregarle 100 mililitros de agua, el mismo vaso con los mismos 12 gramos en 200 " +
    "mililitros.",
  "/preguntas/qui-destilacion.svg":
    "Montaje de destilación: un matraz con la mezcla calentado por un mechero, un " +
    "termómetro en el cuello, un tubo inclinado refrigerado con agua fría y un vaso " +
    "al final donde se acumula el líquido recogido.",
  "/preguntas/qui-escala-ph.svg":
    "Escala de pH del 0 al 14 dividida en zona ácida hasta el 6, neutra en el 7 y " +
    "básica del 8 en adelante. Están ubicados el jugo de limón en 2, el café en 5, " +
    "el agua pura en 7, el bicarbonato en 9 y un limpiador en 12.",
  "/preguntas/qui-titulacion.svg":
    "Curva de pH contra volumen de base agregada a un ácido. Se mantiene cerca de pH " +
    "1 hasta los 20 mililitros, sube bruscamente pasando por pH 7 a los 25 " +
    "mililitros, punto marcado como P, y luego se aplana cerca de pH 13.",
  "/preguntas/qui-iones-disoluciones.svg":
    "Tres vasos con iones dibujados. El I tiene 8 iones hidrógeno y 1 hidróxido. El " +
    "II tiene 4 de cada uno. El III tiene 1 ion hidrógeno y 8 hidróxido.",
  "/preguntas/qui-fenolftaleina.svg":
    "Tres tubos de ensayo después de agregarles fenolftaleína: el I quedó incoloro, " +
    "el II rosado y el III incoloro. El pie indica que la fenolftaleína es incolora " +
    "hasta pH 8 y rosada desde ahí hacia arriba.",
  // ---------- Biología ----------
  "/preguntas/bio-celula-organelos.svg":
    "Esquema de una célula animal con cinco estructuras numeradas: 1 la membrana " +
    "plasmática, 2 el núcleo con su nucléolo, 3 una estructura ovalada con pliegues " +
    "internos, 4 una pila de sacos aplanados y 5 una red de membranas con puntos " +
    "adheridos.",
  "/preguntas/bio-osmosis-membrana.svg":
    "Un recipiente dividido en dos por una membrana permeable solo al agua. El lado " +
    "A tiene 2 gramos de soluto por cada 100 mililitros y el lado B, 8 gramos por " +
    "cada 100 mililitros. El nivel del líquido es el mismo en ambos lados.",
  "/preguntas/bio-pedigri-autosomico.svg":
    "Árbol genealógico de tres generaciones. En la primera, un hombre y una mujer " +
    "sin la enfermedad. De ellos nacen una mujer afectada y otros dos hijos sanos. " +
    "Uno de esos hijos sanos forma pareja con una mujer sana y tienen un hombre " +
    "afectado y dos mujeres sanas.",
  "/preguntas/bio-punnett-incognita.svg":
    "Cuadro de Punnett de dos por dos. Los gametos de ambos progenitores están " +
    "tapados con signos de interrogación. Las cuatro casillas de la descendencia " +
    "son, en orden: Aa, aa, Aa, aa.",
  "/preguntas/bio-red-trofica.svg":
    "Red trófica. El pasto alimenta al roedor y al insecto; el arbusto alimenta al " +
    "insecto. El roedor alimenta a la culebra y también al águila. El insecto " +
    "alimenta a un ave insectívora. La culebra y el ave insectívora alimentan al " +
    "águila.",
  "/preguntas/bio-celula-vegetal-animal.svg":
    "Dos células comparadas. La célula A es rectangular, con un borde externo " +
    "grueso marcado con el número 1, un compartimento grande y claro marcado con " +
    "el 2, un núcleo y varios cuerpos ovalados verdes, uno de ellos marcado con " +
    "el 3. La célula B es redondeada, sin borde grueso, con núcleo y dos cuerpos " +
    "ovalados con pliegues internos, uno marcado con el 4.",
  "/preguntas/bio-tonicidad-globulos.svg":
    "Tres glóbulos rojos iguales una hora después de ponerlos en tres soluciones " +
    "distintas. El I quedó hinchado y a punto de romperse, el II conserva su forma " +
    "normal y el III quedó arrugado, con el borde lleno de puntas.",
  "/preguntas/bio-transporte-saturacion.svg":
    "Gráfico de la velocidad de entrada de dos sustancias a la célula según su " +
    "concentración fuera de ella. La sustancia X sube como una recta que no se " +
    "detiene. La sustancia Y sube rápido al principio y luego se aplana en un " +
    "valor máximo, aunque la concentración siga aumentando.",
  "/preguntas/bio-membrana-mosaico.svg":
    "Esquema de la membrana plasmática: dos filas de cabezas redondas con dos " +
    "colas cada una, enfrentadas cola con cola, marcadas con el número 1. El 2 " +
    "señala una proteína que atraviesa las dos filas dejando un poro abierto de " +
    "lado a lado. El 3 señala una cadena ramificada de azúcares que sobresale " +
    "hacia el exterior. El 4 señala una pieza rígida encajada entre las colas.",
  "/preguntas/bio-mitosis-fases.svg":
    "Cuatro células con los cromosomas en distintas etapas de la mitosis, " +
    "presentadas en desorden. En la I los cromosomas están alineados en una fila " +
    "sobre el plano del centro de la célula. En la II hay dos grupos de " +
    "cromosomas en los extremos y la célula se está estrangulando por el medio. " +
    "En la III los cromosomas están condensados y repartidos por toda la célula, " +
    "sin envoltura nuclear. En la IV las cromátidas de cada cromosoma ya están " +
    "separadas y viajan hacia los dos extremos.",
  "/preguntas/bio-pedigri-ligado-x.svg":
    "Árbol genealógico de tres generaciones. En la primera, un hombre afectado y " +
    "una mujer sana. De ellos nacen un hombre sano y una mujer sana. Esa mujer " +
    "forma pareja con un hombre sano y tienen tres hijos: dos hombres afectados y " +
    "una mujer sana. Ninguna mujer del árbol presenta la enfermedad.",
  "/preguntas/bio-transcripcion-arnm.svg":
    "Una hebra molde de ADN con la secuencia T A C G G A A T C, leída de 3 prima " +
    "a 5 prima, y debajo una flecha rotulada transcripción que apunta a la hebra " +
    "de ARN mensajero, cuyas nueve bases están sin completar.",
  "/preguntas/bio-cariotipo.svg":
    "Cariotipo humano ordenado por tamaño. Los pares 1 al 20 y el 22 tienen dos " +
    "cromosomas cada uno. El par 21 tiene tres. Los cromosomas sexuales son uno X " +
    "y uno Y.",
  "/preguntas/bio-piramide-energia.svg":
    "Pirámide de cuatro niveles tróficos. Los productores tienen 10.000 " +
    "kilocalorías, los consumidores primarios 1.000, los consumidores secundarios " +
    "100 y el nivel de los consumidores terciarios aparece con un signo de " +
    "interrogación.",
  "/preguntas/bio-ciclo-carbono.svg":
    "Ciclo del carbono con cuatro depósitos y cuatro flechas rotuladas. La flecha " +
    "W va del dióxido de carbono de la atmósfera hacia las plantas. La X va de " +
    "las plantas a los animales. La Y va de los animales al dióxido de carbono de " +
    "la atmósfera. La Z va de los combustibles fósiles al dióxido de carbono de " +
    "la atmósfera.",
  "/preguntas/bio-depredador-presa.svg":
    "Gráfico de dos poblaciones del mismo ecosistema durante veinticuatro meses. " +
    "La especie M es siempre más numerosa y sube y baja en ciclos. La especie N " +
    "es mucho menos numerosa y repite el mismo ciclo, pero sus máximos ocurren " +
    "unos tres meses después que los de M.",
  "/preguntas/bio-curvas-j-y-s.svg":
    "Dos curvas de crecimiento de una población. La curva 1 arranca lenta y se " +
    "empina cada vez más, sin detenerse, con forma de jota. La curva 2 sube, " +
    "alcanza su punto más empinado a mitad de camino y luego se aplana en un " +
    "valor máximo, con forma de ese.",
  "/preguntas/bio-crecimiento-poblacional.svg":
    "Gráfico del número de conejos a lo largo de doce años. La curva tiene forma de " +
    "S: parte casi plana cerca de cero, se empina hasta pasar por 600 individuos a " +
    "los 6 años y luego se aplana acercándose a una línea horizontal marcada como " +
    "capacidad de carga K igual a 1.200. Sobre la curva hay cuatro puntos: P al año " +
    "y medio, Q a los 6 años, R a los 9 y S a los 11 y medio.",
};
