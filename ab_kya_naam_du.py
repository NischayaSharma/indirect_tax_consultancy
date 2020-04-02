from tkinter import *
import sqlite3
import smtplib


def destructive():
    child.withdraw()

def send_mail():
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    cur.execute("SELECT email FROM user WHERE id="+str(us_id[0][0]))
    recipient_email = cur.fetchall()

    server.login('tax.troubleshooterr@gmail.com','dbcsomrfzzhzdciw')

    subject='Query Answered!!!'
    body="Your query regarding the gst doubt has been answered please check the following"

    msg=f"Subject:{subject}\n\n{body}"

    server.sendmail('tax.troubleshooterr@gmail.com',recipient_email,msg)

    print("Hey Email has been Sent!!!!")

    server.quit()

def seequery(value):
    root.withdraw()
    global ans
    global label
    global child
    global us_id
    cur = conn.cursor()
    cur.execute("SELECT query FROM doubts WHERE id="+str(value))
    getit = cur.fetchall()
    cur.execute("SELECT query FROM doubts WHERE id="+str(value))
    getit = cur.fetchall()
    cur.execute("SELECT userid FROM doubts WHERE id="+str(value))
    us_id = cur.fetchall()
    print(us_id)
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
    send_mail()
    destructive()
    mymain()


def mymain():
    global root
    root = Tk()
    root.geometry("400x400")
    cur.execute("SELECT id, query FROM doubts WHERE reply is NULL")
    users=cur.fetchall()
    var=IntVar(root,0)
    for text in users:
        Radiobutton(root,text=text[1],variable=var,value=text[0]).pack()

    btn=Button(root,text="select",command=lambda:seequery(var.get()))
    btn.pack()

    root.mainloop()
conn=sqlite3.connect('database.db')
cur=conn.cursor()
mymain()
