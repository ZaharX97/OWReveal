import math


class Bitbuffer:
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
            
    # Add 32 bits free to use and grab new data to buffer
    def fetchNext(self):
        self.bitsFree = 32
        self.grabNext4Bytes()    
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
    # ---------------------------------------------------------
    
    # Read VAR
    def readUBitVar(self):
        ret = self.read_uint_bits(6)
        if ret & 48 == 16:
            ret = (ret & 15) | (self.read_uint_bits(4) << 4)
        elif ret & 48 == 32:
            ret = (ret & 15) | (self.read_uint_bits(8) << 4)
        elif ret & 48 == 48:
            ret = (ret & 15) | (self.read_uint_bits(28) << 4)
        return ret

    def read_var_int(self):
        ret = 0
        count = 0
        while True:
            if count == 5:
                return ret
            b = self.read_uint_bits(8)
            ret |= (b & 0x7F) << (7 * count)
            count += 1
            if not (b & 0x80):
                break
        return ret

    # Read unsigned n-bits
    def read_uint_bits(self, a_bits):
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
    def read_sint_bits(self, a_bits):
        return (self.read_uint_bits(a_bits) << (32 - a_bits)) >> (32 - a_bits)

    # Read string
    def read_string(self, length=0):
        res = ""
        index = 1
        while True:
            char = self.read_sint_bits(8)
            if char == 0 and length == 0:
                break
            res += chr(char)
            if index == length:
                break
            index += 1
        return res

    # Read n-bits
    def readBits(self, a_bits):
        res = b""
        bitsleft = a_bits
        while bitsleft >= 32:
            res += bytes([self.read_uint_bits(8), self.read_uint_bits(8), self.read_uint_bits(8), self.read_uint_bits(8)])
            bitsleft -= 32
        while bitsleft >= 8:
            res += bytes([self.read_uint_bits(8)])
            bitsleft -= 8
        if bitsleft:
            res += bytes([self.read_uint_bits(bitsleft)])
        return res

    # Read n-bytes
    def readBytes(self, a_bytes):
        return self.readBits(a_bytes << 3)

    # Read 1 bit
    def read_bit(self):
        aBit = self.dataPart & 1
        self.bitsFree -= 1
        if self.bitsFree == 0:
            self.fetchNext()
        else:
            self.dataPart >>= 1
        return aBit
