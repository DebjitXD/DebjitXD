# prep_photo.py - removes the background and boosts contrast, ready for ASCII.
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

PHOTO = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"   # your photo
OUTPUT = "photo-prepped.png"                                # file we create

# Crop box: (left, top, right, bottom) in pixels. Change it to frame your head.
CROP = (360, 300, 1340, 1420)

# 1) Cut out the person (the background becomes transparent)
person = remove(Image.open(PHOTO), session=new_session("u2net_human_seg"))
person = person.crop(CROP)

# 2) Paste the person onto a pure BLACK background (black = empty space later)
black = Image.new("RGBA", person.size, (0, 0, 0, 255))
black.alpha_composite(person)

# 3) Make it grey and boost the contrast (CLAHE brings out the face details)
grey = cv2.cvtColor(np.array(black.convert("RGB")), cv2.COLOR_RGB2GRAY)
grey = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(6, 6)).apply(grey)

# 4) Stretch the person's brightness so it uses the full dark-to-bright range
mask = grey > 5                                   # pixels that belong to the person
low, high = np.percentile(grey[mask], (3, 97))    # ignore the extreme 3% each side
grey = np.clip((grey - low) / (high - low), 0, 1)
grey = (255 * grey * mask).astype(np.uint8)       # background stays black

# 5) Save
Image.fromarray(grey).save(OUTPUT)
print("Saved", OUTPUT)
