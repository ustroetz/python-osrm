#!/bin/sh
# script largely inspired by gdal install script of rasterio python package:
#  https://github.com/mapbox/rasterio/blob/master/scripts/travis_gdal_install.sh

set -ex

GDALOPTS="  --with-ogr \
            --with-geos \
            --with-expat \
            --without-libtool \
            --without-gif \
            --without-pg \
            --without-grass \
            --without-libgrass \
            --without-cfitsio \
            --without-pcraster \
            --without-netcdf \
            --without-gif \
            --without-ogdi \
            --without-fme \
            --without-hdf4 \
            --with-spatialite
            --with-static-proj4=/usr/lib"

# Create build dir if not exists
if [ ! -d "$GDALBUILD" ]; then
  mkdir $GDALBUILD;
fi

if [ ! -d "$GDALINST" ]; then
  mkdir $GDALINST;
fi

if [ ! -d $GDALINST/gdal-2.1.0 ]; then
  cd $GDALBUILD
  wget http://download.osgeo.org/gdal/2.1.0/gdal-2.1.0.tar.gz
  tar -xzf gdal-2.1.0.tar.gz
  cd gdal-2.1.0
  ./configure --prefix=$GDALINST/gdal-2.1.0 $GDALOPTS
  make -s -j 2
  make install
fi
# change back to travis build dir
cd $TRAVIS_BUILD_DIR
