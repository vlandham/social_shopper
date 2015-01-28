#!/bin/bash

DAY=`date +%Y_%m_%d`
rm -f out/macys_${DAY}.jsonlines
scrapy crawl macys -o out/macys_${DAY}.jsonlines
