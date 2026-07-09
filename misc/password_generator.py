import random
passowrd=''.join(random.choices("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-=_+{}[]\"\\;',.<>/",k=random.randint(7,20)))
print(passowrd +" "+str(len(passowrd)))