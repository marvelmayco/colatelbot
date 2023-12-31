from decouple import config
import telebot
import os, subprocess, psutil
import libtorrent as lt
import time
import re
import pickle
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from os import makedirs, path as ospath
from IPython.display import clear_output


# Replace with your Telegram bot token
TELEGRAM_TOKEN = "6474896702:AAH3o6gmHK06yrHsaB0uAbGBaFoHLVYSnwQ"
CHAT_ID = "383694315"
#token = config("TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
caution_msg = "\n\n<i>💖 When I'm Doin This, Do Something Else ! <b>Because, Time Is Precious ✨</b></i>"

ses = lt.session()
ses.listen_on(6881, 6891)

save_path = '/content/drive/Shareddrives/#104/MyBot_Downloads/'
current_time = []
current_time.append(time.time())

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
    bars = int(percentage / 10)
    return "⬛" * bars + "⬜" * (10 - bars)

def sysINFO():
    ram_usage = psutil.Process(os.getpid()).memory_info().rss
    disk_usage = psutil.disk_usage("/")
    cpu_usage_percent = psutil.cpu_percent()

    string = "\n\n⌬─────「 Colab Usage 」─────⌬\n"
    string += f"\n╭🖥️ <b>CPU Usage »</b>  <i>{cpu_usage_percent}%</i>"
    string += f"\n├💽 <b>RAM Usage »</b>  <i>{sizeUnit(ram_usage)}</i>"
    string += f"\n╰💾 <b>DISK Free »</b>  <i>{sizeUnit(disk_usage.free)}</i>"
    string += caution_msg

    return string

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


def get_Aria2c_Name(link):
    cmd = f'aria2c -x10 --dry-run --file-allocation=none "{link}"'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    stdout_str = result.stdout.decode("utf-8")
    filename = stdout_str.split("complete: ")[-1].split("\n")[0]
    name = filename.split("/")[-1]
    if len(name) == 0:
        name = "UNKNOWN DOWNLOAD NAME"
    return name

def getTime(seconds):
    seconds = int(seconds)
    days = seconds // (24 * 3600)
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def sizeUnit(size):
    if size > 1024 * 1024 * 1024 * 1024 * 1024:
        siz = f"{size/(1024**5):.2f} PiB"
    elif size > 1024 * 1024 * 1024 * 1024:
        siz = f"{size/(1024**4):.2f} TiB"
    elif size > 1024 * 1024 * 1024:
        siz = f"{size/(1024**3):.2f} GiB"
    elif size > 1024 * 1024:
        siz = f"{size/(1024**2):.2f} MiB"
    elif size > 1024:
        siz = f"{size/1024:.2f} KiB"
    else:
        siz = f"{size} B"
    return siz


def fileType(file_path: str):
    extensions_dict = {
        ".mp4": "video",
        ".avi": "video",
        ".mkv": "video",
        ".m2ts": "video",
        ".mov": "video",
        ".webm": "video",
        ".vob": "video",
        ".m4v": "video",
        ".mp3": "audio",
        ".wav": "audio",
        ".flac": "audio",
        ".aac": "audio",
        ".ogg": "audio",
        ".jpg": "photo",
        ".jpeg": "photo",
        ".png": "photo",
        ".bmp": "photo",
        ".gif": "photo",
    }
    _, extension = ospath.splitext(file_path)

    if extension.lower() in extensions_dict:
        return extensions_dict[extension]
    else:
        return "document"


def shortFileName(path):
    if ospath.isfile(path):
        dir_path, filename = ospath.split(path)
        if len(filename) > 60:
            basename, ext = ospath.splitext(filename)
            basename = basename[: 60 - len(ext)]
            filename = basename + ext
            path = ospath.join(dir_path, filename)
        return path
    elif ospath.isdir(path):
        dir_path, dirname = ospath.split(path)
        if len(dirname) > 60:
            dirname = dirname[:60]
            path = ospath.join(dir_path, dirname)
        return path
    else:
        if len(path) > 60:
            path = path[:60]
        return path


