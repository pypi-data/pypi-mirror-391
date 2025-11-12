__version__ = '1.6.0'
from PIL import ImageGrab
from PIL import Image
from contextlib import contextmanager
from ctypes import windll
import collections, ctypes, cv2, numpy, time, win32gui, win32ui, win32con, win32api, win32print

def get_scaling():
    '''獲取螢幕縮放比例'''
    hDC = win32gui.GetDC(0)
    proportion = round(win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES) / win32api.GetSystemMetrics(0), 2)
    return proportion

# 後臺操作
class Bd:
 
    # 定義構造方法
    def __init__(self, title = '%', class_name = None, display_zoom = get_scaling()):
        '''
        後臺綁定(窗口名稱,類別名稱,顯示器縮放比例)
        bw = Bd('夜神模擬器')
        '''
        self.hwnd = win32gui.FindWindow(class_name, title)
        self.display_zoom = display_zoom #display_zoom =>依據顯示器的縮放比調整數值,如縮放與版面配置設定為125%,display_zoom的值則設定為1.25

    # 綁定窗口
    def bind_window(self):
        self.hwnd = input('輸入要綁定的窗口句柄\n')

    # 綁定子窗口
    def bind_child_window(self, child_list_number):
        '''
        先綁定父窗口,再綁定子窗口,例如:
        bw = Bd('雷電模擬器');
        bw.bind_child_window(0)
        child_list_number:數字代表選擇的順序,輸入0選擇第一個,輸入1選擇第二個
        '''
        parent_hwnd = self.hwnd
        hwnd_child_list = []
        win32gui.EnumChildWindows(parent_hwnd, lambda hwnd, param: param.append(hwnd), hwnd_child_list)
        self.hwnd = hwnd_child_list[child_list_number]

    def window_locate(self):
        '''窗口定位,返回窗口左上角和右下角的坐標'''
        self.left, self.top, self.right, self.bottom = win32gui.GetWindowRect(self.hwnd)
        return self.left, self.top, self.right, self.bottom
        
    def lclick(self,x,y,second=0.1):
        '''後臺滑鼠左鍵單擊指定座標,lclick(55,110)'''
        self.x = x; self.y = y; self.second = second
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, ((int(self.y/self.display_zoom)) << 16 | (int(self.x//self.display_zoom))))
        time.sleep(self.second)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((int(self.y/self.display_zoom)) << 16 | (int(self.x//self.display_zoom))))

    def lclick2(self,x,y):
        '''後臺滑鼠左鍵雙擊指定座標,lclick2(55,110)'''
        self.x = x; self.y = y
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, ((self.y) << 16 | (self.x)))
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((self.y) << 16 | (self.x)))
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, ((self.y) << 16 | (self.x)))
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((self.y) << 16 | (self.x)))
            
    def rclick(self,x,y):
        '''後臺滑鼠右鍵單擊指定座標,rclick(55,110)'''
        self.x = x; self.y = y
        win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONDOWN, 0, ((self.y) << 16 | (self.x)))
        win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONUP, 0, ((self.y) << 16 | (self.x)))

    def mouse_down(self,x,y,delay=0.7):
        '''
        後臺滑鼠點擊
        mouse_down(232, 556)
        '''
        self.x = x; self.y = y
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, ((int(self.y/self.display_zoom)) << 16 | (int(self.x//self.display_zoom))))
        print(f"在座標({x},{y})點擊滑鼠")
        return True
    
    def mouse_up(self,x,y,delay=0.7):
        '''
        後臺滑鼠釋放
        mouse_up(132, 556)
        '''
        time.sleep(delay)
        self.x = x; self.y = y
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((int(self.y/self.display_zoom)) << 16 | (int(self.x//self.display_zoom))))
        print(f"在座標({x},{y})鬆開滑鼠")
        return True
    
        

    def mouse_drag(self,x,y,x2,y2,delay=0.7):
        '''
        後臺滑鼠拖拽,從(x,y) 拖拽到(x2,y2)
        mouse_drag(132, 556, 0, 0)
        '''
        try:
            time.sleep(delay)
            duration = 0.7  # 持續拖動的時間（秒）
            steps = 50  # 移動步數
            delta_x = x2 - x
            delta_y = y2 - y
            step_x = delta_x / steps
            step_y = delta_y / steps
            delay = duration / steps
            
            self.x = x; self.y = y
            self.x2 = x2; self.y2 = y2
            
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, ((int(self.y/self.display_zoom)) << 16 | (int(self.x//self.display_zoom))))
            for i in range(steps):
                x_pos = int(self.x + step_x * i)
                y_pos = int(self.y + step_y * i)
                win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, (int(y_pos/self.display_zoom) << 16 | int(x_pos//self.display_zoom)))
                time.sleep(delay)
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((int(self.y2/self.display_zoom)) << 16 | (int(self.x2//self.display_zoom))))
            return True
        except Exception as e:
            print(f"mouse_drag 失敗: {e}")
            return False
        
        
    
    def keypress(self,vk_code,second):
        '''
        後臺按鍵,keypress(按鍵代碼,按下X秒後鬆開)
        keypress(68,2)
        目前模擬器中後臺按鍵失效,尋找更底層的方法替代
        '''
        try:
            self.vk_code = vk_code; self.second = second
            win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, self.vk_code, 1)
            time.sleep(self.second)
            win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, self.vk_code, 0)
            return  True
        except Exception as e:
            print(f"keypress 失敗: {e}")
            return False

    def str(self,text):
        '''後臺文字,str('訊息')'''
        self.text = text
        astrToint = [ord(c) for c in self.text]
        for item in astrToint:
            win32api.PostMessage(self.hwnd, win32con.WM_CHAR, item, 0)
        
    
    def topwd(self):
        '''窗口置頂'''
        hwnd = self.hwnd
        win32gui.SetForegroundWindow(hwnd)
        
    def miniwd(self):
        '''窗口最小化'''
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWMINIMIZED)

    def maxwd(self):
        '''窗口最大化'''
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWMAXIMIZED)

    def hidewd(self):
        '''窗口隱藏'''
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def showwd(self):
        '''窗口顯示(隱藏後顯示,非置頂)'''
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def closewd(self):
        '''窗口關閉'''
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)

    def wd_transparency(self,a):
        '''窗口透明度,參數a是透明度,數值為 0-250'''
        self.a = a
        win32gui.SetWindowLong (self.hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (self.hwnd, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(0,0,0), self.a, win32con.LWA_ALPHA)
        
    def getpoint(self):
        '''獲取相對座標'''
        windowRec = win32gui.GetWindowRect(self.hwnd) # 目標窗口
        python = win32gui.GetForegroundWindow() # 聚焦當前窗口
        win32gui.SetWindowPos(python, win32con.HWND_TOPMOST,0,0,250,450, win32con.SWP_SHOWWINDOW) # 設置窗口大小
        while True:
            point = win32api.GetCursorPos() # 記錄鼠標所處位置的坐標
            x = point[0]-windowRec[0] # 計算相對x坐標
            y = point[1]-windowRec[1] # 計算相對y坐標
            print(x,y)
            time.sleep(0.2)

    def screenshot(self, screenshot = 'test.bmp'):
        '''
        winapi後臺截圖
        screenshot(截圖保存位置)
        screenshot('111.bmp'):
        '''
        #獲取句柄窗口的大小信息
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        width = int((right - left)*self.display_zoom)
        height = int((bot - top)*self.display_zoom)

        #返回句柄窗口的設備環境,覆蓋整個窗口,包括非客戶區,標題欄,菜單,邊框
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)

        #創建設備描述表
        mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)

        #創建內存設備描述表
        saveDC = mfcDC.CreateCompatibleDC()

        #創建位圖對像准備保存圖片
        saveBitMap = win32ui.CreateBitmap()

        #為bitmap開辟存儲空間
        saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)

        #將截圖保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)

        #保存bitmap到內存設備描述表
        saveDC.BitBlt((0,0), (width,height), mfcDC, (0, 0), win32con.SRCCOPY)

        #保存圖像
        ###保存bitmap到文件
        saveBitMap.SaveBitmapFile(saveDC,screenshot)


    def screenshot2(self):
        '''PIL後臺截圖'''

        #獲取句柄窗口的大小信息
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        width = int((right - left)*self.display_zoom)
        height = int((bot - top)*self.display_zoom)

        #返回句柄窗口的設備環境,覆蓋整個窗口,包括非客戶區,標題欄,菜單,邊框
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)

        #創建設備描述表
        mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)

        #創建內存設備描述表
        saveDC = mfcDC.CreateCompatibleDC()

        #創建位圖對像准備保存圖片
        saveBitMap = win32ui.CreateBitmap()

        #為bitmap開辟存儲空間
        saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)

        #將截圖保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)

        #保存bitmap到內存設備描述表
        saveDC.BitBlt((0,0), (width,height), mfcDC, (0, 0), win32con.SRCCOPY)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        #生成圖片
        im_PIL = Image.frombuffer('RGB',(bmpinfo['bmWidth'],bmpinfo['bmHeight']),bmpstr,'raw','BGRX',0,1)
        return im_PIL
    
    def match_template(self, target_img, template_img):
        '''
        匹配模板識圖點擊,match_template('22.png', '11.jpg')
        target_img:目標圖片
        template_img:模板圖片
        '''
        #讀取目標圖片
        target = cv2.imread(target_img)

        #讀取模板圖片
        template = cv2.imread(template_img)

        #執行模板匹配,使用的匹配方式cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(target,template,cv2.TM_SQDIFF_NORMED)

        #歸一化處理
        cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )

        #尋找矩陣（一維數組當做向量,用Mat定義）中的最大值和最小值的匹配結果及其位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        #繪制矩形邊框,將匹配區域標注出來
        #min_loc:矩形定點
        #(min_loc[0]+template.shape[1],min_loc[1]+template.shape[0]):矩形的寬高
        #(0,0,225):矩形的邊框顏色；2:矩形邊框寬度
        cv2.rectangle(target,min_loc,(min_loc[0]+template.shape[1],min_loc[1]+template.shape[0]),(0,0,225),2)

        #cv2.TM_SQDIFF 和 cv2.TM_SQDIFF_NORMED方法,min_val越趨近與0匹配度越好,匹配位置取min_loc
        #其他方法,max_val越趨近於1匹配度越好,匹配位置取max_loc
        img_x = int(min_loc[0]/self.display_zoom)
        img_y = int(min_loc[1]/self.display_zoom)
        
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, ((img_y) << 16 | (img_x)))
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((img_y) << 16 | (img_x)))

        print(f'點擊坐標({img_x},{img_y})')

        #顯示結果
        #cv2.imshow('test',target)
        #cv2.waitKey()
        #cv2.destroyAllWindows()

    def img_click(self,bind,img,wait=0.5,grayscale=True,Offset_x=0,Offset_y=0,confidence=0.9):
        '''
        後臺點擊匹配到的圖片,
        img_click(圖片,點擊後等待X秒,是否使用灰階,x座標偏移量,y座標偏移量,相似度)  
        bw = Bd('夜神模擬器')  
        img_click(bw,'1.png',False,12,50,0.5)  
        '''
        try:
            time.sleep(wait)
            print(f"嘗試點擊圖像: {img}")
            search_img = img_center_point2(img, bind, confidence=confidence, grayscale=grayscale)
            if search_img:
                x,y = search_img
                self.x = x; self.y = y
                click_x = int((self.x + Offset_x) / self.display_zoom)
                click_y = int((self.y + Offset_y) / self.display_zoom)
                time.sleep(wait)
                win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, ((click_y) << 16 | (click_x)))
                win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((click_y) << 16 | (click_x)))
                print(f"點擊位置: ({click_x}, {click_y})")
                return True
        except ImageNotFoundException as e:
            print(f"未找到圖像: {img}. 錯誤: {e}")
        return False
    
    def img_drag(self, bind, img, img2, delay=0.3, grayscale=True):
        '''
        拖拽圖片,滑鼠從圖片1座標拖拽到圖片2座標
        bw = Bd('夜神模擬器')
        img_drag(bw,'1.png','2.png')
        '''
        try:
            time.sleep(delay)
            search_img = img_center_point2(img, bind, confidence=0.9, grayscale=grayscale)
            if search_img:
                x,y = img_center_point2(img, bind, confidence=0.9, grayscale=grayscale)
                x2,y2 = img_center_point2(img2, bind, confidence=0.9, grayscale=grayscale)
                self.x = x; self.y = y
                self.x2 = x2; self.y2 = y2
                time.sleep(0.3)
                win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, ((int(self.y/self.display_zoom)) << 16 | (int(self.x//self.display_zoom))))
                time.sleep(delay)
                win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, ((int(self.y2/self.display_zoom)) << 16 | (int(self.x2//self.display_zoom))))
                return True
        except Exception as e:
            print(f"img_drag 失敗: {e}")


# 前臺操作        
class Fd:
    hDC = win32gui.GetDC(0)
    monitor_scaling = round(win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES) / win32api.GetSystemMetrics(0), 2)
    MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA #掃描碼

    def keypress(vk_code,second=0.1):
        '''
        keypress(按鍵代碼,按下X秒後鬆開),keypress(68, 1)
        '''
        try:
            win32api.keybd_event(vk_code, Fd.MapVirtualKey(vk_code, 0),0,0)
            time.sleep(second)
            win32api.keybd_event(vk_code, Fd.MapVirtualKey(vk_code, 0), win32con.KEYEVENTF_KEYUP,0)
            return  True
        except Exception as e:
            print(f"keypress 失敗: {e}")
            return False

    def key_down(vk_code):
        '''
        前臺按鍵按下,key_down(68)
        '''
        win32api.keybd_event(vk_code, Fd.MapVirtualKey(vk_code, 0),0,0)

    def key_up(vk_code):
        '''
        前臺按鍵鬆開,key_up(68)
        '''
        win32api.keybd_event(vk_code, Fd.MapVirtualKey(vk_code, 0), win32con.KEYEVENTF_KEYUP,0)
 
    def lclick(x,y):
        '''
        前臺滑鼠左鍵單擊指定座標,lclick(55,110)
        '''
        ctypes.windll.user32.SetCursorPos(int(x/Fd.monitor_scaling),int(y/Fd.monitor_scaling))
        ctypes.windll.user32.mouse_event(2,0,0,0,0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(4,0,0,0,0)
        
    def lclick2(x,y):
        '''
        前臺滑鼠左鍵雙擊指定座標,lclick2(55,110)
        '''
        ctypes.windll.user32.SetCursorPos(int(x/Fd.monitor_scaling),int(y/Fd.monitor_scaling))
        ctypes.windll.user32.mouse_event(2,0,0,0,0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(4,0,0,0,0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(2,0,0,0,0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(4,0,0,0,0)

    def rclick(x,y):
        '''
        前臺滑鼠右鍵單擊指定座標,rclick(55,110)
        '''
        win32api.SetCursorPos([int(x/Fd.monitor_scaling),int(y/Fd.monitor_scaling)])
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP | win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)

    def mouse_down(x,y):
        '''
        前臺滑鼠左鍵按下,mouse_down(55,110)
        '''
        ctypes.windll.user32.SetCursorPos(int(x/Fd.monitor_scaling),int(y/Fd.monitor_scaling))
        ctypes.windll.user32.mouse_event(2,0,0,0,0)

    def mouse_up():
        '''
        前臺滑鼠左鍵釋放
        '''
        ctypes.windll.user32.mouse_event(4,0,0,0,0)

    def moveto(x,y):
        '''
        前臺滑鼠移動,moveto(33,56)
        '''
        ctypes.windll.user32.SetCursorPos(int(x/Fd.monitor_scaling),int(y/Fd.monitor_scaling))

    def mouse_drag(x,y,x2,y2,delay=0.7):
        '''
        從(x,y) 拖拽到(x2,y2),mouse_drag(132, 556, 0, 0)
        '''
        try:
            time.sleep(delay)
            ctypes.windll.user32.SetCursorPos(int(x), int(y))
            ctypes.windll.user32.mouse_event(2,0,0,0,0)

            duration = 1
            steps = 50  # 步數
            dx = (x2 - x) / steps
            dy = (y2 - y) / steps

            start_time = time.time()

            for _ in range(steps):
                x += dx
                y += dy
                ctypes.windll.user32.SetCursorPos(int(x), int(y))
                elapsed_time = time.time() - start_time
                time.sleep(max(0, min(duration / steps, duration - elapsed_time)))

            ctypes.windll.user32.SetCursorPos(int(x2), int(y2))
            ctypes.windll.user32.mouse_event(4,0,0,0,0)
            return  True
        except Exception as e:
            print(f"mouse_drag 失敗: {e}")
            return False

    def scroll_up(WHEEL_DELTA = 120):
        '''
        前臺滑鼠向上滾動(WHEEL_DELTA:滾動幅度),scroll_up(120)
        '''
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,WHEEL_DELTA)

    def scroll_down(WHEEL_DELTA = -120):
        '''
        前臺滑鼠向下滾動(WHEEL_DELTA:滾動幅度),scroll_dow(120)
        '''
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,WHEEL_DELTA)

    def getpoint():
        '''
        獲取絕對座標
        '''
        hwnd = win32gui.GetForegroundWindow() # 聚焦當前窗口
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,0,0,150,180, win32con.SWP_SHOWWINDOW) # 設置窗口大小
        while True:
            point = win32api.GetCursorPos()
            print(point)
            time.sleep(0.5)

    def get_hwnd():
        '''
        取得滑鼠位置的窗口句柄
        '''
        point = win32gui.GetCursorPos()#獲取滑鼠坐標
        hwnd = win32gui.WindowFromPoint(point)#獲取滑鼠點擊位置的窗口句柄
        print(hwnd)
        time.sleep(1)

    def get_all_hwnd():
        '''
        獲取所有窗口句柄
        '''
        hwnd_title = {}
        def get_all_window_handle(hwnd, mouse):
            if (win32gui.IsWindow(hwnd)
                    and win32gui.IsWindowEnabled(hwnd)
                    and win32gui.IsWindowVisible(hwnd)):
                hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

        win32gui.EnumWindows(get_all_window_handle, 0)
        for h, t in hwnd_title.items():
            if t :
                print (h, t)

    def open_file(a):
        '''
        打開檔案/資料夾/網址
        open_file("D:\\OneDrive\\code\\123.py")
        open_file("D:\\OneDrive\\code\\python")
        open_file("http://www.j4.com.tw/big-gb/")
        '''
        from win32con import SW_HIDE, SW_SHOWNORMAL
        win32api.ShellExecute(None, "open", a, None, None, SW_SHOWNORMAL)

    def img_click(img, wait=0.1,grayscale=True,Offset_x=0,Offset_y=0,confidence=0.9):
        '''
        前臺點擊匹配到的圖片,
        img_click(圖片,點擊後等待X秒,是否使用灰階,x座標偏移量,y座標偏移量,圖片相似度)
        img_click('1.png',0.5,True,12,50,0.5)
        '''
        try:
            time.sleep(wait)
            print(f"嘗試點擊圖像: {img}")
            search_img = img_center_point(img, confidence=confidence, grayscale=grayscale)
            if search_img:
                x,y = search_img
                click_x = int((x + Offset_x) / Fd.monitor_scaling)
                click_y = int((y + Offset_y) / Fd.monitor_scaling)
                time.sleep(wait)
                ctypes.windll.user32.SetCursorPos(click_x,click_y)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(2,0,0,0,0)
                time.sleep(0.1)
                ctypes.windll.user32.mouse_event(4,0,0,0,0)
                print(f"點擊位置: ({click_x}, {click_y})")
                return True
        except ImageNotFoundException as e:
            print(f"未找到圖像: {img}. 錯誤: {e}")
        return False
    
    def img_drag(img, img2, delay=0.3, grayscale=True):
        '''
        拖拽圖片,滑鼠從圖片1座標拖拽到圖片2座標
        img_drag('1.png','2.png')
        '''
        try:
            search_img = img_center_point(img, confidence=0.9, grayscale=grayscale)
            if search_img:
                x,y = img_center_point(img, confidence=0.9, grayscale=grayscale)
                x2,y2 = img_center_point(img2, confidence=0.9, grayscale=grayscale)
                time.sleep(0.3)
                ctypes.windll.user32.SetCursorPos(int(x/Fd.monitor_scaling),int(y/Fd.monitor_scaling))
                ctypes.windll.user32.mouse_event(2,0,0,0,0)
                time.sleep(delay)
                ctypes.windll.user32.SetCursorPos(int(x2/Fd.monitor_scaling),int(y2/Fd.monitor_scaling))
                time.sleep(delay)
                ctypes.windll.user32.mouse_event(4,0,0,0,0)
                return True
        except Exception as e:
            print(f"img_drag 失敗: {e}")
        
# 圖色識別
# 函式來自 pyscreeze , https://github.com/asweigart/pyscreeze

unicode = str # 在 Python 3 上,所有 isinstance(spam, (str, unicode)) 調用都將與 Python 2 一樣工作
USE_IMAGE_NOT_FOUND_EXCEPTION = False
GRAYSCALE_DEFAULT = False
ImageNotFoundException = False

# 以左上角(x, y)為起點,往右移動 n 寬度,再往下移動 n 高度,畫出一個方形範圍
Box = collections.namedtuple('Box', '左 上 寬 高')

Point = collections.namedtuple('Point', 'x y')
RGB = collections.namedtuple('RGB', 'red green blue')



# win32 DC(DeviceContext) 管理器
@contextmanager
def __win32_openDC(hWnd):
    hDC = windll.user32.GetDC(hWnd)
    if hDC == 0: # NULL
        raise WindowsError("windll.user32.GetDC failed : return NULL")
    try:
        yield hDC
    finally:
        windll.user32.ReleaseDC.argtypes = [ctypes.c_ssize_t, ctypes.c_ssize_t]
        if windll.user32.ReleaseDC(hWnd, hDC) == 0:
            raise WindowsError("windll.user32.ReleaseDC failed : return 0")


def _load_cv2(img, grayscale=None):
    """
    如果給定文件名則加載圖像,或根據需要轉換為 opencv
    Alpha 層此時會導致失敗,因此扁平化為 RGB。
    RGBA: 加載 (-1 * cv2.CV_LOAD_IMAGE_COLOR) 以保留 alpha
    要匹配模板,需要模板和圖像相同且具有 alpha
    """
    if grayscale is None:
        grayscale = GRAYSCALE_DEFAULT
    if isinstance(img, (str, unicode)):
        '''
        函數 imread 從指定的文件加載圖像並返回它。
        如果圖像無法讀取（因為缺少文件、不正確的權限、不支持或無效的格式）
        函數返回一個空矩陣
        參考:http://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html
        '''
        if grayscale:
            img_cv = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        else:
            img_cv = cv2.imread(img, cv2.IMREAD_COLOR)
        if img_cv is None:
            raise IOError("由於文件丟失,讀取 %s 失敗,"
                            "具有不適當的權限,或者是不支持"
                            "或無效的格式" % img)
    elif isinstance(img, numpy.ndarray):
        # 不要嘗試將已經是灰色的圖片轉換為灰色
        if grayscale and len(img.shape) == 3:  # img.shape[2] == 3:
            img_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_cv = img
    elif hasattr(img, 'convert'):
        # 假設它是一個 PIL.Image,轉換為 opencv 格式
        img_array = numpy.array(img.convert('RGB'))
        img_cv = img_array[:, :, ::-1].copy()  # -1 does RGB -> BGR
        if grayscale:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        raise TypeError('需要 圖片文件名稱, OpenCV numpy 數組,或 PIL 圖片')
    return img_cv


def _locateAll_opencv(needleImage, haystackImage, grayscale=None, limit=10000, region=None, step=1,
                        confidence=0.999):

    if grayscale is None:
        grayscale = GRAYSCALE_DEFAULT

    confidence = float(confidence)

    needleImage = _load_cv2(needleImage, grayscale)
    needleHeight, needleWidth = needleImage.shape[:2]
    haystackImage = _load_cv2(haystackImage, grayscale)

    if region:
        haystackImage = haystackImage[region[1]:region[1]+region[3],
                                        region[0]:region[0]+region[2]]
    else:
        region = (0, 0)  # 全圖； yield 語句中使用的這些值
    if (haystackImage.shape[0] < needleImage.shape[0] or
        haystackImage.shape[1] < needleImage.shape[1]):
        # avoid semi-cryptic OpenCV error below if bad size
        raise ValueError('指針尺寸超過 haystack image 或 區域尺寸')

    if step == 2:
        confidence *= 0.95
        needleImage = needleImage[::step, ::step]
        haystackImage = haystackImage[::step, ::step]
    else:
        step = 1

    # 取得所有匹配的結果, 參考: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
    result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_CCOEFF_NORMED)
    match_indices = numpy.arange(result.size)[(result > confidence).flatten()]
    matches = numpy.unravel_index(match_indices[:limit], result.shape)

    if len(matches[0]) == 0:
        if USE_IMAGE_NOT_FOUND_EXCEPTION:
            raise ImageNotFoundException('找不到圖片 (最高 confidence = %.3f)' % result.max())
        else:
            return

    # 使用生成器實現 API 一致性:
    matchx = matches[1] * step + region[0]  # 矢量化
    matchy = matches[0] * step + region[1]
    for x, y in zip(matchx, matchy):
        yield Box(x, y, needleWidth, needleHeight)


locateAll = _locateAll_opencv


def screenshot(imageFilename=None, region=None):
    im = ImageGrab.grab()
    if region is not None:
        assert len(region) == 4, 'region 參數必須是四個整數的元組'
        region = [int(x) for x in region]
        im = im.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
    if imageFilename is not None:
        im.save(imageFilename)
    return im


def locate(needleImage, haystackImage, **kwargs):
    '''耗盡迭代器,以便在 locateAll 中關閉 needle 和 haystack 文件。'''
    kwargs['limit'] = 1
    points = tuple(locateAll(needleImage, haystackImage, **kwargs))
    if len(points) > 0:
        return points[0]
    else:
        if USE_IMAGE_NOT_FOUND_EXCEPTION:
            raise ImageNotFoundException('找不到圖片')
        else:
            return None
        
def locateOnScreen(image, minSearchTime=0, **kwargs):
    '''獲取圖片區域'''
    start = time.time()
    while True:
        try:
            screenshotIm = screenshot(region=None) # locateAll() 函數必須處理裁剪以返回準確的坐標,因此不要在此處傳遞區域。
            retVal = locate(image, screenshotIm, **kwargs)
            try:
                screenshotIm.fp.close()
            except AttributeError:
                '''
                #Windows 上的屏幕截圖不會有 fp,因為它們來自ImageGrab,不是文件。
                Linux 上的屏幕截圖將設置 fp為無,因為文件已取消鏈接。
                '''
                pass
            if retVal or time.time() - start > minSearchTime:
                return retVal
        except ImageNotFoundException:
            if time.time() - start > minSearchTime:
                if USE_IMAGE_NOT_FOUND_EXCEPTION:
                    raise
                else:
                    return None


def locateOnScreen2(image, bind, minSearchTime=0, **kwargs):
    '''後臺獲取圖片區域'''
    start = time.time()
    while True:
        try:
            screenshotIm = bind.screenshot2() # locateAll() 函數必須處理裁剪以返回準確的坐標,因此不要在此處傳遞區域。
            retVal = locate(image, screenshotIm, **kwargs)
            try:
                screenshotIm.fp.close()
            except AttributeError:
                '''
                #Windows 上的屏幕截圖不會有 fp,因為它們來自ImageGrab,不是文件。
                Linux 上的屏幕截圖將設置 fp為無,因為文件已取消鏈接。
                '''
                pass
            if retVal or time.time() - start > minSearchTime:
                return retVal
        except ImageNotFoundException:
            if time.time() - start > minSearchTime:
                if USE_IMAGE_NOT_FOUND_EXCEPTION:
                    raise
                else:
                    return None

def center(coords):
    """
    返回一個 Point 對象,其中 x 和 y 設置為由 coords 格式的整數。
    coords 參數是一個 4 整數元組（左、上、寬、高）。
    取得 coords 中心點範例:
    
    center((10, 10, 6, 8))
    返回 Point(x=13, y=14)
    """
    return Point(coords[0] + int(coords[2] / 2), coords[1] + int(coords[3] / 2))


def img_center_point(image, **kwargs):
    '''
    獲取圖片中心點坐標
    可選參數:grayscale； confidence； region
    grayscale: 灰度匹配,設為True 可啟用
    confidence:相似度（數值為0到1）
    region:指定區域
    
    範例如下:
    img_center_point('1.jpg', confidence=0.9, grayscale=True, region=(0,0,300,400))
    
    參考 pyscreeze.locateCenterOnScreen
    '''
    coords = locateOnScreen(image, **kwargs)
    if coords is None:
        return None
    else:
        return center(coords)


def img_center_point2(image, bind, **kwargs):
    '''
    後臺獲取圖片中心點坐標,
    範例如下:
    bw = Bd('夜神模擬器')
    auto.img_center_point2('2.png', bw, confidence=0.9, grayscale=True)
    '''
    coords = locateOnScreen2(image, bind, **kwargs)
    if coords is None:
        return None
    else:
        return center(coords)

def pixel(x, y):
    with __win32_openDC(0) as hdc: # 句柄將自動釋放
        color = windll.gdi32.GetPixel(hdc, x, y)
        if color < 0:
            raise WindowsError("windll.gdi32.GetPixel failed : return {}".format(color))
        # 顏色的格式為 0xbbggrr https://msdn.microsoft.com/en-us/library/windows/desktop/dd183449(v=vs.85).aspx
        bbggrr = "{:0>6x}".format(color) # bbggrr => 'bbggrr' (hex)
        b, g, r = (int(bbggrr[i:i+2], 16) for i in range(0, 6, 2))
        return (r, g, b)


def matches_color(x, y, expectedRGBColor, tolerance=0):
    """
    坐標找色
    expectedRGBColor:RGB顏色
    tolerance:容差,可在一定誤差內進行匹配
    matches_color(100, 200, (25, 118, 199), tolerance=20)
    """
    pix = pixel(x, y)
    if len(pix) == 3 or len(expectedRGBColor) == 3: # RGB 模式
        r, g, b = pix[:3]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
    elif len(pix) == 4 and len(expectedRGBColor) == 4: # RGBA 模式
        r, g, b, a = pix
        exR, exG, exB, exA = expectedRGBColor
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance) and (abs(a - exA) <= tolerance)
    else:
        assert False, '顏色模式預計長度為 3 (RGB) 或 4 (RGBA),但像素為長度 %s 並且 expectedRGBColor 是長度 %s' % (len(pix), len(expectedRGBColor))

# 執行任務
def perform_task(task_function, *args, max_retries=3, **kwargs):
    task_completed = False
    retries = 0
    while not task_completed and retries < max_retries:
        print(f'執行任務 {task_function.__name__} (第 {retries+1} 次)')
        if task_function(*args, **kwargs):
            task_completed = True
            print(f"任務 {task_function.__name__} 完成\n")
        else:
            print(f"任務重試中...\n")
            retries += 1
            time.sleep(1)
    if not task_completed:
        print(f"任務 {task_function.__name__} 失敗，跳過\n")

# 依序執行任務
def execute_tasks_in_sequence(tasks, max_retries=3):
    for task in tasks:
        task_function, *args = task
        perform_task(task_function, *args, max_retries=max_retries)


def mouse_getRGB(second=1):
    ''' 獲取滑鼠坐標和RGB顏色'''
    print(f'{second} 秒後獲取 滑鼠坐標 和 RGB顏色')
    time.sleep(second)
    locate_mouse = win32api.GetCursorPos()
    im = screenshot()
    im_pixel = im.getpixel(locate_mouse)
    print('滑鼠坐標, RGB顏色模型')
    x, y = locate_mouse
    print(f'{x}, {y}, {im_pixel}')

def mouse_getHEX(second=1):
    ''' 獲取滑鼠坐標和HEX顏色'''
    print(f'{second} 秒後獲取 滑鼠坐標 和 HEX顏色')
    time.sleep(second)
    locate_mouse = win32api.GetCursorPos()
    im = screenshot()
    im_pixel = im.getpixel(locate_mouse)
    print('滑鼠坐標, HEX顏色模型')
    x, y = locate_mouse
    HEX=f'#{im_pixel[0]:02x}{im_pixel[1]:02x}{im_pixel[2]:02x}'
    print(f'{x}, {y}, {HEX}')
    return f'#{im_pixel[0]:02x}{im_pixel[1]:02x}{im_pixel[2]:02x}'

    
