#!/bin/bash

DAY=`date +%Y_%m_%d`
rm -f out/sephora_${DAY}.jsonlines
scrapy crawl sephora -o out/sephora_${DAY}.jsonlines
