#!/bin/env python
# encoding: utf-8


import urllib
from urllib2 import HTTPError
from datastore.client import DataStoreClient

# datahub ID
SERIES_DATA_KEY = '4faaef85-3b22-4ebb-ad28-fcc6bd4f5f3d'
# CSV download URL
SERIES_DATA_CSV_URL = 'https://docs.google.com/spreadsheet/pub?key=0AogGMvffTHrgdFFjQy1qVWJGT1IteEhPallQbGlpbmc&single=true&gid=4&output=csv'

# datahub ID
METADATA_KEY = 'fffc6388-01bc-44c4-ba0d-b860d93e6c7c'
# CSV download URL
METADATA_CSV_URL = 'https://docs.google.com/spreadsheet/pub?key=0AogGMvffTHrgdFFjQy1qVWJGT1IteEhPallQbGlpbmc&single=true&gid=1&output=csv'


# i18n data
I18N_CSV_URL = 'https://docs.google.com/spreadsheet/pub?key=0AogGMvffTHrgdFFjQy1qVWJGT1IteEhPallQbGlpbmc&single=true&gid=5&output=csv'
I18N_CSV_PATH = 'static/data/i18n.csv'


def transfer_data(label, csv_url, datahub_id):
    # download
    print "Getting CSV data for " + label + "..."
    urllib.urlretrieve(csv_url, 'data/' + label + '.csv')
    print 'Retrieved latest data for ' + label
    # empty target repository
    datahub_url = 'http://thedatahub.org/api/data/' + datahub_id
    client = DataStoreClient(datahub_url)
    try:
        client.delete()
        print 'Emptied repository for ' + label
    except HTTPError:
        print 'Repository for ' + label + ' was empty'

    #mapping = json.load(open('data/mapping.json'))
    #client.mapping_update(mapping)

    print 'Start uploading data for ' + label + '...'
    client.upload('data/' + label + '.csv')
    print 'Finished uploading data for ' + label


def download_data(url, path):
    print "Downloading", url, "to", path
    urllib.urlretrieve(url, path)

if __name__ == '__main__':
    download_data(I18N_CSV_URL, I18N_CSV_PATH)
    #transfer_data('series_data', SERIES_DATA_CSV_URL, SERIES_DATA_KEY)
    #transfer_data('metadata', METADATA_CSV_URL, METADATA_KEY)
