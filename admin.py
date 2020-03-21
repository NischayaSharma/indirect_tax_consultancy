from tkinter import *
import sqlite3

root=Tk()
root.geometry("400x400")

conn=sqlite3.connect('database.db')
cur=conn.cursor()
cur.execute("SELECT query from doubts")
list0=cur.fetchall()
print(list0)
cur.close()
conn.close()
count=0
value="0"
def myfunction(i):
    textarea2.delete(0,END)
    global count
    count = count + 1
    print(count)
    rep=textarea2.get()
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(f'UPDATE doubts SET reply="{rep}" where id="{count}"')

    cur.close()
    conn.close()

    global value
    #textarea1.delete(0,END)
    textarea1 = Label(root, text=value)
    textarea1.grid(row=0)
    value=str(list0[i])




textarea2=Entry(root,width=15)
textarea2.grid(row=1)
submit=Button(root,text="Submit",command=lambda:myfunction2(count))
submit.grid(row=2)
next=Button(root,text="Next",command=lambda:myfunction(count))
next.grid(row=3)






root.mainloop()




