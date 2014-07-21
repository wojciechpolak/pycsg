#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  pycsg.py -- Python CSS Sprites Generator.
#  Copyright (C) 2009, 2010, 2011, 2014 Wojciech Polak.
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your
#  option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import glob
import getopt

try:
    from PIL import Image
except ImportError:
    import Image


def csg(args):
    vertical = (not args['horizontal']) or False
    master_name = args['master'] or 'master.png'

    if args.get('filelist'):
        d = os.path.dirname(os.path.abspath(args['filelist']))
        try:
            with open(args['filelist']) as fp:
                args['files'] = [os.path.join(d, line.strip())
                                 for line in fp.readlines() if line.strip()]
        except IOError as e:
            print(e)
            return
    else:
        args['files'].sort()

    if not args['files']:
        print('No input files. Exiting.')
        return

    images = [(Image.open(f), f) for f in args['files']]
    print('Joining %d images.' % len(images))

    master_width, master_height = 0, 0
    for img, filename in images:
        if vertical:
            if img.size[0] > master_width:
                master_width = img.size[0]
            master_height += img.size[1]
        else:
            if img.size[1] > master_height:
                master_height = img.size[1]
            master_width += img.size[0]

    print("The master image will be %dx%d pixels." % (master_width,
                                                      master_height))

    master = Image.new(mode='RGBA', size=(master_width, master_height),
                       color=(0, 0, 0, 0))

    offset = 0
    for data in images:
        image, filename = data
        print("adding %s at %d" % (filename, offset))
        if vertical:
            master.paste(image, (0, offset))
            offset += image.size[1]
        else:
            master.paste(image, (offset, 0))
            offset += image.size[0]

    print('Saving %s' % master_name)
    master.save(master_name)
    print('Final size is %s bytes' % os.path.getsize(master_name))

    if args.get('crush'):
        import subprocess

        name, suffix = master_name.rsplit('.', 1)
        master_crushed = '%s.crushed.%s' % (name, suffix)

        if suffix.lower() == 'png':
            cmd = 'pngcrush -q -reduce -brute -l 9 %s %s' % (master_name,
                                                             master_crushed)
        else:
            print('Unknown crusher for the "%s" file suffix - skipped' % suffix)
            cmd = None

        if cmd:
            print('Crushing master: %s' % cmd)

            p = subprocess.Popen(cmd, shell=True,
                                 stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

            cmd_stdout = p.stdout.read()
            p.stdout.close()

            cmd_stderr = p.stderr.read()
            p.stderr.close()

            if p.wait() != 0:
                if not cmd_stderr:
                    cmd_stderr = 'Unable to crush master image: %s' % cmd

            if cmd_stdout:
                print(cmd_stdout)

            if cmd_stderr:
                print(cmd_stderr)

            print('Crushed size is %s bytes!' % os.path.getsize(master_crushed))


    css_template_v = """.%(filename)s {
  background: transparent url(%(master_name)s) no-repeat 0 %(offset)dpx;
  width: %(width)dpx; height: %(height)dpx;
}
"""
    css_template_h = """.%(filename)s {
  background: transparent url(%(master_name)s) no-repeat %(offset)dpx 0;
  width: %(width)dpx; height: %(height)dpx;
}
"""

    name, suffix = master_name.rsplit('.', 1)
    with open(name + '.css', 'w') as css_file:
        offset = 0
        print('Writing %s' % css_file.name)
        for data in images:
            image, filename = data

            fmt = {
                'filename': os.path.basename(filename),
                'master_name': master_name,
                'offset': 0 - offset,
                'width': image.size[0],
                'height': image.size[1],
            }

            if vertical:
                css_file.write(css_template_v % fmt)
                offset += image.size[1]
            else:
                css_file.write(css_template_h % fmt)
                offset += image.size[0]


def run():
    params = {
        'files': [],
        'horizontal': True,
        'master': None,
        'crush': False,
    }

    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'cf:g:m:',
            [
                'filelist=',
                'glob=',
                'vertical',
                'master=',
                'crush',
            ])
        for o, arg in opts:
            if o in ('-f', '--filelist'):
                arg = os.path.expandvars(arg)
                arg = os.path.expanduser(arg)
                params['filelist'] = arg
            elif o in ('-g', '--glob'):
                params['files'] = glob.glob(arg)
            elif o in ('--vertical',):
                params['horizontal'] = False
            elif o in ('-m', '--master'):
                params['master'] = arg
            elif o in ('-c', '--crush'):
                params['crush'] = True

        if not opts:
            raise getopt.GetoptError(1)

    except getopt.GetoptError:
        print("Usage: %s OPTION..." % sys.argv[0])
        print("""%s -- CSS Sprites Generator

  -f, --filelist=FILENAME  Read input image list from file
  -g, --glob=PATTERN       File pattern like '*.png'
  -m, --master=FILENAME    Master output file name
      --vertical           Use vertically positioned images
  -c, --crush              Crush master image file size
  """ % sys.argv[0])
        sys.exit(0)

    csg(params)


if __name__ == '__main__':
    run()
