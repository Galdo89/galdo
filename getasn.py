import requests            
import os   
import csv, smtplib, ssl   
from email.mime.text import MIMEText  
import shutil   
from datetime import datetime, timedelta     
from utilities import *        
    
notify=os.environ.get("ASN_NOTIFY", "false").lower() == "true"

f=open('secs.txt','r') 
lines=f.readlines()
f.close()   
  

trues=[]  
falses=[]
sectors=[]
dates=[]
r1=[]
r2=[]
for line in lines:
    check=False
    s1=line.split()[0]
    s2=line.split()[1]
    page="https://asn23.cineca.it/pubblico/miur/esito/"+s1+"%252F"+s2+"/2/6"
    l=getfulllist(page,s1+s2)
    #print(text)
    date=None
    if len(l)>0:
        check=True
        res2=evstats(l)
        if 'res2' not in locals():
            res2="-"
        date=None
        print(l)
        for item in l:
            if item["Esito"]=="Si":
                date=item["Data"]
                break
    page="https://asn23.cineca.it/pubblico/miur/esito/"+s1+"%252F"+s2+"/1/6"
    l=getfulllist(page,s1+s2)
    if len(l)>0:
        check=True
        res1=evstats(l)
        if 'res1' not in locals():
            res1="-"
        if not check or date is None:
            for item in l:
                if item["Esito"]=="Si":
                    date=item["Data"]
                    break
    #print(s1+s2,date)
    if check:
        dates.append(date)
        trues.append(line)
        sectors.append(line.split()[0]+'/'+line.split()[1])
        if 'res1' in locals():
            r1.append(str(round(res1*1000)/10))
        else:
            r1.append('-')
        if 'res2' in locals():
            r2.append(str(round(res2*1000)/10))
        else:
            r2.append('-')
    else:
        falses.append(line)
    print(line.split()[0]+'/'+line.split()[1]+' '+str(check))

if notify and len(trues) > 0:
    from_address = os.environ["ASN_EMAIL_FROM"]
    password = os.environ["ASN_EMAIL_PASSWORD"]

    recipients = os.environ.get("ASN_NOTIFY_TO", "").split()

    context = ssl.create_default_context()

    with open("notifications.out", "a") as no:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(from_address, password)

            for s in sectors:
                for email in recipients:
                    p = f"I have notified {email} for sector {s}\n"
                    no.write(p)

                    msg = MIMEText(f"Sono stati pubblicati i risultati del SSC {s}")
                    msg["Subject"] = "NUOVI RISULTATI ASN"
                    msg["From"] = from_address
                    msg["To"] = email

                    server.sendmail(
                        from_address,
                        email,
                        msg.as_string()
                    )
    
f1=open('present.txt','w')
f2=open('notpresent.txt','w')
f3=open('secs_ordered.txt','a')

for line in falses:
    f2.write(line)
i=-1
for line in trues:
    i+=1
    print('dates',i,dates[i])
    print('line',i,line)
    if (dates[i] is None):
        dates[i]=datetime.now().strftime('%d/%m/%Y')
    print(dates[i])
    f1.write('- '+dates[i]+' '+line)
    f3.write('')
    #f3.write('- '+dates[i]+' '+line)
    f3.write('- '+dates[i]+' '+line.rstrip('\n')+' PERCENTUALI: '+r1[i]+' (I) '+r2[i]+" (II)\n")

f1.close()
f2.close()
f3.close() 


shutil.copyfile('notpresent.txt','secs.txt')

f=open('secs_ordered.txt')
lines=f.readlines()
count=0
secs=[]
for line in lines:
    if len(line.split())>1:
        secs.append(line)
        count+=1
f.close()

f=open('README.md','w')
#f.write('visita il sito [https://www.risultatiasn.it](https://www.risultatiasn.it) (aggiornato in tempo reale)\n')
f.write('ESITI PUBBLICATI '+str(count)+'/190 \n')
secs.sort(key=lambda date: (datetime.strptime(date.split()[1], '%d/%m/%Y'), date.split()[2], date.split()[3]))
for sec in secs[::-1]:
    s1=sec.split()[2]
    s2=sec.split()[3]
    p1="https://asn23.cineca.it/pubblico/miur/esito/"+s1+"%252F"+s2+"/1/6"
    p2="https://asn23.cineca.it/pubblico/miur/esito/"+s1+"%252F"+s2+"/2/6" 
    f.write('\n')
    f.write(sec.partition("PERCENTUALI")[0]+" [I fascia]("+p1+") [II fascia]("+p2+") \n")

secs.sort(key=lambda date: (date.split()[2], date.split()[3]))
f.write("\n")
f.write("PERCENTUALI DI PASSAGGIO PER SETTORE:\n")
for sec in secs:
    s1=sec.split()[2]
    s2=sec.split()[3]
    f.write('\n')
    f.write(s1+'/'+s2+': '+sec.partition("PERCENTUALI")[2])



f.write('\n')
now = datetime.now()
hours=1
hoursToAdd = timedelta(hours = hours)
timeToPrint=now+hoursToAdd

f.write('UPDATED '+str(timeToPrint))
        
fs=open('spiegazione.txt','r')        
lines=fs.readlines()
fs.close()
for line in lines:
        f.write(line)
        
        
f.close()
        
        
