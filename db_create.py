from db_connection import get_database_connection


cursor, db = get_database_connection()

 
cursor.execute('''CREATE TABLE payto (id int AUTO_increment PRIMARY KEY,
                                      name varchar(255),
                                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)''')

cursor.execute('''CREATE TABLE payfor (id int AUTO_increment PRIMARY KEY,
                                        name varchar(255),
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)''')

cursor.execute('''CREATE TABLE bank (id int AUTO_increment PRIMARY KEY,
                                        name varchar(255),
                                        balance double DEFAULT 0.0,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)''')

cursor.execute('''CREATE TABLE concern (id int AUTO_increment PRIMARY KEY,
                                        name varchar(255),
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)''')

cursor.execute('''CREATE TABLE income (id int AUTO_increment PRIMARY KEY,
                                        bank_id int,
                                        amount double,
                                        notes longtext DEFAULT '',
                                        documents VARCHAR(512) DEFAULT '',
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)''')

cursor.execute('''CREATE TABLE transaction (id int AUTO_increment PRIMARY KEY,
                                              bill_date TIMESTAMP,
                                              check_issue_date TIMESTAMP,
                                              amount double,
                                              total double,
                                              payto_id int,
                                              payfor_id int,
                                              bank_id int,
                                              concern_id int,
                                              check_no VARCHAR(255),
                                              notes longtext DEFAULT '',
                                              documents VARCHAR(512) DEFAULT '',
                                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                              FOREIGN KEY(payto_id) REFERENCES payto(id),
                                              FOREIGN KEY(payfor_id) REFERENCES payfor(id),
                                              FOREIGN KEY(bank_id) REFERENCES bank(id),
                                              FOREIGN KEY(concern_id) REFERENCES concern(id))''')

cursor.execute("show tables from payment")
tables = cursor.fetchall()
print(tables)