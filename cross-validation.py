#!/usr/bin/env python
import sys
import yaml
import os.path
import copy
import subprocess
import datetime
import time
import csv

image_directories = {}
image_directories['MSCR'] = "/home/goering/data/images/MSRC_v2/Images/"
image_directories['VOC'] = "/home/goering/data/images/VOC2010/SegmentationClass/"


def main():
    if( len(sys.argv) < 3 ):
        print "not enough arguments: binary_dir output_dir image_list1 [image_list2 ...]"
        exit() #todo: output some helpful information?

    binary_directory = sys.argv[1]
    global output_directory 
    output_directory = sys.argv[2] + "/" + os.path.basename(binary_directory.strip('/')) + "-" + str(datetime.datetime.now()).replace(" ","-").replace(".","-").replace(":","-")
    os.mkdir(output_directory)

    list_of_imagelists = sys.argv[3:]

    print "binary_dir:", binary_directory
    print "output_dir:", output_directory
    print "list_of_imagelists:", list_of_imagelists

    global binary_learn
    binary_learn = binary_directory + "/learn.bin"
    global binary_test
    binary_test = binary_directory + "/test.bin"
    global binary_test_options
    binary_test_options = ["-m","2"]

    global logfile
    logfile = open(output_directory + "/log","a",1)
    logfile.write(str( sys.argv ) + "\n")
    logfile.write(" ".join(sys.argv))

    global resultsfile
    resultsfile = csv.writer(open(output_directory + "/results","a",1))

    resultsfile.writerow([ 
        "image name", 
        "image class", 
        "model", 
        "model class",
        'true negative',
        'true positive',
        'false negative',
        'false positive',
        'unknown pixels',
        'bgd',
        'fgd',
        'joint',
        'fgd KL input result',
        'fgd KL result input',
        'fgd KL sym',
        'bgd KL input result',
        'bgd KL result input',
        'bgd KL sym', 
        'ownclass'
    ])

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


    #for imagelist in imagelists:
    #    print imagelist
    #    for image in imagelist['list']:
    #        print image


    #print imagelists

    #validate(imagelists, imagelists[0]['list'][0], imagelists[0]['classnumber'])

    for imagelist in imagelists:
        for image in imagelist['list']:
            validate(imagelists, image, imagelist['classnumber'])

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

def compute_model(imagelist, suffix, validation_image, validation_class, ownclass):
    #print
    #print "suffix: ", suffix
    #print "compute model: ", imagelist
    #print
    #print

    outputstring = output_directory + "/model." + str(imagelist['classnumber']) + suffix + ".yml"
    imagesstrings = [ imagelist['directory'] + "/" + elem for elem in imagelist['list']]
    args = [ binary_learn ]
    args.extend( [ outputstring, str(imagelist['classnumber']) ])
    args.extend( imagesstrings )

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


    args_test = [binary_test, outputstring, str(validation_class), imagelist['directory'] + "/" + validation_image, outputstring + validation_image + ".yml"]
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
    print "output: ", output_var
    print "error: ", error
    logfile.write(str(output_var) + "\n")
    logfile.write("\n\n")

    resultsfile.writerow([ 
        validation_image, 
        validation_class, 
        suffix, 
        imagelist['classnumber'],
        output_var['true negative'],
        output_var['true positive'],
        output_var['false negative'],
        output_var['false positive'],
        output_var['unknown'],
        output_var['bgd'],
        output_var['fgd'],
        output_var['joint'],
        output_var['fgd KL input result'],
        output_var['fgd KL result input'],
        output_var['fgd KL sym'],
        output_var['bgd KL input result'],
        output_var['bgd KL result input'],
        output_var['bgd KL sym'],
        ownclass
    ])


def validate(imagelists, validation_image, validation_class):
    for imagelist in imagelists:
        if validation_class != imagelist['classnumber']:
            compute_model(imagelist, ".all", validation_image, validation_class, 0)
        else:
            print "remove image: ", validation_image
            tmp_imagelist = copy.deepcopy( imagelist )
            tmp_imagelist['list'].remove(validation_image)
            compute_model(tmp_imagelist,".wo-%s"%".".join(validation_image.split(".")[0:-1]), validation_image, validation_class, 1)
            
if __name__ == "__main__":
    main()
