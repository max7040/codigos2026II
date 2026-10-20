"""Modelo de grafo propio con lista de adyacencia (Semana 9 del sílabo: grafos).

La estructura interna es una LISTA DE ADYACENCIA implementada con diccionarios:
    _ady[u][v] = propiedades de la conexión u -> v
Además puede generarse una MATRIZ DE ADYACENCIA para compararlas (Módulo F).
NetworkX no se usa aquí: se usa solo en la visualización (visualizacion/grafo_visual.py).
"""

import math

TIPOS_NODO = ("equipo", "servidor", "cuenta")
MAX_LONGITUD_ID = 64


class ErrorGrafo(ValueError):
    """Error de uso del grafo (dato inválido, nodo inexistente, duplicado...)."""


def _validar_id(valor):
    if not isinstance(valor, str):
        raise ErrorGrafo("El identificador del nodo debe ser texto.")
    valor = valor.strip()
    if not valor:
        raise ErrorGrafo("El identificador del nodo no puede estar vacío.")
    if len(valor) > MAX_LONGITUD_ID:
        raise ErrorGrafo(f"El identificador no puede superar {MAX_LONGITUD_ID} caracteres.")
    return valor


def _validar_tipo(tipo):
    if tipo not in TIPOS_NODO:
        raise ErrorGrafo(f"Tipo de nodo no válido: {tipo!r}. Opciones: {', '.join(TIPOS_NODO)}.")
    return tipo


def _numero(valor, campo, *, entero=False, estrictamente_positivo=False):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErrorGrafo(f"'{campo}' debe ser un número.")
    if not math.isfinite(valor):
        raise ErrorGrafo(f"'{campo}' debe ser un número finito.")
    if estrictamente_positivo and valor <= 0:
        raise ErrorGrafo(f"'{campo}' debe ser mayor que 0.")
    if valor < 0:
        raise ErrorGrafo(f"'{campo}' no puede ser negativo.")
    if entero:
        if int(valor) != valor:
            raise ErrorGrafo(f"'{campo}' debe ser un número entero.")
        return int(valor)
    return float(valor)


def _propiedades(peso, frecuencia, eventos):
    return {
        "peso": _numero(peso, "peso", estrictamente_positivo=True),
        "frecuencia": _numero(frecuencia, "frecuencia"),
        "eventos": _numero(eventos, "eventos", entero=True),
    }


