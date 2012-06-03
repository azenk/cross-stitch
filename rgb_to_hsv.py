#!/usr/bin/env python

def rgb2hsv(r,g,b):
	rgb = [r,g,b]
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

if __name__ == "__main__":
	values = [(0,0,0),(255,255,255),(255,0,0),(0,255,0),(0,0,255),(76,139,80),(206, 145, 36)]
	for v in values:
		print "RGB: %s -- HSV: %s" %(v,rgb2hsv(v[0],v[1],v[2]))
