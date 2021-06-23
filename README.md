
# OWReveal
CSGO Overwatch revealer by sniffing packets

![Main window](https://i.imgur.com/lulwtDh.png) ![WatchList](https://i.imgur.com/LEablcb.png)

## Suspects added by people: [zahar.one/owrev](https://zahar.one/owrev)

## Latest Version:  
  
* v**4.4.4** [Download](https://github.com/ZaharX97/OWReveal/releases/latest)  
	* created a small site to show suspects from all people using this app  
	* [zahar.one/owrev](https://zahar.one/owrev)  
	* fixed [issue #12](https://github.com/ZaharX97/OWReveal/issues/12), net adapter is saved to settings  
	* fixed [issue #14](https://github.com/ZaharX97/OWReveal/issues/14), right click to copy steamid  
	* added some kind of format to renaming demos, [more info](https://github.com/ZaharX97/OWReveal#demo-rename-format)  
	* fixed [issue #15](https://github.com/ZaharX97/OWReveal/issues/15), right click on the link to copy demo name
  
## How to use?
1. Download and install npcap (https://nmap.org/npcap/)
2. Open my program
3. Select your network interface
4. Press Start

## How to build a .exe from this?
1. Install the latest python v3
2. Install pyinstaller
3. Download this project and extract into a folder
4. Open cmd/powershell in that folder
5.
a) For app version >= 4.2 use  
> pyinstaller --icon app_icon.ico --clean --add-data "resources/app_icon.png;resources" --add-data "resources/csgo_rank_icons/*.png;resources/csgo_rank_icons" --onefile --noconsole main.py
> 
b) For app version <= 4.1.x use  
> pyinstaller --icon app_icon.ico --onefile --noconsole main.py
6. The .exe should be in /dist/ folder

## Q&A
**Q**: Will I get VAC banned?  
**A**: Probably not, it does the same thing as Wireshark to get the link  

**Q**: What is npcap and why do I need it?  
**A**: I'm not sure but on Windows it's needed to sniff packets  


**Q**: How do I find The Suspect's profile with this?  
**A**: Check who has the same score as The Suspect and click his name  

**Q**: What is with the _console_ version of the .exe?  
**A**: The one with _console_ opens a cmd along and prints errors or whatever print statements I forgot to remove  

**Q**: Not a question, but k/d/a in your app is wrong  
**A**: Could be, in my app it's displayed as k/a/d and I'm not sure I covered all edge cases  
Also when you select a round, it shows the stats from the end of that round.

**Q**: What python version was this written for?  
**A**: I wrote this using python 3.8.1  
  
## Demo Rename Format:
**?N** gets replaced by original demo name (bunch of numbers)  
**?Ttime_format?** gets replaced by demo date in the format you choose  
more info here: [time format codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
  
## Older Versions: 

* v**4.3.6** [Download](https://github.com/ZaharX97/OWReveal/releases/tag/4.3.6)  
	* created a small site to show suspects from all people using this app  
	* [zahar.one/owrev](https://zahar.one/owrev)  
	* fixed: only 1 suspect was added to site, then a restart was needed  
	* fixed: check vac didnt work in v4.3  
	* fixed: unranked gamed didnt show team scores  
	* added demo date
	* (new) fixed: stats in wingman unranked (who plays that) were not shown correctly
  
* v**3.1.5** [Download](https://github.com/ZaharX97/OWReveal/releases/tag/3.1.5)  
  * changed npcap link to main site  
  * fixed a bug when first adding to watchlist 
  
* v**3.0** [Download](https://github.com/ZaharX97/OWReveal/releases/tag/3.0)
  * Added a watchlist to track suspect players
  
* v**2.0** [Download](https://github.com/ZaharX97/OWReveal/releases/tag/2.0)
  * added demo parsing, see player stats in each round
  * click on player to open steam profile
  
* v**1.0** [Download](https://github.com/ZaharX97/OWReveal/releases/tag/1.0)
  * First release, only finds the demo link  
  
## Tags that might help find this  
csgo overwatch revealer the suspect find profile cs:go vac watchlist demo guide tutorial  
How to Find "The Suspects" profile in Overwatch  
csgo find suspect profile  
[Tutorial] Viewing "The Suspect's" steam profile.  
how to get the real name of the suspect in overwatch cases  
