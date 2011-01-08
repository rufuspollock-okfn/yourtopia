import csv 
import sys

from iso3166 import countries

from mongo import get_db, DBRef

CATEGORIES = {
    'economy': {'label': 'Economy', 'set': 'hdi', 'proxy': 'NYGDPPCAPPPCD', 'color': '#e4adc5'},
    'health': {'label': 'Health', 'set': 'hdi', 'proxy': 'SPDYNLE00IN', 'color': '#e4543a'},
    'education': {'label': 'Education', 'set': 'hdi', 'proxy': 'SESECENRR', 'color': '#d9df29'},
    'inequality': {'label': 'Inequality', 'set': 'hdi', 'proxy': 'SIPOVGINI', 'color': '#a9d0e4'},
    'social_cap': {'label': 'Social capital', 'set': '', 'color': '#0aaae1'},
    'environ': {'label': 'Environment', 'set': '', 'color': '#89c141'},
    'institutions': {'label': 'Institutions', 'set': '', 'color': '#ea872e'},
    'security': {'label': 'Security', 'set': '', 'color': '#e4adc5'},
    'governance': {'label': 'Governance', 'set': '', 'color': '#9f11ab'},
    'goal1': {'label': 'Eradicate extreme poverty and hunger', 'set': 'mdg', 'color': '#00ff00'},
    'goal2': {'label': 'Achieve universal primary education', 'set': 'mdg', 'color': '#ffff00'},
    'goal3': {'label': 'Promote gender equality and empower women', 'set': 'mdg', 'color': '#ff0000'},
    'goal4': {'label': 'Reduce child mortality', 'set': 'mdg', 'color': '#00ffff'},
    'goal5': {'label': 'Improve maternal health', 'set': 'mdg', 'color': '#ff00ff'},
    'goal6': {'label': 'Combat HIV/AIDS, malaria and other diseases', 'set': 'mdg', 'color': '#0000ff'},
    'goal7': {'label': 'Ensure environmental sustainability', 'set': 'mdg', 'color': '#219d10'},
    'goal8': {'label': 'Develop a global partnership for development', 'set': 'mdg', 'color': '#9f11ab'},
    'goal9': {'label': 'World Domination', 'set': 'mdg', 'color': '#000000'},
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
                'set': category.get('set')
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
        try:    
            cc3 = row.get('country')
            cc3 = {'ROM': 'ROU',
                   'ZAR': 'COD',
                   'TMP': 'TLS'}.get(cc3, cc3)
            cc =  countries.get(cc3).alpha2
        except: 
            #print row
            continue
        query = {'indicator': indicator.get('_id'), 
                 'country': cc, 
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


