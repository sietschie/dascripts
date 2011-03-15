#!/usr/bin/env python
import Image
import sys
import yaml

im_filename = sys.argv[1]

if len(sys.argv) < 3:
    out_filename = sys.argv[1].replace("png","jpg") + ".yml"
else:
    out_filename = sys.argv[2]

im = Image.open(im_filename)

pixels = im.getdata()

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

mat = Matrix(rows,cols,'u', list(pixels))
obj = {}
obj['mask'] = mat

dump_stream = yaml.dump(obj, Dumper=yaml.CDumper)
print "finished dumping.."

dump_stream_fixed = dump_stream.replace("!opencv-matrix", "!!opencv-matrix").replace("!!python/object:__main__.Matrix", "!!opencv-matrix")

print "finished fixing.."

output = open(out_filename,"w")
output.write("%YAML 1.0\n---\n")
output.write(dump_stream_fixed)
print "finished writing.. ", out_filename
