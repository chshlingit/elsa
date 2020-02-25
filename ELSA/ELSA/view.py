# from django.http import HttpResponse
 
# def hello(request):
#     return HttpResponse("Hello world !  ")

from django.shortcuts import render
 
def hello(request):
    context          = {}
    context['hello'] = 'Hello World!'
    return render(request, 'app/hello.html', context)

def add(request):
    # =====新增的程式碼=====# 
    if request.method == "POST":
        user_name = request.POST.get('user_name')  # 對應剛剛add.html 中的input name
        # user_img = request.FILES.get('user_image')
        user_mp4 = request.FILES.get('user_mp4')
        user = User(user_name=user_name,  user_mp4=user_mp4)
        user.save()
        response="Here's the text of the Web"
        try:
            print(user.user_mp4) #this will print the name of the file
            
            # in processing 
            os.system("python3 /home/user/Documents/autotrace/Main.py %s" % (user.user_mp4))
            #return HttpResponse("Here's the text of the Web")
            #processing done
        except StopIteration:
            print("No file was updated!")
        return render(request, 'app/feedback.html', locals())

    # =====新增的程式碼=====#
    return render(request, 'app/add.html', locals())