"""
import multiprocessing
import time

def calc_square(numbers, q):
    while(True):
        for n in numbers:
            q.put(n*n)
            time.sleep(0.2)

    q.put(-1)
    print('Exiting function')

if __name__ == '__main__':
    print('Now in the main code. Process name is:', __name__)
    numbers = [2, 3, 4, 5]
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=calc_square, args=(numbers, q))
    p.start()

    while True:
        nq = q.get()
        print('Message is:', nq)
        if nq == -1:
            break

    print('Done')
    p.join()
"""

import time
from multiprocessing import Process
 
class TestClass():
    def test_f(self):
        ctr = 0
        while True:
            ctr += 1
            print("     ", ctr)
            time.sleep(1.0)
 
if __name__ == '__main__':
    ## run function in the background
    CT=TestClass()
    p = Process(target=CT.test_f)
    p.start()

    ## will not exit if function finishes, only when
    ## "q" is entered, but this is just a simple example
    stop_char=""
    while stop_char.lower() != "q":
        stop_char=input("Enter 'q' to quit ")
        if stop_char.lower() == "u":
            print("lol")
    print("terminate process")
    if p.is_alive():
        p.terminate()