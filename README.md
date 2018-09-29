# Transfer Learning Explanation

This project contains some code examples, flight ontology and data used in the paper "Knowledge-based Transfer Learning Explanation, KR 2018".

## Data/HowToAccessData.md: Information for data access and download

## Onto/FlightOntology.owl: OWL ontology (TBox axioms of concepts and roles, and some important individuals)

## FlightOntology: An IntelliJ maven project for constructing LSOs (BuildKGRun.java), root individual extraction (RootEntRun.java), external axiom importing and entailment reasoning (XKnowRun.java)

## Onto/Entailments: Entailment closure of an example learning domain (output example of ./FlightOntology project)

## Flight_RL/Learn: Prediction input/output processing (ExtXY.py), CNN feature transfer implemented with Tensorflow 1.4.0 (CNN.py), Transferability measurement (TraEva.py) 

## Flight_RL/Explain: Inference of explanatory evidence

## Data/Sample: Input/output and learned CNN model of an example learning domain

## Data/ST_Result: Transferability index of soft transfer (FGI) of some example transfers

## Data/HT_Result: Transferability index of hard transfer (FSI) of some example transfers

For more details, please contact the authors.
