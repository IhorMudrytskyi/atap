import psycopg2
import streamlit as st

connection = psycopg2.connect(
    host = st.secrets["psql"]["host"],
    user = st.secrets["psql"]["user"],
    port = st.secrets["psql"]["port"],
    database = st.secrets["psql"]["database"],
    password = st.secrets["psql"]["password"]
)

cursor = connection.cursor()

connection.autocommit = True

tab = st.tabs(["Авторизація", "Реєстрація", "Забув логін/пароль"])

with tab[0]:
    auth_login = st.text_input("Логін").replace(" ", "")
    auth_password = st.text_input("Пароль", type='password').replace(" ", "")
    if st.button("Увійти"):
        cursor.execute("select login, password from auth where login = %s and password = %s;",(auth_login, auth_password))
        auth_result = cursor.fetchone()
        if auth_result:
            st.success("Ви успішно авторизувались!")
            st.header("Дані користувача:")
            cursor.execute("""
            select first_name, last_name, email
            from user_info
            join auth on user_info.id = auth.id
            where auth.login = %s and auth.password = %s;""",(auth_login, auth_password))
            st.text(f"Ім'я: {auth_result[0]}")
            st.text(f"Прізвище: {auth_result[1]}")
            st.text(f"Електронна пошта: {auth_result[2]}")
        else:
            st.warning("Неправильно введені логін чи пароль!")

with tab[1]:
    reg_first_name = st.text_input("Ім'я ").replace(" ", "")
    reg_last_name = st.text_input("Прізвище ").replace(" ", "")
    reg_email = st.text_input("Електронна пошта ").replace(" ", "")
    reg_login = st.text_input("Логін ").replace(" ", "")
    reg_password = st.text_input("Пароль ").replace(" ", "")
    if st.button("Створити акаунт"):
        cursor.execute("select login from auth where login = %s;",(reg_login,))
        login_result = cursor.fetchone()
        if login_result:
            st.warning("Користувач з таким іменем вже існує!")
        else:
            cursor.execute("select email from user_info where email = %s;",(reg_email,))
            email_result = cursor.fetchone()
            if email_result:
                st.warning("Користувач з такою електронною поштою вже існує!")
            else:
                cursor.execute("insert into auth(login, password) values (%s, %s) returning id;",(reg_login, reg_password))
                reg_id = cursor.fetchone()
                cursor.execute("insert into user_info(id, first_name, last_name, email) values (%s, %s, %s, %s);",(reg_id, reg_first_name, reg_last_name, reg_email))
                st.success("Акаунт успішно створено!")
with tab[2]:
    zab_first_name = st.text_input("Ім'я  ").replace(" ", "")
    zab_last_name = st.text_input("Прізвище  ").replace(" ", "")
    zab_email = st.text_input("Електронна пошта  ").replace(" ", "")
    if st.button("Нагадати"):
        cursor.execute("""select auth.login, 
                       auth.password from auth 
                       join user_info on auth.id = user_info.id 
                       where user_info.first_name = %s
                       and user_info.last_name = %s
                       and user_info.email = %s;""",(zab_first_name, zab_last_name, zab_email))
        zab_result = cursor.fetchone()
        if zab_result:
            st.header("Дані для авторизації: ")
            st.text(f"Логін: {zab_result[0]}")
            st.text(f"Пароль: {zab_result[1]}")
        else:
            st.warning("Користувача з такими даними не знайдено!")
