import json
import hashlib
import requests

#считывание числа в заданных границах
def get_number(l, r):
    while True:
        try:
            number = int(input())
            if l <= number <= r:
                return number
            else:
                print("Вне доступных границ. Повторите")
        except:
            print("Повторите")


#считывание почты
def get_email():
    while True:
        try:
            email = input()
            if '@' in email:
                return email
            else:
                print("Неверный формат. Повторите")
        except:
            print("Повторите")

#регистрация
def reg():
    while True:
        print("Логин")
        username = input()
        print("Почта")
        email = get_email()
        print("Пароль")
        password = input()
        print("Кто вы?")
        print("1. customer")
        print("2. chef")
        print("3. manager")
        get_role = get_number(1, 3)
        role = ["customer", "chef", "manager"][get_role - 1]
        data = dict()
        data["username"] = username
        data["email"] = email
        data["password"] = password
        data["role"] = role
        response = requests.post('http://localhost:3009/register', json=data)
        inf = response.json()
        if response.status_code == 201:
            print(inf["message"])
            return
        elif response.status_code == 400:
            print(inf["message"])
        else:
            print(inf["message"])

#вход в аккаунт
def log():
    while True:
        try:
            get_token = open('token')
            token = get_token.read()
            get_token.close()
            data = {'token': token}
            if requests.post('http://localhost:3009/login/token', json=data):
                print("Мы вас помним")
        except:
            print("Нет файла с токеном")

        print("Почта")
        email = get_email()
        print("Пароль")
        password = input()
        data = {
            'email': email,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'password_hash': password,
        }
        response = requests.post('http://localhost:3009/login', json=data)
        inf = response.json()
        print(inf["message"])
        if response.status_code == 200:
            print_token = open('token', 'w')
            print(inf['token'], file=print_token)
            print_token.close()
            return

#получение информации
def info():
    try:
        get_token = open('token')
        token = get_token.read()
        get_token.close()
        data = {'token': token}
        if requests.post('http://localhost:3009/login/token', json=data):
            print("Мы вас помним")
            person_inf = requests.post('http://localhost:3009/user_info', json=data)
            for key in person_inf.json():
                print(key, person_inf[key])
    except:
        print("Нет файла с токеном")

#меню
if __name__ == "__main__":
    while True:
        print("Возможные действия:")
        print("1. Регистрация нового пользователя")
        print("2. Вход пользователя в систему (авторизация)")
        print("3. Предоставление информации о пользователе")
        print("4. Конец")
        number = get_number(1, 4)
        if number == 1:
            reg()
        elif number == 2:
            log()
        elif number == 3:
            info()
        else:
            break
