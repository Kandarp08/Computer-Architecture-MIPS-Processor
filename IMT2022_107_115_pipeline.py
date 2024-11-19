# Returns the decimal nummber corresponding to the binary number represented by str
def binaryToDecimal(str):

    decimal = 0 # Final answer

    # Decimal number = summation of ((2 ** i) * (bit at position (len(str) - i - 1)))
    for i in range(len(str)):
        decimal += (2 ** i) * int(str[len(str) - i - 1])

    return decimal

# Returns the value of the key from the given dictionary. Returns None if key is not found in dictionary
def getValueFromDictionary(key, dict):

    if key in dict:
        return dict[key]
    
    return None

# Fetch instruction from instruction memory
def instructionFetch(PC, instructionMemory):

    return instructionMemory[PC] # Return the instruction corresponding to PC
    
# Decodes the instruction and returns a list containing rs, rt, immediate value, etc.
def instructionDecode(instruction, registerToValue, registerToClockCycle, registerToWB, executeValues, curr_clock_cycle, instructionNumber, codeToRegister):

    opcode = instruction[0: 6] # Opcode of instruction

    global forwardingMessages # To print forwarding messages

    # R-format instruction (ADD or MUL)
    if opcode == "000000" or opcode == "011100":

        rs = binaryToDecimal(instruction[6: 11])  # Source register 1
        rt = binaryToDecimal(instruction[11: 16]) # Source register 2
        rd = binaryToDecimal(instruction[16: 21]) # Destination register

        rs_value = registerToValue[rs] # Current value of rs
        rt_value = registerToValue[rt] # CUrrent value of rt

        funct = instruction[26: 32] # Function field to identify operation

        return [opcode, rs, rs_value, rt, rt_value, rd, funct] # Return the decoded instruction
    
    # Add immediate instruction / Store word instruction / Load word instruction / BEQ instruction
    elif opcode == "001000" or opcode == "101011" or opcode == "100011" or opcode == "000100":

        rs = binaryToDecimal(instruction[6: 11])            # Source register 1
        rt = binaryToDecimal(instruction[11: 16])           # Destination register
        immediateVal = binaryToDecimal(instruction[16: 32]) # Immediate value

        rs_value = registerToValue[rs] # Current value of rs
        rt_value = registerToValue[rt] # Current value of rt

        # Implement fast branching for BEQ instruction
        if opcode == "000100":

            wb_rs = getValueFromDictionary(rs, registerToWB) # Clock cycle at which WB of rs occurs
            wb_rt = getValueFromDictionary(rt, registerToWB) # Clock cycle at which WB of rt occurs

            t_rs = getValueFromDictionary(rs, registerToClockCycle) # Clock cycle when value of rs is available (not yet written back)
            t_rt = getValueFromDictionary(rt, registerToClockCycle) # Clock cycle when value of rt is available (not yet written back)

            # Both registers have been written back and their values are same (Thus branching has to occur)
            if wb_rs is not None and wb_rs <= curr_clock_cycle and wb_rt is not None and wb_rt <= curr_clock_cycle and \
               registerToValue[rs] == registerToValue[rt] :
                return (True, [opcode, rs, rs_value, rt, rt_value, immediateVal])
            
            # WB is not yet done but register values are available from previous stages, for example EX
            elif t_rs is not None and t_rs < curr_clock_cycle and t_rt is not None and t_rt < curr_clock_cycle:
                
                # Need to forward rs
                if wb_rs is None or wb_rs > curr_clock_cycle:
                    forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rs]} from clock cycle {t_rs} to clock cycle {curr_clock_cycle}")
                
                # Need to forward rt
                if (wb_rt is not None or wb_rt > curr_clock_cycle) and rs != rt and rt != 9:
                    forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rt]} from clock cycle {t_rt} to clock cycle {curr_clock_cycle}") 

                # Values of rs and rt are same (Thus branching occurs)
                if executeValues[rs] == executeValues[rt]:
                    return (True, [opcode, rs, rs_value, rt, rt_value, immediateVal])
            
            # Need to stall as value of either rs or rt is not yet available
            elif t_rs is None or t_rs >= curr_clock_cycle or t_rt is None or t_rt >= curr_clock_cycle:
                return None

        return [opcode, rs, rs_value, rt, rt_value, immediateVal] # Return decoded instruction
    
    # Jump instruction
    elif opcode == "000010":

        immediateVal = binaryToDecimal("0000" + instruction[6: ] + "00") # Jump target address
 
        return [opcode, immediateVal] # Return decoded instruction

