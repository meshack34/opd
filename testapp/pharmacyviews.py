
# from automium import schedule
from django.shortcuts import render,redirect
import calendar
from datetime import date
from calendar import HTMLCalendar
from testapp.forms import *
from testapp.models import *
from django.http import HttpResponse,HttpResponseRedirect
from OpdManagement.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY
import razorpay
from datetime import *
from django.views.generic import *
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from testapp.models import OpdPayment
from IPDapp.models import AdmissionInfos
from testapp.serializers import *
from usermanagementapp.models import *
from encrypt_util import *
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from OpdManagement import utils as utils_response
from rest_framework import status
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from datetime import datetime as dt
import json
from django.contrib import messages
import random
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.mail import send_mail,EmailMessage
from django.db.models import Sum
from django.db.models import Q, F


def unique_id(pre, suf):
    tot_rec_count = len(suf) + 1
    if len(str(tot_rec_count)) == 1:
        id = pre + '00' + str(tot_rec_count)
    elif len(str(tot_rec_count)) == 2:
        id = pre + '0' + str(tot_rec_count)
    else:
        id = pre + str(tot_rec_count)
    return id

#=================purchase order===================

@login_required(login_url='/user_login')
def purchase_order(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'purchase_order' in access.user_profile.screen_access:
        try:
            vendar=VendorMaster.objects.all()
            item=Inventory_ItemMaster.objects.all()
            po_temp=PurchaseOrder_Temp.objects.all()
            store_detail = StoreMaster.objects.get(store_type=0)
            location_detail = LocationMaster.objects.all()
            dept_detail = ServiceDepartment.objects.all()
            quantity = [data.quantity for data in po_temp]
            rate = [data.rate for data in po_temp]
            adding = zip(quantity,rate)
            basic_amount = 0
            for data1,data2 in adding:
                print("data1 data2",data1,data2 )
                basic_amount1 = int(data1) * int(data2)
                basic_amount = basic_amount + basic_amount1
            print("basic_amount",basic_amount)

            net_amount1=[data.amount for data in po_temp]
            netamount = 0
            for data in net_amount1:
                print("data",int(float(data)))
                netamount = netamount + int(float(data))

            # po_temporory
            add_button=request.POST.get('add_button')
            PO_ID=PurchaseOrder_Parent.objects.all().count()
            today=date.today()
            today=today.strftime("%d%m%y")
            POID='PO'+today+'000'+str(PO_ID)
            if request.method=='POST':
                if add_button == "save_temp":
                    item_name=request.POST.get('item_name').split('.')
                    qty=request.POST.get('qty')
                    unit=request.POST.get('unit_id')
                    free_qty=request.POST.get('free_qty')
                    stock_qty=request.POST.get('stock_qty')
                    rate=request.POST.get('rate')
                    schema=request.POST.get('schema')
                    amount=request.POST.get('amount')
                    discount_amt=request.POST.get('discount_amt')
                    discount=request.POST.get('discount')
                    tax_details=request.POST.get('tax_details')

                    if free_qty == "":
                        free_qty = 0

                    if schema == "":
                        schema = ""

                    if  discount_amt == "":
                        discount_amt = 0

                    if discount == "":
                        discount = ""


                    POtemp=PurchaseOrder_Temp(
                        item_ID_id=item_name[0],
                        quantity=int(qty),
                        unit_id=unit,
                        free_qty=free_qty,
                        stock_qty=stock_qty,rate=rate,
                        schema=schema,discount=discount,
                        discount_amt=discount_amt,amount=amount,
                        tax_details=tax_details,status="pending"
                    )
                    POtemp.save(print("po tem saved"))


                    temp_saved="temp_saved"
                    context={
                        'POtemp':POtemp,'temp_saved':temp_saved,'po_temp':po_temp,'vendar':vendar
                    }
                    return HttpResponseRedirect("/purchase_order",context)

                save_button=request.POST.get('saved')
                print("save_button",save_button)
                if save_button == "saved":
                    vendor_id=request.POST.get('vendor_id')
                    store_id=request.POST.get('store_id')
                    basic_amount=request.POST.get('basic_amount')
                    net_amount=request.POST.get('net_amount')
                    department=request.POST.get('department')
                    location=request.POST.get('location')

                    POparent=PurchaseOrder_Parent(
                        PO_id=POID,
                        PO_datetime=datetime.now(),
                        vendar_id_id=vendor_id,
                        Department_id=department,
                        Location_id=location,
                        po_location_id=request.POST.get('po_location'),
                        store_id_id=store_id,
                        net_amount=net_amount,
                        basic_amt=basic_amount,
                        PO_status="pending",
                        approval_status="pending",
                        issue_status='pending',
                    )
                    POparent.save(print("po parent saved"))

                    temp_items=PurchaseOrder_Temp.objects.all()
                    print("temp_items",temp_items)
                    temp_Items1=[data.item_ID_id for data in temp_items]
                    assets=[]
                    for data in temp_Items1:
                        items=Inventory_ItemMaster.objects.get(id=data)
                        asset=items.assets
                        assets.append(asset)
                    items=[data.item_ID_id for data in po_temp]
                    quantity=[data.quantity for data in po_temp]
                    unit=[data.unit_id for data in po_temp]
                    free_qty=[data.free_qty for data in po_temp]
                    stock_qty=[data.stock_qty for data in po_temp]
                    rate=[data.rate for data in po_temp]
                    discount=[data.discount for data in po_temp]
                    discount_amt=[data.discount_amt for data in po_temp]
                    amount=[data.amount for data in po_temp]
                    tax_details=[data.tax_details for data in po_temp]
                    schema=[data.schema for data in po_temp]

                    print("len",len(items))

                    for data in range(len(items)):
                        print(data,"data")
                        POchild=PurchaseOrder_Child(
                            PO_Id=POID,
                            item_id_id=items[data],
                            qty=quantity[data],
                            unit_id=unit[data],
                            PO_datetime=datetime.now(),
                            free_qty=free_qty[data],
                            stocy_qty=stock_qty[data],
                            rate=rate[data],
                            schema=schema[data],
                            discount=discount[data],
                            discount_amt=discount_amt[data],
                            amount=amount[data],
                            tex_details=tax_details[data],
                            received_qty="0",
                            issued_qty=0,
                            status="pending",
                            approval_status="pending",
                            issue_status='pending',
                            assets=assets[data],
                        )
                        POchild.save(print("po child saved"))

                    po_temp.delete()
                    return HttpResponseRedirect("/purchase_order")


            context={
                    'vendar':vendar,'add_button':add_button,'item':item,'po_temp':po_temp,"basic_amount":basic_amount,"netamount":netamount,"dept_detail":dept_detail,
                    'store_detail':store_detail,
                    'location_detail':location_detail
                }
            return render(request,'pharmacy/purchase_order.html',context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

def PO_calculate(request):
    try:
        itemid=request.POST.get("Item_name1").split('.')
        unit_from_invenentory=Inventory_ItemMaster.objects.get(id=itemid[0])
        unit_id = unit_from_invenentory.unit
        data1 = ItemUnitMaster.objects.get(id=unit_id)
        my_dict=json.dumps({
            'data1': data1.unit,
            'unit_id': data1.id,
            'item_id':itemid[0],
        })
        data = eval(my_dict)
        return JsonResponse(data,safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def get_stock_details(request):
    try:
        item_id=request.POST.get("item_id")
        if Stock_BatchWise.objects.filter(item_id_id=item_id).exists():
            stock_qty = Stock_BatchWise.objects.filter(item_id_id=item_id).last()
            total_qty = stock_qty.total_qty
            rate=stock_qty.rate
        else:
            total_qty = 0
            rate=0
        my_dict=json.dumps({
            'total_qty': total_qty ,
            'rate':rate,
        })
        data = eval(my_dict)
        return JsonResponse(data,safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def PO_preview(request):
    try:
        records=PurchaseOrder_Parent.objects.latest('PO_id')
        po_id=records.id
        po_no=records.PO_id
        vendor_id=records.vendar_id_id
        vendor_master = VendorMaster.objects.get(id=vendor_id)
        po_parent=PurchaseOrder_Parent.objects.get(PO_id=po_no)
        datetime=records.PO_datetime
        PO_child=PurchaseOrder_Child.objects.filter(PO_Id=po_no)
        total_rate = 0
        for data in PO_child:
            total_rate = int(total_rate) + int(data.rate)
        context={
            "po_no":po_no,"datetime":datetime,'records':records,"PO_child":PO_child,
            'vendor_master' : vendor_master,
            'po_parent' :po_parent,
            'total_rate':total_rate
        }
        return render(request,"pharmacy/po_preview.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def PO_approval_preview(request):
    try:
        records=PurchaseOrder_Parent.objects.latest('PO_id')
        po_id=records.id
        po_no=records.PO_id
        vendor_id=records.vendar_id_id
        datetime=records.PO_datetime
        PO_child=PurchaseOrder_Child.objects.filter(PO_Id=po_no)
        total_rate = 0
        for data in PO_child:
            total_rate = int(total_rate) + int(data.rate)
        po_parent=PurchaseOrder_Parent.objects.get(PO_id=po_no)
        vendor_master = VendorMaster.objects.get(id=vendor_id)
        vendor_email=vendor_master.email
        vendor_name = vendor_master.vendor_name
        send_mail = request.POST.get("send_mail")
        if send_mail == "send_mail":
            subject=request.POST.get("subject")
            files = request.FILES.get('filename')
            message=request.POST.get("message")
            mail=vendor_email
            mail1 = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [mail])
            mail1.attach(files.name, files.read(), files.content_type)
            mail1.send()
        context={
            "po_no":po_no,"datetime":datetime,'records':records,"PO_child":PO_child,"vendor_name":vendor_name,"vendor_email":vendor_email,'vendor_master':vendor_master,
            'po_parent' :po_parent,'total_rate':total_rate
        }
        return render(request,"pharmacy/PO_approval_preview.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

#=========================PO Approval=======================

@login_required(login_url='/user_login')
def purchase_order_approval(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'po_approval' in access.user_profile.screen_access:
        try:
            vendor=VendorMaster.objects.all()
            approved1 = PurchaseOrder_Parent.objects.filter(approval_status="completed")
            vendor1 = [data.vendar_id_id for data in approved1]
            vendor_name = []
            for data in vendor1:
                vendor1 = VendorMaster.objects.get(id=data)
                vendor_name.append(vendor1.vendor_name)
            approved = zip(approved1,vendor_name)
            pending = PurchaseOrder_Parent.objects.filter(approval_status="pending")
            vendor2 = [data.vendar_id_id for data in pending]
            vendor_name2 = []
            for data in vendor2:
                vendor2 = VendorMaster.objects.get(id=data)
                vendor_name2.append(vendor2.vendor_name)
            pending1 = zip(pending,vendor_name2)
            count_approved = approved1.count()
            count_pending = pending.count()
            context={
                'vendor':vendor,'pending1':pending1,'approved':approved,'count_approved':count_approved,'count_pending':count_pending
            }
            return render(request,"pharmacy/po_approval.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def PO_approveview(request,pk):
    try:
        records=PurchaseOrder_Child.objects.filter(PO_Id=pk)
        context={
            "records":records
        }
        return render(request,"pharmacy/PO_aproveview.html",context)
    except Exception as error:
           return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def PO_pending_update(request,pk):
    try:
        records=PurchaseOrder_Child.objects.filter(PO_Id=pk)
        PO_approve=PurchaseOrder_Parent.objects.get(PO_id=pk)
        approve=request.POST.get("Approve")
        if request.method == "POST":
            if approve == "Approved":
                for data in records:
                    data.approval_status="completed"
                    data.save(print("save"))
                PO_approve.approval_status= "completed"
                PO_approve.save(print("saved"))
                PK=f'{pk}'

                return HttpResponseRedirect(f"/PO_pending_update/{PK}")
        records1=PurchaseOrder_Parent.objects.latest('PO_id')
        vendor_id=records1.vendar_id_id
        vendor_master = VendorMaster.objects.get(id=vendor_id)
        vendor_email=vendor_master.email
        vendor_name = vendor_master.vendor_name

        send_mail = request.POST.get("send_mail")
        if send_mail == "send_mail":
            subject=request.POST.get("subject")
            files = request.FILES.get('filename')
            message=request.POST.get("message")
            mail=vendor_email
            mail1 = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [mail])
            mail1.attach(files.name, files.read(), files.content_type)
            mail1.send()
            HttpResponseRedirect("/purchase_order_approval")
        context={
            "records":records,"vendor_email":vendor_email,"vendor_name":vendor_name
        }
        return render(request,"pharmacy/po_pendingupdate.html",context)
    except Exception as error:
           return render(request,'error.html',{'error':error})

# Update pendin approvel
@login_required(login_url='/user_login')
def PO_update(request):
    try:
        po_id=request.GET.get("po_id")
        itemid=request.GET.get("itemid")
        qty=request.GET.get("qty")
        rate=request.GET.get("rate")
        discount=request.GET.get("discount")
        amount=request.GET.get("amount")
        PO_child=PurchaseOrder_Child.objects.get(PO_Id=po_id,item_id=itemid)
        PO_child.qty=qty
        PO_child.rate=rate
        PO_child.discount=discount
        PO_child.amount=amount
        PO_child.save()
        data='updated'
        return JsonResponse(data, safe=False)
    except Exception as error:
           return render(request,'error.html',{'error':error})

# ================================== email sending common function===========================
@login_required(login_url='/user_login')
def email_sending(subject,message,mail):
    mail_from = 'lovelan@gmail.com'
    email_to = mail
    send_mail(
        subject,
        message,
        mail_from,
        [email_to],
        fail_silently=False
    )
    return HttpResponse("Mail Send Successfully")



#=================Stock Entry=====================
@login_required(login_url='/user_login')
def stock_entry(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'stock_entry' in access.user_profile.screen_access:
        try:
            search_po = request.POST.get("search_po")
            if search_po == "search_po":
                search_po_id = request.POST.get("po_no")
                PK=f'{search_po_id}'
                return HttpResponseRedirect(f"/search_single_PO/{PK}")

            po_no=PurchaseOrder_Parent.objects.select_related('vendar_id').filter(PO_status__in =["pending","partially completed"],approval_status="completed")
            vendor1=[data.vendar_id_id for data in po_no]
            vendor_name=[]
            for data in vendor1:
                vendor1=VendorMaster.objects.get(id=data)
                vendor_name.append(vendor1.vendor_name)
            stock_entry=zip(po_no,vendor_name)

            search=request.POST.get("search")
            if search == "search":
                po_id=request.POST.get("po_no")
                po_ids=f'{po_id}'
                return HttpResponseRedirect(f"/search_single_PO/{po_ids}")
            context={
                'stock_entry':stock_entry
            }
            return render(request,'pharmacy/Stockentry/stock_entry.html',context)

        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


from datetime import datetime
@login_required(login_url='/user_login')
def search_single_PO(request,pk):
    try:
        PO_child = PurchaseOrder_Child.objects.filter(PO_Id=pk)
        PO_child2 = PurchaseOrder_Child.objects.select_related('item_id').filter(Q(PO_Id=pk,status="pending")|Q(PO_Id=pk,status="partially completed"))
        PO_parent = PurchaseOrder_Parent.objects.select_related('vendar_id').get(PO_id=pk)
        vendor_name = PO_parent.vendar_id_id
        vendor_name_1 = VendorMaster.objects.get(id=vendor_name)
        vendor_name_2 = vendor_name_1.vendor_name
        store_id = StoreMaster.objects.filter(store_type='1').last()

        Saveall = request.POST.get("saveall")

        if request.method == "POST":
            if Saveall == "saveall":
                po_id=request.POST.get("po_no")
                PO_date=request.POST.get("po_datetime")
                vendor_id=request.POST.get("vendor_id")
                net_amt=request.POST.get("po_net_amt")
                basic_amt=request.POST.get("po_basic_amt")
                invoice_no=request.POST.get("po_invoice_no")
                item_name=request.POST.getlist("po_item_id")
                serial_batch=request.POST.getlist("po_serial_batch")
                expiry_date=request.POST.getlist("po_expiry_date")
                po_qty=request.POST.getlist("qty")
                received_qty=request.POST.getlist("po_physical_qty")
                rate=request.POST.getlist("rate")
                discount=request.POST.getlist("discount")
                discount_amt=request.POST.getlist("discount_amt")
                amount=request.POST.getlist("amount")
                tax=request.POST.getlist("tax")
                schema=request.POST.getlist("schema")
                stock_qty=request.POST.getlist("stock_qty")
                free_qty=request.POST.getlist("free_qty")
                department=request.POST.get("department")

                # Generate ID
                stoc_parent=StockEntry_Parent.objects.all().count()
                today=date.today()
                today_date=today.strftime("%d%m%y")
                GRN_ID='GRN'+today_date+'00'+str(stoc_parent)

                #received quantity save in PO child
                receved1=[data.received_qty for data in PO_child2]
                for data1 ,data in zip(range(len(received_qty)),PO_child2):
                    if received_qty[data1] == "":
                        received_qty[data1] = 0
                        data.received_qty= received_qty[data1] + receved1[data1]
                        data.save(print("received saved"))
                    elif receved1[data1] == "":
                        received_qty[data1] = 0
                        data.received_qty= received_qty[data1] + receved1[data1]
                        data.save(print("received saved"))
                    else:

                        data.received_qty=int(str(received_qty[data1])) +int(str(receved1[data1]))
                        data.save(print("received saved"))

                PO_parent=PurchaseOrder_Parent.objects.get(PO_id=pk)

                grn_amount = 0
                for data in range(len(item_name)):
                    if serial_batch[data] and expiry_date[data] and received_qty[data]:
                        #openning Balance
                        records=Stock_BatchWise.objects.filter(item_id=item_name[data]).last()
                        consume=Stock_BatchWise.objects.filter(item_id=item_name[data],batch_no=serial_batch[data]).last()
                        # expiry_date_record = Stock_BatchWise.objects.filter(Q(item_id=item_name[data],batch_no=serial_batch[data],expiry_date=expiry_date[data])|Q(item_id=item_name[data],batch_no=serial_batch[data])).last()

                        if received_qty[data] and schema[data] and discount[data] and tax[data]:
                            rate_amt = int(received_qty[data]) * int(rate[data])
                            schema_amt = int(int(int(rate_amt) * int(schema[data])) / 100)
                            disc_amt = int(int(int(rate_amt) * int(discount[data])) / 100)
                            tax_amt = int(int(int(rate_amt) * int(tax[data])) / 100)
                            total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                            grn_amount += rate_amt - schema_amt - disc_amt + tax_amt
                        elif received_qty[data] and tax[data] and schema[data]:
                            rate_amt = int(received_qty[data]) * int(rate[data])
                            schema_amt = int(int(int(rate_amt) * int(schema[data])) / 100)
                            tax_amt = int(int(int(rate_amt) * int(tax[data])) / 100)
                            total_cost = rate_amt - schema_amt + tax_amt
                            grn_amount += rate_amt - schema_amt + tax_amt
                        elif received_qty[data] and tax[data] and discount[data]:
                            rate_amt = int(received_qty[data]) * int(rate[data])
                            disc_amt = int(int(int(rate_amt) * int(discount[data])) / 100)
                            tax_amt =  int(int(int(rate_amt) * int(tax[data])) / 100)
                            total_cost = rate_amt - disc_amt + tax_amt
                            grn_amount += rate_amt - disc_amt + tax_amt
                        elif received_qty[data] and tax[data]:
                            rate_amt = int(received_qty[data]) * int(rate[data])
                            tax_amt =  int(int(int(rate_amt) * int(tax[data])) / 100)
                            total_cost = rate_amt + tax_amt
                            grn_amount += rate_amt + tax_amt
                        elif received_qty[data]:
                            rate_amt = int(received_qty[data]) * int(rate[data])
                            # tax_amt =  int(int(int(rate_amt) * int(tax[data])) / 100)
                            total_cost = rate_amt 
                            grn_amount += rate_amt  
                        else:
                            grn_amount = 0
                            total_cost = 0

                        if records:
                            opening=records.total_qty
                            opening_cost = records.total_cost
                            total_cost_amt = int(records.total_cost) + int(total_cost)
                            total_qty = int(records.total_qty) + int(received_qty[data])
                        else:
                            opening=0
                            opening_cost=0
                            total_cost_amt = total_cost
                            total_qty = received_qty[data]

                        if consume:
                            consume_qty = int(consume.total_consume_qty) + int(received_qty[data])
                            available_qty = int(consume.available_qty) + int(received_qty[data])
                        else:
                            consume_qty = received_qty[data]
                            available_qty = received_qty[data]

                        # if expiry_date_record:
                        #     available_qty = int(expiry_date_record.available_qty) + int(received_qty[data])
                        # else:
                        #     available_qty = received_qty[data]

                        stock_child=StockEntry_Child(                                                 #stock entry child
                            GRN_id=GRN_ID,PO_id=po_id,
                            GRN_datetime=datetime.now(),
                            item_id_id=item_name[data],
                            item_qty=po_qty[data],
                            serial_batch=serial_batch[data],
                            rate=rate[data],
                            amount=amount[data],
                            expiry_date=expiry_date[data],
                            physical_qty=received_qty[data],
                            total_qty=total_qty,
                            opening_balance=opening,
                            transaction_cost = total_cost,
                            total_cost=total_cost_amt,
                            opening_cost=opening_cost,
                            free_qty=free_qty[data],
                            stock_qty=stock_qty[data],
                            schema=schema[data],
                            discount=discount[data],
                            discount_amt=discount_amt[data],
                            tax_details=tax[data],
                            remark='',
                            status= "pending",
                            movement_status="GRN ENTRY"
                        )
                        batch_wise=Stock_BatchWise(                                                      #stock entry batwise
                            GRN_id=GRN_ID,GRN_datetime=datetime.now(),
                            PO_id=po_id,
                            PO_datetime=PO_parent.PO_datetime,
                            item_id_id=item_name[data],
                            batch_no=serial_batch[data],
                            expiry_date=expiry_date[data],
                            received_qty=received_qty[data],
                            rate=rate[data],amount=amount[data],store_id_id=request.POST.get('store_id'),
                            vendar_id_id=vendor_id,
                            department_id_id=department,
                            location_id_id=request.POST.get('location_id'),
                            po_location_id=request.POST.get('po_location'),
                            available_qty=available_qty,
                            total_qty=total_qty,
                            total_cost = total_cost_amt,
                            adjust_qty="",
                            status=" ",
                            total_consume_qty = consume_qty,
                        )
                        if serial_batch[data] and expiry_date[data] and received_qty[data]:

                            stock_child.save(print("stock_child saved"))

                            batch_wise.save(print("batchwise saved"))

                            PO_status=PurchaseOrder_Child.objects.filter(PO_Id=pk)
                            # change status to po child
                            PO_Received=[data.received_qty for data in PO_child2]
                            PO_poqty=[data.qty for data in PO_child2]
                            items=[data.item_id_id for data in PO_child2]
                            for data1,data2,data3 in zip(PO_Received,PO_poqty,items):
                                    if data1 == data2:
                                        PO_status=PurchaseOrder_Child.objects.get(PO_Id=pk,item_id_id=data3)
                                        PO_status.status = "completed"
                                        PO_status.save()
                                    else:
                                        PO_status=PurchaseOrder_Child.objects.get(PO_Id=pk,item_id_id=data3)
                                        PO_status.status = "partially completed"
                                        PO_status.save()

                            #Po parent status change
                            PO_status=PurchaseOrder_Child.objects.filter(PO_Id=pk)
                            status=[data.status for data in PO_status]
                            status1=len(status)
                            PC=0
                            com=0
                            pen=0
                            for data in status:
                                if data == "partially completed":
                                    PC+=1
                                elif data == "completed":
                                    com+=1
                                elif data == "pending":
                                    pen+=1

                            if "partially completed" in status:
                                POparent=PurchaseOrder_Parent.objects.get(PO_id=pk)
                                POparent.PO_status = "partially completed"
                                POparent.save(print("parent status saved"))
                            elif status1 == com:
                                POparent=PurchaseOrder_Parent.objects.get(PO_id=pk)
                                POparent.PO_status = "completed"
                                POparent.save(print("parent status saved"))

                            elif status1 == pen:
                                POparent=PurchaseOrder_Parent.objects.get(PO_id=pk)
                                POparent.PO_status = "pending"
                                POparent.save(print("parent status saved"))
                PK=f'{PO_parent.PO_id}'
                stock_parent=StockEntry_Parent(                        #stock entry patent
                    GRN_id=GRN_ID,GRN_datetime=datetime.today(),
                    PO_id=po_id,PO_datetime=PO_parent.PO_datetime,
                    invoice_no=invoice_no,vendar_id_id=vendor_id,department_id=department,
                    basic_amount=basic_amt,
                    store_id_id=request.POST.get('store_id'),
                    location_id_id=request.POST.get('location_id'),
                    po_location_id=request.POST.get('po_location'),
                    net_amount=net_amt,
                    GRN_amount = grn_amount,
                    status="",paid_amount="0",Payment_status="Pending"
                )
                stock_parent.save(print("stock entry parent saved"))
                context={
                    "PO_parent":PO_parent,'PO_child2':PO_child2,'store_id':store_id
                }
                return HttpResponseRedirect('/stock_entry')
                # return HttpResponseRedirect(f"/search_single_PO/{PK}",context)

        PO_outstanding=[data.qty for data in PO_child2 ]
        PO_outstanding1=[data.received_qty for data in PO_child2 ]
        outstanding=[]
        for data1,data2 in zip(PO_outstanding,PO_outstanding1):
            print("dfgdf",data1,data2)
            if data2 == "":
                data2 = 0
            print("not empty")
            aaa=int(data1)-int(data2)
            outstanding.append(aaa)

        records1=zip(PO_child2,outstanding)

        context={
            "PO_child":PO_child,"PO_parent":PO_parent,"PO_child2":PO_child2,"records1":records1,"vendor_name_2":vendor_name_2,'store_id':store_id,
        }
        return render(request,'pharmacy/Stockentry/search_po.html',context)
    except Exception as error:
           return render(request,'error.html',{'error':error})


@login_required(login_url='/user_login')
def SE_without_po(request):
    try:
        vendor=VendorMaster.objects.all()
        item=Inventory_ItemMaster.objects.all()
        store_detail = StoreMaster.objects.get(store_type=0)
        location_detail = LocationMaster.objects.all()
        dept_detail = ServiceDepartment.objects.all()
        SE_temp1=StockEntry_Temp.objects.all()

        if SE_temp1:
            quantity = [data.physical_qty for data in SE_temp1]
            rate = [data.rate for data in SE_temp1]
            adding = zip(quantity,rate)
            basic_amount = 0
            for data1,data2 in adding:
                basic_amount1 = int(data1) * int(data2)
                basic_amount = basic_amount + basic_amount1
            net_amount1=[data.amount for data in SE_temp1]
            netamount = 0
            for data in net_amount1:
                netamount = netamount + int(float(data))
        else:
            basic_amount = 0
            netamount = 0


        if request.method=="POST":
            if request.POST.get("add_button") == "add_button" :
                item_name=request.POST.get("item_name").split('.')
                temp_table=StockEntry_Temp(
                    PO_id="",
                    item_id_id = item_name[0],
                    store_id_id = request.POST.get("store_id"),
                    serial_batch = request.POST.get("serial_batch"),
                    rate = request.POST.get("rate"),
                    amount = request.POST.get("amount"),
                    expiry_date = request.POST.get("expiry_date"),
                    physical_qty = request.POST.get("physical_qty"),
                    free_qty = request.POST.get("free_qty"),
                    stock_qty = request.POST.get("stock_qty"),
                    schema = request.POST.get("schema"),
                    discount = request.POST.get("discount"),
                    discount_amt=request.POST.get("discount_amt"),
                    tax_details=request.POST.get("tax_detail"),
                    remark = request.POST.get("remark"),
                    status="pending",
                )

                temp_table.save()
                context={
                    "vendor":vendor,'item':item
                }
                return HttpResponseRedirect("/Without_PO")

            if request.POST.get("Save") == "Save":
                vendor_name = request.POST.get("vendor_id")
                basic_amount = request.POST.get("basic_amount")
                net_amount = request.POST.get("net_amount")
                invoice_no = request.POST.get("invoice_no")
                department = request.POST.get("department2")
                # Generate ID

                stoc_parent=StockEntry_Parent.objects.all().count()
                today=date.today()
                today_date=today.strftime("%d%m%y")
                GRN_ID='GRN'+today_date+'00'+str(stoc_parent)
                stock_temp=StockEntry_Temp.objects.all()
                rate=[data.rate for data in stock_temp]
                grn_amount = 0
                #total quantity
                for data in stock_temp:
                    records = Stock_BatchWise.objects.filter(item_id_id=data.item_id_id).last()
                    consume=Stock_BatchWise.objects.filter(item_id_id=data.item_id_id,batch_no=data.serial_batch).last()

                    if data.physical_qty and data.schema and data.discount and data.tax_details:
                        rate_amt = int(data.physical_qty) * int(data.rate)
                        schema_amt = int(int(int(rate_amt) * int(data.schema)) / 100)
                        disc_amt = int(int(int(rate_amt) * int(data.discount)) / 100)
                        tax_amt = int(int(int(rate_amt) * int(data.tax_details)) / 100)
                        total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                        grn_amount += rate_amt - schema_amt - disc_amt + tax_amt
                    elif data.physical_qty and data.tax_details and data.schema:
                        rate_amt = int(data.physical_qty) * int(data.rate)
                        schema_amt = int(int(int(rate_amt) * int(data.schema)) / 100)
                        tax_amt = int(int(int(rate_amt) * int(data.tax_details)) / 100)
                        total_cost = rate_amt - schema_amt + tax_amt
                        grn_amount += rate_amt - schema_amt + tax_amt
                    elif data.physical_qty and data.tax_details and data.discount:
                        rate_amt = int(data.physical_qty) * int(data.rate)
                        disc_amt = int(int(int(rate_amt) * int(data.discount)) / 100)
                        tax_amt =  int(int(int(rate_amt) * int(data.tax_details)) / 100)
                        total_cost = rate_amt - disc_amt + tax_amt
                        grn_amount += rate_amt - disc_amt + tax_amt
                    elif data.physical_qty and data.tax_details:
                        rate_amt = int(data.physical_qty) * int(data.rate)
                        tax_amt =  int(int(int(rate_amt) * int(data.tax_details)) / 100)
                        total_cost = rate_amt + tax_amt
                        grn_amount += rate_amt + tax_amt
                    else:
                        grn_amount = 0
                        total_cost = 0

                    if records:
                        opening=records.total_qty
                        opening_cost = records.total_cost
                        total_cost_amt = int(records.total_cost) + int(total_cost)
                        total_qty = int(records.total_qty) + int(data.physical_qty)
                    else:
                        opening=0
                        opening_cost=0
                        total_cost_amt = total_cost
                        total_qty = data.physical_qty

                    if consume:
                        consume_qty = int(consume.total_consume_qty) + int(data.physical_qty)
                        available_qty = int(consume.available_qty) + int(data.physical_qty)
                    else:
                        consume_qty = data.physical_qty
                        available_qty = data.physical_qty

                    stock_entry_child = StockEntry_Child(
                        GRN_id=GRN_ID,
                        GRN_datetime = datetime.today(),
                        PO_id = "",
                        item_id_id = data.item_id_id,
                        item_qty = "",
                        serial_batch = data.serial_batch,
                        rate = data.rate,
                        amount = data.amount,
                        expiry_date = data.expiry_date,
                        physical_qty = data.physical_qty,
                        total_qty = total_qty,
                        opening_balance = opening,
                        transaction_cost = total_cost,
                        total_cost=total_cost_amt,
                        opening_cost=opening_cost,
                        free_qty = data.free_qty,
                        stock_qty = data.stock_qty,
                        schema = data.schema,
                        discount = data.discount,
                        discount_amt=data.discount_amt,
                        tax_details=data.tax_details,
                        remark = data.remark,
                        status = data.status,
                        movement_status = "GRN Entry",

                    )

                    stock_entry_batch = Stock_BatchWise(
                        GRN_id=GRN_ID,
                        GRN_datetime=datetime.now(),
                        PO_id="",
                        item_id_id=data.item_id_id,
                        batch_no=data.serial_batch,
                        expiry_date=data.expiry_date,
                        received_qty=data.physical_qty,
                        rate=data.rate,
                        amount=data.amount,
                        store_id_id=request.POST.get("store_id"),
                        vendar_id_id=vendor_name,
                        location_id_id=request.POST.get("location"),
                        po_location_id=request.POST.get('po_location'),
                        department_id_id=department,
                        available_qty=available_qty,
                        total_qty=total_qty,
                        total_cost=total_cost_amt,
                        adjust_qty=0,
                        status="",
                        total_consume_qty = consume_qty,
                    )

                    stock_entry_child.save(print("child saved"))
                    stock_entry_batch.save(print("batch saved"))

                SE_temp1.delete()

                stock_entry_parent = StockEntry_Parent(
                    GRN_id=GRN_ID,
                    GRN_datetime=datetime.now(),
                    PO_id="",
                    PO_datetime="",
                    invoice_no=invoice_no,
                    vendar_id_id=vendor_name,
                    department_id=department,
                    location_id_id=request.POST.get("location"),
                    po_location_id=request.POST.get('po_location'),
                    basic_amount=basic_amount,
                    store_id_id=request.POST.get("store_id"),
                    net_amount=net_amount,
                    GRN_amount = grn_amount,
                    status="",
                    paid_amount=0,
                    Payment_status="Pending",
                )

                stock_entry_parent.save()

        context ={
            "vendor":vendor,'item':item,"SE_temp1":SE_temp1,"dept_detail":dept_detail,"basic_amount":basic_amount,"netamount":netamount,
            'store_detail':store_detail,
            'location_detail':location_detail,
        }
        return render(request,"pharmacy/Stockentry/without_PO.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def vendor_payment(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'vendor_payment' in access.user_profile.screen_access:
        try:
            stock_entry_parent1 =StockEntry_Parent.objects.filter(Payment_status__in=["Partially Completed","Pending"])
            vendor_name =[data.vendar_id_id for data in stock_entry_parent1]
            vendor_name1=[]
            for data in vendor_name:
                vendarmaster=VendorMaster.objects.get(id=data)
                vendor_name2 = vendarmaster.vendor_name
                vendor_name1.append(vendor_name2)
            vendor_payment_count=Vendor_Payment.objects.all().count()
            today=date.today()
            today_date=today.strftime("%d%m%y")
            vendor_payment_no='VP'+today_date+str(vendor_payment_count)
            save_all = request.POST.get("save_all")

            if  save_all == "save_all":  # save all
                if request.method == "POST":
                    vendor_id = request.POST.getlist("vendor_id")
                    invoice_no = request.POST.getlist("invoice_no")
                    po_id = request.POST.getlist("po_id")
                    po_date = request.POST.getlist("po_date")
                    grn_id = request.POST.getlist("grn_id")
                    grn_date = request.POST.getlist("grn_date")
                    net_amt = request.POST.getlist("net_amt")
                    payable_amt = request.POST.getlist("payable_amt")
                    paid_amt = request.POST.getlist("paid_amt1")
                    store_id = request.POST.getlist("store_id")
                    location_id = request.POST.getlist("location_id")
                    department_id = request.POST.getlist("department_id")

                    for data in range(len(vendor_id)):
                        # update status in vendor payment
                        vendor_paidamount1=Vendor_Payment.objects.filter(grn_no=grn_id[data])
                        paid=[data.paid_amount for data in vendor_paidamount1]
                        paid_amount1=0
                        for data1 in paid:
                            paid_amount1=paid_amount1+ int(data1)

                        if str(payable_amt[data]) == str(paid_amount1):
                            status = "Completed"
                        elif str(payable_amt[data]) != str(paid_amount1):
                            status = "Partially Completed"

                        stock_entry_parent3=StockEntry_Parent.objects.get(GRN_id=grn_id[data])
                        vendor_payment2=Vendor_Payment(
                            vendor_payment_no=vendor_payment_no,
                            payment_datetime=datetime.now(),
                            invoice_no=invoice_no[data],
                            grn_no=grn_id[data],
                            grn_datetime=stock_entry_parent3.PO_datetime,
                            po_no=po_id[data],
                            po_datetime=po_date[data],
                            vendor_id_id=vendor_id[data],
                            store_id_id=store_id[data],
                            department_id_id=department_id[data],
                            location_id_id=location_id[data],
                            grn_amount=net_amt[data],
                            paid_amount=paid_amt[data],
                            status=status,
                        )
                        if paid_amt[data]:
                            vendor_payment2.save(print("vendor payment is saved"))

                            # update paid amount stock entry parent and change status

                            stock_entry_parent = StockEntry_Parent.objects.get(GRN_id=grn_id[data])
                            stock_entry_parent.paid_amount= int(stock_entry_parent.paid_amount)+int(paid_amt[data])
                            stock_entry_parent.save()

                            if int(stock_entry_parent.GRN_amount) == stock_entry_parent.paid_amount:
                                stock_entry_parent.Payment_status = "completed"
                                stock_entry_parent.save(print("stockentry parent status change"))
                            else:
                                stock_entry_parent.Payment_status = "partially completed"
                                stock_entry_parent.save(print("stockentry parent status change"))
                    return HttpResponseRedirect("/vendor_payment")
            stock_entry_parent_outstanding=[]
            stock_entry_parent_netamount=[data.GRN_amount for data in stock_entry_parent1]
            stock_entry_paid_amount=[data.paid_amount for data in stock_entry_parent1]
            stockentry_parent_4 = zip(stock_entry_parent_netamount,stock_entry_paid_amount)
            for data1,data2 in stockentry_parent_4:
                if data1 and data2:
                    stock_entry_parent_outstanding.append(int(data1)-int(data2))
                else:
                    stock_entry_parent_outstanding.append('0')

            stock_entry_parent2=zip(stock_entry_parent1,vendor_name1,stock_entry_parent_outstanding)

            context={
                "stock_entry_parent2":stock_entry_parent2
            }
            return render(request,"pharmacy/vendor_payment.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def vendor_payment_js(request):
    try:
        vendor_name = request.POST.get("vendor_id")
        invoice_no = request.POST.get("invoice_no")
        po_id = request.POST.get("po_id")
        po_date = request.POST.get("po_date")
        grn_id = request.POST.get("grn_id")
        grn_date = request.POST.get("grn_date")
        net_amt = request.POST.get("net_amt")
        payable_amt = request.POST.get("payable_amt")
        paid_amt = request.POST.get("paid_amt")
        store_id = request.POST.get("store_id")
        location_id = request.POST.get("location_id")
        department_id = request.POST.get("department_id")

        # update status in vendor payment
        if int(payable_amt) == int(paid_amt):
            status = "Completed"
        else:
            status = "Partially Completed"
        vendor_payment_count=Vendor_Payment.objects.all().count()
        today=date.today()
        today_date=today.strftime("%d%m%y")
        vendor_payment_no='VP'+today_date+str(vendor_payment_count)

        vendor_payment3=Vendor_Payment(
            vendor_payment_no=vendor_payment_no,
            payment_datetime=datetime.today(),
            invoice_no=invoice_no,
            grn_no=grn_id,
            grn_datetime=grn_date,
            po_no=po_id,
            po_datetime=po_date,
            vendor_id_id=vendor_name,
            store_id_id=store_id,
            department_id_id=department_id,
            location_id_id=location_id,
            po_location_id=request.POST.get("po_location"),
            grn_amount=net_amt,
            paid_amount=paid_amt,
            status=status,
        )
        vendor_payment3.save(print("vendor payment is saved"))

        # update statusstock entry parent
        stock_entry_parentt = StockEntry_Parent.objects.get(GRN_id=grn_id)
        stock_entry_parentt.paid_amount= int(stock_entry_parentt.paid_amount)+int(paid_amt)
        stock_entry_parentt.save()

        if int(stock_entry_parentt.GRN_amount) == int(stock_entry_parentt.paid_amount):
            stock_entry_parentt.Payment_status = "Completed"
            stock_entry_parentt.save(print("stockentry parents status change"))
        else:
            stock_entry_parentt.Payment_status = "Partially Completed"
            stock_entry_parentt.save(print("stockentry parent status change"))

        data="Successfully paid to vendor"
        return JsonResponse(data,safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def item_issue_to_mainstore(request):
    try:
        po_parent=PurchaseOrder_Parent.objects.filter(PO_status__in=["completed","partially completed"],issue_status__in=["pending","partially completed"])

        context={
            'po_parent':po_parent,
        }
        return render(request,'pharmacy/item_issue_mainstore/item_issue_to_mainstore.html',context)
    except Exception as error:
        return render(request,'error.html',{'error':error})


@login_required(login_url='/user_login')
def item_issue_tomainstore(request,po_id):
    try:
        po_child=PurchaseOrder_Child.objects.filter(PO_Id=po_id,issue_status__in=["pending","partially completed"])
        PO_parent=PurchaseOrder_Parent.objects.get(PO_id=po_id)
        receiving_store=StoreMaster.objects.get(location_id_id=PO_parent.po_location,store_type=1)
        cpc_store=StoreMaster.objects.get(location_id_id=PO_parent.Location_id,store_type=0)
        batch_nos =[]
        for data in po_child:
            get_batch = Stock_BatchWise.objects.exclude(available_qty=0).filter(item_id_id=data.item_id_id,location_id_id=PO_parent.Location,store_id_id=cpc_store.id).order_by('expiry_date')
            batch_no = []
            for data in get_batch:
                print(data,data.batch_no)
                batch_no.append(data.batch_no)
            batch_nos.append(batch_no)

        save_all = request.POST.get("save_all")
        if save_all == "save_all":
            if request.method == "POST":
                # Generate ID
                item_issue_parent_count=Item_Issue_Parent.objects.all().count()
                today=date.today()
                today_date=today.strftime("%d%m%y")
                item_issue_no='ITI'+today_date+"00"+str(item_issue_parent_count)
                item_id=request.POST.getlist("item_id_id")
                barcode=request.POST.getlist("barcode")
                serial_batch=request.POST.getlist("serial_batch")
                expiry_date=request.POST.getlist("expiry_date")
                issued_qty=request.POST.getlist("issued_qty")
                indent_qty=request.POST.getlist("indent_qty")
                available_qty=request.POST.getlist("available_qty")
                rate=request.POST.getlist("rate")
                amount=request.POST.getlist("amount")
                remark=request.POST.getlist("remark")

                # Item Isuue Parent

                ITI_Child3=Item_Issue_Child.objects.filter(intent_no=po_id)
                totalamount3=[data.amount for data in ITI_Child3]
                totalamts=0
                for data in totalamount3:
                    totalamts= int(totalamts) + int(data)

                item_issue_parent=Item_Issue_Parent(
                        item_issue_no=item_issue_no,
                        intent_no=request.POST.get("po_no"),
                        item_issue_date=datetime.now(),
                        issued_store_id=cpc_store.id,
                        received_store_id=request.POST.get("p_received_store_1"),
                        location_id_id=cpc_store.location_id_id,
                        issue_location_id=cpc_store.location_id_id,
                        receive_location_id=request.POST.get("receive_location"),
                        department_id=request.POST.get("department_1"),
                        approved_by=request.POST.get("p_approved_by"),
                        total_amount=totalamts,
                        p_status="pending"
                )
                item_issue_parent.save()

                for data in range(len(issued_qty)):
                    if barcode[data] and serial_batch[data] and issued_qty[data] != "":
                        # item issue child total quantity
                        totalamt=Stock_BatchWise.objects.filter(item_id_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                        if issued_qty[data] == "":
                            issued_qty[data] = 0
                        total_amount = int(str(totalamt.total_qty)) - int(str(issued_qty[data]))

                        # item issue child available quantity
                        available = Stock_BatchWise.objects.filter(item_id_id=item_id[data],batch_no=serial_batch[data],location_id_id=cpc_store.location_id_id).last()
                        available_main = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data],batch_no=serial_batch[data],store_id_id=request.POST.get("p_received_store_1")).last()
                        total_main = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data],store_id_id=request.POST.get("p_received_store_1")).last()
                        if not available:
                            available_qty = 0
                        else:
                            available_qty = available.available_qty
                        available_qty = int(str(available_qty)) - int(str(issued_qty[data]))

                        if total_main:
                            total_main_qty=int(str(total_main.total_qty)) + int(str(issued_qty[data]))
                        else:
                            total_main_qty=issued_qty[data]

                        if available_main:
                            available_main_qty=int(str(available_qty)) + int(str(issued_qty[data]))
                        else:
                            available_main_qty=issued_qty[data]
                        get_po_id = Stock_BatchWise.objects.filter(item_id_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                        po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.PO_id,item_id_id=item_id[data])

                        if po_detail.schema and po_detail.discount and po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                        elif po_detail.schema and po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt - schema_amt + tax_amt
                        elif po_detail.discount and po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt - disc_amt + tax_amt
                        elif po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt + tax_amt
                        else:
                            total_cost = int(issued_qty[data]) * int(rate[data])

                        total_cost_amt = int(totalamt.total_cost) - int(total_cost)

                        item_issue_child = Item_Issue_Child(
                            item_issue_no = item_issue_no,
                            intent_no = request.POST.get("po_no"),
                            item_id_id = item_id[data],
                            item_issue_date = datetime.now(),
                            barcode = barcode[data],
                            serial_batch = serial_batch[data],
                            expiry_date = expiry_date[data],
                            available_qty = issued_qty[data],
                            issued_qty = issued_qty[data],
                            rate = rate[data],
                            intent_qty = indent_qty[data],
                            total_amount = total_amount,
                            opening_balance = totalamt.total_qty,
                            transaction_cost = total_cost,
                            total_cost=total_cost_amt,
                            opening_cost=totalamt.total_cost,
                            remark = remark[data],
                            priority = '',
                            amount = amount[data],
                            status = "",
                            movement_status = "CPC Issue Entry",
                        )
                        batch_wise=Stock_BatchWise_Mainstore(                                                      #stock entry batwise
                            item_issue_no=item_issue_no,
                            item_issue_date=datetime.now(),
                            intent_no=request.POST.get("po_no"),
                            indent_date=PO_parent.PO_datetime,
                            item_id_id=item_id[data],
                            batch_no=serial_batch[data],
                            expiry_date=expiry_date[data],
                            received_qty=issued_qty[data],
                            rate=rate[data],amount=amount[data],store_id_id=request.POST.get('p_received_store_1'),
                            vendor_id_id=request.POST.get('vendor_id'),
                            department_id_id=request.POST.get("department_1"),
                            location_id_id=cpc_store.location_id_id,
                            receive_location_id=request.POST.get("receive_location"),
                            available_qty=available_main_qty,
                            total_qty=total_main_qty,
                            total_cost = total_cost,
                            adjust_qty="",
                            status=" ",
                            total_consume_qty = '',
                        )
                        if barcode[data] and serial_batch[data] and issued_qty[data] != "":
                            item_issue_child.save()
                            batch_wise.save()

                            # Update Total Cost to Batchwise table
                            total_cost_detail = Stock_BatchWise.objects.filter(item_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                            if issued_qty[data] == "":
                                total_cost = 0
                            total_cost_detail.total_cost = int(total_cost_detail.total_cost) - int(total_cost)
                            total_cost_detail.save()

                            # Update available Amount To Batchwise Table

                            available=Stock_BatchWise.objects.filter(item_id=item_id[data],batch_no=serial_batch[data],location_id_id=cpc_store.location_id_id).last()
                            if issued_qty[data] == "":
                                issued_qty[data]=0
                            available_qty= int(str(available.available_qty)) - int(str(issued_qty[data]))
                            available.available_qty=available_qty
                            available.save()

                            # Update Total Quantity to Batchwise table

                            totalamt=Stock_BatchWise.objects.filter(item_id_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                            if issued_qty[data] == "":
                                issued_qty[data] = 0
                            total_amount = int(str(totalamt.total_qty)) - int(str(issued_qty[data]))
                            totalamt.total_qty = total_amount
                            totalamt.save()

                            #update purchase order child table issued qty and issue_status
                            #received

                            po_child = PurchaseOrder_Child.objects.get(item_id_id=item_id[data],PO_Id=po_id)
                            issue_qty = int(po_child.issued_qty) + int(issued_qty[data])
                            if int(po_child.qty) == issue_qty:
                                po_child.issue_status = 'completed'
                                po_child.issued_qty = issue_qty
                                po_child.save()
                            else:
                                po_child.issue_status = 'partially completed'
                                po_child.issued_qty = issue_qty
                                po_child.save()

                po_count = PurchaseOrder_Child.objects.filter(PO_Id=po_id).count()
                completed_count = PurchaseOrder_Child.objects.filter(PO_Id=po_id,status='completed').count()
                po_parent = PurchaseOrder_Parent.objects.get(PO_id=po_id)
                if po_count == completed_count:
                    po_parent.issue_status = 'completed'
                    po_parent.save()
                else:
                    po_parent.issue_status = 'partially completed'
                    po_parent.save()

                po_id=f'{PO_parent.PO_id}'
                context={

                }
                return HttpResponseRedirect(f"/item_issue_tomainstore/{po_id}",context)


        #outstanding Value
        outstanding_ITI=Item_Issue_Child.objects.filter(intent_no=po_id)
        issue_qty_frm_ITI=[data.issued_qty for data in outstanding_ITI]
        intent_qty_frm_ITI=[data.qty for data in po_child]
        issue_qty_frm_ITI.extend([0] * (len(intent_qty_frm_ITI)-len(issue_qty_frm_ITI)))
        record1=zip(issue_qty_frm_ITI,intent_qty_frm_ITI)
        if not issue_qty_frm_ITI:
            records=zip(po_child,intent_qty_frm_ITI,batch_nos)
        else:
            Outstanding_value=[]
            for data1,data2 in record1:
                data=int(data2)-int(data1)
                Outstanding_value.append(data)
            records=zip(po_child,Outstanding_value,batch_nos)
        context={
            'po_child':po_child,
            'PO_parent':PO_parent,
            'receiving_store':receiving_store,
            'records':records,
        }
        return render(request,'pharmacy/item_issue_mainstore/po_list_details.html',context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def search_batch_intent_JQ(request):
    try:
        serial_batch=request.POST.get("serial_batch")
        item_id=request.POST.get("item_id")
        batchwise=Stock_BatchWise.objects.filter(batch_no=serial_batch,item_id_id=item_id).last()
        expiry=str(batchwise.expiry_date)
        my_dict=json.dumps({
            'expiry_date': expiry,
            "rate": batchwise.rate,
            "available_qty":batchwise.available_qty,
        })
        data=eval(my_dict)
        return JsonResponse(data,content_type='application/json',safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})


@login_required(login_url='/user_login')
def material_indent(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'material_indent' in access.user_profile.screen_access:
        try:
            request_store = request.store_id
            request_location = request.location
            mainstore = StoreMaster.objects.filter(store_type=1)
            substore = StoreMaster.objects.filter(store_type=2)
            store_master=StoreMaster.objects.filter(store_type="2",id__in=request_store).last()
            main_store = StoreMaster.objects.filter(id__in=request_store,store_type=1).last()
            item_master=Inventory_ItemMaster.objects.all()
            material_intent_temp=Material_Intent_Temp.objects.filter(location_id_id=request_location)
            Insert_button=request.POST.get("insert")
            Saved_button=request.POST.get("Saved_button")
            if Insert_button == "Insert":
                if request.method == "POST":
                    main_store_name = request.POST.get("main_store_id")
                    main_store_name1 = StoreMaster.objects.get(id=main_store_name)
                    sub_store = request.POST.get("sub_store")
                    sub_store1 = StoreMaster.objects.get(id=sub_store)
                    priority = request.POST.get("priority")
                    item_name = request.POST.get("item_name")
                    department = request.POST.get("department_id")
                    quantity = request.POST.get("quantity")
                    item_code = request.POST.get("item_code")
                    item_belongs_to = request.POST.get("item_belongs_to")
                    amount = request.POST.get("amount")
                    remark = request.POST.get("remark")
                    material_intent_count=Material_Intent_Parent.objects.all().count()
                    today = date.today()
                    today_date = today.strftime("%d%m%y")
                    material_intent_id = "MI"+ today_date +"00"+str(material_intent_count)
                    location_id=StoreMaster.objects.get(id=sub_store)

                    material_intent_temp1=Material_Intent_Temp(
                        intent_id=material_intent_id,
                        intent_datetime=datetime.now(),
                        substore_id_id=sub_store,
                        department_id=department,
                        main_store_id=main_store_name,
                        location_id_id=location_id.location_id_id,
                        priority=priority,
                        item_id_id=item_name,
                        quantity=quantity,
                        item_code=item_code,
                        item_belongs_to=item_belongs_to,
                        remark=remark,
                        status="Pending",
                    )
                    material_intent_temp1.save(print("temporary table is saved"))
                    context ={
                        "store_master":store_master,"item_master":item_master,'material_intent_temp':material_intent_temp,
                        'main_store': main_store,'request_store':request_store,'substore':substore,'mainstore':mainstore,'sub_store':sub_store1,
                        'main_store_name':main_store_name1,'priority':priority
                    }
                    return render(request,'pharmacy/material_indent.html',context)

            if  Saved_button =="Saved_button":
                if request.method == "POST":

                    for data in material_intent_temp:
                        material_intent_child=Material_Intent_Child(
                            intent_id=data.intent_id,
                            intent_datetime=datetime.now(),
                            priority=data.priority,
                            item_id_id=data.item_id_id,
                            quantity=data.quantity,
                            received_qty=0,
                            item_code=data.item_code,
                            item_belongs_to=data.item_belongs_to,
                            remark=data.remark,
                            status="Pending",

                        )

                        material_intent_child.save(print("material_intent_child saved"))

                    material_intent_parent=Material_Intent_Parent(
                        intent_id=material_intent_temp.last().intent_id,
                        intent_datetime=datetime.now(),
                        substore_id_id=material_intent_temp.last().substore_id_id,
                        main_store_id=material_intent_temp.last().main_store_id,
                        location_id_id=material_intent_temp.last().location_id_id,
                        department_id=material_intent_temp.last().department_id,
                        p_status="Pending",
                        approval_status = 'pending'
                    )
                    material_intent_parent.save(print("material_intent_parent saved"))

                    Material_Intent_Temp.objects.filter(location_id_id=request_location).delete()
                    return HttpResponseRedirect("/material_indent")

            context ={
                "store_master":store_master,"item_master":item_master,'material_intent_temp':material_intent_temp,
                'main_store': main_store,'request_store':request_store,'substore':substore,'mainstore':mainstore
            }
            return render(request,'pharmacy/material_indent.html',context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def SE_preview(request):
    try:
        records = StockEntry_Parent.objects.all().last()
        if records:
            PO_date = records.PO_datetime
            payment_status= records.Payment_status
            GRN_date = records.GRN_datetime
            grn_id=records.GRN_id
            PO_id = records.PO_id
            vendor_id = records.vendar_id_id
            bill_amount = records.net_amount
            total_amount = records.basic_amount
            tax =''
            vendor_master = VendorMaster.objects.get(id=vendor_id)
            vendor_email=vendor_master.email
            vendor_name = vendor_master.vendor_name
            stock_entry_child = StockEntry_Child.objects.filter(GRN_id=grn_id)
            context = {
                "stock_entry_child":stock_entry_child,"PO_date":PO_date,"GRN_date":GRN_date,"vendor_name":vendor_name,"payment_status":payment_status,"bill_amount":bill_amount,
                "total_amount":total_amount,"tax":tax,"vendor_email":vendor_email

            }
            return render(request,"pharmacy/Stockentry/SE_preview.html",context)
        return render(request,"pharmacy/Stockentry/SE_preview.html")
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def meterial_intent_JS(request):
    try:
        item_name=request.GET.get("item_name")
        item_master=Inventory_ItemMaster.objects.get(id=item_name)
        belongs_to1=ItemBelongsToMaster.objects.get(id=item_master.belongs_to)
        dept = item_master.department_id
        service_depart =ServiceDepartment.objects.get(id=dept)
        # rate = PurchaseOrder_Child.objects.filter(item_id_id=item_name).last()

        my_dict=json.dumps({
            'belongs_to1': belongs_to1.belongs_to,
            "shortcode1": item_master.shortcode,
            "department": service_depart.service_department,
            "dept_id":dept,
            # 'rate' : rate.rate,
        })
        data1=eval(my_dict)
        return JsonResponse(data1,content_type='application/json',safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def material_indent_approval(request):
    try:
        vendor=VendorMaster.objects.all()
        material_approved=Material_Intent_Parent.objects.select_related('substore_id','department').filter(approval_status="approved")
        material_pending=Material_Intent_Parent.objects.select_related('substore_id','department').filter(approval_status="pending")
        count_approved=material_approved.count()
        count_pending=material_pending.count()
        context={
            'vendor':vendor,'material_pending':material_pending,'material_approved':material_approved,'count_approved':count_approved,'count_pending':count_pending
        }
        return render(request,'pharmacy/material_indent_approval.html',context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def material_indent_item_detail(request,indent_id):
    try:
        records=Material_Intent_Parent.objects.get(intent_id=indent_id)
        MI_approve=Material_Intent_Child.objects.filter(intent_id=indent_id)
        approve=request.POST.get("Approve")
        print("approve",approve)
        if request.method == "POST":
            if approve == "Approved":
                print("approved")
                for data in MI_approve:
                    data.approval_status="approved"
                    data.save(print("save"))
                records.approval_status = "approved"
                records.save()
                return HttpResponseRedirect("/material_indent_approval")
        context={
            "records":records,"MI_approve":MI_approve
        }
        return render(request,"pharmacy/material_indent_item_detail.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def materialindent_approve_item_detail(request,indent_id):
    try:
        MI_approve=Material_Intent_Child.objects.filter(intent_id=indent_id)

        context={
        "MI_approve" : MI_approve
        }
        return render(request,"pharmacy/materialindent_approve_item_detail.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def indent_inbox(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'indent_inbox' in access.user_profile.screen_access:
        try:
            store_master=StoreMaster.objects.filter(store_type="2")
            substore=[data.store_name for data in store_master]
            material_intent_parent=Material_Intent_Parent.objects.filter(p_status__in=["Pending","Partially Completed"])
            search=request.POST.get("search")
            if search == "search":
                if request.method == "POST":
                    start_date=request.POST.get('from_date')
                    end_date=request.POST.get('to_date')
                    substore=request.POST.get('sub_store')
                    if  start_date and end_date != " ":
                        material_intent_parent=Material_Intent_Parent.objects.filter(intent_datetime__range=[start_date,end_date])
                        context={
                        'material_intent_parent':material_intent_parent,"substore":substore
                    }
                        return render(request,'pharmacy/indent_inbox.html',context)
                    elif start_date and end_date and substore != " ":
                        material_intent_parent=Material_Intent_Parent.objects.filter(intent_datetime__range=[start_date,end_date],substore_id=substore)
                        context={
                        'material_intent_parent':material_intent_parent,"substore":substore
                    }
                        return render(request,'pharmacy/indent_inbox.html',context)

                    else:
                        material_intent_parent=Material_Intent_Parent.objects.filter(substore_id=substore)
                        context={
                        'material_intent_parent':material_intent_parent,"substore":substore
                    }
                        return render(request,'pharmacy/indent_inbox.html',context)
                return HttpResponseRedirect("/indent_inbox")
            context={
                'substore':substore,"material_intent_parent":material_intent_parent
            }
            return render(request,'pharmacy/indent_inbox.html',context)
        except Exception as error:
           return render(request,'error.html',{'error':error})

    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def item_issue(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_issuse' in access.user_profile.screen_access:
        try:
            material_intent_parent=Material_Intent_Parent.objects.filter(p_status__in=["Pending","Partially Completed"],location_id_id=request.location)

            context={
                'material_intent_parent':material_intent_parent,
            }
            return render(request,'pharmacy/Item_Issue/item_issue.html',context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


@login_required(login_url='/user_login')
def WO_intent(request):
    try:
        item_master=Inventory_ItemMaster.objects.all()
        item_issue_temp=Item_Issue_Temp.objects.all()
        store_master=StoreMaster.objects.filter(store_type="2")
        mainstore=StoreMaster.objects.filter(store_type="1").first()
        dept_detail = ServiceDepartment.objects.all()
        if request.POST.get("add_btn") == "add_btn":
            if request.method == "POST":
                item_name = request.POST.get("item_name").split('.')
                item_issue_tem=Item_Issue_Temp(
                    intent_no="",
                    item_id_id=item_name[0],
                    priority="",
                    barcode=request.POST.get("barcode"),
                    serial_batch=request.POST.get("serial_batch"),
                    expiry_date=request.POST.get("expiry_date"),
                    available_qty=request.POST.get("available_qty"),
                    issued_qty=request.POST.get("issued_qty"),
                    rate=request.POST.get("rate"),
                    intent_qty="",
                    remaining_qty="",
                    remark=request.POST.get("remark"),
                    amount=request.POST.get("amount"),
                )
                item_issue_tem.save()
                return HttpResponseRedirect("/WO_intent")

        if request.POST.get("save_btn") == "save_btn":


            item_issue_parent_count=Item_Issue_Parent.objects.all().count()
            today=date.today()
            today_date=today.strftime("%d%m%y")
            item_issue_no='ITI'+today_date+"00"+str(item_issue_parent_count)

            item_id=[data.item_id for data in item_issue_temp]
            barcode=[data.barcode for data in item_issue_temp]
            serial_batch=[data.serial_batch for data in item_issue_temp]
            expiry_date=[data.expiry_date for data in item_issue_temp]
            available_qty=[data.available_qty for data in item_issue_temp]
            issued_qty=[data.issued_qty for data in item_issue_temp]
            rate=[data.rate for data in item_issue_temp]
            remark=[data.remark for data in item_issue_temp]
            amount=[data.amount for data in item_issue_temp]

            for data in item_issue_temp:
                #total quantity
                totalamt = Stock_BatchWise.objects.filter(item_id_id=data.item_id_id).last()
                total_amount = int(str(totalamt.total_qty)) - int(str(data.issued_qty))
                totalamt.total_qty = total_amount
                totalamt.save()
                available = Stock_BatchWise.objects.filter(batch_no=data.serial_batch).last()
                #available Quantity
                available_qty = int(str(available.available_qty)) - int(str(data.issued_qty))
                available.available_qty = available_qty
                available.save()

                issue_child=Item_Issue_Child(
                    item_issue_no=item_issue_no,
                    intent_no="",
                    item_id_id=data.item_id_id,
                    item_issue_date=datetime.today(),
                    barcode=data.barcode,
                    serial_batch=data.serial_batch,
                    expiry_date=data.expiry_date,
                    available_qty=data.issued_qty,
                    issued_qty=data.issued_qty,
                    rate=data.rate,
                    intent_qty="",
                    total_amount=totalamt.total_qty,
                    opening_balance=data.issued_qty,
                    transaction_cost = '',
                    total_cost='',
                    opening_cost='',
                    remark=data.remark,
                    priority="",
                    amount=data.amount,
                    status="",
                    movement_status="CPC Issue Entry"
                )

                issue_child.save()

            ITI_Child3=Item_Issue_Child.objects.filter(item_issue_no=item_issue_no)
            totalamount3=[data.amount for data in ITI_Child3]
            totalamts=0
            for data in totalamount3:
                totalamts=int(totalamts)+int(data)
            item_issue_parent=Item_Issue_Parent(
                    item_issue_no=item_issue_no,
                    intent_no="",
                    item_issue_date=datetime.now(),
                    issued_store_id=request.POST.get("issuing_store_name"),
                    received_store_id=request.POST.get("receiving_store"),
                    department_id=request.POST.get("department"),
                    approved_by=request.POST.get("approved_by"),
                    total_amount=totalamts,
                    p_status="pending"
            )

            item_issue_parent.save()
            item_issue_temp.delete()
            return HttpResponseRedirect("/WO_intent")
        context={
            "item_master":item_master,"item_issue_temp":item_issue_temp,"store_master":store_master,"mainstore":mainstore,"dept_detail":dept_detail
        }
        return render(request,"pharmacy/Item_Issue/WO_intent.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def without_JQ(request):
    try:
        serial_batch=request.POST.get("serial_batch")
        item_id=request.POST.get("item_id").split('.')
        batchwise=Stock_BatchWise.objects.filter(batch_no=serial_batch,item_id_id=item_id[0]).last()
        expiry=str(batchwise.expiry_date)
        my_dict=json.dumps({
            'expiry_date': expiry,
            "rate": batchwise.rate,
            "available_qty":batchwise.available_qty,
        })

        data=eval(my_dict)
        return JsonResponse(data,content_type='application/json',safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

# clicking material item intent records Item issue
@login_required(login_url='/user_login')
def search_material_intent(request,pk):
    try:    
        materialintent_child = Material_Intent_Child.objects.filter(intent_id=pk,status__in=["Pending","Partially Completed"])
        batch_nos =[]
        materialintent_parent = Material_Intent_Parent.objects.get(intent_id=pk,location_id_id=request.location)
        for data in materialintent_child:
            get_batch = Stock_BatchWise_Mainstore.objects.exclude(available_qty=0).filter(item_id_id=data.item_id_id,receive_location_id=materialintent_parent.location_id_id).order_by('expiry_date')
            batch_no = []
            for data in get_batch:
                batch_no.append(data.batch_no)
            batch_nos.append(batch_no)

        save_all = request.POST.get("save_all")
        if save_all == "save_all":
            if request.method == "POST":
                # Generate ID
                item_issue_parent_count=Item_Issue_ToSubStore_Parent.objects.all().count()
                today=date.today()
                today_date=today.strftime("%d%m%y")
                item_issue_no='ITI'+today_date+"00"+str(item_issue_parent_count)

                item_id=request.POST.getlist("item_id_id")
                barcode=request.POST.getlist("barcode")
                serial_batch=request.POST.getlist("serial_batch")
                expiry_date=request.POST.getlist("expiry_date")
                issued_qty=request.POST.getlist("issued_qty")
                indent_qty=request.POST.getlist("indent_qty")
                available_qty=request.POST.getlist("available_qty")
                rate=request.POST.getlist("rate")
                amount=request.POST.getlist("amount")
                p_priority=request.POST.getlist("p_priority")
                remark=request.POST.getlist("remark")

                # Item Isuue Parent

                ITI_Child3=Item_Issue_ToSubStore_Child.objects.filter(intent_no=pk)
                totalamount3=[data.amount for data in ITI_Child3]
                totalamts=0
                for data in totalamount3:
                    totalamts= int(totalamts) + int(data)
                issued_store_id=StoreMaster.objects.get(location_id=request.POST.get("location_id"),store_type=1)
                item_issue_parent=Item_Issue_ToSubStore_Parent(
                        item_issue_no=item_issue_no,
                        intent_no=request.POST.get("p_indent_no"),
                        item_issue_date=datetime.now(),
                        issued_store_id=issued_store_id.id,
                        received_store_id=request.POST.get("p_received_store_1"),
                        location_id_id=request.POST.get("location_id"),
                        issue_location_id=request.POST.get("location_id"),
                        receive_location_id=request.POST.get("location_id"),
                        department_id=request.POST.get("department_1"),
                        approved_by=request.POST.get("p_approved_by"),
                        total_amount=totalamts,
                        p_status="pending"
                )
                item_issue_parent.save()

                for data in range(len(issued_qty)):
                    if barcode[data] and serial_batch[data] and issued_qty[data] != "":
                        # item issue child total quantity
                        totalamt=Stock_BatchWise_Mainstore.objects.filter(item_id=item_id[data],receive_location_id=request.POST.get("location_id")).last()
                        if issued_qty[data] == "":
                            issued_qty[data] = 0
                        if totalamt:
                            total_amount = int(str(totalamt.total_qty)) - int(str(issued_qty[data]))
                        else:
                            total_amount = issued_qty[data]

                        # item issue child available quantity
                        available = Stock_BatchWise_Mainstore.objects.filter(batch_no=serial_batch[data],receive_location_id=request.POST.get("location_id")).last()
                        if not available:
                            available_qty = 0
                        else:
                            available_qty = available.available_qty
                        available_qty = int(str(available_qty)) - int(str(issued_qty[data]))
                        
                        get_po_id = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data],batch_no=serial_batch[data],receive_location_id=request.POST.get("location_id")).last()
                        po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.intent_no,item_id_id=item_id[data])

                        if po_detail.schema and po_detail.discount and po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                        elif po_detail.schema and po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt - schema_amt + tax_amt
                        elif po_detail.discount and po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt - disc_amt + tax_amt
                        elif po_detail.tex_details:
                            rate_amt = int(issued_qty[data]) * int(rate[data])
                            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                            total_cost = rate_amt + tax_amt
                        else:
                            total_cost = int(issued_qty[data]) * int(rate[data])

                        total_cost_amt = int(totalamt.total_cost) - int(total_cost)

                        item_issue_child = Item_Issue_ToSubStore_Child(
                            item_issue_no = item_issue_no,
                            intent_no = request.POST.get("p_indent_no"),
                            item_id_id = item_id[data],
                            issued_store_id=issued_store_id.id,
                            item_issue_date = datetime.now(),
                            barcode = barcode[data],
                            serial_batch = serial_batch[data],
                            expiry_date = expiry_date[data],
                            available_qty = issued_qty[data],
                            issued_qty = issued_qty[data],
                            rate = rate[data],
                            intent_qty = indent_qty[data],
                            total_amount = total_amount,
                            opening_balance = totalamt.total_qty,
                            transaction_cost = total_cost,
                            total_cost=total_cost,
                            opening_cost=totalamt.total_cost,
                            remark = remark[data],
                            priority = p_priority[data],
                            amount = amount[data],
                            status = "",
                            movement_status = "MainStore Issue Entry",
                        )
                        if barcode[data] and serial_batch[data] and issued_qty[data] != "":
                            item_issue_child.save()

                            # Update Total Cost to Batchwise table
                            total_cost_detail = Stock_BatchWise_Mainstore.objects.filter(item_id=item_id[data],receive_location_id=request.POST.get("location_id")).last()
                            if issued_qty[data] == "":
                                total_cost = 0
                            total_cost_detail.total_cost = int(total_cost_detail.total_cost) - int(total_cost)
                            total_cost_detail.save()

                            # Update available Amount To Batchwise Table

                            available=Stock_BatchWise_Mainstore.objects.filter(item_id=item_id[data],batch_no=serial_batch[data],receive_location_id=request.POST.get("location_id")).last()
                            if issued_qty[data] == "":
                                issued_qty[data]=0
                            available_qty= int(str(available.available_qty)) - int(str(issued_qty[data]))
                            available.available_qty=available_qty
                            available.save()

                            # Update Total Quantity to Batchwise table

                            totalamt=Stock_BatchWise_Mainstore.objects.filter(item_id=item_id[data],receive_location_id=request.POST.get("location_id")).last()
                            if issued_qty[data] == "":
                                issued_qty[data] = 0
                            total_amount = int(str(totalamt.total_qty)) - int(str(issued_qty[data]))
                            totalamt.total_qty = total_amount
                            totalamt.save()

                            #Status

                            mi_child = Material_Intent_Child.objects.get(item_id_id=item_id[data],intent_id=pk)
                            issue_qty = int(mi_child.received_qty) + int(issued_qty[data])

                            if int(mi_child.quantity) == issue_qty:
                                mi_child.status = 'Completed'
                                mi_child.received_qty = issue_qty
                                mi_child.save()
                            else:
                                mi_child.status = 'Partially Completed'
                                mi_child.received_qty = issue_qty
                                mi_child.save()

                mi_count = Material_Intent_Child.objects.filter(intent_id=pk).count()
                completed_count = Material_Intent_Child.objects.filter(intent_id=pk,status='Completed').count()
                mi_parent = Material_Intent_Parent.objects.get(intent_id=pk)
                if mi_count == completed_count:
                    mi_parent.p_status = 'Completed'
                    mi_parent.save()
                else:
                    mi_parent.p_status = 'Partially Completed'
                    mi_parent.save()

                PK=f'{materialintent_parent.intent_id}'
                context={

                }
                return HttpResponseRedirect(f"/search_material_intent/{PK}",context)

        #outstanding Value
        outstanding_ITI=Item_Issue_ToSubStore_Child.objects.filter(intent_no=pk)
        issue_qty_frm_ITI=[data.issued_qty for data in outstanding_ITI]
        intent_qty_frm_ITI=[data.quantity for data in materialintent_child]
        issue_qty_frm_ITI.extend([0] * (len(intent_qty_frm_ITI)-len(issue_qty_frm_ITI)))
        record1=zip(issue_qty_frm_ITI,intent_qty_frm_ITI)
        if not issue_qty_frm_ITI:
            records=zip(materialintent_child,intent_qty_frm_ITI,batch_nos)
        else:
            Outstanding_value=[]
            for data1,data2 in record1:
                data=int(data2)-int(data1)
                Outstanding_value.append(data)
            records=zip(materialintent_child,Outstanding_value,batch_nos)
        context={
            "records":records,"materialintent_parent":materialintent_parent,
        }
        return render(request,'pharmacy/Item_Issue/search_material_intent.html',context)
    except Exception as error:
        return render(request,'error.html',{'error':error})
   
@login_required(login_url='/user_login')
def search_material_intent_JQ(request):
    try:
        serial_batch=request.POST.get("serial_batch")
        item_id=request.POST.get("item_id")
        location_id=request.POST.get("location_id")
        batchwise=Stock_BatchWise_Mainstore.objects.filter(batch_no=serial_batch,item_id_id=item_id,receive_location_id=location_id).last()
        expiry=str(batchwise.expiry_date)
        my_dict=json.dumps({
            'expiry_date': expiry,
            "rate": batchwise.rate,
            "available_qty":batchwise.available_qty,
        })
        data=eval(my_dict)
        return JsonResponse(data,content_type='application/json',safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

# item return to mainstore from substore
@login_required(login_url='/user_login')
def item_return(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'return_to_mainstore' in access.user_profile.screen_access:
        try:
            item_category = ItemCategoryMaster.objects.all()
            item_name = Inventory_ItemMaster.objects.all()
            substore_detail = StoreMaster.objects.filter(store_type = "2")

            if request.POST.get("Search") == "Search":
                items = request.POST.get("po_no").split(".")
                substore_id = request.POST.get("substore_id")
                store_master = StoreMaster.objects.filter(store_type = "2")
                main_store = StoreMaster.objects.filter(store_type="1")
                if substore_id and request.POST.get("item_cat") != "select":
                    item_master = Inventory_ItemMaster.objects.filter(item_category=request.POST.get("item_cat"))
                    item_ids = [data.id for data in item_master]
                    issue_parent=Item_Issue_ToSubStore_Parent.objects.filter(received_store_id=substore_id)
                    Item_Issue_Child1 = []
                    for data in issue_parent:
                        Item_Issue_Child1.append(Item_Issue_ToSubStore_Child.objects.filter(item_id__in=item_ids,item_issue_no=data.item_issue_no))
                    print('Item_Issue_Child1',Item_Issue_Child1)
                elif items[1]:
                    issue_parent=Item_Issue_ToSubStore_Parent.objects.filter(received_store_id=substore_id)
                    Item_Issue_Child1 = []
                    for data in issue_parent:
                        Item_Issue_Child1.append(Item_Issue_ToSubStore_Child.objects.filter(item_id=items[0],item_issue_no=data.item_issue_no))
                context={
                    "store_master":store_master,"Item_Issue_Child1":Item_Issue_Child1,"main_store":main_store,
                    'substore_id':substore_id,
                    }
                return render(request,"pharmacy/item_return/search_issued_item.html",context)

            # save_all=request.POST.get("Save_all")
            # inditual=request.POST.get("inditual_save")
            # print("inditual",inditual)
            # if save_all == "Save_all":
            #     print("save_alll")
            #     if request.method == "POST":
            #         return_store_id=request.POST.get("return_store_id")
            #         batch_no=request.POST.getlist("batch_no")
            #         item_id=request.POST.getlist("item_id")
            #         print("item_id",item_id)
            #         expiry_date=request.POST.getlist("expiry_date")
            #         return_qty=request.POST.getlist("return_qty")
            #         print("return_qty",return_qty)
            #         amount=request.POST.getlist("amount")
            #         print("amount",amount)
            #         rate=request.POST.getlist("rate")
            #         reason=request.POST.getlist("reason")
            #         print("reason",reason)
            #         today=date.today()
            #         today_date=today.strftime("%d%m%y")
            #         counter=Item_Return_Parent.objects.all().count()
            #         item_return_id="IR"+today_date+"00"+str(counter)

            #         item_return_parent=Item_Return_Parent(
            #                 item_return_no=item_return_id,
            #                 return_date=today,
            #                 return_store="1",
            #                 receiving_store=return_store_id,
            #                 status="Pending"
            #             )
            #         item_return_parent.save()

            #         for data in range(len(item_id)):
            #             #opening balance and total quantity of Item_return_Child
            #             batchwise=Stock_BatchWise.objects.filter(item_id=item_id[data]).last()
            #             returnqty= return_qty[data]
            #             print("returnqty",returnqty)
            #             if returnqty == "":
            #                 returnqty=0
            #             total_quantity=int(str(batchwise.total_qty)) - int(str(returnqty))
            #             print("total_quantity",total_quantity)

            #             item_return_child=Item_return_Child(
            #                 item_return_no=item_return_id,
            #                 return_date=datetime.now(),
            #                 batch_no=batch_no[data],
            #                 expiry_date=expiry_date[data],
            #                 item_id=item_id[data],
            #                 return_qty=return_qty[data],
            #                 rate=rate[data],
            #                 amount=amount[data],
            #                 total_qty=total_quantity,
            #                 opening_balance =batchwise.total_qty,
            #                 reason =reason[data],
            #                 status ="Pending",
            #                 movable_status ="Return Entry",
            #             )
            #             if return_qty[data] and amount[data] and reason[data]:
            #                 item_return_child.save()

            #                 # update to total quantity to item issue table

            #                 item_issue_child=Item_Issue_Child.objects.filter(item_id=item_id[data]).last()
            #                 item_issue_child.total_amount=int(str(item_issue_child.total_amount)) - int(str(return_qty[data]))
            #                 item_issue_child.save()

            #                 # update to available quantity item issue table

            #                 Item_issue_available=Item_Issue_Child.objects.filter(serial_batch=batch_no[data]).last()
            #                 Item_issue_available.available_qty=int(str(Item_issue_available.available_qty)) - int(str(return_qty[data]))
            #                 Item_issue_available.save()

            #                 # Update Total Quantity to Batchwise Table

            #                 batchwise1=Stock_BatchWise.objects.filter(item_id=item_id[data]).last()
            #                 batchwise1.total_qty=int(str(batchwise1.total_qty)) + int(str(return_qty[data]))
            #                 batchwise1.save()

            #                 # update Available Quantity to Batchwise Table

            #                 batchwise1_available=Stock_BatchWise.objects.filter(batch_no=batch_no[data]).last()
            #                 batchwise1_available.available_qty=int(str(batchwise1_available.available_qty)) + int(str(return_qty[data]))
            #                 batchwise1_available.save()
            #         return HttpResponseRedirect("/item_return")

            # elif inditual == "inditual_save":
            #     print("inditual")
            #     if request.method == "POST":
            #         return_store_id=request.POST.get("return_store_id")
            #         batch_no=request.POST.get("batch_no")
            #         item_id=request.POST.get("item_id")
            #         expiry_date=request.POST.get("expiry_date")
            #         return_qty=request.POST.get("return_qty")
            #         amount=request.POST.get("amount")
            #         rate=request.POST.get("rate")
            #         reason=request.POST.get("reason")
            #         today=date.today()
            #         today_date=today.strftime("%d%m%y")
            #         counter=Item_Return_Parent.objects.all().count()
            #         item_return_id="IR"+today_date+"00"+str(counter)
            #         if item_id and batch_no:
            #             print("hf")
            #             #update total qty to batchwise table

            #             totalamt=Stock_BatchWise.objects.filter(item_id=item_id).last()
            #             #opening balance(item return child table)
            #             opening_balance = totalamt.total_qty

            #             if return_qty == "":
            #                 return_qty=0
            #             total_amount=int(str(totalamt.total_qty)) + int(str(return_qty))
            #             totalamt.total_qty=total_amount
            #             totalamt.save()

            #             #update total qty,available to item issue child
            #             totalamt1=Item_Issue_Child.objects.filter(item_id=item_id).last()
            #             total_amount1=int(str(totalamt1.total_amount)) - int(str(return_qty))
            #             totalamt1.total_amount=total_amount1
            #             Item_issue_available=Item_Issue_Child.objects.filter(serial_batch=batch_no)
            #             Item_issue_available2=[data.available_qty for data in Item_issue_available]
            #             Item_issue_available3=0
            #             for data1 in Item_issue_available2:
            #                 Item_issue_available3=Item_issue_available3+int(str(data1))
            #             totalamt1.available_qty=Item_issue_available3
            #             totalamt1.save()
            #             #update available qty to batchwise table
            #             available=Stock_BatchWise.objects.filter(batch_no=batch_no).last()
            #             if return_qty == "":
            #                 return_qty=0
            #             available_qty= int(str(available.available_qty)) + int(str(return_qty))
            #             available.available_qty=available_qty
            #             available.save()

            #         item_return_child=Item_return_Child(
            #             item_return_no=item_return_id,
            #             return_date=today,
            #             batch_no=batch_no,
            #             expiry_date=expiry_date,
            #             item_id=item_id,
            #             return_qty=return_qty,
            #             rate=rate,
            #             amount=amount,
            #             total_qty=total_amount1,
            #             opening_balance =opening_balance,
            #             reason =reason,
            #             status ="Pending",
            #             movable_status ="Return Entry",
            #         )
            #         item_return_parent=Item_Return_Parent(
            #             item_return_no=item_return_id,
            #             return_date=today,
            #             return_store="1",
            #             receiving_store=return_store_id,
            #             status=""
            #         )
            #         if return_qty and amount and reason:
            #             item_return_child.save(print("item_return_child"))
            #             item_return_parent.save(print("item_return_parent"))
            #         return HttpResponseRedirect("/item_return")
            context={
                "item_category":item_category,"item_name":item_name,
                'substore_detail':substore_detail,
            }
            return render(request,"pharmacy/item_return/item_return.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def item_return_JS(request):
    try:
        total_qty1 = Stock_BatchWise_Mainstore.objects.filter(item_id=request.POST.get("item_id"),store_id=request.POST.get("receiving_store_id")).last()
        total_qty_1 = int(total_qty1.total_qty) + int(request.POST.get("return_qty"))

        today = date.today()
        today_date = today.strftime("%d%m%y")
        counter = Item_Return_Parent.objects.all().count()
        item_return_id = "IR"+today_date+"00"+str(counter)
        location_id=StoreMaster.objects.get(id=request.POST.get("receiving_store_id"))
        item_return_parent = Item_Return_Parent(
            item_return_no = item_return_id,
            return_date = datetime.today(),
            return_store_id = request.POST.get("return_store_id"),
            receiving_store_id = request.POST.get("receiving_store_id"),
            location_id_id = location_id.location_id_id,
            status = "pending",
        )
        item_id = request.POST.get("item_id")
        return_qty = request.POST.get("return_qty")
        serial_batch = request.POST.get("batch_no")
        rate = request.POST.get("rate")
        get_po_id = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id,batch_no=serial_batch,store_id=request.POST.get("receiving_store_id")).last()
        po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.intent_no,item_id_id=item_id)


        if po_detail.schema and po_detail.discount and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - schema_amt - disc_amt + tax_amt
        elif po_detail.schema and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - schema_amt + tax_amt
        elif po_detail.discount and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - disc_amt + tax_amt
        elif po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt + tax_amt
        else:
            total_cost = int(return_qty) * int(rate)

        total_cost_amt = int(total_qty1.total_cost) + int(total_cost)

        item_return_child = Item_return_Child(
            item_return_no = item_return_id,
            return_date = datetime.today(),
            batch_no = request.POST.get("batch_no"),
            expiry_date = request.POST.get("expiry_date"),
            item_id_id = request.POST.get("item_id"),
            return_qty = request.POST.get("return_qty"),
            rate = request.POST.get("rate"),
            amount = request.POST.get("amount"),
            total_qty = total_qty_1,
            opening_balance = total_qty1.total_qty,
            transaction_cost = total_cost,
            total_cost=total_cost_amt,
            opening_cost=total_qty1.total_cost,
            reason = request.POST.get("reason"),
            status = "pending",
            movable_status = "Item Return",
        )
        item_return_parent.save()
        item_return_child.save()
        # Update Total Cost to Batchwise table
        total_cost_detail = Stock_BatchWise_Mainstore.objects.filter(item_id=item_id,store_id=request.POST.get("receiving_store_id")).last()
        total_cost_detail.total_cost = int(total_cost_detail.total_cost) + int(total_cost)
        total_cost_detail.save()
        # update available qty from batchwise table
        available2 = Stock_BatchWise_Mainstore.objects.filter(item_id=request.POST.get("item_id"),batch_no=request.POST.get("batch_no"),store_id=request.POST.get("receiving_store_id")).last()
        if available2:

            available2.available_qty = int(available2.available_qty) + int(request.POST.get("return_qty"))
            available2.save()

        # update total qty from batchwise table
        total_qty2 = Stock_BatchWise_Mainstore.objects.filter(item_id=request.POST.get("item_id"),store_id=request.POST.get("receiving_store_id")).last()
        if total_qty2:
            total_qty2.total_qty = int(total_qty2.total_qty) + int(request.POST.get("return_qty"))
            total_qty2.save()

        # update available qty from itemissue child table

        available3 = Item_Issue_ToSubStore_Child.objects.filter(item_id=request.POST.get("item_id"),serial_batch=request.POST.get("batch_no"),issued_store_id=request.POST.get("receiving_store_id")).last()
        if available3:
            available3.available_qty = int(available3.available_qty) - int(request.POST.get("return_qty"))
            # available3.total_cost = int(available3.total_cost) - int(total_cost)
            available3.save()

        data='Successfully Item Returned'
        return JsonResponse(data, safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def item_return_to_cpc(request):
    try:
        item_category = ItemCategoryMaster.objects.all()
        item_Name = Inventory_ItemMaster.objects.all()
        item_return_parent = Item_Return_Parent.objects.filter(status='pending')
        mainstore_detail = StoreMaster.objects.filter(store_type=1)
        view_detail = request.POST.get("view_detail")
        if request.POST.get("Search") == "Search":
            item_name1 = request.POST.get("item_name").split(".")
            vendor_master = VendorMaster.objects.all()
            mainstore_id=request.POST.get("mainstore_id")
            if mainstore_id and request.POST.get("item_cat") != "select":
                item_master = Inventory_ItemMaster.objects.filter(item_category=request.POST.get("item_cat"))
                item_ids = [data.id for data in item_master]
                Item_return_child1 = Stock_BatchWise_Mainstore.objects.filter(item_id__in=item_ids,store_id_id=mainstore_id)

                # Item_return_child1 = Stock_BatchWise.objects.filter(item_id__in=item_ids).distinct()
                for data in Item_return_child1:
                    print('data',data)
            elif item_name1:
                Item_return_child1 = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_name1[0],store_id_id=mainstore_id)
            context={
                "vendor_master":vendor_master,"Item_return_child1":Item_return_child1,'mainstore_id':mainstore_id
                }
            return render(request,"pharmacy/item_return/item_return_cpc_search_batchwise.html",context)
        elif view_detail == "view_detail":
            return_parent_no=request.POST.get("return_parent_no")
            item_return_to_mainstore = Item_return_Child.objects.filter(item_return_no=return_parent_no)
            context={
                    "item_return_to_mainstore":item_return_to_mainstore
                    }
            return render(request,"pharmacy/item_return/return_itemdetail.html",context)

        context={
                "item_category":item_category,"item_return_parent":item_return_parent,"item_Name":item_Name,'mainstore_detail':mainstore_detail
                }
        return render(request,"pharmacy/item_return/item_return_to_cpc.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def return_to_cpc_js(request):
    try:
        batch_no = request.POST.get("batch_no")
        item_id = request.POST.get("item_id")
        expiry_date = request.POST.get("expiry_date")
        mainstore_id = request.POST.get("mainstore_id")
        return_qty = request.POST.get("return_qty")
        reason = request.POST.get("reason")
        rate = request.POST.get("rate")
        amount = request.POST.get("amount")

        total_qty1 = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id).last()
        total_qty_1 = int(total_qty1.total_qty) - int(return_qty)
        today=date.today()
        today_date=today.strftime("%d%m%y")
        counter=Item_Return_ToCPC_Parent.objects.all().count()
        item_return_id="IRS"+today_date+"00"+str(counter)

        location_id=StoreMaster.objects.get(id=mainstore_id)
        cpc_store=StoreMaster.objects.get(store_type=0)

        return_cpc_parent=Item_Return_ToCPC_Parent(
            return_no=item_return_id,
            return_date=today,
            return_store_id=mainstore_id,
            location_id_id=location_id.location_id_id,
            receiving_store_id=cpc_store.id,
            request_no = '',
            stock_transfer = '0',
            status="",
        )

        get_po_id = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id,batch_no=batch_no,store_id=mainstore_id).last()
        po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.intent_no,item_id_id=item_id)


        if po_detail.schema and po_detail.discount and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - schema_amt - disc_amt + tax_amt
        elif po_detail.schema and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - schema_amt + tax_amt
        elif po_detail.discount and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - disc_amt + tax_amt
        elif po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt + tax_amt
        else:
            total_cost = int(return_qty) * int(rate)

        total_cost_amt = int(total_qty1.total_cost) - int(total_cost)

        item_return_cpc_child=Item_Return_ToCPC_Child(
            return_no=item_return_id,
            return_date=datetime.today(),
            batch_no=batch_no,
            expiry_date=expiry_date,
            rate=rate,
            amount=amount,
            item_id_id=item_id,
            return_qty=return_qty,
            total_qty=total_qty_1,
            opening_balance=total_qty1.total_qty,
            transaction_cost=total_cost,
            total_cost=total_cost_amt,
            opening_cost=total_qty1.total_cost,
            reason=reason,
            status="Pending",
            stock_transfer = '0',
            movable_status='Return To CPC'
        )

        return_cpc_parent.save()
        item_return_cpc_child.save()

        totalqty2=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id,store_id=mainstore_id).last()
        totalqty2.total_qty = int(str(total_qty1.total_qty)) - int(str(return_qty))
        totalqty2.total_cost = total_cost_amt
        totalqty2.save()

        availableqty=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id,batch_no=batch_no,store_id=mainstore_id).last()
        availableqty.available_qty= int(str(availableqty.available_qty)) - int(str(return_qty))
        availableqty.save()

        totalqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id,po_location=location_id.location_id_id).last()
        totalqty_m.total_qty = int(str(totalqty_m.total_qty)) + int(str(return_qty))
        totalqty_m.total_cost = int(str(totalqty_m.total_cost)) + int(total_cost)
        totalqty_m.save()

        availableqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id,batch_no=batch_no,po_location=location_id.location_id_id).last()
        availableqty_m.available_qty= int(str(availableqty_m.available_qty)) + int(str(return_qty))
        availableqty_m.save()

        # issue_list_c=Item_return_Child.objects.filter(item_id_id=item_id)
        # for data in issue_list_c:
        #     data.status='completed'
        #     data.save()
        #     issue_list_p=Item_Return_Parent.objects.get(item_return_no=data.item_return_no)
        #     issue_list_p.status='completed'
        #     issue_list_p.save()

        data='Successfully Item Returned to CPC'
        return JsonResponse(data, safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def without_indent_stock_transfer(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_request_to_mainstore' in access.user_profile.screen_access:
        try:
            item_detail = Inventory_ItemMaster.objects.all()
            item_issue_temp=Item_Transfer_Issue_Temp.objects.all()
            store_master=StoreMaster.objects.filter(store_type="1")
            mainstore=StoreMaster.objects.filter(store_type="1").first()
            dept_detail = ServiceDepartment.objects.all()
            if request.POST.get("add_btn") == "add_btn":
                if request.method == "POST":
                    item_name = request.POST.get("item_id").split('.')
                    item_issue_tem=Item_Transfer_Issue_Temp(
                        item_id_id=item_name[0],
                        barcode=request.POST.get("barcode"),
                        batch_no=request.POST.get("serial_batch"),
                        expiry_date=request.POST.get("expiry_date"),
                        available_qty=request.POST.get("available_qty"),
                        issued_qty=request.POST.get("issued_qty"),
                        rate=request.POST.get("rate"),
                        remark=request.POST.get("remark"),
                        amount=request.POST.get("amount"),
                    )
                    item_issue_tem.save()
                    return HttpResponseRedirect("/without_indent_stock_transfer")

            if request.POST.get("save_btn") == "save_btn":
                item_issue_parent_count=Item_Issue_Parent.objects.all().count()
                today=date.today()
                today_date=today.strftime("%d%m%y")
                item_issue_no='ITI'+today_date+"00"+str(item_issue_parent_count)
                receive_store = request.POST.get("receiving_store")
                department_id = StoreMaster.objects.get(id=receive_store)
                cpc_store = StoreMaster.objects.get(store_type=0)

                item_id=[data.item_id_id for data in item_issue_temp]
                barcode=[data.barcode for data in item_issue_temp]
                serial_batch=[data.batch_no for data in item_issue_temp]
                expiry_date=[data.expiry_date for data in item_issue_temp]
                available_qty=[data.available_qty for data in item_issue_temp]
                issued_qty=[data.issued_qty for data in item_issue_temp]
                rate=[data.rate for data in item_issue_temp]
                remark=[data.remark for data in item_issue_temp]
                amount=[data.amount for data in item_issue_temp]

                for data in item_issue_temp:
                    # item issue child total quantity
                    totalamt=Stock_BatchWise.objects.filter(item_id_id=data.item_id_id,location_id_id=cpc_store.location_id_id).last()
                    if data.issued_qty == "":
                        data.issued_qty = 0
                    total_amount = int(str(totalamt.total_qty)) - int(str(data.issued_qty))

                    # item issue child available quantity
                    available = Stock_BatchWise.objects.filter(item_id_id=data.item_id_id,batch_no=data.batch_no,location_id_id=cpc_store.location_id_id).last()
                    available_main = Stock_BatchWise_Mainstore.objects.filter(item_id_id=data.item_id_id,batch_no=data.batch_no,store_id_id=receive_store).last()
                    total_main = Stock_BatchWise_Mainstore.objects.filter(item_id_id=data.item_id_id,store_id_id=receive_store).last()
                    if not available:
                        available_qty = 0
                    else:
                        available_qty = available.available_qty
                        available_qty = int(str(available_qty)) - int(str(data.issued_qty))

                    if total_main:
                        total_main_qty=int(str(total_main.total_qty)) + int(str(data.issued_qty))
                    else:
                        total_main_qty=data.issued_qty

                    if available_main:
                        available_main_qty=int(str(available_qty)) + int(str(data.issued_qty))
                    else:
                        available_main_qty=data.issued_qty
                    get_po_id = Stock_BatchWise.objects.filter(item_id_id=data.item_id_id,location_id_id=cpc_store.location_id_id).last()
                    po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.PO_id,item_id_id=data.item_id_id)

                    if po_detail.schema and po_detail.discount and po_detail.tex_details:
                        rate_amt = int(data.issued_qty) * int(data.rate)
                        schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                        disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                        tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                    elif po_detail.schema and po_detail.tex_details:
                        rate_amt = int(data.issued_qty) * int(data.rate)
                        schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                        tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt - schema_amt + tax_amt
                    elif po_detail.discount and po_detail.tex_details:
                        rate_amt = int(data.issued_qty) * int(data.rate)
                        disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                        tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt - disc_amt + tax_amt
                    elif po_detail.tex_details:
                        rate_amt = int(data.issued_qty) * int(data.rate)
                        tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt + tax_amt
                    else:
                        total_cost = 0

                    total_cost_amt = int(totalamt.total_cost) - int(total_cost)

                    item_issue_child = Item_Issue_Child(
                        item_issue_no=item_issue_no,
                        intent_no="",
                        item_id_id=data.item_id_id,
                        item_issue_date=datetime.today(),
                        barcode=data.barcode,
                        serial_batch=data.batch_no,
                        expiry_date=data.expiry_date,
                        available_qty=data.issued_qty,
                        issued_qty=data.issued_qty,
                        rate=data.rate,
                        intent_qty="",
                        total_amount=total_cost,
                        opening_balance=totalamt.total_qty,
                        transaction_cost = total_cost,
                        total_cost=total_cost_amt,
                        opening_cost=totalamt.total_cost,
                        remark=data.remark,
                        priority="",
                        amount=data.amount,
                        status="",
                        movement_status="CPC Issue Entry",
                        transfer_status='without transfer issue'
                    )
                    batch_wise=Stock_BatchWise_Mainstore(                                                      #stock entry batwise
                        item_issue_no=item_issue_no,
                        item_issue_date=datetime.now(),
                        intent_no='',
                        indent_date='',
                        item_id_id=data.item_id_id,
                        batch_no=data.batch_no,
                        expiry_date=data.expiry_date,
                        received_qty=data.issued_qty,
                        rate=data.rate,amount=data.amount,
                        store_id_id=receive_store,
                        vendor_id_id='',
                        department_id_id=department_id.department_id_id,
                        location_id_id=cpc_store.location_id_id,
                        receive_location_id=department_id.location_id_id,
                        available_qty=available_main_qty,
                        total_qty=total_main_qty,
                        total_cost = total_cost_amt,
                        adjust_qty="",
                        status=" ",
                        total_consume_qty = 0,
                    )

                    item_issue_child.save()
                    batch_wise.save()

                    # Update Total Cost to Batchwise table
                    total_cost_detail = Stock_BatchWise.objects.filter(item_id=data.item_id_id,location_id_id=cpc_store.location_id_id).last()
                    if data.issued_qty == "":
                        total_cost = 0
                        total_cost_detail.total_cost = int(total_cost_detail.total_cost) - int(total_cost)
                        total_cost_detail.save()

                    # Update available Amount To Batchwise Table

                    available=Stock_BatchWise.objects.filter(item_id=data.item_id_id,batch_no=data.batch_no,location_id_id=cpc_store.location_id_id).last()
                    if data.issued_qty == "":
                        data.issued_qty=0
                        available_qty= int(str(available.available_qty)) - int(str(data.issued_qty))
                        available.available_qty=available_qty
                        available.save()

                    # Update Total Quantity to Batchwise table

                    totalamt=Stock_BatchWise.objects.filter(item_id_id=data.item_id_id,location_id_id=cpc_store.location_id_id).last()
                    if data.issued_qty == "":
                        data.issued_qty = 0
                        total_amount = int(str(totalamt.total_qty)) - int(str(data.issued_qty))
                        totalamt.total_qty = total_amount
                        totalamt.save()

                    # issue_child=Item_Issue_Child(
                    #     item_issue_no=item_issue_no,
                    #     intent_no="",
                    #     item_id_id=data.item_id_id,
                    #     item_issue_date=datetime.today(),
                    #     barcode=data.barcode,
                    #     serial_batch=data.batch_no,
                    #     expiry_date=data.expiry_date,
                    #     available_qty=data.issued_qty,
                    #     issued_qty=data.issued_qty,
                    #     rate=data.rate,
                    #     intent_qty="",
                    #     total_amount=totalamt.total_qty,
                    #     opening_balance=data.issued_qty,
                    #     transaction_cost = '',
                    #     total_cost='',
                    #     opening_cost='',
                    #     remark=data.remark,
                    #     priority="",
                    #     amount=data.amount,
                    #     status="",
                    #     movement_status="Issue Entry",
                    #     transfer_status='without transfer issue'
                    # )

                    # issue_child.save()

                ITI_Child3=Item_Issue_Child.objects.filter(item_issue_no=item_issue_no)
                totalamount3=[data.amount for data in ITI_Child3]
                totalamts=0
                for data in totalamount3:
                    totalamts=int(totalamts)+int(data)
                item_issue_parent=Item_Issue_Parent(
                            item_issue_no=item_issue_no,
                            intent_no='',
                            item_issue_date=datetime.now(),
                            issued_store_id=cpc_store.id,
                            received_store_id=receive_store,
                            location_id_id=cpc_store.location_id_id,
                            issue_location_id=cpc_store.location_id_id,
                            receive_location_id=department_id.location_id_id,
                            department_id=department_id.department_id_id,
                            approved_by=request.POST.get("approved_by"),
                            total_amount=totalamts,
                            p_status="pending",
                            transfer_status='without transfer issue'
                )

                item_issue_parent.save()
                item_issue_temp.delete()
                return HttpResponseRedirect("/without_indent_stock_transfer")
            context={
                "item_detail":item_detail,"item_issue_temp":item_issue_temp,"store_master":store_master,"mainstore":mainstore,"dept_detail":dept_detail
            }

            return render(request,"pharmacy/stock_transfer/without_indent_stock_transfer.html",context)

        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

def stock_transfer_to_cpc(request):
    batch_no = request.POST.get("batch_no")
    item_id = request.POST.get("item_id")
    expiry_date = request.POST.get("expiry_date")
    mainstore_id = request.POST.get("mainstore_id")
    return_qty = request.POST.get("return_qty")
    reason = request.POST.get("reason")
    rate = request.POST.get("rate")
    amount = request.POST.get("amount")

    total_qty1 = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id).last()
    total_qty_1 = int(total_qty1.total_qty) - int(return_qty)
    today=date.today()
    today_date=today.strftime("%d%m%y")
    counter=Item_Return_ToCPC_Parent.objects.all().count()
    item_return_id="IRS"+today_date+"00"+str(counter)

    location_id=StoreMaster.objects.get(id=mainstore_id)
    cpc_store=StoreMaster.objects.get(store_type=0)

    return_cpc_parent=Item_Return_ToCPC_Parent(
        return_no=item_return_id,
        return_date=today,
        return_store_id=mainstore_id,
        location_id_id=location_id.location_id_id,
        receiving_store_id=cpc_store.id,
        request_no = '',
        stock_transfer = '1',
        status="",
    )

    item_return_cpc_child=Item_Return_ToCPC_Child(
        return_no=item_return_id,
        return_date=datetime.today(),
        batch_no=batch_no,
        expiry_date=expiry_date,
        rate=rate,
        amount=amount,
        item_id_id=item_id,
        return_qty=return_qty,
        total_qty=total_qty_1,
        opening_balance=total_qty1.total_qty,
        transaction_cost='',
        total_cost='',
        opening_cost='',
        reason=reason,
        status="Pending",
        stock_transfer = '1',
        movable_status='Return To CPC'
    )

    return_cpc_parent.save()
    item_return_cpc_child.save()

    totalqty2=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id).last()
    totalqty2.total_qty = int(str(total_qty1.total_qty)) - int(str(return_qty))
    totalqty2.save()

    availableqty=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id,batch_no=batch_no).last()
    availableqty.available_qty= int(str(availableqty.available_qty)) - int(str(return_qty))
    availableqty.save()

    totalqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id).last()
    totalqty_m.total_qty = int(str(total_qty1.total_qty)) + int(str(return_qty))
    totalqty_m.save()

    availableqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id,batch_no=batch_no).last()
    availableqty_m.available_qty= int(str(availableqty.available_qty)) + int(str(return_qty))
    availableqty_m.save()

    data='Successfully Stock Transfered to CPC'
    return JsonResponse(data, safe=False)

def mainstore_makereturn(request):
        # collect frontend table records
        item_master = Inventory_ItemMaster.objects.all()
        item_name = [data.item_name for data in item_master]
        item_return_child = Item_return_Child.objects.filter(status="pending")

        item_name1 = [data.id for data in item_master]
        #total quantity

        total_amount=[]
        total_qty=[]
        for data in item_name1:
            item_return_child1 = Item_return_Child.objects.filter(item_id_id=data, status="pending")
            total=[data.return_qty for data in item_return_child1]
            total_qty1=0
            for data1 in total:
                total_qty1=total_qty1+int(data1)
            total_qty.append(total_qty1)

            #total amount
            total_amt1=0
            total_amt=[data.amount for data in item_return_child1]
            for data2 in total_amt:
                total_amt1=total_amt1+int(data2)
            total_amount.append(total_amt1)

        amount_qty=zip(total_qty,total_amount,item_name,item_name1) # have total qty, total qty, total amount
        # item_return_child = Item_return_Child.objects.filter(status="Pending") # table records

        # # after click insertbutton save temporary table

        insert_btn=request.POST.get("insert_btn")

        if insert_btn == "insert_btn":
            for data in range(len(item_name)):
                makeitem_return_temp=MakeItem_return_ToCPC_Temp(
                    date=datetime.today(),
                    item_id_id = item_name1[data],
                    total_qty = total_qty[data],
                    total_amt = total_amount[data],
                    status ="entered",
                )
                if total_qty[data]!= 0 and total_amount[data] != 0:
                    makeitem_return_temp.save(print("makeitem_return_temp save"))

                    #Update Item_return_Child table status

                    item_return_child2=Item_return_Child.objects.filter(item_id_id=item_name1[data],status="pending")
                    for data2 in item_return_child2:
                        data2.status="entered"
                        data2.save()
            return HttpResponseRedirect("/mainstore_makereturn")

        # # click save button

        # # frontend table motal

        return_store=StoreMaster.objects.filter(store_type=1)
        makeitem_return_temp1=MakeItem_return_ToCPC_Temp.objects.all()
        item_return_child4=Item_return_Child.objects.filter(status="entered")
        rate4=[data.rate for data in item_return_child4]
        amount4=[data.amount for data in item_return_child4]
        expiry_date4=[data.expiry_date for data in item_return_child4]
        batch_no4=[data.batch_no for data in item_return_child4]
        total1=[data.total_qty for data in makeitem_return_temp1]
        tota_amtl1=[data.total_amt for data in makeitem_return_temp1]

        total_qty11=0
        for data1 in total1:
            total_qty11=total_qty11+int(data1)

        total_amt11=0
        for data1 in tota_amtl1:
            total_amt11=total_amt11+int(data1)

        makeitem_return_temp2=zip(makeitem_return_temp1,expiry_date4,batch_no4,rate4,amount4)

        if request.POST.get("Make_Return") == "Make_Return":
            item_id3=request.POST.getlist("item_id3")
            batch_no3=request.POST.getlist("batch_no3")
            return_qty3=request.POST.getlist("return_qty3")
            rate3=request.POST.getlist("rate3")
            amount3=request.POST.getlist("amount3")
            reason=request.POST.get("reason")
            return_store_id=request.POST.get("return_store_id")
            today=date.today()
            today_date=today.strftime("%d%m%y")
            counter=Item_Return_ToCPC_Parent.objects.all().count()
            item_return_id="IRS"+today_date+"00"+str(counter)
            location_id=StoreMaster.objects.get(id=return_store_id)
            cpc_store=StoreMaster.objects.get(store_type=0)

            return_cpc_parent=Item_Return_ToCPC_Parent(
                return_no=item_return_id,
                return_date=today,
                return_store_id=return_store_id,
                location_id_id=location_id.location_id_id,
                receiving_store_id=cpc_store.id,
                request_no = '',
                stock_transfer = '0',
                status="",
            )
            return_cpc_parent.save()

            for data in range(len(item_id3)):
                # Item_Return_Supplier_Child total quantity get batchwise table
                totalqty=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id3[data]).last()
                totalqty11=int(str(totalqty.total_qty)) - int(str(return_qty3[data]))

                get_po_id = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id3[data],batch_no=batch_no3[data],store_id=return_store_id).last()
                po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.intent_no,item_id_id=item_id3[data])

                if po_detail.schema and po_detail.discount and po_detail.tex_details:
                    rate_amt = int(return_qty3[data]) * int(rate3[data])
                    schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                    disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                    tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                    total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                elif po_detail.schema and po_detail.tex_details:
                    rate_amt = int(return_qty3[data]) * int(rate3[data])
                    schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                    tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                    total_cost = rate_amt - schema_amt + tax_amt
                elif po_detail.discount and po_detail.tex_details:
                    rate_amt = int(return_qty3[data]) * int(rate3[data])
                    disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                    tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                    total_cost = rate_amt - disc_amt + tax_amt
                elif po_detail.tex_details:
                    rate_amt = int(return_qty3[data]) * int(rate3[data])
                    tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                    total_cost = rate_amt + tax_amt
                else:
                    total_cost = int(return_qty3[data]) * int(rate3[data])

                total_cost_amt = int(totalqty.total_cost) - int(total_cost)

                item_return_cpc_child=Item_Return_ToCPC_Child(
                        return_no=item_return_id,
                        return_date=datetime.today(),
                        batch_no=batch_no3[data],
                        expiry_date=expiry_date4[data],
                        rate=rate3[data],
                        amount=amount3[data],
                        item_id_id=item_id3[data],
                        return_qty=return_qty3[data],
                        total_qty=totalqty11,
                        opening_balance=totalqty.total_qty,
                        transaction_cost=total_cost,
                        total_cost=total_cost_amt,
                        opening_cost=totalqty.total_cost,
                        reason=reason,
                        status="Pending",
                        stock_transfer = '0',
                        movable_status='Return To CPC'
                    )
                item_return_cpc_child.save(print("return_suplier_child saved"))

                # update batchwise table total qty

                totalqty2=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id3[data],store_id=return_store_id).last()
                totalqty2.total_qty = int(str(totalqty.total_qty)) - int(str(return_qty3[data]))
                totalqty2.total_cost = total_cost_amt
                totalqty2.save()

                availableqty=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id3[data],batch_no=batch_no3[data],store_id=return_store_id).last()
                availableqty.available_qty= int(str(availableqty.available_qty)) - int(str(return_qty3[data]))
                availableqty.save()

                totalqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id3[data],po_location=location_id.location_id_id).last()
                totalqty_m.total_qty = int(str(totalqty_m.total_qty)) + int(str(return_qty3[data]))
                totalqty_m.total_cost = int(str(totalqty_m.total_cost)) + int(total_cost)
                totalqty_m.save()

                availableqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id3[data],batch_no=batch_no3[data],po_location=location_id.location_id_id).last()
                availableqty_m.available_qty= int(str(availableqty_m.available_qty)) + int(str(return_qty3[data]))
                availableqty_m.save()

                issue_list_c=Item_return_Child.objects.filter(item_id_id=item_id3[data],batch_no=batch_no3[data],status='entered')
                for data in issue_list_c:
                    data.status='completed'
                    data.save()
                    issue_list_p=Item_Return_Parent.objects.get(item_return_no=data.item_return_no)
                    issue_list_p.status='completed'
                    issue_list_p.save()


            MakeItem_return_ToCPC_Temp.objects.all().delete()
            return HttpResponseRedirect("/mainstore_makereturn")

        context={
            "item_master":item_master,"item_return_child":item_return_child,"amount_qty":amount_qty,"return_store":return_store,"makeitem_return_temp2":makeitem_return_temp2,"total_qty11":total_qty11,"total_amt11":total_amt11
        }
        return render(request,"pharmacy/item_return/make_return_to_cpc.html",context)
   
