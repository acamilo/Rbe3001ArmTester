class CalcAvg:
    avg = 0
    avg_array = []
    records = 20
    def __init__(self,records=20):
        self.avg=0
        self.records = records
        self.avg_array = [0.0] * self.records
        
    def add(self,value):
        value = float(value)
        self.avg = 0
        self.avg_array = [value] + self.avg_array[0:self.records-1]
        for v in self.avg_array:
            self.avg += v
        self.avg = self.avg/self.records

