#!/awips2/python/bin/python
#use gio open to view gif
############################################################################
############################################################################
#
#Michelle McAuley Jan 2021 APRFC
#
############################################################################
############################################################################

from ufpy.dataaccess import DataAccessLayer
import matplotlib as mpl
mpl.use('Agg')
from matplotlib.path import Path
import matplotlib.pyplot as plt, numpy as np
#import shapely

import datetime, os, time, sys, re, subprocess, calendar
sys.path.append(os.path.abspath(".."))
try:
   import cPickle as pickle
except:
   import pickle as pickle
from dateutil.parser import parse
from mpl_toolkits.basemap import Basemap
# Import local file for radar color table
from radarColorTable import *
from shapely.geometry import base as shpbase
from shapely.geometry.polygon import LinearRing

homeDir = '/home/mmcauley/Practice/python/radarImages/'
rda = sys.argv[1]

os.environ['TZ'] = 'US/Alaska'
time.tzset()

############################################################################
# First check to see if this script is already running. If so, then exit.
# This will avoid duplicate versions running.
processes = subprocess.Popen(['ps','-ef'], stdout=subprocess.PIPE).communicate()[0]
for p in processes:
 if re.search('makeImage', p):
  print("***********************************************************")
  print(p)
  print('Script is already running, terminating this instance early.')
  quit()


############################################################################
# Initialize map projection
#  Check to see if it already exists. If not, create and save off.
coords = {'paih':[-154,57,-140,63],
          'pahg':[-155,57,-142,63],
          'pacg':[-144,54,-128,60],
          'papd':[-150,63,-143,66],
          'pakc':[-160,56,-153,61],
          'pabc':[-166,57,-158,63],
          'paec':[-168,61,-159,68]
         }
if os.path.exists(homeDir+'bin/'+rda+'map.pck'):
 m = pickle.load(open(homeDir+'bin/'+rda+'map.pck','r'))
else:
 m = Basemap(projection='lcc', resolution='h', area_thresh=0., epsg=3572,
  llcrnrlon=coords[rda][0], llcrnrlat=coords[rda][1], urcrnrlon=coords[rda][2], urcrnrlat=coords[rda][3])
 pickle.dump(m, open(homeDir+'bin/'+rda+'map.pck','w'))

#get projection boundaries
path = Path([(m.xmin,m.ymin),(m.xmin,m.ymax),(m.xmax,m.ymax),(m.xmax,m.ymin)])
envelope = LinearRing(((coords[rda][0],coords[rda][1]),(coords[rda][0],coords[rda][3]),(coords[rda][2],coords[rda][3]),(coords[rda][2],coords[rda][1])))

############################################################################
if os.path.exists(homeDir+'images/'+rda+'/foreground.png') == False:
 print('Foreground map does not exist, creating...')

 # Turn interactive plotting off
 plt.ioff()

 # Initialize figure size (48,27) for 4K and (24,15) for 1080p
 plt.figure(num=1, figsize=(8,5), dpi=80)
 m.drawmapboundary()

 # Look for cities list, if not create it... create it in file so you can 
 # comment out cities
 if os.path.exists(homeDir+'bin/'+rda+'cities.pck') == False:
  cityList = []
  req = DataAccessLayer.newDataRequest(datatype='maps',table='mapdata.city',geomField='the_geom',parameters=['name','lon','lat'],envelope=envelope)
  response = DataAccessLayer.getGeometryData(req,times=None)
  for city in response:
   cityInfo = str(city.getString('name'))+","+str(city.getNumber('lon'))+","+str(city.getNumber('lat'))
   cityList.append(cityInfo)
  pickle.dump(cityList, open(homeDir+'bin/'+rda+'cities.pck','w'))
 else:
  cityList = pickle.load(open(homeDir+'bin/'+rda+'cities.pck','r'))
  
 for city in cityList:
  (name,lon,lat) = city.split(',')
  if name[0] != "#": #for postediting to comment out
   lon,lat = m(lon,lat)
   if path.contains_point([lon,lat]):
    plt.text(lon,lat,' '+name+'\n',size=7,va='bottom',ha='left',linespacing=0.5,fontweight=600,clip_on=True)
    plt.scatter(lon,lat,marker='+',c='black')

 plt.savefig(homeDir+'images/'+rda+'/foreground.png', bbox_inches='tight',pad_inches=0,transparent=True)
 plt.close()
 print('...saved foreground image')

