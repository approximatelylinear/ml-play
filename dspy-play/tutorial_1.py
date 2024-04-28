import os
import sys

repo_path = '.'
if repo_path not in sys.path:
    sys.path.append(repo_path)

import dspy

turbo = dspy.OpenAi(model='gpt-3.5-turbo')
colbertv2_wiki17_abstracts = dspy.ColBERTv2(
    url='http://20.102.90.50:2017/wiki17_abstracts'
)
dspy.settings.configure(
    lm=turbo,
    rm=colbertv2_wiki17_abstracts
)

# Process
#   - collect data
#   - write program
#   - define validation logic
#   - compile with dspy
#   - iterate

from dspy.datasets import HotPotQA

dataset = HotPotQA(
    train_seed=1, 
    train_size=20,
    eval_seed=2023,
    dev_size=50,
    test_size=0
)

trainset = [x.with_inputs('question') for x in dataset.train]
devset = [x.with_inputs('question') for x in dataset.dev]

len(trainset), len(devset)

