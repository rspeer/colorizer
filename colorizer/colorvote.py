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

def complement_bonus(winners, candidate):
    L1, a1, b1 = candidate
    weight = 1.0
    for L2, a2, b2 in winners:
        dotprod = (a1*a2 + b1*b2)/10000
        weight *= abs(dotprod)
    return weight

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

def weighted_elect_samples(colorvotes, n=8):
    if len(colorvotes) > 1000:
        samples = random.sample(colorvotes, n*10)
        colorvotes = random.sample(colorvotes, 500)
    elif len(colorvotes) > n*10:
        samples = random.sample(colorvotes, n*10)
    else:
        samples = colorvotes
    
    candidates = [c for c, w in samples]
    votes = []
    for labcolor, weight in colorvotes:
        color = np.array(labcolor)
        ratings = []
        for candidate in candidates:
            ratings.append((euclidean_distance(color, candidate),
                tuple(candidate)))
        ratings.sort()
        vote = [r[1] for r in ratings]
        votes.append((vote, weight))

    winners = weighted_color_vote(candidates, votes, n)
    return winners


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

if __name__ == '__main__':
    make_html()

