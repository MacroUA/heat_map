from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing import image
import keras.backend as K
import numpy as np
import cv2
import sys

#file = 'hare2.jpg'
#file = 'owl.jpg'
file = 'animals1.jpg'
path = './examples/'

Model_summary = False


model = VGG16(weights="imagenet")

if Model_summary:
    print(model.summary())
    input('press any key to continue')

img_path = path + file
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

preds = model.predict(x)

top_1 = decode_predictions(preds)[0]
print(top_1)
exit()


class_idx = np.argmax(preds[0]) #find the index of max preds[0]

class_output = model.output[:, class_idx]
last_conv_layer = model.get_layer("block5_conv3")

grads = K.gradients(class_output, last_conv_layer.output)[0]
pooled_grads = K.mean(grads, axis=(0, 1, 2))
iterate = K.function([model.input], [pooled_grads, last_conv_layer.output[0]])
pooled_grads_value, conv_layer_output_value = iterate([x])


for i in range(len(pooled_grads_value)): #512
#    print(pooled_grads_value[i])
    conv_layer_output_value[:, :, i] *= pooled_grads_value[i]

heatmap = np.mean(conv_layer_output_value, axis=-1)
heatmap = np.maximum(heatmap, 0)
heatmap /= np.max(heatmap)

img = cv2.imread(img_path)
heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
heatmap = np.uint8(255 * heatmap)
heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
superimposed_img = cv2.addWeighted(img, 0.5, heatmap, 0.5, 0)

cv2.imshow("Original", img)
#cv2.imshow("Heatmap", heatmap)
cv2.imshow("Hybrid", superimposed_img)

cv2.waitKey(0)