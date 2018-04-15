#! /usr/bin/env python3
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib as rdf
import numpy as np


def tripletFd(direction,triplet):
    g = rdf.Graph()
    g.load(triplet)
    aux = ""
    with open(direction,'w') as fd:
        for s,p,o in g:
            aux = '<'+s+'>\n'
            fd.write(aux)


def labels(text, prop):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    labels = [] # Lista de todas las labels
    with open(text) as fd: # Leemos el archivo con las tripletas
        for line in fd:
            sparql.setQuery("""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dbo: <http://dbpedia.org/ontology/>
                SELECT ?label ?prop
                WHERE {
                    %s rdfs:label ?label.
                    %s dbo:%s ?prop.
                    FILTER (lang(?label) = 'en')
                }
                """ % (line[:-1],line[:-1],prop))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                if result['prop']["value"] != []:
                    labels.append(result["label"]["value"].split(" "))
    return labels


def rank(labels):
    model = Word2Vec(labels, min_count=1, workers=4) # Modelo de word2vec con los labels
    vec = model.wv # Lista de vectores
    averageVector = np.zeros(model.layer1_size) # Vector promedio
    del model
    ranking = {} # Valor de las diferencias como clave y las palabras a las que corresponde
    nRank = np.array([]) # Valores de las diferencias para ser ordenados
    div = 0 # Número de palabras
    aux = 0 # Variable auxiliar para guardar las diferencias
    i = 0 # Para el while
    result = [] # Lista de palabras resultantes
    for label in labels:
        for words in label:
            averageVector = np.add(averageVector,vec.get_vector(words))
            div += 1
    averageVector = np.divide(averageVector,div) # Calculo del vector promedio
    for label in labels:
        for words in label:
            aux = abs(sum(np.subtract(vec.get_vector(words),averageVector)))
            ranking[aux] = words
            nRank = np.append(nRank,aux)
    nRank = np.sort(nRank,kind="mergesort") # Ordenamiento
    while( len(result) < 10): # Creamos la lista de palabras mas similares
        if ranking[nRank[i]] not in result:
            result.append(ranking[nRank[i]])
        i += 1
    return result


if __name__=='__main__':

    #tripletFd("../test/test2.txt", 'http://dbpedia.org/resource/')
    lab = labels("../test/test2.txt","wikiPageID")
    ranking = rank(lab)
    print(ranking)
