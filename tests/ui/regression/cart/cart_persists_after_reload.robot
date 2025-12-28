*** Settings ***
Documentation     Regression: cart content persists after reload.
...               Adds a product to the cart, verifies it is visible, reloads the page,
...               and verifies the same product name is still visible in the cart.
Resource          ../../resources/keywords/common.robot
Library           String
Suite Setup       Open Toolshop
Test Setup        Open Toolshop
Test Teardown     Close Toolshop


*** Test Cases ***
Cart Persists After Reload
    [Documentation]    Add a product to the cart, reload the page, and verify the cart still contains it.
    [Tags]    regression

    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0

    # Capture product name from details page.
    Wait For Elements State    css=h1    visible    timeout=15s
    ${name}=    Get Text    css=h1
    ${name}=    Strip String    ${name}

    # Add to cart and verify the product appears in the cart.
    Click    text=Add to cart
    Wait For Elements State    text=Shopping cart    visible    timeout=15s
    Click    text=Shopping cart
    Wait For Elements State    text=${name}    visible    timeout=15s

    # Reload and verify cart content persists.
    Reload
    Wait For Elements State    text=${name}    visible    timeout=15s