import Urlinator

def test(url):
    return Urlinator.get_report(url)

if __name__ == '__main__':
    target = ("https://virgilev11.serv00.net/SELL/sella-banca-on-line/app/user.php")
    print(test(target))


