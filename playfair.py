from pprint import pprint


def matrix(key):
    matrix = []

    # add unique key elements
    for e in key:
        if e.upper() not in matrix:
            matrix.append(e.upper())

    letters = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

    # add remaining alphabets
    for e in letters:
        if e.upper() not in matrix:
            matrix.append(e.upper())

    # split 25 elements into 5x5 matrix
    return [matrix[i:i + 5] for i in range(0, 25, 5)]


def messages(user_message):
    # convert string to list with all capital letters
    message = list(map(str.upper, user_message))

    # remove spaces
    message = list(filter(lambda x: x != ' ', message))

    # add 'X' between duplicates if first one is at odd index
    for i in range(len(message)):
        if message[i-1] == message[i] and i % 2:
            message.insert(i, 'X')

    # append 'X' if list has odd number of elements to make valid pairs
    if len(message) % 2 == 1:
        message.append('X')

    # make pairs from even number of elements
    return [message[i:i+2] for i in range(0, len(message), 2)]


def position(matrixk, letter):
    for i in range(5):
        for j in range(5):
            if matrixk[i][j] == letter:
                return i, j


def encrypt(user_message, key):
    message = messages(user_message)
    matrixk = matrix(key)

    cipher = []
    # get indices of pairs
    for a, b in message:
        x1, y1 = position(matrixk, a)
        x2, y2 = position(matrixk, b)

        # Elements in same row
        if x1 == x2:
            # if y reached one end (4), %5 will make (4+1)%5 = 0
            cipher.append(matrixk[x1][(y1 + 1) % 5])
            cipher.append(matrixk[x1][(y2 + 1) % 5])

        # Elements in same column
        elif y1 == y2:
            # if x reached one end (4), %5 will make (4+1)%5 = 0
            cipher.append(matrixk[(x1 + 1) % 5][y1])
            cipher.append(matrixk[(x2 + 1) % 5][y2])

        # Elements make a box so use remaining corners
        else:
            cipher.append(matrixk[x1][y2])
            cipher.append(matrixk[x2][y1])

    # convert list to string
    return ''.join(cipher)


def decrypt(user_cipher, key):

    # generate pairs from cipher
    cipher = [user_cipher[i:i+2] for i in range(0, len(user_cipher), 2)]
    matrixk = matrix(key)

    plaintext = []
    for a, b in cipher:
        x1, y1 = position(matrixk, a)
        x2, y2 = position(matrixk, b)

        # Elements in same row
        if x1 == x2:
            # if y reached one end (0), %5 will make (0-1)%5 = 4
            plaintext.append(matrixk[x1][(y1 - 1) % 5])
            plaintext.append(matrixk[x1][(y2 - 1) % 5])

        # Elements in same column
        elif y1 == y2:
            # if x reached one end (0), %5 will make (0-1)%5 = 4
            plaintext.append(matrixk[(x1 - 1) % 5][y1])
            plaintext.append(matrixk[(x2 - 1) % 5][y2])

        # Elements make a box so use remaining corners
        else:
            plaintext.append(matrixk[x1][y2])
            plaintext.append(matrixk[x2][y1])

    # convert list to string
    return ''.join(plaintext)


key = input('Please input the key: ')
plaintext = input('Please input the message: ')
cipher = encrypt(plaintext, key)
decipher = decrypt(cipher, key)

print("Plaintext Matrix: ", messages(plaintext))
print("Key Matrix:")
pprint(matrix(key))
print("Encrypted text: ", cipher)
print("Decrypted text: ", decipher)
