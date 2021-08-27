import keras
import cv2
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
import matplotlib.pyplot as plt
import numpy as np
import time
import os, sys
import tensorflow as tf

class Detector():
    selectedImage = None
    # Model
    HeardTrackingModel = None
    UndefinedObjectTrackingModel = None
    BlurPointTrackingModel = None
    PleuralEffusionTrackingModel = None
    # Output Path
    OutHeardPath = None
    OutUndefinedObjectPath = None
    OutBlurPointPath = None
    PleuralEffusionPath = None
    # Label
    labels_to_BlurPoint = {0: 'blur_point'}
    labels_to_Heard = {0: 'Heard'}
    labels_to_UndefinedObject = {0: 'Undefined Object'}
    Labels_to_PleuralEffusion = {0: 'Pleural Effusion'}
    # out value
    Listresult = [None, None, None, None]
    resultDiagnosis = [None, None, None, None]
    def get_session(self):
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        return tf.compat.v1.Session(config=config)
    def loadModel(self):
        currentPath = os.getcwd()
        modelPath = currentPath + "\\DL_model\\model\\"
        # Heard Tracking
        modelHeardPath = modelPath + "Heard_tracking_model.h5"
        self.HeardTrackingModel = models.load_model(modelHeardPath, backbone_name='resnet50')
        self.OutHeardPath = currentPath + "\\dataImage\\OutputImage\\BigHeard\\"
        # Undefined Object
        modelUndefinedObjectPath = modelPath + "UndefinedObject_tracking_model.h5"
        self.UndefinedObjectTrackingModel = models.load_model(modelUndefinedObjectPath, backbone_name='resnet50')
        self.OutUndefinedObjectPath = currentPath + "\\dataImage\\OutputImage\\UndefinedObject\\"
        # Blur Point
        BlurPointTrackingPath = modelPath + "Blur_Tracking_Model.h5"
        self.BlurPointTrackingModel = models.load_model(BlurPointTrackingPath, backbone_name='resnet50')
        self.OutBlurPointPath = currentPath + "\\dataImage\OutputImage\BlurPoint\\"
        # Pleural Effusion
        PleuralEffusionTrackingPath = modelPath + "PluralEffusion_tracking_model.h5"
        self.PleuralEffusionTrackingModel = models.load_model(PleuralEffusionTrackingPath, backbone_name='resnet50')
        self.PleuralEffusionPath = currentPath + "\\dataImage\OutputImage\\PluralEffusion\\"
    def detection_on_image(self, image_path, mode):
        # establish parameter
        model = None
        labels_to_names = None
        outPutDirectory = None
        # core
        currentPath = os.getcwd()
        # OutputPathDic = currentPath + "\\dataImage\\OutputImage\\" + image_path.ImgName
        Count = 0
        image = cv2.imread(image_path.URLimage)
        draw = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = preprocess_image(image)
        image, scale = resize_image(image)
        if mode == 0:
            model = self.HeardTrackingModel
            labels_to_names = self.labels_to_Heard
            outPutDirectory = self.OutHeardPath + image_path.ImgName
        else:
            if mode == 1:
                model = self.UndefinedObjectTrackingModel
                labels_to_names = self.labels_to_UndefinedObject
                outPutDirectory = self.OutUndefinedObjectPath + image_path.ImgName
            else:
                if mode == 2:
                    model = self.BlurPointTrackingModel
                    labels_to_names = self.labels_to_BlurPoint
                    outPutDirectory = self.OutBlurPointPath + image_path.ImgName
                else:
                    if mode == 3:
                        model = self.PleuralEffusionTrackingModel
                        labels_to_names = self.Labels_to_PleuralEffusion
                        outPutDirectory = self.PleuralEffusionPath + image_path.ImgName
        # print(OutputPathDic)
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
        boxes /= scale

        def isPath(x, y):
            if (max(x[0], y[0]) <= min(x[2], y[2]) and max(x[1], y[1]) <= min(x[3], y[3])):
                return True
            return False
        
        vector = []
        
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            if score < 0.4:
                break
            vector.append(box)
        
        b = [0 for _ in range(len(vector))]
        d = [[] for _ in range(len(vector) + 1)]
        
        def DFS(u):
            b[u] = Count
            d[Count].append(u)
            for v in g[u]:
                if (b[v] == 0):
                    DFS(v)

        g = [[] for _ in range(len(vector))]
        for i in range(len(vector)):
            for j in range(i + 1, len(vector)):
                if (isPath(vector[i], vector[j])):
                    g[i].append(j)
                    g[j].append(i)

        for i in range(len(vector)):
            if (b[i] == 0):
                Count += 1
                DFS(i)
        
        vectorBoxes = []
        vectorScores = np.array([])
        vectorLabels = np.array([])
        
        for i in range(1, Count + 1):
            minx = 1000000
            maxx = -1000000
            miny = 1000000
            maxy = -1000000
            maxScore = 0
            label = ""
            for j in d[i]:
                label = labels[0][j]
                minx = min(minx, vector[j][0])
                miny = min(miny, vector[j][1])
                maxx = max(maxx, vector[j][2])
                maxy = max(maxy, vector[j][3])
                maxScore = max(maxScore, scores[0][j])
            vectorBoxes.append([minx, miny, maxx, maxy])
            vectorScores = np.append(vectorScores, maxScore)
            vectorLabels = np.append(vectorLabels, label)
        self.Listresult[mode] = vectorBoxes
        for box, score in zip(vectorBoxes, vectorScores):
            box = np.array(box)
            label = 0
            if score < 0.4:
                break

            color = label_color(label)
            b = box.astype(int)
            draw_box(draw, b, color=color)
            caption = "{} {:.3f}".format(labels_to_names[label], score)
            draw_caption(draw, b, caption)

        detected_img =cv2.cvtColor(draw, cv2.COLOR_RGB2BGR)
        cv2.imwrite(outPutDirectory, detected_img)
    def DiagnosisResultGenerator(self):
        for i in range(0, 4):
            if i == 0:
                self.resultDiagnosis[i] = self.GenStringBigHeard(self.Listresult[i])
            else:
                if i == 1:
                    self.resultDiagnosis[i] = self.GenString(self.Listresult[i])
                else:
                    if i == 2:
                        self.resultDiagnosis[i] = self.GenStringBlurPoint(self.Listresult[i])
                    else:
                        if i == 3:
                            self.resultDiagnosis[i] = self.GenString(self.Listresult[i])
    def GenString(self, Pos):
        Str = "Tracking result:\n-----------------\n"
        if Pos == None:
            Str+="\nNot Found."
        else:
            Str+="\nFound " + str(len(Pos)) + " component.\n"
            for i in range (0, len(Pos)):
                Str+=str(i+1)+". "
                Str+="Position: x: " + str(int(Pos[i][0])) + " y: " + str(int(Pos[i][1]))
                Str+="\n   Size: "
                height = abs(Pos[i][3]-Pos[i][1])
                width = abs(Pos[i][2]-Pos[i][0])
                height = height*0.15625
                width = width*0.15625
                height = (int(height*100))/100
                width = (int(width*100))/100
                Str+= str(width) + "x" + str(height) + "cm.\n"
        return Str
    def GenStringBigHeard(self, Pos):
        Str = "Tracking result:\n-----------------\n"
        if Pos == None:
            Str+="\nNot Found."
        else:
            Str+="\nBig heard shadow detected.\n"
            for i in range (0, len(Pos)):
                Str+=str(i+1)+". "
                Str+="Position: x: " + str(int(Pos[i][0])) + " y: " + str(int(Pos[i][1]))
                Str+="\n   Size: "
                height = abs(Pos[i][3]-Pos[i][1])
                width = abs(Pos[i][2]-Pos[i][0])
                height = height*0.15625
                width = width*0.15625
                height = (int(height*100))/100
                width = (int(width*100))/100
                Str+= str(width) + "x" + str(height) + "cm.\n"
        return Str
    def GenStringBlurPoint(self, Pos):
        Str = "Tracking result:\n-----------------\n"
        if Pos == None:
            Str+="\nNot Found."
        else:
            Str+="\nFound " + str(len(Pos)) + " component.\n"
            for i in range (0, len(Pos)):
                Str+=str(i+1)+". "
                Str+="Position: x: " + str(int(Pos[i][0])) + " y: " + str(int(Pos[i][1]))
                Str+="\n   Size: "
                height = abs(Pos[i][3]-Pos[i][1])
                width = abs(Pos[i][2]-Pos[i][0])
                height = height*0.15625
                width = width*0.15625
                height = (int(height*100))/100
                width = (int(width*100))/100
                Str+= str(width) + "x" + str(height) + "cm.\n"
                Str+= "   Shape: Medium.\n"
        return Str

