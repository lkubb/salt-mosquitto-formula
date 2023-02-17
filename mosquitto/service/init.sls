# vim: ft=sls

{#-
    Starts the mosquitto container services
    and enables them at boot time.
    Has a dependency on `mosquitto.config`_.
#}

include:
  - .running
