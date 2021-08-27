# INTERAL MODULE
#######################################################################
from app_module import *
# from database.app_connector import AppConnector
# from database.model.Patient import Patient
# from database.model.XrayImage import XrayImage
# from database.model.PatientHospitalizeInfor import Patient_hospitalize_infor
# from database.model.ImpImage import ImpImage
# from database.model.ImageInforToShow import ImageInforToShow
from DL_model.Detector import Detector
#######################################################################

# EXTERAL LIBRARY
#######################################################################
import sys, os, shutil
from PyQt5.QtCore import QDate, Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime, date
import random
from distutils.dir_util import copy_tree

import keras
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
import matplotlib.pyplot as plt
import cv2

import numpy as np
import time
import tensorflow as tf
#######################################################################

# TITLEBAR FUNCTION
#######################################################################
def removeTitleBar(MainWindow):
    MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
def setupTitleBar(ui):
    ui.btn_close.clicked.connect(closeWindow)
    ui.btn_minimize.clicked.connect(minimizeWindow)
    ui.btn_maximize_restore.clicked.connect(fullScreenWindow)
def closeWindow():
    dbconnector.myconn.close()
    sys.exit()
def minimizeWindow():
    MainWindow.showMinimized()
def fullScreenWindow():
    updateImage()
    if(MainWindow.isMaximized()):
        MainWindow.showNormal()
    else:
        MainWindow.showMaximized()
def closeSignInWindow():
    Form_Sign.close()
    MainWindow.show()
def popupWindow():
    calendarForm.show()
def turnOfPopupWindow():
    calendarForm.close()
#######################################################################

# MAIN MENU FUNCTION
#######################################################################

def getDateFromCalendar():
    currentDate = ui_Calendar.calendarWidget.selectedDate()
    date = currentDate.getDate()
    dateYear  = date[0]
    dateMonth = date[1]
    dateDay   = date[2]
    dateText = str(dateYear) + "-" + str(dateMonth) + "-" + str(dateDay)
    turnOfPopupWindow()
    ui.label_HospitalizeTimeInfor_inputMenu.setText(dateText)
    return dateText
def Imp_updatePatientInformation():
    # Impliment data
    Imp_PatientInfor = Patient(None, None, None, None, None, None, None, None)
    Imp_XrayImageInfor = XrayImage(None, None, None, None, None, None, None)
    Imp_PatientHospitalizeInfor = Patient_hospitalize_infor(None, None, None, None, None)
    # update Patient infor
    Imp_PatientInfor.ResidentNumber = ui.textbox_ResidentNumber_inputMenu.toPlainText()
    Imp_PatientInfor.HealthInsuranceID = ui.textbox_HealthInsuranceID_inputMenu.toPlainText()
    Imp_PatientInfor.PatientName = ui.textbox_PatientName_inputMenu.toPlainText()
    Imp_PatientInfor.birthyear = ui.comboBox_birthday_inputMenu.currentText()
    # Gender
    if ui.radioBtn_male_inputMenu.isChecked():
        Imp_PatientInfor.gender = 1
    else:
        if ui.radioBtn_female_inputMenu.isChecked():
            Imp_PatientInfor.gender = 0
    Imp_PatientInfor.job = ui.textbox_Job_inputMenu.toPlainText()
    Imp_PatientInfor.address = ui.textEdit_Address_inputMenu.toPlainText()
    # update
    dbconnector.patientInfor = Imp_PatientInfor
    # push patient information record to database
    dbconnector.pushPatientInfor()
    # update patient hospitalize information
    Imp_PatientHospitalizeInfor.hospitalizeTime = getDateFromCalendar()
    Imp_PatientHospitalizeInfor.hospitalizeLocation = ui.textbox_HospitalizeLocation_inputMenu.toPlainText()
    Imp_PatientHospitalizeInfor.hospitalizeSymptom = ui.textbox_PreSymptom_inputMenu.toPlainText()
    # update
    dbconnector.patientHospitalizeInfor = Imp_PatientHospitalizeInfor
    # push patient hospitalize information record to database
    dbconnector.pushPatientHospitalizeInfor()
    dbconnector.pushImpImageInfor()
    storeData()

# END OF DATABASE BEHAVIOR
#######################################################################

# FILE BEHAVIOR
#######################################################################

