import sqlite3
from random import choice
import re
import os
import time


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def connectDB():
    try:
        connection = sqlite3.connect("datab.sqlite")
        print("connected to the DataBase.")
        return connection
    except Exception as err:
        print(err)
        return None


def createDBtable(connection):
    c = connection.cursor()
    try:
        sqlCommand = '''CREATE TABLE "Users" (
                          "username"  TEXT NOT NULL UNIQUE,
                          "password"  TEXT NOT NULL,
                          "win"  INTEGER,
                          "lose"  INTEGER,
                          PRIMARY KEY("username")
                        );'''
        c.execute(sqlCommand)
        print("Database configuration complete")
    except Exception as err:
        if "already exists" in str(err):
            print("Database Table is ready.")
        else:
            print("Can't create Table.")
            raise Exception("Something went wrong at creation of table: {}".format(err))


def user_pass_checker(username):
    pattern = re.compile("[A-Za-z0-9]+")
    if pattern.fullmatch(username):
        return True
    else:
        return False


def check_existence(connection, username):
    cur = connection.cursor()
    cur.execute("SELECT username FROM Users WHERE lower(username) = (?)", (username.lower(),))
    data = cur.fetchone()
    if data:
        if data[0].lower() == username.lower():
            return True
    else:
        return False


def signup(connection, username, password):
    try:
        cur = connection.cursor()
        cur.execute("INSERT INTO Users(username, password) VALUES (?,?)", (username, password))
        connection.commit()
    except Exception as err:
        print("Some thing went wrong with your signing up", err)


def password_checker(connection, userName, passWord):
    cur = connection.cursor()
    cur.execute("SELECT username, password FROM Users WHERE lower(username) = (?)", (userName.lower(),))
    data = cur.fetchone()
    if data:
        if data[1] == passWord:
            return True
    else:
        return False


def stats(connection, username):
    cur = connection.cursor()
    cur.execute("SELECT username, win, lose FROM Users WHERE lower(username) = (?)", (username.lower(),))
    data = list(cur.fetchone())
    for i in range(len(data)):
        if data[i] is None:
            data[i] = 0
    try:
        rate = int(data[1]/(data[1]+data[2])*100)
    except ZeroDivisionError:
        if data[1] != 0:
            rate = 100
        else:
            rate = 0
    stat = "{}, your win rate is {}% with {} wins and {} loses.".format(data[0], rate, data[1], data[2])
    return stat


def game_menu(connection, username):
    while True:
        time.sleep(2)
        clear_screen()
        menuText = '''THIS IS RPS GAME.\nChoose as you wish:\n1. Start a New Game.\n2. Show my stats.\n3. Logout.\n> '''
        inp = input(menuText)
        match inp:
            case '1':
                game_core(connection, username)
            case '2':
                stat = stats(connection, username)
                print(stat)
                print("Wait for this to be gone...")
                time.sleep(3)
            case '3':
                print("logging out...")
                break
            case _:
                print("Valid inputs are 1, 2, 3.")


def win(connection, username):
    cur = connection.cursor()
    cur.execute("SELECT username, win FROM Users WHERE lower(username) = (?)", (username.lower(),))
    data = list(cur.fetchone())
    for i in range(len(data)):
        if data[i] is None:
            data[i] = 0
    nwin = data[1] + 1
    cur.execute(''' UPDATE Users SET win = ? WHERE lower(username) = (?)''', (nwin, username.lower()))
    connection.commit()


def lost(connection, username):
    cur = connection.cursor()
    cur.execute("SELECT username, lose FROM Users WHERE lower(username) = (?)", (username.lower(),))
    data = list(cur.fetchone())
    for i in range(len(data)):
        if data[i] is None:
            data[i] = 0
    nlose = data[1] + 1
    cur.execute(''' UPDATE Users SET lose = ? WHERE lower(username) = (?)''', (nlose, username.lower()))
    connection.commit()


