import subprocess
import smtplib
import os
import datetime
import tomli
from email.message import EmailMessage

def buy(UID,UCNT):
    rt_out = ''
    buycnt=' \'\''
    #구매 명령어 dhapi buy-lotto645 -y -p [사용자명(UID)] ''
    cmd = 'dhapi buy-lotto645'+' -y -p '+ UID + str(buycnt)*int(UCNT)
    print(cmd)
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                rt_out = rt_out + '\n' + output.strip()
    except Exception as e:
        print(f"buy command ERRER: {e}")
        return f"buy command ERRER: {e}"
    rt_out += '\n'
    
    #예치금조회 dhapi show-balance -p [사용자명(UID)]
    cmd = 'dhapi show-balance'+' -p '+ UID
    print(cmd)
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                rt_out = rt_out + '\n' + output.strip()
    except Exception as e:
        print(f"balance command ERRER: {e}")
        return f"balance command ERRER: {e}"
    
    return rt_out

def sand_mail(EMAIL_ADDR,EMAIL_PASSWORD,To_email,Sand_content):
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_ADDR, EMAIL_PASSWORD)

        dt_now = datetime.datetime.now()
        message = EmailMessage()
        message.set_content(Sand_content)
        message["Subject"] = "[로또6/45 구매결과]" + str(dt_now.date())
        message["From"] = EMAIL_ADDR
        message["To"] = To_email

        smtp.send_message(message)
        smtp.quit()
    except Exception as e:
        print(f"Email sending ERROR: {e}")


if __name__ == "__main__":
    try:
        with open(os.path.expanduser("~/.dhapi/credentials"), "rb") as f:
            data = tomli.load(f)

        profile_data=data.get("Setting")
        FW_Email = profile_data.get("ForwardingEmail")
        FW_Passwd = profile_data.get("ForwardingPassword")
        
        for profile_name in data.keys():
            if profile_name == "Setting":
                continue
            profile_data = data.get(profile_name)
            print(profile_data.get("name")+" 사용자")
            ID = profile_data.get("username")
            Email = profile_data.get("email")
            CNT = profile_data.get("buystat")
            if int(CNT) > 0:
                rt_out = buy(ID, str(CNT))
                print('결과값', rt_out)
                sand_mail(FW_Email,FW_Passwd,Email, rt_out)
            else:
                print("미구매")
    except Exception as e:
        print(f"RUNNING MAIN ERROR: {e}")
