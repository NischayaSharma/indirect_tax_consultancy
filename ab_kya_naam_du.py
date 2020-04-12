from tkinter import *
import sqlite3
import smtplib
from PIL import ImageTk,Image
from tkinter import messagebox

def start():
    root.withdraw()
    mymain()

root=Tk()
root.geometry("960x600")
myimg = ImageTk.PhotoImage(Image.open("home2.png"))
mylabel_img = Label(root, image=myimg)
mylabel_img.place(x=0,y=0)
start_btn=Button(root,text="START",bg="black",fg="white",command=start)
start_btn.place(x=435,y=280)
start_btn.config(font=('Courier',20))



def destructive():
    child2.withdraw()

def send_mail():
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    cur.execute("SELECT email FROM user WHERE id="+str(us_id))
    recipient_email = cur.fetchall()

    server.login('tax.troubleshooterr@gmail.com','dbcsomrfzzhzdciw')

    subject='Query Answered!!!'
    body="Your query regarding the gst doubt has been answered please check the following"

    msg=f"Subject:{subject}\n\n{body}"

    server.sendmail('tax.troubleshooterr@gmail.com',recipient_email,msg)

    print("Hey Email has been Sent!!!!")
    messagebox.showinfo(title="Mail Sent", message="Hey! E-mail has been sent")

    destructive()
    mymain()

    server.quit()

def seequery(value):
    child1.withdraw()
    global ans
    global label
    global child2
    global us_id
    cur = conn.cursor()
    cur.execute("SELECT query,title,userid FROM doubts WHERE id="+str(value))
    getit = cur.fetchall()
    # cur.execute("SELECT query,title,userid FROM subqueries WHERE qryid="+str(value))
    # subq=cur.fetchall()
    # print(subq)
    us_id=getit[0][2]
    print(getit[0][2])
    child2=Toplevel()
    child2.geometry("960x600")
    myimg = ImageTk.PhotoImage(Image.open("home2.png"))
    mylabel_img = Label(child2, image=myimg)
    mylabel_img.place(x=0,y=0)
    mylabel=Label(child2,text=getit[0][0],bg="black",fg="white",wraplengt=390)
    mylabel.place(x=300,y=100)
    ans=Text(child2,width=48,height=15,bg="black",fg="white")
    ans.place(x=300,y=200)

    mybtn=Button(child2,text="Submit",command=lambda:mysubmit(ans.get('1.0', 'end'),value),bg="black",fg="white")
    mybtn.place(x=440,y=520)
    mybtn.config(font=("Courier", 20))
    child2.mainloop()


def mysubmit(value,id):
    cur.execute("UPDATE doubts SET reply=\"" + value + "\" where id=" + str(id) + ";")
    conn.commit()
    send_mail()




def mymain():
    global child1
    child1 = Toplevel()
    child1.geometry("960x600")
    myimg = ImageTk.PhotoImage(Image.open("home2.png"))
    mylabel = Label(child1, image=myimg)
    mylabel.place(x=0,y=0)
    cur.execute("SELECT id, title FROM doubts WHERE reply is NULL")
    users=cur.fetchall()
    # cur.execute("SELECT id, title FROM subqueries WHERE reply is NULL")
    # subq=cur.fetchall()
    # print(subq)
    var=IntVar(child1,0)
    linespace_y=50
    if len(users) == 0:
        no_ques = Label(child1, text="No more questions remaining")
        no_ques.place(x=100, y=80)
        no_ques.config(font=('Courier', 35))
    else:
        for text in users:
            Radiobutton(child1,text=text[1],variable=var,value=text[0],bg="black",fg="white",selectcolor="black").place(x=90,y=linespace_y)
            linespace_y+=30

    btn=Button(child1,text="select",command=lambda:seequery(var.get()),bg="black",fg="white")
    btn.place(x=420,y=525)
    btn.config(font=("Courier", 20))

    child1.mainloop()
conn=sqlite3.connect('database.db')
cur=conn.cursor()
root.mainloop()

