/*
This module implements Humbug's user consent mechanisms.
*/

export default class HumbugConsent {
    /*
    HumbugConsent stores the client's consent settings.
    */
    buggerOffStatus: () => boolean

    constructor(
        public mechanisms?: boolean
    ) {
        if (mechanisms === undefined) {
            this.mechanisms = false
        }
        this.buggerOffStatus = environmentVariableOptOut("BUGGER_OFF", ["yes"])
    }

    check(): boolean {
        /*
        Checks if all consent mechanisms signal the user's consent. 
        If any of them signal false, returns false. Otherwise, 
        returns True.

        If the user has set BUGGER_OFF=yes then do not assume consent.
        Otherwise, at this point, we can assume consent.
        */
        if (this.mechanisms === false) {
            return false
        }
        return this.buggerOffStatus()
    }
}

function environmentVariableOptOut(
    envVar: string, optOutValues: string[]
) {
    return () => {
        const envVal = process.env[envVar];
        if (envVal !== undefined) {
            return !optOutValues.includes(envVal);
        }
        return true
    }
}