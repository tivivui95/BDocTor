import mysql.connector
import os, sys
from database.model.Patient import Patient
from database.model.XrayImage import XrayImage
from database.model.ImpImage import ImpImage
from database.model.ImageInforToShow import ImageInforToShow
from database.model.PatientHospitalizeInfor import Patient_hospitalize_infor
class AppConnector():
    host = None
    user = None
    passwd = None
    database = None
    myconn = None
    cur = None
    currentID = None
    patientInfor = Patient(None, None, None, None, None, None, None, None)
    XrayImageInfor = XrayImage(None, None, None, None, None, None, None)
    XrayImageList = []
    searchFoundImage = []
    searchFoundImageShow = []
    patientHospitalizeInfor = Patient_hospitalize_infor(None, None, None, None, None)
    def __init__(self, hostStr, userStr, passwdStr, databaseStr):
        self.host = hostStr
        self.user = userStr
        self.passwd = passwdStr
        self.database = databaseStr
    def connectTodataBase(self):
        self.myconn = mysql.connector.connect(host = self.host, user = self.user, passwd = self.passwd, database = self.database)
        self.cur = self.myconn.cursor()
    def updatePatientInfor(self, ID, ResidentNumber, HealthInsuranceID, PatientName, birthyear, gender, job, address):
        self.patientInfor.ID = ID
        self.patientInfor.ResidentNumber = ResidentNumber
        self.patientInfor.HealthInsuranceID = ResidentNumber
        self.patientInfor.PatientName = PatientName
        self.patientInfor.birthyear = birthyear
        self.patientInfor.gender = gender
        self.patientInfor.job = job
        self.patientInfor.address = address
    def updateImageInfor(self, ID, patientID, URLImage, imageTime, symptom, imageDirection, imageSide):
        self.XrayImageInfor.ID = ID
        self.XrayImageInfor.patientID = ID
        self.XrayImageInfor.URLImage = URLImage
        self.XrayImageInfor.imageTime = imageTime
        self.XrayImageInfor.symptom = symptom
        self.XrayImageInfor.imageDirection = imageDirection
        self.XrayImageInfor.imageSide = imageSide
    def pushPatientInfor(self):
        sqlPatient = ("insert into bdoctordb.patient(ID, ResidentNumber, HealthInsuranceID, PatientName, birthyear, gender, job, address) "
                        "values (%s, %s, %s, %s, %s, %s, %s, %s)")
        PatientInforVal = (self.patientInfor.ID,
                           self.patientInfor.ResidentNumber,
                           self.patientInfor.HealthInsuranceID,
                           self.patientInfor.PatientName,
                           self.patientInfor.birthyear,
                           self.patientInfor.gender,
                           self.patientInfor.job,
                           self.patientInfor.address)
        try:
            #inserting the values into the table
            self.cur.execute(sqlPatient, PatientInforVal)
            #commit the transaction
            self.myconn.commit()
        except:
            self.myconn.rollback()
        print(self.cur.rowcount,"Patient record uploaded!")
        # self.myconn.close()
    def removeUnexpectedChar(self, nextID):
        nextID = nextID.replace(',', '')
        nextID = nextID.replace('(', '')
        nextID = nextID.replace(')', '')
        return nextID
    def getCurrentID(self):
        # Get number of current row of profile
        self.cur.execute("SELECT ID FROM bdoctordb.patient")
        allRecord = self.cur.fetchall()
        numberOfRecord = len(allRecord)
        nextID = allRecord[numberOfRecord-1]
        nextID = str(nextID)
        nextID = self.removeUnexpectedChar(nextID)
        self.currentID = nextID
    def pushPatientHospitalizeInfor(self):
        self.getCurrentID()
        self.patientHospitalizeInfor.patientID = self.currentID
        sqlPatientHospitalizeInfor = ("insert into PatientHospitalizeInfor(ID, patientID, hospitalizeTime, hospitalizeLocation, hospitalizeSymptom) " 
                        "values (%s, %s, %s, %s, %s)")
        PatientHospitalizeInforVal = (self.patientHospitalizeInfor.ID,
                                      self.patientHospitalizeInfor.patientID,
                                      self.patientHospitalizeInfor.hospitalizeTime,
                                      self.patientHospitalizeInfor.hospitalizeLocation,
                                      self.patientHospitalizeInfor.hospitalizeSymptom)
        try:
            #inserting the values into the table
            self.cur.execute(sqlPatientHospitalizeInfor, PatientHospitalizeInforVal)
            #commit the transaction
            self.myconn.commit()
        except:
            self.myconn.rollback()
        print(self.cur.rowcount,"Patient hospitalize record uploaded!")
    def addImage(self, ID, URLimage, ImgName, patientID):
        self.XrayImageList.append( ImpImage(ID, URLimage, ImgName, patientID) )
    def buildImpImageData(self):
        currentPath = os.getcwd()
        imp_OutputPathFile = currentPath + "/dataImage/TemporaryImage/"
        imp_StoredPathFile = currentPath + "/dataImage/StoredImage/"
        os.chdir(imp_OutputPathFile)
        listFile = os.listdir()
        listFileURL = listFile.copy()
        for i in range(0, len(listFileURL)):
            listFileURL[i] = imp_StoredPathFile + listFileURL[i]
        for i in range(0, len(listFileURL)):
            self.addImage(None, listFileURL[i], listFile[i], self.currentID)
        os.chdir(currentPath)
    def pushImpImageInfor(self):
        self.buildImpImageData()
        sqlImpImageData = ("insert into impxrayimage(ID, URLimage, ImgName, patientID) " 
                        "values (%s, %s, %s, %s)")
        for tmp in self.XrayImageList:
            Imp_XrayImageVal = (None,
                                tmp.URLimage,
                                tmp.ImgName,
                                tmp.patientID)
            try:
                #inserting the values into the table
                self.cur.execute(sqlImpImageData, Imp_XrayImageVal)
                #commit the transaction
                self.myconn.commit()
            except:
                self.myconn.rollback()
            print(self.cur.rowcount, tmp.ImgName, " uploaded!")
    def searchAndPushForPatient(self, keyWord):
        foundImageProfile = []
        self.cur.execute("SELECT id, PatientName FROM bdoctordb.patient WHERE ResidentNumber = %s"%(keyWord,))
        allRecord = self.cur.fetchall()
        tmpName = allRecord[0][1]
        tmpID = []
        for tmp in allRecord:
            tmpID.append(tmp[0])
        for tmp in tmpID:
            self.cur.execute("SELECT * FROM impxrayimage where patientID =%s"%(tmp,))
            foundImage = self.cur.fetchall()
            self.cur.execute("SELECT hospitalizeTime, hospitalizeLocation, hospitalizeSymptom FROM patienthospitalizeinfor where patientID =%s"%(tmp,))
            foundInfor = self.cur.fetchall()
            tmp_searchFoundImage = []
            for tmpImg in foundImage:
                self.searchFoundImageShow.append(ImageInforToShow(  tmpName,
                                                                    foundInfor[0][0],
                                                                    keyWord,
                                                                    foundInfor[0][1],
                                                                    foundInfor[0][2],
                                                                    ImpImage(tmpImg[0], tmpImg[1], tmpImg[2], tmpImg[3])))
    # def pushDetailXrayInformation(self):
