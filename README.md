
# This is just a small project, it has only been tested on rimworld. It will only work on games that allow for anonymous downloads through steamCMD.


# How to use


## 1. Download the latest release
Go to releases and download PyWorkshopDownloader.exe and put it anywhere

## 2. Install steamCMD
make shure you have steamCMD installed and working (https://developer.valvesoftware.com/wiki/SteamCMD) (https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip)

## 3. Run PyWorkshopDownloader.exe
This will open a GUI (if the program actually works) 

First enter a collection link and press laod, this should find the game ID and fill the list with mod ID's. any of them
can be double clicked to open the workshop page in your browser.

click browse and sellect steamcmd.exe where you installed it.

click start download and wait for it to finish. a progress bar will show the progress of the download.
also green text will mean a download was successful and red text will mean a download failed.

## 4. Install the mods
the mods should end up in "steamCMD\steamapps\workshop\content\gameid" folder. 


## additionaly.

you can add or remove mods from the list by selecting a mod in the list and pressing the delete sellected button or add
by pressing the add from link button, that will prompt you for a link to the steam page of the mod.

additionally a txt file can be made and loaded using the add from file button. the file should contain a list of mod links
like so:

"https://steamcommunity.com/sharedfiles/filedetails/?id=2589384830

https://steamcommunity.com/sharedfiles/filedetails/?id=2883216840

https://steamcommunity.com/sharedfiles/filedetails/?id=2519621745"

(without the space inbetween)