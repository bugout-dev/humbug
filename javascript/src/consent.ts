/*
This module implements Humbug's user consent mechanisms.
*/
type MechanismFunc = () => boolean;
type Mechanism = MechanismFunc | boolean
const yes = ["1", "t", "y", "T", "Y", "true", "yes", "True", "Yes", "TRUE", "YES"]
/**
 * HumbugConsent stores the client's consent settings.
 */
export default class HumbugConsent {
    buggerOffStatus: () => boolean
    public mechanism : Mechanism[] = [];
    /**
     * Humbug consent constructor
     * @param mechanisms list of booleans and function that return boolean
     */
    constructor(...mechanisms : Mechanism[]) {
        this.mechanism = mechanisms;
        this.buggerOffStatus = environmentVariableOptOut("BUGGER_OFF", yes)
    }

    /**
     * Checks if all consent mechanisms signal the user's consent.
     * If any of them signal false, returns false. Otherwise,
     * returns True.
     * If the user has set BUGGER_OFF=yes then do not assume consent.
     * Otherwise, at this point, we can assume consent.
     */
    check(): boolean {
        for (const el of this.mechanism) {
            if (typeof el === "boolean") {
                if (!el)
                    return false;
            }
            else if (typeof el === "function") {
                if (!el())
                    return false;
            }
            else
                throw new Error("Unknown type of consent mechanism")
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