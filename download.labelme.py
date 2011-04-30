import lxml
import lxml.html
import urllib
import urlparse 
import cgi
import yaml
import os.path


def dataToYaml(dt, data, out_filename, class_name, filename, foldername):
    class Matrix(yaml.YAMLObject):
	yaml_tag = u'!opencv-matrix'
	def __init__(self, rows, cols, dt, data):
	    self.rows = rows
	    self.cols = cols
	    self.dt = dt
	    self.data = data
	def __repr__(self):
	    return "%s(rows=%r, cols=%r, dt=%r, data=%r)" (self.__class__.__name__, self.rows, self.cols, self.dt, self.data)

    obj = {}
    obj['class_name'] = class_name
    obj['image_name'] = filename + " "
    obj['folder_name'] = foldername

    list_of_mat = []

    for elem in data:
	mat = Matrix(len(elem) / 2, 2, dt, elem)
	list_of_mat.append(mat)

    obj['outlines'] = list_of_mat


    #print yaml.dump(obj).replace("!opencv-matrix", "!!opencv-matrix")

    dump_stream = yaml.dump(obj, Dumper=yaml.CDumper)
    #print "finished dumping.."

    dump_stream_fixed = dump_stream.replace("!opencv-matrix", "!!opencv-matrix").replace("!!python/object:__main__.Matrix", "!!opencv-matrix")
    dump_stream_fixed = dump_stream_fixed.replace("- !!opencv-matrix", " - !!opencv-matrix")
    #print "finished fixing.."

    output = open(out_filename,"w")
    output.write("%YAML 1.0\n---\n")
    output.write(dump_stream_fixed)
    #print "finished writing.. ", out_filename


def main():
    labelmeurl = "http://people.csail.mit.edu/torralba/research/LabelMe/js/LabelMeQueryObjectFast.cgi"

    searchstring = "head"

    w = urllib.urlopen(labelmeurl + "?query=" + searchstring )

    #print "\n".join( w.readlines() )

    wparsed = lxml.html.fromstring("".join(w.readlines() ) )

    for element in wparsed.iter("a"):
    #for element in range(1):
	#print("%s - %s" % (element.tag, element.text))
	#print lxml.html.tostring( element )
	labelimageurl = element.attrib["href"]

	#labelimageurl = "http://labelme.csail.mit.edu/tool.html?collection=LabelMe&folder=sep1_seq4_bldg400_outdoor&image=00006.jpg"

	if "http://labelme.csail.mit.edu/tool.html?collection=LabelMe&" in labelimageurl:
	    params = cgi.parse_qs(urlparse.urlsplit(labelimageurl).query)
	    
	    folder = params['folder'][0]
	    imagename = params['image'][0]

	    imageurl = "http://labelme.csail.mit.edu/Images/" + folder + "/" + imagename 
	    annotationurl = "http://labelme.csail.mit.edu/Annotations/" + folder + "/" + imagename.replace('jpg','xml')

	    wannotation = urllib.urlopen( annotationurl )

	    wannotationparsed = lxml.html.fromstring("".join(wannotation.readlines() ) )

	    print imagename

	    list_of_list_of_points = []

	    for elem in wannotationparsed.iter("object"):
		#print elem[0].tag, elem[0].text
		tags = {}
		for child in elem:
		    #print child.tag, child.text
		    tags[child.tag] = child.text


		#print "tag = \"%s\"" % tags['name']
		
                print 'name: ', repr(tags['name']), '   deleted: ', repr(tags['deleted'])
		if tags['name'] != None and searchstring in tags['name'].strip() and tags['deleted'].strip() == '0':
		    print 'found object...', tags['name']
		    
		    list_of_points = []

		    for point in elem.iter("pt"):
			#print lxml.etree.tostring(point)
			#print point[0].text, point[1].text
			list_of_points.append( int( point[0].text ) )
			list_of_points.append( int( point[1].text ) )

		    list_of_list_of_points.append( list_of_points )

		    #since an object was found, save image and data to file

	    if os.path.isfile(imagename):
		print "file %s already exists.. " % imagename
		print "imageurl = ", imageurl
		continue
		    

	    dataToYaml('i', list_of_list_of_points, imagename + ".contour.yml", searchstring, imagename, folder)

		

	    wimage = urllib.urlopen( imageurl )
	    fimage = open( imagename, 'w' )
	    fimage.write( wimage.read() )

	    wimage.close()
	    fimage.close()

	    wxml = urllib.urlopen( annotationurl )
	    fxml = open( imagename.replace('jpg','xml'), 'w' )
	    fxml.write( wxml.read() )

	    wxml.close()
	    fxml.close()
	    
	    #for elem in wannotationparsed:
		#print elem.tag, elem.text


	    #print "".join(wannotation.readlines())
	    



if __name__ == "__main__":
    main()




