#!/usr/bin/env python
import Image
import sys
import yaml
import os

html_summary = []

def main():
    if not( len(sys.argv) == 2 and os.path.isdir(sys.argv[1]) ):
        print "usage: script testoutputdir"
        return

    allfiles = os.listdir(sys.argv[1])
    outputfiles = [sys.argv[1] + item for item in allfiles if (".tested-with." in item and "yml" == item.split(".")[-1]) ]
    in_filenames = outputfiles

    html_summary.append("<html><body>")

    summary_file = open(sys.argv[1] + "/summary",'r')
    summaries = summary_file.readlines()
    html_summary.append("<p>")

    html_summary.append("</p><p>".join(summaries))

    html_summary.append("</p>")

    html_summary.append("<div style=\"width: 3000px\" ><table>")

    in_filenames_tuples = [ (name.split(".tested-with.")[-1], name) for name in in_filenames ]

    in_filenames_tuples.sort()

    in_filenames = [ name for (key, name) in in_filenames_tuples ]

    for filename in in_filenames:
        create_all_bgdfgd_image(filename)

    #create_all_bgdfgd_image(in_filenames[0])

    
    html_summary.append("</table></div>")
    html_summary.append("</body></html>")

    

    html_file = open(sys.argv[1] + "/summary.html",'w')
    html_file.writelines(html_summary)

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

    fgd_filename = in_filename.split('/')[-1] + '.' + suffix + '.fgd.png'
    bgd_filename = in_filename.split('/')[-1] + '.' + suffix + '.bgd.png'
    html_summary.append("<td><a href=\"%s\"><img src=\"%s\" title=\"%s\"></a></td>" % (fgd_filename, fgd_filename, suffix + " foreground"))
    html_summary.append("<td><a href=\"%s\"><img src=\"%s\" title=\"%s\"></a></td>" % (bgd_filename, bgd_filename, suffix + " background"))


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

    fgd_filename = in_filename.split('/')[-1] + '.' + suffix + '.fgd.png'
    bgd_filename = in_filename.split('/')[-1] + '.' + suffix + '.bgd.png'
    html_summary.append("<td><a href=\"%s\"><img src=\"%s\" title=\"%s\"></a></td>" % (fgd_filename, fgd_filename, suffix + " foreground"))
    html_summary.append("<td><a href=\"%s\"><img src=\"%s\" title=\"%s\"></a></td>" % (bgd_filename, bgd_filename, suffix + " background"))


def create_all_bgdfgd_image(in_filename):
    html_summary.append("<tr>")

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


    html_summary.append("<td width=\"300\">")

    true_positive = yamlfile["true positive"]
    true_negative = yamlfile["true negative"]
    false_positive = yamlfile["false positive"]
    false_negative = yamlfile["false negative"]

    bgd = yamlfile["bgd"]
    fgd = yamlfile["fgd"]
    joint = yamlfile["joint"]

    prob_fgd_KL_sym = yamlfile["prob fgd KL sym"]

    if ".wo-" in in_filename:
        class_number = int( in_filename.split('.')[1] )
        html_summary.append("<p> correct class </p>")

    html_summary.append("<p> joint rate = %s </p>" % joint)
    html_summary.append("<p> prob fgd KL sym = %s </p>" % prob_fgd_KL_sym)

    try:
        msst_prob_fgd_KL_sym = yamlfile["msst prob fgd KL sym"]
        xi = yamlfile["xi"]
        html_summary.append("<p> msst prob fgd KL sym = %s </p>" % msst_prob_fgd_KL_sym)
        html_summary.append("<p> xi = %s </p>" % xi)
    except KeyError:
        pass

    html_summary.append("</td>")

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

    html_summary.append("</tr>\n")


if __name__ == "__main__":
    main()
