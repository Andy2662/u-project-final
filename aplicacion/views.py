from distutils.log import error
from django.shortcuts import render, redirect

from colour import Color
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from .filters import *
from folium import *
from folium.plugins import MarkerCluster, HeatMap
from django.core.files.storage import FileSystemStorage
from numpy import interp

from pathlib import Path
from django.contrib.admin.views.decorators import staff_member_required


import os
import pandas as pd
import folium
import csv

import branca.colormap as cm


BASE_DIR = Path(__file__).resolve().parent.parent


@login_required(login_url='login')
def home(request):
    if request.user.is_staff:
        return redirect('home1')
    else:
                
        return render(request,'aplicacion/dashboard.html')

@login_required(login_url='login')
def home1(request):
    return render(request,'aplicacion/dashboard1.html')

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        try:
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Cuenta creada para '+ user)
                return redirect('login')
        except:
            messages.info(request, Exception) 
    context = {'form':form}
    return render(request, 'aplicacion/register1.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_staff:
                return redirect('home1')
            else:
                return redirect('home')
        else:
            messages.info(request, 'Usuario o Contraseña son incorrectos.') 
    context = {}
    return render(request, 'aplicacion/login1.html', context) 

@login_required
def logoutUser(request):
    logout(request)
    return redirect('login')
    
@login_required
def cargar_csv(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'aplicacion/user_csv.html', context)

@login_required
def lista_csv(request):
    user_id = request.user.id
    csvs = user_csvs.objects.filter(id_usr=user_id)
    datos_csv = csvs
    context = {
        'datos':datos_csv,
    }
    return render(request, 'aplicacion/csv_list.html', context)

@login_required
def cargarusr_csv(request):

    if request.method == 'POST':
        form = csvForm(request.POST, request.FILES)
        username = request.user.username
        user_id = request.user.id
        if form.is_valid():

            form.save()
  
            obj = user_csvs.objects.get(activated=True)

            with open(obj.archivocsv.path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter = ',')
                list_of_column_names = []
                for row in csv_reader:
                    list_of_column_names.append(row)
                    break
                columns = ['latitud','longitud']
                for i in columns:
                    if i in list_of_column_names[0]:
                        c=1

                    else:
                        c=0
                        user_csvs.objects.filter(activated=True).delete()
                        
                        break
                if c==1:
                    instance = form.save(commit=False)
                    instance.usuario = username
                    instance.id_usr = user_id
                    instance.save()
                    savefile=user_csvs.objects.get(activated=True)
                    savefile.activated = False
                    savefile.save()
                    return redirect('user_csv')
                else:
                    messages.error(request, "El formato del archivo CSV no contiene los datos necesarios, el archivo por lo menos debe contener las columnas: [latitud,longitud]")
    else:
        form = csvForm()
    return render(request, 'aplicacion/cargar_csv.html',{
        'form': form
    })

@login_required
def borrarcsv(request, pk):
    if request.method == 'POST':
        csvfile = user_csvs.objects.get(pk=pk)
        csvfile.delete()
        return redirect('user_csv')
@login_required
def vermap(request, pk):
    csvfile = user_csvs.objects.get(pk=pk)
    datos_csv=pd.read_csv(csvfile.archivocsv)
    print(csvfile.archivocsv.path)
    data_html=datos_csv.to_html()
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()
    m = folium.Map(
            width='100%', 
            height='100%', 
            max_zoom=18, 
            min_zoom=18,
            zoom_start=18, 
            location=(default_lat, default_lon),
            )
    lat_lon=datos_csv[['latitud','longitud','pot']].values
    valcsv = datos_csv[['latitud','longitud','pot']].values                
    for each in datos_csv.iterrows():
        folium.Marker(list((each[1]['latitud'],each[1]['longitud'])), 
                popup=each[1],
        
                ).add_to(m)

    m.save('user_map.html')
    m = m._repr_html_()
    context={
        'map':m,
        'data':csvfile,
        'datos':valcsv,
        'tabla':data_html,
        'csv_col':datos_csv.columns,
        'csv_row':datos_csv.to_dict('records'),
    }
    return render(request, 'aplicacion/usermap.html', context)

            


def delete_data_t(request):
    torre.objects.all().delete()
    return redirect('home')

@login_required
def maps_appV1(request):
    data_display = medidas.objects.all().order_by('-id')
    rootcsv = os.path.join(BASE_DIR, 'static/CSV/mapsV1.csv')
    rootcsv1 = os.path.join(BASE_DIR, 'static/CSV/maps1V1.csv')
    rootxlxs = os.path.join(BASE_DIR, 'static/CSV/mapsV1.xlsx')
    #rootcsv='mapsV1.csv'
    #rootcsv1='maps1V1.csv'
    #rootxlxs = 'mapsV1.xlsx'
    mediFitro = tablaFilter(request.GET, queryset=data_display)
    datos = mediFitro.qs 
    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'latitud', 
            'longitud',
            'pot',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo',
            'id'
            ])
        for dat in datos.values_list(
            'latitud',
            'longitud',
            'pot_db',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo',
            'id'
            ):
            writer.writerow(dat)
    newd_csv=pd.read_csv(rootcsv)
    newd_csv["pot_db"]=newd_csv['pot'].apply(lambda x: interp(x,[-120,-50],[0,29]))
    newd_csv.to_csv(rootcsv1, index=False)
    datos_csv=pd.read_csv(rootcsv1)

    datos_csv1=pd.read_csv(rootcsv)
    datos_csv1.to_excel(rootxlxs,index = None, header=True)

    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()

    
    m = folium.Map(
            width='100%', 
            height='100%', 
            location=(default_lat, default_lon),
            #tiles='OpenStreetMap',
            tiles='OpenStreetMap',
            control_scale=True,
            min_zoom=10, 
            max_zoom=16,
            zoom_start=14,

            )

    colormap = cm.LinearColormap(colors=[ 'blue', 'cyan', 'yellow', 'orange', 'red'],
                             index=[-120, -110, -100, -95, -90], vmin=-120, vmax=-90,
                             caption='Gradiente de la señal en dBm 4G')


    
    m.add_child(colormap);  

    for each in datos_csv.iterrows():
        # marker_info=("Operador: %s\n" 
        #             "Potenccia_dB: %s\n"
        #             "Latitud: %s\n" 
        #             "Longitud: %s\n"
        #             "Id: %s"
        #             )%(each[1]['operador'],each[1]['pot'],each[1]['latitud'],each[1]['longitud'],each[1]['id'])
        html_popup= """
                
                    <h4>Info de la muestra</h4>
                    <li>Operador: %s</li>
                    <li>Potenccia_dB: %s</li>
                    <li>Latitud: %s</li>
                    <li>Longitud: %s</li>
                    <li>Id: %s</li>
                
            """%(each[1]['operador'],each[1]['pot'],each[1]['latitud'],each[1]['longitud'],each[1]['id'])
        popup=Popup(html=html_popup,max_width=500)
        blue = Color("blue")
        colors = list(blue.range_to(Color("red"),30))
        cvalue = colors[round(float(each[1]['pot_db']))]
        folium.Circle(list((each[1]['latitud'],each[1]['longitud'])), 
                popup=popup,
                radius=50,
                fill=True,
                fill_opacity = 0.2,
                fill_color = '%s' %cvalue,
                stroke = False,
                interactive = True,
                bubblingMouseEvents = True,
            
                ).add_to(m)



   
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.LayerControl().add_to(m)
    map_url = os.path.join(BASE_DIR, 'static/Maps/map_filtroV1.html')
    m.save(map_url)
    m = m._repr_html_()
    context = {
        'filtro':mediFitro,
        'datos':datos,
        'map':m,
    }
    return render(request, 'aplicacion/api_mapsV1.html', context)

