from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MainApp'
    def ready(self):
            from MainApp.models import ServerDataModel
    
            personal_key = os.environ.get("PERSONAL_KEY")
    
            if personal_key:
                try:
                    entry = ServerDataModel.objects.get(id=1)
                    entry.personal_key = personal_key
                    entry.save()
                except ObjectDoesNotExist:
                    ServerDataModel.objects.create(personal_key=personal_key)
