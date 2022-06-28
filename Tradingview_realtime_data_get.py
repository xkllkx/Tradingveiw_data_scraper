import cv2
import pynput
from PIL import Image, ImageGrab

import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C://Program Files//Tesseract-OCR//tesseract.exe'


#####------------------------- 選取截圖範圍 -------------------------#####


point_list = []
isClickFinished = 2


def on_click(x, y, button, is_press):
    if(is_press):
        point_list_len = len(point_list)
        point_list.append([])
        point_list[point_list_len].append(x)
        point_list[point_list_len].append(y)


def on_press(key):
    global isClickFinished
    try:
        if key.char == 'y':
            isClickFinished = 1  # jump out the selectRegion
        if key.char == 'n':
            isClickFinished = 0  # start again the selectRegion
    except AttributeError:
        isClickFinished = 2  # other key
        return False


def selectRegion():
    global point_list, isClickFinished
    while True:
        listener_mouse = pynput.mouse.Listener(on_click=on_click)
        listener_keyboard = pynput.keyboard.Listener(on_press=on_press)

        # ------------------ 滑鼠框選範圍 ------------------
        print("----- 選取截圖範圍 -----")
        print("請選取欲截圖範圍的左上角與右下角")

        last_list_length = 0
        listener_mouse.start()
        while True:
            list_length = len(point_list)
            if(list_length != last_list_length):
                print(
                    f'已選取第{list_length}個點 ({point_list[last_list_length][0]},{point_list[last_list_length][1]})')
            last_list_length = list_length
            if(list_length == 2):
                break
        listener_mouse.stop()

        # -------------------- 鍵盤確認 --------------------
        print("辨識範圍確認(y/n):")
        listener_keyboard.start()
        while isClickFinished == 2:
            pass
        listener_keyboard.stop()

        # -------------------- 跳出/重來 --------------------
        if (isClickFinished == 1):
            break

        point_list = []
        isClickFinished = 2
        print("----- 重新選擇範圍 -----")
        print()

    print("----- 範圍已選取 -----")


#####--------------------------- 截圖 ---------------------------#####


def sreenshot(saveFileName):
    screenshotRange = (point_list[0][0], point_list[0][1],
                       point_list[1][0], point_list[1][1])
    # 擷取圖片
    image = ImageGrab.grab(bbox=screenshotRange)

    # 儲存檔案
    image.save(saveFileName)


#####------------------------- 圖片處理 -------------------------#####


def diff(img, background_color):
    length = len(img)
    sum = 0
    for i in range(length):
        sum += (img[i]-background_color[i])**2
    return sum


def filter(imageFileName):
    img = cv2.imread(imageFileName)
    background_color = img[0][0]

    img_bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    height, width, channel = img_bgra.shape
    for h in range(height):
        for w in range(width):
            if(diff(img_bgra[h][w][0:2], background_color) < 10):
                img_bgra[h][w][0] = 255
                img_bgra[h][w][1] = 255
                img_bgra[h][w][2] = 255
                img_bgra[h][w][3] = 0
            else:
                img_bgra[h][w][0] = 0
                img_bgra[h][w][1] = 0
                img_bgra[h][w][2] = 0
                img_bgra[h][w][3] = 1

    gray = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2GRAY)
    # 儲存過濾後的照片
    fileName, extension = imageFileName.split('.')
    newFileName = fileName+"_filtered.png"
    cv2.imwrite(newFileName, gray)
    return newFileName


#####------------------------- 偵測文字 -------------------------#####


def detect_word(openFileName):
    image = Image.open(openFileName)
    return pytesseract.image_to_string(image, lang='eng')


#####------------------------- 主函式 -------------------------#####

if __name__ == '__main__':
    fileName = 'detect.png'
    selectRegion()

    while True:
        sreenshot(fileName)
        filteredFileName = filter(fileName)
        text = detect_word(filteredFileName)
        if(len(text)):
            print(text)