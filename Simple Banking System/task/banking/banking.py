# Write your code here
import sqlite3
import random

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card('
            'id INTEGER,'
            'number TEXT,'
            'pin TEXT,'
            'balance INTEGER DEFAULT 0'
            ');')


def generate_card_number():
    summ = 0
    last_numbers = [(random.randint(0, 9)) for i in range(0, 9)]
    for i in range(9):
        if i % 2 == 0:
            if last_numbers[i] < 5:
                summ += last_numbers[i] * 2
            else:
                summ += last_numbers[i] * 2 - 9
        else:
            summ += last_numbers[i]
    check_sum = (10 - (summ + 8) % 10) % 10
    if check_sum != 10:
        card_number = '400000' + ''.join(
            str(i) for i in last_numbers) + str(check_sum)
    else:
        card_number = '400000' + ''.join(str(i) for i in last_numbers) + '0'
    return card_number


def luhn_check(number):
    summ = 0
    for i in range(len(number) - 1):
        if i % 2 == 0:
            if int(number[i]) < 5:
                summ += int(number[i]) * 2
            else:
                summ += int(number[i]) * 2 - 9
        else:
            summ += int(number[i])
    if (summ + int(number[-1])) % 10 == 0:
        return 1
    else:
        return 0


state = 6

cards = {}

while state != 0:
    print('1. Create an account\n2. Log into account\n0. Exit')
    state = int(input())
    if state == 1:
        card_number = generate_card_number()
        cur.execute('SELECT number '
                    'FROM card '
                    'WHERE number=?;', (card_number,))
        while cur.fetchone():
            card_number = generate_card_number()
        pin = ''.join([str(random.randint(0, 9)) for i in range(0, 4)])
        print('Your card has been created \nYour card number:')
        print(card_number)
        print('Your card PIN:')
        print(pin)
        cards[card_number] = [pin, 0]
        cur.execute('INSERT INTO card(number, pin, balance)'
                    'VALUES(?, ?, ?);', (card_number, pin, 0))
        conn.commit()
    if state == 2:
        check_card = input('Enter your card number:\n')
        check_pin = input('Enter your PIN:\n')
        cur.execute('SELECT number, pin '
                    'FROM card '
                    'WHERE number=?;', (check_card,))
        to_check = cur.fetchone()
        if to_check:
            if check_pin == to_check[1]:
                print('You have successfully logged in!')
                log_number = to_check[0]
                while state != 0 or state != 5:
                    print('1. Balance\n'
                          '2. Add income\n'
                          '3. Do transfer\n'
                          '4. Close account\n'
                          '5. Log out\n'
                          '0. Exit')
                    state = int(input())
                    if state == 1:
                        cur.execute('SELECT balance '
                                    'FROM card '
                                    'WHERE number=?;', (log_number,))
                        balance = cur.fetchone()[0]
                        print('Balance:', balance)
                    elif state == 2:
                        inc = int(input('Enter income:\n'))
                        cur.execute('UPDATE card '
                                    'SET balance = balance+?'
                                    'WHERE number=?;', (inc, log_number))
                        conn.commit()
                        print('Income was added!')
                    elif state == 3:
                        print('Transfer')
                        transfer_number = input('Enter card number:\n')
                        if transfer_number == log_number:
                            print("You can't transfer money to the same account!")
                        elif not luhn_check(transfer_number):
                            print('Probably you made a mistake in the card number. Please try again!')
                        elif not cur.execute('SELECT number '
                                    'FROM card '
                                    'WHERE number=?;', (transfer_number,)).fetchone():
                            print('Such a card does not exist.')
                        else:
                            print('Enter how much money you want to transfer:')
                            transfer_money = int(input())
                            balance = cur.execute('SELECT balance '
                                        'FROM card '
                                        'WHERE number=?;', (log_number,)).fetchone()[0]
                            if balance >= transfer_money:
                                cur.execute('UPDATE card '
                                            'SET balance = balance-?'
                                            'WHERE number = ?', (transfer_money, log_number))
                                cur.execute('UPDATE card '
                                            'SET balance = balance+?'
                                            'WHERE number = ?', (transfer_money, transfer_number))
                                conn.commit()
                                print('Success!')
                            else:
                                print('Not enough money!')
                    elif state == 4:
                        cur.execute('DELETE FROM card '
                                    'WHERE number=?', (log_number,))
                        conn.commit()
                        print('The account has been closed!')
                    elif state == 5:
                        state = 6
                        break
                    elif state == 0:
                        break
            else:
                print('Wrong card number or PIN!')
        else:
            print('Wrong card number or PIN!')
conn.commit()
print('Bye!')
