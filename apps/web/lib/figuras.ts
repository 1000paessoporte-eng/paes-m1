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

  // ---------- Matemática: geometría ----------
  "/preguntas/mat-terreno-en-l.svg":
    "Terreno con forma de L. El lado de abajo mide 12 metros y el de la izquierda, " +
    "8 metros. Desde la esquina de arriba a la izquierda, el borde superior avanza " +
    "7 metros hacia la derecha y ahí baja formando un escalón, hasta encontrarse " +
    "con el lado derecho, que mide 5 metros.",
  "/preguntas/mat-trapecio-acotado.svg":
    "Trapecio con la base mayor de 10 centímetros abajo y la base menor de 6 " +
    "centímetros arriba. Una línea punteada perpendicular a las bases marca la " +
    "altura, de 4 centímetros.",
  "/preguntas/mat-sector-circular.svg":
    "Círculo de 6 centímetros de radio. Un sector de 90 grados, marcado con su " +
    "ángulo recto, está sombreado; el resto del círculo está en blanco.",
  "/preguntas/mat-paralelogramo-altura.svg":
    "Paralelogramo con la base de 10 centímetros y el lado inclinado de 7 " +
    "centímetros. Una línea punteada perpendicular a la base marca la altura, de 6 " +
    "centímetros.",
  "/preguntas/mat-escalera-muro.svg":
    "Escalera de 13 metros apoyada contra un muro vertical. Su pie está a 5 metros " +
    "del muro y el suelo forma ángulo recto con él. La altura a la que llega el " +
    "extremo superior está marcada con un signo de interrogación.",
  "/preguntas/mat-rombo-diagonales.svg":
    "Rombo con sus dos diagonales dibujadas en línea punteada y cortándose en " +
    "ángulo recto. La diagonal horizontal mide 16 centímetros y la vertical, 12.",
  "/preguntas/mat-trapecio-isosceles.svg":
    "Trapecio isósceles con la base mayor de 14 centímetros, la base menor de 8 y " +
    "los dos lados inclinados de 5 centímetros cada uno. Una línea punteada marca " +
    "la altura, sin su medida.",
  "/preguntas/mat-cancha-diagonal.svg":
    "Cancha rectangular de 24 metros de largo por 10 de ancho, con una diagonal " +
    "trazada de esquina a esquina. La medida de esa diagonal está marcada con un " +
    "signo de interrogación.",
  "/preguntas/mat-traslacion-cuadricula.svg":
    "Plano cartesiano con dos triángulos rectángulos iguales. El triángulo T tiene " +
    "sus vértices en (1, 1), (4, 1) y (1, 5). El triángulo T', del mismo tamaño y " +
    "la misma orientación, tiene sus vértices en (6, 3), (9, 3) y (6, 7).",
  "/preguntas/mat-reflexion-eje.svg":
    "Plano cartesiano con dos cuadriláteros en espejo, uno a cada lado del eje y. " +
    "El de la derecha, P, tiene sus vértices en (2, 1), (5, 1), (5, 4) y (3, 5); " +
    "este último está marcado con un punto y la letra R. El de la izquierda, P', " +
    "tiene el vértice correspondiente marcado con la letra R prima.",
  "/preguntas/mat-rotacion-origen.svg":
    "Plano cartesiano con dos triángulos rectángulos iguales y un punto rojo en el " +
    "origen, señalado como centro del giro, con una flecha curva que va desde el " +
    "eje x hacia el eje y. El triángulo F tiene sus vértices en (2, 1), (6, 1) y " +
    "(2, 3), con el cateto largo horizontal. El triángulo F' tiene sus vértices en " +
    "(−1, 2), (−1, 6) y (−3, 2), con el cateto largo vertical.",
  "/preguntas/mat-ejes-simetria.svg":
    "Cuatro figuras planas numeradas. La I es un rectángulo más ancho que alto. La " +
    "II es un triángulo equilátero. La III es un trapecio isósceles. La IV es un " +
    "cuadrado.",
  "/preguntas/mat-tales-paralela.svg":
    "Triángulo ABC con el vértice A arriba. Un segmento DE, paralelo al lado BC, " +
    "corta los otros dos lados: D en el lado AB y E en el lado AC. En el lado AB, " +
    "el trozo AD mide 4 y el trozo DB mide 6. En el lado AC, el trozo AE mide 5 y " +
    "el trozo EC está rotulado como x.",
  "/preguntas/mat-sombra-poste.svg":
    "Un poste de 2 metros de alto con una sombra de 1,5 metros y, más a la " +
    "derecha, una torre mucho más alta con una sombra de 9 metros. Los rayos de " +
    "sol están dibujados con la misma inclinación en los dos casos. La altura de " +
    "la torre está marcada con un signo de interrogación.",
  "/preguntas/mat-triangulos-semejantes.svg":
    "Dos triángulos de la misma forma y distinto tamaño, con dos pares de ángulos " +
    "iguales marcados con el mismo color. En el triángulo chico T, el lado " +
    "izquierdo mide 6 centímetros y la base 8. En el triángulo grande T', el lado " +
    "izquierdo mide 9 centímetros y la base está rotulada como x.",
  "/preguntas/mat-plano-escala.svg":
    "Plano de una sala rectangular que en el papel mide 4 centímetros de largo por " +
    "3 de ancho. Bajo el dibujo dice: escala 1 : 200.",
  "/preguntas/mat-desarrollo-prisma.svg":
    "Desarrollo plano de una caja: cuatro rectángulos en fila, de 3 centímetros de " +
    "alto y de anchos 6, 4, 6 y 4 centímetros, más dos rectángulos de 6 por 4 " +
    "centímetros, uno pegado arriba del primero y otro pegado abajo.",
  "/preguntas/mat-cilindro-cotas.svg":
    "Cilindro dibujado en perspectiva. En su tapa circular está marcado el radio, " +
    "de 5 centímetros, y a un costado su altura, de 10 centímetros.",
  "/preguntas/mat-paralelepipedo-area.svg":
    "Paralelepípedo recto dibujado en perspectiva, con las aristas ocultas " +
    "punteadas. Sus tres medidas son 8, 5 y 3 centímetros.",
  "/preguntas/mat-cubo-cubitos.svg":
    "Cubo de 6 centímetros de arista dibujado en perspectiva. Sus tres caras " +
    "visibles están divididas en cuadrados iguales, tres por lado.",

  // ---------- Matemática: álgebra, datos y azar ----------
  "/preguntas/mat-proporcionalidad-directa.svg":
    "Gráfico de precio contra cantidad. Una recta parte del origen y sube hasta " +
    "los 15 mil pesos en 10 kilos. Sobre ella hay un punto marcado en 2 kilos y 3 " +
    "mil pesos.",
  "/preguntas/mat-proporcionalidad-inversa.svg":
    "Gráfico de días de trabajo contra cantidad de trabajadores. La curva baja " +
    "rápido y después se va aplanando sin llegar a cero. Hay dos puntos marcados: " +
    "3 trabajadores con 8 días y 6 trabajadores con 4 días.",
  "/preguntas/mat-dos-llaves.svg":
    "Gráfico del agua acumulada contra el tiempo, con dos rectas que parten del " +
    "origen. La llave A llega a 50 litros a los 10 minutos y la llave B, a 30 " +
    "litros en ese mismo tiempo.",
  "/preguntas/mat-cuatro-graficos.svg":
    "Cuatro gráficos numerados, todos con los ejes sin escala. El I es una recta " +
    "que sube y parte del origen. El II es una recta que sube y parte por encima " +
    "del origen. El III es una curva que baja rápido y luego se aplana. El IV es " +
    "una curva que sube cada vez más empinada.",
  "/preguntas/mat-parabola-vertice.svg":
    "Parábola con las ramas hacia arriba dibujada en un plano cartesiano. Corta el " +
    "eje x en −1 y en 3, y su punto más bajo, marcado como vértice, está en (1, −4).",
  "/preguntas/mat-recta-pendiente.svg":
    "Recta que baja de izquierda a derecha en un plano cartesiano, con dos puntos " +
    "marcados: (0 ; 3), donde corta el eje y, y (4 ; 1).",
  "/preguntas/mat-parabola-hacia-abajo.svg":
    "Parábola con las ramas hacia abajo dibujada en un plano cartesiano. Corta el " +
    "eje x en dos puntos, −2 y 2, y su punto más alto está sobre el eje y.",
  "/preguntas/mat-trayectoria-balon.svg":
    "Gráfico de la altura de un balón contra el tiempo. La curva parte del origen, " +
    "sube hasta un máximo de 20 metros a los 2 segundos —marcado con líneas " +
    "punteadas— y baja hasta tocar el eje del tiempo a los 4 segundos.",
  "/preguntas/mat-barras-notas.svg":
    "Gráfico de barras con la cantidad de estudiantes por nota: 4 estudiantes " +
    "sacaron un 4, seis sacaron un 5, ocho sacaron un 6 y dos sacaron un 7.",
  "/preguntas/mat-circular-transporte.svg":
    "Gráfico circular del medio de transporte de los estudiantes, con cuatro " +
    "sectores: micro 40%, metro 25%, auto 20% y bicicleta 15%.",
  "/preguntas/mat-histograma-edades.svg":
    "Histograma de edades en cuatro intervalos de diez años: de 10 a 20 años hay 5 " +
    "personas, de 20 a 30 hay 12, de 30 a 40 hay 9 y de 40 a 50 hay 4.",
  "/preguntas/mat-dos-sucursales.svg":
    "Gráfico de líneas con las ventas mensuales de dos sucursales entre enero y " +
    "junio. La sucursal A vende 20, 35, 30, 45, 50 y 40 unidades. La sucursal B " +
    "vende 15, 25, 35, 30, 20 y 45. Las dos líneas se cruzan en marzo.",
  "/preguntas/mat-cajon-puntajes.svg":
    "Diagrama de cajón sobre un eje de puntajes de 0 a 100. El bigote izquierdo " +
    "parte en 20, el cajón va de 35 a 60 con la línea de la mediana en 45, y el " +
    "bigote derecho termina en 80.",
  "/preguntas/mat-dos-cajones.svg":
    "Dos diagramas de cajón sobre un mismo eje de puntajes de 0 a 100. El del 4°A " +
    "va de 30 a 90, con el cajón entre 45 y 65 y la mediana en 55. El del 4°B va " +
    "de 20 a 80, con el cajón entre 40 y 70 y la mediana en 60.",
  "/preguntas/mat-ojiva-puntajes.svg":
    "Ojiva de frecuencia acumulada contra puntaje. Parte en 0 acumulados a los 10 " +
    "puntos y sube pasando por 8 a los 20 puntos, 22 a los 30, 34 a los 40 y 40 a " +
    "los 50.",
  "/preguntas/mat-tabla-frecuencias.svg":
    "Tabla de tres columnas: puntaje, frecuencia y frecuencia acumulada. El " +
    "intervalo de 0 a 20 tiene 6 estudiantes y acumula 6; el de 20 a 40 tiene 14 y " +
    "acumula 20; el de 40 a 60 tiene 12 y acumula 32; el de 60 a 80 tiene 8 y " +
    "acumula 40.",
  "/preguntas/mat-arbol-probabilidad.svg":
    "Árbol de probabilidades de dos extracciones. Desde el inicio salen dos ramas: " +
    "roja con 3/5 y azul con 2/5. De la rama roja salen otras dos, roja con 2/4 y " +
    "azul con 2/4; de la rama azul salen roja con 3/4 y azul con 1/4.",
  "/preguntas/mat-ruleta-sectores.svg":
    "Ruleta con una flecha arriba, dividida en ocho sectores iguales rotulados con " +
    "letras: tres A, dos B, una C y dos D.",
  "/preguntas/mat-venn-deportes.svg":
    "Diagrama de Venn dentro de un rectángulo rotulado como un curso de 30 " +
    "estudiantes. En la parte del círculo del fútbol que no se cruza hay 11; en la " +
    "zona común, 7; en la parte del básquetbol que no se cruza, 7; y fuera de los " +
    "dos círculos, 5.",
  "/preguntas/mat-dos-urnas.svg":
    "Dos urnas con bolitas. La urna 1 tiene 3 bolitas blancas y 5 negras. La urna " +
    "2 tiene 2 bolitas blancas y 4 negras.",

  // ---------- Matemática: segundo lote ----------
  "/preguntas/mat-recta-racionales.svg":
    "Recta numérica graduada de −2 a 2 con cuatro puntos marcados: P entre −2 y " +
    "−1, Q entre −1 y 0 y más cerca de −1, R entre 0 y 1 justo en la mitad, y S " +
    "entre 1 y 2.",
  "/preguntas/mat-fracciones-barras.svg":
    "Cuatro barras iguales divididas en partes iguales, con las primeras partes " +
    "sombreadas. La I está dividida en cuatro partes con tres sombreadas; la II " +
    "en ocho con cinco sombreadas; la III en cinco con tres sombreadas; la IV en " +
    "diez con siete sombreadas.",
  "/preguntas/mat-grilla-porcentaje.svg":
    "Cuadrícula de diez por diez celdas iguales. Están sombreadas las tres " +
    "primeras filas completas y cinco celdas de la cuarta fila.",
  "/preguntas/mat-barras-encuesta.svg":
    "Gráfico de barras con el deporte favorito de un grupo de personas: fútbol " +
    "60, tenis 30, natación 40 y otros 70.",
  "/preguntas/mat-cuadrado-area.svg":
    "Cuadrado con la leyenda «Área = 144 cm²» escrita en su interior. La medida " +
    "de su lado está marcada con un signo de interrogación.",
  "/preguntas/mat-cubo-volumen.svg":
    "Cubo dibujado en perspectiva con la leyenda «64 cm³» escrita sobre su cara " +
    "frontal. La medida de su arista está marcada con un signo de interrogación.",
  "/preguntas/mat-rectangulo-expresion.svg":
    "Rectángulo cuyo lado horizontal mide x más 3 y cuyo lado vertical mide x " +
    "más 2.",
  "/preguntas/mat-cuadrado-partido.svg":
    "Cuadrado cuyo lado está dividido en un tramo a y otro b, tanto a lo ancho " +
    "como a lo alto, lo que lo parte en cuatro regiones rotuladas: un cuadrado a " +
    "al cuadrado, dos rectángulos a por b y un cuadrado b al cuadrado.",
  "/preguntas/mat-balanza-ecuacion.svg":
    "Balanza de dos platillos en equilibrio. En el platillo izquierdo hay dos " +
    "cajas iguales rotuladas con la letra x y una pesa de 2 kilos. En el derecho " +
    "hay tres pesas: de 5, 5 y 2 kilos.",
  "/preguntas/mat-recta-inecuacion.svg":
    "Recta numérica graduada de −2 a 6. Desde el 3 hacia la derecha la recta " +
    "está marcada con línea gruesa terminada en flecha, y sobre el 3 hay un " +
    "círculo sin rellenar.",
  "/preguntas/mat-sistema-rectas.svg":
    "Plano cartesiano con dos rectas: L1 baja de izquierda a derecha y L2 sube. " +
    "Se cortan en el punto P, que está en (3, 2). L1 corta el eje vertical en 5 " +
    "y el horizontal en 5; L2 corta el eje horizontal en 1.",
  "/preguntas/mat-dos-planes.svg":
    "Gráfico del costo contra los minutos consumidos, con dos rectas. El plan A " +
    "parte de 4 mil pesos con cero minutos y llega a 14 mil en 500 minutos. El " +
    "plan B parte del origen y llega a 20 mil en 500 minutos. Las dos rectas se " +
    "cruzan en los 200 minutos, con un costo de 8 mil pesos.",
  "/preguntas/mat-tabla-funcion.svg":
    "Tabla de dos filas. En la fila x los valores son 0, 1, 2 y 3. En la fila y, " +
    "los correspondientes son 5, 8, 11 y 14.",
  "/preguntas/mat-tres-parabolas.svg":
    "Tres parábolas con las ramas hacia arriba y el vértice en el origen, " +
    "dibujadas en el mismo plano. La I, de línea llena, es la más angosta; la " +
    "II, punteada, es intermedia; la III, de puntos, es la más abierta.",
  "/preguntas/mat-triangulo-altura.svg":
    "Triángulo con una base horizontal de 14 centímetros y una altura punteada " +
    "de 8 centímetros, trazada desde el vértice superior perpendicular a la base.",
  "/preguntas/mat-circulo-diametro.svg":
    "Círculo con un trazo que pasa por su centro y une dos puntos opuestos de la " +
    "circunferencia, acotado en 10 centímetros.",
  "/preguntas/mat-cuadrado-circulo.svg":
    "Cuadrado de 12 centímetros de lado con un círculo dibujado dentro, que toca " +
    "los cuatro lados. La región que queda entre el cuadrado y el círculo está " +
    "sombreada.",
  "/preguntas/mat-triangulo-cateto.svg":
    "Triángulo rectángulo con el ángulo recto abajo a la izquierda. El lado " +
    "horizontal mide 24 centímetros y el lado inclinado, 26. El lado vertical " +
    "está marcado con un signo de interrogación.",
  "/preguntas/mat-desarrollo-cilindro.svg":
    "Desarrollo de un cilindro: dos círculos iguales de 3 centímetros de radio, " +
    "rotulados como tapas, y un rectángulo rotulado como manto, de 7 centímetros " +
    "de alto.",
  "/preguntas/mat-piscina-volumen.svg":
    "Piscina con forma de paralelepípedo dibujada en perspectiva, con las " +
    "aristas ocultas punteadas. Mide 10 metros de largo, 6 de ancho y 2 de " +
    "profundidad.",
  "/preguntas/mat-vector-plano.svg":
    "Plano cartesiano con el punto A en (2, 1) y el punto B en (7, 4), unidos " +
    "por una flecha que va de A hacia B.",
  "/preguntas/mat-rotacion-punto.svg":
    "Plano cartesiano con el punto M en (3, 2) y el punto M prima en (−3, −2), " +
    "unidos por una línea punteada que pasa por el origen, donde hay un punto " +
    "marcado.",
  "/preguntas/mat-mapa-escala.svg":
    "Mapa con dos localidades marcadas, Villa Alegre y San Pedro, unidas por una " +
    "línea punteada rotulada «5 cm en el mapa». Abajo hay una barra de escala de " +
    "2 centímetros que equivale a 20 kilómetros.",
  "/preguntas/mat-tabla-relativa.svg":
    "Tabla con el deporte preferido de un grupo: fútbol, frecuencia 12 y " +
    "frecuencia relativa 0,30; básquetbol, 8 y 0,20; vóleibol, 14 y 0,35; otros, " +
    "6 y 0,15.",
  "/preguntas/mat-barras-dobles.svg":
    "Gráfico de barras dobles con los libros leídos por curso en 2025 y en 2026. " +
    "En 1° medio, 20 y 15; en 2° medio, 25 y 10; en 3° medio, 15 y 20; en 4° " +
    "medio, 10 y 25.",
  "/preguntas/mat-cajon-interpretar.svg":
    "Diagrama de cajón sobre un eje de tiempo en minutos. El bigote izquierdo " +
    "parte en 4, el cajón va de 10 a 24 con la línea de la mediana en 16, y el " +
    "bigote derecho termina en 34.",
  "/preguntas/mat-tabla-dados.svg":
    "Tabla de doble entrada de seis filas por seis columnas. Las filas son los " +
    "puntos del primer dado y las columnas los del segundo; cada celda contiene " +
    "la suma de ambos, desde 2 en la esquina superior izquierda hasta 12 en la " +
    "inferior derecha.",
  "/preguntas/mat-fichas-numeradas.svg":
    "Ocho fichas circulares iguales, numeradas del 1 al 8.",

  // ---------- Matemática M2 ----------
  "/preguntas/mat-recta-real-puntos.svg":
    "Recta numérica graduada de 0 a 6 con cuatro puntos marcados: P entre 1 y 2, " +
    "Q entre 2 y 3, R apenas pasado el 3 y S entre 4 y 5.",
  "/preguntas/mat-cuadrado-diagonal-recta.svg":
    "Cuadrado de lado 1 apoyado sobre una recta numérica, con su vértice " +
    "izquierdo en el 0 y el derecho en el 1. Está dibujada su diagonal, y un " +
    "arco de circunferencia con centro en el 0 la lleva hasta cortar la recta en " +
    "un punto T, ubicado entre el 1 y el 2.",
  "/preguntas/mat-interes-simple-compuesto.svg":
    "Gráfico del capital contra los años, con dos líneas que parten del mismo " +
    "punto, en un millón de pesos. La I, de línea llena, se empina cada vez más " +
    "y termina sobre los cuatro millones. La II, punteada, es una recta y " +
    "termina en dos millones y medio.",
  "/preguntas/mat-tabla-credito.svg":
    "Tabla con las condiciones de un crédito: monto 1.200.000 pesos, 18 cuotas, " +
    "cada cuota de 84.000 pesos, y el total pagado marcado con un signo de " +
    "interrogación.",
  "/preguntas/mat-grafico-logaritmo.svg":
    "Curva que pasa por el punto (1, 0) y por el punto (10, 1), sube cada vez " +
    "más despacio y cae bruscamente cuando x se acerca a cero. No existe para " +
    "valores negativos de x.",
  "/preguntas/mat-tabla-magnitudes.svg":
    "Tabla que relaciona la magnitud de un sismo con la energía que libera: " +
    "magnitud 3 con 10 elevado a 3, magnitud 4 con 10 elevado a 4, magnitud 5 " +
    "con 10 elevado a 5 y magnitud 6 con 10 elevado a 6.",
  "/preguntas/mat-rectas-paralelas.svg":
    "Dos rectas paralelas dibujadas en un mismo plano cartesiano: tienen la " +
    "misma inclinación y no se cortan en ningún punto.",
  "/preguntas/mat-rectas-coincidentes.svg":
    "Un solo trazo recto en el plano cartesiano, formado por una línea llena que " +
    "lleva encima otra punteada: las dos rectas del sistema quedaron " +
    "superpuestas.",
  "/preguntas/mat-grafico-exponencial.svg":
    "Curva que crece cada vez más rápido, pasa por (0, 1) y por (3, 8), y hacia " +
    "la izquierda se acerca al eje horizontal sin llegar a tocarlo.",
  "/preguntas/mat-tres-curvas.svg":
    "Tres gráficos numerados y sin escala. El I parte del origen, sube despacio " +
    "y después se empina. El II sube rápido al principio y luego se va " +
    "aplanando. El III corta el eje vertical por encima del origen y se dispara " +
    "hacia arriba.",
  "/preguntas/mat-grafico-seno.svg":
    "Onda que parte en 0, sube hasta 1 en π/2, vuelve a 0 en π, baja hasta −1 en " +
    "3π/2 y regresa a 0 en 2π: un ciclo completo.",
  "/preguntas/mat-seno-amplitud.svg":
    "Onda que completa dos ciclos completos entre 0 y 2π, llegando hasta 3 hacia " +
    "arriba y hasta −3 hacia abajo.",
  "/preguntas/mat-homotecia-razon.svg":
    "Un triángulo T y otro triángulo T' del doble de tamaño. Los vértices de " +
    "cada uno están alineados con un punto O mediante líneas punteadas, y las " +
    "dos figuras quedan del mismo lado de O.",
  "/preguntas/mat-homotecia-negativa.svg":
    "Un triángulo T y otro T' del mismo tamaño, ubicados a lados opuestos de un " +
    "punto O y con la orientación invertida. Cada vértice está unido con el que " +
    "le corresponde por una línea punteada que pasa por O.",
  "/preguntas/mat-triangulo-trigonometria.svg":
    "Triángulo rectángulo con el ángulo recto abajo a la izquierda y un ángulo " +
    "de 30 grados en el vértice de la derecha. La hipotenusa mide 10 centímetros " +
    "y el cateto vertical está marcado con un signo de interrogación.",
  "/preguntas/mat-rampa-angulo.svg":
    "Rampa apoyada en el suelo, dibujada como un triángulo rectángulo de 24 " +
    "metros de base y 7 metros de altura. El ángulo que forma la rampa con el " +
    "suelo está rotulado como θ.",
  "/preguntas/mat-angulo-inscrito.svg":
    "Circunferencia de centro O con los puntos A y B sobre la parte de abajo del " +
    "borde. Los trazos OA y OB forman en el centro un ángulo de 80 grados. Desde " +
    "el punto P, en lo más alto del borde, salen dos trazos hacia A y hacia B, " +
    "que forman el ángulo x.",
  "/preguntas/mat-cuerdas-circunferencia.svg":
    "Circunferencia con dos cuerdas, AB y CD, que se cortan en un punto " +
    "interior. Los dos trozos de AB miden 6 y 4; en CD, uno mide 8 y el otro " +
    "está rotulado como x.",
  "/preguntas/mat-esfera-radio.svg":
    "Esfera dibujada como un círculo con su ecuador punteado, y un trazo desde " +
    "el centro hasta el borde acotado en 5 centímetros.",
  "/preguntas/mat-cupula-hemisferio.svg":
    "Cúpula con forma de media esfera apoyada sobre su base circular, con el " +
    "radio de esa base acotado en 6 metros.",
  "/preguntas/mat-rectas-perpendiculares.svg":
    "Dos rectas que se cortan formando un ángulo recto, marcado con un " +
    "cuadradito: L1 sube empinada y L2 baja suavemente.",
  "/preguntas/mat-recta-dos-puntos.svg":
    "Plano cartesiano con una recta que pasa por el punto A, en (2, 2), y por el " +
    "punto B, en (6, 5).",
  "/preguntas/mat-dos-dispersiones.svg":
    "Dos gráficos de barras con las notas de dos cursos de 14 estudiantes cada " +
    "uno. En el curso A ocho estudiantes sacaron la nota del medio y solo uno " +
    "cada nota extrema. En el curso B las cinco notas se reparten parejo, entre " +
    "dos y tres estudiantes por nota.",
  "/preguntas/mat-tabla-desviacion.svg":
    "Tabla con el promedio y la desviación estándar de tres cursos: A tiene " +
    "promedio 6,0 y desviación 0,3; B tiene promedio 6,0 y desviación 1,4; C " +
    "tiene promedio 5,2 y desviación 0,4.",
  "/preguntas/mat-tabla-contingencia.svg":
    "Tabla de doble entrada de 100 personas. De los 50 hombres, 18 usan lentes y " +
    "32 no. De las 50 mujeres, 22 usan lentes y 28 no. En total, 40 usan lentes " +
    "y 60 no.",
  "/preguntas/mat-arbol-condicional.svg":
    "Árbol de probabilidades de dos etapas. En la primera, estudió con " +
    "probabilidad 0,7 y no estudió con 0,3. De quienes estudiaron, 0,9 aprueba y " +
    "0,1 reprueba; de quienes no estudiaron, 0,4 aprueba y 0,6 reprueba.",
  "/preguntas/mat-arbol-menu.svg":
    "Árbol que combina dos entradas, E1 y E2, con tres platos de fondo, P1, P2 y " +
    "P3: de cada entrada salen tres ramas.",
  "/preguntas/mat-casilleros-cifras.svg":
    "Cuatro casilleros vacíos en fila, rotulados como primera, segunda, tercera " +
    "y cuarta posición de un número de cuatro cifras distintas. Abajo dice que " +
    "las cifras disponibles son 1, 2, 3, 5 y 7.",
  "/preguntas/mat-barras-binomial.svg":
    "Gráfico de barras con la probabilidad de obtener 0, 1, 2, 3 o 4 caras al " +
    "lanzar cuatro veces una moneda. Las barras miden 0,0625; 0,25; 0,375; 0,25 " +
    "y 0,0625.",
  "/preguntas/mat-campana-normal.svg":
    "Curva con forma de campana simétrica respecto de su centro, marcado con una " +
    "línea punteada en la media. La zona que va desde una desviación estándar " +
    "bajo la media hasta una sobre ella está sombreada.",

  // ---------- Historia y Ciencias Sociales ----------
  "/preguntas/his-tabla-fuentes.svg":
    "Tabla que compara dos fuentes. La fuente 1 es una carta personal escrita " +
    "por un comerciante del puerto en 1887, con el propósito de contar a su " +
    "familia cómo vive. La fuente 2 es un artículo de investigación escrito por " +
    "una historiadora en 2019, con el propósito de explicar el auge del puerto.",
  "/preguntas/his-grafico-exportaciones.svg":
    "Gráfico de las exportaciones de un producto entre 1880 y 1930, en miles de " +
    "toneladas: 5 en 1880, 18 en 1890, 32 en 1900, 50 en 1910, 45 en 1920 y 8 en " +
    "1930. La figura advierte que los datos son ficticios.",
  "/preguntas/his-recorte-prensa.svg":
    "Recorte de un diario llamado El Diario del Puerto, fechado en Valparaíso el " +
    "14 de marzo de 1907. El titular dice «Los obreros del salitre piden ser " +
    "escuchados» y la bajada cuenta que una delegación llegó a exponer sus " +
    "demandas ante las autoridades, y que la empresa sostiene que las " +
    "condiciones ofrecidas son las de costumbre. La figura advierte que el " +
    "recorte es ficticio.",
  "/preguntas/his-dos-recortes.svg":
    "Dos gráficos de la misma variable en distinto tramo de años. La fuente 1 " +
    "cubre de 1960 a 2020 y sube de 20 a 80. La fuente 2 cubre solo de 2010 a " +
    "2020, sube de 72 a 80 y en su escala se ve casi plana.",
  "/preguntas/his-linea-tiempo.svg":
    "Línea de tiempo de 1900 a 2000 dividida en cuatro tramos iguales de " +
    "veinticinco años, rotulados I, II, III y IV. Las marcas son 1900, 1925, " +
    "1950, 1975 y 2000.",
  "/preguntas/his-esquema-bloques.svg":
    "Esquema de un territorio partido en dos por una línea gruesa. A la " +
    "izquierda, el bloque occidental, con economía de mercado y democracias " +
    "liberales. A la derecha, el bloque oriental, con economía planificada y " +
    "partido único. Sobre la línea divisoria hay una ciudad dividida. La figura " +
    "aclara que es un esquema y no un mapa a escala.",
  "/preguntas/his-piramides-poblacion.svg":
    "Dos pirámides de población del mismo país, por grupos de edad y sexo. La de " +
    "1960 es muy ancha en la base y se angosta rápido hacia arriba. La de 2020 " +
    "tiene la base más angosta y los tramos de adultos y mayores mucho más " +
    "anchos. La figura advierte que los datos son ficticios.",
  "/preguntas/his-grafico-urbanizacion.svg":
    "Gráfico del porcentaje de población urbana de un país entre 1900 y 2000: " +
    "20% en 1900, 30% en 1925, 45% en 1950, 70% en 1975 y 85% en 2000. La figura " +
    "advierte que los datos son ficticios.",
  "/preguntas/his-organigrama-poderes.svg":
    "Organigrama del Estado de Chile: de una caja superior dependen tres cajas " +
    "al mismo nivel. El poder ejecutivo gobierna y administra, el legislativo " +
    "hace las leyes y el judicial resuelve conflictos. Una nota indica que los " +
    "tres poderes son autónomos entre sí.",
  "/preguntas/his-flujo-ley.svg":
    "Diagrama de flujo de la tramitación de una ley, con cinco pasos encadenados " +
    "por flechas: iniciativa por mensaje o moción; cámara de origen, que discute " +
    "y vota; cámara revisora, que discute y vota; el Presidente, que promulga o " +
    "veta; y la publicación, con la que la ley entra en vigencia.",
  "/preguntas/his-grafico-participacion.svg":
    "Gráfico de barras con la participación electoral en cuatro elecciones " +
    "sucesivas: 87%, 49%, 47% y 85%. La figura advierte que los datos son " +
    "ficticios.",
  "/preguntas/his-circular-medios.svg":
    "Gráfico circular con el medio por el que se informa un grupo de personas: " +
    "redes sociales 42%, televisión 30%, radio 16% y diarios 12%. La figura " +
    "advierte que los datos son ficticios.",
  "/preguntas/his-piramide-judicial.svg":
    "Esquema de los tribunales en tres niveles unidos por flechas que suben: en " +
    "la base, los juzgados de primera instancia; sobre ellos, las Cortes de " +
    "Apelaciones; y arriba, la Corte Suprema. Una nota indica que las flechas " +
    "muestran hacia dónde se apela una sentencia.",
  "/preguntas/his-linea-derechos.svg":
    "Línea de tiempo entre 1940 y 2000 con tres hitos: en 1948, la Declaración " +
    "Universal de Derechos Humanos; en 1966, los pactos internacionales de " +
    "derechos; y en 1989, la Convención sobre los Derechos del Niño.",
  "/preguntas/his-tabla-derechos-laborales.svg":
    "Tabla de dos columnas que empareja cada derecho laboral con quién lo " +
    "resguarda: la jornada de trabajo con un máximo legal, con la Dirección del " +
    "Trabajo; el pago de las remuneraciones pactadas, con los tribunales " +
    "laborales; la negociación colectiva, con el sindicato de la empresa; y la " +
    "seguridad en el lugar de trabajo, con la mutualidad y la fiscalización.",
  "/preguntas/his-grafico-sindicalizacion.svg":
    "Gráfico de barras con el porcentaje de trabajadores sindicalizados por " +
    "sector: minería 32%, industria 18%, comercio 9% y servicios 12%. La figura " +
    "advierte que los datos son ficticios.",
  "/preguntas/his-grafico-ipc.svg":
    "Gráfico de la variación mensual del IPC durante seis meses: 0,8%; 0,5%; " +
    "0,2%; −0,1%; 0,3% y 1,0%. Solo abril queda bajo la línea del cero. La " +
    "figura advierte que los datos son ficticios.",
  "/preguntas/his-grafico-desempleo.svg":
    "Gráfico de barras con la tasa de desempleo por trimestre: 7%, 8%, 10% y 9%. " +
    "La figura advierte que los datos son ficticios.",
  "/preguntas/his-tabla-canasta.svg":
    "Tabla con los precios en pesos de una canasta de tres productos en dos " +
    "años: pan de 1.200 a 1.440, leche de 900 a 1.080 y arroz de 1.500 a 1.800. " +
    "El total pasa de 3.600 a 4.320. La figura advierte que los datos son " +
    "ficticios.",
  "/preguntas/his-circular-pib.svg":
    "Gráfico circular con la composición del PIB de un país por sector: " +
    "servicios 55%, industria 25%, minería 12% y agricultura 8%. La figura " +
    "advierte que los datos son ficticios.",
  "/preguntas/his-oferta-demanda.svg":
    "Gráfico de precio contra cantidad con dos rectas: la de oferta sube y la de " +
    "demanda baja. Se cortan en el punto E, desde el que salen líneas punteadas " +
    "hacia p* en el eje de precios y hacia q* en el de cantidades.",
  "/preguntas/his-demanda-desplazada.svg":
    "Gráfico de precio contra cantidad. La oferta sube y no cambia. La demanda " +
    "D1 se desplaza hacia la derecha hasta D2, y el equilibrio pasa de E1 a E2, " +
    "que queda más arriba y más a la derecha.",
  "/preguntas/his-flujo-circular.svg":
    "Esquema del flujo circular de la economía: dos cajas, hogares y empresas, " +
    "unidas por cuatro flechas. De los hogares a las empresas van el trabajo y " +
    "el capital, y el gasto en bienes; de las empresas a los hogares, los " +
    "sueldos y rentas, y los bienes y servicios.",
  "/preguntas/his-precio-maximo.svg":
    "Gráfico de oferta y demanda con una línea horizontal punteada por debajo " +
    "del cruce, rotulada precio máximo. A ese precio, la cantidad ofrecida queda " +
    "muy a la izquierda de la cantidad demandada.",
};
