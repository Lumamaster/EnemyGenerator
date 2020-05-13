import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import numpy as np
import math
import random
from tkinter.filedialog import askopenfilename

filepath = ""

basetable = pd.DataFrame.empty

statnames = ["Name", "HP", "Strength", "Magic", "Skill", "Speed", "Luck", "Defense", "Resistance", "Base Hit", "Base Avoid", "Base Crit", "Offensive Stat"]

playernum = 0

playerlist = ["Placeholder"]

playerobjects = []

generatedstats = []


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
    return baseavoid + math.floor(speed/4) * 2 + math.floor(luck/5)


def calculatehit(basehit, skill, luck):
    return basehit + math.floor(skill/3) + math.floor(luck/5)


def calculatecrit(enemyskill, playerluck):
    return min(max(int((enemyskill - playerluck) / 5)/20, 0), 20)


def calculatehitrate(hit, avoid):
    return max(min(1, (hit - avoid)/20), 0.05)


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
    if critrate >= hitrate:
        basedamage *= 3
    else:
        if critrate > 0:
            critpercent = critrate/hitrate
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
    pdps = 0
    if player.offensivestat == "STR":
        pdps = calculatedps(calculatehitrate(calculatehit(player.basehit, player.skill, player.luck), calculateavoid(7, enemy[4], enemy[5])), calculatecrit(player.skill, enemy[5]), player.strength, enemy[6], calculatedouble(player.speed, enemy[4]))
    else:
        pdps = calculatedps(calculatehitrate(calculatehit(player.basehit, player.skill, player.luck), calculateavoid(7, enemy[4], enemy[5])), calculatecrit(player.skill, enemy[5]), player.magic, enemy[7], calculatedouble(player.speed, enemy[4]))
    print("player dps: " + str(pdps))
    edps = 0
    if enemy[1] > enemy[2]:
        edps = calculatedps(calculatehitrate(calculatehit(0, enemy[3], enemy[5]), calculateavoid(player.baseavoid, player.speed, player.luck)), calculatecrit(enemy[3], player.luck), enemy[1], player.defense, calculatedouble(enemy[4], player.speed))
    else:
        edps = calculatedps(calculatehitrate(calculatehit(0, enemy[3], enemy[5]), calculateavoid(player.baseavoid, player.speed, player.luck)), calculatecrit(enemy[3], player.luck), enemy[2], player.resistance, calculatedouble(enemy[4], player.speed))
    print("enemy dps: " + str(edps))
    while php > 0 and ehp > 0:
        php -= edps
        ehp -= pdps
    if php <= 0:
        return True
    else:
        return False


def validate(stats, players, target):
    print("testting statrange " + str(stats))
    playerwins = 0
    for i in range(len(players)):
        print("testting matchup vs " + players[i].name)
        if calculatematchup(players[i], stats):
            print("matchup won")
            playerwins += 1
        else:
            print("matchup lost")
    if playerwins == target:
        return True
    else:
        return False


def generate():
    global playernum
    global basetable
    global generatedstats
    # get percentage of players enemy can beat, set to 50 by default if invalid value
    if type(percententry.get()) != type(int):
        settext(percententry, "50")
    percent = int(percententry.get())
    tempstats = [0] * 8
    playersbeaten = int(float(percent/100) * playernum)
    for i in range(8):
        tempstats[i] = int(basetable[statnames[i+1]].mean())
        tempstats[i] = int((1 + random.random() * 0.6 - 0.3) * tempstats[i])
        if tempstats[i] < 0:
            tempstats[i] = 0
    while not validate(tempstats, playerobjects, playersbeaten):
        for i in range(8):
            tempstats[i] = int(basetable[statnames[i + 1]].mean())
            tempstats[i] = int((1 + random.random() * 0.6 - 0.3) * tempstats[i])
            if tempstats[i] < 0:
                tempstats[i] = 0
    generatedstats = tempstats
    statstring = ""
    statstring += "HP: " + str(generatedstats[0]) + "\n"
    statstring += "STR: " + str(generatedstats[1]) + "\n"
    statstring += "MAG: " + str(generatedstats[2]) + "\n"
    statstring += "SKL: " + str(generatedstats[3]) + "\n"
    statstring += "SPD: " + str(generatedstats[4]) + "\n"
    statstring += "LUCK: " + str(generatedstats[5]) + "\n"
    statstring += "DEF: " + str(generatedstats[6]) + "\n"
    statstring += "RES: " + str(generatedstats[7]) + "\n"
    statstring += "\n\n\n\nPlease note that these stats do not take into account weapons, skills, etc., and should be " \
                  "tuned accordingly for your purposes."
    outputtext['text'] = statstring


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
    offenseselect['values'] = offnames
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


