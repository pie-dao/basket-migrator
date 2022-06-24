"""
This appears to be unrelated to BDI and is a script for the DEFI+S/L -> DEFI++ Merge that happened previously
"""

from ape_safe import ApeSafe
from brownie import chain, interface
from brownie import Contract, ZERO_ADDRESS


DPP_ADDR = "0x8D1ce361eb68e9E05573443C407D4A3Bed23B033"
DPL_ADDR = "0x78f225869c08d478c34e5f645d07a87d3fe8eb78"
DPS_ADDR = "0xad6a626ae2b43dcb1b39430ce496d2fa0365ba9c"
DPL_LENDING_MANAGER_ADDR = "0x64659f9c7293677D03492Bd9881908Cb38C57142"
EXPERINATOR = "0xd6a2AAeb7ee0243D7d3148cCDB10C0BD1bb56336"

DEV_SAFE_ADDRESS = "0x6458A23B020f489651f2777Bd849ddEd34DfCcd2"


def unlend_assets_defi_pl(safe):
    dpl_lending_manager = interface.ILendingManager(DPL_LENDING_MANAGER_ADDR)

    lended_assets = [
        "0xA64BD6C70Cb9051F6A9ba1F163Fdc07E0DfB5F84",  # aLINK
        "0x70e36f6BF80a52b3B46b3aF8e106CC0ed743E8e4",  # cCOMP
        "0x328C4c80BC7aCa0834Db37e6600A6c49E12Da4DE",  # aSNX
        "0x35A18000230DA775CAc24873d00Ff85BccdeD550",  # cUNI
        "0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272",  # xSUSHI
        "0x12e51E77DAAA58aA0E9247db7510Ea4B46F9bEAd",  # aYFI
    ]

    for asset in lended_assets:
        dpl_lending_manager.unlend(asset, 2**256 - 1, {"from": safe.account})


# convert defi++ to ExperiPie
def experinate_defi_pp(safe):
    dpp_proxy = interface.IProxy(DPP_ADDR)
    experinator = Contract.from_explorer(EXPERINATOR)
    dpp_balancer_pool = Contract.from_explorer(DPP_ADDR)

    dpp_proxy.setProxyOwner(EXPERINATOR, {"from": safe.account})
    dpp_balancer_pool.setController(EXPERINATOR, {"from": safe.account})
    experinator.toExperiPie(DPP_ADDR, DEV_SAFE_ADDRESS, {"from": safe.account})


def exit_underlying_pies_defi_pp(safe):
    dpp_caller = interface.ICallFacet(DPP_ADDR)
    dpl_basket = interface.IBasketFacet(DPL_ADDR)
    dps_basket = interface.IBasketFacet(DPS_ADDR)

    # exit DEFI+L
    exit_pool_data_dpl = dpl_basket.exitPool.encode_input(
        dpl_basket.balanceOf(DPP_ADDR)
    )

    dpp_caller.callNoValue([DPL_ADDR], [exit_pool_data_dpl], {"from": safe.account})

    # exit DEFI+S
    exit_pool_data_dps = dps_basket.exitPool.encode_input(
        dps_basket.balanceOf(DPP_ADDR)
    )

    dpp_caller.callNoValue([DPS_ADDR], [exit_pool_data_dps], {"from": safe.account})


def reconfig_defi_pp(safe):
    dpp_basket = interface.IBasketFacet(DPP_ADDR)

    underlying_baskets = [DPL_ADDR, DPS_ADDR]

    for b in underlying_baskets:
        dpp_basket.removeToken(b, {"from": safe.account})

    for b in underlying_baskets:
        b_contract = interface.IBasketFacet(b)
        underlyings = b_contract.getTokens()

        for u in underlyings:
            dpp_basket.addToken(u, {"from": safe.account})

    dpp_basket.setCap(100000000e18, {"from": safe.account})
    dpp_basket.setLock(chain.height, {"from": safe.account})


def main():
    safe = ApeSafe(DEV_SAFE_ADDRESS)

    unlend_assets_defi_pl(safe)
    experinate_defi_pp(safe)
    exit_underlying_pies_defi_pp(safe)
    reconfig_defi_pp(safe)

    safe_tx = safe.multisend_from_receipts()
    safe.preview(safe_tx)
    safe.sign_with_frame(safe_tx)
    safe.post_transaction(safe_tx)
