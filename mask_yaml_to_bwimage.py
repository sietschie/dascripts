from optparse import OptionParser
import Image
import os.path
import yaml

def main():
    usage = "usage: %prog [options] inputimage"
    parser = OptionParser(usage)
    parser.add_option("-o", "--output", dest="outputfilename",
                      help="write output image to this file instead to standard filename", metavar="FILE")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=True,
                      help="print status messages to stdout")
    (options, args) = parser.parse_args()

    if len(args) != 1 and len(args) != 4:
        parser.error("incorrect number of arguments")

    inputfilename = args[0]

    def mat_constructor(loader, node):
        return loader.construct_mapping(node)

    yaml.CLoader.add_constructor(u'tag:yaml.org,2002:opencv-matrix', mat_constructor)
    yaml.add_constructor(u'tag:yaml.org,2002:opencv-matrix', mat_constructor)


    try:
        stream = open(inputfilename)
    except IOError:
        parser.error("can't open input file \""+ inputfilename +"\"")

    #yamlfile = yaml.load(stream, Loader = yaml.CLoader)
    yamlfile = yaml.load(stream)
    mask = yamlfile['mask']

    im = Image.new("RGB", (mask['cols'], mask['rows']))

    lut = {}
    lut[0] = (0,0,0)
    lut[2] = (85,85,85)
    lut[1] = (170,170,170)
    lut[3] = (255,255,255)

    data = [ lut[x] for x in mask['data']  ]
    
    im.putdata(data)
    


    pixels = im.getdata()

    basename, extension = os.path.splitext(inputfilename)


    if options.outputfilename == None:
        outputfilename = basename + "_refined.bmp"
    else:
        outputfilename = options.outputfilename
        
    try:
        im.save(outputfilename)
    except IOError:
        parser.error("error in writing to \""+ outputfilename +"\"")


    #im.show()


if __name__ == "__main__":
    main()