def seteasy():
    percententry.config(state='normal')
    settext(percententry, "25")
    percententry.config(state='disabled')


def setmed():
    percententry.config(state='normal')
    settext(percententry, "50")
    percententry.config(state='disabled')


def sethard():
    percententry.config(state='normal')
    settext(percententry, "75")
    percententry.config(state='disabled')


def setcust():
    percententry.config(state='normal')


m = tk.Tk()
m.title("Nealboot Automatic Enemy Generator")
m.geometry('800x600')

instructframe = tk.Frame(m, height=200, width=800, bd=3, relief='ridge')
instructframe.grid(row=0, column=0, columnspan=3)
instructframe.grid_propagate(False)

outputframe = tk.Frame(m, height=400, width=300, bd=3, relief='ridge')
outputframe.grid(row=1, column=0, rowspan=2)
outputframe.grid_propagate(False)

optionframe1 = tk.Frame(m, height=200, width=300, bd=3, relief='ridge')
optionframe1.grid(row=1, column=1)
optionframe1.grid_propagate(False)

optionframe2 = tk.Frame(m, height=400, width=200, bd=3, relief='ridge')
optionframe2.grid(row=1, column=2, rowspan=2)
optionframe2.grid_propagate(False)

forecastframe = tk.Frame(m, height=200, width=300, bd=3, relief='ridge')
forecastframe.grid(row=2, column=1)
forecastframe.grid_propagate(False)

playerforecast = tk.Frame(forecastframe, height=200, width=147)
playerforecast.grid(column=1, row=0)
playerforecast.grid_propagate(False)

enemyforecast = tk.Frame(forecastframe, height=200, width=147)
enemyforecast.grid(column=0, row=0)
enemyforecast.grid_propagate(False)

generatebutton = tk.Button(optionframe2, text="Generate", fg='green', state='disabled', command=generate)
generatebutton.grid(row=5)

percententry = tk.Entry(optionframe2, width=10, state='disabled')
percententry.grid(row=4)
settext(percententry, "0")

instructions = tk.Label(instructframe, text="To generate enemies, first input a .csv file containing all your players "
                                            "in the following format: Name, HP, Strength, Magic, Skill, Speed, Luck, "
                                            "Defense, Resistance, Base Hit, Base Avoid, Base Crit, and Offensive "
                                            "Stat. By default, there are three options for easy, medium, and hard "
                                            "enemies. You can also input a custom percentage of players you want the "
                                            "enemy to be stronger than on average. Do note that this currently does not"
                                            " take enemy skills into account so you will likely need to adjust it "
                                            "accordingly.", wraplength=800, justify='left')
instructions.grid()

forecastenemy = tk.Label(enemyforecast, text="Enemy Forecast", wraplength=140, justify='left')
forecastplayer = tk.Label(playerforecast, text="Player Forecast", wraplength=140, justify='left')
forecastenemy.grid()
forecastplayer.grid()

outputtext = tk.Label(outputframe, text="Enemy Output")
outputtext.grid()

fileinputdesc = tk.Label(optionframe1, text="Select CSV", wraplength=300, justify='left')
fileinputdesc.grid(row=0, column=0, columnspan=2)

fileinput = tk.Entry(optionframe1, width=30, state='disabled')
fileinput.grid(row=1, column=0)

filebutton = tk.Button(optionframe1, command=selectfile, text="Select File")
filebutton.grid(row=1, column=1)

easy = tk.Radiobutton(optionframe2, text='Easy', value=0, command=seteasy)
medium = tk.Radiobutton(optionframe2, text='Medium', value=1, command=setmed)
hard = tk.Radiobutton(optionframe2, text='Hard', value=2, command=sethard)
custom = tk.Radiobutton(optionframe2, text='Custom', value=3, command=setcust)
easy.grid(row=0)
medium.grid(row=1)
hard.grid(row=2)
custom.grid(row=3)
easy.select()
medium.deselect()
hard.deselect()
custom.deselect()

offensedesc = tk.Label(optionframe1, text="Select Offensive Stat", wraplength=300, justify='left')
offensedesc.grid(row=2, column=0)
offenseselect = ttk.Combobox(optionframe1)
offenseselect.grid(row=3, column=0)

playerdesc = tk.Label(optionframe1, text="Select Player for Forecast", wraplength=300, justify='left')
playerdesc.grid(row=4, column=0)
playerselect = ttk.Combobox(optionframe1, values=playerlist)
playerselect.grid(row=5, column=0)

m.mainloop()
