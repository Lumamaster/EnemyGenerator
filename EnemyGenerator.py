import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import numpy as np
import math
from tkinter.filedialog import askopenfilename

filepath = ""

basetable = pd.DataFrame.empty

statnames = ["Name", "HP", "Strength", "Magic", "Skill", "Speed", "Luck", "Defense", "Resistance", "Base Hit", "Base Avoid", "Base Crit", "Offensive Stat"]

playernum = 0

playerlist = ["Placeholder"]

playerobjects = []

enemystats = []


class player:
    def __init__(self, NAME, HP, STR, MAG, SKL, SPD, LUK, DEF, RES, BHIT, BAVO, BCRIT, OFF):
        self.name = NAME
        self.HP = HP
        self.strength = STR
        self.magic = MAG
        self.skill = SKL
        self.speed = SPD
        self.luck = LUK
        self.defense = DEF
        self.resistance = RES
        self.basehit = BHIT
        self.baseavoid = BAVO
        self.basecrit = BCRIT
        self.offensivestat = OFF


def createerror(text):
    errortext = "An error occured! Reason: " + text
    errorwindow = tk.Tk()
    errorwindow.title = "Error"
    textframe = tk.Frame(errorwindow, height=100, width=250)
    textframe.grid()
    textframe.grid_propagate(False)
    textwidget = tk.Label(textframe, text=errortext, wraplength=250)
    textwidget.grid(row=0, column=0)
    okbutton = tk.Button(textframe, command=errorwindow.destroy, width=20, text="OK")
    okbutton.grid(row=1, column=0)
    errorwindow.mainloop()


def calculateavoid(baseavoid, speed, luck):
    return baseavoid + math.floor(speed/int(spdtoavoidbox.get())) * int(spdavoidbonusbox.get()) + math.floor(luck/int(lucktobonusbox.get())) * int(bonusfromluckbox.get())


def calculatehit(basehit, skill, luck):
    return basehit + math.floor(skill/int(skltohitbox.get()))*int(hitbonusbox.get()) + math.floor(luck/int(lucktobonusbox.get())) * int(bonusfromluckbox.get())


def calculatecrit(enemyskill, playerluck):
    return min(max(int((enemyskill - playerluck) / 5)/20, 0), 20)


def calculatehitrate(hit, avoid):
    return max(min(1, (20 + hit - avoid)/20), 0.05)


def calculatedouble(enemyspeed, playerspeed):
    if enemyspeed + 5 >= playerspeed:
        return True
    else:
        return False


def calculatedps(hitrate, critrate, attackstat, defenderstat, candouble):
    basedamage = max(attackstat - defenderstat, 0)
    if basedamage == 0:
        return 0
    basedamage *= hitrate
    if critrate >= 20:
        basedamage *= 3
    else:
        if critrate > 0:
            critpercent = critrate/20
            basedamage = basedamage * (1 - critpercent) + basedamage * critpercent * 3
    if candouble:
        basedamage *= 2
    return basedamage


def enemyoutput(statnames, stats):
    res = ""
    i = 0
    while i < stats.length():
        res += statnames[i] + ": " + stats[i] + "\n"
        i += 1
    return res


def settext(e, s):
    e.delete(0, 'end')
    e.insert(0, s)


def calculatematchup(player, enemy):
    php = player.HP
    ehp = enemy[0]
    if player.strength > player.magic:
        print(player.name + " is using strength")
        pdps = calculatedps(calculatehitrate(calculatehit(player.basehit, player.skill, player.luck), calculateavoid(enemy[9], enemy[4], enemy[5])), calculatecrit(player.skill, enemy[5]), player.strength, enemy[6], calculatedouble(player.speed, enemy[4]))
    else:
        print(player.name + " is using magic")
        pdps = calculatedps(calculatehitrate(calculatehit(player.basehit, player.skill, player.luck), calculateavoid(enemy[9], enemy[4], enemy[5])), calculatecrit(player.skill, enemy[5]), player.magic, enemy[7], calculatedouble(player.speed, enemy[4]))
    if enemy[1] > enemy[2]:
        edps = calculatedps(calculatehitrate(calculatehit(enemy[8], enemy[3], enemy[5]), calculateavoid(player.baseavoid, player.speed, player.luck)), calculatecrit(enemy[3], player.luck), enemy[1], player.defense, calculatedouble(enemy[4], player.speed))
    else:
        edps = calculatedps(calculatehitrate(calculatehit(enemy[8], enemy[3], enemy[5]), calculateavoid(player.baseavoid, player.speed, player.luck)), calculatecrit(enemy[3], player.luck), enemy[2], player.resistance, calculatedouble(enemy[4], player.speed))
    loopbreak = 0
    while php > 0 and ehp > 0 and loopbreak < 10:
        php -= edps
        ehp -= pdps
        loopbreak += 1
    if php <= 0:
        return True
    else:
        return False


