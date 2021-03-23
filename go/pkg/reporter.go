package humbug

import (
	"fmt"

	bugout "github.com/bugout-dev/bugout-go/pkg"
	"github.com/bugout-dev/bugout-go/pkg/spire"
)

type Reporter interface {
	Tag(key string, modifier string)
	Untag(key string, modifier string)
	Tags() []string
	Publish(report Report) error
}

type HumbugReporter struct {
	clientID          string
	sessionID         string
	consent           Consent
	bugoutClient      bugout.BugoutClient
	bugoutAccessToken string
	bugoutJournalID   string
	tags              map[string]bool
}

func (reporter *HumbugReporter) Tag(key, modifier string) {
	if reporter.tags == nil {
		reporter.tags = make(map[string]bool)
	}
	tag := key
	if modifier != "" {
		tag = fmt.Sprintf("%s:%s", key, modifier)
	}
	reporter.tags[tag] = true
}

func (reporter *HumbugReporter) Untag(key, modifier string) {
	if reporter.tags == nil {
		reporter.tags = make(map[string]bool)
	}
	tag := key
	if modifier != "" {
		tag = fmt.Sprintf("%s:%s", key, modifier)
	}
	reporter.tags[tag] = false
}

func (reporter *HumbugReporter) Tags() []string {
	tags := make([]string, len(reporter.tags))
	i := 0
	for tag, value := range reporter.tags {
		if value {
			tags[i] = tag
			i++
		}
	}
	return tags[:i]
}

func MergeTags(tags0, tags1 []string) []string {
	tagSet := make(map[string]bool)
	for _, tag := range tags0 {
		tagSet[tag] = true
	}
	for _, tag := range tags1 {
		tagSet[tag] = true
	}
	mergedTags := make([]string, len(tagSet))
	i := 0
	for tag := range tagSet {
		mergedTags[i] = tag
		i++
	}
	return mergedTags
}

func (reporter *HumbugReporter) Publish(report Report) error {
	defer func() {
		// TODO(zomglings): For now, we only recover here so panicked Publish calls do not have an
		// effect on any program using the Humbug library. In the future, there should be an option
		// of writing log messages if an environment variable (e.g. HUMBUG_LOG_LEVEL) has been
		// set appropriately.
		recover()
	}()
	var err error
	userHasConsented := reporter.consent.Check()
	if userHasConsented {
		context := spire.EntryContext{
			ContextType: "humbug",
			ContextID:   reporter.sessionID,
		}
		tags := MergeTags(report.Tags, reporter.Tags())
		_, err = reporter.bugoutClient.Spire.CreateEntry(reporter.bugoutAccessToken, reporter.bugoutJournalID, report.Title, report.Content, tags, context)
	}
	return err
}

func CreateHumbugReporter(consent Consent, clientID string, sessionID string, bugoutAccessToken string, bugoutJournalID string) (*HumbugReporter, error) {
	reporter := HumbugReporter{
		consent:           consent,
		clientID:          clientID,
		sessionID:         sessionID,
		bugoutAccessToken: bugoutAccessToken,
		bugoutJournalID:   bugoutJournalID,
	}

	reporter.Tag("session", sessionID)
	if clientID != "" {
		reporter.Tag("client", clientID)
	}

	bugoutClient, err := bugout.ClientFromEnv()
	if err != nil {
		return &reporter, err
	}
	reporter.bugoutClient = bugoutClient
	return &reporter, nil
}
