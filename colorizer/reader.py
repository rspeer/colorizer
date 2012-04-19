import simplenlp
from luminoso3.background_space import get_commonsense_assoc
from colorizer.color_data import make_lab_color_data, lab_to_rgb, rgb_to_hsv
from colorizer.colorvote import weighted_elect_samples

ENGLISH = simplenlp.get('en')
ASSOC = get_commonsense_assoc('en', 100)

class IncrementalColorizer(object):
    def __init__(self, ncolors):
        self.ncolors = ncolors
        self.colors = [(128,128,128)] * ncolors
        self.active_colors = [(128,128,128)] * (ncolors//2)
        self.colordata = dict(make_lab_color_data())
        self.votes = []

    def get_color_votes(self, concept, weight=1):
        votes = []
        if concept in self.colordata:
            morevotes = [(color, weight) for color in self.colordata[concept]]
            votes.extend(morevotes)
        similar = ASSOC.terms_similar_to_vector(
            ASSOC.vector_from_terms([(concept, 1)]))[:10]
        for sim, wsim in similar:
            if sim in self.colordata:
                morevotes = [(color, wsim*weight*0.25) for color in
                             self.colordata[sim]]
                votes.extend(morevotes)
        return votes

    def add_text(self, text):
        concepts = ENGLISH.extract_concepts(text)[-3:]

        self.add_concepts(concepts, 0.9)
        active_concept = None
        if (len(concepts) >= 3 and ' ' in concepts[-3]
            and concepts[-3] in self.colordata):
            active_concept = concepts[-3]
        elif len(concepts) >= 1 and concepts[-1] in self.colordata:
            active_concept = concepts[-1]
        
        self.colors = weighted_elect_samples(self.votes, self.ncolors)
        
        if active_concept:
            active_votes = self.get_color_votes(active_concept)
            print len(active_votes)
            self.active_colors = weighted_elect_samples(active_votes,
                                                        self.ncolors//2)
        return (self.colors, active_concept, self.active_colors)
        
    def add_concepts(self, concepts, old_weight):
        self.votes = [(b, w*old_weight) for (b, w) in self.votes][-10000:]
        weight = 1.0
        for concept in concepts[::-1]:
            self.votes.extend(self.get_color_votes(concept, weight))
            weight *= 0.9
        
        return self.votes


