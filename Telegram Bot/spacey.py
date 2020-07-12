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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # logger.info("User {user} sent {message}".format(user=update.message.from_user.username, message=update.message.text))

LOCATION, CHECKWHAT, SUBSCRIBE_MAIN, SUBSCRIBE_TYPE, SUBSCRIBE_LOCATION, UNSUBSCRIBE_TYPE= range(6)

def start(update, context):
    chat_type = update.message.chat.type
    name = update.message.from_user.first_name
    username = update.message.from_user.username
    user_id = str(update.message.from_user.id)
    date = datetime.datetime.now()
    
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv") as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ",") 
        results = []
        user_id_list = []
        for i in spamreader:
            results.append(i)
            user_id_list.append(i[2])
    if user_id not in user_id_list:
        results.append([name,username,user_id,date,0,0,0])
        with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv", 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter = ",") 
            for i in results:
                spamwriter.writerow(i)
    if chat_type == 'private':
        location_data = getcsv()
        # update.message.reply_text(location_data) 
        keyboard=[]
        for location in location_data.keys():
            keyboard.append([InlineKeyboardButton(location, callback_data=location)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Hi '+name+', which location would you like to check?', reply_markup=reply_markup)
        return LOCATION
    else:
        update.message.reply_text('Hi '+ name+', type /help to learn more!')
        return ConversationHandler.END

def help(update, context):
    update.message.reply_text("Welcome to Spacey! Find out the current seat occupancy using simple commands!\n"
                                "Bot is in the still undergoing testing. Hardware implementation has not been integrated, hence all values are arbitrary for now.\nUse these commands to test the functions of bot:\n /test_spacey_occupancy (gets seats occupancy of location)\n /test_spacey_details (gets coordinates and info about the establishment)")

def getcsv():
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\locations.csv") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter = ",")
        results = {}
        for i in spamreader:
            location = i.pop('Location')
            results[location] = dict(i)
        return results

def get_locations():
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\locations.csv") as csvfile:
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
            [InlineKeyboardButton("How to go", callback_data='How to go')]]
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
        seats_available = int(location_data[location]['Seats Available'])
        seats_taken = int(location_data[location]['Seats Taken'])
        seats_total = int(location_data[location]['Seats Total'])
        seats_occupancy = seats_taken/seats_total*100
        labels = ['Occupied','Free']
        colors = ['Red','Green']
        sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]
        explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Free')

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
        plt.savefig('C:\\Users\chuanan\Documents\grambots\spacey\\chart_'+str(location)+'.png')
        
        context.bot.send_message(user_id, text="<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)",parse_mode='HTML')
        context.bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Documents\grambots\spacey\\chart_'+str(location)+'.png', 'rb'))
    elif option == 'Operation Hours':
        context.bot.send_message(user_id, text=location_data[location]["Operation Hours"])
    else:
        latitude = location_data[location]['Latitude']
        longitude = location_data[location]['Longitude']
        address = location_data[location]['Address']
        context.bot.send_venue(user_id, latitude=latitude, longitude=longitude, title=location, address=address)
  
    return ConversationHandler.END
  
def test_spacey_occupancy(update, context):
    chat_id = update.message.from_user.id
    localtime = time.localtime(time.time())
    date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
    time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
    labels = ['Occupied','Free']
    colors = ['Red','Green']
    sizes = [70, 30]
    explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Free')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Graph of seat occupancy at Spacey Cafe\nUpdated as of '+str(date)+" "+str(time_now))
    plt.savefig('C:\\Users\chuanan\Documents\grambots\spacey\\testchart.png')
    
    context.bot.send_message(chat_id, text="<b>Seat Occupancy</b>: 350/500 ("+ str(350/500*100)+"%)",parse_mode='HTML')
    context.bot.send_photo(chat_id, photo=open('C:\\Users\chuanan\Documents\grambots\spacey\\testchart.png', 'rb'))

