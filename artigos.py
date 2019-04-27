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

class Individual:
    def __init__(self, distribution, fit):
        self.distribution = distribution
        self.fit = fit

# creates a random state.
def distribution(s):
    # create a list of possible reviewers
    # with his position at s.dataset and the
    # number of papers can review.
    possibleReviewers = list()
    for i in range(0,len(s.dataset)):
        r = [i, s.dataset[i][-1]] 
        possibleReviewers.append(r)

    ret = list()
    for i in range(s.lenPapers):
        num = random.randint(0, len(possibleReviewers) - 1)
        # get the position of reviwer at s.dataset.
        ret.append(possibleReviewers[num][0])
        possibleReviewers[num][1] -= 1

        if possibleReviewers[num][1] <= 0:
            possibleReviewers.remove(possibleReviewers[num])
    return ret 

# fitness determines fitness function value
def fitness(s, distribution):                                   
    val = 0
    for i in range(0, len(distribution)):
        r = distribution[i]
        val += s.dataset[r][i]
    return val

# create our inicial random set
def createFirstPopulation (s):
    population = list()
    for i in range(s.lenPapers): 
        dist = distribution(s)                                                  # Creates a population of the size of lenPapers   ##### TRY TO CHANGE THIS VALUE LATER  ########
        element = Individual(dist, fitness(s, dist))
        population.append(element)                                              # Adds the new individual to the population
    return population.sort(key=lambda individual: individual.fit, reverse=True) # This is sorted (greatest fitness to smallest)

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
    
def crossover(s, parent1, parent2):  
    descendents = [parent1, parent2]                                              # Assumes crossover won't happen
    x = random.randint(0, 100) /100.0
    if x <= s.crossoverrate:                                                      # Verifies if crossover will happen
        valid = False
        i = 0
        while not valid and i in range(100):                                       # crossover parents until both children are valid or for 100 times 
            cutPoint = random.randint(0,len(parent1)-1)                           # Determines cutting point
            child1 = parent1[0 : cutPoint] + parent2[cutPoint : len(parent2)]      
            valid = checkReviewers(s, child1)                                     # verifies if the first mutation was valid
            child2 = parent2[0 : cutPoint] + parent1[cutPoint : len(parent1)]     
            valid = checkReviewers(s, child2)                                     # verifies if the second mutation was valid
            i+=1
        
        if valid:
            descendents = [child1, child2]                                        # updates the descendents if a valid state was generated
    return descendents

def mutate(s, d): 
    x = random.randint(0,100)/100.0
    if x <= s.mutationrate:                                     # Determines if the mutation will happen
        valid = False
        while not valid:                                        # generate new states until one of them is valid
            aux = d
            p = random.randint(0, len(d) - 1)                   # Choses a position on the state   
            n = random.randint(0,5)                             # choses a random reviewer
            aux[p] = n                                          # Creates new possible mutated state
            valid = checkReviewers(s, aux)                      # verifies if the mutation was valid
        d = aux                                                 # mutates the state
    return d

def crossAndMutate(s, parent1, parent2):
    children = crossover(s, parent1, parent2)
    children[0] = mutate(s, children[0])
    children[1] = mutate(s, children[1])
    return children

def searchRoulette(roulette, num):
    #TODO: use a binary search.
    i = 0
    for i in range(len(roulette)):
        if num < roulette[i]:
            break
    return i

def select(s, population):
    roulette = list()
    fitSum = 0
    for i in range(len(population)):
        # example 0: fitSum = 0 and population[0].fit = 25
        # fitSum = 25, append 25. Numbers between [0, 25) will
        # select the population[0].
        #
        # example 1: fitSum = 25 and population[1].fit = 13
        # fitSum = 38, append 38. Numbers between [25,38) will
        # select the population[1].
        fitSum += population[i].fit
        roullete.append(fitSum)

    l = list()
    for i in range(len(population)/2):
        n = random.randint(0, fitSum - 1)
        p1 = searchRoulette(roulette, n)
        p2 = 0
        # Try at max 100 times.
        for j in range(100): 
            m = random.randint(0, fitSum - 1)
            p2 = searchRoulette(roulette, m)
            if p1 != p2:
                pair = [population[p1], population[p2]]
                l.append(pair) 
                break
    return l  

def reproduce(s, population):
    newPopu = list()
    newPopu.append(population[0])                   # sends the individual with the highest fit to the next generation
    #TODO: function to create the next generetion

if __name__ == "__main__":
    s = Scheduler(0.7, 0.1, "matrix.txt")
    
