# Cross-Seed-AutoDL
Finds cross-seedable torrents for Movies and TV via Jackett. Parses existing files/folders in order to download matching torrents.

Forked from BC44's [Cross-Seed-AutoDL](https://github.com/BC44/Cross-Seed-AutoDL) with added support for release group matching and fetching existing torrents from rtorrent. Further torrent client integrations may be implemented in the future.

Requires minimum python 3.6

Requires [Jackett](https://github.com/Jackett/Jackett)


## Setup
Run `pip3 install -r requirements.txt` to install the required libraries


## How it works

#### Default behavior
Cross-Seed-AutoDL uses the existing file or folder name to build a Jackett search query for a given torrent. The default behavior uses [guessit](https://github.com/guessit-io/guessit) to extract release information. Typically for movies, this results in a Jackett query of the form `"<Release Name> <Release Year>"` for movies, and simply `<Release Name>` for TV shows. The `season` and `episode` Jackett query parameters are also set if either were extracted by guessit (for example a season pack would contain a `season` parameter but not an `episode`. For each Jackett result, the total filesize is then compared to that of the local item. If the sizes are similar enough, the .torrent file for that search result is downloaded.

#### Release group matching
Cross-Seed-AutoDL can also be configured to attempt to extract the release group name from the input item, and append that name to the Jackett query. This is especially useful when searching for remuxes, as filesizes between release groups tend to be quite similar but the resulting torrents are obviously not cross-seedable. If a valid release group name cannot be found, Cross-SeedAutoDL will not include one in the Jackett query.

#### Torrent client connections
Currently, Cross-Seed-AutoDL is capable of connecting to a running rtorrent instance and fetching a list of currently loaded torrent infohashes. This list of infohashes is then used when processing Jackett results. If the Jackett indexer for a given tracker returns infohashes for results, each Jackett result's infohash is compared to the list of infohashes fetched from your torrent client, and the search result is ignored if that torrent is already active in your client. This functionality can be somewhat hit or miss depending on what trackers you have configured in Jackett, as many Jackett indexers do not return infohash data for releases.

#### Only downloading duplicates
If you have a large number of seeding torrents and cannot connect your torrent client to the script (or most of the trackers you're searching do not return infohashes), `--only-dupes` can be used as a stopgap measure to ignore torrents where the only match is (probably) the one you're already seeding. This is not as complete a solution as connecting to a torrent client since you will still download .torrent files for torrents you already have if there are multiple Jackett results. This option is best used in conjunction with release group matching.


## Connecting your torrent client

Currently supported torrent clients: rtorrent

#### rtorrent
Cross-Seed-AutoDL can connect directly to rtorrent's [SCGI](https://github.com/nascheme/scgi) port, or over XMLRPC via an http proxy. If you use rutorrent, your `.rtorrent.rc` file should already have an SCGI port configured, pointing to `127.0.0.1:5000` by default. See rtorrent's references for [enabling an SCGI port](https://rtorrent-docs.readthedocs.io/en/latest/cmd-ref.html#term-network-scgi-open-port), and for [setting up an XMLRPC http proxy endpoint](https://github.com/rakshasa/rtorrent-doc/blob/master/RPC-Setup-XMLRPC.md) if you'd like to access rtorrent on a remote machine. Note that rtorrent has no access control built in for the SCGI port, so if you expose the SCGI port remotely in any way, whether directly or through an XMLRPC http proxy, **you must implement some form of access control to prevent unauthorized usage.** Failure to do so will allow arbitrary remote code execution with the runtime privileges of the user running rtorrent. It is highly reccomended to run this script locally and avoid exposing the SCGI port remotely in any way.

Example arguments to connect directly through rtorrent's SCGI port: `-u "scgi://127.0.0.1:5000" -c "rtorrent"`

Example arguments to connect through an XMLRPC http proxy: `-u "https://192.168.1.xxx/RPC2" -c "rtorrent"`


## Usage
    usage: CrossSeedAutoDL.py [-h] [-p] [-g] [-d delay] -i input_path -s save_path
                              -j jackett_url -k api_key [-t trackers] [-u client_url] 
                              [-c client_type] [--ignore-history] [--strict-size] [--only-dupes]
    
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


## Examples

Basic usage: search all trackers for a single item (file or folder) and download all matching .torrents using default matching behavior.

        python CrossSeedAutoDL.py -i "\\NAS\Movies\My.Movie.2010.1080p.mkv" -s "./output_torrents" -j "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t"

(include `-p` flag) Run a search on the `blutopia` tracker for each of the input directory's child items using default matching behavior.

	python CrossSeedAutoDL.py -p -i "\\NAS\Movies" -s "./output_torrents" -j "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t" -t blutopia
        
Search for input items on `blutopia` and `passthepopcorn`, and attempt to extract and add release group name to the Jackett search query (especially useful for remuxes which all tend to be very similar in size) See [above](#release-group-matching) for an explanation of `--match-release-group`

        python CrossSeedAutoDL.py -p --match-release-group -i "\\NAS\Movies" -s "./output_torrents" -j "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t" -t blutopia,passthepopcorn

Search for input items on all trackers, match release group names, and only download torrents with more than one match. See [above](#only-downloading-duplicates) for an explanation of `--only-dupes`

        python CrossSeedAutoDL.py -p -g -i "\\NAS\Movies" -s "./output_torrents" -j "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t" --only-dupes

Search for input items on all trackers, match release group names, and ignore torrents that are already loaded in a local rtorrent client instance. See [above](#connecting-your-torrent-client) for info on how to connect your torrent client.

        python CrossSeedAutoDL.py -p -g -i "\\NAS\Movies" -s "./output_torrents" -j "http://127.0.0.1:9117" -k "cb42579eyh4j11ht5sktjswq89t89q5t" -u "scgi://127.0.0.1:5000" -c "rtorrent"
