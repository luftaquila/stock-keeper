import os
import re
import time
import json
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def format_bytes(size):
  # 2**10 = 1024
  power = 2 ** 10
  n = 0
  power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
  while size > power:
    size /= power
    n += 1
  return str(round(size, 1)) + ' ' + power_labels[n] + 'B'

print('Crawler is on startup...')
driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_options)
print('Driver loaded.')
time.sleep(0.5)

with open('index_data.json') as json_file:
  count = 0
  failure = []
  
  data = json.load(json_file)
  print('Lookup data loaded.')
  time.sleep(0.5)
  print('Startup finished. Crawling sequence start\n')
  time.sleep(1)
  
  init = time.time()
  
  for obj in data:
    count = count + 1
    print('Loading page', count, '/', len(data), ':', obj['nm'], '...', end='')
    
    start = time.time()
    attr = {}
    driver.get('http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?gicode=' + obj['cd'])

    try:
      WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'divHighTerm')))
      print('OK\nPage loaded. Collecting data...', end='')
      html = driver.find_element(By.CSS_SELECTOR, 'div#highlight_D_Y table').get_attribute('innerHTML')
      table = BeautifulSoup(html, 'html.parser')
      
      thead = table.thead.select('tr:nth-child(2) th div')
      attr['year'] = list(map(lambda x: x.find('span').string if x.select('span') else x.string, thead))
      
      for x in table.tbody.select('tr'):
        try: attr[x.th.div.string.replace(u'\xa0', '')] = list(map(lambda o: o.string.replace(u'\xa0', ''), x.select('td')))
        except:
          try: attr[x.th.div.a.span.string.replace(u'\xa0', '')] = list(map(lambda o: o.string.replace(u'\xa0', ''), x.select('td')))
          except: failure.append({ 'count': count, 'name': obj['nm'], 'code': obj['cd'] })
            
      # process attr
      f = open('output.json', 'a')
      f.write(json.dumps({ 'name': obj['nm'], 'code': obj['cd'], 'attr': attr }, ensure_ascii = False))
      f.write(',')
      f.close()

      end = time.time()
      elapsed = str(datetime.timedelta(seconds=(end - init)))
      eta = str(datetime.timedelta(seconds=((end - init) / (count + 1) * (len(data) + 1)) - (end - init)))
      print('OK\n', round(end - start, 1), 's spent, ET:', elapsed, '/ EET:', eta, '\n')

    except: failure.append({ 'count': count, 'name': obj['nm'], 'code': obj['cd'] })
      
  print('\nFinished. fail:', len(failure), 'detail:', failure)
      
