# CanalBot
A small Python script ~~not the best written~~ made to automate the addition of weekly anime episodes on my server, withe the help of a certain RSS page on a cat torrent website.
Originally made to work on a **linux** server, with [JellyFin](https://github.com/jellyfin/jellyfin), Plex or other Streaming service

## Requirements :
- Python 3.7 at least 
- a [qBittorrent](https://github.com/qbittorrent/qBittorrent) Web UI, **hosted on the same machine as the script** (use qBittorrent-nox on servers)
- [HandBrakeCLI](https://github.com/HandBrake/HandBrake) installed on your linux distro (dpkg, not the flatpack version)
- [feedparser](https://github.com/kurtmckee/feedparser), a python module
- [python-qBittorrent](https://github.com/v1k45/python-qBittorrent), another python module
### Install all requirements :
```
apt-get install python3
apt-get install qbittorrent-nox
apt-get install handbrake-cli
pip3 install feedparser
pip3 install python-qbittorrent
apt-get update && apt-get upgrade
```

## What does this script do ?
It takes anime from the RSS page of Erai-raws's team on the cat torrent website, then it adds the anime you selected into qBittorrent Web UI, and finally it encode the episodes to `{target_directory}/animes/{anime_name}/s1/{anime_name}.s1eXX.vostfr.mp4`

This script was intended to work with Erai-raws's torrents, giving the script another RSS feed will break the script. Sadly, is currently limited to adding only the first season of an anime, as Erai-Raws doesn't specify the season in their episode releases.

Default encoding settings (~500MB ouput file size, for a ~24mn episode): 
- Bitrate : 2500kbps
- Audio Bitrate : 512kbps
- Subtitle : Hardub

## Usage guide :
- Install all dependencies
- Start qBitrorrent Web UI if it wasn't already
- Download the file `CanalBot.py` into a direcroty
- Create a file named `proceed_list.txt`, it will store the name of which files have already been encoded
- Create another file named `anime_list.txt`, and enter **ONE** keyword (seperated by a return line) for each animes you want the script to take (you can add as many keywords as you want, as long as there is one keyword per anime)
  * *It should look like this :*
    ```
    keyword1
    keyword2
    keyword3
    ```
- Now edit CanalBot.py and modify the first variables to match your settings :
  * `lang` is used to choose the language of subtitles that will be burned in the video (you can choose to not burn the subtitles, see Customisation)
  * `suffix` define the end of the file. Episode name will be in this format : {anime_name}.s1e{episode_number}.{suffix}.mp4, for French subtitles you could put "vostfr" for instance.
  * `target_directory` tells the script where does the animes go
  * `torrents_location` define on which directory torrents are downloaded
  * `linuxuser` specify which linux user shoud own the files
  * `user` is the user of the qBittorrent Web UI
  * `password` is the password of the qBittorrent Web UI
  * `qb` set the link to the qBittorrent Web UI

- If you've done everything, you can start the script and it will ask you if you want to delete torrents afterwards and start his job.
- If the script crashes, just restart it, it won't re-add episodes, or re-encode episode.

## Customisation
- You can custom the encoding command if you want, *see [HandBrakeCLI Documentation](https://handbrake.fr/docs/en/latest/cli/cli-options.html)*
- You can stop the script at any moment py pressing <kbd>CTRL</kbd> + <kbd>C</kbd>, otherwise it will run infinitely
