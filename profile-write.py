#!/usr/bin/env python2

# Utility to write a single profile to Jcard-based SIM card
#

from sim_reader import SIM_Reader

class EF:
    def __init__(self, name, tp="transparent"):
        self.name = name
        self.fci = None
        self.tp = tp  # transparent, linear, cyclic
        self.data = None
        self.adpu = None

    def __repr__(self):
        return "\nName: {}\n Type: {} \n FCI: {} \n Data: {}\n".format(self.name, self.tp, self.fci, self.data)

    def set_fci(self, fci):
        self.fci = fci

    def set_data(self, data):
        self.data = data

    def set_type(self, tp):
        assert (tp == "transparent" or tp == "linear" or tp == "cyclic")
        self.tp = tp

    def set_apdu(self, apdu):
        self.apdu = apdu


def load_profile_single(s):
    # print(s)
    l = [k.strip("]").strip(":").strip().split("\n") for k in s.split("Name")[1:]]
    ret = []
    for record in l:
        ef = EF(record[0])
        ef.tp = record[1].strip().strip("Type").strip(":").strip()
        ef.fci = record[2].strip().strip("FCI").strip(":").strip()
        st = record[3].strip().strip("Data").strip(":").strip()
        print(st)
        if ef.tp == "transparent":
            ef.data = st
        else:
            ef.data = [subst.strip().strip("'") for subst in st.strip('][').split(',')]
        ret.append(ef)
    return ret


def load_profile(folder="./profile/"):
    with open(folder + "mf.txt", "r") as f:
        mf = load_profile_single(f.read())

    with open(folder + "adf.txt", "r") as f:
        adf = load_profile_single(f.read())

    with open(folder + "gsm.txt", "r") as f:
        gsm = load_profile_single(f.read())

    with open(folder + "telecom.txt", "r") as f:
        telecom = load_profile_single(f.read())

    return mf, adf, gsm, telecom


def write_EF(ef, parent):
    print("===============")
    print(ef)
    # sr.send_apdu(ins = 'a4',p1 = '00', p2 = '00', data = '3F00')
    # sr.send_apdu(ins = 'a4',p1 = '00', p2 = '00', data = parent)
    sr.send_apdu(ins='e0', p1='00', p2='00', data=ef.fci)
    sr.send_apdu(ins='a4', p1='00', p2='00', data=ef.name)
    if ef.tp == "transparent":
        sr.send_apdu(ins='d6', p1='00', p2='00', data=ef.data)
        sr.send_apdu(ins='a4', p1='00', p2='00', data=ef.name)
        sw, data = sr.send_apdu_without_length(ins='b0', p1='00', p2='00', data='0a')
        print(sw, data)
    if ef.tp == "linear":
        records = ef.data
        item = 1
        for record in records:
            if set(record) == set("f"):
                continue
            print(item)
            sw, data = sr.send_apdu(ins='dc', p1='%02x' % (item), p2='04', data=record)
            sw, data = sr.send_apdu_without_length(ins='b2', p1='%02x' % (item), p2='04', data=str(26))
            item += 1


if __name__ == '__main__':

    sr = SIM_Reader()
    sr.wait_for_card()

    IMSI = sr.imsi("001010000024038")
    OPC = "0102030405060708090A0B0C0D0E0F00"
    KEY = "0102030405060708090A0B0C0D0E0F00"

    print(sr.send_apdu_text('00a5000000'))
    sr.send_apdu(ins='a4', p1='00', p2='04', data='3F00')

    mf, adf, gsm, telecom = load_profile("./profile/")

    for ef in mf:
        write_EF(ef, '3F00')

    sr.send_apdu(ins='a4', p1='00', p2='00', data='3F00')
    sr.send_apdu(ins='e0', p1='00', p2='00',
                  data="62308202782183027f20a51683027fffcb0d00000000000000000000000000ca01828a01058b032f0601c606900100830101")
    for ef in gsm:
        write_EF(ef, '7F20')

    sr.send_apdu(ins='a4', p1='00', p2='00', data='3F00')
    sr.send_apdu(ins='e0', p1='00', p2='00',
                  data='62308202782183027f10a51683027fffcb0d00000000000000000000000000ca01828a01058b032f0601c606900100830101')
    for ef in telecom:
        write_EF(ef, '7F10')

    sr.send_apdu(ins='a4', p1='00', p2='00', data='3F00')
    print(sr.send_apdu_text('00e000005962578202782183027fff8410a0000000871002ffffffff8907090000a51683027fffcb0d00000000000000000000000000ca01808a0105ab15800101a40683010a95010880014097008001069000c609900140830101830181'))

    for ef in adf:
        write_EF(ef, '7FFF')

    # INSTALL default profile
    print(sr.send_apdu_text('00a6010000'))
    print(sr.send_apdu_text("00a7000029" + IMSI + OPC + KEY))
