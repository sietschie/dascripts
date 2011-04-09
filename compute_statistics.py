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

    joint_rates = []
    for l in data:
        if l['model class'] == l['image class']:
            joint_rates.append( float(l['joint']))

    #print joint_rates

    print 'mean joint probability: ', sum(joint_rates) / len(joint_rates)

    correct_class = [float(elem['ownclass']) for elem in data]
    fgd_sym_class = [float(elem['fgd KL sym']) for elem in data]
    fgd_ir_class = [float(elem['fgd KL input result']) for elem in data]
    fgd_ri_class = [float(elem['fgd KL result input']) for elem in data]
    bgd_sym_class = [float(elem['bgd KL sym']) for elem in data]
    bgd_ir_class = [float(elem['bgd KL input result']) for elem in data]
    bgd_ri_class = [float(elem['bgd KL result input']) for elem in data]
    
    print "correlation fgd KL sym: ", correlation(correct_class, fgd_sym_class) 
    print "correlation fgd KL ir: ", correlation(correct_class, fgd_ir_class) 
    print "correlation fgd KL ri: ", correlation(correct_class, fgd_ri_class) 
    print "correlation bgd KL sym: ", correlation(correct_class, bgd_sym_class) 
    print "correlation bgd KL ir: ", correlation(correct_class, bgd_ir_class) 
    print "correlation bgd KL ri: ", correlation(correct_class, bgd_ri_class) 


    prob_fgd_sym_class = [float(elem['prob fgd KL sym']) for elem in data]
    prob_fgd_ir_class = [float(elem['prob fgd KL input result']) for elem in data]
    prob_fgd_ri_class = [float(elem['prob fgd KL result input']) for elem in data]
    prob_bgd_sym_class = [float(elem['prob bgd KL sym']) for elem in data]
    prob_bgd_ir_class = [float(elem['prob bgd KL input result']) for elem in data]
    prob_bgd_ri_class = [float(elem['prob bgd KL result input']) for elem in data]
    
    print "correlation prob fgd KL sym: ", correlation(correct_class, prob_fgd_sym_class) 
    print "correlation prob fgd KL ir: ", correlation(correct_class, prob_fgd_ir_class) 
    print "correlation prob fgd KL ri: ", correlation(correct_class, prob_fgd_ri_class) 
    print "correlation prob bgd KL sym: ", correlation(correct_class, prob_bgd_sym_class) 
    print "correlation prob bgd KL ir: ", correlation(correct_class, prob_bgd_ir_class) 
    print "correlation prob bgd KL ri: ", correlation(correct_class, prob_bgd_ri_class) 


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
