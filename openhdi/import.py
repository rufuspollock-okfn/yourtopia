import csv 
import sys

from mongo import get_db 

def load_indicator_from_file(file_name):
    fh = open(file_name, 'rb') 
    db = get_db()
    reader = csv.DictReader(fh) 
    for row in reader: 
        indicator =  {
            'name': row.get('name'),
            'label': row.get('label'),
            'question': row.get('question'),
            'description': row.get('description'), 
            'source': row.get('source'),
            'category': row.get('category'),
            'base_weight': row.get('base_weight', 0.5)}
        
    fh.close() 
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s [indicator|dataset] indicator_file.csv" % sys.argv[0]
        sys.exit() 
    if sys.argv[1] not in ['indicator', 'dataset']: 
        print "Unknown import type!"
        sys.exit()
    if sys.argv[1] == 'indicator':
        load_indicator_from_file(sys.argv[2])
    elif sys.argv[1] == 'dataset': 
        load_dataset_from_file(sys.argv[2])


