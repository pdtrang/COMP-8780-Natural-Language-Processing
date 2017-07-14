import sys
import string
import re
from collections import Counter

# identify the beginning of each parse tree
idfy = "(TOP END_OF_TEXT_UNIT)"
# number of top frequent tags
n_top = 20

infile = sys.argv[1] 
outfile = sys.argv[2] # save one-line sentences to output file

##############################################################
# (i) [10 points] Write a Perl script that maps each parse tree in the
#    SnapshotBROWN.pos.all.txt file (see the website) into one-line
#    sentences as shown below. You should retain only the parts-of-speech
#    and the words from the parse trees. Each sentence should span a single
#    line in the outpute file.
##############################################################

with open(infile) as f:
    content = "".join(line for line in f if not line.isspace())

# print(content)

sentences = content.split(idfy)

print (sentences)

# print(sentences[0])
# print(sentences[1])

words_tags_list = []

fo = open(outfile, "w")

for s in sentences:
	POS = [p.split(')')[0] for p in s.split('(') if ')' in p]
	if POS:
		t = " ".join(POS)
		#print(t)
		fo.write(t + "\n")
		for q in POS:
			words_tags_list += q.split(" ")
		

fo.close()

#print(words_tags_list)

words = words_tags_list[1::2]
tags = words_tags_list[0::2]

##############################################################
# (ii) [10 points] Generate the hash of hashes from the clean file BROWN-clean.pos.txt .
##############################################################
h = {}
for w, t in zip(words,tags):
	if w not in h:
		h[w] = {t:1}
	else:
		if t not in h[w]:
			h[w][t]=1
		else:
			h[w][t] += 1

# print(h['the'])

##############################################################
# (iii) [10 points] In BROWN-clean.pos.txt detect the 20 most frequent tags. Report their frequency.
##############################################################
tags_count = Counter(tags)
print("The Top {0} Frequent Tags:".format(n_top))
for tag, count in tags_count.most_common(n_top):
	print("{0}: {1}".format(tag, count))


##############################################################
# (iv) [10 points] take the most frequent tag and use it to
# tag the words in all the sentences from the BROWN-clean.pos.txt file. 
# Report the performance of this tagger. See the slides for details on 
# how to measure the performance.
##############################################################
my_tags = []
for w in words:
	tag = max(h[w], key=lambda i: h[w][i])
	my_tags.append(tag)

count = 0
for mtag, tag in zip(my_tags,tags):
	if mtag == tag:
		count += 1
accuracy = float(count)/float(len(tags))

print("Performance of this tagger by accuracy: {0}".format(accuracy))
