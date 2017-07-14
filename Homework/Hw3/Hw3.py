import sys
import string
import re
import nltk
from collections import Counter
from nltk.tokenize import RegexpTokenizer

iden = "(TOP END_OF_TEXT_UNIT)"

train = sys.argv[1]
test = sys.argv[2]

# 25 sentences file
N_sentences = sys.argv[3]

########################################################################
# (i) [10 points] Use the assignment#2's hash of hashes to train a
# baseline lexicalized statistical tagger on the entire BROWN corpus.
########################################################################

# read training data
with open(train) as f:
    content = "".join(line for line in f if not line.isspace())

#print(content)

# read test data
with open(test) as f:
    content1 = "".join(line for line in f if not line.isspace())

# read 25 sentences
with open(N_sentences) as f:
	text = "".join(line for line in f if not line.isspace())

tokenizer = RegexpTokenizer(r'\w+')
tokens_from_N_sentences = tokenizer.tokenize(text)

# split content by iden
sentences = content.split(iden)

list_words_tags = []

# Get tags and words for training
for se in sentences:
	POS = [p.split(')')[0] for p in se.split('(') if ')' in p]
	if POS:
		t = " ".join(POS)
		# print(t)		
		for q in POS:
			list_words_tags += q.split(" ")
		
# print(list_words_tags)
words = list_words_tags[1::2]
tags = list_words_tags[0::2]


# split content by iden
sentences1 = content1.split(iden)

list_words_tags1 = []

# Get tags and words for testing on the Snapshot file
for se1 in sentences1:
	POS1 = [p.split(')')[0] for p in se1.split('(') if ')' in p]
	if POS1:
		t = " ".join(POS1)
		# print(t)		
		for q in POS1:
			list_words_tags1 += q.split(" ")
		
# print(list_words_tags)
words1 = list_words_tags[1::2]
tags1 = list_words_tags[0::2]

# Hash of hashes to train a baseline lexicalized statistical tagger on the entire BROWN corpus
h = {}
for w, t in zip(words,tags):
	if w not in h:
		h[w] = {t:1}
	else:
		if t not in h[w]:
			h[w][t] = 1
		else:
			h[w][t] += 1


########################################################################
# (ii) [20 points] Use the baseline lexicalized statistical tagger to tag 
# all the words in the SnapshotBROWN.pos.all.txt file. Evaluate and report the
# performance of this baseline tagger on the Snapshot file.
########################################################################

# Tag my taggers on Snapshot
my_tags1 = []
for w in words1:
	if w in h:
		tag = max(h[w], key=lambda i: h[w][i])
		my_tags1.append(tag)
	else:
		my_tags1.append("NA")

# print(tags1)
# print(my_tags1)

# Accuracy on Snapshot
c = 0
for mytag, t in zip(my_tags1, tags1):
	if mytag == t:
		c += 1
accuracy1 = float(c)/float(len(tags1))

print("Accuracy of baseline lexicalized tagger on Snapshot file: {0}".format(accuracy1))

########################################################################
# (iii) [20 points] add few rules to handle unknown words for the tagger
#    in (ii). The rules can be morphological, contextual, or of other
#    nature. Use 25 new sentences to evaluate this tagger (the (ii) tagger +
#    unknown word rules). You can pick 25 sentences from a news article
#    from the web and report the performance on those.
########################################################################

# Tag my taggers on 25 sentences
my_tags = []
for w in tokens_from_N_sentences:
	if w in h:
		tag = max(h[w], key=lambda i: h[w][i])
		my_tags.append(tag)
	else: # some alternative rules
		if w.endswith("ly"):
			my_tags.append("RB")
		elif w.endswith("ive"):
			my_tags.append("JJ")
		elif w.endswith("ness") or w.endswith("ion"):
			my_tags.append("NN")
		elif w.endswith("ions") or w.endswith("ses"):
			my_tags.append("NNS")
		elif w.isnumeric():
			my_tags.append("CD")
		elif w.endswith("ing"):
			my_tags.append("VBG")
		elif w.istitle():
			my_tags.append("NNP")
		elif w.endswith("ed"):
			my_tags.append("VBN")
		else: my_tags.append("NA")


# Accuracy on 25 sentences
nltk_tags = [ta[1] for ta in nltk.pos_tag(tokens_from_N_sentences)]

c = 0
for mytag, t in zip(my_tags, nltk_tags):
	if mytag == t:
		c += 1
accuracy = float(c)/float(len(nltk_tags))

print("Accuracy of my tagger on 25 sentences: {0}".format(accuracy))
