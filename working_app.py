import streamlit as st

import yagmail
import yaml

from PIL import Image
from db_connection import get_database_connection, get_all_members, get_single_member
# from search_members import get_all_members


st.set_page_config(
    page_title="Payslip Distribution",
    page_icon=":dolphin:",
    layout="wide",
    initial_sidebar_state="expanded",
)


with open('credintials.yml', 'r') as f:
    credintials = yaml.safe_load(f)
    db_credintials = credintials['db']
    system_pass = credintials['system_pass']['admin']
    email_sender = credintials['email_sender']


# database localhost connection
# @st.cache()


# def get_database_connection():
#     db = mysql.connect(host = "remotemysql.com",
#                       user = "vV66J5Vj2g",
#                       passwd = "5infQurhh1",
#                       database = "vV66J5Vj2g",
#                       auth_plugin='mysql_native_password')
#     cursor = db.cursor()

#     return cursor, db

cursor, db = get_database_connection()

all_members = get_all_members(db, cursor)

cursor.execute("SHOW DATABASES")

databases = cursor.fetchall() ## it returns a list of all databases present

TEAMS = ['Management', 'HR', 'Expansion', 'Web Development', 'Technology', 'Accounts', 'Listing Sites', 'Marketing',
         'Email Marketing', 'PPC', 'Video Marketing', 'R&D', 'Reed', 'CS', 'Design', 'Web Publishing',
         'Digital Design', 'Product', 'External Affairs', 'IT Support', 'Brand Protection', 'Web Sales']

# st.write(databases)

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

cursor.execute("show tables from PayslipDB")
tables = cursor.fetchall()
# st.write(tables)


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

        cursor.execute('''SHOW columns from monthlydisbursement''')
        # monthly_dis_parameters = []
        # for i in cursor.fetchall():
        #     monthly_dis_parameters.append(i[0])
        monthly_dis_parameters = [i[0] for i in cursor.fetchall()]
        monthly_dis_parameters = monthly_dis_parameters[7:]
        # monthly_dis_parameters.remove('working_days')
        # monthly_dis_parameters.remove('total')
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

        cols1, cols2, cols3 = st.columns(3)
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
                    attribute_salary_val = gross_salary * (int(t)/100)
                    final_parameter_calculation[md] = attribute_salary_val
                    total += attribute_salary_val
                    # st.write(total)
                elif param_calculation[md] == '৳':
                    if md == 'casual_leave' and working_days:
                        deduct = (gross_salary/int(working_days)) * int(t)
                        final_parameter_calculation[md] = -deduct 
                        total += (-deduct)
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

                del final_parameter_calculation['gross_salary']
                # del final_parameter_calculation['total']

                for f, v in final_parameter_calculation.items():
                    if f != 'total':
                        attrib_s += f + ','
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
                db.commit()
                try:
                    st.success(f'''Hi *{final_parameter_calculation['disburse_by']}*,  
                                Salary disbursement info is recorded to the DB successfully for **{member}**''')
                except:
                    st.success(f'''Hi,  
                                Salary disbursement info is recorded to the DB successfully for **{member}**''')

                
                # Sending Payslip to the employee Email 
                # del final_parameter_calculation['member_id']
                # del final_parameter_calculation['disburse_date']

                # basic = final_parameter_calculation['basic']
                # del final_parameter_calculation['basic']
                # print_string = '<b>Basic</b>' + \
                #     ' = ' + str(round(basic, 2)) + '\n'
                # st.write(f'**Basic: ** {str(round(basic, 2))}')

                # home_rent_allowance = final_parameter_calculation['home_rent_allowance']
                # del final_parameter_calculation['home_rent_allowance']
                # print_string += '<b>Home Rent Allowance</b>' + \
                # del final_parameter_calculation['gross_salary']
                #     ' = ' + str(round(home_rent_allowance, 2)) + '\n'
                # st.write(
                # del final_parameter_calculation['gross_salary']
                #     f'**Home Rent Allowance: ** {str(round(home_rent_allowance, 2))}')

                # conveyance_allowance = final_parameter_calculation[
                #     'conveyance_allowance']
                # del final_parameter_calculation['conveyance_allowance']
                # print_string += '<b>Conveyance Allowance</b>' + \
                # del final_parameter_calculation['gross_salary']
                #     ' = ' + str(round(conveyance_allowance, 2)) + '\n'
                # st.write(
                # del final_parameter_calculation['gross_salary']
                #     f'**Conveyance Allowance: ** {str(round(conveyance_allowance, 2))}')

                # medical_allowance = final_parameter_calculation[
                #     'medical_allowance']
                # del final_parameter_calculation['medical_allowance']
                # print_string += '<b>Medical Allowance</b>' + \
                # del final_parameter_calculation['gross_salary']
                #     ' = ' + str(round(medical_allowance, 2)) + '\n'
                # st.write(
                # del final_parameter_calculation['gross_salary']
                #     f'**Medical Allowance: ** {str(round(medical_allowance, 2))}')

                # print_string += '<b>-------------------------------------------<b>' + '\n'
                # st.write(f'-------------------------------')

                # gross_salary = final_parameter_calculation['gross_salary']
                # del final_parameter_calculation['gross_salary']
                # print_string += '<b>Gross Salary' + ' = ' + \
                # del final_parameter_calculation['gross_salary']
                #     str(round(gross_salary, 2)) + '\n'
                # del final_parameter_calculation['gross_salary']
                # st.write(f'**Gross Salary: ** {str(round(gross_salary, 2))}')

                # try:
                #     bonus_description = final_parameter_calculation['bonus_description']
                #     del final_parameter_calculation['bonus_description']
                # except:
                #     bonus_description = ''

                # try:
                #     disburse_by = final_parameter_calculation['disburse_by']
                #     del final_parameter_calculation['disburse_by']
                # except:
                #     disburse_by = ''
                
                # try:
                #     remarks = final_parameter_calculation['remarks']
                #     del final_parameter_calculation['remarks']
                # except:
                #     remarks = ''

                # for k, v in final_parameter_calculation.items():
                #     k_mail = '<b>'
                #     k_sl = ''
                #     for _ in k.split('_'):

                #         k_mail += _.capitalize() + ' '
                #         k_sl += _.capitalize() + ' '
                #     k_mail += '</b>'

                #     try:
                #         print_string = print_string + k_mail + \
                #             ' = ' + str(round(v, 2)) + '\n'
                #         st.write(f'**{k_sl}: ** {str(round(v, 2))}')
                #     except:
                #         print_string = print_string + k_mail + ' = ' + v + '\n'
                #         st.write(f'**{k_sl}: ** {v}')

                # print_string += '<b>-------------------------------------------<b>' + '\n'
                # st.write(f'-------------------------------')
                # print_string += '<b>Total Remunaration</b>' + \
                #     ' = ' + str(round(total, 2)) + '\n'
                # st.write(f'**Total Remunaration: ** {str(round(total, 2))}')

                # if bonus_description != '':
                #     print_string += '<b>Bonus Description</b>' + ' = ' + bonus_description + '\n'
                #     st.write(f'**Bonus Description: ** {bonus_description}')

                # if remarks != '':
                #     print_string += '<b>Remarks</b>' + ' = ' + remarks + '\n'
                #     st.write(f'**Remarks: ** {remarks}')

                # if disburse_by != '':
                #     print_string += '<b>Disburse By</b>' + ' = ' + disburse_by + '\n'
                #     st.write(f'**Disburse By: ** {disburse_by}')

                # print_string += '\n\n<b>Regards</b>' + '\n' + \
                #     '<br>Company Name</br>' + '\n' + \
                #     'Company Address, Road - X, Block - X, ABC R/A'

                # # st.write(print_string)
                # receiver = name_email[member]
                # body = f'''<h3>Dear {member}</h3>
                #             Assalamualikum Warahmatullah. Hope your are doing well. 
                #             <h4>Here is your payslip for {disburse_date}</h4>
                #             {print_string}'''
                # # st.write(body)


                # try:
                #     email_id = email_sender['email']
                #     email_pass = email_sender['pass']
                #     yag = yagmail.SMTP(email_id, email_pass)
                #     yag.send(
                #         to=receiver,
                #         subject=f"Payslip: {disburse_date}",
                #         contents=body
                #     )
                #     st.success("Email payslip sent successfully")
                #     st.balloons()
                #     st.session_state.flag = 0
                # except Exception as e:
                #     st.write(e)
                #     st.error("Error, email was not sent")
                # del final_parameter_calculation

            else:
                st.write("Click above button If you are Sure")
    else:
        st.warning("Please fill up above form")


