from openwa import WhatsAPIDriver
from openwa.objects.chat import Chat
from lib import get_data, get_message
from sys import exit

driver = WhatsAPIDriver(profile="/home/misha/.mozilla/firefox/cbjepcbf.default")
driver.wait_for_login()
print("Bot started")

test_chat = [x for x in driver.get_all_chats() if x.id == "972542286434-1609678617@g.us"]

if len(test_chat) == 0:
    print("Can't find chat.")
    driver.close()
    exit(1)

test_chat = test_chat[0]

message = get_message(get_data())

test_chat.send_message(message)
print("Done")
driver.close()
