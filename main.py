from os.path import dirname, abspath, join
import sys
root = dirname(abspath(__file__))
sys.path.append(join(root, "Server"))
sys.path.append(join(root, "Server", "Telegram_Bot_Spacey"))
from Server.Telegram_Bot_Spacey import botw
from Server.Telegram_Bot_Spacey import spacey
from Server.Telegram_Bot_Spacey import spacey2

if __name__ == "__main__":
    spacey2.main()