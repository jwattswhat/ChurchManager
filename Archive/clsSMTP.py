import yagmail

from clsConfig import CONFIG


class clsSMTP:
    def __init__(self):
        global CONFIG

        smtprows = CONFIG.get_Config_Family("SMTP")
        for smtp in range(len(smtprows)):
            match smtprows[smtp][0]:
                case "Server":
                    self.SMTPSERVER = smtprows[smtp][1]
                case "UserName":
                    self.SMTPUSERNAME = smtprows[smtp][1]
                case "Password":
                    self.SMTPPASSWORD = smtprows[smtp][1]
                case "Port":
                    self.SMTPPORT = int(smtprows[smtp][1])
                case "Key":
                    self.SMTPKEY = smtprows[smtp][1]

        self.email = yagmail.SMTP(self.SMTPUSERNAME, self.SMTPPASSWORD)

    def sendeMail(self, emailaddress, name, subject, msg, attachment):
        # print (self.SMTPUSERNAME,emailaddress,msg)
        if emailaddress != None:
            self.email.send(emailaddress, subject, msg, attachment)
