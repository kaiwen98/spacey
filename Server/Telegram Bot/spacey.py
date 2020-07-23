from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request
import matplotlib.pyplot as plt
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import time
import datetime 
import csv
import json

import config as cfg
from imagegen import *
import os
from os.path import dirname as dir, splitext, basename, join
import sys
import base64
import res_info as res
from multiprocessing import Process, Pipe, Lock
import random
import time
import redis

bot = telegram.Bot(TOKEN)

# _root = dir(dir(__file__)) 

# # To extract database interface functions
# sys.path.append(join(_root, "Redis"))
# import redisDB
# # Relevant file directories

# # Image Assets
# image_folder = os.path.join(_root, "images")
# image_asset_folder = os.path.join(image_folder, "assets")
# image_output_graphic_folder = os.path.join(image_folder, "output graphic")
# nodeOn_path = os.path.join(image_asset_folder,"unoccupied_nodes.png")
# nodeOff_path = os.path.join(image_asset_folder, "occupied_nodes.png")


# # Database information

# remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
# password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'
# port = '13969'

# available_restaurants_name = None
# nodeOn = None
# nodeOff = None
# restaurants = None
# cfg.database = redisDB.redis_database(_root, cfg.remote_host, cfg.port, cfg.password)
# interrupt = ""

# class ResServer(object):
#     def __init__(self, userID):

        
#         print(cfg.database.client.keys())
#         self.userID = userID
#         self.available_restaurants_name = cfg.database.get_all_restaurant_from_user(userID)
#         self.restaurants = {}
#         self.remote_host = 'redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com'
#         self.port = '13969'
#         self.password = 'PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL'

#         for i in self.available_restaurants_name:
#             occupancy = {}
#             coord = {}

#             full_name = self.userID + "_" + i
#             full_name_occupancy = full_name + "_occupancy"
#             full_name_coord = full_name + "_coord"
#             occupancy = cfg.database.client.hgetall(full_name_occupancy)
#             coord = cfg.database.client.hgetall(full_name_coord)
#             cfg.json_deserialize_image(coord["processed_img"], cfg.get_output_graphic_path(full_name))
#             self.box_len = int(coord["box_len"])
#             del coord["processed_img"]
#             del coord["box_len"]
#             self.restaurants[full_name] = res.restaurant_info(full_name, occupancy, coord, cfg.get_output_graphic_path(full_name)
#             # self.restaurants.append(res.restaurant_info(full_name, occupancy, coord, cfg.get_output_graphic_path(full_name), self.box_len))
            
#     def scan_update(self):
#         """
#         print(self.userID)
#         """
#         global mutex
#         client = redis.Redis(host=self.remote_host, port=self.port,
#                              db=0, password=self.password, decode_responses=True)
#         while(True):
            
#             for i in range(len(self.available_restaurants_name)):
#                 if(r.empty() is False and r.get() == '1'):
#                     self.randomize()

#                 print("checking...", self.available_restaurants_name[i])

#                 occupancy = {}
#                 full_name = self.userID + "_" + \
#                     self.available_restaurants_name[i]
#                 full_name_occupancy = full_name + "_occupancy"

#                 # occupancy = cfg.database.client.hgetall(full_name_occupancy)
#                 occupancy = client.hgetall(full_name_occupancy)
#                 if self.restaurants[i].occupancy != occupancy:
#                     imageupdate(self.restaurants[i], occupancy)
#                 # You can change update frequency from here. The scan is asynchronous
                
#                 time.sleep(15)
            
        
        
 




logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # logger.info("User {user} sent {message}".format(user=update.message.from_user.username, message=update.message.text))

LOCATION, CHECKWHAT, SUBSCRIBE_MAIN, SUBSCRIBE_TYPE, SUBSCRIBE_LOCATION, UNSUBSCRIBE_TYPE= range(6)
red_alert = "\ud83d\udd34"
yellow_alert = "\ud83d\udfe1"
green_alert = "\ud83d\udfe2"
seats_emoji = "\ud83e\ude91"

