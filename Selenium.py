from time import time
from fake_useragent import UserAgent
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import re
import pandas as pd

start_time = time()

def split_manufacturer_model(manufacturer_model, brand_options):
  for brand_option in brand_options:
    if manufacturer_model.startswith(brand_option):
      return brand_option, manufacturer_model[len(brand_option)+1:]
  return None, manufacturer_model


def get_all_cars(load_all_url):
  driver.get(load_all_url)
  while True:
    try:
      car_cards_locator = (By.CLASS_NAME, 'bBHUGW')
      car_cards = wait.until(EC.presence_of_all_elements_located(car_cards_locator))
      sleep(3)
      break
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
      print(f"Exception caught: {type(e).__name__}, reloading page and retrying...")
      driver.refresh()
  print(f"Total car in this page: {len(car_cards)}")

  for car_card in car_cards:
    car_details_tag = car_card.find_element(By.CSS_SELECTOR, 'a.sc-ibQAlb')
    if 'occasions' in car_details_tag.text:
      cars_count = car_details_tag.text.split(' ')[1]
      other_cars_url_prefix, other_cars_url_suffix = car_details_tag.get_attribute('href').split('productgroep')
      other_cars_url = ''.join([other_cars_url_prefix,'begin-bij=',cars_count,'/productgroep',other_cars_url_suffix])
      car_group_url_list.append(other_cars_url)
    else:
      car_details_url_dict = {}
      car_details_url_dict['manufacturer_model'] = car_card.find_element(By.CLASS_NAME, 'sc-cDJyZ').text.strip()
      car_details_url_dict['manufacturer'], car_details_url_dict['model'] = split_manufacturer_model(car_details_url_dict['manufacturer_model'], brand_options)
      car_details_url_dict.pop('manufacturer_model', None)
      car_details_url_dict['price'] = car_card.find_element(By.CLASS_NAME, 'sc-Gppvi').text
      car_details_url_dict['car_details_url'] = car_details_tag.get_attribute('href')
      car_details_url_dicts.append(car_details_url_dict)

  try:
    load_all_url = car_group_url_list[0]
  except:
    return
  else:
    del car_group_url_list[0]
    get_all_cars(load_all_url)


car_details_url_dicts = [] # for storing every car's detailed info page url
car_group_url_list = [] # for storing urls that contains more than 1 car's detailed info page
url = 'https://www.anwb.nl/auto/private-lease/anwb-private-lease/aanbod'
chrome_options = Options()
chrome_options.add_argument(f"user-agent={UserAgent().random}")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option("detach", True) # useful for debugging when not in headless mode
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 60)

driver.get(url)
while True:
  try:
    total_car_locator = (By.CLASS_NAME, 'sc-fnGdJe')
    total_car_tag = wait.until(EC.presence_of_element_located(total_car_locator))
    sleep(3)
    total_car = total_car_tag.text
    break
  except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
    print(f"Exception caught: {type(e).__name__}, reloading page and retrying...")
    driver.refresh()
print(f"Total car in initial page: {total_car}")

# get all manufacturers possible names
show_more_brand = driver.find_element(By.CLASS_NAME,"sc-icgRgT")
driver.execute_script("arguments[0].click();", show_more_brand)
brand_options = driver.find_elements(By.XPATH,"//h6[contains(text(), 'Merk')]/../../../div/div[@class='sc-bqnQIQ SPSXv']")
brand_options = [brand_option.text.split(' (')[0] for brand_option in brand_options]
print(f"Total brand: {len(brand_options)}")
print(brand_options)

# reload page with additional parameter to show all available cars 
# (some url is a group of used cars that need to be scraped further to obtain more urls)
load_all_url = ''.join([url,'/begin-bij=',total_car])
get_all_cars(load_all_url) 

i = 1
for car_details_url_dict in car_details_url_dicts:
  driver.get(car_details_url_dict['car_details_url'])
  while True:
    try:
      if 'samenstelling' in car_details_url_dict['car_details_url']:
        fuel_locator = (By.XPATH, '//*[@name="brandstof-value"]')
        chassis_locator = (By.XPATH, '//*[@name="carrosserie-value"]')
      else:
        fuel_locator = (By.XPATH, '//*[contains(text(), "Brandstof")]')
        chassis_locator = (By.XPATH, '//*[contains(text(), "Carrosserie")]')
      fuel_type_tag = wait.until(EC.presence_of_element_located(fuel_locator))
      vehicle_chasis_tag = wait.until(EC.presence_of_element_located(chassis_locator))
      sleep(3)
      car_details_url_dict['fuel_type'] = re.sub(r'Brandstof: ','',fuel_type_tag.text).strip()
      car_details_url_dict['vehicle_chasis'] = re.sub(r'Carrosserie: |\(|\)|\d.+deurs','',vehicle_chasis_tag.text).strip()
      break
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
      try:
        empty_notice = driver.find_element(By.XPATH,'//*[contains(text(), "Helaas! Pagina onder Auto is niet gevonden")]')
        print("skipped, content has been moved")
        break
      except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"Exception caught: {type(e).__name__}, reloading page and retrying...")
        driver.refresh()
  print(i, car_details_url_dict, '\n', end=' ')
  i+=1

df = pd.DataFrame(car_details_url_dicts)
# print(df)
df.to_csv('cars.csv', index=False)

end_time = time()
duration = end_time - start_time
print(f"Script execution took {duration:.6f} seconds")