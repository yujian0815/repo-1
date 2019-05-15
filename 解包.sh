#!/bin/sh
dpkg-deb -x ./deb/a.deb ./a
dpkg-deb -e ./deb/a.deb ./a/DEBIAN




