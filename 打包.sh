#!/bin/sh
find . -name '*.DS_Store' -type f -delete
dpkg-deb -Zgzip -b a/ /Users/tashigefengzi/Desktop/源文件/
rm -r -f /Users/tashigefengzi/Desktop/github/a.deb





