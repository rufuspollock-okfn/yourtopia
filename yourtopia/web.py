# encoding: utf-8
import os
import re
import sqlite3
from contextlib import closing
import datetime
import urllib
import json

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
from jinja2 import evalcontextfilter
from jinja2 import Markup
from jinja2 import escape
from flask import abort

# dev mode
DEV_MODE = True

# languages available, sorted by priority
LANG_PRIORITIES = ['it', 'en']

__HERE__ = os.path.dirname(__file__)
# path to the metadata JSON file
METADATA_PATH = os.path.join(__HERE__, 'static/data/metadata.json')
DATABASE = os.path.join(__HERE__, 'static/data/database.db')

BROWSE_PERPAGE = 9

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

app = Flask(__name__)

@app.route('/')
def home():
    category_headlines = extract_i18n_keys(i18n, r'category_headline.*')
    return render_template('home.html', metadata=metadata, i18n_strings=category_headlines)


@app.route('/browse/', defaults={'page': 1})
@app.route('/browse/<int:page>/')
def browse(page):
    offset = 0
    if page > 1:
        offset = (page - 1) * BROWSE_PERPAGE
    entries = get_usercreated_entries(BROWSE_PERPAGE + 1, offset)
    if len(entries):
        show_prev = False
        show_next = False
        if (len(entries) > BROWSE_PERPAGE):
            entries.pop()
            show_next = True
        if offset > 0:
            show_prev = True
        return render_template('browse.html',
            entries=entries, page=page,
            show_next=show_next,
            show_prev=show_prev)
    else:
        abort(404)


@app.route('/about/')
def about():
    return render_template('about.html', metadata=metadata)


@app.route('/i/<int:id>/')
def details(id):
    url = request.scheme + "://" + request.host + request.path
    category_headlines = extract_i18n_keys(i18n, r'category_headline.*')
    entry = get_usercreated_entries(id=id)
    return render_template('details.html', entry=entry, i18n_strings=category_headlines, url=url)


@app.route('/edit/<int:id>/')
def edit_single(id):
    # user can only access his own ID here
    if 'dataset_id' not in session:
        abort(401)
    if session['dataset_id'] != id:
        abort(401)
    entry = get_usercreated_entries(id=id)
    i18n_strings = extract_i18n_keys(i18n, r'category_headline.*')
    i18n_strings.update(extract_i18n_keys(i18n, r'sharing_.*'))
    return render_template('edit.html', id=id, entry=entry, i18n_strings=i18n_strings)


@app.route('/edit/', methods=['POST'])
def edit():
    """
    This view function receives the user-created model
    via POST and redirects the user to finalize the
    sharing process. The user's dataset's ID is stored
    in the session.
    """
    anonymized_ip = anonymize_ip(request.remote_addr)
    if 'id' not in request.form:
        # first save
        id = add_usercreated_entry(request.form['data'], anonymized_ip)
        session['dataset_id'] = id
        return redirect(url_for('edit_single', id=id))
    else:
        # second/subsequent save (publishing/sharing)
        id = session['dataset_id']
        if id != int(request.form['id']):
            # user is probably creating a second dataset
            abort(401)
        user_name = None
        user_url = None
        description = None
        if 'description' in request.form:
            if request.form['description'] != i18n['sharing_textfield_default'][session['lang']]:
                description = request.form['description']
        if 'user_name' in request.form:
            if request.form['user_name'] != i18n['sharing_userfield_default'][session['lang']]:
                user_name = request.form['user_name']
        if 'user_url' in request.form:
            user_url = request.form['user_url']
        update_usercreated_entry(id=id,
            user_name=user_name,
            user_url=user_url,
            description=description)
        return redirect(url_for('details', id=id))


def connect_db():
    return sqlite3.connect(DATABASE)


