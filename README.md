# OWReveal
CSGO Overwatch revealer by sniffing packets

![Main window](https://i.imgur.com/MaP0Fut.png) ![WatchList](https://i.imgur.com/bh06N3I.png)

## Latest Version:  
  
* v**4.0.1** [Download](https://github.com/ZaharX97/OWReveal/releases)  
  * added more info (rank, server)  
  * added a check for newer versions  
  * added some more stats to the WatchList
  * 4.0.1: fixed a bug when cheaters had no name in WatchList
  * 4.0.1: fixed the check for newer versions
  
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
5. > pyinstaller --icon app_icon.ico --onefile --noconsole main.py
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
  
## Older Versions: 
  
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
