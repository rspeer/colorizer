import simplenlp
import math, random
from luminoso3.background_space import get_commonsense_assoc
from colorizer.color_data import make_lab_color_data, lab_to_rgb, rgb_to_hsv
from colorizer.colorvote import weighted_elect_samples

ENGLISH = simplenlp.get('en')
ASSOC = get_commonsense_assoc('en', 100)

COLORDATA = {}
origdata = make_lab_color_data()
for key, values in origdata.items():
    subset_values = random.sample(values,
      min(len(values), int(math.ceil(4*math.sqrt(len(values))))))
    COLORDATA[key] = subset_values


def output_colors(labcolors):
    return [lab_to_rgb(c) for c in sorted(labcolors)]

class IncrementalColorizer(object):
    def __init__(self, ncolors):
        self.ncolors = ncolors
        self.colors = [(128,128,128)] * ncolors
        self.active_colors = [(128,128,128)] * (ncolors//2)
        self.colordata = {}
        self._load_color_data()
        self.votes = []

    def _load_color_data(self):
        self.colordata = COLORDATA

    def get_color_votes(self, concept, weight=1):
        votes = []
        if concept in self.colordata:
            morevotes = [(color, weight) for color in self.colordata[concept]]
            votes.extend(morevotes)
        similar = ASSOC.terms_similar_to_vector(
            ASSOC.vector_from_terms([(concept, 1)]))[:3]
        for sim, wsim in similar:
            if sim in self.colordata:
                morevotes = [(color, wsim*weight*0.1) for color in
                             self.colordata[sim]]
                votes.extend(morevotes)
        return votes

    def add_text(self, text, force_stopword=False):
        active_concept = text
        active_concept_norm = ENGLISH.normalize(text).strip()
        if force_stopword or ENGLISH.is_stopword(text):
            return {
                'colors': output_colors(self.colors),
                'active': text,
                'activeColors': [],
                'weight': 0
            }
        active_votes = []
        if active_concept:
            active_votes = self.get_color_votes(active_concept_norm)
            if not active_votes and text.endswith('y'):
                active_concept_norm = ENGLISH.normalize(text[:-1]).strip()
                active_votes = self.get_color_votes(active_concept_norm)
            if not active_votes and text.endswith('ish'):
                active_concept_norm = ENGLISH.normalize(text[:-3]).strip()
                active_votes = self.get_color_votes(active_concept_norm)

            self.votes.sort(key=lambda v: v[1])
            self.votes = [(b, w*0.9) for (b, w) in self.votes[-400:]]
            self.votes.extend(active_votes)
            self.active_colors = weighted_elect_samples(active_votes,
                                                        self.ncolors//2+1)
        
            self.colors = weighted_elect_samples(self.votes, self.ncolors)
        return {
            'colors': output_colors(self.colors),
            'active': active_concept,
            'activeColors': output_colors(self.active_colors),
            'weight': len(active_votes)
        }
