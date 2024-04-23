#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p "python3.withPackages(ps: [ ps.requests ps.pytz ])"
import json
from time import sleep
import requests
from datetime import datetime
import pytz

def main():

    whitelist_prayers = ['Fajr','Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'];
    today = requests.get("http://api.aladhan.com/v1/timingsByCity?city=Toronto&country=CA").json();
    timezone = pytz.timezone(today["data"]["meta"]["timezone"])
    olddate = datetime.now(timezone).date()
    current_date = datetime.now(timezone).date()
    #request prayer times
    while True:
        if olddate != current_date:
            today = requests.get("http://api.aladhan.com/v1/timingsByCity?city=Toronto&country=CA").json();
            olddate = datetime.now(timezone).date()
        current_date = datetime.now(timezone).date()
        filterd = filter(today["data"]["timings"], whitelist_prayers);
        respond(findNext(filterd, timezone), formatTooltip(filterd))
        sleep(60)


def respond(text, tooltip):
    dict = {}
    dict["text"] = text
    dict["tooltip"] = tooltip
    print(json.dumps(dict), flush=True)

def filter(d, whitelist):
    new = {}
    for prayers in d.keys():
        if prayers in whitelist:
            new[prayers] = d[prayers];
    return new

#tooltip
def formatTooltip(filterd):
    s = ""
    for prayer, time in filterd.items():
        s += f"{prayer}: {time} \n"
    return s

def str_to_time(hour_minute, timezone):
    # Get current date
    current_date = datetime.now(timezone).date()

    # Parse input time string and combine it with current date
    return timezone.localize(datetime.strptime(f"{current_date} {hour_minute}", "%Y-%m-%d %H:%M"))

def findNext(filterd, timezone):
    times = {prayer: str_to_time(time_str, timezone) for prayer, time_str in filterd.items()}
    current_time = datetime.now(timezone)
    closest_time = None
    closest_prayer = "";
    for prayers, time in times.items():
        # note using times SUCKS
        # some timezones consist of two ofsets! ex America/Toronto has EST and EDT
        # print(f"setting {time} vs {current_time} ====> {time > current_time}")
        if time > current_time and (closest_time is None or time < closest_time):
            closest_time = time
            closest_prayer = prayers
    diff = (closest_time - current_time).total_seconds(); #ide might give error here 
    hours = diff/3600
    mins = diff/60
    if hours < 1:
        return f"{closest_prayer} in {round(mins)} mins"
    else:
        return f"{closest_prayer} in {round(hours)} hours"

if __name__ == "__main__":
    main()
