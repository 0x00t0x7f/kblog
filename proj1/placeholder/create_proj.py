""" 可复用模板 startproject 的模板是一个目录或 zip文件
当命令运行时想成Django模板，制作过程中会把 create_proj, project_directory, secret_key
和 docs_version 作为上下文传递， 文件名同样会被制作到这个上下文中

DEBUG = os.environ.get("DEBUG", "on") == "on"
SECRET_KEY = os.environ.get("SECRET_KEY", "&*97j89)&wp(+vq!2t@2kpb&)&)uv1_l0-b4amsx+m*w7$m=#q")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

"""


import sys
import os
from django.conf import settings


DEBUG = os.environ.get("DEBUG", "on") == "on"
SECRET_KEY = os.environ.get("SECRET_KEY", "&*97j89)&wp(+vq!2t@2kpb&)&)uv1_l0-b4amsx+m*w7$m=#q")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
BASE_DIR = os.path.dirname(__file__)

settings.configure(
	DEBUG = DEBUG,
	SECRET_KEY = SECRET_KEY,
	ALLOWED_HOSTS = ALLOWED_HOSTS,
	# SECRET_KEY = 'qn6^qd$%f=j3=4$!encui4z*of&be(6d$1#0*wumg@#v*-)ejo',
	ROOT_URLCONF = __name__,
	MIDDLEWARE = (
		'django.middleware.common.CommonMiddleware',
		'django.middleware.csrf.CsrfViewMiddleware',
		'django.middleware.clickjacking.XFrameOptionsMiddleware')
	,

	INSTALLED_APPS=(
		"django.contrib.staticfiles",
	),

	TEMPLATES=(
		{
			"BACKEND" : "django.template.backends.django.DjangoTemplates",
			"DIRS" : (os.path.join(BASE_DIR, "templates"),),
		},
	),

	STATICFILES_DIRS = (
		os.path.join(BASE_DIR, "static"),
	),

	STATIC_URL = "/static/",
)

import hashlib
from django.conf.urls import url
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.wsgi import get_wsgi_application
from django import forms
from django.shortcuts import render
from io import BytesIO
from PIL import Image, ImageDraw
from django.core.cache import cache
from django.views.decorators.http import etag


def generate_etag(request, width, height):
	content = "Placeholder: {}x{}".format(width, height)
	return hashlib.sha1(content.encode("utf-8")).hexdigest()


class ImageForm(forms.Form):

	height = forms.IntegerField(min_value=1, max_value=1024)
	width = forms.IntegerField(min_value=1, max_value=1024)

	def generate(self, image_format="PNG"):
		height, width = self.cleaned_data["height"], self.cleaned_data["width"]

		key = "{}.{}.{}".format(width, height, image_format)
		content = cache.get(key)

		if content is None:
			image = Image.new("RGB", (width, height))
			draw = ImageDraw.Draw(image)
			text = "{}x{}".format(width, height)
			textWidth, textHeight = draw.textsize(text)

			if textWidth < width and textHeight < height:
				texttop, textleft = (height - textHeight) // 2, (width - textWidth) // 2
				draw.text((textleft, texttop), text, fill="red")

			content = BytesIO()
			image.save(content, image_format)
			content.seek(0, 0)

			cache.set(key, content, 60 * 60)
		return content


def home(request):
	return HttpResponse("welcome to placeholder homepage.")


def index(request):
	example = reverse("placeholder", kwargs={"width" : 50, "height" : 50})
	context = {
		"example" : request.build_absolute_uri(example)
	}
	return render(request, "home.html", context)


@etag(generate_etag)
def placeholder(request, width, height):
	form = ImageForm(dict([("height", height), ("width", width)]))
	if form.is_valid():
		image = form.generate()
		return HttpResponse(image, content_type="image/png")
	else:
		return HttpResponseBadRequest("Invalid image request")


urlpatterns = (
	url(r"^$", index, name="homepage"),
	url(r"^image/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$", placeholder, name="placeholder"),
)


application = get_wsgi_application()


if __name__ == "__main__":
	from django.core.management import execute_from_command_line
	execute_from_command_line(sys.argv)
