from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
import datetime
import pynput
import pandas as pd

#####------------------------- 時間戳轉換函式 -------------------------#####

def string2timestamp(timeString):
    # Input  : "2020-09-10 03:00:00"
    # Output : 1599678000
    struct_time = time.strptime(timeString, "%Y-%m-%d_%H-%M-%S")
    time_stamp = int(time.mktime(struct_time))  # 轉成時間戳
    return time_stamp

def timestamp2string(timestamp):
    # Input  : 1599678000
    # Output : "2020-09-10 03:00:00"
    struct_time = time.localtime(timestamp)
    timeString = time.strftime("%Y-%m-%d_%H-%M-%S", struct_time)  # 轉成字串
    return timeString

#####------------------------- 選取截圖範圍 -------------------------#####

isHotkeyFinished = False
listener_keyboard = 0
listener_mouse = 0
point_list = []
time_list = []

def active_window():
    mouse = pynput.mouse.Controller()
    mouse.click(pynput.mouse.Button.left)

def on_click(x, y, button, is_press):
    if(is_press):
        point_list_len = len(point_list)
        point_list.append([])
        point_list[point_list_len].append(x)
        point_list[point_list_len].append(y)
    
        if len(point_list) == 3:
            point_list[0] = point_list[1]
            point_list[1] = point_list[2]
            del point_list[2]

def on_activate():
    global isHotkeyFinished,listener_mouse
    listener_mouse.stop()
    isHotkeyFinished = True

def for_canonical(f):
    return lambda k: f(listener_keyboard.canonical(k))

def detect_hotkey(driver):
    global listener_keyboard,listener_mouse
    print("---照順序雙擊滑鼠左建選取終點、起點---")
    print("終點請放置在資料點後一條K棒")
    print("起點請放置在資料點前一條K棒")

    listener_mouse = pynput.mouse.Listener(on_click=on_click)
    listener_mouse.start()

    hotkey = pynput.keyboard.HotKey(
        pynput.keyboard.HotKey.parse('<ctrl>+y'), on_activate)
    with pynput.keyboard.Listener(on_press=for_canonical(hotkey.press)) as listener_keyboard:
        while isHotkeyFinished == False:
            find_data_time(driver)
            pass

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")         # 最大化視窗
    options.add_argument("--disable-popup-blocking")  # 禁用彈出攔截
    driver = webdriver.Chrome(options=options)
    return driver

def find_data_time(driver):
    global point_list,time_list

    path = {
            "time": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[8]/div"
        }
    
    if len(point_list) == 2 and set(point_list[0]) == set(point_list[1]) and len(time_list) != 2:
        timestamp = driver.find_element(By.XPATH, path["time"]).text
        timeString = timestamp2string(float(timestamp))
        time_list.append(timestamp)
        # print(time_list)
        point_list = []

        if len(time_list) == 1:
            print("成功選取終點")
        else:
            print("成功選取起點")
            print("確認選取後，將滑鼠放置在起點處")
            print("並按下快捷鍵 ctrl+y 即可開始爬取資料")

def login(driver):
    path = {
        "name": "//*[@id='overlap-manager-root']/div/div[2]/div/div/div/div/div/div/div[1]/div[4]/div/span"
    }
    login_url = "https://www.tradingview.com/#signin"
    account = "帳號"
    password = "密碼"
    driver.get(login_url)
    time.sleep(1)

    print('---使用mail登入---')
    driver.find_element(By.XPATH, path["name"]).click()
    time.sleep(1)

    try:
        print('---帳號密碼輸入---')
        driver.find_element(By.NAME, 'username').send_keys(account)
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.NAME, 'password').send_keys(Keys.ENTER)
        time.sleep(3)
    except Exception as e:
        print("---登入失敗---")
        print(e)
    print()


def select_currency(driver, symbol, target):
    path = {
        "allow_cookie": "/html/body/div[4]/div/div/div/article/div[2]/div/button",
        "delete_msg": "//*[@id='overlap-manager-root']/div/div/div[1]/div/div[1]/span"
    }
    print('---交易畫面載入---')
    DataUrl = "https://www.tradingview.com/chart/w9WmcMnp/?symbol=" + symbol + "%3A" + target # target url
    driver.get(DataUrl)
    time.sleep(3)

    try:
        print('---允許Cookie---')
        driver.find_element(By.XPATH, path["allow_cookie"]).click()
        time.sleep(1)
    except Exception as e:
        print('---無Cookie 彈出視窗---')
        # print(e)

    try:
        print('---刪除存在通知---')
        driver.find_element(By.XPATH, path["delete_msg"]).click()
        time.sleep(1)
    except Exception as e:
        print('---無彈出視窗---')
        # print(e)
    print()


