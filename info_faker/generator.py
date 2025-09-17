import string

import faker
import random


fake = faker.Faker('en_US')

def getName(): return fake.name()

def getUsernameByName(name: str, patterns=['{1}{2}']) -> str:
    pass


def getEmailByName(name, domains: tuple[str]=("gmail.com", "donnet.org", "proton.me")) -> str:
    return name.lower().replace(' ', '') \
            + ''.join(str(random.randint(0, 9)) for _ in range( random.randint(2, 5) )) \
            + '@' + random.choice(domains)


def generate_username(name_of_user):
    # Constraints
    minimum_digits = random.choice([0, 0, 0, 2, 3])
    min_len_of_username = 8

    # variable to store generated username
    username = ""

    # remove space from name of user
    name_of_user = "".join(name_of_user.split())

    # convert whole name in lowercase
    name_of_user = name_of_user.lower()

    # calculate minimum characters that we need to take from name of user
    minimum_char_from_name = min_len_of_username-minimum_digits

    # take required part from name
    temp = 0
    for i in range(random.randint(minimum_char_from_name,len(name_of_user))):
        username += name_of_user[i]

    # temp_list to store digits and special_chars so that they can be shuffled before adding to username
    temp_list = []
    # add required digits
    for i in range(minimum_digits):
        temp_list.append(str(random.randint(0,9)))

    # shuffle list
    random.shuffle(temp_list)

    username += "".join(temp_list)

    return username



if __name__ == "__main__":
    for _ in range(20):
        name = getName()
        username = generate_username(name)
        email = getEmailByName(name)

        print(name)
        print(username)
        print(email, '\n')