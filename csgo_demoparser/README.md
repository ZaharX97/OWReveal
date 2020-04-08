# CSGO Demoparser in python

It's a custom parser that returns a dictionary with rounds and playerstats.
I didn't parse demo entities yet (todo) (will be easier to get stats and other advanced stats
like player position, where are they looking, ranks...)

## Thanks to
1. (https://github.com/ValveSoftware/csgo-demoinfo)
2. (https://github.com/ibm-dev-incubator/demoparser)
3. (https://github.com/holosiek/csgodemo-python)
4. (https://github.com/markus-wa/demoinfocs-golang)
5. (https://github.com/SteamDatabase/GameTracking-CSGO)  
  
Without looking (and copying :D) at other projects it would have been impossible for me to understand how csgo demos work.  
Well, I still need to understand how to parse entities... whatever

## To use this:
```python
import DemoParser
parser = DemoParser(path_to_demo)
parser2 = DemoParser(path_to_demo, path_to_dump_file) # it prints out some data from demo if u specify a dump path
stats = parser.parse()
```
* if all went well, stats should be a dictionary like  
{  
  1: MyRoundStats object  
  2: ...  
  .  
  .  
  .  
  last round: MyRoundStats object  
  "nrplayers": 10 or 4  
  "map": mapname  
}  

# MyRoundStats structure
1. score_team2 (doesnt mean T or CT, just one of the teams)
2. score_team3
3. pscore (a list with MyPlayer objects sorted by kills)

# MyPlayer structure
I'll list the most important ones, you can check all of variables in [structures.py]()
1. name
2. profile (steam profile url)
3. k (kills)
4. a (assists)
5. d (deaths)
6. start_team (2 "T" or 3 "CT", very important to know how to arrange in main app)
