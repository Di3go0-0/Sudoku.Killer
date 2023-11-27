Resolutor de Sudoku Killer
==============================
El Sudoku Asesino es una variante del Sudoku donde, además de los nonetos regulares de números del 1 al 9,
también existen jaulas adicionales que actúan como una limitación adicional sobre qué números pueden estar dónde.
Las jaulas son básicamente la única adición al Sudoku regular, por lo que donde el Sudoku regular dicta
que los números del 1 al 9 solo pueden existir una vez por cada fila, columna y noneto. El Sudoku Asesino
se construye sobre eso y agrega una limitación adicional de que el mismo número no puede estar representado más
de una vez en cada jaula, y que la suma de los números dentro de la jaula debe ser un número específico.

En el Sudoku, las limitaciones adicionales suelen ser una ventaja para el jugador, ya que limitan mucho las
combinaciones posibles que se pueden jugar. Sin embargo, en el Sudoku Asesino hay menos campos (si es que hay alguno) completados desde
el principio.

============================================================
Rendimiento
==============================

En mi Core i7 4770K, resolver un rompecabezas de nivel experto (sin ningún campo en el tablero) toma menos de
un segundo utilizando este algoritmo. El tiempo que se tarda en completar varía de un rompecabezas a otro y está
fundamentalmente basado en cuántas combinaciones se pueden eliminar del árbol de búsqueda. Para probar el
rendimiento localmente, utiliza el parámetro --benchmark que mostrará cuánto tiempo se tarda en resolver el
rompecabezas proporcionado(s).

============================================================
Cómo funciona
==============================

El código funciona básicamente llenando el tablero con valores, probando la combinación, y si no es
válida, intenta otra combinación. Obviamente, esa es una explicación simplificada, pero fundamentalmente el
código llena el tablero un campo a la vez, hasta que está completamente lleno, luego valida el tablero
y si la combinación no fue válida, el último valor agregado se elimina y se elige el siguiente valor, y se repite la validación. Esto continúa hasta que todos los valores posibles han sido probados en la última posición, si aún no es válido, el próximo valor grande se reemplaza con el siguiente valor posible,
y el proceso se repite.

Sin embargo, simplemente probar todas las combinaciones no es un enfoque viable, hay demasiadas posibles
combinaciones, 6,670,903,752,021,072,936,960 para ser exactos. Por lo tanto, es necesario limitar la cantidad
de combinaciones probadas. Primero eliminando combinaciones inválidas, es decir, duplicados y valores en
jaulas que exceden el total. Para cada celda se calcula un mínimo y un máximo. Este es el valor más bajo posible y el valor más alto posible que la celda puede tener.

Considera una jaula con el valor de 17, compuesta por dos celdas, el valor mínimo es 8, ya que ningún
otro número menor que ese puede sumar 17. El valor máximo es 9. Entonces, las celdas tendrán cada una 8
o 9. No tiene sentido probar otros números en esa jaula, así que no hay razón para probar otras combinaciones.
Si 8 o 9 no están disponibles y ya están tomados, entonces ya sabemos que la combinación no es válida,
y no hay razón para continuar con la búsqueda.

Otra limitación simple son las jaulas de tamaño 2, que tienen un número par. Aquí el valor que es la mitad
de este número no se puede usar. Por ejemplo, una jaula con el valor 10 y tamaño de 2, no puede usar el
valor 5, ya que eso requeriría que ambos campos tengan el mismo valor, y eso no es legal. Así que aquí
podemos eliminar otra posible combinación de búsqueda.

Cada vez que se rellenan algunos de los valores de una jaula, podemos restar esos valores del total y
aplicar la optimización de valor mínimo y máximo en las celdas restantes.

============================================================
Cómo usarlo
==============================

El código se puede llamar desde Python creando una estructura de tablero y una lista de jaulas. La estructura
del tablero es realmente solo una lista bidimensional de valores para cada celda. Un 0 indica que la celda
está vacía. Para los desafíos de nivel experto