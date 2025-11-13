import json,os
from deepKernel import base,information

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

def save_png(job:str, step:str, layers:list, xmin:int, ymin:int, xmax:int, ymax:int, picpath:str, backcolor:list, layercolors:list)->bool:
    try:
        (picpath,picname) = os.path.split(picpath)
        layer_sum = len(layers)
        color_sum = len(layercolors)
        back_sum = len(backcolor)
        b = True
        if  back_sum != 4:
            b = False
        else:
            if layer_sum != color_sum:
                b = False
            else:
                for i in range(0,color_sum):
                    color = layercolors[i]
                    if len(color) != 4:
                        b = False
                        break
        if b == True:
            _ret = base.save_png(job,step,layers,xmin,ymin,xmax,ymax,picpath,picname,backcolor,layercolors)
            ret = json.loads(_ret)['status']
            if ret == 'true':
                ret = True
            else:
                ret = False
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