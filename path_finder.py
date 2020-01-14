from copy import deepcopy


def find_path(path, x1, y1, x2, y2):
    file = open(path, mode='r', encoding='utf-8')
    data = [list(i[:-1]) for i in file.readlines()]
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] in 'wmb':
                data[i][j] = -1
            else:
                data[i][j] = 0
    a = [print(i) for i in data]
    lest = deepcopy(data)
    lest[x1][y1] = 1
    lest[x2][y2] = 0
    wave = True
    height = len(data)
    width = len(data[0])
    while wave and lest[x2][y2] == 0:
        wave = False
        for i in range(height - 1):
            for j in range(width - 1):
                if lest[i][j] not in [0, -1]:
                    if 0 <= i - 1 < height:
                        if lest[i - 1][j] == 0:
                            lest[i - 1][j] = lest[i][j] + 1
                            wave = True
                    if 0 <= i + 1 < height:
                        if lest[i + 1][j] == 0:
                            lest[i + 1][j] = lest[i][j] + 1
                            wave = True
                    if 0 <= j - 1 < width:
                        if lest[i][j - 1] == 0:
                            lest[i][j - 1] = lest[i][j] + 1
                            wave = True
                    if 0 <= j + 1 < width:
                        if lest[i][j + 1] == 0:
                            lest[i][j + 1] = lest[i][j] + 1
                            wave = True
    path_lest = []
    if lest[x2][y2] != 0:
        x, y = x2, y2
        path_lest.append((x2, y2))
        while lest[x][y] != 1:
            if 0 <= x - 1 < height:
                if lest[x - 1][y] == lest[x][y] - 1:
                    path_lest.append((x - 1, y))
                    x -= 1
            if 0 <= x + 1 < height:
                if lest[x + 1][y] == lest[x][y] - 1:
                    path_lest.append((x + 1, y))
                    x += 1
            if 0 <= y - 1 < width:
                if lest[x][y - 1] == lest[x][y] - 1:
                    path_lest.append((x, y - 1))
                    y -= 1
            if 0 <= y + 1 < width:
                if lest[x][y + 1] == lest[x][y] - 1:
                    path_lest.append((x, y + 1))
                    y += 1
    file.close()
    return path_lest[::-1]
