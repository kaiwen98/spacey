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


"""

from multiprocessing import Pool
import time
def myfunction(m):
    while(true):

        time.sleep(5)

        
if __name__ == '__main__':
    my_pool = Pool(processes=4) # start 4 worker processes
    result = my_pool.apply_async(myfunction, (10,)) # evaluate "f(10)" asynchronously in a single process
    print (result.get(timeout=1))

    print (my_pool.map(myfunction, range(10))) # prints "[0, 1, 4,..., 81]"
    my_it = my_pool.imap(myfunction, range(10))
    print (my_it.next() ) # prints "0"
    print (my_it.next() ) # prints "1"
    print (my_it.next(timeout=1) ) # prints "4" unless your computer is *very* slow
    result = my_pool.apply_async(time.sleep, (10,))
    print (result.get(timeout=1) ) # raises multiprocessing.TimeoutError
    q = ""
    while q != 'q':
       
        q = input("Press x to randomize")
        if q  == 'x':

                   
        elif q == 'q':

