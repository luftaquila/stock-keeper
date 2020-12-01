import os
import re
import time
import json
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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
print('Driver loaded. Requesting initial page.')
driver.get("http://gmoney.or.kr/PageLink.do?link=forward:/gmoney/searchFranchisee.do&tempParam1=&menuNo=040000&subMenuNo=040100&thirdMenuNo=")
print('Initial page loaded. Crawling started.')
init = time.time()

startpage = 1
endpage = 5720

for page in range(startpage, endpage + 1):
  start = time.time()
  print('Page', page, '/', endpage, ': Requesting...')
  driver.execute_script('fn_select_noticeList(%s);' % str(page))
  
  try:
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'mainpage')))
    print('Page', page, '/', endpage, ': Loaded.')
  except TimeoutException:
    print('Loading Timeout')

  print('Page', page, '/', endpage, ': Crawling...')
  points = driver.find_element_by_xpath("/html/head/script[18]")
  points = points.get_attribute('innerHTML').replace('\t', '').splitlines()
  gps = []
  list = []

  for n in range(len(points)):
    if points[n].find('points2.push') > -1:
      try:
        name = re.search('<div>(.*)</div>', points[n]).group(1).strip()
      except:
        continue
      lat = re.search('"(.*)"', points[n + 1]).group(1).strip()
      lon = re.search('"(.*)"', points[n + 2]).group(1).strip()
      gps.append({ 'name': name, 'lat': lat, 'lon': lon })
    
  points = driver.find_elements_by_xpath('//*[@id="mainpage"]/div[2]/div/section/div/form/div[2]/table/tbody/tr')

  for obj in points:
    cnt = 0
    store = {}
    for element in obj.find_elements_by_tag_name("td"):
      if cnt == 0:
        store['name'] = element.get_attribute('innerText').strip()
      elif cnt == 1:
        store['address'] = element.get_attribute('innerText').strip()
      elif cnt == 2:
        store['type'] = element.get_attribute('innerText').strip()
      elif cnt == 3:
        store['contact'] = element.get_attribute('innerText').strip()
      cnt = cnt + 1
    list.append(store)
  
  print('Page', page, '/', endpage, ': Merging data...')
  
  for obj in list:
    target = next((item for item in gps if item['name'] == obj['name']), None)
    if target:
      obj['lat'] = target['lat']
      obj['lon'] = target['lon']
    else:
      obj['lat'] = '0'
      obj['lon'] = '0'
  
  print('Page', page, '/', endpage, ': Writing into file...')
  f1 = open('stores.csv', 'a')
  f2 = open('stores.txt', 'a')
  for obj in list:
    line = obj['name'] + '∆' + obj['address'] + '∆' + obj['type'] + '∆' + obj['contact'] + '∆' + obj['lat'] + '∆' + obj['lon'] + '\n'
    f1.write(line)
    f2.write(json.dumps(obj, ensure_ascii = False))
    f2.write('\n')
  f1.close()
  f2.close()
  
  csvsize = os.path.getsize('stores.csv')
  txtsize = os.path.getsize('stores.txt')
  
  end = time.time()
  spent = end - start
  eslaped = str(datetime.timedelta(seconds=(end - init)))
  eta = str(datetime.timedelta(seconds=((end - init) / (page - startpage + 1) * (endpage - startpage + 1)) - (end - init)))
  
  print('Page', page, '/', endpage, ': Finished. File size : csv', format_bytes(csvsize), '/ txt', format_bytes(txtsize))
  print(round(spent, 1), 's spent,', eslaped, '/', eta, '\n')
       
driver.quit()