def validate(stats, players):
    playerwins = 0
    playerlist = ""
    for i in range(len(players)):
        if calculatematchup(players[i], stats):
            playerwins += 1
            playerlist += players[i].name + "\n"
    result = "This generic wins against " + str(playerwins) + " players.\nPlayers: " + playerlist
    return result


def generate():
    global playernum
    global basetable
    global enemystats
    if not verifystats():
        createerror("One or more enemy stats were invalid! Please make sure that they are all positive integers.")
    else:
        generatedstats = [int(hpbox.get()), int(strbox.get()), int(magbox.get()), int(sklbox.get()), int(spdbox.get()), int(luckbox.get()), int(defbox.get()), int(resbox.get()), int(hitbox.get()), int(avoidbox.get())]
        wins = validate(generatedstats, playerobjects)
        outputtext['text'] = wins
        enemystats = generatedstats
        testplayer.config(state='active')


def selectfile():
    global basetable
    global filepath
    global playerlist
    global playernum
    filepath = askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
    try:
        basetable = pd.read_csv(filepath)
    except:
        createerror("An error occured when reading the specified file. Make sure the format is correct.")
    fileinput.config(state='normal')
    fileinput.insert(0, filepath)
    fileinput.config(state='readonly')
    columnnames = basetable.columns.values.tolist()
    i = 0
    while i < len(columnnames):
        if columnnames[i].lower() != statnames[i].lower():
            createerror("Column " + str(i) + " in CSV file was not named \"" + statnames[i] + "\"")
            return
        i += 1
    nullcheck = basetable.isnull()
    if not nullchecker(nullcheck):
        createerror("A character value in the csv was left blank.")
        return
    notnumber = basetable.applymap(np.isreal).all()
    for i, v in notnumber.items():
        if i.lower() != "name" and i.lower() != "offensive stat":
            if not v:
                createerror("Column " + i + " contains a non-numeric value.")
                return
    offstats = basetable["Offensive Stat"].unique()
    for s in offstats:
        if columnnames.count(s) == 0:
            createerror(s + " in the Offensive Stat column is not a valid offensive stat.")
            return
    playernames = list(basetable[columnnames[0]])
    playerlist = np.array(playernames)
    playernum = len(playerlist)
    processed = []
    iterator = 0
    for p in playerlist:
        processed.append(p)
        temp = player(p, basetable.at[iterator, columnnames[1]], basetable.at[iterator, columnnames[2]], basetable.at[iterator, columnnames[3]], basetable.at[iterator, columnnames[4]], basetable.at[iterator, columnnames[5]], basetable.at[iterator, columnnames[6]], basetable.at[iterator, columnnames[7]], basetable.at[iterator, columnnames[8]], basetable.at[iterator, columnnames[9]], basetable.at[iterator, columnnames[10]], basetable.at[iterator, columnnames[11]], basetable.at[iterator, columnnames[12]])
        playerobjects.append(temp)
        iterator += 1
    playerselect['values'] = processed
    offnames = []
    for o in offstats:
        offnames.append(o)
    generatebutton.config(state='active')


def nullchecker(testframe):
    colnames = testframe.columns.values.tolist()
    i = 0
    while i < len(colnames):
        for res in testframe[colnames[i]].unique():
            if res == "True":
                return False
        i += 1
    return True