# Check to see if the background image is there, if not make it
if os.path.exists(homeDir+'images/'+rda+'/background.png') == False:
 print('Background map does not exist, creating...')
 
 # Turn interactive plotting off
 plt.ioff()

 # Initialize figure size (48,27) for 4K and (24,15) for 1080p
 plt.figure(num=2, figsize=(8,5), dpi=80)

 # Add details to map
 m.drawmapboundary(fill_color='#91c8ed')
 #m.fillcontinents(color='#c6fc9d',lake_color='aqua')
 m.fillcontinents(color='white',lake_color='aqua')
# m.drawrivers(linewidth=1,color='blue')
 m.drawstates(linewidth=0.7, color='black')
 m.drawcoastlines(linewidth=0.7, color='black')
 m.drawcountries(linewidth=0.7, color='black')
 m.drawcounties(linewidth=0.5, color='gray')

#get roads
 if os.path.exists(homeDir+'bin/'+rda+'roads.pck') == False:
  roads = []
  req = DataAccessLayer.newDataRequest(datatype='maps',table='mapdata.ak_highways',geomField='the_geom',parameters=['hwyname'],envelope=envelope)
  response = DataAccessLayer.getGeometryData(req)
  for hwy in response:
   roads.append({'name':hwy.getString('hwyname'),'coords':shpbase.dump_coords(hwy.getGeometry())})
   #roads.append(shpbase.dump_coords(hwy.getGeometry()))
  pickle.dump(roads, open(homeDir+'bin/'+rda+'roads.pck','w'))
 else:
  roads = pickle.load(open(homeDir+'bin/'+rda+'roads.pck','r'))

 for hwy in roads:
  if hwy['name'][0] != '#':
   for line in hwy['coords']:
    lon = []
    lat = []
    for point in line:
     lon.append(point[0])
     lat.append(point[1])
    lons,lats= m(lon,lat)
    plt.plot(lons,lats,color='#7d0428',linestyle='solid',linewidth=0.7)

 #get rivers
 rivers = []
 #req = DataAccessLayer.newDataRequest(datatype='maps',table='mapdata.rivers_med_detail',geomField='the_geom')
 req = DataAccessLayer.newDataRequest(datatype='maps',table='mapdata.hydrography_rivers',geomField='the_geom')
 response = DataAccessLayer.getGeometryData(req)
 for river in response:
  rivers.append(shpbase.dump_coords(river.getGeometry()))

 for river in rivers:
  for line in river:
   lon = []
   lat = []
   for point in line:
    lon.append(point[0])
    lat.append(point[1])
   lons,lats=m(lon,lat) 
   plt.plot(lons,lats,color='blue',linestyle='solid',linewidth=0.5)


 # Adjust final image, save, and close out plot
 plt.savefig(homeDir+'images/'+rda+'/background.png',bbox_inches='tight',pad_inches=0)
 plt.close()
 print('...saved background image')
 
############################################################################
# Get a list of all radar images
images = [x for x in os.listdir(homeDir+'images/'+rda) if (x[-3:] == 'png' and x[0] != 'b' and x[0] != 'f')]
images.sort()

# Clear out old ones
cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=480)

for i in images:
 if parse(i.split('.')[0]) < cutoff:
  print('removing old image{}'.format(i))
  os.remove(homeDir+'images/'+rda+'/'+i)

############################################################################
# Initialize new request
req = DataAccessLayer.newDataRequest()
req.setDatatype('radar')

# Set desired data to pull
req.setLocationNames(rda)
req.setParameters('Composite Refl')

