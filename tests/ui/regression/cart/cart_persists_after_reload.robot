*** Settings ***
Documentation     Regression: cart content persists after reload.
Resource          ../../resources/keywords/common.robot
Library           String
Suite Setup       Open Toolshop

*** Test Cases ***
Cart Persists After Reload
    [Tags]    regression
    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    css=h1    visible    timeout=15s
    ${name}=    Get Text    css=h1
    ${name}=    Strip String    ${name}

    Click    text=Add to cart
    Wait For Elements State    text=Shopping cart    visible    timeout=15s

    Click    text=Shopping cart
    Wait For Elements State    text=${name}    visible    timeout=15s

    Reload
    Wait For Elements State    text=${name}    visible    timeout=15s