def storeData():
    currentPath = os.getcwd()
    temp_PathFile = currentPath + "/dataImage/TemporaryImage/"
    temp_StoredLocation = currentPath + "/dataImage/StoredImage/"
    os.chdir(temp_PathFile)
    tmp_fileList = os.listdir()
    tmp_targetFileList = tmp_fileList.copy()
    for tmp in range(0, len(tmp_fileList)):
        tmp_fileList[tmp] = temp_PathFile + tmp_fileList[tmp]
    for tmp in range(0, len(tmp_targetFileList)):
        tmp_targetFileList[tmp] = temp_StoredLocation + tmp_targetFileList[tmp]
    for tmp in range(0, len(tmp_fileList)):
        shutil.move(tmp_fileList[tmp], tmp_targetFileList[tmp])
    os.chdir(currentPath)
def loadRawImage():
    currentPath = os.getcwd()
    imp_OutputPathFile = currentPath + "/dataImage/TemporaryImage/"
    # rawImagePath = currentPath + "//dataImage//OriginalXrayImage//"
    filePath = loadFiles()
    for tmp in filePath:
        tmp_filename = getFileNameFromPath(tmp)
        outputPathFile = imp_OutputPathFile + getRandomText() + '.jpg'
        shutil.copy2(tmp, outputPathFile)
        # print(tmp)
    # update selectedbox
    updateListFile()
    
def updateListFile():
    currentPath = os.getcwd()
    imp_OutputPathFile = currentPath + "/dataImage/TemporaryImage/"
    os.chdir(imp_OutputPathFile)
    restFile = os.listdir()
    os.chdir(currentPath)
    if len(restFile)!=0:
        ui.comboBox_inputImage_inputMenu.clear()
        for tmp in restFile:
            ui.comboBox_inputImage_inputMenu.addItem(tmp)
        updateImage()
def resizePixmap(inPixmap, label):
    labelWidth   = label.width()
    labelHeight  = label.height()
    pixmapWidth  = inPixmap.width()
    pixmapHeight = inPixmap.height()
    ratioLabel   = labelWidth/labelHeight
    ratioPixmap  = pixmapWidth/pixmapHeight
    # inPixmap.scaledToHeight(pixmapHeight)
    # resize
    if ratioPixmap > ratioLabel:
        tmp_pixmapWidth = pixmapWidth
        pixmapWidth = labelWidth
        pixmapHeight = (labelWidth*pixmapHeight)/tmp_pixmapWidth
    else:
        if ratioPixmap < ratioLabel:
            tmp_pixmapHeight = pixmapHeight
            pixmapHeight = labelHeight
            pixmapWidth = (labelHeight*pixmapWidth)/tmp_pixmapHeight
    inPixmap = inPixmap.scaled(pixmapWidth, pixmapHeight)
    return inPixmap
def updateImage():
    # update image
    currentPath = os.getcwd()
    imp_OutputPathFile = currentPath + "/dataImage/TemporaryImage/"
    os.chdir(imp_OutputPathFile)
    listFile = os.listdir()
    if len(listFile) > 0:
        pixmap = QtGui.QPixmap(imp_OutputPathFile + ui.comboBox_inputImage_inputMenu.currentText())
        # print(imp_OutputPathFile + ui.comboBox_inputImage_inputMenu.currentText())
        pixmap = resizePixmap(pixmap, ui.label_imageUp_inputMenu)
        ui.label_imageUp_inputMenu.setPixmap(pixmap)
    os.chdir(currentPath)
# FEATURE FUNCTION
#######################################################################
def getRandomText():
    now = datetime.now()
    today = date.today()
    current_time = now.strftime("%Ho%Mo%S")
    current_date = today.strftime("%mo%do%y")
    randomNumber = int(random.random()*100000000)
    randomText = str(current_date)+'o'+str(current_time)+'o'+str(randomNumber)
    return randomText
def getFileNameFromPath(xfilePath):
    max = len(xfilePath)
    fileName = ""
    for i in range(max-1, 0, -1):
        if xfilePath[i] == '/':
            break
        fileName+=xfilePath[i]
    fileName = fileName[::-1]
    return fileName
def loadFiles():
    filter = "JPG (*.jpg);;PNG (*.png)"
    dialog = QtWidgets.QFileDialog()
    dialog.setWindowTitle("Select File")
    dialog.setNameFilter(filter)
    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
    file_full_path = ""
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        file_full_path+=str(dialog.selectedFiles())
    else:
        return None
    filePath = file_full_path.split(',')
    for i in range(0, len(filePath)):
        tmp = filePath[i]
        tmp = tmp.replace("'", '')
        tmp = tmp.replace('[', '')
        tmp = tmp.replace(']', '')
        tmp = tmp.replace(' ', '')
        filePath[i] = tmp
    return filePath
# END OF FEATURE FUNCTION
#######################################################################

