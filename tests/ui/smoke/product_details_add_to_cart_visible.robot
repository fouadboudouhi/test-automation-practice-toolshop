*** Settings ***
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Product Details Shows Add To Cart
    [Tags]    smoke
    Go To    ${BASE_URL}
    Wait For At Least One Product Card

    Click    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")])[1]

    # Add-to-cart should be present on details page
    Wait For Elements State    css=[data-test="add-to-cart"]    visible    timeout=30s
