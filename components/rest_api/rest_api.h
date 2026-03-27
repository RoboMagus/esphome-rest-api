
#pragma once

#include "esphome/components/json/json_util.h"
#include "esphome/components/web_server_base/web_server_base.h"
#include "esphome/core/component.h"

#include <functional>
#include <list>
#include <map>
#include <string>
#include <utility>
#include <vector>

namespace esphome::web_server {

// Type for parameter names that can be stored in flash on ESP8266
#ifdef USE_ESP8266
using ParamNameType = const __FlashStringHelper *;
#else
using ParamNameType = const char *;
#endif

struct EpValue {
    int method;
    std::function<void(AsyncWebServerRequest *request)> func;
};

class RestApi final : public Component, public AsyncWebHandler {
 public:
  RestApi(web_server_base::WebServerBase *base);

  void add_endpoint(std::string endpoint, int method, std::function<void(AsyncWebServerRequest *request)> &&f);

  // ========== INTERNAL METHODS ==========
  // (In most use cases you won't need these)
  /// Setup the internal web server and register handlers.
  void setup() override;
  void loop() override;

  void dump_config() override;

  float get_setup_priority() const override;

  /// Override the web handler's canHandle method.
  bool canHandle(AsyncWebServerRequest *request) const override;
  /// Override the web handler's handleRequest method.
  void handleRequest(AsyncWebServerRequest *request) override;
  /// This web handle is not trivial.
  bool isRequestHandlerTrivial() const override;  // NOLINT(readability-identifier-naming)

 protected:
  web_server_base::WebServerBase *base_;

private:
  std::map<const std::string, EpValue> endpoints_;
};

}  // namespace esphome::web_server
