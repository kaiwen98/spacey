from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request
import matplotlib.pyplot as plt
import numpy as np
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
from os.path import dirname as dir, splitext, basename, join, abspath
import sys
import base64
import res_info as res
from multiprocessing import Process, Pipe, Lock
import random
import time
import redis

_root = dir(dir(abspath(__file__)))
PORT = int(os.environ.get('PORT', 5000))
TOKEN = '1165909865:AAHR4VkQAIKXFv6Jw-lbe4faMIil_mjXBK4'

# users_info_path = os.path.join(_root, "Telegram_Bot_Spacey", "users_info.csv")
# locations_path = os.path.join(_root, "Telegram_Bot_Spacey", "locations.csv")
image_folder = os.path.join(_root, "images")
image_output_graphic_folder = os.path.join(image_folder, "output graphic")


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # logger.info("User {user} sent {message}".format(user=update.message.from_user.username, message=update.message.text))

LOCATION, CHECKAREA, CHECKWHAT, SUBSCRIBE_MAIN, SUBSCRIBE_TIME, SUBSCRIBE_TYPE, SUBSCRIBE_AREA, SUBSCRIBE_LOCATION, UNSUBSCRIBE_TYPE, SETSPACEYVALUE= range(10)
red_alert = "\ud83d\udd34"
yellow_alert = "\ud83d\udfe1"
green_alert = "\ud83d\udfe2"
seats_emoji = "\ud83e\ude91"
blue_bullet_point = "\ud83e\udd4f"
diamond = "\ud83d\udd39"

def start(update, context):
    # chat_type = update.message.chat.type
    name = update.message.from_user.first_name
    username = update.message.from_user.username
    user_id = str(update.message.from_user.id)
    date = datetime.datetime.now()
    #Store user data in csv
    # with open(users_info_path) as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter = ",") 
    #     results = []
    #     user_id_list = []
    #     for i in spamreader:
    #         results.append(i)
    #         user_id_list.append(i[2])
    # if user_id not in user_id_list:
    #     results.append([name,username,user_id,date,0,0,0])
    #     with open(users_info_path, 'w', newline='') as csvfile:
    #         spamwriter = csv.writer(csvfile, delimiter = ",") 
    #         for i in results:
    #             spamwriter.writerow(i)

    #Store user data in database
    users_info = cfg.database.client.hgetall('users_info')
    if user_id not in users_info.keys():
        dict_object = {"name": name, "username": username, "daily_notifications": "0", "full_notifications": "0", "flag":"0","daily_time":"0","daily_area":"0",">80_area":"0"}
        stringified_dict_obj = json.dumps(dict_object) 
        new_entry = {user_id:stringified_dict_obj}
        cfg.database.client.hmset('users_info',new_entry)

    context.bot.send_message(user_id,text='Hi '+name+', Welcome to <b>Spacey Telegram Bot</b>!\n<u><i>Please read the following before continuing</i></u>.\n\n'
                                            '/menu to start checking details of a location.\n'
                                            +diamond+ ' <b>Occupancy.</b> Gives current seat occupancy of the given location.\n'
                                            +diamond+' <b>Operation Hours.</b> Gives the opening hours of the given location.\n'
                                            +diamond+' <b>How to go.</b> Gives the address and map of the given location.\n'
                                            +diamond+' <b>Recent statistics.</b> Gives the recent visitors count of given location.\n\n'
                                            '/notifications to subscribe to notifications.\n'
                                            +diamond+' <b>Daily notifications.</b> Sends daily updates of your chosen location at different timings.\n'
                                            +diamond+' <b>>80% notifications.</b> Sends updates of your chosen location whenever it is reaching its full capacity.\n'
                                            '<i>Note: seat occupancies are updated through sensors. However, for simulation purposes, use /setspaceyoccupancy to manipulate the occupancy of <u>Spacey Cafe</u> to either 20%, 60% or 80%!</i>\n'
                                            '<i>Note 2: >80% notifications and latest visitors count are checked every 2mins and 5 mins respectively for testing purposes.</i>\n\n', parse_mode = 'HTML')

