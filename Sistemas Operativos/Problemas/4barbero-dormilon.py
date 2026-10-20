import threading
import time
import random
from collections import deque

SILLAS_ESPERA = 3
NUM_CLIENTES = 6

sala_espera = deque()    # Cola FIFO de la sala de espera: guarda (id_cliente, su_semaforo)

mutex = threading.Semaphore(1)               # Protege la sala de espera
clientes = threading.Semaphore(0)            # Cuenta los clientes esperando (despierta al barbero)
corte_terminado = threading.Semaphore(0)     # El barbero avisa que terminó el corte


def barbero():
    while True:
        # Si no hay clientes, el barbero se duerme (bloqueado, sin gastar CPU)
        if not clientes.acquire(blocking=False):
            print("[BARBERO] Sin clientes. Se duerme...")
            clientes.acquire()

        mutex.acquire()
        id_cliente, turno_cliente = sala_espera.popleft()   # Atiende al que lleva más tiempo esperando
        mutex.release()

        turno_cliente.release()                             # Llama a ese cliente a la silla
        print(f"--> [BARBERO] Cortando el cabello al cliente {id_cliente}...")
        time.sleep(random.uniform(1, 2))
        print(f"<-- [BARBERO] Terminó con el cliente {id_cliente}.")
        corte_terminado.release()


def cliente(id_cliente):
    time.sleep(random.uniform(0.1, 0.5))
    print(f"[CLIENTE {id_cliente}] Llega a la barbería.")

    mi_turno = threading.Semaphore(0)       # Semáforo propio: el barbero lo usa para llamarlo

    mutex.acquire()
    if len(sala_espera) < SILLAS_ESPERA:
        sala_espera.append((id_cliente, mi_turno))
        print(f"[CLIENTE {id_cliente}] Se sienta en la sala de espera (sillas ocupadas: {len(sala_espera)}/{SILLAS_ESPERA}).")
        clientes.release()                  # Despierta al barbero si dormía
        mutex.release()

        mi_turno.acquire()                  # Espera a que el barbero lo llame
        print(f"[CLIENTE {id_cliente}] Pasa a la silla del barbero.")
        corte_terminado.acquire()           # Espera a que termine el corte
        print(f"[CLIENTE {id_cliente}] Se va con su corte listo.")
    else:
        mutex.release()
        print(f"x [CLIENTE {id_cliente}] Sala LLENA. Se va sin corte.")


if __name__ == "__main__":
    print("=== INICIO DE LA SIMULACIÓN DEL BARBERO DORMILÓN ===")

    t_barbero = threading.Thread(target=barbero, daemon=True)
    t_barbero.start()

    hilos = []
    for i in range(1, NUM_CLIENTES + 1):
        t = threading.Thread(target=cliente, args=(i,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    print("=== FIN DE LA SIMULACIÓN ===")