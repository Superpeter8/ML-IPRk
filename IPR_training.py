import numpy as np
import random
import math
from tensorflow import keras

random.seed(1)


# this function will return the distance between two given atoms
# two arrays in form of [x,y,z] should be provided, array2 is set to be the origin by default
def calculate_dis(array1, array2=[0, 0, 0]):
    sum = 0
    for x in array1:
        for y in array2:
            sum += (x - y) ** 2

    return math.sqrt(sum)


# this function will return a list of lists for each line in the file
# every sublist has the structure: [atom type, index for that atom, list of is coordinates]
def get_coordinates(info):
    atom = info[0::4]
    x = info[1::4]
    y = info[2::4]
    z = info[3::4]
    coordinates = []
    for i in range(len(atom)):
        coordinates.append([atom[i], i, [x[i], y[i], z[i]]])
    return coordinates


# this function will return a list of lists
# every sublist has the structure: [atom type, distance]
def get_distance(coordinates):
    distance = []
    for atom in coordinates:
        dis = calculate_dis(atom[2])
        distance.append([atom[0], dis])
    return distance


# this function will return the angle for 2 given atoms
def calculate_angle(array1, array2):
    cos = (array1[0] * array2[0] + array1[1] * array2[1] + array1[2] * array2[2]) / \
          (math.sqrt(array1[0] ** 2 + array1[1] ** 2 + array1[2] ** 2) * math.sqrt(
              array2[0] ** 2 + array2[1] ** 2 + array2[2] ** 2))
    if cos > 1:
        cos = 1
    angle = math.acos(cos)
    return angle


# this function will return a list of lists
# every sublist has the structure: [9 angles between other 9 atoms]
def get_angle(coordinates):
    Angles = []

    for atom1 in coordinates:

        angle = []

        for atom2 in coordinates:

            if atom1[1] == atom2[1]:

                continue

            else:
                angle.append(calculate_angle(atom1[2], atom2[2]))

        Angles.append(angle)

    return Angles


# this function will sort the processed data based on the distance with the atom and origin which is the second
# element of the sublist
def Sort(sub_li):
    l = len(sub_li)
    for i in range(0, l):
        for j in range(0, l - i - 1):
            if (sub_li[j][1] > sub_li[j + 1][1]):
                tempo = sub_li[j]
                sub_li[j] = sub_li[j + 1]
                sub_li[j + 1] = tempo
    return sub_li


# read the files
with open('./label.txt', "r") as label:
    label_list = []
    index = 0
    index0 = []
    index1 = []
    index2 = []
    for line in label:
        if float(line) < 0.1:  # define the threshold here for low IPR value
            label_list.append(0)
            index0.append(index)
        elif float(line) >= 0.4:  # define the threshold here for high IPR value
            label_list.append(1)
            index1.append(index)
        else:   # this one can be discard if the thresholds are set to the same value,
            # but it was kept here in case we want to enhance the characteristics of low IPR class
            label_list.append(2)
            index2.append(index)
        index += 1


with open('./data.txt', "r") as data:
    data_list = []
    for line in data:
        info = [float(point) for point in line.split(" ")]
        coordinates = get_coordinates(info)
        distance_list = get_distance(coordinates)
        angle_list = get_angle(coordinates)
        all_list = []   # create the list for data
        for i in range(len(distance_list)):
            sublist = all_list.append(distance_list[i] + angle_list[i])
            # the sublist has the structure: [atom type, distance, 9 angles], total of 11 features per input
        sorted_list = Sort(all_list)
        data_list.append(sorted_list)


random.shuffle(index0)
random.shuffle(index1)
index = index1 + index0[:len(index1) * 2]  # + index2[:len(index1)]
# using index to separate data for training and validation

random.shuffle(index)
cut_off = round(len(index) * 0.8)
# 80% of data are used for training
train_index = index[:cut_off]


# generating np arrays for training and validation
val_index = index[cut_off + 1:]
train_data, train_label, val_data, val_label = [], [], [], []

for i in train_index:
    train_data.append(data_list[i])
    train_label.append(label_list[i])

for i in val_index:
    val_data.append(data_list[i])
    val_label.append(label_list[i])

np_train_data = np.array(train_data)
np_train_label = np.array(train_label)
np_val_data = np.array(val_data)
np_val_label = np.array(val_label)

# the model need to be test more data
model = keras.Sequential([

    keras.layers.Flatten(input_shape=(10, 11)),

    keras.layers.Dense(110, activation='tanh'),

    keras.layers.Dense(64, activation='tanh'),

    keras.layers.Dense(16, activation='tanh'),

    keras.layers.Dense(8, activation='tanh'),

    keras.layers.Dense(2, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(np_train_data, np_train_label, epochs=70, batch_size=16)
test_loss, test_acc = model.evaluate(np_val_data, np_val_label, verbose=1)
# with the limited data we have now, the model has an accuracy around 60 - 70 percent.
predictions = model.predict(np_val_data)
print(predictions, np_val_label)
