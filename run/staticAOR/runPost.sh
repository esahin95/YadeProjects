#!/bin/bash

# Inspect results
for file in results/*.pdf; do
    [ -f "$file" ] || break
    wslview "$file"
done