def verifystats():
    if not str.isdigit(hpbox.get()):
        print("inputted HP was invalid")
        return False
    if not str.isdigit(strbox.get()):
        print("inputted Strength was invalid")
        return False
    if not str.isdigit(magbox.get()):
        print("inputted Magic was invalid")
        return False
    if not str.isdigit(sklbox.get()):
        print("inputted Skill was invalid")
        return False
    if not str.isdigit(spdbox.get()):
        print("inputted Speed was invalid")
        return False
    if not str.isdigit(luckbox.get()):
        print("inputted Luck was invalid")
        return False
    if not str.isdigit(defbox.get()):
        print("inputted Defense was invalid")
        return False
    if not str.isdigit(resbox.get()):
        print("inputted Resistance was invalid")
        return False
    if not str.isdigit(hitbox.get()):
        print("inputted Base Hit was invalid")
        return False
    if not str.isdigit(avoidbox.get()):
        print("inputted Base Avoid was invalid")
        return False
    if not str.isdigit(skltohitbox.get()):
        print("inputted skill per hit bonus was invalid")
        return False
    if not str.isdigit(hitbonusbox.get()):
        print("inputted bonus hit per skill bonus was invalid")
        return False
    if not str.isdigit(spdtoavoidbox.get()):
        print("inputted speed per avoid bonus was invalid")
        return False
    if not str.isdigit(spdavoidbonusbox.get()):
        print("inputted bonus avoid from speed was invalid")
        return False
    if not str.isdigit(lucktobonusbox.get()):
        print("inputted luck per bonus was invalid")
        return False
    if not str.isdigit(bonusfromluckbox.get()):
        print("inputted bonus from luck was invalid")
        return False
    return True


def showmatchup():
    global enemystats
    playerinfo = "Player\n"
    enemyinfo = "Enemy\n"
    if playerselect.get() == "":
        createerror("No player was selected in the dropdown.")
    else:
        found = False
        for i in range(len(playerobjects)):
            if playerobjects[i].name == playerselect.get():
                tempplayer = playerobjects[i]
                found = True
                playerhit = calculatehit(tempplayer.basehit, tempplayer.skill, tempplayer.luck)
                playeravoid = calculateavoid(tempplayer.baseavoid, tempplayer.speed, tempplayer.luck)
                enemyhit = calculatehit(enemystats[8], enemystats[3], enemystats[5])
                enemyavoid = calculateavoid(enemystats[9], enemystats[4], enemystats[5])
                playercrit = calculatecrit(tempplayer.skill, enemystats[5])
                enemycrit = calculatecrit(enemystats[3], tempplayer.luck)
                playerinfo += "Hit: " + str(playerhit) + "\n"
                playerinfo += "Avoid: " + str(playeravoid) + "\n"
                playerinfo += "Hitrate: "
                if 20 + playerhit - enemyavoid > 20:
                    playerinfo += "100%\n"
                elif 20 + playerhit - enemyavoid < 1:
                    playerinfo += "5%\n"
                else:
                    playerinfo += str((20 + playerhit - enemyavoid) * 5) + "%\n"
                playerinfo += "Damage: "
                if tempplayer.strength > tempplayer.magic:
                    playerinfo += str(tempplayer.strength - enemystats[6]) + "\n"
                else:
                    playerinfo += str(tempplayer.magic - enemystats[7]) + "\n"
                playerinfo += "Speed: " + str(tempplayer.speed) + "\n"
                playerinfo += "Crit: " + str(playercrit * 100) + "%\n"
                playerinfo += "DPS: "
                if tempplayer.strength > tempplayer.magic:
                    playerinfo += str(calculatedps(calculatehitrate(playerhit, enemyavoid), playercrit, tempplayer.strength, enemystats[6], calculatedouble(tempplayer.speed, enemystats[4]))) + "\n"
                else:
                    playerinfo += str(calculatedps(calculatehitrate(playerhit, enemyavoid), playercrit, tempplayer.magic, enemystats[7], calculatedouble(tempplayer.speed, enemystats[4]))) + "\n"

                enemyinfo += "Hit: " + str(enemyhit) + "\n"
                enemyinfo += "Avoid: " + str(enemyavoid) + "\n"
                enemyinfo += "Hitrate: "
                if 20 + enemyhit - playeravoid > 20:
                    enemyinfo += "100%\n"
                elif 20 + enemyhit - playeravoid < 1:
                    enemyinfo += "5%\n"
                else:
                    enemyinfo += str((20 + enemyhit - playeravoid) * 5) + "%\n"
                enemyinfo += "Damage: " + str(max(enemystats[1] - tempplayer.defense, enemystats[2] - tempplayer.resistance)) + "\n"
                enemyinfo += "Speed: " + str(enemystats[4]) + "\n"
                enemyinfo += "Crit: " + str(enemycrit * 100) + "%\n"
                enemyinfo += "DPS: "
                if (enemystats[1] - tempplayer.defense) > (enemystats[2] - tempplayer.resistance):
                    enemyinfo += str(calculatedps(calculatehitrate(enemyhit, playeravoid), enemycrit, enemystats[1], tempplayer.defense, calculatedouble(enemystats[4], tempplayer.speed))) + "\n"
                else:
                    enemyinfo += str(calculatedps(calculatehitrate(enemyhit, playeravoid), enemycrit, enemystats[2], tempplayer.resistance, calculatedouble(enemystats[4], tempplayer.speed))) + "\n"
                forecastplayer.config(text=playerinfo)
                forecastenemy.config(text=enemyinfo)

        if not found:
            createerror("An error occurred when finding the player. Contact the developer for more help.")



