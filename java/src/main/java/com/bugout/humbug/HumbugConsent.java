package com.bugout.humbug;

import java.util.List;

public class HumbugConsent {

    private static final String BUGGER_OFF = "BUGGER_OFF";
    private static final List<String> YES =
            List.of("1", "t", "y", "T", "Y", "true", "yes", "True", "Yes", "TRUE", "YES");

    private final ConsentMechanism[] consentMechanisms;

    public HumbugConsent(boolean mechanism) {
        this(()->mechanism);
    }

    public HumbugConsent(ConsentMechanism ...consentMechanisms) {
        this.consentMechanisms = consentMechanisms;
    }

    public boolean check() {
        for (ConsentMechanism i : consentMechanisms) {
            if (!i.call())
                return false;
        }
        String envVal = System.getenv(BUGGER_OFF);
        if (envVal != null) {
            return !YES.contains(envVal);
        }
        return true;
    }

}
