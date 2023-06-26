from django.db import models


class User(models.Model):
    tg_id = models.TextField()
    name = models.TextField()

    def __str__(self):
        return self.name


class Speaker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Изменено на ForeignKey
    start_date = models.TextField()
    end_date = models.TextField()
    subject = models.TextField()
    delay = models.BooleanField(default=False)


class Message(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest_messages')  # Изменено на ForeignKey
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE,
                                related_name='speaker_messages')  # Изменено на ForeignKey
    message = models.TextField()


from django.db import models

# Create your models here.