m = tk.Tk()
m.title("Nealboot Automatic Enemy Generator")
m.geometry('800x600')

instructframe = tk.Frame(m, height=200, width=800, bd=3, relief='ridge')
instructframe.grid(row=0, column=0, columnspan=3)
instructframe.grid_propagate(False)

outputframe = tk.Frame(m, height=400, width=300, bd=3, relief='ridge')
outputframe.grid(row=1, column=0, rowspan=2)
outputframe.grid_propagate(False)

optionframe1 = tk.Frame(m, height=250, width=300, bd=3, relief='ridge')
optionframe1.grid(row=1, column=1)
optionframe1.grid_propagate(False)

optionframe2 = tk.Frame(m, height=400, width=200, bd=3, relief='ridge')
optionframe2.grid(row=1, column=2, rowspan=2)
optionframe2.grid_propagate(False)

forecastframe = tk.Frame(m, height=150, width=300, bd=3, relief='ridge')
forecastframe.grid(row=2, column=1)
forecastframe.grid_propagate(False)

playerforecast = tk.Frame(forecastframe, height=200, width=147)
playerforecast.grid(column=1, row=0)
playerforecast.grid_propagate(False)

enemyforecast = tk.Frame(forecastframe, height=200, width=147)
enemyforecast.grid(column=0, row=0)
enemyforecast.grid_propagate(False)

hplabel = tk.Label(optionframe2, text="HP:")
hplabel.grid(column=0, row=0)
hpbox = tk.Entry(optionframe2, width=6, justify='left')
hpbox.grid(column=1, row=0)
hpbox.insert(0, "0")

strlabel = tk.Label(optionframe2, text="Strength:")
strlabel.grid(column=0, row=1)
strbox = tk.Entry(optionframe2, width=6, justify='left')
strbox.grid(column=1, row=1)
strbox.insert(0, "0")

maglabel = tk.Label(optionframe2, text="Magic:")
maglabel.grid(column=0, row=2)
magbox = tk.Entry(optionframe2, width=6, justify='left')
magbox.grid(column=1, row=2)
magbox.insert(0, "0")

skllabel = tk.Label(optionframe2, text="Skill:")
skllabel.grid(column=0, row=3)
sklbox = tk.Entry(optionframe2, width=6, justify='left')
sklbox.grid(column=1, row=3)
sklbox.insert(0, "0")

spdlabel = tk.Label(optionframe2, text="Speed:")
spdlabel.grid(column=0, row=4)
spdbox = tk.Entry(optionframe2, width=6, justify='left')
spdbox.grid(column=1, row=4)
spdbox.insert(0, "0")

lucklabel = tk.Label(optionframe2, text="Luck:")
lucklabel.grid(column=0, row=5)
luckbox = tk.Entry(optionframe2, width=6, justify='left')
luckbox.grid(column=1, row=5)
luckbox.insert(0, "0")

deflabel = tk.Label(optionframe2, text="Defense:")
deflabel.grid(column=0, row=6)
defbox = tk.Entry(optionframe2, width=6, justify='left')
defbox.grid(column=1, row=6)
defbox.insert(0, "0")

reslabel = tk.Label(optionframe2, text="Resistance:")
reslabel.grid(column=0, row=7)
resbox = tk.Entry(optionframe2, width=6, justify='left')
resbox.grid(column=1, row=7)
resbox.insert(0, "0")

hitlabel = tk.Label(optionframe2, text="Base Hit:")
hitlabel.grid(column=0, row=8)
hitbox = tk.Entry(optionframe2, width=6, justify='left')
hitbox.grid(column=1, row=8)
hitbox.insert(0, "0")

