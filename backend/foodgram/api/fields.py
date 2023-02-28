import base64
import os

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64EncodedImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, datastr = data.split(";base64,")
            ext = format.split("/")[-1]
            img = base64.b64decode(datastr)
            name = os.urandom(8).hex()
            data = ContentFile(img, name=f"{name}." + ext)
        return super().to_internal_value(data)
