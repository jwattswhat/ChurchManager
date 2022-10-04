import yagmail
   
yag_mail = yagmail.SMTP(user='pwbjwatt@gmail.com', password='bmyxndfvsznrkymi', host='smtp.gmail.com')
  
to= "jonathan@wattswhat.net"
subject = "Welcome to Journaldev!!"
body = ["World of infinite knowledge"]
 
yag_mail.send(to=to, subject=subject, contents=body)
print("Email has been sent successfully to the receiver's address.")
