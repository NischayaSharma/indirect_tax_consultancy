from tkinter import *
import sqlite3

def destructive():
    child.withdraw()

def seequery(value):
    root.withdraw()
    global ans
    global label
    global child
    cur = conn.cursor()
    cur.execute("SELECT query FROM doubts WHERE id="+str(value))
    getit = cur.fetchall()
    child=Toplevel()
    child.geometry("400x400")
    mylabel=Label(child,text=getit[0][0]).pack()
    ans=Entry(child)
    ans.pack()
    mybtn=Button(child,text="Submit",command=lambda:mysubmit(ans.get(),value))
    mybtn.pack()


def mysubmit(value,id):
    cur.execute("UPDATE doubts SET reply=\"" + value + "\" where id=" + str(id) + ";")
    conn.commit()
    destructive()
    mymain()


def mymain():
    global root
    root = Tk()
    root.geometry("400x400")
    cur.execute("SELECT id, query FROM doubts WHERE reply is NULL")
    users=cur.fetchall()
    print(users)
    var=IntVar(root,0)
    for text in users:
        Radiobutton(root,text=text[1],variable=var,value=text[0]).pack()

    btn=Button(root,text="select",command=lambda:seequery(var.get()))
    btn.pack()

    root.mainloop()
conn=sqlite3.connect('database.db')
cur=conn.cursor()
mymain()
