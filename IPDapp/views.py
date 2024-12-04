from distutils.log import error
from django.shortcuts import render
from django.shortcuts import render
import calendar
from datetime import date
from calendar import HTMLCalendar
from testapp.forms import *
from testapp.models import *
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from OpdManagement.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY
import razorpay
from datetime import *
from django.views.generic import *
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from IPDapp.models import *
from IPDapp.forms import *





def bed_allotment(request):
    form=BedAllotmentForm()
    if request.method=='POST':
        form=BedAllotmentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/ipd/bed_allotment')
    records=BedAllotments.objects.all()
    return render(request,'general_master/bed_allotment.html',{'form':form,'records':records})


         


from django.shortcuts import redirect

def person_create_view(request):
    form=PersonCreateForm()
    if request.method=='POST':
        form=PersonCreateForm(request.POST)
        print('This is data coming for person page')
        cities=request.POST.get('city')
        Name=request.POST.get('Name')
        country=request.POST.get('country')
        print('Name ',Name)
        print('country Name',country)
        print('Citis Name',cities)
        if form.is_valid():
            form.save()
            return redirect('person_add')
    records=Person.objects.all()
    return render(request,'try/home.html',{'form':form,'records':records})
def person_update_view(request):
    form=PersonCreateForm()
    if request.method=='POST':
        form=PersonCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('person_add')
    return render(request,'try/home.html',{'form':form})
def load_cities(request):
    load_room_master
    country_id=request.GET.get('country_id')
    cities=City.objects.filter(country_id=country_id)
    print(cities)
    # return render(request,'try/city_dropdown.html',{'cities':cities})
    return JsonResponse(list(cities.values('id','name')),safe=False)
def country_view(request):
    form=CountryForm()
    if request.method=='POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('country')
    is_country_form=True
    title='Country Page'
    context={
        'form':form,'is_country_form':is_country_form,'title':title,
    }
    return render(request,'try/forms.html',context)
def city_view(request):
    form=CityForm()
    if request.method=='POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('city')
    title='City Page'
    context={
        'form':form,'title':title,
    }
    return render(request,'try/forms.html',context)

# ========================Ward Categories Form=========================
def load_ward_type_master(request):
    wing_id=request.GET.get('floor_id')
    print('wing_id Id',wing_id)
    floor=RoomMaster.objects.filter(floor_name_id=wing_id)
    print(floor)
    # return render(request,'try/city_dropdown.html',{'cities':cities})
    return JsonResponse(list(floor.values('id','room_number')),safe=False)
    
