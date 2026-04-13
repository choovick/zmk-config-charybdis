/*
 * Copyright (c) 2026
 *
 * SPDX-License-Identifier: MIT
 */

#define DT_DRV_COMPAT zmk_behavior_rgb_local

#include <errno.h>
#include <zephyr/device.h>
#include <zephyr/logging/log.h>
#include <zephyr/sys/util.h>

#include <drivers/behavior.h>
#include <dt-bindings/zmk/rgb.h>
#include <zmk/behavior.h>
#include <zmk/rgb_underglow.h>

#if IS_ENABLED(CONFIG_ZMK_SPLIT) && IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL)
#include <zmk/split/central.h>
#endif

LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

#if DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT)

#define RGB_LOCAL_SYNC_APPLY_CMD 0x52474253u /* 'RGBS' */

#define RGB_HUE_MAX 360U
#define RGB_SAT_MAX 100U
#define RGB_BRT_MAX 100U
#define RGB_EFFECT_COUNT 4U

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_HUE_START
#define CONFIG_ZMK_RGB_UNDERGLOW_HUE_START 0
#endif

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_SAT_START
#define CONFIG_ZMK_RGB_UNDERGLOW_SAT_START 100
#endif

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_BRT_START
#define CONFIG_ZMK_RGB_UNDERGLOW_BRT_START 50
#endif

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_EFF_START
#define CONFIG_ZMK_RGB_UNDERGLOW_EFF_START 0
#endif

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_ON_START
#define CONFIG_ZMK_RGB_UNDERGLOW_ON_START 1
#endif

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_HUE_STEP
#define CONFIG_ZMK_RGB_UNDERGLOW_HUE_STEP 10
#endif

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_SAT_STEP
#define CONFIG_ZMK_RGB_UNDERGLOW_SAT_STEP 10
#endif

#ifndef CONFIG_ZMK_RGB_UNDERGLOW_BRT_STEP
#define CONFIG_ZMK_RGB_UNDERGLOW_BRT_STEP 10
#endif

struct rgb_sync_state {
    struct zmk_led_hsb color;
    uint8_t effect;
    bool on;
};

static struct rgb_sync_state central_model_state;
static bool central_model_initialized;

static struct rgb_sync_state default_rgb_state(void) {
    return (struct rgb_sync_state){
        .color =
            {
                .h = CONFIG_ZMK_RGB_UNDERGLOW_HUE_START,
                .s = CONFIG_ZMK_RGB_UNDERGLOW_SAT_START,
                .b = CONFIG_ZMK_RGB_UNDERGLOW_BRT_START,
            },
        .effect = CONFIG_ZMK_RGB_UNDERGLOW_EFF_START,
        .on = IS_ENABLED(CONFIG_ZMK_RGB_UNDERGLOW_ON_START),
    };
}

static uint16_t wrap_hue(int32_t value) {
    int32_t wrapped = value % (int32_t)RGB_HUE_MAX;

    if (wrapped < 0) {
        wrapped += RGB_HUE_MAX;
    }

    return (uint16_t)wrapped;
}

static uint8_t clamp_percent(int32_t value) {
    return (uint8_t)CLAMP(value, 0, 100);
}

static uint8_t wrap_effect(int32_t value) {
    int32_t wrapped = value % (int32_t)RGB_EFFECT_COUNT;

    if (wrapped < 0) {
        wrapped += RGB_EFFECT_COUNT;
    }

    return (uint8_t)wrapped;
}

static int read_local_rgb_state(struct rgb_sync_state *state) {
    if (!IS_ENABLED(CONFIG_ZMK_RGB_UNDERGLOW)) {
        return -ENOTSUP;
    }

    bool on = false;
    int err = zmk_rgb_underglow_get_state(&on);
    if (err < 0) {
        return err;
    }

    state->on = on;
    state->color = zmk_rgb_underglow_calc_hue(0);
    err = zmk_rgb_underglow_calc_effect(0);
    if (err < 0) {
        return err;
    }

    state->effect = (uint8_t)err;
    return 0;
}

static void ensure_model_initialized(void) {
    if (central_model_initialized) {
        return;
    }

    central_model_state = default_rgb_state();

    struct rgb_sync_state current = {0};
    if (read_local_rgb_state(&current) == 0) {
        central_model_state = current;
    }

    central_model_initialized = true;
}

static void refresh_model_from_local_if_available(void) {
    struct rgb_sync_state current = {0};
    if (read_local_rgb_state(&current) == 0) {
        central_model_state = current;
    }
}

static uint32_t pack_rgb_state(const struct rgb_sync_state *state) {
    return (state->color.h & 0x1FFu) | ((state->color.s & 0x7Fu) << 9) |
           ((state->color.b & 0x7Fu) << 16) | ((state->effect & 0x1Fu) << 23) |
           ((state->on ? 1u : 0u) << 28);
}

static int unpack_rgb_state(uint32_t packed, struct rgb_sync_state *state) {
    state->color.h = packed & 0x1FFu;
    state->color.s = (packed >> 9) & 0x7Fu;
    state->color.b = (packed >> 16) & 0x7Fu;
    state->effect = (packed >> 23) & 0x1Fu;
    state->on = ((packed >> 28) & 0x1u) != 0u;

    if (state->color.h > RGB_HUE_MAX || state->color.s > RGB_SAT_MAX || state->color.b > RGB_BRT_MAX ||
        state->effect >= RGB_EFFECT_COUNT) {
        return -EINVAL;
    }

    return 0;
}

