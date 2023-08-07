import configparser
import logging
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as WDWait

login_page: str = 'https://www.dice.com/dashboard/login'


def random_wait() -> None:
    w_time = random.randrange(200, 700, 1) / 100
    time.sleep(w_time)


def has(v_type: str, value: str) -> any:
    def internal_has(element: WebElement) -> bool:
        element_value = None
        match v_type:
            case 'class':
                element_value = element.get_attribute('class').split()
            case 'classes':
                element_value = element.get_attribute('class').split()
            case 'tag':
                element_value = element.tag_name
        return element_value == value if not hasattr(element_value, '__iter__') else (
            all(item in element_value for item in value) if hasattr(value, '__iter__') else value in element_value)

    return internal_has


def print_elements(data: WebElement | list[WebElement]) -> bool:
    if isinstance(data, list):
        print(f"{len(data)} elements")
        for idx, elm in enumerate(data):
            print(f"{idx}: <{elm.tag_name}> class='{elm.get_attribute('class')}', text:{elm.text}")
    else:
        print(f"<{data.tag_name}> class='{data.get_attribute('class')}', text:{data.text}")


def update_profile(config: configparser.ConfigParser, salary: int) -> None:
    # noinspection PyTypeChecker
    email_field = password_field = signin_btn = None
    options = Options()
    if config['args']['headless']:
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("window-size=1920,1080") 
    driver = webdriver.Chrome(options=options)
    driver.get(login_page)
    assert 'Sign In' in driver.title
    try:
        email_field: WebElement = WDWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'email')))
    except Exception as e:
        logging.exception('Exception occurred')
    try:
        password_field: WebElement = WDWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'password')))
    except Exception as e:
        logging.exception('Exception occurred')
    email_field.clear()
    password_field.clear()
    email_field.send_keys(config['credentials']['email'])
    password_field.send_keys(config['credentials']['pwd'])
    try:
        signin_btn: WebElement = (WDWait(driver, 5)
                                  .until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))))
    except Exception as e:
        logging.exception('Exception occurred')
    signin_btn.click()
    assert 'Dashboard Home Feed | Dice.com' in driver.title
    profile_link = driver.find_element(By.ID, 'profileLink')
    profile_link.click()
    assert 'Profile | Dice.com' in driver.title
    time.sleep(3)
    sr: ShadowRoot = driver.find_element(By.TAG_NAME, 'dhi-candidates-wired-candidate-profile').shadow_root
    edit_ij_btn: WebElement = (sr.find_element(
        By.CSS_SELECTOR, 'dhi-candidates-candidate-profile-ideal-job-view > div > dhi-seds-core-button')
                               .shadow_root.find_element(By.CSS_SELECTOR, 'button > dhi-seds-icon'))
    edit_ij_btn.click()
    time.sleep(3)
    input_shadow_host: WebElement = (sr.find_element(
        By.CSS_SELECTOR, 'dhi-candidates-wired-candidate-profile-ideal-job '
                         'dhi-candidates-validated-form-field:nth-child(2) '
                         'div:nth-child(2) input'))

    input_shadow_host.clear()
    input_shadow_host.send_keys(salary)

    confirm_btn: WebElement = sr.find_element(
        By.CSS_SELECTOR, 'dhi-candidates-wired-candidate-profile-ideal-job dhi-seds-core-button:nth-child(2)')
    confirm_btn.click()

    if config['args']['dev_stop']:
        time.sleep(600)
    driver.close()
    return True
