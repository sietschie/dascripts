#!/usr/bin/env python
import Image
import sys
import yaml
import os

def main():
    if len(sys.argv) < 2:
        print "usage: script testoutput1.yml testoutput2.yml ..."
        print "or  script testoutputdir"
        return

    if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
            allfiles = os.listdir(sys.argv[1])
            outputfiles = [sys.argv[1] + item for item in allfiles if ".tested-with." in item]
            #print "THE INPUT IS A DIRECTORY", outputfiles
            in_filenames = outputfiles
    else:
        in_filenames = sys.argv[1:]


    for filename in in_filenames:
        create_all_bgdfgd_image(filename)

def create_bgdfgd_image(in_filename, input_image, mask, suffix):
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
            

    output_fgd.save(in_filename + '.' + suffix + '.fgd.png')
    output_bgd.save(in_filename + '.' + suffix + '.bgd.png')


def create_bgdfgd_image_multiclass(in_filename, input_image, mask, suffix, class_number):
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
            

    output_fgd.save(in_filename + '.' + suffix + '.fgd.png')
    output_bgd.save(in_filename + '.' + suffix + '.bgd.png')

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

    input_image_filename = yamlfile['input_image']
    input_image = Image.open(input_image_filename)

    mask = yamlfile['mask']
    create_bgdfgd_image(in_filename, input_image, mask, 'mask')

    initial_mask = yamlfile['initial_mask']
    create_bgdfgd_image(in_filename, input_image, initial_mask, 'initial_mask')

    try:
        initial_mask = yamlfile['initial_mask_color']
        create_bgdfgd_image(in_filename, input_image, initial_mask, 'initial_mask_color')
    except KeyError:
        pass

    try:
        initial_mask = yamlfile['initial_mask_msst']
        create_bgdfgd_image(in_filename, input_image, initial_mask, 'initial_mask_msst')
    except KeyError:
        pass

    gt_mask_filename = input_image_filename + ".yml"

    try:
        stream = open(gt_mask_filename)
    except IOError:
        parser.error("can't open input file \""+ gt_mask_filename +"\"")


    if ".wo-" in in_filename:
        class_number = int( in_filename.split('.')[1] )

        yamlfile = yaml.load(stream)
        mask = yamlfile['mask']
        create_bgdfgd_image_multiclass(in_filename, input_image, mask, 'gt_mask', class_number)

if __name__ == "__main__":
    main()
