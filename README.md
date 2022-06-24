# BasketDAO Migrator App

## Setup

Install Brownie as per the docs. 

For testing ensure the testing utils are installed: 

```sh
$ pipx inject eth-brownie brownie-token-tester ape-safe
```

If using Pylance with VSCode, you should point the interpreter to the pipx installation

`Ctrl/Cmd + Shift + P` -> "Select interpreter" -> `~/.local/pipx/venvs/eth-brownie/bin/python`

Setup your .env file with:

```sh
WEB3_INFURA_PROJECT_ID=API_KEY_GOES_HERE
```

## Lifecycle

The deposit works in 3 phases:
    - 0: accepting deposits (open)
    - 1: no more deposits accepted (baking)
    - 2: users can withdraw (done)

The application has an initial `state` variable of 0 (the default uint8 value).

The msg.sender must be the gov address to change the state.

State 1 can be entered by calling closeEntry().
    - You must be in state=0 to call this function
State 2 can be entered by calling settle(true).
    - You must be in state=1 to call this function

You cannot rewind state.

To see an example of the full lifecylce, take a look at `tests/e2e/test_e2e.py`

### Actions
In state == 0, users can send their BDI to the contract, the governance contract can call closeEntry() to end this phase.

In state 1, the governor can call 4 contract calls:

1. `burnAndUnwrap` converts BDI tokens to their underlying assets
2. `execSwaps` swaps the underlying BDI assets for WETH, using the multisig.
3. `bake` converts WETH to DEFI++
4. `settle` computes the exchange rate between BDI deposited and DEFI++ to be redeemed, for the holders. Call `settle(true)` to end the baking phase and move to phase 2.

(The script to execute the execSwaps action is `exec_swaps_given_in.py`)

Finally, in state 2, BDI token holders can call `exit` to redeem for DEFI++ at the given rate.

### Questions:
- What is the purpose of the deadline in external functions? 
- The bake script needs AMOUNT_OUT to be set

