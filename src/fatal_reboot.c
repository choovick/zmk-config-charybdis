/*
 * Copyright (c) 2026 The ZMK Contributors
 * SPDX-License-Identifier: MIT
 *
 * Reboot on any kernel fatal error (stack overflow caught by HW stack protection,
 * hard fault, k_panic/k_oops, ...) instead of Zephyr's default behaviour of halting.
 * A halted half looks exactly like a "frozen" keyboard that needs a power cycle;
 * rebooting recovers it automatically in ~1s and it reconnects to the central.
 */

#include <zephyr/kernel.h>
#include <zephyr/fatal.h>
#include <zephyr/logging/log_ctrl.h>
#include <cmsis_core.h>

void k_sys_fatal_error_handler(unsigned int reason, const struct arch_esf *esf) {
    ARG_UNUSED(esf);
    ARG_UNUSED(reason);

    LOG_PANIC();
    NVIC_SystemReset();

    CODE_UNREACHABLE;
}
