from django.db import models
from django.urls import reverse

class master_Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])
    
class Product(models.Model):
    id = models.CharField(max_length=6, primary_key=True, unique=True, default="")
    product_name = models.CharField(max_length=100)
    master_Category = models.ForeignKey(
        master_Category,
        related_name='products',
        on_delete=models.CASCADE
        )
    sub_Category = models.CharField(max_length=100, default="")
    article_Type = models.CharField(max_length=50, default="")
    colour = models.CharField(max_length=50, default="")
    gender = models.TextField(max_length=50, default="Not Specified")
    season = models.CharField(max_length=50, default="")
    usage = models.CharField(max_length=20, default="")
    price = models.PositiveIntegerField()
    slug = models.SlugField(max_length=200, default="")
    image = models.ImageField(upload_to='shop/images/', default="")
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product_name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['product_name']),
            models.Index(fields=['-created_date'])
        ]
    def __str__(self):
        return self.product_name
    
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

class Contact(models.Model):
    msg_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50, default="")
    phone = models.IntegerField(default=10)
    desc = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
    
class Orders(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone = models.IntegerField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=6)