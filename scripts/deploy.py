from brownie import accounts, BasketMigrator
from brownie import ZERO_ADDRESS

GOV_ADDRESS = ZERO_ADDRESS  # todo: update before deploy


def main():
    deployer = accounts.load("piedao-deployer")
    migrator = deployer.deploy(BasketMigrator, GOV_ADDRESS)
    print(f"Migrator contract deployed at: {migrator.address}")
