import numpy as np
import random
class Scheduler:
    def __init__(self, crossoverrate, mutationrate, inputpath, maxgen=100):
        self.crossoverrate = crossoverrate
        self.mutationrate = mutationrate
        self.maxgen = maxgen
        self.matrixPath = inputpath 
        self.loadDataFromFile()

        self.lenReviewers = len(self.dataset)
        self.lenPapers = len(self.dataset[0]) - 1 

    def loadDataFromFile(self):
        self.dataset = np.loadtxt(self.matrixPath, delimiter = ",")

# distribute creates a random individual.
def distribute(s):
    # create a list of possible reviewers
    # with his position at s.dataset and the
    # number of papers can review.
    possibleReviewers = list()
    for i in range(0,len(s.dataset)):
        r = [i, s.dataset[i][-1]] 
        possibleReviewers.append(r)

    l = list()
    for i in range(s.lenPapers):
        num = random.randint(0, len(possibleReviewers) - 1)
        # get the position of reviwer at s.dataset.
        l.append(possibleReviewers[num][0])
        possibleReviewers[num][1] -= 1

        if possibleReviewers[num][1] <= 0:
            possibleReviewers.remove(possibleReviewers[num])
    return l 

def fitness(s, distribution):
    val = 0
    for i in range(0, len(distribution)):
        r = distribution[i]
        val += s.dataset[r][i]
    return val

# TODO: check if after crossover the individual
# respects the number of papers of reviewers.
def crossover(s, d1, d2):
    cutPoint = int(s.crossoverrate * len(d1))
    d3 = list()
    d4 = list()
    for i in range(0, cutPoint):
        d3.append(d1[i])
        d4.append(d2[i])
    for i in range(cutPoint, len(d1)): 
        d3.append(d2[i])
        d4.append(d1[i])
    return [d3, d4]


if __name__ == "__main__":
    s = Scheduler(0.7, 1, "matrix.txt")
    l1 = distribute(s)
    l2 = distribute(s)
    f = fitness(s, l1)
    print(l1)
    print(l2)
    print(f)
    ls = crossover(s, l1, l2)
    print(ls[0])
    print(ls[1])
