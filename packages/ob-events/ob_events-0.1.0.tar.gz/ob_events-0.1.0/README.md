# Python package to publish Events to Outerbounds platform

## Installation

Install the package using `pip`:

```bash
pip install ob-events
```

This library has no dependencies for standard, inline configurations.

If you need to load configurations from AWS Secrets Manager, you must install the boto3 library. You can do this by installing the aws extra:

```bash
pip install ob-events[aws]
```

### Usage Example

#### Metaflow Flow (The Receiver)

First, assume you have a Metaflow Flow that is triggered by an event, like `my_event`.

```python
from metaflow import FlowSpec, step, current, trigger


@trigger(event='my_event')
class NodeSimpleTriggeredFlow(FlowSpec):
    @step
    def start(self):
        self.var_1 = ["h", "e", "l", "l"]
        self.next(self.b, foreach='var_1')

    @step
    def b(self):
        print("In B")
        self.next(self.join)

    @step
    def join(self, inputs):
        self.next(self.end)

    @step
    def end(self):
        print("In end")

if __name__ == "__main__":
    NodeSimpleTriggeredFlow()
```

#### Python Trigger (The Sender)

You can trigger this flow using the ob-events Python library. This assumes you are using Service Principals for programmatic auth. You can get the configString for the machine user from the OBP UI.

```python
from ob_events import EventTrigger, ConfigError, TriggerError

try:
    # Event name, must match what's in @trigger
    event_trigger = EventTrigger("my_event")

    # Initialize the library with the config string from the OBP UI
    # This can also be a file path:
    # event_trigger.init(config_file_path="/path/to/config.json")
    event_trigger.init(config_string="awssm-arn:...")

    # OR static API key:
    # event_trigger.init_from_service_principal(
    #     service_principal_name="some-static-key-principal",
    #     deployment_domain="mycompany.obp.outerbounds.com",
    #     perimeter="default",
    #     jwt_token="...key goes here..."
    # )

    # Trigger the event with an optional payload
    print("Triggering event 'my_event'...")
    event_trigger.trigger(payload={"foo": "bar", "source": "my-service"})
    print("Event triggered successfully!")

except ConfigError as e:
    print(f"Configuration error: {e}")
except TriggerError as e:
    print(f"Trigger error: {e}")
except ImportError as e:
    print(f"Dependency error: {e}")
    print("If using AWS Secrets Manager, please run 'pip install ob-events[aws]'")
```
