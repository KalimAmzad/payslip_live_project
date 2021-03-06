import mysql.connector as mysql
import pandas as pd
import time
from datetime import datetime
from PIL import Image
import json
import base64
import yagmail
import re
from re import search
# import smtplib

import streamlit as st
import streamlit.components.v1 as components
from streamlit import caching

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from sqlalchemy import create_engine
from mysql.connector.constants import ClientFlag

st.set_page_config(
    page_title="Payslip Distribution",
    page_icon=":dolphin:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# database localhost connection
# @st.cache()
def get_database_connection():
    db = mysql.connect(host = "localhost",
                      user = "root",
                      passwd = "root",
                      database = "PayslipDB",
                      auth_plugin='mysql_native_password')
    cursor = db.cursor()
    
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall() ## it returns a list of all databases present
    print(databases)

    return cursor, db

cursor, db = get_database_connection()



TEAMS = ['Management', 'HR', 'Expansion', 'Web Development', 'Technology', 'Accounts', 'Listing Sites', 'Marketing',
         'Email Marketing', 'PPC', 'Video Marketing', 'R&D', 'Reed', 'CS', 'Design', 'Web Publishing',
         'Digital Design', 'Product', 'External Affairs', 'IT Support', 'Brand Protection', 'Web Sales']
# mysql://b8d71fe9ee3a44:602e54ac@eu-cdbr-west-03.cleardb.net/heroku_e1641d5df4354dd?reconnect=true

# @st.cache(allow_output_mutation=True,)
# def get_database_connection():
#   engine = create_engine("mysql://be5fdbe5827510:89433526@eu-cdbr-west-01.cleardb.com/heroku_0ff92f1d6b43577")
#   connection = engine.raw_connection()
#   cursor = connection.cursor()
#   return cursor, connection

# cursor, connection = get_database_connection()
if 'login' not in st.session_state:
    st.session_state.login = False
    # driver()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# db_selection = mysql.connect(host="139.59.9.61",
#                              user="kalim",
#                              passwd="kalim",
#                              port=3306,
#                              database="payslip")
# db_selection_cursor = db_selection.cursor()

# db_selection_cursor.execute('''Select member, db_name, date from db_selection 
#                                 ORDER BY ID DESC LIMIT 1''')
# db_option = db_selection_cursor.fetchall()[0]


# db_selection_cursor.execute('''Select member, email, pass, date from email_selection 
#                                 ORDER BY ID DESC LIMIT 1''')
# email_option = db_selection_cursor.fetchall()[0]

# st.write(f'''Last Selected DB: {db_option[1]}
#       changed by {db_option[0]} at {db_option[2]}''')

# if db_option[1] == 'demo':
#     connection = mysql.connect(host="139.59.9.61",
#                                user="kalim",
#                                passwd="kalim20",
#                                port=3306,
#                                database="payslipdb_demo")
#     cursor = connection.cursor()
#     # st.write('Demo DB Selected')

# else:
#     connection = mysql.connect(host="139.59.9.61",
#                                user="kalim",
#                                passwd="kalim20",
#                                port=3306,
#                                database="payslipdb_original")
#     cursor = connection.cursor()
    # st.write("Original DB Selected")


# cursor = get_database_connection()

# cursor.execute('set max_allowed_packet=67108864')
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall() ## it returns a list of all databases present
print(databases)

# cursor.execute("DROP TABLE DailyMemberIsuues")
# cursor.execute("DROP TABLE members")
# cursor.execute('''CREATE TABLE members (id int AUTO_increment PRIMARY KEY,
#                                       name varchar(255),
#                                       nickname varchar(255),
#                                       email varchar(255),
#                                       dept varchar(255),
#                                       status varchar(255),
#                                       joining_date date,
#                                       account_number varchar(255),
#                                       gross_salary int)''')


# cursor.execute('''CREATE TABLE parameter (id int AUTO_increment PRIMARY KEY,
#                                         name varchar(255),
#                                         calculation_type varchar(255))''')

# cursor.execute('''CREATE TABLE monthlydisbursement (id int AUTO_increment PRIMARY KEY,
#                                               disburse_date date,
#                                               working_days int,
#                                               member_id int,
#                                               basic int,
#                                               home_rent_allowance int,
#                                               conveyance_allowance int,
#                                               medical_allowance int,
#                                               study_attendence int,
#                                               project_bonus int,
#                                               referral_bonus int,
#                                               eid_bonus int,
#                                               kpi int,
#                                               casual_leave int,
#                                               overtime int,
#                                               dearness_allowance int,
#                                               csr_sale_bonus int,
#                                               FOREIGN KEY(member_id) REFERENCES members(id))''')


width = 550
height = 450

# disburse_date    working_days    member_id    basic    home_rent_allowance
# conveyance_allowance medical_allowance   study_attendence   project_bonus   referral_bonus
# eid_bonus   kpi    casual_leave     overtime     dearness_allowance     csr_sale_bonus


def as_words(n):
    """Convert an integer n (+ve or -ve) to English words."""
    # lookups
    ones = ['zero', 'one', 'two', 'three', 'four',
            'five', 'six', 'seven', 'eight', 'nine', 
            'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
            'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
    tens = ['zero', 'ten', 'twenty', 'thirty', 'forty',
            'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    # negative case
    if n < 0:
        return "minus {0}".format(as_words(abs(n)))
    # 1000+
    for order, word in [(10**12, "trillion"), (10**9, "billion"),
                        (10**6, "million"), (10**3, "thousand")]:
        if n >= order:
            return "{0} {1}{2}".format(as_words(n // order), word,
                                       " {0}".format(as_words(n % order))
                                       if n % order else "")
    # 100-999
    if n >= 100:
        if n % 100:
            return "{0} hundred and {1}".format(as_words(n // 100), 
                                                as_words(n % 100))
        else:
            return "{0} hundred".format(as_words(n // 100))
    # 0-99
    if n < 20:
        return ones[n]
    else:
        return "{0}{1}".format(tens[n // 10],
                               "-{0}".format(as_words(n % 10)) 
                               if n % 10 else "")
        

def salary_disbursement():
    if 'flag' not in st.session_state:
        st.session_state.flag = 0
    with st.form(key='salary_submit_form', clear_on_submit=False):
        disburse_date = st.date_input('Salary Disbursement Date')
        working_days = st.text_input('Working Days')
        cursor.execute("Select id, name, gross_salary, email from members")
        members = cursor.fetchall()
        name_salary = dict()
        name_id = dict()
        name_email = dict()
        for m in members:
            name_salary[m[1]] = m[2]
            name_id[m[1]] = m[0]
            name_email[m[1]] = m[3]

        cursor.execute("Select name, calculation_type from parameter")
        parameters = cursor.fetchall()
        param_calculation = dict()
        for p in parameters:
            param_calculation[p[0]] = p[1]

        cursor.execute('''SHOW columns FROM monthlydisbursement''')
        monthly_dis_parameters = [i[0] for i in cursor.fetchall()]
        monthly_dis_parameters = monthly_dis_parameters[7:]
        monthly_dis_parameters.remove('working_days')
        monthly_dis_parameters.remove('total')
        # monthly_dis_parameters.remove('bonus_description')
        # monthly_dis_parameters.remove('remarks')
        # monthly_dis_parameters.remove('disburse_by')

        m_option = list(name_salary.keys())
        member = st.selectbox('Team Member Name', m_option)

        member_id = name_id[member]
        gross_salary = name_salary[member]
        basic_salary = gross_salary * 0.6
        home_rent_allowance = gross_salary * 0.3
        conveyance_allowance = gross_salary * 0.05
        medical_allowance = gross_salary * 0.05
        # study_attendence =

        # if 'final_parameter_calculation' not in st.session_state:
        final_parameter_calculation = dict()
        final_parameter_calculation['basic'] = basic_salary
        final_parameter_calculation['home_rent_allowance'] = home_rent_allowance
        final_parameter_calculation['conveyance_allowance'] = conveyance_allowance
        final_parameter_calculation['medical_allowance'] = medical_allowance
        final_parameter_calculation['gross_salary'] = gross_salary

        cols1, cols2, cols3 = st.beta_columns(3)
        total = gross_salary

        for k, md in enumerate(monthly_dis_parameters):
            # st.write(f'**{md}**')
            if k % 3 == 0:
                t = cols1.text_input(f'{md}', key=f'{md}')
            elif k % 3 == 1:
                t = cols2.text_input(f'{md}', key=f'{md}')
            else:
                t = cols3.text_input(f'{md}', key=f'{md}')
            if t and t != '0':
                if md in ['bonus_description', 'remarks', 'disburse_by']:
                    if t:
                        final_parameter_calculation[md] = t
                    else:
                        final_parameter_calculation[md] = 'N/A'
                elif param_calculation[md] == '%':
                    val = gross_salary * (int(t)/100)
                    final_parameter_calculation[md] = val
                    total += val
                    # st.write(total)
                elif param_calculation[md] == '???':
                    if md == 'casual_leave' and working_days:
                        deduct = (gross_salary/int(working_days)) * int(t)
                        final_parameter_calculation[md] = deduct * -1
                        total += (deduct*-1)
                        # st.write(total)

                    elif md != 'casual_leave':
                        final_parameter_calculation[md] = int(t)
                        total += int(t)
                        # st.write(total)
        final_parameter_calculation['total'] = total
        final_parameter_calculation['disburse_date'] = disburse_date
        final_parameter_calculation['member_id'] = int(member_id)
        if working_days:
            final_parameter_calculation['working_days'] = int(working_days)

        if st.form_submit_button('Save & Check'):
            if working_days:
                st.session_state.flag = 1

                # st.write(total)

                st.success(f"Please check the Payslip of **{member}**")
                st.write(final_parameter_calculation)

                # st.write(st.session_state.flag)
            else:
                st.warning("Please input the working day")

    # st.write(st.session_state.flag)
    if st.session_state.flag:
        # st.write(final_parameter_calculation)

        with st.form(key='final', clear_on_submit=True):
             # st.write(final_parameter_calculation)

            if st.form_submit_button('Are you Sure to Disburse?'):
                # st.write(final_parameter_calculation)
                st.session_state.flag = 0
                attrib_s = '('
                value_s = '('
                values = []
                # st.write(final_parameter_calculation)

                for f, v in final_parameter_calculation.items():
                    if f != 'gross_salary':
                        attrib_s = attrib_s + f + ','
                        value_s = value_s + '%s' + ','
                        values.append(v)

                attrib_s = attrib_s[:-1]
                value_s = value_s[:-1]
                attrib_s += ')'
                value_s += ')'

                # st.write(attrib_s)
                # st.write(value_s)

                query = f'''INSERT INTO monthlydisbursement {attrib_s}  VALUES {value_s}'''
                # values = tuple(final_parameter_calculation.values())
                # st.write(values)

                cursor.execute(query, values)
                connection.commit()
                try:
                    st.success(f'''Hi *{final_parameter_calculation['disburse_by']}*,  
                                Salary disbursement info is recorded to the DB successfully for **{member}**''')
                except:
                    st.success(f'''Hi,  
                                Salary disbursement info is recorded to the DB successfully for **{member}**''')

                del final_parameter_calculation['member_id']
                del final_parameter_calculation['disburse_date']

                basic = final_parameter_calculation['basic']
                del final_parameter_calculation['basic']
                print_string = '<b>Basic</b>' + \
                    ' = ' + str(int(basic, 2)) + '\n'
                st.write(f'**Basic: ** {str(int(basic, 2))}')

                home_rent_allowance = final_parameter_calculation['home_rent_allowance']
                del final_parameter_calculation['home_rent_allowance']
                print_string += '<b>Home Rent Allowance</b>' + \
                    ' = ' + str(int(home_rent_allowance, 2)) + '\n'
                st.write(
                    f'**Home Rent Allowance: ** {str(int(home_rent_allowance, 2))}')

                conveyance_allowance = final_parameter_calculation[
                    'conveyance_allowance']
                del final_parameter_calculation['conveyance_allowance']
                print_string += '<b>Conveyance Allowance</b>' + \
                    ' = ' + str(int(conveyance_allowance, 2)) + '\n'
                st.write(
                    f'**Conveyance Allowance: ** {str(int(conveyance_allowance, 2))}')

                medical_allowance = final_parameter_calculation[
                    'medical_allowance']
                del final_parameter_calculation['medical_allowance']
                print_string += '<b>Medical Allowance</b>' + \
                    ' = ' + str(int(medical_allowance, 2)) + '\n'
                st.write(
                    f'**Medical Allowance: ** {str(int(medical_allowance, 2))}')

                print_string += '<b>-------------------------------------------<b>' + '\n'
                st.write(f'-------------------------------')

                gross_salary = final_parameter_calculation['gross_salary']
                del final_parameter_calculation['gross_salary']
                print_string += '<b>Gross Salary' + ' = ' + \
                    str(int(gross_salary, 2)) + '\n'
                st.write(f'**Gross Salary: ** {str(int(gross_salary, 2))}')

                try:
                    bonus_description = final_parameter_calculation['bonus_description']
                    del final_parameter_calculation['bonus_description']
                except:
                    bonus_description = ''

                try:
                    disburse_by = final_parameter_calculation['disburse_by']
                    del final_parameter_calculation['disburse_by']
                except:
                    disburse_by = ''
                
                try:
                    remarks = final_parameter_calculation['remarks']
                    del final_parameter_calculation['remarks']
                except:
                    remarks = ''

                for k, v in final_parameter_calculation.items():
                    k_mail = '<b>'
                    k_sl = ''
                    for _ in k.split('_'):

                        k_mail += _.capitalize() + ' '
                        k_sl += _.capitalize() + ' '
                    k_mail += '</b>'

                    try:
                        print_string = print_string + k_mail + \
                            ' = ' + str(int(v, 2)) + '\n'
                        st.write(f'**{k_sl}: ** {str(int(v, 2))}')
                    except:
                        print_string = print_string + k_mail + ' = ' + v + '\n'
                        st.write(f'**{k_sl}: ** {v}')

                print_string += '<b>-------------------------------------------<b>' + '\n'
                st.write(f'-------------------------------')
                print_string += '<b>Total Remunaration</b>' + \
                    ' = ' + str(int(total, 2)) + '\n'
                st.write(f'**Total Remunaration: ** {str(int(total, 2))}')

                if bonus_description != '':
                    print_string += '<b>Bonus Description</b>' + ' = ' + bonus_description + '\n'
                    st.write(f'**Bonus Description: ** {bonus_description}')

                if remarks != '':
                    print_string += '<b>Remarks</b>' + ' = ' + remarks + '\n'
                    st.write(f'**Remarks: ** {remarks}')

                if disburse_by != '':
                    print_string += '<b>Disburse By</b>' + ' = ' + disburse_by + '\n'
                    st.write(f'**Disburse By: ** {disburse_by}')

                print_string += '\n\n<b>Regards</b>' + '\n' + \
                    '<br>Staff Asia</br>' + '\n' + \
                    'Al Oli Center, House:32, Road:2,' + 'Block:E, Uposhohar Sylhet, 3100'

                # st.write(print_string)
                receiver = name_email[member]
                body = f'''<h3>Dear {member}</h3>
                            Assalamualikum Warahmatullah. Hope your are doing well. 
                            <h4>Here is your payslip for {disburse_date}</h4>
                            {print_string}'''
                # st.write(body)


                try:
                    with open('email_credintials.yml', 'r') as f:
                        credintials = yaml.load(f)
                        email_id = credintials['payslip']['email']
                        email_pass = credintials['payslip']['pass']

                    yag = yagmail.SMTP(email_id, email_pass)
                    yag.send(
                        to=receiver,
                        subject=f"Payslip: {disburse_date}",
                        contents=body
                    )
                    st.success("Email payslip sent successfully")
                    st.balloons()
                    st.session_state.flag = 0
                except Exception as e:
                    st.write(e)
                    st.error("Error, email was not sent")
                del final_parameter_calculation

            else:
                st.write("Click above button If you are Sure")
    else:
        st.warning("Please fill up above form")


def member_register():
    with st.form(key='member_form'):
        name = st.text_input('Full Name')
        nickname = st.text_input('Nickname')
        email = st.text_input('Email')
        dept = st.selectbox('Team Name', TEAMS)
        status = st.selectbox('Status', ('Probationary', 'Permanent'))
        joining_date = st.date_input('Joining Date')
        account_number = st.text_input('Account Number')
        gross_salary = st.text_input('Gross Salary')
        if st.form_submit_button('Submit'):
            query = '''INSERT INTO members (name, nickname, email, dept, status, 
                                            joining_date, account_number, gross_salary) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            values = (name, nickname, email, dept, status,
                      joining_date, account_number, gross_salary)
            cursor.execute(query, values)
            connection.commit()
            st.success(f'{name} info inserted successfully')
            # cursor.execute("Select * from members")
            # members = cursor.fetchall()
            # st.write(members)


def parameter_listing():
    with st.form(key='parameter_listing_form'):
        name = st.text_input('Sarlary parameter Name')
        calculation_type = st.selectbox("What's the calculation type", ("%???"))
        sort_name = '_'.join(name.split())
        if st.form_submit_button('Submit'):
            query = "INSERT INTO parameter (name, calculation_type) VALUES (%s, %s)"
            values = (name, calculation_type)
            cursor.execute(query, values)
            connection.commit()
            st.success(f'*{name}* parameter inserted successfully')

            # add new column to monthlydisbursement table
            # query = f'''ALTER TABLE monthlydisbursement ADD {sort_name} varchar(255)'''
            # values = (sort_name,)
            # cursor.execute(query)
            # connection.commit()
            # st.success(f'*{name}* parameter inserted into monthlydisbursement successfully')

    if st.button("Show all salary parameter"):
        # cursor.execute('''SHOW columns FROM monthlydisbursement''')
        # parameters = [i[0] for i in cursor.fetchall()]
        # st.json(parameters[3:])

        cursor.execute('''Select name, calculation_type  from parameter''')
        parameters = cursor.fetchall()
        df = pd.DataFrame(parameters, columns=[
                          'parameter', 'Calculation Type'])
        st.table(df)



def driver(user_type):
        st.sidebar.header('Select your requirement')
        task = st.sidebar.selectbox('',
                                    ('-----------------------------',
                                     'Salary Disbursement', 
                                     'Member Registration', 'Salary parameter Insertion'))

        if task == 'Salary Disbursement':
            salary_disbursement()
        elif task == 'Member Registration':
            member_register()
        elif task == 'Salary parameter Insertion':
            parameter_listing()


def main():
    cols1, cols2, cols3 = st.columns((1, 4, 1))
    cols2.title('Payslip Distribution Portal')
    cols2.write('A real-life project of CSE-3532 course work')


    username = st.sidebar.text_input(
        'Username', 'Enter your staffasia mail', key='user')

    password = st.sidebar.text_input(
        "Enter a password", type="password", key='pass')


    st.session_state.login = st.sidebar.checkbox('Log In')
    
    if st.session_state.login:
        if username.split('@')[-1] =="gmail.com" and password == "admin123":
            driver()
        
        else:
            st.sidebar.warning('Wrong Credintials')


if __name__ == '__main__':
    main()
