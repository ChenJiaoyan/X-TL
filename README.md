# X-TL

This project contains the codes, ontology and data for the paper "Transfer Learning Explanation with Ontologies".

./Data: Information for data access and download

./Onto/FlightOntology.owl: OWL ontology (TBox axioms of concepts and roles, and some important individuals)

./FlightOntology: An IntelliJ maven project for constructing LSOs (BuildKGRun.java), root individual extraction (RootEntRun.java), external axiom importing and entailment reasoning (XKnowRun.java)

./Onto/Entailments: Entailment closure of an example learning domain (output example of ./FlightOntology project)

./Flight_RL/Learn: Prediction input/output processing (ExtXY.py), CNN feature transfer implemented with Tensorflow 1.4.0 (CNN.py), Transferability measurement (TraEva.py) 

./Flight_RL/Explain: Inference of explanatory evidence

For any questions, please contact jiaoyan.chen@cs.ox.ac.uk
