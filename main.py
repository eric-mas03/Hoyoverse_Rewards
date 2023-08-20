import requests, json, time, os

from colorama import init, Fore
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

USER_DATA_RUTE = f"--user-data-dir=C:\\Users\\{os.getlogin()}\\AppData\\Local\\Microsoft\\Edge\\User Data Hoyoverse_rewards"

init()
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RED = Fore.RED
WHITE = Fore.WHITE
YELLOW = Fore.YELLOW
RESET = Fore.RESET

def get_codes(url) -> None:
    """Go to the website and get all the codes."""
    codes = []

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        all_tr_elements = soup.find_all('tr')

        for tr in all_tr_elements:
            if not "Expired" in tr.text:
                tds = tr.find_all('td')

                try:
                    if " " in tds[0].text: continue
                    codes.append(tds[0].text.replace('\n', ''))

                except:pass
                
        codes = list(dict.fromkeys(codes))
        print(f"[{YELLOW}!{RESET}] Codes: {codes}")

    else:
        print(f"{RED}[{WHITE}·{RED}] {RESET}Failed to fetch the website. Status code: {response.status_code}")

    return codes
 

def redeem_code(codes: list, ACCOUNT: dict, manual: bool = False) -> None:
    """Logs in and redeems the codes."""
    options = webdriver.EdgeOptions()
    options.add_argument(USER_DATA_RUTE)
    options.add_argument("--start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # Removes the logs
    
    if not manual: options.add_argument("--headless")
    
    try: driver = webdriver.Edge(options=options)
    except: 
        options.arguments.remove(USER_DATA_RUTE)
        driver = webdriver.Edge(options=options)

    first = True

    print(f'{YELLOW}================================\n{BLUE}[{WHITE}·{BLUE}] {RESET}STARTING CODE REDEEMTION PAGE...')
    for code in codes:
        driver.get('https://genshin.hoyoverse.com/en/gift?code=' + code)
    
        if first == True:
            try: 
                print(f'{BLUE}[{WHITE}·{BLUE}] {RESET}Trying to log-in...')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cdkey-form__submit')))
                driver.execute_script('document.getElementsByClassName("login__btn")[0].click()')
                
                try: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'hyv-account-frame')))
                except: pass
                
                driver.switch_to.frame(driver.find_element(By.ID, 'hyv-account-frame'))
      
                try: 
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'el-input__inner')))
                    driver.find_elements(By.CLASS_NAME, "el-input__inner")[0].send_keys(ACCOUNT['username'])
                    driver.find_elements(By.CLASS_NAME, "el-input__inner")[1].send_keys(ACCOUNT['password'])
                    driver.find_elements(By.CLASS_NAME, "el-button")[0].click()
                    time.sleep(10)
                except: pass

                driver.switch_to.default_content()

                driver.execute_script("window.scrollTo(0, 0);")
                driver.execute_script("document.body.style.zoom='50%'")
                
                if not manual and not "salir" in driver.page_source.lower() and not "log out" in driver.page_source.lower():
                    print(f'{RED}[{WHITE}·{RED}] {RESET}Error, manual login required.')
                    driver.quit()
                    redeem_code(codes, ACCOUNT, True)
                    return None
                
                if manual: 
                    print(f'{BLUE}[{WHITE}·{BLUE}] {RESET}Press any key to continue once login is finished...')
                    input()

                time.sleep(10)
            
            except: first = False
        
        i = 0
        while ACCOUNT['nickname'] not in driver.page_source:
            i += 1
            time.sleep(1)
            if i == 10: break

        driver.execute_script('document.getElementsByClassName("cdkey-select__option")[1].click()')
        driver.execute_script("window.scrollTo(0, 0);")
        first = False

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cdkey-form__submit')))    
        time.sleep(5)
        driver.execute_script('document.getElementsByClassName("cdkey-form__submit")[0].click()')
        for _ in range(20):
            try: 
                if "in use".lower() in driver.execute_script('return document.getElementsByClassName("cdkey-result")[0].innerText').lower() \
                or "ya utilizado".lower() in driver.execute_script('return document.getElementsByClassName("cdkey-result")[0].innerText').lower():
                    print(f'{RED}[{WHITE}·{RED}] {RESET}Code [{RED}{code}{RESET}] already in use.')
                    break
                else: 
                    print(f'{GREEN}[{WHITE}·{GREEN}] {RESET}Code [{GREEN}{code}{RESET}] redeemed.')
                    break
            except: time.sleep(0.5)
       
    driver.quit()


