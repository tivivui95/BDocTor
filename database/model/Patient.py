class Patient:
    ID = None
    ResidentNumber = None
    HealthInsuranceID = None
    PatientName = None
    birthyear = None
    gender = None
    job = None
    address = None
    def __init__(self, ID, ResidentNumber, HealthInsuranceID, PatientName, birthyear, gender, job, address):
        self.ID = ID
        self.ResidentNumber = ResidentNumber
        self.HealthInsuranceID = HealthInsuranceID
        self.PatientName = PatientName
        self.birthyear = birthyear
        self.gender = gender
        self.job = job
        self.address = address

