from PIL import Image

for name in ("pawn", "knight", "bishop", "rook", "queen", "king"):

    img = Image.open(name+".black.png")
    pix = img.load()

    size = img.size

    for x in range(size[0]):
        for y in range(size[1]):
            colour = pix[x, y]
            if colour[:-1] == (219, 219, 219):
                pix[x, y] = (182, 182, 182, colour[-1])

    img.save(name+".black.png", "PNG")
