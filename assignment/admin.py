from django.contrib import admin
from .models import (
    Assignment,
    Subtask,
    Team,
    Submission,
    Review,
    File
)

admin.site.register(Assignment)
admin.site.register(Subtask)
admin.site.register(Team)
admin.site.register(Submission)
admin.site.register(Review)
admin.site.register(File)