#######################################################################
# LUNG ANALYSING MENU
def addItemTable(ImageInfor):
    ui.tableWidget_foundResident_LungMenu.setItem(ui.numberOfRowTable, 0, QtWidgets.QTableWidgetItem(str(ImageInfor.Name)))
    ui.tableWidget_foundResident_LungMenu.setItem(ui.numberOfRowTable, 1, QtWidgets.QTableWidgetItem(str(ImageInfor.Date)))
    ui.tableWidget_foundResident_LungMenu.setItem(ui.numberOfRowTable, 2, QtWidgets.QTableWidgetItem(str(ImageInfor.hospitalizeLocation)))
    ui.tableWidget_foundResident_LungMenu.setItem(ui.numberOfRowTable, 3, QtWidgets.QTableWidgetItem(str(ImageInfor.symptom)))
    ui.numberOfRowTable+=1
    if ui.numberOfRowTable > 3:
        ui.tableWidget_foundResident_LungMenu.setRowCount(ui.numberOfRowTable+1)
    
def searchData():
    keyWord = ui.textbox_ResidentNumber_LungMenu.toPlainText()
    dbconnector.searchAndPushForPatient(keyWord)
    for tmp in dbconnector.searchFoundImageShow:
        addItemTable(tmp)
def showImageLabelFromTable(row):
    if row > 0 and row < ui.numberOfRowTable:
        tmpPath = dbconnector.searchFoundImageShow[row-1].value.URLimage
        detector.selectedImage = dbconnector.searchFoundImageShow[row-1].value
        pixmap = QtGui.QPixmap(tmpPath)
        pixmap = resizePixmap(pixmap, ui.label_ImageUp_LungMenu)
        ui.label_ImageUp_LungMenu.setPixmap(pixmap)
# END OF LUNG ANALYSING MENU
#######################################################################

#######################################################################
# DETECTING
def setupModel():
    detector.loadModel()
def detectHeard():
    ui.progressBar_ImageAnalysing_LungMenu.setValue(20)
    detector.detection_on_image(detector.selectedImage, 1)
    ui.progressBar_ImageAnalysing_LungMenu.setValue(40)
    detector.detection_on_image(detector.selectedImage, 0)
    ui.progressBar_ImageAnalysing_LungMenu.setValue(60)
    detector.detection_on_image(detector.selectedImage, 2)
    ui.progressBar_ImageAnalysing_LungMenu.setValue(80)
    detector.detection_on_image(detector.selectedImage, 3)
    ui.progressBar_ImageAnalysing_LungMenu.setValue(100)
    # detector.detection_on_image(imgPath, 0)
    detector.DiagnosisResultGenerator()
# END OF DETECTING MODULE
#######################################################################

#######################################################################
# REPORT

def ShowReport():
    DevPath = os.getcwd()
    DevPath+="\\asset\\artboard2.png"
    # print(DevPath)
    DevPixmap = QtGui.QPixmap(DevPath)
    DevPixmap = resizePixmap(DevPixmap, Rp_ui.label_ImgPluraleffusion)
    Rp_ui.label_ImgPluraleffusion.setPixmap(DevPixmap)
    # print(detector.selectedImage.URLimage)
    if(updateOutput(detector.selectedImage)==1):
        Rp_Form.show()
def closeReport():
    Rp_Form.close()
