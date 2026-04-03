
from esphome import automation
import esphome.codegen as cg
from esphome.components import text_sensor, web_server_base
from esphome.components.web_server_base import CONF_WEB_SERVER_BASE_ID
import esphome.config_validation as cv
from esphome.const import (
    CONF_AUTH,
    CONF_ID,
    CONF_LAMBDA,
    CONF_METHOD,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PATH,
    CONF_PORT,
    CONF_USERNAME,
    CONF_WEB_SERVER,
)
from esphome.core import CORE, CoroPriority, coroutine_with_priority

AUTO_LOAD = ["text_sensor", "json", "web_server_base"]
DEPENDENCIES = ["api"]
CODEOWNERS = ["@RoboMagus"]

CONF_ENDPOINTS = "endpoints"
CONF_EVENT_SENSOR = "event_sensor"

web_server_ns = cg.esphome_ns.namespace("web_server")
RestApi = web_server_ns.class_("RestApi", cg.Component)

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(RestApi),
            cv.GenerateID(CONF_WEB_SERVER_BASE_ID): cv.use_id(
                web_server_base.WebServerBase
            ),
            cv.OnlyWithout(CONF_PORT, CONF_WEB_SERVER, default=80): cv.All(
                cv.conflicts_with_component(CONF_WEB_SERVER),
                cv.port,
            ),
            cv.OnlyWithout(CONF_AUTH, CONF_WEB_SERVER, default=80): cv.All(
                cv.conflicts_with_component(CONF_WEB_SERVER),
                cv.Schema(
                    {
                        cv.Required(CONF_USERNAME): cv.All(
                            cv.string_strict, cv.Length(min=1)
                        ),
                        cv.Required(CONF_PASSWORD): cv.All(
                            cv.string_strict, cv.Length(min=1)
                        ),
                    }
                ),
            ),
            cv.Optional(CONF_EVENT_SENSOR): text_sensor.text_sensor_schema().extend(
                {
                    cv.Optional(CONF_NAME, default="Last API event"): cv.string_strict
                }
            ),
            cv.Required(CONF_ENDPOINTS): cv.ensure_list(
                cv.Schema(
                    {
                        cv.Required(CONF_PATH): cv.string,
                        cv.Optional(CONF_METHOD, default="GET"): cv.enum({
                                "GET": cg.global_ns.HTTP_GET,
                                "POST": cg.global_ns.HTTP_POST,
                                "PUT": cg.global_ns.HTTP_PUT,
                            }, 
                            upper=True
                        ),
                        cv.Required(CONF_LAMBDA): cv.lambda_,
                    }
                )
            ),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)


@coroutine_with_priority(CoroPriority.WEB)
async def to_code(config):
    paren = await cg.get_variable(config[CONF_WEB_SERVER_BASE_ID])

    var = cg.new_Pvariable(config[CONF_ID], paren)
    await cg.register_component(var, config)

    if CONF_PORT in config:
        cg.add(paren.set_port(config[CONF_PORT]))
    if CONF_AUTH in config:
        cg.add_define("USE_WEBSERVER_AUTH")
        cg.add(paren.set_auth_username(config[CONF_AUTH][CONF_USERNAME]))
        cg.add(paren.set_auth_password(config[CONF_AUTH][CONF_PASSWORD]))

    if CONF_EVENT_SENSOR in config:
        evt = await text_sensor.new_text_sensor(config[CONF_EVENT_SENSOR])
        cg.add(var.add_event_sensor(evt))
    for endpoint in config[CONF_ENDPOINTS]:
        lambda_ = await cg.process_lambda(endpoint[CONF_LAMBDA], [(cg.global_ns.namespace("AsyncWebServerRequest *") ,"request")], return_type=cg.void)
        cg.add(var.add_endpoint(endpoint[CONF_PATH], endpoint[CONF_METHOD], lambda_))
