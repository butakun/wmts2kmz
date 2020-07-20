import urllib.request
import mercantile
import simplekml
import os
import pathlib
import argparse
from PIL import Image
import zipfile
import time


def convert_png_to_jpg(filename_png):

    filename_jpg = filename_png.replace(".png", ".jpg")
    Image.open(filename_png).convert("RGB").save(filename_jpg, quality=75)
    return filename_jpg


def get_corner_tiles(z, latlng_sw, latlng_ne, multiple=None):

    tile_sw = mercantile.tile(latlng_sw[1], latlng_sw[0], z)
    tile_ne = mercantile.tile(latlng_ne[1], latlng_ne[0], z)
    if multiple is None:
        return tile_sw, tile_ne

    nx = tile_ne.x - tile_sw.x + 1
    ny = tile_sw.y - tile_ne.y + 1

    tile_ne = mercantile.Tile(tile_ne.x + multiple - nx % multiple, tile_ne.y, z)
    tile_sw = mercantile.Tile(tile_sw.x, tile_sw.y + multiple - ny % multiple, z)
    return tile_sw, tile_ne


def fetch_tile_images(url_template, z, tile_sw, tile_ne, image_format, dirname, sleep):

    # os.removedirs(dirname)
    os.makedirs(dirname)

    print("tile_sw = ", tile_sw, ", tile_ne = ", tile_ne)

    tiles = []
    for y in range(tile_ne.y, tile_sw.y + 1):
        for x in range(tile_sw.x, tile_ne.x + 1):
            url = url_template.format(x=x, y=y, z=z)
            filename = "{z}_{x}_{y}.png".format(x=x, y=y, z=z)
            saveto_png = dirname + os.path.sep + filename
            print("URL = ", url)
            print("saving to = ", saveto_png)
            success = False
            while not success:
                try:
                    urllib.request.urlretrieve(url, saveto_png)
                    success = True
                except urllib.error.HTTPError as e:
                    print(f"{e.code}: {e.reason}")
                    if e.code == 500:
                        print(f"retrying after {sleep} second(s).")
                        time.sleep(sleep)
                    else:
                        raise

            if image_format == "jpg":
                image_filename = os.path.basename(convert_png_to_jpg(saveto_png))
            elif image_format == "png":
                image_filename = os.path.basename(saveto_png)
            else:
                raise ValueError
            tiles.append([image_filename, mercantile.Tile(x, y, z)])

    return tiles


def merge_tile_images(dirname, tiles, multiple=2):

    z = tiles[0][1].z

    x_min = min(tiles, key=lambda t: t[1].x)[1].x
    y_min = min(tiles, key=lambda t: t[1].y)[1].y
    x_max = max(tiles, key=lambda t: t[1].x)[1].x
    y_max = max(tiles, key=lambda t: t[1].y)[1].y
    print(x_min, x_max)

    lx = x_max - x_min + 1
    ly = y_max - y_min + 1
    assert lx % multiple == 0 and ly % multiple == 0

    tiles_dict = dict((t, f) for f, t in tiles)

    tiles_merged = []
    for x in range(x_min, x_max + 1, multiple):
        for y in range(y_min, y_max + 1, multiple):
            merged = Image.new("RGB", (256 * multiple, 256 * multiple))
            print("---")
            for i in range(multiple):
                for j in range(multiple):
                    tile = mercantile.Tile(x + i, y + j, z)
                    image_filename = dirname + os.path.sep + tiles_dict[tile]
                    print("  ", tile, image_filename)
                    image = Image.open(image_filename)
                    merged.paste(image, (256 * i, 256 * j))
            merged_filename = (
                dirname
                + os.path.sep
                + "{z}_{x}_{y}_{d}x{d}.jpg".format(x=x, y=y, z=z, d=multiple)
            )
            print("  -> ", merged_filename)
            merged.save(merged_filename)
            tiles_merged.append(
                [
                    os.path.basename(merged_filename),
                    [
                        mercantile.Tile(x, y, z),
                        mercantile.Tile(x + multiple - 1, y + multiple - 1, z),
                    ],
                ]
            )

    return tiles_merged


def generate_kml(tiles):
    """ tiles = [(filename, mercantile.Tile), ...] """

    kml = simplekml.Kml()

    for filename, (tile_nw, tile_se) in tiles:
        bounds_nw = mercantile.bounds(tile_nw)
        bounds_se = mercantile.bounds(tile_se)
        west = bounds_nw.west
        east = bounds_se.east
        south = bounds_se.south
        north = bounds_nw.north
        tileoverlay = kml.newgroundoverlay(
            name="{z}_{x}_{y}".format(x=tile_nw.x, y=tile_nw.y, z=tile_nw.z)
        )
        tileoverlay.icon.href = filename
        tileoverlay.latlonbox.west = west
        tileoverlay.latlonbox.east = east
        tileoverlay.latlonbox.south = south
        tileoverlay.latlonbox.north = north

    return kml


def test():

    # tiles = fetch_tile_images(14, [39.8099,140.8402], [40.0038,141.0367], 'tiles')
    tiles = fetch_tile_images(14, [35.333333, 139.0], [36, 140.0], "tiles")
    kml = generate_kml(tiles)
    kml.save("test.kml")


def main(name, latlng_sw, latlng_ne, zoom_level, multiple, image_format, url, sleep=0):

    tile_sw, tile_ne = get_corner_tiles(zoom_level, latlng_sw, latlng_ne, multiple)

    x_min, x_max = tile_sw.x, tile_ne.x
    y_min, y_max = tile_ne.y, tile_sw.y
    nx = x_max - x_min + 1
    ny = y_max - y_min + 1
    nx_merged = nx / multiple
    ny_merged = ny / multiple
    print("multiple = ", multiple)
    print("nx, ny = ", nx, ny)
    print("nx_merged, ny_merged = ", nx_merged, ny_merged)
    print("x min max = ", x_min, x_max)
    print("y min max = ", y_min, y_max)
    print("there are ", nx * ny, " tiles at zoom level ", zoom_level)
    print("there are ", nx_merged * ny_merged, " merged tiles")

    if nx_merged * ny_merged > 100:
        print(
            "keep the number of merged tile images to at most 100, by increasing `multiple` parameter"
        )
        return

    tiles = fetch_tile_images(
        url, zoom_level, tile_sw, tile_ne, image_format="png", dirname=name,
        sleep=sleep
    )
    merged_tiles = merge_tile_images(name, tiles, multiple)
    kml = generate_kml(merged_tiles)
    kml_file_name = pathlib.Path(name) / "doc.kml"
    kml.save(kml_file_name)

    kmz = zipfile.ZipFile(f"{name}.kmz", "w")
    kmz.write(kml_file_name)
    for filename, _ in merged_tiles:
        img_path = pathlib.Path(name) / filename
        kmz.write(img_path)
    kmz.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("--config")
    parser.add_argument("--config", help="config file")
    parser.add_argument("--sleep", type=float, default=1,  help="sleep (in sec) between tile fetch")
    args = parser.parse_args()
    config = {}
    exec(open(args.config).read(), None, config)
    main(
        config["name"],
        config["latlng_sw"],
        config["latlng_ne"],
        config["zoom_level"],
        config["multiple"],
        config["image_format"],
        config["url"],
        args.sleep
    )
