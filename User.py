class User:

    def __init__(self, id):
        self.id = id
        self.balance = 0
        self.dailyStreak = 0

        #cooldowns
        self.scav = 0
        self.steal = 0
        self.cf = 0
        self.daily = 0

        #shop
        self.multi = 1
        self.inv = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.items = {21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0}

    #overloaded comparison operators
    def __gt__(self, other):
        return self.balance > other.balance
    
    def __lt__(self, other):
        return self.balance < other.balance

    def __eq__(self, other):
        return self.balance == other.balance
    
    def __ge__(self, other):
        return self.balance >= other.balance

    def __le__(self, other):
        return self.balance <= other.balance