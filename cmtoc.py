from optparse import OptionParser
import Image
import os.path

def parseRGBValue(string, parser):
    try:
        v = int(string)
    except ValueError:
        parser.error("RGB values have to integers, but \""+ string +"\" is not.")
    return v

def main():
    usage = "usage: %prog [options] inputimage [r g b]"
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

    try:
        im = Image.open(inputfilename)
    except IOError:
        parser.error("can't open input file \""+ inputfilename +"\"")

    pixels = im.getdata()

    if len(args) != 4:
        values = []
        for p in pixels:
            if not p in values:
                values.append(p)
        for i in range(len(values)):
            print i, ": ", values[i]
        
        inp = raw_input("Which RGB value is the relevant class: ")
        if inp == 'q':
            quit()

        try:
            v_index = int(inp)
        except ValueError:
            print inp, "is not an integer"
            quit()

        if v_index >= len(values):
            print "integer not in range"
            quit()

        r = values[v_index][0]
        g = values[v_index][1]
        b = values[v_index][2]
        
                
    else:
        r = parseRGBValue(args[1], parser)
        g = parseRGBValue(args[2], parser)
        b = parseRGBValue(args[3], parser)

    white = (255,255,255)
    black = (0,0,0)

    outputlist = []
    for i in xrange(len(pixels)):
        if pixels[i] == (r,g,b):
            outputlist.append(white)
        else:
            outputlist.append(black)


    #print outputlist

    im.putdata(outputlist)

    basename, extension = os.path.splitext(inputfilename)


    if options.outputfilename == None:
        outputfilename = basename + "_oneclass" + extension
    else:
        outputfilename = options.outputfilename
        
    try:
        im.save(outputfilename)
    except IOError:
        parser.error("error in writing to \""+ outputfilename +"\"")


    #im.show()


if __name__ == "__main__":
    main()
