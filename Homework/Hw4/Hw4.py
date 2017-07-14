# Extract from the BROWN file all grammar rules embedded in parse
# trees. Do not consider punctuation as a nonterminal. Eliminate
# numbers attached to non-terminals such as '-1', '-2', etc. Report 
# how many distinct rules you found, what are the 10 most frequent
# rules regardless of the non-terminal on the left-hand side, and
# what is the non-terminal with the most alternate rules (i.e. the
# non-terminal that can have most diverse structures). 

import sys
import string
import re
from collections import Counter

iden = "(TOP END_OF_TEXT_UNIT)"

# set of tags
tagset = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN",
"NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM",
"TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]


input_file = sys.argv[1]

# repository for grammar
grammar_repo = []

# read the input file and strip sentences in file
with open(input_file) as f:
    content = "".join(line.strip() for line in f if not line.isspace())

content = content.replace(iden,"").replace("("," ( ").replace(")"," ) ")

# process string (replace double space by single space)
s = content.replace("   ", " ").replace("  ", " ")

# find inner parenthesis (no-need-to-parse-grammar) or (lhs rhs) format
simple_grammars = re.findall("\([^\(\)]*\)", s)

# delete NONE
clean_grammars = [g for g in simple_grammars if "NONE" not in g]

# repeat until you cannot find any ( lhs rhs ) grammar
# add all simple grammar into grammar repository
# replace them with their head
while len(clean_grammars) > 0: 
    for simple_grammar in clean_grammars:
        grammar = simple_grammar.split(" ")
        lhs = grammar[1]
        rhs = grammar[2:-1]
        if (lhs, rhs) not in grammar_repo:
            grammar_repo.append((lhs, rhs))
        
        s = s.replace(simple_grammar, lhs)

    simple_grammars = re.findall("\([^\(\)]*\)", s)
    clean_grammars = [g for g in simple_grammars if "NONE" not in g]


# clean grammar repository
clean_grammar_repo = [g for g in grammar_repo if g[0] not in string.punctuation]

# In clean_grammar_repo, there are grammars end with words in sentences.
# for example: NN -> investigation, JJ-> primary
# we need to remove those grammar from our repo by checking whether the rhs is not in tagset or not

# remove redundant grammar
final_grammar_set = []
for g in clean_grammar_repo:
    clean = True
    for rhs in g[1]:
        if rhs not in tagset:
            clean = False
    if clean:
        final_grammar_set.append(g)


for g in final_grammar_set:
    t = g[0] + " ->"
    for ite in g[1]:
        t += " " + ite
    print(t)

# Print total distinct rules
print("Total distinct rules in file: ", len(final_grammar_set))

n_top = 10
print("\n10 most frequent rules regardless of the non-terminal on the left-hand side: ")

# Counter frequency of rules
non_ter_list = [g[0] for g in final_grammar_set]
rule_count = Counter(non_ter_list)
for rule, count in rule_count.most_common(n_top):
    print("{0}: {1}".format(rule, count))

print("\nThe non-terminal with the most alternative rules: ", rule_count.most_common(1)[0][0])