def getSize(path):
    if ospath.isfile(path):
        return ospath.getsize(path)
    else:
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = ospath.join(dirpath, f)
                total_size += ospath.getsize(fp)
        return total_size

def isTimeOver(current_time):
    ten_sec_passed = time.time() - current_time[0] >= 3
    if ten_sec_passed:
        current_time[0] = time.time()
    return ten_sec_passed


def speedETA(start, done, total):
    percentage = (done / total) * 100
    percentage = 100 if percentage > 100 else percentage
    elapsed_time = (datetime.now() - start).seconds
    if done > 0 and elapsed_time != 0:
        raw_speed = done / elapsed_time
        speed = f"{sizeUnit(raw_speed)}/s"
        eta = (total - done) / raw_speed
    else:
        speed, eta = "N/A", 0
    return speed, eta, percentage

def status_bar(down_msg, speed, percentage, eta, done, left, engine):
    bar_length = 12
    filled_length = int(percentage / 100 * bar_length)
    # bar = "⬢" * filled_length + "⬡" * (bar_length - filled_length)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    if is_it_magnetlink:
      message = (
          f"\n╭「{bar}」 <b>»</b> <i>{percentage:.2f}%</i>\n├⚡️ <b>Speed »</b> <i>{speed}</i>\n├⚙️ <b>Engine »</b> <i>{engine}</i>"
          + f"\n├⏳ <b>Time Left »</b> <i>{eta}</i>"
          + f"\n├🍃 <b>Time Spent »</b> <i>{getTime((datetime.now() - start_time).seconds)}</i>"
          + f"\n├🦧 <b>Peers »</b> <i>{peers_list}</i> <b> & </b>🦉 <b>Seeders »</b> <i>{seeds_list}</i>"
          + f"\n├✅ <b>Processed »</b> <i>{done}</i>\n╰📦 <b>Total Size »</b> <i>{left}</i>"
      )
    else:
      message = (
          f"\n╭「{bar}」 <b>»</b> <i>{percentage:.2f}%</i>\n├⚡️ <b>Speed »</b> <i>{speed}</i>\n├⚙️ <b>Engine »</b> <i>{engine}</i>"
          + f"\n├⏳ <b>Time Left »</b> <i>{eta}</i>"
          + f"\n├🍃 <b>Time Spent »</b> <i>{getTime((datetime.now() - start_time).seconds)}</i>"
          + f"\n├✅ <b>Processed »</b> <i>{done}</i>\n╰📦 <b>Total Size »</b> <i>{left}</i>"
      )
    sys_text = sysINFO()
    try:
        print(f"\r{engine} ║ {bar} ║ {percentage:.2f}% ║ {speed} ║ ⏳ {eta}", end="")
        # Edit the message with updated progress information.
        if isTimeOver(current_time):
            bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=mssg_id,  # type: ignore
                text=down_msg + message + sys_text,
                parse_mode="HTML"
            )

    except Exception as e:
        # Catch any exceptions that might occur while editing the message.
        print(f"Error Updating Status bar: {str(e)}")

