#!/bin/bash

# remove results
rm -r results >/dev/null 2>&1

# run simulation
yade -n -j 8 staticAOR.py