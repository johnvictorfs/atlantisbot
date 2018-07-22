from urllib.request import urlopen


def get_user_info(name):
    url = (f"http://services.runescape.com/m=website-data/playerDetails.ws?names=%5B%22{name},"
           f"%22%5D&callback=jQuery000000000000000_0000000000&_=0")
    client = urlopen(url)
    data = client.read()
    return str(data)


def get_user_clan(name):
    info = get_user_info(name)
    info = str(info.split(':'))
    info = info.split(',')
    user_clan = info[8].replace("'", "").replace('"', "").replace(" ", "")
    return user_clan


if __name__ == '__main__':
    # Tests #
    check_name = input("Username to check clan of: ")
    print(get_user_clan(check_name))
