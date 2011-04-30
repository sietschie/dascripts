#!/usr/bin/env python
import sys
import yaml
import os.path
import os
import copy
import subprocess
import datetime
import time
import csv

image_directories = {}
image_directories['MSCR'] = "/home/goering/data/images/MSRC_v2/Images/"
image_directories['VOC'] = "/home/goering/data/images/VOC2010/SegmentationClass/"


def main():
    if( len(sys.argv) < 4 ):
        print "not enough arguments: binary_dir output_dir output_suffix image_list1 [image_list2 ...]"
        exit() #todo: output some helpful information?

    binary_directory = sys.argv[1]
    global output_directory 
    timestring = str(datetime.datetime.now()).replace(" ","-").replace(".","-").replace(":","-")
    output_directory = sys.argv[2] + "/" + os.path.basename(binary_directory.strip('/')) + "-" + sys.argv[3]+ "-" + timestring
    os.mkdir(output_directory)

    list_of_imagelists = sys.argv[4:]

    print "binary_dir:", binary_directory
    print "output_dir:", output_directory
    print "list_of_imagelists:", list_of_imagelists

    global binary_learn
    binary_learn = binary_directory + "/learn.bin"
    global binary_test
    binary_test = binary_directory + "/test.bin"
    global binary_test_options
    binary_test_options = ["-m","10"]

    build_directory = '/'.join( binary_directory.rstrip('/').split('/')[:-1] )
    global binary_shape
    binary_shape = build_directory + "/shapes/shape.bin"
	#binary_test_options = []

    global logfile
    logfile = open(output_directory + "/log","a",1)
    logfile.write(str( sys.argv ) + "\n")
    logfile.write(" ".join(sys.argv))
    logfile.write("\n\n")

    fieldnames = [ 
        "image name", 
        "image class", 
        "model", 
        "model class",
        'true negative',
        'true positive',
        'false negative',
        'false positive',
        'unknown',
        'bgd',
        'fgd',
        'joint',
        'fgd KL input result',
        'fgd KL result input',
        'fgd KL sym',
        'bgd KL input result',
        'bgd KL result input',
        'bgd KL sym', 
        'prob fgd KL input result',
        'prob fgd KL result input',
        'prob fgd KL sym',
        'prob bgd KL input result',
        'prob bgd KL result input',
        'prob bgd KL sym', 
        'msst fgd KL input result',
        'msst fgd KL result input',
        'msst fgd KL sym',
        'msst bgd KL input result',
        'msst bgd KL result input',
        'msst bgd KL sym', 
        'msst prob fgd KL input result',
        'msst prob fgd KL result input',
        'msst prob fgd KL sym',
        'msst prob bgd KL input result',
        'msst prob bgd KL result input',
        'msst prob bgd KL sym', 
        'xi',
        'ownclass',
		'prob humoments'
    ]

    # prepare file to output results
    global resultsfile
    resultsfile = csv.DictWriter(open(output_directory + "/results","a",1), fieldnames)
    resultsfile.writerow(dict(zip(fieldnames, fieldnames)))

    # read imagelist from files
    imagelists = []
    for imagelist in list_of_imagelists:
        il = {}
        directory, filename = os.path.split(imagelist)
        il['classnumber'] = int(filename.split(".")[-2])
        il['image_dir'] = image_directories[filename.split(".")[-3]]
        il['filename'] = filename
        il['directory'] = directory

        f = open(imagelist)
        l  = []
        for line in f:
            l.append(line.strip())

        il['list'] = l

        imagelists.append(il)

    # precompute models for the complete lists
    for imagelist in imagelists:
        compute_model(imagelist, ".all" )

    # process imagelist
    for imagelist in imagelists:
        for image in imagelist['list']:
            validate(imagelists, image, imagelist['classnumber'])

    # after crossvalidating with all images, run some scripts

    # compute some general statistics
    scriptpath = os.path.abspath(sys.argv[0])
    statisticspath = os.path.dirname(scriptpath) + "/compute_statistics.py"
    args = [ statisticspath, output_directory + "/results"]
    print " ".join(args)
    p = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    p.wait()
    (output, error) = p.communicate()
    print "output: ", output
    f = open(output_directory + "/summary", "w")
    f.write(output)
    #f.write("\n\n ERRORS:\n")
    #f.write(error)

    # generate html file
    visualizepath = os.path.dirname(scriptpath) + "/visualize.test-output.summary.py"
    args = [ visualizepath, output_directory + "/"]
    print " ".join(args)
    p = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    p.wait()
    (output, error) = p.communicate()
    print "output: ", output
    print "error: ", error