def updateOutput(fileInfor):
    if(fileInfor != None):
        currentPath = os.getcwd()
        outputPath = currentPath + "\\dataImage\\OutputImage\\"
        # Specific path for each symptom
        BlurPointPath = outputPath + "BlurPoint\\"
        BigHeardPath = outputPath + "BigHeard\\"
        UndefinedObjectPath = outputPath + "UndefinedObject\\"
        PleuralEffusionPath = outputPath + "PluralEffusion\\"
        AtelectasisPath = outputPath + "Atelectasis\\"
        # search picture in directory
        os.chdir(BlurPointPath)
        listImage = os.listdir()
        for tmp in listImage:
            # Found ?
            if tmp==fileInfor.ImgName:
                # show diagnosis result
                # blur point
                rpBlurPixmap = QtGui.QPixmap(BlurPointPath+tmp)
                rpBlurPixmap = resizePixmap(rpBlurPixmap, Rp_ui.label_imgBlurpoint)
                Rp_ui.label_imgBlurpoint.setPixmap(rpBlurPixmap)
                # show result diagnosis
                Rp_ui.label_BlurpointSymptom.setText(detector.resultDiagnosis[2])
                # Big heard
                rpHeardPixmap = QtGui.QPixmap(BigHeardPath+tmp)
                rpHeardPixmap = resizePixmap(rpHeardPixmap, Rp_ui.label_ImgBigheard)
                Rp_ui.label_ImgBigheard.setPixmap(rpHeardPixmap)
                # show result diagnosis
                Rp_ui.label_BigheardSymptom.setText(detector.resultDiagnosis[0])
                # Undefined Object
                rpUOPixmap = QtGui.QPixmap(UndefinedObjectPath+tmp)
                rpUOPixmap = resizePixmap(rpUOPixmap, Rp_ui.label_UndefinedObject)
                Rp_ui.label_UndefinedObject.setPixmap(rpUOPixmap)
                # show result diagnosis
                Rp_ui.label_UndefinedObjectSymptom.setText(detector.resultDiagnosis[1])
                # Pleural Effusion
                PEPixmap = QtGui.QPixmap(PleuralEffusionPath + tmp)
                PEPixmap = resizePixmap(PEPixmap, Rp_ui.label_ImgPluraleffusion)
                Rp_ui.label_ImgPluraleffusion.setPixmap(PEPixmap)
                # show result diagnosis
                Rp_ui.label_PluralEffusionSymptom.setText(detector.resultDiagnosis[3])
                # Atelectasis
                AtelectasisPixmap = QtGui.QPixmap(AtelectasisPath + "artboard2.png")
                AtelectasisPixmap = resizePixmap(AtelectasisPixmap, Rp_ui.label_ImgAtelectasis)
                Rp_ui.label_ImgAtelectasis.setPixmap(AtelectasisPixmap)
                # show result diagnosis
                Rp_ui.label_AtelectasisSymptom.setText("Module is in internal verification\n and testing process.")
        os.chdir(currentPath)
        return 1
    else:
        # ui.btn_printResult_LungMenu.setToolTip("Search and Select image first.")
        msg = QtWidgets.QMessageBox()
        msg.setText("Search and Select image first.")
        x = msg.exec_()
        return None
    # read fileName:
#######################################################################

# MAIN FUNCTION
#######################################################################
if __name__ == "__main__":
    # CREATE OBJECT
    ###################################################################
    # UI APP
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ###################################################################

    # DATABASE CONNECTOR
    ###################################################################
    # dbconnector = AppConnector("localhost", "root", "123456", "bdoctordb")
    # dbconnector.connectTodataBase()
    ###################################################################

    # CONFIGURATION
    ###################################################################
    ui.setupUi(MainWindow)
    # hide title bar
    removeTitleBar(MainWindow)
    # setup title bar
    setupTitleBar(ui)
    # Open Sign Window
    Form_Sign = QtWidgets.QWidget()
    ui_Signin = Ui_Form_SignIn()
    ui_Signin.setupUi(Form_Sign)
    removeTitleBar(Form_Sign)

    # calendar form
    ###################################################################
    calendarForm = QtWidgets.QWidget()
    ui_Calendar = Ui_Calendar_Form()
    ui_Calendar.setupUi(calendarForm)
    calendarForm.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    ###################################################################

    # Report Form
    ###################################################################
    Rp_Form = QtWidgets.QWidget()
    Rp_ui = Ui_Form_Report()
    Rp_ui.setupUi(Rp_Form)
    Rp_Form.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    ui.btn_DetailResult_LungMenu.clicked.connect(ShowReport)
    Rp_ui.Done.clicked.connect(closeReport)
    ###################################################################
    # DETECTING
    ###################################################################
    detector = Detector()
    setupModel()
    ui.btn_analyse_LungMenu.clicked.connect(detectHeard)
    ###################################################################

    # Sign in component
    ###################################################################
    Form_Sign.show()
    ui_Signin.btn_SignIn.clicked.connect(closeSignInWindow)
    ###################################################################

    # Calendar form component
    ###################################################################
    getDateFromCalendar()
    ui_Calendar.btn_ok.clicked.connect(getDateFromCalendar)
    ###################################################################

    # Main menu component
    ###################################################################
    updateListFile()
    ui.btn_HospitalizeTime_inputMenu.clicked.connect(popupWindow)
    ui.btn_EnterInfor_inputMenu.clicked.connect(Imp_updatePatientInformation)
    ui.btn_inputLink_inputMenu.clicked.connect(loadRawImage)
    ui.comboBox_inputImage_inputMenu.currentIndexChanged.connect(updateImage)
    ui.btn_Search_LungMenu.clicked.connect(searchData)
    ui.tableWidget_foundResident_LungMenu.cellDoubleClicked.connect(showImageLabelFromTable)
    ###################################################################
    sys.exit(app.exec_())
