# Cross-Seed-AutoDL
Finds cross-seedable torrents for Movies and TV via Jackett. Parses existing files/folders in order to download matching torrents.

Requires minimum python 3.6

Requires [Jackett](https://github.com/Jackett/Jackett)

# Setup


Run `pip3 install -r requirements.txt` to install the required libraries


# Usage

    usage: CrossSeedAutoDL.py [-h] [-p] [-g] [-d delay] -i input_path -s save_path
    -j jackett_url -k api_key [-t trackers] [-u client_url] [-c client_type] 
    [--ignore-history] [--strict-size] [--only-dupes]
    
    Searches for cross-seedable torrents
    
    arguments:
      -h, --help            show this help message and exit
      -p, --parse-dir       Optional. Indicates whether to search for all the items 
                            inside the input directory as individual releases
      -g, --match-release-group
                            Optional. Indicates whether to attempt to extract 
                            a release group name and include it in the search query.
      -d delay, --delay delay
                            Optional. Pause duration (in seconds) between searches (default: 10)
      -i input_path, --input-path input_path
                            File or Folder for which to find a matching torrent
      -s save_path, --save-path save_path
                            Directory in which to store downloaded torrents
      -j jackett_url, --jackett-url jackett_url
                            URL for your Jackett instance, including port number or path if needed
      -k api_key, --api-key api_key
                            API key for your Jackett instance
      -t trackers, --trackers trackers
                            Optional. Tracker(s) on which to search. Comma-separated if 
                            multiple (no spaces). If omitted, all trackers will be searched.
      -u client_url, --client-url client_url
                            Optional. Torrent client URL to fetch existing torrents 
                            from, including port number or path if needed
      -c client_type, --client-type client_type
                            Optional. Torrent client type. Use in conjuction with --client-address. 
                            Valid values are: rtorrent
      --ignore-history      Optional. Indicates whether to skip searches or downloads for files 
                            that have previously been searched/downloaded previously.
      --strict-size         Optional. Indicates whether to match torrent search result sizes to 
                            exactly the size of the input path. Might miss otherwise cross-seedable 
                            torrents that contain additional files such as .nfo files
      --only-dupes          Optional. Indicates whether to skip downloads for 
                            searches with only one match. Might miss cross-seedable 
                            torrents if the input files are not indexed by Jackett


Examples:

If you're on Windows, use `py` like indicated below, otherwise replace `py` with `python3` if you're on Linux/Mac.

(include `-p` flag) Conducts multiple searches: Runs a search for each of the input directory's child items. ie. If input path is a season pack that contains 10 files, a search will be conducted for each file (10 total searches)

	py CrossSeedAutoDL.py -p -i "D:\TorrentClientDownloadDir\complete" -s "D:\DownloadedTorrents" -u "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t" -t blutopia

Search for a single item, a video file (omit `-p` flag)

	py CrossSeedAutoDL.py -i "D:\TorrentClientDownloadDir\complete\My.Movie.2010.720p.mkv" -s "D:\DownloadedTorrents" -u "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t" -t blutopia,passthepopcorn

Search for a single item, a season pack (omit `-p` flag)

	py CrossSeedAutoDL.py -i "D:\TorrentClientDownloadDir\complete\My.Show.Season.06.Complete" -s "D:\DownloadedTorrents" -u "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t" -t blutopia,broadcasthenet,morethantv

TODO: Add examples for torrent client connections and explanation of when to use --only-dupes and -g