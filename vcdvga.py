# Author - Russ Webber - russ@rw.id.au - https://github.com/russkel

import grammar
import numpy as np
#import scipy.misc
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description="Draws an image from VGA signals dumped in a VCD")
parser.add_argument('vcd', type=str, help='VCD file to draw from')
parser.add_argument('--frame', metavar='frame_num', type=int, default=1,
                    help='Which frame to draw (default is after the first vsync)')
parser.add_argument('--vsync', '-V', metavar='sig', type=str, required=True, help='Full name of the VSYNC signal')
parser.add_argument('--red', '-R', metavar='sig', type=str, required=True, help='Full name of the red VGA signal')
parser.add_argument('--green', '-G', metavar='sig', type=str, required=True, help='Full name of the green VGA signal')
parser.add_argument('--blue', '-B', metavar='sig', type=str, required=True, help='Full name of the blue VGA signal')
args = parser.parse_args()

img_width = 640
img_height = 480
pixel_tick = 40e3
v_backporch_ns = 23200 * pixel_tick
h_inbetween = (16 + 48 + 96 + 640) * pixel_tick

scope = []
signals = {}
signals_ref = {}
id_counter = 0

tree = grammar.vcd.parseFile(args.vcd)
raw_steps = tree.steps

for i in tree:
    if not hasattr(i, 'getName'): continue
    if i.getName() == 'scope':
        scope.append(i.module)
    if i.getName() == 'upscope':
        scope.pop()
    if i.getName() == 'signal':
        name = ".".join(scope + [i.name])
        signals_ref[i.id] = (id_counter, name)
        signals[name] = id_counter # (i.id,
        id_counter += 1


def process_steps(lines, signals_ref):
    ts = 0

    for line in lines.strip().split('\n'):
        if line == '$dumpvars' or line == '$end':
            continue

        if line[0] == '#':
            ts = int(line[1:])
            continue

        if line[0] == 'b':
            val, ident = line.split()
            val = int(val[1:], 2)
        else:
            val = line[0]
            if val == 'x':
                val = -1
            else:
                val = int(val)
            ident = line[1:]

        ident = signals_ref[ident][0]

        yield ts
        yield ident
        yield val

steps = np.fromiter(process_steps(raw_steps, signals_ref), np.double)
steps = steps.reshape((len(steps) // 3, 3))

# skip to first/desired VSYNC signal
vsync_transitions = steps[steps[:, 1] == signals[args.vsync], :]
end_sync = steps[(steps[:, 1] == signals[args.vsync]) & (steps[:, 2] == 1), :][args.frame, 0]

start_display = end_sync + v_backporch_ns

red_signals = steps[steps[:, 1] == signals[args.red], :]
green_signals = steps[steps[:, 1] == signals[args.green], :]
blue_signals = steps[steps[:, 1] == signals[args.blue], :]

horiz_sample_times = np.arange(0, img_width * pixel_tick, pixel_tick)
vert_sample_times = np.arange(0, img_height * h_inbetween, h_inbetween)
sample_times = np.tile(horiz_sample_times, (img_height, 1)) + \
               np.tile(vert_sample_times, (img_width, 1)).T + start_display

img = np.empty((img_height, img_width, 3), dtype=np.uint8)

for i, sigs in enumerate([red_signals, green_signals, blue_signals]):
    pixels_idx = sigs[:, 0].searchsorted(sample_times, 'right') - 1
    pixels = sigs[pixels_idx, 2]
    img[:, :, i] = 255 * pixels.reshape((480, 640))

plt.imshow(img)
plt.show()

#scipy.misc.imsave('test.png', img)
