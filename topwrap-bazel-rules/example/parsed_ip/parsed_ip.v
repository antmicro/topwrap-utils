// Copyright (c) 2026 Antmicro <www.antmicro.com>
// SPDX-License-Identifier: Apache-2.0

module parsed_ip(
    input wire clk,
    input wire rst,
    output wire led
);

  reg [23:0] count;

  always @(posedge clk) begin
    if (rst)
      count <= 24'd0;
    else
      count <= count + 24'd1;
  end

  assign led = count[23];

endmodule