@login_required(login_url='/user_login')
def item_return_supplier(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_return_to_supplier' in access.user_profile.screen_access:
        try:
            item_category = ItemCategoryMaster.objects.all()
            item_Name = Inventory_ItemMaster.objects.all()
            item_return_parent = Item_Return_ToCPC_Parent.objects.filter(status="",stock_transfer='0')
            view_detail = request.POST.get("view_detail")
            if request.POST.get("Search") == "Search":
                item_name1 = request.POST.get("item_name").split(".")
                vendor_master = VendorMaster.objects.all()
                if request.POST.get("item_cat") != "select":
                    item_master = Inventory_ItemMaster.objects.filter(item_category=request.POST.get("item_cat"))
                    item_ids = [data.id for data in item_master]
                    Item_return_child1 = Stock_BatchWise.objects.filter(item_id__in=item_ids)

                    # Item_return_child1 = Stock_BatchWise.objects.filter(item_id__in=item_ids).distinct()
                    print('Item_return_child1',Item_return_child1)
                    for data in Item_return_child1:
                        print('data',data)
                elif item_name1:
                    Item_return_child1 = Stock_BatchWise.objects.filter(item_id=item_name1[0])
                context={
                    "vendor_master":vendor_master,"Item_return_child1":Item_return_child1
                    }
                return render(request,"pharmacy/item_return/item_return_search_batchwise.html",context)
            elif view_detail == "view_detail":
                return_parent_no=request.POST.get("return_parent_no")
                item_return_to_mainstore = Item_Return_ToCPC_Child.objects.filter(return_no=return_parent_no)
                context={
                        "item_return_to_mainstore":item_return_to_mainstore
                        }
                return render(request,"pharmacy/item_return/return_itemdetail.html",context)
            # save_all=request.POST.get("Save_all")
            # if save_all == "Save_all":
            #     if request.method == "POST":
            #         vendor=request.POST.get("vendor")
            #         batch_no=request.POST.getlist("batch_no")
            #         item_id=request.POST.getlist("item_id")
            #         expiry_date=request.POST.getlist("expiry_date")
            #         return_qty=request.POST.getlist("return_qty")
            #         amount=request.POST.getlist("amount")
            #         reason=request.POST.getlist("reason")
            #         today=date.today()
            #         today_date=today.strftime("%d%m%y")
            #         counter=Item_Return_Supplier_Parent.objects.all().count()
            #         item_return_supplier_id="IRS"+today_date+"00"+str(counter)

            #         item_return_supplier_parent=Item_Return_Supplier_Parent(
            #                 supplier_return_no=item_return_supplier_id,
            #                 return_date=date.today(),
            #                 store_id=1,
            #                 vendor_id=vendor,
            #                 status="pending",
            #             )
            #         item_return_supplier_parent.save()

            #         for data in range(len(item_id)):
            #             if item_id[data] and batch_no[data]:
            #                 #update total qty to batchwise table
            #                 totalamt=Stock_BatchWise.objects.filter(item_id=item_id[data]).last()
            #                 #opening balance(item return child table)
            #                 opening_balance = totalamt.total_qty
            #                 if return_qty == "":
            #                     return_qty=0
            #                 total_amount=int(str(totalamt.total_qty)) - int(str(return_qty[data]))
            #                 totalamt.total_qty=total_amount
            #                 totalamt.save()
            #                 #update available qty to batchwise table
            #                 available=Stock_BatchWise.objects.filter(batch_no=batch_no[data]).last()
            #                 if return_qty == "":
            #                     return_qty=0
            #                 available_qty= int(str(available.available_qty)) + int(return_qty[data])
            #                 available.available_qty=available_qty
            #                 available.save()
            #             import dateutil.parser
            #             Expiry=dateutil.parser.parse(expiry_date[data])
            #             print("Expiry",Expiry)
            #             item_return_supplier_child=Item_Return_Supplier_Child(
            #                 supplier_return_no=item_return_supplier_id,
            #                 return_date=date.today(),
            #                 batch_no=batch_no[data],
            #                 expiry_date=Expiry,
            #                 item_id=item_id[data],
            #                 return_qty=return_qty[data],
            #                 total_qty=totalamt.total_qty,
            #                 opening_balance=opening_balance,
            #                 return_amount=amount[data],
            #                 reason=reason[data],
            #                 status="pending",
            #             )
            #             if return_qty and amount and reason:
            #                 item_return_supplier_child.save()

            #         return HttpResponseRedirect("/item_return")

            context={
                    "item_category":item_category,"item_return_parent":item_return_parent,"item_Name":item_Name
                    }
            return render(request,"pharmacy/item_return/return_to_supplier.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


@login_required(login_url='/user_login')
def STV_makereturn(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_status_report' in access.user_profile.screen_access:
        try:
            # collect frontend table records
            item_master = Inventory_ItemMaster.objects.all()
            item_name = [data.item_name for data in item_master]
            item_return_child = Item_Return_ToCPC_Child.objects.filter(status="Pending")

            item_name1 = [data.id for data in item_master]
            #total quantity

            total_amount=[]
            total_qty=[]
            for data in item_name1:
                item_return_child1 = Item_Return_ToCPC_Child.objects.filter(item_id_id=data, status="Pending")
                total=[data.return_qty for data in item_return_child1]
                total_qty1=0
                for data1 in total:
                    total_qty1=total_qty1+int(data1)
                total_qty.append(total_qty1)

                #total amount
                total_amt1=0
                total_amt=[data.amount for data in item_return_child1]
                for data2 in total_amt:
                    total_amt1=total_amt1+int(data2)
                total_amount.append(total_amt1)

            amount_qty=zip(total_qty,total_amount,item_name,item_name1) # have total qty, total qty, total amount
            print(total_amount,total_qty)
            # item_return_child = Item_return_Child.objects.filter(status="Pending") # table records

            # # after click insertbutton save temporary table

            insert_btn=request.POST.get("insert_btn")

            if insert_btn == "insert_btn":
                rate = request.POST.getlist("rate")
                for data in range(len(item_name)):
                    makeitem_return_temp=MakeItem_return_Temp(
                        date=datetime.today(),
                        item_id_id = item_name1[data],
                        total_qty = total_qty[data],
                        rate = rate[data],
                        total_amt = total_amount[data],
                        status ="pending",
                    )
                    if total_qty[data] and total_amount[data] != 0:
                        makeitem_return_temp.save(print("makeitem_return_temp save"))

                        #Update Item_return_Child table status

                        item_return_child2=Item_Return_ToCPC_Child.objects.filter(item_id_id=item_name1[data],status="Pending")
                        for data2 in item_return_child2:
                            data2.status="entered"
                            data2.save()
                return HttpResponseRedirect("/STV_makereturn")

            # # click save button

            # # frontend table motal

            vendor_master=VendorMaster.objects.all()
            makeitem_return_temp1=MakeItem_return_Temp.objects.all()
            item_return_child4=Item_Return_ToCPC_Child.objects.filter(status="Entered")
            expiry_date4=[data.expiry_date for data in item_return_child4]
            batch_no4=[data.batch_no for data in item_return_child4]
            total1=[data.total_qty for data in makeitem_return_temp1]
            tota_amtl1=[data.total_amt for data in makeitem_return_temp1]

            total_qty11=0
            for data1 in total1:
                total_qty11=total_qty11+int(data1)

            total_amt11=0
            for data1 in tota_amtl1:
                total_amt11=total_amt11+int(data1)

            makeitem_return_temp2=zip(makeitem_return_temp1,expiry_date4,batch_no4)

            if  request.POST.get("Make_Return") == "Make_Return":
                item_id3=request.POST.getlist("item_id3")
                batch_no3=request.POST.getlist("batch_no3")
                return_qty3=request.POST.getlist("return_qty3")
                rate3=request.POST.getlist("rate3")
                reason=request.POST.get("reason")
                vendor=request.POST.get("vendor_id")
                today=date.today()
                today_date=today.strftime("%d%m%y")
                counter=Item_Return_Supplier_Parent.objects.all().count()
                item_return_supplier_id="IRS"+today_date+"00"+str(counter)
                cpc_store=StoreMaster.objects.get(store_type=0)

                return_suplier_parent=Item_Return_Supplier_Parent(
                    supplier_return_no=item_return_supplier_id,
                    return_date=today,
                    store_id_id=cpc_store.id,
                    location_id_id=cpc_store.location_id_id,
                    vendor_id_id=vendor,
                    status="",
                )
                return_suplier_parent.save()

                for data in range(len(item_id3)):
                    # Item_Return_Supplier_Child total quantity get batchwise table
                    totalqty=Stock_BatchWise.objects.filter(item_id_id=item_id3[data]).last()
                    totalqty11=int(str(totalqty.total_qty)) - int(str(return_qty3[data]))

                    get_po_id = Stock_BatchWise.objects.filter(item_id_id=item_id3[data],batch_no=batch_no3[data],location_id_id=cpc_store.location_id_id).last()
                    po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.PO_id,item_id_id=item_id3[data])

                    if po_detail.schema and po_detail.discount and po_detail.tex_details:
                        rate_amt = int(return_qty3[data]) * int(rate3[data])
                        schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                        disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                        tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                    elif po_detail.schema and po_detail.tex_details:
                        rate_amt = int(return_qty3[data]) * int(rate3[data])
                        schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                        tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt - schema_amt + tax_amt
                    elif po_detail.discount and po_detail.tex_details:
                        rate_amt = int(return_qty3[data]) * int(rate3[data])
                        disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                        tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt - disc_amt + tax_amt
                    elif po_detail.tex_details:
                        rate_amt = int(return_qty3[data]) * int(rate3[data])
                        tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                        total_cost = rate_amt + tax_amt
                    else:
                        total_cost = int(return_qty3[data]) * int(rate3[data])

                    total_cost_amt = int(totalqty.total_cost) - int(total_cost)

                    item_return_supplier_child=Item_Return_Supplier_Child(
                            supplier_return_no=item_return_supplier_id,
                            return_date=datetime.today(),
                            batch_no=batch_no3[data],
                            expiry_date=expiry_date4[data],
                            item_id_id=item_id3[data],
                            return_qty=return_qty3[data],
                            total_qty=totalqty11,
                            opening_balance=totalqty.total_qty,
                            transaction_cost=total_cost,
                            total_cost=total_cost_amt,
                            opening_cost=totalqty.total_cost,
                            return_amount=return_qty3[data],
                            reason=reason,
                            status="Pending",
                            movement_status='Supplier Return Entry'
                        )
                    item_return_supplier_child.save(print("return_suplier_child saved"))

                    # update batchwise table total qty

                    totalqty2=Stock_BatchWise.objects.filter(item_id_id=item_id3[data]).last()
                    totalqty2.total_qty = int(str(totalqty.total_qty)) - int(str(return_qty3[data]))
                    totalqty2.total_cost = total_cost_amt
                    totalqty2.save()

                    availableqty=Stock_BatchWise.objects.filter(batch_no=batch_no3[data]).last()
                    availableqty.available_qty= int(str(availableqty.available_qty)) - int(str(return_qty3[data]))
                    availableqty.save()

                    issue_list_c=Item_Return_ToCPC_Child.objects.filter(item_id_id=item_id3[data],status='entered',batch_no=batch_no3[data],stock_transfer='0')
                    for data in issue_list_c:
                        data.status='completed'
                        data.save()
                        issue_list_p=Item_Return_ToCPC_Parent.objects.get(return_no=data.return_no,stock_transfer='0')
                        issue_list_p.status='completed'
                        issue_list_p.save()

                MakeItem_return_Temp.objects.all().delete()
                return HttpResponseRedirect("/STV_makereturn")

            context={
                "item_master":item_master,"item_return_child":item_return_child,"amount_qty":amount_qty,"vendor_master":vendor_master,"makeitem_return_temp2":makeitem_return_temp2,"total_qty11":total_qty11,"total_amt11":total_amt11
            }
            return render(request,"pharmacy/item_return/make_return.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

# Pharmacy Reporting Part
@login_required(login_url='/user_login')
def item_status_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_status_report' in access.user_profile.screen_access:
        try:
            Item_Status_Report_Temp.objects.all().delete()
            dept = ServiceDepartment.objects.all()
            search_button=request.POST.get("Submit_btn")
            print("search_button",search_button)
            if search_button == "submit_btn":
                start_date=request.POST.get("from_date")
                end_date=request.POST.get("to_date")
                department_1=request.POST.get("department")

                items=Inventory_ItemMaster.objects.all()
                items_name=[data.item_name for data in items]
                # get Items from inventory item master
                if start_date and end_date and department_1 == "Select":
                    print("daterange only")
                    if request.method == "POST":

                        # get records from Stock entry child

                        stockchild=StockEntry_Child.objects.filter(GRN_datetime__range=[start_date,end_date])
                        # get records from item Issue Child
                        item_issuechild=Item_Issue_Child.objects.filter(item_issue_date__range=[start_date,end_date])
                        # get records from item return Child
                        item_returnchild=Item_return_Child.objects.filter(return_date__range=[start_date,end_date])
                        for data in stockchild:
                            itemstatus_report_temp = Item_Status_Report_Temp(
                                item=data.item_id,
                                date=data.GRN_datetime,
                                particular=data.movement_status,
                                opening_balance=data.opening_balance,
                                transaction=data.physical_qty,
                                closing_qty=data.total_qty,
                            )
                            itemstatus_report_temp.save(print("itemstatus_report_temp save"))

                        for data in item_issuechild:
                            itemstatus_report_temp1 = Item_Status_Report_Temp(
                                item=data.item_id,
                                date=data.item_issue_date,
                                particular=data.movement_status,
                                opening_balance=data.opening_balance,
                                transaction=data.issued_qty,
                                closing_qty=data.total_amount,
                            )
                            itemstatus_report_temp1.save(print("itemstatus_report_temp1 save"))

                        for data in item_returnchild:
                            itemstatus_report_temp2 = Item_Status_Report_Temp(
                                item=data.item_id,
                                date=data.return_date,
                                particular=data.movable_status,
                                opening_balance=data.opening_balance,
                                transaction=data.return_qty,
                                closing_qty=data.total_qty,
                            )
                            itemstatus_report_temp2.save(print("itemstatus_report_temp1 save"))
                        itemstatus_report_temp3=Item_Status_Report_Temp.objects.all().order_by('date')
                    context={
                        "items_name":items_name , "itemstatus_report_temp3":itemstatus_report_temp3,"dept":dept
                    }
                    return render(request,"pharmacy/reports/item_status_report.html",context)

                # elif start_date and end_date and department_1 != "Select":
                #     print("both=====================")
                #     if request.method == "POST":
                #         # get records from Stock entry child

                #         stockparent = StockEntry_Parent.objects.filter(department=department_1)
                #         stockparent_depart = [data.GRN_id for data in stockparent]
                #         stockchild=StockEntry_Child.objects.filter(GRN_datetime__range=[start_date,end_date],GRN_id=stockparent_depart)
                #         # get records from item Issue Child
                #         issueparent = Item_Issue_Parent.objects.filter(department=department_1)
                #         issue_parent_depart = [data.item_issue_no for data in stockparent]
                #         item_issuechild=Item_Issue_Child.objects.filter(item_issue_date__range=[start_date,end_date],item_issue_no=issue_parent_depart)

                #         # get records from item return Child
                #         issueparent = Item_Issue_Parent.objects.filter(department=department_1)
                #         issue_parent_depart = [data.item_issue_no for data in stockparent]
                #         item_returnchild=Item_return_Child.objects.filter(return_date__range=[start_date,end_date])


                #         for data in stockchild:
                #             itemstatus_report_temp = Item_Status_Report_Temp(
                #                 item=data.item_id,
                #                 date=data.GRN_datetime,
                #                 particular=data.movement_status,
                #                 opening_balance=data.opening_balance,
                #                 transaction=data.physical_qty,
                #                 closing_qty=data.total_qty,
                #             )
                #             itemstatus_report_temp.save(print("itemstatus_report_temp save"))

                #         for data in item_issuechild:
                #             itemstatus_report_temp1 = Item_Status_Report_Temp(
                #                 item=data.item_id,
                #                 date=data.item_issue_date,
                #                 particular=data.movement_status,
                #                 opening_balance=data.opening_balance,
                #                 transaction=data.issued_qty,
                #                 closing_qty=data.total_amount,
                #             )
                #             print("item_returnchild",data.movement_status)
                #             itemstatus_report_temp1.save(print("itemstatus_report_temp1 save"))

                #         for data in item_returnchild:
                #             itemstatus_report_temp2 = Item_Status_Report_Temp(
                #                 item=data.item_id,
                #                 date=data.return_date,
                #                 particular=data.movable_status,
                #                 opening_balance=data.opening_balance,
                #                 transaction=data.return_qty,
                #                 closing_qty=data.total_qty,
                #             )
                #             itemstatus_report_temp2.save(print("itemstatus_report_temp1 save"))
                #         itemstatus_report_temp3=Item_Status_Report_Temp.objects.all().order_by('date')
                #         print("itemstatus_report_temp3",itemstatus_report_temp3)
                #         context={
                #             "items_name":items_name , "itemstatus_report_temp3":itemstatus_report_temp3,"dept":dept
                #         }
                #         return render(request,"pharmacy/reports/item_status_report.html",context)


            context={
                    "dept":dept
                }
            return render(request,"pharmacy/reports/item_status_report.html",context)

        except Exception as error:
            return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def purchase_intent(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'purchase_indent' in access.user_profile.screen_access:
        try:
            mainstore=StoreMaster.objects.filter(store_type="1")
            cpcstore=StoreMaster.objects.get(store_type="0")
            request_store = request.store_id
            cpc_store= StoreMaster.objects.filter(id__in=request_store,store_type='0').last()
            main_store = StoreMaster.objects.filter(id__in=request_store,store_type=1).last()

            item_master=Inventory_ItemMaster.objects.all()
            purchase_intent_temp=Purchase_Intent_Temp.objects.filter(location_id_id=request.location)
            Insert_button=request.POST.get("insert")
            Saved_button=request.POST.get("Saved_button")
            if Insert_button == "Insert":
                if request.method=="POST":
                    main_store_name=request.POST.get("main_store")
                    main_store_name1 = StoreMaster.objects.get(id=main_store_name)
                    location_id=StoreMaster.objects.get(id=main_store_name)
                    cpc_store_id=request.POST.get("cpc_store_id")
                    cpc_store_id1 = StoreMaster.objects.get(id=cpc_store_id)
                    priority=request.POST.get("priority")
                    item_name=request.POST.get("item_name")
                    quantity=request.POST.get("quantity")
                    item_code=request.POST.get("item_code")
                    department1=request.POST.get("department")
                    item_belongs_to=request.POST.get("item_belongs_to")
                    remark=request.POST.get("remark")

                    purchase_intent_count=Purchase_Intent_Parent.objects.all().count()
                    today=date.today()
                    today_date=today.strftime("%d%m%y")
                    purchase_intent_id = "PI"+ today_date +"00"+str(purchase_intent_count)
                    purchase_intent_temp1=Purchase_Intent_Temp(
                        intent_id=purchase_intent_id,
                        intent_datetime=datetime.now(),
                        cpc_store_id=cpc_store_id,
                        main_store_id=main_store_name,
                        location_id_id=location_id.location_id_id,
                        department_id=department1,
                        priority=priority,
                        item_id_id=item_name,
                        quantity=quantity,
                        rate=request.POST.get("rate"),
                        amount=request.POST.get("amount"),
                        item_code=item_code,
                        item_belongs_to=item_belongs_to,
                        remark=remark,
                        status="Pending",
                    )
                    purchase_intent_temp1.save(print("temporary table is saved"))
                    context ={
                        "cpc_store":cpc_store,"mainstore":mainstore,"item_master":item_master,'purchase_intent_temp':purchase_intent_temp,
                        'main_store_name':main_store_name1,'priority':priority,'main_store':main_store,'cpcstore':cpcstore,'cpc_store_id':cpc_store_id1
                    }
                    print('main_store',main_store)
                    return render(request,"pharmacy/purchase_intent.html",context)


            if  Saved_button =="Saved_button":
                if request.method == "POST":
                    intent_id1=[data.intent_id for data in purchase_intent_temp]
                    cpc_store_id1=[data.cpc_store_id for data in purchase_intent_temp]
                    location_id1=[data.location_id_id for data in purchase_intent_temp]
                    mainstore1=[data.main_store_id for data in purchase_intent_temp]
                    priority1=[data.priority for data in purchase_intent_temp]
                    item_id1=[data.item_id_id for data in purchase_intent_temp]
                    quantity1=[data.quantity for data in purchase_intent_temp]
                    item_code1=[data.item_code for data in purchase_intent_temp]
                    item_belongs_to1=[data.item_belongs_to for data in purchase_intent_temp]
                    remark1=[data.remark for data in purchase_intent_temp]
                    dept1=[data.department_id for data in purchase_intent_temp]
                    rate1=[data.rate for data in purchase_intent_temp]
                    amount1=[data.amount for data in purchase_intent_temp]

                    total=0
                    for data1 in intent_id1:
                        totalamt=Purchase_Intent_Parent.objects.filter(intent_id=data1)
                        if not totalamt:
                            totalamt.total_amount = 0
                        total= total + int(str(totalamt.total_amount))
                    purchase_intent_parent=Purchase_Intent_Parent(
                        intent_id=intent_id1[0],
                        intent_datetime=datetime.now(),
                        cpc_store_id=cpc_store_id1[0],
                        department_id=dept1[0],
                        location_id_id=location_id1[0],
                        main_store_id=mainstore1[0],
                        total_amount=total,
                        p_status="pending",
                        approval_status="pending",
                    )
                    purchase_intent_parent.save(print("purchase_intent_parent saved"))

                    for data in range(len(item_id1)):
                        purchase_intent_child=Purchase_Intent_Child(
                            intent_id=intent_id1[data],
                            intent_datetime=datetime.now(),
                            priority=priority1[data],
                            item_id_id=item_id1[data],
                            quantity=quantity1[data],
                            rate=rate1[data],
                            amount=amount1[data],
                            item_code=item_code1[data],
                            item_belongs_to=item_belongs_to1[data],
                            remark=remark1[data],
                            status="pending",
                            approval_status="pending",

                        )

                        purchase_intent_child.save(print("material_intent_child saved"))

                    Purchase_Intent_Temp.objects.filter(location_id_id=request.location).delete()
                    return HttpResponseRedirect("/purchase_intent")

            context ={
                "cpc_store":cpc_store,"mainstore":mainstore,"item_master":item_master,'purchase_intent_temp':purchase_intent_temp,
                'main_store':main_store,'cpcstore':cpcstore
            }
            return render(request,"pharmacy/purchase_intent.html",context)

        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def purchase_intent_approval(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'purchase_indent_approval' in access.user_profile.screen_access:
        try:
            vendor=VendorMaster.objects.all()
            PI_approved1=Purchase_Intent_Parent.objects.filter(approval_status="completed")
            pending=Purchase_Intent_Parent.objects.filter(approval_status="pending")
            count_approved=PI_approved1.count()
            count_pending=pending.count()
            context={
                'vendor':vendor,'pending':pending,'PI_approved1':PI_approved1,'count_approved':count_approved,'count_pending':count_pending
            }
            return render(request,"pharmacy/purchase_intent_aproval.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


@login_required(login_url='/user_login')
def PI_pending_update(request,pk):
    try:
        records=Purchase_Intent_Parent.objects.get(intent_id=pk)
        PI_approve=Purchase_Intent_Child.objects.filter(intent_id=pk)
        approve=request.POST.get("Approve")
        if request.method == "POST":
            if approve == "Approved":
                for data in PI_approve:
                    data.approval_status="completed"
                    data.save(print("save"))
                records.approval_status = "completed"
                records.save()
                return HttpResponseRedirect("/purchase_intent_approval")
        context={
            "records":records,"PI_approve":PI_approve
        }
        return render(request,"pharmacy/PI_approval_update.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

# Update Pending approvel Pi
@login_required(login_url='/user_login')
def PI_update(request):
    try:
        pi_id=request.GET.get("pi_id")
        itemid=request.GET.get("itemid")
        qty=request.GET.get("qty")
        rate=request.GET.get("rate")
        amount=request.GET.get("amount")
        PI_child=Purchase_Intent_Child.objects.get(intent_id=pi_id,item_id=itemid)
        PI_child.quantity=qty
        PI_child.rate=rate
        PI_child.amount=amount
        PI_child.save()
        data='updated'
        return JsonResponse(data, safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})



@login_required(login_url='/user_login')
def make_PO_for_PI(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'make_po_for_pi' in access.user_profile.screen_access:
        try:
            records = Purchase_Intent_Parent.objects.filter(approval_status="completed",p_status="pending")
            item_cate = ItemCategoryMaster.objects.all()
            items=Inventory_ItemMaster.objects.all()
            dept_detail = ServiceDepartment.objects.all()
            store_detail = StoreMaster.objects.get(store_type=0)
            location_detail = LocationMaster.objects.all()
            makePO_btn = request.POST.get("Make_PO")
            if request.POST.get("Search") == "Search":
                if request.POST.get("item_cat") and request.POST.get("item_name"):
                    item_id = request.POST.get("item_name").split('.')
                    item_master = Inventory_ItemMaster.objects.filter(item_category = request.POST.get("item_cat"),id=item_id[0])
                    item_ids = [data.id for data in item_master]
                    PIchild2 = Purchase_Intent_Child.objects.filter(item_id_id__in=item_ids,status='pending')
                elif request.POST.get("item_cat"):
                    item_master = Inventory_ItemMaster.objects.filter(item_category = request.POST.get("item_cat"))
                    item_ids = [data.id for data in item_master]
                    PIchild2 = Purchase_Intent_Child.objects.filter(item_id_id__in=item_ids,status='pending')

                elif request.POST.get("item_name"):
                    item_id = request.POST.get("item_name").split('.')
                    item_master = Inventory_ItemMaster.objects.filter(id=item_id[0])
                    PIchild2 = Purchase_Intent_Child.objects.filter(item_id_id=item_id[0],status='pending')
                    # total_qty = Purchase_Intent_Child.objects.filter(item_id_id=item_id[0]).aggregate(Sum('quantity'))

                context={
                    "PIchild2":PIchild2,
                    'item_master': item_master,
                    'dept_detail' : dept_detail,
                }
                return render(request,"pharmacy/search_PI.html",context)
            Insert_btn = request.POST.get("Insert")
            if Insert_btn == "Insert":
                if request.method == "POST":
                    check_id = request.POST.getlist('check')
                    # item_id=request.POST.getlist("item_id")
                    for data in check_id:
                        pi_child_list = Purchase_Intent_Child.objects.filter(item_id_id=data,status='pending')
                        rate = Purchase_Intent_Child.objects.filter(item_id_id=data,status='pending').last()
                        stock_qty1 = Stock_BatchWise.objects.filter(item_id_id=data).last()
                        if stock_qty1:
                            stock_qty = stock_qty1.available_qty
                        else:
                            stock_qty=0
                        unit = Inventory_ItemMaster.objects.get(id=data)
                        qty=0
                        for data1 in pi_child_list:
                            qty += int(str(data1.quantity))
                        total_amt = int('0'+rate.rate) * int(qty)

                        PI_Temp = Makepo_PI_Temp(
                            datetime=datetime.now(),
                            item_id_id=data,
                            total_qty=qty,
                            unit_id_id=unit.unit,
                            rate = rate.rate,
                            stock_qty = stock_qty,
                            total_amount=total_amt,
                            status=""
                        )
                        PI_Temp.save(print("temp table saved"))
                        for data2 in pi_child_list:
                            data2.status = 'entered'
                            data2.save()
                    return redirect('make_PO_for_PI')


            PI_Temp_1 = Makepo_PI_Temp.objects.all()
            basic_amt = 0
            for data in PI_Temp_1:
                basic_amt += int(str(data.total_amount))
            if PI_Temp_1:
                # netamt = [data.amount for data in PI_Temp_1]
                Net_Amt = 0
                # for data in netamt:
                #     Net_Amt=Net_Amt + int(data)

            else:
                Net_Amt = 0


            vendor=VendorMaster.objects.all()

            Make_PO = request.POST.get("Make_PO")
            if Make_PO == "Make_PO":
                if request.method == "POST":
                    vendor_id=request.POST.get("vendor_id")
                    tax=request.POST.get("tax")
                    basic_amount=request.POST.get("basic_amount")
                    item_name=request.POST.getlist("item_name1")
                    qty=request.POST.getlist("qty1")
                    unit=request.POST.getlist("unit1")
                    free_qty=request.POST.getlist("free_qty1")
                    stock_qty=request.POST.getlist("stock_qty1")
                    rate=request.POST.getlist("rate1")
                    schema=request.POST.getlist("schema1")
                    discount=request.POST.getlist("discount1")
                    discount_amt=request.POST.getlist("discount_amt1")
                    amount=request.POST.getlist("amount1")
                    tax_details=request.POST.getlist("tax_details1")

                    print("amount",amount,tax_details,schema)

                    for data in range(len(tax_details)):
                        po_temp=PurchaseOrder_Temp(
                            item_ID_id=item_name[data],
                            quantity=qty[data],
                            unit_id=unit[data],
                            free_qty=free_qty[data],
                            stock_qty=stock_qty[data],
                            rate=rate[data],
                            schema=schema[data],
                            discount=discount[data],
                            discount_amt=discount_amt[data],
                            amount=amount[data],
                            tax_details=tax_details[data],
                            status="Pending",
                        )
                        po_temp.save(print("temp table saved"))

                    # Po Parent

                    PO_ID=PurchaseOrder_Parent.objects.all().count()
                    today=date.today()
                    today=today.strftime("%d%m%y")
                    POID='PO'+today+'000'+str(PO_ID)
                    POparent=PurchaseOrder_Parent(
                        PO_id=POID,
                        PO_datetime=datetime.now(),
                        vendar_id_id=vendor_id,
                        Department_id=request.POST.get("department"),
                        Location_id=request.POST.get('location'),
                        po_location_id=request.POST.get('po_location'),
                        store_id_id=request.POST.get('store_id'),
                        net_amount=request.POST.get('net_amount'),
                        basic_amt=basic_amount,
                        PO_status="pending",
                        approval_status="pending",
                        issue_status='pending',
                    )
                    POparent.save(print("po parent saved"))

                    temp_items=PurchaseOrder_Temp.objects.all()

                    items=[data.item_ID_id for data in temp_items]
                    quantity=[data.quantity for data in temp_items]
                    unit=[data.unit_id for data in temp_items]
                    free_qty=[data.free_qty for data in temp_items]
                    stock_qty=[data.stock_qty for data in temp_items]
                    rate=[data.rate for data in temp_items]
                    discount=[data.discount for data in temp_items]
                    discount_amt=[data.discount_amt for data in temp_items]
                    amount=[data.amount for data in temp_items]
                    tax_details=[data.tax_details for data in temp_items]
                    schema=[data.schema for data in temp_items]
                    assets=[]
                    for data in items:
                        print("data",data)
                        items1=Inventory_ItemMaster.objects.get(id=data)
                        asset1=items1.assets
                        assets.append(asset1)
                    indent_id = []
                    for data in range(len(items)):
                        POchild=PurchaseOrder_Child(
                            PO_Id=POID,
                            item_id_id=items[data],
                            qty=quantity[data],
                            unit_id=unit[data],
                            PO_datetime=datetime.now(),
                            free_qty=free_qty[data],
                            stocy_qty=stock_qty[data],
                            rate=rate[data],
                            schema=schema[data],
                            discount=discount[data],
                            discount_amt=discount_amt[data],
                            amount=amount[data],
                            tex_details=tax_details[data],
                            received_qty="0",
                            issued_qty=0,
                            status="pending",
                            approval_status="pending",
                            issue_status='pending',
                            assets=assets[data],
                        )
                        POchild.save(print("po child saved"))
                        pi_child = Purchase_Intent_Child.objects.filter(item_id_id=items[data],status='entered')
                        for data2 in pi_child:
                            indent_id.append(data2.intent_id)
                            data2.status = 'completed'
                            data2.save()
                    temp_items.delete()
                    Makepo_PI_Temp.objects.all().delete()
                    for data in indent_id:
                        indent_count = Purchase_Intent_Child.objects.filter(intent_id=data).count()
                        completed_count = Purchase_Intent_Child.objects.filter(intent_id=data,status='completed').count()
                        pi_parent = Purchase_Intent_Parent.objects.get(intent_id=data)
                        if indent_count == completed_count:
                            pi_parent.p_status = 'completed'
                            pi_parent.save()


                    return HttpResponseRedirect("/make_PO_for_PI")
            Purchase_Intent_Temp.objects.all().delete()

            context={
                "records":records,"item_cate":item_cate,"PI_Temp_1":PI_Temp_1,"vendor":vendor,"items":items,
                "basic_amt" :basic_amt,
                'dept_detail': dept_detail,
                'store_detail':store_detail,
                'location_detail':location_detail,
            }
            return render(request,"pharmacy/make_po_PI.html",context)

        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


@login_required(login_url='/user_login')
def PI_items_details(request,pk):
    try:
        pi_list = Purchase_Intent_Child.objects.filter(intent_id=pk)
        PI_Child_list=Purchase_Intent_Child.objects.filter(intent_id=pk,status='pending')
        pi_parent_detail=Purchase_Intent_Parent.objects.get(intent_id=pk)
        store_detail = StoreMaster.objects.get(store_type=0)
        location_detail = LocationMaster.objects.all()
        basic_amt = 0
        unit_id = []
        unit_name = []
        stock_qty = []
        indent_id=pk
        for data in PI_Child_list:
            stock_quantity = Stock_BatchWise.objects.filter(item_id_id=data.item_id_id).last()
            unit = Inventory_ItemMaster.objects.get(id=data.item_id_id)
            unit_n = ItemUnitMaster.objects.get(id=unit.unit)
            unit_name.append(unit_n.unit)
            unit_id.append(unit.unit)
            stock_qty.append(stock_quantity.available_qty)
            basic_amt += int(str(data.amount))
        PI_Child = zip(PI_Child_list,unit_id,stock_qty,unit_name)
        dept_detail = ServiceDepartment.objects.all()
        # netamount=[data.amount for data in PI_Child]
        # netamount1=0
        # for data in netamount:
        #     netamount1 += int('0'+data)
        vendor=VendorMaster.objects.all()
        make_po_btn=request.POST.get("Make_PO")
        if make_po_btn == "Make_PO":
            if request.method == "POST":
                vendor_id=request.POST.get("vendor_id")
                tax=request.POST.get("tax")
                basic_amount=request.POST.get("basic_amount")
                item_name=request.POST.getlist("item_name1")
                qty=request.POST.getlist("qty1")
                unit=request.POST.getlist("unit1")
                free_qty=request.POST.getlist("free_qty1")
                stock_qty=request.POST.getlist("stock_qty1")
                rate=request.POST.getlist("rate1")
                schema=request.POST.getlist("schema1")
                discount=request.POST.getlist("discount1")
                discount_amt=request.POST.getlist("discount_amt1")
                amount=request.POST.getlist("amount1")
                tax_details=request.POST.getlist("tax_details1")


                for data in range(len(tax_details)):
                    po_temp=PurchaseOrder_Temp(
                        item_ID_id=item_name[data],
                        quantity=qty[data],
                        unit_id=unit[data],
                        free_qty=free_qty[data],
                        stock_qty=stock_qty[data],
                        rate=rate[data],
                        schema=schema[data],
                        discount=discount[data],
                        discount_amt=discount_amt[data],
                        amount=amount[data],
                        tax_details=tax_details[data],
                        status="Pending",
                    )
                    po_temp.save(print("temp table saved"))

                # Po Parent

                PO_ID=PurchaseOrder_Parent.objects.all().count()
                today=date.today()
                today=today.strftime("%d%m%y")
                POID='PO'+today+'000'+str(PO_ID)
                POparent=PurchaseOrder_Parent(
                    PO_id=POID,
                    PO_datetime=datetime.now(),
                    vendar_id_id=vendor_id,
                    Department_id=request.POST.get("department"),
                    Location_id=request.POST.get('location'),
                    po_location_id=request.POST.get('po_location'),
                    store_id_id=request.POST.get('store_id'),
                    net_amount=request.POST.get('net_amount'),
                    basic_amt=basic_amount,
                    PO_status="pending",
                    approval_status="pending",
                    issue_status='pending',
                )
                POparent.save(print("po parent saved"))

                temp_items=PurchaseOrder_Temp.objects.all()

                items=[data.item_ID_id for data in temp_items]
                quantity=[data.quantity for data in temp_items]
                unit=[data.unit_id for data in temp_items]
                free_qty=[data.free_qty for data in temp_items]
                stock_qty=[data.stock_qty for data in temp_items]
                rate=[data.rate for data in temp_items]
                discount=[data.discount for data in temp_items]
                discount_amt=[data.discount_amt for data in temp_items]
                amount=[data.amount for data in temp_items]
                tax_details=[data.tax_details for data in temp_items]
                schema=[data.schema for data in temp_items]
                assets=[]
                for data in items:
                    print("data",data)
                    items1=Inventory_ItemMaster.objects.get(id=data)
                    asset1=items1.assets
                    assets.append(asset1)
                indent_id = []
                for data in range(len(items)):
                    POchild=PurchaseOrder_Child(
                        PO_Id=POID,
                        item_id_id=items[data],
                        qty=quantity[data],
                        unit_id=unit[data],
                        PO_datetime=datetime.now(),
                        free_qty=free_qty[data],
                        stocy_qty=stock_qty[data],
                        rate=rate[data],
                        schema=schema[data],
                        discount=discount[data],
                        discount_amt=discount_amt[data],
                        amount=amount[data],
                        tex_details=tax_details[data],
                        issued_qty=0,
                        received_qty="0",
                        status="pending",
                        approval_status="pending",
                        issue_status='pending',
                        assets=assets[data],
                    )
                    POchild.save(print("po child saved"))
                    pi_child = Purchase_Intent_Child.objects.get(item_id_id=items[data],intent_id=request.POST.get('indent_id'))
                    pi_child.status = 'completed'
                    pi_child.save()

                temp_items.delete()
                indent_count = Purchase_Intent_Child.objects.filter(intent_id=request.POST.get('indent_id')).count()
                completed_count = Purchase_Intent_Child.objects.filter(intent_id=request.POST.get('indent_id'),status='completed').count()
                pi_parent = Purchase_Intent_Parent.objects.get(intent_id=request.POST.get('indent_id'))
                print('completed_count',completed_count)
                print('indent_count',indent_count)
                if indent_count == completed_count:
                    pi_parent.p_status = 'completed'
                    pi_parent.save()

                return HttpResponseRedirect("/make_PO_for_PI")


        context={
            "PI_Child":PI_Child,"vendor":vendor,
            'dept_detail':dept_detail,
            'pi_list':pi_list,
            'basic_amt':basic_amt,
            'indent_id':indent_id,
            'store_detail':store_detail,
            'location_detail':location_detail,
            'pi_parent_detail':pi_parent_detail,
        }
        return render(request,"pharmacy/PI_items_details.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def manual_stock_adjustment(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'manual_stock_ajustment' in access.user_profile.screen_access:
        try:
            item_category = ItemCategoryMaster.objects.all()
            item_subcategory = ItemsubcategoryMaster.objects.all()
            store_names = StoreMaster.objects.all()
            department = ServiceDepartment.objects.all()
            item_names = Inventory_ItemMaster. objects.all()
            location_detail=LocationMaster.objects.all()
            item_list = []
            item_list1 = []
            store_id='0'
            location_id='0'
            if request.POST.get("search") == "search":
                item_category_1 = request.POST.get("item_cate")
                item_name = request.POST.get("item_name")
                item_id = item_name.split('.')
                store_id = request.POST.get("store_id")
                location_id = request.POST.get("location_id")

                if item_category_1 != "" and store_id != "" and location_id != "" and item_name !='':
                    store_type = StoreMaster.objects.get(id=store_id)
                    item_master = Inventory_ItemMaster.objects.get(item_category=item_category_1,id=item_id[0])

                    if store_type.store_type == '1':
                        item_list.append(Stock_BatchWise_Mainstore.objects.filter(location_id_id=location_id,store_id_id=store_id,item_id_id=item_master.id))
                    elif store_type.store_type == '2':
                        item_issue_p = Item_Issue_ToSubStore_Parent.objects.filter(location_id_id=location_id,received_store_id=store_id)
                        for data in item_issue_p:
                            item_list1.append(Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data.item_issue_no,item_id_id=item_master.id))
                    elif store_type.store_type == '0':
                        item_list.append(Stock_BatchWise.objects.filter(location_id_id=location_id,store_id_id=store_id,item_id_id=item_master.id))
                elif item_category_1 != "" and store_id != "" and location_id != "":
                    store_type = StoreMaster.objects.get(id=store_id)
                    item_master = Inventory_ItemMaster.objects.filter(item_category=item_category_1)
                    item_ids = [data.id for data in item_master]

                    if store_type.store_type == '1':
                        item_list.append(Stock_BatchWise_Mainstore.objects.filter(location_id_id=location_id,store_id_id=store_id,item_id__in=item_ids))
                    elif store_type.store_type == '2':
                        item_issue_p = Item_Issue_ToSubStore_Parent.objects.filter(location_id_id=location_id,received_store_id=store_id)
                        for data in item_issue_p:
                            item_list1.append(Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data.item_issue_no,item_id__in=item_ids))
                    elif store_type.store_type == '0':
                        item_list.append(Stock_BatchWise.objects.filter(location_id_id=location_id,store_id_id=store_id,item_id__in=item_ids))


            context = {
                "item_category":item_category,"item_subcategory":item_subcategory,"store_names":store_names,"item_names":item_names,"department":department,
                'location_detail':location_detail,'item_list':item_list,'item_list1':item_list1,'store_id':store_id,'location_id':location_id,
            }
            return render(request,"pharmacy/item_adjustment_record.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

# Update pendin approvel
@login_required(login_url='/user_login')
def Single_update_adjustment(request):
    try:
        store_id = request.GET.get("store")
        location_id = request.GET.get("location")
        item_id=request.GET.get("item_id")
        batch_no=request.GET.get("batch_no")
        available_qty=request.GET.get("available_qty")
        adjust_qty=request.GET.get("adjust_qty")
        amount=request.GET.get("amount")
        total_qty=request.GET.get("total_qty")
        remark=request.GET.get("remark")
        store_type = StoreMaster.objects.get(id=store_id)

        if store_type.store_type == '1':
            batchwise_table = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id,batch_no=batch_no,store_id_id=store_id,location_id_id=location_id).last()
            batchwise_table.total_qty = total_qty
            batchwise_table.adjust_qty = adjust_qty
            if available_qty < total_qty:
                batchwise_table.amount = int(str(batchwise_table.amount)) +  int(amount)
                batchwise_table.available_qty =  int(str(batchwise_table.available_qty)) + int(adjust_qty)
            else:
                batchwise_table.amount = int((batchwise_table.amount)) -  int(amount)
                batchwise_table.available_qty =  int(str(batchwise_table.available_qty)) - int(adjust_qty)
            batchwise_table.save()

        elif store_type.store_type == '2':
            item_issue_p = Item_Issue_ToSubStore_Parent.objects.filter(location_id_id=location_id,received_store_id=store_id)
            for data in item_issue_p:
                item_issue_child = Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data.item_issue_no,item_id_id=item_id,serial_batch=batch_no)
                # item_issue_child = Item_Issue_Child.objects.filter(item_id=item_id,serial_batch=batch_no).last()
                # item_issue_child.total_amount = total_qty
                item_issue_child.remark = remark

                if available_qty < total_qty:
                    item_issue_child.amount = int(str(item_issue_child.amount)) +  int(amount)
                    item_issue_child.available_qty =  int(str(item_issue_child.available_qty)) + int(adjust_qty)
                else:
                    item_issue_child.amount = int(str(item_issue_child.amount)) -  int(amount)
                    item_issue_child.available_qty =  int(str(item_issue_child.available_qty)) - int(adjust_qty)
                item_issue_child.save()
        elif store_type.store_type == '0':
            batchwise_table = Stock_BatchWise.objects.filter(item_id_id=item_id,batch_no=batch_no,store_id_id=store_id,location_id_id=location_id).last()
            batchwise_table.total_qty = total_qty
            batchwise_table.adjust_qty = adjust_qty
            if available_qty < total_qty:
                batchwise_table.amount = int(str(batchwise_table.amount)) +  int(amount)
                batchwise_table.available_qty =  int(str(batchwise_table.available_qty)) + int(adjust_qty)
            else:
                batchwise_table.amount = int((batchwise_table.amount)) -  int(amount)
                batchwise_table.available_qty =  int(str(batchwise_table.available_qty)) - int(adjust_qty)
            batchwise_table.save()

        data='Item Updated Successfilly'
        return JsonResponse(data, safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def transfer_indent(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_indent' in access.user_profile.screen_access:
        try:
            mainstore=StoreMaster.objects.filter(store_type="1")
            cpcstore=StoreMaster.objects.get(store_type="0")
            item_master=Inventory_ItemMaster.objects.all()
            request_store = request.store_id
            cpc_store= StoreMaster.objects.filter(id__in=request_store,store_type='0').last()
            main_store = StoreMaster.objects.filter(id__in=request_store,store_type=1).last()
            transfer_intent_temp=Transfer_Intent_Temp.objects.filter(location_id_id=request.location)

            Insert_button=request.POST.get("insert")
            Saved_button=request.POST.get("Saved_button")
            if Insert_button == "Insert":
                if request.method=="POST":
                    main_store_name=request.POST.get("main_store")
                    main_store_name1 = StoreMaster.objects.get(id=main_store_name)
                    location_id=StoreMaster.objects.get(id=main_store_name)
                    cpc_store_id=request.POST.get("cpc_store_id")
                    cpc_store_id1 = StoreMaster.objects.get(id=cpc_store_id)
                    priority=request.POST.get("priority")
                    item_name=request.POST.get("item_name")
                    quantity=request.POST.get("quantity")
                    item_code=request.POST.get("item_code")
                    department1=request.POST.get("department")
                    item_belongs_to=request.POST.get("item_belongs_to")
                    remark=request.POST.get("remark")

                    purchase_intent_count=Transfer_Intent_Parent.objects.all().count()
                    today=date.today()
                    today_date=today.strftime("%d%m%y")
                    purchase_intent_id = "TI"+ today_date +"00"+str(purchase_intent_count)
                    Transfer_Intent_Temp1=Transfer_Intent_Temp(
                        trnasfer_indent_no=purchase_intent_id,
                        intent_date=datetime.now(),
                        cpc_store_id=cpc_store_id,
                        main_store_id=main_store_name,
                        location_id_id=location_id.location_id_id,
                        department_id=department1,
                        priority=priority,
                        item_id_id=item_name,
                        quantity=quantity,
                        rate=request.POST.get("rate"),
                        amount=request.POST.get("amount"),
                        item_code=item_code,
                        item_belongs_to=item_belongs_to,
                        remark=remark,
                        status="Pending",
                    )
                    Transfer_Intent_Temp1.save(print("temporary table is saved"))
                    context ={
                        "cpc_store":cpc_store,"mainstore":mainstore,"item_master":item_master,'transfer_intent_temp':transfer_intent_temp,
                        'main_store_name':main_store_name1,'priority':priority,'main_store':main_store,'cpcstore':cpcstore,'cpc_store_id':cpc_store_id1
                    }

            if  Saved_button =="Saved_button":
                if request.method == "POST":
                    intent_id1=[data.trnasfer_indent_no for data in transfer_intent_temp]
                    cpc_store_id1=[data.cpc_store_id for data in transfer_intent_temp]
                    location_id1=[data.location_id_id for data in transfer_intent_temp]
                    mainstore1=[data.main_store_id for data in transfer_intent_temp]
                    priority1=[data.priority for data in transfer_intent_temp]
                    item_id1=[data.item_id_id for data in transfer_intent_temp]
                    quantity1=[data.quantity for data in transfer_intent_temp]
                    item_code1=[data.item_code for data in transfer_intent_temp]
                    item_belongs_to1=[data.item_belongs_to for data in transfer_intent_temp]
                    remark1=[data.remark for data in transfer_intent_temp]
                    dept1=[data.department_id for data in transfer_intent_temp]
                    rate1=[data.rate for data in transfer_intent_temp]
                    amount1=[data.amount for data in transfer_intent_temp]

                    total=0
                    for data1 in intent_id1:
                        totalamt=Transfer_Intent_Parent.objects.filter(trnasfer_indent_no=data1)
                        if not totalamt:
                            totalamt.total_amount = 0
                        total= total + int(str(totalamt.total_amount))
                    transfer_intent_Parent=Transfer_Intent_Parent(
                        trnasfer_indent_no=intent_id1[0],
                        intent_date=datetime.now(),
                        cpc_store_id=cpc_store_id1[0],
                        department_id=dept1[0],
                        location_id_id=location_id1[0],
                        main_store_id=mainstore1[0],
                        total_amount=total,
                        p_status="pending",
                        approval_status="pending",
                    )
                    transfer_intent_Parent.save(print("purchase_intent_parent saved"))

                    for data in range(len(item_id1)):
                        transfer_intent_child=Transfer_Intent_Child(
                            trnasfer_indent_no=intent_id1[data],
                            intent_date=datetime.now(),
                            priority=priority1[data],
                            item_id_id=item_id1[data],
                            quantity=quantity1[data],
                            rate=rate1[data],
                            amount=amount1[data],
                            item_code=item_code1[data],
                            item_belongs_to=item_belongs_to1[data],
                            remark=remark1[data],
                            status="pending",
                            received_qty='0',
                            approval_status="pending",

                        )
                        transfer_intent_child.save(print("material_intent_child saved"))

                    Transfer_Intent_Temp.objects.filter(location_id_id=request.location).delete()
                    return HttpResponseRedirect("/transfer_indent")

            context ={
                "cpc_store":cpc_store,"mainstore":mainstore,"item_master":item_master,'transfer_intent_temp':transfer_intent_temp,
                'main_store':main_store,'cpcstore':cpcstore
            }
            return render(request,"pharmacy/stock_transfer/transfer_indent.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def stock_transfer(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_request_to_mainstore' in access.user_profile.screen_access:
        try:
            transfer_indent = Transfer_Request_Mainstore_Parent.objects.filter(status__in=['completed','partially sended'])
            context ={
                'transfer_indent':transfer_indent,
            }
            return render(request,"pharmacy/stock_transfer/stock_transfer.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def transfer_request_tomainstore(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_request_to_mainstore' in access.user_profile.screen_access:
        try:
            transfer_indent = Transfer_Intent_Parent.objects.filter(p_status="pending")
            context ={
                'transfer_indent':transfer_indent,
            }
            return render(request,"pharmacy/stock_transfer/transfer_request_tomainstore.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def search_transfer_item_detail(request,pk):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_request_to_mainstore' in access.user_profile.screen_access:
        try:
            transfer_indent_p = Transfer_Intent_Parent.objects.get(trnasfer_indent_no=pk)
            transfer_indent_c = Transfer_Intent_Child.objects.filter(trnasfer_indent_no=pk,status="pending")
            cpc_store=StoreMaster.objects.get(store_type=0)
            store_detail = StoreMaster.objects.filter(store_type=1)

            save_all = request.POST.get("save_all")
            if save_all == "save_all":
                if request.method == "POST":
                    request_count=Transfer_Request_Mainstore_Parent.objects.all().count()
                    today=date.today()
                    today_date=today.strftime("%d%m%y")
                    request_no='RTN'+today_date+"00"+str(request_count)
                    item_id=request.POST.getlist("item_id_id")
                    indent_qty=request.POST.getlist("indent_qty")
                    priority=request.POST.getlist("p_priority")
                    rate=request.POST.getlist("rate")
                    amount=request.POST.getlist("amount")
                    remark=request.POST.getlist("remark")

                    request_parent=Transfer_Request_Mainstore_Parent(
                            request_no=request_no,
                            transfer_indent_no=pk,
                            intent_date=request.POST.get("p_indent_date"),
                            request_date=datetime.now(),
                            transfer_return_no='',
                            indent_store_id=request.POST.get("p_received_store_1"),
                            request_store_id=request.POST.get("request_store"),
                            location_id_id=request.POST.get("location_id"),
                            department_id=request.POST.get("department_1"),
                            status="pending",
                            receive_status='pending',
                    )
                    request_parent.save()
                    for data in range(len(item_id)):
                        request_child=Transfer_Request_Mainstore_Child(
                            request_no=request_no,
                            request_date=datetime.now(),
                            priority=priority[data],
                            item_id_id=item_id[data],
                            quantity=indent_qty[data],
                            rate=rate[data],
                            issued_qty='0',
                            remark=remark[data],
                            amount=amount[data],
                            status="pending",
                            receive_status='pending',
                        )
                        request_child.save()

                        indent_child = Transfer_Intent_Child.objects.filter(trnasfer_indent_no=pk,item_id_id=item_id[data]).first()
                        indent_child.status = 'requested'
                        indent_child.save()

                    indent_parent = Transfer_Intent_Parent.objects.get(trnasfer_indent_no=pk)
                    indent_parent.p_status = 'requested'
                    indent_parent.save()


            context={
                'transfer_indent_p':transfer_indent_p,
                'transfer_indent_c':transfer_indent_c,'store_detail':store_detail,
            }
            return render(request,"pharmacy/stock_transfer/search_transfer_item_detail.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def transfer_to_cpc(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_request_to_mainstore' in access.user_profile.screen_access:
        try:
            request_parent = Transfer_Request_Mainstore_Parent.objects.filter(status='pending')
            # request_child = Transfer_Request_Mainstore_Child.objects.all()
            context={
                'request_parent':request_parent,
                # 'request_child':request_child,
            }

            return render(request,"pharmacy/stock_transfer/request_transfer_details.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def request_transfer_item_list(request,pk):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_request_to_mainstore' in access.user_profile.screen_access:
        try:
            request_parent = Transfer_Request_Mainstore_Parent.objects.get(request_no=pk)
            request_child = Transfer_Request_Mainstore_Child.objects.filter(request_no=pk)
            batch_nos =[]
            for data in request_child:
                get_batch = Stock_BatchWise_Mainstore.objects.exclude(available_qty=0).filter(item_id_id=data.item_id_id).order_by('expiry_date')
                batch_no = []
                for data in get_batch:
                    batch_no.append(data.batch_no)
                batch_nos.append(batch_no)
            save_all = request.POST.get("save_all")
            if save_all == "save_all":
                if request.method == 'POST':
                    batch_no = request.POST.getlist("serial_batch")
                    item_id = request.POST.getlist("item_id_id")
                    expiry_date = request.POST.getlist("expiry_date")
                    indent_store = request.POST.get("indent_store_1")
                    return_qty = request.POST.getlist("return_qty")
                    reason = request.POST.get("reason")
                    rate = request.POST.getlist("rate")
                    amount = request.POST.getlist("amount")
                    mainstore_id = 2
                    indent_id = request.POST.get("indent_id")

                    today=date.today()
                    today_date=today.strftime("%d%m%y")
                    counter=Item_Return_ToCPC_Parent.objects.all().count()
                    item_return_id="TRN"+today_date+"00"+str(counter)

                    location_id=StoreMaster.objects.get(id=mainstore_id)
                    cpc_store=StoreMaster.objects.get(store_type=0)


                    return_cpc_parent=Item_Return_ToCPC_Parent(
                        return_no=item_return_id,
                        return_date=today,
                        indent_store_id=indent_store,
                        return_store_id=mainstore_id,
                        request_no=pk,
                        location_id_id=location_id.location_id_id,
                        receiving_store_id=cpc_store.id,
                        stock_transfer = '1',
                        status="",
                    )
                    return_cpc_parent.save()

                    for data in range(len(item_id)):
                        if return_qty[data]:
                            total_qty1 = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data]).last()
                            total_qty_1 = int(total_qty1.total_qty) - int(return_qty[data])
                            item_return_cpc_child=Item_Return_ToCPC_Child(
                                return_no=item_return_id,
                                return_date=datetime.today(),
                                batch_no=batch_no[data],
                                expiry_date=expiry_date[data],
                                rate=rate[data],
                                amount=amount[data],
                                item_id_id=item_id[data],
                                return_qty=return_qty[data],
                                total_qty=total_qty_1,
                                opening_balance=total_qty1.total_qty,
                                transaction_cost='',
                                total_cost='',
                                opening_cost='',
                                reason=reason,
                                status="Pending",
                                stock_transfer = '1',
                                movable_status='Return To CPC'
                            )

                            item_return_cpc_child.save()

                            totalqty2=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data]).last()
                            totalqty2.total_qty = int(str(total_qty1.total_qty)) - int(str(return_qty[data]))
                            totalqty2.save()

                            availableqty=Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data],batch_no=batch_no[data]).last()
                            availableqty.available_qty= int(str(availableqty.available_qty)) - int(str(return_qty[data]))
                            availableqty.save()

                            totalqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id[data]).last()
                            totalqty_m.total_qty = int(str(total_qty1.total_qty)) + int(str(return_qty[data]))
                            totalqty_m.save()

                            availableqty_m=Stock_BatchWise.objects.filter(item_id_id=item_id[data],batch_no=batch_no[data]).last()
                            availableqty_m.available_qty= int(str(availableqty.available_qty)) + int(str(return_qty[data]))
                            availableqty_m.save()

                            request_child_c = Transfer_Request_Mainstore_Child.objects.filter(request_no=pk,item_id_id=item_id[data]).first()
                            request_child_c.status = 'completed'
                            request_child_c.save()

                            trans_child = Transfer_Intent_Child.objects.filter(trnasfer_indent_no=indent_id,item_id_id=item_id[data]).first()
                            trans_child.status = 'transfered'
                            trans_child.save()

                    request_parent = Transfer_Request_Mainstore_Parent.objects.get(request_no=pk)
                    request_parent.status = 'completed'
                    request_parent.transfer_return_no = item_return_id
                    request_parent.save()

                    trans_parent = Transfer_Intent_Parent.objects.get(trnasfer_indent_no=indent_id)
                    trans_parent.status = 'transfered'
                    trans_parent.save()

                    return HttpResponseRedirect('/transfer_to_cpc')

            request_child_c = zip(request_child,batch_nos)
            context={
                'request_parent':request_parent,
                'request_child':request_child_c,
            }
            return render(request,"pharmacy/stock_transfer/request_transfer_item_list.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def search_transfer_intent(request,pk):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'transfer_request_to_mainstore' in access.user_profile.screen_access:
        try:
            transfer_indent_p = Transfer_Request_Mainstore_Parent.objects.get(transfer_indent_no=pk,status__in=['completed','partially sended'])
            transfer_indent_c = Transfer_Request_Mainstore_Child.objects.filter(request_no=transfer_indent_p.request_no,status__in=['completed','partially sended'])
            cpc_store=StoreMaster.objects.get(store_type=0)
            batch_nos =[]
            for data in transfer_indent_c:
                get_batch = Stock_BatchWise.objects.exclude(available_qty=0).filter(item_id_id=data.item_id_id).order_by('expiry_date')
                batch_no = []
                for data in get_batch:
                    batch_no.append(data.batch_no)
                batch_nos.append(batch_no)

            save_all = request.POST.get("save_all")
            if save_all == "save_all":
                if request.method == "POST":
                    # Generate ID
                    item_issue_parent_count=Item_Issue_Parent.objects.all().count()
                    today=date.today()
                    today_date=today.strftime("%d%m%y")
                    item_issue_no='ITI'+today_date+"00"+str(item_issue_parent_count)
                    item_id=request.POST.getlist("item_id_id")
                    barcode=request.POST.getlist("barcode")
                    serial_batch=request.POST.getlist("serial_batch")
                    expiry_date=request.POST.getlist("expiry_date")
                    issued_qty=request.POST.getlist("issued_qty")
                    indent_qty=request.POST.getlist("indent_qty")
                    available_qty=request.POST.getlist("available_qty")
                    rate=request.POST.getlist("rate")
                    amount=request.POST.getlist("amount")
                    remark=request.POST.getlist("remark")

                    # Item Isuue Parent

                    ITI_Child3=Item_Issue_Child.objects.filter(intent_no=pk)
                    totalamount3=[data.amount for data in ITI_Child3]
                    totalamts=0
                    for data in totalamount3:
                        totalamts= int(totalamts) + int(data)

                    item_issue_parent=Item_Issue_Parent(
                            item_issue_no=item_issue_no,
                            intent_no=pk,
                            item_issue_date=datetime.now(),
                            issued_store_id=cpc_store.id,
                            received_store_id=request.POST.get("p_received_store_1"),
                            location_id_id=cpc_store.location_id_id,
                            issue_location_id=cpc_store.location_id_id,
                            receive_location_id=request.POST.get("location_id"),
                            department_id=request.POST.get("department_1"),
                            approved_by=request.POST.get("p_approved_by"),
                            total_amount=totalamts,
                            p_status="pending",
                            transfer_status='transfer issue',
                    )
                    item_issue_parent.save()

                    for data in range(len(issued_qty)):
                        if barcode[data] and serial_batch[data] and issued_qty[data] != "":
                            # item issue child total quantity
                            totalamt=Stock_BatchWise.objects.filter(item_id_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                            if issued_qty[data] == "":
                                issued_qty[data] = 0
                            total_amount = int(str(totalamt.total_qty)) - int(str(issued_qty[data]))

                            # item issue child available quantity
                            available = Stock_BatchWise.objects.filter(item_id_id=item_id[data],batch_no=serial_batch[data],location_id_id=cpc_store.location_id_id).last()
                            available_main = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data],batch_no=serial_batch[data],store_id_id=request.POST.get("p_received_store_1")).last()
                            total_main = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data],store_id_id=request.POST.get("p_received_store_1")).last()
                            if not available:
                                available_qty = 0
                            else:
                                available_qty = available.available_qty
                            available_qty = int(str(available_qty)) - int(str(issued_qty[data]))

                            if total_main:
                                total_main_qty=int(str(total_main.total_qty)) + int(str(issued_qty[data]))
                            else:
                                total_main_qty=issued_qty[data]

                            if available_main:
                                available_main_qty=int(str(available_qty)) + int(str(issued_qty[data]))
                            else:
                                available_main_qty=issued_qty[data]
                            get_po_id = Stock_BatchWise.objects.filter(item_id_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                            po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.PO_id,item_id_id=item_id[data])

                            if po_detail.schema and po_detail.discount and po_detail.tex_details:
                                rate_amt = int(issued_qty[data]) * int(rate[data])
                                schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                                disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                                tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                                total_cost = rate_amt - schema_amt - disc_amt + tax_amt
                            elif po_detail.schema and po_detail.tex_details:
                                rate_amt = int(issued_qty[data]) * int(rate[data])
                                schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
                                tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                                total_cost = rate_amt - schema_amt + tax_amt
                            elif po_detail.discount and po_detail.tex_details:
                                rate_amt = int(issued_qty[data]) * int(rate[data])
                                disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
                                tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                                total_cost = rate_amt - disc_amt + tax_amt
                            elif po_detail.tex_details:
                                rate_amt = int(issued_qty[data]) * int(rate[data])
                                tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
                                total_cost = rate_amt + tax_amt
                            else:
                                total_cost = 0

                            total_cost_amt = int(totalamt.total_cost) - int(total_cost)

                            item_issue_child = Item_Issue_Child(
                                item_issue_no = item_issue_no,
                                intent_no = pk,
                                item_id_id = item_id[data],
                                item_issue_date = datetime.now(),
                                barcode = barcode[data],
                                serial_batch = serial_batch[data],
                                expiry_date = expiry_date[data],
                                available_qty = issued_qty[data],
                                issued_qty = issued_qty[data],
                                rate = rate[data],
                                intent_qty = indent_qty[data],
                                total_amount = total_amount,
                                opening_balance = totalamt.total_qty,
                                transaction_cost = total_cost,
                                total_cost=total_cost_amt,
                                opening_cost=totalamt.total_cost,
                                remark = remark[data],
                                priority = '',
                                amount = amount[data],
                                status = "",
                                transfer_status='transfer issue',
                                movement_status = "CPC Issue Entry",
                            )
                            batch_wise=Stock_BatchWise_Mainstore(                                                      #stock entry batwise
                                item_issue_no=item_issue_no,
                                item_issue_date=datetime.now(),
                                intent_no=pk,
                                indent_date=transfer_indent_p.intent_date,
                                item_id_id=item_id[data],
                                batch_no=serial_batch[data],
                                expiry_date=expiry_date[data],
                                received_qty=issued_qty[data],
                                rate=rate[data],amount=amount[data],store_id_id=request.POST.get('p_received_store_1'),
                                # vendor_id_id=0,
                                department_id_id=request.POST.get("department_1"),
                                location_id_id=cpc_store.location_id_id,
                                receive_location_id=request.POST.get("location_id"),
                                available_qty=available_main_qty,
                                total_qty=total_main_qty,
                                total_cost = total_cost_amt,
                                adjust_qty="",
                                status=" ",
                                total_consume_qty = '',
                                transfer_status='transfer issue',
                            )
                            if barcode[data] and serial_batch[data] and issued_qty[data] != "":
                                item_issue_child.save()
                                batch_wise.save()

                                # Update Total Cost to Batchwise table
                                total_cost_detail = Stock_BatchWise.objects.filter(item_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                                if issued_qty[data] == "":
                                    total_cost = 0
                                total_cost_detail.total_cost = int(total_cost_detail.total_cost) - int(total_cost)
                                total_cost_detail.save()

                                # Update available Amount To Batchwise Table

                                available=Stock_BatchWise.objects.filter(item_id=item_id[data],batch_no=serial_batch[data],location_id_id=cpc_store.location_id_id).last()
                                if issued_qty[data] == "":
                                    issued_qty[data]=0
                                available_qty= int(str(available.available_qty)) - int(str(issued_qty[data]))
                                available.available_qty=available_qty
                                available.save()

                                # Update Total Quantity to Batchwise table

                                totalamt=Stock_BatchWise.objects.filter(item_id_id=item_id[data],location_id_id=cpc_store.location_id_id).last()
                                if issued_qty[data] == "":
                                    issued_qty[data] = 0
                                total_amount = int(str(totalamt.total_qty)) - int(str(issued_qty[data]))
                                totalamt.total_qty = total_amount
                                totalamt.save()

                                #update purchase order child table issued qty and issue_status
                                #received

                                transfer_child = Transfer_Intent_Child.objects.get(item_id_id=item_id[data],trnasfer_indent_no=pk)
                                issue_qty = int(transfer_child.received_qty) + int(issued_qty[data])

                                if int(transfer_child.quantity) == issue_qty:
                                    transfer_child.status = 'completed'
                                    transfer_child.received_qty = issue_qty
                                    transfer_child.save()
                                else:
                                    transfer_child.status = 'partially completed'
                                    transfer_child.received_qty = issue_qty
                                    transfer_child.save()

                                request_parent = Transfer_Request_Mainstore_Parent.objects.get(transfer_indent_no=pk)
                                request_child = Transfer_Request_Mainstore_Child.objects.get(item_id_id=item_id[data],request_no=request_parent.request_no)
                                issued_qtyy = int(request_child.issued_qty) + int(issued_qty[data])
                                if int(request_child.quantity) == issued_qtyy:
                                    request_child.status = 'sended'
                                    request_child.issued_qty = issued_qtyy
                                    request_child.save()
                                else:
                                    request_child.status = 'partially sended'
                                    request_child.issued_qty = issued_qtyy
                                    request_child.save()

                    transfer_count = Transfer_Intent_Child.objects.filter(trnasfer_indent_no=pk).count()
                    completed_count = Transfer_Intent_Child.objects.filter(trnasfer_indent_no=pk,status='completed').count()
                    transfer_parent = Transfer_Intent_Parent.objects.get(trnasfer_indent_no=pk)
                    if transfer_count == completed_count:
                        transfer_parent.p_status = 'completed'
                        transfer_parent.save()
                    else:
                        transfer_parent.p_status = 'partially completed'
                        transfer_parent.save()

                    request_count = Transfer_Request_Mainstore_Child.objects.filter(request_no=request_parent.request_no).count()
                    r_completed_count = Transfer_Request_Mainstore_Child.objects.filter(request_no=request_parent.request_no,status='sended').count()
                    if request_count == r_completed_count:
                        request_parent.status = 'sended'
                        request_parent.save()
                    else:
                        request_parent.status = 'partially sended'
                        request_parent.save()

                    transfer_id=f'{transfer_indent_p.transfer_indent_no}'
                    context={

                    }
                    return HttpResponseRedirect('/stock_transfer')

            #outstanding Value
            trans_outstanding=[data.quantity for data in transfer_indent_c ]
            trans_outstanding1=[data.issued_qty for data in transfer_indent_c ]
            outstanding=[]
            for data1,data2 in zip(trans_outstanding,trans_outstanding1):
                if data2 == "":
                    data2 = 0
                aaa=int(data1)-int(data2)
                outstanding.append(aaa)

            records = zip(transfer_indent_c,batch_nos,outstanding)

            context ={
                'transfer_indent_p':transfer_indent_p,
                'transfer_indent_c':records,
            }
            return render(request,"pharmacy/stock_transfer/search_transfer_intent.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def add_counter_saleout_patient(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'add_counter_sales' in access.user_profile.screen_access:
        try:
            patient_registration = PatientsRegistrationsAllInOne.objects.all()
            CounterSale_Temp_1 = PS_CounterSale_Temp.objects.all()
            countersale_temp_otc = PS_CounterSale_Temp_OTC.objects.all()

            #get itemname from item master
            item_names = Inventory_ItemMaster.objects.all()
            batch_no = Item_Issue_ToSubStore_Parent.objects.filter(received_store__in=request.store_id)
            item_issued_id=[data.item_issue_no for data in batch_no]
            # serial batch from item isusse table
            serial_batch=[]
            for data in item_issued_id:
                batch_no = Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data)
                batch = [data.serial_batch for data in batch_no]
                for data2 in batch:
                    serial_batch.append(data2)
            serial_batch_1 = list(set(serial_batch))

            Op_sales_no = PS_CounterSale_Parent.objects.all().count()
            today = date.today()
            today = today.strftime("%d%m%y")
            PSID = 'PS'+today+'000'+str(Op_sales_no)
            if request.POST.get("save_temp") == "save_temp":
                item_id = request.POST.get("item_id").split('.')
                batch = request.POST.get("batch")
                patient_name=request.POST.get("patient_name")
                uhid=request.POST.get("uhid")
                consultant=request.POST.get("consultant")
                consultant_name=request.POST.get("consultant_name")
                mob_no=request.POST.get("mob_no")
                age=request.POST.get("age")
                gender=request.POST.get("gender")
                visit_id=request.POST.get("visit_id")
                panel=request.POST.get("panel")
                types_value=request.POST.get("type")
                request.session['ph_uhid']=uhid
                request.session['ph_visit_id']=visit_id
                CounterSale_Temp = PS_CounterSale_Temp(
                    item_id_id=item_id[0],
                    batch_no=request.POST.get("batch"),
                    expiry_date=request.POST.get("expiry"),
                    mrp=request.POST.get("mrp"),
                    qty=request.POST.get("qty"),
                    rate=request.POST.get("rate"),
                    before_disc_amount=request.POST.get("before_disc_amount"),
                    discount=request.POST.get("discount"),
                    amount=request.POST.get("amount"),
                    status="pending",
                    moment_status="PS Entry",
                    reason='',
                )
                CounterSale_Temp.save()

                context ={
                "item_names":item_names,"serial_batch_1":serial_batch_1,"patient_registration":patient_registration,"CounterSale_Temp_1":CounterSale_Temp_1,
                'countersale_temp_otc':countersale_temp_otc,'gender':gender,'age':age,'mob_no':mob_no,'consultant_name':consultant_name,
                'consultant':consultant,'uhid':uhid,'patient_name':patient_name,'visit_id':visit_id,'panel':panel,'types_value':types_value
                }
                return render(request,"pharmacy/pharmacy_sale/acso_patient.html",context)

                # return HttpResponseRedirect("/add_counter_saleout_patient")

            if request.POST.get("otc_save_temp") == "otc_save_temp":
                item_id = request.POST.get("item_id1").split('.')
                batch = request.POST.get("batch1")
                patient_name=request.POST.get("patient_name1")
                consultant=request.POST.get("consultant1")
                consultant_name=request.POST.get("consultant_name1")
                mob_no=request.POST.get("mob_no1")
                age=request.POST.get("age1")
                gender=request.POST.get("gender1")
                panel=request.POST.get("panel1")
                types_value=request.POST.get("type1")
                CounterSale_Temp_otc = PS_CounterSale_Temp_OTC(
                    item_id_id=item_id[0],
                    batch_no=request.POST.get("batch1"),
                    expiry_date=request.POST.get("expiry1"),
                    mrp='',
                    qty=request.POST.get("qty1"),
                    rate=request.POST.get("rate1"),
                    before_disc_amount=request.POST.get("before_disc_amount1"),
                    discount=request.POST.get("discount1"),
                    amount=request.POST.get("amount1"),
                    status="pending",
                    moment_status="PS Entry",
                    reason='',
                )
                CounterSale_Temp_otc.save()

                context ={
                "item_names":item_names,"serial_batch_1":serial_batch_1,"patient_registration":patient_registration,"CounterSale_Temp_1":CounterSale_Temp_1,
                'countersale_temp_otc':countersale_temp_otc,'gender':gender,'age':age,'mob_no':mob_no,'consultant_name':consultant_name,
                'consultant':consultant,'patient_name':patient_name,'panel':panel,'types_value':types_value
                }
                return render(request,"pharmacy/pharmacy_sale/acso_patient.html",context)

            if request.POST.get("saved") == "saved":

                ps_temp = PS_CounterSale_Temp.objects.all()
                total_amount = 0
                for data in ps_temp:
                    total_qty = Stock_BatchWise_Mainstore.objects.filter(item_id_id=data.item_id_id).last()
                    Total_Qty = int(total_qty.total_qty) - int(data.qty)
                    grn = Stock_BatchWise_Mainstore.objects.filter(item_id_id=data.item_id_id,batch_no=data.batch_no).last()
                    inhand = int(grn.total_consume_qty) - int(data.qty)

                    total_amount += float(data.amount)

                    CounterSale_child = PS_CounterSale_child(
                        Op_sales_no=PSID,
                        sales_date=datetime.now(),
                        item_id_id=data.item_id_id,
                        batch_no=data.batch_no,
                        expiry_date=data.expiry_date,
                        mrp=data.mrp,
                        qty=data.qty,
                        rate=data.rate,
                        before_disc_amount=data.before_disc_amount,
                        discount=data.discount,
                        amount=data.amount,
                        total_qty=Total_Qty,
                        opening_balance=total_qty.total_qty,
                        status="",
                        moment_status="PS Entry",
                        reason="",
                        grn_consume_hand_qty = inhand,
                    )

                    CounterSale_child.save()

                    item_issue_child_1 = Item_Issue_ToSubStore_Child.objects.filter(item_id_id=data.item_id_id,serial_batch=data.batch_no).last()
                    if not item_issue_child_1:
                        avaliable = 0
                    else:
                        avaliable = item_issue_child_1.available_qty

                    total_qty.total_qty = Total_Qty
                    total_qty.save()

                    item_issue_child_1.available_qty = int(avaliable) - int(data.qty)
                    item_issue_child_1.save()

                    grn.total_consume_qty = inhand
                    grn.save()

                    request_store = request.store_id

                CounterSale_parent = PS_CounterSale_Parent(
                    Op_sales_no=PSID,
                    sales_date=datetime.now(),
                    uhid=request.POST.get("uhid"),
                    visit_id=request.POST.get("visit_id"),
                    store_id_id=request_store[0],
                    location_id_id=request.location,
                    patient_name=request.POST.get("patient_name"),
                    consultant_type=request.POST.get("consultant"),
                    consultant_name=request.POST.get("consultant_name"),
                    mobile=request.POST.get("mob_no"),
                    age=request.POST.get("age"),
                    gender=request.POST.get("gender"),
                    panel=request.POST.get("panel"),
                    type=request.POST.get("type"),
                    patient_type=request.POST.get("patient_type"),
                    opd_no='',
                    total_qty=0,
                    total_taxable_amount=total_amount,
                    p_status="",
                    reason="",
                )
                CounterSale_parent.save()
                PS_CounterSale_Temp.objects.all().delete()
                context ={
                "item_names":item_names,"serial_batch_1":serial_batch_1,"patient_registration":patient_registration,"CounterSale_Temp_1":CounterSale_Temp_1,
                'countersale_temp_otc':countersale_temp_otc,
                }
                return render(request,"pharmacy/pharmacy_sale/acso_patient.html",context)

#=========================== mantu code for pharmacy to opd billing ==============================

            opd_billing_button=request.POST.get("forward_opd_billing")
            if opd_billing_button == 'FORWARD_OPD_BILLING':
                id_uhid=request.session['ph_uhid']
                id_visit_id=request.session['ph_visit_id']
                CounterSale_parent = PS_CounterSale_Parent.objects.filter(uhid=id_uhid,visit_id=id_visit_id).last()
                pat_id=CounterSale_parent.Op_sales_no
                service_cat=ServiceCategory.objects.get(service_category__startswith='Medicine & Consumables')
                ser_name=ServiceChargeMaster.objects.filter(ward_type=service_cat.id).last()
                # CounterSale_child = PS_CounterSale_child.objects.filter(Op_sales_no=pat_id)
                print('ser_name==-----,',ser_name.service_id)
                OpdBillingTemper.objects.create(
                    uhid=id_uhid,
                    visit_no=id_visit_id,
                    service_name=f"{ser_name.service_id} {CounterSale_parent.Op_sales_no}",
                    rate=CounterSale_parent.total_taxable_amount,
                    net_ammount=CounterSale_parent.total_taxable_amount,
                    outstanding_amount='0',
                    receive_amount=CounterSale_parent.total_taxable_amount,
                    discount='0',
                    total_amount=CounterSale_parent.total_taxable_amount,
                    unit=CounterSale_parent.total_qty,
                    service_category=ser_name.ward_type,
                    service_sub_category=ser_name.ward_category,
                )
# ================================= END =================================================================

            if request.POST.get("otc_saved") == "otc_saved":
                ps_temp = PS_CounterSale_Temp_OTC.objects.all()
                total_amount = 0
                for data in ps_temp:
                    total_qty = Stock_BatchWise_Mainstore.objects.filter(item_id_id=data.item_id_id).last()
                    Total_Qty = int(total_qty.total_qty) - int(data.qty)
                    grn = Stock_BatchWise_Mainstore.objects.filter(item_id_id=data.item_id_id,batch_no=data.batch_no).last()
                    inhand = int(grn.total_consume_qty) - int(data.qty)

                    total_amount += float(data.amount)

                    CounterSale_child = PS_CounterSale_child(
                        Op_sales_no=PSID,
                        sales_date=datetime.now(),
                        item_id_id=data.item_id_id,
                        batch_no=data.batch_no,
                        expiry_date=data.expiry_date,
                        mrp=data.mrp,
                        qty=data.qty,
                        rate=data.rate,
                        before_disc_amount=data.before_disc_amount,
                        discount=data.discount,
                        amount=data.amount,
                        total_qty=Total_Qty,
                        opening_balance=total_qty.total_qty,
                        status="",
                        moment_status="PS Entry",
                        reason="",
                        grn_consume_hand_qty = inhand,
                    )

                    CounterSale_child.save()

                    item_issue_child_1 = Item_Issue_ToSubStore_Child.objects.filter(item_id_id=data.item_id_id,serial_batch=data.batch_no).last()
                    if not item_issue_child_1:
                        avaliable = 0
                    else:
                        avaliable = item_issue_child_1.available_qty

                    item_issue_child_1.available_qty = int(avaliable) - int(data.qty)
                    item_issue_child_1.save()

                    total_qty.total_qty = Total_Qty
                    total_qty.save()

                    grn.total_consume_qty = inhand
                    grn.save()

                CounterSale_parent = PS_CounterSale_Parent(
                    Op_sales_no=PSID,
                    sales_date=datetime.now(),
                    uhid='',
                    visit_id='',
                    store_id_id='3',
                    location_id_id='1',
                    patient_name=request.POST.get("patient_name1"),
                    consultant_type=request.POST.get("consultant1"),
                    consultant_name=request.POST.get("consultant_name1"),
                    mobile=request.POST.get("mob_no1"),
                    age=request.POST.get("age1"),
                    gender=request.POST.get("gender1"),
                    panel=request.POST.get("panel1"),
                    type=request.POST.get("type1"),
                    patient_type=request.POST.get("patient_type1"),
                    opd_no='',
                    total_qty=0,
                    total_taxable_amount=total_amount,
                    p_status="",
                    reason="",

                )
                CounterSale_parent.save()
                PS_CounterSale_Temp_OTC.objects.all().delete()
                context ={
                "item_names":item_names,"serial_batch_1":serial_batch_1,"patient_registration":patient_registration,"CounterSale_Temp_1":CounterSale_Temp_1,
                'countersale_temp_otc':countersale_temp_otc,
                }
                return render(request,"pharmacy/pharmacy_sale/acso_patient.html",context)
            if request.POST.get("prescription") == "prescription":
                request.session['uhid'] = request.POST.get('uhid')
                request.session['visit_id'] = request.POST.get('visit_id')

                return HttpResponseRedirect("/prescription_details")
            context ={
                "item_names":item_names,"serial_batch_1":serial_batch_1,"patient_registration":patient_registration,"CounterSale_Temp_1":CounterSale_Temp_1,
                'countersale_temp_otc':countersale_temp_otc,
            }

            return render(request,"pharmacy/pharmacy_sale/acso_patient.html",context)
        except Exception as error:
            return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def payment_detail_sale(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'add_counter_sales' in access.user_profile.screen_access:
        try:
            PSCounterSale_Parent = PS_CounterSale_Parent.objects.filter(bill_status='pending').last()
            print('PSCounterSale_Parent',PSCounterSale_Parent)
            if request.method=='POST':
                sale_no=request.POST.get('sale_no')
                amount=request.POST.get('bill_amt')
                mode_type=request.POST.get('mode_type')

                # ================== fields ===========
                # cash
                cash_paid_by=request.POST.get('cash_paid_by')
                cash_pay_amount=request.POST.get('cash_pay_amount')
                # m-pesa
                mpesa_paid_by=request.POST.get('mpesa_paid_by')
                mpesa_ref_no=request.POST.get('mpesa_ref_no')
                mpesa_card_holder_name=request.POST.get('mpesa_card_holder_name')
                mpesa_mobile_no=request.POST.get('mpesa_mobile_no')
                mpesa_pay_amount=request.POST.get('mpesa_pay_amount')
                # card
                card_ref_no=request.POST.get('card_ref_no')
                card_paid_by=request.POST.get('card_paid_by')
                card_pay_amount=request.POST.get('card_pay_amount')
                card_bank_no=request.POST.get('card_bank_no')

                if mode_type == 'cash':
                    PS_Sales_Payement_Detail.objects.create(
                            op_sale_no=sale_no,mode_type=mode_type,sale_date=datetime.now(),
                            paid_by=cash_paid_by,bill_amt=amount,paid_amount=cash_pay_amount,status=''
                    )
                    ps_parent = PS_CounterSale_Parent.objects.get(Op_sales_no=sale_no)
                    ps_parent.bill_status = 'bill_paid'
                    ps_parent.type = mode_type
                    ps_parent.save()
                elif mode_type == 'debit_credit_card':
                    PS_Sales_Payement_Detail.objects.create(
                            op_sale_no=sale_no,mode_type=mode_type,sale_date=datetime.now(),
                            paid_by=card_paid_by,bill_amt=amount,paid_amount=card_pay_amount,ref_number=card_ref_no,status='',bank_no=card_bank_no
                    )
                    ps_parent = PS_CounterSale_Parent.objects.get(Op_sales_no=sale_no)
                    ps_parent.bill_status = 'bill_paid'
                    ps_parent.type = mode_type
                    ps_parent.save()
                elif mode_type == 'm_pesa':
                    PS_Sales_Payement_Detail.objects.create(
                            op_sale_no=sale_no,mode_type=mode_type,sale_date=datetime.now(),
                            paid_by=mpesa_paid_by,bill_amt=amount,paid_amount=mpesa_pay_amount,ref_number=mpesa_ref_no,status='',card_holder_name=mpesa_card_holder_name,mobile_nummber=mpesa_mobile_no,
                    )
                    ps_parent = PS_CounterSale_Parent.objects.get(Op_sales_no=sale_no)
                    ps_parent.bill_status = 'bill_paid'
                    ps_parent.type = mode_type
                    ps_parent.save()
                elif mode_type == 'all':
                    status=''
                    if cash_pay_amount:
                        PS_Sales_Payement_Detail.objects.create(
                            op_sale_no=sale_no,mode_type=mode_type,sale_date=datetime.now(),
                            paid_by=cash_paid_by,bill_amt=amount,paid_amount=cash_pay_amount,status=status
                        )
                        ps_parent = PS_CounterSale_Parent.objects.get(Op_sales_no=sale_no)
                        ps_parent.bill_status = 'bill_paid'
                        ps_parent.type = mode_type
                        ps_parent.save()
                    if card_pay_amount:
                        PS_Sales_Payement_Detail.objects.create(
                                op_sale_no=sale_no,mode_type=mode_type,sale_date=datetime.now(),
                                paid_by=card_paid_by,bill_amt=amount,paid_amount=card_pay_amount,ref_number=card_ref_no,status=status,bank_no=card_bank_no
                        )
                        ps_parent = PS_CounterSale_Parent.objects.get(Op_sales_no=sale_no)
                        ps_parent.bill_status = 'bill_paid'
                        ps_parent.type = mode_type
                        ps_parent.save()
                    if mpesa_pay_amount:
                        PS_Sales_Payement_Detail.objects.create(
                                op_sale_no=sale_no,mode_type=mode_type,sale_date=datetime.now(),
                                bank_no=mpesa_paid_by,bill_amt=amount,paid_amount=mpesa_pay_amount,ref_number=mpesa_ref_no,status=status,card_holder_name=mpesa_card_holder_name,mobile_nummber=mpesa_mobile_no
                        )
                        ps_parent = PS_CounterSale_Parent.objects.get(Op_sales_no=sale_no)
                        ps_parent.bill_status = 'bill_paid'
                        ps_parent.type = mode_type
                        ps_parent.save()
                return HttpResponseRedirect('/add_counter_saleout_patient_preview')
            context={
                "PSCounterSale_Parent":PSCounterSale_Parent
            }
            return render(request,"pharmacy/pharmacy_sale/payment_detail_sale.html",context)
        except Exception as error:
            return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


@login_required(login_url='/user_login')
def prescription_details(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'add_counter_sales' in access.user_profile.screen_access:
        try:
            uhid = request.session['uhid']
            visit_id = request.session['visit_id']
            medicine_details = PreMedicine.objects.filter(uhid=uhid,visit_id=visit_id)
            patient_details = PatientsRegistrationsAllInOne.objects.get(uhid=uhid)
            visit_id = PatientVisitMains.objects.filter(uhid=uhid).last()
            batch_nos =[]
            qty = []
            for data in medicine_details:
                if data.dosage == 'BD':
                    quantity = data.no_of_days * 2
                elif data.dosage == 'TD':
                    quantity = data.no_of_days * 3
                elif data.dosage == 'OD':
                    quantity = data.no_of_days * 1
                qty.append(quantity)
                get_batch = Stock_BatchWise_Mainstore.objects.exclude(available_qty=0).filter(item_id_id=data.medicine).order_by('expiry_date')
                batch_no = []
                for data in get_batch:
                    batch_no.append(data.batch_no)
                batch_nos.append(batch_no)
            medicine_detail = zip(medicine_details,batch_nos,qty)
            Op_sales_no = PS_CounterSale_Parent.objects.all().count()
            today = date.today()
            today = today.strftime("%d%m%y")
            PSID = 'PS'+today+'000'+str(Op_sales_no)
            if request.method =='POST':
                item_id = request.POST.getlist('item_id')
                batch_no = request.POST.getlist('batch')
                expiry_date = request.POST.getlist('expiry_date')
                qty = request.POST.getlist('qty')
                rate = request.POST.getlist('rate')
                discount = request.POST.getlist('discount')
                before_disc_amount = request.POST.getlist('before_disc_amount')
                amount = request.POST.getlist('amount')
                total_amount = 0
                for data in range(len(rate)):
                    total_qty = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data]).last()
                    Total_Qty = int(total_qty.total_qty) - int(data.qty)
                    grn = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_id[data],batch_no=batch_no[data]).last()
                    inhand = int(grn.total_consume_qty) - int(qty[data])

                    total_amount += float(amount[data])

                    CounterSale_child = PS_CounterSale_child(
                        Op_sales_no=PSID,
                        sales_date=datetime.now(),
                        item_id_id=item_id[data],
                        batch_no=batch_no[data],
                        expiry_date=expiry_date[data],
                        mrp='',
                        qty=qty[data],
                        rate=rate[data],
                        before_disc_amount=before_disc_amount[data],
                        discount=discount[data],
                        amount=amount[data],
                        total_qty=Total_Qty,
                        opening_balance=total_qty.total_qty,
                        status="",
                        moment_status="PS Entry",
                        reason="",
                        grn_consume_hand_qty = inhand,
                        bill_status=''
                    )

                    CounterSale_child.save()

                    item_issue_child_1 = Item_Issue_ToSubStore_Child.objects.filter(item_id_id=item_id[data],serial_batch=batch_no[data]).last()
                    if not item_issue_child_1:
                        avaliable = 0
                    else:
                        avaliable = item_issue_child_1.available_qty

                    item_issue_child_1.available_qty = int(avaliable) - int(qty[data])
                    item_issue_child_1.save()

                    total_qty.total_qty = Total_Qty
                    total_qty.save()

                    grn.total_consume_qty = inhand
                    grn.save()

                CounterSale_parent = PS_CounterSale_Parent(
                    Op_sales_no=PSID,
                    sales_date=datetime.now(),
                    uhid=request.POST.get("uhid"),
                    visit_id=request.POST.get("visit_id"),
                    store_id_id='3',
                    location_id_id='1',
                    patient_name=request.POST.get("patient_name"),
                    consultant_type=request.POST.get("consultant"),
                    consultant_name=request.POST.get("consultant_name"),
                    mobile=request.POST.get("mob_no"),
                    age=request.POST.get("age"),
                    gender=request.POST.get("gender"),
                    panel=request.POST.get("panel"),
                    type=request.POST.get("type"),
                    patient_type='',
                    opd_no='',
                    total_qty=0,
                    total_taxable_amount=total_amount,
                    p_status="",
                    reason="",
                    bill_status=''
                )
                CounterSale_parent.save()
            context = {
                'medicine_details':medicine_detail,
                'patient_details' :patient_details,
                'visit_id' : visit_id,
            }
            return render(request,"pharmacy/pharmacy_sale/prescription_details.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

def search_batchno(request):
    try:
        item_id = request.POST.get("item_id").split('.')
        get_batch = Item_Issue_ToSubStore_Child.objects.exclude(available_qty=0).filter(item_id_id=item_id[0]).order_by('expiry_date')
        return JsonResponse(list(get_batch.values('serial_batch')),safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def searchbatchno_mainstore(request):
    try:
        item_id = request.POST.get("item_id").split('.')
        get_batch = Stock_BatchWise.objects.exclude(available_qty=0).filter(item_id_id=item_id[0]).order_by('expiry_date')
        return JsonResponse(list(get_batch.values('batch_no')),safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def add_count_sale_js(request):
    try:
        item_name=request.POST.get("item_id")
        serial_batch=request.POST.get("serial_batch")
        batch_no = Item_Issue_ToSubStore_Child.objects.filter(item_id_id=item_name[0],serial_batch=serial_batch).last()
        expiry=str(batch_no.expiry_date)
        my_dict=json.dumps({
            'expiry_date': expiry,
            "rate": batch_no.rate,
        })
        data=eval(my_dict)
        return JsonResponse(data, safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def status_update_to_PS(request):
    try:
        bill_generate = request.POST.get("values")
        ps_parent = PS_CounterSale_Parent.objects.all().last()
        ps_parent.bill_status = "Bill Generated"
        ps_parent.save()
        PS_child = PS_CounterSale_child.objects.filter(Op_sales_no=ps_parent.Op_sales_no)
        for data in PS_child:
            data.bill_status = "Bill Generated"
            data.save()
        return JsonResponse(data,safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def add_counter_saleout_patient_preview(request):
    try:
        PSCounterSale_Parent = PS_CounterSale_Parent.objects.all().last()
        PSCounterSale_child = ''
        if PSCounterSale_Parent:
            PSCounterSale_child = PS_CounterSale_child.objects.filter(Op_sales_no=PSCounterSale_Parent.Op_sales_no)
        context={
            "PSCounterSale_Parent":PSCounterSale_Parent,"PSCounterSale_child":PSCounterSale_child
        }
        return render(request,"pharmacy/pharmacy_sale/acso_patient_preview.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})


def sales_return_from_OP_invoice(request):
    sales_return = PS_sales_return_Parent.objects.all().last()
    ps_sale_parent = PS_CounterSale_Parent.objects.filter(uhid=sales_return.uhid).last()
    print(ps_sale_parent)
    sales_return_child = PS_sales_return_Child.objects.filter(sales_return_id=sales_return.sales_return_id,)

    context={
        "sales_return_child":sales_return_child,"ps_sale_parent":ps_sale_parent
    }
    return render(request,"pharmacy/pharmacy_sale/sale_return_invoice.html",context)

def status_update_to_PS(request):
    bill_generate = request.POST.get("values")
    ps_parent = PS_CounterSale_Parent.objects.all().last()
    ps_parent.bill_status = "Bill Generated"
    ps_parent.save()
    PS_child = PS_CounterSale_child.objects.filter(Op_sales_no=ps_parent.Op_sales_no)
    for data in PS_child:
        data.bill_status = "Bill Generated"
        data.save()
    return JsonResponse(data,safe=False)

def status_update_to_PSR(request):
    forwardtiOPD = request.POST.get("values")
    if forwardtiOPD == "Forward to OPD":
        ps_parent = PS_CounterSale_Parent.objects.all().last()
        ps_parent.bill_status = "Forward to OPD"
        ps_parent.save()
        PS_child = PS_CounterSale_child.objects.filter(Op_sales_no=ps_parent.Op_sales_no)
        for data in PS_child:
            data.bill_status = "Forward to OPD"
            data.save()

    data="hello World"
    return JsonResponse(data,safe=False)

def get_patientregistration_js(request):
    patient_name=request.POST.get("patient_name").split('.')
    patient_registration = PatientsRegistrationsAllInOne.objects.get(id=patient_name[0])
    visit_id = PatientVisitMains.objects.filter(uhid=patient_registration.uhid).last()
    my_dict=json.dumps({
        'uhid': patient_registration.uhid,
        "mobile": patient_registration.mobile_number,
        'age': patient_registration.age,
        "gender": patient_registration.gender,
        'visit_id':visit_id.visit_id,
        'name': f'{patient_registration.first_name} {patient_registration.middle_name} {patient_registration.last_name}',
    })
    data=eval(my_dict)
    return JsonResponse(data, safe=False)

@login_required(login_url='/user_login')
def sales_return_from_OP(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'sales_return' in access.user_profile.screen_access:
        try:
            item_master=Inventory_ItemMaster.objects.all()
            submit_btn =  request.POST.get("submit_btn")

            if submit_btn == "submit_btn":
                opd_no = request.POST.get("opd_no")
                items = request.POST.get("item_name")
                request.session['OPD_No'] = opd_no
                request.session['items_name'] = items

                if request.session['OPD_No'] or request.session['OPD_No'] and request.session['items_name']:
                    return HttpResponseRedirect("/sales_return_from_OP_1")
            context = {
                "item_master":item_master,'access':access
            }
            return render(request,"pharmacy/pharmacy_sale/sale_return_op.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


@login_required(login_url='/user_login')
def sales_return_from_OP_1(request):
    OP_no = request.session['OPD_No']
    items = request.session['items_name']

    if OP_no and not items:
        CounterSale_parent=PS_CounterSale_Parent.objects.get(Op_sales_no=OP_no)
        CounterSale_child = PS_CounterSale_child.objects.filter(Op_sales_no=OP_no)
        sales_return_no_1 = PS_sales_return.objects.filter(sales_no = OP_no)
        total_amount = [data.return_amount for data in sales_return_no_1]
        Total_Amount = 0
        for data1 in total_amount:
            Total_Amount = float(Total_Amount) + float(data1)

        save_btn = request.POST.get("save_btn")
        if request.method == "POST":
            if save_btn == "save_btn":
                sales_return_no=PS_sales_return.objects.all().count()
                today=date.today()
                today=today.strftime("%d%m%y")
                PSRID='PSR'+today+'000'+str(sales_return_no)
                sales_no = request.POST.getlist("sales_no")
                item_1 = request.POST.getlist("item_id")
                batch = request.POST.getlist("batch_no")
                reason_1 = request.POST.get("reason")
                discount_1 = request.POST.getlist("discount")
                sale_qty_1 = request.POST.getlist("qty")
                return_qty_1 = request.POST.getlist("return_qty")
                sale_amount_1 = request.POST.getlist("amount")
                return_amount_1 = request.POST.getlist("return_amount")
                rate_1 = request.POST.getlist("rate")

                for data in range(len(sale_qty_1)):
                    sale_return_table = PS_sales_return(
                        sales_no = sales_no[data],
                        sales_return_id =PSRID,
                        sales_date =CounterSale_parent.sales_date,
                        sales_return_date =datetime.now(),
                        item_id = item_1[data],
                        sale_qty = sale_qty_1[data],
                        return_qty = return_qty_1[data],
                        sale_amount = sale_amount_1[data],
                        return_amount = return_amount_1[data],
                        rate = rate_1[data],
                        discount = discount_1[data],
                        reason = reason_1,
                        status ="",
                    )
                    if return_qty_1[data] and return_amount_1[data] != "":
                        sale_return_table.save()

                        CounterSale_child_1 = PS_CounterSale_child.objects.filter(Op_sales_no=OP_no,item_id=item_1[data]).last()
                        CounterSale_child_1.reason = reason_1[data]
                        CounterSale_child_1.status = "Returned"
                        CounterSale_child_1.save()

                        # minius avalailable qty from item issue child
                        item_issue_child_1 = Item_Issue_Child.objects.filter(item_id=item_1[data],serial_batch=batch[data]).last()
                        item_issue_child_1.available_qty = item_issue_child_1.available_qty + return_qty_1[data]
                        item_issue_child_1.save()


                return HttpResponseRedirect("/sales_return_from_OP_1")
    else:
        CounterSale_parent=PS_CounterSale_Parent.objects.get(Op_sales_no=OP_no)
        CounterSale_child = PS_CounterSale_child.objects.filter(Op_sales_no=OP_no,item_id = items)
        save_btn = request.POST.get("save_btn")
        if request.method == "POST":
            if save_btn == "save_btn":
                sales_return_no=PS_sales_return.objects.all().count()
                sales_return_no_1 = PS_sales_return.objects.filter(sales_no = OP_no,item_id=items)
                total_amount = [data.return_amount for data in sales_return_no_1]
                Total_Amount = 0
                for data1 in total_amount:
                    Total_Amount = float(Total_Amount) + float(data1)


                today=date.today()
                today=today.strftime("%d%m%y")
                PSRID='PSR'+today+'000'+str(sales_return_no)
                sales_no = request.POST.getlist("sales_no")
                item_1 = request.POST.getlist("item_id")
                reason_1 = request.POST.get("reason")
                discount_1 = request.POST.getlist("discount")
                sale_qty_1 = request.POST.getlist("qty")
                return_qty_1 = request.POST.getlist("return_qty")
                sale_amount_1 = request.POST.getlist("amount")
                return_amount_1 = request.POST.getlist("return_amount")
                rate_1 = request.POST.getlist("rate")

                for data in range(len(sale_qty_1)):
                    sale_return_table = PS_sales_return(
                        sales_no = sales_no[data],
                        sales_return_id =PSRID,
                        sales_date =CounterSale_parent.sales_date,
                        sales_return_date =datetime.now(),
                        item_id = item_1[data],
                        sale_qty = sale_qty_1[data],
                        return_qty = return_qty_1[data],
                        sale_amount = sale_amount_1[data],
                        return_amount = return_amount_1[data],
                        rate = rate_1[data],
                        discount = discount_1[data],
                        reason = reason_1,
                        status ="",
                    )
                    if return_qty_1[data] and return_amount_1[data] != "":
                        sale_return_table.save()
                        CounterSale_child_1 = PS_CounterSale_child.objects.filter(Op_sales_no=OP_no,item_id=item_1[data]).last()
                        CounterSale_child_1.reason = reason_1[data]
                        CounterSale_child_1.status = "Returned"
                        CounterSale_child_1.save()

                        # minius avalailable qty from item issue child
                        item_issue_child_1 = Item_Issue_Child.objects.filter(item_id=item_1[data],serial_batch=batch[data]).last()
                        item_issue_child_1.available_qty = item_issue_child_1.available_qty + return_qty_1[data]
                        item_issue_child_1.save()
                return HttpResponseRedirect("/sales_return_from_OP_1")

    context = {
        "CounterSale_parent":CounterSale_parent,"CounterSale_child":CounterSale_child,"Total_Amount":Total_Amount
    }


    return render(request,"pharmacy/pharmacy_sale/sales_return_OP_1.html",context)

@login_required(login_url='/user_login')
def department_consump_search(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'department_consumption' in access.user_profile.screen_access:
        try:
            item_name = Inventory_ItemMaster.objects.all()
            item_category = ItemCategoryMaster.objects.all()
            location_detail=LocationMaster.objects.all()
            store_detail=StoreMaster.objects.filter(store_type=2)
            search_butn = request.POST.get("submit_btn")
            if search_butn == "submit_btn":
                # Item_name = request.POST.get("item_name").split('.')

                request.session['item_category'] = request.POST.get("item_category")
                request.session['store_id'] =  request.POST.get("store_id")
                request.session['location_id'] = request.POST.get("location_id")

                return HttpResponseRedirect("/department_consump")

            context ={
                "item_name":item_name,
                'location_detail':location_detail,
                'store_detail':store_detail,
                'item_category':item_category,
            }
            return render(request,"pharmacy/department_consump_search.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def department_consump(request):
    try:
        item_category = request.session['item_category']
        store_id = request.session['store_id']
        location_id = request.session['location_id']
        if item_category != "" and store_id != "" and location_id != "":
            store_type = StoreMaster.objects.get(id=store_id)
            item_master = Inventory_ItemMaster.objects.filter(item_category=item_category)
            item_ids = [data.id for data in item_master]
            item_list = []
            item_list1 = []
            # if store_type.store_type == '1':
            #     item_list.append(Stock_BatchWise_Mainstore.objects.filter(location_id_id=location_id,store_id_id=store_id,item_id__in=item_ids))
            if store_type.store_type == '2':
                item_issue_p = Item_Issue_ToSubStore_Parent.objects.filter(location_id_id=location_id,received_store_id=store_id)
                for data in item_issue_p:
                    item_list1.append(Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data.item_issue_no,item_id__in=item_ids))

        single_sub = request.POST.get("save_item_consume")
        department_consumption =Department_Consumption.objects.all().count()
        today=date.today()
        today=today.strftime("%d%m%y")
        DCID='PSR'+today+'000'+str(department_consumption)

        # item_issue_detail = zip(item_issue_child,store_name,store_id)

        context = {
            # "item_issue_child":item_issue_detail
            'item_list':item_list,
            'item_list1':item_list1,
            'store_id':store_id,
            'store_type':store_type,
        }
        return render(request,"pharmacy/department_consump.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def PO_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'po_report' in access.user_profile.screen_access:
        try:
            PO_parent =PurchaseOrder_Parent.objects.all()
            search_btn = request.POST.get("submit_btn")
            if search_btn == "submit_btn":
                Po_id = request.POST.get("PO_no")
                PO_parent_1 = PurchaseOrder_Parent.objects.filter(PO_id=Po_id.strip())
                context ={
                    "PO_parent_1":PO_parent_1
                }
                return render(request,"pharmacy/reports/PO_report.html",context)
            context ={
                "PO_parent":PO_parent
            }
            return render(request,"pharmacy/reports/PO_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def PO_report_pk(request,pk):
    try:
        po_child = ''
        po_child = PurchaseOrder_Child.objects.filter(PO_Id=pk)
        context ={
        "po_child":po_child
        }
        return render(request,"pharmacy/reports/ipo_report_pk.html",context)
    except Exception as error:
           return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def batchwise_report(request):
        store_id = StoreMaster.objects.all()
        item_cat = ItemCategoryMaster.objects.all()
        item_subcat = ItemsubcategoryMaster.objects.all()
        item_name = Inventory_ItemMaster.objects.all()
        mainstore=''
        items=''
        item_cate_name_2=''
        item_subcate_name_2 = ''
        item_shortcode_2=''
        if request.POST.get("search") == "search":
            store_id_1 =request.POST.get("store_id")
            item_cate =request.POST.get("item_cate")
            item_subcate =request.POST.get("item_subcate")
            item_name_1 =request.POST.get("item_name").split('.')
            store_type = StoreMaster.objects.get(id=store_id_1)
            if store_id_1 and item_cate:
                item_master = Inventory_ItemMaster.objects.filter(item_category=item_cate)
                items = [data.id for data in item_master]

                if store_type.store_type == '0':
                    mainstore = []
                    mainstores = Stock_BatchWise.objects.filter(item_id__in=items,store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)
                elif store_type.store_type == '1':
                    mainstore = []
                    mainstores = Stock_BatchWise_Mainstore.objects.filter(item_id__in=items,store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise_Mainstore.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)

                elif store_type.store_type == '2':
                    issue_parent = Item_Issue_ToSubStore_Parent.objects.filter(received_store_id=store_id_1)
                    item_issue_no = [data.item_issue_no for data in issue_parent]
                    substore = []
                    substores = Item_Issue_ToSubStore_Child.objects.exclude(available_qty=0).filter(item_id__in=items,item_issue_no__in=item_issue_no).values('serial_batch').distinct()
                    for data in substores:
                        substore.append(Item_Issue_ToSubStore_Child.objects.filter(serial_batch=data['serial_batch']).last())
                    # substore_1 = zip(substore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"substore":substore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)

            elif store_id_1 and item_subcate:
                item_master = Inventory_ItemMaster.objects.filter(item_subcategory=item_subcate)
                items = [data.id for data in item_master]

                if store_type.store_type == '0':
                    mainstore = []
                    mainstores = Stock_BatchWise.objects.filter(item_id__in=items,store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)
                elif store_type.store_type == '1':
                    mainstore = []
                    mainstores = Stock_BatchWise_Mainstore.objects.filter(item_id__in=items,store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise_Mainstore.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)

                elif store_type.store_type == '2':
                    issue_parent = Item_Issue_ToSubStore_Parent.objects.filter(received_store_id=store_id_1)
                    item_issue_no = [data.item_issue_no for data in issue_parent]
                    substore = []
                    substores = Item_Issue_ToSubStore_Child.objects.exclude(available_qty=0).filter(item_id__in=items,item_issue_no__in=item_issue_no).values('serial_batch').distinct()
                    for data in substores:
                        substore.append(Item_Issue_ToSubStore_Child.objects.filter(serial_batch=data['serial_batch']).last())
                    # substore_1 = zip(substore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"substore":substore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)

            elif store_id_1 and item_name_1[0]:
                if store_type.store_type == '0':
                    mainstore = []
                    mainstores = Stock_BatchWise.objects.filter(item_id_id=item_name_1[0],store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)
                elif store_type.store_type == '1':
                    mainstore = []
                    mainstores = Stock_BatchWise_Mainstore.objects.filter(item_id_id=item_name_1[0],store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise_Mainstore.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)

                elif store_type.store_type == '2':
                    issue_parent = Item_Issue_ToSubStore_Parent.objects.filter(received_store_id=store_id_1)
                    item_issue_no = [data.item_issue_no for data in issue_parent]
                    substore = []
                    substores = Item_Issue_ToSubStore_Child.objects.exclude(available_qty=0).filter(item_id_id=item_name_1[0],item_issue_no__in=item_issue_no).values('serial_batch').distinct()
                    for data in substores:
                        substore.append(Item_Issue_ToSubStore_Child.objects.filter(serial_batch=data['serial_batch']).last())
                    # substore_1 = zip(substore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"substore":substore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)
            elif store_id_1:
                if store_type.store_type == '0':
                    mainstore = []
                    mainstores = Stock_BatchWise.objects.filter(store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)
                elif store_type.store_type == '1':
                    mainstore = []
                    mainstores = Stock_BatchWise_Mainstore.objects.filter(store_id_id=store_id_1).values('batch_no').distinct()
                    for data in mainstores:
                        mainstore.append(Stock_BatchWise_Mainstore.objects.filter(batch_no=data['batch_no']).last())
                    # records = zip(mainstore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"mainstore":mainstore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)

                elif store_type.store_type == '2':
                    issue_parent = Item_Issue_ToSubStore_Parent.objects.filter(received_store_id=store_id_1)
                    item_issue_no = [data.item_issue_no for data in issue_parent]
                    substore = []
                    substores = Item_Issue_ToSubStore_Child.objects.exclude(available_qty=0).filter(item_issue_no__in=item_issue_no).values('serial_batch').distinct()
                    for data in substores:
                        substore.append(Item_Issue_ToSubStore_Child.objects.filter(serial_batch=data['serial_batch']).last())
                    # substore_1 = zip(substore,item_subcate_name_2,item_cate_name_2,item_shortcode_2)
                    context = {
                        "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name,"substore":substore
                    }
                    return render(request,"pharmacy/reports/batchwise_report.html",context)
        context = {
            "store_id":store_id,"item_cat":item_cat,"item_subcat":item_subcat,"item_name":item_name
        }
        return render(request,"pharmacy/reports/batchwise_report.html",context)
  

def file_upload(request):
    try:
        if request.method == 'POST' and request.FILES['file']:
            file = request.FILES['file']
            stock_entry_parent=StockEntry_Parent.objects.all().last()
            stock_entry_parent.invoice_upload=file
            stock_entry_parent.save()
            data="success"
            return JsonResponse(data,safe=False)
        else:
            print("unsuccess")
            data="success"
            return JsonResponse(data,safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})


def PO_approval_sendmail(request):
    try:
        if request.method == 'POST' and request.FILES['file']:
            records=PurchaseOrder_Parent.objects.latest('PO_id')
            po_no=records.PO_id
            vendor_id=records.vendar_id_id
            vendor_master = VendorMaster.objects.get(id=vendor_id)
            vendor_email=vendor_master.email
            file = request.FILES['file']
            subject="Purchase order is approved"
            message="Purchase order is approved message"
            mail1 = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [vendor_email])
            mail1.attach(file.name, file.read(), file.content_type)
            mail1.send()
            data="Mail send successfully"
            return JsonResponse(data,safe=False)
        else:
            print("unsuccess")
            data="successfully cannot send successfully"
            return JsonResponse(data,safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def po_supplier_wise_search(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'po_supplier_wise_report' in access.user_profile.screen_access:
        try:
            records=VendorMaster.objects.all()
            if request.method=='POST':
                vendar_id=request.POST.get('vendor_id')
                from_date=request.POST.get('from_date')
                to_date=request.POST.get('to_date')

                if vendar_id != "Select":
                    return HttpResponseRedirect(f"po_supplier_wise_report/{vendar_id}")
                elif from_date and to_date:
                    record=PurchaseOrder_Parent.objects.filter(PO_datetime__range=[from_date,to_date])
                    child=[]
                    parent=[]
                    for data in record:
                        da=PurchaseOrder_Child.objects.filter(PO_Id=data.PO_id)
                        child.append(da)
                        parent.append(data)
                    records=zip(child,parent)
            context = {
                "records":records,'access':access
            }
            return render(request,"pharmacy/reports/po_supplier_wise_search.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def po_supplier_wise_report(request,pk):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'po_supplier_wise_report' in access.user_profile.screen_access:
        try:
            record=PurchaseOrder_Parent.objects.filter(vendar_id=pk)
            child=[]
            parent=[]
            for data in record:
                da=PurchaseOrder_Child.objects.filter(PO_Id=data.PO_id)
                child.append(da)
                parent.append(data)
            records=zip(child,parent)
            context = {
                "records":records
            }
            return render(request,"pharmacy/reports/po_supplier_wise_report.html",context)
        except Exception as error:
            return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def po_aging_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'po_aging_report' in access.user_profile.screen_access:
        try:
            vendor = VendorMaster.objects.all()
            records = PurchaseOrder_Parent.objects.extra(select={
                'vendor_name':'Select vendor_name from testapp_vendormaster where id=testapp_purchaseorder_parent.vendar_id_id',
            }).filter(approval_status='pending')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            vendor_id = request.POST.get('vendor_id')
            if from_date and to_date and vendor_id:
                records = PurchaseOrder_Parent.objects.filter(PO_datetime__range=[from_date,to_date],vendar_id_id=vendor_id,approval_status='pending')
            elif from_date and to_date:
                records = PurchaseOrder_Parent.objects.filter(PO_datetime__range=[from_date,to_date],approval_status='pending')
            elif vendor_id:
                records = PurchaseOrder_Parent.objects.filter(vendar_id_id=vendor_id,approval_status='pending')
            context = {
                "records":records,'vendor':vendor
            }
            return render(request,"pharmacy/reports/po_aging_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def po_item_details_report(request,pk):
    try:
        records = PurchaseOrder_Child.objects.filter(PO_Id=pk)
        context = {
            "records":records
        }
        return render(request,"pharmacy/reports/po_item_details_report.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def item_issue_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_issuse_report' in access.user_profile.screen_access:
        try:
            from_stores = StoreMaster.objects.filter(store_type__in=[0,1])
            to_stores = StoreMaster.objects.filter(store_type__in=[1,2])
            issue_detail = ''
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                from_store =request.POST.get('from_store')
                to_store = request.POST.get('to_store')
                from_store_type = StoreMaster.objects.get(id=from_store)
                to_store_type = StoreMaster.objects.get(id=to_store)
                # if from_store and to_store and from_date and to_date:
                if from_store_type.store_type == '0' and to_store_type.store_type == '1':
                    issue_detail = Item_Issue_Parent.objects.filter(received_store=to_store,item_issue_date__range=[from_date,to_date],issued_store=from_store)
                elif from_store_type.store_type == '1' and to_store_type.store_type == '2':
                    issue_detail = Item_Issue_ToSubStore_Parent.objects.filter(received_store=to_store,item_issue_date__range=[from_date,to_date],issued_store=from_store)
                # elif from_date and to_date:
                #     issue_detail = Item_Issue_Parent.objects.filter(item_issue_date_date_range=[from_date,to_date])
                # elif to_store:
                #     issue_detail = Item_Issue_Parent.objects.filter(received_store=to_store)
            context = {
                'from_stores': from_stores,
                'to_stores' : to_stores,
                'issue_detail' :issue_detail
            }
            return render(request,"pharmacy/reports/item_issue_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

def item_issue_report_details(request,pk):
    item_issue_detail = Item_Issue_Child.objects.filter(item_issue_no=pk)
    context ={
    'item_issue_detail' : item_issue_detail,
    }
    return render(request,"pharmacy/reports/issued_item_detail.html",context)

def item_issue_details(request,pk):
    try:
        issue_detail = Item_Issue_Child.objects.filter(item_issue_no=pk)
        context = {
                'issue_detail' :issue_detail
            }
        return render(request,"pharmacy/reports/item_issue_details.html",context)
    except Exception as error:
          return render(request,'error.html',{'error':error})


@login_required(login_url='/user_login')
def item_return_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_return_report' in access.user_profile.screen_access:
        try:
            store_detail1 = StoreMaster.objects.filter(store_type=2)
            store_detail = StoreMaster.objects.all()
            main_store = StoreMaster.objects.filter(store_type=1)
            return_detail = ''
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                from_store = request.POST.get('from_store')
                to_store = request.POST.get('to_store')
                if from_store and to_store and from_date and to_date:
                    return_detail = Item_Return_Parent.objects.extra(select={
                        'reason':'Select reason from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'batch_no':'Select batch_no from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'item_id':'Select item_id_id from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'return_qty':'Select return_qty from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'expiry_date':'Select expiry_date from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                    }).filter(return_store=from_store,receiving_store=to_store,return_date__date__range=[from_date,to_date])

                elif from_date and to_date:
                    return_detail = Item_Return_Parent.objects.extra(select={
                        'reason':'Select reason from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'batch_no':'Select batch_no from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'item_id':'Select item_id_id from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'return_qty':'Select return_qty from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'expiry_date':'Select expiry_date from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                    }).filter(return_date__date__range=[from_date,to_date])
                elif from_store and to_store:
                    return_detail = Item_Return_Parent.objects.extra(select={
                        'reason':'Select reason from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'batch_no':'Select batch_no from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'item_id':'Select item_id_id from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'return_qty':'Select return_qty from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                        'expiry_date':'Select expiry_date from testapp_item_return_child where item_return_no=testapp_item_return_parent.item_return_no',
                    }).filter(return_store=from_store,receiving_store=to_store)
            item_name=[]
            for data in return_detail:
                item_name.append(Inventory_ItemMaster.objects.get(id=data.item_id).item_name)
            records = zip(return_detail,item_name)
            context = {
                'store_detail': store_detail,
                'main_store' : main_store,
                'return_detail' :return_detail,
                'store_detail1':store_detail1,
                "records":records
            }
            return render(request,"pharmacy/reports/item_return_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def op_sale_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'op_sales_report' in access.user_profile.screen_access:
        try:
            sale_detail=''
            item_detail = ''
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                sale_detail = PS_CounterSale_Parent.objects.filter(sales_date__range=[from_date,to_date])
            context ={
                'sale_detail' : sale_detail,
            }
            return render(request,"pharmacy/reports/op_sale_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')


def op_sale_report_details(request,pk):
    try:
        item_detail = PS_CounterSale_child.objects.filter(Op_sales_no=pk)
        context ={
        'item_detail' : item_detail,
        }
        return render(request,"pharmacy/reports/opsale_item_list.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')
def op_sale_return_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'op_sales_return_report' in access.user_profile.screen_access:
        try:
            sale_return_detail=''
            item_detail = ''
            view_btn = request.POST.get('view_btn')
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                sale_return_detail = PS_sales_return.objects.filter(sales_return_date__date__range=[from_date,to_date])

            if view_btn == 'view_btn':
                return_no = request.POST.get('return_no')
                item_detail = PS_sales_return.objects.extra(select={
                    'item_name':'Select item_name from testapp_inventory_itemmaster where id=testapp_ps_countersale_child.item_id',
                    }).filter(sales_return_id=return_no)
                context ={
                'item_detail' : item_detail,
                }
                return render(request,"pharmacy/reports/opsale_return_itemlist.html",context)

            context ={
                'sale_return_detail' : sale_return_detail,
            }
            return render(request,"pharmacy/reports/op_sale_return_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def vendor_payment_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'vendor_paymet_report' in access.user_profile.screen_access:
        try:
            payment_detail=''
            vendor_detail = VendorMaster.objects.all()

            if request.method == 'POST':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                vendor_id = request.POST.get('vendor_id')

                if from_date and to_date and vendor_id == "Select":
                    payment_detail = Vendor_Payment.objects.filter(payment_datetime__range=[from_date,to_date])
                elif vendor_id !="Select"  and from_date and to_date:
                    payment_detail = Vendor_Payment.objects.filter(payment_datetime__range=[from_date,to_date],vendor_id_id=vendor_id)
                elif vendor_id != "Select":
                    payment_detail = Vendor_Payment.objects.filter(vendor_id_id=vendor_id)

            context ={
                'payment_detail' : payment_detail,
                'vendor_detail' : vendor_detail,
            }
            return render(request,"pharmacy/reports/vendor_payment_report.html",context)

        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def expiry_item_list_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'expiry_item_list_report' in access.user_profile.screen_access:
        try:
            item_detail =''
            issue_detail =''
            main_store = ''
            sub_store = ''
            supplier_name=''
            dept_detail = StoreMaster.objects.all()
            if request.method == 'POST':
                main_store = StoreMaster.objects.filter(store_type=1).first()
                sub_store = StoreMaster.objects.filter(store_type=2)
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                dept_id = request.POST.get('dept_id')

                if dept_id != "select" and not from_date:
                    dept_name = StoreMaster.objects.get(id=dept_id)
                    dept_name_1=dept_name.store_name
                    dept_id_1=dept_name.main_store
                    item_parent = StockEntry_Parent.objects.filter(store_id=dept_id)
                    item_parent_GRN_id = [data.GRN_id for data in item_parent]
                    supplier_name = [data.vendar_id for data in item_parent]
                    item_detail = StockEntry_Child.objects.filter(GRN_id__in=item_parent_GRN_id)
                    issue_parent = Item_Issue_Parent.objects.filter(Q(received_store=dept_name_1) or Q(issued_store=dept_id_1))
                    issue_detail = Item_Issue_Child.objects.filter(item_issue_no__in=issue_parent_GRN_id)

                elif from_date and to_date and dept_id == "select":
                    item_detail = StockEntry_Child.objects.filter(GRN_datetime__range=[from_date,to_date])
                    item_parent = StockEntry_Parent.objects.filter(GRN_datetime__range=[from_date,to_date])
                    supplier_name = [data.vendar_id for data in item_parent]
                    issue_detail = Item_Issue_Child.objects.filter(item_issue_date__range=[from_date,to_date])

                elif from_date and to_date and dept_id != "select":
                    dept_name = StoreMaster.objects.get(id=dept_id)
                    dept_name_1=dept_name.id
                    dept_id_1=dept_name.store_type
                    item_parent = StockEntry_Parent.objects.filter(store_id_id=dept_id)
                    supplier_name = [data.vendar_id for data in item_parent]
                    item_parent_GRN_id = [data.GRN_id for data in item_parent]
                    item_detail = StockEntry_Child.objects.filter(GRN_datetime__range=[from_date,to_date],GRN_id__in=item_parent_GRN_id)
                    issue_parent = Item_Issue_Parent.objects.filter(Q(received_store_id=dept_name_1) or Q(issued_store_id=dept_id_1))
                    issue_parent_GRN_id = [data.item_issue_no for data in issue_parent]
                    issue_detail = Item_Issue_Child.objects.filter(item_issue_date__range=[from_date,to_date],item_issue_no__in=issue_parent_GRN_id)

            item_details = zip(supplier_name,[main_store],[item_detail])
            issue_details = zip(sub_store,[issue_detail])
            context ={
                'issue_details' : issue_details,
                'item_details' : item_details,
                'dept_detail' : dept_detail,
            }
            return render(request,"pharmacy/reports/expiry_item_list_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def stock_adjustement_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'grn_report' in access.user_profile.screen_access:
        try:
            stock_adjust=''
            store_detail = StoreMaster.objects.all()
            if request.method == 'POST':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                store_id = request.POST.get('store_id')
                if from_date and to_date and store_id:
                    stock_adjust = Manual_Stock_Adjustment.objects.filter(adjustment_date__range=[from_date,to_date],store_id_id=store_id)
                elif from_date and to_date:
                    stock_adjust = Manual_Stock_Adjustment.objects.filter(adjustment_date__range=[from_date,to_date])
                elif store_id:
                    stock_adjust = Manual_Stock_Adjustment.objects.filter(store_id_id=store_id)

            context={
                'stock_adjust':stock_adjust,'store_detail':store_detail
            }
            return render(request,"pharmacy/reports/stock_adjustement_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def department_consumption_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'department_consumption_report' in access.user_profile.screen_access:
        try:
            consumption_detail =''
            item_detail = ''
            store_detail = StoreMaster.objects.all()
            if request.method == 'POST':
                item_detail = Inventory_ItemMaster.objects.all()
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                store_id = request.POST.get('store_id')
                if from_date and to_date and store_id:
                    consumption_detail = Department_Consumption.objects.extra(select={
                    'store_name':'Select store_name from testapp_storemaster where id=testapp_department_consumption.store_id_id',
                    }).filter(consumption_date__range=[from_date,to_date],store_id_id=store_id)
                elif from_date and to_date:
                    consumption_detail = Department_Consumption.objects.extra(select={
                    'store_name':'Select store_name from testapp_storemaster where id=testapp_department_consumption.store_id_id',
                    }).filter(consumption_date__range=[from_date,to_date])
                elif store_id:
                    consumption_detail = Department_Consumption.objects.extra(select={
                    'store_name':'Select store_name from testapp_storemaster where id=testapp_department_consumption.store_id_id',
                    }).filter(store_id_id=store_id)
            # consumption_details = consumption_detail])

            context ={
                'consumption_detail' : consumption_detail,
                'store_detail' : store_detail,
                'item_detail' : item_detail,
            }

            return render(request,"pharmacy/reports/department_consumption_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def stock_movement_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'stock_movement_report' in access.user_profile.screen_access:
        try:
            payment_detail=''
            item_name = Inventory_ItemMaster.objects.all()
            dept_detail = ServiceDepartment.objects.all()
            item_name_header = ''
            opening_balance = '0'
            grn_item = '0'
            item_issue = '0'
            item_return = '0'
            item_issue_details = ''
            grn_item_details = ''
            item_return_details = ''
            store_detail = StoreMaster.objects.all()

            if request.method == 'POST':
                item_id = request.POST.get('item_id').split('.')
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                if from_date and to_date and len(item_id) != 0:
                    item_name_header = Inventory_ItemMaster.objects.get(id=item_id[0])
                    grn_item = StockEntry_Child.objects.filter(GRN_datetime__date__range=[from_date,to_date],item_id_id=item_id[0]).aggregate(Sum('physical_qty'))
                    item_issue = Item_Issue_Child.objects.filter(item_issue_date__date__range=[from_date,to_date],item_id_id=item_id[0]).aggregate(Sum('issued_qty'))
                    item_return = Item_return_Child.objects.filter(return_date__date__range=[from_date,to_date],item_id_id=item_id[0]).aggregate(Sum('return_qty'))
                    grn_item_details = StockEntry_Child.objects.filter(GRN_datetime__date__range=[from_date,to_date],item_id_id=item_id[0])
                    item_issue_details = Item_Issue_Child.objects.filter(item_issue_date__date__range=[from_date,to_date],item_id_id=item_id[0])
                    item_return_details = Item_return_Child.objects.filter(return_date__date__range=[from_date,to_date],item_id_id=item_id[0])
            context ={
                'payment_detail' : payment_detail,
                'item_name' : item_name,
                'store_detail' : store_detail,
                'item_name_header' : item_name_header,
                'opening_balance' : opening_balance,
                'grn_item' : grn_item,
                'item_issue' : item_issue,
                'item_return' : item_return,
                'item_issue_details' : item_issue_details,
                'grn_item_details' : grn_item_details,
                'item_return_details' : item_return_details,
                'dept_detail' : dept_detail,
            }
            return render(request,"pharmacy/reports/stock_movement_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def itemwise_purchase_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_wise_purchase_report' in access.user_profile.screen_access:
        try:
            po_details = ''
            item_name = ''
            item_details = Inventory_ItemMaster.objects.all()
            if request.method == 'POST':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                item_id = request.POST.get('item_id').split('.')
                item_name = item_id[1]
                if len(item_id) == 0 and from_date and to_date:
                    po_details = PurchaseOrder_Child.objects.filter(PO_datetime__range=[from_date,to_date],item_id_id=item_id[0])
                elif from_date and to_date:
                    po_details = PurchaseOrder_Child.objects.filter(PO_datetime__range=[from_date,to_date])
                elif item_id:
                    po_details = PurchaseOrder_Child.objects.filter(item_id_id=item_id[0])
            po_detail = zip([item_name],[po_details])
            context ={
                'po_detail' : po_detail,
                'item_details' : item_details,
            }
            return render(request,"pharmacy/reports/itemwise_purchase_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def po_status_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'po_status_report' in access.user_profile.screen_access:
        try:
            po_detail=''
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                po_status = request.POST.get('po_status')
                if po_status and from_date and to_date:
                    po_detail = PurchaseOrder_Parent.objects.filter(PO_datetime__range=[from_date,to_date],PO_status=po_status)
                elif po_status == 'all':
                    po_detail = PurchaseOrder_Parent.objects.all()
                elif po_status:
                    po_detail = PurchaseOrder_Parent.objects.filter(PO_status=po_status)
            context ={
                'po_detail' : po_detail,
            }
            return render(request,"pharmacy/reports/po_status_report.html",context)

        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def grn_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'stock_adjustement_report' in access.user_profile.screen_access:
        try:
            grn_detail=''
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                grn_detail = StockEntry_Parent.objects.filter(GRN_datetime__range=[from_date,to_date])

            context ={
                'grn_detail' : grn_detail,
            }
            return render(request,"pharmacy/reports/grn_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def grn_item_detail(request,pk):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'grn_report' in access.user_profile.screen_access:
        try:
            item_detail = StockEntry_Child.objects.filter(GRN_id=pk)
            context ={
            'item_detail' : item_detail,
            }
            return render(request,"pharmacy/reports/grn_item_detail.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def pharmacysale_summary_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'pharmacysale_summary_report' in access.user_profile.screen_access:
        try:
            sale_detail=''
            item_detail = ''
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                sale_detail = PS_CounterSale_Parent.objects.filter(sales_date__range=[from_date,to_date])
            context ={
                'sale_detail' : sale_detail,
            }
            return render(request,"pharmacy/reports/pharamaysale_summary_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def pharmacysale_detail_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'pharmacysale_detail_report' in access.user_profile.screen_access:
        try:
            item_detail = []
            sale_id =[]
            item_details =[]
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                sale_id = PS_CounterSale_Parent.objects.filter(sales_date__range=[from_date,to_date])
                for data in sale_id:
                    item_detail.append(PS_CounterSale_child.objects.filter(Op_sales_no=data.Op_sales_no))
                    print('item_detail',item_detail)
                item_details = zip(sale_id,item_detail)
            context ={
                'item_details' : item_details,'sale_id':sale_id
            }

            return render(request,"pharmacy/reports/pharmacysale_detail_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def stock_transfer_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'stock_transfer_report' in access.user_profile.screen_access:
        try:
            transfer_detail = ''
            store_detail = StoreMaster.objects.filter(store_type=1)
            search_btn = request.POST.get('search_btn')
            if search_btn == 'search_btn':
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                indent_store_id = request.POST.get('indent_store_id')
                return_store_id = request.POST.get('return_store_id')
                if indent_store_id and return_store_id and from_date and to_date:
                    transfer_detail = Transfer_Request_Mainstore_Parent.objects.filter(request_date__range=[from_date,to_date],indent_store_id=indent_store_id,request_store_id=return_store_id)
                elif from_date and to_date:
                    transfer_detail = Transfer_Request_Mainstore_Parent.objects.filter(request_date__range=[from_date,to_date])
                elif indent_store_id and return_store_id:
                    transfer_detail = Transfer_Request_Mainstore_Parent.objects.filter(indent_store_id=indent_store_id,request_store_id=return_store_id)
                elif indent_store_id:
                    transfer_detail = Transfer_Request_Mainstore_Parent.objects.filter(indent_store_id=indent_store_id)
                elif return_store_id:
                    transfer_detail = Transfer_Request_Mainstore_Parent.objects.filter(request_store_id=return_store_id)

            context ={
                'store_detail' : store_detail,'transfer_detail':transfer_detail
            }
            return render(request,"pharmacy/reports/stock_transfer_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def stock_tranfer_items_list(request,pk):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'stock_transfer_report' in access.user_profile.screen_access:
        try:
            transfer_detail = Transfer_Request_Mainstore_Child.objects.filter(request_no=pk)
            context ={
                'transfer_detail':transfer_detail
            }
            return render(request,"pharmacy/reports/stock_tranfer_items_list.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def detail_item_status_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'detailed_item_status_report' in access.user_profile.screen_access:
        try:
            detail_item_list = ''
            item_details = ''
            search_btn = request.POST.get('search_btn')
            dept_detail = ServiceDepartment.objects.all()
            if search_btn == 'search_btn':
                item_details = Inventory_ItemMaster.objects.all()
                from_date = request.POST.get('from_date')
                to_date = request.POST.get('to_date')
                particulars=request.POST.get('particular')
                if from_date and to_date:
                    Detailed_ItemStatus_Temp.objects.all().delete()
                    po_details = StockEntry_Child.objects.filter(GRN_datetime__range=[from_date,to_date])
                    consume_detail = Department_Consumption.objects.filter(consumption_date__range=[from_date,to_date])
                    ps_sale_detail = PS_CounterSale_child.objects.filter(sales_date__range=[from_date,to_date])
                    for data in po_details:
                        temp_save = Detailed_ItemStatus_Temp(
                            item_id = data.item_id,
                            date_time = data.GRN_datetime,
                            opening_balance=data.opening_balance,
                            opening_cost=data.opening_cost,
                            transaction_cost=data.transaction_cost,
                            closing_balance=data.total_qty,
                            closing_cost=data.total_cost,
                            purchase_qty = data.physical_qty,
                            consume_qty = '',
                            in_hand_qty = data.total_qty,
                            status = 'GRN'
                        )
                        temp_save.save()
                    for data in consume_detail:
                        temp_save = Detailed_ItemStatus_Temp(
                            item_id = data.item_id,
                            date_time = data.consumption_date,
                            opening_balance=data.opening_balance,
                            opening_cost='',
                            transaction_cost='',
                            closing_balance=data.grn_consume_hand_qty,
                            closing_cost='',
                            purchase_qty = '',
                            consume_qty = data.consumption_qty,
                            in_hand_qty = data.grn_consume_hand_qty,
                            status = 'Consume'
                        )
                        temp_save.save()
                    for data in ps_sale_detail:
                        temp_save = Detailed_ItemStatus_Temp(
                            item_id = data.item_id,
                            date_time = data.sales_date,
                            opening_balance=data.opening_balance,
                            opening_cost='',
                            transaction_cost='',
                            closing_balance=data.grn_consume_hand_qty,
                            closing_cost='',
                            purchase_qty = '',
                            consume_qty = data.qty,
                            in_hand_qty = data.grn_consume_hand_qty,
                            status = 'Sale_Consume'
                        )
                        temp_save.save()
                    detail_item_list = Detailed_ItemStatus_Temp.objects.all().order_by('date_time')
                    context ={
                        'detail_item_list' : detail_item_list,
                        'item_details' : item_details,
                        'dept_detail' : dept_detail,
                    }
                    return render(request,"pharmacy/reports/detail_item_status_report.html",context)

                elif len(particulars) != 0:
                    detail_item_list = Detailed_ItemStatus_Temp.objects.filter(status=particulars).order_by('date_time')
                    context ={
                        'detail_item_list' : detail_item_list,
                        'item_details' : item_details,
                        'dept_detail' : dept_detail,
                    }
                    return render(request,"pharmacy/reports/detail_item_status_report.html",context)
            context ={
                    'dept_detail' : dept_detail,
            }
            return render(request,"pharmacy/reports/detail_item_status_report.html",context)
        except Exception as error:
           return render(request,'error.html',{'error':error})
    else:
        return redirect('dashboard')

@login_required(login_url='/user_login')
def item_status_with_particular(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'item_status_with_particulars_report' in access.user_profile.screen_access:
            dept_detail = ServiceDepartment.objects.all()
            store_detail = StoreMaster.objects.filter(store_type__in=[0,1])
            location_detail = LocationMaster.objects.all()
            search_button=request.POST.get("Submit_btn")
            if search_button == "submit_btn":
                start_date=request.POST.get("from_date")
                date_to = request.POST.get("to_date")
                end_date = ''
                store_id = request.POST.get("store_id")
                if store_id:
                    store_type = StoreMaster.objects.get(id=store_id)
                if date_to:
                    to_date=datetime.strptime(request.POST.get("to_date"), "%Y-%m-%d").date()
                    end_date = to_date + timedelta(days=1)
                particulars=request.POST.get("particular")


                items=Inventory_ItemMaster.objects.all()
                # get Items from inventory item master
                if start_date and end_date and store_id:
                    Item_Status_Particular_Temp.objects.all().delete()
                    if store_type.store_type == '0':
                        # get records from Stock entry child
                        stockchild=StockEntry_Child.objects.filter(GRN_datetime__range=[start_date,end_date])
                        # get records from item Issue to mainstore Child
                        item_issuechild=Item_Issue_Child.objects.filter(item_issue_date__range=[start_date,end_date])
                        # get records from return to supplier
                        return_tosupplier = Item_Return_Supplier_Child.objects.filter(return_date__range=[start_date,end_date])
                        for data in stockchild:
                            itemstatus_report_temp = Item_Status_Particular_Temp(
                                item_id_id=data.item_id_id,
                                date=data.GRN_datetime,
                                particular=data.movement_status,
                                opening_balance=data.opening_balance,
                                opening_cost=data.opening_cost,
                                transaction_cost = data.transaction_cost,
                                purchase_qty=data.physical_qty,
                                issue_qty='',
                                return_qty='',
                                closing_cost=data.total_cost,
                                closing_balance=data.total_qty,
                            )
                            itemstatus_report_temp.save(print("itemstatus_report_temp save"))
                        for data in item_issuechild:
                            itemstatus_report_temp1 = Item_Status_Particular_Temp(
                                item_id_id=data.item_id_id,
                                date=data.item_issue_date,
                                particular=data.movement_status,
                                opening_balance=data.opening_balance,
                                opening_cost=data.opening_cost,
                                transaction_cost = data.transaction_cost,
                                purchase_qty='',
                                issue_qty=data.issued_qty,
                                return_qty='',
                                closing_cost=data.total_cost,
                                closing_balance=data.total_amount,
                            )
                            itemstatus_report_temp1.save(print("itemstatus_report_temp1 save"))
                        for data in return_tosupplier:
                            itemstatus_report_temp1 = Item_Status_Particular_Temp(
                                item_id_id=data.item_id_id,
                                date=data.return_date,
                                particular=data.movement_status,
                                opening_balance=data.opening_balance,
                                opening_cost=data.opening_cost,
                                transaction_cost = data.transaction_cost,
                                purchase_qty='',
                                issue_qty='',
                                return_qty=data.return_qty,
                                closing_cost=data.total_cost,
                                closing_balance=data.total_qty,
                            )
                            itemstatus_report_temp1.save(print("itemstatus_report_temp1 save"))    
                    elif store_type.store_type == '1':        
                        # get records from item return to mainstore Child
                        item_returnchild=[]
                        item_issue_subchild=[]
                        item_return_cpcchild=[]
                        item_return_p = Item_Return_Parent.objects.filter(return_date__range=[start_date,end_date],receiving_store_id=store_id)
                        for data in item_return_p:
                            item_returnchild.append(Item_return_Child.objects.filter(item_return_no=data.item_return_no))
                        # get records from item Issue to substore Child
                        item_issue_p = Item_Issue_ToSubStore_Parent.objects.filter(item_issue_date__range=[start_date,end_date],issued_store_id=store_id)
                        for data in item_issue_p:
                            item_issue_subchild.append(Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data.item_issue_no))
                        # get records from item return to substore Child
                        item_return_cpc = Item_Return_ToCPC_Parent.objects.filter(return_date__range=[start_date,end_date],return_store_id=store_id)
                        for data in item_return_cpc:
                            item_return_cpcchild.append(Item_Return_ToCPC_Child.objects.filter(return_no=data.return_no))

                        for data2 in item_issue_subchild:
                            for data in data2:
                                itemstatus_report_temp = Item_Status_Particular_Temp(
                                    item_id_id=data.item_id_id,
                                    date=data.item_issue_date,
                                    particular=data.movement_status,
                                    opening_balance=data.opening_balance,
                                    opening_cost=data.opening_cost,
                                    transaction_cost = data.transaction_cost,
                                    purchase_qty='',
                                    issue_qty=data.issued_qty,
                                    return_qty='',
                                    closing_cost=data.total_cost,
                                    closing_balance=data.total_amount,
                                )
                                itemstatus_report_temp.save(print("itemstatus_report_temp save"))
                        for data2 in item_returnchild:
                            for data in data2:
                                itemstatus_report_temp2 = Item_Status_Particular_Temp(
                                    item_id_id=data.item_id_id,
                                    date=data.return_date,
                                    particular=data.movable_status,
                                    opening_balance=data.opening_balance,
                                    opening_cost=data.opening_cost,
                                    transaction_cost = data.transaction_cost,
                                    purchase_qty='',
                                    issue_qty='',
                                    return_qty=data.return_qty,
                                    closing_cost=data.total_cost,
                                    closing_balance=data.total_qty,
                                )
                                itemstatus_report_temp2.save(print("itemstatus_report_temp1 save"))

                        for data2 in item_return_cpcchild:
                            for data in data2:
                                itemstatus_report_temp = Item_Status_Particular_Temp(
                                    item_id_id=data.item_id_id,
                                    date=data.return_date,
                                    particular=data.movable_status,
                                    opening_balance=data.opening_balance,
                                    opening_cost=data.opening_cost,
                                    transaction_cost = data.transaction_cost,
                                    purchase_qty='',
                                    issue_qty='',
                                    return_qty=data.return_qty,
                                    closing_cost=data.total_cost,
                                    closing_balance=data.total_qty,
                                )
                                itemstatus_report_temp.save(print("itemstatus_report_temp save"))
                    itemstatus_report_temp3=Item_Status_Particular_Temp.objects.all().order_by('date')

                    context={
                        "items_name":items,"itemstatus_report_temp3":itemstatus_report_temp3,"dept_detail":dept_detail,'location_detail':location_detail,'store_detail':store_detail
                    }
                    return render(request,"pharmacy/reports/item_status_particular.html",context)

                elif not start_date and not end_date and particulars != "Select":
                    itemstatus_report_temp3=Item_Status_Particular_Temp.objects.filter(particular=particulars).order_by('date')
                    context={
                            "items_name":items,"itemstatus_report_temp3":itemstatus_report_temp3,"dept_detail":dept_detail,'location_detail':location_detail,'store_detail':store_detail
                        }
                    return render(request,"pharmacy/reports/item_status_particular.html",context)


            context={
                    "dept_detail":dept_detail,'location_detail':location_detail,'store_detail':store_detail
                }
            return render(request,"pharmacy/reports/item_status_particular.html",context)
       
    else:
        return redirect('dashboard')

def return_to_supplier_js(request):
        batch_no = request.POST.get("batch_no")
        item_id = request.POST.get("item_id")
        expiry_date = request.POST.get("expiry_date")
        vendor = request.POST.get("vendor")
        return_qty = request.POST.get("return_qty")
        reason = request.POST.get("reason")
        rate = request.POST.get("rate")
        amount = request.POST.get("amount")

        total_qty1 = Stock_BatchWise.objects.filter(item_id_id=item_id).last()
        total_qty_1 = int(total_qty1.total_qty) - int(return_qty)
        today=date.today()
        today_date=today.strftime("%d%m%y")
        counter=Item_Return_Supplier_Parent.objects.all().count()
        item_return_supplier_id="IRS"+today_date+"00"+str(counter)
        cpc_store=StoreMaster.objects.get(store_type=0)

        return_to_supplier_parent=Item_Return_Supplier_Parent(
            supplier_return_no=item_return_supplier_id,
            return_date=datetime.today(),
            store_id_id=cpc_store.id,
            location_id_id=cpc_store.location_id_id,
            vendor_id_id=vendor,
            status="pending",
        )

        get_po_id = Stock_BatchWise.objects.filter(item_id_id=item_id,batch_no=batch_no,location_id_id=cpc_store.location_id_id).last()
        po_detail = PurchaseOrder_Child.objects.get(PO_Id=get_po_id.PO_id,item_id_id=item_id)

        if po_detail.schema and po_detail.discount and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - schema_amt - disc_amt + tax_amt
        elif po_detail.schema and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            schema_amt = int(int(int(rate_amt) * int(po_detail.schema)) / 100)
            tax_amt = int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - schema_amt + tax_amt
        elif po_detail.discount and po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            disc_amt = int(int(int(rate_amt) * int(po_detail.discount)) / 100)
            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt - disc_amt + tax_amt
        elif po_detail.tex_details:
            rate_amt = int(return_qty) * int(rate)
            tax_amt =  int(int(int(rate_amt) * int(po_detail.tex_details)) / 100)
            total_cost = rate_amt + tax_amt
        else:
            total_cost = int(return_qty) * int(rate)

        total_cost_amt = int(total_qty1.total_cost) - int(total_cost)

        return_to_supplier_child=Item_Return_Supplier_Child(
            supplier_return_no=item_return_supplier_id,
            return_date=datetime.today(),
            batch_no=batch_no,
            expiry_date=expiry_date,
            item_id_id=item_id,
            return_qty=return_qty,
            total_qty=total_qty_1,
            opening_balance=total_qty1.total_qty,
            transaction_cost=total_cost,
            total_cost=total_cost_amt,
            opening_cost=total_qty1.total_cost,
            return_amount=amount,
            reason=reason,
            status="pending",
            movement_status='Supplier Return Entry'
        )
        return_to_supplier_parent.save(print("return_to_supplier_parent"))
        return_to_supplier_child.save(print("return_to_supplier_child"))

        # update available qty from batchwise table
        available2 = Stock_BatchWise.objects.filter(item_id_id=item_id,batch_no=batch_no).last()
        if available2:
            available2.available_qty = int(available2.available_qty) - int(return_qty)
            available2.save()

        # update total qty from batchwise table
        total_qty2 = Stock_BatchWise.objects.filter(item_id_id=item_id).last()
        if total_qty2:
            total_qty2.total_qty = int(total_qty2.total_qty) - int(return_qty)
            total_qty2.total_cost = total_cost_amt
            total_qty2.save()

        # issue_list_c=Item_Return_ToCPC_Child.objects.filter(item_id_id=item_id,batch_no=batch_no,status='entered',stock_transfer='0')
        # for data in issue_list_c:
        #     data.status='completed'
        #     data.save()
        #     issue_list_p=Item_Return_ToCPC_Parent.objects.get(return_no=data.return_no)
        #     issue_list_p.status='completed'
        #     issue_list_p.save()

        data='Successfully Item Returned to Supplier'
        return JsonResponse(data, safe=False)
   
@login_required(login_url='/user_login')

def patient_feedback(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'patient_feedback' in access.user_profile.screen_access:
        try:
            feedback_count = Patient_Feedback.objects.all()
            feedback_id = unique_id('PF',feedback_count)
            if request.method == 'POST':
                pf_save = Patient_Feedback(
                    feedback_id = feedback_id,
                    datetime = datetime.now(),
                    uhid = request.POST.get('uhid'),
                    visit_id = '',
                    facility = request.POST.get('facility'),
                    state_on_condition = request.POST.get('state_on_condition'),
                    doctor_knowledge = request.POST.get('doctor_knowledge'),
                    doctor_kindness = request.POST.get('doctor_kindness'),
                    nurse_patience = request.POST.get('nurse_patience'),
                    nurse_knowledge = request.POST.get('nurse_knowledge'),
                    waiting_time = request.POST.get('waiting_time'),
                    hygiene = request.POST.get('hygiene'),
                    improve_service = request.POST.get('improve_service'),
                )
                pf_save.save()
            return render(request,"pharmacy/patient_feedback.html")
        except Exception as error:
            return render(request,'error.html',{'error':error})

def get_uhid_detail(request):
    try:
        uhid=request.POST.get("uhid")
        records=PatientsRegistrationsAllInOne.objects.filter(uhid=uhid).first()
        data=json.dumps({
            'uhid': records.uhid,
            "mobile": records.mobile_number,
            'age': records.age,
            "gender": records.gender,
            'first_name': records.first_name,
            'middle_name': records.middle_name,
            'last_name': records.last_name,
            'dob': str(records.dob),
            'address': records.address,
            'city': records.city,
            'state': records.state,
            'country': records.country,
            'pin_code': records.pin_code,
            'email': records.email,
            })
        return HttpResponse(data, content_type='application/json')
    except Exception as error:
        return render(request,'error.html',{'error':error})

@login_required(login_url='/user_login')

def patient_feedback_report(request):
    access=CreateUser.objects.select_related('user_profile').filter(login_id=request.user).first()
    if request.user.is_superuser or 'patient_feedback_report' in access.user_profile.screen_access:
        try:
            very_satisfied = ''
            satisfied = ''
            neutral = ''
            unsatisfied = ''
            very_unsatisfied = ''
            if request.method == 'POST':
                the_field=request.POST.get('parameter')
                very_satisfied = Patient_Feedback.objects.filter(**{the_field: 'Very satisfied'}).count()
                satisfied = Patient_Feedback.objects.filter(**{the_field: 'Satisfied'}).count()
                neutral = Patient_Feedback.objects.filter(**{the_field: 'Neutral'}).count()
                unsatisfied = Patient_Feedback.objects.filter(**{the_field: 'Unsatisfied'}).count()
                very_unsatisfied = Patient_Feedback.objects.filter(**{the_field: 'Very unsatisfied'}).count()

            context ={
                'very_satisfied' : 10,
                'satisfied' : 4,
                'neutral' : 5,
                'unsatisfied' : 6,
                'very_unsatisfied' : 7,
            }
            return render(request,"Reports/patient_feedback_report.html",context)
        except Exception as error:
            return render(request,'error.html',{'error':error})

def viewPO_in_poapproval(request):
    try:
        approved1 = PurchaseOrder_Parent.objects.filter(approval_status="completed")
        search_butn = request.POST.get("submit_btn")
        if search_butn == "submit_btn":
            from_date = request.POST.get("from_date")
            to_date = request.POST.get("to_date")
            PO_no = request.POST.get("PO_no")
            if from_date and to_date and not PO_no:
                approved1 = PurchaseOrder_Parent.objects.filter(approval_status="completed",PO_datetime__range=[from_date,to_date])
                context = {
                    "approved1":approved1
                }
                return render(request,"pharmacy/viewpo_in_approval.html",context)
            elif PO_no:
                approved1 = PurchaseOrder_Parent.objects.filter(approval_status="completed",PO_id=PO_no)
                context = {
                    "approved1":approved1
                }
                return render(request,"pharmacy/viewpo_in_approval.html",context)
        context = {
            "approved1":approved1
        }
        return render(request,"pharmacy/viewpo_in_approval.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})

def viewPO_in_poapproval_details(request,pk):
    try:
        po_child = PurchaseOrder_Child.objects.filter(PO_Id=pk)
        context = {
            "po_child":po_child
        }
        return render(request,"pharmacy/viewpo_details.html",context)
    except Exception as error:
        return render(request,'error.html',{'error':error})


def save_department_consume(request):
    try:
        department_consumption =Department_Consumption.objects.all().count()
        today=date.today()
        today=today.strftime("%d%m%y")
        DCID='PSR'+today+'000'+str(department_consumption)
        item_name = request.POST.get("item_id")
        batch = request.POST.get("batch_no")
        expiry_date = request.POST.get("expiry_date")
        inhand_qty = int(request.POST.get("inhand_qty")) - int(request.POST.get("consume_qty"))
        consume_qty = request.POST.get("consume_qty")
        rate = request.POST.get("rate")
        amount = request.POST.get("amount")
        remark = request.POST.get("remark")
        store_id = request.POST.get("store_id")
        location_id=request.POST.get("location_id")
        store_type = StoreMaster.objects.get(id=store_id)
        if store_type.store_type == '1':
            totalqty = Stock_BatchWise_Mainstore.objects.filter(location_id_id=location_id,store_id_id=store_id,item_id_id=item_name).last()
            total_qty = int(totalqty.total_qty) - int(consume_qty)
            grn = Stock_BatchWise_Mainstore.objects.filter(location_id_id=location_id,store_id_id=store_id,item_id_id=item_name,batch_no=batch).last()
            inhand = int(grn.total_consume_qty) - int(consume_qty)
            totalqty.total_qty = total_qty
            totalqty.save()
            grn.total_consume_qty = inhand
            grn.available_qty = int(grn.available_qty) - int(consume_qty)
            grn.save()
        elif store_type.store_type == '2':
            issue_list = Item_Issue_ToSubStore_Parent.objects.filter(location_id_id=location_id,received_store_id=store_id)
            for data in issue_list:
                totalqty = Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data.item_issue_no,item_id_id=item_name).last()
                grn = Item_Issue_ToSubStore_Child.objects.filter(item_issue_no=data.item_issue_no,item_id_id=item_name,serial_batch=batch).last()
                if totalqty:
                    total_qty = int(totalqty.total_amount) - int(consume_qty)
                    totalqty.total_amount = total_qty
                    valu = totalqty.total_amount
                    # totalqty.save()
                # inhand = int(grn.total_consume_qty) - int(consume_qty)

                if grn:
                    grn.available_qty = int(grn.available_qty) - int(consume_qty)
                    grn.save()
        department_consumptions =Department_Consumption(
            consumption_No =DCID,
            batch_no =batch,
            item_id_id =item_name,
            expiry_date =expiry_date,
            store_id_id =store_id,
            location_id_id=location_id,
            department_id=request.POST.get("department_id"),
            inhand_qty =inhand_qty,
            consumption_qty=consume_qty,
            rate =rate,
            total_amount =amount,
            remark =remark,
            status ="",
            total_qty = total_qty,
            opening_balance = valu,
            grn_consume_hand_qty = consume_qty,
            )
        department_consumptions.save(print('data saved'))
        data = 'Qty Consumed Sucessfully'
        return HttpResponse(data, content_type='application/json',safe=False)
    except Exception as error:
        return render(request,'error.html',{'error':error})


def pharmacy_dashboard(request):
    return render(request,"pharmacy/dashboard.html")
