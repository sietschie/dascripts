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
