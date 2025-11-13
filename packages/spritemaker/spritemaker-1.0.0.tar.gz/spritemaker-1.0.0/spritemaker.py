from PIL import Image
import random

def create_sprite(width, height, color=(0,0,0,0)):
    return Image.new("RGBA", (width, height), color)

def save_sprite(sprite, filename):
    sprite.save(filename, "PNG")

def draw_rectangle(sprite, x, y, w, h, color):
    for i in range(x, x+w):
        for j in range(y, y+h):
            if 0 <= i < sprite.width and 0 <= j < sprite.height:
                sprite.putpixel((i,j), color)

def random_character_sprite(size=16):
    spr = create_sprite(size, size)
    body_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255)
    draw_rectangle(spr, size//3, size//2, size//3, size//2, body_color)
    return spr
