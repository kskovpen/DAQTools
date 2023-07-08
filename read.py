#!/usr/bin/env python3

import os, sys
from optparse import OptionParser
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Plot oscilloscope data"
    
    parser = OptionParser(usage)
    parser.add_option("--input", default='output.dat', help="Input data file [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
    
    options = main()
    
    delim = ',['

    edep = []
    with open(options.input, 'r') as f:
        for il, l in enumerate(f.readlines()):
            conf = l.split(delim)[0]
            d = [int(s) for s in l.split(delim)[1].replace(']\n', '').replace('[', '').replace(' ', '').split(',')]
            conf = conf.replace('\'', '').split(';')
            v = [float(conf[15])-float(conf[13])*float(conf[12])+(float(conf[12])*dd) for dd in d]
            t = [float(conf[9])*i for i in range(int(conf[5]))]
            if il == 0:
                print('Number of points', len(t))
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.scatter(t,v)
                fig.savefig('pics/pulse.pdf')
#            print(il)
            edep.append(max(v))
            
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(edep, bins=50)
    fig.savefig('pics/edep.pdf')
