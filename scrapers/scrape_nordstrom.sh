#!/bin/bash

DAY=`date +%Y_%m_%d`
rm -f out/nordstrom_${DAY}.jsonlines
scrapy crawl nordstrom -o out/nordstrom_${DAY}.jsonlines
