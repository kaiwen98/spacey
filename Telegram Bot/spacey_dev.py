from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
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

bot = telegram.Bot(token="1165909865:AAEv_8NwFukQvWjcKb-WJzpntlhIjY193sw")
LOCATION, CHECKWHAT= range(2)

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
        results.append([name,username,user_id,date,0])
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
    #results = getcsv()
    #update.message.reply_text(results)
    #chat_type = update.message.chat.type
    
    #bot.send_message(772520752, "<b>SUCK MY KUKUJIAO</b>",parse_mode='HTML')
    # keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
    #          InlineKeyboardButton("Option 2", callback_data='2')],
    #       [InlineKeyboardButton("Option 3", callback_data='3')]]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)

def main():
    # Create the Updater and pass in bot's token.
    updater = Updater("1165909865:AAEv_8NwFukQvWjcKb-WJzpntlhIjY193sw", use_context=True)
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
        entry_points=[CommandHandler('start', start)],

        states={
            LOCATION: [CallbackQueryHandler(check_location, pass_user_data=True)],

            CHECKWHAT: [CallbackQueryHandler(check_what)]
        },

        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)
    
    
    #updater.dispatcher.add_handler(CallbackQueryHandler(location))
    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


# python -m pip install python-telegram-bot
# pip install -r requirements.txt
