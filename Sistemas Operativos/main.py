"""
main.py
Punto de entrada de la aplicación. Ejecutar con:  python main.py
"""

import tkinter as tk

from interfaz import InterfazSimulador


def main():
    raiz = tk.Tk()
    InterfazSimulador(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()