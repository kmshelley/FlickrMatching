#! /home/hadoop/anaconda2/bin/python
import sys

if __name__=='__main__':
    prev_key=None
    min_dist=float('inf')
    best_url=None
    for line in sys.stdin:
        data = line.strip().split('\t')
        if len(data)==2:
            key,val = data
            url,dist = val.split('|')
            if key == prev_key:
                if float(dist)<min_dist:
                    best_url=url
                    min_dist=float(dist)
            else:
                if prev_key and best_url:
                    sys.stdout.write('%s,%s\n' % (prev_key,best_url))
                best_url=url
                min_dist=float(dist)
                prev_key=key
                
    if prev_key and best_url:
        sys.stdout.write('%s,%s\n' % (prev_key,best_url))
                    
                
                
