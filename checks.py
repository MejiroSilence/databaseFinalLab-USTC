def customerIDcheck(ID):
    if ID == "":
        return "ID can not be null"
    if len(ID) > 20:
        return "ID too long, limit: 20"
    return ""


def customerCheck(data):
    if data["customerName"] == "":
        return "customerName can not be null"
    if data["customerPhone"] == "":
        return "customerPhone can not be null"
    if data["customerAdress"] == "":
        return "customerAdress can not be null"
    if data["contactName"] == "":
        return "contactName can not be null"
    if data["contactPhone"] == "":
        return "contactPhone can not be null"
    if data["contactMail"] == "":
        return "contactMail can not be null"
    if data["userContactRelation"] == "":
        return "userContactRelation can not be null"
    if len(data["customerName"]) > 20:
        return "customerName too long, limit: 20"
    if len(data["customerPhone"]) > 20:
        return "customerPhone too long, limit: 20"
    if len(data["customerAdress"]) > 20:
        return "customerAdress too long, limit: 20"
    if len(data["contactName"]) > 20:
        return "contactName too long, limit: 20"
    if len(data["contactPhone"]) > 20:
        return "contactPhone too long, limit: 20"
    if len(data["contactMail"]) > 30:
        return "contactMail too long, limit: 30"
    if len(data["userContactRelation"]) > 20:
        return "userContactRelation too long, limit: 20"
    return ""


def checkAccountCheck(form):
    try:
        number = float(form["overdraft"])
    except ValueError:
        return False
    return True


def depositaAccountCheck(form):
    try:
        number = float(form["interestRate"])
    except ValueError:
        return False
    return True


def checkAccountEditCheck(form):
    try:
        number = float(form["overdraft"])
        number = float(form["accountBalance"])
    except ValueError:
        return False
    return True


def depositaAccountEditCheck(form):
    try:
        number = float(form["interestRate"])
        number = float(form["accountBalance"])
    except ValueError:
        return False
    return True
