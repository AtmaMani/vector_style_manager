# StyleUploader
This is a Python utility for the Vector Tiles project. This Python Project creates create Vector Tile Service online item and uploads style data to its resources section. The companion StyleDownloader script can be used to download style resources for a portal item - either from the item's resource or from original vector tile server it is pointing to. New addition in v1.4 is StyleUpdater which can be used to update the style resources associated with an item.

## Dependencies
1. Python 3.4 or higher
2. Python 'Requests' 3rd party library

### Solving dependencies on your machine
1. Getting Python package installer pip: [http://pip.readthedocs.org/en/stable/installing/](http://pip.readthedocs.org/en/stable/installing/)
2. Once pip is installed, get requests by typing command `$ pip install requests`  More help at [http://docs.python-requests.org/en/latest/user/install/](http://docs.python-requests.org/en/latest/user/install/)

## Usage
### StyleUploader.py script
Edit the script with your
* portal URL
* portal Username and password
* name of the online item you wish to create
* URL of the vector tile service the item should point to
* path to local directory which contains style files. The following directories are required
  * styles (containing root.json which becomes itemid/data resource)
  * sprites (available as itemid/resources/sprites resource)
  * fonts (fonts as .pbf files, available as itemid/resources/fonts resource)

### StyleDownloader.py script
Edit the script with your
* portal URL
* portal Username and password
* itemID of the vector tile service layer item on the portal
* path to local directory to which you want to download the style resources
* whether or not you want to download resourcse from the vector tile service only

### StyleUpdater.py script
Edit the script with your
* portal URL
* portal username and password
* itemID of the vector tile service layer item on portal that you wish to update
* path to local directory which contains new style files. The following directories are required
  * styles (containing root.json which becomes itemid/data resource)
  * sprites (available as itemid/resources/sprites resource)
  * fonts (fonts as .pbf files, available as itemid/resources/fonts resource)

## Notes
* Script performs multipart upload of all files
* Script replicates folder structure in the resources url during upload and in local file directory during download
