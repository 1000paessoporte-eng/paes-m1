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
  "/preguntas/bio-crecimiento-poblacional.svg":
    "Gráfico del número de conejos a lo largo de doce años. La curva tiene forma de " +
    "S: parte casi plana cerca de cero, se empina hasta pasar por 600 individuos a " +
    "los 6 años y luego se aplana acercándose a una línea horizontal marcada como " +
    "capacidad de carga K igual a 1.200. Sobre la curva hay cuatro puntos: P al año " +
    "y medio, Q a los 6 años, R a los 9 y S a los 11 y medio.",
};
