# Alunos:
# Caio Riyousuke Miyada Tokunaga, RGA: 201719040028
# Claudio Padilha da Silva, RGA: 201719040036
# Marco Ortavio Duarte de Almeida, RGA: 201519070365
# Rodrigo Schio Wengenroth Silva, RGA: 201719040010

import numpy as np
import random
import matplotlib.pyplot as plt
import sys


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
    # with their position at s.dataset and the
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

# fitness determines fitness function value.
def fitness(s, distribution):                                   
    val = 0
    for i in range(0, len(distribution)):
        r = distribution[i]
        val += s.dataset[r][i]
    return val

# create our inicial random set.
def createFirstPopulation (s):
    population = list()
    
    if s.lenReviewers < s.lenPapers:                                    # experimented some diferent relations here, I think this had the best result
        tam = s.lenPapers                                               # for varying matrices. Didn't really understand why...
    else:                                                                       
        tam = s.lenReviewers                                        

    for i in range(tam): 
        dist = distribution(s)                                           # Creates a population of the size of lenPapers
        element = Individual(dist, fitness(s, dist))
        population.append(element)                                       # Adds the new individual to the population
    population.sort(key=lambda individual: individual.fit, reverse=True) # This is sorted (greatest fitness to smallest)
    return population

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

def mutate(s, distribution): 
    x = random.randint(0,100)/100.0
    if x <= s.mutationrate:                                                     # Determines if the mutation will happen
        p1 = random.randint(0, len(distribution) - 1)                           # Choses a position on the state   
        p2 = random.randint(0, len(distribution) - 1)                           # choses another position on the state
        distribution[p1], distribution[p2] = distribution[p2], distribution[p1] # swaps the revisors from two random positions
    return distribution

def crossAndMutate(s, parent1, parent2):
    children = crossover(s, parent1, parent2)
    children[0] = mutate(s, children[0])
    children[1] = mutate(s, children[1])
    return children

def searchRoulette(roulette, num):
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
        # fitSum = 38, append 38. Numbers between [25, 38) will
        # select the population[1].
        fitSum += population[i].fit
        roulette.append(fitSum)

    l = list()
    for i in range(len(population)/2):
        n = random.randint(0, fitSum - 1)
        m = random.randint(0, fitSum - 1)
        p1 = searchRoulette(roulette, n)
        p2 = searchRoulette(roulette, m)
        pair = [population[p1], population[p2]]
        l.append(pair) 
    return l  

def reproduce(s, population, selectedPairs):
    newPopu = list()
    newPopu.append(population[0])                                                                       # sends the individual with the best fit to the
    for i in range(len(selectedPairs)):                                                                 # next generation
        kids = crossAndMutate(s, selectedPairs[i][0].distribution, selectedPairs[i][1].distribution)    
        elem0 = Individual(kids[0], fitness(s, kids[0]))
        elem1 = Individual(kids[1], fitness(s, kids[1]))                                                # cross and mutate individuals and put them on
        newPopu.append(elem0)                                                                           # the new generation
        newPopu.append(elem1)
    newPopu.sort(key=lambda individual: individual.fit, reverse=True) 
    return newPopu

# meansCalc calcs the average of all tries
# for each generation.
def meansCalc(allTries):
    means = list()
    for i in range(0, len(allTries[0])):
        mean = 0
        for j in range(0, len(allTries)):
            # sum the fitness of generation i
            # for all tries.
            mean += allTries[j][i].fit
        mean /= len(allTries)
        means.append(mean)
    return means

def findBestTry(allTries):
    best = 0
    for i in range(0, len(allTries)):
        if allTries[i][-1].fit > allTries[best][-1].fit:
            best = i
    return best

# plotGraph creates a image with best try and with
# the mean of all tries. Axis X represents the number
# of generation and Axis Y the fitness. The image is
# fitness.png.
def plotGraph(allTries):
    best = findBestTry(allTries)
    # Get the number of generations.
    xAxisValues = range(0, len(allTries[0]))
    yAxisValues = list()
    # Append only the best fitness of each generation of best try.
    for i in range(0, len(allTries[best])):
        yAxisValues.append(allTries[best][i].fit)
    line1 = plt.plot(xAxisValues, yAxisValues, label="melhor solucao")
    
    means = meansCalc(allTries)
    yMeansValues = list()
    # Append the average of all tries' best fitness.
    for i in range(0, len(means)):
        yMeansValues.append(means[i])
    line2 = plt.plot(xAxisValues, yMeansValues, label="media")

    plt.legend()
    plt.xlabel("generation")
    plt.ylabel("fitness")
    plt.savefig("fitness.png")

def alocator(crossoverrate, mutationrate, inputpath, maxgen=100):
    s = Scheduler(crossoverrate, mutationrate, inputpath, maxgen)

    allTries = list()
    for i in range(10):
        currentGeneration = createFirstPopulation(s)
        bestsOfGenerations = list()
        for j in range(s.maxgen):
            pairs =  select(s, currentGeneration)
            currentGeneration = reproduce(s, currentGeneration, pairs)
            bestsOfGenerations.append(currentGeneration[0])
        allTries.append(bestsOfGenerations)
    # Write the best combination and execution time to file. 
    with open("saida-genetico.txt", "w") as f:
        best = findBestTry(allTries)
        out = list()
        for i in range(0, len(allTries[best][-1].distribution)):
            out.append(allTries[best][-1].distribution[i] + 1)
        f.write("%s" % out[0])
        for i in range(1, len(out)):
            f.write(",%s" % out[i])
        f.close()
    # Save the graph to file.
    plotGraph(allTries)
    

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python alocacaoArtigos.py [crossoverrate] [mutationrate] [inputpath] [maxgen]")
    else: 
        csrate = float(sys.argv[1])
        mtrate = float(sys.argv[2])
        inputp = sys.argv[3]
        if len(sys.argv) > 4:
            alocator(csrate, mtrate, inputp, int(sys.argv[4]))
        else:
            alocator(csrate, mtrate, inputp)
