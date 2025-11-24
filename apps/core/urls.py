from accounts.views import clear_all_sessions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    
    path('emergency-clear-sessions/', clear_all_sessions, name='clear_sessions'),
    
]
