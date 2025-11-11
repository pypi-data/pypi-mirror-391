#! /usr/bin/env python

from __future__ import print_function
import json

# Model parameters

#- Geometry
length = 12
width = 4
height = 1.5

#- Material properties
density = 1000 # kg/m3
color = 'black'

# Calculations...

base_area = length * width
volume = base_area * height

mass = volume * density

# Print output (in json format)

output = {
            'base_area': base_area,
            'volume': volume,
            'mass': mass
         }

print('base_area =', base_area)
print('volume =', volume)
print('mass =', mass)

with open('output.json', 'w') as f:
    f.write(json.dumps(output))
    print('Successfully written results to output file "output.json"')
