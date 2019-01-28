from subprocess import Popen, PIPE
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import re
import tabula
import json
import pandas as pd


def convert_to_text(fname):
    pages=None
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close

    text_list = text.split('\n')
    txt = text_list[:3]
    text = ' '.join(text_list[3:])


    print("###################")
    print(txt)

    ## spliting word from string

    word_list = text.split(' ')
    string_input = ""
    flag = 0
    for word in word_list:
        # print("*********")
        # print(word)

        if (word.lower() == 'tran'):
            break
        else:
            if(word.lower() == 'customer' or word.lower() == 'scheme' or word.lower() == 'currency' or word.lower() == 'for'):
                word = '\n'+word

            elif(word.lower() == 'statement'):
                word = '\n'+ word
                flag = 1
            elif(word.lower() == 'account' and flag==1):
                word = '\n'+word


        string_input += word + " "
    print("::::::::::::::::::::::")
    # print(string_input)

    file_name = fname.split('/')[-1]
    file_name = file_name.split('.')[0]
    # print(file_name)

    # write Content to .txt
    text_file = open("/home/dell/Documents/Aha-Loans/Production/PdfAnalyser/output/txt/output_"+file_name+".txt", "w")
    text = re.sub("\s\s+", " ", text)

    text_file.write("%s" % text)
    text_file.close()
    file_name_main = "output_"+file_name+".csv"
    csv_file = open("/home/dell/Documents/Aha-Loans/Production/PdfAnalyser/output/csv/"+file_name_main, "w")
    text = re.sub("\s\s+", " ", string_input)
    csv_file.write("%s" % string_input)
    csv_file.close()
    length_lines = len(string_input.split('\n'))
    # print("-----------",length_lines)
    convert_to_table(fname, string_input, txt)


def convert_to_table(fname, string_input, txt):

    df = tabula.read_pdf(fname)
    df.to_csv('output.csv', encoding='utf-8', index=False)
    # print(df)
    # Read remote pdf into DataFrame
    # convert PDF into CSV
    file_path = fname.split("/")[-1]
    file_name = file_path.split(".")[0]
    # print("-------------",file_name)
    file_name_csv_table = "output_table_"+file_name+".csv"
    tabula.convert_into(fname,"/home/dell/Documents/Aha-Loans/Production/PdfAnalyser/output/csv/"+file_name_csv_table , output_format="csv", row_start=10)
    to_json(string_input, df, txt)

def to_json(string_input, df, txt):
    final = dict()
    # print(string_input)
    flag = 0
    string_input += '\n'
    string_input += txt[2]
    data_extract = string_input.split('\n')
    final['Name'] = txt[1]
    final['Address'] = data_extract[0]

    for item in data_extract:
        print(item)
        try:
            data = item.split(":")
            final[data[0]] = data[1]
            flag = 1
        except:
            continue
    tenure = data_extract[-2]
    print("********************")
    tenure_from = tenure.split('(')[1]
    tenure_to  = tenure_from.split(')')[0]
    tenure = tenure_to.split(' ')
    final['from'] = tenure[2]
    final['to'] = tenure[6]
    # tenure_from = tenure[:3]
    # tenure_to = tenure[3:]
    # print(tenure_from)
    # print(tenure_to)
    # print(final)
        # final[data[0]] = data[1]
    # final =dict(item.split(":") for item in string_input.split('\n'))

    dict_result = dict()
    dict_result['Account'] = final
    dict_result['table'] = json.loads((df.to_json(orient='records')))
    json_result = json.dumps(dict_result)
    print(json_result)






convert_to_text("/home/dell/Documents/Aha-Loans/Production/PdfAnalyser/bank_statement/axis/test_Axis10.pdf")
