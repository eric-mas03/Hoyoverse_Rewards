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

    for code in codes:
        driver.get('https://genshin.hoyoverse.com/en/gift?code=' + code)
    
        if first == True:
            try: 
                print(f'{BLUE}[{WHITE}·{BLUE}] {RESET}Iniciando sesión...')
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

                driver.execute_script('document.getElementsByClassName("cdkey-select__option")[1].click()')
                driver.execute_script("window.scrollTo(0, 0);")
                first = False
                time.sleep(10)
            
            except: first = False

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cdkey-form__submit')))    
        print(f'{BLUE}[{WHITE}·{BLUE}] {RESET}Redeeming code: [{GREEN}{code}{RESET}]...')
        time.sleep(5)
        driver.execute_script('document.getElementsByClassName("cdkey-form__submit")[0].click()')
        time.sleep(5)
    
    driver.quit()


def get_credentials():
    """Gets the credentials from the credentials.json file."""
    with open('credentials.json', 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    """Main function."""
    codes = get_codes("https://genshin-impact.fandom.com/wiki/Promotional_Code")
    redeem_code(codes, get_credentials(), False)
    print(f'{GREEN}[{WHITE}·{GREEN}] {RESET}Done.')