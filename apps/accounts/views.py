# accounts/views.py
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def clear_all_sessions(request):
    """
    Emergency endpoint to clear all sessions
    Visit this URL to fix the UUID/Integer session error
    """
    try:
        count = Session.objects.all().count()
        Session.objects.all().delete()
        return HttpResponse(
            f"SUCCESS! Cleared {count} sessions. "
            f"Now go to /admin/ and login again.",
            content_type="text/plain"
        )
    except Exception as e:
        return HttpResponse(
            f"ERROR: {str(e)}",
            content_type="text/plain",
            status=500
        )
