from django.contrib import admin

from customers.models import Customer

"""
The admin.site.register() method is used to register a model with the Django admin interface. 
This allows us to manage the instances of the model through the admin interface, including creating, 
editing, and deleting instances.
In this file, we are registering the Customer model with the admin interface. 
Once registered, we can access the Customer model through the admin interface and perform CRUD 
(Create, Read, Update, Delete) operations on its instances.
"""

# Register your models here.
admin.site.register(Customer)