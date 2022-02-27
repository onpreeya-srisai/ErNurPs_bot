import json
import os
from flask import Flask
from flask import request
from flask import make_response

#import requests
#import urllib.request
#from bs4 import BeautifulSoup


import psycopg2
import sys


os.putenv('LANG','en_US.UTF-8')
os.putenv('LC_ALL','en_US.UTF-8')
#เป็นตัวที่สร้างลิงค์ขึ้นมาใช้ในการรัน แต่จะเป็นตัวที่ใช้ได้แค่บนเครื่องของเราสำหรับรันทดสอบ ต้องรันในเทอร์มิเนอร์ถึงจะใช้ได้ทุกคน
app = Flask(__name__)
@app.route('/',methods=['POST'])

def MainFunction():
    question = request.get_json(silent=True,force=True)
    #เป็นการรับของข้อมูลจาก dialogflow เป็นข้อมูลแบบ json

    c,answer = generating_answer(question)
    #จำแนกข้อมูลที่ได้จาก json

    if len(c) > 0 :
        r = make_response(answer)
    else:
        r = make_response(question)
    #ตอบสนองข้อมูลกลับไปหา dialogflow
        
    r.headers['Content-Type'] = 'application/json'
    #รับค่าชนิดของข้อมูล
    
    return r

def generating_answer(question):
    print(json.dumps(question,indent = 4,ensure_ascii=False))
    #ปริ้นค่าที่ได้รับจาก question_from_dialogflow_dict

    intent = question["queryResult"]["intent"]["displayName"]
    #เก็บชื่อของ intent จาก dialogflow
    h = "xxx.xxx.xxx.xxx"
    db = "postgres"
    us = "postgres"
    pw = "your password"

    hm = "127.0.0.1"
    dbm = "project"
    usm = "postgres"
    pwm = "12345678" #เป็นการเชื่อมต่อบนเครื่องของตัวเอง

    # ตัวเชื่อมต่อกับฐานข้อมูล
    con = psycopg2.connect(host = h, database = db, user = us, password = pw,port=5432)
    cur = con.cursor()
    
    #Getting intent name form intent that recived from dialogflow.
    lineId = question["originalDetectIntentRequest"]["payload"]["data"]["source"][ "userId"]
    answer_str = ""

    #เลือกชื่อของ intent
    if(intent == 'วิชา'):
        sumject = question["queryResult"]["parameters"]["sumject"][0]
        cur.execute("INSERT INTO homeworks(line_id,sumject) VALUES ( '" + lineId + "' , '" + sumject + "')" )

    elif(intent == 'วันส่ง'):
        sumject = question["queryResult"]["outputContexts"][2]["parameters"]["sumject"][0]
        date = question["queryResult"]["parameters"]["date-time"]
        cur.execute("UPDATE homeworks SET deadline = '" + date + "' WHERE line_id = '" + lineId + "' and  sumject = '"+sumject+"'" )

    elif(intent == 'เพิ่มเติม'):
        sumject = question["queryResult"]["outputContexts"][1]["parameters"]["sumject"][0]
        content = question["queryResult"]["queryText"]
        cur.execute("UPDATE homeworks SET content = '" + content + "' WHERE line_id = '" + lineId + "' and sumject = '"+sumject+"'" )

    elif(intent == 'std_id'):
        id = id = question["queryResult"]["parameters"]["phone-number"]
        cur.execute("INSERT INTO users(line_id,std_id) VALUES ( '" + lineId + "','" + id + "')" )
        
    elif(intent == 'ชื่อ-นามสกุล'):
        fname,lname = (question["queryResult"]["parameters"]["person"]["name"]).split()
        cur.execute("UPDATE users SET  name= '" + fname + "' WHERE line_id = '" + lineId + "'" )
        cur.execute("UPDATE users SET  surname= '" + lname + "' WHERE line_id = '" + lineId + "' "  )
        
    elif(intent == 'คณะ'):
        dep = question["queryResult"]["parameters"]["Department"]
        cur.execute("UPDATE users SET department = '" + dep + "' WHERE line_id = '" + lineId + "'")
        
    elif(intent == 'ปี'):
        y = question["queryResult"]["parameters"]["number"]
        cur.execute("UPDATE users SET year = '" + y + "' WHERE line_id = '" + lineId + "'")
        
    elif(intent == 'เทอม'):
        m = question["queryResult"]["parameters"]["term"]
        cur.execute("UPDATE users SET term = '" + m + "' WHERE line_id = '" + lineId + "'")

    elif(intent == 'ตารางเรียน - เลขนิสิต'):
        numid = question["queryResult"]["parameters"]["numid"]
        b = "https://reg.src.ku.ac.th/res/table_std.php?id="+str(numid)+"&c_level=Bachelor"
        answer_str = b

    elif(intent == 'gpa'):
        cur.execute("select * from users where line_id = '" + lineId+"'")
        rows = cur.fetchall()
        if(len(rows)<=0):
            answer_str = "คุณต้องลงทะเบียนก่อนนะ"
        else:
            answer_str = "ตอนนี้คุณอยู่ปี "+str(rows[0][5])+" เทอม "+str(rows[0][6])+" ใช่ไหมครับ"

    elif(intent == 'กรอกแต่ละเทอม' or intent == 'กรอกแต่ละเทอม2' or intent == 'กรอกแต่ละเทอม3' or intent == 'กรอกแต่ละเทอม4' or intent == 'กรอกแต่ละเทอม5' or intent == 'กรอกแต่ละเทอม6' or intent == 'กรอกแต่ละเทอม7'):
        grade = question["queryResult"]["outputContexts"][2]["parameters"]["grade"]
        credit = question["queryResult"]["outputContexts"][2]["parameters"]["credit"]
        gradit = grade*credit

        cur.execute("select * from users where line_id = '" + lineId+"'")
        yt = cur.fetchall()
        y = yt[0][5]
        t = yt[0][6]
        
        cur.execute("select * from graders where line_id = '" + lineId+"'")
        rows = cur.fetchall()
        if(len(rows)==1):
            cur.execute("UPDATE graders SET gpa = " + str(grade) + ",credit = "+ str(credit) + ",gpaxcredit = "+ str(gradit) +" WHERE line_id = " +"'"+ lineId +"'"+ "and years = 1 and term = 1")
        elif(len(rows)==2):
            cur.execute("UPDATE graders SET gpa = " + str(grade) + ",credit = "+ str(credit) + ",gpaxcredit = "+ str(gradit) +" WHERE line_id = " +"'"+ lineId +"'"+ "and years = 1 and term = 2")
        elif(len(rows)==3):
            cur.execute("UPDATE graders SET gpa = " + str(grade) + ",credit = "+ str(credit) + ",gpaxcredit = "+ str(gradit) +" WHERE line_id = " +"'"+ lineId +"'"+"and years = 2 and term = 1")
        elif(len(rows)==4):
            cur.execute("UPDATE graders SET gpa = " + str(grade) + ",credit = "+ str(credit) + ",gpaxcredit = "+ str(gradit) +" WHERE line_id = " +"'"+ lineId +"'"+"and years = 2 and term = 2")
        elif(len(rows)==5):
            cur.execute("UPDATE graders SET gpa = " + str(grade) + ",credit = "+ str(credit) + ",gpaxcredit = "+ str(gradit) +" WHERE line_id = " +"'"+ lineId +"'"+"and years = 3 and term = 1")
        elif(len(rows)==6):
            cur.execute("UPDATE graders SET gpa = " + str(grade) + ",credit = "+ str(credit) + ",gpaxcredit = "+ str(gradit) +" WHERE line_id = " +"'"+ lineId +"'"+"and years = 3 and term = 2")
        elif(len(rows)==7):
            cur.execute("UPDATE graders SET gpa = " + str(grade) + ",credit = "+ str(credit) + ",gpaxcredit = "+ str(gradit) +" WHERE line_id = " +"'"+ lineId +"'"+"and years = 4 and term = 1")

        if(y==1 and t==1):
            many = 1
        elif(y==1 and t==2):
            many = 2
        elif(y==2 and t==1):
            many = 3
        elif(y==2 and t==2):
            many = 4
        elif(y==3 and t==1):
            many = 5
        elif(y==3 and t==2):
            many = 6
        elif(y==4 and t==1):
            many = 7
        elif(y==4 and t==2):
            many = 8
            
        if(len(rows)<=0 or len(rows)<many-1):
                
            cur.execute("select * from graders where line_id = '" + lineId+"'")
            rows = cur.fetchall()
            if(len(rows)==1):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',1,2)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 1 เทอม 2 ด้วยครับ"
            elif(len(rows)==2):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',2,1)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 2 เทอม 1 ด้วยครับ"
            elif(len(rows)==3):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',2,2)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 2 เทอม 2 ด้วยครับ"
            elif(len(rows)==4):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',3,1)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 3 เทอม 1 ด้วยครับ"
            elif(len(rows)==5):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',3,2)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 3 เทอม 2 ด้วยครับ"
            elif(len(rows)==6):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',4,1)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 4 เทอม 1 ด้วยครับ"
        elif(len(rows)==many-1):
            answer_str = "ผมขอหน่วยกิตเทอมนี้และเป้าหมายเกรด โดยพิมพ์ว่า เรียน18หน่วยเป้าหมาย4.00"

    elif(intent == 'ลงปีเทอมใหม่'):
        year = question["queryResult"]["outputContexts"][2]["parameters"]["yyear"]
        term = question["queryResult"]["outputContexts"][2]["parameters"]["tterm"]
        cur.execute("UPDATE users SET year = " + str(year) + ",term = "+ str(term) + " WHERE line_id = " +"'"+ lineId +"'")
        cur.execute("select * from users where line_id = '" + lineId+"'")
        yt = cur.fetchall()
        answer_str = "เพิ่มข้อมูลเรียบร้อยครับ ปัจจุบันคุณอยู่ปี "+str(yt[0][5])+" เทอม "+str(yt[0][6])+"นะครับ"

    elif(intent == 'ถามปีและเทอมซ้ำแล้วใช่'):
        cur.execute("select * from users where line_id = '" + lineId+"'")
        yt = cur.fetchall()
        y = yt[0][5]
        t = yt[0][6]
        if(y==1 and t==1):
            many = 1
        elif(y==1 and t==2):
            many = 2
        elif(y==2 and t==1):
            many = 3
        elif(y==2 and t==2):
            many = 4
        elif(y==3 and t==1):
            many = 5
        elif(y==3 and t==2):
            many = 6
        elif(y==4 and t==1):
            many = 7
        elif(y==4 and t==2):
            many = 8
            
        cur.execute("select * from graders where line_id = '" + lineId+"'")
        rows = cur.fetchall()
        if(many<2):
            answer_str = "เนื่องจากคุณเป็น freshy น้องใหม่เราจึงยังไม่เปิดให้ใช้บริการนะครับ"
        elif(len(rows)<=0 or len(rows)<many-1):
                
            cur.execute("select * from graders where line_id = '" + lineId+"'")
            rows = cur.fetchall()

            if(len(rows)==0):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',1,1)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 1 เทอม 1 ด้วยครับ"
            elif(len(rows)==1):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',1,2)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 1 เทอม 2 ด้วยครับ"
            elif(len(rows)==2):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',2,1)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 2 เทอม 1 ด้วยครับ"
            elif(len(rows)==3):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',2,2)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 2 เทอม 2 ด้วยครับ"
            elif(len(rows)==4):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',3,1)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 3 เทอม 1 ด้วยครับ"
            elif(len(rows)==5):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',3,2)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 3 เทอม 2 ด้วยครับ"
            elif(len(rows)==6):
                cur.execute("INSERT INTO graders(line_id,years,term) VALUES ( '" + lineId + "',4,1)" )
                answer_str = "ขอข้อมูลเกรดและหน่วยกิตของปี 4 เทอม 1 ด้วยครับ"
        elif(len(rows)==many-1):
            answer_str = "ผมขอหน่วยกิตเทอมนี้และเป้าหมายเกรด โดยพิมพ์ว่า เรียน18หน่วยเป้าหมาย4.00"

    elif(intent == 'หน่วยกิตปัจจุบันและเกรดปัจจุบัน' or intent =='กรอกเทอมครบแล้วถามหน่วยกิตเกรด'):
        creditnow = question["queryResult"]["outputContexts"][2]["parameters"]["creditnow"]
        targrade = question["queryResult"]["outputContexts"][2]["parameters"]["targrade"]
        sumcredit = creditnow
        sumx = 0
        
        
        cur.execute("select * from graders where line_id = '" + lineId+"'")
        rows = cur.fetchall()
        i = 0
        while(i<len(rows)):
            sumcredit = sumcredit + rows[i][4]
            sumx = sumx + rows[i][5]
            
            i = i+1

        a = sumcredit*4
        b = targrade/4
        c = b*a
        x = c-sumx
        gpa = (x/creditnow)
        x = '%.2f'%gpa
            
        
        if(gpa<=4.00):
            answer_str = x
        else:
            answer_str = "เป็นไปไม่ได้เลยครับ ไม่ร้องนะ"
        
    else:
        answer_str = "น่าจะมีอะไรผิดพลาด"

    con.commit()
    con.close()
    
    #answer_from_bot = answer_str
    answer_from_bot = {"fulfillmentText": answer_str}
    #สร้างคำตอบของ bot จากค่าที่ได้รับมาจากตัวเลือก

    answer_from_bot = json.dumps(answer_from_bot,indent=4)
    #แปลงคำตอบให้เป็นรูปแบบ json

    return answer_str,answer_from_bot


#ใช้ Flask ในการสร้างลิงค์บ้าน
if(__name__=='__main__'):
    port = int(os.getenv('PORT',5000))
    print("Starting app on port %d" %port)
    app.run(debug=True,host='0.0.0.0',threaded=True)

    
