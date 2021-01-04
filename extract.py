import os
from PIL import Image
import requests
from io import BytesIO

# Based on https://gist.github.com/BigglesZX/4016539 (but adapted to be a
# generator that yields frames instead of a function that saves out frames)

def analyseImage(im):
    '''
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    '''
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    im.seek(0)
    return results


def getFrames(im):
    '''
    Iterate the GIF, extracting each frame.
    '''
    mode = analyseImage(im)['mode']

    p = im.getpalette()
    last_frame = im.convert('RGBA')

    try:
        while True:
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.putpalette(p)

            new_frame = Image.new('RGBA', im.size)

            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(im, (0,0), im.convert('RGBA'))
            yield new_frame

            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass


def getDeltas(url):
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))

    prevFrame = ''
    deltas = []

    for (i, frame) in enumerate(getFrames(im)):
        if prevFrame == '':
            prevFrame = frame
            continue

        assert prevFrame.mode == frame.mode, "Different kinds of images."
        assert prevFrame.size == frame.size, "Different sizes."

        pairs = zip(prevFrame.getdata(), frame.getdata())
        if len(prevFrame.getbands()) == 1:
            # for gray-scale jpegs
            dif = sum(abs(p1-p2) for p1,p2 in pairs)
        else:
            dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))

        ncomponents = prevFrame.size[0] * prevFrame.size[1] * 3
        deltas.append((dif / 255.0 * 100) / ncomponents)

        prevFrame = frame

    return deltas
