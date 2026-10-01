# Cumulocity IoT opcua-device-gateway

:warning: This repo is subject to change but provided to demonstrate connecting thin-edge.io to OPC UA servers by way of the opcua-device-gateway client.

This repository provides a containerized version of the Cumulocity IoT opcua-device-gateway Java based client customized to work with thin-edge.io out of the box.
To configure the opcua-device gateway inside the container you can use environment variables.

This example shows a docker compose to be used in the tedge-demo-container (podman hence `tcp://host.containers.internal`). The device will be attached as a child device to thinEdge device. To prevent from id clashes the external id of the gateway will be combination of THINEDGE_DEVICEID:GATEWAY_IDENTIFIER

```yaml
services:
  gateway:
    # Image is maintained under: https://github.com/thin-edge/opcua-device-gateway-container
    image: ghcr.io/thin-edge/opcua-device-gateway:latest
    container_name: opc-device-gateway
    restart: always
    environment:
    # Use configuration from https://cumulocity.com/docs/device-integration/opcua/#gateway-configuration-and-registration 
      - GATEWAY_IDENTIFIER=OPCUAGateway
      - GATEWAY_NAME=OPCUAGateway
      - GATEWAY_THINEDGE_MQTTSERVERURL=tcp://host.containers.internal:1883
      - GATEWAY_THINEDGE_USEFORDATAFORWARDING=true
      - GATEWAY_THINEDGE_ENABLED=true
      - GATEWAY_MAPPINGS_MERGECYCLICREAD=true
      - GATEWAY_MONITORING_INTERVAL=3600000
    volumes:
      - opcua_data:/app/data
      # Provide access to thin-edge.io configuration
      - /etc/tedge:/etc/tedge
      - /etc/tedge/device-certs:/etc/tedge/device-certs
    networks:
      - backend

volumes:
  opcua_data:
networks:
  backend:
    name: backend
```

Example to run the gateway standalone

```yaml
services:
  gateway:
    # Image is maintained under: https://github.com/thin-edge/opcua-device-gateway-container
    image: ghcr.io/thin-edge/opcua-device-gateway:latest
    container_name: opc-device-gateway-standalone
    restart: always
    environment:
    # Use configuration from https://cumulocity.com/docs/device-integration/opcua/#gateway-configuration-and-registration
      - C8Y_BASEURL=https://example.eu-latest.cumulocity.com
      - GATEWAY_IDENTIFIER=OPCUAGateway-standalone
      - GATEWAY_NAME=OPCUAGateway-standalone
      - GATEWAY_MONITORING_INTERVAL=3600000
    volumes:
      - opcua_data:/app/data
    networks:
      - backend

volumes:
  opcua_data:
networks:
  backend:
    name: backend
```

There is no application.yaml for the gateway configuration included in the container. All config env parameters are converted like

```yaml
gateway:
    identifier: OPCUAGateway
```

To

```sh
GATEWAY_IDENTIFIER=OPCUAGateway
```

### Logging

The gateway writes its log to `/root/.opcua/log/` inside the container. Files roll over daily or at 50MB, are kept for 3 days and are capped at 500MB in total. These limits, and the log levels, can be changed with the standard Spring Boot environment variables:

```yaml
    environment:
      - LOGGING_LOGBACK_ROLLINGPOLICY_MAX_FILE_SIZE=20MB
      - LOGGING_LOGBACK_ROLLINGPOLICY_MAX_HISTORY=2
      - LOGGING_LOGBACK_ROLLINGPOLICY_TOTAL_SIZE_CAP=200MB
      - LOGGING_LOGBACK_ROLLINGPOLICY_CLEAN_HISTORY_ON_START=true
      - LOGGING_LEVEL_COM_CUMULOCITY=WARN
```

## Project tasks

This project uses [just](https://github.com/casey/just) to run tasks.

### Publish a release

```sh
just release
```
