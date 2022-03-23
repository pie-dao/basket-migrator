import pytest
import brownie

from brownie import chain
from brownie_tokens import MintableForkToken


class _MintableTestToken(MintableForkToken):
    def __init__(self, address):
        super().__init__(address)


@pytest.fixture
def MintableTestToken():
    yield _MintableTestToken


@pytest.fixture
def BDI():
    yield _MintableTestToken("0x0309c98B1bffA350bcb3F9fB9780970CA32a5060")


@pytest.fixture
def DPP():
    yield _MintableTestToken("0x8D1ce361eb68e9E05573443C407D4A3Bed23B033")


@pytest.fixture
def gov(accounts):
    yield accounts[0]


@pytest.fixture
def misc_accounts(accounts):
    yield accounts[2:8]


@pytest.fixture
def migrator(gov, BasketMigrator):
    yield gov.deploy(BasketMigrator, gov)


def test_initial_state(gov, migrator):
    assert migrator.rate() == 0
    assert migrator.state() == 0
    assert migrator.totalDeposits() == 0
    assert migrator.gov() == gov


# user's interactions


def test_enter(BDI, misc_accounts, migrator):
    alice = misc_accounts[0]

    BDI._mint_for_testing(alice, 1e19)
    BDI.approve(migrator, 1e19, {"from": alice})
    migrator.enter(1e19, {"from": alice})

    assert migrator.state() == 0
    assert migrator.deposits(alice) == 1e19
    assert migrator.totalDeposits() == 1e19


def test_enter_twice(BDI, misc_accounts, migrator):
    alice = misc_accounts[0]

    BDI._mint_for_testing(alice, 1e19)
    BDI.approve(migrator, 1e19, {"from": alice})

    migrator.enter(5e18, {"from": alice})
    migrator.enter(5e18, {"from": alice})

    assert migrator.state() == 0
    assert migrator.deposits(alice) == 1e19
    assert migrator.totalDeposits() == 1e19


def test_cant_exit_if_not_finalized(BDI, misc_accounts, migrator):
    alice = misc_accounts[0]

    BDI._mint_for_testing(alice, 1e19)
    BDI.approve(migrator, 1e19, {"from": alice})

    migrator.enter(5e18, {"from": alice})

    with brownie.reverts():
        migrator.exit({"from": alice})


def test_cant_exit_if_entry_closed(BDI, gov, misc_accounts, migrator):
    alice = misc_accounts[0]

    BDI._mint_for_testing(alice, 1e19)
    BDI.approve(migrator, 1e19, {"from": alice})

    migrator.enter(5e18, {"from": alice})

    migrator.closeEntry({"from": gov})

    with brownie.reverts():
        migrator.exit({"from": alice})


def test_can_exit_if_settled(BDI, DPP, gov, misc_accounts, migrator):
    alice = misc_accounts[0]

    BDI._mint_for_testing(alice, 1e19)
    BDI.approve(migrator, 1e19, {"from": alice})

    migrator.enter(5e18, {"from": alice})

    migrator.closeEntry({"from": gov})

    DPP._mint_for_testing(migrator, 5e18)
    migrator.settle(True, {"from": gov})

    migrator.exit({"from": alice})


# state changes


def test_close_entry(gov, migrator):
    assert migrator.state() == 0

    migrator.closeEntry({"from": gov})

    assert migrator.state() == 1


def test_burn_and_unwrap_doesnt_change_state(BDI, misc_accounts, gov, migrator):
    alice = misc_accounts[0]
    BDI._mint_for_testing(alice, 5e18)
    BDI.approve(migrator, 5e18, {"from": alice})

    migrator.enter(5e18, {"from": alice})

    migrator.closeEntry({"from": gov})

    assert migrator.state() == 1

    migrator.burnAndUnwrap({"from": gov})

    assert migrator.state() == 1


def test_settle_not_final_doesnt_change_state(DPP, BDI, misc_accounts, gov, migrator):
    alice = misc_accounts[0]
    BDI._mint_for_testing(alice, 5e18)
    BDI.approve(migrator, 5e18, {"from": alice})

    migrator.enter(5e18, {"from": alice})

    migrator.closeEntry({"from": gov})

    assert migrator.state() == 1

    DPP._mint_for_testing(migrator, 5e18)
    migrator.settle(False, {"from": gov})

    assert migrator.state() == 1


def test_settle_final_changes_state(DPP, BDI, misc_accounts, gov, migrator):
    alice = misc_accounts[0]
    BDI._mint_for_testing(alice, 5e18)
    BDI.approve(migrator, 5e18, {"from": alice})

    migrator.enter(5e18, {"from": alice})

    migrator.closeEntry({"from": gov})

    assert migrator.state() == 1

    DPP._mint_for_testing(migrator, 5e18)
    migrator.settle(True, {"from": gov})

    assert migrator.state() == 2


# rate


def test_rate(DPP, BDI, misc_accounts, gov, migrator):
    alice = misc_accounts[0]
    BDI._mint_for_testing(alice, 5e18)
    BDI.approve(migrator, 5e18, {"from": alice})

    migrator.enter(5e18, {"from": alice})

    migrator.closeEntry({"from": gov})

    migrator.burnAndUnwrap({"from": gov})

    DPP._mint_for_testing(migrator, 5e18)
    migrator.settle(False, {"from": gov})

    assert migrator.rate() == 1e18

    DPP._mint_for_testing(migrator, 5e18)
    migrator.settle(True, {"from": gov})

    assert migrator.rate() == 2e18
