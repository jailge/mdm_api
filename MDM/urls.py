from django.conf.urls.static import static
from mdm_api import settings
from django.conf.urls import url
from MDM import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^api/v1/auth$', views.AuthView.as_view(), name='auth'),
    url(r'^api/v1/mdm/maindatas/$', views.MainDataList.as_view()),
    url(r'^api/v1/mdm/maindata/(?P<pk>[0-9]+)/$', views.MainDataDetail.as_view()),
    url(r'^api/v1/mdm/mdmpost/$', views.MdmPost.as_view()),
    url(r'^api/v1/mdm/mdmdatapost/$', views.MdmDataPost.as_view()),
    url(r'^api/v1/mdm/propertycategory/$', views.PropertyCategoryList.as_view()),
#    url(r'^api/v1/mdm/propertydetail/(?P<tuid>[0-9A-Za-z_]+)/$', views.PropertyDetailList.as_view()),
    url(r'^api/v1/mdm/propertydetail/$', views.PropertyDetailList.as_view()),
    url(r'^api/v1/mdm/propertydetailuid/$', views.PropertyDetailUid.as_view()),
    url(r'^api/v1/mdm/propertynamelist/$', views.PropertyNameList.as_view()),
    # 条件查询
    url(r'^api/v1/mdm/searchqualification/$', views.SearchQualification.as_view()),

    url(r'^api/v1/test/$', views.Test.as_view()),
    url(r'^api/v1/test/posttest/$', views.PostTest.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

