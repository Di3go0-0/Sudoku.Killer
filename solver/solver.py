import json
import timeit

Cages = list[tuple[int, list[tuple[int, int]]]]
Board = list[list[int]]
MinMaxCache = list[list[tuple[int, int]]]

validations_performed = 0
combinations_tried = 0


def find_cage_index(cages: Cages, x: int, y: int) -> int:
    """Encuentra el índice de la jaula en la coordenada (x, y).

    Si la jaula en la coordenada (x, y) no existe en la lista de jaulas, se generará una AssertionError.

    :param jaulas: La lista de jaulas para consultar
    :param x: La coordenada x con índice cero
    :param y: La coordenada y con índice cero
    :return: Devuelve el índice de la jaula para la jaula en x, y
    """

    index = 0
    for total, fields in cages:
        if (x, y) in fields:
            return index
        index += 1

    raise AssertionError(f"No se encontró la jaula para las coordenadas ({x}, {y})")



def is_same_cage(cages: Cages, x1: int, y1: int, x2: int, y2: int) -> bool:
    """Devuelve verdadero si dos coordenadas pertenecen a la misma jaula.

    Si cualquiera de los conjuntos de coordenadas no se encuentra como una jaula, se generará una AssertionError.

    :param jaulas: La lista de jaulas para consultar
    :param x1: La coordenada x con índice cero de la primera jaula
    :param y1: La coordenada y con índice cero de la primera jaula
    :param x2: La coordenada x con índice cero de la segunda jaula
    :param y2: La coordenada y con índice cero de la segunda jaula
    :return: Devuelve verdadero si las jaulas son las mismas
    """

    return find_cage_index(cages, x1, y1) == find_cage_index(cages, x2, y2)


def print_board(board: Board, cages: Cages) -> None:
    """Imprime el tablero con las jaulas en la consola.

    :param board: El tablero que se va a imprimir
    :param jaulas: La lista de jaulas para mostrar en el tablero
    """

    print("+" + "---+" * 9)
    for y in range(9):
        print("|", end="")
        sep_line = "|"
        for x in range(9):
            value = board[y][x]
            end_char = "|"
            if x < 8 and is_same_cage(cages, x, y, x + 1, y):
                end_char = " "
            if y < 8 and is_same_cage(cages, x, y, x, y + 1):
                sep_line += "   +"
            else:
                sep_line += "---+"
            print(f" {value if  value > 0 else ' '} {end_char}", end="")
        print()
        print(sep_line)


def find_taken_value(board: Board, cages: Cages, cage_cache: Board,
                     x: int, y: int) -> list[int]:
    """Encuentra valores ocupados, que no estarán disponibles en la celda de la coordenada (x, y).

    :param board: El tablero donde buscar los valores ocupados
    :param cages: Las jaulas donde buscar los valores ocupados, pero solo la que incluye la coordenada
    :param cage_cache: La caché de búsqueda que convierte una coordenada en una jaula
    :param x: La coordenada x con índice cero de la posición a examinar
    :param y: La coordenada y con índice cero de la posición a examinar
    :return: Devuelve una lista de valores que ya están ocupados
    """

    taken_values = []

    # Valores ocupados en el nodo
    for ty in find_nonet_range(y):
        for tx in find_nonet_range(x):
            if board[ty][tx] > 0:
                taken_values.append(board[ty][tx])

    # Valores ocupados en la jaula
    total, fields = cages[cage_cache[y][x]]
    field_count = len(fields)
    for fx, fy in fields:
        val = board[fy][fx]
        if val > 0:
            total -= val
            field_count -= 1
            taken_values.append(val)
    # Calcular valores que son demasiado grandes para encajar ahora en la jaula, ya que hemos restado los
    # valores ya ocupados del total y reducido el conteo de campos, esto podría reducir considerablemente el número
    # de valores posibles.

    max_value = min(total - sum([i for i in range(1, 10)][:field_count - 1]), 9)
    if max_value < 9:
        taken_values.extend(range(max_value + 1, 10))
    min_value = max(total - sum([i for i in range(9, 0, -1)][:field_count - 1]), 1)
    if min_value > 1:
        taken_values.extend(range(1, min(min_value, 10)))

    # Encontrar valores ocupados en la columna y la fila en los que se encuentra la posición
    for pos in range(9):
        if board[y][pos] > 0:
            taken_values.append(board[y][pos])
        if board[pos][x] > 0:
            taken_values.append(board[pos][x])

    return taken_values


