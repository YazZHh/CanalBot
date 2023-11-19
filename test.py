def index_verify(file_name, index):                                     # Theses three following index_things functions work together and return the position of the index of the file (Here used to search " - ")
    if file_name[index + 3:index + 4] == "E":
        try:                                                                # It finds the first occurence of the index, then verify it by trying to int() the two next characters (the two next characters being the episode number)
            int(file_name[index + 1:index + 3])
            return True
        except ValueError:
            return False
    else:
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

def get_season_ep_number(torrent_name):
    index = search_index(torrent_name)
    if index != None:
        index2 = torrent_name.find("VOSTFR")
        if index2 == -1:           # Handle the case of a toreent name from Disney plus, which is multi subs as there is no "VOSTFR" in the torrent_name
            index2 = torrent_name.find("1080p")
        if torrent_name[index + 1:index + 2] == "0":
            season_number = torrent_name[index + 2:index + 3]
        episode_number = torrent_name[index + 4:index2 - 1]
        return (season_number, episode_number)
    return None

torrent_test = "Uma Musume - Pretty Derby S03E01 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR)"
torrent_test2 = "Uma Musume: Pretty Derby S02 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR)"

print(get_season_ep_number(torrent_test))
print(get_season_ep_number(torrent_test2))
