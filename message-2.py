# pip install requests if needed
import sys

import requests
import json
import argparse
from dotenv import load_dotenv
import os
import csv
from datetime import datetime, date, timedelta
import mysql.connector

def connection_db():
    load_dotenv()
    
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    return conn

def insert_data(name, date, severity, description, score, more):
    conn = connection_db()

    cursor = conn.cursor()

    query = "INSERT INTO cve (name, date, severity, description, score, more) VALUES (%s, %s, %s, %s, %s, %s)"

    cursor.execute(query, (name, date, severity, description, score, more))
        
    conn.commit()

    cursor.close()
    conn.close()
    
def create_csv():
    data = [
    ['Numéro CVE', 'Date de publication', 'Sévérité', 'Description', 'CVSS score', 'Plus d\'info']
    ]

    with open('cves.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        
        for line in data:
            writer.writerow(line)
    
def insert_csv(name, date, severity, description, score, more):
    data = [
    [name, date, severity, description, score, more]
    ]

    with open('cves.csv', mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        
        for line in data:
            writer.writerow(line)

def display_cves(num_cves):
    url = 'https://access.redhat.com/hydra/rest/securitydata/cve.json'
    
    response = requests.get(url)

    if response.status_code == 200:
        cve_data = json.loads(response.content)

        print("Vous préférez afficher les CVEs dans un fichier JSON ou un fichier texte ?")
        print("1. JSON")
        print("2. CSV")
        print("3. Les deux (JSON et CSV)")
        format = input("Entrez votre choix : ")
        
        if format == '1':
            with open('cves.json', 'w') as f:
                json.dump(cve_data, f, indent=4)
            print("Les données sont enregistrées dans le fichier cves.json")
            print("Les données sont enregistrées dans la base de données")
        
        elif format == '2':          
            for cve in cve_data[:num_cves]:
                insert_csv(cve['CVE'], cve['public_date'], cve['severity'], cve['bugzilla_description'], cve['cvss3_score'], cve['resource_url'])
                insert_data(cve['CVE'], cve['public_date'], cve['severity'], cve['bugzilla_description'], cve['cvss3_score'], cve['resource_url'])
    
                print("")
                print("Les données sont enregistrées dans le fichier cves.csv")
                print("Les données sont enregistrées dans la base de données")
                print("")
                    
        elif format == '3':
            for cve in cve_data[:num_cves]:
                insert_csv(cve['CVE'], cve['public_date'], cve['severity'], cve['bugzilla_description'], cve['cvss3_score'], cve['resource_url'])
                insert_data(cve['CVE'], cve['public_date'], cve['severity'], cve['bugzilla_description'], cve['cvss3_score'], cve['resource_url'])
            
                print("")
                print("Les données sont enregistrées dans le fichier cves.csv")
                print("Les données sont enregistrées dans le fichier cves.json")
                print("Les données sont enregistrées dans la base de données")
                print("")
                
            with open('cves.json', 'w') as f:
                json.dump(cve_data, f, indent=4)
        else: 
            print("Choix invalide. Veuillez sélectionner une option valide.")
            exit()
        
        for cve in cve_data[:num_cves]:
            print(f"Numéro CVE : {cve['CVE']}")
            print(f"Date de publication : {cve['public_date']}")
            print(f"Sévérité : {cve['severity']}")
            print(f"Description: {cve['bugzilla_description']}")
            print(f"CVSS score: {cve['cvss3_score']}")
            print(f"Plus d'info: {cve['resource_url']}")
            print("")
            print("")
    else:
        print('Erreur lors de la récupération des données :', response.status_code)

def display_cve_info(cve_id):
    url = f'https://access.redhat.com/hydra/rest/securitydata/cve/{cve_id}'

    response = requests.get(url)

    if response.status_code == 200:
        cve = json.loads(response.content)

        with open(f'{cve_id}.txt', 'w') as f:
            print(f"Numéro CVE : {cve['CVE']}", file=f)
            print(f"Date de publication : {cve['public_date']}", file=f)
            print(f"Sévérité : {cve['severity']}", file=f)
            print(f"Description: {cve['bugzilla_description']}", file=f)
            print(f"CVSS score: {cve['cvss3_score']}", file=f)
            print(f"Plus d'info: {cve['resource_url']}", file=f)
            
        print(f"Numéro CVE : {cve['CVE']}", file=f)
        print(f"Date de publication : {cve['public_date']}", file=f)
        print(f"Sévérité : {cve['severity']}", file=f)
        print(f"Description: {cve['bugzilla_description']}", file=f)
        print(f"CVSS score: {cve['cvss3_score']}", file=f)
        print(f"Plus d'info: {cve['resource_url']}", file=f)
        
        insert_data(cve['CVE'], cve['public_date'], cve['severity'], cve['bugzilla_description'], cve['cvss3_score'], cve['resource_url'])
    else:
        print('Erreur lors de la récupération des données :', response.status_code)



def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--score', type=str)
    parser.add_argument('-S', '--scorev3', type=str)
    parser.add_argument('-se', '--severity', type=str)
    parser.add_argument('-p', '--product', type=str)
    parser.add_argument('-P', '--package', type=str)
    parser.add_argument('-c', '--cwe', type=str)
    parser.add_argument('-d', '--date', type=str)
    parser.add_argument('-b', '--before', type=str)
    parser.add_argument('-a', '--after', type=str)
    parser.add_argument('-d', '--date', type=str)
    
    args = parser.parse_args()

    url = 'https://access.redhat.com/hydra/rest/securitydata/cve.json?'

    if not len(sys.argv) > 1:
        while True:
            print("Sélectionnez une option :")
            print("1. Afficher un nombre de CVE spécifique")
            print("2. Afficher des informations sur une CVE précise")
            choice = input("Entrez votre choix : ")

            if choice == '1':
                num_cves = int(input("Combien de CVEs souhaitez-vous afficher ? "))
                print("")
                display_cves(num_cves)
            elif choice == '2':
                cve_id = input("Entrez le numéro CVE de la CVE que vous souhaitez afficher : ")
                print("")
                display_cve_info(cve_id)
            else:
                print("Choix invalide. Veuillez sélectionner une option valide.")
                print("")
    else:
        if args.score:
            url += "cvss_score=" + args.score
        if args.product:
            url += "product=" + args.product
        if args.cwe:
            url += "cwe=" + args.cwe
        if args.scorev3:
            url += "cvss3_score=" + args.scorev3
        if args.date:
            today = datetime.now()
            user_date = datetime.strptime(args.date, "%Y/%m/%d")
            delta = (today - user_date).days
            url += "created_days_ago=" + str(delta)
        if args.package:
            url += "package=" + args.package
        if args.severity:
            param = ""
            if args.severity == "1":
                param = "low"
            elif args.severity == "2":
                param = "moderate"
            elif args.severity == "3":
                param = "important"
            url += "severity=" + param
        if args.before:
            url += "before=" + args.before
        if args.after:
            url += "after=" + args.after
        # Get CVE at a specific date
        if args.date:
            url += "before=" + args.date + "&after=" + args.date
            
        response = requests.get(url)
        if response.status_code == 200:
            cve_data = json.loads(response.content)
        #parsing

if __name__ == '__main__':
    create_csv()
    load_dotenv()
    parseArgs()
