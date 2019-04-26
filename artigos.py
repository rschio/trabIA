import numpy as np
import random
import heapq
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

# checkReviewers check if distribution respects
# the max number of papers that reviewers can take.
def checkReviewers(s, distribution):
    reviewers = list()
    for i in range(0, len(s.dataset)):
        numPapers = s.dataset[i][-1] 
        reviewers.append(numPapers)
    for i in range(0, len(distribution)):
        r = distribution[i]
        reviewers[r] -= 1
        if reviewers[r] < 0:
            return False
    return True
    
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
    ds = [d3, d4]
    return ds

def mutate(s, d):
    x = int(s.mutationrate * len(d))
    for i in (0, x):
        p = random.randint(0, len(d) - 1)
        n = random.randint(0,5)
        d[p] = n
    return d

def crossAndMutate(s, d1, d2):
    ds = crossover(s, d1, d2)
    ds[0] = mutate(s, ds[0])
    ds[1] = mutate(s, ds[1])
    ret = []
    if checkReviewers(s, ds[0]):
        ret.append(ds[0])
    if checkReviewers(s, ds[1]):
        ret.append(ds[1])
    return ret

    
class HepElem:
    def __init__(self, pos, fit):
       self.pos = pos 
       self.fit = fit
    def __cmp__(self, other):
        return cmp(self.fit, other.fit)

# TODO: verificar o que eh selecao por
# roleta e implementar.
def select(s, distributions):
    h = list()
    heapq.heapify(h)
    for i in range(0, len(distributions)):
        f = fitness(s, distributions[i])
        e = HepElem(i, f)
        heapq.heappush(h, e)
        if len(h) > 200:
            heapq.heappop(h)
    selection = list()
    for i in range(0, len(h)):
        selection.append(distributions[h[i].pos])
    return selection

def genParents(s, number):
    parents = list()
    for i in range(0, number): 
        parents.append(distribute(s))
    return parents
    
def genChildren(s, parents):
    children = list()
    for i in range(0, len(parents)):
        for j in range(0, len(parents)):
            if i == j:
                continue
            cs = crossAndMutate(s, parents[i], parents[j])
            for k in range(0, len(cs)):
                children.append(cs[k])
    return children

def generationFit(s, distributions):
    maxFit = 0
    for i in range(0, len(distributions)):
        f = fitness(s, distributions[i])
        if f > maxFit:
            maxFit = f
    return maxFit

if __name__ == "__main__":
    s = Scheduler(0.7, 0.3, "matrix.txt")
    
    parents = genParents(s, 200)
    gensFit = list() 
    for i in range(0, 20):
        children = genChildren(s, parents)
        print("children:")
        print(len(children))
        parents = select(s, children)
        gensFit.append(generationFit(s, parents))
        #s.crossoverrate = random.uniform(0.6, 1)

    for i in range(0, len(gensFit)):
        print(gensFit[i])
