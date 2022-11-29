import feedparser
from threading import Thread, Event
from qbittorrent import Client
import os, sys, time, requests

# Please change the following variables to your own settings

class settings:
    delete_torrents_afterwards = False                      # Delete torrents after they are no longer in the RSS search results
    auto_encode = True                                      # Set to True if you want to automatically encode the torrents (otherwise it'll just copy the file to the targer directory)
    lang = "french"                                         # Language you want the subtitles to be
    suffix = "vostfr"                                       # Episode name will be in this format : {anime_name}.s1e{episode_number}.{suffix}.mp4, Change this to whatever you want
    quality = "1080p"                                       # Video quality of the torrents
    handbrake_settings = f"-vfr -e x264 -b 2500 -E av_aac -B 512 -T -2 -O --subtitle-lang-list {lang} --subtitle-burn"  # HandBrakeCLI settings
    target_directory = "/animes/output/directory"           # This should be the directory where animes will be stored, please note that the sctipt will create a subfolder in this directory named "anime"
    torrents_location = "/animes/torrent/directory"         # Episodes files should be in this directory, please configure your qBittorrent Web UI
    linuxuser = "user"                                      # Linux user who will get the acces rights to the files
    user = "admin"                                          # Username of your qBittorrent Web UI
    password = "adminadmin"                                 # Password for the Web ui
    webui_link = "http://localhost:8080"                    # Change "https://link-to-my-web.ui:PORT" to your actual web domain, please note that you can also use "http://localhost:8080" if you don't have a domain name
    rss_link = "https://nyaa.si/?page=rss&u=Tsundere-Raws"  # Just remove the "()" and run the script

request_count = 0                           # Do not modify the following lines
rss_search_results = []
last_torrent_proceed = None
source_rss = []
qb = Client(settings.webui_link)
start_time = time.time()
crash = False
fail_count = 0

print("\033[1;96mCanalBot v0.6.1\033[0m")

class txt:

    def __init__(self, file_name, type):
        self.file_name = file_name
        self.type = type
        txt.load_data(self)
        self.len = len(self.data)

    def read_txt_to_list_of_lists(self):
        temp = open(self.file_name, "r")
        return list(x.split(", ") for x in temp.read().split("\n"))

    def read_txt_to_list(self):
        try:
            temp = open(self.file_name, "r")
        except FileNotFoundError:
            temp = open(self.file_name, "x")
            temp = open(self.file_name, "r")
        return list(temp.read().split("\n"))

    def load_data(self):
        if self.type == 1:                                              # Type = 1 -> anime_list.txt
            self.data = self.read_txt_to_list_of_lists()
            self.keywords = list(anime[0] for anime in self.data)
        elif self.type == 2:                                            # Type = 2 -> processed_list.txt
            self.data = self.read_txt_to_list()

    def get_info(self, file_name):
        for anime in self.data:
            if anime != ['']:
                if file_name.find(anime[0]) != -1:
                    return anime[0], anime[1], anime[2], anime[3]
        return None

    def check_if_on_the_list(self, file_name):
        for anime in self.data:
            if anime != ['']:
                if file_name.find(anime[0]) != -1:
                    return True
        return False

    def write_to_txt(self):
        list = '\n'.join(self.data)
        temp = open(self.file_name, "w")
        temp.write(list)

    def clean_torrent_list(self, file_name):
        nb = 0
        for torrent in self.data:
            if torrent == file_name:
                self.data.pop(nb)
            nb += 1
        self.write_to_txt()

    def check_if_processed(self, file_name):
        for torrent in self.data:
            if file_name == torrent:
                return True
        return False


def index_verify(file_name, index):                                     # Theses three following index_things functions work together and return the position of the index of the file (Here used to search " - ")
    try:                                                                # It finds the first occurence of the index, then verify it by trying to int() the two next characters (the two next characters being the episode number)
        int(file_name[index + 1:index + 3])
        return True
    except ValueError:
        return False

def find_index(file_name, index, number):
    start = file_name.find(index)
    while start >= 0 and number > 1:
        start = file_name.find(index, start+len(index))
        number -= 1
    return start

def search_index(file_name):
    for i in range(1, 5):
        if index_verify(file_name, find_index(file_name, "S", i)):
            return find_index(file_name, "S", i)

def check_if_added(index, keyword, ep_number):
        check = False
        for torrent in qb.torrents():
            torrent_name = torrent['name']
            if torrent_name.find(keyword) != -1:
                if torrent_name[index + 4:index + 6] == ep_number:
                    check = True
        return check

