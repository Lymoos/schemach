class CPU:
    def __init__(self, memory_size=256, reg_count=16):
        # Регистры процессора
        self.PC = 0  # Program Counter - счетчик команд
        self.cmd_reg = None  # Регистр команды
        self.RF = [0] * reg_count  # RegFile - регистровый файл
        self.mem = [0] * memory_size  # Memory - оперативная память
        self.cmd_mem = []  # Память команд

        #                 OpA   OpB    OpPip resH  resL  Res
        self.curr_value = [None, None, None, None, None, None]
        self.curr_value_before = [None, None, None, None, None, None]
        self.before_using = [None, ["", None], ["", None], [""], ["", None, None]]
        self.before_res = [None, None, None]
        # Инициализация RF как указано
        self.RF[0] = 0
        self.RF[1] = 1

        self.buffer = [None, None, None, None, None]
        self.operand1 = 0
        self.operand2 = 0
        self.pipeline_operand = 0
        self.result = 0
        self.resH = 0
        self.resL = 0

        self.result_before = 0
        self.resH_before = 0
        self.resL_before = 0


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
            "1001": "JUMP"
        }

        # Обработчики команд
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
            "JUMP": self.execute_jump
        }

        self.executors_before = {
            "NOP": self.execute_nop,
            "LTM": self.execute_ltm_before,
            "MTR": self.execute_mtr_before,
            "RTR": self.execute_rtr_before,
            "JL": self.execute_jl_before,
            "SBT": self.execute_sbt_before,
            "SUMM": self.execute_summ_before,
            "MTRD": self.execute_mtrd_before,
            "RTM": self.execute_rtm_before,
            "JUMP": self.execute_jump
        }

    def fetch(self):
        """1 такт: выборка команды"""
        if self.PC < len(self.cmd_mem):
            self.cmd_reg = self.cmd_mem[self.PC]
            self.buffer[4] = self.buffer[3]
            self.buffer[3] = self.buffer[2]
            self.buffer[2] = self.buffer[1]
            self.buffer[1] = self.buffer[0]
            self.buffer[0] = self.cmd_reg
            print(f"FETCH: PC={self.PC}, Загружена команда {self.cmd_reg}")
        else:
            self.cmd_reg = None
            print("FETCH: Нет команд для выполнения")

    def decode1_before(self):
        """2 такт: выборка первого операнда"""

        self.curr_value_before[0] = self.operand1
        self.curr_value_before[2] = self.pipeline_operand

        if self.buffer[1]:
            opcode = self.buffer[1][0]
            self.before_using[1][0] = opcode
            if self.before_using[1][0] == "MTR":
                self.before_using[1][1] = self.buffer[1][1]
            elif self.before_using[1][0] == "LTM":
                self.before_using[1][1] = self.buffer[1][1]
            elif self.before_using[1][0] in ["RTR", "RTM"]:
                self.before_using[1][1] = self.buffer[1][1]
            elif self.before_using[1][0] in ["JL", "SUB", "SUM", "MTRK", "SBT", "SUMM", "MTRD"]:
                self.before_using[1][1] = self.buffer[1][1]
            elif self.before_using[1][0] in ["JMP", "JUMP"]:
                # self.operand1 = self.buffer[1][1]
                ...
            elif self.before_using[1][0] in ["NOP"]:
                self.before_using[1][1] = -1

    def decode2_before(self):
        """3 такт: выборка второго операнда"""

        self.curr_value_before[1] = self.operand2

        if self.buffer[2]:
            opcode = self.buffer[2][0]
            self.before_using[2][0] = opcode
            if opcode in ["LTM"]:
                self.before_using[2][1] = self.buffer[2][2]  # Literal value
            elif opcode in ["MTRK", "MTRD"]:
                self.before_using[2][1] = self.mem[self.operand1]
            elif opcode in ["JL", "SUB", "SUM", "SUMM", "SBT"]:
                self.before_using[2][1] = self.buffer[2][2]
            elif opcode == "RTM":
                self.before_using[2][1] = self.buffer[2][1]
            elif opcode == "NOP":
                self.before_using[2][1] = -1

    def execute_before(self):
        """4 такт: исполнение команды"""
        self.before_res[0] = self.resH_before
        self.before_res[1] = self.resL_before
        self.before_res[2] = self.result_before
        if self.buffer[3]:
            opcode = self.buffer[3][0]
            self.before_using[3][0] = opcode
            if opcode in self.executors:
                self.executors_before[opcode]()
                print(f"EXECUTE_BEFORE: Выполнена операция {opcode}")

    def execute_ltm_before(self):
        self.resH_before = self.curr_value_before[2]  # self.pipeline_operand
        self.resL_before = self.curr_value_before[1]  # self.operand2

    def execute_mtr_before(self):
        self.result_before = self.curr_value_before[1]  # self.pipeline_operand

    def execute_rtr_before(self):
        self.result_before = self.curr_value_before[0]  # self.pipeline_operand

    def execute_jl_before(self):
        self.result_before = (self.curr_value_before[0] < self.curr_value_before[1])
        print(
            f"JL: RF[{self.curr_value_before[2]}]={self.curr_value_before[0]} < RF[{self.curr_value_before[1]}]={self.curr_value_before[1]} -> {self.result}")

    def execute_sbt_before(self):
        self.result_before = (self.curr_value[0] - self.curr_value_before[1])

    def execute_summ_before(self):
        self.result_before = (self.curr_value_before[2] + self.curr_value[1])

    def execute_mtrd_before(self):
        self.result_before = self.curr_value_before[1]

    def execute_rtm_before(self):
        self.resH_before = self.curr_value_before[0]  # self.pipeline_operand
        self.resL_before = self.curr_value_before[1]  # self.operand2

    #3 - H  - 0
    #4 - L  - 1
    #5 - result  - 2
    def writeback_before(self):
        """5 такт: запись результата"""
        if self.buffer[4]:
            opcode = self.buffer[4][0]
            self.before_using[4][0] = opcode
            # Обновление PC
            if opcode == "JUMP":
                self.before_using[4][1] = self.buffer[4][1]
                self.before_using[4][2] = -1
            elif opcode == "JL":
                if self.curr_value[5]:  # self.result:
                    # Если условие истинно (A < B), увеличиваем PC на 1
                    ...
                else:
                    # Если условие ложно (A >= B), переходим по адресу
                    self.before_using[4][1] = self.before_res[0]
                    self.before_using[4][2] = -1
            elif opcode == "LTM":
                self.before_using[4][1] = self.buffer[4][1]
                self.before_using[4][2] = self.buffer[4][2]
            elif opcode == "MTR":
                self.before_using[4][1] = self.buffer[4][2]
                self.before_using[4][2] = self.before_res[2]
            elif opcode == "RTR":
                self.before_using[4][1] = self.buffer[4][1]
                self.before_using[4][2] = self.before_res[2]
            elif opcode == "SBT":
                self.before_using[4][1] = self.buffer[4][3]
                self.before_using[4][2] = self.before_res[2]
            elif opcode == "SUMM":
                self.before_using[4][1] = self.buffer[4][3]
                self.before_using[4][2] = self.before_res[2]
            elif opcode == "MTRD":
                self.before_using[4][1] = self.buffer[4][2]
                self.before_using[4][2] = self.before_res[2]
            elif opcode == "RTM":
                self.before_using[4][1] = self.before_res[0]
                self.before_using[4][2] = self.before_res[1]
            elif opcode == "NOP":
                self.before_using[4][1] = -1
                self.before_using[4][2] = -1

    def decode1(self):
        self.curr_value[0] = self.operand1
        self.curr_value[2] = self.pipeline_operand
        """2 такт: выборка первого операнда"""
        if self.buffer[1]:
            opcode = self.buffer[1][0]
            if opcode == "MTR":
                if(self.before_using[1][1] != self.before_using[4][1] or self.before_using[4][0] in ["RTR", "MTR", "JL", "SUB", "SUM", "MTRK", "SBT", "SUMM", "MTRD", "JMP", "JUMP"]):
                    self.pipeline_operand = self.operand1
                    print(f"DECODE1: Операнд1 = {self.pipeline_operand}")
                else:
                    self.pipeline_operand = self.before_using[4][2]
                    print(f"DECODE1: Операнд1 = {self.pipeline_operand}")
            elif opcode == "LTM":
                self.pipeline_operand = self.operand1
                self.operand1 = self.buffer[1][1]
                print(f"DECODE1: Операнд1 = {self.operand1}")
            elif opcode in ["RTR", "RTM"]:
                if(self.before_using[1][1] != self.before_using[4][1] or self.before_using[4][0] in ["LTM","RTM"]):
                    self.pipeline_operand = self.operand1
                    self.operand1 = self.RF[self.buffer[1][2]]
                    print(f"DECODE1: Операнд1 = {self.operand1}")
                else:
                    self.pipeline_operand = self.before_using[4][2]
                    self.operand1 = self.before_using[4][2]
                    print(f"DECODE1: Операнд1 = {self.operand1}")
            elif opcode in ["JL", "SUB", "SUM", "MTRK", "SBT", "SUMM", "MTRD"]:
                if(self.before_using[1][1] != self.before_using[4][1]):
                    self.pipeline_operand = self.operand1
                    self.operand1 = self.RF[self.buffer[1][1]]
                    print(f"DECODE1: Адрес операнда1 RF[{self.operand1}]")
                else:
                    self.pipeline_operand = self.before_using[4][2]
                    self.operand1 = self.before_using[4][2]
                    print(f"DECODE1: Адрес операнда1 RF[{self.operand1}]")
            elif opcode in ["JMP", "JUMP"]:
                self.pipeline_operand = self.operand1
                # self.operand1 = self.buffer[1][1]
                print(f"DECODE1: Адрес перехода = {self.operand1}")

    def decode2(self):
        """3 такт: выборка второго операнда"""
        self.curr_value[1] = self.operand2
        if self.buffer[2]:
            opcode = self.buffer[2][0]
            if opcode in ["LTM"]:
                self.operand2 = self.buffer[2][2]  # Literal value
                print(f"DECODE2: Literal = {self.operand2}")
            elif opcode in ["MTRK", "MTRD"]:
                self.operand2 = self.mem[self.operand1]
                print(f"DECODE2: Операнд2 = {self.operand2}")
            elif opcode in ["JL", "SUB", "SUM", "SUMM", "SBT"]:
                if(self.before_using[2][1] != self.before_using[4][1]):
                    self.operand2 = self.RF[self.buffer[2][2]]
                    print(f"DECODE2: Адрес операнда2 RF[{self.operand2}]")
                else:
                    self.operand2 = self.before_using[4][2]
                    print(f"DECODE2: Адрес операнда2 RF[{self.operand2}]")
            elif opcode == "RTM":
                if(self.before_using[2][1] != self.before_using[4][1]):
                    self.operand2 = self.RF[self.buffer[2][1]]
                    print(f"DECODE2: Адрес операнда2 RF[{self.operand2}]")
                else:
                    self.operand2 = self.before_using[4][2]
                    print(f"DECODE2: Адрес операнда2 RF[{self.operand2}]")

            # Для команд с тремя операндами
            # if opcode in ["JL", "SUB", "SUM"] and len(self.buffer[2]) > 3:
            #     self.operand3 = self.buffer[2][3]
            #     print(f"DECODE2: Операнд3 = {self.operand3}")

    def execute(self):
        """4 такт: исполнение команды"""
        self.curr_value[3] = self.resH
        self.curr_value[4] = self.resL
        self.curr_value[5] = self.result
        if self.buffer[3]:
            opcode = self.buffer[3][0]
            if opcode in self.executors:
                self.executors[opcode]()
                print(f"EXECUTE: Выполнена операция {opcode}")

    def writeback(self):
        """5 такт: запись результата"""
        if self.buffer[4]:
            opcode = self.buffer[4][0]
            # Обновление PC
            if opcode == "JUMP":
                self.PC = self.buffer[4][1]
                print(f"WRITEBACK: Безусловный переход на PC={self.PC}")
            elif opcode == "JL":
                if self.curr_value[5]:  # self.result:
                    # Если условие истинно (A < B), увеличиваем PC на 1
                    self.PC += 1
                    print(f"WRITEBACK: PC увеличен до {self.PC} (A < B)")
                else:
                    # Если условие ложно (A >= B), переходим по адресу
                    self.PC = self.buffer[4][3]
                    print(f"WRITEBACK: Условный переход на PC={self.PC} (A >= B)")
            elif opcode == "LTM":
                self.mem[self.curr_value[3]] = self.curr_value[4]
            elif opcode == "MTR":
                self.RF[self.buffer[4][2]] = self.curr_value[5]
            elif opcode == "RTR":
                self.RF[self.buffer[4][1]] = self.curr_value[5]
            elif opcode == "SBT":
                self.RF[self.buffer[4][3]] = self.curr_value[5]
            elif opcode == "SUMM":
                self.RF[self.buffer[4][3]] = self.curr_value[5]
            elif opcode == "MTRD":
                self.RF[self.buffer[4][2]] = self.curr_value[5]
            elif opcode == "RTM":
                self.mem[self.curr_value[3]] = self.curr_value[4]

            # else:
            #     self.PC += 1
            #     print(f"WRITEBACK: PC увеличен до {self.PC}")

            # Сброс условия перехода

            if opcode != "JUMP" and opcode != "JL":
                self.PC += 1
                print(f"WRITEBACK: PC увеличен до {self.PC}")
        else:
            self.PC += 1

    # Реализации команд
    def execute_nop(self):
        pass

    def execute_jump(self):
        pass

    def execute_ltm(self):
        self.resH = self.curr_value[2]  # self.pipeline_operand
        self.resL = self.curr_value[1]  # self.operand2

    def execute_mtr(self):
        self.result = self.curr_value[1]  # self.pipeline_operand

    def execute_rtr(self):
        self.result = self.curr_value[0]  # self.pipeline_operand

    def execute_jl(self):
        self.result = (self.curr_value[0] < self.curr_value[1])
        print(
            f"JL: RF[{self.curr_value[2]}]={self.curr_value[0]} < RF[{self.curr_value[1]}]={self.curr_value[1]} -> {self.result}")

    def execute_sbt(self):
        self.result = (self.curr_value[0] - self.curr_value[1])

    def execute_summ(self):
        self.result = (self.curr_value[2] + self.curr_value[1])

    def execute_mtrd(self):
        self.result = self.curr_value[1]

    def execute_rtm(self):
        self.resH = self.curr_value[0]  # self.pipeline_operand
        self.resL = self.curr_value[1]  # self.operand2

    def run_instruction(self):
        print("\n" + "=" * 60)
        print(f"Начало выполнения команд (PC={self.buffer})")
        print("=" * 60)

        self.fetch()  # Такт 1

        self.decode1_before()
        self.decode2_before()
        self.execute_before()
        self.writeback_before()

        self.decode1()  # Такт 2
        self.decode2()  # Такт 3
        self.execute()  # Такт 4
        self.writeback()  # Такт 5
        # self.execute()
        # self.decode2()
        # self.decode1()
        # self.fetch()

        print("=" * 60)
        print(f"Начало выполнения команд (PC={self.buffer})")
        print("=" * 60)

        return self.PC < len(self.cmd_mem)

    def load_program(self, program):
        self.cmd_mem = program
        self.PC = 0

    def print_state(self):
        print("\nТекущее состояние процессора:")
        print(f"PC = {self.PC}")
        print(f"OpA: {self.operand1}")
        print(f"OpB: {self.operand2}")
        print(f"Op pipeline {self.pipeline_operand}")
        print(f"Result: {self.result}")
        print(f"Result H: {self.resH}")
        print(f"Result L: {self.resL}")
        print(f"before_res_H: {self.before_res[0]}")
        print(f"before_res_L: {self.before_res[1]}")
        print(f"before_res: {self.before_res[2]}")
        print(f"result_before: {self.result_before}")
        print(f"Buffer: {self.buffer}")
        print(f"before_using: {self.before_using}")
        print(f"curr_val: {self.curr_value}")
        print(f"RF = {self.RF[:10]}")
        print(f"mem[0:10] = {self.mem[:10]}")
        if self.PC < len(self.cmd_mem):
            print(f"Следующая команда: {self.cmd_mem[self.PC]}")
        else:
            print("Следующая команда: КОНЕЦ ПРОГРАММЫ")


