from flask_restx import Namespace, Resource, reqparse
from collections import OrderedDict


import stanza 
import time

api = Namespace('stanza', description="Biomedical named entity recognition (NER) with Stanza NLP")

#Request Parsing
parser = reqparse.RequestParser()
parser.add_argument('query', required=True, help="Dude, query cannot be blank.")

#Download required processors + initialize Pipelines. Initial run will download and will reference local cache moving forward
stanza.download('en', package='mimic', processors={'ner':'i2b2'})
stanza.download('en', package='mimic', processors={'ner':'ncbi_disease'})
stanza.download('en', package='mimic', processors={'ner':'anatem'})

anatomyPipeline = stanza.Pipeline('en', package="mimic", processors={'ner':"antem"})
i2b2Pipeline = stanza.Pipeline('en', package="mimic", processors={'ner':'i2b2'})
ncbiDiseasePipeline = stanza.Pipeline('en', package="mimic", processors={'ner':'ncbi_disease'})


def findAnatomyEntities(query):
    if anatomyPipeline:
        temp_doc = anatomyPipeline(query)

        anatomy = []

        for entity in temp_doc.entities:
            anatomy.append(entity.text)

        #using set() to remove obvious duplicates
        if anatomy:
            anatomy = list(OrderedDict.fromkeys(anatomy))

        return anatomy

def findI2B2Entities(query):
    if i2b2Pipeline:
        temp_doc = i2b2Pipeline(query)
        problems = []
        treatments = []
        tests = []
        
        for entity in temp_doc.entities:
            if entity.type == 'PROBLEM':
                problems.append(entity.text)
            elif entity.type == 'TREATMENT':
                treatments.append(entity.text)
            elif entity.type == 'TEST':
                tests.append(entity.text)
        
        #using set() to remove obvious duplicates
        if problems:
            problems = list(OrderedDict.fromkeys(problems))
        if treatments:
            treatments = list(OrderedDict.fromkeys(treatments))
        if tests:
            tests = list(OrderedDict.fromkeys(tests))

        return problems, treatments, tests

def findNCBIDiseases(query):
    if ncbiDiseasePipeline:
        temp_doc = ncbiDiseasePipeline(query)
        diseases = []

        for entity in temp_doc.entities:
            diseases.append(entity.text)
        
        #using set() to remove obvious duplicates
        if diseases:
            diseases = list(OrderedDict.fromkeys(diseases))

        return diseases

def findMedicalEntities(query):
    anatomy = []
    problems = []
    treatments = []
    tests = []
    diseases = []
    #default error state
    errorMessages = []
    errorCode = 1
    
    #Try to find varying entities
    try:
       anatomy = findAnatomyEntities(query)
    except Exception as e:
        errorString = repr(e)
        errorMessages.append('Error NER (anatem): '+errorString)

    try: 
        problems, treatments, tests = findI2B2Entities(query)
    except Exception as e:
        errorString = repr(e)
        errorMessages.append('Error NER (i2b2): '+errorString)


    try:
        diseases = findNCBIDiseases(query)
    except Exception as e:
        errorString = repr(e)
        errorMessages.append('Error NER (ncbi_disease): '+errorString) 

    #check if errorMessages is still null then change errorCode to 0
    if len(errorMessages) == 0:
        errorCode = 0

    return anatomy, problems, treatments, tests, diseases, errorCode, errorMessages


@api.route('/')
@api.doc(params={'query':"Will accept a string and will return medical entities as per i2b2, anatem & ncbi_disease models"})
class Stanza(Resource):
    @api.doc('Stanza NLP')
    def post(self):
        request_time = time.time()
        #Parse query from request obj
        args = parser.parse_args()
        query = args['query']
        #look for medical entities
        anatomy, problems, treatments, tests, diseases, errorCode, errorMessages = findMedicalEntities(query)
        #Finding time it took between request and entities recognition to complete
        end_time = time.time()
        return {'vers#': 1, 'query': query, 'symptoms': problems, 'body_structures' : anatomy, 'medications': treatments, 'conditions' : diseases, 'procedures' : tests, 'errorCode' : errorCode, 'errorMessages' : errorMessages, 'run_time_in_secs': (end_time-request_time)}


