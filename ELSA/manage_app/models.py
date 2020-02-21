from django.db import models

# Create your models here.

class User(models.Model):
    user_name = models.CharField(max_length=100)#CharField 代表字符串的model的一個屬性

    #user_image = models.ImageField(upload_to='image/') #ImageField 代表圖片的的一個屬性
    
    user_mp4 = models.FileField(upload_to='user_mp4/') #introduce 是一個檔案，在資料庫中會記錄他的路徑
    
    def __str__(self):
        return self.user_name
    