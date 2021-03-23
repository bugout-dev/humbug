package humbug

import (
	"os"
	"testing"
)

func TestTrue(t *testing.T) {
	if !True() {
		t.Error("True returned false")
	}
}

func TestFalse(t *testing.T) {
	if False() {
		t.Error("False returned true")
	}
}

func TestHumbugConsentWithTrue(t *testing.T) {
	consent := HumbugConsent{[]ConsentMechanism{True}}
	if !consent.Check() {
		t.Error("Consent check was false, was expecting it to be true.")
	}
}

func TestHumbugConsentWithFalse(t *testing.T) {
	consent := HumbugConsent{[]ConsentMechanism{False}}
	if consent.Check() {
		t.Error("Consent check was true, was expecting it to be false.")
	}
}

func TestHumbugConsentWithFalseThenTrue(t *testing.T) {
	consent := HumbugConsent{[]ConsentMechanism{False, True}}
	if consent.Check() {
		t.Error("Consent check was true, was expecting it to be false.")
	}
}

func TestHumbugConsentWithTrueThenFalse(t *testing.T) {
	consent := HumbugConsent{[]ConsentMechanism{True, False}}
	if consent.Check() {
		t.Error("Consent check was true, was expecting it to be false.")
	}
}

func TestHumbugConsentWithEnvVarOptInDenied(t *testing.T) {
	envVar := "HUMBUG_TEST_ENV_VAR_OPT_IN"
	os.Setenv(envVar, "0")
	defer os.Unsetenv(envVar)
	mechanism := EnvironmentVariableConsent(envVar, Yes, false)
	consent := HumbugConsent{[]ConsentMechanism{mechanism}}
	if consent.Check() {
		t.Error("Consent check was true, was expecting it to be false.")
	}
}

func TestHumbugConsentWithEnvVarOptInGranted(t *testing.T) {
	envVar := "HUMBUG_TEST_ENV_VAR_OPT_IN"
	os.Setenv(envVar, "1")
	defer os.Unsetenv(envVar)
	mechanism := EnvironmentVariableConsent(envVar, Yes, false)
	consent := HumbugConsent{[]ConsentMechanism{mechanism}}
	if !consent.Check() {
		t.Error("Consent check was false, was expecting it to be true.")
	}
}

func TestHumbugConsentWithEnvVarOptInGrantedButShortCircuited(t *testing.T) {
	envVar := "HUMBUG_TEST_ENV_VAR_OPT_IN"
	os.Setenv(envVar, "1")
	defer os.Unsetenv(envVar)
	os.Setenv(ShortCircuitVar, "true")
	defer os.Unsetenv(ShortCircuitVar)
	mechanism := EnvironmentVariableConsent(envVar, Yes, false)
	consent := HumbugConsent{[]ConsentMechanism{mechanism}}
	if consent.Check() {
		t.Error("Consent check was true, was expecting it to be false.")
	}
}
