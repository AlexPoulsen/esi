# esi
Extremely Simple Image file format, an image format designed for databending.

Here is a set of pictures demonstrating various databends with the format http://imgur.com/a/P03U5

If you are going to edit it with audacity, U-Law adds colorful artifacts to the image. Use A-Law encoding to prevent any unwanted image artifacts.

ESI has a minimal header of only 12 bytes, or 12 samples in audacity with typical settings. the last 5 are ignored so you can start your effect at the start of the image and not worry if you messed with a header byte. Furthermore, the color bit depth setting is currently unimplemented (it only works in 8bit rgb), so that byte is also not important. This means there is only 6 important bytes to preserve during editing.
