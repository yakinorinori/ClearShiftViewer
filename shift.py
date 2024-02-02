# -*- coding: utf-8 -*-
import os
import pdfplumber
import re
import datetime
import csv
import sys

def extract_employee_info_by_number(file_path, employee_number, name, csv_writer):
    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)
        date_pattern = re.compile(r'(\d{4}年\s*\d{1,2}月\s*\d{1,2}日)(\([\w\s]*\))?')
        info_pattern = re.compile(r'\d+\s+\d{2}:\d{2}\s+\d{2}:\d{2}\s+\d{1,2}:\d{2}\s+\d{1,2}:\d{2}')

        for page_num in range(num_pages):
            page_text = pdf.pages[page_num].extract_text()
            date_match = date_pattern.search(page_text)
            if date_match:
                date_str = date_match.group(1).replace('年', '/').replace('月', '/').replace('日', '').replace(' ', '')
                date_object = datetime.datetime.strptime(date_str, "%Y/%m/%d")
                date_str = date_object.strftime("%Y/%m/%d(%a)")

            info_matches = info_pattern.findall(page_text)
            for match in info_matches:
                if str(employee_number) in match.split()[0]:
                    info_parts = match.split()
                    csv_writer.writerow([date_str, info_parts[1], info_parts[2], info_parts[3], info_parts[4]])

if __name__ == "__main__":
    folder_path = sys.argv[1] if len(sys.argv) > 1 else "shiftPDF"
    employee_number = sys.argv[2] if len(sys.argv) > 2 else "925145"
    name = sys.argv[3] if len(sys.argv) > 3 else "山口 陽功"

    with open("output.csv", "w", newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["日付", "出勤時間", "退勤時間", "勤務時間", "休憩時間"])

        for file in os.listdir(folder_path):
            if file.endswith(".pdf"):
                file_path = os.path.join(folder_path, file)
                extract_employee_info_by_number(file_path, employee_number, name, csv_writer)
                print("Processed: {}".format(file))
                
    data = []
    with open('output.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            date_str = row[0]
            date_obj = datetime.datetime.strptime(date_str, "%Y/%m/%d(%a)")
            data.append([date_obj] + row[1:])

    data.sort(key=lambda x: x[0])

    with open('sorted_output.csv', 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(header)
        for row in data:
            csv_writer.writerow([row[0].strftime("%Y/%m/%d(%a)")] + row[1:])

    print("All files processed and sorted!")

