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

def bytes_to_human_readable(size_bytes):
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

def get_progress_bar(percentage):
    bars = int(percentage / 5)
    return "█" * bars + "░" * (20 - bars)

def format_eta(seconds):
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def format_elapsed_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

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

@bot.message_handler(commands=["test"])
def enviar (message):
    mess = "<code>inline fixed-width code</code>"
    bot.reply_to (message, mess, parse_mode="HTML")

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
            downloaded = bytes_to_human_readable(s.total_done)
            total_size = bytes_to_human_readable(torrent_info.total_size())
            download_speed = bytes_to_human_readable(s.download_rate)
            progress_percentage = (s.total_done / torrent_info.total_size()) * 100
            progress_bar_t = get_progress_bar(progress_percentage)


            # Calculate elapsed time
            current_time = time.time()
            elapsed_time_seconds = current_time - start_time
            elapsed_time_formatted = format_elapsed_time(elapsed_time_seconds)

            # Calculate ETA
            remaining_bytes = torrent_info.total_size() - s.total_done
            download_speed_eta = s.download_rate
            if download_speed_eta > 0:
              eta_seconds = remaining_bytes / download_speed_eta
              eta_formatted = format_eta(eta_seconds)
            else:
              eta_formatted = "N/A"

            state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
            progress_bar.set_description(state_str[min(s.state, len(state_str)-1)])
            progress_bar.update(s.total_done - progress_bar.n)
            hmessage = f"\n<b>Uploading....</b>\n\n<pre>{torrent_info.name()}</pre>\n\n<code>{downloaded} of {total_size} done.</code>\n[{progress_bar_t}] <pre>({s.progress * 100:.2f}%)</pre>\n<code>Speed: {download_speed}/s</code>\n\n<code>Elapsed Time: {elapsed_time_formatted}</code>\n<code>ETA: {eta_formatted}</code>\n\n<i>Progress will be updated every 5 secs</i>\n"
            #bot.send_message(mess, hmessage)
            if message is None:
              message = bot.send_message(chat_id=CHAT_ID, text=hmessage)
            else:
              bot.edit_message_text(chat_id=CHAT_ID, message_id=message.message_id, text=hmessage, parse_mode="HTML")
            #send_status(message.message_id, hmessage)
            #bot.edit_message_text(message.message_id, hmessage)
            time.sleep(5)

        progress_bar.close()

        #end_time = time.time()
        #total_time_seconds = end_time - start_time
        #total_time_minutes = total_time_seconds / 60

        #num_files = torrent_info.num_files()

        # Torrent is seeding, send a final status update
        status = handle.status()
        downloaded = status.total_done
        total_size = torrent_info.total_size()
        progress_percentage = (downloaded / total_size) * 100
        progress_bar_t = get_progress_bar(progress_percentage)

        hmessage = f"\n\n<code>{torrent_info.name()}</code>\n\n<strong>Download Completed Successfully!!!</strong>"
        bot.edit_message_text(chat_id=CHAT_ID, message_id=message.message_id, text=hmessage, parse_mode="HTML")

        #bot.send_message(mess, f"\nFile name: {torrent_info.name()}")
        #bot.send_message(mess, f"File size: {file_size_str}")
        #bot.send_message(mess, f"Total Time: {total_time_seconds:.2f} seconds / {total_time_minutes:.2f} minutes")
        #bot.send_message(mess, f"Number of files: {num_files}")
        #bot.send_message(mess, f"Saved location: {save_path}")

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
