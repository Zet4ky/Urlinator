import Urlinator

def test(url):
    return Urlinator.get_report(url)

if __name__ == '__main__':
    target = ("https://google.com/")
    print(test(target))