def rss_search(keyword, quality):
    entries = source_rss.entries
    found = False
    entry_number = -1                                                                                           # -1 to start at the first result (because even before searching, we add 1 to entry_number)
    for entry in entries:
        entry_number += 1
        if entry.title.find(keyword) != -1:                                                                     # Searching for a torrent with a corresponding keyword
            rss_torrent_title = entries[entry_number].title
            if rss_torrent_title.find(quality) != -1 and rss_torrent_title.find('VOSTFR') != -1:                                                 # Then search for the right quality
                torrent_index = search_index(rss_torrent_title)
                # print("rss_torrent_title :", rss_torrent_title)
                # print("torrent_index :", torrent_index)
                # print("keyword :", keyword)
                #print(f'check_if_added("{torrent_index}", "{keyword}", "{rss_torrent_title[torrent_index + 4:torrent_index + 6]}")')
                if torrent_index != None :
                    if check_if_added(torrent_index, keyword, rss_torrent_title[torrent_index + 4:torrent_index + 6]) == False:
                        qb.download_from_link(entries[entry_number].link)
                        rss_search_results.append(entries[entry_number].title)
                        print(f'\033[1;96m\033[1mFound : "{entries[entry_number].title}"\033[0m, torrent successfully added')
                    else:
                        print(f'\033[90mTorrent "{rss_torrent_title}" have already been added..\033[0m')
                        rss_search_results.append(source_rss.entries[entry_number].title)
                    found = True
    if found == False:
        not_found.append(keyword)

def clean_torrents():
    delete_list = list(set(previous_rss_search_results) - set(rss_search_results))
    if len(delete_list) == 0:
        print("\033[90mNo torrent to delete\033[0m")
    else:
        for anime_torrent in delete_list:
            torrent_index = search_index(anime_torrent)
            anime_name, ep_number = anime_torrent[0:torrent_index - 1], anime_torrent[torrent_index + 2:torrent_index + 6]
            print("anime_name :", anime_name)   # DEBUG
            print("ep_number :", ep_number)     # DEBUG
            for torrent in torrents_info:
                torrent_file_name, hash = torrent['name'], torrent['hash']
                if torrent_file_name.find(anime_name) != -1 and torrent_file_name.find(ep_number) != -1:
                    print("torrent_file_name :", torrent_file_name)
                    print(f'\033[1;91mDeleting "{torrent_file_name}"\n\033[0m')
                    # qb.delete_permanently(hash)
                    processed_list.clean_torrent_list(torrent_file_name)

def rss_request():
    print("\n\033[93mCollecting RSS feed..\033[0m")
    success = False
    global crash
    while success == False:
        try:
            feed_request = requests.get(settings.rss_link, timeout=20.0)
            print("\033[1;92mRSS link successfully retrieved\033[0m")
            success, crash = True, False
            feed = feedparser.parse(feed_request.content)
            return feed
        except:
            print("\033[1;91mError while retrieving RSS feed, next try in 10 seconds\033[0m")
            wait(10)

def qb_request():
    print("\n\033[93mConnection Request to qBittorrent WebUI\033[0m")
    success = False
    global crash
    while success == False:
        try:
            qb.login(settings.user, settings.password)
            print("\033[1;92mConnection to qBittorrent WebUI successfully established\033[0m")
            success, crash = True, False
        except:
            print("\033[1;91mError while connecting to qBittorrent Web UI, next try in 5 minutes.\033[0m")
            crash = True
            wait(300)


def time_calculation(time_in_seconds):
    days = time_in_seconds // 86400
    hours = (time_in_seconds - (86400 * days)) // 3600
    minutes = (time_in_seconds - (86400 * days) - (3600 * hours)) // 60
    seconds = time_in_seconds - (86400 * days) - (3600 * hours) - (60 * minutes)
    if days == 0 and hours == 0:
        if seconds < 10:
            seconds = f"0{seconds}"
        return f'{minutes} min {seconds} sec'
    elif days == 0:
        return f'{hours}h {minutes}min'
    else:
        return f'{days}d {hours}h {minutes}min'

def wait(seconds):
    for remaining_seconds in range(seconds):
        sys.stdout.write(f"\033[90mTime remaining : {time_calculation(seconds - remaining_seconds)}\033[0m                                                   ")
        sys.stdout.write("\r")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r                                                   \r")
    sys.stdout.flush()

def search_for_new_torrents():
    global crash
    crash = False
    try:
        for keyword in anime_list.keywords:
            if keyword != "":
                rss_search(keyword, settings.quality)
    except:
        crash = True
        # print("\033[1;91mError while searching for new torrents / Error while retrieving Torrents info from the qBittorrent Web UI\033[0m")
        # Line above commented because the error can appears when no crash has happen (likely because the request() function takes a bit of time to execute sometimes)

