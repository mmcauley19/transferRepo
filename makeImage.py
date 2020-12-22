############################################################################
############################################################################
#
#	SAD/TV Wall Radar Loop Generator	
#
#	Paul Iniguez, PSR
#
#	v1: 9 JUN 2017
#		- Initial version of this script.
#
############################################################################
############################################################################

from ufpy.dataaccess import DataAccessLayer
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt, numpy as np
import datetime, os, time, sys, re, subprocess
try:
   import cPickle as pickle
except:
   import pickle as pickle
from dateutil.parser import parse
from mpl_toolkits.basemap import Basemap
# Import local file for radar color table
from radarColorTable import *

homeDir = '/localapps/runtime/SAD_radar/'

############################################################################
# First check to see if this script is already running. If so, then exit.
# This will avoid duplicate versions running.
processes = subprocess.Popen(['ps','-ef'], stdout=subprocess.PIPE).communicate()[0]
for p in processes:
	if re.search('makeImage', p):
		print('Script is already running, terminating this instance early.')
		quit()


############################################################################
# Initialize map projection
#  Check to see if it already exists. If not, create and save off.
if os.path.exists(homeDir+'map.pck'):
	m = pickle.load(open(homeDir+'bin/map.pck','r'))
else:
	m = Basemap(projection='lcc', resolution='h', area_thresh=10000., epsg=4269,
		llcrnrlon=-120, llcrnrlat=28, urcrnrlon=-100, urcrnrlat=40)
	pickle.dump(m, open(homeDir+'bin/map.pck','w'))


############################################################################
# Check to see if the background image is there, if not make it
if os.path.exists(homeDir+'images/background.png') == False:
	print('Background map does not exist, creating...')

	# Turn plotting off
	plt.ioff()

	# Initialize figure size (48,27) for 4K and (24,15) for 1080p
	plt.figure(num=None, figsize=(24,15), dpi=80)

	# Add details to map
	m.shadedrelief()
	m.drawstates(linewidth=1, color='black')
	m.drawcoastlines(linewidth=1, color='black')
	m.drawcountries(linewidth=1, color='black')
	m.drawcounties(linewidth=0.5, color='gray')

	# Adjust final image, save, and close out plot
	plt.tight_layout()
	plt.savefig(homeDir+'images/background.png', bbox_inches='tight')
	plt.close()
	print('...saved background image')


############################################################################
# Get a list of all radar images
images = [x for x in os.listdir(homeDir+'images') if (x[-3:] == 'png' and x[0] != 'b')]
images.sort()

# Clear out old ones
cutoff = datetime.datetime.now() - datetime.timedelta(minutes=480)
for i in images:
	if parse(i.split('.')[0]) < cutoff:
		print('removing old image{}'.format(i))
		os.remove(homeDir+'images/'+i)


############################################################################
# Initialize new request
req = DataAccessLayer.newDataRequest()
req.setDatatype('grid')

# Set desired data to pull
req.setLocationNames('MRMS_1000')
req.setParameters('MergedReflectivityQCComposite')
req.setLevels('500.0FH')

# Pull available times
times = DataAccessLayer.getAvailableTimes(req)

# Get the lat/lon data
#response = DataAccessLayer.getGridData(req, [times[-1]])
#lon, lat = response[0].getLatLonCoords()
#lon, lat = m(lon, lat)


############################################################################
# Turn plotting off
plt.ioff()

# Make images... each frame is two minutes. So 30 for an hour, 60 for two, etc.
for x in range(-240,0,1):

	# Filename
	filename = times[x].validPeriod.end.strftime('%Y-%m-%d-%H%M') + '.png'

	# If image does not exist, make it
	if filename not in images:

		try:
			# Get data
			response = DataAccessLayer.getGridData(req, [times[x]])
			data = response[0].getRawData()
			data = np.ma.masked_where(data<=-99,data)
			# Get the lat/lon data
			lon, lat = response[0].getLatLonCoords()
			lon, lat = m(lon, lat)

			# Initialize figure size (48,27) for 4K and (24,15) for 1080p
			plt.figure(num=None, figsize=(24,15), dpi=80)

			# Add radar data
			m.pcolormesh(lon, lat, data, cmap=radarColors, vmin=-30, vmax=85, alpha=0.5, zorder=3)
			plt.tight_layout()

			# Add date/time stamp
			timestamp = (times[x].validPeriod.end-datetime.timedelta(hours=7)).strftime('%a %x %I:%M %p')
			plt.text(-119.9, 28.1, timestamp, fontsize=32, fontweight='bold')

			# Save the image
			plt.savefig(homeDir+'images/'+filename, bbox_inches='tight', transparent=True)
			plt.close()
			print('created image {}'.format(filename))

		except:
			print('Error with {}'.format(filename))


############################################################################
# Obtain new list of images
images = [x for x in os.listdir(homeDir+'images') if (x[-3:] == 'png' and x[0] != 'b')]
images.sort()

# Generate loop
cmd = 'convert -dispose none -delay 0 ' + homeDir+ 'images/background.png -dispose previous'
cmd += ' -delay 100 ' + homeDir + 'images/' + images[0]
cmd += ' -delay 3 '
for f in images[1:-1]: cmd += homeDir + 'images/' + f + ' '
cmd += '-delay 200 ' + homeDir + 'images/'+images[-1]
cmd += ' -loop 0 ' + homeDir + 'images/loop.gif'
print(cmd)
os.system(cmd)

# Move loop
cmd = 'scp ' + homeDir + 'images/loop.gif ldad@ls1:/ldad/LocalApps/data/FilesFromAWIPS/.'
os.system(cmd)

print('Radar loop created. Script done.')
