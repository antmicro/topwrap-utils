// Copyright (c) 2026 Antmicro <www.antmicro.com>
// SPDX-License-Identifier: Apache-2.0

module manual_ip(
    input wire a,
    input wire b,
    output wire y
);

  assign y = a | b;

endmodule