def ward_type_view(request):
    print('aseedfasd')
    name=request.session['Name']
    form=AdmissionWardTypeForm()
    records=AdmissionWardType.objects.all
    if request.method=='POST':
        form=AdmissionWardTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wt')
    is_ward_type_view=True
    context={
        'records':records, 'form':form,'is_ward_type_view':is_ward_type_view,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['ward_type_add'] is True:
                context["add"].append("add")
            if request.session['ward_type_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,'general_master/addmision_ward_cate_type.html',context)


def ward_cate_view(request):
    name=request.session['Name']
    print('admission',AdmissionWardCategory.objects.all())
    form=AdmissionWardCateForm()
    if request.method=='POST':
        form=AdmissionWardCateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/ipd/ward-cate')
    is_ward_cate_view=True
    records = AdmissionWardCategory.objects.all()
    context={
         'form':form,'is_ward_cate_view':is_ward_cate_view,'records':records,'login_name':name
    }
    return render(request,'general_master/addmision_ward_cate_type.html',context)

# ============================Master Screen Views=================================
def ward_t_view(request):
    name=request.session['Name']
    form=AdmissionWardTypeForm()
    if request.method=='POST':
        form = AdmissionWardTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wt')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_ward_type=True
    records=AdmissionWardType.objects.all()
    print(records.count())
    context={
        'form':form,'is_ward_type':is_ward_type,'records':records
    }
    return render(request,template_name,context)


def load_ward_cat_master(request):
    floor_id=request.GET.get('floor_id')
    room_id=request.GET.get('room_id')
    print(floor_id,room_id)
    if room_id is None:
        floor=RoomMaster.objects.filter(floor_name_id=floor_id)
        return JsonResponse(list(floor.values('id','room_number')),safe=False)
    else:
        ward_type=AdmissionWardType.objects.filter(floor_name_id=floor_id,room_number_id=room_id)
        print(ward_type)
        return JsonResponse(list(ward_type.values('id','ward_type')),safe=False)

def ward_c_view(request):
    print('ashuidhx')
    name=request.session['Name']
    form=AdmissionWardCateForm()
    if request.method=='POST':
        form = AdmissionWardCateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wc')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_ward_cate=True
    records=AdmissionWardCate.objects.all() 
    context={
         'form':form,'is_ward_cate':is_ward_cate,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            print(request.session['ipd_ward_category_add'])
            if request.session['ipd_ward_category_add'] is True:
                print('add')
                context["add"].append("add")
            if request.session['ipd_ward_category_view'] is True:
                print('view')
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)
def ward_name_view(request):
    name=request.session['Name']
    form=WardNameForm()
    if request.method=='POST':
        form = WardNameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wn')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_ward_name=True
    records=WardName.objects.all()
    context={
        'form':form,'is_ward_name':is_ward_name,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['ward_name_add'] is True:
                context["add"].append("add")
            if request.session['ward_name_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)

def bed_location_view(request):
    name=request.session['Name']
    form=BedLocationForm()
    if request.method=='POST':
        form = BedLocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bl')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_bed_location=True
    records=BedLocation.objects.all()
    context={
        'form':form,'is_bed_location':is_bed_location,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['bed_location_add'] is True:
                context["add"].append("add")
            if request.session['bed_location_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)
def nursing_station_counter_view(request):
    name=request.session['Name']
    form=NursingStationCounterForm()
    if request.method=='POST':
        form = NursingStationCounterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('nsv')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_nsc=True
    records=NursingStationCounter.objects.all()
    context={
        'form':form,'is_nsc':is_nsc,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['nursing_counter_add'] is True:
                context["add"].append("add")
            if request.session['nursing_counter_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)

def wing_master_view(request):
    name=request.session['Name']
    form=WingMasterForm()
    if request.method=='POST':
        form = WingMasterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wm')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_wing_master=True
    records=WingMaster.objects.all()
    context={
        'form':form,'is_wing_master':is_wing_master,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['wing_master_add'] is True:
                context["add"].append("add")
            if request.session['wing_master_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)
def floor_master_view(request):
    name=request.session['Name']
    form=FloorMasterForm()
    if request.method=='POST':
        form = FloorMasterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fm')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_floor_master=True
    records=FloorMaster.objects.all()
    context={
        'form':form,'is_floor_master':is_floor_master,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['floor_master_add'] is True:
                context["add"].append("add")
            if request.session['floor_master_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)
def load_room_master(request):
    wing_id=request.GET.get('wing_id')
    print('wing_id Id',wing_id)
    wings=FloorMaster.objects.filter(wing_name_id=wing_id)
    print(wings)
    # return render(request,'try/city_dropdown.html',{'cities':cities})
    return JsonResponse(list(wings.values('id','floor_name')),safe=False)
def room_master_view(request):
    name=request.session['Name']
    form=RoomMasterForm()
    if request.method=='POST':
        wing_name=request.POST.get('wing_name')
        floor_name=request.POST.get('floor_name')
        room_number=request.POST.get('room_number')
        description=request.POST.get('description')
        print(wing_name,floor_name,room_number,description)
        form = RoomMasterForm(request.POST)
        if form.is_valid():
            try:
                if  RoomMaster.objects.get(wing_name=wing_name,floor_name=floor_name,room_number=room_number)!='':
                    print('error')
            except:
                form.save()
                return redirect('rm')
    template_name = 'general_master/ipd_master/AllIpdMaster.html'
    is_room_master = True
    records = RoomMaster.objects.all()
    context = {
        'form': form, 'is_room_master': is_room_master, 'records': records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['ipd_room_master_add'] is True:
                context["add"].append("add")
            if request.session['ipd_room_master_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request, template_name, context)
def load_bed_master(request):
    wing_id = request.GET.get('wing_id')
    floor_id = request.GET.get('floor_id')
    room_id = request.GET.get('room_id')
    print(room_id,floor_id,wing_id)
    wings = FloorMaster.objects.filter(wing_name_id=wing_id)
    rooms = RoomMaster.objects.filter(wing_name_id=floor_id)
    data=list(wings.values('id', 'floor_name'))
    # data2=list(rooms.values('id', 'room_number'))
    # list3=data+data2
    # print('list3',list3)
    return JsonResponse(data, safe=False)

    # return render(request,'try/city_dropdown.html',{'cities':cities})
    #return JsonResponse(list(wings.values('id', 'floor_name')), safe=False)
def bed_master_view(request):
    name=request.session['Name']
    form=BedMasterForm()
    if request.method=='POST':
        form = BedMasterForm(request.POST)
        if form.is_valid():
            wing_name=request.POST.get('wing_name')
            floor_name=request.POST.get('floor_name')
            request.session['s_v_wing_name']=wing_name
            request.session['s_v_floor_name']=floor_name
            return redirect('bmn')
    template_name = 'general_master/ipd_master/AllIpdMaster.html'
    is_bed_master = True
    records = BedMasterMain.objects.all().order_by('wing_name')
    context = {
        'form': form, 'is_bed_master': is_bed_master, 'records': records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['bed_master_add'] is True:
                context["add"].append("add")
            if request.session['bed_master_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request, template_name, context)

def load_bed_master_next(request):
    wing_id = request.session['s_v_wing_name']
    floor_id = request.session['s_v_floor_name']
    room_id = request.GET.get('room_id')
    ward_id = request.GET.get('ward_id')
    print(room_id,floor_id,wing_id,ward_id)
    if ward_id is None:
        ward_type = AdmissionWardType.objects.filter(floor_name_id=floor_id,room_number_id=room_id)
        data=list(ward_type.values('id', 'ward_type'))
        print('data',data)
    else:
        ward_cat=AdmissionWardCate.objects.filter(floor_name_id=floor_id,room_number_id=room_id,ward_type=ward_id)
        data=list(ward_cat.values('id', 'category_name'))
    return JsonResponse(data, safe=False)

def bed_master_next_view(request):
    form=BedMasterNextForm()
    s_v_wing_name=request.session['s_v_wing_name']
    s_v_floor_name=request.session['s_v_floor_name']
    room_no_records=RoomMaster.objects.filter(floor_name_id=s_v_floor_name)
    if request.method=='POST':
        form = BedMasterNextForm(request.POST)
        if form.is_valid():
            room_number=request.POST.get('room_number')
            bed_no=request.POST.get('bed_no')
            description=request.POST.get('description')
            ward_type=form.cleaned_data['ward_type']
            ward_category=form.cleaned_data['ward_category']
            bed_location=form.cleaned_data['bed_location']
            print(f'{s_v_wing_name},{s_v_floor_name},{room_number},{bed_no},{description},{ward_category},{bed_location}')
            print('room_number',room_number)
            wing_name=WingMaster.objects.get(id=s_v_wing_name)
            floor_name=FloorMaster.objects.get(id=s_v_floor_name)
            room_master=RoomMaster.objects.get(id=room_number)
            print(wing_name.wing_name)
            print(floor_name.floor_name)
            # if BedMasterMain.objects.get(floor_name = floor_name, ward_type = ward_type, ward_category = ward_category):
            #     print('alredy exists')
            bed_master=BedMasterMain.objects.get_or_create(
                wing_name= wing_name,
                floor_name = floor_name,
                room_number = room_master.room_number,
                bed_no = bed_no,
                ward_type = ward_type,
                ward_category = ward_category,
                bed_location =bed_location,
                description = description,
            )
            # bed_master.save()
            return redirect('bm')
    template_name = 'general_master/ipd_master/AllIpdMaster.html'
    is_bed_master_next = True
    records = BedMasterMain.objects.all().order_by('wing_name')
    context = {
        'form': form, 'is_bed_master_next': is_bed_master_next, 'records': records,'room_no_records':room_no_records
    }
    return render(request, template_name, context)
def depatment_view(request):
    name=request.session['Name']
    form=IpdDepartmentForm()
    if request.method=='POST':
        form = IpdDepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dpt')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_department=True
    records=Ipd_Dept.objects.all()
    context={
        'form':form,'is_department':is_department,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['ipd_department_add'] is True:
                context["add"].append("add")
            if request.session['ipd_department_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)

def room_defination(request):
    name=request.session['Name']
    form=RoomDefinationForm()
    if request.method=='POST':
        form = RoomDefinationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rd')
    template_name='general_master/ipd_master/AllIpdMaster.html'
    is_room_defination=True
    records=Room_Defination.objects.all()
    context={
        'form':form,'is_room_defination':is_room_defination,'records':records,'add':[],'edit':[],'view':[],'login_name':name
    }
    try:
        if request.session['admin'] !='':
            print('admin')
            context["add"].append("add")
            context["view"].append("view")
        else:
            if request.session['room_defination_add'] is True:
                context["add"].append("add")
            if request.session['room_defination_view'] is True:
                context["view"].append("view")
    except:
        print('error')
        pass
    return render(request,template_name,context)