@login_required
def tower_locationT(request):

    rootcsv = os.path.join(BASE_DIR, 'static/CSV/towermap.csv')
    rootxlxs = os.path.join(BASE_DIR, 'static/CSV/towermap.xlsx')

    data_display_tower = torre_data.objects.all().order_by('-id')
    tower_filt = towerFilterT(request.GET, queryset=data_display_tower)
    datos = tower_filt.qs
    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'tecnologia',
            'mcc',
            'net',
            'operador', 
            'lac',
            'cellid',
            'latitud',
            'longitud',
            'cobertura',
            'fecha',
            'id'
            ])
        for dat in datos.values_list(
            'tecnologia',
            'mcc',
            'net',
            'operador', 
            'lac',
            'cellid',
            'latitud',
            'longitud',
            'cobertura',
            'fecha',
            'id'
            ):
            writer.writerow(dat)
    print("done")
    datos_csv=pd.read_csv(rootcsv)
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()
    m = folium.Map(
            width='100%', 
            height='100%', 
            location=(default_lat, default_lon),
            tiles='OpenStreetMap',
            control_scale=True,
            #min_zoom=14, 
            #max_zoom=18,
            zoom_start=14,
            )
    datos_csv=pd.read_csv(rootcsv)
    datos_csv.to_excel(rootxlxs,index = None, header=True)
      
    icon_url = os.path.join(BASE_DIR, 'static/icons/tower.png')
    trres = pd.read_csv(rootcsv)
    marker_cluster = MarkerCluster(name="Antenas").add_to(m)
    for each in trres.iterrows():
        marker_info="CellID:%s\n LAC:%s\n Tecnología:%s\n Operador:%s\n Cobertura(m):%s"%(each[1]['cellid'],each[1]['lac'],each[1]['tecnologia'],each[1]['operador'],each[1]['cobertura'])
        tower_icon = folium.CustomIcon(
        icon_url,
        icon_size=(14,14), 
        icon_anchor=None, 
        shadow_image=None, 
        shadow_size=None, 
        shadow_anchor=None, 
        popup_anchor=None)
        html_popup= """
        
            <h4>Info de la muestra</h4>
            <li>CellID: %s</li>
            <li>LAC: %s</li>
            <li>Tecnología: %s</li>
            <li>Operador: %s</li>
            <li>Cobertura(m): %s</li>
            <li>ID: %s</li>
        
            """%(each[1]['cellid'],each[1]['lac'],each[1]['tecnologia'],each[1]['operador'],each[1]['cobertura'],each[1]['id'])
        popup=Popup(html=html_popup,max_width=500)
        folium.Marker(list((each[1]['latitud'],each[1]['longitud'])), 
                popup=popup,
                icon = tower_icon
                ).add_to(marker_cluster)
                
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.LayerControl().add_to(m)
    map_url = os.path.join(BASE_DIR, 'static/Maps/map_filtroT.html')
    m.save(map_url)
    marker_cluster.add_to(m)
      
    m.save('towermap-F.html')
    m = m._repr_html_()
    context = {
        'filtro':tower_filt,
        'datos':datos,
        'map':m,
    }
    return render(request, 'aplicacion/torreT.html', context)

