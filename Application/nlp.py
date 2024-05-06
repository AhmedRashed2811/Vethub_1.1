#------------------------------------------------------------------------------------------Importing Libraries
import json
import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import os

#------------------------------------------------------------------------------------------Importing the File of the Training Data
# Assuming 'intents.json' is located in the same directory as your Django app
file_path = os.path.join(os.path.dirname(__file__), 'intents.json')


with open(file_path, 'r') as json_file:
    intents = json.load(json_file)

#------------------------------------------------------------------------------------------Words Manipulation

#--------------------------------------------------------------------------Words Methods
#------------------------------------------------------Tokenize
def tokenize(sentence):
    sentence = sentence.lower()
    return nltk.word_tokenize(sentence)

#------------------------------------------------------Stemming
def stem(word):
    stemmer = LancasterStemmer()
    return stemmer.stem(word.lower())

#------------------------------------------------------Bag of Words "Vectorizing"
def bag_of_words(tokenized_sentence, all_words):
    tokenized = [stem(w) for w in tokenized_sentence] #Tokenizing each pattern
    bag = np.zeros(len(all_words), dtype = np.float32)         #Creating the bag of words and initialize it to zeros
    for idx, word in enumerate(all_words):
        if word in tokenized:
            bag[idx] = 1.0
    return bag


#--------------------------------------------------------------------------Applying Methods on Words
all_words = []      #Array will hold all words in the data
tags = []           #List  will hold all tags "Diseases"
xy = []             #List  will hold the pattern with the corresponding tag
counter = 0

for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intents['intents'][counter]['patterns']:
        w = tokenize(pattern)   #Tokenizing
        all_words.extend(w)
        xy.append((w,tag))
    counter += 1

stop_words = stopwords.words('english')
ignore_words = ['suffers','suffering', 'issue','problem','disease']
ignore_words = stop_words + ignore_words

all_words = [stem(w) for w in all_words if w.lower() not in ignore_words]   #Stemming

all_words = sorted(set(all_words))      #Sorting the words and remove duplicates
tags = sorted(set(tags))                #Sorting the tags and remove duplicates

#------------------------------------------------------------------------------------------Creating Dataset for Training
X_train = []
y_train = []


for (pattern_sentence,tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)  #Converting each pattern to a bag of words (1|0)
    X_train.append(bag)
    
    label = tags.index(tag)         #Labelling the tags
    y_train.append(label)           #Cross Entropy Loss
    
X_train = np.array(X_train)         #Converting the X_train to Numpy array to proceed
y_train = np.array(y_train)         #Converting the y_train to Numpy array to proceed


#------------------------------------------------------------------------------------------Creating ChatDataset Class for DataLoader
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train
        
    def __get_item__(self, index):
        return self.x_data[index], self.y_data[index]
    
    def __len__(self):
        return self.n_samples

def preprocessed_words():
    return (all_words, tags, X_train, y_train)


#------------------------------------------------------------------------------------------Building the NeuralNetwork
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes): #Building the Neural Network
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)  #hidden layer 1
        self.l2 = nn.Linear(hidden_size, hidden_size) #hidden layer 2
        self.l3 = nn.Linear(hidden_size, hidden_size) #hidden layer 3
        self.l4 = nn.Linear(hidden_size, hidden_size) #hidden layer 4
        self.l5 = nn.Linear(hidden_size, num_classes) #hidden layer 5
        self.relu = nn.ReLU()                         #Activation Function
        
    def forward(self, x):    #Forward Learning
        out = self.l1(x) 
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        out = self.relu(out)
        out = self.l4(out)
        out = self.relu(out)
        out = self.l5(out)
        return out


#------------------------------------------------------------------------------------------Building and Training the Model 

#--------------------------------------------------------------------------Building the Model

model_data = torch.load('data2.pth')
input_size = model_data['input_size']
hidden_size = model_data['hidden_size']
output_size = model_data['output_size']
all_words = model_data['all_words']
tags = model_data['tags']
model_state = model_data['model_state']
model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)
model.eval()



def predict(sentence):
    sentence = tokenize(sentence)             #Tokenize the input sentence
    X = bag_of_words(sentence, all_words)     #Vectorizing the sentence "1|0"
    X = X.reshape(1, X.shape[0])              #Reshaping (1 row: 1 sample, no. of columns)
    X = torch.from_numpy(X)                   #Converting to tensor

    output = model(X)                         #Applying the model to the input sentence
    _, predicted = torch.max(output, dim = 1) #Getting the maximum probability tag

    tag = tags[predicted.item()]              #Getting the tag name
    
    probs = torch.softmax(output, dim=1)      #Getting all probabilities
    prob = probs[0][predicted.item()]         #Getting the maximum probability
    probability = prob.item() *100
    
    for intent in intents["intents"]:
        if tag == intent["tag"]:
            temp = ""
            for prevention in intent['preventions']:
                temp += prevention
                temp += "\n"
            return (f"""Disease: {tag} \nPreventions: {temp} \nProbability: {probability:.4f}%""")
            
