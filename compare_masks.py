from optparse import OptionParser
import yaml

def main():
    usage = "usage: %prog mask gtmask"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("incorrect number of arguments")

    filename = args[0]
    gtfilename = args[1]

    def mat_constructor(loader, node):
        return loader.construct_mapping(node)

    yaml.CLoader.add_constructor(u'tag:yaml.org,2002:opencv-matrix', mat_constructor)
    yaml.add_constructor(u'tag:yaml.org,2002:opencv-matrix', mat_constructor)


    try:
        stream = open(filename)
    except IOError:
        parser.error("can't open input file \""+ filename +"\"")

    yamlfile = yaml.load(stream, Loader = yaml.CLoader)
    #yamlfile = yaml.load(stream)
    mask = yamlfile['mask']

    try:
        stream = open(gtfilename)
    except IOError:
        parser.error("can't open input file \""+ gtfillename +"\"")

    yamlfile = yaml.load(stream, Loader = yaml.CLoader)
    #yamlfile = yaml.load(stream)
    gtmask = yamlfile['mask']

    if mask['cols'] != gtmask['cols'] or mask['rows'] != gtmask['rows']:
        parser.error("image size is not identical")

    count_correct = 0
    count_wrongforeground = 0
    count_wrongbackground = 0

    for i in xrange(mask['cols'] * mask['rows']):
        value = mask['data'][i]
        gtvalue = gtmask['data'][i]
        if (value & 1) == (gtvalue & 1):
            count_correct += 1
        elif (gtvalue & 1) == 0:
            count_wrongbackground += 1
        else:
            count_wrongforeground += 1

    correct = count_correct / float( mask['rows'] * mask['cols'] )
    wrongforeground = count_wrongforeground / float( mask['rows'] * mask['cols'] )
    wrongbackground = count_wrongbackground / float( mask['rows'] * mask['cols'] )
            
    print "correct: %f,   wrongly classified foreground pixels: %f,   wrongly classified background pixels: %f" % (correct, wrongforeground, wrongbackground)


if __name__ == "__main__":
    main()
