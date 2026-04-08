package gokv

import (
	"testing"
	"time"
)

func TestKV_SetGet(t *testing.T) {
	kv := New()
	kv.Set("foo", "bar", 0)

	val, ok := kv.Get("foo")
	if !ok || val != "bar" {
		t.Errorf("Expected 'bar', got %v", val)
	}
}

func TestKV_Expiration(t *testing.T) {
	kv := New()
	kv.Set("foo", "bar", 50*time.Millisecond)

	val, ok := kv.Get("foo")
	if !ok || val != "bar" {
		t.Fatal("Expected 'bar' to be present")
	}

	time.Sleep(100 * time.Millisecond)

	_, ok = kv.Get("foo")
	if ok {
		t.Error("Expected 'foo' to be expired")
	}
}

func TestKV_Delete(t *testing.T) {
	kv := New()
	kv.Set("foo", "bar", 0)
	kv.Delete("foo")

	_, ok := kv.Get("foo")
	if ok {
		t.Error("Expected 'foo' to be deleted")
	}
}
