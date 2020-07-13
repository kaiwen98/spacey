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