

from django import forms
from IPDapp.models import *



class BedAllotmentForm(forms.ModelForm):
    class Meta:
        model=BedAllotments
        fields='__all__'

class AdmissionInfoForm(forms.ModelForm):
    global td
    td = datetime.now()
    class Meta:
        model=AdmissionInfos
        fields='__all__'
        widgets={
            'admission_datetime':forms.TextInput(attrs={'readonly':'readonly','value':td}),
            'uhid':forms.TextInput(attrs={'type':'hidden'}),
            'admission_ID':forms.TextInput(attrs={'type':'hidden'}),
            'admission_type':forms.Select(attrs={'class':'form-control'}),
            'req_ward_type':forms.Select(attrs={'class':'form-control'}),
            'req_ward_cate':forms.Select(attrs={'class':'form-control'}),
            'infected':forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'MLC':forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'MLC_No':forms.TextInput(attrs={'class':'form-control'}),
            'primary_doctor':forms.Select(attrs={'class':'form-control'}),
            'department':forms.Select(attrs={'class':'form-control'}),
            'secondary_doctor':forms.Select(attrs={'class':'form-control'}),
            'ref_hospital':forms.Select(attrs={'class':'form-control'}),
            'bed_no':forms.Select(attrs={'class':'form-control'}),
        }

    #     def __init__(self,*args,**kwargs):
    #         super().__init__(*args,**kwargs)
    #         self.fields['city'].queryset=City.objects.none()
    #         if 'country' in self.data:
    #             try:
    #                 country_id=int(self.data.get('country'))
    #                 self.fields['city'].queryset=City.objects.filter(country_id=country_id).order_by('name')
    
    #             except (ValueError,TypeError):
    #                 pass
    #         elif self.instance.pk:
    #             self.fields['cities'].queryset=self.instance.country.city_order_by('name')
    
    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     self.fields['req_ward_cate'].queryset=AdmissionWardCategory.objects.none()
    #     if 'req_ward_type' is self.data:
    #         try:
    #             req_ward_type_id=int(self.data.get('req_ward_type'))
    #             self.fields['req_ward_cate'].queryset=AdmissionWardCategory.objects.filter(req_ward_type_id=req_ward_type_id).order_by('name')

    #         except (ValueError,TypeError):
    #             pass
    #     elif self.instance.pk:
    #         # self.fields['req_ward_categories'].queryset=self.instance.req_ward_type.req_ward_cate_order_by('name')
    #         pass
    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     self.fields['bed_no'].queryset=BedMasterMain.objects.none()
    #     print('skhfsdhf',self.data)
    #     #self.fields['room_number'].queryset=FloorMaster.objects.none()
    #     # if 'bed_no' in self.data:
    #     try:
    #         req_ward_type_id=self.data.get('new_ward_type')
    #         req_ward_cate_id=self.data.get('req_ward_cate')
    #         print('req_ward_type_id',self.data)
    #         self.fields['bed_no'].queryset=BedMasterMain.objects.filter(ward_type=req_ward_type_id)
    #         print('aaa',self.data)
    #         print('bbbb')
    #     except (ValueError,TypeError):
    #         print('cccc')
    #         pass
    # def _init_(self, *args, **kwargs):
    #     super(BedTransferForm, self)._init_(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         visible.field.widget.attrs['class'] = 'form-control'


class BedTransferForm(forms.ModelForm):
    global td
    td = datetime.now()
    class Meta:
        model=Bed_Transfer
        fields='__all__'
        widgets={
            'transfer_datatime': forms.DateInput(attrs={'type': 'date','readonly':'readonly','class':'form-control'}),
            'bed_transfer_id':forms.TextInput(attrs={'type':'hidden'}),
            'admission_ID':forms.TextInput(attrs={'type':'hidden'}),
            'uhid':forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
            'from_ward_type':forms.Select(attrs={'class':'form-control','readonly':'readonly'}),
            'from_ward_cat':forms.Select(attrs={'class':'form-control','readonly':'readonly'}),
            'from_bed_no':forms.Select(attrs={'class':'form-control','readonly':'readonly'}),
            'to_ward_type':forms.Select(attrs={'class':'form-control'}),
            'to_ward_cat':forms.Select(attrs={'class':'form-control'}),
            'to_bed_no':forms.Select(attrs={'class':'form-control'}),
           
        }

