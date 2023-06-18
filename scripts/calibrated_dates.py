HEADER_LINE = 'site-name,lab-id,sample-ref,bp,error,human,marine,d13C,d15N,C/N,marine-fraction,cal-start-2s,cal-end-2s,segments-2s,cal-start-1s,cal-end-1s,segments-1s\n'

SITE_NAME = 0
LAB_ID = 1
SAMPLE_REF = 2
BP = 3
ERROR = 4
HUMAN = 5
MARINE = 6
D13C = 7
D15N = 8
CN = 9
MARINE_FRACTION = 10
CAL_START_2S = 11
CAL_END_2S = 12
SEGMENTS_2S = 13
CAL_START_1S = 14
CAL_END_1S = 15
SEGMENTS_1S = 16


class CalibratedDate:
    def __init__(self, fields=None):
        if fields == None:
            self.site_name = None
            self.lab_id = None
            self.sample_ref = None
            self.bp = None
            self.error = None
            self.human = None
            self.marine = None
            self.d13C = None
            self.d15N = None
            self.CN = None
            self.marine_fraction = None
            self.cal_start_2s = None
            self.cal_end_2s = None
            self.segments_2s = None
            self.cal_start_1s = None
            self.cal_end_1s = None
            self.segments_1s = None
            
            return

        self.site_name = fields[SITE_NAME]
        self.lab_id = fields[LAB_ID]
        self.sample_ref = fields[SAMPLE_REF]
        self.bp = fields[BP]
        self.error = fields[ERROR]
        self.human = fields[HUMAN]
        self.marine = fields[MARINE]
        self.d13C = fields[D13C]
        self.d15N = fields[D15N]
        self.CN = fields[CN]
        self.marine_fraction = fields[MARINE_FRACTION]
        self.cal_start_2s = fields[CAL_START_2S]
        self.cal_end_2s = fields[CAL_END_2S]
        self.segments_2s = fields[SEGMENTS_2S]
        self.cal_start_1s = fields[CAL_START_1S]
        self.cal_end_1s = fields[CAL_END_1S]
        self.segments_1s = fields[SEGMENTS_1S]


    def fields(self):
        flds = []
        flds.append(self.site_name)
        flds.append(self.lab_id)
        flds.append(self.sample_ref)
        flds.append(self.bp)
        flds.append(self.error)
        flds.append(self.human)
        flds.append(self.marine)
        flds.append(self.d13C)
        flds.append(self.d15N)
        flds.append(self.CN)
        flds.append(self.marine_fraction)
        flds.append(self.cal_start_2s)
        flds.append(self.cal_end_2s)
        flds.append(self.segments_2s)
        flds.append(self.cal_start_1s)
        flds.append(self.cal_end_1s)
        flds.append(self.segments_1s)

        return flds
