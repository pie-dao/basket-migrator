import pytest
import brownie

from brownie import chain, interface
from brownie import Contract, ZERO_ADDRESS
from brownie_tokens import MintableForkToken
from eth_abi import encode_single

HALF_HOUR = 1800
DEV_SAFE_ADDRESS = "0x6458A23B020f489651f2777Bd849ddEd34DfCcd2"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


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
def DPL():
    yield _MintableTestToken("0x78f225869c08d478c34e5f645d07a87d3fe8eb78")


@pytest.fixture
def DPS():
    yield _MintableTestToken("0xad6a626ae2b43dcb1b39430ce496d2fa0365ba9c")


@pytest.fixture
def bdi_assets():
    yield [
        "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
        "0xc00e94cb662c3520282e6f5717214004a7f26888",
        "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",
        "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
        "0x408e41876cCCDC0F92210600ef50372656052a38",
        "0xdeFA4e8a7bcBA345F687a2f1456F5Edd9CE97202",
        "0xBBbbCA6A901c926F240b89EacB641d8Aec7AEafD",
        "0xba100000625a3754423978a60c9317c58a424e3D",
        "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
        "0x2ba592F78dB6436527729929AAf6c908497cB200",
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "0x9d409a0A012CFbA9B15F6D4B36Ac57A46966Ab9a",
        "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
    ]


@pytest.fixture
def dpp_proxy():
    yield interface.IProxy("0x8D1ce361eb68e9E05573443C407D4A3Bed23B033")


@pytest.fixture
def dpp_balancer_pool():
    yield Contract.from_explorer("0x8D1ce361eb68e9E05573443C407D4A3Bed23B033")


@pytest.fixture
def dpp_caller_facet():
    yield interface.ICallFacet("0x8D1ce361eb68e9E05573443C407D4A3Bed23B033")


@pytest.fixture
def dpp_basket_facet():
    yield interface.IBasketFacet("0x8D1ce361eb68e9E05573443C407D4A3Bed23B033")


@pytest.fixture
def dpl_basket_facet():
    yield interface.IBasketFacet("0x78f225869c08d478c34e5f645d07a87d3fe8eb78")


@pytest.fixture
def dps_basket_facet():
    yield interface.IBasketFacet("0xad6a626ae2b43dcb1b39430ce496d2fa0365ba9c")


@pytest.fixture
def weth_token():
    yield interface.ERC20(WETH)


@pytest.fixture
def router_sushi():
    yield Contract.from_explorer("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")


@pytest.fixture
def router_univ2():
    yield Contract.from_explorer("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")


@pytest.fixture
def router_univ3():
    yield Contract.from_explorer("0xE592427A0AEce92De3Edee1F18E0157C05861564")


@pytest.fixture
def quoter_univ3():
    yield Contract.from_explorer("0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6")


@pytest.fixture
def factory_univ3():
    yield Contract.from_explorer("0x1F98431c8aD98523631AE4a59f267346ea31F984")


@pytest.fixture
def experinator():
    yield Contract.from_explorer("0xd6a2AAeb7ee0243D7d3148cCDB10C0BD1bb56336")


@pytest.fixture
def gov(accounts):
    yield accounts[0]


@pytest.fixture
def misc_accounts(accounts):
    yield accounts[2:8]


@pytest.fixture
def migrator(gov, BasketMigrator):
    yield gov.deploy(BasketMigrator, gov)


def quote_univ2(router, token_in, token_out, amount_in):
    router = interface.IUniswapV2Router01(router)
    try:
        return router.getAmountsOut(amount_in, [token_in, token_out])[1]
    except:
        return 0


def quote_univ2_given_out(router, token_in, token_out, amount_out):
    router = interface.IUniswapV2Router01(router)
    try:
        return router.getAmountsIn(amount_out, [token_in, token_out])[0]
    except:
        return 2**256 - 1


def swap_univ2(router, token_in, token_out, max_in, amount_out, account):
    router = interface.IUniswapV2Router01(router)

    interface.ERC20(token_in).approve(router, max_in, {"from": account})

    router.swapTokensForExactTokens(
        amount_out,
        max_in,
        [token_in, token_out],
        account,
        chain.time() + HALF_HOUR,
        {"from": account},
    )


