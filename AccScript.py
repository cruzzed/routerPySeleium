from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import subprocess
import time
import requests
import json

apt_dict = {"Vista A": 0,
            "Vista A1": 1,
            "Vista A2": 2,
            "Endah C": 3,
            "Endah D": 4,
            "Fortune Park A": 5,
            "Fortune Park B": 6,
            "Academia": 7}
apt_array = ["VC-A-","VC-A1","VC-A2","EP-C","EP-D","FP-A","FP-B","AC"]

wifi_init = subprocess.check_output('netsh wlan show interfaces').decode('utf-8').split()
wifi_init = wifi_init[wifi_init.index("SSID")+2].split("@")[0] #takes the house name, not including the @
#wifi_init = wifi_init[:5]
index_of_wifi_list = 0

for elem in apt_array:
    if elem in wifi_init:
        index_of_wifi_list = apt_array.index(elem)
        break
    index_of_wifi_list =+ 1

routerMac=subprocess.check_output(["arp","-a", "192.168.0.1"]).decode('utf-8').split()[-2].split('-') #get MAC of router
routerMac = ''.join(routerMac).upper()
print(routerMac[-4:])

url = "http://192.168.0.1/webpages/login.html" #set url var
username = "admin" #set username var
password = "TIME"+routerMac[-4:] #set password var
#newpassword = "APU@"+routerMac[-4:] <- ignore
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
driver.get(url)
driver.implicitly_wait(10)

#enter input
driver.find_element_by_id("login-username").send_keys(username)
driver.find_element_by_xpath("//input[@type='password']").send_keys(password)
driver.find_element_by_id("login-btn").click()
#if wrong pass then ask here

#go take pppoe user and pass
while True:
    try:
        wait.until(EC.element_to_be_clickable((By.NAME,"advanced"))).click()#buggy so need this workaround
    except:
        print("Wrong click, retrying...")
        continue
    break
wait.until(EC.presence_of_element_located((By.NAME,"network"))).click()
wait.until(EC.presence_of_element_located((By.NAME,"internet"))).click()
#pppoe page
pppoe_username = driver.find_element_by_xpath("//input[@name='username']").get_attribute("snapshot")
while(pppoe_username == None):
    pppoe_username = driver.find_element_by_xpath("//input[@name='username']").get_attribute("snapshot")#get pppoe_username
print(pppoe_username)
pppoe_password = driver.find_element_by_xpath("//input[@name='password']").get_attribute("value")#get pppoe_password
print(pppoe_password)
#take modem sn (impossible)
#go change webcontrol password to APU@<4-digit-MAC> and save
wait.until(EC.presence_of_element_located((By.NAME,"system-tools"))).click()#clicks on system tools tab
wait.until(EC.presence_of_element_located((By.NAME,"administration"))).click()#clicks on administration tab
driver.find_element_by_xpath("//input[@name='old_acc']").send_keys("wait")#input wait
while(driver.find_element_by_xpath("//input[@name='old_acc']").get_attribute("value")!=''):# wait until textbox is reset to empty
    pass
driver.find_element_by_xpath("//input[@name='old_acc']").send_keys(username)# input admin username
driver.find_element_by_xpath("//div[@class='container widget-container text-container password-container  ']//input[@type='password']").send_keys(password)#input old admin password
driver.find_element_by_xpath("//input[@name='new_acc']").send_keys(username)# input new admin username
driver.find_element_by_xpath("//div[@class='container widget-container text-container password-container  level']//input[@type='password']").send_keys(password)#input admin new password
driver.find_element_by_xpath("//div[@class='container widget-container text-container password-container inline']//input[@type='password']").send_keys(password)#input admin confirm password
#driver.find_element(By.XPATH, "//div[@class='form-submit button-container submit']//button[@type='button']").click()#click submit button
#last thing, set wifi username and pass and save
#2.4GHz wifi page
wait.until(EC.presence_of_element_located((By.NAME,"wireless"))).click()
wait.until(EC.presence_of_element_located((By.NAME,"wireless-settings"))).click()
wait.until(EC.presence_of_element_located((By.ID,"show_2g"))).click()
while(driver.find_element_by_xpath("//input[@name='ssid']").get_attribute("value")==''):# wait until textbox is reset to empty
    pass
if (driver.find_element_by_xpath("//input[@name='ssid']").get_attribute("value").find("@")==-1):
    driver.find_element_by_xpath("//input[@name='ssid']").send_keys("@2.4GHz")

if (driver.find_element_by_xpath("//input[@type='password']").get_attribute("value")!=''):
    wifinewpass = driver.find_element_by_xpath("//input[@type='password']").get_attribute("value")
    driver.find_element_by_xpath("//input[@type='password']").clear()
    driver.find_element_by_xpath("//input[@type='password']").send_keys(wifinewpass)
#driver.find_element(By.XPATH, "//div[@class='form-submit button-container submit']//button[@type='button']").click()#click submit button
#5GHz wifi page
wait.until(EC.presence_of_element_located((By.ID,"show_5g"))).click()
while(driver.find_element_by_xpath("//input[@name='ssid']").get_attribute("value")==''):# wait until textbox is reset to empty
    pass
if (driver.find_element_by_xpath("//input[@name='ssid']").get_attribute("value").find("@")==-1):
    driver.find_element_by_xpath("//input[@name='ssid']").send_keys("@5GHz")

if (driver.find_element_by_xpath("//input[@type='password']").get_attribute("value")!=''):
    wifinewpass = driver.find_element_by_xpath("//input[@type='password']").get_attribute("value")
    driver.find_element_by_xpath("//input[@type='password']").clear()
    driver.find_element_by_xpath("//input[@type='password']").send_keys(wifinewpass)
#driver.find_element(By.XPATH, "//div[@class='form-submit button-container submit']//button[@type='button']").click()#click submit button

# TODO 
# 1. replace all hardcoded variable 
# - unitName
# - SSID
# - routerModel
# - routerSN
# - routerMac
# 2. Maybe different router different selenium solution ?
# 3. Try save the token in a file maybe ? so it wont ask for token everytime 
# --- It's for future enchancement, for now its still okey 


unitInfo = {
        "token": getToken(),
        "unitNumber": "A1-10-06",
        "ssid": "VS-A1-10-06",
        "wifiPass": wifinewpass,
        "PPPoeUserName": pppoe_username,
        "PPPoePassword": pppoe_password,
        "routerModel": "TP-LINK AC1200",
        "routerSN": "ASDSADSADSAD",
        "routerMac": "ADSDSADASD",
        "routerPass": password
    }


def getToken():
    loginUrl = "https://us-central1-chengkangzai.cloudfunctions.net/login"
    loginInfo = {
        "email": "email@email.com",
        "password": "password",
        "unit": unitName
    }
    payload = json.dumps(loginInfo)
    headers = {'Content-Type': 'application/json'}
    response = requests.request(
        "POST", loginUrl, headers=headers, data=payload)
    jsonString = json.loads(response.text)
    token = jsonString['token']
    return(token)




def sendInformation():
    
    updateUrl = "https://us-central1-chengkangzai.cloudfunctions.net/updateUnit"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps(unitInfo)
    response = requests.request(
        "POST", updateUrl, headers=headers, data=payload)
    jsonString = json.loads(response.text)
    if jsonString['stauts'] == 400:
    print(jsonString['message'])
    else:
        print("Something wrong" + jsonString['message'])

sendInformation()