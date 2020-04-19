from csgo_demoparser.DemoParser import DemoParser

path = r"C:\Users\Zahar\Desktop\asd\demo.dem"
dump_path = r"C:\Users\Zahar\Desktop\asd\demodump.txt"
x = DemoParser(path, dump_path)
stats = x.parse()