def quote_univ3(factory, quoter, token_in, token_out, amount_in):
    factory = interface.IUniswapV3Factory(factory)
    pool = factory.getPool(token_in, token_out, 3000)

    if pool == ZERO_ADDRESS:
        return 0
    else:
        try:
            quoter = interface.IQuoter(quoter)
            quote = quoter.quoteExactInputSingle.call(
                token_in, token_out, 3000, amount_in, 0
            )
            return quote
        except:
            return 0


def quote_univ3_given_out(factory, quoter, token_in, token_out, amount_out):
    factory = interface.IUniswapV3Factory(factory)
    pool = factory.getPool(token_in, token_out, 3000)

    if pool == ZERO_ADDRESS:
        return 2**256 - 1
    else:
        try:
            quoter = interface.IQuoter(quoter)
            quote = quoter.quoteExactOutputSingle.call(
                token_in, token_out, 3000, amount_out, 0
            )
            return quote
        except:
            return 2**256 - 1


def swap_univ3(router, token_in, token_out, max_in, amount_out, account):
    router = interface.ISwapRouter(router)
    interface.ERC20(token_in).approve(router, max_in, {"from": account})
    router.exactOutputSingle(
        [
            token_in,
            token_out,
            3000,
            account,
            chain.time() + HALF_HOUR,
            amount_out,
            max_in,
            0,
        ],
        {"from": account},
    )


def migration_dpp(
    dpp_proxy,
    dpp_balancer_pool,
    dpp_caller_facet,
    dpp_basket_facet,
    dpl_basket_facet,
    dps_basket_facet,
    experinator,
):
    dpp_proxy.setProxyOwner(experinator, {"from": DEV_SAFE_ADDRESS})

    dpp_balancer_pool.setController(
        experinator, {"from": dpp_balancer_pool.getController()}
    )

    experinator.toExperiPie(
        dpp_caller_facet, DEV_SAFE_ADDRESS, {"from": experinator.owner()}
    )

    # exit pools
    exit_pool_data_dpl = dpl_basket_facet.exitPool.encode_input(
        dpl_basket_facet.balanceOf(dpp_proxy)
    )

    dpp_caller_facet.callNoValue(
        [dpl_basket_facet], [exit_pool_data_dpl], {"from": DEV_SAFE_ADDRESS}
    )

    # exit pools
    exit_pool_data_dps = dps_basket_facet.exitPool.encode_input(
        dps_basket_facet.balanceOf(dpp_proxy)
    )
    dpp_caller_facet.callNoValue(
        [dps_basket_facet], [exit_pool_data_dps], {"from": DEV_SAFE_ADDRESS}
    )

    # remove dpl, dps, adds only tokens from dps (should be enough for an e2e test)

    dpp_basket_facet.removeToken(dpl_basket_facet, {"from": DEV_SAFE_ADDRESS})
    dpp_basket_facet.removeToken(dps_basket_facet, {"from": DEV_SAFE_ADDRESS})

    dpp_basket_facet.addToken(
        "0xBBbbCA6A901c926F240b89EacB641d8Aec7AEafD", {"from": DEV_SAFE_ADDRESS}
    )
    dpp_basket_facet.addToken(
        "0x408e41876cCCDC0F92210600ef50372656052a38", {"from": DEV_SAFE_ADDRESS}
    )
    dpp_basket_facet.addToken(
        "0x04Fa0d235C4abf4BcF4787aF4CF447DE572eF828", {"from": DEV_SAFE_ADDRESS}
    )
    dpp_basket_facet.addToken(
        "0xba100000625a3754423978a60c9317c58a424e3D", {"from": DEV_SAFE_ADDRESS}
    )
    dpp_basket_facet.addToken(
        "0xec67005c4E498Ec7f55E092bd1d35cbC47C91892", {"from": DEV_SAFE_ADDRESS}
    )
    dpp_basket_facet.addToken(
        "0x89Ab32156e46F46D02ade3FEcbe5Fc4243B9AAeD", {"from": DEV_SAFE_ADDRESS}
    )

    dpp_basket_facet.setLock(chain.height, {"from": DEV_SAFE_ADDRESS})
    dpp_basket_facet.setCap(100000000e18, {"from": DEV_SAFE_ADDRESS})


