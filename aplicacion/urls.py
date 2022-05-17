from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('staff/', views.home1, name="home1"),
 
 
    path('delete/',views.delete_data_t),
    #path('app/tables/',views.maps_app,name="tablas"),

    path('app/torresT/',views.tower_locationT,name="torresT"),
      
    path('app/tablesV1/',views.maps_appV1,name="tablasV1"),
    #path('user_csv/',views.cargar_csv,name="cargar_csv"),

    path('user_csv/',views.lista_csv,name="user_csv"),
    path('user_csv/subir_csv/',views.cargarusr_csv,name="subir_csv"),
    path('user_csv/<int:pk>/',views.borrarcsv,name="borrar_csv"),
    path('user_csv/ver_csv/<int:pk>/',views.vermap,name="ver_csv"),

    path('register/',views.registerPage, name="register"),
    path('login/',views.loginPage, name="login"),
    path('logout/',views.logoutUser, name="logout"),
    path('subir/', views.cargar_csv_db, name='cargar'),
    path('subirT/', views.cargar_csv_db_torres, name='cargar_torres'),

    path('api/signalview/',views.signal_view,name="signalview"),
    path('api/signalview/borrar/<int:pk>/',views.borrarsignal,name="borrarsignal"),
    path('api/signalview/borrarselectrue',views.borrarsignals,name="borrarsignals"),

    path('api/towerview/',views.tower_view,name="towerview"),
    path('api/towerview/borrar/<int:pk>/',views.borrartower,name="borrartower"),
    path('api/towerview/borrarselectrue',views.borrartowers,name="borrartowers"),
]   




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)