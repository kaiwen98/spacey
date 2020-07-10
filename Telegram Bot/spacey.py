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


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # logger.info("User {user} sent {message}".format(user=update.message.from_user.username, message=update.message.text))

bot = telegram.Bot(token=TOKEN)
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
        results.append([name,username,user_id,date,0,0])
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
        
        bot.send_message(user_id, text="<b>Seat Occupancy</b>: "+ str(seats_taken)+'/'+str(seats_total) + " ("+ str(seats_occupancy)+"%)",parse_mode='HTML')
        bot.send_photo(user_id, photo=open('C:\\Users\chuanan\Documents\grambots\spacey\\chart_'+str(location)+'.png', 'rb'))
    elif option == 'Operation Hours':
        bot.send_message(user_id, text=location_data[location]["Operation Hours"])
    else:
        latitude = location_data[location]['Latitude']
        longitude = location_data[location]['Longitude']
        address = location_data[location]['Address']
        bot.send_venue(user_id, latitude=latitude, longitude=longitude, title=location, address=address)
    # bot.send_message(user_id, text=location_data)
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
    
    bot.send_message(chat_id, text="<b>Seat Occupancy</b>: 350/500 ("+ str(350/500*100)+"%)",parse_mode='HTML')
    bot.send_photo(chat_id, photo=open('C:\\Users\chuanan\Documents\grambots\spacey\\testchart.png', 'rb'))

def test_spacey_details(update, context):
    chat_id = update.message.from_user.id
    bot.send_venue(chat_id, latitude=1.298726, longitude=103.775113, title='Spacey Cafe', address='31 Lower Kent Ridge Rd, Singapore 119078')  
    bot.send_message(chat_id, "<b><u>Operation Hours:</u></b>\n"+"Mon-Fri, 8.00am-8.00pm",parse_mode='HTML')

def test(update, context):
    chat_id = update.message.from_user.id
    for ix in range(10):
        context.bot.send_message(chat_id=chat_id, text='%s) %s' % (ix + 1, "msgt"))
    
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
                bot.send_message(user_id, text='You have not subscribed to notifications. Do you want to subscribe?',reply_markup=reply_markup)
                
            elif i[4]!='0' and i[5]=='0': #subscribed to daily only
                keyboard=[[InlineKeyboardButton('Subscribe to notifications whenever occupancy >80%', callback_data='Subscribe>80%')],
                            [InlineKeyboardButton('Unsubscribe from daily notifications', callback_data='Unsubscribedaily')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(user_id, text='You are currently subscribed to daily notifications (<b>'+ str(i[4]) + '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif i[4]=='0' and i[5]!='0':     #subscribed to >80% only
                keyboard=[[InlineKeyboardButton('Subscribe to daily notifications ', callback_data='Subscribedaily')],
                            [InlineKeyboardButton('Unsubscribe from >80% notifications', callback_data='Unsubscribe>80%')],
                            [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(user_id, text='You are currently subscribed to >80% notifications (<b>' +str(i[5])+ '</b>). What would you like to do?',reply_markup=reply_markup, parse_mode='HTML')
        
            elif i[4]!='0' and i[5]!='0': #subscribed to both
                keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribe')],[InlineKeyboardButton('Cancel', callback_data='Cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(user_id, text='You have subscribed to daily notifications (<b>'+ str(i[4]) + '</b>) and >80% notifications (<b>'+str(i[5])+ '</b>). Would you like to unsubscribe?',reply_markup=reply_markup, parse_mode='HTML')
        
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
        
        bot.send_message(user_id, text="Which notification would you like to subscribe to?", reply_markup=reply_markup)
        return SUBSCRIBE_TYPE

    elif query.data == 'Unsubscribe':
        keyboard=[[InlineKeyboardButton('Daily Notifications', callback_data='Unsubscribedaily')],
                    [InlineKeyboardButton('>80% Notifications', callback_data='Unsubscribe>80%')],
                    [InlineKeyboardButton('Both', callback_data='UnsubscribeBoth')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot.send_message(user_id, text="Which notification would you like to unsubscribe from?", reply_markup=reply_markup)
        return UNSUBSCRIBE_TYPE

    elif query.data == 'Unsubscribedaily':
        keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribedaily')],
                    [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot.send_message(user_id, text="Are you sure to unsubscribe from daily notifications?", reply_markup=reply_markup)
        return UNSUBSCRIBE_TYPE

    elif query.data == 'Unsubscribe>80%':
        keyboard=[[InlineKeyboardButton('Yes', callback_data='Unsubscribe>80%')],
                    [InlineKeyboardButton('Cancel', callback_data='Cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot.send_message(user_id, text="Are you sure to unsubscribe from >80% notifications?", reply_markup=reply_markup)
        return UNSUBSCRIBE_TYPE

    elif query.data == 'Cancel':
        bot.send_message(user_id, text="No changes were made")
        return ConversationHandler.END 

    else: #query.data == 'Subscribe>80%', 'Subscribedaily'
        context.user_data['subscribe_type'] = query.data
        locations_list = get_locations()
        keyboard=[]
        for location in locations_list:
            keyboard.append([InlineKeyboardButton(location, callback_data=location)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)    
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
    bot.send_message(user_id, text="Which location would you like to be notified?", reply_markup=reply_markup)
   
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

    bot.send_message(user_id, notification_type + ' for <b>' +query.data+ '</b> set!',parse_mode='HTML')
    
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
                location_removed = str(i[4]) + " and " + str(i[5])
                i[4] = 0
                i[5] = 0
                notification_type =  'Both notifications'
                

            elif query.data == 'Cancel':
                bot.send_message(user_id, 'No changes were made!')
                return ConversationHandler.END

    with open("C:\\Users\chuanan\Documents\grambots\spacey\\users_info.csv", 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ",") 
        for i in users_info_list:
            spamwriter.writerow(i)

    if notification_type == 'Both notifications':
        bot.send_message(user_id, notification_type+' for <b>'+location_removed+ '</b> removed!',parse_mode='HTML')
    else: 
        bot.send_message(user_id, notification_type + ' for <b>' +location_removed+ '</b> removed!',parse_mode='HTML')
    
    return ConversationHandler.END


def callback_day(context):
    chatid = '772520752'
    # print(msgt, chatid)
    for ix in range(10):
        context.bot.send_message(chat_id=chatid, text='%s) %s' % (ix + 1, '123'))

def callback_minute(context):
    chatid = '772520752'
    # print(msgt, chatid)
    for ix in range(10):
        context.bot.send_message(chat_id=chatid, text='%s) %s' % (ix + 1, 'asd'))

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
    # for test purposes limit global throughput to 3 messages per 3 seconds
    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)
    testbot = MQBot(TOKEN, request=request, mqueue=q)
    
    # Create the Updater and pass in bot's token.
    updater = Updater(bot=testbot, use_context = True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Get job queue
    j = updater.job_queue
    # Set daily notifications
    t = datetime.time(17,8,00,000000)

    job_daily = j.run_daily(callback_day,t)
    # Set >80% notifications
  
    

    
    dp.add_handler(CallbackQueryHandler(callback_minute))
    job_minute = j.run_repeating(callback_minute, interval=900, first=0) #run every 15mins

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
    
    
    #updater.dispatcher.add_handler(CallbackQueryHandler(location))
    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