def on_output(output: str):
    # print("=" * 60 + f"\n\n{output}\n\n" + "*" * 60)
    global link_info, d_total_size, peers_list, seeds_list
    total_size = "0B"
    progress_percentage = "0B"
    downloaded_bytes = "0B"
    eta = "0S"
    
    try:
        if "ETA:" in output:
            parts = output.split()
            total_size = parts[1].split("/")[1]
            total_size = total_size.split("(")[0]
            progress_percentage = parts[1][parts[1].find("(") + 1 : parts[1].find(")")]
            downloaded_bytes = parts[1].split("/")[0]
            eta = parts[4].split(":")[1][:-1]

            # Iterate through the parts to find the values
            for part in parts:
              if part.startswith('CN:'):
                  peers_list = part[3:]
              elif part.startswith('SD:'):
                  seeds_list = part[3:]
    except Exception as do:
        print(f"Could't Get Info Due to: {do}")

    #final_total_size = total_size
    percentage = re.findall("\d+\.\d+|\d+", progress_percentage)[0]  # type: ignore
    down = re.findall("\d+\.\d+|\d+", downloaded_bytes)[0]  # type: ignore
    down_unit = re.findall("[a-zA-Z]+", downloaded_bytes)[0]
    if "G" in down_unit:
        spd = 3
    elif "M" in down_unit:
        spd = 2
    elif "K" in down_unit:
        spd = 1
    else:
        spd = 0

    elapsed_time_seconds = (datetime.now() - start_time).seconds

    if elapsed_time_seconds >= 270 and not link_info:
        raise Exception("Failed to get download information ! Probably dead link 💀")
    # Only Do this if got Information
    if total_size != "0B":
        # Calculate download speed
        link_info = True
        d_total_size = total_size
        current_speed = (float(down) * 1024**spd) / elapsed_time_seconds
        speed_string = f"{sizeUnit(current_speed)}/s"

        status_bar(
            down_msg,
            speed_string,
            int(percentage),
            eta,
            downloaded_bytes,
            total_size,
            "Aria2c 🧨",
        )

