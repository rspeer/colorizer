from colorizer.reader import IncrementalColorizer
import json

col = IncrementalColorizer(8)

def read_timing(filename):
    responses = []
    file = open(filename)
    for line in file:
        line = line.strip()
        if not line: continue
        parts = line.split(' ')
        time = float(parts[0])
        for word in parts[1:]:
            if word:
                stopword = True
                newline = False
                if word.startswith('|'):
                    word = word[1:]
                    newline = True
                if word.startswith('*'):
                    word = word[1:]
                    stopword = False
                response = col.add_text(word, stopword)
                response['time'] = time
                response['newline'] = newline
                responses.append(response)
                print response
            time += 0.1

    outfile = open(filename+'.out.json', 'w')
    json.dump(responses, outfile, indent=2)
    outfile.close()

read_timing('lewis-timing-excerpt.txt')
