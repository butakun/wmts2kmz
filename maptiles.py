import urllib.request
import mercantile
import simplekml
import os
import argparse
from PIL import Image

def convert_png_to_jpg(filename_png):

    filename_jpg = filename_png.replace(".png", ".jpg")
    Image.open(filename_png).convert("RGB").save(filename_jpg, quality = 95)
    return filename_jpg

def fetch_tile_images(z, latlng_sw, latlng_ne, image_format, dirname):

    #os.removedirs(dirname)
    os.makedirs(dirname)

    tile_sw = mercantile.tile(latlng_sw[1], latlng_sw[0], z)
    tile_ne = mercantile.tile(latlng_ne[1], latlng_ne[0], z)

    print("tile_sw = ", tile_sw, ", tile_ne = ", tile_ne)

    tiles = []
    for y in range(tile_ne.y, tile_sw.y + 1):
        for x in range(tile_sw.x, tile_ne.x + 1):
            url = "https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png".format(x = x, y = y, z = z)
            filename = "{z}_{x}_{y}.png".format(x = x, y = y, z = z)
            saveto_png = dirname + os.path.sep + filename
            print("URL = ", url)
            print("saving to = ", saveto_png)
            urllib.request.urlretrieve(url, saveto_png)
            if image_format == "jpg":
                image_filename = os.path.basename(convert_png_to_jpg(saveto_png))
            elif image_format == "png":
                image_filename = os.path.basename(saveto_png)
            else:
                raise ValueError
            tiles.append([image_filename, mercantile.Tile(x, y, z)])

    return tiles

def generate_kml(tiles):
    """ tiles = [(filename, mercantile.Tile), ...] """

    kml = simplekml.Kml()

    for filename, tile in tiles:
        bounds = mercantile.bounds(tile)
        tileoverlay = kml.newgroundoverlay(name = "{z}_{x}_{y}".format(x = tile.x, y = tile.y, z = tile.z))
        tileoverlay.icon.href = filename
        tileoverlay.latlonbox.west = bounds.west
        tileoverlay.latlonbox.east = bounds.east
        tileoverlay.latlonbox.south = bounds.south
        tileoverlay.latlonbox.north = bounds.north

    return kml

def test():

    #tiles = fetch_tile_images(14, [39.8099,140.8402], [40.0038,141.0367], "tiles")
    tiles = fetch_tile_images(14, [35.333333,139.0], [36,140.0], "tiles")
    kml = generate_kml(tiles)
    kml.save("test.kml")

def main(name, latlng_sw, latlng_ne, zoom_level, image_format):

    tiles = fetch_tile_images(zoom_level, latlng_sw, latlng_ne, image_format, name)
    kml = generate_kml(tiles)
    kml.save(name + os.path.sep + "doc.kml")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("--config")
    parser.add_argument("--config", help = "config file")
    args = parser.parse_args()
    config = {}
    exec(open(args.config).read(), None, config)
    main(config["name"], config["latlng_sw"], config["latlng_ne"], config["zoom_level"], config["image_format"])
