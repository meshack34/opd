from django.db import models
from testapp.models import *
# Create your models here.
class BedAllotments(models.Model):
    bed_id=models.CharField(max_length=20,unique=True,null=False,blank=False)
    room_nos=models.ForeignKey('testapp.RoomNumber',on_delete=models.CASCADE)
    bed_nos=models.CharField(max_length=20,unique=True,null=False,blank=False)
    def __str__(self):
        return str(self.bed_nos)
class Department(models.Model):
    department_name=models.CharField(max_length=100,unique=True,null=False,blank=False)
    description=models.TextField(blank=True,null=True)
    def __str__(self):
        return self.department_name

class Ipd_Dept(models.Model):
    department_name=models.CharField(max_length=100,unique=True,null=False,blank=False)
    description=models.TextField(blank=True,null=True)
    def __str__(self):
        return self.department_name

class WardName(models.Model):
    ward_name=models.CharField(max_length=100,unique=True,null=False,blank=False)
    description=models.TextField(blank=True,null=True)
    def __str__(self):
        return self.ward_name
class WingMaster(models.Model):
    wing_name=models.CharField(max_length=100,unique=True,null=False,blank=False)
    description=models.TextField(blank=True,null=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.wing_name
class FloorMaster(models.Model):
    wing_name=models.ForeignKey(WingMaster,on_delete=models.CASCADE)
    floor_name=models.CharField(max_length=100,unique=True,null=False,blank=False)
    description=models.TextField(blank=True,null=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.floor_name
class RoomMaster(models.Model):
    wing_name=models.ForeignKey(WingMaster,on_delete=models.CASCADE)
    floor_name=models.ForeignKey(FloorMaster,on_delete=models.CASCADE)
    room_number=models.CharField(max_length=40)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.room_number

class AdmissionWardType(models.Model):
    floor_name=models.ForeignKey(FloorMaster,on_delete=models.CASCADE)
    room_number=models.ForeignKey(RoomMaster,on_delete=models.CASCADE)
    ward_type=models.CharField(max_length=100,unique=True,)
    description=models.TextField(blank=True,null=True)
    def __str__(self):
        return self.ward_type

class AdmissionWardCate(models.Model):
    floor_name=models.ForeignKey(FloorMaster,on_delete=models.CASCADE)
    room_number=models.ForeignKey(RoomMaster,on_delete=models.CASCADE)
    ward_type=models.ForeignKey(AdmissionWardType,on_delete=models.CASCADE)
    category_name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)
    def __str__(self):
        return self.category_name

class BedMaster(models.Model):
    BED_LOCATION=(
        ('WINDOWS SIDE','WINDOWS SIDE'),
        ('CENTER','CENTER'),
        ('LEFT SIDE','LEFT SIDE'),
        ('RIGHT SIDE','RIGHT SIDE'),
    )
    wing_name = models.ForeignKey(WingMaster, on_delete=models.CASCADE)
    floor_name = models.ForeignKey(FloorMaster, on_delete=models.CASCADE)
    room_number = models.ForeignKey(RoomMaster,on_delete=models.CASCADE)
    bed_no=models.CharField(max_length=30)
    ward_type=models.ForeignKey(AdmissionWardType,on_delete=models.CASCADE)
    ward_category=models.ForeignKey(AdmissionWardCate,on_delete=models.CASCADE)
    bed_location=models.CharField(max_length=100,choices=BED_LOCATION)
    description=models.TextField(blank=True,null=True)
    def __str__(self):
        return str(self.bed_no)
class BedMasterMain(models.Model):
    status=(
        ('Active','Active'),
        ('Inactive','Inactive'),
        ('Occupied','Occupied'),
        ('Un-occupied','Un-occupied'),
    )
    wing_name = models.CharField(max_length=40)
    floor_name = models.CharField(max_length=40)
    room_number = models.CharField(max_length=40)
    bed_no = models.CharField(max_length=30)
    ward_type = models.CharField(max_length=40)
    ward_category = models.CharField(max_length=40)
    bed_location = models.CharField(max_length=40)
    status=models.CharField(max_length=100,choices=status,default='Active')
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return str(self.bed_no)
class BedLocation(models.Model):
    location_name=models.CharField(max_length=100,unique=True,null=False,blank=False)
    description = models.TextField(blank=True, null=True)
class NursingStationCounter(models.Model):
    counter_name=models.CharField(max_length=100,unique=True,null=False,blank=False)
    inactive=models.BooleanField()
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.counter_name
class Room_Defination(models.Model):
    GENDER=(('MALE','MALE'),('FEMALE','FEMALE'))
    ward_type=models.ForeignKey(AdmissionWardType,on_delete=models.CASCADE,related_name='wardtype')
    ward_name=models.ForeignKey(WardName,on_delete=models.CASCADE,related_name='wardname')
    ward_cate=models.ForeignKey(AdmissionWardCate,on_delete=models.CASCADE,related_name='wardcate')
    wing=models.ForeignKey(WingMaster,on_delete=models.CASCADE,related_name='wing')
    floor=models.ForeignKey(FloorMaster,on_delete=models.CASCADE,related_name='floor')
    department=models.ForeignKey('testapp.RoomNumber',on_delete=models.CASCADE,related_name='department')
    nursing_counter=models.ForeignKey(NursingStationCounter,on_delete=models.CASCADE,related_name='nursecounter')
    room_no=models.ForeignKey('testapp.RoomNumber',on_delete=models.CASCADE,related_name='room')
    Gender=models.CharField(max_length=20,choices=GENDER)
    bed_charge_not_applicable=models.BooleanField()
    inactive=models.BooleanField()
class AdmissionWardCategory(models.Model):
    ward_type=models.ForeignKey(AdmissionWardType,on_delete=models.CASCADE)
    ward_category=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)
    def __str__(self):
        return self.ward_category
