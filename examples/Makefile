# Copyright (c) 2026 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: Apache-2.0

ALL_TESTS := $(dir $(wildcard */design.yaml))

run_tests:
	for test_dir in $(ALL_TESTS); do \
		$(MAKE) -C $$test_dir; \
	done

clean:
	for test_dir in $(ALL_TESTS); do \
		$(MAKE) -C $$test_dir clean; \
	done

.DEFAULT: run_tests
.PHONY: run_tests clean
