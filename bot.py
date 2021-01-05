from openwa import WhatsAPIDriver
from openwa.objects.chat import Chat
from lib import get_data, get_message
from sys import exit
import json, sched, time
from os import environ

driver = WhatsAPIDriver(environ["CLIENT"], environ["PROFILE"], headless=True)
driver.wait_for_login()
print("Bot started")

test_chat = [x for x in driver.get_all_chats() if x.id == environ["CHAT"]]

if len(test_chat) == 0:
    print("Can't find chat.")
    driver.close()
    exit(1)

test_chat = test_chat[0]

data = None
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    pass

def check_for_updates():
    global data
    current_data = get_data()
    if json.dumps(current_data, sort_keys=True) != json.dumps(data, sort_keys=True):
        # Different!
        data = current_data
        with open("data.json", "w") as f:
            json.dump(current_data, f)
        test_chat.send_message(get_message(current_data))
    scheduler.enterabs(time.time() + 1800, 0, check_for_updates)

scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enterabs(time.time() + 1, 0, check_for_updates)
scheduler.run()
