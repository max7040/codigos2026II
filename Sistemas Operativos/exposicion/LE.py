import threading
import time
import random

base_de_datos = "Información Inicial"

mutex = threading.Semaphore(1)
rw_mutex = threading.Semaphore(1)


lectores_activos = 0


def lector(id_lector):
    global lectores_activos
    
    print(f"[LECTOR {id_lector}] Quiere leer.")
    
    
    mutex.acquire()
    lectores_activos += 1
    if lectores_activos == 1:
        
        rw_mutex.acquire()
    mutex.release()  
    
    
    print(f"--> [LECTOR {id_lector}] LEYENDO. Dato actual: '{base_de_datos}' (Lectores activos: {lectores_activos})")
    time.sleep(random.uniform(1, 2)) 
    print(f"<-- [LECTOR {id_lector}] Terminó de leer.")
    
    
    mutex.acquire()
    lectores_activos -= 1
    if lectores_activos == 0:
        
        rw_mutex.release()
    mutex.release()


def escritor(id_escritor):
    global base_de_datos
    
    print(f"[ESCRITOR {id_escritor}] Quiere escribir.")
    
    
    rw_mutex.acquire()
    
  
    print(f"====> [ESCRITOR {id_escritor}]  ESCRIBIENDO en la base de datos...")
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

    
    t_escritor1 = threading.Thread(target=escritor, args=(1,))
    hilos.append(t_escritor1)
    t_escritor1.start()


    for i in range(4, 7):
        t = threading.Thread(target=lector, args=(i,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    print("=== FIN DE LA SIMULACIÓN ===")