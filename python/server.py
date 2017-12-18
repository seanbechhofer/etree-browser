#! env/bin/python3
import argparse
import jinja2
import os
import functools
import sparql
import logging
import formatting
import urllib.parse
import etree
import graphs

from bottle import jinja2_view, route, run, static_file, request, redirect, response, Response, Bottle

app = Bottle()

# Filter that allows us to pass URLs as arguments
def url_filter(config):
    ''' Matches a url. '''
    regexp = r'http://.*/.*'

    def to_python(match):
        return match

    def to_url(url):
        return url

    return regexp, to_python, to_url

app.router.add_filter('url', url_filter)

# Filter that allows us to pass any old crap as arguments
def whatever_filter(config):
    ''' Matches anything'''
    regexp = r'..*'

    def to_python(match):
        return match

    def to_url(url):
        return url

    return regexp, to_python, to_url

app.router.add_filter('whatever', whatever_filter)

# Setting up template directory
here = os.path.dirname(os.path.abspath(__file__))
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(here + '/templates'))

# Filter for use in jinja templates
filter_dict = {}
def filter(func):
	"""Decorator to add the function to filter_dict"""
	filter_dict[func.__name__] = func
	return func

@filter
def encode(s):
    return urllib.parse.quote_plus(s)
    
view = functools.partial(jinja2_view, template_lookup=[here + '/templates'],
                             template_settings={'filters': filter_dict})

# Static pages, css, js etc.
@app.route('/css/<filename>')
def static_css(filename):
    return static_file(filename, root=here + '/../web/css')

@app.route('/js/<filename>')
def static_js(filename):
    return static_file(filename, root=here + '/../web/js')

@app.route('/fonts/<filename>')
def static_fonts(filename):
    return static_file(filename, root=here + '/../web/fonts')

@app.route('/static/<filename>')
def static_js(filename):
    return static_file(filename, root=here + '/../web/static')
@app.route('/static/<filename>')

@app.route('/static/images/<filename>')
def static_image(filename):
    return static_file(filename, root=here + '/../web/static/images')

@app.route('/static/')
def static_index():
    return static_file("index.html", root=here + '/../web/static')

# ========== Routes ===============
@app.route('/')
@view('home.html')
def home():
    return {
    }

@app.route('/artists')
@view('artists.html')
def artists():
    order = "label"
    if request.query.order == "performances":
        order = "performances"
    direction = "asc"
    if request.query.direction == "desc":
        direction = "desc"
    query = etree.prefix + '''
SELECT ?thing ?label ?mb ?mbw ?opmb ?opmbw ?oplfm ?oplfmw ?slfm ?slfmw (COUNT(?performance) AS ?performances) WHERE {{
?thing rdf:type mo:MusicArtist.
?thing skos:prefLabel ?label.
?performance mo:performer ?thing.
?performance event:time ?time.

OPTIONAL {{
?sim1 sim:subject ?thing.
?sim1 sim:object ?mb.
?sim1 sim:method etree:simpleMusicBrainzMatch.
?sim1 sim:weight ?mbw.
}}
OPTIONAL {{
?sim2 sim:subject ?thing.
?sim2 sim:object ?opmb.
?sim2 sim:method etree:opMusicBrainzMatch.
?sim2 sim:weight ?opmbw.
}}
OPTIONAL {{
?sim3 sim:subject ?thing.
?sim3 sim:object ?oplfm.
?sim3 sim:method etree:opLastFMMatch.
?sim3 sim:weight ?oplfmw.
}}
OPTIONAL {{
?sim4 sim:subject ?thing.
?sim4 sim:object ?slfm.
?sim4 sim:method etree:mroSetListFMArtistMatch.
?sim4 sim:weight ?slfmw.
}}

}} GROUP BY ?thing ?label ?mb ?mbw ?opmb ?opmbw ?oplfm ?oplfmw ?slfm ?slfmw
ORDER BY {direction}(?{order})
'''.format(order=order, direction=direction)

    results = sparql.result_to_table(sparql.query(name='artists'+'-'+direction+'-'+order,
                             query=query))
    arts = []
    coll = {
        'mb': 'MusicBrainz',
        'opmb': 'MusicBrainz',
        'oplfm': 'last.fm',
        'slfm': 'setlist.fm',
    }

        
    for result in results['bindings']:
        if not result['label'] == '':
            art = {
                'name': result['label'],
                'url': result['thing'],
                'performances': result['performances'],
                'mappings': [],
                }
            # Iterate through the similarities
            for key in ['mb','opmb','oplfm','slfm']:
                if key in result:
                    confidence = float(result[key+"w"])
                    #  Ignore very low confidence
                    if confidence > 0.01:
                        art['mappings'].append({
                            'collection': coll[key],
                            'url' : result[key],
                            # Pass formatting information through to the template. Bit iffy.
                            'confidence': formatting.badge(confidence)
                            })
            arts.append(art)
    return {
        'slices': 2,
        'title': 'Artists',
        'artists': arts
    }