def find_minmax_value(cages: Cages, x: int, y: int) -> tuple[int, int]:
    """ Encuentra los valores mínimo y máximo posibles para una celda en el tablero

    Dado que las jaulas son un subconjunto de campos que rara vez contienen los 9 números, es posible
    calcular los valores mínimo y máximo posibles de cada campo en una jaula. El enfoque simple
    utilizado aquí considerará toda la jaula de la misma manera. Esto ayudará a reducir la cantidad de posibles
    combinaciones lo suficiente como para que incluso los tableros expertos sean solucionables en un tiempo adecuado.

    Este método solo se ejecuta una vez, y como solo se ejecuta una vez, y la caché de mín/máx se calcula
    al mismo tiempo que la caché de la jaula, buscaremos el índice de la jaula para cada celda.

    :param cages: Las jaulas a evaluar
    :param x: El índice basado en cero de la coordenada x
    :param y: El índice basado en cero de la coordenada y
    :return: Devuelve una tupla de los valores mínimo y máximo posibles
    """

    cage_index = find_cage_index(cages, x, y)
    total, fields = cages[cage_index]
    field_count = len(fields)
    min_val = max(total - sum([i for i in range(9, 0, -1)][:field_count - 1]), 1)
    max_val = min(total - sum([i for i in range(1, 10)][:field_count - 1]), 9)
    return min_val, max_val


def find_nonet_range(coord: int) -> range:
    """ Encuentra el rango de un noneto a lo largo de un solo eje.

    Los primeros 3 campos a lo largo de un eje son iguales al noneto que reside en el rango [0;3[. El
    siguiente grupo de 3 campos es igual al rango [3;6[ y los últimos 3 campos son iguales a [6:9[. Ya que esto es igual para ambos ejes,
    este método se llama para un solo eje cada vez.

    :param coord: La coordenada con base cero a lo largo de un eje
    :return: Devuelve el rango utilizado por el noneto a lo largo del eje específico
    """
    if coord < 3:
        return range(0, 3)
    if coord < 6:
        return range(3, 6)
    return range(6, 9)


def find_next_cell(board: Board, x: int, y: int) -> tuple[int, int]:
    """ Encontrar la siguiente celda desocupada en el tablero, o devolver (-1, -1).

    El método buscará la siguiente celda vacía en el tablero, sin incluir la proporcionada por
    los parámetros `x` y `y`. La búsqueda primero intentará con la celda contigua a la especificada a lo largo
    del eje x, y continuará a lo largo de este eje mientras no haya celdas libres. Si alcanza el
    final, continuará desde el comienzo de la siguiente línea en el eje y.

    Si no se encuentra ninguna celda vacía, se devolverá la tupla (-1, -1).

    :param board: El tablero donde buscar
    :param x: La coordenada de inicio en el eje x basada en cero desde la cual buscar
    :param y: La coordenada de inicio en el eje y basada en cero desde la cual buscar
    :return: Devuelve una tupla de las coordenadas x y y de la siguiente celda libre
    """
    col = x
    row = y
    while True:
        col += 1
        if col > 8:
            col = 0
            row += 1
        if row > 8:
            return -1, -1
        if board[row][col] == 0:
            return col, row


def validate_rows(board: Board) -> bool:
    """ Valida las filas en el tablero, verificando que no existan duplicados en una sola fila.

    Solo se validarán las celdas completadas, lo que significa que una fila medio completada puede ser válida siempre y cuando
    no contenga duplicados. Este método solo busca duplicados y detiene la búsqueda
    tan pronto como descubre uno.

    :param board: El tablero a validar
    :return: Devuelve un booleano Verdadero si ninguna fila contiene duplicados
    """
    for col in range(9):
        row_set = set()
        for row in range(9):
            value = board[row][col]
            if value != 0:
                if value in row_set:
                    return False
                row_set.add(value)
    return True


def validate_cols(board: Board) -> bool:
    """ Valida las columnas en el tablero, verificando que no existan duplicados en una sola columna.

    Solo se validarán las celdas completadas, lo que significa que una columna medio completada puede ser válida siempre y cuando
    no contenga duplicados. Este método solo busca duplicados y detiene la búsqueda
    tan pronto como descubre uno.

    :param board: El tablero a validar
    :return: Devuelve un booleano Verdadero si ninguna columna contiene duplicados
    """
    for row in range(9):
        col_set = set()
        for value in board[row]:
            if value != 0:
                if value in col_set:
                    return False
                col_set.add(value)
    return True


