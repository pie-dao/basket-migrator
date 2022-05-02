from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS
from eth_abi import encode_single
from brownie import interface, chain
from brownie import Contract, BasketMigrator

AMOUNT_OUT = 0  # todo: update when baking

HALF_HOUR = 1800
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
DEV_SAFE_ADDRESS = "0x6458A23B020f489651f2777Bd849ddEd34DfCcd2"

MIGRATOR = ""
DPP_ADDR = "0x8D1ce361eb68e9E05573443C407D4A3Bed23B033"
ROUTER_UNIV2 = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
ROUTER_SUSHI = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
ROUTER_UNIV3 = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
QUOTER_UNIV3 = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"
FACTORY_UNIV3 = "0x1F98431c8aD98523631AE4a59f267346ea31F984"


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


def main():
    safe = ApeSafe(DEV_SAFE_ADDRESS)
    migrator = BasketMigrator(MIGRATOR)
    dpp_basket = interface.IBasketFacet(DPP_ADDR)
    router_univ2 = Contract.from_explorer(ROUTER_UNIV2)
    router_univ3 = Contract.from_explorer(ROUTER_UNIV3)
    router_sushi = Contract.from_explorer(ROUTER_SUSHI)
    quoter_univ3 = Contract.from_explorer(QUOTER_UNIV3)
    factory_univ3 = Contract.from_explorer(FACTORY_UNIV3)

    (tokens, amounts) = dpp_basket.calcTokensForAmount(AMOUNT_OUT)

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

    weth_erc20 = interface.ERC20(WETH)
    balance_weth_before = weth_erc20.balanceOf(MIGRATOR)

    print(f"balance WETH before: {balance_weth_before / 1e18}")

    migrator.bake(
        2000e18,
        max_amount_in,
        chain.time() + HALF_HOUR,
        True,
        swaps,
        {"from": safe.account},
    )

    print(f"DEFI++ balance: {dpp_basket.balanceOf(MIGRATOR)}")
    print(f"balance WETH after: {weth_erc20.balanceOf(MIGRATOR)}")

    safe_tx = safe.multisend_from_receipts()
    safe.preview(safe_tx)
    safe.sign_with_frame(safe_tx)
    safe.post_transaction(safe_tx)
