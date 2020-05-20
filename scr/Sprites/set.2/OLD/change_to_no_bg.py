from PIL import Image

name = "knight"

img = Image.open(name+".png")
img = img.convert("RGB")
pix = img.load()

size = img.size

img2 = Image.new("RGBA", size)
pix2 = img2.load()

for x in range(size[0]):
    for y in range(size[1]):
        colour = pix[x, y]
        if colour == (255, 255, 255):
            pix2[x, y] = (0, 0, 255, 0)
        else:
            pix2[x, y] = colour+(255, )

img2.save(name+".white.png", "PNG")
