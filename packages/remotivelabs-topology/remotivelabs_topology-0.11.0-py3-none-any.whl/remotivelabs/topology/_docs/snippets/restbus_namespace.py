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
        # start the restbus with signal database defaults and wait until cancelled
        await hlcu_can.restbus.start()
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
