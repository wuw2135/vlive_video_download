# Import the required modules
import json
import os
import shutil
import time
from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager


def downloadpro(response,url):
    total_size = int(response.headers.get('content-length', 0))

    # 初始化橫條進度條
    pbar = tqdm(total=total_size, unit='B', unit_scale=True)

    # 寫入文件
    print(url.split('/')[-1].split('?')[0])
    with open(url.split('/')[-1].split('?')[0], 'wb') as f:
        for data in response.iter_content(1024):
            # 更新進度條
            pbar.update(len(data))
            f.write(data)

    # 完成下載，關閉進度條
    pbar.close()
# Main Function
if __name__ == "__main__":
    
    # Enable Performance Logging of Chrome.
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    # Create the webdriver object and pass the arguments
    options = webdriver.ChromeOptions()

    # Chrome will start in Headless mode
    options.add_argument('headless')

    # Ignores any certificate errors if there is any
    options.add_argument("--ignore-certificate-errors")

    # Startup the chrome webdriver with executable path and
    # pass the chrome options and desired capabilities as
    # parameters.
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()),
                              chrome_options=options,
                              desired_capabilities=desired_capabilities)

    # Send a request to the website and let it load
    with open('downloadurl.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            dirname = line.split('/')[-1].replace('\n','')
            print(dirname)
            
            try:
                os.mkdir(dirname)
            except OSError:
                print('資料夾已經存在')
                continue

            driver.get(line)

            # Sleeps for 10 seconds
            time.sleep(10)

            invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
            title = '[' +  datetime.strptime(driver.find_element(By.CSS_SELECTOR,"div[class^='post_info']").text,'%Y.%m.%d. %H:%M').strftime('%Y-%m-%d') + ']' + driver.find_element(By.CSS_SELECTOR,'head > meta:nth-child(4)').get_attribute('content').replace('[V LIVE] ','')
            for char in invalid_chars:
                title = title.replace(char, '')

            
            
            # Gets all the logs from performance in Chrome
            logs = driver.get_log("performance")

            # Opens a writable JSON file and writes the logs in it
            for log in logs:
                network_log = json.loads(log["message"])["message"]

                # Checks if the current 'method' key has any
                # Network related value.
                
                if("Network.response" in network_log["method"]
                        or "Network.request" in network_log["method"]
                        or "Network.webSocket" in network_log["method"]) and ("response" in network_log["params"] 
                        and "url" in network_log["params"]["response"]) and "https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/" in network_log["params"]["response"]["url"]:

                    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54'}
                    response = requests.get(network_log['params']['response']['url'], headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                    
                        #影片(最高畫質)
                        maxqualarr = [int(item['encodingOption']['name'].replace('P', '')) for item in data['videos']['list']]
                        maxqualnum = max(maxqualarr)
                        maxqualind = next(index for index, number in enumerate(maxqualarr) if number == maxqualnum)
                        response = requests.get(data['videos']['list'][maxqualind]['source'], stream=True, headers=headers)

                        downloadpro(response,data['videos']['list'][maxqualind]['source'])

                        os.rename(data['videos']['list'][maxqualind]['source'].split('/')[-1].split('?')[0], title + '.mp4')
                        shutil.move(title + '.mp4', dirname)


                        #封面照片
                        titleimgurl = driver.find_element(By.CSS_SELECTOR, 'head > meta:nth-child(6)').get_attribute('content')
                        titleimgurl = titleimgurl[:titleimgurl.index('?')]
                        response = requests.get(titleimgurl, stream=True, headers=headers)

                        downloadpro(response,titleimgurl)

                        os.rename(titleimgurl.split('/')[-1].split('?')[0], title + '.jpg')
                        shutil.move(title + '.jpg', dirname)

                        #下載字幕
                        if 'captions' in data:
                            os.makedirs(os.path.join(dirname, 'vtt-subs'))
                            for sub in data['captions']['list']:
                                response = requests.get(sub['source'], stream=True, headers=headers)

                                downloadpro(response,sub['source'])
                                
                                capname = ''
                                if sub['type'] == 'cp':
                                    capname = title + '.official.' + sub['locale'] +  '.vtt' 
                                elif sub['type'] == 'auto':
                                    capname = title + '.autoSub.' + sub['locale'] +  '.vtt'
                                elif sub['type'] == 'fan':
                                    capname = title + '.fanSub.' + sub['locale'] +  '.vtt'
                                else:
                                    capname = title + '.' + sub['locale'] +  '.vtt'

                                os.rename(sub['source'].split('/')[-1].split('?')[0], capname)
                                
                                shutil.move(capname,dirname+'/vtt-subs')

                        count = 0
                    else:
                        print('請求失敗，狀態碼：', response.status_code)


            time.sleep(5)

    print("Quitting Selenium WebDriver")
    driver.quit()