class Grafo:
    """Grafo dirigido o no dirigido, sin lazos ni conexiones repetidas entre el mismo par.

    Propiedades de cada conexión:
      peso        (> 0)   importancia o costo relativo de la conexión.
      frecuencia  (>= 0)  eventos por unidad de tiempo (valor simulado).
      eventos     (>= 0)  cantidad de eventos registrados (entero).

    Complejidades (n nodos, m conexiones, g = grado del nodo):
      agregar_nodo / agregar_conexion / existe_conexion / obtener_conexion: O(1) promedio.
      vecinos / grado: O(g).   eliminar_conexion: O(1) promedio.
      eliminar_nodo: O(g) (O(n) en el peor caso en dirigidos por los predecesores).
      matriz_adyacencia: O(n^2) tiempo y espacio.   conexiones(): O(n + m).
    """

    def __init__(self, dirigido=False):
        self._dirigido = bool(dirigido)
        self._tipos = {}      # id -> tipo
        self._ady = {}        # u -> {v: props}   (salientes; en no dirigido, todos los vecinos)
        self._pred = {}       # v -> {u: props}   (solo se usa en dirigidos)

    # ---------- Información general ----------
    @property
    def dirigido(self):
        return self._dirigido

    def nodos(self):
        return list(self._tipos)

    def tipo_nodo(self, nodo):
        self._exigir_nodo(nodo)
        return self._tipos[nodo]

    @property
    def num_nodos(self):
        return len(self._tipos)

    @property
    def num_conexiones(self):
        total = sum(len(v) for v in self._ady.values())
        return total if self._dirigido else total // 2

    def total_eventos(self):
        """Suma de los eventos registrados en todas las conexiones."""
        return sum(c["eventos"] for c in self.conexiones())

    def _exigir_nodo(self, nodo):
        if nodo not in self._tipos:
            raise ErrorGrafo(f"El nodo {nodo!r} no existe.")

    # ---------- Nodos ----------
    def agregar_nodo(self, nodo, tipo="equipo"):
        nodo = _validar_id(nodo)
        tipo = _validar_tipo(tipo)
        if nodo in self._tipos:
            raise ErrorGrafo(f"El nodo {nodo!r} ya existe.")
        self._tipos[nodo] = tipo
        self._ady[nodo] = {}
        self._pred[nodo] = {}
        return nodo

    def editar_nodo(self, nodo, tipo):
        """Cambia el tipo de un nodo existente."""
        self._exigir_nodo(nodo)
        self._tipos[nodo] = _validar_tipo(tipo)

    def eliminar_nodo(self, nodo):
        """Elimina el nodo y todas las conexiones que lo tocan."""
        self._exigir_nodo(nodo)
        for v in list(self._ady[nodo]):
            self.eliminar_conexion(nodo, v)
        if self._dirigido:
            for u in list(self._pred[nodo]):
                self.eliminar_conexion(u, nodo)
        del self._tipos[nodo]
        del self._ady[nodo]
        del self._pred[nodo]

    # ---------- Conexiones ----------
    def agregar_conexion(self, origen, destino, peso=1.0, frecuencia=0.0, eventos=0):
        self._exigir_nodo(origen)
        self._exigir_nodo(destino)
        if origen == destino:
            raise ErrorGrafo(f"No se permiten conexiones de un nodo consigo mismo ({origen!r}).")
        if self.existe_conexion(origen, destino):
            raise ErrorGrafo(f"La conexión {origen!r} -> {destino!r} ya existe; edítela en su lugar.")
        props = _propiedades(peso, frecuencia, eventos)
        self._ady[origen][destino] = props
        if self._dirigido:
            self._pred[destino][origen] = props
        else:
            self._ady[destino][origen] = props  # mismo diccionario: editar uno actualiza ambos

    def editar_conexion(self, origen, destino, peso=None, frecuencia=None, eventos=None):
        """Modifica solo las propiedades indicadas (las None se conservan)."""
        actual = self._obtener(origen, destino)
        nuevas = _propiedades(
            actual["peso"] if peso is None else peso,
            actual["frecuencia"] if frecuencia is None else frecuencia,
            actual["eventos"] if eventos is None else eventos,
        )
        actual.update(nuevas)  # se actualiza in situ para conservar el diccionario compartido

    def eliminar_conexion(self, origen, destino):
        self._obtener(origen, destino)
        del self._ady[origen][destino]
        if self._dirigido:
            del self._pred[destino][origen]
        else:
            del self._ady[destino][origen]

    def existe_conexion(self, origen, destino):
        return origen in self._ady and destino in self._ady[origen]

    def _obtener(self, origen, destino):
        self._exigir_nodo(origen)
        self._exigir_nodo(destino)
        if destino not in self._ady[origen]:
            raise ErrorGrafo(f"La conexión {origen!r} -> {destino!r} no existe.")
        return self._ady[origen][destino]

    def obtener_conexion(self, origen, destino):
        """Devuelve una copia de las propiedades de la conexión."""
        return dict(self._obtener(origen, destino))

    def conexiones(self):
        """Lista de conexiones como diccionarios (en no dirigidos, cada una aparece una vez)."""
        posicion = {n: i for i, n in enumerate(self._tipos)}
        resultado = []
        for u, vecinos in self._ady.items():
            for v, p in vecinos.items():
                if self._dirigido or posicion[u] < posicion[v]:
                    resultado.append({"origen": u, "destino": v, **p})
        return resultado

    # ---------- Consultas (Módulo F) ----------
    def vecinos(self, nodo):
        """Vecinos alcanzables desde el nodo (salientes si el grafo es dirigido)."""
        self._exigir_nodo(nodo)
        return list(self._ady[nodo])

    def predecesores(self, nodo):
        """Nodos que apuntan al nodo (en no dirigidos coincide con vecinos)."""
        self._exigir_nodo(nodo)
        return list(self._pred[nodo]) if self._dirigido else list(self._ady[nodo])

    def grado_salida(self, nodo):
        self._exigir_nodo(nodo)
        return len(self._ady[nodo])

    def grado_entrada(self, nodo):
        self._exigir_nodo(nodo)
        return len(self._pred[nodo]) if self._dirigido else len(self._ady[nodo])

    def grado(self, nodo):
        """No dirigido: número de vecinos. Dirigido: grado de entrada + grado de salida."""
        if self._dirigido:
            return self.grado_entrada(nodo) + self.grado_salida(nodo)
        return self.grado_salida(nodo)

    # ---------- Representaciones ----------
    def lista_adyacencia(self):
        """Devuelve {nodo: [vecinos]}."""
        return {n: list(v) for n, v in self._ady.items()}

    def matriz_adyacencia(self, usar_pesos=False):
        """Devuelve (nodos, matriz). La celda [i][j] vale 1 (o el peso) si hay conexión i -> j."""
        nodos = self.nodos()
        indice = {n: i for i, n in enumerate(nodos)}
        matriz = [[0] * len(nodos) for _ in nodos]
        for u, vecinos in self._ady.items():
            for v, p in vecinos.items():
                matriz[indice[u]][indice[v]] = p["peso"] if usar_pesos else 1
        return nodos, matriz

    # ---------- Serialización ----------
    def a_dict(self):
        return {
            "dirigido": self._dirigido,
            "nodos": [{"id": n, "tipo": t} for n, t in self._tipos.items()],
            "conexiones": self.conexiones(),
        }

    def copiar(self):
        nuevo = Grafo(self._dirigido)
        for n, t in self._tipos.items():
            nuevo.agregar_nodo(n, t)
        for c in self.conexiones():
            nuevo.agregar_conexion(c["origen"], c["destino"], c["peso"], c["frecuencia"], c["eventos"])
        return nuevo

    def __len__(self):
        return len(self._tipos)

    def __contains__(self, nodo):
        return nodo in self._tipos
