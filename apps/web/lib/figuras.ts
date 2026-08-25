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
