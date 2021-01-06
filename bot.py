from openwa import WhatsAPIDriver
from openwa.objects.chat import Chat
from openwa.objects.message import Message, MediaMessage
from openwa.helper import convert_to_base64
from lib import get_data as get_moodle_data, get_message as moodle_message
import sys, json, time, io, math
from PIL import Image, ImageFont, ImageDraw
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


def draw_text(img, text, top=True):
    font = ImageFont.truetype("./font.ttf", 80)
    draw = ImageDraw.Draw(img)
    draw.text((256, 5 if top else 507), text, font=font, fill=(255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0), anchor=("mt" if top else "mb"), direction="rtl")

def got_message(message):
    global memory
    msg = message.messages[0]

    if isinstance(msg, MediaMessage):
        command = msg.caption
    else:
        command = msg.content

    if not command.startswith("מישה "):
        return
    command = command[5:]
    command_words = command.split(" ")
    command_first_word = command_words[0]

    if command_first_word == "מודל":
        driver.chat_send_message(
            msg.chat_id, moodle_message(
                get_moodle_current_data()
            ))
    elif command_first_word == "סטיקר":
        if isinstance(msg, MediaMessage):
            img = Image.open(driver.download_media(msg, force_download=True))
            # Resize image
            if img.width > img.height:
                result_width = 512
                result_height = math.floor(img.height * (512 / img.width))
            else:
                result_height = 512
                result_width = math.floor(img.width * (512 / img.height))
            resized = img.resize((result_width, result_height)).convert("RGBA")
            sticker_img = Image.new("RGBA", (512, 512))
            sticker_img.paste(resized, ((512 - result_width) // 2, (512 - result_height) // 2))
            # Potentially add text
            semicolon_seperated = " ".join(command_words[1:]).split(";")
            if len(semicolon_seperated) != 0 and semicolon_seperated[0] != "":
                # draw text
                draw_text(sticker_img, semicolon_seperated[0], top=True)
                if len(semicolon_seperated) >= 2:
                    draw_text(sticker_img, semicolon_seperated[1], top=False)
            # Send result image
            webp_img = io.BytesIO()
            sticker_img.save(webp_img, "webp")
            webp_img.seek(0)
            img_base_64 = convert_to_base64(webp_img, is_thumbnail=True)
            return driver.wapi_functions.sendImageAsSticker(img_base_64, msg.chat_id, {})
        else:
            driver.chat_send_message(msg.chat_id, "אין פה תמונה")
    elif command_first_word == "מידע":
        driver.chat_send_message(msg.chat_id, """היי אני הבוט של מישה!
הפקודות שלי הן:
1. מישה סטיקר טקסט עליון;טקסט תחתון
2. מישה מודל - נותן את ההגשות של התרגילים במודל""")


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
