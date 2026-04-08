package lib

import (
	"fmt"
	"log"
)

// ProcessData handles data processing
func ProcessData(input string) error {
	// TODO: Add validation

	if input == "" {
		// Warning: panic usage
		panic("input cannot be empty")
	}

	// Info: Print without format
	fmt.Print(input)

	return nil
}

// ValidateConfig checks configuration
func ValidateConfig(config map[string]string) bool {
	// FIXME: Incomplete validation

	for key, value := range config {
		if value == "" {
			log.Printf("Invalid config for %s", key)
			// Warning: another panic
			panic(fmt.Sprintf("config %s is empty", key))
		}
	}

	return true
}

// nolint - Info: linter suppression
func UnsafeOperation() {
	// XXX: This needs review
	fmt.Print("Doing something unsafe")
}
