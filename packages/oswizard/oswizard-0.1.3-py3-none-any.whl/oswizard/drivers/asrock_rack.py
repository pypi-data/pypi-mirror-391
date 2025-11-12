from .redfish import RedfishVirtualMedia, RedfishConfig


class ASRockRack(RedfishVirtualMedia):
    """
    ASRock Rack (ASPEED BMC) generally uses Managers/1.
    """

    name = "asrock"

    def __init__(self, ctx, rf: RedfishConfig | None = None):
        cfg = rf or RedfishConfig(
            ctx.host,
            ctx.user,
            ctx.password,
            verify_tls=False,
            manager_id="1",
        )
        super().__init__(ctx, cfg)
