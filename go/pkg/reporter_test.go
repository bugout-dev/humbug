package humbug

import (
	"testing"
)

func TestMergeTags(t *testing.T) {
	tags0 := []string{"a", "b", "c"}
	tags1 := []string{"b", "c", "d"}
	mergedTags := MergeTags(tags0, tags1)
	expectedNumTags := 4
	if len(mergedTags) != expectedNumTags {
		t.Errorf("Got incorrect number of tags. Actual: %d, Expected %d", len(mergedTags), expectedNumTags)
	}

	mergedTagSet := make(map[string]bool)
	for _, tag := range mergedTags {
		mergedTagSet[tag] = true
	}
	for _, tag := range tags0 {
		v, ok := mergedTagSet[tag]
		if !ok || !v {
			t.Errorf("Tag (%s) not present in merged tags as expected", tag)
		}
	}
	for _, tag := range tags1 {
		v, ok := mergedTagSet[tag]
		if !ok || !v {
			t.Errorf("Tag (%s) not present in merged tags as expected", tag)
		}
	}
}
