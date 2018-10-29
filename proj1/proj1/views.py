import os
from django.conf import settings
from django.utils._os import safe_join
from django.template import Template

import hashlib
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest
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


def get_page_or_404(name):
	try:
		file_path = safe_join(settings.SITE_PAGES_DIRECTORY, name)
	except ValueError:
		# raise Http404("Page not found")
		file_path = safe_join(settings.SITE_PAGES_DIRECTORY, "404.html")
	else:
		if not os.path.exists(file_path):
			# raise Http404("Page not found")
			file_path = safe_join(settings.SITE_PAGES_DIRECTORY, "404.html")

	with open(file_path, encoding="utf-8") as fread:
		page = Template(fread.read())

	return page


def page(request, slug="login"):
	file_name = "{}.html".format(slug)
	page = get_page_or_404(file_name)
	context = {
		"slug" : slug,
		"page" : page,
	}

	return render(request, "page.html", context)

