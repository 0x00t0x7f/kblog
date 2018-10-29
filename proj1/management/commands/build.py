"""
自定义管理命令， 用于将内容输出到可部署的静态文件夹下
"""

import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test.client import Client


def get_pages():
	for name in os.listdir(settings.SITE_PAGRS_DIRECTORY):
		if name.endswith(".html"):
			yield name[:5]


class Command(BaseCommand):
	help = "Build static site output"

	leave_locale_alone = True

	def handle(self, *args, **kwargs):
		""" request pages and build output"""
		if os.path.exists(settings.SITE_OUTPUT_DIRECTORY):
			shutil.rmtree(settings.SITE_OUTPUT_DIRECTORY)

		os.mkdir(settings.SITE_OUTPUT_DIRECTORY)
		os.makedirs(settings.STATIC_ROOT, exists_ok=True)

		call_command("collectstatic", interactive=False, clear=True, verbosity=0)

		client = Client()

		for page in get_pages():
			url = reverse("page", kwargs={"slug" : page})
			response = client.get(url)
			if page == "login":
				output_dir = settings.SITE_OUTPUT_DIRECTORY
			else:
				output_dir = os.path.join(settings.SITE_OUTPUT_DIRECTORY, page)
				os.makedirs(output_dir)

			with open(os.path.join(output_dir, "login.html"), "wb") as f:
				f.write(response.content)



























