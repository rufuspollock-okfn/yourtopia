import csv 
import sys

from mongo import get_db, DBRef

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
            'hdi_weight': 0.0}
        if row.get('hdi_weight'): 
            indicator['hdi_weight'] = float(row.get('hdi_weight')) 
        query = {'name': row.get('name')}
        indicator.update(query)
        db.indicator.update(query, indicator, upsert=True)
    fh.close() 
 
def load_dataset_from_file(file_name):
    fh = open(file_name, 'rb') 
    db = get_db()
    reader = csv.DictReader(fh) 
    for row in reader: 
        if not row.get('indicator_name'):
            continue
        dataset = {
            'country_name': row.get('country2')}
        if row.get('value'):
            dataset['value'] = float(row.get('value'))
        else: 
            dataset['value'] = 0.0 
        if row.get('normalized_value'):
             dataset['normalized_value'] = float(row.get('normalized_value'))
        else: 
            dataset['normalized_value'] = dataset['value'] 
        indicator = db.indicator.find_one({'name': row.get('indicator_name')})
        assert indicator, "Indicator %s could not be found!" % row.get('indicator_name') 
        query = {'indicator': indicator.get('_id'), 
                 'country': row.get('country'), 
                 'time': row.get('time')}
        dataset.update(query)
        dataset['indicator_name'] = indicator.get('name')
        db.datum.update(query, dataset, upsert=True) 
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


