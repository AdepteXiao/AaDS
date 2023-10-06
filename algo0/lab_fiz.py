with open("inp.txt", 'r') as file:
    vals = list(map(lambda x: tuple(map(float, x.replace("\n", "").split())), file.readlines()))
lam = 632.8 * (10 ** (-9))
F = 0.05


def pprint_list(prnt_list):