def member_register():
    with st.form(key='member_form'):
        name = st.text_input('Full Name')
        # nickname = st.text_input('Nickname')
        email = st.text_input('Email')
        dept = st.selectbox('Team Name', TEAMS)
        status = st.selectbox('Status', ('Probationary', 'Permanent'))
        joining_date = st.date_input('Joining Date')
        account_number = st.text_input('Account Number')
        gross_salary = st.text_input('Gross Salary')
        
        if st.form_submit_button('Submit'):
            member_query = '''INSERT INTO members (name, email, dept, status, 
                                            joining_date, account_number, gross_salary) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            member_values = (name, email, dept, status, joining_date, account_number, gross_salary)
            cursor.execute(member_query, member_values)
            db.commit()
            st.success(f'{name} info inserted successfully')
            
    
    member_select_option = st.selectbox('Search Member', ('----------','All Member List', 'Search a single member?'))
    
    if member_select_option == 'Search a single member?':
        search_member = st.text_input('Enter the employee full name')
        
        cursor.execute("Select name, status, gross_salary from members")
        members = cursor.fetchall()

        member_found_flag = False
        
        for m in members:
            if search_member == m[0]:
                st.success('Hurrah! the employee is already registered')
                st.write(m)
                member_found_flag = True
                break

        if member_found_flag == False:
            st.warning('Sorry, not available.')

        # st.write(members)

    elif member_select_option == 'All Member List':
        cursor.execute('SELECT name, email, status, gross_salary from members')
        all_members = cursor.fetchall()

        st.write(all_members)



def parameter_listing():
    with st.form(key='parameter_listing_form'):
        name = st.text_input('Sarlary parameter Name')
        calculation_type = st.selectbox("What's the calculation type", ("%৳"))
        # sort_name = '_'.join(name.split())

        if st.form_submit_button('Submit'):
            query = "INSERT INTO parameter (name, calculation_type) VALUES (%s, %s)"
            values = (name, calculation_type)
            cursor.execute(query, values)
            db.commit()
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
        # df = pd.DataFrame(parameters, columns=[
        #                   'parameter', 'Calculation Type'])
        # st.table(df)

        st.write(parameters)


def driver():
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


    username = st.sidebar.text_input('Username', 'Enter Your E-mail', key='user')

    password = st.sidebar.text_input("Enter a password", type="password", key='pass')


    st.session_state.login = st.sidebar.checkbox('Log In')
    
    if st.session_state.login:
        if username.split('@')[-1] == "gmail.com" and password == system_pass:
            driver()
        
        else:
            st.sidebar.warning('Wrong Credintials')


if __name__ == '__main__':
    main()

