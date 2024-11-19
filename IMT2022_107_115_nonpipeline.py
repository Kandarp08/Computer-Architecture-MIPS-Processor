# Choose which program needs to be executed
print("1. Fibonacci Numbers")
print("2. Factorials of first 10 numbers")
choice = int(input("Enter appropriate number: "))

n = "Garbage value"
Inputs = "Garbage value"
# Fibonacci program
if choice == 1:
    
    Inputs = int(input("Enter starting address of data memory: "))
    n = int(input("Enter number of fibonacci numbers to be calculated: "))
    with open('fibonacci_binary.txt') as f:
        lines = f.readlines()
    PC = 4194328

# Factorial program
elif choice == 2:
    
    Inputs = int(input("Enter starting address of data memory: "))
    n = 10
    with open('factorial_binary.txt') as f:
        lines = f.readlines()
    PC = 4194304

#Use a for loop to read "machine code input" from the text file & store it in a python dictionary
#Types of dictionarys: Instruction memory, register file, data memory
InstructionMemory = {}  #Number(address) to string(instruction) mapping
RegisterFile = {"s0": "Garbage value", "s1": "Garbage value", "s2": "Garbage value", "s3": "Garbage value", "s4": "Garbage value", "s5": "Garbage value", "s6": "Garbage value", "s7": "Garbage value", "0": 0,   
                "t0": "Garbage value", "t1": n,  "t2": Inputs, "t3": "Garbage value", "t4": "Garbage value", "t5": "Garbage value", "t6": "Garbage value", "t7": "Garbage value"}       #string(register name) to Number(register content value) mapping
DataMemory = {}         #Number(address) to Number(data value) mapping

registerNumberMapping = {16: "s0", 17: "s1", 18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7", 0: "0",   
                          8: "t0", 9: "t1",  10: "t2", 11: "t3", 12: "t4", 13: "t5", 14: "t6", 15: "t7"}

# In case of factorial program
if choice == 2:

    RegisterFile["t3"] = Inputs
    RegisterFile["t2"] = "Garbage value"

for i in range(len(lines)):
    InstructionMemory[PC + (i * 4)] = lines[i]
clockCycles = 0
PCMax = PC + (4 * len(lines))
print("PCMax = ", PCMax)

# Returns the decimal nummber corresponding to the binary number represented by str
def binaryToDecimal(str):

    decimal = 0 # Final answer

    # Decimal number = summation of ((2 ** i) * (bit at position (len(str) - i - 1)))
    for i in range(len(str)):
        decimal += (2 ** i) * int(str[len(str) - i - 1])

    return decimal
    
