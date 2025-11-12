import os

def help():
    print("Developer   : Niranjan Kumar K")
    print("Email Id    : hackerenvironment1514@gmail.com")
    print("Description : This module for creating simple data bases")
    print("All Built in Functions are given bellow")
    print(" ------------------------------------ ")
    print("|SI.NO  |FUNCTION                    |")
    print("|-------|----------------------------|")
    print("|1      |create()                    |")
    print("|-------|----------------------------|")
    print("|2      |add()                       |")
    print("|-------|----------------------------|")
    print("|3      |delete()                    |")
    print("|-------|----------------------------|")
    print("|4      |view()                      |")
    print("|-------|----------------------------|")
    print("|5      |update()                    |")
    print("|-------|----------------------------|")
    print("|6      |drop()                      |")
    print("|-------|----------------------------|")
    print("|7      |IDLE()                      |")
    print(" ------------------------------------ ")

def IDLE():
    print("EXIT : ctrl+D")
    os.system("python")

def create():
    fn=input("Enter Data Base name :\n")
    if '.' not in fn:
        fn=fn+'.kni'
    f=open(fn,'w')
    n=int(input("Enter no.of coloums:\n"))
    f.write(str(n)+'|')
    f.close()
    print(f"Succesfully Created your {fn} Data Base !")

def add():
    fn=input("Enter Data Base name :\n")
    if '.' not in fn:
        fn=fn+'.kni'
    f=open(fn,"r")
    c=f.read().split('|')
    f.close()
    t=int(c[0])
    data=[]
    for i in range(1,len(c)):
        if c[i].strip()!='':
            data.append(eval(c[i]))
    n=int(input("Enter no.of tuples :\n"))
    for i in range(n):
        l=[]
        for j in range(t):
            l.append(input(f"Enter {i+1} tuple {j+1} coloum:\n"))
        data.append(l)
    f=open(fn,"w")
    f.write(str(t)+'|')
    for i in data:
        f.write(str(i)+'|')
    f.close()
    print(f"Succesfully Added Data into {fn} Data Base !")

def view():
    fn=input("Enter Data Base name :\n")
    if '.' not in fn:
        fn=fn+'.kni'
    f=open(fn,"r")
    c=f.read().split('|')
    f.close()
    t=int(c[0])
    data=[]
    for i in range(1,len(c)):
        if c[i].strip()!='':
            data.append(eval(c[i]))
    for i in range(len(data)):
        for j in range(t):
            print(f"{data[i][j]:^15}",end='|')
        print()

def delete():
    fn=input("Enter Data Base name :\n")
    if '.' not in fn:
        fn=fn+'.kni'
    f=open(fn,"r")
    c=f.read().split('|')
    f.close()
    t=int(c[0])
    data=[]
    for i in range(1,len(c)):
        if c[i].strip()!='':
            data.append(eval(c[i]))
    r=int(input("Enter row to delete :\n"))
    r=r-1
    if 0<=r<len(data):
        del data[r]
    f=open(fn,"w")
    f.write(str(t)+'|')
    for i in data:
        f.write(str(i)+'|')
    f.close()
    print(f"Row Deleted Successfully from {fn} Data Base !")

def update():
    fn=input("Enter Data Base name :\n")
    if '.' not in fn:
        fn=fn+'.kni'
    f=open(fn,"r")
    c=f.read().split('|')
    f.close()
    t=int(c[0])
    data=[]
    for i in range(1,len(c)):
        if c[i].strip()!='':
            data.append(eval(c[i]))
    r=int(input("Enter row to update :\n"))
    r=r-1
    if 0<=r<len(data):
        for j in range(t):
            data[r][j]=input(f"Enter new value for column {j+1}:\n")
    f=open(fn,"w")
    f.write(str(t)+'|')
    for i in data:
        f.write(str(i)+'|')
    f.close()
    print(f"Row Updated Successfully in {fn} Data Base !")

def drop():
    fn=input("Enter Data Base name :\n")
    if '.' not in fn:
        fn=fn+'.kni'
    if os.path.exists(fn):
        os.remove(fn)
        print(f"{fn} Data Base Deleted Successfully !")
    else:
        print(f"{fn} Data Base not found !")
