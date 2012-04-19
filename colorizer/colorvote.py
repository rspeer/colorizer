from colorizer.color_data import make_lab_color_data, lab_to_rgb, rgb_to_hsv
from collections import defaultdict
from luminoso3.background_space import get_commonsense_assoc
import numpy as np
import random
import simplenlp

HEADER = """
<!doctype html>
<html><body bgcolor="#999999">
<table>
"""

FOOTER = """
</table>
</body></html>
"""
ENGLISH = simplenlp.get('en')
ASSOC = get_commonsense_assoc('en', 100)

def euclidean_distance(vec1, vec2):
    if isinstance(vec1, tuple):
        vec1 = np.array(vec1)
    if isinstance(vec2, tuple):
        vec2 = np.array(vec2)
    return np.sqrt(np.sum((vec1-vec2)**2))

def elect_stv(candidates, ballots, nwinners):
    winners = []
    running = set(candidates)
    quota = int(len(ballots) / (nwinners+1.0)) + 1

    while len(winners) < nwinners:
        if len(running) == 0:
            break
        totals = defaultdict(int)
        for ballot in ballots:
            for vote in ballot:
                if vote in running:
                    totals[vote] += 1
                    break
        total_votes = totals.items()
        total_votes.sort(key=lambda x: -x[1])
        elected_one = False
        for candidate, votes in total_votes:
            if votes >= quota:
                winners.append(candidate)
                running.remove(candidate)
                elected_one = True
                break
        if not elected_one:
            loser = total_votes[-1][0]
            running.remove(loser)

    assert len(winners) <= nwinners

    return winners

def weighted_color_vote(candidates, ballots, nwinners):
    winners = []
    running = set(candidates)
    total = sum(b[1] for b in ballots)
    quota = int(total / (nwinners+1.0)) + 1

    # TODO: reward complementary colors
    while len(winners) < nwinners:
        if len(running) == 0:
            break
        totals = defaultdict(int)
        for ballot, weight in ballots:
            for vote in ballot:
                if vote in running:
                    totals[vote] += weight
                    break
        total_votes = totals.items()
        total_votes.sort(key=lambda x: -x[1])
        elected_one = False
        for candidate, votes in total_votes:
            if votes >= quota:
                winners.append(candidate)
                running.remove(candidate)
                elected_one = True
                break
        if not elected_one:
            loser = total_votes[-1][0]
            running.remove(loser)

    return winners

def elect_samples(colors, n=8):
    if len(colors) > 1000:
        samples = random.sample(colors, n*5)
        colors = random.sample(colors, 1000)
    elif len(colors) > n*5:
        samples = random.sample(colors, n*5)
        assert len(samples) == n*5
    else:
        samples = colors
    votes = []

    for color in colors:
        ratings = []
        for candidate in samples:
            ratings.append((euclidean_distance(color, candidate),
                tuple(candidate)))
        ratings.sort()
        vote = [r[1] for r in ratings]
        votes.append(vote)

    winners = elect_stv(samples, votes, n)
    return [lab_to_rgb(x) for x in winners]

def weighted_elect_samples(colorvotes, n=8):
    if len(colorvotes) > 1000:
        samples = random.sample(colorvotes, n*5)
        colorvotes = random.sample(colorvotes, 1000)
    elif len(colorvotes) > n*5:
        samples = random.sample(colorvotes, n*5)
        assert len(samples) == n*5
    else:
        samples = colorvotes
    
    candidates = [c for c, w in samples]
    votes = []
    for color, weight in colorvotes:
        ratings = []
        for candidate in candidates:
            ratings.append((euclidean_distance(color, candidate),
                tuple(candidate)))
        ratings.sort()
        vote = [r[1] for r in ratings]
        votes.append((vote, weight))

    winners = weighted_color_vote(candidates, votes, n)
    return [lab_to_rgb(x) for x in winners]

def make_html():
    out = open('color_samples.html', 'w')
    out.write(HEADER)
    colordata = make_lab_color_data()
    names = colordata.keys()
    names.sort()
    for colorname in names:
        colors = colordata[colorname]
        freq = len(colors)
        if freq >= 8:
            samples = elect_samples(colors, 8)
            if len(samples) == 8:
                print colorname, samples
                print >> out, "<tr>"
                for sample in samples:
                    print >> out, '<td bgcolor="#%02x%02x%02x" width="32">&nbsp;</td>' % sample
                print >> out, '<td>%s (%d)</td>' % (colorname, freq)
                print >> out, '</tr>'
    out.write(FOOTER)
    out.close()

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

if __name__ == '__main__':
    make_html()

