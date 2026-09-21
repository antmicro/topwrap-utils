// Copyright (c) 2026 Antmicro <www.antmicro.com>
// SPDX-License-Identifier: Apache-2.0

module stream_ip(
    input wire clk,
    output wire [7:0] out_data,
    output wire out_valid,
    input wire out_ready
);

  reg [7:0] count;

  always @(posedge clk) begin
    if (out_ready)
      count <= count + 8'd1;
  end

  assign out_data = count;
  assign out_valid = 1'b1;

endmodule