def validate_nonets(board: Board) -> bool:
    """ Valida los nonetes en el tablero, verificando que no existan duplicados en un nonet.

    Solo se validarán las celdas completadas, lo que significa que un nonet medio completado puede ser válido siempre y cuando
    no contenga duplicados. Este método solo busca duplicados y detiene la búsqueda
    tan pronto como descubre uno.

    :param board: El tablero a validar
    :return: Devuelve un booleano Verdadero si no existen duplicados en ningún nonet
    """
    for nonet_x in range(0, 9, 3):
        range_x = find_nonet_range(nonet_x)
        for nonet_y in range(0, 9, 3):
            nonet_set = set()
            for y in find_nonet_range(nonet_y):
                for x in range_x:
                    value = board[y][x]
                    if value != 0:
                        if value in nonet_set:
                            return False
                        nonet_set.add(value)
    return True


def validate_cages(board: Board, cages: Cages) -> bool:
    """ Valida todas las jaulas, verificando que no existan duplicados en estas, y que la suma sea igual
    al total deseado de la jaula.

    El método itera a través de todas las jaulas, para probar tanto los duplicados como también la suma total
    dentro de la jaula. Solo se examinan los valores completados, por lo que una jaula puede ser válida si no
    contiene duplicados y no está completamente llena. Si todos los campos están llenos, se examina la suma total
    de la jaula y si no es igual a la suma deseada de la jaula, el método
    devolverá un booleano Falso.

    Esta comprobación también podría imponerse para jaulas no terminadas, donde una suma que es más alta, o
    demasiado alta para ser alcanzada con los valores disponibles no reclamados, resultaría en un fallo. Dado que este
    método solo se usa realmente para nodos hoja, que tienen todos los campos llenos, no tendría sentido
    hacerlo más costoso al comprobar esto también. En otras palabras, perjudicaría
    el rendimiento, y por lo tanto no se realiza.

    :param board: El tablero del que extraer valores
    :param cages: Las jaulas a validar
    :return: Devuelve un booleano Verdadero si no se encuentran duplicados en una jaula, y el total es igual al
             total válido de la jaula
    """
    for total, fields in cages:
        cage_set = set()
        for x, y in fields:
            value = board[y][x]
            if value != 0:
                if value in cage_set:
                    return False
                cage_set.add(value)
        if len(cage_set) == len(fields):
            if sum(cage_set) != total:
                return False
    return True


def validate(board: Board, cages: Cages) -> bool:
    """ Valida las columnas, filas, nonetes y jaulas en el tablero.

    Valida las columnas, filas, nonetes y campos en ese orden. Si alguna de estas no es válida, la
    función se interrumpirá inmediatamente para ahorrar potencia de procesamiento. La validación puede validar un
    tablero sin terminar, siempre y cuando no contenga duplicados, será marcado como válido. Por lo tanto,
    para que un tablero sea completamente válido y esté terminado, debe ser válido sin celdas vacías restantes.

    :param board: El tablero a validar
    :param cages: Las jaulas a validar
    :return: Devuelve un booleano Verdadero si el tablero es válido
    """
    global validations_performed
    validations_performed += 1

    return validate_cols(board) and validate_rows(board) and validate_nonets(board) and \
        validate_cages(board, cages)


def fill_out_next(board: Board, cages: Cages, cage_cache: Board,
                  minmax_cache: MinMaxCache, x: int, y: int) -> bool:
    """ Rellenar el siguiente valor en el tablero, y si todos los valores están completos, validar el tablero.

    Si el campo en (x, y) ya está lleno, el método generará un AssertionError.

    Este método funciona básicamente tomando un valor que aún no está en conflicto con un valor existente
    en la fila, columna, nonet o jaula de la coordenada. Aplica el valor y se llama a sí mismo
    recursivamente para la siguiente celda, hasta que todas las celdas estén llenas, en ese momento retrocede
    e intenta el siguiente valor disponible.

    :param board: El tablero para rellenar
    :param cages: Las jaulas a respetar
    :param cage_cache: La caché de búsqueda de jaulas
    :param minmax_cache: Los límites de valor mínimo/máximo a usar para limitar el tamaño de la búsqueda
    :param x: La coordenada x basada en cero para rellenar
    :param y: La coordenada y basada en cero para rellenar
    :return: Devuelve un booleano Verdadero si este tablero es válido, y Falso si nunca podría serlo en su
             forma actual
    """
    if board[y][x] != 0:
        raise AssertionError(f"Field ({x}, {y}) is not empty")

    global combinations_tried
    combinations_tried += 1

    next_x, next_y = find_next_cell(board, x, y)
    taken_values = find_taken_value(board, cages, cage_cache, x, y)

    # Si queda más de un valor, recorre todos los valores en el rango de mínimo a máximo, y omite los
    # que ya están tomados, reservados (necesarios en otro lugar), o fuera de alcance (demasiado altos o bajos para
    # la jaula). Si solo queda un valor, entonces la lista de valores tomados incluirá todos los valores
    # que no puede ser, y solo se completará una iteración
    min_value, max_value = minmax_cache[y][x]
    for value in range(min_value, max_value + 1):
        if value not in taken_values:
            board[y][x] = value
            if next_x == -1:
                success = validate(board, cages)
                if not success:
                    board[y][x] = 0
                return success
            if fill_out_next(board, cages, cage_cache, minmax_cache, next_x, next_y):
                return True
    board[y][x] = 0
    return False


