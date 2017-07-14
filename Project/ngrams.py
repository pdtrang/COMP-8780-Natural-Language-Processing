import sys
import string
import re
from collections import Counter, OrderedDict, defaultdict
from math import log10, isnan
import random

# input file
infile = sys.argv[1] 
# n
n = int(sys.argv[2])

def getVocabSize(words):
	vocab = {}
	for i in range(0, len(words)):
		w = words[i]
		if w in vocab:
			vocab[w] = vocab[w] + 1
		else:
			vocab[w] = 1

	return len(vocab)

def processCorpus(corpus, n):
	punct = string.punctuation.translate(str.maketrans("", "", ".?!'"))

	start_tkn = "<s>"
	end_tkn = "</s>"
	begin_tokens = ""
	for i in range(n-1):
		begin_tokens += ' ' + start_tkn

	start_tokens = " " + "</s>"
	start_tokens += begin_tokens + ' '
	
	processed_text = ""
	for ch in punct:
		processed_text = corpus.replace(ch, ' ' + ch + ' ')

	
	processed_text = processed_text.replace(".", " ." + start_tokens)
	processed_text = re.sub("(\!+\?|\?+\!)[?!]*", " \u203D" + start_tokens, processed_text)
	processed_text = re.sub("\!\!+", " !!" + start_tokens, processed_text)
	processed_text = re.sub("\?\?+", " ??" + start_tokens, processed_text)
	
	processed_text = processed_text.replace("  ", " ")
	processed_text = processed_text.replace("   ", " ")
	processed_text = processed_text.replace("    ", " ")

	tmp = processed_text.split()
	tokens = []
	for i in range(n-1):
		tokens.append(tmp.pop())

	tokens.extend(tmp)

	return tokens, processed_text

def dictionary_creator(freq_dict, wrd, words, total_words, n):
	if words:
		freq_tmp = freq_dict
		count_tmp = total_words[wrd]

		# Go through the dicts with the words
		for word in words[:-3]:
			if not freq_tmp or not freq_tmp[word]:
				freq_tmp[word] = defaultdict(dict)
			if not count_tmp or not count_tmp[word]:
				count_tmp[word] = defaultdict(dict)
			freq_tmp = freq_tmp[word]
			count_tmp = count_tmp[word]

		# Increase the counts
		if n > 3:
			if not count_tmp or not count_tmp[words[-3]]:
				count_tmp[words[-3]] = defaultdict(int)
			count_tmp[words[-3]][words[-2]] += 1

			if not freq_tmp or not freq_tmp[words[-3]]:
				freq_tmp[words[-3]] = defaultdict(dict)
			freq_tmp = freq_tmp[words[-3]]
		else:
			count_tmp[words[-2]] += 1

		if not freq_tmp or not freq_tmp[words[-2]]:
			freq_tmp[words[-2]] = defaultdict(int)
		freq_tmp[words[-2]][words[-1]] += 1

# 1-grams
def count_pairs_unigram(tokens, n):
    total_words = len(tokens)

    word_freq_pairs = dict.fromkeys(tokens, 0) # initialize map[key] value to 0
    
    for token in tokens:
        word_freq_pairs[token] += 1

    return total_words, word_freq_pairs

def unsmoothed_unigrams(word_freq_pairs, total_words):
    prob_dict = word_freq_pairs

    items = prob_dict.items()
    for word, count in items:
        prob_dict[word] = count / total_words

    return prob_dict

def smoothed_unigrams(word_freq_pairs, total_words, V):
    prob_dict = word_freq_pairs

    items = prob_dict.items()
    for word, count in items:
        prob_dict[word] = (count+1) / (total_words+V)

    return prob_dict
     
# bigrams
def count_pairs_bigram(tokens, n):
    start_token = '<s>'
    end_token = '</s>'

    total_words = Counter(tokens)
    total_words[end_token] -= 1  # Last token won't have a bigram
        
    word_freq_pairs = {word: defaultdict(int) for word in total_words}
    for i, token in enumerate(tokens[:-1]):
        word_freq_pairs[token][tokens[i+1]] += 1

    return total_words, word_freq_pairs

def unsmoothed_bigrams(word_freq_pairs, total_words):
    prob_dict = word_freq_pairs

    items = prob_dict.items()
    for word, follow_word_dict in items:
        follow_word_items = follow_word_dict.items()
        for word_infront, cnt in follow_word_items:
            follow_word_dict[word_infront] = cnt / total_words[word]

    return prob_dict

# n-grams     
def count_pairs_ngrams(tokens, n):
	dict_type = dict if n > 3 else int
	total_words = {token: defaultdict(dict_type) for token in tokens}
	word_freq_pairs = {token: defaultdict(dict) for token in tokens}

	# print (word_freq_pairs)
	words_infront = []
	for word in tokens[1:n]:
		words_infront.append(word)

	# print ("words in front", words_infront)

	# Count the ngrams as reading the tokens
	for i, token in enumerate(tokens[:-n]):
	    dictionary_creator(word_freq_pairs[token], token, words_infront, total_words, n)
	    del words_infront[0]
	    words_infront.append(tokens[i+n])
	token = tokens[-n]
	dictionary_creator(word_freq_pairs[token], token, words_infront, total_words, n)

	# for w in word_freq_pairs:
	# 	print (word_freq_pairs[w])

	return total_words, word_freq_pairs

