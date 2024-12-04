from django.urls import path
from IPDapp import views
urlpatterns=[
    path('bed_allotment', views.bed_allotment,name='bed_allotment'),
    path('ward-type',views.ward_type_view,name='wt'),
    path('ward-cate',views.ward_cate_view,name='wc'),

#     Master Level Url Like Room Definition......
    path('wing-master',views.wing_master_view,name='wm'),
    path('floor-master',views.floor_master_view,name='fm'),
    path('room-master',views.room_master_view,name='rm'),
    path('bed-master',views.bed_master_view,name='bm'),
    path('bed-master-next',views.bed_master_next_view,name='bmn'),
    path('ward-type',views.ward_t_view,name='wt'),
    path('ward-category',views.ward_c_view,name='wc'),
    path('ward-name',views.ward_name_view,name='wn'),
    path('bed-location',views.bed_location_view,name='bl'),
    path('nursing-station-counter',views.nursing_station_counter_view,name='nsv'),
    path('department',views.depatment_view,name='dpt'),
    path('room-defination',views.room_defination,name='rd'),
    path('ajax-load-room',views.load_room_master,name='ajax_room_m_urls'),
    path('ajax-load-bed',views.load_bed_master,name='ajax_bed_master'),
    path('ajax-load-ward_type',views.load_ward_type_master,name='ajax_ward_type_master'),
    path('ajax-load-ward_cat',views.load_ward_cat_master,name='ajax_ward_cat_master'),
    path('ajax-load-bed_next',views.load_bed_master_next,name='load_bed_master_next'),

#     Django DropDown URL
    path('add/',views.person_create_view,name='person_add'),
    path('country/',views.country_view,name='country'),
    path('city/',views.city_view,name='city'),
    path('<int:pk>/',views.person_update_view,name='person_change'),
    path('ajax/load-cities/',views.load_cities,name='ajax_load_cities')#ajax

]