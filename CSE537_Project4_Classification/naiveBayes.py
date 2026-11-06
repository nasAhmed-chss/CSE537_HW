# naiveBayes.py
# -------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import util as util
import classificationMethod as classificationMethod
import math

class NaiveBayesClassifier(classificationMethod.ClassificationMethod):
  """
  See the project description for the specifications of the Naive Bayes classifier.
  
  Note that the variable 'datum' in this code refers to a counter of features
  (not to a raw samples.Datum).
  """
  def __init__(self, legalLabels):
    self.legalLabels = legalLabels
    self.type = "naivebayes"
    self.k = 1 # this is the smoothing parameter, ** use it in your train method **
    self.automaticTuning = False # Look at this flag to decide whether to choose k automatically ** use this in your train method **
    
  def setSmoothing(self, k):
    """
    This is used by the main method to change the smoothing parameter before training.
    Do not modify this method.
    """
    self.k = k

  def train(self, trainingData, trainingLabels, validationData, validationLabels):
    """
    Outside shell to call your method. Do not modify this method.
    """  
      
    # might be useful in your code later...
    # this is a list of all features in the training set.
    self.features = list(set([ f for datum in trainingData for f in datum.keys() ]));
    
    if (self.automaticTuning):
        kgrid = [0.001, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 20, 50]
    else:
        kgrid = [self.k]
        
    self.trainAndTune(trainingData, trainingLabels, validationData, validationLabels, kgrid)
      
  def trainAndTune(self, trainingData, trainingLabels, validationData, validationLabels, kgrid):
    """
    Trains the classifier by collecting counts over the training data, and
    stores the Laplace smoothed estimates so that they can be used to classify.
    Evaluate each value of k in kgrid to choose the smoothing parameter 
    that gives the best accuracy on the held-out validationData.
    
    trainingData and validationData are lists of feature Counters.  The corresponding
    label lists contain the correct label for each datum.
    
    To get the list of all possible features or labels, use self.features and 
    self.legalLabels.
    """

    "*** YOUR CODE HERE ***"
  
    # coutn everything from trainign data once
    labelCounts = util.Counter()
    featureOnCounts = util.Counter()
    for datum, label in zip(trainingData, trainingLabels):
      labelCounts[label] += 1
      for f, value in datum.items():
        if value > 0:
          featureOnCounts[(f, label)] += 1

    # Prior P(y) = c(y) / n  (not smoothed)
    n = float(len(trainingLabels))
    prior = util.Counter()
    for label in self.legalLabels:
      prior[label] = labelCounts[label] / n

    # try each k 
    bestAccuracy = -1
    bestK, bestCondProb = None, None
    for k in kgrid:
      #laplace smoothed conditional 
      condProb = util.Counter()
      for label in self.legalLabels:
        denom = labelCounts[label] + 2.0 * k
        for f in self.features:
          condProb[(f, label)] = (featureOnCounts[(f, label)] + k) / denom

      # evaluatie on validation data
      self.prior, self.condProb = prior, condProb
      guesses = self.classify(validationData)
      correct = sum(1 for g, t in zip(guesses, validationLabels) if g == t)
      accuracy = correct / float(len(validationLabels))

     
      if accuracy > bestAccuracy:
        bestAccuracy, bestK, bestCondProb = accuracy, k, condProb

    # store the parameters for the chosen k
    self.k = bestK
    self.prior = prior
    self.condProb = bestCondProb
        
  def classify(self, testData):
    """
    Classify the data based on the posterior distribution over labels.
    
    You shouldn't modify this method.
    """
    guesses = []
    self.posteriors = [] # Log posteriors are stored for later data analysis (autograder).
    for datum in testData:
      posterior = self.calculateLogJointProbabilities(datum)
      guesses.append(posterior.argMax())
      self.posteriors.append(posterior)
    return guesses
      
  def calculateLogJointProbabilities(self, datum):
    """
    Returns the log-joint distribution over legal labels and the datum.
    Each log-probability should be stored in the log-joint counter, e.g.    
    logJoint[3] = <Estimate of log( P(Label = 3, datum) )>
    
    To get the list of all possible features or labels, use self.features and 
    self.legalLabels.
    """
    logJoint = util.Counter()
    
    "*** YOUR CODE HERE ***"
    
    for label in self.legalLabels:
      if self.prior[label] == 0:
        # label never seen in traingin data
        logJoint[label] = float('-inf')
        continue
      logProb = math.log(self.prior[label])
      for f in self.features:
        pOn = self.condProb[(f, label)]
        if datum[f] > 0:
          logProb += math.log(pOn)        # P(f=1 | y)
        else:
          logProb += math.log(1.0 - pOn)  # P(f=0 | y)
      logJoint[label] = logProb
    
    return logJoint
  
  def findHighOddsFeatures(self, label1, label2):
    """
    Returns the 100 best features for the odds ratio:
            P(feature=1 | label1)/P(feature=1 | label2) 
    
    Note: you may find 'self.features' a useful way to loop through all possible features
    """
    featuresOdds = []
       
    "*** YOUR CODE HERE ***"
        
    #odds ratio = P(f=1 | y1) / P(f=1 | y2)
    odds = util.Counter()
    for f in self.features:
      odds[f] = self.condProb[(f, label1)] / self.condProb[(f, label2)]

    # sort features by odds ratio and return the top 100
    featuresOdds = sorted(self.features, key=lambda f: odds[f], reverse=True)[:100]

    return featuresOdds
    

    
      