def game_core(connection, username):
    userscore = 0
    botscore = 0

    while True:
        tscore = 5
        print("Set the target score. (Min is 3 and max is 10. 5 is recommended.) ")
        try:
            tscore = int(input(": "))
            if tscore > 10:
                print("Maximum is 10.")
                continue
            elif tscore < 3:
                print("Min is 3")
                continue
        except:
            print("Please enter a number.")

        moves = ['rock', 'paper', 'scissors']
        validnums = [1, 2, 3]
        gametxt= '''Choose your move.\n1. ROCK\n2. PAPER \n3. SCISSORS\n>> '''
        rounds = 0
        while rounds < tscore:
            while True:
                try:
                    usermove = int(input(gametxt))
                    if usermove in validnums:
                        if usermove == 1:
                            usermove = moves[0]
                        elif usermove == 2:
                            usermove = moves[1]
                        else:
                            usermove = moves[2]
                    else:
                        print("Enter a number from 1 to 3.")
                        continue
                    break
                except:
                    print("Please Enter a number.")
            botmove = choice(moves)
            print("User move is:", usermove, "| {} is bot move ".format(botmove))
            if usermove == botmove:
                print("TIE! both played", usermove)
            elif usermove == 'rock':
                if botmove == 'scissors':
                    print("Rock smashes scissors, YOU WON!")
                    userscore += 1
                else:
                    print("Paper covers rock, YOU LOST!")
                    botscore += 1
            elif usermove == 'scissors':
                if botmove == 'paper':
                    print("Scissors cuts paper, YUO WON!")
                    userscore += 1
                else:
                    print("Rock smashes scissors, YOU LOST!")
                    botscore += 1
            elif usermove == 'paper':
                if botmove == 'rock':
                    print("Paper covers rock, YOU WON!")
                    userscore += 1
                else:
                    print("Scissors cuts paper, YUO LOST!")
                    botscore += 1
            else:
                print("this was not supposed  to happen!")
                break
            print("-----------------")
            print("YOU {} - {} Computer".format(userscore, botscore))
            rounds += 1
        break

    if userscore == botscore:
        print(f"You scored {userscore} and your computer scored {botscore} wins.\nIt's a Tie and Ties won't be counted.")
        time.sleep(5)
    elif userscore > botscore:
        win(connection, username)
        print(f'''You scored {userscore} and your computer scored {botscore} wins.
        You have WON the game.
        Congratulations.''')
        time.sleep(5)
    else:
        lost(connection, username)
        print(f'''Your computer scored {botscore} and You scored {userscore} wins.\nbetter luck next time.''')
        time.sleep(5)


while True:
    db = connectDB()
    cur = db.cursor()
    if db:
        try:
            createDBtable(db)
        except:
            print("something went wrong with Tables. Exiting...")
            break
    else:
        print("Error with Database connection.")
        break
    print("You are all set.")
    while True:
        time.sleep(2)
        clear_screen()
        mainText = '''Welcome to RPS Game.\nYou need to login before playing.\n1. Login\n2. Sign Up
Type and Enter your desired action number or q for exit.'''
        print(mainText)
        usrinp = input("> ")
        if usrinp == '1':
            username = input("Enter your Username: ")
            password = input("Enter your Password: ")
            if check_existence(db, username):
                if password_checker(db, username, password):
                    print("You have successfully logged in")
                    game_menu(db, username)
                else:
                    print("Wrong password.")
                    continue
            else:
                print("Username 404. not found.")
                continue
        elif usrinp == '2':
            print("Valid characters for both username and password are a-z and 0-9.")
            userName = input("Enter an Username: ")
            if user_pass_checker(userName):
                if check_existence(db, userName):
                    print("Username already exists. choose a different one.")
                    continue
            else:
                print("Wrong input, Try again.")
                continue
            print("Now choose a strong password at least 6 characters.")
            passWord = input("Enter a Password: ")
            if user_pass_checker(passWord):
                if len(passWord) >= 6:
                    signup(db, userName, passWord)
                    print("* Account Created *")
                    time.sleep(2)
                else:
                    print("Password is too short. Try again.")
                    continue
            else:
                print("Invalid characters detected. Try again.")
        elif usrinp.lower() == 'q':
            print("Goodbye.")
            break
        else:
            print("Allowed inputs are 1, 2 or q. Try again.")

    db.close()
    break
