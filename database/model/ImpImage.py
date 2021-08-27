class ImpImage:
    ID = None
    URLimage = None
    ImgName = None
    patientID = None
    def __init__(self, ID, URLimage, ImgName, patientID):
        self.ID = ID
        self.URLimage = URLimage
        self.ImgName = ImgName
        self.patientID = patientID
        