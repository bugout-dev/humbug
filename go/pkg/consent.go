package humbug

import (
	"os"
)

// ConsentMechanism is a report-independent means of checking user consent.
type ConsentMechanism func() bool

// Consent is the interface that Humbug uses to determine user consent to reporting.
type Consent interface {
	Check() bool
}

// Short circuit environment variable. Humbug will never report errors if BUGGER_OFF=true (or any)
// other value in the Yes set.
var ShortCircuitVar string = "BUGGER_OFF"

// HumbugConsent is a concrete implementation of the Consent interface. It each of a list of
// consent mechanisms in order until one of them denies consent or all of them grant consent.
// It also includes a system-wide short circuit mechanism that a user can use to turn off all
// Humbug reporting (regardless of the tool that is integrated with Humbug).
type HumbugConsent struct {
	Mechanisms []ConsentMechanism
}

// A set of values indicating a "no"
var No map[string]bool = map[string]bool{
	"0":     false,
	"f":     false,
	"n":     false,
	"F":     false,
	"N":     false,
	"false": false,
	"no":    false,
	"False": false,
	"No":    false,
	"FALSE": false,
	"NO":    false,
}

// A set of values indicating a "yes"
var Yes map[string]bool = map[string]bool{
	"1":    true,
	"t":    true,
	"y":    true,
	"T":    true,
	"Y":    true,
	"true": true,
	"yes":  true,
	"True": true,
	"Yes":  true,
	"TRUE": true,
	"YES":  true,
}

// True is a consent mechanism that always indicates granted consent
var True ConsentMechanism = func() bool { return true }

// False is a consent mechanism that always indicates denied consent
var False ConsentMechanism = func() bool { return false }

// Reads consent from the value of the given environment variable. The valueConsentMap specifies
// which values for the environment variable correspond to consent or lack thereof. If the
// environment variable is not defined, the whenUndefined parameter determines the default
// behavior.
func EnvironmentVariableConsent(envVar string, valueConsentMap map[string]bool, whenUndefined bool) ConsentMechanism {
	return func() bool {
		envValue := os.Getenv(envVar)
		if consent, exists := valueConsentMap[envValue]; exists {
			return consent
		}
		return whenUndefined
	}
}

func (consent *HumbugConsent) Check() bool {
	shortCircuit := EnvironmentVariableConsent(ShortCircuitVar, Yes, false)
	if shortCircuit() {
		return false
	}
	for _, mechanism := range consent.Mechanisms {
		if !mechanism() {
			return false
		}
	}
	return true
}

func CreateHumbugConsent(mechanisms ...ConsentMechanism) *HumbugConsent {
	return &HumbugConsent{Mechanisms: mechanisms}
}
