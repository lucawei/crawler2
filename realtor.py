# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 15:04:10 2018

@author: admin
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.common.keys import Keys
import pickle
import traceback
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import gc
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import multiprocessing
from proxybroker import Broker
import asyncio
import random
import json
from selenium.webdriver.common.proxy import Proxy, ProxyType

def exit_handler(key_index, fail):
    with open(r'D:\case shiller data\data2\fail.pk','wb') as f:
        pickle.dump(fail, f)
    with open(r'D:\case shiller data\data2\key_index.pk','wb') as f:
        pickle.dump(key_index, f)
        

    with open(r'D:\case shiller data\data2\backup\fail.pk','wb') as f:
        pickle.dump(fail, f)
    with open(r'D:\case shiller data\data2\backup\key_index.pk','wb') as f:
        pickle.dump(key_index, f)
    



def initializekeys():
    df = pd.read_csv(r'C:\Users\admin\Dropbox\Research\case shiller\realtor.csv')
    key_index = []
    fail = []
    for index in range(df.shape[0]):
        row = df.iloc[index]
        key = ' '.join([str(row['house_number']), str(row['street']), str(row['city']), 'NY', str(row['zipcode'])])
        key_index.append((key,index))

    with open(r'D:\case shiller data\data2\key_index.pk','wb') as f:
        pickle.dump(key_index,f)
    with open(r'D:\case shiller data\data2\fail.pk','wb') as f:
        pickle.dump(fail,f)


def read_record():
    with open(r'D:\case shiller data\data2\key_index.pk','rb') as f:
        key_index = pickle.load(f)
    with open(r'D:\case shiller data\data2\fail.pk','rb') as f:
        fail = pickle.load(f)
    return key_index, fail

def getProxy(count):
    proxyList = []
    async def show(proxies):
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            proxyList.append('{}:{}'.format(proxy.host, proxy.port))
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(
        broker.find(types=['HTTP'], limit=count),
        show(proxies))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)
    return proxyList
    
def initializechrome(proxy=None,headless = False):
    # set the chrome not to accept picture
    chrome_options = webdriver.ChromeOptions()
    prefs = {#"profile.managed_default_content_settings.images":2,
             #'download.default_directory': filepath,
             }
    chrome_options.add_argument('blink-settings=imagesEnabled=false') # headless 模式下也生效
    if proxy is not None:
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        
    chrome_options.add_experimental_option("prefs",prefs)
    if headless:
        # see https://stackoverflow.com/questions/46920243/how-to-configure-chromedriver-to-initiate-chrome-browser-in-headless-mode-throug
        chrome_options.add_argument("--headless")
        #chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--log-level=3");
        chrome_options.add_argument("--silent")
    chrome_options.add_argument('--user-agent="%s"'%UserAgent().random)
    
    global browser
    browser = webdriver.Chrome(r'C:\Users\admin\AppData\Local\Google\Chrome\Application\chromedriver.exe',
                               chrome_options=chrome_options)
    global wait
    wait=WebDriverWait(browser,10)
    
    

def input_check_search_result(keys):
        # click pop ups
    try:
        browser.find_element_by_css_selector('#acsMainInvite > div > a.acsInviteButton.acsDeclineButton').click()
    except NoSuchElementException:
        pass
    #wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#searchBox')))
    time.sleep(1+random.random())                                          
    browser.find_element_by_css_selector('#searchBox').click()
    browser.find_element_by_css_selector('#searchBox').click()
    browser.find_element_by_css_selector('#searchBox').click()
    browser.find_element_by_css_selector('#searchBox').click()

                                       
    
    browser.find_element_by_css_selector('#searchBox').clear()
    browser.find_element_by_css_selector('#searchBox').send_keys(keys)
    browser.find_element_by_css_selector('#searchBox').send_keys(Keys.ENTER)
    
    time.sleep(3+random.random())
    try:
        browser.find_element_by_css_selector('body').get_attribute('class')
        if 'property_details' in browser.find_element_by_css_selector('body').get_attribute('class'):
        #page_result = get_result(keys)
            return True
    except NoSuchElementException:
        url = r'https://www.realtor.com' + browser.find_element_by_css_selector('#srp-list > ul > li').get_attribute('data-url')
        browser.get(url)
            
            #page_result = get_result(keys)
            return True
        except

    
    else:
        try:
            url = r'https://www.realtor.com' + browser.find_element_by_css_selector('#srp-list > ul > li').get_attribute('data-url')
            browser.get(url)
            
            #page_result = get_result(keys)
            return True
        except KeyboardInterrupt:
            # 'program exit'
            return None
        except:
            # key not found
            return False
			
            

        
        
        
        
        
        
        
        
        
        
def get_result(keys):
    # check keys is right:

    time.sleep(2+random.random())
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#ldp-address')))
    
    # if the browser window is small, it will be squeezed to two lines and have \n
    # if not, it is just one line!!!                                           
    address =  browser.find_element_by_css_selector('#ldp-address').text.split(' ')
    if address[0] in keys:
        pass
    else:
        return None

    # some house don't have detail feature, only simple feature                                           
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#ldp-detail-features')))                                           
        browser.find_element_by_css_selector('#ldp-detail-features > div > a').click()
        time.sleep(1)                                     
        detail = browser.find_element_by_css_selector('#ldp-detail-features').text.split('\n')
    except NoSuchElementException:            
        detail = browser.find_element_by_css_selector('#ldp-detail-public-records').text.split('\n')
    
    # not sure whether features are the same, so use dict for dataframe                                                  
    detail_dict = dict()
    for i in detail:
        if ':' in i:
            i = i.split(': ')
            detail_dict[i[0]] = i[1]
       
    # price and tax history, need further cleaning    
    detail_dict['price history'] = browser.find_element_by_css_selector('#ldp-history-price').text    
    detail_dict['tax history'] = browser.find_element_by_css_selector('#ldp-history-taxes').text
    detail_dict['keys'] = keys           
    return detail_dict

    


                

            