def start(update, context):
    # chat_type = update.message.chat.type
    name = update.message.from_user.first_name
    username = update.message.from_user.username
    user_id = str(update.message.from_user.id)
    date = datetime.datetime.now()
    #Store user data in csv
    with open("C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\users_info.csv") as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ",") 
        results = []
        user_id_list = []
        for i in spamreader:
            results.append(i)
            user_id_list.append(i[2])
    if user_id not in user_id_list:
        results.append([name,username,user_id,date,0,0,0])
        with open("C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\users_info.csv", 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter = ",") 
            for i in results:
                spamwriter.writerow(i)

    #Store user data in database
    users_info = cfg.database.client.hgetall('users_info')
    if user_id not in users_info.keys():
        dict_object = {"name": name, "username": username, "daily_notifications": "0", "full_notifications": "0", "flag":"0"}
        stringified_dict_obj = json.dumps(dict_object) 
        new_entry = {user_id:stringified_dict_obj}
        cfg.database.client.hmset('users_info',new_entry)

    context.bot.send_message(user_id,text='Hi '+name+', Welcome to <b>Spacey Telegram Bot</b>!\n<u><i>Please read the following before continuing</i></u>.\n\n'
                                            '/menu to start checking details of a location.\n'
                                            '-<b>Occupancy.</b> Gives current seat occupancy of the given location.\n'
                                            '-<b>Operation Hours.</b> Gives the opening hours of the given location.\n'
                                            '-<b>How to go.</b> Gives the address and map of the given location.\n\n'
                                            '/notifications to subscribe to notifications.\n'
                                            '-<b>Daily notifications.</b> Sends daily updates at 12pm of your chosen location.\n'
                                            '-<b>>80% notifications.</b> Sends updates of your chosen location whenever it is reaching its full capacity.\n'
                                            '-<i>Note: seat occupancies are updated through sensors. However, for simulation purposes, use /setspaceylow, /setspaceymid and /setspaceyhigh to manipulate the occupancy of <u>Spacey cafe</u> to 20%, 60% and above 80% respectively!</i>\n', parse_mode = 'HTML')

def menu(update,context):
    locations_list = cfg.database.get_all_restaurant_from_user('NUS')
    keyboard=[]
    for location in locations_list:
        keyboard.append([InlineKeyboardButton(location, callback_data=location)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Which location would you like to check?', reply_markup=reply_markup)
    return LOCATION

def getcsv():
    with open("C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\locations.csv") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter = ",")
        results = {}
        for i in spamreader:
            location = i.pop('Location')
            results[location] = dict(i)
        return results

def get_locations():
    with open("C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\locations.csv") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter = ",")
        locations = []
        for i in spamreader:
            location = i.pop('Location')
            locations.append(location)
        return locations

