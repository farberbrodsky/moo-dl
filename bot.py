from openwa import WhatsAPIDriver
from openwa.objects.message import MessageGroup
from openwa.objects.chat import Chat
from sys import exit
from time import sleep

driver = WhatsAPIDriver(profile="/home/misha/.mozilla/firefox/cbjepcbf.default")
driver.wait_for_login()
print("Bot started")

test_chat = [x for x in driver.get_all_chats() if x.id == "972542286434-1609678617@g.us"]

if len(test_chat) == 0:
    print("Can't find chat.")
    driver.close()
    exit(1)

test_chat = test_chat[0]
test_chat.send_message("Hello")
print("Done")
driver.close()
