#!/usr/bin/env python

import PIL
import Image
import array
from optparse import OptionParser
import csv
from math import sqrt,sin,cos,pi
#from configparser import ConfigParser

class Color:
	def __init__(self,color,frequency=None,name=None):
		if name != None:
			name = name.strip()
		self.name = name
		self.color = color
		self.frequency = frequency
		self.score = 0

	def distance(self,color):
		hsv1 = self.toHSV()
		hsv2 = color.toHSV()
		def x(h,s):
			return s*cos(h*2*pi/360)
		def y(h,s):
			return s*sin(h*2*pi/360)
		return sqrt((hsv2[2] - hsv1[2])**2 + (x(hsv2[0],hsv2[1]) - x(hsv1[0],hsv1[1]))**2 + (y(hsv2[0],hsv2[1]) - y(hsv1[0],hsv1[1]))**2 )

	def toHSV(self):
		rgb = [self.color[0],self.color[1],self.color[2]]
		M = max(rgb)
		m = min(rgb)
		C = M-m
		if C == 0:
			H_prime = 0
		elif M == rgb[0]:
			H_prime = (float(rgb[1] - rgb[2]) / C) % 6
		elif M == rgb[1]:
			H_prime = (float(rgb[2] - rgb[0]) / C) + 2 
		elif M == rgb[2]:
			H_prime = (float(rgb[0] - rgb[1]) / C) + 4 
	
		H = 60 * H_prime
	
		V = float(M) / 255 * 100

		if V == 0:
			S = 0
		else:
			S = float(C)/(V / 100 * 255) * 100

		return [H,round(S),round(V)]

	def __str__(self):
		return "%s -- %s -- %s" % (self.name,self.color,self.frequency)

class ColorCatalog:
	def __init__(self,colorlist):
		self.colors = colorlist

	def get_top(self,n):
		byfreq = sorted(self.colors,cmp=lambda x,y: x[0] - y[0],reverse=True)
		return byfreq[0:n]

	def find_closest(self,color):
		diffs = map(lambda x: x.distance(color),self.colors)
		color = self.colors[diffs.index(min(diffs))]
		return color

	def getColorByName(self,name):
		for color in self.colors:
			if color.name == name:
				return color
		return None

	def addColor(self,color):
		if self.getColorByName(color.name) == None:
			self.colors.append(color)

	def generate_map(self,colorcatalog):
		colormap = dict()
		for color in self.colors:
			# Ignore Snow White
			#if color.color == (255,255,255):
				#continue
			mappedcolor = colorcatalog.find_closest(color)
			if colormap.has_key(mappedcolor):
				colormap[mappedcolor].append(color)
			else:
				colormap[mappedcolor] = [color]
		
		
		
		for mappedcolor,colorlist in colormap.items():
			freq = 0
			for color in colorlist:
				freq = freq + color.frequency

			mappedcolor.frequency = freq
				
		return colormap

	def getpctcolors(self,pct=90.0):
		total_pixels = reduce(lambda x,y: x+ y.frequency ,self.colors,0)
		toppct = sorted(self.colors,cmp=lambda x,y: x.frequency - y.frequency,reverse=True)
		while reduce(lambda x,y: x + y.frequency,toppct,0) > float(pct)/100 * total_pixels:
			toppct.pop()
		return toppct
			
		

class ColorMap:
	def __init__(self,sourcecolors,destcolors,n):
		self.sourcecolors = sourcecolors
		self.destcolors = destcolors
		self.colormap = sourcecolors.generate_map(destcolors)
		self.__reduce(n)

	def __reduce(self,n):
		mappedcolors = self.colormap.keys()

		# Find mapped colors that cover the most pixels
		#topn = ColorCatalog(sorted(mappedcolors,cmp=lambda x,y: x.frequency - y.frequency,reverse=True)[0:min(len(mappedcolors),n)])
		commoncolors = sorted(mappedcolors,cmp=lambda x,y: x.frequency - y.frequency,reverse=True)

		distances = []
		freqs = []
		for i  in range(len(commoncolors)):
			color1 = commoncolors[i]
			cdist = []
			cfreq = []
			for j in range(len(commoncolors)):
				color2 = commoncolors[j]
				cdist.append(color1.distance(color2))
				cfreq.append(color1.frequency + color2.frequency)
			distances.append(cdist)
			freqs.append(cfreq)

		dl = []
		for l in freqs:
			dl += l

		dl.sort()
		dl.reverse()
		
		minfreq = dl[len(commoncolors)**2 / n]
		mindist= (223/n)
		#print mindist

		skip = []
		for i in range(len(distances)):
			d = distances[i]
			f = freqs[i]
			#print d
			for j in range(len(d)):
				if d[j] > 0 and f[j] < minfreq and d[j] < mindist and j < i:
					#print "Skipping %s -- %s %s" % (commoncolors[j].name,d[j],f[j])
					skip.append(j)
					
		#print len(skip)

		reduced = []
		for i in range(len(commoncolors)):
			if i not in skip:
				reduced.append(commoncolors[i])
			
		topn = ColorCatalog(sorted(reduced,lambda x,y: x.frequency - y.frequency,reverse=True))
		

		#topn = ColorCatalog(commoncolors)
			
		
		# Force black to be one of the colors
		white = self.destcolors.getColorByName("White")
		black = self.destcolors.getColorByName("310")
		topn.addColor(white)
		topn.addColor(black)

		# Remap
		self.colormap = self.sourcecolors.generate_map(topn)

	def getMap(self):
		return self.colormap		
		
			
		

def main():
	p = OptionParser()
	p.add_option("-t","--floss-table",dest="flosstable")
	p.add_option("-o","--output-table",dest="output")
	p.add_option("-n","--thread-colors",dest="colorcount",type="int")
	(options,args) = p.parse_args()

	f = csv.reader(open(options.flosstable,'rb'),delimiter=",", quotechar='"')
	cl = []
	for row in f:
		cl.append(Color(name=row[0],color=(int(row[1]),int(row[2]),int(row[3])),frequency=None))

	dmc_colors = ColorCatalog(cl)

	im = Image.open(args[0])
	colors = ColorCatalog(map(lambda x: Color(name=None,color=x[1],frequency=x[0]),im.getcolors(im.size[0]*im.size[1])))

	print len(colors.getpctcolors(85.0))

	colormap = ColorMap(colors,dmc_colors,options.colorcount)	
	
	matches = colormap.getMap().keys()
	#print matches
	
	data = array.array('B')
	for match in matches:
		print match
		data.append(match.color[0])
		data.append(match.color[1])
		data.append(match.color[2])
	for fill in range(len(matches),256):
		data.append(0)
		data.append(0)
		data.append(0)
	data.append(0)
	data.append(len(matches))
	data.append(255)
	data.append(255)
	data.byteswap()
	o = open(options.output,'w')
	data.tofile(o)
	o.close()

if __name__ == "__main__":
	main()
