from cinemana import Cinemana

cinem = Cinemana("Man in the high castle")

test = ""
for i in cinem.links:
    test += i['url'] + '\n'

print(test)