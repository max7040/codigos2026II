import threading
import time
import random
from collections import deque

TAM_BUFFER = 3

buffer = deque()          # Cola FIFO: append() al final, popleft() al inicio
contador_items = 0        # Dato compartido: numera los items producidos

mutex = threading.Semaphore(1)                        # Exclusión mutua sobre buffer y contador
espacios_libres = threading.Semaphore(TAM_BUFFER)     # Cuenta los huecos libres del buffer
items_disponibles = threading.Semaphore(0)            # Cuenta los items listos para consumir


def productor(id_productor, cantidad):
    global contador_items

    for _ in range(cantidad):
        time.sleep(random.uniform(0.1, 0.4))   # Tiempo de "fabricar" el item

        # Si no hay espacio, el hilo se bloquea (duerme) hasta que alguien libere un hueco
        if not espacios_libres.acquire(blocking=False):
            print(f"[PRODUCTOR {id_productor}] Buffer LLENO. Se duerme esperando espacio...")
            espacios_libres.acquire()

        mutex.acquire()
        contador_items += 1
        item = contador_items
        buffer.append(item)
        print(f"--> [PRODUCTOR {id_productor}] Produjo item {item}. Buffer: {list(buffer)}")
        mutex.release()

        items_disponibles.release()   # Avisa que hay un item más


def consumidor(id_consumidor, cantidad):
    for _ in range(cantidad):

        # Si no hay items, el hilo se bloquea (duerme) hasta que alguien produzca
        if not items_disponibles.acquire(blocking=False):
            print(f"[CONSUMIDOR {id_consumidor}] Buffer VACÍO. Se duerme esperando items...")
            items_disponibles.acquire()

        mutex.acquire()
        item = buffer.popleft()       # Sale el item más antiguo (FIFO)
        print(f"<-- [CONSUMIDOR {id_consumidor}] Consumió item {item}. Buffer: {list(buffer)}")
        mutex.release()

        espacios_libres.release()     # Avisa que hay un hueco más
        time.sleep(random.uniform(0.5, 1.0))   # Tiempo de "usar" el item


if __name__ == "__main__":
    print("=== INICIO DE LA SIMULACIÓN DE PRODUCTOR - CONSUMIDOR ===")
    hilos = []

    for i in range(1, 3):
        t = threading.Thread(target=productor, args=(i, 5))
        hilos.append(t)
        t.start()

    for i in range(1, 3):
        t = threading.Thread(target=consumidor, args=(i, 5))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    print("=== FIN DE LA SIMULACIÓN ===")