def worker(
        shared_key_index,shared_fail,lock,headless=False
        ):
    initial_page = [r'https://www.realtor.com/realestateandhomes-detail/65-Central-Park-W-Apt-7A_New-York_NY_10023_M32696-05892?view=qv',
                    r'https://www.realtor.com/realestateandhomes-detail/1-W-67th-St-909_New-York_NY_10023_M46227-09579',
                    r'https://www.realtor.com/realestateandhomes-detail/388-Forest-Ave_Massapequa_NY_11758_M38250-08726',
                    r'https://www.realtor.com/realestateandhomes-detail/1-Central-Park-W-D40_New-York_NY_10023_M41712-20550',
                    r'https://www.realtor.com/realestateandhomes-detail/15-Central-Park-W-Apt-34A_New-York_NY_10023_M45436-57022']
    # resume or start all over
    try:
        result = []
        n=0
        proxy = getProxy(1)[0]
        #print('got proxy')
        initializechrome(proxy,headless = headless)
        #print('chrome opened')
        browser.get(random.choice(initial_page))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#ldp-details')))
                                          
        while True:
            lock.acquire()
            key_index = shared_key_index.pop()
            lock.release()
            
            # check search result
            check_result = input_check_search_result(key_index[0])
            
            if check_result is None: #either IP blocked or search box not clickable
                lock.acquire()
                shared_key_index.append(key_index)
                lock.release()
                raise KeyboardInterrupt
            elif check_result == True:
                page_result = get_result(key_index[0])
            elif check_result == False: # key not found, next key
                page_result = None

            
            if page_result is None:
                lock.acquire()
                shared_fail.append(key_index)
                lock.release()
            else:
                result.append(page_result)
                n+=1
            
  

    except Exception as e:
        print(e)
        #print(traceback.print_exc)
        # return is required to forcely enter finally??
                
    finally:
        if n >0:
            lock.acquire()
            print('%s crawled %s remained '%(n,len(shared_key_index)) +time.ctime())
            with open(r'D:\case shiller data\data2\result\%s.json'%(time.time()),'w',encoding = 'utf-8') as f:
                f.write(json.dumps(result,ensure_ascii=False)) # f防止中文乱码
            lock.release()
        else:
            print('ip not available')
        
        browser.delete_all_cookies()    
        browser.quit()
        gc.collect()
        # exit manually
        return
            


        
def gps_coordinates_to_address(df_test,skip = None):
    # https://www.gps-coordinates.net/gps-coordinates-converter
    # https://www.latlong.net/Show-Latitude-Longitude.html
    null_index = df_test.loc[df_test['house_number'] == 'None'].index
    if skip:
        null_index = null_index[skip:]
    for i in null_index:
        time.sleep(7)
        try:
            browser.find_element_by_css_selector('#address').clear()
            latitude = df_test.loc[i,'latitude']
            longitude =  df_test.loc[i,'longitude']
            browser.find_element_by_css_selector('#longitude').click()
            browser.find_element_by_css_selector('#longitude').clear()
            browser.find_element_by_css_selector('#longitude').send_keys(str(longitude)) 
            browser.find_element_by_css_selector('#latitude').click()
            browser.find_element_by_css_selector('#latitude').clear()
            browser.find_element_by_css_selector('#latitude').send_keys(str(latitude))
            browser.find_element_by_css_selector('#wrap > div.container > div:nth-child(2) > div.col-md-4 > form:nth-child(2) > div:nth-child(4) > div > button').click()
            
            
            result = browser.find_element_by_css_selector('#address').get_attribute('value')
            if result !='':
                result = result.split(' ')
            else:
                time.sleep(3+random.random())
                result = browser.find_element_by_css_selector('#address').get_attribute('value')
                if result !='':
                    result = result.split(' ')
                else:
                    continue
            try:
                house_number = int(result[0])                                  
                globals()['df_test'].loc[i,'house_number'] = house_number
            except:
                print('not interger')
                continue
        except:
            print('something wrong')
            continue


if __name__ == '__main__':
    try:
        pool = multiprocessing.Pool(1)
        manager = multiprocessing.Manager() # as a manager of all subprocess
        lock = manager.Lock()
        #lock = multiprocessing.Lock() this is wrong! should use manager lock for all subprocess to share!!!
        print('initialize record')
        key_index, fail = read_record()
        shared_key_index = manager.list()
        shared_key_index.extend(key_index)
        shared_fail = manager.list()
        shared_fail.extend(fail)
        del key_index, fail
        gc.collect()
        print('start crawling')
        
        while True:
            # 参数一定要写对？？
                pool.apply_async(func = worker,args = (shared_key_index,shared_fail,lock,True))
                time.sleep(1) # must sleep, otherwise the loop is really fast and consume computer sources 
			              # what is the mechanism of apply_async when the pool is full?


    except Exception as e:
        print(e)
    finally:
        print('exiting')
        #key_index = []
        #key_index = key_index.extend(shared_key_index)
        #fail = []
        #fail = fail.extend(shared_fail)
        #print('sleep')
        #time.sleep(4)
        #exit_handler(key_index,fail)
        print(len(fail))
        try:
            pool.terminate()
            pool.join()
        except Exception as e:
            print(e)
        



    
      