@app.route('/venues')
@view('venues.html')
def venues():
    query = etree.prefix + '''
SELECT ?thing ?label ?count WHERE {
 {
  SELECT ?thing (COUNT(?sim) AS ?count) WHERE {
  ?sim sim:object ?thing.
  ?sim sim:method etree:simpleLastfmMatch.
  } GROUP BY ?thing
 }
 ?thing skos:prefLabel ?label.
} ORDER BY DESC(?count)
'''
    results = sparql.query(name='venues',
                             query=query)
    vens = []
    for result in results['results']['bindings']:
        vens.append({
            'name': result['label']['value'],
            'url': result['thing']['value'],
            'performances': result['count']['value']
            })
    return {
        'slices': 3,
        'title': 'Venues',
        'venues': vens
        }

@app.route('/locations')
@view('things.html')
def locations():
    query = etree.prefix + '''
SELECT DISTINCT ?thing (concat(?n, ", ", ?c) as ?label) WHERE {
?thing geo:name ?n.
?thing geo:countryCode ?c.
} ORDER BY ?label
'''
    results = sparql.query(name='locations',
                             query=query)
    locs = []
    for result in results['results']['bindings']:
        print(result)
        locs.append({
            'label': result['label']['value'],
            'url': result['thing']['value'],
            })
    return {
        'slices': 4,
        'thing_type': 'Locations',
        'title': 'Locations',
        'things': locs,
        'prefix': '/geo/',
        }

@app.route('/artist/<artist_id:whatever>')
@view('artist.html')
def artist(artist_id):
    variables = {'artist_id': artist_id}
    query = etree.prefix + '''
SELECT ?label ?mb ?opmb ?oplfm ?slfm WHERE {{
<{artist_id}> skos:prefLabel ?label.
OPTIONAL {{
?sim1 sim:subject <{artist_id}>.
?sim1 sim:object ?mb.
?sim1 sim:method etree:simpleMusicBrainzMatch.
?sim1 sim:weight ?mbw.
}}
OPTIONAL {{
?sim2 sim:subject <{artist_id}>.
?sim2 sim:object ?opmb.
?sim2 sim:method etree:opMusicBrainzMatch.
?sim2 sim:weight ?opmbw.
}}
OPTIONAL {{
?sim3 sim:subject <{artist_id}>.
?sim3 sim:object ?oplfm.
?sim3 sim:method etree:opLastFMMatch.
?sim3 sim:weight ?oplfmw.
}}
OPTIONAL {{
?sim4 sim:subject <{artist_id}>.
?sim4 sim:object ?slfm.
?sim4 sim:method etree:mroSetListFMArtistMatch.
?sim4 sim:weight ?slfmw.
}}
}}
'''.format(artist_id=artist_id)
    print(query)
    sims = sparql.query(query=query)
    mappings = []
    coll = {
        'mb': 'MusicBrainz',
        'opmb': 'MusicBrainz',
        'oplfm': 'last.fm',
        'slfm': 'setlist.fm',
    }
    name = ""
    for result in sims['results']['bindings']:
        name = result['label']['value']
        for key in coll.keys():
            if key in result:
                mappings.append({
                    'collection': coll[key],
                    'url': result[key]['value']
                    })
    query = etree.prefix + '''
SELECT ?event ?eventName ?date WHERE {{
<{artist_id}> mo:performed ?event.
?event skos:prefLabel ?eventName.
?event event:time ?time.
?time timeline:beginsAtDateTime ?date.
}} ORDER BY DESC(?date)
'''.format(artist_id=artist_id)
    events = sparql.query(query=query)
    performances = []
    for result in events['results']['bindings']:
        performances.append({
            'url': result['event']['value'],
            'label': result['eventName']['value'],
            'date': result['date']['value'],
            })
    return {
        'id': artist_id,
        'name': name,
        'mappings': mappings,
        'performances': performances,
    }

