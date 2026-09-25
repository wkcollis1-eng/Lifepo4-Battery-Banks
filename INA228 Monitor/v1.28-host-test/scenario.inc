// Host replay of the V1.28 CORE lambdas (turnover §10 gate 3). Lambdas are the
// generated code, verbatim; only the wiring below and stubs.h are harness.
#include "replay.inc"

static int g_fail = 0, g_pass = 0;
#define CHECK(cond, ...) do { if (cond) { g_pass++; printf("PASS  "); } else { g_fail++; printf("FAIL  "); } \
  printf(__VA_ARGS__); printf("\n"); } while (0)

static const double C_AH = 397.0;
static double V_BUS = 13.30;

static void wire() {
  hw_charge_ah->tmpl = HWC_T;
  hw_charge_ah->on_value = {[](float x) { HWC_OV(x); cycle_integration_delta->update(); soc_estimate->update(); }};
  hw_energy_wh->tmpl = HWE_T;
  hw_energy_wh->on_value = {[](float x) { HWE_OV(x); }};
  soc_estimate->tmpl = SOC_T;
  soc_ledger_sensor->tmpl = LEDGER_T;
  cycle_integration_delta->tmpl = CID_T;
  soc_anchor_set->fn = [](float a, int s, bool c) { ANCHOR_SET(a, s, c); };
}

// one boot: driver setup (SHUNT_CAL, ADC_CONFIG), then on_boot at -200
static void boot(double max_current) {
  reset_transients();
  ina.driver_setup(max_current);
  BOOT();
}

// advance the bank: current I (A) for dt seconds, polling like the firmware
static void run(double seconds, double amps, bool poll_energy = true) {
  double t = 0;
  while (t < seconds - 1e-9) {
    double step = std::min(60.0, seconds - t);
    ina.advance(step, amps, V_BUS);
    g_ms += (uint32_t) (step * 1000.0);
    t += step;
    ina228_current->state = (float) amps;
    ina228_voltage->state = (float) V_BUS;
    hw_charge_ah->update();
    if (poll_energy) hw_energy_wh->update();
    soc_estimate->update();
  }
}

static float soc() { return soc_estimate->state; }

// a reboot: uptime (millis) restarts, wall time continues, the reboot script's delay is over
static void reboot_fresh() {
  time_t wall = ha_time->base + g_ms / 1000;
  g_ms = 20000;
  ha_time->base = wall - g_ms / 1000;
  ina_reset_reboot_.running = false;
  boot(400.0);
}

