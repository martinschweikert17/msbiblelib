from mblreferences import References
from mblservers import Bibleservers
from mblversions import Versions
from mblbooks import Books
from mblservers import Bibleservers





def main():

    bibleservers = Bibleservers()
    bibleversions = Versions()
    biblebooks = Books()


    srv = bibleservers.get_servers()
    x=0


if __name__ == "__main__":
    main()