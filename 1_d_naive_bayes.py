import csv
import random
# As file content is separated by space so I've used delimiter ' ' to read the file
csv.register_dialect('myDialect', delimiter = ' ')

# This function is used to load dataset from space seperated file.
def loadDataset(filename):
    with open(filename, "rt") as csvfile:
        lines = csv.reader(csvfile, dialect='myDialect')
        data = []
        dataset = list(lines)
        for x in range(len(dataset)-1):
            # This condition is there as I'm assuming first line of the file is column names 
            if(x != 0):
                for y in range(len(dataset[x])):
                    if(type(dataset[x][y]) == float):
                        dataset[x][y] = float(dataset[x][y])
                    else:
                        dataset[x][y] = dataset[x][y]
        return dataset

# This function is used to split train data into train and test data to build our model.
def splitDataIntoTrainAndTest(trainingSet, randomValue):
    trainDataSet = []
    testDataSet = []
    trainDataSet.append(trainingSet[0])
    del trainDataSet[0]
    for x in range(len(trainingSet)):
        if random.random() < randomValue:
            trainDataSet.append(trainingSet[x])
        else:
            testDataSet.append(trainingSet[x])
    retVar = {'trainDataSet': trainDataSet, 'testDataSet': testDataSet}
    return retVar

#This function is used to calculate all lables probability
def countClassLable(trainingSet, countClassLableFreq = {}):
    lablesProb = {}
    for i in range(len(trainingSet)):
        lablesProb[trainingSet[i][len(trainingSet[i])-1]]=0
        countClassLableFreq[trainingSet[i][len(trainingSet[i])-1]] = 0
    for i in range(len(trainingSet)):
        lablesProb[trainingSet[i][len(trainingSet[i])-1]] = lablesProb[trainingSet[i][len(trainingSet[i])-1]] + 1
        countClassLableFreq[trainingSet[i][len(trainingSet[i])-1]] = countClassLableFreq[trainingSet[i][len(trainingSet[i])-1]] + 1
    for lable in lablesProb:
        lablesProb[lable] = float(lablesProb[lable])/(len(trainingSet))
#     print(countClassLableFreq)
    return lablesProb

# This function is used to find number of unique strings among the data
def findUnique(trainDataSet, featureViseUnique):
    uniqueObj = {}
    for k in range(len(trainDataSet[0]) -1):
            featureViseUnique["f%s"%(k)] = 0
    for i in range(len(trainDataSet)):
        for j in range(len(trainDataSet[i]) -1):            
            if str(j)+'-'+str(trainDataSet[i][j]) in uniqueObj:
                continue
            else:
                uniqueObj[str(j)+'-'+str(trainDataSet[i][j])] = 1
                featureViseUnique["f%s"%(j)] = featureViseUnique["f%s"%(j)] + 1
    return featureViseUnique

#This function is used to calculate all features probability.
def calculateFeaturesprobability(trainDataSet,featuresProb, featuresColumn, featureViseUnique, countClassLableFreq):
    featureLength = len(trainDataSet[0])-1
    for j in range(featureLength):
        featuresProb["f%s" %(j)] = {}
        featuresColumn["f%s" %(j)] = {}
    featureViseUnique = findUnique(trainDataSet, featureViseUnique)
    for i in range(len(trainDataSet)):
        for j in range(featureLength):
            featuresColumn["f%s" %(j)][trainDataSet[i][j] + '~-~' + trainDataSet[i][featureLength]] = 0

    for i in range(len(trainDataSet)):
        for j in range(featureLength):
            featuresColumn["f%s" %(j)][trainDataSet[i][j] + '~-~' + trainDataSet[i][featureLength]] = featuresColumn["f%s" %(j)][trainDataSet[i][j] + '~-~' + trainDataSet[i][featureLength]] + 1
    
    for i in featuresColumn:
        for j in featuresColumn[i]:
            featuresProb[i][j] = float((float(featuresColumn[i][j]) + 1) / (float(countClassLableFreq[(j.split('~-~'))[1]]) + float(featureViseUnique[i])))
    return featuresProb # So called conditional probabilities
    
def predictTestData(data, conditionalProb, classLableProb, countClassLableFreq, featureViseUnique):
    prediction = {}
    testPred = {}
    for label in classLableProb:
        prediction[label] = float(classLableProb[label])
        count = 0
        for feature in data:
            prediction[label] = float(prediction[label]) * (float(conditionalProb['f%s'%count]['%s'%feature+'~-~'+'%s'%label]) if('%s'%feature+'~-~'+'%s'%label in conditionalProb['f%s'%count].keys()) else (float(1)/(float(countClassLableFreq[label]) + float(featureViseUnique['f%s'%count]))))
            count = count + 1
    probability = 0
    predictedValue = ""
    for key in prediction:
        if(prediction[key] > probability):
            probability = prediction[key]
            predictedValue = key
    return predictedValue

def Main():
    print("Started...")
    countClassLableFreq = {}
    trainingSet = loadDataset('./vertebrate.txt')
    del trainingSet[0]
    
    #Spliting using function (random spliting)
    bothSet = splitDataIntoTrainAndTest(trainingSet, 0.8)
    trainingSet = bothSet['trainDataSet']
    testDataSet = bothSet['testDataSet']
        
    #Manual splting is done below
    #testDataSet = []
    #testDataSet.append(trainingSet[14])
    #del trainingSet[14]
    
    trainDataSet = trainingSet
    
    #To load new testDataset file.
#     testDataSet = loadDataset('./vertebrate.txt')
    featuresColumn = {}
    classLableProb = countClassLable(trainingSet, countClassLableFreq) #so called prior probabilities
    print('PRIOR PROBABILITIES :')
    print(classLableProb)
    featuresProb = {}
    featureViseUnique = {}
    #likelihood
    conditionalProbabilities = calculateFeaturesprobability(trainDataSet, featuresProb, featuresColumn, featureViseUnique, countClassLableFreq)
    print('Likelihood :')
    print(conditionalProbabilities)
    print('PREDICTED CLASSES')
    for ind in range(len(testDataSet)):
        # pass only data row one by one here, if first row is names of the columns then uncomment below line
    #     if ind !=0:
        del testDataSet[ind][len(testDataSet[ind])-1]
        output = predictTestData(testDataSet[ind], conditionalProbabilities, classLableProb, countClassLableFreq, featureViseUnique)
        print('Predicted class is :', output, ' for given input: ',testDataSet[ind])
        
if __name__ == '__main__':
    Main()
