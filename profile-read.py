#!/usr/bin/env python2

# Utility to extract the profile from a SIM card

import re
import os
import cPickle as pickle
from sim_reader import SIM_Reader

USE_RECORD = False

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


def lsdf(dir):
    adf_dir = []
    error_adf = []
    for adf_ef in dir:
        print("***********************************************************************")
        adf_ef = EF(adf_ef)
        print(adf_ef.name)
        (fci, sw), parsed = sr.send_apdu(ins='a4', p1='00', p2='04', data=adf_ef.name)
        adf_ef.set_fci(fci)

        if sw == '6a82':
            continue
        elif sw == '6982':
            print("Access Rule Encountered")
            continue
        elif sw == '9000':
            # transparent
            if '82' in parsed.keys() and parsed['82'].startswith('41'):
                (data, sw) = sr.send_apdu_without_length(ins='b0', p1='00', p2='00', data=parsed['80'][2:4])
                if sw == '6982':
                    print("Access Rule Encountered")
                    continue
                assert (sw == '9000')
                adf_ef.set_type('transparent')
                adf_ef.set_data(data)

            # linear
            elif '82' in parsed.keys() and parsed['82'].startswith('42'):
                record_list = []
                num_rec = int(parsed['82'][8:], 16)
                len_rec = parsed['82'][6:8]
                for i in range(num_rec):
                    i = i + 1
                    (data, sw) = sr.send_apdu_without_length(ins='b2', p1='%02x' % (i), p2='04', data=str(len_rec))
                    record_list.append(data)

                adf_ef.set_type('linear')
                adf_ef.set_data(record_list)


            # cyclic
            elif USE_RECORD and '82' in parsed.keys() and parsed['82'].startswith('46'):
                record_list = []
                num_rec = int(parsed['82'][8:], 16)
                len_rec = parsed['82'][6:8]
                print(num_rec, len_rec)
                for i in range(num_rec):
                    i = i + 1
                    (data, sw) = sr.send_apdu_without_length(ins='b2', p1='%02x' % (i), p2='04', data=str(len_rec))
                    record_list.append(data)

                adf_ef.set_type('cyclic')
                adf_ef.set_data(record_list)
            else:
                error_adf.append((adf_ef, sw))
                continue
            adf_dir.append(adf_ef)
        else:
            error_adf.append((adf_ef, sw))
    return adf_dir, error_adf


def save_profile(mf="", adf="", gsm="", telecom="", folder="./profile-read/"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(folder + "mf.profile", "w") as f:
        pickle.dumps(mf)
    with open(folder + "mf.txt", 'w') as f:
        f.write(str(mf))

    with open(folder + "adf.profile", "wb") as f:
        pickle.dump(adf, f)
    with open(folder + "adf.txt", 'w') as f:
        f.write(str(adf))

    with open(folder + "gsm.profile", "wb") as f:
        pickle.dump(gsm, f)
    with open(folder + "gsm.txt", 'w') as f:
        f.write(str(gsm))

    with open(folder + "telecom.profile", "wb") as f:
        pickle.dump(telecom, f)
    with open(folder + "telecom.txt", 'w') as f:
        f.write(str(telecom))


if __name__ == '__main__':
    sr = SIM_Reader()
    sr.wait_for_card()

    sr.send_apdu(ins='a4', p1='00', p2='04', data='3F00')
    sr.send_apdu(ins='a4', p1='00', p2='04', data='3F00')

    # mf
    mf_list = ['2F00', '2F05', '2F06', '2FE2', '2F08']
    mf_dir, error_mf = lsdf(mf_list)

    # adf
    sr.send_apdu(ins='a4', p1='00', p2='04', data='2F00')
    res = sr.send_apdu_without_length(ins='b2', p1='01', p2='04', data='26')

    adf_aid = re.findall("a0000000871002[a-f0-9]{18}", str(res[0]))[0]
    sr.send_apdu(ins='a4', p1='04', p2='04', data=adf_aid)

    adf_list = ['6F05', '6F06', '6F07', '6F08', '6F09', '6F2C', '6F31', '6F32', '6F37', '6F38', '6F39', '6F3B', '6F3C',
                '6F3E', '6F3F', '6F40', '6F41', '6F42', '6F43', '6F45', '6F46', '6F47', '6F48', '6F49', '6F4B', '6F4C',
                '6F4D', '6F4E', '6F4F', '6F50', '6F55', '6F56', '6F57', '6F58', '6F5B', '6F5C', '6F5C', '6F60', '6F61',
                '6F62', '6F73', '6F78', '6F7B', '6F7E', '6F80', '6F81', '6F82', '6F83', '6FAD', '6FB1', '6FB2', '6FB3',
                '6FB4', '6FB5', '6FB6', '6FB7', '6FC3', '6FC4', '6FC5', '6FC6', '6FC7', '6FC8', '6FC9', '6FCA', '6FCB',
                '6FCC', '6FCD', '6FCE', '6FCF', '6FD0', '6FD1', '6FD2', '6FD3', '6FD4', '6FD5', '6FD6', '6FD7', '6FD8',
                '6FD9', '6FDA', '6FDB', '6FDC', '6FDD', '6FDE', '6FDF', '6FE2', '6FE3', '6FE4', '6FE6', '6FE7', '6FE8',
                '6FEC', '6FED', '6FEE', '6FEF', '6FF0', '6FF1', '6FF2', '6FF3', '6FF4']

    adf_dir, error_adf = lsdf(adf_list)

    sr.send_apdu(ins='a4', p1='00', p2='04', data='3F00')
    sr.send_apdu(ins='a4', p1='00', p2='04', data='7F20')
    gsm_list = ['6F05', '6F07', '6F20', '6F2C', '6F30', '6F31', '6F32', '6F37', '6F38', '6F39', '6F3E', '6F3F', '6F41',
                '6F45', '6F46', '6F48', '6F74', '6F78', '6F7B', '6F7E', '6FAD', '6FAE', '6FB1', '6FB2', '6FB3', '6FB4',
                '6FB5', '6FB6', '6FB7', '6F50', '6F51', '6F52', '6F53', '6F54', '6F60', '6F61', '6F62', '6F63', '6F64',
                '6FC5', '6FC6', '6FC7', '6FC8', '6FC9', '6FCA', '6FCB', '6FCC']
    gsm_dir, error_gsm = lsdf(gsm_list)

    sr.send_apdu(ins='a4', p1='00', p2='04', data='3F00')
    sr.send_apdu(ins='a4', p1='00', p2='04', data='7F10')
    telecom_list = ['6F06', '6F3A', '6F3B', '6F3C', '6F40', '6F42', '6F43', '6F44', '6F47', '6F49', '6F4A', '6F4B',
                    '6F4C', '6F4D', '6F4E', '6F4F', '6F53', '6F54', '6FE0', '6FE1', '6FE5']
    telecom_dir, error_telecom = lsdf(telecom_list)

    save_profile(mf_dir, adf_dir, gsm_dir, telecom_dir, "./profile-read/")
