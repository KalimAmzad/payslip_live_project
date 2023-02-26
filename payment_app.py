import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

import os
import yaml

from PIL import Image
from db_connection import get_database_connection
import pandas as pd
import base64
import io

st.set_page_config(
    page_title="Payslip Distribution",
    page_icon=":dolphin:",
    layout="wide",
    initial_sidebar_state="expanded",
)


with open('credintials.yml', 'r') as f:
    credintials = yaml.load(f, Loader=yaml.FullLoader)
    db_credintials = credintials['db']
    system_pass = credintials['system_pass']['admin']
    email_sender = credintials['email_sender']



cursor, db = get_database_connection()


cursor.execute("SHOW DATABASES")

databases = cursor.fetchall() ## it returns a list of all databases present
TEAMS = ['Management', 'HR', 'Expansion', 'Web Development', 'Technology', 'Accounts', 'Listing Sites', 'Marketing',
         'Email Marketing', 'PPC', 'Video Marketing', 'R&D', 'Reed', 'CS', 'Design', 'Web Publishing',
         'Digital Design', 'Product', 'External Affairs', 'IT Support', 'Brand Protection', 'Web Sales']

# st.write(databases)

# cursor.execute('''DROP TABLE payto IF EXISTS payto''')
# cursor.execute('''DROP TABLE payfor IF EXISTS payfor''')
# cursor.execute('''DROP TABLE bank IF EXISTS bank''')
# cursor.execute('''DROP TABLE transaction IF EXISTS transaction''')
# cursor.execute('''DROP TABLE concern IF EXISTS concern''')

# cursor.execute('''CREATE TABLE payto (id int AUTO_increment PRIMARY KEY,
#                                       name varchar(255))''')

# cursor.execute('''CREATE TABLE payfor (id int AUTO_increment PRIMARY KEY,
#                                         name varchar(255))''')

# cursor.execute('''CREATE TABLE bank (id int AUTO_increment PRIMARY KEY,
#                                         name varchar(255))''')

# cursor.execute('''CREATE TABLE concern (id int AUTO_increment PRIMARY KEY,
#                                         name varchar(255))''')

# cursor.execute('''CREATE TABLE transaction (id int AUTO_increment PRIMARY KEY,
#                                               bill_date date,
#                                               check_issue_date date,
#                                               amount float,
#                                               total float,
#                                               payto_id int,
#                                               payfor_id int,
#                                               bank_id int,
#                                               concern_id int,
#                                               FOREIGN KEY(payto_id) REFERENCES payto(id),
#                                               FOREIGN KEY(payfor_id) REFERENCES payfor(id),
#                                               FOREIGN KEY(bank_id) REFERENCES bank(id),
#                                               FOREIGN KEY(concern_id) REFERENCES concern(id))''')

# cursor.execute("show tables from payment")
# tables = cursor.fetchall()
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
        
