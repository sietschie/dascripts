#!/usr/bin/env python
import Image
import sys
import yaml

classes_list = [['void', 0, 0, 0], ['building', 128, 0, 0], ['grass', 0, 128, 0], ['tree', 128, 128, 0], ['cow', 0, 0, 128], ['horse', 128, 0, 128], ['sheep', 0, 128, 128], ['sky', 128, 128, 128], ['mountain', 64, 0, 0], ['aeroplane', 192, 0, 0], ['water', 64, 128, 0], ['face', 192, 128, 0], ['car', 64, 0, 128], ['bicycle', 192, 0, 128], ['flower', 64, 128, 128], ['sign', 192, 128, 128], ['bird', 0, 64, 0], ['book', 128, 64, 0], ['chair', 0, 192, 0], ['road', 128, 64, 128], ['cat', 0, 192, 128], ['dog', 128, 192, 128], ['body', 64, 64, 0], ['boat', 192, 64, 0]]

class_names = dict([ (index, elem[0]) for index, elem in enumerate(classes_list)])

classes = dict([ ((elem[1],elem[2],elem[3]), index) for index,elem in enumerate(classes_list) ])

#print classes
print class_names

im_filename = sys.argv[1]

if len(sys.argv) < 3:
    out_filename = sys.argv[1].replace("_GT","") + ".yml"
else:
    out_filename = sys.argv[2]

im = Image.open(im_filename)

pixels = im.getdata()

print "start converting... ", im_filename

outputlist = []
for i in xrange(len(pixels)):
    outputlist.append( classes[pixels[i]] )

print "finished converting..."



class Matrix(yaml.YAMLObject):
    yaml_tag = u'!opencv-matrix'
    def __init__(self, rows, cols, dt, data):
        self.rows = rows
        self.cols = cols
        self.dt = dt
        self.data = data
    def __repr__(self):
        return "%s(rows=%r, cols=%r, dt=%r, data=%r)" (self.__class__.__name__, self.rows, self.cols, self.dt, self.data)

(cols, rows) = im.size

mat = Matrix(rows,cols,'u', outputlist)
obj = {}
obj['mask'] = mat


#print yaml.dump(obj).replace("!opencv-matrix", "!!opencv-matrix")

dump_stream = yaml.dump(obj, Dumper=yaml.CDumper)
print "finished dumping.."

dump_stream_fixed = dump_stream.replace("!opencv-matrix", "!!opencv-matrix").replace("!!python/object:__main__.Matrix", "!!opencv-matrix")
print "finished fixing.."

output = open(out_filename,"w")
output.write("%YAML 1.0\n---\n")
output.write(dump_stream_fixed)
print "finished writing.. ", out_filename