int main() {
  wire();
  ha_time->base = REPLAY_T0_EPOCH - g_ms / 1000;
  g_quiet = false;

  // =============== S1: V1.27 -> V1.28 upgrade on the 09-25 13:30Z state ===============
  printf("\n=== S1 first V1.28 boot: LSB 200 -> 400 A migration, provisional anchor from the ledger ===\n");
  {
    const double lsb_old = 200.0 / 524288.0;
    const double hw0 = REPLAY[0][1];           // -5.0276 Ah (HA export)
    const double off_old = -1.7500;            // any V1.26 bridge offset
    ina.lsb = lsb_old;
    ina.charge_cnt = (hw0 - off_old) * 3600.0 / lsb_old;
    ina.energy_cnt = (569.0 - 12.0) * 3600.0 / (51.2 * lsb_old);
    ina.reg16[0x10] = 0x7FFE;                  // V1.27 wrote the sentinel
    hw_charge_offset_ah_.v = (float) off_old;
    hw_charge_saved_ah_.v = (float) hw0;
    hw_energy_offset_wh_.v = 12.0f;
    hw_energy_saved_wh_.v = 569.0f;
    ah_discharged_cycle->state = 0.13f; ah_charged_cycle->state = 0.0f;   // ledger: 99.967 %
    self_discharge_ah->state = 0.0f;
    const float ledger0 = 100.0f - 0.13f / 397.0f * 100.0f;
    boot(400.0);
    CHECK(std::fabs(hw_charge_ah->state - hw0) < 2e-4, "HW Net Charge continues across the LSB change: %.5f vs %.5f Ah", hw_charge_ah->state, hw0);
    CHECK(std::fabs(hw_energy_wh->state - 569.0f) < 0.05f, "HW Energy continues: %.2f Wh", hw_energy_wh->state);
    CHECK(std::fabs(hw_lsb_a_.v - (float) (400.0 / 524288.0)) < 1e-12, "hw_lsb_a migrated to %.6g", hw_lsb_a_.v);
    CHECK(ina.reg16[0x11] == 0x0960, "PWR_LIMIT = 0x%04X (want 0x0960)", ina.reg16[0x11]);
    CHECK(ina_expect_valid_.v && ina_expect_adc_config_.v == 0xFDC5, "readback: SHUNT_CAL=%u ADC_CONFIG=0x%04X [%s]", ina_expect_shunt_cal_.v, ina_expect_adc_config_.v, ina228_config_readback->state.c_str());
    CHECK(soc_anchor_src_.v == 3 && std::isnan(hw_charge_anchor_ah_.v) && !std::isnan(hw_prov_anchor_ah_.v), "provisional anchor from the SW ledger (src %d)", soc_anchor_src_.v);
    CHECK(std::fabs(soc() - ledger0) < 0.001f, "no SOC step at the V1.28 boot: %.4f%% vs ledger %.4f%%", soc(), ledger0);
    CHECK(soc_source->state.find("provisional anchor from the SW ledger") != std::string::npos, "SOC Source: %s", soc_source->state.c_str());
  }

  // =============== S1b: replay the 09-25 HW Net Charge record (13:30-20:25Z) ===============
  printf("\n=== S1b replay: 404 HA rows of HW Net Charge, 6.9 h idle ===\n");
  {
    g_quiet = true;
    float soc_start = soc();
    double hw_start = REPLAY[0][1];
    size_t n = sizeof(REPLAY) / sizeof(REPLAY[0]);
    for (size_t k = 1; k < n; k++) {
      double dt = REPLAY[k][0] - REPLAY[k - 1][0];
      double amps = (REPLAY[k][1] - REPLAY[k - 1][1]) * 3600.0 / dt;
      run(dt, amps);
    }
    g_quiet = false;
    double hw_end = REPLAY[n - 1][1];
    double want = soc_start + (hw_end - hw_start) / C_AH * 100.0;
    CHECK(std::fabs(hw_charge_ah->state - hw_end) < 5e-4, "HW Net Charge tracks the record: %.5f vs %.5f Ah", hw_charge_ah->state, hw_end);
    CHECK(std::fabs(soc() - want) < 0.001, "SOC follows CHARGE: %.4f%% (expected %.4f%%)", soc(), want);
    CHECK(std::fabs(brk_out_ah_.v - (hw_start - hw_end)) < 2e-3 && brk_in_ah_.v < 1e-3, "bracket out %.4f Ah (record %.4f), in %.4f Ah", brk_out_ah_.v, hw_start - hw_end, brk_in_ah_.v);
    CHECK(std::fabs(brk_whout_.v - brk_out_ah_.v * V_BUS) < 0.02, "Wh out %.3f = Ah out x V", brk_whout_.v);
    auto mr = MEANNET();
    float mean_ma = mr.has_value() ? *mr : NAN;
    CHECK(mean_ma < -8.0f && mean_ma > -9.5f && hours_since_anchor_.v > 6.8f, "mean net current since anchor %.2f mA over %.2f h (HA record: -8.8 mA)", mean_ma, hours_since_anchor_.v);
    CHECK(soc_last_good_.v == soc_last_good_.v, "soc_last_good persisted (%.3f)", soc_last_good_.v);
  }

  // =============== S2: runtime INA228 POR -> B2a detects, reboot bridges ===============
  printf("\n=== S2 INA228 power-on reset while running (B2a) ===\n");
  {
    float soc_before = soc();
    float hw_before = hw_charge_ah->state;
    run(30, -0.0105);                       // the last good poll saves ...
    ina.por();                              // ... then the chip resets
    int reb = ina_reset_reboot_.runs;
    int pubs = hw_charge_ah->publishes;
    g_ms += 60000; hw_charge_ah->update();  // next poll sees SHUNT_CAL/ADC_CONFIG/TEMP_LIMIT wrong
    CHECK(ina_reset_reboot_.runs == reb + 1, "reset detected, reboot scheduled (%s)", ina228_reset_check->state.c_str());
    CHECK(ina_reset_reboots_.v == 1, "reset reboot counted (%d in a row)", ina_reset_reboots_.v);
    CHECK(hw_charge_ah->publishes == pubs, "nothing published from the reset chip");
    // reboot (the script's safe_reboot): chip keeps its POR state; driver rewrites SHUNT_CAL/ADC_CONFIG
    ina.driver_setup(400.0);
    ina.advance(5, -0.0105, V_BUS);
    reset_transients();
    ina_reset_reboot_.running = false;
    BOOT();
    CHECK(hw_bridge_count_.v >= 1, "boot bridged the reset (bridge #%d): %s", hw_bridge_count_.v, ina228_reset_check->state.c_str());
    CHECK(std::fabs(hw_charge_ah->state - hw_before) < 0.02f, "HW Net Charge continuous within the 10 mAh save step: %.4f vs %.4f", hw_charge_ah->state, hw_before);
    CHECK(std::fabs(soc() - soc_before) < 0.01f, "SOC continuous: %.4f%% vs %.4f%%", soc(), soc_before);
    CHECK(soc_anchor_src_.v == 3, "anchor kept (src %d)", soc_anchor_src_.v);
  }

  // =============== S2b: a chip that keeps resetting -> reboots rate-limited (review 2026-09-25) ===============
  printf("\n=== S2b INA228 resetting every minute for 3 h: reboot rate limit (B2a) ===\n");
  {
    ina_reset_reboots_.v = 0;                      // (S2's reboot kept uptime > 1 h, so its boot poll cleared it)
    float soc_before = soc();
    g_quiet = true;
    reboot_fresh();
    int boots = 0, last_boot = -1, min_gap = 1 << 30;
    bool doubled = false;
    std::string deferred;
    for (int minute = 0; minute < 180; minute++) {
      ina.por();                                   // the chip resets ...
      int r = ina_reset_reboot_.runs, c = ina_reset_reboots_.v;
      run(60, -0.0105);                            // ... and the next poll sees it
      if (ina228_reset_check->state.find("deferred") != std::string::npos) deferred = ina228_reset_check->state;
      if (ina_reset_reboot_.runs != r) {
        hw_charge_ah->update();                    // a component.update inside the 2 s delay
        if (ina_reset_reboots_.v != c + 1 || ina_reset_reboot_.runs != r + 1) doubled = true;
        if (boots >= 3) min_gap = std::min(min_gap, minute - last_boot);
        last_boot = minute;
        boots++;
        reboot_fresh();
      }
    }
    g_quiet = false;
    CHECK(boots >= 6 && boots <= 9, "%d reboots in 180 min of a reset every minute (no limit: 1 per poll)", boots);
    CHECK(min_gap >= 30, "after 3 in a row, reboots >= 30 min apart (closest %d min)", min_gap);
    CHECK(!doubled, "a component.update inside the 2 s delay neither re-counts nor re-executes");
    CHECK(!deferred.empty(), "deferral announced: %s", deferred.c_str());
    CHECK(std::fabs(soc() - soc_before) < 0.05f, "SOC through the resets: %.4f%% vs %.4f%%", soc(), soc_before);
    reboot_fresh();                                // the fault clears
    run(3000, -0.0105);
    CHECK(ina_reset_reboots_.v == boots, "count held through 50 min of held config (%d)", ina_reset_reboots_.v);
    run(900, -0.0105);
    CHECK(ina_reset_reboots_.v == 0, "count cleared after 1 h with the config held (%d)", ina_reset_reboots_.v);
  }

  // =============== S3: reset that cannot be bridged -> carry from the last CHARGE SOC ===============
  printf("\n=== S3 INA228 reset with nothing saved to bridge from ===\n");
  {
    run(600, -0.0105);
    float soc_before = soc();
    hw_charge_saved_ah_.v = NAN;
    ina.por(); ina.driver_setup(400.0);
    reset_transients();
    BOOT();
    CHECK(soc_anchor_src_.v == 4, "provisional anchor carried from the last CHARGE SOC (src %d): %s", soc_anchor_src_.v, soc_source->state.c_str());
    CHECK(std::fabs(soc() - soc_before) <= 0.051f, "SOC continuous within the 0.05 %% save step: %.4f%% vs %.4f%%", soc(), soc_before);
  }

  // =============== S4: full charge, tapered (O2 passes) -> clean anchor, closure ===============
  printf("\n=== S4 full charge: CC 80 A, CV taper to 6.5 A, charger stops ===\n");
  {
    run(3600.0 * 24 * 3, -0.0105);           // 3 days idle
    float soc_pre = soc();
    // charge session
    is_charging_.state = true; CHG_PRESS();
    V_BUS = 14.0; run(3600.0 * 0.5, 80.0);    // CC
    V_BUS = 14.4; battery_fully_charged_.state = true; absorption_reached_.v = true;
    for (double a : {60.0, 40.0, 25.0, 15.0, 10.0, 7.5, 6.5}) {
      run(300, a);
      ina228_current->state = (float) a; TAIL_5S();
    }
    battery_fully_charged_.state = false; is_charging_.state = false;
    V_BUS = 13.40; run(60, -0.0105);         // charger stopped; is_charging releases 60 s later
    hw_charge_ah->update();                  // on_release: component.update first
    CHG_SESS();
    bool ok = CHG_COND();
    CHECK(ok, "O2 passes: CV tail %.2f A <= 10 A", absorb_tail_min_a_.v);
    if (ok) {
      CHG_THEN();
      ah_discharged_cycle->reset(); ah_charged_cycle->reset(); wh_discharged_cycle->reset(); self_discharge_ah->reset();
    } else CHG_ELSE();
    float ah_in_session = last_session_ah_.v;
    CHECK(ah_in_session > 40.0f + 11.0f, "session Ah (CHARGE) %.3f, Wh %.1f", ah_in_session, last_session_wh_.v);
    CHECK(!std::isnan(last_closure_ah_.v), "closure logged: %.3f Ah (provisional start at %.2f%% before charging)", last_closure_ah_.v, soc_pre);
    soc_estimate->update();
    CHECK(std::fabs(soc() - 100.0f) < 0.001f && soc_anchor_src_.v == 1 && brk_clean_.v, "SOC 100 %% on a clean anchor: %s", soc_source->state.c_str());
  }

  // =============== S4b: generator stops mid-CV -> O2 refuses the anchor ===============
  printf("\n=== S4b charge stopped mid-CV at 30 A ===\n");
  {
    run(3600.0 * 5, -3.0);                   // 15 Ah out
    float soc_pre = soc();
    is_charging_.state = true; CHG_PRESS();
    V_BUS = 14.4; battery_fully_charged_.state = true; absorption_reached_.v = true;
    run(600, 30.0); ina228_current->state = 30.0f; TAIL_5S(); TAIL_5S();   // 2 CV polls: one commits
    battery_fully_charged_.state = false; is_charging_.state = false;
    V_BUS = 13.4; run(60, -0.0105);
    hw_charge_ah->update(); CHG_SESS();
    bool ok = CHG_COND();
    CHECK(!ok, "O2 refuses: CV tail %.1f A > 10 A", absorb_tail_min_a_.v);
    if (!ok) CHG_ELSE();
    CHECK(soc_anchor_src_.v == 1 && soc() < 100.0f && soc() > soc_pre, "no false 100 %%: SOC %.2f%% (was %.2f%%, +5 Ah x CE)", soc(), soc_pre);
  }

  // =============== S5: clean bracket -> CHARGE RECON ~0 when the drain was seen ===============
  printf("\n=== S5 clean full -> 20 d idle -> full: RECON (CHARGE) ===\n");
  {
    // top up to a clean full first
    is_charging_.state = true; CHG_PRESS();
    V_BUS = 14.4; battery_fully_charged_.state = true; absorption_reached_.v = true;
    double deficit = (100.0 - soc()) / 100.0 * C_AH;
    run(3600.0 * deficit / 0.99 / 20.0, 20.0);
    ina228_current->state = 6.5f; TAIL_5S(); TAIL_5S();   // 2 CV polls: one commits
    battery_fully_charged_.state = false; is_charging_.state = false;
    hw_charge_ah->update(); CHG_SESS(); if (CHG_COND()) { CHG_THEN(); ah_discharged_cycle->reset(); ah_charged_cycle->reset(); wh_discharged_cycle->reset(); self_discharge_ah->reset(); }
    CHECK(brk_clean_.v && soc_anchor_src_.v == 1, "clean anchor, bracket starts");
    // 20 days idle at -10.5 mA, then a recharge that returns exactly drain / CE
    V_BUS = 13.30;
    g_quiet = true; run(3600.0 * 24 * 20, -0.0105); g_quiet = false;
    double drain = 0.0105 * 24 * 20;
    is_charging_.state = true; CHG_PRESS();
    V_BUS = 14.4; battery_fully_charged_.state = true; absorption_reached_.v = true;
    run(3600.0 * (drain / 0.99) / 5.0, 5.0);
    ina228_current->state = 5.0f; TAIL_5S(); TAIL_5S();   // 2 CV polls: one commits
    battery_fully_charged_.state = false; is_charging_.state = false;
    hw_charge_ah->update(); CHG_SESS();
    if (CHG_COND()) { CHG_THEN(); ah_discharged_cycle->reset(); ah_charged_cycle->reset(); wh_discharged_cycle->reset(); self_discharge_ah->reset(); }
    CHECK(std::fabs(last_unseen_drain_ah_.v) < 0.01f, "RECON U = %.4f Ah (drain fully seen, CE = recon_coul_eff)", last_unseen_drain_ah_.v);
    CHECK(std::fabs(last_offset_suggest_ma_.v) < 0.03f, "Suggested Offset Current %.3f mA", last_offset_suggest_ma_.v);
    CHECK(std::fabs(last_session_ah_.v - drain / 0.99) < 0.02, "session Ah %.3f = drain/CE %.3f", last_session_ah_.v, drain / 0.99);
  }

  // =============== S6: CHARGE invalid -> ledger movement from the last CHARGE SOC ===============
  printf("\n=== S6 CHARGE unreadable for 10 min ===\n");
  {
    V_BUS = 13.3;
    run(3600, -2.0);
    float soc_before = soc();
    ina.fail = true;
    g_ms += 240000; hw_charge_ah->update(); soc_estimate->update();   // fallback engages
    ah_discharged_cycle->state += 0.2f;      // then the ledger books 2 A x 6 min
    soc_estimate->update();
    CHECK(soc_source->state.find("SW ledger movement") != std::string::npos, "fallback after 180 s: %s", soc_source->state.c_str());
    CHECK(std::fabs(soc() - (soc_before - 0.2f / 397.0f * 100.0f)) < 0.06f, "SOC %.3f%% = last CHARGE SOC %.3f%% - ledger movement", soc(), soc_before);
    ina.fail = false;
    run(60, -2.0);
    CHECK(soc_source->state.find("INA228 CHARGE") != std::string::npos, "back on CHARGE: %s", soc_source->state.c_str());
  }

  // =============== S7: noise gauge ===============
  printf("\n=== S7 noise gauge ===\n");
  {
    V_BUS = 13.3;
    for (int k = 0; k < 20; k++) { ina.energy_cnt += (0.231 - 0.0105 * 13.3) / 60.0 / (51.2 * ina.lsb / 3600.0); run(60, -0.0105, true); }
    CHECK(ina_noise_state->state == "quiet", "0.231 W -> %s (gauge %.3f W)", ina_noise_state->state.c_str(), ina_noise_gauge->state);
    for (int k = 0; k < 30; k++) { ina.energy_cnt += (0.46 - 0.0105 * 13.3) / 60.0 / (51.2 * ina.lsb / 3600.0); run(60, -0.0105, true); }
    CHECK(ina_noise_state->state == "noisy", "0.46 W -> %s (gauge %.3f W)", ina_noise_state->state.c_str(), ina_noise_gauge->state);
  }

  // =============== S8: manual anchor, Wi-Fi readback, every template ===============
  printf("\n=== S8 manual anchor, readbacks, all templates ===\n");
  {
    MANUAL();
    ah_discharged_cycle->reset(); ah_charged_cycle->reset(); wh_discharged_cycle->reset(); self_discharge_ah->reset();
    soc_estimate->update();
    CHECK(soc_anchor_src_.v == 2 && !brk_clean_.v && std::fabs(soc() - 100.0f) < 0.001f, "manual anchor: %s", soc_source->state.c_str());
    WIFI_RB();
    CHECK(wifi_ps_readback->state.find("MIN_MODEM") == 0 && std::fabs(wifi_txp_readback->state - 11.0f) < 0.01f, "Wi-Fi readback: %s, %.2f dBm", wifi_ps_readback->state.c_str(), wifi_txp_readback->state);
    int nan_count = 0;
    for (auto &f : ALL_TEMPLATES) { auto r = f(); if (r.has_value() && std::isnan(*r)) nan_count++; }
    CHECK(true, "all %zu V1.28-touched templates ran (%d returned NAN, e.g. no clean RECON yet)", ALL_TEMPLATES.size(), nan_count);
  }

  // =============== S9: LSB change with the registers unreadable ===============
  printf("\n=== S9 LSB change but the chip is unreadable at boot ===\n");
  {
    hw_lsb_a_.v = (float) (200.0 / 524288.0);
    ina.fail = true;
    reset_transients();
    ina.driver_setup(400.0);
    BOOT();
    CHECK(std::isnan(hw_charge_anchor_ah_.v) && std::isnan(hw_prov_anchor_ah_.v), "anchors invalidated: %s", ina228_reset_check->state.c_str());
    ina.fail = false;
    float before = soc_last_good_.v;
    run(60, -0.0105);
    CHECK(soc_anchor_src_.v == 4 && std::fabs(soc() - before) < 0.06f, "SOC carries on from %.3f%% -> %.3f%% (%s)", before, soc(), soc_source->state.c_str());
  }

  // =============== S4c (review 2026-09-25): mid-CV stop with ONE straddling reading ===============
  // The INA228 averages 256 x 6.244 ms = 1.6 s. The conversion that covers a charger
  // stop reads between the CV current and ~0. Absorption Phase is still ON for its
  // 30 s delayed_off and the reading is > charge_threshold_a, so the 5 s tracker sees it.
  // V1.28 as first built committed it: the 8 A case FAILED here ("anchor ACCEPTED").
  for (int k = 0; k < 2; k++) {
    const float straddle = k == 0 ? 8.0f : 15.0f;   // k=0 fault, k=1 control (> 10 A)
    printf("\n=== S4c charge stopped mid-CV at 30 A, straddling reading %.1f A ===\n", straddle);
    run(3600.0 * 5, -3.0);
    is_charging_.state = true; CHG_PRESS();
    V_BUS = 14.4; battery_fully_charged_.state = true; absorption_reached_.v = true;
    run(600, 30.0); ina228_current->state = 30.0f; TAIL_5S(); TAIL_5S();
    ina228_current->state = straddle; TAIL_5S();          // the one straddling conversion
    ina228_current->state = 0.0f; TAIL_5S();              // charger off, Absorption Phase held on
    battery_fully_charged_.state = false; is_charging_.state = false;
    V_BUS = 13.4; run(60, -0.0105);
    hw_charge_ah->update(); CHG_SESS();
    bool ok = CHG_COND();
    CHECK(!ok, "O2 refuses a mid-CV stop at 30 A (straddle %.1f A): CV tail read %.1f A, anchor %s",
          straddle, absorb_tail_min_a_.v, ok ? "ACCEPTED - false 100 pct" : "refused");
    if (!ok) CHG_ELSE();
    else { absorption_reached_.v = false; absorb_tail_min_a_.v = NAN; }
  }

  // =============== S4d (review 2026-09-25): the straddle reading is dropped, not carried ===============
  printf("\n=== S4d straddle, charger off, charger back on at 30 A ===\n");
  {
    run(3600.0, -3.0);
    is_charging_.state = true; CHG_PRESS();
    V_BUS = 14.4; battery_fully_charged_.state = true; absorption_reached_.v = true;
    run(600, 30.0); ina228_current->state = 30.0f; TAIL_5S();
    ina228_current->state = 8.0f; TAIL_5S();               // straddles the stop
    ina228_current->state = 0.0f; TAIL_5S();               // Absorption Phase still held on
    ina228_current->state = 30.0f; TAIL_5S(); TAIL_5S();   // charger back, CV again
    CHECK(absorb_tail_min_a_.v > 29.0f, "straddle reading dropped at the stop: CV tail %.1f A", absorb_tail_min_a_.v);
    battery_fully_charged_.state = false; is_charging_.state = false;
    V_BUS = 13.4; run(60, -0.0105);
    hw_charge_ah->update(); CHG_SESS();
    if (!CHG_COND()) CHG_ELSE();
  }

  printf("\n%d passed, %d failed\n", g_pass, g_fail);
  return g_fail ? 1 : 0;
}
