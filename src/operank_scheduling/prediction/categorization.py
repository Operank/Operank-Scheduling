def duration_bin(x):
    if 0 < x <= 60:
        return 0
    elif 60 < x <= 120:
        return 1
    else:
        return 2


def bin_to_duration(x):
    if x == 0:
        return 60
    elif x == 1:
        return 120
    else:
        return 180


def age_bin(x):
    if 0 < x <= 10:
        return -5
    elif 10 < x <= 20:
        return -4
    elif 20 < x <= 30:
        return -3
    elif 40 < x <= 50:
        return -2
    elif 50 < x <= 60:
        return -1
    elif 60 < x <= 70:
        return 0
    elif 70 < x <= 80:
        return 1
    elif 80 < x <= 90:
        return 2
    elif 90 < x <= 100:
        return 3
    else:
        return 4


def gender_category(x):
    if x[0] == "Male":
        return -1
    elif x[0] == "Female":
        return 1
