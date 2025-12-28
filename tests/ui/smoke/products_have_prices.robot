*** Settings ***
Documentation     Smoke: verify product cards display a price-like value.
...               Reads the first product card text and asserts it contains digits (optionally with decimals).
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Product Cards Show A Price
    [Documentation]    Assert the first product card text matches a price-like pattern (contains digits).
    [Tags]    smoke

    Go To    ${BASE_URL}
    Wait For At Least One Product Card

    ${card_text}=    Get Text    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")])[1]
    # Price usually contains digits (and often decimals).
    Should Match Regexp    ${card_text}    .*\\d+([\\.,]\\d{2})?.*