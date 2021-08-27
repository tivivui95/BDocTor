class Patient_hospitalize_infor:
    ID = None
    patientID = None
    hospitalizeTime = None
    hospitalizeLocation = None
    hospitalizeSymptom = None
    def __init__(self, ID, patientID, hospitalizeTime, hospitalizeLocation, hospitalizeSymptom):
        self.ID = ID
        self.patientID = patientID
        self.hospitalizeTime = hospitalizeTime
        self.hospitalizeLocation = hospitalizeLocation
        self.hospitalizeSymptom = hospitalizeSymptom