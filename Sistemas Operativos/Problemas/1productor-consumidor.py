import threading
import time
import random
from collections import deque

BUFFER_SIZE = 5
buffer = deque()
mutex = threading.Lock()
not_empty = threading.Condition(mutex)
not_full = threading.Condition(mutex)

def productor(id_prod):
    for i in range(5):
        item = random.randint(1, 100)
        with not_full:
            while len(buffer) == BUFFER_SIZE:
                not_full.wait() 
            buffer.append(item)
            print(f"[Productor {id_prod}] Produjo {item} | Buffer: {list(buffer)}")
            not_empty.notify() 
        time.sleep(random.uniform(0.1, 0.5))

def consumidor(id_cons):
    for i in range(5):
        with not_empty:
            while len(buffer) == 0:
                not_empty.wait()
            item = buffer.popleft() 
            print(f"--> [Consumidor {id_cons}] Consumió {item} | Buffer: {list(buffer)}")
            not_full.notify()
        time.sleep(random.uniform(0.2, 0.6))


if __name__ == "__main__":
    print("--- INICIO: PRODUCTOR - CONSUMIDOR ---")
    p = threading.Thread(target=productor, args=(1,))
    c = threading.Thread(target=consumidor, args=(1,))
    p.start(); c.start()
    p.join(); c.join()