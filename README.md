# wmts2kmz

You have a Garmin eTrex capable of loading custom maps, yet you don't want to pay for custom maps or you are in a country for which you don't qualify for free map data? Then this script might be of help.

This is a Python script for downloading raster map tiles via Web Map Tile Services and have them neatly packaged into kmz archives that can then be copied to Garmin GPS navigators such as eTrex 30.

## WMTS Services
So far the following WMTS services have been successfully used and maps deployed on my Garmin eTrex 30. Any WMTS service should work, as long as it serves EPS:900913 tiles.
- [Geographical Information Authority of Japan](https://www.gsi.go.jp/)
- [Institut National de l'Informatique Géographique et Forestière](http://www.ign.fr/)
- [Kartverktet / Norwegian Mapping Authority](https://www.kartverket.no/)
- [Kortforsyningen.dk]()
  - [GetCapabilities](https://services.kortforsyningen.dk/service?request=GetCapabilities&version=1.1.1&servicename=topo25&service=WMS)

## Usage
```
# edit config.example to your liking.
# refer to sample configs in example dir.
pipenv shell
python ./maptiles.py --config=foobar.config
```

## Notes on KMZ format Garmin expects
* no PNG
* kml file must be named `doc.kml`
* overlay files must be in the same directory as `doc.kml`

## N.B.
- KMZ files are not created automatically. Remove PNG files from the directory created and then zip it, with kmz as suffix.
