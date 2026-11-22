if(TARGET app)
  target_sources(app PRIVATE src/behaviors/behavior_rgb_local.c)
  target_sources(app PRIVATE src/fatal_reboot.c)
endif()
