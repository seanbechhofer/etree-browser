# Basic setup for etree sparqling. Endpoint location, prefixes etc. 
endpoint = 'http://etree.linkedmusic.org/sparql'

prefix = '''
PREFIX etree:<http://etree.linkedmusic.org/vocab/>
PREFIX calma:<http://calma.linkedmusic.org/vocab/>
PREFIX mo:<http://purl.org/ontology/mo/>
PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX geo:<http://www.geonames.org/ontology#>
PREFIX sim:<http://purl.org/ontology/similarity/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX lineage: <http://etree.linkedmusic.org/vocab/lineage/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
'''
