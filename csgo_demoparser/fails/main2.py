import struct
import math
# Buffer reader


class CBitRead:
    # ---------------------------------------------------------
    # Grab another part of data to buffer
    def grabNext4Bytes(self):
        if self.posByte >= len(self.data):
            self.bitsFree = 1
            self.dataPart = 0
            self.overflow = True
        else:
            self.dataPart = self.data[self.posByte] + (self.data[self.posByte + 1] << 8) + (
                    self.data[self.posByte + 2] << 16) + (self.data[self.posByte + 3] << 24)
            self.posByte += 4

    # Add 32 bits free to use and grab new data to buffer
    def fetchNext(self):
        self.bitsFree = 32
        self.grabNext4Bytes()

    # ---------------------------------------------------------
    # Read VAR
    def readUBitVar(self):
        ret = self.readUBitLong(6)
        if ret & 48 == 16:
            ret = (ret & 15) | (self.readUBitLong(4) << 4)
        elif ret & 48 == 32:
            ret = (ret & 15) | (self.readUBitLong(8) << 4)
        elif ret & 48 == 48:
            ret = (ret & 15) | (self.readUBitLong(28) << 4)
        return ret

    # Read unsigned n-bits
    def readUBitLong(self, a_bits):
        if self.bitsFree >= a_bits:
            # By using mask take data needed from buffer
            res = self.dataPart & ((2 ** a_bits) - 1)
            self.bitsFree -= a_bits
            # Check if we need to grab new data to buffer
            if self.bitsFree == 0:
                self.fetchNext()
            else:
                # Move buffer to the right
                self.dataPart >>= a_bits
            return res
        else:
            # Take whats left
            res = self.dataPart
            a_bits -= self.bitsFree
            # Save how many free bits we used
            t_bitsFree = self.bitsFree
            # Grab new data to buffer
            self.fetchNext()
            # Append new data to result
            if self.overflow:
                return 0
            res |= ((self.dataPart & ((2 ** a_bits) - 1)) << t_bitsFree)
            self.bitsFree -= a_bits
            # Move buffer to the right
            self.dataPart >>= a_bits
            return res

    # Read signed n-bits
    def readSBitLong(self, a_bits):
        return (self.readUBitLong(a_bits) << (32 - a_bits)) >> (32 - a_bits)

    # Read string
    def readString(self, length=0):
        res = ""
        index = 1
        while True:
            char = self.readSBitLong(8)
            print(char)
            print(self.posByte)
            print("...")
            if char == 0 and length == 0:
                break
            res += chr(char)
            if index == length:
                break
            index += 1
        return res

    # Read n-bits
    def readBits(self, a_bits):
        res = b''
        bitsleft = a_bits
        while bitsleft >= 32:
            res += bytes([self.readUBitLong(8), self.readUBitLong(8), self.readUBitLong(8), self.readUBitLong(8)])
            bitsleft -= 32
        while bitsleft >= 8:
            res += bytes([self.readUBitLong(8)])
            bitsleft -= 8
        if bitsleft:
            res += bytes([self.readUBitLong(bitsleft)])
        return res

    # Read n-bytes
    def readBytes(self, a_bytes):
        return self.readBits(a_bytes << 3)

    # Read 1 bit
    def readBit(self):
        aBit = self.dataPart & 1
        self.bitsFree -= 1
        if self.bitsFree == 0:
            self.fetchNext()
        else:
            self.dataPart >>= 1
        return aBit

    # ---------------------------------------------------------
    def __init__(self, a_data):
        self.data = ""
        self.dataBytes = 0
        self.dataPart = ""

        self.posByte = 0
        self.bitsFree = 0
        self.overflow = False
        # Save data to vars
        self.data = a_data
        self.dataBytes = len(a_data)

        # Calculate head
        head = self.dataBytes % 4

        # If there is less bytes than potencial head OR head exists
        if self.dataBytes < 4 or head > 0:
            if head > 2:
                self.dataPart = self.data[0] + (self.data[1] << 8) + (self.data[2] << 16)
                self.posByte = 3
            elif head > 1:
                self.dataPart = self.data[0] + (self.data[1] << 8)
                self.posByte = 2
            else:
                self.dataPart = self.data[0]
                self.posByte = 1
            self.bitsFree = head << 3
        else:
            self.posByte = head
            self.dataPart = self.data[self.posByte] + (self.data[self.posByte + 1] << 8) + (
                    self.data[self.posByte + 2] << 16) + (self.data[self.posByte + 3] << 24)
            if self.data:
                self.fetchNext()
            else:
                self.dataPart = 0
                self.bitsFree = 1
            self.bitsFree = min(self.bitsFree, 32)


