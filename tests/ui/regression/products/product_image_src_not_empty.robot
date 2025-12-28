*** Settings ***
Documentation     Regression: first product card image src is not empty.
...               Verifies that the first product card renders an image with a non-empty src attribute.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Product Card Image Src Is Not Empty
    [Documentation]    Assert the first product card image has a non-empty src attribute.
    [Tags]    regression

    Wait For At Least One Product Card
    ${src}=    Get Attribute    css=a.card[data-test^="product-"] img >> nth=0    src
    Should Not Be Empty    ${src}