class CPU:
    def __init__(self, memory_size=256, reg_count=16):
        self.PC = 0    
        self.cmd_reg = None 
        self.RF = [0] * reg_count 
        self.mem = [0] * memory_size
        self.cmd_mem = []  
        self.RF[0] = 0  
        self.RF[1] = 1  

        # Промежуточные операнды
        self.operand1 = 0
        self.operand2 = 0
        self.operand3 = 0
        self.result = 0
        self.jump_condition = False  
        self.instruction_set = {
            "0000": "NOP",
            "0001": "LTM",
            "0010": "MTR",
            "0011": "RTR",
            "0100": "JL",
            "0101": "SBT",
            "0110": "SUMM",
            "0111": "MTRD",
            "1000": "RTM",
            "1001": "JUMP",
        }

        self.executors = {
            "NOP": self.execute_nop,
            "LTM": self.execute_ltm,
            "MTR": self.execute_mtr,
            "RTR": self.execute_rtr,
            "JL": self.execute_jl,
            "SBT": self.execute_sbt,
            "SUMM": self.execute_summ,
            "MTRD": self.execute_mtrd,
            "RTM": self.execute_rtm,
            "JUMP": self.execute_jump,
        }


    def fetch(self):
        if self.PC < len(self.cmd_mem):
            self.cmd_reg = self.cmd_mem[self.PC]
        else:
            self.cmd_reg = None

    def decode1(self):
        if not self.cmd_reg:
            return
        opcode = self.cmd_reg[0]

        if opcode in ["LTM", "MTR", "RTR", "MTRD"]:
            self.operand1 = self.cmd_reg[1]
        
        elif opcode == "RTM":
            self.operand1 = self.RF[self.cmd_reg[2]]
        elif opcode in ["JL", "SBT", "SUMM"]:
            self.operand1 = self.cmd_reg[1] 
        elif opcode == "JUMP":
            self.operand1 = self.cmd_reg[1] 

    def decode2(self):
        if not self.cmd_reg:
            return
        opcode = self.cmd_reg[0]

        if opcode == "LTM":
            self.operand2 = self.cmd_reg[2]
        elif opcode in ["MTR", "RTR", "MTRD"]:
            self.operand2 = self.cmd_reg[2]
        elif opcode == "RTM":
            self.operand2 = self.cmd_reg[1]
        elif opcode in ["JL", "SBT", "SUMM"]:
            self.operand2 = self.cmd_reg[2]
            if len(self.cmd_reg) > 3:
                self.operand3 = self.cmd_reg[3]

    def execute(self):
        if not self.cmd_reg:
            return
        opcode = self.cmd_reg[0]
        if opcode in self.executors:
            self.executors[opcode]()

    def writeback(self):
        if not self.cmd_reg:
            return
        opcode = self.cmd_reg[0]

        if opcode == "JUMP" and self.jump_condition:
            self.PC = self.operand1
        elif opcode == "JL":
            if self.jump_condition:
                self.PC += 1
            else:
                self.PC = self.operand3
        else:
            self.PC += 1

        self.jump_condition = False 

    def execute_nop(self):
        self.result = 0

    def execute_ltm(self):
        self.mem[self.operand1] = self.operand2
        self.result = self.operand2

    def execute_mtr(self):
        self.RF[self.operand1] = self.mem[self.operand2]
        self.result = self.RF[self.operand1]

    def execute_rtr(self):
        self.RF[self.operand1] = self.RF[self.operand2]
        self.result = self.RF[self.operand1]

    def execute_jl(self):
        a = self.RF[self.operand1]
        b = self.RF[self.operand2]
        self.jump_condition = (a < b)

    def execute_sbt(self):
        a = self.RF[self.operand1]
        b = self.RF[self.operand2]
        self.RF[self.operand3] = a - b
        self.result = self.RF[self.operand3]

    def execute_summ(self):
        a = self.RF[self.operand1]
        b = self.RF[self.operand2]
        self.RF[self.operand3] = a + b
        self.result = self.RF[self.operand3]

    def execute_mtrd(self):
        mem_addr = self.RF[self.operand1]
        self.RF[self.operand2] = self.mem[mem_addr]
        self.result = self.RF[self.operand2]

    def execute_rtm(self):
        self.mem[self.operand1] = self.RF[self.operand2]
        self.result = self.RF[self.operand2]

    def execute_jump(self):
        self.jump_condition = True

    def run_instruction(self):

        self.fetch()
        self.decode1()
        self.decode2()
        self.execute()
        self.writeback()

        return self.PC < len(self.cmd_mem)

    def load_program(self, program):
        self.cmd_mem = program
        self.PC = 0

    def print_state(self):
        print(f"PC = {self.PC}")
        print(f"RF = {self.RF[:10]}")
        print(f"Memory = {self.mem[:10]}")


cpu = CPU()

program = [

    # === данные ===
    ["LTM", 0, 3],     # mem[0] = 3
    ["LTM", 1, -1],    # mem[1] = -1
    ["LTM", 2, 2],     # mem[2] = 2
    ["LTM", 3, 3],     # mem[3] = n = 3

    # ===== init =====
    ["RTR", 2, 0],     # RF2 = i = 0
    ["MTR", 3, 3],     # RF3 = n
    ["SUMM", 3, 1, 5], # RF5 = j = n + 1

    ["JL", 2, 3, 22],  

    ["MTRD", 2, 4],

    ["RTM", 4, 5],
    ["SUMM", 5, 1, 5], 

    # if A[i] < 0 ?
    ["JL", 4, 0, 14], 

    # mem[j] = 0
    ["RTM", 0, 5],
    ["SUMM", 5, 1, 5], 

    # === skip_zero ===
    ["SUMM", 2, 1, 2], 
    ["JUMP", 7],

    # ===== EXIT =====
    ["NOP"]
]

cpu.load_program(program)

print("НАЧАЛЬНОЕ СОСТОЯНИЕ:")
cpu.print_state()

max_instructions = 200  
instructions_executed = 0

while cpu.PC < len(cpu.cmd_mem) and instructions_executed < max_instructions:
    cpu.run_instruction()
    instructions_executed += 1

    if instructions_executed >= max_instructions:
        print("\nПРЕРВАНО: достигнут лимит выполненных команд")
        break

print("\nФИНАЛЬНОЕ СОСТОЯНИЕ:")
cpu.print_state()
print(f"Всего выполнено команд: {instructions_executed}")
