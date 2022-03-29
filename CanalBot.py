import feedparser
from qbittorrent import Client
import os
from time import sleep

lang = "language"                                       # Basically language you want the subtitles to be
suffix = "vosten"                                       # Episode name will be in this format : {anime_name}.s1e{episode_number}.{suffix}.mp4
target_directory = "/animes/output/directory"           # This should be the directory where animes will be stored (Don't put a "/" at the end), please note that the sctipt will create a subfolder in this directory named "anime"
torrents_location = "/anime/torrent/directory"          # Episodes files should be in this directory (Don't put a "/" at the end), please configure your qBittorrent Web UI
linuxuser = "user"                                      # Linux user who will get the acces rights to the files

user = "admin"                                          # Username of your qBittorrent Web UI
password = "adminadmin"                                 # Password for the Web ui
qb = Client('http://localhost:8080')                    # Change "https://link-to-my-web.ui:PORT" to your actual web domain, please note that you can also use "http://localhost:8080" if you don't have a domain name

rss_link = 'https://nyaa(.)si/?page=rss&u=Erai-raws'    # Just remove the "()" and run the script

request_count = 0
connection_cooldown_qbittorrent = 0
rss_search_results = []
last_torrent_added = None
erai = []

print("\033[1;96mCanalBot v0.1 Beta\033[0m")
delete = input("Do you want to delete the torrents once they are no longer in the RSS search results ? [Y/n] : ")
assert delete == 'y' or delete == 'Y' or delete == 'n' or delete == 'N', "Please specify your answer with y (yes) or n (no)"

# Function that (is supposed to) prevent the program from crashing if the RSS request fails
def request(test_request):
    try:
        test_request
    except:
        print("\033[91m\033[1mRequest FAILED, next try in 5 seconds...\033[0m")
        sleep(5)
        request(test_request)
    return test_request

def read_txt(file):
    temp = open(file, "r")
    return list(temp.read().split("\n"))

def write_txt(file, list):
    list = '\n'.join(list)
    temp = open(file, "w")
    temp.write(list)

def check_if_encoded(torrent_name):
    for i in encoded_list:
        if torrent_name == i:
            return True

def check_if_added(torrent_name):
    for torrent in qb.torrents():
        if torrent_name == torrent['name']:
            return True

def rss_search(keyword, quality):
    entry_number = -1
    for i in erai.entries:
        entry_number += 1
        find = i.title.find(keyword)
        if find != -1:
            q = erai.entries[entry_number].title.find(quality)
            torrent_name = erai.entries[entry_number].title
            if q != -1:
                if check_if_added(erai.entries[entry_number].title) == None:
                    qb.download_from_link(erai.entries[entry_number].link)
                    rss_search_results.append(erai.entries[entry_number].title)
                    print(f'\033[1;96m\033[1mFound : "{erai.entries[entry_number].title}"\033[0m", torrent successfully added')
                    break
                else:
                    print(f'\033[90mTorrent "{torrent_name}" have already been added..\033[0m')
                    already_found.append(erai.entries[entry_number].title)
                    rss_search_results.append(erai.entries[entry_number].title)
                    break
    if find == -1:
        not_found.append(anime_list[a_l])

def clean_torrents():
    delete_list = list(set(previous_rss_search_results) - set(rss_search_results))
    if len(delete_list) == 0:
        print("\033[90mNo torrent to delete\033[0m")
    else:
        for file in delete_list:
            for torrent in torrents_info:
                file_name, hash = torrent['name'], torrent['hash']
                if file == file_name and file_name[0:11] == "[Erai-raws]" and check_if_encoded(file_name) == True and check_if_added(file_name) == True:
                        print(f'\033[1;91mDeleting "{file_name}"\033[0m')
                        qb.delete_permanently(hash)
                        clean_torrent_list(file_name)

def clean_torrent_list(torrent):
    temp = read_txt("encoded-list.txt")
    nb = 0
    for i in temp:
        if i == torrent:
            temp.pop(nb)
        nb += 1
    write_txt("encoded-list.txt", temp)

while True:
    # Connection request to the qBittorrent Web UI every 18 minutes (3*6)
    if connection_cooldown_qbittorrent <= 0:
        print("\n\033[1mConnection request to the qBittorrent Web UI..\033[0m")
        request(qb.login(user, password))
        connection_cooldown_qbittorrent = 3

    connection_cooldown_qbittorrent -= 1
    anime_list = read_txt("anime-list.txt")
    encoded_list = read_txt("encoded-list.txt")

    print("\n\033[93mCollecting RSS feed..\033[0m")
    erai = request(feedparser.parse(rss_link))
    
    if len(erai) == 9:          # lengh of RSS request is 9 if it was successful (idk why, maybe useless now with the request() function)
        request_count += 1
        not_found = []
        previous_rss_search_results = rss_search_results
        rss_search_results = []
        already_found = []

        print("\033[1mLast torrent added in the RSS feed\033[0m :", erai.entries[0].title)

        for i in range(len(anime_list)):
            a_l = i
            if anime_list[i] != "":
                rss_search(anime_list[i], '1080p')
            else:
                print("\033[1;96minvalid keyword, skipping..\033[0m")

        not_found_list = ', '.join(not_found)
        if len(not_found_list) != 0:
            print("No results for :", not_found_list)

        if last_torrent_added != None:
            print("Last torrent encoded :", last_torrent_added)
        if len(list(set(rss_search_results) - set(previous_rss_search_results))) == 0:
            print("\033[90mNo new torrent found\033[0m")

        torrents_info = qb.torrents()
        encode = False

        for torrent in torrents_info:
            file_name = torrent['name']
            if file_name[0:11] == "[Erai-raws]" and check_if_encoded(file_name) == None:
                if torrent['state'] != 'downloading':
                    # Setting up the encoding parameters (THESES ONES ONLY MATCH ERAI-RAWS'S RELEASES)
                    index = file_name.find(" - ")
                    anime_name = file_name[12:index]
                    episode_number = file_name[index + 3:index + 5]
                    destination_folder_name = anime_name.replace(" ", "-").lower()
                    point_name = anime_name.replace(" ", ".")
                    input_file_name = input_file_name = file_name.replace(" ", "\ ")
                    output_file_name = f'{point_name}.s1e{episode_number}.{suffix}.mp4'

                    os.system(f'mkdir -p {target_directory}/animes/{destination_folder_name}/s1')

                    print("Encoding", file_name)
                    os.system(f'HandBrakeCLI -i {torrents_location}/{input_file_name} -o {target_directory}/animes/{destination_folder_name}/s1/{output_file_name} -vfr -B 512 -b 2500 -T -2 -O --subtitle-lang-list {lang} --subtitle-burn')
                    encode = True

                    encoded_list.append(file_name)
                    write_txt("encoded-list.txt", encoded_list)

                    last_torrent_added = file_name

                    os.system(f'sudo chown {linuxuser} {target_directory}/animes/{destination_folder_name}/s1/{output_file_name}')
                    os.system(f'sudo chmod 777 {target_directory}/animes/{destination_folder_name}/s1/{output_file_name}')

                elif torrent['state'] == 'downloading':
                    print(f'File {file_name} is still downloading')

        if request_count != 1 and delete == 'y' or delete == 'Y':
            clean_torrents()

        print(f'\n\033[4m{request_count} requests made\033[0m')
        if encode == False:
            print("\033[6mWating 7 minutes before the next request..\033[0m")
            sleep(420)

    elif len(erai) == 5:
        print("RSS request failed, next try in 5 seconds..")
        sleep(5)