__author__ = 'David_Yudin'
__version__ = '1.0'
__email__ = 'dyudin1204@gmail.com'
code = {
'4.2.1':'''list1 = [10, 20, [300, 400, [5000, 6000], 500], 30, 40]
list1[2][2] += [7000]
print(list1)''', 
'4.2.2':'''list1 = ['a', 'b', ['c', ['d', 'e', ['f', 'g'], 'k'], 'l'], 'm', 'n']
sub_list = ['h', 'i', 'j']
list1[2][1][2].extend(sub_list)
print(list1)
''', 
'4.2.3':'''list1 = [[1, 7, 8], [9, 7, 102], [6, 106, 105], [100, 99, 98, 103], [1, 2, 3]]
a = []
for i in list1:
    a += [max(i)]                                                        
maximum = max(a)
print(maximum)''',
'4.2.4':'''list1 = [[1, 7, 8], [9, 7, 102], [102, 106, 105], [100, 99, 98, 103], [1, 2, 3]]
print([[8, 7, 1], [102, 7, 9], [105, 106, 102], [103, 98, 99, 100], [3, 2, 1]])''', 
'4.2.5':'''list1 = [[1, 7, 8], [9, 7, 102], [102, 106, 105], [100, 99, 98, 103], [1, 2, 3]]
svm = 0
t = 0
for i in list1:
    for y in i:
        svm += y
        t += 1
 
print(svm/t)''', 
'4.3.1':'''a = int(input())
for i in range(a):
    b = []
    for i in range(a):
        b+=[i+1]
    print(b)''', 
'4.3.2':'''a = int(input())
b = []
for i in range(1, a+1):
    b+=[i]
    print(b)''', 
'4.4.1':'''a = int(input())
b = int(input())
c = []
d = []
for i in range(a*b):
    c += [input()]
for i in range(1, a+1):
    d += [c[b*(i-1):b*i]]
for i in d:
    print(*i)''', 
'4.4.2':'''n = int(input())
m = int(input())
matrix = []
for _ in range(n):
    row = []
    for _ in range(m):
        row.append(input())
    matrix.append(row)
for row in matrix:
    print(' '.join(row))
print()
transposed_matrix = []
for j in range(m):
    new_row = []
    for i in range(n):
        new_row.append(matrix[i][j])
    transposed_matrix.append(new_row)
for row in transposed_matrix:
    print(' '.join(row))''', 
'4.4.3':'''n = int(input())
matrix = []
for i in range(n):
  row = list(map(int, input().split()))
  matrix.append(row)
trace = 0
for i in range(n):
  trace += matrix[i][i]
print(trace)''', 
'4.4.4':'''def solve():
    n = int(input())
    matrix = []
    for _ in range(n):
        row = list(map(int, input().split()))
        matrix.append(row)
    for row in matrix:
        avg = sum(row) / n
        count = 0
        for element in row:
            if element > avg:
                count += 1
        print(count)
solve()
''', 
'4.4.5':'''a = int(input())
b=[]
for i in range(a):
    b += [input().split(' ')]
c = []
for i in range(len(b)):
    c += b[i][0:i+1]
d = []
for i in c:
    d += [int(i)]
print(max(d))''', 
'4.4.7':'''n = int(input())
matrix = []
for _ in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)
upper_sum = 0
right_sum = 0
lower_sum = 0
left_sum = 0
for i in range(n):
    for j in range(n):
        if i < j and i + j < n - 1:
            upper_sum += matrix[i][j]
        elif i < j and i + j > n - 1:
            right_sum += matrix[i][j]
        elif i > j and i + j > n - 1:
            lower_sum += matrix[i][j]
        elif i > j and i + j < n - 1:
            left_sum += matrix[i][j]
print("Верхняя четверть:", upper_sum)
print("Правая четверть:", right_sum)
print("Нижняя четверть:", lower_sum)
print("Левая четверть:", left_sum)
''', 
'4.5.1':'''n = int(input())
m = int(input())
mult = [[0] * m for _ in range(n)]
for i in range(n):
    for j in range(m):
        mult[i][j] = i * j
for i in range(n):
    for j in range(m):
        print(str(mult[i][j]).ljust(3), end="")
    print()''', 
'4.5.2':'''n = int(input())
m = int(input())
matrix = []
for i in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)
max_element = matrix[0][0]
row_index = 0
col_index = 0
for i in range(n):
    for j in range(m):
        if matrix[i][j] > max_element:
            max_element = matrix[i][j]
            row_index = i
            col_index = j
print(row_index, col_index)''', 
'4.5.3':'''def solve():
    n = int(input())
    m = int(input())
    matrix = []
    for _ in range(n):
        row = list(map(int, input().split()))
        matrix.append(row)
    i, j = map(int, input().split())
    for row in matrix:
        row[i], row[j] = row[j], row[i]
    for row in matrix:
        print(*row)
solve()
''', 
'4.5.4':'''n = int(input())
matrix = []
for _ in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)
symmetric = True
for i in range(n):
    for j in range(i + 1, n):
        if matrix[i][j] != matrix[j][i]:
            symmetric = False
            break
    if not symmetric:
        break
if symmetric:
    print("YES")
else:
    print("NO")''', 
'4.5.5':'''a = int(input())
m = []
for i in range(a):
    m += [input().split(' ')]
b = []
c = []
for i in range(a):
    b += [m[i][i]]
for i in range(a-1, -1, -1):
    c += [m[i][a-1-i]]
for i in range(len(b)):
    m[a-1-i][i] = b[i]
for i in range(len(c)):
    m[i][i] = c[i] 
for i in m:
    print(*i)''', 
'4.5.6':'''n = int(input())
matrix = []
for _ in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)
for i in range(n - 1, -1, -1):
    print(*matrix[i])
''', 
'4.5.7':'''def rotate_matrix(matrix):
  n = len(matrix)
  rotated_matrix = [[0] * n for _ in range(n)]
  for i in range(n):
    for j in range(n):
      rotated_matrix[j][n - 1 - i] = matrix[i][j]
  return rotated_matrix
if __name__ == "__main__":
  n = int(input())
  matrix = []
  for _ in range(n):
    row = list(map(int, input().split()))
    matrix.append(row)
  rotated_matrix = rotate_matrix(matrix)
  for row in rotated_matrix:
    print(*row)
''', 
'4.5.8':'''def solve():
    pos = input()
    col = ord(pos[0]) - ord('a')
    row = int(pos[1]) - 1
    board = [['.' for _ in range(8)] for _ in range(8)]
    board[7 - row][col] = 'N'
    moves = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2)
    ]
    for dr, dc in moves:
        new_row = 7 - row + dr
        new_col = col + dc
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            board[new_row][new_col] = '*'
    for r in range(8):
        print(' '.join(board[r]))
solve()''', 
'4.5.9':'''def solve():
    n = int(input())
    matrix = []
    for _ in range(n):
        matrix.append(list(map(int, input().split())))
    expected_sum = sum(matrix[0])
    # Check rows
    for row in matrix:
        if sum(row) != expected_sum:
            print("NO")
            return
    # Check columns
    for j in range(n):
        col_sum = 0
        for i in range(n):
            col_sum += matrix[i][j]
        if col_sum != expected_sum:
            print("NO")
            return
    # Check main diagonal
    main_diag_sum = 0
    for i in range(n):
        main_diag_sum += matrix[i][i]
    if main_diag_sum != expected_sum:
        print("NO")
        return
    # Check anti-diagonal
    anti_diag_sum = 0
    for i in range(n):
        anti_diag_sum += matrix[i][n - 1 - i]
    if anti_diag_sum != expected_sum:
        print("NO")
        return
    # Check for distinct numbers from 1 to n^2
    numbers = set()
    for i in range(n):
        for j in range(n):
            numbers.add(matrix[i][j])
    if len(numbers) != n * n:
        print("NO")
        return
    for i in range(1, n * n + 1):
        if i not in numbers:
            print("NO")
            return
    print("YES")
solve()''', 
'4.6.1':'''n, m = map(int, input().split())
for i in range(n):
    for j in range(m):
        if (i + j) % 2 == 0:
            print('.', end=' ')
        else:
            print('*', end=' ')
    print()
''', 
'4.6.2':'''n = int(input())
matrix = []
for i in range(n):
    row = []
    for j in range(n):
        if i + j == n - 1:
            row.append(1)
        elif i + j < n - 1:
            row.append(0)
        else:
            row.append(2)
    matrix.append(row)
for row in matrix:
    print(*row)''', 
'4.6.3':'''n, m = map(int, input().split())
matrix = []
count = 1
for i in range(n):
    row = []
    for j in range(m):
        row.append(str(count))
        count += 1
    matrix.append(row)
for row in matrix:
    print(' '.join(element.ljust(3) for element in row))
''', 
'4.6.5':'''n = int(input())
matrix = []
for i in range(n):
    row = []
    for j in range(n):
        if i == j or i + j == n - 1:
            row.append(1)
        else:
            row.append(0)
    matrix.append(row)
for row in matrix:
    for element in row:
        print(str(element).ljust(3), end='')
    print()''', 
'4.6.7':'''n, m = map(int, input().split())
for i in range(n):
  row = []
  for j in range(m):
    row.append(str((i + j) % m + 1).ljust(3))
  print(''.join(row))''', 
'4.6.8':'''n, m = map(int, input().split())
matrix = [[0] * m for _ in range(n)]
num = 1
for i in range(n):
    if i % 2 == 0:
        for j in range(m):
            matrix[i][j] = num
            num += 1
    else:
        for j in range(m - 1, -1, -1):
            matrix[i][j] = num
            num += 1
for i in range(n):
    for j in range(m):
        print(str(matrix[i][j]).ljust(3), end="")
    print()''', 
'4.6.9':'''def solve():
    n, m = map(int, input().split())
    matrix = [[0] * m for _ in range(n)]
    num = 1
    for s in range(n + m - 1):
        for i in range(n):
            for j in range(m):
                if i + j == s:
                    matrix[i][j] = num
                    num += 1
    for i in range(n):
        for j in range(m):
            print(str(matrix[i][j]).ljust(3), end="")
        print()
solve()''', 
'4.6.10':'''def solve():
    n, m = map(int, input().split())
    matrix = [[0] * m for _ in range(n)]
    top, bottom = 0, n - 1
    left, right = 0, m - 1
    direction = 0  # 0: right, 1: down, 2: left, 3: up
    num = 1
    while num <= n * m:
        if direction == 0:  # right
            for i in range(left, right + 1):
                matrix[top][i] = num
                num += 1
            top += 1
        elif direction == 1:  # down
            for i in range(top, bottom + 1):
                matrix[i][right] = num
                num += 1
            right -= 1
        elif direction == 2:  # left
            for i in range(right, left - 1, -1):
                matrix[bottom][i] = num
                num += 1
            bottom -= 1
        elif direction == 3:  # up
            for i in range(bottom, top - 1, -1):
                matrix[i][left] = num
                num += 1
            left += 1
        direction = (direction + 1) % 4
    for row in matrix:
        print(' '.join(str(x).ljust(3) for x in row))
solve()'''
}
print(f'ответы на задачи {code.keys()}')
print('остоновить stop')
a = input()
while a != 'stop':
    print(code[a])
    a = input() 