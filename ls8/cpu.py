"""CPU functionality."""

import sys
import os
dirpath = os.path.dirname(os.path.abspath(__file__))
examplespath = os.path.dirname(os.path.abspath(__file__)) + '/examples'
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.RAM = [0] * 256
        self.REG = [0] * 8
        self.FL = [0] * 8
        self.PC = 0
        self.MAR = 0  # Memory Address Register
        self.MDR = 0 # Memory Data Register
        self.SP = 0xF4
        self.instructions = {
            0b10000010 : self.handle_LDI,
            0b01000111 : self.handle_PRN,
            0b00000001 : self.handle_HLT,
            0b10100000 : self.handle_ADD,
            0b10100010 : self.handle_MUL,
            0b01000110: self.handle_POP,
            0b01000101: self.handle_PUSH,
            0b00010001: self.handle_RET,
            0b01010000: self.handle_CALL,
        }

        self.alu_operations = {
            'MUL': self.ALU_MUL,
            'ADD': self.ALU_ADD
         }

    def bitwise_addition(self, num1, num2):
        if num2 <= 0:
            return num1
        else:
            return self.bitwise_addition(num1 ^ num2, (num1 & num2) << 1)

    def bitwise_subtraction(self, num1, num2):
        if num2 <= 0:
            return num1
        else:
            return self.bitwise_subtraction(num1 ^ num2, (~num1 & num2) << 1)

    def bitwise_multiplication(self, num1, num2):
        product = 0
        count = 0
        while num2 > 0:
            if num2 % 2 == 1:
                product += num1 << count
            count += 1
            num2 = num2 // 2
        return product

    def bitwise_division(self, num1, num2):
        sign = 1
        if num1 < 0 ^ num2 < 0:
            sign = -1
        num1 = abs(num1)
        num2 = abs(num2)
        quotient = 0
        temp = 0
        for i in range(7, -1, -1): 
            if (temp + (num2 << i) <= num1): 
                temp += num2 << i 
                quotient |= 1 << i
        return sign * quotient

    def load(self):
        """Load a program into memory."""
        program = sys.argv[1]

        with open(program) as file:
            for line in file:
                # if the line is a line break or a comment, don't add to memory
                if line[0] == '#' or line[0] == '\n':
                    continue
                self.MDR = int(line[:8], 2) # only read the command code
                self.ram_write(self.MDR, self.MAR)
                self.MAR += 1
        print(self.RAM)

    def handle_LDI(self, ops):
        self.MAR = self.ram_read(self.PC + 1)
        self.MDR = self.ram_read(self.PC + 2)
        self.REG[self.MAR] = self.MDR
        self.PC = self.bitwise_addition(self.PC, ops)

    def handle_LD(self, ops):
        self.MAR = self.reg[self.PC + 2]
        self.MDR = self.ram_read(self.MAR)
        self.MAR = self.PC + 1
        self.reg[self.MAR] = self.MDR

    def handle_PRN(self, ops):
        self.MAR = self.ram_read(self.PC + 1)
        print(self.REG[self.MAR])
        self.PC = self.bitwise_addition(self.PC, ops)

    def handle_PRA(self, ops):
        self.MAR = self.ram_read(self.PC + 1)
        self.MDR = self.REG[self.MAR]
        print(chr(self.MDR))
        self.PC = self.bitwise_addition(self.PC, ops)

    def handle_MUL(self, ops):
        self.alu('MUL', self.PC + 1, self.PC + 2)
        self.PC = self.bitwise_addition(self.PC, ops)

    def handle_ADD(self, ops):
        self.alu('ADD', self.PC + 1, self.PC + 2)
        self.PC = self.bitwise_addition(self.PC, ops)
    
    def handle_HLT(self, ops):
        self.running = False
        self.PC = self.bitwise_addition(self.PC, ops)

    def handle_POP(self, ops):
        if self.SP == 0xF4:
            print('Stack is empty!')
            sys.exit(1)
        self.MAR = self.SP
        self.MDR = self.ram_read(self.MAR)
        self.MAR = self.PC + 1
        self.REG[self.ram_read(self.MAR)] = self.MDR
        self.SP = self.bitwise_addition(self.SP, 1)
        self.PC = self.bitwise_addition(self.PC, ops)

    def handle_PUSH(self, ops):
        self.SP = self.bitwise_subtraction(self.SP, 1)
        if self.SP <= self.PC + 1:
            print('Stack overflow!')
            sys.exit(1)
        self.MAR = self.ram_read(self.PC + 1)
        self.MDR = self.REG[self.MAR]
        self.ram_write(self.MDR, self.SP)
        self.PC = self.bitwise_addition(self.PC, ops)
    
    def handle_RET(self, ops):
        # Pop the value from the top of the stack and store it in the `PC`.
        if self.SP == 0xF4:
            print('Stack is empty!')
            sys.exit(1)
        self.PC = self.ram_read(self.SP)
        self.SP = self.bitwise_addition(self.SP, 1)

    def handle_CALL(self, ops):
        self.MAR = self.bitwise_addition(self.PC, ops)
        self.SP = self.bitwise_subtraction(self.SP, 1)
        if self.SP == self.PC:
            print(f'Stack overflow!')
            sys.exit(1)
        self.ram_write(self.MAR, self.SP)
        self.MAR = self.ram_read(self.PC + 1)
        self.PC = self.REG[self.MAR]

    

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op in self.alu_operations:
            self.alu_operations[op](reg_a, reg_b)
        else:
            raise Exception("Unsupported ALU operation")

    def ALU_ADD(self, reg_a, reg_b):
        self.MAR = self.ram_read(reg_b)
        self.MDR = self.REG[self.MAR]
        self.MAR = self.ram_read(reg_a)
        self.MDR = self.bitwise_addition(self.MDR, self.REG[self.MAR])
        self.MDR = self.MDR & 0xFF
        self.REG[self.MAR] = self.MDR

    def ALU_MUL(self, reg_a, reg_b):
        self.MAR = self.ram_read(reg_b)
        self.MDR = self.REG[self.MAR]
        self.MAR = self.ram_read(reg_a)
        self.MDR = self.bitwise_multiplication(self.reg[self.MAR], self.MDR)
        self.MDR = self.MDR & 0xFF
        self.reg[self.MAR] = self.MDR

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            self.IR = self.ram_read(self.PC)
            if self.IR in self.instructions:
                num_operations = ((self.IR & 0b11000000) >> 6) + 1
                self.instructions[self.IR](num_operations)
            else:
                print(f'Unknown instruction {self.IR} at address {self.PC}')
                sys.exit(1)

    def ram_read(self, memory_address):
        return self.RAM[memory_address]

    def ram_write(self, memory_data, memory_address):
        self.RAM[memory_address] = memory_data
