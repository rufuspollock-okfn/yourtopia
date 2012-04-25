# encoding: utf-8

from flask import Flask
from flask import Markup
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import escape
from flask import g
import unicodecsv
from jinja2 import evalcontextfilter, Markup, escape
import re
import simplejson as json
import sqlite3
from contextlib import closing
import datetime

# dev mode
DEV_MODE = True

# languages available, sorted by priority
LANG_PRIORITIES = ['it', 'en']

# path to the metadata JSON file
METADATA_PATH = 'static/data/metadata.json'

DATABASE = 'static/data/database.db'

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html', devmode=DEV_MODE)


@app.route('/browse/')
def browse():
    g.db = get_connection()
    entries = get_usercreated_entries(9)
    return render_template('browse.html', entries=entries)


@app.route('/about/')
def about():
    return render_template('about.html', metadata=metadata)


@app.route('/i/<int:id>/')
def details(id):
    g.db = get_connection()
    entry = get_usercreated_entries(id=id)
    return render_template('details.html', entry=entry)


def connect_db():
    return sqlite3.connect(DATABASE)


def get_connection():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = connect_db()
    return db


def get_usercreated_entries(num=1, offset=0, id=None):
    """
    Read a number of user-generated datasets from
    the database
    """
    if id is not None:
        entry = query_db('SELECT * FROM usercreated WHERE id=?', [id], one=True)
        return entry
    else:
        entries = query_db('SELECT * FROM usercreated ORDER BY id DESC LIMIT ?, ?', [offset, num])
        return entries


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def import_series_metadata(path):
    """
    Reads metadata information from JSON file
    """
    app.logger.debug('import_series_metadata() called')
    try:
        f = open(path)
    except:
        app.logger.error('File ' + path + ' could not be opened.')
        return
    raw = json.loads(f.read())
    metadata = {}
    for item in raw['hits']['hits']:
        entry = {
            'id': item['_source']['id'],
            'label': {},
            'description': {},
            'type': item['_source']['type'],
            'format': item['_source']['format'],
            'source_url': None,
            'icon': item['_source']['icon'],
            'high_is_good': None
        }
        # read language-dependent strings
        for key in item['_source'].keys():
            if '@' in key:
                (name, lang) = key.split('@')
                entry[name][lang] = item['_source'][key]
        # source URL
        url_find = re.search(r'(http[s]*://.+)\b', item['_source']['source'])
        if url_find is not None:
            entry['source_url'] = url_find.group(1)
        metadata[item['_source']['id']] = entry
    return metadata


def import_i18n_strings(path):
    """
    Read internationalization strings from CSV data source
    and return it as a dict
    """
    f = open(path)
    reader = unicodecsv.reader(f, encoding='utf-8', delimiter=",",
        quotechar='"', quoting=unicodecsv.QUOTE_MINIMAL)
    rowcount = 0
    i18n = {}
    fieldnames = []
    for row in reader:
        if rowcount == 0:
            fieldnames = row
        else:
            my_id = ''
            my_strings = {}
            fieldcount = 0
            for field in row:
                if fieldnames[fieldcount] == 'string_id':
                    my_id = field
                else:
                    my_strings[fieldnames[fieldcount]] = field
                fieldcount += 1
            i18n[my_id] = my_strings
        rowcount += 1
    return i18n


def set_language():
    """
    Sets the language according to what we support, what
    the user agent says it supports and what the session
    says it supports
    """
    lang_url_param = request.args.get('lang', '')
    if lang_url_param != '' and lang_url_param in LANG_PRIORITIES:
        lang = lang_url_param
    elif 'lang' not in session:
        lang = LANG_PRIORITIES[0]
        ua_languages = request.accept_languages
        for user_lang, quality in ua_languages:
            for offered_lang in LANG_PRIORITIES:
                if user_lang == offered_lang:
                    lang = offered_lang
    else:
        lang = session['lang']
    session['lang'] = lang


@app.template_filter('i18n')
def i18n_filter(s, lang="en"):
    """
    Output the key in the user's selected language
    """
    #app.logger.debug(session['lang'])
    #app.logger.debug(s)
    #app.logger.debug(i18n[s][session['lang']])
    if s not in i18n:
        app.logger.debug("Key is invalid: " + s)
        return 'Key "' + s + '" is invalid'
    if session['lang'] not in i18n[s]:
        app.logger.debug("Key is not translated: " + s)
        return 'Key "' + s + '" not available in "' + session['lang'] + '"'
    if session['lang'] == '':
        app.logger.debug("Key is empty: " + s)
        return 'Key "' + s + '" in "' + session['lang'] + '" is empty'
    return Markup(i18n[s][session['lang']])


@app.template_filter('dateformat')
def dateformat_filter(s, format='%Y-%m-%d'):
    """
    Output a date according to a given format
    """
    value = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    return Markup(value.strftime(format))


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


if __name__ == '__main__':
    i18n = import_i18n_strings('static/data/i18n.csv')
    app.before_request(set_language)
    app.secret_key = 'A0ZrhkdsjhkjlksgnkjnsdgkjnmN]LWX/,?RT'
    metadata = import_series_metadata(METADATA_PATH)
    if DEV_MODE:
        app.run(debug=True)
    else:
        app.run(debug=False, host='0.0.0.0')
