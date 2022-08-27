import feedparser
from threading import Thread, Event
from qbittorrent import Client
import os
import time
import requests

# Please change the following variables to your own settings

class settings:
    delete_torrents_afterwards = False                      # Delete torrents after they are no longer in the RSS search results
    auto_encode = True                                      # Set to True if you want to automatically encode the torrents
    lang = "english"                                        # Language you want the subtitles to be
    suffix = "suffix"                                       # Episode name will be in this format : {anime_name}.s1e{episode_number}.{suffix}.mp4, Change this to whatever you want
    quality = "1080p"                                       # Video quality of the torrents
    handbrake_settings = f"-vfr -e x264 -b 2500 -E av_aac -B 512 -T -2 -O --subtitle-lang-list {lang} --subtitle-burn"  # HandBrakeCLI settings
    target_directory = "/animes/output/directory"           # This should be the directory where animes will be stored, please note that the sctipt will create a subfolder in this directory named "anime"
    torrents_location = "/animes/torrent/directory"         # Episodes files should be in this directory, please configure your qBittorrent Web UI
    linuxuser = "user"                                      # Linux user who will get the acces rights to the files
    user = "admin"                                          # Username of your qBittorrent Web UI
    password = "adminadmin"                                 # Password for the Web ui
    webui_link = "http://localhost:8080"                    # Change "https://link-to-my-web.ui:PORT" to your actual web domain, please note that you can also use "http://localhost:8080" if you don't have a domain name
    rss_link = "https://nyaa(.)si/?page=rss&u=Erai-raws"    # Just remove the "()" and run the script

request_count = 0                           # Do not modify the following lines
rss_search_results = []
last_torrent_proceed = None
erai = []
qb = Client(settings.webui_link)
start_time = time.time()
crash = False
fail_count = 0

print("\033[1;96mCanalBot v0.5-beta2\033[0m")

class index:
    def index_verify(file_name, index):
        try:
            int(file_name[index + 3:index + 5])
            return True
        except ValueError:
            return False

    def find_index(file_name, index, number):
        start = file_name.find(index)
        while start >= 0 and number > 1:
            start = file_name.find(index, start + len(index))
            number -= 1
        return start

    def search_index(file_name):
        for i in range(1, 5):
            if index.index_verify(file_name, index.find_index(file_name, " - ", i)):
                return index.find_index(file_name, " - ", i)

class checks:
    def check_if_processed(torrent_name):
        check = False
        for i in proceed_list:
            if torrent_name == i:
                check = True
        return check

    def check_if_added(index, keyword, ep_number):
        check = False
        for torrent in qb.torrents():
            torrent_name = torrent['name'] 
            if torrent_name.find(keyword) != -1:
                if torrent_name[index + 3:index + 5] == ep_number:
                    check = True
        return check

    def check_if_on_the_list(torrent):
        check = False
        for i in anime_list:
            if i != ['']:
                if torrent.find(i[0]) != -1:
                    check = True
        return check

    def get_anime_info(torrent_name):
        for i in anime_list:
            if i != ['']:
                if torrent_name.find(i[0]) != -1:
                    return i[0], i[1], i[2], i[3]
        return None

class torrents:
    def rss_search(keyword, quality):
        erai_rss = erai.entries
        entry_number = -1
        for i in erai_rss:
            entry_number += 1
            find = i.title.find(keyword)
            if find != -1:
                q = erai_rss[entry_number].title.find(quality)
                torrent_name = erai_rss[entry_number].title
                if q != -1:
                    rss_torrent_title = erai_rss[entry_number].title
                    if rss_torrent_title.find("HEVC") == -1 and rss_torrent_title.find("Multiple Subtitle") != -1: # Get rid of the shitty HEVC torrents and releases that have only ENG subs
                        torrent_index = index.search_index(rss_torrent_title)
                        if checks.check_if_added(torrent_index, keyword, rss_torrent_title[torrent_index + 3:torrent_index + 5]) == False:
                            qb.download_from_link(erai_rss[entry_number].link)
                            rss_search_results.append(erai_rss[entry_number].title)
                            print(f'\033[1;96m\033[1mFound : "{erai_rss[entry_number].title}"\033[0m, torrent successfully added')
                            break
                        else:
                            print(f'\033[90mTorrent "{torrent_name}" have already been added..\033[0m')
                            rss_search_results.append(erai.entries[entry_number].title)
                            break
        if find == -1:
            not_found.append(keyword)

    def clean_torrents():
        delete_list = list(set(previous_rss_search_results) - set(rss_search_results))
        if len(delete_list) == 0:
            print("\033[90mNo torrent to delete\033[0m")
        else:
            for anime_ep in delete_list:
                torrent_index = index.search_index(anime_ep)
                anime_name, ep_number = anime_ep[12:torrent_index], anime_ep[torrent_index + 2:torrent_index + 6]
                for torrent in torrents_info:
                    torrent_file_name, hash = torrent['name'], torrent['hash']
                    if torrent_file_name.find(anime_name) != -1 and torrent_file_name.find(ep_number) != -1:# file_name[0:11] == "[Erai-raws]" and checks.check_if_processed(file_name) == True and checks.check_if_added(file_name) == True:
                        print(f'\033[1;91mDeleting "{torrent_file_name}"\033[0m')
                        print(f"DELETE : qb.delete_permanently({hash})") # DEBUG
                        # torrents.clean_torrent_list(torrent_file_name) # DEBUG

    def clean_torrent_list(torrent):
        temp = txt.read_txt_to_list("proceed_list.txt")
        nb = 0
        for i in temp:
            if i == torrent:
                temp.pop(nb)
            nb += 1
        txt.write_list_to_txt("proceed_list.txt", temp)

