import simplenlp
import math, random
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
        self.colordata = {}
        self._load_color_data()
        self.votes = []

    def _load_color_data(self):
        origdata = make_lab_color_data()
        for key, values in origdata.items():
            subset_values = random.sample(values,
              int(math.ceil(math.sqrt(len(values)))))
            self.colordata[key] = subset_values

    def get_color_votes(self, concept, weight=1):
        votes = []
        if concept in self.colordata:
            morevotes = [(color, weight) for color in self.colordata[concept]]
            votes.extend(morevotes)
        similar = ASSOC.terms_similar_to_vector(
            ASSOC.vector_from_terms([(concept, 1)]))[:10]
        for sim, wsim in similar:
            if sim in self.colordata:
                morevotes = [(color, wsim*weight*0.1) for color in
                             self.colordata[sim]]
                votes.extend(morevotes)
        return votes

    def add_text(self, text):
        active_concept = None
        active_concept_norm = None
        tokens = ENGLISH.tokenize(text).split()
        for pos in xrange(len(tokens)):
            if not ENGLISH.is_stopword(tokens[pos]):
                suffix = ENGLISH.untokenize(' '.join(tokens[pos:]))
                if ENGLISH.normalize(suffix) in self.colordata:
                    active_concept = suffix
                    active_concept_norm = ENGLISH.normalize(suffix)
                    break

        if active_concept:
            active_votes = self.get_color_votes(active_concept_norm)
            self.votes = [(b, w*0.9) for (b, w) in self.votes[-1000:]]
            self.votes.extend(active_votes)
            self.active_colors = weighted_elect_samples(active_votes,
                                                        self.ncolors//2)
        
            self.colors = weighted_elect_samples(self.votes, self.ncolors)
        return {
            'colors': self.colors,
            'active': active_concept,
            'active_colors': self.active_colors
        }
        
    def add_concepts(self, concepts, old_weight):
        self.votes = [(b, w*old_weight) for (b, w) in self.votes][-1000:]
        weight = 1.0
        for concept in concepts[::-1]:
            somevotes = self.get_color_votes(concept, weight)
            self.votes.extend(somevotes)
            weight *= 0.9
        
        return self.votes

