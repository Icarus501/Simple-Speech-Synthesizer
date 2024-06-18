from pathlib import Path
import simpleaudio
import synth
from synth_args import process_commandline
from nltk.corpus import cmudict
import re
import numpy as np
from datetime import datetime

date_string1 = "8/12/80"
date_string2 = "20/5/2003"
date_string3 = "12/6"

phrase = "John Lennon died on 8/12/80 20/5/1978 12/6  it's"

list_date = [date_string1, date_string2, date_string3]

# print("the day is: ", date_obj.date().day)
# print("the month is: ", date_obj.date().month)

utt_tokens = [re.sub(r'[^\w\s^/\']', '', token.lower()) for token in phrase.split()]
print(utt_tokens)

number = ["one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen",
          "fifteen","sixteen","seventeen","eighteen","nineteen"]
months = ["January", "February", "March", "April", "May", "June", "seven", "August", "September", "October",
          "November", "December"]
days = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh",
        "twelfth", "thirteenth","fourteenth","fifteenth","sixteenth","eighteenth","nineteenth","twentieth","twentieth",
        "twenty first","twenty second","twenty third","twenty fourth","twenty fifth","twenty sixth","twenty seventh",
        "twenty eighth","twenty ninth","thirtieth","thirty first"]

ten_numbers = ["ten","twenty","thirty","forty","fifty","sixty","seventy","ninety","hundred"]

for item in utt_tokens:
    if re.match(r"\d+/\d+/\d+|\d+/\d+", item):
        print(item)
        try:
            date_obj = datetime.strptime(item, "%d/%m/%y")
        except ValueError:
            try:
                date_obj = datetime.strptime(item, "%d/%m/%Y")
            except ValueError:
                date_obj = datetime.strptime(item, "%d/%m")
        # print(date_obj.month)
        month = months[date_obj.month - 1]
        day = days[date_obj.day-1]
        year = 0
        if date_obj.year == 1900:
            year = "nineteen hundred"
        elif date_obj.year < 1910:
            year = f"one thousand nine hundred {number[date_obj.year%100 - 1]}"
        elif date_obj.year < 1920:
            year = f"nineteen {number[date_obj.year%100 - 1]}"
        else:
            year = f"nineteen {ten_numbers[date_obj.year%100//10 - 1]} {number[date_obj.year%100%10 - 1]}"

        print(month,day,year)
print("########")

