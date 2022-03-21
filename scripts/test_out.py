from brownie import accounts, interface, Contract, BasketMigrator

BDI = Contract.from_explorer("0x0309c98B1bffA350bcb3F9fB9780970CA32a5060")
BDI_WHALE = "0x25431341a5800759268a6ac1d3cd91c029d7d9ca"  # ~2000 BDI


def main():
    gov = accounts[0]
    fish = accounts[1]

    # transfer from whale
    BDI.transfer(fish, 2000 * 1e18, {"from": BDI_WHALE})

    # deploy BasketMigrator
    migrator = gov.deploy(BasketMigrator, gov)

    # deposit into BasketMigrator
    BDI.approve(migrator, 2000 * 1e18, {"from": fish})
    migrator.enter(2000 * 1e18, {"from": fish})

    # close the round
    migrator.closeEntry({"from": gov})
    migrator.burnAndUnwrap({"from": gov})
