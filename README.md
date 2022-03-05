# CanalBot
A small Python script ~~not the best written~~ made to automate the addition of weekly anime episodes on my server.

IT'S NOT RELEAESED YET BECAUSE OF CRASHING ERRORS (f u urllib3)

## Requirements :
- Python 3.7 at least (get Python 3.9 👉 `apt-get install python3`)
- a [qBittorrent](https://github.com/qbittorrent/qBittorrent) Web UI, hosted on the same machine as the script (you can use qbittorrent-nox 👉 `apt-get install qbittorrent-nox`)
- [HandBrakeCLI](https://github.com/HandBrake/HandBrake) installed on your linux distro (get the dpkg package 👉 `apt-get install handbrake-cli`)
- [feedparser](https://github.com/kurtmckee/feedparser), a python module 👉 `pip3 install feedparser`
- [python-qBittorrent](https://github.com/v1k45/python-qBittorrent), another python module 👉 `pip3 install python-qbittorrent`

## What does this script do ?
> It takes anime from the RSS page of Erai-raws's team on the cat torrent website, then it adds the anime you selected into qBittorrent Web UI, and finally it encode the episodes to `{target_directory}/animes/{anime_name}/s1/{anime_name}.s1eXX.vostfr.mp4`

## Usage guide :
- Start qBitrorrent-nox Web UI if it wasn't already
- Download the file `CanalBot.py` into a direcroty
- Create a file named `encoded-list.txt`, it will store the name of which files have already been encoded
- Create another file named `anime-list.txt`, and enter **ONE** keyword (seperated by a return line) for each animes you want the script to take (you can add as many keywords as you want, as long as there is one keyword per anime)
  * *It should look like this :*
    ```
    keyword1
    keyword2
    keyword3
    ```
- Now edit CanalBot.py and modify the first variables to match your settings :
  * `lang` is used to choose the language of subtitles that will be burned in the video (you can choose to not burn the subtitles, see Customisation)
  * `target_directory` tells the script where does the animes go
  * `linuxuser` specify which linux user shoud own the files
  * `user` is the user of the qBittorrent Web UI
  * `password` is the password of the qBittorrent Web UI
  * `qb` set the link to the qBittorrent Web UI

- If you've done everything, you can start the script by running `python3 CanalBot.py`, it will ask you if you want to delete torrents afterwards and start his job.
- If the script crashes, just restart it, it won't re-add episodes, or re-encode episode.

## Customisation
- You can custom the encoding command if you want, for example, to raise up or lower the bitrate...
  * *see [HandBrakeCLI Documentation](https://handbrake.fr/docs/en/latest/cli/cli-options.html)*
- You can stop the script at any moment py pressing <kbd>CTRL</kbd> + <kbd>C</kbd>