def menu(update,context):
    areas = cfg.database.client.smembers ('registered_users')
    keyboard=[]
    for area in areas:
        keyboard.append([InlineKeyboardButton(area, callback_data=area)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Which area would you like to check?', reply_markup=reply_markup)
    return CHECKAREA

def check_area(update,context):
    query = update.callback_query
    context.user_data['area'] = query.data
    locations_list = cfg.database.get_all_restaurant_from_user(query.data)
    keyboard=[]
    for location in locations_list:
        keyboard.append([InlineKeyboardButton(location, callback_data=location)])
    keyboard.append([InlineKeyboardButton("Back", callback_data="Back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text='Which location would you like to check?', reply_markup=reply_markup)
    return LOCATION


# def getcsv():
#     with open(locations_path) as csvfile:
#         spamreader = csv.DictReader(csvfile, delimiter = ",")
#         results = {}
#         for i in spamreader:
#             location = i.pop('Location')
#             results[location] = dict(i)
#         return results

# def get_locations():
#     with open(locations_path) as csvfile:
#         spamreader = csv.DictReader(csvfile, delimiter = ",")
#         locations = []
#         for i in spamreader:
#             location = i.pop('Location')
#             locations.append(location)
#         return locations

def check_location(update, context):
    query = update.callback_query
    location = query.data
    query.edit_message_text(text="Selected location: {}".format(location))
    
    if query.data == "Back":
        areas = cfg.database.client.smembers ('registered_users')
        keyboard=[]
        for area in areas:
            keyboard.append([InlineKeyboardButton(area, callback_data=area)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='Which area would you like to check?', reply_markup=reply_markup)
        return CHECKAREA

    else:
        context.user_data['location'] = location
        keyboard=[[InlineKeyboardButton("Occupancy", callback_data='Occupancy'),
            InlineKeyboardButton("Operation Hours", callback_data='Operation Hours')],

            [InlineKeyboardButton("How to go", callback_data='How to go'),
            InlineKeyboardButton("Recent Statistics", callback_data="Recent Statistics")],

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
    area = context.user_data['area']
    # location_data = getcsv()
    if option == 'Occupancy':
        localtime = time.localtime(time.time())
        date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
        time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
        seats_available = 0
        seats_taken = 0
        occupancy_data = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
        for seat in occupancy_data.values():
            if seat == '0':
                seats_available += 1
            else:
                seats_taken += 1
        seats_total = seats_available + seats_taken
        seats_occupancy = round(seats_taken/seats_total*100, 2)

        #Generate PIE CHART
        labels = ['Occupied','Free']
        colors = ['#808080','#66b3ff'] #grey and blue
        sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]
        
        centre_circle = plt.Circle((0,0),0.75,color='white', fc='white', linewidth=0.5)
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.pie(sizes, colors=colors, autopct='%1.1f%%', pctdistance=0.85,
                shadow=False, startangle=90, center=(0,0)) #pctdistance for percentage labels position
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.legend(labels, loc=3,prop={'size': 15}) #bottom right
        plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
        plt.tight_layout()
        plt.savefig(join(image_output_graphic_folder,"chart_"+str(location)+".png"))
        plt.clf()
        #Generate FLOORPLAN
        config_obj = cfg.ResServer(area)
        restaurants_data = config_obj.get_info()
        for loc_data, obj_data in restaurants_data.items():
            if location == loc_data:
                occupancy = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
                imageupdate(obj_data, occupancy)
                imagegen(obj_data)

        if seats_occupancy < 50:
            alert = green_alert
        elif seats_occupancy >=80:
            alert = red_alert
        else:
            alert = yellow_alert 

        #Send occupancy data, pie chart and floorplan
        context.bot.send_message(user_id, text=seats_emoji+"<b> Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%) "+ alert,parse_mode='HTML')
        context.bot.send_photo(user_id, photo=open(image_output_graphic_folder+'\\chart_'+str(location)+'.png', 'rb'))
        context.bot.send_photo(user_id, photo=open(join(image_output_graphic_folder,'output_'+str(area)+'_'+str(location)+'.png'), 'rb'))

        keyboard=[[InlineKeyboardButton("Operation Hours", callback_data='Operation Hours'),
            InlineKeyboardButton("How to go", callback_data='How to go'),
            InlineKeyboardButton("Recent Statistics", callback_data='Recent Statistics')],
            [InlineKeyboardButton("Back to Menu", callback_data='Back to Menu'),InlineKeyboardButton("End", callback_data='End')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Anything else regarding " + location +" that you would like to know about?", reply_markup=reply_markup)
        return CHECKWHAT
    
    elif option == 'Operation Hours':
        try:
            # context.bot.send_message(user_id, text=location_data[location]["Operation Hours"])
            data = cfg.database.client.hgetall(area+"_"+location+"_res_info")
            context.bot.send_message(user_id, data['res_occup_hr'])
        except:
            context.bot.send_message(user_id, text='No data found!')

        keyboard=[[InlineKeyboardButton("Occupancy", callback_data='Occupancy'),
            InlineKeyboardButton("How to go", callback_data='How to go'),
            InlineKeyboardButton("Recent Statistics", callback_data='Recent Statistics')],
            [InlineKeyboardButton("Back to Menu", callback_data='Back to Menu'),InlineKeyboardButton("End", callback_data='End')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Anything else regarding " + location +" that you would like to know about?", reply_markup=reply_markup)
        return CHECKWHAT

    elif option == 'How to go':
        try:
            # latitude = location_data[location]['Latitude']
            # longitude = location_data[location]['Longitude']
            # address = location_data[location]['Address']
            data = cfg.database.client.hgetall(area+"_"+location+"_res_info")
            latitude = data['res_lat']
            longitude = data['res_lng']
            address = data['res_addr']      
            context.bot.send_venue(user_id, latitude=latitude, longitude=longitude, title=location, address=address)
        except:
            context.bot.send_message(user_id, text='No data found!')

        keyboard=[[InlineKeyboardButton("Occupancy", callback_data='Occupancy'),
            InlineKeyboardButton("Operation Hours", callback_data='Operation Hours'),
            InlineKeyboardButton("Recent Statistics", callback_data='Recent Statistics')],
            [InlineKeyboardButton("Back to Menu", callback_data='Back to Menu'),InlineKeyboardButton("End", callback_data='End')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Anything else regarding " + location +" that you would like to know about?", reply_markup=reply_markup)
        return CHECKWHAT

    elif option == "Recent Statistics":
        data = cfg.database.client.hgetall(area+"_"+location+"_totalvisitors")
        latest10 = list(data)[-10:]
        total_visitors_list = []
        for timestamp in latest10:
            total_visitors_list.append(int(data[timestamp]))
            
        height = total_visitors_list
        bars = latest10
        y_pos = np.arange(len(bars))
        #Set y-ticks to whole numbers
        # yticks_values = range(min(height), (max(height)+1))
        # plt.yticks(yticks_values)
        # Create bars
        plt.bar(y_pos, height)
        
        # Create names on the x-axis
        plt.xticks(y_pos, bars,rotation='vertical')
        # Set labels
        plt.ylabel("Number of users")
        plt.xlabel("Time")
        plt.title("Graph of most recent visitors count in "+location+'.\n')
        plt.tight_layout()
        plt.savefig(image_output_graphic_folder+'\\bar_'+str(location)+'.png')
        context.bot.send_photo(user_id, photo=open(image_output_graphic_folder+'\\bar_'+location+'.png', 'rb'))
        plt.clf()

        keyboard=[[InlineKeyboardButton("Occupancy", callback_data='Occupancy'),
            InlineKeyboardButton("Operation Hours", callback_data='Operation Hours'),
            InlineKeyboardButton("How to go", callback_data='How to go')],
            [InlineKeyboardButton("Back to Menu", callback_data='Back to Menu'),InlineKeyboardButton("End", callback_data='End')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="Anything else regarding " + location +" that you would like to know about?", reply_markup=reply_markup)
        return CHECKWHAT

    elif option == 'Back':
        locations_list = cfg.database.get_all_restaurant_from_user(area)
        keyboard=[]
        for location in locations_list:
            keyboard.append([InlineKeyboardButton(location, callback_data=location)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, 'Which location would you like to check?', reply_markup=reply_markup)
        return LOCATION

    elif option == 'Back to Menu':
        areas = cfg.database.client.smembers ('registered_users')
        keyboard=[]
        for area in areas:
            keyboard.append([InlineKeyboardButton(area, callback_data=area)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, 'Which area would you like to check?', reply_markup=reply_markup)
        return CHECKAREA

    elif option == 'End':
        context.bot.send_message(user_id, "Have a good day! \ud83d\ude0a")
        return ConversationHandler.END
    


# def test(update, context):
#     chatid = update.message.from_user.id
#     grpid = update.message.chat.id

#     data = cfg.database.client.hgetall("NUS_Deck_res_info")
#     update.message.reply_text(data['res_lat'])
    
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
                context.bot.send_message(user_id, text='You are currently subscribed to daily notifications (<b>'+ str(data['daily_notifications']) +", "+str(data['daily_time'])+ '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif str(data['daily_notifications']) == '0' and str(data['full_notifications']) != '0':     #subscribed to >80% only
                keyboard=[[InlineKeyboardButton('Subscribe to daily notifications ', callback_data='Subscribedaily')],
                            [InlineKeyboardButton('Unsubscribe from >80% notifications', callback_data='Unsubscribe>80%')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You are currently subscribed to >80% notifications (<b>' +str(data['full_notifications'])+ '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif str(data['daily_notifications']) != '0' and str(data['full_notifications']) != '0': #subscribed to both
                keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You have subscribed to daily notifications (<b>'+ str(data['daily_notifications']) +", "+str(data['daily_time']) + '</b>) and >80% notifications (<b>'+str(data['full_notifications'])+ '</b>). Would you like to unsubscribe?',reply_markup=reply_markup, parse_mode='HTML')
        
    return SUBSCRIBE_MAIN        

def subscribe_main(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    
    if query.data == 'Subscribe':
        keyboard=[[InlineKeyboardButton('Daily Notifications', callback_data='Subscribedaily'),
                    InlineKeyboardButton('>80% Notifications', callback_data='Subscribe>80%')],
                    [InlineKeyboardButton('Both', callback_data='SubscribeBoth')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(user_id, text="Which notification would you like to subscribe to?", reply_markup=reply_markup)
        return SUBSCRIBE_TYPE

    elif query.data == 'Unsubscribe':
        keyboard=[[InlineKeyboardButton('Daily Notifications', callback_data='Unsubscribedaily'),
                    InlineKeyboardButton('>80% Notifications', callback_data='Unsubscribe>80%')],
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

    elif query.data == 'Subscribe>80%':
        context.user_data['subscribe_type'] = query.data
        areas = cfg.database.client.smembers ('registered_users')
        keyboard=[]
        for area in areas:
            keyboard.append([InlineKeyboardButton(area, callback_data=area)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, 'Which area would you like to choose?', reply_markup=reply_markup)
        return SUBSCRIBE_AREA
        # locations_list = cfg.database.get_all_restaurant_from_user('NUS')
        # keyboard=[]
        # for location in locations_list:
        #     keyboard.append([InlineKeyboardButton(location, callback_data=location)])
        # reply_markup = InlineKeyboardMarkup(keyboard)
        # context.bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)
        # return SUBSCRIBE_LOCATION

    elif query.data == 'Subscribedaily':
        context.user_data['subscribe_type'] = query.data
        keyboard=[[InlineKeyboardButton("12pm", callback_data="12pm"),
                InlineKeyboardButton("1pm", callback_data="1pm"),
                InlineKeyboardButton("2pm", callback_data="2pm")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="What time would you like to be notified?", reply_markup=reply_markup)
        return SUBSCRIBE_TIME
    

def subscribe_type(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    context.user_data['subscribe_type'] = query.data

    if query.data == 'Subscribedaily' or query.data == 'SubscribeBoth':
        keyboard=[[InlineKeyboardButton("12pm", callback_data="12pm"),
                InlineKeyboardButton("1pm", callback_data="1pm"),
                InlineKeyboardButton("2pm", callback_data="2pm")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(user_id, text="What time would you like to be notified?", reply_markup=reply_markup)
        return SUBSCRIBE_TIME

    #query.data == 'Subscribe>80%'
    areas = cfg.database.client.smembers ('registered_users')
    keyboard=[]
    for area in areas:
        keyboard.append([InlineKeyboardButton(area, callback_data=area)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(user_id, 'Which area would you like to choose?', reply_markup=reply_markup)
    return SUBSCRIBE_AREA

    

def subscribe_area(update,context):
    query = update.callback_query
    query.edit_message_text(text="Selected option: {}".format(query.data))
    user_id = str(query.from_user.id)
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        if id_number == user_id:
            data = json.loads(data)
            if context.user_data['subscribe_type'] == 'Subscribedaily':
                data['daily_area'] = query.data
                context.user_data['daily_area'] = query.data
            elif context.user_data['subscribe_type'] == 'Subscribe>80%': 
                data['>80_area'] = query.data
                context.user_data['>80_area'] = query.data
            elif context.user_data['subscribe_type'] == 'SubscribeBoth':
                data['daily_area'] = query.data
                data['>80_area'] = query.data
                context.user_data['daily_area'] = query.data
                context.user_data['>80_area'] = query.data
            data = json.dumps(data)
            new_entry = {id_number:data}
            cfg.database.client.hmset('users_info',new_entry)

    locations_list = cfg.database.get_all_restaurant_from_user(query.data)
    keyboard=[]
    for location in locations_list:
        keyboard.append([InlineKeyboardButton(location, callback_data=location)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)
    return SUBSCRIBE_LOCATION


def subscribe_time(update,context):
    query = update.callback_query
    user_id = str(query.from_user.id)
    query.edit_message_text(text="Selected time: {}".format(query.data))
    context.user_data['subscribe_time'] = query.data

    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        if id_number == user_id:
            data = json.loads(data)
            data['daily_time'] = query.data
            data = json.dumps(data)
            new_entry = {id_number:data}
            cfg.database.client.hmset('users_info',new_entry)
    
    areas = cfg.database.client.smembers ('registered_users')
    keyboard=[]
    for area in areas:
        keyboard.append([InlineKeyboardButton(area, callback_data=area)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(user_id, 'Which area would you like to be choose?', reply_markup=reply_markup)
    return SUBSCRIBE_AREA

    # locations_list = cfg.database.get_all_restaurant_from_user('NUS')
    # keyboard=[]
    # for location in locations_list:
    #     keyboard.append([InlineKeyboardButton(location, callback_data=location)])
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # context.bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)
    # return SUBSCRIBE_LOCATION

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
                time = data['daily_time']
                context.bot.send_message(user_id, 'Daily notifications for <b>' +query.data+ '</b> set at <b>'+time+ '</b> daily!',parse_mode='HTML')

            elif context.user_data['subscribe_type'] == 'Subscribe>80%':
                data['full_notifications'] = query.data
                context.bot.send_message(user_id, '>80% notifications for <b>' +query.data+ '</b> set!',parse_mode='HTML')

            elif context.user_data['subscribe_type'] == 'SubscribeBoth':
                data['daily_notifications'] = query.data
                data['full_notifications'] = query.data
                time = data['daily_time']
                context.bot.send_message(user_id, 'Daily notifications at <b>'+ time+ '</b> and >80% notifications for <b>' +query.data+ '</b> set!',parse_mode='HTML')
            data = json.dumps(data)
            new_entry = {id_number:data}
            cfg.database.client.hmset('users_info',new_entry)

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
                data['daily_time'] = 0
                data['daily_area'] = 0
                notification_type =  'Daily notifications'
                
            elif query.data == 'Unsubscribe>80%':
                location_removed = data['full_notifications']
                data['full_notifications'] = 0
                data['flag'] = 0
                data['>80_area'] = 0
                notification_type =  '>80% notifications'
                
            elif query.data == 'UnsubscribeBoth':
                location1_removed = data['daily_notifications']
                location2_removed = data['full_notifications']
                data['daily_notifications'] = 0
                data['daily_time'] = 0
                data['daily_area'] = 0
                data['full_notifications'] = 0
                data['flag'] = 0
                data['>80_area'] = 0
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

def daily_notifications_12pm(context):
    # location_data = getcsv()
    # locations_list = cfg.database.get_all_restaurant_from_user('NUS')      
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        data = json.loads(data)
        if str(data['daily_notifications']) != '0' and data['daily_time'] == '12pm': #daily 12pm notification on, send notification
            name = data['name']
            user_id = id_number
            area = data['daily_area']
            location = data['daily_notifications']
            localtime = time.localtime(time.time())
            date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
            time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
            for seat in occupancy_data.values():
                if seat == '0':
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = seats_available + seats_taken
            seats_occupancy = round(seats_taken/seats_total*100, 2)
            #Generate PIE CHART
            # labels = ['Occupied','Free']
            # colors = ['#808080','#66b3ff'] #grey and blue
            # sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]

            # centre_circle = plt.Circle((0,0),0.75,color='white', fc='white', linewidth=0.5)
            # fig = plt.gcf()
            # fig.gca().add_artist(centre_circle)
            # plt.pie(sizes, colors=colors, autopct='%1.1f%%', pctdistance=0.85,
            #         shadow=False, startangle=90)
            # plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            # plt.legend(labels, loc=3,prop={'size': 15})
            # plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
            # plt.savefig(image_output_graphic_folder+'\\chart_'+str(location)+'.png')
            # plt.clf()
            #Generate FLOORPLAN
            # config_obj = cfg.ResServer('NUS')
            # restaurants_data = config_obj.get_info()
            # for loc_data, obj_data in restaurants_data.items():
            #     if location == loc_data:
            #         occupancy = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
            #         imageupdate(obj_data, occupancy)
            #         imagegen(obj_data)

            if seats_occupancy < 50:
                alert = green_alert
            elif seats_occupancy >=80:
                alert = red_alert
            else:
                alert = yellow_alert 
            #Send occupancy data, pie chart and floorplan
            context.bot.send_message(user_id, text="Hey "+ name +"! Here is your daily notification for <b><u>"+location+"</u></b>!\n\n"+seats_emoji+"<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)"+alert, parse_mode='HTML')
            # context.bot.send_photo(user_id, photo=open(image_output_graphic_folder+'\\chart_'+str(location)+'.png', 'rb'))
            # context.bot.send_photo(user_id, photo=open(image_output_graphic_folder+'\output_NUS_'+location+'.png', 'rb'))


def daily_notifications_1pm(context):     
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        data = json.loads(data)
        if str(data['daily_notifications']) != '0' and data['daily_time'] == '1pm': #daily 1pm notification on, send notification
            name = data['name']
            user_id = id_number
            area = data['daily_area']
            location = data['daily_notifications']
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
            for seat in occupancy_data.values():
                if seat == '0':
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = seats_available + seats_taken
            seats_occupancy = round(seats_taken/seats_total*100, 2)

            if seats_occupancy < 50:
                alert = green_alert
            elif seats_occupancy >=80:
                alert = red_alert
            else:
                alert = yellow_alert 
            #Send occupancy data
            context.bot.send_message(user_id, text="Hey "+ name +"! Here is your daily notification for <b><u>"+location+"</u></b>!\n\n"+seats_emoji+"<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)"+alert, parse_mode='HTML')
            
def daily_notifications_2pm(context):     
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        data = json.loads(data)
        if str(data['daily_notifications']) != '0' and data['daily_time'] == '2pm': #daily 2pm notification on, send notification
            name = data['name']
            user_id = id_number
            area = data['daily_area']
            location = data['daily_notifications']
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
            for seat in occupancy_data.values():
                if seat == '0':
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = seats_available + seats_taken
            seats_occupancy = round(seats_taken/seats_total*100, 2)

            if seats_occupancy < 50:
                alert = green_alert
            elif seats_occupancy >=80:
                alert = red_alert
            else:
                alert = yellow_alert 
            #Send occupancy data
            context.bot.send_message(user_id, text="Hey "+ name +"! Here is your daily notification for <b><u>"+location+"</u></b>!\n\n"+seats_emoji+"<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)"+alert, parse_mode='HTML')
            

def full_notifications(context):
    users_info = cfg.database.client.hgetall('users_info')
    for id_number, data in users_info.items():
        data = json.loads(data)
        if str(data['full_notifications']) != '0' and str(data['flag']) == '0': #>80% notifications on and flag off. ie send notification
            name = data['name']
            user_id = id_number
            area = data['>80_area']
            location = data['full_notifications']
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
            for seat in occupancy_data.values():
                if seat == '0':
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = seats_available + seats_taken
            seats_occupancy = round(seats_taken/seats_total*100, 2)
            if seats_occupancy >= 80:
                # localtime = time.localtime(time.time())
                # date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
                # time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
                # labels = ['Occupied','Free']
                # colors = ['#808080','#66b3ff'] #grey and blue
                # sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]
                
                # centre_circle = plt.Circle((0,0),0.75,color='white', fc='white', linewidth=0.5)
                # fig = plt.gcf()
                # fig.gca().add_artist(centre_circle)
                # plt.pie(sizes, colors=colors, autopct='%1.1f%%', pctdistance=0.85,
                #         shadow=False, startangle=90)
                # plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                # plt.legend(labels, loc=3,prop={'size': 15})
                # plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
                # plt.savefig(image_output_graphic_folder+'\\chart_'+str(location)+'.png')
                # plt.clf()        

                #Generate FLOORPLAN
                # config_obj = cfg.ResServer('NUS')
                # restaurants_data = config_obj.get_info()
                # for loc_data, obj_data in restaurants_data.items():
                #     if location == loc_data:
                #         occupancy = cfg.database.client.hgetall('NUS_'+location+'_occupancy')
                #         imageupdate(obj_data, occupancy)
                #         imagegen(obj_data)

                #Send occupancy data
                context.bot.send_message(user_id, text="Hey "+ name +"! <b><u>"+location+"</u></b> is getting crowded!\n\n"+seats_emoji+"<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)"+red_alert,parse_mode='HTML')
                # context.bot.send_photo(user_id, photo=open(image_output_graphic_folder+'\\chart_'+str(location)+'.png', 'rb')) 
                # context.bot.send_photo(user_id, photo=open(image_output_graphic_folder+'\output_NUS_'+location+'.png', 'rb'))

                data['flag'] = '1'
                data = json.dumps(data)
                new_entry = {id_number:data}
                cfg.database.client.hmset('users_info',new_entry)

        elif str(data['full_notifications']) != '0' and str(data['flag']) == '1': # >80% notifications on and flag is on
            area = data['>80_area']
            location = data['full_notifications']
            seats_available = 0
            seats_taken = 0
            occupancy_data = cfg.database.client.hgetall(area+'_'+location+'_occupancy')
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

def hourly_update(context):
    areas = cfg.database.client.smembers ('registered_users')
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
def setspaceyoccupancy(update,context):
    user_id = update.message.from_user.id
    keyboard=[[InlineKeyboardButton('80%', callback_data='80%'),InlineKeyboardButton('60%', callback_data='60%'),InlineKeyboardButton('40%', callback_data='40%')],[InlineKeyboardButton('Random', callback_data='Random')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(user_id, text="What occupancy level of Spacey Cafe would you like to set?", reply_markup=reply_markup)
    return SETSPACEYVALUE

def setspaceyvalue(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    # query.edit_message_text(text="Selected option: {}".format(query.data))
    occupancy_data = cfg.database.client.hgetall('NUS_Spacey Cafe_occupancy')
    count = 0
    if query.data == '80%':
        for seat_num, status in occupancy_data.items():
            if count < len(occupancy_data)*0.8:
                occupancy_data[seat_num] = '1'
                count += 1
            else:
                occupancy_data[seat_num] = '0'
    elif query.data == '60%':
        for seat_num, status in occupancy_data.items():
            if count < len(occupancy_data)*0.60:
                occupancy_data[seat_num] = '1'
                count += 1
            else:
                occupancy_data[seat_num] = '0'
    elif query.data == '40%':
        for seat_num, status in occupancy_data.items():
            if count < len(occupancy_data)*0.40:
                occupancy_data[seat_num] = '1'
                count += 1
            else:
                occupancy_data[seat_num] = '0'
    elif query.data == 'Random':
        random_value = random.randint(0,len(occupancy_data))
        for seat_num, status in occupancy_data.items():
            if count < random_value:
                occupancy_data[seat_num] = '1'
                count += 1
            else:
                occupancy_data[seat_num] = '0'
    percentage = round(count/len(occupancy_data)*100)     
    cfg.database.client.hmset('NUS_Spacey Cafe_occupancy', occupancy_data)    
    context.bot.send_message(user_id, 'Occupancy for Spacey Cafe set to <b>'+str(percentage)+'</b>%!' ,parse_mode='HTML')
    return ConversationHandler.END

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
    cfg.main()
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
    # dp.add_handler(CommandHandler("test", test))

    dp.add_error_handler(error_callback)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu),CommandHandler('notifications', notifications),CommandHandler('setspaceyoccupancy', setspaceyoccupancy)],

        states={
            LOCATION: [CallbackQueryHandler(check_location)],
            CHECKAREA: [CallbackQueryHandler(check_area)],
            CHECKWHAT: [CallbackQueryHandler(check_what)],
            SUBSCRIBE_MAIN: [CallbackQueryHandler(subscribe_main)],
            SUBSCRIBE_TYPE: [CallbackQueryHandler(subscribe_type)],
            SUBSCRIBE_TIME: [CallbackQueryHandler(subscribe_time)],
            SUBSCRIBE_AREA: [CallbackQueryHandler(subscribe_area)],
            SUBSCRIBE_LOCATION: [CallbackQueryHandler(subscribe_location)],
            UNSUBSCRIBE_TYPE: [CallbackQueryHandler(unsubscribe_type)],
            SETSPACEYVALUE: [CallbackQueryHandler(setspaceyvalue)]
        },

        fallbacks=[CommandHandler('menu', menu),CommandHandler('notifications', notifications),CommandHandler('setspaceyoccupancy', setspaceyoccupancy)]
    )
    dp.add_handler(conv_handler)
    
    # Get job queue
    j = updater.job_queue

    # Set daily notifications
    daily_notification_12pm_t = datetime.time(13,10,00,000000)
    dp.add_handler(CallbackQueryHandler(daily_notifications_12pm))
    job_daily1 = j.run_daily(daily_notifications_12pm, daily_notification_12pm_t)

    daily_notification_1pm_t = datetime.time(13,12,00,000000)
    dp.add_handler(CallbackQueryHandler(daily_notifications_1pm))
    job_daily2 = j.run_daily(daily_notifications_1pm, daily_notification_1pm_t)

    daily_notification_2pm_t = datetime.time(13,14,00,000000)
    dp.add_handler(CallbackQueryHandler(daily_notifications_2pm))
    job_daily3 = j.run_daily(daily_notifications_2pm, daily_notification_2pm_t)

    # t_1 = datetime.time(13,30,00,000000)
    # dp.add_handler(CallbackQueryHandler(hourly_info1))
    # job_daily = j.run_daily(hourly_info1,t_1)

    # t_2 = datetime.time(13,32,00,000000)
    # dp.add_handler(CallbackQueryHandler(hourly_info2))
    # job_daily = j.run_daily(hourly_info2,t_2)

    # Set >80% notifications
    dp.add_handler(CallbackQueryHandler(full_notifications))
    job_minute1 = j.run_repeating(full_notifications, interval=120, first=0) #check and alert every 2 mins

    dp.add_handler(CallbackQueryHandler(hourly_update))
    job_minute2 = j.run_repeating(hourly_update, interval=300, first=0)

    # Update seats occupancy
    # dp.add_handler(CallbackQueryHandler(update_seats))
    # job_minute2 = j.run_repeating(update_seats, interval=888, first=0) #run every 3 mins 180
    
    # Start the Bot
    # updater.start_polling()
    
    updater.start_webhook(listen="0.0.0.0",
                      port= int(PORT),
                      url_path=TOKEN)
    updater.bot.setWebhook("https://spaceyherok.herokuapp.com/" + TOKEN)
    
    updater.idle()


if __name__ == '__main__':
    
    # userID = 'NUS'
    # cfg.database.timeout()
    # x = ResServer(userID)
    # p = Process(target=x.scan_update)
    # p.start()
    main()


#https://api.telegram.org/botNIMAMA/getUpdates
