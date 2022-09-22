import time

import gspread as gsp
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import requests
import math

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gsp.authorize(creds)

sheet = client.open("HousingAwards").sheet1

data = sheet.get_all_records()

allIGNs = sheet.col_values(2)


def getLevel(exp):
    level = math.sqrt(exp + 15312.5)
    frac = (125 / math.sqrt(2))
    level = (level - frac)
    level = level / (25 * math.sqrt(2))
    return level


def validatePlayer(ign):
    info = requests.get(
        url="https://api.hypixel.net/player",
        params={
            "key": "5dc506b5-babc-4922-a3e0-702ad5b5b7cf",
            "name": ign.replace(" ", "")
        }
    ).json()
    if not info["success"]:
        print(info)
        return False
    elif not info["player"] is None:
        try:
            if info["player"]["firstLogin"] < 1647821889:
                print(ign + " newer than 3 weeks old!")
                return False
            elif getLevel(int(info["player"]["networkExp"])) < 10:
                print(ign + " is less than lvl 10! LVL: " + str(getLevel(int(info["player"]["networkExp"]))))
                return False
        except:
            print(ign + " caused an unknown error!")
            return False
        return True
    else:
        print(ign + " is a Invalid IGN!")
        return False


duplicates = []

for x in range(1, sheet.row_count):
    try:
        cell = str(allIGNs[x - 1]).lower().replace(" ", "")
    except IndexError:
        break
    cellNum = "(" + str(x) + ",2)"
    if cell in duplicates:
        pprint(cell + " Is a duplicate at: " + cellNum)
        sheet.update_cell(x, 9, "False")
        sheet.format("I" + str(x), {
            "backgroundColor": {
                "red": 1.0,
                "green": 0.0,
                "blue": 0.0,

            }
        })
    else:
        if validatePlayer(cell):
            sheet.update_cell(x, 9, "True")
            sheet.format("I" + str(x), {
                "backgroundColor": {
                    "red": 0.0,
                    "green": 1.0,
                    "blue": 0.0,

                }
            })
        else:
            pprint(cell + " could not be validated! Location: " + cellNum)
            sheet.update_cell(x, 9, "False")
            sheet.format("I" + str(x), {
                "backgroundColor": {
                    "red": 1.0,
                    "green": 0.0,
                    "blue": 0.0,

                }
            })
    duplicates.append(cell)
    time.sleep(2)

pprint("END")
