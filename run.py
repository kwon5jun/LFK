import subprocess
import smtplib
import os
import datetime
import tomllib
import random
import logging
from email.message import EmailMessage

log_dir = "log" # 해당파일 아래 log폴더 생성하여 로그파일 기록
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"lotto_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file, mode='a'),
                        logging.StreamHandler()  # 콘솔 출력 추가
                    ])

def generate_lotto_numbers():
    return f" '{', '.join(map(str, sorted(random.sample(range(1, 46), 6))))}'"

def buy(UID,UCNT,Fixed_numbers):
    Return_value=[]
    Select_number=''
    
    if not Fixed_numbers:
        Fixed_numbers =[]
        
    if str(type(Fixed_numbers)) == "<class 'str'>":
        Fixed_numbers = eval(Fixed_numbers)
        
    if Fixed_numbers is not None:
        formatted_strings = [" " + ", ".join(map(str, sublist)) for sublist in Fixed_numbers]

        if len(formatted_strings) < UCNT:
            formatted_strings.extend([''] * (UCNT - len(formatted_strings)))

        Select_number = " " + " ".join(f"'{string}'" for string in formatted_strings)
    else:
        for _ in range(UCNT):
            Select_number += generate_lotto_numbers()
            #Select_number += " ''" #자동으로 원할경우
            
    #구매 명령어 dhapi buy-lotto645 -y -p [사용자명(UID)] ''
    cmd = f'dhapi buy-lotto645 -y -p {UID}{Select_number}'
    logging.info(f"command: {cmd}")
    rt_out = ""
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if "RuntimeError" in output:
                    return f"{output}"
                rt_out = rt_out + '\n' + output.strip()
    except Exception as e:
        logging.error(f"buy command ERRER: {e}")
        return f"buy command ERRER: {e}"
    
    try:
        Out_value = rt_out.split("\n")
        Out_value = Out_value[Find_indexes_list(Out_value,"✅")[-1]:]
        Return_value.append(Out_value[0])
        
        for _ex in ["A","B","C","D","E"]:
            _ef = Find_indexes_list(Out_value,_ex)
            if not _ef:
                break
            Return_value.append(f'{Number_processing(Out_value[_ef[0]].replace(" ", ""))}\n')
    except Exception as e:
        logging.error(f"buy output ERRER: {e}")
        return f"buy output ERRER: {e}"

    #예치금조회 dhapi show-balance -p [사용자명(UID)]
    cmd = f'dhapi show-balance -p {UID}'
    logging.info(f"command: {cmd}")
    rt_out = ""
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if "RuntimeError" in output:
                    return f"{output}"
                rt_out = rt_out + '\n' + output.strip()
    except Exception as e:
        logging.error(f"balance command ERRER: {e}")
        return f"balance command ERRER: {e}"
    
    try:
        Out_value = rt_out.split("\n")
        Out_value = Out_value[Find_indexes_list(Out_value,"✅")[-1]:]
        Return_value.append(f'{Out_value[0]}\n')
        Return_value.append(Balance_processing(Out_value[4].replace(" ", "")))
        Return_value = "\n".join(Return_value)
    except Exception as e:
        logging.error(f"balance output ERRER: {e}")
        return f"balance output ERRER: {e}"
    
    return Return_value

def Find_indexes_list(lst, substring):
    return [index for index, item in enumerate(lst) if substring in item]

def process_fields(text, labels):
    text = text.split("│")
    return "\n".join(f"{label}\t: {value}" for label, value in zip(labels, text[1:]))

def Number_processing(text):
    labels = ["슬롯", "Mode", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6"]
    return process_fields(text, labels)

def Balance_processing(text):
    labels = ["총예치금액", "구매가능금액", "예약구매금액", "구매불가금액", "이번달누적금액"]
    return process_fields(text, labels)

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
        logging.error(f"Email sending ERROR: {e}")


if __name__ == "__main__":
    try:
        with open(os.path.expanduser("~/.dhapi/credentials"), "rb") as f:
            data = tomllib.load(f)
    except Exception as e :
        logging.error(f"File open fail : {e}")
        exit()
        
    try:
        profile_data=data.get("Setting")
        FW_Email = profile_data.get("ForwardingEmail")
        FW_Passwd = profile_data.get("ForwardingPassword")
        
        for profile_name in data.keys():
            if profile_name == "Setting":
                continue
            profile_data = data.get(profile_name)
            logging.info(profile_data.get("name")+" 사용자")
            ID = profile_data.get("username")
            Email = profile_data.get("email")
            CNT = profile_data.get("buystat")
            Fixed_numbers = profile_data.get("fixed_numbers")
            if 0 < int(CNT) <= 5:
                rt_out = buy(ID, int(CNT),Fixed_numbers)
                logging.info(f"결과값 : {rt_out}")
                sand_mail(FW_Email,FW_Passwd,Email, rt_out)
            elif int(CNT) > 5:
                logging.warning("5장 이상 구매불가")
            else:
                logging.info("미구매")
    except Exception as e:
        logging.error(f"RUNNING MAIN ERROR: {e}")
