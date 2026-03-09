import sys

# Register aliases mapped explicitly to binary codes
registers = {
    "zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100",
    "t0": "00101", "t1": "00110", "t2": "00111",
    "s0": "01000", "fp": "01000",  # alias
    "s1": "01001",
    "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101",
    "a4": "01110", "a5": "01111", "a6": "10000", "a7": "10001",
    "s2": "10010", "s3": "10011", "s4": "10100", "s5": "10101",
    "s6": "10110", "s7": "10111", "s8": "11000", "s9": "11001",
    "s10": "11010", "s11": "11011",
    "t3": "11100", "t4": "11101", "t5": "11110", "t6": "11111"
}

# Instruction formats
R_type = {
    "add": ("000", "0000000"),
    "sub": ("000", "0100000"),
    "sll": ("001", "0000000"),
    "slt": ("010", "0000000"),
    "sltu": ("011", "0000000"),
    "xor": ("100", "0000000"),
    "srl": ("101", "0000000"),
    "or":  ("110", "0000000"),
    "and": ("111", "0000000")
}

I_type = {
    "lw":    ("010", "0000011"),
    "addi":  ("000", "0010011"),
    "sltiu": ("011", "0010011"),
    "jalr":  ("000", "1100111")
}

S_type = {"sw": ("010", "0100011")}

B_type = {
    "beq": "000", "bne": "001", "blt": "100", "bge": "101",
    "bltu": "110", "bgeu": "111"
}

U_type = {"lui": "0110111", "auipc": "0010111"}
J_type = {"jal": "1101111"}


def to_binary(val, bits):
    """Convert integer to two's complement binary string of given width."""
    val = int(val)
    if val < 0:
        val = (1 << bits) + val
    return format(val & ((1 << bits) - 1), f'0{bits}b')


def get_reg(reg):
    try:
        return registers[reg]
    except KeyError:
        raise ValueError(f"Invalid register: {reg}")


def parse(lines):
    """Parse assembly lines into instructions and label map."""
    labels = {}
    instructions = []
    pc = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if ":" in line:
            label, rest = line.split(":", 1)
            labels[label.strip()] = pc
            line = rest.strip()
            if not line:
                continue

        instructions.append(line)
        pc += 4

    return instructions, labels


def assemble(lines):
    instructions, labels = parse(lines)
    pc = 0
    output = []

    for line in instructions:
        parts = line.replace(",", " ").replace("(", " ").replace(")", " ").split()
        op = parts[0]

        if op in R_type:
            rd, rs1, rs2 = parts[1], parts[2], parts[3]
            funct3, funct7 = R_type[op]
            opcode = "0110011"
            binary = funct7 + get_reg(rs2) + get_reg(rs1) + funct3 + get_reg(rd) + opcode

        elif op in I_type:
            if op == "lw":
                rd, imm, rs1 = parts[1], parts[2], parts[3]
            else:
                rd, rs1, imm = parts[1], parts[2], parts[3]
            funct3, opcode = I_type[op]
            imm_bin = to_binary(imm, 12)
            binary = imm_bin + get_reg(rs1) + funct3 + get_reg(rd) + opcode

        elif op in S_type:
            rs2, imm, rs1 = parts[1], parts[2], parts[3]
            funct3, opcode = S_type[op]
            imm_bin = to_binary(imm, 12)
            binary = imm_bin[:7] + get_reg(rs2) + get_reg(rs1) + funct3 + imm_bin[7:] + opcode

        elif op in B_type:
            rs1, rs2, target = parts[1], parts[2], parts[3]
            offset = labels.get(target, int(target)) - pc
            imm = to_binary(offset, 13)
            funct3 = B_type[op]
            opcode = "1100011"
            binary = imm[0] + imm[2:8] + get_reg(rs2) + get_reg(rs1) + funct3 + imm[8:12] + imm[1] + opcode

        elif op in U_type:
            rd, imm = parts[1], parts[2]
            opcode = U_type[op]
            imm_bin = to_binary(imm, 20)
            binary = imm_bin + get_reg(rd) + opcode

        elif op in J_type:
            rd, target = parts[1], parts[2]
            offset = labels.get(target, int(target)) - pc
            imm = to_binary(offset, 21)
            opcode = J_type[op]
            binary = imm[0] + imm[10:20] + imm[9] + imm[1:9] + get_reg(rd) + opcode

        else:
            raise ValueError(f"Invalid instruction: {op}")

        output.append(binary)
        pc += 4

    return output


def main():
    if len(sys.argv) != 3:
        print("Usage: assembler.py <input_file> <output_file>")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]

    with open(input_file, "r") as f:
        lines = f.readlines()

    try:
        result = assemble(lines)
    except ValueError as e:
        print(f"Assembly error: {e}")
        sys.exit(1)

    with open(output_file, "w") as f:
        for line in result:
            f.write(line + "\n")


if __name__ == "__main__":
    main()