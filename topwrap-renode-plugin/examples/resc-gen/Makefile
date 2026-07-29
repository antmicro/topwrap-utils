# Copyright (c) 2026 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: Apache-2.0

BUILD_DIR := ./build
OUTPUT := $(BUILD_DIR)/output.repl

$(OUTPUT): design.yaml | $(BUILD_DIR)
	topwrap build -d $< -b $(BUILD_DIR)

clean:
	rm -r $(BUILD_DIR)

$(BUILD_DIR):
	mkdir -p $@

.DEFAULT: $(OUTPUT)
.PHONY: clean
