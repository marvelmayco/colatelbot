from decouple import config
import telebot
import os
import libtorrent as lt
import time
import re
import pickle
from tqdm import tqdm
from pathlib import Path


# Replace with your Telegram bot token
TELEGRAM_TOKEN = "6474896702:AAH3o6gmHK06yrHsaB0uAbGBaFoHLVYSnwQ"
CHAT_ID = "383694315"
#token = config("TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

ses = lt.session()
ses.listen_on(6881, 6891)

save_path = '/content/drive/MyDrive/Torrent Downloads/'

params = {
    'save_path': save_path,
    'storage_mode': lt.storage_mode_t.storage_mode_sparse,
}

magnet_link_pattern = r'^magnet:\?xt=urn:btih:[a-zA-Z0-9]*'

resume_data_file = os.path.join(save_path, 'resume_data.pickle')

def send_status(message_id, text):
  bot.edit_message_text(CHAT_ID, message_id=message_id, text=text)

if os.path.exists(resume_data_file):
    with open(resume_data_file, 'rb') as f:
        resume_data = pickle.load(f)
        for data in resume_data:
            ses.add_torrent(data)


@bot.message_handler(commands =  ["start"])
def enviar (message):
    bot.reply_to (message, "This is a bot which can mirror all your links to Google drive!\n"
                "Type /help to get a list of available commands")
    


@bot.message_handler(commands=["help"])
def enviar (message):
    bot.reply_to (message, """
    /mirrorMagnet
    """)

@bot.message_handler(func=lambda message:True)
def run(message):
        
    link= message.text
    mess = message.chat.id
    mess_id = message.message_id
    model_engine = "text-davinci-003"
    #link = input("Enter the magnet link: ")
    if re.match(magnet_link_pattern, link):
        handle = lt.add_magnet_uri(ses, link, params)
    else:
        initial_message = bot.reply_to(message, "Invalid magnet link format. Please try again.")
    if re.match(magnet_link_pattern, link):
        message = bot.reply_to(message, "\nDownloading Metadata...")
        #("\nDownloading Metadata...")
        while not handle.has_metadata():
            time.sleep(1)
        #print("Got Metadata, Starting Torrent Download...")
        bot.edit_message_text(chat_id=CHAT_ID, message_id=message.message_id, text="Got Metadata, Starting Torrent Download...")
        #bot.edit_message_text("Got Metadata, Starting Torrent Download...", mess, initial_message.message_id)

        torrent_info = handle.get_torrent_info()
      
        for i in range(torrent_info.num_files()):
            handle.file_priority(i, 1)

        file_size = torrent_info.total_size()
        file_size_mb = file_size / (1024 ** 2)
        file_size_gb = file_size / (1024 ** 3)
        #file_size_str = f"{file_size_mb:.2f} MB / {file_size_gb:.2f} GB"
        file_size_str = f"{file_size_gb:.2f} GB"
        #print(f"File size: {file_size_str}")
        #bot.send_message(mess, f"File size: {file_size_str}")

        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, leave=True)

        start_time = time.time()

        #message = None
        while handle.status().state != lt.torrent_status.seeding:
            s = handle.status()
            state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
            progress_bar.set_description(state_str[min(s.state, len(state_str)-1)])
            progress_bar.update(s.total_done - progress_bar.n)
            hmessage = f"\nTorrent Name: {torrent_info.name()}\n\nFile size: {file_size_str}\n\nDownload Progress: {s.progress * 100:.2f}%\n\nDownload Speed: {s.download_rate / 1000:.2f} KB/s"
            #bot.send_message(mess, hmessage)
            if message is None:
              message = bot.send_message(chat_id=CHAT_ID, text=hmessage)
            else:
              bot.edit_message_text(chat_id=CHAT_ID, message_id=message.message_id, text=hmessage)
            #send_status(message.message_id, hmessage)
            #bot.edit_message_text(message.message_id, hmessage)
            time.sleep(1)

        progress_bar.close()

        end_time = time.time()
        total_time_seconds = end_time - start_time
        total_time_minutes = total_time_seconds / 60

        num_files = torrent_info.num_files()

        bot.send_message(mess, f"\nFile name: {torrent_info.name()}")
        bot.send_message(mess, f"File size: {file_size_str}")
        bot.send_message(mess, f"Total Time: {total_time_seconds:.2f} seconds / {total_time_minutes:.2f} minutes")
        bot.send_message(mess, f"Number of files: {num_files}")
        bot.send_message(mess, f"Saved location: {save_path}")

    #return bot.send_message(mess, "Torrent Downloaded Successfully")

# save resume data
resume_data = []
for handle in ses.get_torrents():
    data = handle.save_resume_data()
    if data:
        resume_data.append({'resume_data': data, 'ti': handle.get_torrent_info(), 'save_path': save_path})
with open(resume_data_file, 'wb') as f:
    pickle.dump(resume_data, f)

bot.infinity_polling()
