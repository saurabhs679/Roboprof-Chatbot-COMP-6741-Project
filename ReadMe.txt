To run the code upload all ipynb, .ttl, .nt and csv files into jupyter Notebook and run each cell. We get complete knowledge base in SPARQL queries.ipynb
Also change the location of input(Slides_for_topics) and output file in Knowledge Base Topic Population according to your need
To run queries we need Apache Fuseki . Upload the merged_output.ttl into Fuseki and take queries from queries folder and run them
Step to run rasa differ from system to system follow lab 9. 
To run our model follow these steps
conda activate rasa
change directory to rasa folder
rasa train
run next 2 simultaneously
rasa run actions
rasa shell

Queries-Contains Sparql queries in notepad format(Total 13)
Queries Output-COntain output in csv format(Total 13)
Queries_Part2-Contains Sparql queries in notepad format(Total 4)
Queries_Part2_Answer-COntain output in csv format(Total 4)
Slides_for_topics- Contains pdf files for Knowledge graph automated
Output- output of slide for topics

CSV files-The following csv files are used to run code.Upload them on jupyter

Intelligent_Systems.csv  -  Contains Course information
Lectures_information.csv   -  Contains Lectures information for courses
Student_information.csv  -  Contains Students information  for courses
Topic_information.csv - Contains Topics information for courses
Univ.csv - Contain University Details
CATALOG.csv - Opendataset containing courses information

IPYNB  files_ upload these on jupyter to run them in this order
Knowledge Graph Vocabulary.ipynb - We used this to create our Vocabulary
Knowledge graph automated.ipynb - We are using this to populate all our vocabulary using all the csv files
Knowledge Base Topic Population.ipynb-knowledge base construction for topic using LOD
Course_Catalog.ipynb - Create Knowledge base of open dataset CSV
Merged topic.ipynb - To merge all the ttl files
SPARQL queries.ipynb - Run SparQl queries in python and convert into merged_data.ttl file 
SparQL_P2.ipynb - Run SparQl queries in python for part 2
N-Triple.ipynb - To convert Turtle file to N-triples.

output_annotations - converted pdf to text file for further processing
output_new.nt - N-Triples for the Constructed Knowledge base 
Topic_triples.nt - N - triples for topic population
Course_Catalog.ttl - Turtle file for Course Information
merged_output.ttl - This turtle contain our complete Knowledge base
Vocabulary.ttl - Basic Vocabulary in turtle format
merged_data.ttl - TTl file for first part
output_new.ttl - TTL file for Topic population

Rasa folder-This folder contains our Rasa chatbot.
The following files has been edited in this folder
domain.yml - 
endpoints.yml - comment out localhost link
config.yml - for nlu fallback
nlu.yml - create training data
rules.yml - to handle nlu fallback
stories.yml - used to link intent and actions
actions.py - contain python code

Expectations-of-Originality-Anubhav Mahajan.pdf - Expectation of Originality form
Expectations-of-Originality-Saurabh - Expectation of Originality form

Final_Report - report on design and implementation