class txt:
    def read_txt_to_list(file):
        temp = open(file, "r")
        return list(temp.read().split("\n"))

    def read_txt_to_list_of_lists(file):
        temp = open(file, "r")
        return list(x.split(", ") for x in temp.read().split("\n"))

    def write_list_to_txt(file, list):
        list = '\n'.join(list)
        temp = open(file, "w")
        temp.write(list)

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
            time.sleep(10)

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
            time.sleep(300)

def calcul_time(time_in_seconds):
    days = time_in_seconds // 86400
    hours = (time_in_seconds - (86400 * days)) // 3600
    minutes = (time_in_seconds - (86400 * days) - (3600 * hours)) // 60
    if days == 0 and hours == 0:
        return f'{minutes} minutes'
    elif days == 0:
        return f'{hours}h {minutes}min'
    else:
        return f'{days}d {hours}h {minutes}min'

def search_for_new_torrents():
    global crash
    crash = False
    for anime in anime_list:
        if anime[0] != "":
            try:
                torrents.rss_search(anime[0], settings.quality)
            except:
                # print("\033[1;91mError while searching for new torrents / Error while retrieving Torrents info from the qBittorrent Web UI\033[0m")
                # Line above commented because the error can appears when no crash has happen (likely because the rss.request takes a bit of time to execute sometimes)
                crash = True

def timeout_search():   # I need to get rid of this function
    stop_event = Event()
    action_thread = Thread(target=search_for_new_torrents)
    action_thread.start()
    action_thread.join(timeout=10)
    stop_event.set()

qb_request()

while True:     # Main infinite loop start
    anime_list = txt.read_txt_to_list_of_lists("anime_list.txt")
    proceed_list = txt.read_txt_to_list("proceed_list.txt")

    if crash == True:
        qb_request()

    erai = rss_request()
        
    if len(erai) == 7:          # did some tests, and lenght = 7 if RSS request success
        fail_count = 0
        request_count += 1
        not_found = []
        encode = False

        if crash == False:
            previous_rss_search_results = rss_search_results
            rss_search_results = []

        print("\033[1mLast torrent added in the RSS feed\033[0m :", erai.entries[0].title)
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
            print("Total run time :", calcul_time(round((time.time() - start_time))))

        if crash == False:
                for torrent in torrents_info:
                    file_name = torrent['name']
                    if file_name[0:11] == "[Erai-raws]" and checks.check_if_processed(file_name) == False and checks.check_if_on_the_list(file_name) == True:
                        if torrent['state'] != 'downloading' and torrent['state'] != 'stalledDL':

                            file_info = checks.get_anime_info(file_name)            # Get infos from anime_list.txt
                            anime_name = file_info[3]
                            index_rank = index.search_index(file_name)              # Search for the real index, because Erai-raws's releases names are not always in the same format, huge thanks to them !
                            episode_number = file_name[index_rank + 3:index_rank + 5]
                            input_file_name = file_name.replace(" ", "\ ")
                            point_name = anime_name.replace(" ", ".")
                            output_file_name = f'{point_name}.s{file_info[2]}e{episode_number}.{settings.suffix}.mp4'

                            if settings.auto_encode == True:    # Encoding the file
                                os.system(f'mkdir -p {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}')    # Create a folder for the output file, if wasn't already
                                print(f'\033[96mEncoding {file_name} to {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name}\033[0m..')
                                os.system(f'HandBrakeCLI -i {settings.torrents_location}/{input_file_name} -o {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name} {settings.handbrake_settings}')
                                print("\033[92mDone !\033[0m")
                                encode = True

                            else:   # Copying the file to the destination folder
                                print(f'\033[96mCopying {file_name} to {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name}..\033[0m')
                                os.system(f'cp {settings.torrents_location}/{input_file_name} {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name}')
                                print("\033[92mDone !\033[0m")

                            proceed_list.append(file_name)
                            txt.write_list_to_txt("proceed_list.txt", proceed_list)

                            last_torrent_proceed = file_name

                            # Giving the file the right permissions
                            os.system(f'sudo chown {settings.linuxuser} {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name}')
                            os.system(f'sudo chmod 775 {settings.target_directory}/animes/{file_info[1]}/s{file_info[2]}/{output_file_name}')

                        else:
                            print(f'\033[31mFile {file_name} is still downloading\033[0m')

        if request_count != 1 and settings.delete_torrents_afterwards == True:
            torrents.clean_torrents()

        print(f'\n\033[4m{request_count} requests made\033[0m')

        if encode == False:
            print("Wating 7 minutes before the next request..")
            time.sleep(420)     # Change this value (in seconds) to wait mor or less befor the next request
        elif crash == True:
            print("Wating 30 seconds before the next request..")
            time.sleep(30)
            qb_request()
        else:
            qb_request()

    elif len(erai) == 5:
        print("RSS request failed, next try in 5 seconds..")
        time.sleep(5)