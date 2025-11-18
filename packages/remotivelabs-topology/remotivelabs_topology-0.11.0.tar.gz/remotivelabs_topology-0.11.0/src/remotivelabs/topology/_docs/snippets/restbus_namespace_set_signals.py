import asyncio

from remotivelabs.broker import BrokerClient

from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig


async def main():
    async with (
        BrokerClient(url="http://127.0.0.1:50051") as broker_client,
        CanNamespace(
            "HazardLightControlUnit-DriverCan0",
            broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name="HazardLightControlUnit")])],
        ) as hlcu_can,
    ):
        # update signals in restbus before starting it
        await hlcu_can.restbus.update_signals(
            ("HazardLightButton.HazardLightButton", 1),
        )

        # start the restbus and loop until cancelled
        await hlcu_can.restbus.start()
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
