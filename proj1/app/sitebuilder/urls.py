from django.conf.urls import url
from .views import page


urlpatterns = [
	url('^$', page, name="homepage"),
	url('^(?P<slug>[\w./-]+)/$', page, name="page"),
]