@staff_member_required
def cargar_csv_db(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        form = CsvModelForm()
        obj = Csv.objects.get(activated=False)

        with open(obj.file_name.path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')
            list_of_column_names = []
            for row in csv_reader:
                list_of_column_names.append(row)
                break
            columns = ['usuario','fecha','imsi','test_name','observacion','operador','latitud','latitud','longitud','pot','rssi','modelo','marca']
            for i in columns:
                if i in list_of_column_names[0]:
                    c=1
                else:
                    c=0
                    break
            if c==1:        
                with open(obj.file_name.path) as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        p=medidas(
                            usuario = row['usuario'],
                            fecha = row['fecha'],
                            imsi = row['imsi'],
                            test_name = row['test_name'],
                            observacion = row['observacion'],
                            operador = row['operador'],
                            latitud = row['latitud'],
                            longitud = row['longitud'],
                            pot_db = row['pot'],
                            rssi = row['rssi'],
                            modelo = row['modelo'],
                            marca = row['marca']
                        )
                        p.save()
                messages.success(request, "Datos guardados.")
            else:
                messages.error(request, "El formato del archivo CSV no contiene los datos necesarios. Debe contener el siguiente formato: [usuario,fecha,imsi,test_name,observacion,operador,latitud,latitud,longitud,pot,rssi,modelo,marca]")                        
        Csv.objects.all().delete()
                      
    return render(request,'aplicacion/subircsv.html', {'form':form})

@staff_member_required
def cargar_csv_db_torres(request):
    form = CsvModelFormT(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        form = CsvModelFormT()
        obj = CsvT.objects.get(activated=False)
        with open(obj.file_name.path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')
            list_of_column_names = []
            for row in csv_reader:
                list_of_column_names.append(row)
                break
            columns = ['tecnologia','mcc','mnc','net','lac','cellid','latitud','longitud','cobertura','fecha']
            for i in columns:
                if i in list_of_column_names[0]:
                    c=1
                else:
                    c=0
                    break
            if c==1:
                with open(obj.file_name.path) as csvfile:
                    reader = csv.DictReader(csvfile)
                    CsvT.objects.create()
                    for row in reader:
                        p=torre_data(
                            tecnologia=row['tecnologia'],
                            mcc=row['mcc'],
                            net=row['mnc'],
                            operador=row['net'],
                            lac=row['lac'],
                            cellid =row['cellid'],
                            latitud=row['latitud'],
                            longitud=row['longitud'],
                            cobertura=row['cobertura'],
                            fecha=row['fecha'],
                        )
                        p.save()
                messages.success(request, "Datos guardados.")
            else:
                messages.error(request, "El formato del archivo CSV no contiene los datos necesarios, debe contener el siguiente formato: [tecnologia,mcc,mnc,net,lac,cellid,latitud,longitud,cobertura,fecha]")
        CsvT.objects.all().delete()
    return render(request,'aplicacion/subircsvT.html', {'form':form})

@staff_member_required
def signal_view(request):

    data_display = medidas.objects.all().order_by('-id')
    rootcsv = os.path.join(BASE_DIR, 'static/CSV/mapsV1.csv')
    rootcsv1 = os.path.join(BASE_DIR, 'static/CSV/maps1V1.csv')
    rootxlxs = os.path.join(BASE_DIR, 'static/CSV/mapsV1.xlsx')
    #rootcsv='mapsV1.csv'
    #rootcsv1='maps1V1.csv'
    #rootxlxs = 'mapsV1.xlsx'

    mediFitro = tablaFilter(request.GET, queryset=data_display)
    datos = mediFitro.qs
    #print(datos.values_list('latitud','longitud','pot_db','usuario','fecha','test_name','observacion','operador','rssi','marca','imsi','modelo')[1])   
    

    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'latitud', 
            'longitud',
            'pot',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo',
            'id',
            
            ])
        for dat in datos.values_list(
            'latitud',
            'longitud',
            'pot_db',
            'usuario',
            'fecha',
            'test_name',
            'observacion',
            'operador',
            'rssi',
            'marca',
            'imsi',
            'modelo',
            'id',
            ):

            writer.writerow(dat)

    newd_csv=pd.read_csv(rootcsv)
    newd_csv["pot_db"]=newd_csv['pot'].apply(lambda x: interp(x,[-120,-50],[0,29]))

  

    newd_csv.to_csv(rootcsv1, index=False)
    datos_csv=pd.read_csv(rootcsv1)
    datos_csv1=pd.read_csv(rootcsv)
    datos_csv1.to_excel(rootxlxs,index = None, header=True)
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()

    #print(default_lat, default_lon)
  
    
    m = folium.Map(
            width='100%', 
            height='100%', 
            location=(default_lat, default_lon),
            tiles='OpenStreetMap',
            control_scale=True,
            min_zoom=10, 
            max_zoom=16,
            zoom_start=14,
            #scaleRadius= True,
            #scale_radius=True,
            )

    
    colormap = cm.LinearColormap(colors=[ 'blue', 'cyan', 'yellow', 'orange', 'red'],
                             index=[-120, -110, -100, -95, -90], vmin=-120, vmax=-90,
                             caption='Gradiente de la señal en dBm 4G')

    m.add_child(colormap);  

    for i, r in datos_csv.iterrows():

        
        blue = Color("blue")
        colors = list(blue.range_to(Color("red"),30))
        cvalue = colors[round(float(r['pot_db']))]
        #print(cvalue)
        
        html_popup= """
        
            <h4>Info de la muestra</h4>
            <li>Id: %s</li>
            <li>Operador: %s</li>
            <li>Potencia_dB: %s</li>
            <li>Latitud: %s</li>
            <li>Longitud: %s</li>
            
        
            """%(r["id"],r["operador"],r["pot"],r["latitud"],r["longitud"])
        popup=Popup(html=html_popup,max_width=500)
        
        folium.Circle([r['latitud'],r['longitud']],
                        radius=100,
                        fill=True,
                        #color = 'grey',
                        fill_opacity = 0.2,
                        #fill_color = '#48c6dd',
                        fill_color = '%s' %cvalue,
                        stroke = False,
                        interactive = True,
                        bubblingMouseEvents = True,
                        #tooltip = f'Operador:{r["operador"]}\n Potencia dB:{r["pot_db"]}\n Latitud:{r["latitud"]}\n Longitud:{r["longitud"]}',
                        #popup = f'Id: {r["id"]}     \n Operador: {r["operador"]}\n Potencia_dB: {r["pot_db"]}\n Latitud: {r["latitud"]}\n Longitud: {r["longitud"]}'
                        popup = popup
                    ).add_to(m)                   
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.LayerControl().add_to(m)

    map_url = os.path.join(BASE_DIR, 'static/Maps/map_filtroV1.html')
    m.save(map_url)
    m = m._repr_html_()
    
    context = {
        'filtro':mediFitro,
        'datos':datos,
        'map':m,
    }
    
    return render(request, 'aplicacion/signalview.html', context)

@staff_member_required
def borrarsignal(request, pk):
    if request.method == 'POST':
        
        csvfile = medidas.objects.get(pk=pk)
        csvfile.delete()
        return redirect('signalview')

@staff_member_required
def borrarsignals(request):
    rootcsv = os.path.join(BASE_DIR, 'static/CSV/mapsV1.csv')
    with open(rootcsv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csvfile = medidas.objects.get(pk=row['id'])
            csvfile.delete()

    return redirect('signalview')

@staff_member_required
def tower_view(request):

    data_display = torre_data.objects.all().order_by('-id')
    rootcsv = os.path.join(BASE_DIR, 'static/CSV/tmapsV1.csv')
    rootcsv1 = os.path.join(BASE_DIR, 'static/CSV/tmaps1V1.csv')
    rootxlxs = os.path.join(BASE_DIR, 'static/CSV/tmapsV1.xlsx')


    mediFitro = towerFilterT(request.GET, queryset=data_display)
    datos = mediFitro.qs
    #print(datos.values_list('latitud','longitud','pot_db','usuario','fecha','test_name','observacion','operador','rssi','marca','imsi','modelo')[1])   
    

    with open(rootcsv, 'w') as crearcsv:
        writer = csv.writer(crearcsv)
        writer.writerow([
            'latitud', 
            'longitud',
            'tecnologia',
            'mcc',
            'operador',
            'net',
            'lac',
            'cellid',
            'cobertura',
            'fecha',
            'id',

            
            ])
        for dat in datos.values_list(
            'latitud', 
            'longitud',
            'tecnologia',
            'mcc',
            'operador',
            'net',
            'lac',
            'cellid',
            'cobertura',
            'fecha',
            'id',
            ):

            writer.writerow(dat)

    newd_csv=pd.read_csv(rootcsv)
    newd_csv.to_csv(rootcsv1, index=False)
    datos_csv=pd.read_csv(rootcsv1)
    datos_csv1=pd.read_csv(rootcsv)
    datos_csv1.to_excel(rootxlxs,index = None, header=True)
    if(datos_csv.empty):
        default_lat = -17.4140
        default_lon = -66.1653
    else:
        default_lat= datos_csv['latitud'].mean()
        default_lon= datos_csv['longitud'].mean()


    m = folium.Map(
            width='100%', 
            height='100%', 
            location=(default_lat, default_lon),
            tiles='OpenStreetMap',
            control_scale=True,
            #min_zoom=14, 
            #max_zoom=18,
            zoom_start=14,
            )

    icon_url = os.path.join(BASE_DIR, 'static/icons/tower.png')


    trres = pd.read_csv(rootcsv)
    marker_cluster = MarkerCluster().add_to(m)
    
    for each in trres.iterrows():
        marker_info="CellID:%s\n LAC:%s\n Red:%s\n Tecnologia:%s\n Cobertura(m):%s"%(each[1]['cellid'],each[1]['lac'],each[1]['net'],each[1]['tecnologia'],each[1]['cobertura'])
        tower_icon = folium.CustomIcon(
        icon_url,
        icon_size=(14,14), 
        icon_anchor=None, 
        shadow_image=None, 
        shadow_size=None, 
        shadow_anchor=None, 
        popup_anchor=None)
        html_popup= """
        
            <h4>Info de la muestra</h4>
            <li>CellID: %s</li>
            <li>LAC: %s</li>
            <li>Red: %s</li>
            <li>Tecnologia: %s</li>
            <li>Cobertura(m): %s</li>
            <li>Id: %s</li>
        
            """%(each[1]['cellid'],each[1]['lac'],each[1]['net'],each[1]['tecnologia'],each[1]['cobertura'],each[1]['id'])
        popup=Popup(html=html_popup,max_width=500)
        folium.Marker(list((each[1]['latitud'],each[1]['longitud'])), 
                popup=popup,
                icon = tower_icon
                
                
                ).add_to(marker_cluster)
   
      
    marker_cluster.add_to(m)
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.LayerControl().add_to(m)
                 

    map_url = os.path.join(BASE_DIR, 'static/Maps/map_filtrotV1.html')
    m.save(map_url)
    m = m._repr_html_()
    
    context = {
        'filtro':mediFitro,
        'datos':datos,
        'map':m,
    }
    
    return render(request, 'aplicacion/towerview.html', context)

@staff_member_required
def borrartower(request, pk):
    if request.method == 'POST':
        
        csvfile = torre_data.objects.get(pk=pk)
        csvfile.delete()
        return redirect('towerview')

@staff_member_required
def borrartowers(request):
    rootcsv = os.path.join(BASE_DIR, 'static/CSV/tmapsV1.csv')
    with open(rootcsv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csvfile = torre_data.objects.get(pk=row['id'])
            csvfile.delete()

    return redirect('towerview')