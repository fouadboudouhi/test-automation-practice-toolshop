*** Settings ***
Documentation     Regression: add product to cart and verify it is shown in cart.
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop
Library           String
Suite Setup       Open Toolshop

*** Test Cases ***
Cart Contains Added Product Name
    [Tags]    regression
    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    css=h1    visible    timeout=15s
    ${name}=    Get Text    css=h1
    ${name}=    Strip String    ${name}

    Click    text=Add to cart
    Wait For Elements State    text=Shopping cart    visible    timeout=15s

    # Open cart via UI (no deep-link)
    Click    text=Shopping cart
    Wait For Elements State    text=${name}    visible    timeout=15s
