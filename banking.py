from random import randrange
import sqlite3
connection = sqlite3.connect("card.s3db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, number TEXT, pin VARCHAR(4), balance INTEGER DEFAULT 0);")
connection.commit()
accounts = {}

def luhn_check(number):
    checksum = number[-1]
    check_number = number[:-1]
    return int(checksum) == calc_checksum(check_number)

def calc_checksum(number):
    card_digits = [int(digit) for digit in number]
    for count, digit in enumerate(card_digits):
        if count % 2 == 0:
            card_digits[count] = digit * 2
    for count, digit in enumerate(card_digits):
        if digit > 9:
            card_digits[count] = digit - 9
    total = sum(card_digits)
    if total % 10 == 0:
        return 0
    return 10 - (total % 10)

def create_account():
    account_number = str(randrange(1000000000))
    account_number = "0" * (9 - len(account_number)) + account_number
    card_number = "400000" + account_number
    card_number += str(calc_checksum(card_number))
    pin = str(randrange(10000))
    pin = "0" * (4 - len(pin)) + pin
    cursor.execute(f"INSERT INTO card (number, pin) VALUES ({card_number}, {pin})")
    connection.commit()
    print("\nYour card has been created", "Your card number:", card_number, "Your card PIN:", pin, sep="\n")
    print()

def log_in():
    login_number = input("Enter your card number:\n")
    login_pin = input("Enter card PIN:\n")
    cursor.execute("SELECT number, pin FROM card")
    results = cursor.fetchall()
    for account in results:
        pinn = "0" * (4 - len(account[1])) + account[1]
        accounts[account[0]] = pinn
    if login_number in accounts and accounts[login_number] == login_pin:
        print("\nYou have successfully logged in!\n")
        user_menu(login_number)
    else:
        print("Wrong card number or PIN!\n")
        main_menu()

def balance(login_number):
    cursor.execute(f"SELECT balance FROM card WHERE number = {login_number}")
    balance = cursor.fetchall()
    return balance[0][0]

def add_income(login_number):
    income = int(input("\nEnter Income:\n"))
    old_balance = balance(login_number)
    new_balance = income + old_balance
    cursor.execute("UPDATE card SET balance = {} WHERE number = {}".format(new_balance, login_number))
    connection.commit()
    print("Income was added!\n")

def transfer(login_number):
    print("Transfer\nEnter card number:")
    destin_card = input()
    if destin_card[0] != "4":
        print("Such a card does not exist.\n")
    elif not luhn_check(destin_card):
        print("Your probably made a mistake in the card number. Please try again!\n")
    elif destin_card == login_number:
        print("You can't transfer money to the same account!\n")
    elif destin_card not in accounts:
        print("Such a card does not exist.\n")
    else:
        amount = int(input("How much money do you want to transfer?\n"))
        old_sender_balance = balance(login_number)
        if amount > old_sender_balance:
            print("Not enough money!\n")
        else:
            new_sender_balance = old_sender_balance - amount
            old_receiver_balance = balance(destin_card)
            new_receiver_balance = old_receiver_balance + amount
            cursor.execute("UPDATE card SET balance = {} WHERE number = {}".format(new_sender_balance, login_number))
            cursor.execute("UPDATE card SET balance = {} WHERE number = {}".format(new_receiver_balance, destin_card))
            connection.commit()
            print("Success!")

def close_account(login_number):
    cursor.execute(f"DELETE FROM card WHERE number = {login_number}")
    connection.commit()
    print("The account has been closed!\n")
    main_menu()


def user_menu(login_number):
    while True:
        print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
        opt = input()
        if opt == "0":
            print("\nBye!")
            exit()
        elif opt == "1":
            print(f"\nBalance: {balance(login_number)}\n")
        elif opt == "2":
            add_income(login_number)
        elif opt == "3":
            transfer(login_number)
        elif opt == "4":
            close_account(login_number)
        elif opt == "5":
            print("\nYou have successfully logged out!\n")
            main_menu()

def main_menu():
    while True:
        print("""1. Create an account
2. Log into account
0. Exit""")
        opt = input()
        if opt == "0":
            print("\nBye!")
            exit()
        elif opt == "1":
            create_account()
        elif opt == "2":
            log_in()

main_menu()