# this part copied from https://github.com/ibm-dev-incubator/demoparser/blob/master/demoparser/props.pyx
class PropTypes:
    DPT_Int = 0
    DPT_Float = 1
    DPT_Vector = 2
    DPT_VectorXY = 3
    DPT_String = 4
    DPT_Array = 5
    DPT_DataTable = 6
    DPT_Int64 = 7
    DT_MAX_STRING_BITS = 9


class PropFlags:
    SPROP_UNSIGNED = (1 << 0)
    SPROP_COORD = (1 << 1)
    SPROP_NOSCALE = (1 << 2)
    SPROP_ROUNDDOWN = (1 << 3)
    SPROP_ROUNDUP = (1 << 4)
    SPROP_NORMAL = (1 << 5)
    SPROP_EXCLUDE = (1 << 6)
    SPROP_XYZE = (1 << 7)
    SPROP_INSIDEARRAY = (1 << 8)
    SPROP_PROXY_ALWAYS_YES = (1 << 9)
    SPROP_IS_A_VECTOR_ELEM = (1 << 10)
    SPROP_COLLAPSIBLE = (1 << 11)
    SPROP_COORD_MP = (1 << 12)
    SPROP_COORD_MP_LOWPRECISION = (1 << 13)
    SPROP_COORD_MP_INTEGRAL = (1 << 14)
    SPROP_CELL_COORD = (1 << 15)
    SPROP_CELL_COORD_LOWPRECISION = (1 << 16)
    SPROP_CELL_COORD_INTEGRAL = (1 << 17)
    SPROP_CHANGES_OFTEN = (1 << 18)
    SPROP_VARINT = (1 << 19)