def fill_form(driver: webdriver, ACCOUNT: dict, manual: bool) -> None:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'input-container')))
    time.sleep(2)
    ActionChains(driver).send_keys(Keys.TAB).perform()
    ActionChains(driver).send_keys(Keys.TAB).perform()
    ActionChains(driver).send_keys(Keys.TAB).perform()
    ActionChains(driver).send_keys(ACCOUNT['username']).perform()
    ActionChains(driver).send_keys(Keys.TAB).perform()
    ActionChains(driver).send_keys(ACCOUNT['password']).perform()
    ActionChains(driver).send_keys(Keys.TAB).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    if manual: 
        print(f'{BLUE}[{WHITE}·{BLUE}] {RESET}Press any key to continue once login is finished...')
        input()


def daily_check_in(ACCOUNT: dict, manual: bool = False) -> None:
    """Logs in and does the daily check in."""
    options = webdriver.EdgeOptions()
    options.add_argument(USER_DATA_RUTE)
    options.add_argument("--start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # Removes the logs
    if not manual: options.add_argument("--headless")

    try: driver = webdriver.Edge(options=options)
    except: 
        options.arguments.remove(USER_DATA_RUTE)
        driver = webdriver.Edge(options=options)
    
    print(f'{YELLOW}================================\n{BLUE}[{WHITE}·{BLUE}] {RESET}STARTING DAILY CHECK-IN PAGE...')
    driver.get('https://act.hoyolab.com/ys/event/signin-sea-v3/index.html?act_id=e202102251931481&lang=en-us')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'mhy-hoyolab-account-block__avatar')))
    driver.execute_script('document.getElementsByClassName("mhy-hoyolab-account-block__avatar")[0].click()')

    try:
        print(f'{BLUE}[{WHITE}·{BLUE}] {RESET}Trying to log-in...') 
        fill_form(driver, ACCOUNT, manual)
    except: pass

    i = 0
    # Wait until other profile pic appears, to know that the login was successful
    while "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAMAAACdt4HsAAAAAXNSR0IArs4c6QAAAbxQTFRFAAAAAAAAAAD/////mZmZmczMzMzMiYmdsbHEgI+fr7/PhpKetsLOg5Kgr73Mh5GljJuqtL7NhJOjsr7Os7/Oh5Oisb3PhZWlsr/PhpOjs73NhZKktLzOhpKisrzOhZOjs73PhZSks73OhpKjqLPFqrXFs7zOhpKjs77PhZGisr3OhZKjs77PhZKjs77PhZKjsbzOsr7OhJKjs7zNhpOksr3PhZKjsr3Osr7PhZKksr3OhZKisr3OhZKksr7OhZKks73PhZKjsb3OhpKjsr3PhZKjhpOksr3Os77PhZKjhpOkh5Okh5Skh5SliJWmiZanipanipenipeojJmqjZmpjZqrjpqrkJ2ukZ2ukZ6vkp+wk5+wlaGylaKylaKzlqKzl6O0mKS1maW2nKe1oKq3oKy8oqy5oq2+o66/pbDCpbHCprLDqbO+qrXGq7bHrLXArLfIrLfJrLjJrrnKr7rLr7vLsLvMsLzMsbvNsbzNsr3Nsr3Otb3Htr7IusHLvMTNzNHY09je2Nzi29/k3eHl4OPn5ejr5+rt6ezu6ezv6uzv8vP18/X2+Pn6+fr6+/z8/Pz8/Pz9/v7+////v0NOrAAAAEl0Uk5TAAEBAQUFBQ0NEBAVFSMjMzMzU1NUVVVgYGFhc3N+fn9/jIyNjY2NpKSlpbS0w8PLy8vS0tTU1dXe39/q6uvr7e3w8Pj4/v7+/gagi+YAAAMRSURBVBgZncGHQxNnHAbgF0JZBhRTcIBh2MJZBcGIRcEwjIRXRdwWceJeWAva4s+9Pdfp9w83+YDkvpBxd8+DQsKRqNU7EE8k4gO9VjQShi8NnbGkGJKxzgZ4VN3SL3n1t1SjtNq2ESlopK0WxZVvHJKihjaWo4j6Himppx4FNY2JB2O/Ir9Qx4R4MtERQh6Vlnhm/YJVKneIDzsqkSNkiS9WCKYO8akDhqYJ8WmiCS71Y+LbWD0yynskgJ5yrNgsgWzGstohCWSoFkvaJKA2aNUjEtBINdJaJLAWpP0pgfUjpUEKW1x4+HBhUQprANAp+dy/Pjt94hC1QyemZ6/fl3w6AcQk1+NbF6e4ytSlW48lVwwIJ8U0N3uUBRydnRNTMoyIGOZmWNTMnBgiiIrL/GWWdHleXKL4Q7JuT9GDqduSZaFPVixeoUdXFmVFH/bJskd/0bPpR7JsH+KyZP40fTg9L0viSIi2cJK+nFwQLYGEpP17lj6d/U/SEohL2nn6dkHS4hiQlJsM4KakDKBPRP6eZACT/4hILywROcdAZkTEQlTkLgO6KxJFRJ6coeHw09dvXhxjjmMv3rx+epiGM08kgnDyDg1H3qqUj6doOPVRpbw9QsOdZBiInaPhudJe0vBSac9pmIkB+I2md0r7TMNnpb2j6XcA62j6pLTvNHxX2iea1iFlNw220hwaHKXZNOxGWjMNttIcGhyl2TQ0I61qmG620hwaHKXZdBuugtZKN1tpDg2O0my6tWJJzSBdbKU5NDhKs+kyWINlG+jyQWnfaPimtA902YAVZd3MeqW09zS8V9orZnWXIaNulBlXf6iUnw9oePBTpfy4yozROrg0jjPj3helvj5jjmdflfpyjxnjjTC0M2vy2o3jXOX4jWuTzGqHKdRFX7pCyFGxnT5sr8AqFV30rKsCeYTax+nJeHsI+TWO0oPRRhRU182SuutQRNmmQRY1uKkMxdW0DrOg4dYalFbVvId57Wmugkdrt+46SMPBXVvXwpc167ds27l3/4ED+/fu3LZl/RoU8D+MKr7YWBrCsAAAAABJRU5ErkJggg==" in driver.page_source:
        time.sleep(1)
        i += 1
        if i == 10:
            print(f'{RED}[{WHITE}·{RED}] {RESET}Error, manual login required.')
            driver.quit()
            daily_check_in(ACCOUNT, manual=True)
            return None

    try:
        driver.find_element(By.XPATH,  "//*[contains(@class, 'red-point')]").click()
        time.sleep(5)
    except: print(f'{RED}[{WHITE}·{RED}] {RESET}Reward alredy claimed.')

    try:
        driver.find_elements(By.CLASS_NAME, "//button[contains(text(), 'Make up for check-in')]")[0].click()
        time.sleep(5)
    except: print(f'{RED}[{WHITE}·{RED}] {RESET}Not posible to make up for check-in.')
    
    driver.quit()


def get_credentials():
    """Gets the credentials from the credentials.json file."""
    with open('credentials.json', 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    """Main function."""
    codes = get_codes("https://genshin-impact.fandom.com/wiki/Promotional_Code")
    account = get_credentials()
    redeem_code(codes, account, True)
    daily_check_in(account, True)
    print(f'{YELLOW}================================\n{GREEN}[{WHITE}·{GREEN}] {RESET}FINISHED.')



    