def unsmoothed_ngrams(word_freq_pairs, total_words, n):
	prob_dict = word_freq_pairs
	# print (prob_dict)
	if n == 2:
		items = prob_dict.items()
		for word, follow_word_dict in items:
			follow_word_items = follow_word_dict.items()
			for word_infront, count in follow_word_items:
				follow_word_dict[word_infront] = count / total_words[word]
		return

	for word in prob_dict:
		unsmoothed_ngrams(prob_dict[word], total_words[word], n - 1)

	return prob_dict

def smooothed_ngrams(word_freq_pairs, total_words, n, V):
	stack = [(word_freq_pairs, total_words, n)]
	prob_dict = word_freq_pairs

	while stack:
		word_freq_pairs, total_words, tmp_n = stack.pop()
		if tmp_n == 2:
			items = word_freq_pairs.items()
			for top_word, follow_word_dict in items:
				follow_word_items = follow_word_dict.items()
				for bot_word, cnt in follow_word_items:
					follow_word_dict[bot_word] = ((cnt+1)/(total_words[top_word]+V))
		else:
			tmp_n -= 1
			for word in word_freq_pairs:
				stack.append((word_freq_pairs[word],total_words[word], tmp_n))

	return prob_dict

# Good Turing
# make a dictionary of how many times a word of a certain frequency occurs.
# def occurrenceMap(word_freq_pairs):    
#     keys = word_freq_pairs.keys()
#     occurence_map = dict.fromkeys(keys)
    
#     items = word_freq_pairs.items()
#     for wrd, follow_word_dict in items:
#         if follow_word_dict:
#             follow_word_vals = follow_word_dict.values()
#             top = max(follow_word_vals)
#             # itop = int(top)
#             occurence_map[wrd] = OrderedDict.fromkeys(range(1, top+2), 0)
#             follow_word_vals = follow_word_dict.values()
#             for value in follow_word_vals:
#             	occurence_map[wrd][value] += 1
#     return occurence_map
 
# generate sentencec based on probability distributions
def weightedPickN(words, prob_dict):
	for word in words:
		try:
			prob_dict = prob_dict[word]
			# print (word, len(prob_dict))
		except KeyError:
			return "</s>"

	s = 0.0
	key = ""
	values = prob_dict.values()
	r = random.uniform(0, sum(values))
	# r = max(values)
	# r = random.random()
	# print ("r ",r)
	items = prob_dict.items()
	# print ("items len ", len(items))
	for key, weight in items:
		# print (key)
		s = s + weight
		# print (s)
		if r < s:
			return key
	return key


def generateSentence(prob_dict, n):
	sentence = []
	words = ["<s>"]*(n-1)
	# print (words)

	word = weightedPickN(words, prob_dict)
	# print ("word ",word)
	endToken = "</s>"

	# print ("generate sentence ")
	while (word != endToken):
		# print ("word != endToken ")
		if n != 1:
			del words[0]
			words.append(word)
		
		sentence.append(word)
		# print (sentence)
		word = weightedPickN(words, prob_dict)
		# print (word)

	# print (sentence)
	# s = ' '.join(sentence)
	# print (s)
	return (' '.join(sentence))

with open(infile, 'r', errors="replace") as text:
	content = text.read()

# print (type(content))

tokens, processed_text = processCorpus(content, n)
# print ("processed ", processed_text)
# print ("tokens ", tokens)

if (n == 1):
	print ("Generate sentence with n = 1\n")
	total_words, word_freq_pairs = count_pairs_unigram(tokens, n)	
	prob_dict = unsmoothed_unigrams(word_freq_pairs, total_words)
	smoothed_prob_dict = smoothed_unigrams(word_freq_pairs, total_words, len(word_freq_pairs))
elif (n == 2):
	print ("Generate sentence with n = 2\n")
	total_words, word_freq_pairs = count_pairs_bigram(tokens, n)	
	prob_dict = unsmoothed_bigrams(word_freq_pairs, total_words)
	smoothed_prob_dict = smooothed_ngrams(word_freq_pairs, total_words, n, len(word_freq_pairs))
	# occurrence_map = occurrenceMap(word_freq_pairs)
	# prob_dictGT = goodTuring(word_freq_pairs, total_words, occurence_map)
else:
	print ("Generate sentence with n = ", n)
	total_words, word_freq_pairs = count_pairs_ngrams(tokens, n)
	prob_dict = unsmoothed_ngrams(word_freq_pairs, total_words, n)
	smoothed_prob_dict = smooothed_ngrams(word_freq_pairs, total_words, n, len(word_freq_pairs))

# for w in word_freq_pairs:
# 	print(word_freq_pairs[w])

# print ("\n ngrams \n")
# print (prob_dict)
# print ("\n smooothed_ngrams \n")
# print (smoothed_prob_dict)

# for w in smoothed_prob_dict:
# 	print(smoothed_prob_dict[w])

# print ("sentence with unsmoothed ngrams\n")
# generateSentence(prob_dict, n)
# print ("sentence with smoothed ngrams\n")
s = generateSentence(smoothed_prob_dict, n)
print (s)

# print ("sentence with smoothed ngrams Good Turing\n")
# s = generateSentence(prob_dictGT, n)
# print (s)
