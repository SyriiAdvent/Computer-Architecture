"""CPU functionality."""

import sys
import os
dirpath = os.path.dirname(os.path.abspath(__file__))
examplespath = os.path.dirname(os.path.abspath(__file__)) + '/examples'
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.fl = [0] * 8
        self.pc = 0
        self.MAR = 0  # Memory Address Register
        self.MDR = 0 # Memory Data Register
        self.instructions = {}
        self.instructions[0b10000010] = self.handle_LDI
        self.instructions[0b01000111] = self.handle_PRN
        self.instructions[0b00000001] = self.handle_HLT
        # self.instructions[10000100] = self.handle_ST
        self.instructions[0b10100010] = self.handle_MUL
        self.instructions[0b10100000] = self.handle_ADD

    def load(self):
        """Load a program into memory."""
        program = sys.argv[1]

        with open(program) as file:
            for line in file:
                # if the line is a line break or a comment, don't add to memory
                if line[0] is '#' or line[0] is '\n':
                    continue
                self.MDR = int(line[:8], 2) # only read the command code
                self.ram_write(self.MDR, self.MAR)
                self.MAR += 1
        print(self.ram)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def handle_LDI(self):
        self.MAR = self.ram_read(self.pc + 1)
        self.MDR = self.ram_read(self.pc + 2)
        self.reg[self.MAR] = self.MDR
        self.pc += 3

    def handle_PRN(self):
        self.MAR = self.ram_read(self.pc + 1)
        print(self.reg[self.MAR])
        self.pc += 2

    def handle_HLT(self):
        self.running = False
        self.pc += 1

    def handle_MUL(self):
        self.alu('MUL', self.pc + 1, self.pc + 2)
        self.pc += 3

    def handle_ADD(self):
        self.alu('ADD', self.PC + 1, self.pc + 2)
        self.pc += 3
    

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.MAR = self.ram_read(reg_b)
            self.MDR = self.reg[self.MAR]
            self.MAR = self.ram_read(reg_a)
            self.MDR = self.MDR + self.reg[self.MAR]
            self.REG[self.MAR] = self.MDR
        elif op == "MUL":
            self.MAR = self.ram_read(reg_b)
            self.MDR = self.reg[self.MAR]
            self.MAR = self.ram_read(reg_a)
            self.MDR = self.MDR * self.reg[self.MAR]
            self.reg[self.MAR] = self.MDR
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            self.IR = self.ram_read(self.pc)
            if self.IR in self.instructions:
                self.instructions[self.IR]()
            else:
                print(f'Unknown instruction {self.IR} at address {self.pc}')
                sys.exit(1)

    def ram_read(self, memory_address):
        return self.ram[memory_address]

    def ram_write(self, memory_data, memory_address):
        self.ram[memory_address] = memory_data