def check_location(update, context):
    query = update.callback_query
    location = query.data
    query.edit_message_text(text="Selected location: {}".format(location))
    context.user_data['location'] = location
    keyboard=[[InlineKeyboardButton("Occupancy", callback_data='Occupancy')],
            [InlineKeyboardButton("Operation Hours", callback_data='Operation Hours')],
            [InlineKeyboardButton("How to go", callback_data='How to go')],
            [InlineKeyboardButton("Back", callback_data='Back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="What would you like to know about " + query.data +"?", reply_markup=reply_markup)
    return CHECKWHAT

def check_what(update, context):
    query = update.callback_query
    option = query.data
    query.edit_message_text(text="Selected option: {}".format(option))
    user_id = query.from_user.id
    location = context.user_data['location']
    location_data = getcsv()
    if option == 'Occupancy':
        localtime = time.localtime(time.time())
        date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
        time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
        seats_available = 0
        seats_taken = 0
        occupancy_data = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
        for seat in occupancy_data.values():
            if seat == '0':
                seats_available += 1
            else:
                seats_taken += 1
        seats_total = seats_available + seats_taken
        seats_occupancy = round(seats_taken/seats_total*100, 2)

        #Generate PIE CHART
        labels = ['Occupied','Free']
        colors = ['#66b3ff','#808080'] #light red '#ff9999'and green'#99ff99'
        sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]
        explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Free')

        fig1, ax1 = plt.subplots()
        centre_circle = plt.Circle((0,0),0.75,color='white', fc='white', linewidth=0.5)
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', pctdistance=0.85,
                shadow=False, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
        plt.savefig('C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\chart_'+str(location)+'.png')
        
        #Generate FLOORPLAN
        config_obj = cfg.ResServer('NUS')
        restaurants_data = config_obj.get_info()
        for loc_data, obj_data in restaurants_data.items():
            if location == loc_data:
                occupancy = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
                imageupdate(obj_data, occupancy)
                imagegen(obj_data)
        context.bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Desktop\lol\spacey\Server\images\output graphic\output_NUS_'+location+'.png', 'rb'))

        if seats_occupancy < 50:
            alert = green_alert
        elif seats_occupancy >=80:
            alert = red_alert
        else:
            alert = yellow_alert 
        context.bot.send_message(user_id, text=seats_emoji+"<b> Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%) "+ alert,parse_mode='HTML')
        context.bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\chart_'+str(location)+'.png', 'rb'))
    
        keyboard=[[InlineKeyboardButton("Operation Hours", callback_data='Operation Hours'),
            InlineKeyboardButton("How to go", callback_data='How to go')],
            [InlineKeyboardButton("End", callback_data='End')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Anything else regarding " + location +" that you would like to know about?", reply_markup=reply_markup)
        return CHECKWHAT
    
    elif option == 'Operation Hours':
        try:
            context.bot.send_message(user_id, text=location_data[location]["Operation Hours"])
        except:
            context.bot.send_message(user_id, text='No data found!')

        keyboard=[[InlineKeyboardButton("Occupancy", callback_data='Occupancy')],
            [InlineKeyboardButton("How to go", callback_data='How to go')],
            [InlineKeyboardButton("End", callback_data='End')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Anything else regarding " + location +" that you would like to know about?", reply_markup=reply_markup)
        return CHECKWHAT

    elif option == 'How to go':
        try:
            latitude = location_data[location]['Latitude']
            longitude = location_data[location]['Longitude']
            address = location_data[location]['Address']
            context.bot.send_venue(user_id, latitude=latitude, longitude=longitude, title=location, address=address)
        except:
            context.bot.send_message(user_id, text='No data found!')

        keyboard=[[InlineKeyboardButton("Occupancy", callback_data='Occupancy')],
            [InlineKeyboardButton("Operation Hours", callback_data='Operation Hours')],
            [InlineKeyboardButton("End", callback_data='End')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Anything else regarding " + location +" that you would like to know about?", reply_markup=reply_markup)
        return CHECKWHAT

    elif option == 'Back':
        locations_list = cfg.database.get_all_restaurant_from_user('NUS')
        keyboard=[]
        for location in locations_list:
            keyboard.append([InlineKeyboardButton(location, callback_data=location)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, 'Which location would you like to check?', reply_markup=reply_markup)
        return LOCATION

    elif option == 'End':
        context.bot.send_message(user_id,"Have a good day! \ud83d\ude0a")
        return ConversationHandler.END
    


def test(update, context):
    chatid = update.message.from_user.id
    grpid = update.message.chat.id

    # cfg.main()
    obj = cfg.ResServer('NUS')
    y = obj.get_info()
    # # client = redis.Redis(host = self.remote_host, port = self.port, db = 0, password = self.password, decode_responses= True)
    # # occupancy = cfg.database.client.hgetall('NUS_Spacey Cafe_occupancy')
    # # locations = cfg.database.get_all_restaurant_from_user('NUS')
    # # users_info = cfg.database.client.hgetall('users_info')
    
    for location,obj in y.items():
        occupancy = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
        count = 0
        for seat_num, status in occupancy.items():
            if count < len(occupancy)*0.85:
                occupancy[seat_num] = '1'
                count += 1
            else:
                occupancy[seat_num] = '0'

        cfg.database.client.hmset('NUS_'+location+'_occupancy', occupancy)    
        imageupdate(obj, occupancy)
        imagegen(obj)
    # context.bot.send_message(chat_id='36927293', text=)
    # occupancy = cfg.database.client.hgetall('NUS_Spacey cafe_occupancy')
    # context.bot.send_message(chat_id=chatid, text=y)
    # for i in cfg.database.client.keys():
    #     context.bot.send_message(chat_id=chatid, text=i)
    
    #results = getcsv()
    context.bot.send_photo(chatid, photo=open('C:\\Users\chuanan\Desktop\lol\spacey\Server\images\output graphic\output_NUS_Deck.png', 'rb'))
    # context.bot.send_photo('C:\Users\chuanan\Desktop\lol\spacey\Server\images\output graphic')
    #chat_type = update.message.chat.type
    
    #bot.send_message(772520752, "<b>SUCK MY KUKUJIAO</b>",parse_mode='HTML')
    # keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
    #          InlineKeyboardButton("Option 2", callback_data='2')],
    #       [InlineKeyboardButton("Option 3", callback_data='3')]]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)
def notifications(update, context):
    user_id = str(update.message.from_user.id)

    #Use CSV to manage notifications
    # with open("C:\\Users\chuanan\Downloads\spacey-linux-windows\spacey-linux-windows\Server\Telegram Bot\\users_info.csv") as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter = ",") 
    #     results = []
    #     for i in spamreader:
    #         results.append(i)
    
    # for i in results:
    #     if user_id in i: 
    #         if i[4]=='0' and i[5]=='0': #not subscribed to any notifications
    #             keyboard=[[InlineKeyboardButton('Yes', callback_data='Subscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
    #             reply_markup = InlineKeyboardMarkup(keyboard)
    #             context.bot.send_message(user_id, text='You have not subscribed to notifications. Do you want to subscribe?',reply_markup=reply_markup)
                
    #         elif i[4]!='0' and i[5]=='0': #subscribed to daily only
    #             keyboard=[[InlineKeyboardButton('Subscribe to notifications whenever occupancy >80%', callback_data='Subscribe>80%')],
    #                         [InlineKeyboardButton('Unsubscribe from daily notifications', callback_data='Unsubscribedaily')],
    #                         [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
    #             reply_markup = InlineKeyboardMarkup(keyboard)
    #             context.bot.send_message(user_id, text='You are currently subscribed to daily notifications (<b>'+ str(i[4]) + '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
    #         elif i[4]=='0' and i[5]!='0':     #subscribed to >80% only
    #             keyboard=[[InlineKeyboardButton('Subscribe to daily notifications ', callback_data='Subscribedaily')],
    #                         [InlineKeyboardButton('Unsubscribe from >80% notifications', callback_data='Unsubscribe>80%')],
    #                         [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
    #             reply_markup = InlineKeyboardMarkup(keyboard)
    #             context.bot.send_message(user_id, text='You are currently subscribed to >80% notifications (<b>' +str(i[5])+ '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
    #         elif i[4]!='0' and i[5]!='0': #subscribed to both
    #             keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
    #             reply_markup = InlineKeyboardMarkup(keyboard)
    #             context.bot.send_message(user_id, text='You have subscribed to daily notifications (<b>'+ str(i[4]) + '</b>) and >80% notifications (<b>'+str(i[5])+ '</b>). Would you like to unsubscribe?',reply_markup=reply_markup, parse_mode='HTML')
        
    # return SUBSCRIBE_MAIN

    #Use database to manage notifications
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        if id_number == user_id:
            data = json.loads(data)
            if str(data['daily_notifications']) == '0' and str(data['full_notifications']) == '0': #not subscribed to any notifications
                keyboard=[[InlineKeyboardButton('Yes', callback_data='Subscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You have not subscribed to notifications. Do you want to subscribe?',reply_markup=reply_markup)
            
            elif str(data['daily_notifications']) != '0' and str(data['full_notifications']) == '0': #subscribed to daily only
                keyboard=[[InlineKeyboardButton('Subscribe to notifications whenever occupancy >80%', callback_data='Subscribe>80%')],
                            [InlineKeyboardButton('Unsubscribe from daily notifications', callback_data='Unsubscribedaily')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You are currently subscribed to daily notifications (<b>'+ str(data['daily_notifications']) + '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif str(data['daily_notifications']) == '0' and str(data['full_notifications']) != '0':     #subscribed to >80% only
                keyboard=[[InlineKeyboardButton('Subscribe to daily notifications ', callback_data='Subscribedaily')],
                            [InlineKeyboardButton('Unsubscribe from >80% notifications', callback_data='Unsubscribe>80%')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You are currently subscribed to >80% notifications (<b>' +str(data['full_notifications'])+ '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif str(data['daily_notifications']) != '0' and str(data['full_notifications']) != '0': #subscribed to both
                keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You have subscribed to daily notifications (<b>'+ str(data['daily_notifications']) + '</b>) and >80% notifications (<b>'+str(data['full_notifications'])+ '</b>). Would you like to unsubscribe?',reply_markup=reply_markup, parse_mode='HTML')
        
    return SUBSCRIBE_MAIN        

def subscribe_main(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    
    if query.data == 'Subscribe':
        keyboard=[[InlineKeyboardButton('Daily Notifications', callback_data='Subscribedaily')],
                    [InlineKeyboardButton('>80% Notifications', callback_data='Subscribe>80%')],
                    [InlineKeyboardButton('Both', callback_data='SubscribeBoth')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(user_id, text="Which notification would you like to subscribe to?", reply_markup=reply_markup)
        return SUBSCRIBE_TYPE

    elif query.data == 'Unsubscribe':
        keyboard=[[InlineKeyboardButton('Daily Notifications', callback_data='Unsubscribedaily')],
                    [InlineKeyboardButton('>80% Notifications', callback_data='Unsubscribe>80%')],
                    [InlineKeyboardButton('Both', callback_data='UnsubscribeBoth')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(user_id, text="Which notification would you like to unsubscribe from?", reply_markup=reply_markup)
        return UNSUBSCRIBE_TYPE

    elif query.data == 'Unsubscribedaily':
        keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribedaily')],
                    [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(user_id, text="Are you sure to unsubscribe from daily notifications?", reply_markup=reply_markup)
        return UNSUBSCRIBE_TYPE

    elif query.data == 'Unsubscribe>80%':
        keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribe>80%')],
                    [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(user_id, text="Are you sure to unsubscribe from >80% notifications?", reply_markup=reply_markup)
        return UNSUBSCRIBE_TYPE

    elif query.data == 'Cancel':
        context.bot.send_message(user_id, text="No changes were made!")
        return ConversationHandler.END 

    else: #query.data == 'Subscribe>80%', 'Subscribedaily'
        context.user_data['subscribe_type'] = query.data
        locations_list = cfg.database.get_all_restaurant_from_user('NUS')
        keyboard=[]
        for location in locations_list:
            keyboard.append([InlineKeyboardButton(location, callback_data=location)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)
        return SUBSCRIBE_LOCATION
    
def subscribe_type(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    context.user_data['subscribe_type'] = query.data

    locations_list = cfg.database.get_all_restaurant_from_user('NUS')
    keyboard=[]
    for location in locations_list:
        keyboard.append([InlineKeyboardButton(location, callback_data=location)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)
    return SUBSCRIBE_LOCATION

def subscribe_location(update,context):
    query = update.callback_query
    user_id = str(query.from_user.id)
    query.edit_message_text(text="Selected option: {}".format(query.data))
    
    #Using CSV
    # with open("C:\\Users\chuanan\Downloads\spacey-linux-windows\spacey-linux-windows\Server\Telegram Bot\\users_info.csv") as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter = ",") 
    #     users_info_list = []
    #     for i in spamreader:
    #         users_info_list.append(i)
    
    # for i in users_info_list:
    #     if str(user_id) in i:
    #         if context.user_data['subscribe_type'] == 'Subscribedaily':
    #             i[4] = query.data
    #             notification_type =  'Daily notifications'
    #         elif context.user_data['subscribe_type'] == 'Subscribe>80%':
    #             i[5] = query.data
    #             notification_type =  '>80% notifications'
    #         elif context.user_data['subscribe_type'] == 'SubscribeBoth':
    #             i[4] = query.data
    #             i[5] = query.data
    #             notification_type =  'Both notifications'
    
    # with open("C:\\Users\chuanan\Downloads\spacey-linux-windows\spacey-linux-windows\Server\Telegram Bot\\users_info.csv", 'w', newline='') as csvfile:
    #     spamwriter = csv.writer(csvfile, delimiter = ",") 
    #     for i in users_info_list:
    #         spamwriter.writerow(i)

    # context.bot.send_message(user_id, notification_type + ' for <b>' +query.data+ '</b> set!',parse_mode='HTML')
    # context.bot.answer_callback_query(callback_query_id=query.id, text="You have subscribed to notiffications! \nTo unsubscribe, use /notifications command again.", show_alert=True)
    # return ConversationHandler.END

#Using database
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        if id_number == user_id:
            data = json.loads(data)
            if context.user_data['subscribe_type'] == 'Subscribedaily':
                data['daily_notifications'] = query.data
                notification_type =  'Daily notifications'
            elif context.user_data['subscribe_type'] == 'Subscribe>80%':
                data['full_notifications'] = query.data
                notification_type =  '>80% notifications'
            elif context.user_data['subscribe_type'] == 'SubscribeBoth':
                data['daily_notifications'] = query.data
                data['daily_notifications'] = query.data
                notification_type =  'Both notifications'
            data = json.dumps(data)
            new_entry = {id_number:data}
            cfg.database.client.hmset('users_info',new_entry)

    context.bot.send_message(user_id, notification_type + ' for <b>' +query.data+ '</b> set!',parse_mode='HTML')
    context.bot.answer_callback_query(callback_query_id=query.id, text="You have subscribed to notiffications! \nTo unsubscribe, use /notifications command again.", show_alert=True)
    return ConversationHandler.END

def unsubscribe_type(update,context):
    query = update.callback_query
    user_id = str(query.from_user.id)
    query.edit_message_text(text="Selected option: {}".format(query.data))
    
    #Using CSV
    # with open("C:\\Users\chuanan\Downloads\spacey-linux-windows\spacey-linux-windows\Server\Telegram Bot\\users_info.csv") as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter = ",") 
    #     users_info_list = []
    #     for i in spamreader:
    #         users_info_list.append(i)
    
    # for i in users_info_list:
    #     if str(user_id) in i:
    #         if query.data == 'Unsubscribedaily':
    #             location_removed = i[4]
    #             i[4] = 0
    #             notification_type =  'Daily notifications'
                
    #         elif query.data == 'Unsubscribe>80%':
    #             location_removed = i[5]
    #             i[5] = 0
    #             notification_type =  '>80% notifications'
                
    #         elif query.data == 'UnsubscribeBoth':
    #             location1_removed = str(i[4])
    #             location2_removed = str(i[5])
    #             i[4] = 0
    #             i[5] = 0
    #             notification_type =  'Both notifications'
                

    #         elif query.data == 'Cancel':
    #             context.bot.send_message(user_id, 'No changes were made!')
    #             return ConversationHandler.END

    # with open("C:\\Users\chuanan\Downloads\spacey-linux-windows\spacey-linux-windows\Server\Telegram Bot\\users_info.csv", 'w', newline='') as csvfile:
    #     spamwriter = csv.writer(csvfile, delimiter = ",") 
    #     for i in users_info_list:
    #         spamwriter.writerow(i)

    # if notification_type == 'Both notifications':
    #     if location1_removed == location2_removed:
    #         context.bot.send_message(user_id, notification_type+' for <b>'+location1_removed+ '</b> removed!',parse_mode='HTML')
    #     else:
    #         context.bot.send_message(user_id, notification_type+' for <b>'+location1_removed+'</b> and <b>'+ location2_removed + '</b> removed!',parse_mode='HTML')
    # else: 
    #     context.bot.send_message(user_id, notification_type + ' for <b>' +location_removed+ '</b> removed!',parse_mode='HTML')
    
    # return ConversationHandler.END

    #Using database
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        if id_number == user_id:
            data = json.loads(data)
            if query.data == 'Unsubscribedaily':
                location_removed = data['daily_notifications']
                data['daily_notifications'] = 0
                notification_type =  'Daily notifications'
                
            elif query.data == 'Unsubscribe>80%':
                location_removed = data['full_notifications']
                data['full_notifications'] = 0
                notification_type =  '>80% notifications'
                
            elif query.data == 'UnsubscribeBoth':
                location1_removed = data['daily_notifications']
                location2_removed = data['full_notifications']
                data['daily_notifications'] = 0
                data['full_notifications'] = 0
                notification_type =  'Both notifications'
                
            elif query.data == 'Cancel':
                context.bot.send_message(user_id, 'No changes were made!')
                return ConversationHandler.END

            data = json.dumps(data)
            new_entry = {id_number:data}
            cfg.database.client.hmset('users_info',new_entry)

    if notification_type == 'Both notifications':
        if location1_removed == location2_removed:
            context.bot.send_message(user_id, notification_type+' for <b>'+location1_removed+ '</b> removed!',parse_mode='HTML')
        else:
            context.bot.send_message(user_id, notification_type+' for <b>'+location1_removed+'</b> and <b>'+ location2_removed + '</b> removed!',parse_mode='HTML')
    else: 
        context.bot.send_message(user_id, notification_type + ' for <b>' +location_removed+ '</b> removed!',parse_mode='HTML')
    return ConversationHandler.END

def daily_notifications(context):
    # location_data = getcsv()
    # locations_list = cfg.database.get_all_restaurant_from_user('NUS')      
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        data = json.loads(data)
        if str(data['daily_notifications']) != '0': #daily notification on, send notification
            name = data['name']
            user_id = id_number
            location = data['daily_notifications']
            localtime = time.localtime(time.time())
            date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
            time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
            for seat in occupancy_data.values():
                if seat == '0':
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = seats_available + seats_taken
            seats_occupancy = round(seats_taken/seats_total*100, 2)
            labels = ['Occupied','Free']
            colors = ['Red','Green']
            sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]
            explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Free')

            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
            plt.savefig('C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\chart_'+str(location)+'.png')
            
            if seats_occupancy < 50:
                alert = green_alert
            elif seats_occupancy >=80:
                alert = red_alert
            else:
                alert = yellow_alert 
            context.bot.send_message(user_id, text="Hey "+ name +"! Here is your daily notification for <b><u>"+location+"</u></b>!\n\n"+seats_emoji+"<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)"+alert, parse_mode='HTML')
            context.bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\chart_'+str(location)+'.png', 'rb'))
    

def full_notifications(context):
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        data = json.loads(data)
        if str(data['full_notifications']) != '0' and str(data['flag']) == '0': #>80% notifications on and flag off. ie send notification
            name = data['name']
            user_id = id_number
            location = data['full_notifications']
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
            for seat in occupancy_data.values():
                if seat == '0':
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = seats_available + seats_taken
            seats_occupancy = round(seats_taken/seats_total*100, 2)
            if seats_occupancy >= 80:
                localtime = time.localtime(time.time())
                date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
                time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
                labels = ['Occupied','Free']
                colors = ['Red','Green']
                sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]
                explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Free')

                fig1, ax1 = plt.subplots()
                ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                        shadow=True, startangle=90)
                ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
                plt.savefig('C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\chart_'+str(location)+'.png')
                
                context.bot.send_message(user_id, text="Hey "+ name +"! Occupancy for <b><u>"+location+"</u></b> has reached >=80%!\n\n"+seats_emoji+"<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)"+red_alert,parse_mode='HTML')
                context.bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Desktop\lol\spacey\Server\Telegram Bot\\chart_'+str(location)+'.png', 'rb'))    
                data['flag'] = '1'
                data = json.dumps(data)
                new_entry = {id_number:data}
                cfg.database.client.hmset('users_info',new_entry)

        elif str(data['full_notifications']) != '0' and str(data['flag']) == '1': # >80% notifications on and flag is on
            location = data['full_notifications']
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
            for seat in occupancy_data.values():
                if seat == '0':
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = seats_available + seats_taken
            seats_occupancy = round(seats_taken/seats_total*100, 2)
            if seats_occupancy < 80:
                data['flag'] = '0'
                data = json.dumps(data)
                new_entry = {id_number:data}
                cfg.database.client.hmset('users_info',new_entry)

def setspaceyhigh(update,context):
    user_id = update.message.from_user.id
    occupancy_data = cfg.database.client.hgetall('NUS_Spacey Cafe_occupancy')
    count = 0
    for seat_num, status in occupancy_data.items():
        if count < len(occupancy_data)*0.85:
            occupancy_data[seat_num] = '1'
            count += 1
        else:
            occupancy_data[seat_num] = '0'

    cfg.database.client.hmset('NUS_Spacey Cafe_occupancy', occupancy_data)    
    context.bot.send_message(user_id, 'Occupancy for Spacey Cafe set to above 80%!')
    context.bot.send_message(user_id, occupancy_data)

def setspaceymid(update,context):
    user_id = update.message.from_user.id
    occupancy_data = cfg.database.client.hgetall('NUS_Spacey Cafe_occupancy')
    count = 0

    for seat_num, status in occupancy_data.items():
        if count < len(occupancy_data)*0.6:
            occupancy_data[seat_num] = '1'
            count += 1
        else:
            occupancy_data[seat_num] = '0'

    cfg.database.client.hmset('NUS_Spacey Cafe_occupancy', occupancy_data)    
    context.bot.send_message(user_id, 'Occupancy for Spacey Cafe set to around 60%!')
    context.bot.send_message(user_id, occupancy_data)

def setspaceylow(update,context):
    user_id = update.message.from_user.id
    occupancy_data = cfg.database.client.hgetall('NUS_Spacey Cafe_occupancy')
    count = 0

    for seat_num, status in occupancy_data.items():
        if count < len(occupancy_data)*0.2:
            occupancy_data[seat_num] = '1'
            count += 1
        else:
            occupancy_data[seat_num] = '0'

    cfg.database.client.hmset('NUS_Spacey Cafe_occupancy', occupancy_data)    
    context.bot.send_message(user_id, 'Occupancy for Spacey Cafe set to around 20%!')
    context.bot.send_message(user_id, occupancy_data)


# def update_seats(context):
#     with open("C:\\Users\chuanan\Downloads\spacey-linux-windows\spacey-linux-windows\Server\Telegram Bot\\locations.csv") as csvfile:
#         spamreader = csv.DictReader(csvfile, delimiter = ",")
#         results = []
#         for i in spamreader:
#             results.append(dict(i))
#     csv_columns = list(results[0].keys())
#     location_data = getcsv()
   
    
#     for i in results:
#         location = i["Location"]
#         try:
#             with open("C:\\Users\chuanan\Documents\grambots\spacey\\seats_"+ location +".json") as f:
#                 seats_data = json.load(f)
#             seats_available = 0
#             seats_taken = 0
#             for seats in seats_data.values():
#                 if seats == 0:
#                     seats_available += 1
#                 else:
#                     seats_taken += 1
#             seats_total = len(seats_data)
#             i['Seats Available'] = seats_available
#             i['Seats Taken'] = seats_taken
#             i['Seats Total'] = seats_total
#             # context.bot.send_message(772520752, text=seats_available)
#         except: 
#             pass
            
#     with open("C:\\Users\chuanan\Downloads\spacey-linux-windows\spacey-linux-windows\Server\Telegram Bot\\locations_write.csv", 'w', newline='') as csvfile:
#         spamwriter = csv.writer(csvfile, delimiter = ",") 
#         spamwriter.writerow(csv_columns)
#         spamwriter = csv.DictWriter(csvfile, fieldnames=csv_columns) 
#         spamwriter.writerows(results)

#     localtime = time.localtime(time.time())
#     date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
#     time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
#     context.bot_data['time_updated'] = date + time_now
        
def test_with_limit(update,context):
    for i in range(10):
        context.bot.send_message("772520752", i) 

def test_no_limit(update,context):
    for i in range(10):
        bot.send_message("772520752", i)    

class MQBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_message(*args, **kwargs)


def main():
    # limit global throughput to 3 messages per 3 seconds
    q = mq.MessageQueue(all_burst_limit=29, all_time_limit_ms=1017)
    request = Request(con_pool_size=8)
    spaceybot = MQBot(TOKEN, request=request, mqueue=q)

    # Create the Updater and pass in bot's token.
    updater = Updater(bot=spaceybot, use_context = True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    

    # Create command handlers
    dp.add_handler(CommandHandler("start", start))
    
    dp.add_handler(CommandHandler("setspaceyhigh", setspaceyhigh))
    dp.add_handler(CommandHandler("setspaceymid", setspaceymid))
    dp.add_handler(CommandHandler("setspaceylow", setspaceylow))

    dp.add_handler(CommandHandler("test", test))
    dp.add_handler(CommandHandler("test_with_limit", test_with_limit))
    dp.add_handler(CommandHandler("test_no_limit", test_no_limit))


    dp.add_error_handler(error_callback)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu),CommandHandler('notifications', notifications)],

        states={
            LOCATION: [CallbackQueryHandler(check_location)],
            CHECKWHAT: [CallbackQueryHandler(check_what)],
            SUBSCRIBE_MAIN: [CallbackQueryHandler(subscribe_main)],
            SUBSCRIBE_TYPE: [CallbackQueryHandler(subscribe_type)],
            SUBSCRIBE_LOCATION: [CallbackQueryHandler(subscribe_location)],
            UNSUBSCRIBE_TYPE: [CallbackQueryHandler(unsubscribe_type)]
        },

        fallbacks=[CommandHandler('menu', menu),CommandHandler('notifications', notifications)]
    )
    dp.add_handler(conv_handler)
    
    # Get job queue
    j = updater.job_queue

    # Set daily notifications
    t = datetime.time(10,45,00,000000)
    dp.add_handler(CallbackQueryHandler(daily_notifications))
    job_daily = j.run_daily(daily_notifications,t)

    # Set >80% notifications
    dp.add_handler(CallbackQueryHandler(full_notifications))
    job_minute1 = j.run_repeating(full_notifications, interval=120, first=0) #check and alert every 2 mins

    # Update seats occupancy
    # dp.add_handler(CallbackQueryHandler(update_seats))
    # job_minute2 = j.run_repeating(update_seats, interval=888, first=0) #run every 3 mins 180
    
    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    cfg.main()
    # userID = 'NUS'
    # cfg.database.timeout()
    # x = ResServer(userID)
    # p = Process(target=x.scan_update)
    # p.start()
    main()


#https://api.telegram.org/botNIMAMA/getUpdates
