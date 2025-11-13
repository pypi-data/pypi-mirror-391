from cinewiz.genai import *
import os

# Initialize configuration for first-time setup
set_start_first_use_config()

#define locapath
path_local = os.getcwd()
path_lib = f'{path_local}/_lib'
path_out = f'{path_lib}/_out'
path_fonts = f'{path_lib}/_fonts'

# Set initial starting image
set_init(f'{path_out}/postcard.jpg')

#define background color RGB like 'blank' or (255, 255, 255)
_rgb = 'BLANK' 

# Create a new canvas
set_board(800, 600, 'white')  # white background blank

# Add a portrait background (by style/keyword)
_background = f'{path_lib}/postcard/postcard.jpg'
_buff_w = set_background(0, "NIL", _background, 0) # #use 0 - to websearch is not allowed - [1 - when is decrapetd]

# Place a character and remove its background
_thumbnail = f'{path_lib}/postcard/image_postcal_01.jpg'
_postal = resize_picture(_thumbnail,(240, 240))
print(f'--------------------------{_postal}---------------------')
_logo =  add_picture(_postal,50,50)
_gui = 'tCpeqDL/VEmiKvYh68d2Iw=='

#set multiline text
_text = """HAPPY LONDON JOURNEY:
BECAUSE I MISS YOU 
PS:BARINSKY"""

# Add text overlay
set_text(1,_gui,_text,60,300,(0, 0, 0),f'{path_fonts}/_fonts/Montserrat-Regular.ttf',22)

set_save()
