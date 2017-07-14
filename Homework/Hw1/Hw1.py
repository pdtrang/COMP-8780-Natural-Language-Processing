import sys
import os
import random
import string
from collections import Counter

# input file
infile = sys.argv[1] 

f = open(infile, "r")

#  count and remove punctuation
count = {}
s = ""  # s contains only words, no punctuation
for line in f:
	line = line.replace("\n", " ")
	for char in line:
		if char in string.punctuation:
			if (char in count) :
				count[char] = count[char] + 1
			else:
				count[char] = 1
		else:
			s = s + char


# change to lowercase
s = s.lower()
# split s by white space
words = s.split(" ")

for i in range(0, len(words)):
	if (words[i] in count):
		count[words[i]] = count[words[i]] + 1
	else:
		count[words[i]] = 1


# print (count,"\n")
# remove empty string in dictionary
del count['']

sorted_count = Counter(count).most_common(10)

print ("Top 10 most frequent words: \n", sorted_count)


