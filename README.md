# geonames-wordnet
Code to generate wordnets from the [GeoNames geographical database](https://www.geonames.org/).

It uses mappings developed by the Geo-Wordnet, GeoWordnet and CILI projects.

You first need to download and uncompress the GeoNames data.  These are big files (300+MB
and 150+MB respectively compressed).

```bash
# get WN data
pushd gndata
wget http://download.geonames.org/export/dump/allCountries.zip	
wget http://download.geonames.org/export/dump/alternateNamesV2.zip
unzip allCountries.zip	
unzip alternateNamesV2.zip
popd
```

Mappings

Filename | Source | Description
-------------------------------
geo_domain_wordnet_eng.tsv|GeoDomainsWordNet|supertype information
GeoNamesFeatures.tsv|GeoNames-Wordnet|enhanced supertype information
GeoWN_3.1.dat.txt|Geo-WordNet|Mapping of locations to PWN synsets

# ToDo


Describe the mappings
