# Projects Overview
## Simple Gravity Deposition

## Funnel Test


# Notes

A simple way to generate animations is by using a combination of VTKRecorder
to generate files for visualization in Paraview and generating a list of
images. These can be transformed into an animation by using ffmpeg e.g.

ffmpeg -framerate 10 -i results/tmp/anim.%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p results/animation.mp4

When using the command like this, images must have even pixel (due to yuv420p).
Framerate should be adjusted depending on the number of images generated.