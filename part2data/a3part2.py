import sys
import copy

manual_features = [["10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99"],
                    ["lt40", "ge40", "premeno"],
                    ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59"],
                    ["0-2", "3-5", "6-8", "9-11", "12-14", "15-17", "18-20", "21-23", "24-26", "27-29", "30-32", "33-35", "36-39"],
                    ["yes", "no"],
                    ["1", "2", "3"],
                    ["left", "right"],
                    ["left_up", "left_low", "right_up", "right_low", "central"],
                    ["yes", "no"]]

training_set = []
testing_set = []

no_recurrence_set = []
recurrence_set = []

all_features = []
no_recurrence_features = []
recurrence_features = []

no_recurrence_table = []
recurrence_table = []
all_features_table = []

class Feature:
    def __init__(self, feature_name):
        self.feature_name = feature_name
        self.feature_pairs = {}

class Instance:
    def __init__(self, features, category) -> None:
        self.features = features
        self.category = category

# Create all of the approprite features
def process_feature_names(feature_names):
    for feature in feature_names:
        all_features.append(Feature(feature))
        no_recurrence_features.append(Feature(feature))
        recurrence_features.append(Feature(feature))   

# Original method, but the data doesn't have all of the feature values in it 
# E.g. does not have any age = 10-19 which could cause errors in the testing
def process_features(values, feature_list):
    index = 0
    for value in values:
        current_feature = feature_list[index]
        if value not in current_feature.feature_pairs:
            current_feature.feature_pairs[value] = 1
        index = index + 1

# Manually load in all of the different feature values
def test_process_features(feature_list):
    for i in range(len(manual_features)):
        current_feature = feature_list[i]
        for j in range(len(manual_features[i])):
            current_feature.feature_pairs[manual_features[i][j]] = 1

# Count the occurance of each value in the training sets
def count_features(current_set, current_features):
    for instance in current_set:
        for i in range(len(instance.features)):
            current_features[i].feature_pairs[instance.features[i]] = current_features[i].feature_pairs[instance.features[i]] + 1

# Create the table with the appropriate probabilities
def populate_table(feature_list, population_size):
    feature_table = copy.deepcopy(feature_list)
    index = 0
    for feature in feature_table:
        for value in feature.feature_pairs.keys():
            feature.feature_pairs[value] = feature.feature_pairs[value] / (population_size + len(manual_features[index]))
        index = index + 1
    return feature_table

# Calculate the score for a test instance
def calc_score(population_size, feature_probabilities, test_features):
    #P(class | features) = (P(class) * P(features | class)) / P(features)
    current_feature_probs = []
    all_feature_probs = []
    index = 0
    for feature in feature_probabilities:
        current_feature_probs.append(feature.feature_pairs[test_features[index]])
        all_feature_probs.append(all_features_table[index].feature_pairs[test_features[index]])
        index = index + 1

    current_feature_product = 1 
    for prob in current_feature_probs:
        current_feature_product *= prob

    all_feature_product = 1
    for prob in all_feature_probs:
        all_feature_product *= prob

    probability = ((population_size/len(training_set)) * current_feature_product) / all_feature_product
    print(population_size/len(training_set))
    print(current_feature_product)
    print(all_feature_product)
    print()
    print()

    return probability

def write_to_file():
    file = open("sampleoutput.txt", "w")

    file.write("No-recurrence Probability: \t Recurrence Probability: \t Predicted Class: \t Actual Class: \n")

    for instance in testing_set:
        no_recurrence_prob = calc_score(len(no_recurrence_set), no_recurrence_table, instance.features)
        recurrence_prob = calc_score(len(recurrence_set), recurrence_table, instance.features)
        predicted_class = "no-recurrence"
        if no_recurrence_prob < recurrence_prob:
            predicted_class = "    recurrence"
        
        file.write(str(no_recurrence_prob) + "\t\t\t " + str(recurrence_prob) + "\t\t" + predicted_class + "\t\t\t" + instance.category + "\n")
    file.close()

def load_data():
    # Load in the 'breast-cancer-training' dataset
    with open(sys.argv[1]) as trainingSet:
        counter = 0; 
        for line in trainingSet:
            elements = line.split(",")
            elements[10] = elements[10].strip() # Delete new line char
            if counter == 0:  # Process the names of the cols as the feature names
                process_feature_names(elements[2:11])
            else:
                category = elements[1]
                training_set.append(Instance(elements[2:11], category))
            counter = counter + 1

    # Load in the 'breast-cancer-testing' dataset
    with open(sys.argv[2]) as testingSet:
        next(testingSet) # Skip the headers line
        for line in testingSet:
            elements = line.split(",")
            elements[10] = elements[10].strip()
            category = elements[1]
            testing_set.append(Instance(elements[2:11], category))


#Implementation/the main program:
if len(sys.argv) != 3:
    print("Error: wrong number of command line arguments")
    sys.exit(1)

load_data()

for i in training_set:
    if i.category == "no-recurrence-events":
        no_recurrence_set.append(i)
    else:
        recurrence_set.append(i)

# Note: "Initialise the count numbers to 1." from the sudo code is already done in process_features()
test_process_features(all_features)
test_process_features(no_recurrence_features)
test_process_features(recurrence_features)

count_features(training_set, all_features)
count_features(no_recurrence_set, no_recurrence_features)
count_features(recurrence_set, recurrence_features)

all_features_table = populate_table(all_features, len(training_set))
no_recurrence_table = populate_table(no_recurrence_features, len(no_recurrence_set))
recurrence_table = populate_table(recurrence_features, len(recurrence_set))

print("No-Recurrence Probabilities:")
for feature in no_recurrence_table:
    print(feature.feature_pairs)

print()
print("Recurrence Probabilities:")

for feature in recurrence_table:
    print(feature.feature_pairs)

write_to_file()