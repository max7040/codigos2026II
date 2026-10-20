"""Tabla hash con encadenamiento separado (Semana 4 del sílabo).

Las colisiones se resuelven guardando una lista de pares (clave, valor) en cada
casillero. La función hash es propia para enteros y cadenas.
"""


class TablaHash:
    """Tabla hash con redimensionamiento automático.

    Operaciones: insertar, buscar y eliminar con tiempo promedio O(1) y
    peor caso O(n) (todas las claves en un mismo casillero).
    Espacio: O(n + m), con m = número de casilleros.
    """

    FACTOR_CARGA_MAXIMO = 0.75

    def __init__(self, capacidad=8):
        if capacidad < 1:
            raise ValueError("La capacidad debe ser al menos 1.")
        self._casilleros = [[] for _ in range(capacidad)]
        self._tamano = 0

    @staticmethod
    def _hash(clave):
        if isinstance(clave, bool):
            return int(clave)
        if isinstance(clave, int):
            return abs(clave)
        if isinstance(clave, str):
            h = 0
            for caracter in clave:
                h = (h * 31 + ord(caracter)) % 2_147_483_647
            return h
        return abs(hash(clave))

    def _indice(self, clave):
        return self._hash(clave) % len(self._casilleros)

    def insertar(self, clave, valor):
        """Inserta o actualiza el valor asociado a la clave."""
        casillero = self._casilleros[self._indice(clave)]
        for i, (k, _) in enumerate(casillero):
            if k == clave:
                casillero[i] = (clave, valor)
                return
        casillero.append((clave, valor))
        self._tamano += 1
        if self._tamano / len(self._casilleros) > self.FACTOR_CARGA_MAXIMO:
            self._redimensionar(len(self._casilleros) * 2)

    def buscar(self, clave, defecto=None):
        """Devuelve el valor asociado o 'defecto' si la clave no existe."""
        for k, v in self._casilleros[self._indice(clave)]:
            if k == clave:
                return v
        return defecto

    def eliminar(self, clave):
        """Elimina la clave. Devuelve True si existía y False si no."""
        casillero = self._casilleros[self._indice(clave)]
        for i, (k, _) in enumerate(casillero):
            if k == clave:
                del casillero[i]
                self._tamano -= 1
                return True
        return False

    def _redimensionar(self, nueva_capacidad):
        pares = list(self.items())
        self._casilleros = [[] for _ in range(nueva_capacidad)]
        for k, v in pares:
            self._casilleros[self._indice(k)].append((k, v))

    def items(self):
        for casillero in self._casilleros:
            for par in casillero:
                yield par

    def __contains__(self, clave):
        return any(k == clave for k, _ in self._casilleros[self._indice(clave)])

    def __len__(self):
        return self._tamano

    @property
    def capacidad(self):
        return len(self._casilleros)

    def estadisticas(self):
        """Datos para analizar colisiones: casilleros usados, mayor cadena y factor de carga."""
        usados = sum(1 for c in self._casilleros if c)
        return {
            "elementos": self._tamano,
            "capacidad": len(self._casilleros),
            "casilleros_usados": usados,
            "cadena_maxima": max((len(c) for c in self._casilleros), default=0),
            "factor_carga": self._tamano / len(self._casilleros),
        }
