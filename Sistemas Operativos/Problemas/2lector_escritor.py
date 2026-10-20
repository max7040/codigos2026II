import threading
import time
import random

base_de_datos = "Información Inicial"

mutex = threading.Semaphore(1)        # Protege el contador lectores_activos
rw_mutex = threading.Semaphore(1)     # Acceso exclusivo a la base de datos
cola_fifo = threading.Semaphore(1)    # Cola de turnos: nadie se salta a nadie (evita inanición)

lectores_activos = 0


def lector(id_lector):
    global lectores_activos

    print(f"[LECTOR {id_lector}] Quiere leer.")

    cola_fifo.acquire()              # Hace fila. Si un escritor espera, se queda detrás de él
    mutex.acquire()
    lectores_activos += 1
    if lectores_activos == 1:
        rw_mutex.acquire()           # El primer lector bloquea a los escritores
    mutex.release()
    cola_fifo.release()              # Ya pasó: deja avanzar al siguiente de la fila

    print(f"--> [LECTOR {id_lector}] LEYENDO. Dato actual: '{base_de_datos}' (Lectores activos: {lectores_activos})")
    time.sleep(random.uniform(1, 2))
    print(f"<-- [LECTOR {id_lector}] Terminó de leer.")

    mutex.acquire()
    lectores_activos -= 1
    if lectores_activos == 0:
        rw_mutex.release()           # El último lector libera la base de datos
    mutex.release()


def escritor(id_escritor):
    global base_de_datos

    print(f"[ESCRITOR {id_escritor}] Quiere escribir.")

    cola_fifo.acquire()              # Hace fila y se queda con el turno mientras espera
    rw_mutex.acquire()               # Espera a que terminen los lectores activos
    cola_fifo.release()              # Ya tiene la base de datos: deja avanzar la fila

    print(f"====> [ESCRITOR {id_escritor}] ESCRIBIENDO en la base de datos...")
    time.sleep(random.uniform(1.5, 2.5))
    base_de_datos = f"Dato actualizado por Escritor {id_escritor}"
    print(f"<==== [ESCRITOR {id_escritor}] Terminó de escribir. Nuevo dato: '{base_de_datos}'")

    rw_mutex.release()


if __name__ == "__main__":
    print("=== INICIO DE LA SIMULACIÓN DE LECTORES Y ESCRITORES ===")
    hilos = []

    for i in range(1, 4):
        t = threading.Thread(target=lector, args=(i,))
        hilos.append(t)
        t.start()
        time.sleep(0.1)              # Orden de llegada bien definido

    t_escritor1 = threading.Thread(target=escritor, args=(1,))
    hilos.append(t_escritor1)
    t_escritor1.start()
    time.sleep(0.1)

    for i in range(4, 7):
        t = threading.Thread(target=lector, args=(i,))
        hilos.append(t)
        t.start()
        time.sleep(0.1)

    for t in hilos:
        t.join()

    print("=== FIN DE LA SIMULACIÓN ===")