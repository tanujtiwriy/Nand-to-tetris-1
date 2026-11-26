
import sys
import re

# ---------- PREDEFINED SYMBOLS ----------

symbol_table = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

for i in range(16):
    symbol_table["R" + str(i)] = i


# ---------- C-INSTRUCTION TABLES ----------

comp_table = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

dest_table = {
    "null": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

jump_table = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


# ---------- CLEAN SOURCE CODE ----------

def clean_file(input_file):
    instructions = []

    with open(input_file, "r") as file:
        for line_number, line in enumerate(file, start=1):

            line = line.split("//")[0]
            line = line.strip()
            line = line.replace(" ", "").replace("\t", "")

            if line:
                instructions.append((line_number, line))

    return instructions


# ---------- FIRST PASS ----------

def first_pass(instructions):
    global symbol_table

    rom_address = 0
    user_symbols = {}

    for line_number, command in instructions:

        if command.startswith("(") and command.endswith(")"):

            label = command[1:-1]

            if not re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", label):
                raise ValueError(
                    f"Line {line_number}: invalid label"
                )

            if label in symbol_table:
                raise ValueError(
                    f"Line {line_number}: duplicate or reserved label {label}"
                )

            symbol_table[label] = rom_address
            user_symbols[label] = rom_address

        else:
            if command.startswith("(") or command.endswith(")"):
                raise ValueError(
                    f"Line {line_number}: invalid label syntax"
                )

            rom_address += 1

    return user_symbols


# ---------- A-INSTRUCTION ----------

def a_instruction(command, variables):

    value = command[1:]

    if value.isdigit():
        number = int(value)

    else:
        if not re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", value):
            raise ValueError("invalid symbol")

        if value not in symbol_table:
            symbol_table[value] = variables[0]
            variables[0] += 1

        number = symbol_table[value]

    if number < 0 or number > 32767:
        raise ValueError("address out of range")

    return format(number, "016b")


# ---------- C-INSTRUCTION ----------

def c_instruction(command):

    dest = "null"
    jump = "null"

    if command.count("=") > 1 or command.count(";") > 1:
        raise ValueError("invalid C-instruction")

    if "=" in command:
        dest, command = command.split("=")

    if ";" in command:
        comp, jump = command.split(";")
    else:
        comp = command

    if dest not in dest_table:
        raise ValueError("invalid destination")

    if comp not in comp_table:
        raise ValueError("invalid computation")

    if jump not in jump_table:
        raise ValueError("invalid jump")

    return (
        "111"
        + comp_table[comp]
        + dest_table[dest]
        + jump_table[jump]
    )


# ---------- SECOND PASS ----------

def second_pass(instructions):

    machine_code = []
    variables = [16]

    for line_number, command in instructions:

        try:
            if command.startswith("@"):
                binary = a_instruction(command, variables)

            elif command.startswith("("):
                continue

            else:
                binary = c_instruction(command)

            machine_code.append(binary)

        except (ValueError, KeyError) as error:
            raise ValueError(
                f"Line {line_number}: {error}"
            ) from error

    return machine_code


# ---------- SAVE SYMBOLS ----------

def save_symbols(user_symbols, output_file):
    predefined = {"SP", "LCL", "ARG", "THIS", "THAT", "SCREEN", "KBD"}
    predefined |= {"R" + str(i) for i in range(16)}

    with open(output_file, "w") as file:
        for name, address in user_symbols.items():
            file.write(f"{name} = {address}\n")
        for name, address in symbol_table.items():
            if name not in user_symbols and name not in predefined:
                file.write(f"{name} = {address}\n")

# ---------- MAIN ASSEMBLER ----------

def assemble_file(input_file, output_file):

    global symbol_table

    symbol_table = {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576
    }

    for i in range(16):
        symbol_table["R" + str(i)] = i

    try:
        instructions = clean_file(input_file)

        # First pass
        user_symbols = first_pass(instructions)

        # Second pass
        machine_code = second_pass(instructions)

        # Save binary output
        with open(output_file, "w") as file:
            for instruction in machine_code:
                file.write(instruction + "\n")

        # Save labels and variables
        symbols_file = "symbols.txt"
        save_symbols(user_symbols, symbols_file)

        print("Assembly completed successfully!")
        print("Output saved in:", output_file)
        print("Symbols saved in:", symbols_file)

    except (ValueError, OSError) as error:
        print("Assembler Error:", error)


# ---------- PROGRAM ENTRY ----------

if __name__ == "__main__":

    input_file = sys.argv[1] if len(sys.argv) > 1 else "test.asm"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "test.hack"

    assemble_file(input_file, output_file)
