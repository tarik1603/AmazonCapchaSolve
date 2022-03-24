from PIL import Image
import numpy as np
import pytesseract
import requests
from io import BytesIO
import getopt, sys


# sudo apt-get install python3
# sudo apt-get install python3-pip
# sudo python3 -m pip install --upgrade pip
# sudo python3 -m pip install --upgrade Pillow
# sudo python3 -m pip install --upgrade Numpy
# sudo python3 -m pip install --upgrade pytesseract
# sudo apt-get install tesseract-ocr


# Bu script pytesseract ve PIL ihtiyac duyar lutfen kullanmadan once yuklediginize emin olunuz.

# Resimler once split edilir.
# Split edilen resimler OCR uygun hale getirilir.
# Daha sonra resimler tek tek okunup kayit edilir.
def ReadCaptcha(img):
    img = img.convert("RGBA")
    pix = img.load()

    imgList = SplitImageGroups(pix, img.size[0], img.size[1])

    text = ""
    count = 1
    for image in imgList:
        a = pytesseract.image_to_string(image, config="--psm 10")
        if len(a) > 0:
            a = a[0]
        text += a
        count += 1

    return text


# Split sirasinda olusan rotasyon sorununu ve amazonun uyguladigi rotasyonu duzeltir.
def FixImageRot(array, imgCount):
    newArray = []
    for y in range(len(array[0])):
        xArray = []
        for x in range(len(array)):
            xArray.append(array[x][y])

        newArray.append(xArray)

    image = Image.fromarray(np.uint8(newArray))

    if imgCount % 2 == 0:
        return image.rotate(15, expand=True)
    else:
        return image.rotate(-15, expand=True)


# Dikey olarak herhangi bir kesin olarak bir siyah pixele denk gelinmesse o kismi farkli bir resim olarak ayirir.
# 255,255,255,255 ve buna yakin renkleri gormez. 5,5,5,255 gibi bir rengi gorur.
# Resimleri daha sonra amazon captcha'sina uygun olarak rotasyon uygulanir.
def SplitImageGroups(pix, xSize, ySize):
    groups = []

    group = []
    addGroup = False

    count = 1
    for x in range(xSize):
        blackColor = False
        yGroups = []

        for y in range(ySize):
            if pix[x, y][0] <= 5 or pix[x, y][1] <= 5 or pix[x, y][2] <= 5:
                blackColor = True
                addGroup = True
            yGroups.append(pix[x, y])

        group.append(yGroups)

        if blackColor == False:
            if addGroup:
                img = FixImageRot(group, count - 1)
                groups.append(img)
                count += 1

                group = []

            addGroup = False
    return groups


if __name__ == '__main__':
    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]

    # Options
    options = "hl:"

    # Long options
    long_options = ["Help", "Link", "OK"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--Help"):
                print(
                    '{"Error":"%s"}' % "Bu script pytesseract ve PIL ihtiyac duyar. -l, --Link => resim url'si veriniz.")

            elif currentArgument in ("-l", "--Link"):
                try:
                    response = requests.get(
                        currentValue)  # https://images-na.ssl-images-amazon.com/captcha/druexhzz/Captcha_bopsbludqf.jpg
                    img = Image.open(BytesIO(response.content))

                    print('{"Text":"%s"}' % ReadCaptcha(img))
                except Exception as err:
                    print('{"Error":"%s"}' % err)
            elif currentArgument in ("--OK"):
                print("OK")

    except getopt.error as err:
        # output error, and return with an error code
        print('{"Error":"%s"}' % err)