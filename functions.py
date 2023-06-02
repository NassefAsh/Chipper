import os, subprocess, sys
import geopandas as gp
from osgeo import gdal, osr, ogr
from shapely.geometry import Polygon
import shapely.wkb
from datetime import datetime, timedelta
import time

#def MountDataset():
#    datasetPath = input('Enter the path to your dataset: ') or '//192.168.3.25/Exchange/ForAsh/CarletonRequest_DRAPE2019TIFF'
#    username = input('Enter the username you want to use to access your dataset: ') or 'administrator'
#    domain = input('Enter the domain name: ') or 'gis'
#    os.system('sudo mount -t cifs ' + datasetPath + ' /mnt/images -o username=' + username + ',domain=' + domain)
#
#if not os.path.isdir('./processed'):
#    os.mkdir('./processed')
#if not os.path.isdir('/mnt/images'):
#    os.system('sudo mkdir /mnt/images')
#    MountDataset()
#
#
#if len(os.listdir(path_orthophotos)) == 0:
#    MountDataset()

# path_polygons = './processed/'

def GetHours(timedelta: datetime):
    return  int(timedelta.hour)

def GetMinutes(timedelta: datetime):
    return  int(timedelta.minute)

def GetSeconds(timedelta: datetime):
    return  int(timedelta.second)

def GetMicroSeconds(timedelta: datetime):
    return int(timedelta.microsecond)

def GetElapsedTime(startTime: datetime, endTime: datetime):
    elapsedTime = endTime - timedelta(hours = GetHours(startTime), minutes = GetMinutes(startTime), seconds = GetSeconds(startTime), microseconds = GetMicroSeconds(startTime))
    return elapsedTime.strftime('%H:%M:%S.%f')[:-3]

def GetSRS(file):
    srs = osr.SpatialReference(wkt=file.GetProjection())
    return srs

def GetExtent(file):
    xmin, xres, xskew, ymax, yskew, yres = file.GetGeoTransform()
    sizeX = file.RasterXSize * xres
    sizeY = file.RasterYSize * yres
    xmax = xmin + sizeX
    ymin = ymax + sizeY
    extent = xmin, ymin, xmax, ymax
    return extent

def CreatePolygon(extent):
    # extent = xmin, ymin, xmax, ymax
    # Polygon(bottom-left, top-left, top-right, bottom-right) - ESRI shapefile
    # Polygon(bottom-left, bottom-right, top-right, top-left) - Simple feature
    
    # ESRI shapefile: 
    #polygon = Polygon([[extent[0],extent[3]], [extent[2],extent[3]], [extent[2],extent[1]], [extent[0],extent[1]]])
    polygon = Polygon([[extent[0],extent[1]], [extent[0],extent[3]], [extent[2],extent[3]], [extent[2],extent[1]]])
    
    # Simple feature:
    #polygon = Polygon([[extent[2],extent[3]], [extent[0],extent[1]], [extent[0],extent[3]], [extent[2],extent[1]]]).buffer(0)
    return polygon

def CreateLayer(dataSource, layerName, projection, polygonType):
    return dataSource.CreateLayer(layerName, projection, polygonType)

def CreateDataSource(filename):
    driver = ogr.GetDriverByName('Esri Shapefile')
    return driver.CreateDataSource(filename)

def SavePolygonToShapefile(path_polygons, i_filename, polygon, projection, o_filename):
    if not os.path.isdir(path_polygons):
        os.mkdir(path_polygons)
    if not os.path.isdir(path_polygons + '/' + i_filename):
        os.mkdir(path_polygons + '/' + i_filename)
    ds = CreateDataSource(path_polygons + '/' + i_filename + '/' + o_filename + '.shp')
    layer = CreateLayer(ds, o_filename, projection, ogr.wkbPolygon)
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    defn = layer.GetLayerDefn()
    feat = ogr.Feature(defn)
    feat.SetField('id', 123)
    geom = ogr.CreateGeometryFromWkb(polygon.wkb)
    feat.SetGeometry(geom)
    layer.CreateFeature(feat)
    feat = geom = ds = layer = feat = geom = None
    return ds

def ClipPolygon(mask, aoi, outputLayer):
    ogr.Layer.Clip(mask.GetLayer(), aoi.GetLayer(), outputLayer)

def Rasterize(shapefile, fieldName, filename, refImg):
    driver = gdal.GetDriverByName('GTiff')
    output = driver.Create(filename, refImg.RasterXSize, refImg.RasterYSize, 1, gdal.GDT_Byte)
    output.SetGeoTransform(refImg.GetGeoTransform())
    band = output.GetRasterBand(1)
    band.SetNoDataValue(0)
    band.FlushCache()
    
    raster = gdal.RasterizeLayer(output, [1], shapefile.GetLayer(), options=["ATTRIBUTE=" + fieldName, "COMPRESS=DEFLATE"])
    output = band = None
    return raster

def ChipImage(image, path, xSize, ySize, verbose):
    imageWidth = image.RasterXSize
    imageHeight = image.RasterYSize
    srs = osr.SpatialReference(wkt=image.GetProjection())

    assert imageWidth % xSize == 0, 'Invalid xSize. Must be a factor of ' + str(imageWidth)
    assert imageHeight % ySize == 0, 'Invalide ySize. Must be a factor of ' + str(imageHeight)

    for i in range(10):
        for j in range(10):
            ds = gdal.Translate(path + str(i + 1) + '-' + str(j + 1) + '.tif', image, srcWin = [xSize * j, ySize * i, xSize, ySize], unscale = True, noData = 0, outputSRS = srs)

            if verbose == 'y':
                print(verbose, path + str(i + 1) + '-' + str(j + 1) + '.tif created.')
            
            ds = None