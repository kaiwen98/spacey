from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import matplotlib.pyplot as plt
import telegram
import logging
import time;


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

def error_callback(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # logger.info("User {user} sent {message}".format(user=update.message.from_user.username, message=update.message.text))

bot = telegram.Bot(token="1165909865:AAEv_8NwFukQvWjcKb-WJzpntlhIjY193sw")
def start(update, context):
    """Send a message when the command /start is issued."""
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    update.message.reply_text('Hi '+ name+', type /help to learn more!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Welcome to Spacey! Find out the current seat occupancy using simple commands!\n"
                                "For example: /deck gives seat occupancy at the deck")

def deck(update, context):
    chat_id = update.message.from_user.id
    localtime = time.localtime(time.time())
    date = str(localtime.tm_mday)+'/'+str(localtime.tm_mon)+'/'+str(localtime.tm_year)
    time_now = str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
    labels = ['Occupied','Free']
    colors = ['Red','Green']
    sizes = [70, 30]
    explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Graph of seat occupancy at The Deck\nUpdated as of '+str(date)+" "+str(time_now))
    plt.savefig('testchart.png')
    
    bot.send_message(chat_id, text="<b>Seat Occupancy</b>: 350/500",parse_mode='HTML')
    bot.send_photo(chat_id, photo=open('C:\grambots\\testchart.png', 'rb'))
    
def test(update, context):
    """Send a message when the command /help is issued."""
    localtime = time.localtime(time.time())
    # update.message.reply_text()

def main():
    # Create the Updater and pass in bot's token.
    updater = Updater("1165909865:AAEv_8NwFukQvWjcKb-WJzpntlhIjY193sw", use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Create command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("deck", deck))
    dp.add_handler(CommandHandler("test", test))

    dp.add_error_handler(error_callback)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()


# python -m pip install python-telegram-bot