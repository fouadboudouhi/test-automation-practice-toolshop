*** Settings ***
Documentation     Regression: add product to cart and verify it is shown in cart.
...               Captures the product name from the product details page and asserts it appears in the cart.
Resource          ../../resources/keywords/common.robot
Library           String
Suite Setup       Open Toolshop
Test Setup        Open Toolshop
Test Teardown     Close Toolshop


*** Test Cases ***
Cart Contains Added Product Name
    [Documentation]    Add the first product to the cart and verify its name is visible in the cart view.
    [Tags]    regression

    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0

    # Capture product name from details page.
    Wait For Elements State    css=h1    visible    timeout=15s
    ${name}=    Get Text    css=h1
    ${name}=    Strip String    ${name}

    # Add to cart and open cart via UI.
    Click    text=Add to cart
    Wait For Elements State    text=Shopping cart    visible    timeout=15s
    Click    text=Shopping cart

    # Assert the cart contains the added product name.
    Wait For Elements State    text=${name}    visible    timeout=15s