# Perform the necessary ALU operation 
def instructionExecute(decodedInstruction, registerToClockCycle, registerToWB, registerToValue, executeValues, ID_clock_cycle, curr_clock_cycle, instructionNumber, codeToRegister):

    opcode = decodedInstruction[0] # Opcode of instruction

    global forwardingMessages # To print forwarding messages

    # R-format instruction (ADD or MUL)
    if opcode == "000000" or opcode == "011100":

        rs = decodedInstruction[1] # Source register 1
        rt = decodedInstruction[3] # Source register 2

        wb_rs = getValueFromDictionary(rs, registerToWB) # Clock cycle at which WB of rs occurs
        wb_rt = getValueFromDictionary(rt, registerToWB) # Clock cycle at which WB of rt occurs

        t_rs = getValueFromDictionary(rs, registerToClockCycle) # Clock cycle at which value of rs is available (not yet written back)
        t_rt = getValueFromDictionary(rt, registerToClockCycle) # Clock cycle at which value of rt is available (not yet written back)

        # Add instruction (R - format)
        if opcode == "000000" and decodedInstruction[-1] == "100000":

            # Both registers have been written back and hence return their sum
            if wb_rs is not None and wb_rs <= ID_clock_cycle and wb_rt is not None and wb_rt <= ID_clock_cycle:
                return decodedInstruction[2] + decodedInstruction[4]

            # Atleast one register's value is not yet available
            if t_rs is None or t_rs >= curr_clock_cycle or t_rt is None or t_rt >= curr_clock_cycle:
                return None
            
            else:

                # Need to forward rs
                if wb_rs is None or wb_rs > curr_clock_cycle:
                    forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rs]} from clock cycle {t_rs} to clock cycle {curr_clock_cycle}")
                
                # Need to forward rt
                if rs != rt and (wb_rt is None or wb_rt > curr_clock_cycle):
                    forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rt]} from clock cycle {t_rt} to clock cycle {curr_clock_cycle}")

                return executeValues[rs] + executeValues[rt] # Return sum of rs and rt

        # Multiply instruction
        elif opcode == "011100":

            # Both registers have been written back and hence return their product
            if wb_rs is not None and wb_rs <= ID_clock_cycle and wb_rt is not None and wb_rt <= ID_clock_cycle:
                return decodedInstruction[2] * decodedInstruction[4]

            # Atleast one of the register's value is not yet available
            if t_rs is None or t_rs >= curr_clock_cycle or t_rt is None or t_rt >= curr_clock_cycle:
                return None
            
            else:

                # Need to forward rs
                if wb_rs is None or wb_rs > curr_clock_cycle:
                    forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rs]} from clock cycle {t_rs} to clock cycle {curr_clock_cycle}")

                # Need to forward rt
                if rs != rt and (wb_rt is None or wb_rt > curr_clock_cycle):
                    forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rt]} from clock cycle {t_rt} to clock cycle {curr_clock_cycle}")
                
                return executeValues[rs] * executeValues[rt] # Return product of rs and rt

    # Add immediate instruction
    elif opcode == "001000":

        rs = decodedInstruction[1] # Source register

        wb_rs = getValueFromDictionary(rs, registerToWB) # Clock cycle at which WB of rs will occur
        t_rs = getValueFromDictionary(rs, registerToClockCycle) # Clock cycle at which value of rs will be available (not yet written back)

        # Register has been written back and hence return rs + immediate value
        if wb_rs is not None and wb_rs <= ID_clock_cycle:
            return decodedInstruction[2] + decodedInstruction[-1]
        
        # Register value is not yet known
        if t_rs is None or t_rs >= curr_clock_cycle:
            return None
        
        else:

            # Need to forward rs
            forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rs]} from clock cycle {t_rs} to clock cycle {curr_clock_cycle}\n")

            return executeValues[rs] + decodedInstruction[-1] # Return rs + immediate value
        
    # Store word / Load word instruction
    elif opcode == "101011" or opcode == "100011":

        rs = decodedInstruction[1] # Source register

        # Value of rs is needed latest during MEM stage. So, it does not matter whether in EX stage we are reading
        # the correct value or not. Forwarding will occur in MEM stage, if needed.
        if registerToValue[rs] is None:
            registerToValue[rs] = 0

        return registerToValue[rs] + decodedInstruction[-1] # Return rs + immediate value
     
    # Jump instruction
    elif opcode == "000010":
    
        return decodedInstruction[-1] # Return jump target address

