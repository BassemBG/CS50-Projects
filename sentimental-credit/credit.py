

def main():
    while True :
        number = input("please enter a credit card number : ")
        if number.isdecimal() and int(number) > 0:
            break
    #check if number given can be a credit card number
    if checksum_valid(number) == True :
        #check if AMEX number
        if len(number) == 15 and int(number[0]) == 3 :
            print("AMEX\n")
        #check if MASTERCARD number
        elif len(number) == 16 and int(number[0]) == 5 :
            print("MASTERCARD\n")
        #check if VISA number
        elif(len(number) == 16 or len(number) == 13) and int(number[0]) == 4 :
            print("VISA\n")
        else:
            print("INVALID\n")
    else:
        print("INVALID\n")



def sum_digits_multiply_2(number):
    length = len(number)
    sum = 0
    #scans the number from right to left starting with the second digit
    for i in range(length,2):
        #multiplies the digit by 2 following luhn's algorithm
        digit = int(number[length-1-i]) * 2
        if digit >= 10 :
            #get 1st digit
            remainder = digit % 10
            #add each digit seperately to the sum
            sum += remainder + ((digit - remainder) / 10)
        else:
            sum += digit
    return sum

def sum_remaining_digits(number):
    length = len(number)
    sum = 0
    #scans the number from right to left starting with the first digit
    for i in range(length,2):
        digit = int(number[length-i])
        #add each digit seperately to the sum
        sum += digit
    return sum

def checksum_valid(number):
    sum1 = sum_digits_multiply_2(number)
    sum2 = sum_remaining_digits(number)
    sum = sum1 + sum2
    if sum % 10 == 0:
        return True
    else :
        return False

if __name__ == "__main__" :
    main()

