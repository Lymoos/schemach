`timescale 1ns / 1ps

module cpu(
    input clk, reset,
    output pc
    );
localparam LITERAL_SIZE = 10;
localparam COP_SIZE = 4;

localparam CMD_MEM_SIZE = 32;
localparam CMD_ADDR_SIZE = $clog2(CMD_MEM_SIZE);
localparam CMD_SIZE = 19;

localparam MEM_SIZE = 32;
localparam MEM_ADDR_SIZE = $clog2(MEM_SIZE);
localparam MEM_DATA_SIZE = LITERAL_SIZE;

localparam RF_SIZE = 16;
localparam RF_ADDR_SIZE = $clog2(RF_SIZE);
localparam RF_DATA_SIZE = LITERAL_SIZE;

localparam NOP = 0, LTM = 1, MTR = 2, RTR = 3, JL = 4, SBT = 5, SUMM = 6, MTRD = 7, RTM = 8, JUMP = 9;

reg [CMD_SIZE       -1:0] cmd_mem [0:CMD_MEM_SIZE-1];
reg signed [MEM_DATA_SIZE  -1:0] mem [0:MEM_SIZE-1];
reg signed [RF_DATA_SIZE   -1:0] RF [0:RF_SIZE-1];
reg [CMD_ADDR_SIZE  -1:0] pc;
reg [CMD_SIZE       -1:0] cmd_reg;
reg signed [LITERAL_SIZE   -1:0] opA, opB;
reg signed [2*LITERAL_SIZE -1:0] res;

`define hi 2*LITERAL_SIZE-1 -: LITERAL_SIZE
`define lo LITERAL_SIZE - 1: 0
reg [2:0] stage_counter;

integer i;
initial
begin
    for(i = 0; i < MEM_SIZE; i = i + 1)
        mem[i] = 0;
    for(i = 0; i < RF_SIZE; i = i + 1)
        RF[i] = 0;
    RF[1] = 1;
    
    $readmemb("cmd_mem.mem", cmd_mem);
end

wire [COP_SIZE-1:0] cop                 = cmd_reg[CMD_SIZE-1 -: COP_SIZE];
wire [RF_ADDR_SIZE-1:0] addr_m_1        = cmd_reg[CMD_SIZE-1 - COP_SIZE -: MEM_ADDR_SIZE];
wire [RF_ADDR_SIZE-1:0] addr_r_1        = cmd_reg[CMD_SIZE-1 - COP_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE-1:0] addr_r_1_MTR    = cmd_reg[CMD_SIZE-1 - COP_SIZE - MEM_ADDR_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE-1:0] addr_r_2        = cmd_reg[CMD_SIZE-1 - COP_SIZE - RF_ADDR_SIZE -: RF_ADDR_SIZE];
wire [RF_ADDR_SIZE-1:0] addr_r_3        = cmd_reg[CMD_SIZE-1 - COP_SIZE - 2*RF_ADDR_SIZE -: RF_ADDR_SIZE];
wire signed [LITERAL_SIZE-1:0] literal         = cmd_reg[LITERAL_SIZE-1:0];
wire [CMD_ADDR_SIZE-1:0] addr_to_jmp    = cmd_reg[CMD_ADDR_SIZE-1:0];

always@(posedge clk)
    if(reset || stage_counter == 4)
        stage_counter <= 0;
    else
        stage_counter <= stage_counter + 1;
    
always@(posedge clk)
    if(reset)
        cmd_reg <= {(CMD_SIZE){1'b0}};
    else
        if(stage_counter == 0)
            cmd_reg <= cmd_mem[pc];
            
always@(posedge clk)
    if(reset)
        opA <= {(LITERAL_SIZE){1'b0}};
    else
        if(stage_counter == 1)
            case (cop)
                LTM: opA <= addr_m_1;
                MTR: opA <= mem[addr_r_1_MTR];
                RTR: opA <= RF[addr_r_2];
                RTM: opA <= RF[addr_r_2];
                JL, SUMM, SBT, MTRD: opA <= RF[addr_r_1];
            endcase
            
always@(posedge clk)
    if(reset)
        opB <= {(LITERAL_SIZE){1'b0}};
    else
        if(stage_counter == 2)
            case (cop)
                LTM: opB <= literal;
                JL, SUMM, SBT: opB <= RF[addr_r_2];
                MTRD: opB <= mem[opA];
                RTM: opB <= RF[addr_r_1];
            endcase

always@(posedge clk)
    if(reset)
        res <= {(2*LITERAL_SIZE){1'b0}};
    else
        if(stage_counter == 3)
            case (cop)
                LTM, RTM: res <= {opA, opB};
                MTR, RTR: res <= opA;
                MTRD: res <= opB;
                JL: res <= opA < opB;
                SBT: res <= opA - opB;
                SUMM: res <= opA + opB;  
            endcase

always@(posedge clk)
    if(reset)
        pc <= {(CMD_ADDR_SIZE){1'b0}};
    else
        if(stage_counter == 4)
            case (cop)
                JL: if(res == 1) pc <= pc + 1; else pc <= addr_to_jmp;
                JUMP: pc <= addr_to_jmp;
                default: pc <= pc + 1;
            endcase

always@(posedge clk)
    if(stage_counter == 4)
        case (cop)
            MTR: RF[addr_m_1] <= res;
            RTR: RF[addr_r_1] <= res;
            SBT, SUMM: RF[addr_r_3] <= res;
            MTRD: RF[addr_r_2] <= res;
        endcase

always@(posedge clk)
    if(stage_counter == 4)
        case (cop)
            LTM, RTM: mem[res[`hi]] <= res[`lo];
        endcase

endmodule
