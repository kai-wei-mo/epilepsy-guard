from extract import getDeltas
import config

def isMalicious(url):
    deltas = getDeltas(url)
    length = len(deltas)

    if length == 1:
        return deltas[0] >= config.limit

    if length == 2:
        return deltas[0] >= config.limit or deltas[1] >= config.limit

    for i in range(2, length):
        if deltas[i] + deltas[i - 1] + deltas[i - 2] > config.cumulative:
            return True

    return False

if __name__ == "__main__":
    url = 'https://i.gifer.com/7b7F.gif'
    isMalicious(url)