import random

odds = 22957480
balance = 0

while(True):
    print(f'Your balance is ${balance}.')
    #input("Press button to purchase ticket.")
    balance -= 2
    num = random.randint(1,odds)
    if(num == 5):
        print(f"You won!")
        balance += 3000
        exit(0)
    else:
        print("You lose.")
    