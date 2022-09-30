from .models import *


def data_separator():

    sys= []
    user = User.objects.all()

    for u in user:
        if u.user_type is not None:
            sys.append(u)
            # u.delete()
    for i in sys:
        su = SystemUser()
        su.last_login = i.last_login
        su.email = i.email
        su.first_name = i.first_name
        su.middle_name = i.middle_name
        su.last_name = i.last_name
        su.password = i.password
        su.school = i.school
        su.argaoCampus = i.argaoCampus
        su.bariliCampus = i.bariliCampus
        su.carmenCampus = i.carmenCampus
        su.CCMECampus = i.CCMECampus
        su.daanbantayanCampus = i.daanbantayanCampus
        su.danaoCampus = i.danaoCampus
        su.dumanjugExt = i.dumanjugExt
        su.ginatilanExt = i.ginatilanExt
        su.mainCampus = i.mainCampus
        su.moalboalCampus = i.moalboalCampus
        su.nagaExt = i.nagaExt
        su.oslobExt = i.oslobExt
        su.pinamungajanExt = i.pinamungajanExt
        su.sanfernandoExt = i.sanfernandoExt
        su.sanfranciscoCampus = i.sanfranciscoCampus
        su.tuburanCampus = i.tuburanCampus
        su.user_type = i.user_type
        su.admin_sao = i.admin_sao
        su.system_admin = i.system_admin
        su.dean = i.dean
        su.campus_director = i.campus_director
        su.userid = i.id
        su.is_active = i.is_active
        su.staff = i.staff
        su.admin = i.admin
        su.timestamp = i.timestamp

        su.save()
