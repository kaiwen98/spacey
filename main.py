from os.path import dirname, abspath, join
import sys
root = dirname(abspath(__file__))
sys.path.append(join(root, "Server"))
sys.path.append(join(root, "Server", "Telegram_Bot_Spacey"))
from Server.Telegram_Bot_Spacey import test

if __name__ == "__main__":
    test.main()