avoidlabel = tk.Label(optionframe2, text="Base Avoid:")
avoidlabel.grid(column=0, row=9)
avoidbox = tk.Entry(optionframe2, width=6, justify='left')
avoidbox.grid(column=1, row=9)
avoidbox.insert(0, "0")

generatebutton = tk.Button(optionframe2, text="Test", fg='green', command=generate, width=10, state='disabled')
generatebutton.grid(column=0, row=10, columnspan=2)

instructions = tk.Label(instructframe, text="To generate enemies, first input a .csv file containing all your players "
                                            "in the following format: Name, HP, Strength, Magic, Skill, Speed, Luck, "
                                            "Defense, Resistance, Base Hit, Base Avoid, Base Crit, and Offensive "
                                            "Stat. Then input the enemy's stats in the boxes on the bottom right. "
                                            "Do note that this currently does not take enemy skills  and weapons into "
                                            "account so you will likely need to adjust it accordingly. If you want to "
                                            "recalculate player matchups, you will have to use the test button again "
                                            "after you have changed your stat parameters.", wraplength=800,
                                            justify='left')
instructions.grid()

forecastenemy = tk.Label(enemyforecast, wraplength=140, justify='left')
forecastplayer = tk.Label(playerforecast, wraplength=140, justify='left')
forecastenemy.grid()
forecastplayer.grid()

outputtext = tk.Label(outputframe)
outputtext.grid()

fileinputdesc = tk.Label(optionframe1, text="Select CSV", wraplength=300, justify='left')
fileinputdesc.grid(row=0, column=0, columnspan=2)

fileinput = tk.Entry(optionframe1, width=30, state='disabled')
fileinput.grid(row=1, column=0)

filebutton = tk.Button(optionframe1, command=selectfile, text="Select File")
filebutton.grid(row=1, column=1)

playerdesc = tk.Label(optionframe1, text="Select Player for Forecast", wraplength=300, justify='left')
playerdesc.grid(row=4, column=0)
playerselect = ttk.Combobox(optionframe1, values=playerlist)
playerselect.grid(row=5, column=0)
testplayer = tk.Button(optionframe1, text="Test Player", state='disabled', command=showmatchup)
testplayer.grid(row=5, column=1)

skldesc = tk.Label(optionframe1, text="Skill per hit bonus", wraplength=300, justify='left')
skldesc.grid(row=6, column=0)
skltohitbox = tk.Entry(optionframe1, width=6, justify='left')
skltohitbox.grid(row=6, column=1)
skltohitbox.insert(0, "3")

sklhitbonusdesc = tk.Label(optionframe1, text="Hit bonus per skill benefit", wraplength=300, justify='left')
sklhitbonusdesc.grid(row=7, column=0)
hitbonusbox = tk.Entry(optionframe1, width=6, justify='left')
hitbonusbox.grid(row=7, column=1)
hitbonusbox.insert(0, "1")

spddesc = tk.Label(optionframe1, text="Speed per avoid bonus", wraplength=300, justify='left')
spddesc.grid(row=8, column=0)
spdtoavoidbox = tk.Entry(optionframe1, width=6, justify='left')
spdtoavoidbox.grid(row=8, column=1)
spdtoavoidbox.insert(0, "3")

spdavoidbonusdesc = tk.Label(optionframe1, text="Avoid bonus per speed benefit", wraplength=300, justify='left')
spdavoidbonusdesc.grid(row=9, column=0)
spdavoidbonusbox = tk.Entry(optionframe1, width=6, justify='left')
spdavoidbonusbox.grid(row=9, column=1)
spdavoidbonusbox.insert(0, "1")

luckdesc = tk.Label(optionframe1, text="Luck per hit/avoid bonus", wraplength=300, justify='left')
luckdesc.grid(row=10, column=0)
lucktobonusbox = tk.Entry(optionframe1, width=6, justify='left')
lucktobonusbox.grid(row=10, column=1)
lucktobonusbox.insert(0, "5")

luckbonusdesc = tk.Label(optionframe1, text="Hit/avoid bonus per luck benefit", wraplength=300, justify='left')
luckbonusdesc.grid(row=11, column=0)
bonusfromluckbox = tk.Entry(optionframe1, width=6, justify='left')
bonusfromluckbox.grid(row=11, column=1)
bonusfromluckbox.insert(0, "1")

m.mainloop()