class Decoder:
    def decode_int(self):
        if self.prop["prop"].flags & PropFlags.SPROP_VARINT:
            if self.prop["prop"].flags & PropFlags.SPROP_UNSIGNED:
                result = self.data.readUBitVar()
            else:
                result = self.data.readUBitVar()
        else:
            if self.prop["prop"].flags & PropFlags.SPROP_UNSIGNED:
                result = self.data.readUBitLong(self.prop["prop"].num_bits)
            else:
                result = self.data.readSBitLong(self.prop["prop"].num_bits)
        # if self.prop["prop"].flags & PropFlags.SPROP_UNSIGNED != 0:
        #     if bits == 1:
        #         result = self.data.readBit()
        #     else:
        #         result = self.data.readUBitLong(bits)
        # else:
        #     result = self.data.readSBitLong(bits)
        return result

    def decode_string(self):
        length = self.data.readUBitLong(9)
        if length >= 1 << 9:
            length = 1 << 9 - 1
        var = self.data.readString(length)
        return var

    def decode_float(self):
        val = self.decode_float_special()
        if val:
            return val
        # print("bits= ", self.prop["prop"].num_bits)
        if self.prop["prop"].num_bits <= 0:
            return val
        intval = self.data.readUBitLong(self.prop["prop"].num_bits)
        val = float(intval / ((1 << self.prop["prop"].num_bits) - 1))
        val = self.prop["prop"].low_value + (self.prop["prop"].high_value - self.prop["prop"].low_value) * val
        return val

    def decode_vector(self):
        x = self.decode_float()
        y = self.decode_float()
        if (self.prop["prop"].flags & PropFlags.SPROP_NORMAL) == 0:
            z = self.decode_float()
        else:
            sign = self.data.readBit()
            absolute = x * x + y * y
            if absolute < 1.0:
                z = float(math.sqrt(1 - absolute))
            else:
                z = 0.0
            if sign:
                z *= -1
        return {"x": x, "y": y, "z": z}

    def decode_vector_xy(self):
        x = self.decode_float()
        y = self.decode_float()
        return {"x": x, "y": y}

    def decode_array(self):
        num = self.prop["prop"].num_elements
        max = num
        res = list()
        bits = 1
        max2 = max >> 1
        while max2 != 0:
            max2 = max2 >> 1
            bits += 1
        nelem = self.data.readUBitLong(bits)
        self.prop = {"prop": self.prop["arprop"]}
        for i in range(nelem):
            res.append(self.decode())
        return res

    def decode_float_special(self):
        flags = self.prop["prop"].flags
        val = 0.0
        if flags & PropFlags.SPROP_COORD:
            val = self.read_bit_coord()
        elif flags & PropFlags.SPROP_COORD_MP:
            val = self.read_bit_coord_mp(0)
        elif flags & PropFlags.SPROP_COORD_MP_LOWPRECISION:
            val = self.read_bit_coord_mp(1)
        elif flags & PropFlags.SPROP_COORD_MP_INTEGRAL:
            val = self.read_bit_coord_mp(2)
        elif flags & PropFlags.SPROP_NOSCALE:
            val = self.data.readUBitLong(32)
        elif flags & PropFlags.SPROP_NORMAL:
            val = self.read_bit_normal()
        elif flags & PropFlags.SPROP_CELL_COORD:
            val = self.read_bit_cell_coord(self.prop["prop"].num_bits, 0)
        elif flags & PropFlags.SPROP_CELL_COORD_LOWPRECISION:
            val = self.read_bit_cell_coord(self.prop["prop"].num_bits, 1)
        elif flags & PropFlags.SPROP_CELL_COORD_INTEGRAL:
            val = self.read_bit_cell_coord(self.prop["prop"].num_bits, 2)
        return val

    def read_bit_coord(self):
        i = self.data.readBit()
        f = self.data.readBit()
        int_val = 0
        frc_val = 0
        if not i and not f:
            return 0.0
        sign = self.data.readBit()
        if i:
            int_val = self.data.readUBitLong(14) + 1
        if f:
            frc_val = self.data.readUBitLong(5)
        value = int_val + (frc_val * (1.0 / (1 << 5)))
        if sign:
            return -value
        return value

    def read_bit_normal(self):
        sign = self.data.readBit()
        frac = self.data.readUBitLong(11)
        value = frac * (1.0 / ((1 << 11) - 1))
        if sign:
            return -value
        return value

    def read_bit_coord_mp(self, coord_type):
        # none = 0
        # lowprec = 1
        # integral = 2
        bLow = True if coord_type == 1 else False
        bIntg = True if coord_type == 2 else False
        intval = 0
        fractval = 0
        value = 0.0
        sign = 0
        bounds = True if self.data.readBit() else False
        if bIntg:
            intval = self.data.readBit()
            if intval:
                sign = self.data.readBit()
                if bounds:
                    value = float(self.data.readUBitLong(11) + 1)
                else:
                    value = float(self.data.readUBitLong(14) + 1)
        else:
            intval = self.data.readBit()
            sign = self.data.readBit()
            if intval:
                if bounds:
                    intval = self.data.readUBitLong(11) + 1
                else:
                    intval = self.data.readUBitLong(14) + 1
            if bLow:
                fractval = self.data.readUBitLong(3)
                value = intval + float(fractval * (1.0 / (1 << 3)))
            else:
                fractval = self.data.readUBitLong(5)
                value = intval + float(fractval * (1.0 / (1 << 5)))
        if sign:
            return -value
        return value

    def read_bit_cell_coord(self, bits, coord_type):
        bLow = True if coord_type == 1 else False
        bIntg = True if coord_type == 2 else False
        intval = 0
        fractval = 0
        value = 0.0
        if bIntg:
            value = float(self.data.readUBitLong(bits))
        else:
            intval = self.data.readUBitLong(bits)
            if bLow:
                fractval = self.data.readUBitLong(3)
                value = intval + float(fractval * (1.0 / (1 << 3)))
            else:
                fractval = self.data.readUBitLong(5)
                value = intval + float(fractval * (1.0 / (1 << 5)))
        return value

    def __init__(self, data, prop):
        self.data = data
        self.prop = prop

    def decode(self):
        ptype = self.prop["prop"].type
        # print("pname= ", self.prop["prop"].var_name, " / ptype= ", ptype)
        assert ptype != PropTypes.DPT_DataTable
        if ptype == PropTypes.DPT_Int:
            return self.decode_int()
        elif ptype == PropTypes.DPT_String:
            return self.decode_string()
        elif ptype == PropTypes.DPT_Float:
            return self.decode_float()
        elif ptype == PropTypes.DPT_Vector:
            return self.decode_vector()
        elif ptype == PropTypes.DPT_VectorXY:
            return self.decode_vector_xy()
        elif ptype == PropTypes.DPT_Int64:
            print("int64")
        #     return self.decode_int64()
        elif ptype == PropTypes.DPT_Array:
            return self.decode_array()
        else:
            print("ELSE")
            return None


def read_field_index(data, last_index, new_way):
    ret = 0
    val = 0
    if new_way and data.readBit():
        return last_index + 1
    if new_way and data.readBit():
        ret = data.readUBitLong(3)
    else:
        ret = data.readUBitLong(7)
        val = ret & (32 | 64)
        if val == 32:
            ret = (ret & ~96) | (data.readUBitLong(2) << 5)
            # assert ret >= 32
        elif val == 64:
            ret = (ret & ~96) | (data.readUBitLong(4) << 5)
            # assert ret >= 128
        elif val == 96:
            ret = (ret & ~96) | (data.readUBitLong(7) << 5)
            # assert ret >= 512
    if ret == 0xfff:
        return -1
    return last_index + 1 + ret


