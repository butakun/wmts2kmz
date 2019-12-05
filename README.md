# gsimap2kmz

A Python script to download raster map tiles via Web Map Tile Services and have them neatly packaged into kmz archives that can simply copied to Garmin GPS navigators such as eTrex 30.

## WMTS Services
So far the following WMTS services have been successfully used and maps deployed on my Garmin eTrex 30. Any WMTS service should work, as long as it serves EPS:900913 tiles.
- [https://www.gsi.go.jp/](Geographical Information Authority of Japan)
- [http://www.ign.fr/](Institut National de l'Informatique Géographique et Forestière)
- [https://www.kartverket.no/](Kartverktet / Norwegian Mapping Authority)

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

