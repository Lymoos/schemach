`timescale 1ns / 1ps
module cpu(
    input clk, reset
);

localparam 
    CMD_SIZE = 19,
    PROG_SIZE = 32,
    PROG_ADDR_SIZE = $clog2(PROG_SIZE),
    WORD_SIZE = 10,
    RF_SIZE = 16,
    RF_ADDR_SIZE = $clog2(RF_SIZE),
    DATA_MEM_SIZE = 32,
    DATA_MEM_ADDR_SIZE = $clog2(DATA_MEM_SIZE),
    COP_SIZE = 4;


localparam
    NOP = 0,
    LTM = 1, 
    RTR = 3, 
    MTR = 2, 
    JL = 4, 
    SUMM = 6, 
    SBT = 5,
    MTRD = 7,
    RTM = 8,
    JMP = 9;

reg [CMD_SIZE  - 1 : 0] Prog     [0 : PROG_SIZE     - 1];
reg signed [WORD_SIZE - 1 : 0] DATA_MEM [0 : DATA_MEM_SIZE - 1];
reg signed [WORD_SIZE - 1 : 0] RF       [0 : RF_SIZE       - 1];

reg [PROG_ADDR_SIZE -1 : 0] pc, pc_next;
reg [CMD_SIZE - 1 : 0] cmd_0, cmd_0_next;
reg [CMD_SIZE - 1 : 0] cmd_1, cmd_1_next;
reg [CMD_SIZE - 1 : 0] cmd_2, cmd_2_next;
reg [CMD_SIZE - 1 : 0] cmd_3, cmd_3_next;

reg signed [WORD_SIZE - 1 : 0] opA_1, opA_1_next;
reg signed [WORD_SIZE - 1 : 0] opA_2, opA_2_next;

reg signed [WORD_SIZE - 1 : 0] opB_2, opB_2_next;
reg signed [2*WORD_SIZE - 1 : 0] res, res_next;


reg [WORD_SIZE          - 1 : 0] RF_data;
reg [RF_ADDR_SIZE       - 1 : 0] RF_addr;
reg [WORD_SIZE          - 1 : 0] DATA_MEM_data;
reg [DATA_MEM_ADDR_SIZE - 1 : 0] DATA_MEM_addr;
reg DATA_MEM_en;
reg RF_en;


integer i;
initial
begin
    for(i = 0; i < DATA_MEM_SIZE; i = i + 1)
        DATA_MEM[i] = 0;
    for(i = 0; i < RF_SIZE; i = i + 1)
        RF[i] = 0;
    RF[1] = 1;
    
    $readmemb("cmd_mem.mem", Prog);
end



//------------------------------
// Fetch
//------------------------------
always@(posedge clk)
    if(reset)
        cmd_0 <= 0;
    else
        cmd_0 <= cmd_0_next;

always@*
    if(will_jmp)
        cmd_0_next <= NOP;
    else
        cmd_0_next <= Prog[pc];

//------------------------------
// Decode 1
//------------------------------

wire [COP_SIZE           - 1 : 0] cop_1 = cmd_0[CMD_SIZE - 1 -: COP_SIZE];
wire [DATA_MEM_ADDR_SIZE - 1 : 0] adr_m_1_1 = cmd_0[CMD_SIZE - 1 - COP_SIZE -: DATA_MEM_ADDR_SIZE];
wire [RF_ADDR_SIZE - 1 : 0] adr_r_1_1 = cmd_0[CMD_SIZE - 1 - COP_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE - 1 : 0] adr_r_2_1 = cmd_0[CMD_SIZE - 1 - COP_SIZE  - RF_ADDR_SIZE -: RF_ADDR_SIZE];

wire [RF_ADDR_SIZE       - 1 : 0] adr_r_1_1_MTR     = cmd_0[CMD_SIZE-1 - COP_SIZE - DATA_MEM_ADDR_SIZE -: RF_ADDR_SIZE];

always@(posedge clk)
    if(reset)
        cmd_1 <= 0;
    else
        cmd_1 <= cmd_1_next;

always@*
    if(will_jmp)
        cmd_1_next <= NOP;
    else
        cmd_1_next <= cmd_0;


always@(posedge clk)
    if(reset)
        opA_1 <= 0;
    else
        opA_1 <= opA_1_next;

always@*
    case(cop_1)
        MTR: 
            if(DATA_MEM_en && DATA_MEM_addr == adr_m_1_1) 
                opA_1_next <= DATA_MEM_data; 
            else 
                opA_1_next <= DATA_MEM[adr_m_1_1];
        RTR, RTM: 
            if(RF_en && RF_addr == adr_r_2_1)
                opA_1_next <= RF_data; 
            else 
                opA_1_next <= RF[adr_r_2_1];
        MTRD, JL, SBT, SUMM: 
            if(RF_en && RF_addr == adr_r_1_1) 
                opA_1_next <= RF_data; 
            else 
                opA_1_next <= RF[adr_r_1_1];       
        default: opA_1_next <= opA_1;
    endcase 

//------------------------------
// Decode 2
//------------------------------

wire [COP_SIZE           - 1 : 0] cop_2 = cmd_1[CMD_SIZE - 1 -: COP_SIZE];
wire [DATA_MEM_ADDR_SIZE - 1 : 0] adr_m_1_2 = cmd_1[CMD_SIZE - 1 - COP_SIZE -: DATA_MEM_ADDR_SIZE];
wire [RF_ADDR_SIZE - 1 : 0] adr_r_1_2 = cmd_1[CMD_SIZE - 1 - COP_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE - 1 : 0] adr_r_2_2 = cmd_1[CMD_SIZE - 1 - COP_SIZE  - RF_ADDR_SIZE -: RF_ADDR_SIZE];

always@(posedge clk)
    if(reset)
        cmd_2 <= 0;
    else
        cmd_2 <= cmd_2_next;

always@*
    if(will_jmp)
        cmd_2_next <= NOP;
    else
        cmd_2_next <= cmd_1;


always@(posedge clk)
    if(reset)
        opA_2 <= 0;
    else
        opA_2 <= opA_2_next;

always@*
    opA_2_next <= opA_1; 


always@(posedge clk)
    if(reset)
        opB_2 <= 0;
    else
        opB_2 <= opB_2_next;

always@*
    case(cop_2)
        JL, SBT, SUMM: 
            if(RF_en && RF_addr == adr_r_2_2) 
                opB_2_next <= RF_data; 
            else 
                opB_2_next <= RF[adr_r_2_2];
        MTRD:
            if(DATA_MEM_en && DATA_MEM_addr == opA_1) 
                opB_2_next <= DATA_MEM_data; 
            else
                opB_2_next <= DATA_MEM[opA_1];
        RTM: 
            if(RF_en && RF_addr == adr_r_1_2) 
                opB_2_next <= RF_data; 
            else 
                opB_2_next <= RF[adr_r_1_2];
        default: opB_2_next <= opB_2;
    endcase 

//------------------------------
// Execute
//------------------------------

wire [COP_SIZE           - 1 : 0] cop_3 = cmd_2[CMD_SIZE - 1 -: COP_SIZE];
wire [DATA_MEM_ADDR_SIZE - 1 : 0] adr_m_1_3 = cmd_2[CMD_SIZE - 1 - COP_SIZE -: DATA_MEM_ADDR_SIZE];
wire [RF_ADDR_SIZE - 1 : 0] adr_r_1_3 = cmd_2[CMD_SIZE - 1 - COP_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE - 1 : 0] adr_r_2_3 = cmd_2[CMD_SIZE - 1 - COP_SIZE  - RF_ADDR_SIZE -: RF_ADDR_SIZE];

always@(posedge clk)
    if(reset)
        cmd_3 <= 0;
    else
        cmd_3 <= cmd_3_next;

always@*
    if(will_jmp)
        cmd_3_next <= NOP;
    else
        cmd_3_next <= cmd_2;


always@(posedge clk)
    if(reset)
        res <= 0;
    else
        res <= res_next;

always@*
    case(cop_3)
        MTR, RTR: res_next <= opA_2;
        JL: res_next <= opA_2 < opB_2;
        SBT: res_next <= opA_2 - opB_2;
        SUMM: res_next <= opA_2 + opB_2;
        MTRD: res_next <= opB_2;
        RTM: res_next <= {opA_2, opB_2};
        default: res_next <= res;
    endcase
    
//------------------------------
// WB
//------------------------------

wire [COP_SIZE           - 1 : 0] cop_4         = cmd_3[CMD_SIZE       - 1 -: COP_SIZE];
wire [DATA_MEM_ADDR_SIZE - 1 : 0] adr_m_1_4     = cmd_3[CMD_SIZE       - 1 - COP_SIZE -: DATA_MEM_ADDR_SIZE];
wire [RF_ADDR_SIZE       - 1 : 0] adr_r_1_4     = cmd_3[CMD_SIZE       - 1 - COP_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE       - 1 : 0] adr_r_2_4     = cmd_3[CMD_SIZE       - 1 - COP_SIZE  - RF_ADDR_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE       - 1 : 0] adr_r_3_4     = cmd_3[CMD_SIZE       - 1 - COP_SIZE  - 2*RF_ADDR_SIZE -: RF_ADDR_SIZE];
wire signed [WORD_SIZE          - 1 : 0]   literal     = cmd_3[WORD_SIZE      - 1 : 0];
wire [PROG_ADDR_SIZE     - 1 : 0] adr_to_jmp    = cmd_3[DATA_MEM_ADDR_SIZE-1:0];
wire [PROG_ADDR_SIZE     - 1 : 0] adr_to_jmp_JL = cmd_3[PROG_ADDR_SIZE - 1 : 0];

wire [RF_ADDR_SIZE       - 1 : 0] adr_r_1_4_MTR     = cmd_3[CMD_SIZE-1 - COP_SIZE - DATA_MEM_ADDR_SIZE -: RF_ADDR_SIZE];

always@*
    case(cop_4)
        MTR, RTR, SBT, SUMM, MTRD: RF_data <= res;
        default: RF_data <= 0;
    endcase

always@*
    case(cop_4)
        MTR : RF_addr <= adr_r_1_4_MTR;
        RTR: RF_addr <= adr_r_1_4;
        SBT, SUMM: RF_addr <= adr_r_3_4;
        MTRD: RF_addr <= adr_r_2_4;
        default: RF_addr <= 0;
    endcase
always@*
    case(cop_4)
        MTR, RTR, SBT, SUMM, MTRD: RF_en <= 1;
        default: RF_en <= 0;
    endcase



always @(posedge clk)
    if(RF_en)
        RF[RF_addr] <= RF_data;


always@*
    case(cop_4)
        LTM: DATA_MEM_data <= literal;
        RTM: DATA_MEM_data <= res;
        default: DATA_MEM_data <= 0;
    endcase

always@*
    case(cop_4)
        LTM: DATA_MEM_addr <= adr_m_1_4;
        RTM: DATA_MEM_addr <= res[2*WORD_SIZE - 1 -: WORD_SIZE];
        default: DATA_MEM_addr <= 0;
    endcase
always@*
    case(cop_4)
        LTM,RTM: DATA_MEM_en <= 1;
        default: DATA_MEM_en <= 0;
    endcase


always @(posedge clk)
    if(DATA_MEM_en)
        DATA_MEM[DATA_MEM_addr] <= DATA_MEM_data;

always@(posedge clk)
    if(reset)
        pc <= 0;
    else
        pc <= pc_next;

always@*
    case(cop_4)
        JMP: pc_next <= adr_to_jmp;
        JL: if(res) pc_next <= pc + 1; else pc_next <= adr_to_jmp_JL;
        default: pc_next <= pc + 1;
    endcase

wire will_jmp = (cop_4 == JL) && (res == 5'b00000);

endmodule
