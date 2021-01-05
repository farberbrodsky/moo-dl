from openwa import WhatsAPIDriver
from openwa.objects.chat import Chat
from openwa.objects.message import Message
from lib import get_data as get_moodle_data, get_message as moodle_message
import sys, json, time
from os import environ
from datetime import datetime

driver = WhatsAPIDriver(
    client=environ["CLIENT"],
    profile=environ["PROFILE"],
    headless=True)
driver.wait_for_login()
time.sleep(1)
print("Bot started")

test_chat = [x for x in driver.get_all_chats() if x.id == environ["CHAT"]]

if len(test_chat) == 0:
    print("Can't find chat.")
    driver.close()
    sys.exit(1)

test_chat = test_chat[0]

memory = {}
try:
    with open("memory.json", "r") as f:
        memory = json.load(f)
except BaseException:
    pass


def save_memory():
    with open("memory.json", "w") as f:
        json.dump(memory, f)


memory["moodle_data"] = memory.get("moodle_data", {})
memory["moodle_last_sent"] = memory.get("moodle_last_sent", 0)

save_memory()


def get_moodle_current_data():
    global memory
    moodle_data = memory["moodle_data"]
    if not moodle_data or moodle_data["timestamp"] <= (time.time() - 1800):
        moodle_data = memory["moodle_data"] = get_moodle_data()
        save_memory()
    return moodle_data


def got_message(message):
    global memory
    msg = message.messages[0]
    if isinstance(msg, Message):
        print(msg.content)
        if not msg.content.startswith("מישה "):
            return
        command = msg.content[5:]

        if command == "לולי":
            driver.chat_send_message(msg.chat_id, "no")
        elif command == "מודל":
            driver.chat_send_message(
                msg.chat_id, moodle_message(
                    get_moodle_current_data()
                ))


while True:
    unread_messages = driver.get_unread()
    for message in unread_messages:
        try:
            got_message(message)
        except Exception as e:
            print("ERROR", repr(e))

    now = datetime.now()
    prev_moodle_date = datetime.fromtimestamp(memory["moodle_last_sent"])
    if now.hour == 8 and \
       prev_moodle_date.strftime("%d/%m/%Y") != now.strftime("%d/%m/%Y"):
        # Send a moodle message at 8am
        memory["moodle_last_sent"] = time.time()
        save_memory()
        driver.chat_send_message(
            test_chat, moodle_message(
                get_moodle_current_data()
            )
        )