@app.route('/performance/<performance_id:whatever>')
@view('performance.html')
def performance(performance_id):
    query = etree.prefix + '''
SELECT DISTINCT ?performance ?etree_id ?artist_id ?artist_name ?artMB ?date ?description ?notes ?uploader ?lineage ?geo ?location ?country ?lastfm ?lastfmName ?lastfmEvent ?setlistfmEvent ?setlistfm
{{
<{performance_id}> mo:performer ?artist_id;
  etree:uploader ?uploader;
  etree:lineage ?lineage;
  etree:id ?etree_id;
  event:place ?venue;
  event:time ?time;
  etree:description ?description;
  skos:prefLabel ?performance;
  etree:notes ?notes.

?artist_id skos:prefLabel ?artist_name.

?time timeline:beginsAtDateTime ?date.

OPTIONAL {{
?sim1 sim:subject ?venue.
?sim1 sim:object ?geo.
?geo geo:name ?location.
?geo geo:countryCode ?country.
}}

OPTIONAL {{
?sim2 sim:subject ?venue.
?sim2 sim:object ?lastfm.
?sim2 sim:method etree:simpleLastfmMatch.
?lastfm skos:prefLabel ?lastfmName.
}}

OPTIONAL {{
?sim3 sim:subject ?art.
?sim3 sim:object ?artMB.
?sim3 sim:method etree:simpleMusicBrainzMatch.
}}

OPTIONAL {{
?sim5 sim:subject <{performance_id}>.
?sim5 sim:object ?lastfmEvent.
?sim5 sim:method etree:mroLastFMPerformanceMatch.
}}

}}
'''.format(performance_id=performance_id)
    perf = sparql.query(query=query)
    for result in perf['results']['bindings']:
        # We assume there's only one, so we'll return from this loop
        performance_info = {
            'performance_id': performance_id,
        }
        for v in result.keys():
            performance_info[v] = result[v]['value']


        # Find track list.
        query = etree.prefix + '''
SELECT DISTINCT ?track ?trackName ?trackNumber ?audio 
{{
<{performance_id}> event:hasSubEvent ?track.
?track skos:prefLabel ?trackName.
?track etree:number ?trackNumber.
OPTIONAL {{
?track etree:audio ?audio.
?audio etree:audioFormat ?format.
FILTER regex(?format, "mp3", "i") 
}}
}} ORDER BY ?trackNumber
'''.format(performance_id=performance_id)
        print(query)
        tracks = sparql.query(query=query)
        performance_info['tracks'] = []
        for track in tracks['results']['bindings']:
            new_info = {
                'track': track['track']['value'],
                'trackName': track['trackName']['value'],
                'trackNumber': track['trackNumber']['value'],
                }
            if 'audio' in track:
                new_info['audio'] = track['audio']['value']

            performance_info['tracks'].append(new_info)

        return performance_info

@app.route('/country/<country_code:whatever>')
@view('things.html')
def country(country_code):
    query = etree.prefix + '''
SELECT ?url ?label {{
?url event:place ?venue.
?url skos:prefLabel ?label.
?sim1 sim:subject ?venue.
?sim1 sim:object ?geo.
?geo geo:name ?location.
?geo geo:countryCode "{country_code}".
}} 
'''.format(country_code=country_code)
    perfs = sparql.query(query=query)
    title = 'Performances in {country_code}'.format(country_code=country_code)
    things = {
        'slices': 3,
        'title': title,
        'thing_type': title,
        'things': [],
        'prefix': '/performance/',
        }
    for result in perfs['results']['bindings']:
        things['things'].append({
            'url': result['url']['value'],
            'label': result['label']['value'],
            })
    return things

@app.route('/geo/<geo_code:whatever>')
@view('things.html')
def geo(geo_code):
    query = etree.prefix + '''
SELECT DISTINCT ?url ?label ?name WHERE {{
?url event:place ?place.
?url skos:prefLabel ?label.
?sim sim:subject ?place.
{{
 {{?sim sim:method etree:simpleGeoMatch.}}
  UNION
 {{?sim sim:method etree:simpleGeoAndLastfmMatch.}}
}}
?sim sim:object <{geo_code}>.
<{geo_code}> geo:name ?name.
}} ORDER BY ?event
'''.format(geo_code=geo_code)
    perfs = sparql.query(query=query)
    things = {
        'title': 'Performances',
        'slices': 3,
        'things': [],
        'prefix': '/performance/'
        }
    for result in perfs['results']['bindings']:
        title = 'Performances in {place}'.format(place = result['name']['value'])
        things['title'] = title
        things['thing_type'] = title
        things['things'].append({
            'url': result['url']['value'],
            'label': result['label']['value'],
            })
    return things

