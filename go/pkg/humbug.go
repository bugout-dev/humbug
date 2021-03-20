package humbug

import (
	bugout "github.com/bugout-dev/bugout-go/pkg"
)

func Ping(bugoutClient bugout.BugoutClient) error {
	_, broodErr := bugoutClient.Brood.Ping()
	if broodErr != nil {
		return broodErr
	}

	_, spireErr := bugoutClient.Spire.Ping()
	if spireErr != nil {
		return spireErr
	}

	return nil
}
