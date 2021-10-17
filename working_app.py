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

    return cursor, db

cursor, db = get_database_connection()

cursor.execute("SHOW DATABASES")

databases = cursor.fetchall() ## it returns a list of all databases present

st.write(databases)

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
st.write(tables)