# Read from memory or write to a memory location in data memory
def memoryStage(PC, decodedInstruction, registerToClockCycle, registerToWB, executeValues, ID_clock_cycle, curr_clock_cycle, dataMemory, instructionNumber, codeToRegister):

    # Jump instruction does not require MEM stage
    if decodedInstruction[0] == "000010":
        return

    global forwardingMessages # To print forwarding messages

    opcode = decodedInstruction[0]        # Opcode of instruction
    rs = decodedInstruction[1]            # Source register 1
    rt = decodedInstruction[3]            # Source / Destination register depending upon instruction
    immediateVal = decodedInstruction[-1] # Immediate value

    wb_rs = getValueFromDictionary(rs, registerToWB) # Clock cycle at which WB of rs will occur
    wb_rt = getValueFromDictionary(rt, registerToWB) # Clock cycle at which WB of rt will occur

    t_rs = getValueFromDictionary(rs, registerToClockCycle) # Clock cycle at which value of rs will be available (not yet written back)
    t_rt = getValueFromDictionary(rt, registerToClockCycle) # Clock cycle at which value of rt will be available (not yet written back)

    # Store word instruction
    if opcode == "101011":

        # Register values have been written back and hence can be used without forwarding
        if wb_rs is not None and wb_rs <= ID_clock_cycle and wb_rt is not None and wb_rt <= ID_clock_cycle:

            memoryLocation = executeValues[PC]               # Memory location
            dataMemory[memoryLocation] = registerToValue[rt] # Write to memory location

        # Register values are not available and forwarding can also not be done
        elif t_rs is None or t_rs >= curr_clock_cycle or t_rt is None or t_rt >= curr_clock_cycle:
            return None
        
        else:

            # Need to forward rs
            if wb_rs > ID_clock_cycle:
                forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rs]} from clock cycle {t_rs} to clock cycle {curr_clock_cycle}")

            # Need to forward rt
            if wb_rt > ID_clock_cycle and rs != rt:
                forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rt]} from clock cycle {t_rt} to clock cycle {curr_clock_cycle}")

            memoryLocation = executeValues[rs] + immediateVal # Memory location
            dataMemory[memoryLocation] = executeValues[rt]    # Write to memory location

    # Load word instruction
    elif opcode == "100011":
        
        # Registers have been written back and hence no forwarding is required
        if wb_rs is not None and wb_rs <= ID_clock_cycle:

            memoryLocation = executeValues[PC] # Memory location
            return dataMemory[memoryLocation]  # Return value found at memory location

        # Register value is not available and forwarding can also not be done
        elif t_rs is None or t_rs >= curr_clock_cycle:
            return None
        
        else:

            # Need to forward rs
            if wb_rs > ID_clock_cycle:
                forwardingMessages[instructionNumber].append(f"Forward {codeToRegister[rs]} from clock cycle {t_rs} to clock cycle {curr_clock_cycle}")

            memoryLocation = executeValues[rs] + immediateVal # Memory location
            return dataMemory[memoryLocation]                 # Return value found at memory location

