# BasketDAO Migrator App


## Setup

Install Brownie as per the docs. 

For testing ensure the testing utils are installed: 

```sh
$ pipx brownie-token-tester
```

If using Pylance with VSCode, you should point the interpreter to the pipx installation

`Ctrl/Cmd + Shift + P` -> "Select interpreter" -> `~/.local/pipx/venvs/eth-brownie/bin/python`

Setup your .env file with:

```sh
WEB3_INFURA_PROJECT_ID=API_KEY_GOES_HERE
```

## The Contract



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

You cannot rewind state


### Questions:
- What is the purpose of the deadline in external functions? 
- The receive function has yet to be implemented

### Potential Improvements:
