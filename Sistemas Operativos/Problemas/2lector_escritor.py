import threading
import time

class LectoresEscritoresJustos:
    def __init__(self):
        self.mutex = threading.Lock()
        self.rmutex = threading.Lock()
        self.e = threading.Lock()
        self.rcount = 0
        self.turn = threading.Lock() 

    def lector(self, id_l):
        with self.turn:
            pass 
        with self.rmutex:
            self.rcount += 1
            if self.rcount == 1:
                self.e.acquire() 
        
      
        print(f"[Lector {id_l}] Leyendo recurso...")
        time.sleep(0.2)
        
        with self.rmutex:
            self.rcount -= 1
            if self.rcount == 0:
                self.e.release() 

    def escritor(self, id_e):
        with self.turn:
            self.e.acquire() 
        

        print(f"=== [Escritor {id_e}] Escribiendo en el recurso... ===")
        time.sleep(0.3)
        
        self.e.release()


if __name__ == "__main__":
    print("\n--- INICIO: LECTORES - ESCRITORES ---")
    le = LectoresEscritoresJustos()
    hilos = [threading.Thread(target=le.lector, args=(i,)) for i in range(3)]
    hilos += [threading.Thread(target=le.escritor, args=(j,)) for j in range(2)]
    
    for h in hilos: h.start()
    for h in hilos: h.join()