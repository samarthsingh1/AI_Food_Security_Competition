

import spacy
from spacytextblob import spacytextblob


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("spacytextblob")

doc = nlp("This dashboard is fantastic!")
print("Polarity:", doc._.polarity)
print("Subjectivity:", doc._.subjectivity)