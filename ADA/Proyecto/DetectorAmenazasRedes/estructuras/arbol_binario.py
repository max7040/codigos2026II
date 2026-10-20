"""Árbol binario de búsqueda (Semana 9 del sílabo: árboles)."""


class _Nodo:
    __slots__ = ("clave", "izq", "der")

    def __init__(self, clave):
        self.clave = clave
        self.izq = None
        self.der = None


class ArbolBinarioBusqueda:
    """BST sin claves duplicadas (insertar una clave existente no la repite).

    Tiempo de insertar/buscar/eliminar: O(h), con h la altura; O(log n) si el
    árbol está equilibrado y O(n) en el peor caso (claves insertadas en orden).
    Espacio: O(n). Las operaciones son iterativas para no depender del límite
    de recursión de Python.
    """

    def __init__(self):
        self._raiz = None
        self._tamano = 0

    def insertar(self, clave):
        """Inserta la clave. Devuelve True si se insertó y False si ya existía."""
        if self._raiz is None:
            self._raiz = _Nodo(clave)
            self._tamano += 1
            return True
        actual = self._raiz
        while True:
            if clave == actual.clave:
                return False
            if clave < actual.clave:
                if actual.izq is None:
                    actual.izq = _Nodo(clave)
                    break
                actual = actual.izq
            else:
                if actual.der is None:
                    actual.der = _Nodo(clave)
                    break
                actual = actual.der
        self._tamano += 1
        return True

    def buscar(self, clave):
        """Devuelve True si la clave está en el árbol."""
        actual = self._raiz
        while actual is not None:
            if clave == actual.clave:
                return True
            actual = actual.izq if clave < actual.clave else actual.der
        return False

    def eliminar(self, clave):
        """Elimina la clave. Devuelve True si existía y False si no."""
        padre, actual = None, self._raiz
        while actual is not None and actual.clave != clave:
            padre = actual
            actual = actual.izq if clave < actual.clave else actual.der
        if actual is None:
            return False
        if actual.izq is not None and actual.der is not None:
            # Dos hijos: se reemplaza por el sucesor inorden (mínimo del subárbol derecho).
            padre_suc, suc = actual, actual.der
            while suc.izq is not None:
                padre_suc, suc = suc, suc.izq
            actual.clave = suc.clave
            padre, actual = padre_suc, suc
        hijo = actual.izq if actual.izq is not None else actual.der
        if padre is None:
            self._raiz = hijo
        elif padre.izq is actual:
            padre.izq = hijo
        else:
            padre.der = hijo
        self._tamano -= 1
        return True

    def inorden(self):
        """Claves en orden ascendente. Tiempo O(n)."""
        resultado, pila, actual = [], [], self._raiz
        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izq
            actual = pila.pop()
            resultado.append(actual.clave)
            actual = actual.der
        return resultado

    def altura(self):
        """Altura del árbol (vacío = 0, un nodo = 1). Tiempo O(n)."""
        if self._raiz is None:
            return 0
        altura, nivel = 0, [self._raiz]
        while nivel:
            altura += 1
            nivel = [h for n in nivel for h in (n.izq, n.der) if h is not None]
        return altura

    def minimo(self):
        if self._raiz is None:
            return None
        actual = self._raiz
        while actual.izq is not None:
            actual = actual.izq
        return actual.clave

    def maximo(self):
        if self._raiz is None:
            return None
        actual = self._raiz
        while actual.der is not None:
            actual = actual.der
        return actual.clave

    def __len__(self):
        return self._tamano

    def __contains__(self, clave):
        return self.buscar(clave)
