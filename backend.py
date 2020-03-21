from tkinter import *
import sqlite3

root=Tk()
root.geometry("400x400")
conn=sqlite3.connect('database.db')
cur=conn.cursor()
cur.execute("Select d.id, d.title, d.query, u.username from doubts d,user u where d.reply is null and d.userid=u.id")
users = cur.fetchall()
var = IntVar()
for user in users:
    btn = Radiobutton(root, text=str(user[0])+". "+user[1]+" by "+user[3]+".", variable=var, value=user[0])
    btn.grid(row=user[0])
btn = Button(root, text="See Query and Answer", command=lambda:seeQuery(var.get(),users))
btn.grid(row=len(users)+1)
lbl = Label(root)
lbl.grid(row=len(users)+2)
lbl2 =Label(root)
lbl2.grid(row=len(users)+3)
def seeQuery(id,users):
    qry = users[id-1]
    lbl.config(text=qry[1])
    lbl2.config(text=qry[2])
    txtBox = Entry(root)
    txtBox.grid(row=len(users)+4)
    btn = Button(root, text="Answer", command=lambda:answer(txtBox.get(),str(id)))
    btn.grid(row=len(users)+5)
def answer(reply,id):
    cur.execute("UPDATE doubts SET reply=\""+reply+"\" where id="+str(id)+";")
    conn.commit()
root.mainloop()