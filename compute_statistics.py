#!/usr/bin/env python
import sys
import csv
import math

def main():
    print sys.argv[0]

    filename = sys.argv[1]
    datafile = csv.DictReader(open(filename,"r"))

    data = []

    for l in datafile:
        data.append(l)

    image_classes = []
    joint_rates = []
    per_class_joint_rates = []
    for l in data:
        if l['model class'] == l['image class']:
            joint_rates.append(  float(l['joint']))
            per_class_joint_rates.append( ( l['image class'], float(l['joint'])))
        if l['image class'] not in image_classes:
            image_classes.append(l['image class'])

        l['prob fgd KL sym x humoments'] = float(l['prob fgd KL sym']) * float(l['prob humoments'])
        l['prob fgd KL sym + humoments'] = float(l['prob fgd KL sym']) + float(l['prob humoments'])
        for factor in [ float(pow(10,x)) for x in range(20,35,5)]:
            l['prob fgd KL sym + %f humoments' % factor] = float(l['prob fgd KL sym']) + factor * float(l['prob humoments'])
             

    #print joint_rates

    print 'mean joint probability: ', sum(joint_rates) / len(joint_rates)
    for rel_class in image_classes:
	one_class_joint_rates = [ prob for (cur_class, prob) in per_class_joint_rates if cur_class == rel_class ]
	print 'mean joint probability class %s: ' % rel_class, sum(one_class_joint_rates) / len(one_class_joint_rates)

    correct_class = [float(elem['ownclass']) for elem in data]
    fgd_sym_class = [float(elem['fgd KL sym']) for elem in data]
    fgd_ir_class = [float(elem['fgd KL input result']) for elem in data]
    fgd_ri_class = [float(elem['fgd KL result input']) for elem in data]
    bgd_sym_class = [float(elem['bgd KL sym']) for elem in data]
    bgd_ir_class = [float(elem['bgd KL input result']) for elem in data]
    bgd_ri_class = [float(elem['bgd KL result input']) for elem in data]
    
    #print "correlation fgd KL sym: ", correlation(correct_class, fgd_sym_class) 
    #print "correlation fgd KL ir: ", correlation(correct_class, fgd_ir_class) 
    #print "correlation fgd KL ri: ", correlation(correct_class, fgd_ri_class) 
    #print "correlation bgd KL sym: ", correlation(correct_class, bgd_sym_class) 
    #print "correlation bgd KL ir: ", correlation(correct_class, bgd_ir_class) 
    #print "correlation bgd KL ri: ", correlation(correct_class, bgd_ri_class) 


    prob_fgd_sym_class = [float(elem['prob fgd KL sym']) for elem in data]
    prob_fgd_ir_class = [float(elem['prob fgd KL input result']) for elem in data]
    prob_fgd_ri_class = [float(elem['prob fgd KL result input']) for elem in data]
    prob_bgd_sym_class = [float(elem['prob bgd KL sym']) for elem in data]
    prob_bgd_ir_class = [float(elem['prob bgd KL input result']) for elem in data]
    prob_bgd_ri_class = [float(elem['prob bgd KL result input']) for elem in data]
    
    #print "correlation prob fgd KL sym: ", correlation(correct_class, prob_fgd_sym_class) 
    #print "correlation prob fgd KL ir: ", correlation(correct_class, prob_fgd_ir_class) 
    #print "correlation prob fgd KL ri: ", correlation(correct_class, prob_fgd_ri_class) 
    #print "correlation prob bgd KL sym: ", correlation(correct_class, prob_bgd_sym_class) 
    #print "correlation prob bgd KL ir: ", correlation(correct_class, prob_bgd_ir_class) 
    #print "correlation prob bgd KL ri: ", correlation(correct_class, prob_bgd_ri_class) 


    list_by_images = {}

    for elem in data:
        im = elem['image name']
        if not im in list_by_images.keys():
            list_by_images[im] = []
        list_by_images[im].append(elem)

    relevant_keys = [ elem for elem in data[0].keys() if "prob" in elem ]
    #relevant_keys = ['prob fgd KL sym']

    multiclass_results = {}
    for key in relevant_keys:
        multiclass_results[key] = []
        for elem in list_by_images:
            #print elem
            res = compute_multiclass_result(list_by_images[elem], key)
            multiclass_results[key].append(res)

    multiclass_results_avg = {}
    for key in relevant_keys:
        avg = sum( multiclass_results[key] ) / len( multiclass_results[key] )
        if avg != -1:
            #print key, " - ", multiclass_results[key]
            print key, avg


    relevant_perclass_keys = []
    for image_class in image_classes:
        relevant_perclass_keys.extend([(image_class, elem) for elem in relevant_keys])

    multiclass_perclass_results = {}
    for key in relevant_perclass_keys:
        multiclass_perclass_results[key] = []
        for elem in list_by_images:
            if list_by_images[elem][0]['image class'] != key[0]:
                continue
            res = compute_multiclass_result(list_by_images[elem], key[1])
            #print key, res
            multiclass_perclass_results[key].append(res)

    multiclass_perclass_results_avg = {}
    for key in relevant_perclass_keys:
        #print key
        avg = sum( multiclass_perclass_results[key] ) / len( multiclass_perclass_results[key] )
        if avg != -1:
            #print key, " - ", multiclass_results[key]
            print key, avg


def compute_multiclass_result(image_data, key):
    probs = {}

    try:

        for elem in image_data:
            #print key, " - ", elem[key], " - ", elem['model class'], " - ", elem['ownclass']
            probs[ float( elem['ownclass'] ) ] = float( elem[key] )

        inverse_probs = [(value, key) for key, value in probs.items()]

        resulting_class = max(inverse_probs)[1]
        #print "probs = ", probs
        #print "resulting_class = ", resulting_class

        return resulting_class
    except ValueError:
        return -1

def correlation(a, b):
    mean_a = sum(a)/len(a)
    mean_b = sum(b)/len(b)

    X = [elem - mean_a for elem in a]
    Y = [elem - mean_b for elem in b]

    XX = [elem * elem for elem in X]
    YY = [elem * elem for elem in Y]

    XY = [ elem_X * elem_Y for (elem_X, elem_Y) in zip(X,Y)]

    return sum(XY) / math.sqrt( sum(XX) * sum(YY) )

            
if __name__ == "__main__":
    main()
