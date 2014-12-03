#! /bin/bash

DATE=`date +%Y-%m-%d`
python manage.py dumpdata catalog feedback news pages shop slideshow auth users --natural > dump_"$DATE".json
git add -A
git commit -a -m "dump ""$DATE"
git push

