import threading
import time
import random

NUM_FILOSOFOS = 5
RONDAS = 3

tenedores = [threading.Semaphore(1) for _ in range(NUM_FILOSOFOS)]   # Un semáforo por tenedor
comidas = [0] * NUM_FILOSOFOS                                        # Dato compartido: veces que comió cada uno


def filosofo(id_filosofo):
    izq = id_filosofo
    der = (id_filosofo + 1) % NUM_FILOSOFOS

    # Jerarquía de recursos: siempre se pide primero el tenedor de menor número
    primero = min(izq, der)
    segundo = max(izq, der)

    for _ in range(RONDAS):
        print(f"[FILÓSOFO {id_filosofo}] Pensando.")
        time.sleep(random.uniform(0.2, 0.6))

        print(f"[FILÓSOFO {id_filosofo}] Tiene hambre. Pide tenedor {primero} y luego tenedor {segundo}.")
        tenedores[primero].acquire()
        tenedores[segundo].acquire()

        print(f"--> [FILÓSOFO {id_filosofo}] COMIENDO con tenedores {primero} y {segundo}.")
        time.sleep(random.uniform(0.3, 0.8))
        comidas[id_filosofo] += 1
        print(f"<-- [FILÓSOFO {id_filosofo}] Terminó de comer.")

        tenedores[segundo].release()
        tenedores[primero].release()


if __name__ == "__main__":
    print("=== INICIO DE LA SIMULACIÓN DE LOS FILÓSOFOS COMENSALES ===")
    hilos = []

    for i in range(NUM_FILOSOFOS):
        t = threading.Thread(target=filosofo, args=(i,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    print(f"Comidas por filósofo: {comidas}")
    print("=== FIN DE LA SIMULACIÓN (sin interbloqueo) ===")