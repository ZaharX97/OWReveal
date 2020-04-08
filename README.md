# OWReveal
CSGO Overwatch revealer by sniffing packets

![Main window](https://i.imgur.com/UU55Csw.jpg) ![Settings](https://i.imgur.com/ACZiZkm.jpg)

## Versions:
* v**1.0** [Download](https://github.com/ZaharX97/OWReveal/releases/tag/1.0)
  * First release, only finds the demo link

* v**2.0** [Download](https://github.com/ZaharX97/OWReveal/releases/tag/2.0)
  * added demo parsing, see player stats in each round
  * click on player to open steam profile

* v**2.1** todo
  * I want to add a watchlist to add suspect players
 
## How to use?
1. Download and install npcap (https://nmap.org/npcap/dist/npcap-0.9988.exe)
2. Open the program
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
**Q**: What is npcap and why do I need it?  
**A**: I'm not sure but on Windows it's needed to sniff packets  


**Q**: How do I find The Suspect's profile with this?  
**A**: Check who has the same score as The Suspect and click his name  

**Q**: Not a question, but k/d/a in your app is wrong  
**A**: Could be, in my app it's displayed as k/a/d and I'm not sure I covered all edge cases
Also when you select a round, it shows the stats from the end of that round.
