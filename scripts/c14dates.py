SITE_NAME = 0
SITE_REF = 1
SAMPLE_REF = 2
LAB_ID = 3
BP = 4
ERROR = 5
HUMAN = 6
MARINE = 7
D13C = 8
D15N = 9
CN = 10
CONTEXT_REF = 11
SOURCE = 12
NOTES = 13


def c14_list(rows):
    c14s = []
    for row in rows:
        c14s.append(C14Date(row))
    
    return c14s



class C14Date:
    def __init__(self, fields=None):
        if fields == None:
            self.site_name = None
            self.site_ref = None
            self.sample_ref = None
            self.lab_id = None
            self.bp = None
            self.error = None
            self.human = None
            self.marine = None
            self.d13C = None
            self.d15N = None
            self.CN = None
            self.context_ref = None
            self.source = None
            self.notes = None
            return
        
        self.site_name = fields[SITE_NAME]
        self.site_ref = fields[SITE_REF]
        self.sample_ref = fields[SAMPLE_REF]
        self.lab_id = fields[LAB_ID]
        self.bp = fields[BP]
        self.error = fields[ERROR]
        self.human = fields[HUMAN]
        self.marine = fields[MARINE]
        self.d13C = fields[D13C]
        self.d15N = fields[D15N]
        self.CN = fields[CN]
        self.context_ref = fields[CONTEXT_REF]
        self.source = fields[SOURCE]
        self.notes = fields[NOTES]
