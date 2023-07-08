#!/usr/bin/env python3

import os, sys
from time import sleep
from optparse import OptionParser
import pyvisa

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Record oscilloscope data"
    
    parser = OptionParser(usage)
    parser.add_option("--nev", type=int, default=1000, help="Number of events [default: %default]")
    parser.add_option("--trig", type=int, default=10, help="Trigger level (mV) [default: %default]")
    parser.add_option("--delay", type=int, default=500, help="Trigger delay (ns) [default: %default]")
    parser.add_option("--ver", type=int, default=10, help="Vertical scale (mV/div) [default: %default]")
    parser.add_option("--hor", type=int, default=100, help="Horizontal scale (ns/div) [default: %default]")
    parser.add_option("--pos", type=int, default=-4, help="Vertical position (div) [default: %default]")
    parser.add_option("--data", type=str, default="output", help="Output file name [default: %default]")
    parser.add_option("--mode", type=str, default="select", help="Mode of data taking [default: %default]")
    parser.add_option("--chan", type=str, default="ch1,ch2", help="Channel to read [default: %default]")

    (options, args) = parser.parse_args(sys.argv[1:])

    return options

if __name__ == '__main__':
    
    options = main()

    rm = pyvisa.ResourceManager()
    print('Library:', rm)
    ress = rm.list_resources()
    print('Available resources: ', ress)
    tek = ress[-1]
    print('Scope: ', tek)
    tds = rm.open_resource(tek)
    tds.baud_rate = 38400
    tds.encoding = 'utf-8'

    tds.write("*IDN?")
    sleep(0.1)
    print(tds.read())
    
    chs = ['CH1', 'CH2']
    chsr = [ch.capitalize() for ch in options.chan.split(',')]

    tds.write("LOC NONE")
    for ch in chs:
        tds.write(ch+":COUPL DC")
        if ch in chsr:
            tds.write("SEL:"+ch+" ON")
            tds.write(ch+":POS "+str(options.pos))
            tds.write(ch+":SCA "+str(options.ver)+".0000E-3")
            tds.write(ch+":BANdwidth ON")
        else:
            tds.write("SEL:"+ch+" OFF")
    
    tds.write("HOR:RECORD 20000")
    if options.mode == 'select':
        tds.write("DATA:START 9000")
        tds.write("DATA:STOP 12000")
    else:
        tds.write("DATA:START 1")
        tds.write("DATA:STOP 20000")

    tds.write("HOR:DEL:TIM "+str(options.delay)+"E-9")
    tds.write("TRIGGER:A:LEVEL "+str(options.trig)+".0000E-3")
    tds.write("TRIG:A:EDGE:SOU CH1")

    tds.write("HOR:SCA "+str(options.hor)+".0000E-9")

    wfvars = 'BIT_Nr?;BN_Fmt?;BYT_Nr?;BYT_Or?;ENCdg?;NR_Pt?;PT_Fmt?;PT_Off?;WFId?;XINcr?;XUNit?;XZEro?;YMUlt?;YOFf?;YUNit?;YZEro?'

    f = open(options.data+'.dat', 'w')

#    tds.write("DATA:SOURCE CH1")
    tds.write("ENCDG RPBinary")
    tds.write("WDMPRE:PT_Fmt Y")
    tds.write("ACQ:STOPA SEQ")

    for i in range(options.nev):
        tds.write("ACQUIRE:STATE RUN")
        run = True
        while(run):
            tds.write("ACQUIRE:STATE?")
            state=tds.read()
            if repr(state) == repr('0\n'):
                print(i)
                run = False
                if i != options.nev-1:
                    tds.write("ACQUIRE:STATE RUN")
            sleep(0.1)
        tds.write("WFMPRE:"+wfvars)
        temp=tds.read()
    
        tds.write("ACQ:STOPA SEQ")
        for ch in chsr:
            tds.write("DATA:SOURCE "+ch)
            curve = tds.query_binary_values('CURVE?', datatype='h', is_big_endian=True)
            f.write(repr(temp.replace('\n', ''))+','+repr(curve)+'\n')

    #tds.write("LOC All")
    #tds.write("ACQ:STOPA SEQ")
    f.close()

