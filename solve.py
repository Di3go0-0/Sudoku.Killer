#!/usr/bin/env python3
import argparse

import solver


def show_about():
    print("""Resolutor de Sudoku Asesino.
          Script para resolver rompecabezas de Sudoku Asesino, donde los clásicos rompecabezas de Sudoku se amplían con jaulas
          que pueden abarcar múltiples nonetes. Las jaulas tienen un número y un operador matemático, y el número es el resultado""")


def main():
    parser = argparse.ArgumentParser(description="Resuelve un Killer Sudoku desde un archivo JSON")
    parser.add_argument("--stats",
                        action="store_true",
                        help=("Si se configura, el solucionador generará información sobre cuántas combinaciones "
                              "fueron intentados antes de encontrar la solución."))
    parser.add_argument("--show-initial-board",
                        action="store_true",
                        help="Muestra el tablero y las regiones antes de intentar resolverlo.")
    parser.add_argument("--benchmark",
                        action="store_true",
                        help=("Haga una comparación con los archivos especificados,"
                              "intentando resolver los acertijos y mostrando el tiempo necesario para hacerlo."))
    parser.add_argument("--about",
                        action="store_true",
                        help="Muestra texto que describe este script y sale")
    parser.add_argument("filename",
                        nargs='+',
                        help="El nombre del archivo JSON para cargar el tablero y las regiones de jaula. ")
    parsed_args = parser.parse_args()

    if parsed_args.about:
        return show_about()

    solver.run_solver(filenames=parsed_args.filename,
                      show_stats=parsed_args.stats,
                      benchmark=parsed_args.benchmark,
                      show_initial_board=parsed_args.show_initial_board)


if __name__ == '__main__':
    main()
