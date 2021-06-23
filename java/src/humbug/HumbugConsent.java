package humbug;


public class HumbugConsent {
    private final boolean mechanism;
    private String envVar;
    private String[] optOutValues;

    public HumbugConsent() {
        this(false);
    }

    public HumbugConsent(boolean mechanism) {
        this.mechanism = mechanism;

        this.envVar = "BUGGER_OFF";
        this.optOutValues = new String[]{"yes"};
    }
    public boolean check() {
        return true;
    }


}