# Write back to required registers
def writeBack(decodedInstruction, executeValues, memoryValues, registerToValue):

    opcode = decodedInstruction[0] # Opcode of instruction

    # R-format instruction (ADD or MUL)
    if opcode == "000000" or opcode == "011100":
        
        rd = decodedInstruction[5]              # Destination register
        registerToValue[rd] = executeValues[rd] # Update value of rd
        
    # Add immediate instruction
    elif opcode == "001000":

        rt = decodedInstruction[3]              # Destination register
        registerToValue[rt] = executeValues[rt] # Update value of rt

    # Load word instruction
    elif opcode == "100011":

        rt = decodedInstruction[3]              # Destination register
        registerToValue[rt] = memoryValues[rt]  # Update value of rt

# Choose which program needs to be executed
print("1. Fibonacci Numbers")
print("2. Factorials of first 10 numbers")
choice = int(input("Enter appropriate number: "))

registerToValue = {0, 0} # To represent the contents of register file
dataMemory = {}          # To represent the contents of data memory
instructionMemory = {}   # To store the binary instructions

# To know the next stage that needs to be executed for an instruction 
nextStage = {"IF": "ID", "ID": "EX", "ME": "WB", "WB": None}

# Maps decimal number to the corresponding register
codeToRegister = {16: "$s0", 17: "$s1", 18: "$s2", 19: "$s3", 20: "$s4", 21: "$s5", 22: "$s6", 23: "$s7", 8: "$t0", 
                  9: "$t1", 10: "$t2", 11: "$t3", 12: "$t4", 13: "$t5", 14: "$t6", 15: "$t7"}

# Maps each register to its value (The values would be garbage at the beginning, hence taken to be None)
registerToValue = {0: 0, 16: None, 17: None, 18: None, 19: None, 20: None, 21: None, 22: None, 23: None, 8: None, 
                   9: None, 10: None, 11: None, 12: None, 13: None, 14: None, 15: None}

# Maps each register to the clock cycle at which its value will be available.
# Note: Register is represented in its decimal form
registerToClockCycle = {0: 0}

# Maps each register to the clock cycle at which its value will be written back
# Note: Register is represented in its decimal form
registerToWB = {0: 0}

# Total number of clock cycles that program takes to execute
totalClockCycles = 0

# Maps PC to the corresponding instruction (used during pipelining and almost same as instructionMemory)
instructions = {}

# Maps PC to the corresponding decoded instruction
decodedInstructions = {}

# Maps PC to the corresponding value calculated during EX stage
executeValues = {}

# Maps PC to the corresponding values read from the data memory during ME stage
memoryValues = {}

# Maps PC to the clock cycle when the ID stage for that instruction occurred
ID_clock_cycle = {}

pipelineDiagram = {}    # Maps instruction number to the corresponding pipeline diagram
forwardingMessages = {} # Maps instruction number to the forwarding messages, if any

pcToInstructionNumber = {} # Maps PC to the instruction number

# Fibonacci program
if choice == 1:
    
    binary_code = open("fibonacci_binary.txt", "r") # Binary code of fibonacci

    # $t1 contains the number of fibonacci nummbers to be calculated
    registerToValue[9] = int(input("No. of fibonacci numbers to be calculated: "))
    
    # $t1 and $t2 are available at the beginning
    registerToClockCycle[9] = 0
    registerToClockCycle[10] = 0

    registerToWB[9] = 0  # $t1 is written back in the beginning
    registerToWB[10] = 0 # $t2 is written back in the beginning

    # $t10 stores the address from where the numbers have to be stored
    registerToValue[10] = int(input("Enter starting address of numbers (in decimal format): "))
  
    executeValues[9] = registerToValue[9]   # Value of $t9
    executeValues[10] = registerToValue[10] # Value of $t10

    PC = 4194328 # Initial PC

    # Map PC to the corresponding instruction
    for instruction in binary_code:
        instructionMemory[PC] = instruction
        PC += 4

    PC_end = PC - 4 # PC of last instruction

    PC = 4194328

