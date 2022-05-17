try:
    import ldap
except:
    pass

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from engagement.models import SurveyProfile

class UserBackend(ModelBackend):

    def authenticate(self, request, **kwargs):
        ldap_username = kwargs['username']
        ldap_password = kwargs['password']
        print(ldap_username)
        print(ldap_password)

        try:
            connect = ldap.initialize("ldap://corp.knorr-bremse.com")
            connect.set_option(ldap.OPT_REFERRALS, 0)
            connect.simple_bind_s('corporate\\' + ldap_username, ldap_password)
            result = connect.search_s("DC=corp,DC=knorr-bremse,DC=com",
                            ldap.SCOPE_SUBTREE,
                            'mailNickname=' + ldap_username,
                            ['userprincipalname', 'uid', 'samaccountname', 'mailnickname'])

            print(result)

            ldap_user = result[0][1]['mailNickname'][0].decode('utf-8')        
        
        except:
            return None

        try:
            if ldap_username.lower() == ldap_user.lower():
                try:
                    user = User.objects.get(username=ldap_username.lower())
                    return user
                except:
                    return None
        except:
            return None