def aria2_Download(link):

    aria2_dn = f"<b>PLEASE WAIT ⌛</b>\n\n<i>Getting Download Info For</i>\n\n<code>{link}</code>"
    try:
        bot.edit_message_text(
            chat_id=CHAT_ID,
            message_id=mssg_id,  # type: ignore
            text=aria2_dn + sysINFO(),
            parse_mode="HTML"
        )
    except Exception as e1:
        print(f"Couldn't Update text ! Because: {e1}")

    global start_time, down_msg, name_d, link_info
    link_info = False
    name_d = get_Aria2c_Name(link)
    start_time = datetime.now()
    link_hyper = f'<a href="{link}">{name_d}</a>'
    down_msg = f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link » {link_hyper}</i>\n\n<b>🏷️ Name » </b><code>{name_d}</code>\n"

    # Create a command to run aria2p with the link
    command = [
        "aria2c",
        "-x8",
        "--seed-time=0",
        "--summary-interval=1",
        "--max-tries=3",
        "--console-log-level=notice",
        "-d",
        save_path,
        link,
    ]

    # Run the command using subprocess.Popen
    proc = subprocess.Popen(
        command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Read and print output in real-time
    while True:
        output = proc.stdout.readline()  # type: ignore
        if output == b"" and proc.poll() is not None:
            break
        if output:
            # sys.stdout.write(output.decode("utf-8"))
            # sys.stdout.flush()
            on_output(output.decode("utf-8"))

    # Retrieve exit code and any error output
    exit_code = proc.wait()
    error_output = proc.stderr.read()  # type: ignore
    if exit_code != 0:
        if exit_code == 3:
            raise Exception(f"The Resource was Not Found in {link}")
        elif exit_code == 9:
            raise Exception(f"Not enough disk space available")
        elif exit_code == 24:
            raise Exception(f"HTTP authorization failed.")
        else:
            raise Exception(
                f"aria2c download failed with return code {exit_code} for {link}.\nError: {error_output}"
            )
        
    

def FinalStep(msg, is_leech: bool):

    """
    final_text = (
        f"<b>☘️ File Count:</b>  <code>{len(sent_file)}</code>\n\n<b>📜 Logs:</b>\n"
    )
    l_ink = "⌬─────[「 Colab Usage 」](https://colab.research.google.com/drive/12hdEqaidRZ8krqj7rpnyDzg1dkKmvdvp)─────⌬"

    file_count = (
        f"├<b>☘️ File Count » </b><code>{len(sent_file)} Files</code>\n"
        if is_leech
        else ""
    )
    

    size = sizeUnit(sum(up_bytes)) if is_leech else sizeUnit(total_down_size)
    """

    last_text = (
        f"\n\n<b>🔥 DOWNLOAD_COMPLETED 🔥</b>\n\n"
        + f"╭<b>📛 Name » </b><code>{name_d}</code>\n"
        + f"├<b>📦 Size » </b><code>{d_total_size}</code>\n"
        #+ file_count
        + f"╰<b>🍃 Saved Time »</b> <code>{getTime((datetime.now() - start_time).seconds)}</code>"
    )

    bot.edit_message_text(
        chat_id=CHAT_ID,
        message_id=msg.id,
        text=last_text,
        parse_mode="HTML"
    )

    """
    if is_leech:
        try:
            final_texts = []
            for i in range(len(sent_file)):
                file_link = f"https://t.me/c/{link_p}/{sent_file[i].id}"
                fileName = sent_fileName[i]
                fileText = f"\n({str(i+1).zfill(2)}) <a href={file_link}>{fileName}</a>"
                if len(final_text + fileText) >= 4096:
                    final_texts.append(final_text)
                    final_text = fileText
                else:
                    final_text += fileText
            final_texts.append(final_text)

            for fn_txt in final_texts:
                msg = bot.send_message(
                    chat_id=chat_id, reply_to_message_id=msg.id, text=fn_txt
                )
        except Exception as e:
            Err = f"<b>Error Sending logs » </b><i>{e}</i>"
            Err += f"\n\n<i>⚠️ If You are Unknown with this <b>ERROR<b>, Then Forward This Message in [Colab Leecher Discussion](https://t.me/Colab_Leecher_Discuss) Where [Xron Trix](https://t.me/XronTrix) may fix it</i>"
            bot.send_message(
                chat_id=chat_id, reply_to_message_id=msg.id, text=Err
            )
      """
    

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
    clear_output()
    link= message.text
    global mssg_id, link_info, is_it_magnetlink
    is_it_magnetlink = False


    down_msg = f"<b>📥 DOWNLOADING » </b>\n"
    while True:
        try:
            message = bot.reply_to(message,
                        text=down_msg
                        + f"\n📝 <i>Starting DOWNLOAD...</i>"
                        + sysINFO(),
                        parse_mode="HTML"
                    )
        except Exception as e:
            pass
        else:
            break

    mssg_id = message.message_id
    
    if re.match(magnet_link_pattern, link):
        is_it_magnetlink = True
        handle = lt.add_magnet_uri(ses, link, params)
    else:
        aria2_Download(link)


    if re.match(magnet_link_pattern, link):
        #message = bot.reply_to(message, "\nDownloading Metadata...")
        #("\nDownloading Metadata...")
        while not handle.has_metadata():
            time.sleep(1)
        trnt_dn = f"<b>PLEASE WAIT ⌛</b>\n\n<i>Getting Download Info For</i>\n\n<code>{link}</code>"
        try:
            bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=mssg_id,  # type: ignore
                text=trnt_dn + sysINFO(),
                parse_mode="HTML"
            )
        except Exception as e1:
            print(f"Couldn't Update text ! Because: {e1}")

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
            hmessage = f"\n<b>Uploading....</b>\n\n<pre>{torrent_info.name()}</pre>\n\n<code>{downloaded} of {total_size} done.</code>\n<code>|</code>{progress_bar_t}<code>|</code> <pre>({s.progress * 100:.2f}%)</pre>\n<code>Speed: {download_speed}/s</code>\n\n<code>Elapsed Time: {elapsed_time_formatted}</code>\n<code>ETA: {eta_formatted}</code>\n\n<i></i>\n"
            #bot.send_message(mess, hmessage)
            if message is None:
              message = bot.send_message(chat_id=CHAT_ID, text=hmessage)
            else:
              bot.edit_message_text(chat_id=CHAT_ID, message_id=message.message_id, text=hmessage, parse_mode="HTML")
            #send_status(message.message_id, hmessage)
            #bot.edit_message_text(message.message_id, hmessage)
            time.sleep(1)

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
    
    FinalStep(message, False)

# save resume data
resume_data = []
for handle in ses.get_torrents():
    data = handle.save_resume_data()
    if data:
        resume_data.append({'resume_data': data, 'ti': handle.get_torrent_info(), 'save_path': save_path})
with open(resume_data_file, 'wb') as f:
    pickle.dump(resume_data, f)

bot.infinity_polling()
