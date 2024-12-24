def is_common_password(password):
    with open('utils/common_passwords.txt', 'r') as file:
        common_passwords = file.read().splitlines()
    return password in common_passwords
