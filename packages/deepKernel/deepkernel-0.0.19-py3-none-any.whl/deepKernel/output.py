import json,os
from deepKernel import base,information
from PIL import Image,ImageEnhance

def enhance_image(input_image, brightness=1.0, contrast=1.0, color=1.0, sharpness=1.0):
    """综合调整图像各项属性"""
    # 调整亮度
    img = input_image
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    # 调整对比度
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    # 调整色彩饱和度
    if color != 1.0:
        img = ImageEnhance.Color(img).enhance(color)
    # 调整锐度
    if sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
    imgx,imgy = img.size
    for i in range(imgx):
        for j in range(imgy):
            color = img.getpixel((i,j))
            if(color[:-1]!=(255,255,255)):
                color = color[:-1]+(255,)
            img.putpixel((i,j),color)
    return img

def png_process(pngpath):
    img = Image.open(pngpath)
    img = img.convert('RGBA')
    imgx,imgy = img.size
    for i in range(imgx):
        for j in range(imgy):
            color = img.getpixel((i,j))
            if(color[:-1]==(255,255,255)):
                color = color[:-1]+(0,)
            img.putpixel((i,j),color)
    img = enhance_image(img,0.9,0.9,1.2,1.5)
    img.save(pngpath)

def save_gerber( job:str, step:str, layer:str, filename:str,  resize:int=0, angle:float=0, 
                scalingX:float=1, scalingY:float=1, mirror:bool=False, rotate:bool=False, 
                scale:bool=False, cw:bool=False,  mirrorpointX:int=0, mirrorpointY:int=0, 
                rotatepointX:int=0, rotatepointY:int=0, scalepointX:int=0, scalepointY:int=0, 
                mirrorX:bool = False, mirrorY:bool = False, numberFormatL:int=2, 
                numberFormatR:int=6, zeros:int=0, unit:int=0)->bool:
    try:
        _type = 0
        gdsdbu = 0.01
        profiletop = False
        cutprofile = True
        isReverse = False
        cut_polygon = []
        if scalingX == 0:
            scalingX == 1
        if scalingY == 0:
            scalingY == 1
        if mirrorX == True and mirrorY ==True:
            mirrordirection = 'XY'
        elif mirrorX==True and mirrorY ==False:
            mirrordirection = 'Y'
        elif mirrorX==False and mirrorY ==True:
            mirrordirection = 'X'
        else:
            mirrordirection = 'NO'
        _ret = base.layer_export(job, step, layer, _type, filename, gdsdbu, resize, angle, scalingX, scalingY, isReverse,
                    mirror, rotate, scale, profiletop, cw, cutprofile, mirrorpointX, mirrorpointY, rotatepointX,
                    rotatepointY, scalepointX, scalepointY, mirrordirection, cut_polygon,numberFormatL,numberFormatR,
                    zeros,unit)
        ret = json.loads(_ret)['status']
        if ret == 'true':
            ret = True
        else:
            ret = False
        return ret
    except Exception as e:
        print(e)
    return False

def save_job(job:str,path:str)->bool:
    try:
        layers = information.get_layers(job)
        steps = information.get_steps(job)
        for step in steps:
            for layer in layers:
                base.load_layer(job,step,layer)
        base.save_job_as(job,path)
        return True
    except Exception as e:
        print(e)
    return False

def save_png(job:str, step:str, layers:list,picpath:str, layercolors:list,size,drawSR=False)->bool:
    try:
        (picpath,picname) = os.path.split(picpath)
        backcolor=[255,255,255,255]
        layer_box = json.loads(base.layer_box(job,step,layers))['paras']
        xmin = layer_box['xmin']
        ymin = layer_box['ymin']
        xmax = layer_box['xmax']
        ymax = layer_box['ymax']
        _ret = base.save_true_png(job,step,layers,xmin,ymin,xmax,ymax,picpath,picname,backcolor,layercolors,drawSR,size)
        png_process(picpath)
        ret = json.loads(_ret)['status']
        return ret
    except Exception as e:
        print(e)
    return False

def save_dxf(job:str,step:str,layers:list,savePath:str)->bool:
    try:
        _ret = base.dxf2file(job,step,layers,savePath)
        ret = json.loads(_ret)['paras']['result']
        return ret
    except Exception as e:
        print(e)
    return False