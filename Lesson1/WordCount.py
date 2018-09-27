
def print_words(filename):
    wordCount = readFile(filename)
    wordCount = dict(sorted(wordCount.items()))
    for key, value in wordCount.items():
        print(key,value)
    return


def print_top(filename):
    wordCount = readFile(filename)
    wordTop = sorted(wordCount.items(), key = lambda x:x[1], reverse = True)
    count = 0
    for key, value in wordTop:
        if count == 20:
            break
        print(key,value)
        count = count + 1
    return

    # Function returning a dictionnary with all words and their occurency in a file
def readFile(filename):
    wordCount = {}
    file = open(filename,"r")
    for line in file:
        words = line.split()
        for w in words:
            w = w.lower()
            if (w in wordCount) == False:
                wordCount[w] = 1
            else:
                wordCount[w] = wordCount[w] + 1
    file.close()
    return wordCount

import sys

# This basic command line argument parsing code is provided and
# calls the print_words() and print_top() functions which you must define.
def main():
    if len(sys.argv) != 3:
        print ('usage: ./WordCount.py {--count | --topcount} file')
        sys.exit(1)

    option = sys.argv[1]
    filename = sys.argv[2]
    if option == '--count':
        print_words(filename)
    elif option == '--topcount':
        print_top(filename)
    else:
        print ('unknown option: ' + option)
        sys.exit(1)

if __name__ == '__main__':
    main()
