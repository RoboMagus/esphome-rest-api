#include "rest_api.h"

#include "esphome/components/json/json_util.h"
#include "esphome/core/progmem.h"
#include "esphome/components/network/util.h"
#include "esphome/core/application.h"
#include "esphome/core/defines.h"
#include "esphome/core/entity_base.h"
#include "esphome/core/helpers.h"
#include "esphome/core/log.h"
#include "esphome/core/util.h"

#if !defined(USE_ESP32) && defined(USE_ARDUINO)
#include "StreamString.h"
#endif

#include <cstdlib>

namespace esphome::web_server {

static const char *const TAG = "rest_api";

RestApi::RestApi(web_server_base::WebServerBase *base) : base_(base) {}

void RestApi::add_endpoint(std::string endpoint, int method, std::function<void(AsyncWebServerRequest *request)> &&f) {
    this->endpoints_[endpoint] = {method, std::move(f)};
}

void RestApi::setup() {
  this->base_->init();
  this->base_->add_handler(this);
}

void RestApi::loop() { }

void RestApi::dump_config() {
  ESP_LOGCONFIG(TAG,
                "REST API:\n"
                "  Address: %s:%u",
                network::get_use_address(), this->base_->get_port());
}
float RestApi::get_setup_priority() const { return setup_priority::WIFI - 1.0f; }

bool RestApi::canHandle(AsyncWebServerRequest *request) const {
#ifdef USE_ESP32
  char url_buf[AsyncWebServerRequest::URL_BUF_SIZE];
  StringRef url = request->url_to(url_buf);
#else
  const auto &url = request->url();
#endif

  auto endpoint = this->endpoints_.find(url.c_str());
  return (endpoint != this->endpoints_.end());
}

void RestApi::handleRequest(AsyncWebServerRequest *request) {
#ifdef USE_ESP32
  char url_buf[AsyncWebServerRequest::URL_BUF_SIZE];
  StringRef url = request->url_to(url_buf);
#else
  const auto &url = request->url();
#endif

  auto endpoint = this->endpoints_.find(url.c_str());
  if (endpoint != this->endpoints_.end()) {
    if (endpoint->second.method == request->method()) {
        endpoint->second.func(request);
        return;
    }
  }

  // No matching handler found - send 404
  ESP_LOGV(TAG, "Request for unknown URL: %s", url.c_str());
  request->send(404, ESPHOME_F("text/plain"), ESPHOME_F("Not Found"));
}

bool RestApi::isRequestHandlerTrivial() const { return false; }


}  // namespace esphome::web_server

