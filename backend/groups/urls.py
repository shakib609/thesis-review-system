from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

router.register('marks', views.MarkViewset)
router.register('groups', views.GroupViewset)
router.register('batches', views.BatchViewset)
router.register('documents', views.DocumentViewset)
router.register('message-channels', views.MessageChannelViewset)
router.register('research-fields', views.ResearchFieldViewset)

app_name = 'groups'

urlpatterns = router.urls + [
    path('messages/', views.MessageAPI.as_view(), name='messages-api',),
]
