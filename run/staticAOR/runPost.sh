#!/bin/bash

# process results
yade -n checkPSD.py
yade -n cleanHeap.py
yade -n fitAngle.py

# Inspect results
for file in results/*.pdf; do
    [ -f "$file" ] || break
    wslview "$file"
done