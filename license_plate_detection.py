from tracemalloc import stop
from unicodedata import name
import cv2
from cv2 import blur
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
from torch import empty

pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\enest\\AppData\\Local\\Tesseract-OCR\\tesseract.exe"

img = cv2.imread("cars/car1.jpg")
img = cv2.resize(img,(500,500))
img_bgr = img
img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
img_blur = cv2.medianBlur(img_gray,5)
img_blur = cv2.medianBlur(img_blur,5)

median = np.median(img_blur)
low = 0.50*median
high = 1.50*median
img_canny = cv2.Canny(img_blur,low,high)
img_canny_dilate = cv2.dilate(img_canny, np.ones((3,3), np.uint8),iterations=1)

cnt = cv2.findContours(img_canny_dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnt = cnt[0]
cnt = sorted(cnt, key=cv2.contourArea, reverse=True)[:30]

license = None

for c in cnt:
    rect = cv2.minAreaRect(c)
    (x,y),(w,h),r = rect

    if (w>h*2) or (h>w*2):
        box = cv2.boxPoints(rect)
        box = np.int64(box)

        minx = np.min(box[:,0])
        miny = np.min(box[:,1])
        maxx = np.max(box[:,0])
        maxy = np.max(box[:,1])

        may_license = img_gray[miny:maxy, minx:maxx].copy()
        may_median = np.median(may_license)
        area = cv2.contourArea(c)
        extent = area / float(w*h)
        
        control1 = may_median > 84 and may_median < 169
        control2 = h < 62 and w < 165
        control3 = w < 62 and h < 165
        control4 = extent > 0.55
        

        print(f"median:{may_median} width:{w}  heigh:{h} area:{area} extent:{extent}")
        found = False   

        if(control1 and ((control2 or control3) and control4)):
            cv2.drawContours(img, [box], 0, (255,0,0), 2)
            license = [int(i) for i in [minx,miny,w,h]]
            plt.title("vuuuuu")
            found = True
            cv2.imwrite("may_license.jpg", may_license)
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.show() 
        else:
            print("couldnt detect")
            cv2.drawContours(img,[box],0,(0,0,255),2)
            plt.title("masmalesef")
        if(found):
            break

img_may_license_v2 = cv2.imread("may_license.jpg",0)
img_may_license_v2 = cv2.resize(img_may_license_v2,(500,180))
img2 = cv2.medianBlur(img_may_license_v2,5)
th_adaptive = cv2.adaptiveThreshold(img2,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,75,12)

###-----------OPENING--------------
kernel = np.ones((5,5), np.uint8)
opening = cv2.morphologyEx(th_adaptive, cv2.MORPH_OPEN, kernel)
string = pytesseract.image_to_string(opening)
print(string)
###-----------OPENING--------------

#cv2.imshow("img", img_may_license)
#cv2.imshow("bilateral", img_bilateral)
#cv2.imshow("canny", img_canny)
#cv2.imshow("cannydilate", img_canny_dilate)
#cv2.imshow("th", img_thresh)
#cv2.imshow("thadaptive", th_adaptive)
#plt.imshow(img_bilateral)
#plt.show()
cv2.imshow("opening", opening)
cv2.waitKey(0)
cv2.destroyAllWindows()