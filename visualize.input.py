#!/usr/bin/env python
import Image
import sys
import yaml

def main():
    if len(sys.argv) < 2:
        print "usage: script input1.bmp.yml input2.bmp.yml ..."
        return

    in_filenames = sys.argv[1:]

    for filename in in_filenames:
        create_all_bgdfgd_image(filename)

def create_bgdfgd_image(in_filename, input_image, mask):
    output_fgd = Image.new("RGB", (mask['cols'], mask['rows']))
    output_bgd = Image.new("RGB", (mask['cols'], mask['rows']))

    rows = mask['rows']
    cols = mask['cols']

    for x in range(0, cols-1):
        for y in range(0, rows-1):
            mask_value = mask['data'][y * cols + x]

            pixel_value = input_image.getpixel((x,y))
            if mask_value % 2 == 1: #fgd
                output_fgd.putpixel((x,y), pixel_value)
                output_bgd.putpixel((x,y), (255,0,255))
            else: #bgd
                output_bgd.putpixel((x,y), pixel_value)
                output_fgd.putpixel((x,y), (255,0,255))
            

    output_fgd.save(in_filename + '.fgd.png')
    output_bgd.save(in_filename + '.bgd.png')


def create_bgdfgd_image_multiclass(in_filename, input_image, mask, class_number):
    output_fgd = Image.new("RGB", (mask['cols'], mask['rows']))
    output_bgd = Image.new("RGB", (mask['cols'], mask['rows']))

    rows = mask['rows']
    cols = mask['cols']

    for x in range(0, cols-1):
        for y in range(0, rows-1):
            mask_value = mask['data'][y * cols + x]

            pixel_value = input_image.getpixel((x,y))
            if mask_value  == class_number: #fgd
                output_fgd.putpixel((x,y), pixel_value)
                output_bgd.putpixel((x,y), (255,0,255))
            else: #bgd
                output_bgd.putpixel((x,y), pixel_value)
                output_fgd.putpixel((x,y), (255,0,255))
            

    output_fgd.save(in_filename + '.fgd.png')
    output_bgd.save(in_filename + '.bgd.png')

def create_all_bgdfgd_image(in_filename):
    print in_filename

    def mat_constructor(loader, node):
        return loader.construct_mapping(node)

    yaml.CLoader.add_constructor(u'tag:yaml.org,2002:opencv-matrix', mat_constructor)
    yaml.add_constructor(u'tag:yaml.org,2002:opencv-matrix', mat_constructor)


    try:
        stream = open(in_filename)
    except IOError:
        parser.error("can't open input file \""+ in_filename +"\"")

    yamlfile = yaml.load(stream)

    input_image_filename = '.'.join(in_filename.split('.')[0:-1])
    input_image = Image.open(input_image_filename)

    mask = yamlfile['mask']
    create_bgdfgd_image_multiclass(in_filename, input_image, mask, 11)


if __name__ == "__main__":
    main()
