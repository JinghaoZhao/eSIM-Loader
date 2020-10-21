from smartcard.CardRequest import *
from smartcard.Exceptions import *
from smartcard.System import *
from pytlv.TLV import TLV


class SIM_Reader(object):
    def __init__(self):
        self.cla = "00"
        self.rec_pdu = ""
        self.rec_data = ""
        self.rec_sw = ""
        r = readers()
        self._reader = r[0]
        self._con = self._reader.createConnection()

    def __del__(self):
        self._con.disconnect()
        return

    def wait_for_card(self, timeout=None, newcardonly=False):
        cr = CardRequest(readers=[self._reader], timeout=timeout, newcardonly=newcardonly)
        try:
            cr.waitforcard()
        except CardRequestTimeoutException:
            raise CardRequestTimeoutException
        try:
            self._con.connect()
        except NoCardException:
            raise NoCardException

    def send_pdu(self, pdu):
        apdu = [(int(x, 16) << 4) + int(y, 16) for x, y in zip(pdu[0::2], pdu[1::2])]
        data, sw1, sw2 = self._con.transmit(apdu)
        sw = [sw1, sw2]
        return ''.join(['%02x' % (x) for x in data]), ''.join(['%02x' % (x) for x in sw])

    def apdu_to_string(self):
        s = self.rec_pdu
        cla = s[0:2]
        ins = s[2:4]
        p1 = s[4:6]
        p2 = s[6:8]
        length = s[8:10]
        data = s[10:]
        k = ("APDU SENT:")
        k += ("\nCLA: " + cla)
        k += ("\nINS: " + ins)
        k += ("\np1: " + p1)
        k += ("\np2: " + p2)
        k += ("\nlength: " + length)
        k += ("\ndata: " + data + '\n')
        k += ("APDU Response code: " + self.rec_sw)
        k += ("APDU Response data : " + self.rec_data)
        return k

    def process_fcp(self, fcp):
        tlvparser = TLV(['82', '83', '84', 'a5', '8a', '8b', '8c', '80', 'ab', 'c6', '81', '88'])
        fcp = fcp.lower()
        if fcp[0:2] != '62':
            return None
        exp_tlv_len = int(fcp[2:4], 16)
        if len(fcp[4:]) / 2 == exp_tlv_len:
            skip = 4
        else:
            exp_tlv_len = int(fcp[2:6], 16)
            if len(fcp[4:]) / 2 == exp_tlv_len:
                skip = 6

        tlv = fcp[skip:]

        parsed_result = tlvparser.parse(tlv)
        print(parsed_result)
        return parsed_result

    def imsi(self, imsi):
        def bsw(s):
            return ''.join([x + y for x, y in zip(s[1::2], s[0::2])])

        l = (len(imsi) + 2) // 2
        tmp = len(imsi) & 1
        encode_imsi = '%02x' % l + bsw('%01x%s' % ((tmp << 3) | 1, imsi + 'f' * (15 - len(imsi))))
        return encode_imsi

    def send_apdu(self, ins, p1='00', p2='00', data=""):
        pdu = self.cla + ins + p1 + p2 + '%02x' % int(len(data) / 2) + data
        data, sw = self.send_pdu(pdu)
        self.rec_pdu = pdu
        self.rec_data = data
        self.rec_sw = sw

        if (sw is not None) and ((sw[0:2] == '9f') or (sw[0:2] == '61')):
            pdu_gr = pdu[0:2] + 'c00000' + sw[2:4]
            data, sw = self.send_pdu(pdu_gr)

        print(self.apdu_to_string())
        if sw == '6a82':
            print("============================")
            return (data, sw), None
        else:
            print(data)
            try:
                parsed = self.process_fcp(data)
            except:
                print("FCP Parse Failed...")
                parsed = None
            print("============================")
            return (data, sw), parsed

    def send_apdu_text(self, pdu):
        data, sw = self.send_pdu(pdu)
        self.rec_pdu = pdu
        self.rec_data = data
        self.rec_sw = sw

        if (sw is not None) and ((sw[0:2] == '9f') or (sw[0:2] == '61')):
            pdu_gr = pdu[0:2] + 'c00000' + sw[2:4]
            data, sw = self.send_pdu(pdu_gr)

        print(self.apdu_to_string())
        if sw == '6a82':
            print("============================")
            return (data, sw), None
        else:
            print(data)
            try:
                parsed = self.process_fcp(data)
            except:
                print("FCP Parse Failed...")
                parsed = None
            print("============================")
            return (data, sw), parsed

    def send_apdu_without_length(self, ins, p1='00', p2='00', data=""):
        pdu = self.cla + ins + p1 + p2 + data
        data, sw = self.send_pdu(pdu)
        self.rec_pdu = pdu
        self.rec_data = data
        self.rec_sw = sw

        if (sw is not None) and ((sw[0:2] == '9f') or (sw[0:2] == '61')):
            pdu_gr = pdu[0:2] + 'c00000' + sw[2:4]
            data, sw = self.send_pdu(pdu_gr)

        print(self.apdu_to_string())
        print("============================")
        return data, sw
