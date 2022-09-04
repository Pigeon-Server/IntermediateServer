from json import load, dump
from os.path import exists

if exists("config.json"):
    config = load(open("config.json", "r", encoding="UTF-8", errors="ignore"))
else:
    config = {
        "Host": "127.0.0.1",
        "Port": 3000
    }
    with open("config.json", "w") as write_file:
        dump(config, write_file, indent="\t", sort_keys=True, ensure_ascii=False)
    config = load(open("config.json", "r", encoding="UTF-8", errors="ignore"))
