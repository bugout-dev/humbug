package humbug

import (
	bugout "github.com/bugout-dev/bugout-go/pkg"
	"github.com/bugout-dev/bugout-go/pkg/spire"
)

type Report struct {
	Title   string
	Tags    []string
	Content string
}

type Reporter interface {
	Tags() []string
	Publish(Report) error
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
	context := spire.EntryContext{
		ContextType: "humbug",
		ContextID:   reporter.sessionID,
	}
	tags := MergeTags(report.Tags, reporter.Tags())
	_, err := reporter.bugoutClient.Spire.CreateEntry(reporter.bugoutAccessToken, reporter.bugoutJournalID, report.Title, report.Content, tags, context)
	return err
}
