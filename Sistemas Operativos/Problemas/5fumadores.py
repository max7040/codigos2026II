import threading
import time
import random

# Ingredientes: 0=Tabaco, 1=Papel, 2=Fósforos
semaforo_agente = threading.Semaphore(1)
fumador_semaforos = [threading.Semaphore(0) for _ in range(3)]
ingredientes_mesa = []
mutex = threading.Lock()

def agente():
    for _ in range(5):
        semaforo_agente.acquire()
        ingredientes = random.sample([0, 1, 2], 2)
        print(f"\n[Agente] Pone sobre la mesa los ingredientes: {ingredientes}")
        
        # Desbloquea al fumador que tiene el ingrediente faltante
        faltante = 3 - sum(ingredientes) # Truco matemático para hallar el faltante (0+1=1 -> falta 2; etc.)
        fumador_semaforos[faltante].release()

def fumador(id_f):
    while True:
        fumador_semaforos[id_f].acquire()
        # --- SECCIÓN CRÍTICA ---
        print(f"--> [Fumador {id_f}] Tiene su ingrediente, arma el cigarrillo y fuma.")
        time.sleep(0.3)
        print(f"[Fumador {id_f}] Terminó de fumar.")
        semaforo_agente.release() # Pide al agente nuevos ingredientes
        time.sleep(0.2)

if __name__ == "__main__":
    print("\n--- INICIO: PROBLEMA DE LOS FUMADORES ---")
    t_agente = threading.Thread(target=agente, daemon=True)
    t_agente.start()

    fumadores = [threading.Thread(target=fumador, args=(i,), daemon=True) for i in range(3)]
    for f in fumadores: f.start()
    
    time.sleep(3) # Dejar correr la simulación por unos segundos