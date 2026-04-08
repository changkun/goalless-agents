package gokv

import (
	"sync"
	"time"
)

type item struct {
	value      interface{}
	expiration int64
}

type KV struct {
	mu    sync.RWMutex
	items map[string]item
}

func New() *KV {
	kv := &KV{
		items: make(map[string]item),
	}
	go kv.evictionLoop()
	return kv
}

func (kv *KV) Set(key string, value interface{}, ttl time.Duration) {
	var exp int64
	if ttl > 0 {
		exp = time.Now().Add(ttl).UnixNano()
	}

	kv.mu.Lock()
	kv.items[key] = item{
		value:      value,
		expiration: exp,
	}
	kv.mu.Unlock()
}

func (kv *KV) Get(key string) (interface{}, bool) {
	kv.mu.RLock()
	defer kv.mu.RUnlock()

	it, ok := kv.items[key]
	if !ok {
		return nil, false
	}

	if it.expiration > 0 && time.Now().UnixNano() > it.expiration {
		return nil, false
	}

	return it.value, true
}

func (kv *KV) Delete(key string) {
	kv.mu.Lock()
	delete(kv.items, key)
	kv.mu.Unlock()
}

func (kv *KV) evictionLoop() {
	ticker := time.NewTicker(time.Second)
	for range ticker.C {
		kv.mu.Lock()
		now := time.Now().UnixNano()
		for k, v := range kv.items {
			if v.expiration > 0 && now > v.expiration {
				delete(kv.items, k)
			}
		}
		kv.mu.Unlock()
	}
}
