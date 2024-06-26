from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Q
import os
import random
from django.db import models

# from ecommerce.aws.download.utils import AWSDownload
from ecommerce.aws.utils import ProtectedS3Storage
from ecommerce.utils import get_filename

# create json copy of database python3 manage.py dumpdata products_app --format json --indent 4 > products_app/fixtures/products.json
# Create your models here.

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.split(base_name)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1, 390148425)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f'products/{final_filename}'


class ProductsQuerySet(models.query.QuerySet):
    def filter_featured(self):
        return self.filter(featured=True)
    
    def search(self,query):
        lookups = (Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(tag__name__icontains=query) )
        return self.filter(lookups).distinct()

class FeaturedManager(models.Manager):
    def get_queryset(self):
        return ProductsQuerySet(self.model, using=self._db)
    
    def get_featured(self):
        found_featured = super().get_queryset().filter(featured=True)
        if found_featured:
            return found_featured
        else:
            return None
        
    def filtered_featured(self):
        return self.get_queryset().filter_featured()


class ProductsManager(models.Manager):
    def get_queryset(self):
        return ProductsQuerySet(self.model, using=self._db)
    
    def get_by_id(self, pk):
        qs = super().get_queryset().filter(pk=pk)
        if qs.count() == 1:
            return qs.first()
        return None
    
    def get_by_slug(self, slug_name):
        qs = super().get_queryset().filter(slug_name = slug_name)
        if qs.count() == 1:
            return qs.first()
        return None
    
    def search(self, query):
        return self.get_queryset().search(query)

class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    price= models.DecimalField(decimal_places=2, max_digits=10, default=39.99)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured = models.BooleanField(default=False)
    slug_name =  models.SlugField(default="", max_length=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_digital = models.BooleanField(default=False)

    objects = models.Manager()
    ftd = FeaturedManager()
    products = ProductsManager()

    def get_absolute_url(self):
        kwargs = {
            "slug_name": self.slug_name
        }
        return reverse("products:detail", kwargs=kwargs)
        #return (f"/products/{self.slug_name}/")

    def __str__(self):
        return self.name
    
    
    def get_downloads(self):
        qs = self.productfile_set.all()
        return qs

def upload_product_file_loc(instance, filename):
        if instance.product.slug_name:
            location = f"product/{instance.product.slug_name}/"
        return location + filename

class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=upload_product_file_loc,
        #storage=FileSystemStorage(location=settings.PROTECTED_ROOT)
        )
    is_free = models.BooleanField(default=False) #purchase required by default
    user_required = models.BooleanField(default=False)

    def __str__(self):
        return str(self.file.name)
    
    def generate_download_url(self):
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'S3DIRECT_REGION')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        if not secret_key or not access_key or not bucket or not region:
            return "/product-not-found/"
        PROTECTED_DIR_NAME = getattr(settings, 'PROTECTED_DIR_NAME', 'protected')
        path = f"{PROTECTED_DIR_NAME}/{str(self.file)}"
        aws_dl_object =  AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(path, new_filename=self.display_name)
        return file_url

    def get_download_url(self):
        return reverse("products:download", kwargs={"slug_name":self.product.slug_name, "pk":self.pk})
    
    @property
    def name(self):
        return get_filename(self.file.name)