def compute_model(imagelist, suffix ):

    # prepare parameters
    outputstring = output_directory + "/model." + str(imagelist['classnumber']) + suffix + ".yml"
    imagesstrings = [ imagelist['directory'] + "/" + elem for elem in imagelist['list']]

    args = [ binary_learn ]
    args.extend( [ outputstring, str(imagelist['classnumber']) ])
    args.extend( imagesstrings )

    # write parameters to logfile and stdout
    logfile.write( " ".join(args) + "\n" )
    print " ".join(args)
    start_time = time.time()
    p = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    p.wait()
    end_time = time.time()
    print "running_time: ", end_time - start_time
    (output, error) = p.communicate()
    print "output: ", output
    #print "error: ", error

    logfile.write( "running_time: " + str(end_time - start_time) + "\n" )
    logfile.write(output)
    logfile.write(error)
    logfile.write("\n")

    return outputstring


def validateImage( validation_image, image_directory, outputstring, validation_class ):
    outputfile = outputstring + ".tested-with." + validation_image + ".yml"
    args_test = [binary_test, outputstring, str(validation_class), image_directory + "/" + validation_image, outputfile]
    args_test.extend(binary_test_options)


    print " ".join(args_test)
    logfile.write( " ".join(args_test) + "\n" )
    start_time = time.time()
    p = subprocess.Popen(args_test, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    p.wait()
    end_time = time.time()
    print "running_time: ", end_time - start_time
    (output, error) = p.communicate()
    print "output: ", output
    print "error: ", error
    lines = output.split("\n")[-3:-1]
    output_var = {}

    logfile.write( "running_time: " + str(end_time - start_time) + "\n" )
    logfile.write(output)
    logfile.write(error)
    logfile.write("\n")

    for l in lines:
        print "line: ", l
        for arg in l.strip().split(','):
            print "[", arg, "]"
            name = arg.split(":")[0].strip()
            value = arg.split(":")[1].strip()
            output_var[name] = value

    return (output_var, outputfile)


def validate(imagelists, validation_image, validation_class):
    for imagelist in imagelists:
        suffix = ""
        output_var = {}
        outputfile = ""
        ownclass = 0
        if validation_class != imagelist['classnumber']:
            suffix = ".all"
            modelfile = output_directory + "/model." + str(imagelist['classnumber']) + suffix + ".yml"

            (output_var, outputfile) = validateImage( validation_image, imagelist['directory'], modelfile, validation_class )
        else:
            print "remove image: ", validation_image
            tmp_imagelist = copy.deepcopy( imagelist )
            tmp_imagelist['list'].remove(validation_image)

            ownclass = 1
            suffix = ".wo-%s"%".".join(validation_image.split(".")[0:-1])
            modelfile = compute_model(tmp_imagelist, suffix )
            (output_var, outputfile) = validateImage( validation_image, imagelist['directory'], modelfile, validation_class )
            
        output_var["image name"] = validation_image
        output_var["image class"] = validation_class 
        output_var["model"] = suffix
        output_var["model class"] = imagelist['classnumber']
        output_var["ownclass"] = ownclass

        args = [binary_shape, outputfile]
        print " ".join(args)
        p = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        p.wait()
        (output, error) = p.communicate()
        print "output: ", output
        print "error: ", error

        lastline = output.split('\n')[-2]
        print lastline
        name = lastline.split(":")[0].strip()
        value = lastline.split(":")[1].strip()
        print name, ": ", value
        output_var[ name] = value

        print "output: ", output_var
        logfile.write(str(output_var) + "\n")
        logfile.write("\n\n")

        resultsfile.writerow(output_var)


if __name__ == "__main__":
    main()