# Factorial program
elif choice == 2:
    
    # $t3 is the memory location from where factorials have to be written
    registerToValue[11] = int(input("Enter starting address of factorials (in decimal format): "))
    
    # $t3 is available at the beginning
    registerToClockCycle[11] = 0
    registerToWB[11] = 0
    executeValues[11] = registerToValue[11]

    binary_code = open("factorial_binary.txt", "r") # Binary code of factorial
    
    PC = 4194304 # Initial PC

    # Map PC to the corresponding instruction
    for instruction in binary_code:
        instructionMemory[PC] = instruction
        PC += 4

    PC_end = PC - 4 # PC of last instruction
    PC = 4194304

instructionNumber = 1   # Keep track of how many instructions have been executed till now
pipelineDiagram[1] = [] # To print pipeline diagram

# The stage that has to be executed for a particular instruction
stageToExecute = {PC : "IF"}

pcToInstructionNumber[PC] = instructionNumber # Map PC to instruction number
forwardingMessages[instructionNumber] = []    # Assume no forwarding message 

# While there is some stage to be executed for an instruction
while len(stageToExecute) > 0:

    totalClockCycles += 1 # Increment clock cycle
    IF_executed = False   # Whether IF is executed in this clock cycle
    ID_executed = False   # Whether ID is executed in this clock cycle
    EX_executed = False   # Whether EX is executed in this clock cycle
    ME_executed = False   # Whether ME is executed in this clock cycle
    WB_executed = False   # Whether WB is executed in this clock cycle

    jump_target = None # Jump target address

    # Execute the required stage for each instruction
    for pc in stageToExecute:

        # IF stage
        if pc in stageToExecute and stageToExecute[pc] == "IF":
            
            # If IF is executed, it cannot be executed again (structural hazard) 
            if IF_executed:
                continue

            instructions[pc] = instructionFetch(pc, instructionMemory) # Fetch instruction
            stageToExecute[pc] = "ID" # Next stage to be executed
            IF_executed = True # IF has been executed

            curr_length = len(pipelineDiagram[pcToInstructionNumber[pc]]) # Current length of pipeline diagram

            # Put appropriate spaces and IF at current clock cycle
            pipelineDiagram[pcToInstructionNumber[pc]].extend("   " for _ in range(totalClockCycles - curr_length - 1))
            pipelineDiagram[pcToInstructionNumber[pc]].append("IF ")

        # ID stage
        elif pc in stageToExecute and stageToExecute[pc] == "ID":
            
            # If ID is executed, it cannot be executed again (structural hazard) 
            if ID_executed:
                IF_executed = True
                continue

            # Decode instruction (can be None in case of BEQ if stall is required)
            res = decodedInstructions[pc] = instructionDecode(instructions[pc], registerToValue, registerToClockCycle, registerToWB, executeValues, totalClockCycles, pcToInstructionNumber[pc], codeToRegister)

            if res is not None:
                
                stageToExecute[pc] = "EX" # Next stage to be executed
                ID_clock_cycle[pc] = totalClockCycles # Keep track of when the ID stage occurred

                # In case branch needs to be taken (BEQ)
                if res[0] == True:

                    PC += 4 * decodedInstructions[pc][-1][-1] # Update PC

                    # Flush instructions
                    stageToExecute = {key: val for key, val in stageToExecute.items() if (key >= PC + 4 or key <= pc)}

                    # Convert from tuple to list
                    decodedInstructions[pc] = decodedInstructions[pc][1]

            # Forwarding required in BEQ
            else:

                pipelineDiagram[pcToInstructionNumber[pc]].append("__ ") # Put stall 
                IF_executed = True # IF is executed due to stall

                continue

            ID_executed = True # ID is executed

            curr_length = len(pipelineDiagram[pcToInstructionNumber[pc]]) # Current length of pipeline diagram

            # Put appropriate spaces and ID at the current clock cycle
            pipelineDiagram[pcToInstructionNumber[pc]].extend("   " for _ in range(totalClockCycles - curr_length - 1))
            pipelineDiagram[pcToInstructionNumber[pc]].append("ID ")

        # EX stage
        elif pc in stageToExecute and stageToExecute[pc] == "EX":
            
            # If EX is executed, it cannot be executed again (structural hazard) 
            if EX_executed:
                ID_executed = True
                continue

            # Execute current instruction (Can be none if stall is required)
            res = instructionExecute(decodedInstructions[pc], registerToClockCycle, registerToWB, registerToValue, executeValues, ID_clock_cycle[pc], totalClockCycles, pcToInstructionNumber[pc], codeToRegister)
            
            if res is not None:

                stageToExecute[pc] = "ME" # Next stage to be executed
                
                # Add instruction / Multiply instruction
                if decodedInstructions[pc][0] == "000000" or decodedInstructions[pc][0] == "011100":
                    
                    rd = decodedInstructions[pc][-2]            # Destination register
                    executeValues[rd] = res                     # Value of rd is know after EX stage
                    registerToClockCycle[rd] = totalClockCycles # Clock cycle at which value of rd is available

                # Add immediate instruction
                elif decodedInstructions[pc][0] == "001000":

                    rt = decodedInstructions[pc][3]             # Destination register 
                    executeValues[rt] = res                     # Value of rt is known after EX stage
                    registerToClockCycle[rt] = totalClockCycles # Clock cycle at which value of rt is available

                # Store word / Load word instruction
                elif decodedInstructions[pc][0] == "101011" or decodedInstructions[pc][0] == "100011":

                    executeValues[pc] = res # The value is not stored in any register so we use PC instead

                # Jump instruction
                elif decodedInstructions[pc][0] == "000010":

                    # Flush instructions
                    stageToExecute = {key: val for key, val in stageToExecute.items() if not (key > pc and key <= res)}
                    jump_target = res # Jump target address

            # BEQ / Jump instruction
            # For these instructions, EX stage will return None. But, these instructions can proceed to next stage.
            elif decodedInstructions[pc][0] == "000100" or decodedInstructions[pc][0] == "000010":

                stageToExecute[pc] = "ME" # Next stage to be executed

            EX_executed = True # EX is executed

            curr_length = len(pipelineDiagram[pcToInstructionNumber[pc]]) # Current length of pipeline diagram

            # Put appropriate number of spaces and EX at the current clock cycle
            pipelineDiagram[pcToInstructionNumber[pc]].extend("__ " for _ in range(totalClockCycles - curr_length - 1))
            pipelineDiagram[pcToInstructionNumber[pc]].append("EX ")

        # ME stage
        elif pc in stageToExecute and stageToExecute[pc] == "ME":
            
            # If ME is executed, it cannot be executed again (structural hazard) 
            if ME_executed:
                EX_executed = True
                continue

            # Memory stage is executed
            res = memoryStage(pc, decodedInstructions[pc], registerToClockCycle, registerToWB, executeValues, ID_clock_cycle[pc], totalClockCycles, dataMemory, pcToInstructionNumber[pc], codeToRegister)

            # Load word instruction
            if decodedInstructions[pc][0] == "100011":

                rt = decodedInstructions[pc][3]             # Destination register
                registerToClockCycle[rt] = totalClockCycles # Clock cycle at which value of rt is known 
                memoryValues[rt] = res                      # To store value of rt 
                executeValues[rt] = res                     # To store value of rt

            stageToExecute[pc] = "WB" # Next stage to be executed
            ME_executed = True # ME is executed

            curr_length = len(pipelineDiagram[pcToInstructionNumber[pc]]) # Current length of pipeline diagram

            # Put appropriate number of spaces and ME at the current clock cycle
            pipelineDiagram[pcToInstructionNumber[pc]].extend("   " for _ in range(totalClockCycles - curr_length - 1))
            pipelineDiagram[pcToInstructionNumber[pc]].append("ME ")

        # WB stage
        elif pc in stageToExecute and stageToExecute[pc] == "WB":

            # If WB is executed, it cannot be executed again (structural hazard) 
            if WB_executed:
                ME_executed = True
                continue

            # Write back to register, if required
            writeBack(decodedInstructions[pc], executeValues, memoryValues, registerToValue)
            stageToExecute[pc] = None # Instruction has been executed completely

            # Add / Multiply instruction
            if decodedInstructions[pc][0] == "000000" or decodedInstructions[pc][0] == "011100":

                rd = decodedInstructions[pc][-2]    # Destination register
                registerToWB[rd] = totalClockCycles # Clock cycle at which WB of rd has occurred

            # Add immediate / Load word instruction
            elif decodedInstructions[pc][0] == "001000" or decodedInstructions[pc][0] == "100011":

                rt = decodedInstructions[pc][3]     # Destination register
                registerToWB[rt] = totalClockCycles # Clock cycle at which WB of rt has occurred

            WB_executed = True # WB has been executed

            curr_length = len(pipelineDiagram[pcToInstructionNumber[pc]]) # Current length of pipeline diagram

            # Put appropriate number of spaces and WB at current clock cycle
            pipelineDiagram[pcToInstructionNumber[pc]].extend("__ " for _ in range(totalClockCycles - curr_length - 1))
            pipelineDiagram[pcToInstructionNumber[pc]].append("WB ")

    # For next instruction
    PC += 4
    instructionNumber += 1

    forwardingMessages[instructionNumber] = [] # Assume no forwarding messages for next instruction

    # Jump to JTA if jump instruction is encountered
    if jump_target is not None:
        PC = jump_target

    pcToInstructionNumber[PC] = instructionNumber # Map PC to instruction number

    # IF stage needs to be executed for next instruction (if there is a next instruction)
    if PC <= PC_end:
        stageToExecute[PC] = "IF"
        pipelineDiagram[instructionNumber] = []

    # Remove completed instruction from dictionary
    stageToExecute = {key: val for key, val in stageToExecute.items() if stageToExecute[key] != None}

binary_code.close() # Close the binary file after reading

print("\nRegister Values: ")

# Print register values at end of program
for key in codeToRegister:

    if key in registerToValue and registerToValue[key] is not None:
        print(f"{codeToRegister[key]}: {registerToValue[key]}")

    else:
        print(f"{codeToRegister[key]}: Garbage value")

print("\nData Memory: ")

# Print values stored in data memory
for address in dataMemory:
    print(f"{address}: {dataMemory[address]}")

# Print total clock cycles taken to execute the program
print(f"\nTotal Clock Cycles: {totalClockCycles}\n")  

print("    ", end = "")

for i in range(1, totalClockCycles + 1):
    print(f"{i: 3d}", end = "")

print()

count = 1

# Print pipeline diagram
for instructionNum in pipelineDiagram:

    print(f"{count: 3d}. ", end = "")
    count += 1

    # Last instruction is flushed due to BEQ
    if pipelineDiagram[instructionNum] == []:
        print("Flushed due to BEQ")
        break

    # Print pipeline stages
    for str in pipelineDiagram[instructionNum]:
        print(str, end = "")

    print()

    # Print forwarding messages for this instruction
    for message in forwardingMessages[instructionNum]:
        print(message)

    print()