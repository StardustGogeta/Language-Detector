import math, re, samples
from collections import Counter

global unitTests
unitTests = 0

# How to use:
# - Create language with Language class
# - Train individual words or sentences with Language.teach()
# - Evaluate individual words or sentences with Language.evaluate()
# - Use LanguageCollection.evaluate() to test multiple languages at once
#   and receive the name of the best-fitting language

class LanguageCollection():
    def __init__(self, langs):
        self.langs = langs

    def evalCore(self,sample):
        best = ['',0]
        for lang in self.langs:
            c = lang.evaluate(sample)
            if c > best[1]:
                best[1] = c
                best[0] = lang.lang
        return best
    
    def runTestCase(self, sample, expectedBest, num):
        global unitTests
        best = self.evalCore(sample)
        if best[0] == expectedBest:
            if unitTests:
                print("Test {} passed successfully.".format(str(num)))
        else:
            print("Test {} failed: returned {} rather than expected {}.".format(num,best[0],expectedBest))
        
    def evaluate(self, sample): # Return best-fit language and score
        best = self.evalCore(sample)
        return best[0]+' with a confidence of '+str(best[1])

    def printFullEval(self,sample): # Print all languages, sorted by score.
        print('\n'.join(l[0]+' with a confidence of '+str(l[1]) for l in self.fullEvaluate(sample)))
        
    def fullEvaluate(self, sample): # Return all languages, sorted by score.
        langs = []
        for lang in self.langs:
            c = lang.evaluate(sample)
            langs.append([lang.lang,c])
        langs.sort(key = lambda x: -x[1])
        return langs
            
# Wrapper Language class spawns Neurons based on configuration
class Language():
    def __init__(self, lang, config = []):
        self.lang = lang
        self.brain = []
        self.config = config if config else [('pre',3),('suf',3),('mid',2),('pre',2),('mid',1),('suf',4),
                                             ('suf',2),('mid',3),('mid',4),('pre',1),('suf',1),('pre',4)]
        for c in self.config:
            self.brain += [NeuronGroup(*c)]
        for l in range(1,5):
            for _ in range(1): self.brain += [NeuronFrequency(l)]
            
    def teach(self, sample):
        sample = sample.lower()
        for word in re.findall(r"[a-z]+",sample):
            for neuron in self.brain:
                neuron.teach(word)
            
    def evaluate(self, sample):
        sample = sample.lower()
        con = [0,0]
        # Finding the average in one pass, rather than keeping a list.
        for word in re.findall(r"[a-z]+",sample):
            for neuron in self.brain:
                c = neuron.evaluate(word)
                con[0] = (con[0]*con[1]+c)/(con[1]+1)
                con[1] += 1
        return con[0]
    
# Parent class for all neuron types:
class Neuron():
    def __init__(self):
        self.lib = {}
        
# Subclass of Neuron built for groups of letters:
class NeuronGroup(Neuron):
    def __init__(self,location, length):
        self.location = location
        self.length = length
        Neuron.__init__(self)

    def getSubstr(self,sample):
        if self.location == 'pre':
            return sample[:self.length]
        elif self.location == 'suf':
            return sample[-self.length:]
        elif self.location == 'mid':
            return sample[int((len(sample)-self.length)/2):int((len(sample)+self.length)/2)]
        
    def teach(self, sample):
        sampleSubstr = self.getSubstr(sample) 
        if sampleSubstr in self.lib:
            self.lib[sampleSubstr] += 1
        else:
            self.lib[sampleSubstr] = 1
            
    def evaluate(self, sample):
        sampleSubstr = self.getSubstr(sample)
        if sampleSubstr in self.lib:
            confidence = 1 - math.e**-self.lib[sampleSubstr]
        else:
            confidence = 0
        return confidence
        
# Subclass of Neuron built for checking letter frequency: 
class NeuronFrequency(Neuron):
    def __init__(self, length):
        self.length = length
        Neuron.__init__(self)
    
    def getFreqs(self,sample):
        mostCommon = [x[0] for x in Counter(sample).most_common(self.length)]
        return ''.join(mostCommon)
        
    def teach(self, sample):
        freqs = self.getFreqs(sample)
        if freqs in self.lib:
            self.lib[freqs] += 1
        else:
            self.lib[freqs] = 1
            
    def evaluate(self, sample):
        freqs = self.getFreqs(sample)
        if freqs in self.lib:
            confidence = 1 - math.e**-self.lib[freqs]
        else:
            confidence = 0
        return confidence


# Use theme songs, poems, and books to train AI
Spanish = Language("Spanish")
Spanish.teach(samples.SpanishBase)
Spanish.teach(samples.SpanishAccents)
Spanish.teach(samples.Spanish1)

English = Language("English")
English.teach(samples.EnglishBase)
English.teach(samples.EnglishLevel1)
English.teach(samples.English1)
English.teach(samples.English2)
English.teach(samples.English3)

Dragon = Language("Dragon")
Dragon.teach(samples.DragonBase)
Dragon.teach(samples.Dragon1)

Latin = Language("Latin")
Latin.teach(samples.Latin1)

L = LanguageCollection([Spanish,English,Dragon,Latin])
L.runTestCase("This is an example of speech synthesis in English.",'English',1)
L.runTestCase("Es un ejemplo de palabras en español.",'Spanish',2)
L.runTestCase("Fus ro dah! Kol val kest!",'Dragon',3)
L.runTestCase("in principio creavit Deus caelum et terram",'Latin',4)
# L.evaluate("Insert text here!")