@app.route('/venue/<venue_code:whatever>')
@view('things.html')
def venue(venue_code):
    query = etree.prefix + '''
SELECT DISTINCT ?url ?label ?name WHERE {{
?url event:place ?place.
?url skos:prefLabel ?label.
?sim sim:subject ?place.
?sim sim:method etree:simpleLastfmMatch.
?sim sim:object <{venue_code}>.
<{venue_code}> skos:prefLabel ?name.
}} ORDER BY ?event
'''.format(venue_code=venue_code)
    perfs = sparql.query(query=query)
    things = {
        'title': 'Performances',
        'slices': 3,
        'things': [],
        'prefix': '/performance/'
        }
    for result in perfs['results']['bindings']:
        title = 'Performances in {place}'.format(place = result['name']['value'])
        things['title'] = title
        things['thing_type'] = title
        things['things'].append({
            'url': result['url']['value'],
            'label': result['label']['value'],
            })
    return things

@app.route('/track/<track_id:whatever>')
@view('track.html')
def track(track_id):
    query = etree.prefix + '''SELECT ?artist ?track_name ?artist_name ?num ?event ?event_name ?num ?setlistfmSong ?calma WHERE {{
<{track_id}> mo:performer ?artist.
?artist skos:prefLabel ?artist_name.
<{track_id}> skos:prefLabel ?track_name.
<{track_id}> etree:isSubEventOf ?event.
<{track_id}> etree:number ?num.
?event skos:prefLabel ?event_name.
OPTIONAL {{
?sim sim:subject <{track_id}>.
?sim sim:object ?setlistfmSong.
?sim sim:method etree:simpleSongSetlistFMMatch.
}}
OPTIONAL {{
<{track_id}> calma:data ?calma.
}}
}}'''.format(track_id=track_id)
    results = sparql.query(query=query)
    for result in results['results']['bindings']:
        # Just return the first one.
        track_info = {
            'track_id': track_id,
            'audio': [],
            }
        for key in result.keys():
            track_info[key] = result[key]['value']

        audio_query = etree.prefix + '''SELECT ?audio ?status WHERE {{
<{track_id}> etree:audio ?audio.
?audio etree:audioDerivationStatus ?status.
}}
ORDER BY DESC(?status)
'''.format(track_id=track_id)
        audio_results = sparql.query(query=audio_query)
        for audio_result in audio_results['results']['bindings']:
            print(audio_result)
            track_info['audio'].append({
                'audio': audio_result['audio']['value'],
                'status': audio_result['status']['value'],
                })
        return track_info

# Bar chart showing performances per year
@app.route('/graph/year')
def graph_year():
    query = etree.prefix + '''
SELECT ?year (COUNT (?perf) AS ?performances) 
WHERE {{
  SELECT DISTINCT ?perf ?year
  WHERE {{ 
    ?perf rdf:type etree:Concert. 
    ?perf etree:date ?date. 
    FILTER regex(?date, '....-..-..')
    FILTER (!(regex(?date, '0000')))
    BIND(SUBSTR(?date,1,4) AS ?year)
  }} 
}} GROUP BY ?year 
ORDER BY ?year
'''
    results = sparql.query(query=query)
    data = {}
    for result in results['results']['bindings']:
        data[result['year']['value']] = int(result['performances']['value'])
    bar = graphs.bar(data=data, title="")
    response.content_type='image/png'
    return bar.getvalue()

# Bar chart showing performances per year
@app.route('/graph/year/<artist:whatever>')
def graph_year_artist(artist):
    query = etree.prefix + '''
SELECT ?year (COUNT (?perf) AS ?performances) 
WHERE {{
  SELECT DISTINCT ?perf ?year
  WHERE {{ 
    ?perf rdf:type etree:Concert. 
    ?perf mo:performer <{artist}>.
    ?perf etree:date ?date. 
    FILTER regex(?date, '....-..-..')
    FILTER (!(regex(?date, '0000')))
    BIND(SUBSTR(?date,1,4) AS ?year)
  }} 
}} GROUP BY ?year 
ORDER BY ?year
'''.format(artist=artist)
    results = sparql.query(query=query)
    data = {}
    for result in results['results']['bindings']:
        data[result['year']['value']] = int(result['performances']['value'])
    bar = graphs.bar(data=data, title="")
    response.content_type='image/png'
    return bar.getvalue()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
Browser for the etree linked data/RDF repository. This web application provides a human readable
view on the data held in the etree metadata collection.
''' )
    parser.add_argument('-p', '--port', help='''
Port. Defaults to 4444
''', default='4444')
    parser.add_argument('-e', '--endpoint', help='''
SPARQL endpoint for the data. Defaults to
{}
'''.format(etree.endpoint), default=etree.endpoint)
    parser.add_argument('-d', '--debug', help='debug', action='store_true')
    args = parser.parse_args()
    sparql.setUp(args)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # Running with host='0.0.0.0' allows access from outside. Possibly insecure!
    app.run(host='0.0.0.0', port=int(args.port))


