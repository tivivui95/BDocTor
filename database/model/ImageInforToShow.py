from database.model.ImpImage import *
class ImageInforToShow():
    Name = None
    Date = None
    residentNumber = None
    symptom = None
    hospitalizeLocation = None
    value = ImpImage(None, None, None, None)
    def __init__(self, Name, Date, residentNumber, hospitalizeLocation, symptom, value):
        self.Name = Name
        self.Date = Date
        self.residentNumber = residentNumber
        self.hospitalizeLocation = hospitalizeLocation
        self.symptom = symptom
        self.value = value