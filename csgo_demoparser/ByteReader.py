import struct


class Bytebuffer:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def read(self, num_bytes):
        data = self.data[self.index:self.index + num_bytes]
        self.index += num_bytes
        return data

    # def read_byte(self):
    #     data = self.read(1)
    #     data = struct.unpack("B", data)[0]
    #     return data

    def read_int(self):
        data = self.read(4)
        data = struct.unpack("<I", data)[0]
        return data

    def read_short(self):
        return struct.unpack("<H", self.read(2))[0]

    # def read_string(self):
    #     text = ""
    #     while True:
    #         data = self.read_byte()
    #         if data == 0:
    #             break
    #         text += chr(data)
    #     return text

    # def read_demo_header(self):
    #     return DemoHeader(self.read(1072))

    # def read_command_header(self):
    #     # cmd = struct.unpack("B", self.read(1))[0]
    #     # tick = struct.unpack("<i", self.read(4))[0]
    #     # pl_id = struct.unpack("B", self.read(1))[0]
    #     # return cmd, tick, pl_id
    #     return CommandHeader(self.read(6))

    # def read_command_data(self):
    #     self.read(152)
    #
    # def read_sequence_data(self):
    #     return struct.unpack("<ii", self.read(8))
    #
    # def read_user_command(self):
    #     seq = struct.unpack("<i", self.read(4))[0]
    #     length, buf = self.read_raw_data()
    #     return seq
    #
    # def read_packet_data(self):
    #     length = struct.unpack("<i", self.read(4))[0]
    #     index = 0
    #     while index < length:
    #         cmd = self.read_varint()
    #         size = self.read_varint()
    #         data = self.read(size)
    #         index = index + size + self.varint_size(cmd) + self.varint_size(size)
    #         yield cmd, size, data

    # def read_raw_data(self):
    #     length = struct.unpack("<i", self.read(4))[0]
    #     buf = self.read(length)
    #     return length, buf

    # def read_bitstream(self):
    #     length, buf = self.read_raw_data()
    #     return bit.BitRead(buf)

    # def read_var_bytes(self):
    #     length = self.read_varint()
    #     return self.read(length)

    def read_string(self):
        output = []
        while True:
            char = struct.unpack("<B", self.read(1))[0]
            if char == 0:
                break
            output.append(chr(char))
        return "".join(output)

    def read_varint(self):
        b = 0
        count = 0
        result = 0
        cont = True
        while cont:
            data = self.read(1)
            b = struct.unpack("B", data)
            b = b[0]
            if count < 5:
                result |= (b & 0x7F) << (7 * count)
            count += 1
            cont = b & 0x80
        return result

    def varint_size(self, value):
        if value < (1 << 7):
            return 1
        elif value < (1 << 14):
            return 2
        elif value < (1 << 21):
            return 3
        elif value < (1 << 28):
            return 4
        else:
            return 5