def show_pdf(file_path):
    with open(file_path,"rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def payment():
    if 'flag' not in st.session_state:
        st.session_state.flag = 0

    with st.form(key='payment_submit_form', clear_on_submit=False):
        tables = ['payto', 'payfor', 'bank', 'concern']
        all_list = []
        for table in tables:
            cursor.execute(f"Select name from {table}")
            all_list.append([i[0] for i in cursor.fetchall()])

        bill_date = st.date_input('Billing Date')
        ck_date = st.date_input('Check Issue Date')
        pay_to = st.selectbox('Pay To', all_list[0])
        pay_for = st.selectbox('Pay For', all_list[1])
        amount = st.text_input('Amount')
        total = st.text_input('Total')
        bank = st.selectbox('Bank', all_list[2])
        concern = st.selectbox('Concern', all_list[3])
        check_no = st.text_input('Check No')
        notes = st.text_area('Remarks')
        document_upload = st.file_uploader('Upload Document', type=['txt','pdf', 'jpg', 'png', 'jpeg'], accept_multiple_files=True)
        if st.form_submit_button(label='Submit'):
            if not(bill_date and ck_date and pay_to and pay_for and amount and total and bank and concern and check_no):
                st.write('Please fill all the fields')
            else:
                st.session_state.flag = 1
                # st.success('Data Submitted Successfully')


    # st.write(st.session_state.flag)
    if st.session_state.flag:
        # st.write(final_parameter_calculation)

        with st.form(key='final', clear_on_submit=True):
             # st.write(final_parameter_calculation)

            if st.form_submit_button('Are you Sure to Payment?'):
                # st.write(final_parameter_calculation)
                st.session_state.flag = 0
                                # insert data into transaction table
                cursor.execute(f"Select id from payto where name = '{pay_to}'")
                payto_id = cursor.fetchone()[0]
                cursor.execute(f"Select id from payfor where name = '{pay_for}'")
                payfor_id = cursor.fetchone()[0]

                cursor.execute(f"Select id from bank where name = '{bank}'")
                bank_id = cursor.fetchone()[0]

                cursor.execute(f"Select id from concern where name = '{concern}'")
                concern_id = cursor.fetchone()[0]
                
                # st.write(document_upload.read())
                # st.write(document_upload.name)
                # st.write(document_upload.getvalue())
                # file = open(document_upload.read(),'rb')
                all_documents = []
                for file in document_upload:
                    st.write(file.name)
                    # st.write(file.getvalue())
                    # st.write(file.read())
                    if file is not None:
                        # Get the file name and extract the extension
                        file_name = file.name
                        # st.write(file_name)
                        file_extension = os.path.splitext(file_name)[1]
                        file_url = "./documents/" + file_name
                        all_documents.append(file_url)

                        # Save the file in its original format
                        with open(file_url, "wb") as f:
                            f.write(file.read())
                        st.success("File has been successfully saved to the directory.")


                query = "Insert into transaction (bill_date, check_issue_date, amount, total, payto_id, payfor_id, bank_id, concern_id, check_no, notes, documents) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (bill_date, ck_date, amount, total, payto_id, payfor_id, bank_id, concern_id, check_no, notes, str(all_documents))
                # st.write(query, values)
                cursor.execute(query, values)
                db.commit()

            else:
                st.write("Click above button If you are Sure")
    else:
        st.warning("Please fill up above form")

    if st.checkbox(f"Show all transaction data"):

        # cursor.execute(f'''DELETE FROM transaction WHERE id=3''')
        # cursor.fetchall()
        df = pd.read_sql('''SELECT t.*, pf.name AS payfor, pt.name AS payto, b.name AS bank, c.name AS concern
                                FROM transaction t
                                LEFT JOIN payfor pf ON t.payfor_id = pf.id
                                LEFT JOIN payto pt ON t.payto_id = pt.id
                                LEFT JOIN bank b ON t.bank_id = b.id
                                LEFT JOIN concern c ON t.concern_id = c.id
                                ''', con=db)
        
        # st.dataframe(df)

        # select the columns you want the users to see
        gb = GridOptionsBuilder.from_dataframe(df[['bill_date',
                                                'check_issue_date',
                                                'amount',
                                                'total',
                                                'payto',
                                                'payfor',
                                                'bank',
                                                'concern',
                                                'check_no',
                                                'notes']])
        # configure selection
        gb.configure_selection(selection_mode="single", use_checkbox=False)
        gb.configure_side_bar()
        gridOptions = gb.build()

        data = AgGrid(df,
                    gridOptions=gridOptions,
                    enable_enterprise_modules=True,
                    allow_unsafe_jscode=True,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

        selected_rows = data["selected_rows"]

        if len(selected_rows) != 0:
            # col1, col2, col3, col4 = st.columns(4)
            documents_urls = selected_rows[0]['documents']
            # st.write(documents_urls)
            documents_urls = documents_urls.strip('[]').split(', ')
            doc_text = False
            for document in documents_urls:
                # file_path += document
                if document:
                    if not doc_text:
                        st.title("Referenced Documents")
                        doc_text = True
                    file_extension = os.path.splitext(document)[1].replace("'", '')
                    if file_extension in [".png", ".jpg", ".jpeg"]:
                        # Display the image file
                        url=os.path.join(os.getcwd(), document.strip("'.//"))
                        st.image(url, width=None)
                    elif file_extension == ".pdf":
                        # Display a link to the pdf file
                        url=os.path.join(os.getcwd(), document.strip("'.//"))
                        show_pdf(url)
                        # st.markdown("[Open the PDF file]({})".format(url))
                    else:
                        # Display the contents of the text file
                        url=os.path.join(os.getcwd(), document.strip("'.//"))
                        with open(url, "r") as f:
                            st.text(f.read())
                else:
                    st.error("File does not exist.")

            # with col1:
            #     st.markdown("##### Name")
            #     st.markdown(f":orange[{selected_rows[0]['name']}]")
            # with col2:
            #     st.markdown("##### City")
            #     st.markdown(f":orange[{selected_rows[0]['city']}]")





def parameter_listing():
    cols = st.columns(4, gap='small')
    form_name = ['payfor', 'payto', 'bank', 'concern']
    for col, form in zip(cols, form_name):
        with col:
            name = st.text_input(f'Add new {form} option')
            with st.form(key=form):
                if st.form_submit_button('Submit'):
                    try:
                        exist_check_query = f"SELECT name FROM {form} WHERE name='{name}'"
                        cursor.execute(exist_check_query)
                        exist_check = cursor.fetchall()
                        if not exist_check:
                            raise Exception
                        col.warning(f'*{name.title()}* parameter already exists')
                    except:
                        query = f"INSERT INTO {form} (name) VALUES (%s)"
                        values = (name.title(),)
                        print(query, values)
                        cursor.execute(query, values)
                        db.commit()
                        col.success(f'*{name.title()}* parameter inserted successfully')

            if col.button(f"Show all {form.title()} Options"):
                cursor.execute(f'''SELECT name, created_at FROM {form}''')
                parameters = cursor.fetchall()
                df = pd.DataFrame(parameters, columns=['Name', 'Created At'])
                col.dataframe(df)
                # col.write(parameters)

def reporting():
    pass

def driver():
        st.sidebar.header('Select your requirement')
        task = st.sidebar.selectbox('',
                                    ('-----------------------------',
                                     'Payment', 
                                     'Parameter Insertion', 
                                     'Reporting'))

        if task == 'Payment':
            payment()
        elif task == 'Reporting':
            reporting()
        elif task == 'Parameter Insertion':
            parameter_listing()


def main():
    cols1, cols2, cols3 = st.columns((1, 4, 1))
    # cols2.title('Payment Management System')
    cols2.title('Payslip Management System')
    # cols2.write('A dynamic system for Al Razi Chemicals Ltd.')
    cols2.write('A dynamic system')


    username = st.sidebar.text_input('Username', 'Enter Your E-mail', key='user')

    password = st.sidebar.text_input("Enter a password", type="password", key='pass')


    st.session_state.login = st.sidebar.checkbox('Log In')
    
    if st.session_state.login:
        # if username.split('@')[-1] == "gmail.com" and password == system_pass:
        if username == "1" and password == "1":
            driver()
        
        else:
            st.sidebar.warning('Wrong Credintials')


if __name__ == '__main__':
    main()