while (PC < PCMax):
    #Instruction fetch stage
        #Just access the dictionary and store the instruction in a variable
        currInstruction = InstructionMemory[PC]
        PC = PC + 4
        clockCycles = clockCycles + 1
        print("currInstruction = ", currInstruction)

    #Decode stage + register read
        #Read the first 6 bits (opcode) & figure out whether its an R, I or J format instruction
        #Map opcodes, registers, funct fields using their key-value pairs in a dictionary
        #Read values of registers using the above dictionary & access elements of the 'register file' dictionary
        #Perform instruction specific operations for LW/SW, Add/Addi, BEQ, J etc
        opcode = currInstruction[0:6]
        instructionToPerform = ""       #Like a Control signal which tells the ALU what instruction to perform
        rs = ""
        rt = ""
        rd = ""
        shamt = ""
        funct = ""
        immediate = ""
        #R-format instructions
        if (opcode == "000000"):
            rs = currInstruction[6:11]
            rt = currInstruction[11:16]
            rd = currInstruction[16:21]
            shamt = currInstruction[21:26]
            funct = currInstruction[26:32]

            if (funct == "100000"):
                instructionToPerform = "add"
        
        if (opcode == "011100"):
            rs = currInstruction[6:11]
            rt = currInstruction[11:16]
            rd = currInstruction[16:21]
            shamt = currInstruction[21:26]
            funct = currInstruction[26:32]
            instructionToPerform = "mul"
            
        #I-format instructions
        elif (opcode == "001000"):
            rs = currInstruction[6:11]
            rt = currInstruction[11:16]
            immediate = currInstruction[16:32]
            instructionToPerform = "addi"

        elif (opcode == "101011"):
            rs = currInstruction[6:11]
            rt = currInstruction[11:16]
            immediate = currInstruction[16:32]
            instructionToPerform = "sw"

        elif (opcode == "100011"):
            rs = currInstruction[6:11]
            rt = currInstruction[11:16]
            immediate = currInstruction[16:32]
            instructionToPerform = "lw"

        elif (opcode == "000100"):
            rs = currInstruction[6:11]
            rt = currInstruction[11:16]
            immediate = currInstruction[16:32]
            instructionToPerform = "beq"

        #J-format instructions
        elif (opcode == "000010"):
            immediate = currInstruction[6:32]
            instructionToPerform = "jump"

        print("instructionToPerform = ", instructionToPerform)
        print("opcode = ", opcode)
        clockCycles = clockCycles + 1

    #ALU stage
        #Perform simple arithmetic operations using python operators
        ALUOutput = "Garbage value"
        rsRegister = registerNumberMapping[binaryToDecimal(rs)]
        rtRegister = registerNumberMapping[binaryToDecimal(rt)]
        if (instructionToPerform == "add"):
            ALUOutput = RegisterFile[rsRegister] + RegisterFile[rtRegister]
        if (instructionToPerform == "mul"):
            ALUOutput = RegisterFile[rsRegister] * RegisterFile[rtRegister]
        elif (instructionToPerform == "addi" or instructionToPerform == "sw" or instructionToPerform == "lw"):
            ALUOutput = RegisterFile[rsRegister] + binaryToDecimal(immediate)
        elif (instructionToPerform == "beq"):
            ALUOutput = RegisterFile[rsRegister] - RegisterFile[rtRegister]
        elif (instructionToPerform == "jump"):
            PC = binaryToDecimal("0000" + currInstruction[6:32] + "00")
        print("ALUOutput = ", ALUOutput)
        clockCycles = clockCycles + 1
        
    #Memory access
        #Access the 'data memory' dictionary and read from it or write to it according to the instruction
        dataMemoryOutput = "Garbage value"
        dataToWriteToMemory = "Garbage value"
        if (instructionToPerform == "sw"):
            dataToWriteToMemory = RegisterFile[registerNumberMapping[binaryToDecimal(rt)]]
            DataMemory[ALUOutput] = dataToWriteToMemory
        elif (instructionToPerform == "lw"):
            dataMemoryOutput = DataMemory[ALUOutput]
        elif (instructionToPerform == "beq" and (ALUOutput == 0)):
            PC = PC + (binaryToDecimal(immediate) * 4)                   #We did not add an additional +4 because that was already done at the end of IF stage
        print("dataMemoryOutput = ", dataMemoryOutput)
        print("dataToWriteToMemory = ", dataToWriteToMemory)
        clockCycles = clockCycles + 1

    #Register writeback
        #Perform register writeback (if required)
        writebackDestination = ""
        dataToWriteToRegister = 0
        if (instructionToPerform == "add"):
            writebackDestination = registerNumberMapping[binaryToDecimal(rd)]
            dataToWriteToRegister = ALUOutput
        elif (instructionToPerform == "mul"):
            writebackDestination = registerNumberMapping[binaryToDecimal(rd)]
            dataToWriteToRegister = ALUOutput
        elif (instructionToPerform == "addi"):
            writebackDestination = registerNumberMapping[binaryToDecimal(rt)]
            dataToWriteToRegister = ALUOutput
        elif (instructionToPerform == "lw"):
            writebackDestination = registerNumberMapping[binaryToDecimal(rt)]
            dataToWriteToRegister = dataMemoryOutput

        # In case of instructions like sw where no write back is needed
        if (writebackDestination != ""):
            RegisterFile[writebackDestination] = dataToWriteToRegister
        
        print("writebackDestination = ", writebackDestination)
        print("dataToWriteToRegister = ", dataToWriteToRegister)
        clockCycles = clockCycles + 1

    #Increase the clock cycle variable by 1 after an instruction is executed (Print it after every instruction)
        print("clock cycles = ", clockCycles)
        print("PC = ", PC)

print("Total number of clock cycles = ", clockCycles)

print("\n\n")
print("Register Values: ")

for key in RegisterFile:
    print(f"${key}: {RegisterFile[key]}")
print("\n\n")
print("Data Memory: ")
for key in DataMemory:
    print(f"{key}: {DataMemory[key]}")