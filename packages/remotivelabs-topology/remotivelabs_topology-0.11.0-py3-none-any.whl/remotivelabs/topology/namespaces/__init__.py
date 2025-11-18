"""
Namespace access module for RemotiveBroker.

Provides an interface to a namespace configured in a RemotiveBroker.
Supported types include:
    - `someip`: Enables sending requests and subscribing to events.
    - `generic`: Enables Restbus access, signal subscriptions, and more.
    - `can`: Same as generic
    - `scripted`: Enables subscribing to frames transformed by scripts

Namespaces can be used standalone or injected into a `BehavioralModel` for simulation or testing.
See individual module documentation for protocol-specific details.

This example creates and configures a CAN namespace, but does not start the restbus.
It is not really useful as is; in a real application you would likely either use it together with a `BehavioralModel`
or start the restbus to send periodic messages.

```python
.. include:: ../_docs/snippets/can_namespace.py
```

It is common to use namespaces together with a behavioral model, as shown in the example below.

```python
.. include:: ../_docs/snippets/can_namespace_bm.py
```
"""
