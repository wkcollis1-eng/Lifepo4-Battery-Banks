// Behavioral stubs mirroring the ESPHome 2026.9.0 / ESP-IDF 5.5 surface used by the
// V1.28 lambdas (generated ->value() / ->state / ->publish_state / ->execute forms).
#pragma once
#include <cmath>
#include <math.h>
#include <algorithm>
using std::isnan;
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <functional>
#include <map>
#include <optional>
#include <string>
#include <vector>

// ---- logging: printf-backed so -Wformat checks every argument list ----------
static bool g_quiet = false;
#define ESP_LOGI(tag, fmt, ...) do { if (!g_quiet) printf("  [I][%s] " fmt "\n", tag, ##__VA_ARGS__); } while (0)
#define ESP_LOGW(tag, fmt, ...) do { if (!g_quiet) printf("  [W][%s] " fmt "\n", tag, ##__VA_ARGS__); } while (0)
#define ESP_LOGE(tag, fmt, ...) do { if (!g_quiet) printf("  [E][%s] " fmt "\n", tag, ##__VA_ARGS__); } while (0)
#define ESP_LOGD(tag, fmt, ...) do { } while (0)

// ---- time ---------------------------------------------------------------------
static uint32_t g_ms = 20000;             // millis(), past the 15 s boot grace
uint32_t millis() { return g_ms; }
struct ESPTime { bool valid; time_t timestamp; bool is_valid() const { return valid; } };
struct HATime { bool valid = true; time_t base = 0; ESPTime now() { return {valid, (time_t) (base + g_ms / 1000)}; } };

struct Application { int reboots = 0; void safe_reboot() { reboots++; } };
static Application App;

// ---- globals --------------------------------------------------------------------
template<typename T> struct G { T v; T init; explicit G(T i) : v(i), init(i) {} T &value() { return v; } };

// ---- sensors ----------------------------------------------------------------------
struct Sensor {
  float state = NAN;
  bool has = false;
  std::function<std::optional<float>()> tmpl;
  std::vector<std::function<void(float)>> on_value;
  int publishes = 0;
  void publish_state(float s) { state = s; has = true; publishes++; for (auto &cb : on_value) cb(s); }
  bool has_state() const { return has; }
  void update() { if (tmpl) { auto r = tmpl(); if (r.has_value()) publish_state(*r); } }
  void reset() { publish_state(0.0f); }
};
struct TextSensor {
  std::string state;
  bool has = false;
  int publishes = 0;
  void publish_state(const std::string &s) { state = s; has = true; publishes++; }
  bool has_state() const { return has; }
};
struct BinarySensor { bool state = false; };

// ---- scripts ------------------------------------------------------------------------
struct Script3 {
  std::function<void(float, int, bool)> fn;
  int runs = 0;
  void execute(float a, int b, bool c) { runs++; if (fn) fn(a, b, c); }
};
struct Script0 { int runs = 0; void execute() { runs++; } };

// ---- I2C + simulated INA228 ------------------------------------------------------------
namespace i2c { enum ErrorCode { ERROR_OK = 0, ERROR_UNKNOWN = 1 }; }
struct INA228Sim {
  uint16_t reg16[0x40] = {0};
  double charge_cnt = 0;    // CHARGE register, in CURRENT_LSB·s units (signed)
  double energy_cnt = 0;    // ENERGY register, in 51.2·CURRENT_LSB units (unsigned)
  double lsb = 400.0 / 524288.0;   // what the chip's SHUNT_CAL currently implies
  uint8_t ptr = 0;
  bool fail = false;
  void por() {
    reg16[0x02] = 0x1000; reg16[0x01] = 0xFB68; reg16[0x10] = 0x7FFF;
    charge_cnt = 0; energy_cnt = 0;
    lsb = 0.0;   // SHUNT_CAL 1000h: counts are off-scale until the driver rewrites it
  }
  // ESPHome ina2xx setup(): CONFIG (no RST, no RSTACC), ADC_CONFIG, SHUNT_CAL.
  void driver_setup(double max_current) {
    lsb = max_current / 524288.0;
    reg16[0x01] = 0xFDC5;
    reg16[0x02] = (uint16_t) (13107.2f * 1000000.0f * (float) lsb * 0.000375f);
  }
  void advance(double dt_s, double amps, double volts) {
    if (lsb <= 0) return;
    charge_cnt += amps * dt_s / lsb;
    energy_cnt += std::fabs(amps * volts) * dt_s / (51.2 * lsb);
  }
  int64_t charge_raw() const { return (int64_t) std::llround(charge_cnt); }
  uint64_t energy_raw() const { return (uint64_t) std::llround(energy_cnt); }
};
static INA228Sim ina;
struct Bus {
  i2c::ErrorCode write(uint8_t addr, const uint8_t *buf, size_t len, bool stop = true) {
    (void) stop;
    if (addr != 0x40 || ina.fail) return i2c::ERROR_UNKNOWN;
    ina.ptr = buf[0];
    if (len == 3) ina.reg16[buf[0]] = (uint16_t) ((buf[1] << 8) | buf[2]);
    return i2c::ERROR_OK;
  }
  i2c::ErrorCode read(uint8_t addr, uint8_t *buf, size_t len) {
    if (addr != 0x40 || ina.fail) return i2c::ERROR_UNKNOWN;
    if (ina.ptr == 0x0A && len == 5) {
      int64_t r = ina.charge_raw();
      uint64_t u = (uint64_t) r & ((1ULL << 40) - 1);
      for (int k = 0; k < 5; k++) buf[k] = (uint8_t) (u >> (8 * (4 - k)));
    } else if (ina.ptr == 0x09 && len == 5) {
      uint64_t u = ina.energy_raw() & ((1ULL << 40) - 1);
      for (int k = 0; k < 5; k++) buf[k] = (uint8_t) (u >> (8 * (4 - k)));
    } else if (len == 2) {
      buf[0] = (uint8_t) (ina.reg16[ina.ptr] >> 8); buf[1] = (uint8_t) (ina.reg16[ina.ptr] & 0xFF);
    } else {
      memset(buf, 0, len);
    }
    return i2c::ERROR_OK;
  }
};

// ---- esp_wifi subset (ESP-IDF 5.5 signatures) -------------------------------------------
typedef int esp_err_t;
#define ESP_OK 0
typedef enum { WIFI_PS_NONE, WIFI_PS_MIN_MODEM, WIFI_PS_MAX_MODEM } wifi_ps_type_t;
static wifi_ps_type_t g_ps = WIFI_PS_MIN_MODEM;
esp_err_t esp_wifi_get_ps(wifi_ps_type_t *type) { *type = g_ps; return ESP_OK; }
esp_err_t esp_wifi_get_max_tx_power(int8_t *power) { *power = 44; return ESP_OK; }