class DoctorTransferForm(forms.ModelForm):
    global td
    td = datetime.now()
    class Meta:
        model=Doctor_Transfer
        fields='__all__'
        widgets={
            'transfer_datatime': forms.DateInput(attrs={'type': 'date','readonly':'readonly','class':'form-control'}),
            'doctor_transfer_id':forms.TextInput(attrs={'type':'hidden'}),
            'admission_ID':forms.TextInput(attrs={'type':'hidden'}),
            'uhid':forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
            'from_doctor':forms.Select(attrs={'class':'form-control','readonly':'readonly'}),
            'from_department':forms.Select(attrs={'class':'form-control','readonly':'readonly'}),
            'to_doctor':forms.Select(attrs={'class':'form-control'}),
            'to_department':forms.Select(attrs={'class':'form-control'}),
           
        }

class CityForm(forms.ModelForm):
    class Meta:
        model=City
        fields='__all__'
class CountryForm(forms.ModelForm):
    class Meta:
        model=Country
        fields='__all__'
class PersonCreateForm(forms.ModelForm):
    class Meta:
        model=Person
        fields="__all__"
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['city'].queryset=City.objects.none()
        if 'country' in self.data:
            try:
                country_id=int(self.data.get('country'))
                self.fields['city'].queryset=City.objects.filter(country_id=country_id).order_by('name')

            except (ValueError,TypeError):
                pass
        elif self.instance.pk:
            self.fields['cities'].queryset=self.instance.country.city_order_by('name')

# ========================MASter FORm ================================
class DepartmentForm(forms.ModelForm):
    class Meta:
        model=Department
        fields='__all__'

class IpdDepartmentForm(forms.ModelForm):
    class Meta:
        model=Ipd_Dept
        fields='__all__'


class DepartmentForm(forms.ModelForm):
    class Meta:
        model=Department
        fields='__all__'
class WardNameForm(forms.ModelForm):
    class Meta:
        model=WardName
        fields='__all__'

class WingMasterForm(forms.ModelForm):
    class Meta:
        model=WingMaster
        fields='__all__'
class FloorMasterForm(forms.ModelForm):
    class Meta:
        model=FloorMaster
        fields='__all__'
class RoomMasterForm(forms.ModelForm):
    class Meta:
        model=RoomMaster
        fields='__all__'
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['floor_name'].queryset=FloorMaster.objects.none()
        print('aaaa',self.data)
        if 'wing_name' in self.data:
            try:
                wing_name_id=int(self.data.get('wing_name'))
                self.fields['floor_name'].queryset=FloorMaster.objects.filter(wing_name_id=wing_name_id).order_by('floor_name')
            except (ValueError,TypeError):
                pass
        elif self.instance.pk:
            # self.fields['cities'].queryset = self.instance.country.city_order_by('name')
            pass
class AdmissionWardTypeForm(forms.ModelForm):
    class Meta:
        model=AdmissionWardType
        fields='__all__'
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['room_number'].queryset=RoomMaster.objects.none()
        if 'floor_name' in self.data:
            try:
                wing_name_id=int(self.data.get('floor_name'))
                self.fields['room_number'].queryset=RoomMaster.objects.filter(floor_name_id=wing_name_id).order_by('room_number')
            except (ValueError,TypeError):
                pass
        elif self.instance.pk:
            # self.fields['cities'].queryset = self.instance.country.city_order_by('name')
            pass

class AdmissionWardCateForm(forms.ModelForm):
    class Meta:
        model=AdmissionWardCate
        fields='__all__'
    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     self.fields['room_number'].queryset=RoomMaster.objects.none()
    #     self.fields['ward_type'].queryset=RoomMaster.objects.none()

class BedMasterForm(forms.ModelForm):
    class Meta:
        model=BedMaster
        # fields='__all__'
        fields=['wing_name','floor_name']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['floor_name'].queryset=FloorMaster.objects.none()
        print(self.data)
        #self.fields['room_number'].queryset=FloorMaster.objects.none()
        if 'wing_name' in self.data:
            try:
                wing_name_id=int(self.data.get('wing_name'))
                self.fields['floor_name'].queryset=FloorMaster.objects.filter(wing_name_id=wing_name_id).order_by('floor_name')
            except (ValueError,TypeError):
                pass
class BedMasterNextForm(forms.ModelForm):
    class Meta:
        model=BedMaster
        # fields='__all__'
        exclude=('wing_name','floor_name','room_number')

class BedLocationForm(forms.ModelForm):
    class Meta:
        model=BedLocation
        fields='__all__'
class NursingStationCounterForm(forms.ModelForm):
    class Meta:
        model=NursingStationCounter
        fields='__all__'

class RoomDefinationForm(forms.ModelForm):
    class Meta:
        model=Room_Defination
        fields='__all__'
