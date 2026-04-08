package utils

import (
	"fmt"
	"strings"
)

// StringHelper provides string manipulation utilities
type StringHelper struct {
	caseSensitive bool
}

// NewStringHelper creates a new StringHelper instance
func NewStringHelper(caseSensitive bool) *StringHelper {
	return &StringHelper{
		caseSensitive: caseSensitive,
	}
}

// Contains checks if a string contains a substring
func (h *StringHelper) Contains(str, substr string) bool {
	if !h.caseSensitive {
		str = strings.ToLower(str)
		substr = strings.ToLower(substr)
	}
	return strings.Contains(str, substr)
}

// Split splits a string by delimiter
func (h *StringHelper) Split(str, delimiter string) []string {
	if str == "" {
		return []string{}
	}
	return strings.Split(str, delimiter)
}

// Join joins strings with a delimiter
func (h *StringHelper) Join(parts []string, delimiter string) string {
	return strings.Join(parts, delimiter)
}

// Reverse reverses a string
func (h *StringHelper) Reverse(str string) string {
	runes := []rune(str)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

// Example demonstrates the helper
func Example() {
	helper := NewStringHelper(false)

	text := "Hello, World!"
	if helper.Contains(text, "hello") {
		fmt.Println("Found!")
	}

	parts := helper.Split(text, ", ")
	for i, part := range parts {
		fmt.Printf("Part %d: %s\n", i, part)
	}

	reversed := helper.Reverse(text)
	fmt.Println(reversed)
}
