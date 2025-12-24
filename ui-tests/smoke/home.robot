*** Settings ***
Resource    ../resources/keywords/common.robot

*** Test Cases ***
Homepage Is Reachable
    Open Toolshop
    Get Title
    Close Toolshop