def timeout_search():   # I need to get rid of this function
    stop_event = Event()
    action_thread = Thread(target=search_for_new_torrents)
    action_thread.start()
    action_thread.join(timeout=10)
    stop_event.set()

if __name__ == "__main__":
    qb_request()
    anime_list = txt("anime_list.txt", 1)
    processed_list = txt("processed_list.txt", 2)

    while True:     # Main infinite loop start
        anime_list.load_data()
        processed_list.load_data()

        if crash == True:
            qb_request()

        source_rss = rss_request()

        if len(source_rss) == 7:          # did some tests, and lenght = 7 if RSS request success
            request_count += 1
            not_found = []
            encode = False

            if crash == False:
                previous_rss_search_results = rss_search_results
                rss_search_results = []

            print("\033[1mLast torrent added in the RSS feed\033[0m :", source_rss.entries[0].title)
            timeout_search()

            if crash == False:
                not_found_list = ', '.join(not_found)
                if len(not_found_list) != 0:
                    print("No results for :", not_found_list)
                try:
                    torrents_info = qb.torrents()
                except:
                    print("\033[1;91mError while retrieving Torrents info from the qBittorrent Web UI\033[0m")
                    crash = True

            if last_torrent_proceed != None:
                print("\033[92mLast torrent proceed\033[0m :", last_torrent_proceed)

            if request_count != 1:
                print("Total run time :", time_calculation(round((time.time() - start_time))))

            if crash == False:
                    for torrent in torrents_info:
                        file_name = torrent['name']
                        if file_name.find(settings.rss_link[28:-1]) != -1 and not processed_list.check_if_processed(file_name) and anime_list.check_if_on_the_list(file_name):
                            if torrent['state'] != 'downloading' and torrent['state'] != 'stalledDL':
                                file_info = anime_list.get_info(file_name)                                              # Get infos from anime_list.txt
                                anime_name = file_info[3]
                                index_rank = search_index(file_name)
                                episode_number = file_name[index_rank + 4:index_rank + 6]
                                input_file_name = file_name.replace(" ", "\ ").replace("(", "\(").replace(")", "\)").replace("\'", "\\'")    # Small changes needed in order to match the syntax of a file name in a linux command 
                                point_name = anime_name.replace(" ", ".")
                                output_file_name = f"{point_name}.s{file_info[2]}e{episode_number}.{settings.suffix}"

                                if settings.auto_encode == True:    # Encoding the file
                                    os.system(f"mkdir -p {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}")    # Create a folder for the output file, if wasn't already
                                    if os.path.exists(f"{settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mp4'}"):
                                        print(f"\033[35mSkipping encoding for {file_name} : output file already exists\033[0m")
                                    else:
                                        print(f"\033[96mEncoding {file_name} to {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mp4'}\033[0m..")
                                        os.system(f"HandBrakeCLI -i {settings.torrents_location}/{input_file_name} -o {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mp4'} {settings.handbrake_settings}")
                                        print("\033[92mDone !\033[0m")
                                        last_torrent_proceed = file_name
                                        encode = True

                                else:                               # Copying the file to the destination folder
                                    if os.path.exists(f"{settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mkv'}"):
                                        print(f"\033[35mSkipping copying {file_name} : output file already exists\033[0m")
                                    else:
                                        print(f"\033[96mCopying {file_name} to {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mkv'}..\033[0m")
                                        os.system(f"cp {settings.torrents_location}/{input_file_name} {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mkv'}")
                                        print("\033[92mDone !\033[0m")
                                        last_torrent_proceed = file_name

                                processed_list.data.append(file_name)
                                processed_list.write_to_txt()

                                if settings.auto_encode == True:    # Giving the file the right permissions
                                    os.system(f"sudo chown {settings.linuxuser} {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mp4'}")
                                    os.system(f"sudo chmod 775 {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mp4'}")
                                else:
                                    os.system(f"sudo chown {settings.linuxuser} {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mkv'}")
                                    os.system(f"sudo chmod 775 {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name + '.mkv'}")

                            else:
                                print(f"\033[31mFile {file_name} is still downloading !\033[0m")

            if request_count != 1 and settings.delete_torrents_afterwards == True:
                clean_torrents()

            print(f"\n\033[4m{request_count} requests made\033[0m")

            if encode == False:
                print("Wating 7 minutes before the next request..")
                wait(420)   # Change this value (in seconds) to wait more or less before the next request

            elif crash == True:
                print("Wating 30 seconds before the next request..")
                wait(30)
                qb_request()

            else:
                qb_request()

        elif len(source_rss) == 5:
            print("RSS request failed, next try in 5 seconds..")
            wait(5)
