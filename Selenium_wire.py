from time import time
from pydantic import BaseModel, Field
from fake_useragent import UserAgent
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from time import sleep
import json
import pandas as pd

start_time = time()

class Item(BaseModel):
  # url : str = Field(alias='externalUrl')
  manufacturer : str
  model : str
  price : float
  fuel_type : str = Field(alias='fuelType')
  vehicle_chasis : str = Field(alias='vehicleChassis')

# a recursive function used for loading a page until it's fully rendered while capturing every XMLHttpRequest the browser made
# also functioned for searching if there is any url that contains more cars unlisted on current page and get the numbers of cars it has
# it modifies url by adding total number of cars so there won't be any need to load more cars
# by using maximum number of cars in a page, it forces the server to yield response containing all data within this page to be scraped
# it uses request's url to identify the target request, there are other requests with same url. The one that yields all data is the last one
def capture_json(url):
  driver.get(url)
  while True:
    try:
      car_url_locator = (By.CSS_SELECTOR, 'a.sc-ibQAlb')
      car_urls = wait.until(EC.presence_of_all_elements_located(car_url_locator))
      sleep(3)
      break
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
      print(f"Exception caught: {type(e).__name__}, reloading page and retrying...")
      driver.refresh()
  print(f"Total car in this page: {len(car_urls)}")

  for request in driver.requests:
    if request.url == 'https://api.anwb.nl/v2/privatelease':
      api_list.append(request)
  selected_api_list.append(api_list[-1])

  for car_url in car_urls:
    if 'occasions' in car_url.text: # url containing more than 1 cars
      cars_count = car_url.text.split(' ')[1]
      used_car_group_url_prefix, used_car_group_url_suffix = car_url.get_attribute('href').split('productgroep')
      used_car_group_url = ''.join([used_car_group_url_prefix,'begin-bij=',cars_count,'/productgroep',used_car_group_url_suffix])
      used_car_group_urls.append(used_car_group_url)

  try:
    load_all_url = used_car_group_urls[0]
  except:
    return
  else:
    del used_car_group_urls[0]
    capture_json(load_all_url)

seleniumwire_options = {
  'ca_cert': 'ca.crt',
  'verify_ssl': True 
}

url = 'https://www.anwb.nl/auto/private-lease/anwb-private-lease/aanbod'
chrome_options = Options()
chrome_options.add_argument(f"user-agent={UserAgent().random}")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option("detach", True) # useful for debugging when not in headless mode
driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
wait = WebDriverWait(driver, 30)
used_car_group_urls = []
api_list = []
selected_api_list = []

# starts scraping...
driver.get(url)
while True:
  try:
    total_car_locator = (By.CLASS_NAME, 'sc-fnGdJe')
    total_car_tag = wait.until(EC.presence_of_element_located(total_car_locator))
    sleep(3)
    total_car = total_car_tag.text
    if total_car == '':
      raise NoSuchElementException
    break
  except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
    print(f"Exception caught: {type(e).__name__}, reloading page and retrying...")
    driver.refresh()
print(f"Total car in initial page: {total_car}")

load_all_url = ''.join([url,'/begin-bij=',total_car])
capture_json(load_all_url)

# saving to csv...
df = pd.DataFrame()
for selected_api in selected_api_list:
  response = selected_api.response
  body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
  decoded_body = body.decode('utf-8')
  json_data = json.loads(decoded_body)
  car_list = [Item.model_validate(car) for car in json_data['items']]
  df = pd.concat([df, pd.DataFrame([car.model_dump() for car in car_list])], ignore_index=True)
df.to_csv('cars.csv', index=False)

end_time = time()
duration = end_time - start_time
print(f"Script execution took {duration:.6f} seconds")

# the website this script is scraping often takes too long to be fully loaded, it often stucks when opened on seleniumwire's webdriver
# resulting on too many time outs and retries
# but since it doesn't need to scrape every car's detailed info pages, this script often finishes faster than synchronous selenium method
# there are differences of data between the one shown on the web and one yielded from the request
# but the differences aren't fatal (eg. price: € 999,- (web) and 999 (XHR))