# Pull available times
times = DataAccessLayer.getAvailableTimes(req)
#print 'len times is ', len(times)

############################################################################
# Turn plotting off
plt.ioff()

# Make images...
firstIdx = 50
if len(times) < 50:
 firstIdx = len(times)
#for x in range(-50,0,1):
for x in range(-1*firstIdx,0,1):

 # Filename
 filename = times[x].validPeriod.end.strftime('%Y-%m-%d-%H%M') + '.png'

 # If image does not exist, make it
 if filename not in images:

  try:
   # Get data
   response = DataAccessLayer.getGridData(req, [times[x]])
   data = response[0].getRawData()
   data = np.ma.masked_invalid(data)

   # Get the lat/lon data
   lon, lat = response[0].getLatLonCoords()
   lon, lat = m(lon, lat)

   # Initialize figure size (48,27) for 4K and (24,15) for 1080p
   #plt.figure(num=None, figsize=(24,15), dpi=80)
   fig = plt.figure(num=None, figsize=(8,5), dpi=80)

   # Add radar data
   cmap = radarColors
   m.pcolormesh(lon, lat, data, cmap=cmap, vmin=-30, vmax=85, alpha=0.5, zorder=3)
   # Add date/time stamp
   timestamp = time.strftime('%a %x %I:%M %p %Z',time.localtime(calendar.timegm(time.strptime(str(times[x].validPeriod.end),"%Y-%m-%d %H:%M:%S"))))

   plt.annotate(timestamp,xy=(0.01,0.01), xycoords='axes fraction',fontsize=10,fontweight=500,bbox=dict(boxstyle="square",fc="#d5e6de"))

   # Save the image
   plt.savefig(homeDir+'images/'+rda+'/'+filename, bbox_inches='tight', transparent=True, pad_inches=0)
   plt.close()
   print('created image {}'.format(filename))

  except:
   print('Error with {}'.format(filename))

############################################################################
# Obtain new list of images
images = [x for x in os.listdir(homeDir+'images/'+rda+'/') if (x[-3:] == 'png' and x[0] != 'b' and x[0] != 'f')]
images.sort()
print("length images is ",len(images))
if len(images) > 50:
 print("making shorter")
 images = images[-50:]

#just send out a blank gif if there's nothing recent
if len(images) == 0 or parse(images[-1].split('.')[0]) < cutoff:
 print("no recent for ",rda)
 cmd = 'scp ' + homeDir+'blank.png ldad@ls1:/tmp/cmsFilesStaging/'+'cms_images+' + rda + 'loop.gif'
 os.system(cmd)
 sys.exit()
#latestValid = images[-1].split(".")[0]
print(images[-1])
 
cmd = 'scp ' + homeDir + 'images/'+rda+'/cms_images+' + rda + 'loop.gif ldad@ls1:/tmp/cmsFilesStaging/'

# Generate loop
cmd = 'convert -dispose none -delay 0 ' + homeDir+ 'images/'+rda+'/background.png -dispose previous'
cmd += ' -delay 100 ' + homeDir + 'images/'+rda+'/' + images[0]
cmd += ' -delay 3 '
for f in images[1:-1]: cmd += homeDir + 'images/'+rda+'/' + f + ' '
cmd += '-delay 200 ' + homeDir + 'images/'+rda+'/'+images[-1]
cmd += ' -loop 0 ' + homeDir + 'images/'+rda+'/cms_images+'+rda+'loop.gif'
os.system(cmd)

#add foreground (cities)
cmd = 'convert ' + homeDir + 'images/'+rda+'/cms_images+'+rda+'loop.gif -coalesce null: '+ homeDir + 'images/'+rda+'/foreground.png -gravity center -layers composite '+ homeDir + 'images/'+rda+'/cms_images+'+rda+'loop.gif'
os.system(cmd)

# Move loop
cmd = 'scp ' + homeDir + 'images/'+rda+'/cms_images+' + rda + 'loop.gif ldad@ls1:/tmp/cmsFilesStaging/'
os.system(cmd)

print('Radar loop created. Script done.')
