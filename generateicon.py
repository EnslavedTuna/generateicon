from PIL import Image
import json
import configparser
import os
import re
import numpy as np
import random
import shutil


def getColoredPixels(img):
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        pixels = list(img.convert('RGBA').getdata())
        tempcolorlist = []
        for r, g, b, a in pixels:
            if (a != 0):  # ignore alpha pixels
                newhex = rgb2hex(r, g, b)
                tempcolorlist.append(newhex)
        img.close()
        return tempcolorlist
    else:
        img.close()
        raise ValueError('This image does not have transparancy')


def createColorMap(orgcolorlist, newcolorlist, name):
    if len(orgcolorlist) != len(newcolorlist):
        print('images for '+name+' do not have matching amount of nontransparant pixels org: ' +
              str(len(orgcolorlist))+' new: '+str(len(newcolorlist)))
        return False
    colormap = {}
    for i in range(len(orgcolorlist)):
        if (orgcolorlist[i] in colormap):
            if (colormap[orgcolorlist[i]] != newcolorlist[i]):
                print(orgcolorlist[i] + ' in '+name+' is already mapped to ' +
                      colormap[orgcolorlist[i]] + ' but tried to also map to: ' + newcolorlist[i])
                return False
        else:
            colormap[orgcolorlist[i]] = newcolorlist[i]
    return colormap


def closest(colormap, targetcolor):
    colors = np.array(colormap)
    color = np.array(targetcolor)
    distances = np.sqrt(np.sum((colors-color)**2, axis=1))
    index_of_smallest = np.where(distances == np.amin(distances))
    smallest_distance = colors[index_of_smallest]
    list = smallest_distance.tolist()[0]
    return (list[0], list[1],list[2])

def rgb2hex(r, g, b):
    return '{:02x}{:02x}{:02x}'.format(r, g, b)

def hex2rgb(h):
    h = h.lstrip('#')
    return(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))


def makeIcon(id, map, variant):
    randomcolormap = map
    hexcolormap = {}
    hexcolormapkeys = []
    for key, value in randomcolormap.items():
        hexcolormapkeys.append(hex2rgb(key))
        hexcolormap[hex2rgb(key)] = hex2rgb(value)

    #print(randomcolormap)

    img = Image.open(os.path.join(destinyfolder,id+".png"))

    img = img.convert("RGBA")
    pixels = img.load()  # create the pixel map

    for i in range(img.size[0]):  # for every pixel:
        for j in range(img.size[1]):
            if (pixels[i, j][3] != 0):
                try:
                    newrgb = hexcolormap[(
                        pixels[i, j][0], pixels[i, j][1], pixels[i, j][2])]
                except:
                    closestkey = closest(hexcolormapkeys, (pixels[i, j][0], pixels[i, j][1], pixels[i, j][2]))
                    newrgb = hexcolormap[closestkey]
                    #print(str((pixels[i, j][0], pixels[i, j][1], pixels[i, j][2]))," becomes" + str(closestkey))
                pixels[i, j] = (newrgb[0], newrgb[1], newrgb[2], 255)

    #img.show()
    #img.save(os.path.join(inputfolder,"icons",str(id)+"-"+str(variant+1)+".png"))
    suboutputfolder = destinyfolder.replace(orgfolder, '')[1:]
    outputfolder = os.path.join("output",suboutputfolder)
    os.makedirs(outputfolder, exist_ok=True)
    img.save(os.path.join(outputfolder, str(id)+"_"+str(variant)+".png"))
    img.close()
    print("Generated image has been created")


def runprogram():
    idvariant = re.findall(r"([0-9]+[^_.]*)", filename)
    id = idvariant[0]
    variant = idvariant[1]

    inputpixels = getColoredPixels(file)
    # print(os.path.join(orgfolder, (id+".png")))
    originalpixels = getColoredPixels(Image.open(os.path.join(
        orgfolder, (id+".png"))))

    currentcolormap = createColorMap(originalpixels, inputpixels, id)
    if currentcolormap:
        if test == "i":
            currentcolormap['202020'] = '202020'
        makeIcon(id, currentcolormap, variant)
    else:
        shutil.copyfile(os.path.join(
            destinyfolder, (id+".png")), id+"_FAIL.png")
        print(
            "No colormap could be created, your sprite probably does not match the original")




config = configparser.ConfigParser()
config.read('config.ini')
#inputfolder = (config['CONFIG']['inputfolder'])
#orgfolder = os.path.join(config['CONFIG']['originalfolder'],"icons")
orgfolder = (config['CONFIG']['originalfolder'])

print()
print()
print("Please select mode:")


test = input("(I)con, (E)xp, (B)ack (V)erify\n").lower()
while (test != "b" and test != "i" and test != "e" and test != "v"):
    test = input("Type I OR E OR B OR V\n").lower()
match test:
    case "b":
        destinyfolder = os.path.join(orgfolder, "exp", "back")
        orgfolder = os.path.join(orgfolder,"back")  
    case "i":
        destinyfolder = os.path.join(orgfolder, "icons")
    case "e":
        destinyfolder = os.path.join(orgfolder, "exp")
    case "v":
        destinyfolder = os.path.join(orgfolder)


file = False
try:
    filename = input("Type image name (without .png)\n").lower()
    file = Image.open(filename+".png")
except:
    file = False
while (file == False):
    try:
        filename = input(filename +" not found, Type image name (without .png)\n").lower()
        file = Image.open(filename+".png")
    except:
        file = False

runprogram()








      




      

