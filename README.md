pycsg.py -- Python CSS Sprites Generator.
Copyright (C) 2009, 2010, 2011, 2014 Wojciech Polak.

Requirements
============

- Python
- Pillow or PIL
- pngcrush for PNG files when using `--crush` option.

Usage
=====

```
Usage: ./pycsg.py OPTION...
./pycsg.py -- CSS Sprites Generator

  -f, --filelist=FILENAME  Read input image list from file
  -g, --glob=PATTERN       File pattern like '*.png'
  -m, --master=FILENAME    Master output file name
      --vertical           Use vertically positioned images
  -c, --crush              Crush master image file size
```

Example usage:

```
$ ./pycsg.py --glob '*.png' --master master.png

$ ./pycsg.py --filelist input_files.csg --master master.png --crush
```

where `input_files.csg` contains file names in the specific processing
order, for example:

	file3.png
	file2.png
	file1.png
