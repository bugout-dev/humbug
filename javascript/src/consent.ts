/*
This module implements Humbug's user consent mechanisms.
*/

export default class HumbugConsent {
    buggerOffStatus: boolean

    constructor(
        public mechanisms?: boolean
    ) {
        if (mechanisms === undefined) {
            this.mechanisms = false
        }
        this.buggerOffStatus = environmentVariableOptOut()
    }

    check(): boolean {
        if (this.mechanisms === false) {
            return false
        }
        else if (this.buggerOffStatus === false) {
            return false
        }
        return true
    }
}

function environmentVariableOptOut(): boolean {
    const envVar = process.env.BUGGER_OFF
    if (envVar === undefined) {
        return true
    }
    if (envVar.toLowerCase() === "false") {
        return false
    }
    else {
        return true
    }
}