def get_connection():
    """
    Return the current database connection. If not yet
    connected, it connects first.
    """
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
        entries = query_db('''SELECT * FROM usercreated
            WHERE user_name IS NOT NULL
            ORDER BY id DESC LIMIT ?, ?''', [offset, num])
        return entries


def add_usercreated_entry(json_data, ip):
    """
    Writes the user-generated data to the database and returns the ID
    """
    data = json.loads(json_data)
    country = data['country']
    version = data['version']
    weights = {}
    for key in data.keys():
        # if key ends in _weight, it is used
        keyparts = key.split('_')
        if keyparts[len(keyparts) - 1] == 'weight':
            weights[key] = data[key]
    #app.logger.debug(weights)
    g.db = get_connection()
    cur = g.db.cursor()
    cur.execute('''INSERT INTO usercreated
        (weights, created_at, user_ip, country, version)
        VALUES(?, DATETIME("NOW"), ?, ?, ?)''', [json.dumps(weights), ip, country, version])
    g.db.commit()
    id = cur.lastrowid
    cur.close()
    return id


def update_usercreated_entry(id, user_name, user_url, description):
    """
    Extends a previously created user-generated dataset
    """
    g.db = get_connection()
    g.db.execute('''UPDATE usercreated
        SET user_name=?, user_url=?, description=?
        WHERE id=?''', [user_name, user_url, description, id])
    g.db.commit()


def query_db(query, args=(), one=False):
    """
    General database query function. Use parameter one=True to
    return one dict instead of a list of dicts.
    See get_usercreated_entries() for an example.
    """
    g.db = get_connection()
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def import_series_metadata(path):
    """
    Reads metadata information from JSON file
    """
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


def extract_i18n_keys(thedict, regex_pattern):
    """
    This helper function extracts keys matching a given regex pattern
    and return them as dict. This is useful for passing only part of
    the i18n data structure to a view.
    """
    ret = {}
    for key in thedict:
        match = re.match(regex_pattern, key)
        if match is not None:
            ret[key] = thedict[key]
    return ret


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


def anonymize_ip(ip):
    """
    Replace last of four number packets in an IP address by zero
    """
    parts = ip.split('.')
    parts[3] = '0'
    return '.'.join(parts)


@app.template_filter('i18n')
def i18n_filter(s, lang="en"):
    """
    Output the key in the user's selected language
    """
    if s not in i18n:
        app.logger.debug("Key is invalid: " + s)
        return 'Key "' + s + '" is invalid'
    if session['lang'] not in i18n[s]:
        app.logger.debug("Key is not translated: " + s)
        return 'Key "' + s + '" not available in "' + session['lang'] + '"'
    if session['lang'] == '':
        app.logger.debug("Key is empty: " + s)
        return 'Key "' + s + '" in "' + session['lang'] + '" is empty'
    #app.logger.debug(['i18n_filter', i18n[s][session['lang']]])
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


@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    #app.logger.debug(['urlencode', s])
    return Markup(s)


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


# initialize the database if not already created
if not os.path.exists(DATABASE):
    db = connect_db()
    sql = '''CREATE TABLE usercreated ( 
        id          INTEGER         PRIMARY KEY ASC AUTOINCREMENT,
        user_name   VARCHAR( 100 ),
        user_url    VARCHAR( 150 ),
        description TEXT( 300 ),
        weights     TEXT( 1000 ),
        created_at  DATETIME        NOT NULL,
        user_ip     VARCHAR( 15 ),
        country     VARCHAR( 3 ),
        version     INTEGER 
    );'''
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    cur.close()
app.before_request(set_language)
app.secret_key = 'A0ZrhkdsjhkjlksgnkjnsdgkjnmN]LWX/,?RT'

i18n = import_i18n_strings(os.path.join(__HERE__, 'static/data/i18n.csv'))
metadata = import_series_metadata(METADATA_PATH)


if __name__ == '__main__':
    if DEV_MODE:
        app.run(debug=True)
    else:
        app.run(debug=False, host='0.0.0.0')
