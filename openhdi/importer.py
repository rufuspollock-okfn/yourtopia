import csv 
import sys

from mongo import get_db, DBRef

CATEGORIES = {
    'economy': {'label': 'Economy', 'is_hdi': True},
    'health': {'label': 'Health', 'is_hdi': True},
    'education': {'label': 'Education', 'is_hdi': True},
    'inequality': {'label': 'Inequality', 'is_hdi': True},
    'social_cap': {'label': 'Social capital', 'is_hdi': False},
    'environ': {'label': 'Environment', 'is_hdi': False},
    'institutions': {'label': 'Institutions', 'is_hdi': False},
    'security': {'label': 'Security', 'is_hdi': False},
    'governance': {'label': 'Governance', 'is_hdi': False}
}

def munge_name(name):
    return name.replace('.', '').replace('-', '').strip()

def load_indicator_from_file(file_name):
    fh = open(file_name, 'rb') 
    db = get_db()
    reader = csv.DictReader(fh) 
    for row in reader: 
        category = CATEGORIES.get(row.get('category'), {})
        indicator =  {
            'id': munge_name(row.get('name')),
            'label': row.get('label'),
            'question': row.get('question'),
            'good': row.get('good').strip()=='1', 
            'select': row.get('select').strip()>'0',
            'description': row.get('description').decode('iso-8859-1'), 
            'source': row.get('source').decode('iso-8859-1'),
            'category': {
                'id': row.get('category'), 
                'label': category.get('label'),
                'is_hdi': category.get('is_hdi')
            }, 
            'hdi_weight': 0.0}
        if row.get('hdi_weight'): 
            indicator['hdi_weight'] = float(row.get('hdi_weight')) 
        query = {'id': munge_name(row.get('name'))}
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
        indicator_name = munge_name(row.get('indicator_name'))
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
        indicator = db.indicator.find_one({'id': indicator_name})
        assert indicator, "Indicator %s could not be found!" % row.get('indicator_name') 
        query = {'indicator': indicator.get('_id'), 
                 'country': row.get('country'), 
                 'time': row.get('time')}
        dataset.update(query)
        dataset['indicator_id'] = indicator.get('id')
        db.datum.update(query, dataset, upsert=True) 
    db.datum.ensure_index('country')
    db.datum.ensure_index('indicator')
    db.datum.ensure_index('time')
    db.datum.ensure_index('indicator_id')
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