def test_e2e(
    BDI,
    bdi_assets,
    weth_token,
    dpp_proxy,
    dpp_balancer_pool,
    dpp_caller_facet,
    dpp_basket_facet,
    dpl_basket_facet,
    dps_basket_facet,
    router_sushi,
    router_univ2,
    router_univ3,
    quoter_univ3,
    factory_univ3,
    experinator,
    gov,
    misc_accounts,
    migrator,
):
    migration_dpp(
        dpp_proxy,
        dpp_balancer_pool,
        dpp_caller_facet,
        dpp_basket_facet,
        dpl_basket_facet,
        dps_basket_facet,
        experinator,
    )

    alice = misc_accounts[0]

    BDI._mint_for_testing(alice, 2000e18)
    BDI.approve(migrator, 2000e18, {"from": alice})
    migrator.enter(2000e18, {"from": alice})

    # close the round
    migrator.closeEntry({"from": gov})
    migrator.burnAndUnwrap({"from": gov})

    # exec bdi swaps to eth
    swaps = []
    for t in bdi_assets:
        token = interface.ERC20(t)
        bal = token.balanceOf(migrator)
        univ2_out = quote_univ2(router_univ2, t, WETH, bal)
        sushi_out = quote_univ2(router_sushi, t, WETH, bal)
        univ3_out = quote_univ3(factory_univ3, quoter_univ3, t, WETH, bal)

        if univ2_out >= sushi_out and univ2_out >= univ3_out:
            swaps.append(
                (
                    False,
                    encode_single(
                        "(address,address[],uint256,uint256)",
                        [router_univ2.address, [t, WETH], bal, univ2_out],
                    ),
                )
            )
        elif sushi_out >= univ2_out and sushi_out >= univ3_out:
            swaps.append(
                (
                    False,
                    encode_single(
                        "(address,address[],uint256,uint256)",
                        [router_sushi.address, [t, WETH], bal, sushi_out],
                    ),
                )
            )
        else:
            swaps.append(
                (
                    True,
                    encode_single(
                        "(address,address,address,uint24,uint256,uint256)",
                        [
                            router_univ3.address,
                            t,
                            WETH,
                            3000,
                            bal,
                            univ3_out,
                        ],
                    ),
                )
            )

    migrator.execSwaps(swaps, chain.time() + HALF_HOUR, {"from": gov})

    assert weth_token.balanceOf(migrator) > 0

    amount_out = 2000e18  # conservative amount
    (tokens, amounts) = dpp_basket_facet.calcTokensForAmount(amount_out)

    swaps = []
    max_amount_in = 0
    for (t, amt) in zip(tokens, amounts):
        univ2_in = int(quote_univ2_given_out(router_univ2, WETH, t, amt) * 1.02)
        sushi_in = int(quote_univ2_given_out(router_sushi, WETH, t, amt) * 1.02)
        univ3_in = int(
            quote_univ3_given_out(factory_univ3, quoter_univ3, WETH, t, amt) * 1.02
        )

        if univ2_in <= sushi_in and univ2_in <= univ3_in:
            swaps.append(
                (
                    False,
                    encode_single(
                        "(address,address[],uint256,uint256)",
                        [router_univ2.address, [WETH, t], amt, univ2_in],
                    ),
                )
            )

            max_amount_in += univ2_in
        elif sushi_in <= univ2_in and sushi_in <= univ3_in:
            swaps.append(
                (
                    False,
                    encode_single(
                        "(address,address[],uint256,uint256)",
                        [router_sushi.address, [WETH, t], amt, sushi_in],
                    ),
                )
            )

            max_amount_in += sushi_in
        else:
            swaps.append(
                (
                    True,
                    encode_single(
                        "(address,address,address,uint24,uint256,uint256)",
                        [router_univ3.address, WETH, t, 3000, amt, univ3_in],
                    ),
                )
            )

            max_amount_in += univ3_in

    balance_weth_before = weth_token.balanceOf(migrator)

    migrator.bake(
        2000e18,
        max_amount_in,
        chain.time() + HALF_HOUR,
        True,
        swaps,
        {"from": gov},
    )

    assert dpp_basket_facet.balanceOf(migrator) == 2000e18
    assert balance_weth_before - weth_token.balanceOf(migrator) <= max_amount_in

    migrator.settle(False, {"from": gov})

    assert migrator.rate() == 1e18

    # test with refund

    migrator.bake(
        2000e18,
        max_amount_in,
        chain.time() + HALF_HOUR,
        True,
        swaps,
        {"from": gov, "value": 1e18},
    )

    assert weth_token.balanceOf(gov) == 1e18
    assert dpp_basket_facet.balanceOf(migrator) == 4000e18
