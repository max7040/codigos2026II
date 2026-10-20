import threading
import time
import random

NOMBRES = ["Tabaco", "Papel", "Fósforos"]
RONDAS = 6

semaforo_agente = threading.Semaphore(1)                          # Una sola ronda a la vez
semaforo_fumador = [threading.Semaphore(0) for _ in range(3)]     # Uno por fumador: el agente lo despierta

mesa = []                    # Dato compartido: ingredientes sobre la mesa
cigarrillos = [0, 0, 0]      # Dato compartido: cigarrillos fumados por cada fumador


def agente():
    global mesa

    for ronda in range(1, RONDAS + 1):
        semaforo_agente.acquire()                     # Espera a que la mesa esté libre

        ingredientes = random.sample([0, 1, 2], 2)    # Elige 2 ingredientes distintos
        mesa = [NOMBRES[i] for i in ingredientes]
        print(f"\n[AGENTE] Ronda {ronda}: pone {mesa[0]} y {mesa[1]} sobre la mesa.")

        faltante = 3 - sum(ingredientes)              # 0 + 1 + 2 = 3, lo que falta sale restando
        semaforo_fumador[faltante].release()          # Despierta solo al fumador que tiene el faltante

    semaforo_agente.acquire()                         # Espera a que el último fumador termine
    print("\n[AGENTE] Terminó todas sus rondas.")


def fumador(id_fumador):
    while True:
        semaforo_fumador[id_fumador].acquire()        # Duerme hasta que el agente lo despierte

        print(f"--> [FUMADOR {id_fumador}] (tiene {NOMBRES[id_fumador]}) toma {mesa} y arma su cigarrillo.")
        time.sleep(random.uniform(0.5, 1.0))
        cigarrillos[id_fumador] += 1
        print(f"<-- [FUMADOR {id_fumador}] Terminó de fumar.")

        semaforo_agente.release()                     # Avisa al agente: mesa libre


if __name__ == "__main__":
    print("=== INICIO DE LA SIMULACIÓN DE LOS FUMADORES ===")

    t_agente = threading.Thread(target=agente)
    t_agente.start()

    for i in range(3):
        t = threading.Thread(target=fumador, args=(i,), daemon=True)
        t.start()

    t_agente.join()

    print(f"Cigarrillos por fumador: {cigarrillos}")
    print("=== FIN DE LA SIMULACIÓN ===")