from django.contrib import admin

from .models import (
    Main,
    Vuz,
    Training,
    Program,
    Regions,
    Districts,
    Ministries,
)

admin.site.register([Main,
                    Vuz,
                    Training,
                    Program,
                    Regions,
                    Districts,
                    Ministries,]
                    )