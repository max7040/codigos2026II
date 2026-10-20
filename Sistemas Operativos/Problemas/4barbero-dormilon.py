import threading
import time
import random
from queue import Queue

SILLAS_ESPERA = 3
cola_clientes = Queue(maxsize=SILLAS_ESPERA)

barbero_listo = threading.Semaphore(0)
cliente_listo = threading.Semaphore(0)
mutex_sillas = threading.Lock()

def barbero():
    while True:
        print("Barbero durmiendo en su sillón...")
        cliente_listo.acquire() # Espera a que llegue un cliente
        
        with mutex_sillas:
            barbero_listo.release() # Indica que está listo para atender
        
        print("--> Barbero cortando el cabello...")
        time.sleep(0.4)
        print("Barbero terminó el corte.")

def cliente(id_c):
    time.sleep(random.uniform(0.1, 0.5))
    with mutex_sillas:
        if cola_clientes.qsize() < SILLAS_ESPERA:
            cola_clientes.put(id_c)
            print(f"Cliente {id_c} se sienta en la sala de espera. Sillas ocupadas: {cola_clientes.qsize()}")
            cliente_listo.release() # Despierta al barbero
            mutex_sillas.release()
            
            barbero_listo.acquire() # Espera su turno con el barbero
            print(f"Cliente {id_c} está siendo atendido.")
        else:
            print(f"x Cliente {id_c} se va porque la barbería está llena.")
            mutex_sillas.release()

if __name__ == "__main__":
    print("\n--- INICIO: BARBERO DORMILÓN ---")
    t_barbero = threading.Thread(target=barbero, daemon=True)
    t_barbero.start()

    clientes = [threading.Thread(target=cliente, args=(i,)) for i in range(6)]
    for c in clientes: c.start()
    for c in clientes: c.join()
    time.sleep(1)