def solve(board: Board, cages: Cages) -> bool:
    """ Resolver Sudoku a partir del tablero y las jaulas

    El método devolverá un booleano verdadero si el tablero fue resuelto, o falso si por alguna razón
    no fue posible resolverlo. El parámetro del tablero se actualizará para reflejar la solución, cuando
    la función termine.

    :param board: El tablero inicial a utilizar
    :param cages: Las jaulas de ese tablero
    :return: Devuelve un booleano verdadero si el Sudoku pudo ser resuelto
    """

    # Crear cachés de búsqueda para acelerar el proceso de encontrar jaulas y limitar los posibles
    # valores de cada celda.
    cage_cache = []
    minmax_cache = []
    for y in range(9):
        cage_row = []
        minmax_row = []
        for x in range(9):
            cage_row.append(find_cage_index(cages, x, y))
            minmax_row.append(find_minmax_value(cages, x, y))
        cage_cache.append(cage_row)
        minmax_cache.append(minmax_row)

    # Rellenar jaulas individuales, comenzamos haciendo esto, ya que son fáciles de aislar y lo harán
    # nos darán un rango de búsqueda más pequeño.

    for total, fields in cages:
        if len(fields) == 1:
            x, y = fields[0]
            board[y][x] = total

    # El siguiente método de rellenar espera que el campo esté vacío, así que asegúrate de que el campo 
    # con el que empezamos esté realmente vacío.
    next_x, next_y = 0, 0
    if board[next_x][next_y] != 0:
        next_x, next_y = find_next_cell(board, next_x, next_y)

    return fill_out_next(board, cages, cage_cache, minmax_cache, next_x, next_y)


def load_from_file(filename: str) -> tuple[Board, Cages]:
    """ Carga los datos del tablero y las jaulas desde un archivo JSON.

    :param filename: El nombre del archivo del cual cargar los datos del tablero y las jaulas
    :return: Devuelve una tupla con el tablero y las jaulas obtenidas del archivo
    """
    with open(filename) as board_file:
        data = json.load(board_file)

        # Convertir jaulas de JSON básico a tuplas útiles
        cages = []
        for total, fields in data["cages"]:
            tuples = []
            for x, y in fields:
                tuples.append((x, y))
            cages.append((total, tuples))
        return data["board"], cages


def run_solver(filenames: list[str], show_stats: bool = False, benchmark: bool = False,
               show_initial_board: bool = False) -> None:
    """Ejecuta el solucionador para una lista de archivos.
    :param filenames: La lista de nombres de archivos para cargar y resolver
    :param show_stats: Si se muestran estadísticas como el número de validaciones y combinaciones únicas
    :param benchmark: Mostrará el tiempo que toma para una iteración
    :param show_initial_board: Si se muestra el diseño del tablero antes de resolverlo
    """
    for filename in filenames:
        global validations_performed, combinations_tried
        validations_performed, combinations_tried = 0, 0
        board, cages = load_from_file(filename=filename)
        print(f"Usando tablero y jaulas de {filename}")
        if show_initial_board:
            print_board(board, cages)

        if benchmark:
            print("Haciendo benchmark...")
            benchmark_result = timeit.timeit(lambda b=board, c=cages: solve(b, c), number=1)
            print_board(board, cages)
            print(f"Benchmark completado para {filename}: duración: {benchmark_result} segundos")
        else:
            print("Calculando...")
            success = solve(board, cages)
            if success:
                print("ÉXITO")
            else:
                print("No se pudo encontrar solución")
            print_board(board, cages)

        if show_stats:
            print(f"Validaciones realizadas: {validations_performed}")
            print(f"Combinaciones únicas probadas: {combinations_tried}")
