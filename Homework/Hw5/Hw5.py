from collections import defaultdict
import sys
import string
import re
from collections import Counter
import matplotlib.pyplot as plt

# identify the beginning of each parse tree
idfy = "(TOP END_OF_TEXT_UNIT)"

# input file
infile = sys.argv[1] 

def ngrams(words, n=2):
    pad = [None]*(n-1)
    grams = pad + words + pad
    return (tuple(grams[i:i+n]) for i in range(0, len(grams) - (n - 1)))

def getVocabSize(words):
	vocab = {}
	for i in range(0, len(words)):
		w = words[i]
		if w in vocab:
			vocab[w] = vocab[w] + 1
		else:
			vocab[w] = 1

	return len(vocab)


with open(infile) as f:
    content = "".join(line for line in f if not line.isspace())

sentences = content.split(idfy)

words_tags_list = []

for s in sentences:
	POS = [p.split(')')[0] for p in s.split('(') if ')' in p]
	if POS:
		t = " ".join(POS)
		for q in POS:
			words_tags_list += q.split(" ")
		



words_content = words_tags_list[1::2]

text = " ".join(words_content)
text = text.replace(" 0 ", " ")


processed_text = ""
for char in text:
	if char not in string.punctuation:
		processed_text = processed_text + char

# print (processed_text)

words = processed_text.lower().split(" ")

# print (words)

# words_count = Counter(words)
words_count = Counter(w for w in words if w != '')

#######################################################################
# 1. From the SnapshotBROWN.pos.all.txt file extract all
# word types and their frequencies. Sort the list of word types in 
# decreasing order based on their frequency. Draw a chart showing the
# relationship between the rank in the ordered list and the frequency
#(Zipf's Law). Do not stem but do ignore punctuation.
#######################################################################
print("\nThe Top {0} Frequent Word Types:".format(10))
top_word = []
top_freq = []
i = 1
idx = []
for w, count in words_count.most_common(10):
	top_word.append(w)
	idx.append(i)
	i = i + 1
	top_freq.append(count)
	print("{0}: {1}".format(w, count))

# Draw chart
plt.xticks(idx, top_word)
plt.plot(idx, top_freq)
plt.show()

print ("\n")
#######################################################################
# 2. Generate a Bigram Grammar from the above file. Perform
# add-one smoothing. Show the grammar before and after smoothing for
# the sentence "A similar resolution passed in the Senate".
#######################################################################


# build Bigram Grammar from the file
n = 2
words = processed_text.split(" ")
# print ('\n%d-grams =' % (n))
# print (list(ngrams(words, n)))

# show frequency
counts = defaultdict(int)
for ng in ngrams(words,n):
	counts[ng] += 1

# print (counts)

# print ('\nfrequencies of bigrams:')
# for c, ng in sorted( ( (c, ng) for ng, c in counts.items() ) , reverse=True):
#     print (c, ng)

probs = defaultdict(float)
smoothed_probs = defaultdict(float)
vocabSize = getVocabSize(words)

# print (vocabSize)

for c in counts:
	probs[c] = counts[c]/len(words)
	smoothed_probs[c] = (counts[c] + 1)/ (len(words) + vocabSize) 

# # print ("Before smoothing: \n")
# # print (probs)
# # print ("After smoothing: \n")
# # print (smoothed_probs)

sentence = "A similar resolution passed in the Senate"
words_sentence = sentence.split(" ")

p = 1 # prob before smmothing
sp = 1 # prob after smoothing
for ws in ngrams(words_sentence,n):
	p = p * probs[ws]
	if ws in smoothed_probs:	
		sp = sp * smoothed_probs[ws]
	else:
		sp = sp * (1/(len(words)+vocabSize))


print ("Sentence:", sentence)
print ("Probability before smoothing: ", p)
print ("Probability after smoothing: ", sp)
print ("\n")