static int apply_local_rgb_state(const struct rgb_sync_state *target) {
    if (!IS_ENABLED(CONFIG_ZMK_RGB_UNDERGLOW)) {
        return 0;
    }

    struct rgb_sync_state current = {0};
    bool have_current = read_local_rgb_state(&current) == 0;

    if (!have_current || current.color.h != target->color.h || current.color.s != target->color.s ||
        current.color.b != target->color.b) {
        int err = zmk_rgb_underglow_set_hsb(target->color);
        if (err < 0) {
            return err;
        }
    }

    if (!have_current || current.effect != target->effect) {
        int err = zmk_rgb_underglow_select_effect(target->effect);
        if (err < 0) {
            return err;
        }
    }

    if (!have_current || current.on != target->on) {
        return target->on ? zmk_rgb_underglow_on() : zmk_rgb_underglow_off();
    }

    return 0;
}

static int broadcast_rgb_state(const char *behavior_dev, struct zmk_behavior_binding_event event,
                               const struct rgb_sync_state *state) {
#if IS_ENABLED(CONFIG_ZMK_SPLIT) && IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL)
    struct zmk_behavior_binding sync_binding = {
        .behavior_dev = behavior_dev,
        .param1 = RGB_LOCAL_SYNC_APPLY_CMD,
        .param2 = pack_rgb_state(state),
    };

    for (uint8_t source = 0; source < ZMK_SPLIT_CENTRAL_PERIPHERAL_COUNT; source++) {
        int err = zmk_split_central_invoke_behavior(source, &sync_binding, event, true);
        if (err < 0) {
            LOG_DBG("RGB sync send to source %d failed (%d)", source, err);
        }
    }
#else
    ARG_UNUSED(behavior_dev);
    ARG_UNUSED(event);
    ARG_UNUSED(state);
#endif

    return 0;
}

static int apply_rgb_command_to_model(uint32_t command) {
    switch (command) {
    case RGB_TOG_CMD:
        central_model_state.on = !central_model_state.on;
        return 0;
    case RGB_ON_CMD:
        central_model_state.on = true;
        return 0;
    case RGB_OFF_CMD:
        central_model_state.on = false;
        return 0;
    case RGB_HUI_CMD:
        central_model_state.color.h =
            wrap_hue((int32_t)central_model_state.color.h + CONFIG_ZMK_RGB_UNDERGLOW_HUE_STEP);
        return 0;
    case RGB_HUD_CMD:
        central_model_state.color.h =
            wrap_hue((int32_t)central_model_state.color.h - CONFIG_ZMK_RGB_UNDERGLOW_HUE_STEP);
        return 0;
    case RGB_SAI_CMD:
        central_model_state.color.s =
            clamp_percent((int32_t)central_model_state.color.s + CONFIG_ZMK_RGB_UNDERGLOW_SAT_STEP);
        return 0;
    case RGB_SAD_CMD:
        central_model_state.color.s =
            clamp_percent((int32_t)central_model_state.color.s - CONFIG_ZMK_RGB_UNDERGLOW_SAT_STEP);
        return 0;
    case RGB_BRI_CMD:
        central_model_state.color.b =
            clamp_percent((int32_t)central_model_state.color.b + CONFIG_ZMK_RGB_UNDERGLOW_BRT_STEP);
        return 0;
    case RGB_BRD_CMD:
        central_model_state.color.b =
            clamp_percent((int32_t)central_model_state.color.b - CONFIG_ZMK_RGB_UNDERGLOW_BRT_STEP);
        return 0;
    case RGB_EFF_CMD:
        central_model_state.effect = wrap_effect((int32_t)central_model_state.effect + 1);
        return 0;
    case RGB_EFR_CMD:
        central_model_state.effect = wrap_effect((int32_t)central_model_state.effect - 1);
        return 0;
    case RGB_SPI_CMD:
    case RGB_SPD_CMD:
        /* No absolute speed setter exists in ZMK underglow API yet. */
        return 0;
    default:
        return -ENOTSUP;
    }
}

static int on_keymap_binding_pressed(struct zmk_behavior_binding *binding,
                                     struct zmk_behavior_binding_event event) {
    ensure_model_initialized();

    if (binding->param1 == RGB_LOCAL_SYNC_APPLY_CMD) {
        struct rgb_sync_state incoming = {0};
        int err = unpack_rgb_state(binding->param2, &incoming);
        if (err < 0) {
            return err;
        }

        central_model_state = incoming;
        return apply_local_rgb_state(&incoming);
    }

    refresh_model_from_local_if_available();

    int err = apply_rgb_command_to_model(binding->param1);
    if (err < 0) {
        return err;
    }

    err = apply_local_rgb_state(&central_model_state);
    if (err < 0) {
        return err;
    }

    err = broadcast_rgb_state(binding->behavior_dev, event, &central_model_state);
    if (err < 0) {
        return err;
    }

    return ZMK_BEHAVIOR_OPAQUE;
}

static int on_keymap_binding_released(struct zmk_behavior_binding *binding,
                                      struct zmk_behavior_binding_event event) {
    ARG_UNUSED(binding);
    ARG_UNUSED(event);
    return ZMK_BEHAVIOR_OPAQUE;
}

static const struct behavior_driver_api behavior_rgb_local_driver_api = {
    .binding_pressed = on_keymap_binding_pressed,
    .binding_released = on_keymap_binding_released,
    .locality = BEHAVIOR_LOCALITY_CENTRAL,
};

BEHAVIOR_DT_INST_DEFINE(0, NULL, NULL, NULL, NULL, POST_KERNEL, CONFIG_KERNEL_INIT_PRIORITY_DEFAULT,
                        &behavior_rgb_local_driver_api);

#endif /* DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT) */
