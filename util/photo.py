from PIL import Image
from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile
from django.conf import settings
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
import StringIO

def upload_to_s3(filename, file_as_string):
    conn = S3Connection(settings.AWS_S3_ACCESS_KEY_ID, settings.AWS_S3_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    key = Key(bucket)
    key.key = filename
    key.set_contents_from_string(file_as_string)
    key.set_acl('public-read')

def square_image(image):
    width, height = image.size

    if width > height:
        delta = width - height
        left = int(delta/2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta/2)
        right = width
        lower = width + upper

    image = image.crop((left, upper, right, lower))
    return image

def fix_image_rotation(image):
    image = image.rotate(-90, expand=True)
    return image


def generate_small_image(upload_filename, image_file):
    try:
        f = storage.open(image_file, 'r')
        image = Image.open(f)
        image = square_image(image)
        image = fix_image_rotation(image)
        image.thumbnail((100,100), Image.ANTIALIAS)
        filename = 'small/{}.jpg'.format(upload_filename)        
        output = StringIO.StringIO()
        image.save(output, "JPEG")
        contents = output.getvalue()
        output.close()
        upload_to_s3(filename, contents)
        return filename
    except IOError as ex:
        print ex
        raise


def generate_medium_image(upload_filename, image_file):
    try:
        f = storage.open(image_file, 'r')
        image = Image.open(f)
        image = square_image(image)
        image = fix_image_rotation(image)
        image.thumbnail((185,185), Image.ANTIALIAS)
        filename = 'medium/{}.jpg'.format(upload_filename)
        output = StringIO.StringIO()
        image.save(output, "JPEG")
        contents = output.getvalue()
        output.close()
        upload_to_s3(filename, contents)
        return filename
    except IOError as ex:
        print ex
        raise

def generate_large_image(upload_filename, image_file):
    try:
        f = storage.open(image_file, 'r')
        image = Image.open(f)
        image = square_image(image)
        image = fix_image_rotation(image)
        image.thumbnail((400,400), Image.ANTIALIAS)
        filename = 'large/{}.jpg'.format(upload_filename)
        output = StringIO.StringIO()
        image.save(output, "JPEG")
        contents = output.getvalue()
        output.close()
        upload_to_s3(filename, contents)
        return filename
    except IOError as ex:
        print ex
        raise
        