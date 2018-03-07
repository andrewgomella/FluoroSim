#!/usr/bin/env python

'''
FluoroSim
Code to run a fluoroscopy simulation as presented at SIR 2018

Based on opencv video_threaded.py sample (Multithreaded video processing sample): 
https://github.com/opencv/opencv/tree/master/samples/python

Usage:
   fluoro_sim.py {<video device number>}

Keyboard shortcuts:
   ESC - exit
   Space - Toggle Peddle
   1 - Toggle Overlay
   2 - Toggle Subtraction
   3 - Fullscreen
   4 - Windowed mode
   5 - Retake background image used in subtraction
   6 - Equalize histogram
   7 - Toggle HUD (On screen text display)
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv

from multiprocessing.pool import ThreadPool
from collections import deque

import RPi.GPIO as GPIO

#location of overlay image
OVERLAY_IMAGE="skel.jpg"

#frome video.py opencv example
def create_capture(source = 0):
    '''source: <int> or '<int>|<filename>|synth [:<param_name>=<value> [:...]]'
    '''
    source = str(source).strip()
    chunks = source.split(':')
    # handle drive letter ('c:', ...)
    if len(chunks) > 1 and len(chunks[0]) == 1 and chunks[0].isalpha():
        chunks[1] = chunks[0] + ':' + chunks[1]
        del chunks[0]

    source = chunks[0]
    try: source = int(source)
    except ValueError: pass
    params = dict( s.split('=') for s in chunks[1:] )

    cap = None
    cap = cv.VideoCapture(source)
    if 'size' in params:
        w, h = map(int, params['size'].split('x'))
        cap.set(cv.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, h)
    if cap is None or not cap.isOpened():
        print('Warning: unable to open video source: ', source)
    return cap

#from common import clock
def clock():
    return cv.getTickCount() / cv.getTickFrequency()

#from common import draw_str
def draw_str(dst, target, s):
    x, y = target
    cv.putText(dst, s, (x+1, y+1), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv.LINE_AA)
    cv.putText(dst, s, (x, y), cv.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv.LINE_AA)

#from common import StatValue
class StatValue:
    def __init__(self, smooth_coef = 0.5):
        self.value = None
        self.smooth_coef = smooth_coef
    def update(self, v):
        if self.value is None:
            self.value = v
        else:
            c = self.smooth_coef
            self.value = c * self.value + (1.0-c) * v

class DummyTask:
    def __init__(self, data):
        self.data = data
    def ready(self):
        return True
    def get(self):
        return self.data

if __name__ == '__main__':
    import sys

    print(__doc__)

    try:
        fn = sys.argv[1]
    except:
        fn = 0
    cap = create_capture(fn)

    #setup peddle input to be GPIO #4 in pull down mode 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    #
    cv.namedWindow("FLUORO", cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty("FLUORO", cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)

    #prepare overlay frame
    overlay = cv.imread(OVERLAY_IMAGE)
    overlay = cv.cvtColor(overlay, cv.COLOR_RGB2GRAY)
    #overlay = cv.flip(overlay,1)
    #overlay = cv.flip(overlay,0)

    #grab background frame
    ret, background = cap.read()
    background = cv.cvtColor(background, cv.COLOR_RGB2GRAY)

    def process_frame(frame, t0, subtract_mode, overlay_mode, equalize_mode):
        #convert to grayscale      
        frame = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
        #do subtraction if enabled
        if subtract_mode:
                frame = cv.absdiff(frame,background) 
                frame = cv.bitwise_not(frame)
        #flip horizontally and vertically
        frame=cv.flip(frame,1)
        frame=cv.flip(frame,0)
        #add overlay
        if overlay_mode:
            frame = cv.addWeighted(overlay, 0.5, frame, 0.5, 0)
        #equalize histogram
        if equalize_mode:
            frame = cv.equalizeHist(frame)
        return frame, t0

    threadn = cv.getNumberOfCPUs()
    pool = ThreadPool(processes = threadn)
    pending = deque()

    subtract_mode = True
    threaded_mode = True
    overlay_mode = True
    equalize_mode = True 
    peddle_mode = True
    hud_mode = True

    latency = StatValue()
    frame_interval = StatValue()
    last_frame_time = clock()
    while True:
        while len(pending) > 0 and pending[0].ready():
            res, t0 = pending.popleft().get()
            latency.update(clock() - t0)
            if hud_mode:
                draw_str(res, (20, 20), "(1)Toggle Subtraction : " + str(subtract_mode) + "  (3)Fullscreen (4)Windowed")
                draw_str(res, (20, 40), "(2)Toggle Overlay     : " + str(overlay_mode) + "   (5)Take Background (6)EqualizeHist")
                draw_str(res, (20, 60), "(Space) Toggle Peddle : " + str(peddle_mode) + "  (7)Toggle HUD")
                #draw_str(res, (20, 80), "latency        :  %.1f ms" % (latency.value*1000))
                #draw_str(res, (20, 60), "frame interval :  %.1f ms" % (frame_interval.value*1000))
                #draw_str(res, (20, 80), "threaded      :  " + str(threaded_mode))
            if GPIO.input(4) == 0:
                draw_str(res, (20, 450), "PEDAL ACTIVE")
            cv.imshow('FLUORO', res)
        if len(pending) < threadn:
            if (GPIO.input(4) == 0 or peddle_mode == False):
                ret, frame = cap.read()
                t = clock()
                frame_interval.update(t - last_frame_time)
                last_frame_time = t
                if threaded_mode:
                    task = pool.apply_async(process_frame, (frame.copy(), t, subtract_mode, overlay_mode, equalize_mode))
                else:
                    task = DummyTask(process_frame(frame, t, subtract_mode, overlay_mode, equalize_mode))
                pending.append(task)
        ch = cv.waitKey(1)
        #if ch == ord(' '):
        #    threaded_mode = not threaded_mode
        if ch == ord(' '):
            peddle_mode = not peddle_mode
        if ch == 49:
            subtract_mode = not subtract_mode
        if ch == 50:
            overlay_mode = not overlay_mode
        if ch == 51:
            cv.setWindowProperty("FLUORO", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        if ch == 52:
            cv.setWindowProperty("FLUORO", cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        if ch == 53:
            background = frame
            background = cv.cvtColor(background, cv.COLOR_RGB2GRAY)
        if ch == 54:
            equalize_mode = not equalize_mode
        if ch == 55:
            hud_mode = not hud_mode
        if ch == 27:
            break
cv.destroyAllWindows()