def test_spacey_details(update, context):
    chat_id = update.message.from_user.id
    context.bot.send_venue(chat_id, latitude=1.298726, longitude=103.775113, title='Spacey Cafe', address='31 Lower Kent Ridge Rd, Singapore 119078')  
    context.bot.send_message(chat_id, "<b><u>Operation Hours:</u></b>\n"+"Mon-Fri, 8.00am-8.00pm",parse_mode='HTML')

def test(update, context):
    chatid = update.message.from_user.id
    grpid = update.message.chat.id
    for ix in range(10):
        context.bot.send_message(chat_id=grpid, text='%s) %s' % (ix + 1, "msgt"))
    
    for ix in range(3):
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        update.message.reply_text(text='%s) %s' % (ix + 1, "okokk"))
        
       
        

        
    
    #results = getcsv()
    #update.message.reply_text(results)
    #chat_type = update.message.chat.type
    
    #bot.send_message(772520752, "<b>SUCK MY KUKUJIAO</b>",parse_mode='HTML')
    # keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
    #          InlineKeyboardButton("Option 2", callback_data='2')],
    #       [InlineKeyboardButton("Option 3", callback_data='3')]]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)
def notifications(update, context):
    chat_type = update.message.chat.type
    user_id = str(update.message.from_user.id)
    
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv") as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ",") 
        results = []
        for i in spamreader:
            results.append(i)
    
    for i in results:
        if user_id in i: 
            if i[4]=='0' and i[5]=='0': #not subscribed to any notifications
                keyboard=[[InlineKeyboardButton('Yes', callback_data='Subscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You have not subscribed to notifications. Do you want to subscribe?',reply_markup=reply_markup)
                
            elif i[4]!='0' and i[5]=='0': #subscribed to daily only
                keyboard=[[InlineKeyboardButton('Subscribe to notifications whenever occupancy >80%', callback_data='Subscribe>80%')],
                            [InlineKeyboardButton('Unsubscribe from daily notifications', callback_data='Unsubscribedaily')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You are currently subscribed to daily notifications (<b>'+ str(i[4]) + '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif i[4]=='0' and i[5]!='0':     #subscribed to >80% only
                keyboard=[[InlineKeyboardButton('Subscribe to daily notifications ', callback_data='Subscribedaily')],
                            [InlineKeyboardButton('Unsubscribe from >80% notifications', callback_data='Unsubscribe>80%')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You are currently subscribed to >80% notifications (<b>' +str(i[5])+ '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif i[4]!='0' and i[5]!='0': #subscribed to both
                keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(user_id, text='You have subscribed to daily notifications (<b>'+ str(i[4]) + '</b>) and >80% notifications (<b>'+str(i[5])+ '</b>). Would you like to unsubscribe?',reply_markup=reply_markup, parse_mode='HTML')
        
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
        context.bot.send_message(user_id, text="No changes were made")
        return ConversationHandler.END 

    else: #query.data == 'Subscribe>80%', 'Subscribedaily'
        context.user_data['subscribe_type'] = query.data
        locations_list = get_locations()
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
    locations_list = get_locations()
    keyboard=[]
    for location in locations_list:
        keyboard.append([InlineKeyboardButton(location, callback_data=location)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)
   
    return SUBSCRIBE_LOCATION

def subscribe_location(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv") as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ",") 
        users_info_list = []
        for i in spamreader:
            users_info_list.append(i)
    
    for i in users_info_list:
        if str(user_id) in i:
            if context.user_data['subscribe_type'] == 'Subscribedaily':
                i[4] = query.data
                notification_type =  'Daily notifications'
            elif context.user_data['subscribe_type'] == 'Subscribe>80%':
                i[5] = query.data
                notification_type =  '>80% notifications'
            elif context.user_data['subscribe_type'] == 'SubscribeBoth':
                i[4] = query.data
                i[5] = query.data
                notification_type =  'Both notifications'
    
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv", 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ",") 
        for i in users_info_list:
            spamwriter.writerow(i)

    context.bot.send_message(user_id, notification_type + ' for <b>' +query.data+ '</b> set!',parse_mode='HTML')
    context.bot.answer_callback_query(callback_query_id=query.id, text="You have subscribed to notiffications! \nTo unsubscribe, use /notifications command again.", show_alert=True)
    return ConversationHandler.END

def unsubscribe_type(update,context):
    query = update.callback_query
    user_id = query.from_user.id
    query.edit_message_text(text="Selected option: {}".format(query.data))
    
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv") as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ",") 
        users_info_list = []
        for i in spamreader:
            users_info_list.append(i)
    
    for i in users_info_list:
        if str(user_id) in i:
            if query.data == 'Unsubscribedaily':
                location_removed = i[4]
                i[4] = 0
                notification_type =  'Daily notifications'
                
            elif query.data == 'Unsubscribe>80%':
                location_removed = i[5]
                i[5] = 0
                notification_type =  '>80% notifications'
                
            elif query.data == 'UnsubscribeBoth':
                location1_removed = str(i[4])
                location2_removed = str(i[5])
                i[4] = 0
                i[5] = 0
                notification_type =  'Both notifications'
                

            elif query.data == 'Cancel':
                context.bot.send_message(user_id, 'No changes were made!')
                return ConversationHandler.END

    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv", 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ",") 
        for i in users_info_list:
            spamwriter.writerow(i)

    if notification_type == 'Both notifications':
        if location1_removed == location2_removed:
            context.bot.send_message(user_id, notification_type+' for <b>'+location1_removed+ '</b> removed!',parse_mode='HTML')
        else:
            context.bot.send_message(user_id, notification_type+' for <b>'+location1_removed+'</b> and <b>'+ location2_removed + '</b> removed!',parse_mode='HTML')
    else: 
        context.bot.send_message(user_id, notification_type + ' for <b>' +location_removed+ '</b> removed!',parse_mode='HTML')
    
    
    return ConversationHandler.END


def daily_notifications(context):
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info_copy.csv") as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ",") 
        results = []
        for i in spamreader:
            results.append(i)
    results.pop(0)
    location_data = getcsv()

    for i in results:
        if i[4] != '0':
            name = i[0]
            user_id = i[2]
            location = i[4]
            localtime = time.localtime(time.time())
            date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
            time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
            seats_available = int(location_data[location]['Seats Available'])
            seats_taken = int(location_data[location]['Seats Taken'])
            seats_total = int(location_data[location]['Seats Total'])
            seats_occupancy = seats_taken/seats_total*100
            labels = ['Occupied','Free']
            colors = ['Red','Green']
            sizes = [seats_taken/seats_total*100, seats_available/seats_total*100]
            explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Free')

            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Graph of seat occupancy at '+str(location)+'\nUpdated as of '+str(date)+" "+str(time_now))
            plt.savefig('C:\\Users\chuanan\Documents\grambots\spacey\\chart_'+str(location)+'.png')
            
            context.bot.send_message(user_id, text="Hey "+ name +"! Here is your daily notification for <b><u>"+location+"</u></b>!\n\n<b>\ud83e\ude91Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)",parse_mode='HTML')
            context.bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Documents\grambots\spacey\\chart_'+str(location)+'.png', 'rb'))    
        

def full_notifications(context):
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info_copy.csv") as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ",") 
        results = []
        for i in spamreader:
            results.append(i)
    
    location_data = getcsv()

    for i in results[1:]:
        if i[5] != '0' and i[6] == '0':
            name = i[0]
            user_id = i[2]
            location = i[5]
            seats_available = int(location_data[location]['Seats Available'])
            seats_taken = int(location_data[location]['Seats Taken'])
            seats_total = int(location_data[location]['Seats Total'])
            seats_occupancy = seats_taken/seats_total*100
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
                plt.savefig('C:\\Users\chuanan\Documents\grambots\spacey\\chart_'+str(location)+'.png')
                
                context.bot.send_message(user_id, text="Hey "+ name +"! Occupancy for <b><u>"+location+"</u></b> has reached >=80%!\n\n<b>\ud83e\ude91Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)",parse_mode='HTML')
                context.bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Documents\grambots\spacey\\chart_'+str(location)+'.png', 'rb'))    
                i[6] = '1'
                with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info_copy.csv", 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter = ",") 
                    for i in results:
                        spamwriter.writerow(i)
        elif i[5] != '0' and i[6] == '1':
            location = i[5]
            seats_available = int(location_data[location]['Seats Available'])
            seats_taken = int(location_data[location]['Seats Taken'])
            seats_total = int(location_data[location]['Seats Total'])
            seats_occupancy = seats_taken/seats_total*100
            if seats_occupancy < 80:
                i[6] = '0'
                with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info_copy.csv", 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter = ",") 
                    for i in results:
                        spamwriter.writerow(i)

def update_seats(context):
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\locations.csv") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter = ",")
        results = []
        for i in spamreader:
            results.append(dict(i))
    csv_columns = list(results[0].keys())
    location_data = getcsv()
   
    # context.bot.send_message(chat_id=chatid, text='B')
    for i in results:
        location = i["Location"]
        try:
            with open("C:\\Users\chuanan\Documents\grambots\spacey\\seats_"+ location +".json") as f:
                seats_data = json.load(f)
            seats_available = 0
            seats_taken = 0
            for seats in seats_data.values():
                if seats == 0:
                    seats_available += 1
                else:
                    seats_taken += 1
            seats_total = len(seats_data)
            i['Seats Available'] = seats_available
            i['Seats Taken'] = seats_taken
            i['Seats Total'] = seats_total
            context.bot.send_message(772520752, text=seats_available)
        except: 
            pass
            
    with open("C:\\Users\chuanan\Documents\grambots\spacey\\locations.csv", 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ",") 
        spamwriter.writerow(csv_columns)
        spamwriter = csv.DictWriter(csvfile, fieldnames=csv_columns) 
        spamwriter.writerows(results)
    
        
        
    

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
    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)
    spaceybot = MQBot('TOKENKKJ', request=request, mqueue=q)
    
    # Create the Updater and pass in bot's token.
    updater = Updater(bot=spaceybot, use_context = True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    

    # Create command handlers
    # dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("test_spacey_occupancy", test_spacey_occupancy))
    dp.add_handler(CommandHandler("test_spacey_details", test_spacey_details))
    
    # dp.add_handler(CallbackQueryHandler(check_location))
    # dp.add_handler(CallbackQueryHandler(check_occupancy))

    dp.add_handler(CommandHandler("test", test))

    dp.add_error_handler(error_callback)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),CommandHandler('notifications', notifications)],

        states={
            LOCATION: [CallbackQueryHandler(check_location)],
            CHECKWHAT: [CallbackQueryHandler(check_what)],
            SUBSCRIBE_MAIN: [CallbackQueryHandler(subscribe_main)],
            SUBSCRIBE_TYPE: [CallbackQueryHandler(subscribe_type)],
            SUBSCRIBE_LOCATION: [CallbackQueryHandler(subscribe_location)],
            UNSUBSCRIBE_TYPE: [CallbackQueryHandler(unsubscribe_type)]
        },

        fallbacks=[CommandHandler('start', start),CommandHandler('notifications', notifications)]
    )
    dp.add_handler(conv_handler)
    
    # Get job queue
    j = updater.job_queue

    # Set daily notifications
    t = datetime.time(2,27,00,000000)
    dp.add_handler(CallbackQueryHandler(daily_notifications))
    job_daily = j.run_daily(daily_notifications,t)

    # Set >80% notifications
    dp.add_handler(CallbackQueryHandler(full_notifications))
    job_minute1 = j.run_repeating(full_notifications, interval=600, first=0) #check and alert every 10 mins

    # Update seats occupancy
    dp.add_handler(CallbackQueryHandler(update_seats))
    job_minute2 = j.run_repeating(update_seats, interval=300, first=0) #run every 3 mins
    
    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

