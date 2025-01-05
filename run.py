import subprocess
import smtplib
import os
import datetime
import tomllib
from email.message import EmailMessage

def buy(UID,UCNT,Fixed_numbers):
    Return_value=[]
    Select_number=''
    if str(type(Fixed_numbers)) == "<class 'str'>":
        Fixed_numbers = eval(Fixed_numbers)
        
    if Fixed_numbers is not None:
        formatted_strings = [" " + ", ".join(map(str, sublist)) for sublist in Fixed_numbers]

        if len(formatted_strings) < UCNT:
            formatted_strings.extend([''] * (UCNT - len(formatted_strings)))

        Select_number = " " + " ".join(f"'{string}'" for string in formatted_strings)
    else:
        for _ in range(UCNT):
            Select_number += " ''"

    #구매 명령어 dhapi buy-lotto645 -y -p [사용자명(UID)] ''
    cmd = f'dhapi buy-lotto645 -y -p {UID}{Select_number}'
    print(cmd)
    rt_out = ""
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
    
    try:
        Out_value = rt_out.split("\n")
        Out_value = Out_value[Find_indexes_list(Out_value,"✅")[-1]:]
        Return_value.append(Out_value[0])
        
        for _ex in ["A","B","C","D","E"]:
            _ef = Find_indexes_list(Out_value,_ex)
            if not _ef:
                break
            Return_value.append(Number_processing(Out_value[_ef[0]].replace(" ", "")))
    except Exception as e:
        print(f"buy output ERRER: {e}")
        return f"buy output ERRER: {e}"

    #예치금조회 dhapi show-balance -p [사용자명(UID)]
    cmd = f'dhapi show-balance -p {UID}'
    print(cmd)
    rt_out = ""
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
    try:
        Out_value = rt_out.split("\n")
        Out_value = Out_value[Find_indexes_list(Out_value,"✅")[-1]:]
        Return_value.append(Out_value[0])
        Return_value.append(Balance_processing(Out_value[4].replace(" ", "")))
        Return_value = "\n".join(Return_value)
    except Exception as e:
        print(f"balance output ERRER: {e}")
        return f"balance output ERRER: {e}"
    
    return Return_value

def Find_indexes_list(lst, substring):
    return [index for index, item in enumerate(lst) if substring in item]

def Number_processing(text):
    text = text.split("│")
    return_text = f"슬롯\t: {text[1]}\n"
    return_text += f"Mode\t: {text[2]}\n"
    return_text += f"번호1\t: {text[3]}\n"
    return_text += f"번호2\t: {text[4]}\n"
    return_text += f"번호3\t: {text[5]}\n"
    return_text += f"번호4\t: {text[6]}\n"
    return_text += f"번호5\t: {text[7]}\n"
    return_text += f"번호6\t: {text[8]}\n"
    #print(return_text)
    return return_text

def Balance_processing(text):
    text = text.split("│")
    return_text = f"총예치금\t: {text[1]}\n"
    return_text += f"구매가능금액\t: {text[2]}\n"
    return_text += f"예약구매금액\t: {text[3]}\n"
    return_text += f"구매불가금액\t: {text[4]}\n"
    return_text += f"이번달누적금액\t: {text[5]}\n"
    #print(return_text)
    return return_text

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
            data = tomllib.load(f)
    except Exception as e :
        print(f"File open fail : {e}")
        exit()
        
    try:
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
            Fixed_numbers = profile_data.get("fixed_numbers")
            if 0 < int(CNT) <= 5:
                rt_out = buy(ID, int(CNT),Fixed_numbers)
                print("결과값", rt_out)
                #sand_mail(FW_Email,FW_Passwd,Email, rt_out)
            elif int(CNT) > 5:
                print("5장 이상 구매불가")
            else:
                print("미구매")
    except Exception as e:
        print(f"RUNNING MAIN ERROR: {e}")