def get_history_data(driver):
    global time_list
    path = {
        "Time": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[8]/div",
        "Open": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/div[2]",
        "High": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[3]/div[2]",
        "Low" : "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[4]/div[2]",
        "Close": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[5]/div[2]",
        "MA_07": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div",
        "MA_10": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[2]/div",
        "MA_20": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[3]/div",
        "MA_30": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[4]/div",
        "MA_40": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[5]/div",
        "MA_50": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[6]/div",
        "MA_99": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[7]/div",
        "Volume": "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[1]/div"
    }

    price = []
    temp_price = []
    timestamp = ''

    print("---開始擷取數據---")
    start_time = time.time()
    while timestamp != time_list[0]:
    # for i in range(time_period):
        try:
            keyboard = pynput.keyboard.Controller()
            keyboard.press(pynput.keyboard.Key.right)
            keyboard.release(pynput.keyboard.Key.right)

            # -----------------------------------------

            # Time
            timestamp = driver.find_element(By.XPATH, path["Time"]).text
            timeString = timestamp2string(float(timestamp))
            temp_price.append(timeString)
            print("Time:", timeString)

            time.sleep(0.3) #資料需時間加載

            # -----------------------------------------

            # Open
            Open = driver.find_element(By.XPATH, path["Open"]).text
            temp_price.append(Open)

            # High
            High = driver.find_element(By.XPATH, path["High"]).text
            temp_price.append(High)

            # Low
            Low = driver.find_element(By.XPATH, path["Low"]).text
            temp_price.append(Low)

            # Close
            Close = driver.find_element(By.XPATH, path["Close"]).text
            temp_price.append(Close)

            # -----------------------------------------

            # MA_07
            MA_07 = driver.find_element(By.XPATH, path["MA_07"]).text
            temp_price.append(MA_07)

            # MA_10
            MA_10 = driver.find_element(By.XPATH, path["MA_10"]).text
            temp_price.append(MA_10)

            # MA_20
            MA_20 = driver.find_element(By.XPATH, path["MA_20"]).text
            temp_price.append(MA_20)

            # MA_30
            MA_30 = driver.find_element(By.XPATH, path["MA_30"]).text
            temp_price.append(MA_30)

            # MA_40
            MA_40 = driver.find_element(By.XPATH, path["MA_40"]).text
            temp_price.append(MA_40)

            # MA_50
            MA_50 = driver.find_element(By.XPATH, path["MA_50"]).text
            temp_price.append(MA_50)

            # MA_99
            MA_99 = driver.find_element(By.XPATH, path["MA_99"]).text
            temp_price.append(MA_99)

            # Volume
            Volume = driver.find_element(By.XPATH, path["Volume"]).text
            temp_price.append(Volume)

            price.append(temp_price)
            temp_price = []

        except Exception as e:
            print("---爬取錯誤---")
            print(e)
            exit()

    end_time = time.time()

    print("所花時間:" + str(round(end_time - start_time)) + "秒")
    return price


def price2csv(price, symbol, target, period):
    global time_list
    start_time = timestamp2string(int(time_list[1][0:10]))
    end_time = timestamp2string(int(time_list[0][0:10]))
    df = pd.DataFrame(price, columns=['Time', 'Open', 'High', 'Low', 'Close',
                                      'MA_07', 'MA_10', 'MA_20', 'MA_30', 'MA_40',
                                      'MA_50', 'MA_99', "Volume"])
    df.to_csv(
        f"{symbol}_{target}_{period}_{start_time}_{end_time}.csv", index=False)

    print("---儲存資料成功---")


if __name__ == '__main__':
    symbol = "NASDAQ"
    target = "TSLA"

    # 台灣時間
    period = '15M'  # period 1D | 4H 3H 2H 1H | 1M 3M 5M 15M 30M 45M
    
    driver = get_driver()
    login(driver)
    select_currency(driver, symbol, target)
    detect_hotkey(driver)
    price = get_history_data(driver)
    price2csv(price, symbol, target, period)