def parse_entity_update(data, svcls, dtbl):
    val = -1
    decoded_props = []
    field_indices = []
    new_way = data.readBit()
    while True:
        val = read_field_index(data, val, new_way)
        if val == -1:
            break
        field_indices.append(val)
    # print("proplen= {} / fi= {}".format(len(svcls.propss), len(field_indices)))
    for index in field_indices:
        # print("index= {} / proplen= {} / fi= {}".format(index, len(svcls.propss), len(field_indices)))
        prop = svcls.propss[index]
        decoder = Decoder(data, prop)
        value = decoder.decode()
        decoded_props.append([prop["prop"].var_name, value])
    return decoded_props


def parseBaselines(baseline_list, sv_cls_list, data_tbls):
    for item in baseline_list:
        data = CBitRead(item[1])
        class_baseline = dict()
        # print("id1= {} / id2= {} / name= {}".format(item[0], sv_cls_list[item[0]].classID, sv_cls_list[item[0]].name))
        index = 0
        for baseline in parse_entity_update(data, sv_cls_list[item[0]], data_tbls):
            while True:
                if sv_cls_list[item[0]].propss[index]["prop"].var_name != baseline[0]:
                    index += 1
                else:
                    break
            class_baseline.update({baseline[0]: baseline[1]})
            index += 1
            # print(sv_cls_list[item[0]].propss[index]["prop"].var_name)
            # print(baseline)
        sv_cls_list[item[0]].valuess.update(class_baseline)
        # print(sv_cls_list[item[0]].valuess)


def flatten(name, data_tables):
    exclusion_list = prop_excludes(name, data_tables)
    flat_props = get_propss(name, data_tables, exclusion_list)
    priorities = list(dict.fromkeys(p["prop"].priority for p in flat_props))
    priorities.append(64)
    priorities = sorted(priorities)
    # print(priorities)
    # print("LP= {} / LPRIO= {}".format(len(flat_props), len(priorities)))
    start = 0
    for prio in priorities:
        while True:
            current_prop = start
            while current_prop < len(flat_props):
                prop = flat_props[current_prop]["prop"]
                if prop.priority == prio or (prio == 64 and prop.flags & PropFlags.SPROP_CHANGES_OFTEN):
                    if start != current_prop:
                        temp = flat_props[start]
                        flat_props[start] = flat_props[current_prop]
                        flat_props[current_prop] = temp
                    start += 1
                    break
                current_prop += 1
            if current_prop == len(flat_props):
                break
    return flat_props


# def flatten(name, data_tables):
#     exclusion_list = prop_excludes(name, data_tables)
#     flat_props = get_propss(name, data_tables, exclusion_list)
#     priorities = list(p["prop"].priority for p in flat_props)
#     priorities.append(64)
#     priorities = sorted(priorities)
#     print("LP= {} / LPRIO= {}".format(len(flat_props), len(priorities)))
#     start = 0
#     for prio in priorities:
#         while True:
#             current_prop = start
#             while current_prop < len(flat_props):
#                 prop = flat_props[current_prop]["prop"]
#                 if prop.priority == prio or prio == 64 and (prop.flags & PropFlags.SPROP_CHANGES_OFTEN):
#                     if start != current_prop:
#                         temp = flat_props[start]
#                         flat_props[start] = flat_props[current_prop]
#                         flat_props[current_prop] = temp
#                     start += 1
#                     break
#                 current_prop += 1
#             if current_prop == len(flat_props):
#                 break
#     return flat_props


def get_propss(name, data_tables, excl_list):
    flat_table = list()
    for index in range(len(data_tables[name].props)):
        prop = data_tables[name].props[index]
        if (prop.flags & PropFlags.SPROP_INSIDEARRAY) or (prop.flags & PropFlags.SPROP_EXCLUDE) or _is_prop_excluded(
                excl_list, name, prop):
            # print("EXCL> ", prop)
            continue
        if prop.type == PropTypes.DPT_DataTable:
            child_props = get_propss(prop.dt_name, data_tables, excl_list)
            # if prop.flags & PropFlags.SPROP_COLLAPSIBLE == 0:
                # for prop2 in child_props:
                #     prop2.update({"col": False})
                # pass
            flat_table.extend(child_props)
        elif prop.type == PropTypes.DPT_Array:
            flat_table.append({"prop": prop,
                               "arprop": data_tables[name].props[index - 1]})
        else:
            flat_table.append({"prop": prop})
        index += 1
    return flat_table


def prop_excludes(name, data_tables):
    excludes = list()
    for prop in data_tables[name].props:
        if prop.flags & PropFlags.SPROP_EXCLUDE:
            excludes.append(prop)
        if prop.type == PropTypes.DPT_DataTable:
            excludes.extend(prop_excludes(prop.dt_name, data_tables))
    return excludes


def _is_prop_excluded(excl, table, prop):
    for item in excl:
        if table == item.dt_name and prop.var_name == item.var_name:
            return True