class AdmissionInfos(models.Model):
    ADMISSION_TYPE=(
        ('Normal Admission','Normal Admission'),
        ('Emergency Admission','Emergency Admission'),
        ('Online Admission','Online Admission'),
        ('Offline Admission','Offline Admission'),
    )
    uhid=models.CharField(max_length=50)
    admission_ID=models.CharField(max_length=100)
    admission_datetime=models.DateTimeField(auto_now_add=True,editable=False)
    admission_type=models.CharField(max_length=50,choices=ADMISSION_TYPE)
    req_ward_type=models.ForeignKey(AdmissionWardType,on_delete=models.CASCADE,blank=True,null=True)
    req_ward_cate=models.ForeignKey(AdmissionWardCate,on_delete=models.CASCADE,blank=True,null=True)
    infected=models.BooleanField()
    MLC=models.BooleanField()
    MLC_No=models.CharField(max_length=50,blank=True,null=True)#
    primary_doctor=models.ForeignKey('testapp.DoctorTable',on_delete=models.CASCADE,related_name='primary_doctor',blank=True,null=True)
    department=models.ForeignKey(Ipd_Dept,on_delete=models.CASCADE,related_name='department',blank=True,null=True)
    secondary_doctor=models.ForeignKey('testapp.DoctorTable',on_delete=models.CASCADE,blank=False,null=False,related_name='secoundry_doctor')
    ref_hospital=models.ForeignKey('testapp.HospitalMaster',on_delete=models.CASCADE,blank=True,null=True)
    bed_no=models.ForeignKey(BedMasterMain,on_delete=models.CASCADE,blank=True)
    status=models.CharField(max_length=100,default='admitted',blank=True)


class Bed_Transfer(models.Model):
    uhid=models.CharField(max_length=50)
    admission_ID=models.CharField(max_length=100)
    bed_transfer_id=models.CharField(max_length=50, blank=True,null=True)
    from_ward_type=models.ForeignKey(AdmissionWardType,on_delete=models.CASCADE,related_name='from_ward_type')
    from_ward_cat=models.ForeignKey(AdmissionWardCate,on_delete=models.CASCADE,related_name='from_ward_type')
    from_bed_no=models.ForeignKey(BedMasterMain,on_delete=models.CASCADE,related_name='from_bed_no')
    to_ward_type=models.ForeignKey(AdmissionWardType,on_delete=models.CASCADE,related_name='to_ward_type')
    to_ward_cat=models.ForeignKey(AdmissionWardCate,on_delete=models.CASCADE,related_name='to_ward_type')
    to_bed_no=models.ForeignKey(BedMasterMain,on_delete=models.CASCADE,related_name='to_bed_no')
    transfer_datatime=models.DateTimeField(auto_now_add=True, blank=True)

class Doctor_Transfer(models.Model):
    uhid=models.CharField(max_length=50)
    admission_ID=models.CharField(max_length=100, blank=True,null=True)
    doctor_transfer_id=models.CharField(max_length=50)
    from_doctor=models.ForeignKey('testapp.DoctorTable',on_delete=models.CASCADE,related_name='from_dept')
    from_department=models.ForeignKey(Ipd_Dept,on_delete=models.CASCADE,related_name='from_doctor')
    to_doctor=models.ForeignKey('testapp.DoctorTable',on_delete=models.CASCADE,related_name='to_dept')
    to_department=models.ForeignKey(Ipd_Dept,on_delete=models.CASCADE,related_name='to_doctor')
    transfer_datatime=models.DateField(default=datetime.now)



# ============================DropDownChaining===========================
# Simple Country State Master In Django
class Country(models.Model):
    name=models.CharField(max_length=30)
    def __str__(self):
        return self.name
class City(models.Model):
    country=models.ForeignKey(Country,on_delete=models.CASCADE)
    name=models.CharField(max_length=30)
    def __str__(self):
        return self.name
class Person(models.Model):
    Name=models.CharField(max_length=30)
    country=models.ForeignKey(Country,on_delete=models.SET_NULL,blank=True,null=True)
    city=models.ForeignKey(City,on_delete=models.SET_NULL,blank=True,null=True)
    def __str__(self):
        return self.name