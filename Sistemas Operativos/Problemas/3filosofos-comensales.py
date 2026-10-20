import threading
import time
import random

NUM_FILOSOFOS = 5
tenedores = [threading.Lock() for _ in range(NUM_FILOSOFOS)]

def filosofo(id_fil):
    izq = id_fil
    der = (id_fil + 1) % NUM_FILOSOFOS
    
  
    primer_tenedor = min(izq, der)
    segundo_tenedor = max(izq, der)

    for _ in range(3):
        print(f"Filósofo {id_fil} está pensando.")
        time.sleep(random.uniform(0.1, 0.3))

        print(f"Filósofo {id_fil} intenta comer.")
        with tenedores[primer_tenedor]:
            with tenedores[segundo_tenedor]:
              
                print(f"--> Filósofo {id_fil} está COMIENDO.")
                time.sleep(random.uniform(0.1, 0.3))
        
        print(f"Filósofo {id_fil} terminó de comer y libera tenedores.")

if __name__ == "__main__":
    print("\n--- INICIO: FILÓSOFOS COMENSALES ---")
    filos = [threading.Thread(target=filosofo, args=(i,)) for i in range(NUM_FILOSOFOS)]
    for f in filos: f.start()
    for f in filos: f.join()