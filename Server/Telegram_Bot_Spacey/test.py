
from datetime import datetime
import time
import config as cfg
from threading import Thread

midnight_flag = False

def shout():
    print("AAAAA")
    time.sleep(2)
class randomThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True:
            cfg.randomise_task()


def hourly_update():
    areas = cfg.database.client.smembers('registered_users')
    temp_locations_list = []
    for area in areas:
        part_locations_list = cfg.database.get_all_restaurant_from_user(area)
        temp_locations_list.append(part_locations_list)

    all_locations_list = []
    for sublist in temp_locations_list:
        for item in sublist:
            all_locations_list.append(item)

    localtime = time.localtime(time.time())
    date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
    time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
    timestamp = date+" "+time_now

    for area in areas:
        for location in all_locations_list:
            try:
                occupancy_data = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
                seats_taken = 0
                for seat in occupancy_data.values():
                    if seat == '1':
                        seats_taken += 1
                new_entry = {timestamp:seats_taken}
                cfg.database.client.hmset(area+'_'+location+'_totalvisitors',new_entry)    
            except:
                pass

def convToSec(timestamp):
    return int(timestamp.strftime("%H"))*60*60 + int(timestamp.strftime("%M"))*60 + int(timestamp.strftime("%S"))

def checkMidNight():
    global midnight_flag
    now = datetime.now()
    if (int(now.strftime("%H")) + int(now.strftime("%M"))) == 0:
        if midnight_flag is False: 
            midnight_flag = True
            return True
        else: return False
    else:
        midnight_flag = False
        return False
        
def task2():
    cfg.main()
    now = datetime.now()
    while(True):
        if(checkMidNight()):
            now = datetime.now()
        this = datetime.now()
        print(this.strftime("%H:%M:%S"))
        print(convToSec(this) - convToSec(now))
        if (convToSec(this) - convToSec(now) >= 5*60):
            hourly_update()
            now = datetime.now()
        time.sleep(10)

def main():
    worker = randomThread()
    worker.start()
    task2()