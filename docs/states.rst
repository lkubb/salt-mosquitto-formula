Available states
----------------

The following states are found in this formula:

.. contents::
   :local:


``mosquitto``
^^^^^^^^^^^^^
*Meta-state*.

This installs the mosquitto containers,
manages their configuration and starts their services.


``mosquitto.package``
^^^^^^^^^^^^^^^^^^^^^
Installs the mosquitto containers only.
This includes creating systemd service units.


``mosquitto.config``
^^^^^^^^^^^^^^^^^^^^
Manages the configuration of the mosquitto containers.
Has a dependency on `mosquitto.package`_.


``mosquitto.auth``
^^^^^^^^^^^^^^^^^^



``mosquitto.auth.acl``
^^^^^^^^^^^^^^^^^^^^^^



``mosquitto.auth.users``
^^^^^^^^^^^^^^^^^^^^^^^^



``mosquitto.service``
^^^^^^^^^^^^^^^^^^^^^
Starts the mosquitto container services
and enables them at boot time.
Has a dependency on `mosquitto.config`_.


``mosquitto.clean``
^^^^^^^^^^^^^^^^^^^
*Meta-state*.

Undoes everything performed in the ``mosquitto`` meta-state
in reverse order, i.e. stops the mosquitto services,
removes their configuration and then removes their containers.


``mosquitto.package.clean``
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Removes the mosquitto containers
and the corresponding user account and service units.
Has a depency on `mosquitto.config.clean`_.
If ``remove_all_data_for_sure`` was set, also removes all data.


``mosquitto.config.clean``
^^^^^^^^^^^^^^^^^^^^^^^^^^
Removes the configuration of the mosquitto containers
and has a dependency on `mosquitto.service.clean`_.

This does not lead to the containers/services being rebuilt
and thus differs from the usual behavior.


``mosquitto.auth.clean``
^^^^^^^^^^^^^^^^^^^^^^^^



``mosquitto.service.clean``
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Stops the mosquitto container services
and disables them at boot time.


