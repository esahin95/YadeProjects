#!/bin/bash

# Export particle size distribution
yade -n checkPSD.py

# Extract powder bed
yade -n extractPowderBed.py

# Inspect results
for file in results/*.pdf; do
    [ -f "$file" ] || break
    wslview "$file"
done