# Создаем процессор
cpu = CPU()

# Загружаем тестовую программу
program = [
    ["LTM", 0, 5],  # 1: mem[0] = 5
    ["LTM", 1, 7],  # 2: mem[1] = 7
    ["LTM", 2, 3],  # 3: mem[2] = 3
    ["LTM", 3, 3],  # 4: mem[3] = 3
    ["RTR", 2, 1],  # 5: RF[2] = RF[0]
    #по идеи должен быть nop
    ["MTR", 3, 3],  # 6: RF[3] = mem[RF[3]]
    ["NOP"], #ОПРАВДАН
    ["JL", 2, 3, 40],  # 8 if ~(RF[2] < RF[3]) jump to 26
    ["NOP"],  #ОПРАВДАН
    ["RTR", 4, 0],  # 10: RF[4] = RF[0]
    ["NOP"],   #11
    ["SBT", 3, 2, 5],  # 12: RF[5] = RF[3] - RF[2]
    ["NOP"],  # 13
    ["NOP"],  # 14: NOP
    ["JL", 4, 5, 37],  # 15: if ~(RF[4] < RF[5]) jump to 18
    ["SUMM", 4, 1, 6],  # 16: RF[6] = RF[4] + RF[1]
    ["NOP"],  # 17
    ["MTRD", 4, 7],  # 18: RF[4] = mem[RF[7]]
    ["NOP"],  # 19 
    ["MTRD", 6, 8],  # 20: RF[6] = mem[RF[8]]
    ["NOP"],  # 21: NOP
    ["NOP"],  # 22: NOP
    ["NOP"],  # 23
    ["JL", 8, 7, 31],  # 24: if ~(RF[7] < RF[8]) jump to 16
    ["NOP"],  # 25
    ["NOP"],  # 26
    ["NOP"],  #27 
    ["NOP"],
    ["RTM", 8, 4],  # 28: mem[RF[4]] = RF[8]
    ["NOP"],  # 29
    ["RTM", 7, 6],  # 30: mem[RF[6]] = RF[7]
    ["NOP"],  # 31
    ["NOP"],  # 32
    ["RTR", 4, 6],  # 33: RF[4] = RF[6]
    ["JUMP", 10],  # 34: jump to 8
    ["NOP"],  # 35
    ["NOP"],  # 36
    ["NOP"],  # 37
    ["NOP"],  # 38
    ["NOP"],  # 39
    ["SUMM", 2, 1, 2],  # 40: RF[1] = RF[2] + RF[2]
    ["JUMP", 7],  # 41: jump to 6
    ["NOP"],#42
    ["NOP"],#43
    ["NOP"],#44
    ["NOP"],#45
    ["NOP"],
]
cpu.load_program(program)

print("НАЧАЛЬНОЕ СОСТОЯНИЕ:")
cpu.print_state()

max_instructions = 200
instructions_executed = 0

while cpu.PC < len(cpu.cmd_mem) and instructions_executed < max_instructions:
    cpu.run_instruction()
    cpu.print_state()
    instructions_executed += 1

    if instructions_executed >= max_instructions:
        print("\nПРЕРВАНО: достигнут лимит выполненных команд")
        break

print("\nФИНАЛЬНОЕ СОСТОЯНИЕ:")
cpu.print_state()
print(f"\nВсего выполнено команд: {instructions_executed}")
