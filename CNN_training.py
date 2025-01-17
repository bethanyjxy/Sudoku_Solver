import numpy as np
import cv2
import os
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import tensorflow as tf

import pickle

### Parameters
path = 'Numbers'
testRatio = 0.2
validationRatio = 0.2
imageDimensions = (32, 32, 3)
###


images = []
classNo = []
myList = os.listdir(path)
numOfClass = len(myList)

print("Total Classes Detected:", numOfClass)
print("Importing Classes .......")
for x in range (0, numOfClass):
    myPicList = os.listdir(path + '/Sample' + str(x))
    for y in myPicList:
        img = cv2.imread(path + '/Sample' + str(x) + '/' + y)
        img = cv2.resize(img, (imageDimensions[0], imageDimensions[1]))
        images.append(img)
        classNo.append(x)
    print(x, end=' ')

print(" ")

images = np.array(images)
classNo = np.array(classNo)

## Split data
X_train, X_test, y_train, y_test = train_test_split(images, classNo, test_size=testRatio)
X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size=validationRatio)


print("Data Shapes")
print("Train", end='')
print(X_train.shape, y_train.shape)
print("Test", end='')
print(X_test.shape, y_test.shape)
print("Validation", end='')
print(X_validation.shape, y_validation.shape)

numOfSamples = []
for x in range(0, numOfClass):
    numOfSamples.append(len(np.where(y_train == x)[0]))

print(numOfSamples)

plt.figure(figsize=(10, 5))
plt.bar(range(0, numOfClass), numOfSamples)
plt.title("No of Images for each Class")
plt.xlabel("Class ID")
plt.ylabel("Number of Images")
plt.show()

def preProcessing(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.equalizeHist(img)
    img = img / 255
    return img

X_train = np.array(list(map(preProcessing, X_train)))
X_test = np.array(list(map(preProcessing, X_test)))
X_validation = np.array(list(map(preProcessing, X_validation)))

#img = X_train[30]
#img = cv2.resize(img, (300, 300))
#cv2.imshow("Preprocessed", img)
#cv2.waitKey(0)

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)
X_validation = X_validation.reshape(X_validation.shape[0], X_validation.shape[1], X_validation.shape[2], 1)



dataGen = tf.keras.preprocessing.image.ImageDataGenerator(width_shift_range=0.1,
                                                        height_shift_range=0.1,
                                                        zoom_range=0.2,
                                                        shear_range=0.1,
                                                        rotation_range=10)

dataGen.fit(X_train)
y_train = tf.keras.utils.to_categorical(y_train, numOfClass)
y_test = tf.keras.utils.to_categorical(y_test, numOfClass)
y_validation = tf.keras.utils.to_categorical(y_validation, numOfClass)

def myModel():
    noOfFilters = 60
    sizeOfFilter1 = (5, 5)
    sizeOfFilter2 = (3, 3)
    sizeOfPool = (2, 2)
    noOfNodes = 500

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Conv2D(noOfFilters, sizeOfFilter1, input_shape=(imageDimensions[0], imageDimensions[1], 1), activation='relu'))
    model.add(tf.keras.layers.Conv2D(noOfFilters, sizeOfFilter1, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=sizeOfPool))
    model.add(tf.keras.layers.Conv2D(noOfFilters // 2, sizeOfFilter2, activation='relu'))
    model.add(tf.keras.layers.Conv2D(noOfFilters // 2, sizeOfFilter2, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=sizeOfPool))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(noOfNodes, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(numOfClass, activation='softmax'))
    model.compile(tf.keras.optimizers.Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model = myModel()

print(model.summary())

######
batchSize = 50
epochsVal = 10
stepsPerEpoch = X_train // batchSize
######

history = model.fit(dataGen.flow(X_train, y_train, batch_size=batchSize),
                    steps_per_epoch=stepsPerEpoch,
                    epochs=epochsVal,
                    validation_data=(X_validation, y_validation),
                    shuffle=True)

plt.figure(1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.legend(['training', 'validation'])
plt.title('Loss')
plt.xlabel('epoch')

plt.figure(2)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(['training', 'validation'])
plt.title('Accuracy')
plt.xlabel('epoch')

plt.show()

score = model.evaluate(X_test, y_test, verbose=0)
print('Test Score = ', score[0])
print('Test Accuracy =', score[1])

model.save("model_trained.keras")

pickle_out = open("model_trained.p", "wb")
pickle.dump(model, pickle_out)
pickle_out.close()

